"""API views for lecture notes."""

from rest_framework import permissions, status
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from courses.models import Course

from .models import LectureNote
from .serializers import LectureNoteSerializer


class LectureNoteUploadView(APIView):
    """Handle lecture note uploads via multipart requests."""

    permission_classes = (permissions.IsAuthenticated,)
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):  # noqa: D401
        user = request.user
        if not (getattr(user, "is_teacher", False) or getattr(user, "is_administrator", False) or user.is_superuser):
            raise PermissionDenied("Only teachers can upload lecture notes.")

        course_id = request.data.get("course")
        if not course_id:
            raise ValidationError({"course": "Course is required."})

        try:
            course = Course.objects.get(pk=course_id)
        except Course.DoesNotExist as exc:
            raise ValidationError({"course": "Course not found."}) from exc

        if course.instructor_id != user.id and not (getattr(user, "is_administrator", False) or user.is_superuser):
            raise PermissionDenied("You do not teach this course.")

        serializer = LectureNoteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        note: LectureNote = serializer.save(author=user, course=course)
        output = LectureNoteSerializer(instance=note, context={"request": request})
        return Response(output.data, status=status.HTTP_201_CREATED)

