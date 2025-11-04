"""Core URL configuration for CSE Plug."""

from django.contrib import admin
from django.urls import path, include
from django.views.decorators.csrf import csrf_exempt
from graphene_django.views import GraphQLView


urlpatterns = [
    path("admin/", admin.site.urls),
    path("graphql/", csrf_exempt(GraphQLView.as_view(graphiql=True))),
    path("api/accounts/", include("accounts.api.urls", namespace="accounts")),
    path("api/courses/", include("courses.urls", namespace="courses")),
    path("api/assignments/", include("assignments.urls", namespace="assignments")),
]

