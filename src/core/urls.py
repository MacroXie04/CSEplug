"""Core URL configuration for CSE Plug."""

from django.contrib import admin
from django.urls import path, include
from graphene_django.views import GraphQLView


urlpatterns = [
    path("admin/", admin.site.urls),
    path("graphql/", GraphQLView.as_view(graphiql=True)),
    path("api/accounts/", include("accounts.urls", namespace="accounts")),
    path("api/courses/", include("courses.urls", namespace="courses")),
    path("api/assignments/", include("assignments.urls", namespace="assignments")),
    path("api/notes/", include("notes.urls", namespace="notes")),
    path("api/support/", include("support.urls", namespace="support")),
]

