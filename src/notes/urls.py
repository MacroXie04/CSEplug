"""URL configuration for notes app."""

from django.urls import path

from .views import LectureNoteUploadView

app_name = "notes"


urlpatterns = [
    path("upload/", LectureNoteUploadView.as_view(), name="upload"),
]

