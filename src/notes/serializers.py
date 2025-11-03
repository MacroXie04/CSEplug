"""Serializers for collaborative notes."""

from rest_framework import serializers

from .models import NotesPage, NotesShape


class NotesShapeSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotesShape
        fields = ("id", "version", "data", "created_at")
        read_only_fields = ("id", "created_at")


class NotesPageSerializer(serializers.ModelSerializer):
    shapes = NotesShapeSerializer(many=True, read_only=True)

    class Meta:
        model = NotesPage
        fields = (
            "id",
            "course",
            "author",
            "order_index",
            "data",
            "thumbnail_src",
            "thumbnail_dark_src",
            "created_at",
            "updated_at",
            "shapes",
        )
        read_only_fields = ("id", "author", "created_at", "updated_at", "shapes")

