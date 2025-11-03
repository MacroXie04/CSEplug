from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
import uuid

class UserProfile(models.Model):

    # foreign key to the custom User model
    user = models.OneToOneField(
        AbstractUser,
        on_delete=models.CASCADE,
        related_name="profile",
    )
