"""Custom authentication backends for the accounts app."""

from __future__ import annotations

from typing import Any

from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend


UserModel = get_user_model()


class EmailBackend(ModelBackend):
    """Authenticate users by their email address."""

    def authenticate(
        self,
        request,
        username: str | None = None,
        password: str | None = None,
        **kwargs: Any,
    ):
        if username is None:
            username = kwargs.get(UserModel.USERNAME_FIELD)

        if username is None or password is None:
            return None

        try:
            user = UserModel._default_manager.get(email__iexact=username)
        except UserModel.DoesNotExist:
            UserModel().set_password(password)
            return None

        if user.check_password(password) and self.user_can_authenticate(user):
            return user

        return None


__all__ = ["EmailBackend"]


