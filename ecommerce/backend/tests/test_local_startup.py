"""Direct Windows startup must work without PYTHONIOENCODING overrides."""

import io
import sys
from unittest.mock import AsyncMock

import pytest

from app import main


@pytest.mark.parametrize("encoding", ["gbk", "cp1252"])
async def test_lifespan_starts_and_closes_with_windows_console_encoding(
    monkeypatch, tmp_path, encoding
):
    init_db = AsyncMock()
    close_db = AsyncMock()
    monkeypatch.setattr(main, "init_db", init_db)
    monkeypatch.setattr(main, "close_db", close_db)
    monkeypatch.setattr(main.settings, "APP_ENV", "development")
    monkeypatch.setattr(main.settings, "UPLOAD_DIR", str(tmp_path / "uploads"))

    with io.TextIOWrapper(io.BytesIO(), encoding=encoding, errors="strict") as stdout:
        with monkeypatch.context() as console:
            console.setattr(sys, "stdout", stdout)
            async with main.lifespan(main.app):
                init_db.assert_awaited_once()
            close_db.assert_awaited_once()
            stdout.flush()

    assert (tmp_path / "uploads").is_dir()
