"""User models for CSE Plug."""

from __future__ import annotations

import uuid

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models

from common.models import BaseModelWithPermissions, TimestampedModel


class UserManager(BaseUserManager):
    """Custom user manager that uses email as the unique identifier."""

    use_in_migrations = True

    def _create_user(self, email: str, password: str | None, **extra_fields):
        if not email:
            raise ValueError("The email address must be set.")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email: str, password: str | None = None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email: str, password: str, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser, BaseModelWithPermissions):
    """Application user model with email as the primary login field."""

    username = None
    email = models.EmailField("email address", unique=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS: list[str] = []

    objects = UserManager()

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

    def can_view(self, user) -> bool:
        if not getattr(user, "is_authenticated", False):
            return False
        return user.is_staff or user.pk == self.pk

    def can_edit(self, user) -> bool:
        if not getattr(user, "is_authenticated", False):
            return False
        return user.is_staff or user.pk == self.pk

    def can_delete(self, user) -> bool:
        if not getattr(user, "is_authenticated", False):
            return False
        return user.is_staff and user.pk != self.pk


class UserProfile(TimestampedModel):
    """Stores additional profile information for users."""

    GENDER_ORIENTATION_CHOICES = [
        ("male", "Male"),
        ("female", "Female"),
        ("transgender_male", "Transgender Male"),
        ("transgender_female", "Transgender Female"),
        ("trans_masculine", "Transmasculine"),
        ("trans_feminine", "Transfeminine"),
        ("non_binary", "Non-binary"),
        ("genderqueer", "Genderqueer"),
        ("genderfluid", "Genderfluid"),
        ("agender", "Agender"),
        ("bigender", "Bigender"),
        ("pangender", "Pangender"),
        ("androgyne", "Androgyne"),
        ("neutrois", "Neutrois"),
        ("demiboy", "Demiboy"),
        ("demigirl", "Demigirl"),
        ("polygender", "Polygender"),
        ("third_gender", "Third Gender"),
        ("two_spirit", "Two-Spirit (Indigenous)"),
        ("genderflux", "Genderflux"),
        ("genderfae", "Genderfae"),
        ("genderfluid_flux", "Genderfluid Flux"),
        ("gender_apath", "Apathgender"),
        ("maverique", "Maverique"),
        ("intergender", "Intergender"),
        ("intersex", "Intersex"),
        ("hijra", "Hijra (South Asian)"),
        ("fa_afafine", "Fa'afafine (Samoa)"),
        ("fa_tama", "Fa’atama (Samoa)"),
        ("bakla", "Bakla (Philippines)"),
        ("kathoey", "Kathoey (Thailand)"),
        ("waria", "Waria (Indonesia)"),
        ("muxhe", "Muxhe (Zapotec, Mexico)"),
        ("sworn_virgin", "Sworn Virgin (Balkan)"),
        ("butch", "Butch"),
        ("femme", "Femme"),
        ("androgynous", "Androgynous"),
        ("masculine_presenting", "Masculine-presenting"),
        ("feminine_presenting", "Feminine-presenting"),
        ("questioning", "Questioning"),
        ("other", "Other"),
        ("prefer_not_to_say", "Prefer not to say"),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    user_uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    gender_orientation = models.CharField(
        max_length=100,
        choices=GENDER_ORIENTATION_CHOICES,
        null=True,
        blank=True,
    )
    user_profile_img = models.TextField(
        null=True,
        blank=True,
        help_text=(
            "Base64 encoded PNG of the user's 128*128 avatar. No data-URI prefix."
        ),
        verbose_name="avatar (Base64)",
    )

    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"

    def __str__(self) -> str:
        return f"Profile of {self.user.email}"

    def can_view(self, user) -> bool:
        if not getattr(user, "is_authenticated", False):
            return False
        return user.is_staff or user.pk == self.user_id

    def can_edit(self, user) -> bool:
        if not getattr(user, "is_authenticated", False):
            return False
        return user.is_staff or user.pk == self.user_id

    def can_delete(self, user) -> bool:
        if not getattr(user, "is_authenticated", False):
            return False
        return user.is_staff


__all__ = ["User", "UserManager", "UserProfile"]

