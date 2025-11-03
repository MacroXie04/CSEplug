"""User models for CSE Plug."""

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Application user model placeholder.

    Role-specific fields will be added during the authentication implementation stage.
    """

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

