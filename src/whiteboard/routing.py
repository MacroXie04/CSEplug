"""Routing configuration for Channels whiteboard consumers."""

from django.urls import re_path

from .consumers import WhiteboardConsumer


websocket_urlpatterns = [
    re_path(r"^ws/whiteboard/(?P<session_id>[0-9a-f-]+)/$", WhiteboardConsumer.as_asgi()),
]

