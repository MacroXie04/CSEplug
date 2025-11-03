"""Channels consumers for real-time whiteboard collaboration."""

from __future__ import annotations

from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.contrib.auth import get_user_model
from django.utils import timezone

from .models import WhiteboardEvent, WhiteboardSession

User = get_user_model()


class WhiteboardConsumer(AsyncJsonWebsocketConsumer):
    """Handle whiteboard collaboration events over WebSocket."""

    async def connect(self):
        user = self.scope.get("user")
        if not user or not user.is_authenticated:
            await self.close(code=4401)
            return

        self.session_id = self.scope["url_route"]["kwargs"].get("session_id")
        try:
            session = await WhiteboardSession.objects.select_related("course", "course__instructor").aget(pk=self.session_id)
        except WhiteboardSession.DoesNotExist:
            await self.close(code=4404)
            return

        course = session.course
        is_enrolled = await course.students.filter(pk=user.id).aexists()
        if not (
            user.is_superuser
            or getattr(user, "is_administrator", False)
            or course.instructor_id == user.id
            or is_enrolled
        ):
            await self.close(code=4403)
            return

        self.session = session
        self.group_name = f"whiteboard-{self.session_id}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

        await self.send_json(
            {
                "type": "session.init",
                "payload": {
                    "sessionId": str(self.session_id),
                    "title": self.session.title,
                    "strokes": self.session.strokes,
                    "snapshot": self.session.snapshot,
                },
            }
        )

    async def disconnect(self, code):  # noqa: D401
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive_json(self, content, **kwargs):
        action = content.get("action")
        payload = content.get("payload", {})
        user = self.scope["user"]

        if action == "stroke.append":
            await self.handle_append_stroke(user, payload)
        elif action == "board.clear":
            await self.handle_clear_board(user)
        elif action == "snapshot.save":
            await self.handle_save_snapshot(user, payload)

    async def handle_append_stroke(self, user: User, payload: dict):
        stroke = payload.get("stroke")
        if stroke is None:
            return
        self.session.strokes.append(stroke)
        await self._persist_session(user, {"stroke": stroke, "action": "stroke.append"})
        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "broadcast.event",
                "event": "stroke.append",
                "data": {
                    "stroke": stroke,
                    "author": user.username,
                    "timestamp": timezone.now().isoformat(),
                },
            },
        )

    async def handle_clear_board(self, user: User):
        self.session.strokes = []
        await self._persist_session(user, {"action": "board.clear"})
        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "broadcast.event",
                "event": "board.clear",
                "data": {
                    "author": user.username,
                    "timestamp": timezone.now().isoformat(),
                },
            },
        )

    async def handle_save_snapshot(self, user: User, payload: dict):
        snapshot = payload.get("snapshot", "")
        strokes = payload.get("strokes")
        if strokes is not None:
            self.session.strokes = strokes
        if snapshot:
            self.session.snapshot = snapshot
        await self._persist_session(user, {"action": "snapshot.save", "snapshot": snapshot})
        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "broadcast.event",
                "event": "snapshot.save",
                "data": {
                    "author": user.username,
                    "timestamp": timezone.now().isoformat(),
                    "snapshot": snapshot,
                },
            },
        )

    async def broadcast_event(self, event):  # noqa: D401
        await self.send_json({"type": event["event"], "payload": event["data"]})

    async def _persist_session(self, user: User, payload: dict):
        await WhiteboardSession.objects.filter(pk=self.session.pk).aupdate(
            strokes=self.session.strokes,
            snapshot=self.session.snapshot,
            updated_at=timezone.now(),
        )
        await WhiteboardEvent.objects.acreate(session=self.session, sender=user, payload=payload)

