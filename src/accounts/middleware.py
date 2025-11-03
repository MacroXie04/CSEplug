"""Middleware for authenticating JWT cookies on non-DRF views."""

from __future__ import annotations

from django.contrib.auth.models import AnonymousUser
from django.utils.deprecation import MiddlewareMixin

from .authentication import CookieJWTAuthentication


class JWTCookieMiddleware(MiddlewareMixin):
    """Attach authenticated user to the request from JWT cookies.

    This allows standard Django views (GraphQL, Channels HTTP handshake) to
    benefit from the same JWT cookie authentication mechanism used by DRF.
    """

    def __init__(self, get_response):
        super().__init__(get_response)
        self.authenticator = CookieJWTAuthentication()

    def process_request(self, request):  # noqa: D401
        if getattr(request, "user", None) and request.user.is_authenticated:
            return

        try:
            auth_result = self.authenticator.authenticate(request)
        except Exception:  # pragma: no cover - defensive
            auth_result = None

        if auth_result is not None:
            user, _ = auth_result
            request.user = user
        elif not getattr(request, "user", None):
            request.user = AnonymousUser()

