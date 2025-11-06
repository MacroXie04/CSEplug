"""Course core models."""

from __future__ import annotations

from django.conf import settings
from django.db import models

from common.models import DateTimeTimezoneField, TimestampedModel


class Course(TimestampedModel):
    """Represents a course available on the platform."""

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    syllabus = models.TextField(blank=True)
    policy = models.TextField(blank=True)

    start_date_utc = models.DateTimeField(null=True, blank=True)
    start_date_timezone = models.CharField(max_length=64, blank=True)
    start_date = DateTimeTimezoneField("start_date_utc", "start_date_timezone")

    end_date_utc = models.DateTimeField(null=True, blank=True)
    end_date_timezone = models.CharField(max_length=64, blank=True)
    end_date = DateTimeTimezoneField("end_date_utc", "end_date_timezone")

    class Meta:
        ordering = ("title", "id")
        verbose_name = "Course"
        verbose_name_plural = "Courses"

    def __str__(self) -> str:
        return self.title

    # Permission helpers -------------------------------------------------

    def _membership_for(self, user):
        if not getattr(user, "is_authenticated", False):
            return None
        return self.memberships.filter(user=user).first()

    def can_view(self, user) -> bool:
        if not getattr(user, "is_authenticated", False):
            return False
        if user.is_staff:
            return True
        return self._membership_for(user) is not None

    def can_edit(self, user) -> bool:
        membership = self._membership_for(user)
        if membership and membership.role in CourseMembership.InstructorRoles:
            return True
        return bool(getattr(user, "is_staff", False))

    def can_delete(self, user) -> bool:
        return self.can_edit(user)


class CourseMembership(TimestampedModel):
    """Connects users to courses with a specific role."""

    class Roles(models.TextChoices):
        INSTRUCTOR = "instructor", "Instructor"
        TEACHING_ASSISTANT = "teaching_assistant", "Teaching Assistant"
        STUDENT = "student", "Student"

    InstructorRoles = {Roles.INSTRUCTOR, Roles.TEACHING_ASSISTANT}

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="course_memberships",
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="memberships",
    )
    role = models.CharField(max_length=32, choices=Roles.choices)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "course")
        verbose_name = "Course Membership"
        verbose_name_plural = "Course Memberships"

    def __str__(self) -> str:
        return f"{self.user.email} → {self.course.title} ({self.get_role_display()})"

    # Permission helpers -------------------------------------------------

    def can_view(self, user) -> bool:
        if not getattr(user, "is_authenticated", False):
            return False
        if user.is_staff:
            return True
        if user.pk == self.user_id:
            return True
        return self.course.memberships.filter(user=user).exists()

    def can_edit(self, user) -> bool:
        if not getattr(user, "is_authenticated", False):
            return False
        if user.is_staff:
            return True
        membership = self.course.memberships.filter(user=user).first()
        return bool(membership and membership.role in self.InstructorRoles)

    def can_delete(self, user) -> bool:
        return self.can_edit(user)

    # Role helpers -------------------------------------------------------

    @property
    def is_instructor(self) -> bool:
        return self.role == self.Roles.INSTRUCTOR

    @property
    def is_teaching_assistant(self) -> bool:
        return self.role == self.Roles.TEACHING_ASSISTANT

    @property
    def is_student(self) -> bool:
        return self.role == self.Roles.STUDENT


__all__ = ["Course", "CourseMembership"]


