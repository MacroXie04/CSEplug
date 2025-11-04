"""Database models for course management."""

from django.conf import settings
from django.db import models

class Course(models.Model):

    title = models.CharField(max_length=255)

class CourseStudent(models.Model):

    # foreign key link to course model
    course = models.OneToOneField(Course, on_delete=models.CASCADE)


class CourseAdmin(models.Model):

    # foreign key link to course model
    course = models.OneToOneField(Course, on_delete=models.CASCADE)

