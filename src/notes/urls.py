"""URL configuration for notes app."""

from django.urls import path

from .views import NotesPageCreateView

app_name = "notes"


urlpatterns = [
    path("pages/", NotesPageCreateView.as_view(), name="create-page"),
]

