"""Validated Uvicorn entry point used by both Docker Compose environments."""

from __future__ import annotations

import argparse
import sys

from pydantic import ValidationError


def _safe_validation_errors(exc: ValidationError) -> str:
    """Format validation failures without echoing environment values or secrets."""
    messages: list[str] = []
    for error in exc.errors(include_url=False, include_input=False):
        location = ".".join(str(part) for part in error.get("loc", ()))
        message = str(error.get("msg", "invalid configuration"))
        messages.append(f"{location}: {message}" if location else message)
    return "\n".join(messages)


def _load_settings():
    try:
        from .core.config import settings
    except ValidationError as exc:
        print(
            f"Production startup preflight failed:\n{_safe_validation_errors(exc)}",
            file=sys.stderr,
        )
        return None
    return settings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Start the Pangchong API safely")
    parser.add_argument(
        "--check",
        action="store_true",
        help="validate environment configuration and exit without starting a server",
    )
    args = parser.parse_args(argv)

    settings = _load_settings()
    if settings is None:
        return 2

    if args.check:
        print(f"Startup configuration valid for APP_ENV={settings.APP_ENV}")
        return 0

    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.RELOAD,
        workers=1 if settings.RELOAD else settings.WEB_CONCURRENCY,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
