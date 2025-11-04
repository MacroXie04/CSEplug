"""Admin registrations for accounts app."""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.utils.html import mark_safe
from django.utils.translation import gettext_lazy as _

from .models import User, UserProfile

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """
    Admin configuration for the UserProfile model.
    """

    # Fields to display in the main list view
    list_display = (
        'user',
        'user_uuid',
        'gender_orientation',
        'get_avatar_preview_list'
    )

    # Enable search on these fields
    search_fields = ('user__username', 'user__email', 'user_uuid')

    # Add a filter sidebar for gender_orientation
    list_filter = ('gender_orientation',)

    # Make fields read-only in the detail/edit view
    readonly_fields = ('user_uuid', 'get_avatar_preview_detail')

    # Customize the layout of the edit/add form
    fieldsets = (
        (None, {
            'fields': ('user', 'user_uuid')
        }),
        ('Profile Details', {
            'fields': ('gender_orientation', 'user_profile_img', 'get_avatar_preview_detail')
        }),
    )

    def get_avatar_preview_list(self, obj):
        """
        Returns a small, circular <img> tag for the list_display.
        """
        if obj.user_profile_img:
            # Display a small, rounded avatar in the list
            return mark_safe(
                f'<img src="data:image/png;base64,{obj.user_profile_img}" '
                'style="width: 40px; height: 40px; border-radius: 50%; object-fit: cover;" />'
            )
        return "No Avatar"

    get_avatar_preview_list.short_description = 'Avatar'

    def get_avatar_preview_detail(self, obj):
        """
        Returns a larger <img> tag for the readonly_fields in the detail view.
        """
        if obj.user_profile_img:
            # Display the 128x128 avatar in the detail view
            return mark_safe(
                f'<img src="data:image/png;base64,{obj.user_profile_img}" '
                'style="max-width: 128px; max-height: 128px; border: 1px solid #ddd; border-radius: 4px;" />'
            )
        return "No avatar provided"

    get_avatar_preview_detail.short_description = 'Avatar Preview'


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    list_display = ("email", "first_name", "last_name", "is_staff", "is_active")
    list_filter = ("is_staff", "is_superuser", "is_active")
    search_fields = ("email", "first_name", "last_name")
    ordering = ("email",)

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (_("Personal info"), {"fields": ("first_name", "last_name")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2"),
            },
        ),
    )
