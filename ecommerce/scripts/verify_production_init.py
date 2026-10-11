#!/usr/bin/env python3
"""Disposable Docker verification for the OPS-102 fresh-production gate.

The script creates an isolated Compose project and volume, proves that production
initialization creates no users/orders, bootstraps exactly one administrator, proves
that a second bootstrap is rejected, and always removes its containers and volume.
"""

from __future__ import annotations

from pathlib import Path
import os
import secrets
import subprocess
import sys
import tempfile


ECOMMERCE_DIR = Path(__file__).resolve().parents[1]
COMPOSE_FILE = ECOMMERCE_DIR / "docker-compose.prod.yml"


def run(
    command: list[str],
    *,
    input_text: str | None = None,
    capture: bool = False,
    check: bool = True,
) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        command,
        cwd=ECOMMERCE_DIR,
        input=input_text,
        text=True,
        capture_output=capture,
        check=False,
    )
    if check and result.returncode != 0:
        if capture:
            sys.stderr.write(result.stdout)
            sys.stderr.write(result.stderr)
        raise RuntimeError(
            f"command failed with exit code {result.returncode}: {' '.join(command)}"
        )
    return result


def main() -> int:
    project_name = f"pangchong-prod-gate-{os.getpid()}-{secrets.token_hex(3)}"
    database_password = f"db-{secrets.token_urlsafe(18)}"
    redis_password = f"redis-{secrets.token_urlsafe(18)}"
    admin_password = f"Gate-{secrets.token_hex(12)}-A1"

    env_file_path: Path | None = None
    compose: list[str] = []
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            prefix="pangchong-prod-gate-",
            suffix=".env",
            delete=False,
        ) as env_file:
            env_file.write(
                "\n".join(
                    [
                        "POSTGRES_DB=pangchong_gate",
                        "POSTGRES_USER=pangchong_gate",
                        f"POSTGRES_PASSWORD={database_password}",
                        f"REDIS_PASSWORD={redis_password}",
                        f"SECRET_KEY={secrets.token_hex(32)}",
                        "DEBUG=false",
                        "RELOAD=false",
                        "WEB_CONCURRENCY=2",
                        'ALLOWED_ORIGINS=["https://gate.invalid"]',
                        "ALIPAY_APP_ID=2026000000000001",
                        "ALIPAY_PRIVATE_KEY=gate-private-credential",
                        "ALIPAY_PUBLIC_KEY=gate-public-credential",
                        "ALIPAY_SANDBOX=false",
                        "",
                    ]
                )
            )
            env_file_path = Path(env_file.name)

        compose = [
            "docker",
            "compose",
            "--project-name",
            project_name,
            "--env-file",
            str(env_file_path),
            "--file",
            str(COMPOSE_FILE),
        ]

        print("[1/5] Starting a fresh isolated production PostgreSQL volume...")
        run([*compose, "up", "--detach", "--wait", "postgres"])

        print("[2/5] Verifying the production init scripts imported no identities or orders...")
        initial_counts = run(
            [
                *compose,
                "exec",
                "-T",
                "postgres",
                "psql",
                "-U",
                "pangchong_gate",
                "-d",
                "pangchong_gate",
                "-At",
                "-c",
                "SELECT (SELECT count(*) FROM users), (SELECT count(*) FROM orders), "
                "(SELECT count(*) FROM order_items);",
            ],
            capture=True,
        ).stdout.strip()
        if initial_counts != "0|0|0":
            raise AssertionError(f"expected fresh counts 0|0|0, got {initial_counts!r}")

        print("[3/5] Building the backend and creating the one-time administrator...")
        run([*compose, "build", "backend"])
        bootstrap_command = [
            *compose,
            "run",
            "--rm",
            "--no-deps",
            "-T",
            "backend",
            "python",
            "-m",
            "app.cli.bootstrap_admin",
            "--username",
            "ops_bootstrap",
            "--email",
            "ops-bootstrap@example.com",
            "--password-stdin",
        ]
        run(bootstrap_command, input_text=f"{admin_password}\n")

        print("[4/5] Verifying exactly one admin, no demo identities, and no orders...")
        final_counts = run(
            [
                *compose,
                "exec",
                "-T",
                "postgres",
                "psql",
                "-U",
                "pangchong_gate",
                "-d",
                "pangchong_gate",
                "-At",
                "-c",
                "SELECT (SELECT count(*) FROM users), "
                "(SELECT count(*) FROM users WHERE is_admin), "
                "(SELECT count(*) FROM orders), "
                "(SELECT count(*) FROM users WHERE username IN ('testuser', 'admin') "
                "OR email IN ('test@pangchong.com', 'admin@pangchong.com'));",
            ],
            capture=True,
        ).stdout.strip()
        if final_counts != "1|1|0|0":
            raise AssertionError(f"expected final counts 1|1|0|0, got {final_counts!r}")

        print("[5/5] Proving a second administrator bootstrap is refused...")
        second_attempt = run(
            bootstrap_command,
            input_text=f"{admin_password}\n",
            capture=True,
            check=False,
        )
        combined_output = second_attempt.stdout + second_attempt.stderr
        if second_attempt.returncode == 0 or "one-time bootstrap is disabled" not in combined_output:
            raise AssertionError(
                "second bootstrap was not rejected by the one-time administrator guard"
            )

        print("PASS: fresh production contains no demo users/orders and bootstrap is one-time.")
        return 0
    finally:
        if compose:
            print("Cleaning up the disposable Compose project and volume...")
            run(
                [*compose, "down", "--volumes", "--remove-orphans", "--rmi", "local"],
                check=False,
            )
        if env_file_path is not None:
            env_file_path.unlink(missing_ok=True)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AssertionError, RuntimeError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
