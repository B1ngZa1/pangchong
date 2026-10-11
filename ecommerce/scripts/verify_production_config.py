#!/usr/bin/env python3
"""Render Compose and enforce the production isolation policy without starting it."""

from __future__ import annotations

import json
import os
from pathlib import Path
import secrets
import subprocess
import sys
import tempfile


ECOMMERCE_DIR = Path(__file__).resolve().parents[1]
LOCAL_COMPOSE = ECOMMERCE_DIR / "docker-compose.yml"
PRODUCTION_COMPOSE = ECOMMERCE_DIR / "docker-compose.prod.yml"

_CONFIG_VARIABLES = {
    "POSTGRES_DB",
    "POSTGRES_USER",
    "POSTGRES_PASSWORD",
    "REDIS_PASSWORD",
    "DATABASE_URL",
    "SECRET_KEY",
    "DEBUG",
    "RELOAD",
    "WEB_CONCURRENCY",
    "ALLOWED_ORIGINS",
    "ALIPAY_APP_ID",
    "ALIPAY_PRIVATE_KEY",
    "ALIPAY_PUBLIC_KEY",
    "ALIPAY_SANDBOX",
    "ALIPAY_NOTIFY_URL",
    "ALIPAY_RETURN_URL",
    "ALIPAY_SELLER_ID",
    "SMTP_USER",
    "SMTP_PASSWORD",
    "ASSET_STORAGE_BACKEND",
    "SUPABASE_URL",
    "SUPABASE_SECRET_KEY",
    "SUPABASE_IMAGE_BUCKET",
    "SUPABASE_MODEL_BUCKET",
    "MAX_REQUEST_SIZE",
}


def _render_compose(files: list[Path], env_file: Path) -> dict:
    command = ["docker", "compose", "--env-file", str(env_file)]
    for compose_file in files:
        command.extend(("--file", str(compose_file)))
    command.extend(("config", "--format", "json"))

    clean_environment = os.environ.copy()
    for variable in _CONFIG_VARIABLES:
        clean_environment.pop(variable, None)

    result = subprocess.run(
        command,
        cwd=ECOMMERCE_DIR,
        env=clean_environment,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "docker compose config failed")
    return json.loads(result.stdout)


def _assert_no_demo_seed(model: dict, *, label: str) -> None:
    for service_name, service in model.get("services", {}).items():
        for volume in service.get("volumes", []):
            source = str(volume.get("source", ""))
            if Path(source).name.casefold() == "seed.sql":
                raise AssertionError(
                    f"{label}: service {service_name!r} imports demo seed {source!r}"
                )


def _assert_production_policy(model: dict, *, label: str) -> None:
    services = model.get("services", {})
    required_services = {"preflight", "postgres", "redis", "migrate", "backend"}
    missing = required_services.difference(services)
    if missing:
        raise AssertionError(f"{label}: missing services: {', '.join(sorted(missing))}")

    _assert_no_demo_seed(model, label=label)

    preflight = services["preflight"]
    backend = services["backend"]
    if preflight.get("command") != ["python", "-m", "app.start", "--check"]:
        raise AssertionError(f"{label}: preflight does not run the startup validator")

    migrate = services["migrate"]

    for service_name, service in (
        ("preflight", preflight),
        ("migrate", migrate),
        ("backend", backend),
    ):
        environment = service.get("environment", {})
        if environment.get("APP_ENV") != "production":
            raise AssertionError(f"{label}: {service_name} does not pin APP_ENV=production")

    for service_name in ("postgres", "redis", "migrate", "backend"):
        condition = (
            services[service_name]
            .get("depends_on", {})
            .get("preflight", {})
            .get("condition")
        )
        if condition != "service_completed_successfully":
            raise AssertionError(
                f"{label}: {service_name} can start before the production preflight"
            )

    if migrate.get("command") != ["alembic", "upgrade", "head"]:
        raise AssertionError(f"{label}: migration service does not run Alembic head")

    migration_dependency = (
        backend.get("depends_on", {}).get("migrate", {}).get("condition")
    )
    if migration_dependency != "service_completed_successfully":
        raise AssertionError(
            f"{label}: backend can start before the schema migration completes"
        )

    init_targets = [
        volume.get("target")
        for volume in services["postgres"].get("volumes", [])
        if str(volume.get("target", "")).startswith("/docker-entrypoint-initdb.d/")
    ]
    if init_targets:
        raise AssertionError(
            f"{label}: production database must be initialized only by Alembic, "
            f"not init scripts: {sorted(init_targets)}"
        )


def _assert_local_demo_path(model: dict) -> None:
    postgres = model.get("services", {}).get("postgres", {})
    seed_mounts = [
        volume
        for volume in postgres.get("volumes", [])
        if Path(str(volume.get("source", ""))).name.casefold() == "seed.sql"
    ]
    if len(seed_mounts) != 1:
        raise AssertionError("local Compose must expose exactly one explicit demo seed mount")
    app_environment = model.get("services", {}).get("backend", {}).get("environment", {})
    if app_environment.get("APP_ENV") != "development":
        raise AssertionError("the demo seed path must remain pinned to local development")


def main() -> int:
    env_file_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            prefix="pangchong-production-config-gate-",
            suffix=".env",
            delete=False,
        ) as env_file:
            env_file.write(
                "\n".join(
                    (
                        "POSTGRES_DB=pangchong_gate",
                        "POSTGRES_USER=pangchong_gate",
                        f"POSTGRES_PASSWORD=Db-{secrets.token_urlsafe(24)}",
                        f"REDIS_PASSWORD=Redis-{secrets.token_urlsafe(24)}",
                        f"SECRET_KEY={secrets.token_hex(32)}",
                        "DEBUG=false",
                        "RELOAD=false",
                        "WEB_CONCURRENCY=2",
                        'ALLOWED_ORIGINS=["https://production-gate.example.invalid"]',
                        "ALIPAY_APP_ID=2026000000000001",
                        "ALIPAY_PRIVATE_KEY=production-gate-private-credential",
                        "ALIPAY_PUBLIC_KEY=production-gate-public-credential",
                        "ALIPAY_SANDBOX=false",
                        "ALIPAY_NOTIFY_URL=https://production-gate.example.invalid/api/payment/callback/alipay",
                        "",
                    )
                )
            )
            env_file_path = Path(env_file.name)

        production = _render_compose([PRODUCTION_COMPOSE], env_file_path)
        _assert_production_policy(production, label="standalone production Compose")

        layered = _render_compose(
            [LOCAL_COMPOSE, PRODUCTION_COMPOSE],
            env_file_path,
        )
        _assert_production_policy(layered, label="local + production Compose")

        local = _render_compose([LOCAL_COMPOSE], env_file_path)
        _assert_local_demo_path(local)
    finally:
        if env_file_path is not None:
            env_file_path.unlink(missing_ok=True)

    print(
        "PASS: production Compose is seed-free, preflight-gated, and Alembic-migrated; "
        "the demo seed remains local-only."
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AssertionError, FileNotFoundError, json.JSONDecodeError, RuntimeError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
