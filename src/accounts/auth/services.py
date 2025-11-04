"""Service helpers for authentication flows."""

from typing import Tuple

from django.conf import settings
from django.utils import timezone
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from ..models import User
from .constants import (
    ACCESS_COOKIE_NAME,
    ACCESS_COOKIE_PATH,
    COOKIE_SAMESITE,
    REFRESH_COOKIE_NAME,
    REFRESH_COOKIE_PATH,
)


SECURE_COOKIE = not settings.DEBUG
ACCESS_MAX_AGE = int(settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"].total_seconds())
REFRESH_MAX_AGE = int(settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"].total_seconds())


def generate_tokens(user: User) -> Tuple[str, str]:
    """Return (access, refresh) token pair for the given user."""

    refresh = RefreshToken.for_user(user)
    access = refresh.access_token
    return str(access), str(refresh)


def set_jwt_cookies(response: Response, access_token: str, refresh_token: str) -> None:
    """Attach JWT cookies to the response."""

    response.set_cookie(
        ACCESS_COOKIE_NAME,
        access_token,
        max_age=ACCESS_MAX_AGE,
        httponly=True,
        secure=SECURE_COOKIE,
        samesite=COOKIE_SAMESITE,
        path=ACCESS_COOKIE_PATH,
    )
    response.set_cookie(
        REFRESH_COOKIE_NAME,
        refresh_token,
        max_age=REFRESH_MAX_AGE,
        httponly=True,
        secure=SECURE_COOKIE,
        samesite=COOKIE_SAMESITE,
        path=REFRESH_COOKIE_PATH,
    )


def clear_jwt_cookies(response: Response) -> None:
    """Remove JWT cookies by setting expired cookies."""

    expired = timezone.now()
    response.set_cookie(
        ACCESS_COOKIE_NAME,
        "",
        expires=expired,
        httponly=True,
        secure=SECURE_COOKIE,
        samesite=COOKIE_SAMESITE,
        path=ACCESS_COOKIE_PATH,
    )
    response.set_cookie(
        REFRESH_COOKIE_NAME,
        "",
        expires=expired,
        httponly=True,
        secure=SECURE_COOKIE,
        samesite=COOKIE_SAMESITE,
        path=REFRESH_COOKIE_PATH,
    )


def blacklist_refresh_token(refresh_token: str) -> None:
    """Black-list a refresh token if the blacklist app is enabled."""

    if not refresh_token:
        return

    try:
        token = RefreshToken(refresh_token)
        token.blacklist()
    except TokenError:
        return

