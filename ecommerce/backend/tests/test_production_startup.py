"""OPS-102/OPS-103 production-isolation and startup preflight tests."""

from __future__ import annotations

import os
from pathlib import Path
import re
import subprocess
import sys

import pytest

from app.cli.bootstrap_admin import _validate_initial_admin_password


ECOMMERCE_DIR = Path(__file__).resolve().parents[2]
BACKEND_DIR = ECOMMERCE_DIR / "backend"


def production_environment() -> dict[str, str]:
    env = os.environ.copy()
    env.update(
        {
            "APP_ENV": "production",
            "DATABASE_URL": (
                "postgresql+asyncpg://pangchong:Db-Gate-Password-2026@"
                "database.example.com:5432/pangchong"
            ),
            "REDIS_URL": "rediss://:Redis-Gate-Password-2026@cache.example.com:6379/0",
            "SECRET_KEY": "93c487dbe661f05ac2a94778f3e10d4c857ab62914d836ce",
            "DEBUG": "false",
            "RELOAD": "false",
            "WEB_CONCURRENCY": "2",
            "AUTH_COOKIE_SECURE": "true",
            "AUTH_COOKIE_SAMESITE": "lax",
            "ALLOWED_ORIGINS": '["https://shop.example.com"]',
            "ALIPAY_SANDBOX": "false",
            "ALIPAY_APP_ID": "2026000000000001",
            "ALIPAY_PRIVATE_KEY": "production-private-credential",
            "ALIPAY_PUBLIC_KEY": "production-public-credential",
        }
    )
    return env


def run_preflight(env: dict[str, str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "app.start", "--check"],
        cwd=BACKEND_DIR,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )


def test_valid_production_configuration_passes_preflight():
    result = run_preflight(production_environment())

    assert result.returncode == 0, result.stderr
    assert "APP_ENV=production" in result.stdout


@pytest.mark.parametrize(
    ("overrides", "expected_error"),
    [
        ({"SECRET_KEY": "CHANGE_THIS_TO_A_RANDOM_SECRET_IN_PRODUCTION"}, "SECRET_KEY"),
        ({"SECRET_KEY": "change-me-local-dev-secret"}, "SECRET_KEY"),
        ({"SECRET_KEY": "short-secret"}, "SECRET_KEY"),
        ({"SECRET_KEY": "a" * 64}, "SECRET_KEY"),
        (
            {
                "DATABASE_URL": (
                    "postgresql+asyncpg://pangchong:pangchong_dev_password@"
                    "database.example.com:5432/pangchong"
                )
            },
            "DATABASE_URL password",
        ),
        (
            {"REDIS_URL": "redis://:pangchong_dev_redis@cache.example.com:6379/0"},
            "REDIS_URL password",
        ),
        ({"REDIS_URL": "redis://cache.example.com:6379/0"}, "REDIS_URL must include"),
        ({"DEBUG": "true"}, "DEBUG must be false"),
        ({"RELOAD": "true"}, "RELOAD must be false"),
        ({"ALLOWED_ORIGINS": "[]"}, "ALLOWED_ORIGINS must contain"),
        ({"ALLOWED_ORIGINS": '["*"]'}, "wildcard"),
        ({"ALLOWED_ORIGINS": '["http://shop.example.com"]'}, "must use HTTPS"),
        ({"ALLOWED_ORIGINS": '["https://localhost"]'}, "local hosts"),
        ({"ALIPAY_SANDBOX": "true"}, "ALIPAY_SANDBOX must be false"),
        ({"ALIPAY_APP_ID": ""}, "ALIPAY_APP_ID is required"),
        ({"ALIPAY_PRIVATE_KEY": ""}, "ALIPAY_PRIVATE_KEY is required"),
        ({"ALIPAY_PUBLIC_KEY": ""}, "ALIPAY_PUBLIC_KEY is required"),
    ],
    ids=[
        "default-secret",
        "local-default-secret",
        "short-secret",
        "low-diversity-secret",
        "default-database-password",
        "default-redis-password",
        "missing-redis-password",
        "debug",
        "reload",
        "empty-cors",
        "wildcard-cors",
        "http-cors",
        "local-cors",
        "sandbox",
        "missing-app-id",
        "missing-private-key",
        "missing-public-key",
    ],
)
def test_unsafe_production_configuration_fails_before_server_start(
    overrides: dict[str, str], expected_error: str
):
    env = production_environment()
    env.update(overrides)

    result = run_preflight(env)

    assert result.returncode == 2
    assert "Production startup preflight failed" in result.stderr
    assert expected_error in result.stderr


def test_preflight_error_does_not_echo_secret_values():
    env = production_environment()
    env["SECRET_KEY"] = "DO_NOT_LEAK"

    result = run_preflight(env)

    assert result.returncode == 2
    assert "SECRET_KEY" in result.stderr
    assert "DO_NOT_LEAK" not in result.stderr


def test_production_compose_excludes_demo_seed_and_pins_production_mode():
    production_compose = (ECOMMERCE_DIR / "docker-compose.prod.yml").read_text(
        encoding="utf-8"
    )
    local_compose = (ECOMMERCE_DIR / "docker-compose.yml").read_text(encoding="utf-8")
    dockerfile = (BACKEND_DIR / "Dockerfile").read_text(encoding="utf-8")

    assert "./database/seed.sql:" not in production_compose
    assert "APP_ENV: production" in production_compose
    assert "service_completed_successfully" in production_compose
    assert 'command: ["python", "-m", "app.start", "--check"]' in production_compose
    assert 'command: ["alembic", "upgrade", "head"]' in production_compose
    assert "migrate:\n" in production_compose
    assert "migrate:\n        condition: service_completed_successfully" in production_compose
    assert "docker-entrypoint-initdb.d" not in production_compose
    assert "volumes: !override" in production_compose
    assert "database/seed.sql" in local_compose
    assert "RELOAD=${RELOAD:-true}" in local_compose
    assert 'CMD ["python", "-m", "app.start"]' in dockerfile
    assert "--reload" not in dockerfile


@pytest.mark.parametrize("filename", ["init.sql", "components.sql"])
def test_production_init_sql_does_not_insert_users_or_orders(filename: str):
    sql = (ECOMMERCE_DIR / "database" / filename).read_text(encoding="utf-8").lower()

    identity_or_order_insert = re.search(
        r"\binsert\s+into\s+(?:public\.)?\"?(?:users|orders|order_items)\"?\b",
        sql,
    )
    assert identity_or_order_insert is None


def test_initial_admin_bootstrap_rejects_weak_or_identity_based_passwords():
    for password in ("Password1", "ops_bootstrap-Strong-2026", "ops-bootstrap-A1!-2026"):
        with pytest.raises(ValueError, match="initial admin password"):
            _validate_initial_admin_password(
                password,
                username="ops_bootstrap",
                email="ops-bootstrap@example.com",
            )


def test_initial_admin_bootstrap_accepts_a_strong_unique_password():
    _validate_initial_admin_password(
        "Gate-7f31c8a2-Bootstrap!",
        username="ops_bootstrap",
        email="ops-bootstrap@example.com",
    )


def test_admin_bootstrap_validation_never_echoes_the_password():
    password = "abcdefghijklmnop"
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "app.cli.bootstrap_admin",
            "--username",
            "ops_bootstrap",
            "--email",
            "ops-bootstrap@example.com",
            "--password-stdin",
        ],
        cwd=BACKEND_DIR,
        env=production_environment(),
        input=f"{password}\n",
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 2
    assert "invalid password" in result.stderr
    assert password not in result.stderr
