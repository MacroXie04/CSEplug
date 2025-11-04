"""Authentication helpers for JWT cookies."""

from typing import Optional, Tuple

from django.contrib.auth.models import AbstractBaseUser
from django.http import HttpRequest
from rest_framework_simplejwt.authentication import JWTAuthentication

from .constants import ACCESS_COOKIE_NAME


class CookieJWTAuthentication(JWTAuthentication):
    """Authentication class that reads JWT access tokens from HttpOnly cookies."""

    def authenticate(self, request: HttpRequest) -> Optional[Tuple[AbstractBaseUser, str]]:
        header = self.get_header(request)
        if header is not None:
            return super().authenticate(request)

        raw_token = request.COOKIES.get(ACCESS_COOKIE_NAME)
        if raw_token is None:
            return None

        validated_token = self.get_validated_token(raw_token)
        return self.get_user(validated_token), validated_token

