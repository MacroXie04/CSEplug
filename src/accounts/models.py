"""User models for CSE Plug."""

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Application user model with role support."""

    class Roles(models.TextChoices):
        STUDENT = "student", "Student"
        TEACHER = "teacher", "Teacher"
        ADMIN = "admin", "Administrator"

    role = models.CharField(
        max_length=20,
        choices=Roles.choices,
        default=Roles.STUDENT,
        help_text="Determines the user's application privileges.",
    )

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

    @property
    def is_student(self) -> bool:
        return self.role == self.Roles.STUDENT

    @property
    def is_teacher(self) -> bool:
        return self.role == self.Roles.TEACHER

    @property
    def is_administrator(self) -> bool:
        return self.role == self.Roles.ADMIN

