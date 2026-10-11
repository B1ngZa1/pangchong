"""Regression tests for the browser session cookie boundary."""

from fastapi import Request, Response
from fastapi import HTTPException

from app.api.auth import _clear_refresh_cookie, _set_refresh_cookie, _token_response, refresh_token
from app.core.security import create_refresh_token
from app.models.user import User


class FakeResult:
    def __init__(self, value):
        self.value = value

    def scalar_one_or_none(self):
        return self.value


class FakeDb:
    def __init__(self, user):
        self.user = user

    async def execute(self, statement):
        assert statement.column_descriptions[0]["entity"] is User
        return FakeResult(self.user)


def test_refresh_cookie_is_httponly_and_scoped_to_auth_api():
    response = Response()
    _set_refresh_cookie(response, "refresh-value")
    header = response.headers["set-cookie"].lower()

    assert "pangchong_refresh=refresh-value" in header
    assert "httponly" in header
    assert "samesite=lax" in header
    assert "path=/api/auth" in header

    cleared = Response()
    _clear_refresh_cookie(cleared)
    assert "max-age=0" in cleared.headers["set-cookie"].lower()


def test_auth_response_does_not_expose_refresh_token_without_explicit_opt_in():
    request = Request(
        {
            "type": "http",
            "method": "POST",
            "path": "/api/auth/login",
            "headers": [],
            "query_string": b"",
            "server": ("testserver", 80),
            "client": ("testclient", 50000),
            "scheme": "http",
        }
    )
    tokens = {"access_token": "access", "refresh_token": "refresh", "token_type": "bearer"}

    assert _token_response(tokens, request)["refresh_token"] is None

    legacy_request = Request(
        {
            "type": "http",
            "method": "POST",
            "path": "/api/auth/login",
            "headers": [(b"x-token-transport", b"body")],
            "query_string": b"",
            "server": ("testserver", 80),
            "client": ("testclient", 50000),
            "scheme": "http",
        }
    )
    assert _token_response(tokens, legacy_request)["refresh_token"] == "refresh"


async def _request_with_cookie(value: str) -> Request:
    return Request(
        {
            "type": "http",
            "method": "POST",
            "path": "/api/auth/refresh",
            "headers": [(b"cookie", f"pangchong_refresh={value}".encode())],
            "query_string": b"",
            "server": ("testserver", 80),
            "client": ("testclient", 50000),
            "scheme": "http",
        }
    )


async def test_refresh_accepts_cookie_without_a_javascript_readable_body():
    user = User(id="11111111-1111-1111-1111-111111111111", is_active=True)
    refresh = create_refresh_token({"sub": str(user.id)})
    request = await _request_with_cookie(refresh)
    response = Response()

    result = await refresh_token(request, response, None, FakeDb(user))

    assert result["access_token"]
    assert "pangchong_refresh=" in response.headers["set-cookie"]


async def test_refresh_rejects_missing_cookie():
    request = await _request_with_cookie("")
    response = Response()

    try:
        await refresh_token(request, response, None, FakeDb(None))
    except HTTPException as exc:
        assert exc.status_code == 401
    else:  # pragma: no cover - a successful refresh would be a security bug
        raise AssertionError("missing refresh cookie was accepted")
