from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.contrib.auth.models import User
import uuid


class UserProfile(models.Model):
    """Extended profile data for Django users."""

    # Link to the built-in User model
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    # user uuid for external reference
    user_uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    GENDER_ORIENTATION_CHOICES = [
        # Binary
        ("male", "Male"),
        ("female", "Female"),

        # Transgender Identities
        ("transgender_male", "Transgender Male"),
        ("transgender_female", "Transgender Female"),
        ("trans_masculine", "Transmasculine"),
        ("trans_feminine", "Transfeminine"),

        # Non-binary Spectrum
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

        # Cultural and Regional Terms
        ("hijra", "Hijra (South Asian)"),
        ("fa_afafine", "Fa'afafine (Samoa)"),
        ("fa_tama", "Fa’atama (Samoa)"),
        ("bakla", "Bakla (Philippines)"),
        ("kathoey", "Kathoey (Thailand)"),
        ("waria", "Waria (Indonesia)"),
        ("muxhe", "Muxhe (Zapotec, Mexico)"),
        ("sworn_virgin", "Sworn Virgin (Balkan)"),

        # Orientation/Gender-expression related identities
        ("butch", "Butch"),
        ("femme", "Femme"),
        ("androgynous", "Androgynous"),
        ("masculine_presenting", "Masculine-presenting"),
        ("feminine_presenting", "Feminine-presenting"),

        # Fluid/Undefined/Other
        ("questioning", "Questioning"),
        ("other", "Other"),
        ("prefer_not_to_say", "Prefer not to say"),
    ]

    gender_orientation = models.CharField(
        max_length=100,
        choices=GENDER_ORIENTATION_CHOICES,
        null=True,
        blank=True,
    )
    user_uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user_profile_img = models.TextField(
        null=True,
        blank=True,
        help_text=(
            "Base64 encoded PNG of the user's 128*128 avatar. No data-URI prefix."
        ),
        verbose_name="avatar (Base64)",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"Profile of {self.user.username}"

def is_palindrome(word):
    word = word.lower()
    return word == word[::-1]