"""Serializers for lecture notes."""

from rest_framework import serializers

from .models import LectureNote


class LectureNoteSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source="course.title", read_only=True)
    author_username = serializers.CharField(source="author.username", read_only=True)

    class Meta:
        model = LectureNote
        fields = (
            "id",
            "course",
            "course_title",
            "author",
            "author_username",
            "title",
            "description",
            "file",
            "is_published",
            "published_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "author",
            "author_username",
            "course_title",
            "is_published",
            "published_at",
            "updated_at",
        )

