"""Create the first production administrator exactly once.

The password is accepted from a protected file, standard input, or an interactive
prompt. It is never accepted as a command-line argument or printed.
"""

from __future__ import annotations

import argparse
import asyncio
from getpass import getpass
from pathlib import Path
import sys

from pydantic import ValidationError
from sqlalchemy import select, text
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from ..core.database import AsyncSessionLocal
from ..core.security import get_password_hash
from ..models.user import User
from ..schemas.user import UserRegister


class AdminAlreadyExists(RuntimeError):
    """Raised when the one-time administrator slot has already been used."""


_KNOWN_WEAK_ADMIN_PASSWORDS = {
    "admin123456",
    "password1",
    "test123456",
}


def _validate_initial_admin_password(password: str, *, username: str, email: str) -> None:
    """Apply a stricter floor than ordinary user registration to the first admin."""
    normalized = password.casefold()
    email_local_part = email.partition("@")[0].casefold()
    if (
        len(password) < 16
        or len(set(password)) < 8
        or normalized in _KNOWN_WEAK_ADMIN_PASSWORDS
        or username.casefold() in normalized
        or (email_local_part and email_local_part in normalized)
    ):
        raise ValueError(
            "initial admin password must be at least 16 characters, contain at least "
            "8 distinct characters, and not contain the username or email local part"
        )


def _read_password(args: argparse.Namespace) -> str:
    if args.password_file:
        password = Path(args.password_file).read_text(encoding="utf-8").rstrip("\r\n")
    elif args.password_stdin:
        password = sys.stdin.readline().rstrip("\r\n")
    else:
        password = getpass("Initial admin password: ")
        confirmation = getpass("Confirm initial admin password: ")
        if password != confirmation:
            raise ValueError("password confirmation does not match")

    if not password:
        raise ValueError("admin password must not be empty")
    return password


async def create_initial_admin(*, username: str, email: str, password: str) -> User:
    _validate_initial_admin_password(password, username=username, email=email)
    validated = UserRegister(username=username, email=email, password=password)

    async with AsyncSessionLocal() as session:
        async with session.begin():
            # Serialize concurrent bootstrap attempts even while the admin table is empty.
            await session.execute(text("SELECT pg_advisory_xact_lock(102, 103)"))
            existing_admin = await session.scalar(
                select(User.id).where(User.is_admin.is_(True)).limit(1)
            )
            if existing_admin is not None:
                raise AdminAlreadyExists(
                    "an administrator already exists; the one-time bootstrap is disabled"
                )

            admin = User(
                username=validated.username,
                email=str(validated.email),
                password_hash=get_password_hash(validated.password),
                nickname="Administrator",
                is_active=True,
                is_admin=True,
            )
            session.add(admin)
            await session.flush()
            return admin


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create the first administrator; refuses once any admin exists"
    )
    parser.add_argument("--username", required=True)
    parser.add_argument("--email", required=True)
    password_source = parser.add_mutually_exclusive_group()
    password_source.add_argument(
        "--password-file",
        help="read the password from a mounted secret file",
    )
    password_source.add_argument(
        "--password-stdin",
        action="store_true",
        help="read one password line from standard input",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    try:
        password = _read_password(args)
        admin = asyncio.run(
            create_initial_admin(
                username=args.username,
                email=args.email,
                password=password,
            )
        )
    except AdminAlreadyExists as exc:
        print(f"Admin bootstrap refused: {exc}", file=sys.stderr)
        return 3
    except ValidationError as exc:
        invalid_fields = sorted(
            {
                str(error["loc"][0])
                for error in exc.errors(include_url=False, include_input=False)
                if error.get("loc")
            }
        )
        field_summary = ", ".join(invalid_fields) or "input"
        print(
            f"Admin bootstrap input rejected: invalid {field_summary}",
            file=sys.stderr,
        )
        return 2
    except ValueError as exc:
        print(f"Admin bootstrap input rejected: {exc}", file=sys.stderr)
        return 2
    except IntegrityError:
        print(
            "Admin bootstrap failed: username or email is already in use; no admin was created",
            file=sys.stderr,
        )
        return 4
    except SQLAlchemyError as exc:
        print(f"Admin bootstrap database failure: {exc.__class__.__name__}", file=sys.stderr)
        return 5

    print(f"Created initial administrator {admin.username!r} ({admin.email})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
