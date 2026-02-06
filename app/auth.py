"""BasicAuth for UI routes."""
import base64
from fastapi import Request, HTTPException, status
from starlette.authentication import AuthenticationBackend, AuthCredentials, SimpleUser
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.requests import HTTPConnection

from app.config import settings


def _check_basic_auth(authorization: str) -> bool:
    """Verify Basic auth credentials."""
    if not settings.UI_USER or not settings.UI_PASS:
        return True  # No auth configured
    try:
        scheme, _, credentials = authorization.partition(" ")
        if scheme.lower() != "basic":
            return False
        decoded = base64.b64decode(credentials).decode("utf-8")
        user, _, password = decoded.partition(":")
        return user == settings.UI_USER and password == settings.UI_PASS
    except Exception:
        return False


async def basic_auth_dependency(request: Request):
    """Dependency for UI routes: require BasicAuth when configured."""
    if not settings.UI_USER or not settings.UI_PASS:
        return
    auth = request.headers.get("Authorization")
    if not auth or not _check_basic_auth(auth):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Basic realm=\"News Studio\""},
        )
