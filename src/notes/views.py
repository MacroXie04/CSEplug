"""API views for notes pages (temporary REST support)."""

from rest_framework import permissions, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from courses.models import Course, CourseMembership

from .models import NotesPage
from .serializers import NotesPageSerializer


class NotesPageCreateView(APIView):
    """Create a notes page entry via REST (GraphQL preferred)."""

    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, *args, **kwargs):  # noqa: D401
        course_id = request.data.get("course")
        if not course_id:
            raise ValidationError({"course": "Course is required."})

        try:
            course = Course.objects.get(pk=course_id)
        except Course.DoesNotExist as exc:
            raise ValidationError({"course": "Course not found."}) from exc

        membership_exists = CourseMembership.objects.filter(course=course, user=request.user).exists()
        if not membership_exists and not request.user.is_superuser:
            raise ValidationError("You are not a member of this course.")

        serializer = NotesPageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        notes_page: NotesPage = serializer.save(author=request.user)
        return Response(NotesPageSerializer(notes_page).data, status=status.HTTP_201_CREATED)

