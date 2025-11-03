"""GraphQL schema entrypoint."""

import base64
from datetime import datetime
from typing import Optional

import graphene
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.db.models import Q
from django.utils import timezone
from graphene_django import DjangoObjectType
from graphql import GraphQLError

from assignments.models import Assignment, Grade, Submission
from courses.models import Course, CourseAnnouncement
from notes.models import LectureNote
from support.models import ChatMessage, SupportTicket
from whiteboard.models import WhiteboardEvent, WhiteboardSession

User = get_user_model()


def require_authenticated_user(info) -> User:
    user = info.context.user
    if not user.is_authenticated:
        raise GraphQLError("Authentication required.")
    return user


def decode_base64_file(data: str, filename: str) -> ContentFile:
    if "," in data:
        data = data.split(",", 1)[1]
    try:
        decoded_file = base64.b64decode(data)
    except (ValueError, TypeError) as exc:  # pragma: no cover - defensive
        raise GraphQLError("Invalid file encoding.") from exc
    return ContentFile(decoded_file, name=filename)


class UserType(DjangoObjectType):
    class Meta:
        model = User
        fields = ("id", "username", "email", "first_name", "last_name", "role")


class CourseType(DjangoObjectType):
    class Meta:
        model = Course
        fields = (
            "id",
            "code",
            "title",
            "description",
            "syllabus",
            "start_date",
            "end_date",
            "instructor",
            "students",
            "created_at",
            "updated_at",
            "announcements",
            "assignments",
        )


class CourseAnnouncementType(DjangoObjectType):
    class Meta:
        model = CourseAnnouncement
        fields = (
            "id",
            "course",
            "author",
            "title",
            "body",
            "is_pinned",
            "created_at",
            "updated_at",
        )


class AssignmentType(DjangoObjectType):
    class Meta:
        model = Assignment
        fields = (
            "id",
            "course",
            "author",
            "title",
            "instructions_markdown",
            "due_at",
            "max_score",
            "is_published",
            "created_at",
            "updated_at",
        )


class SubmissionType(DjangoObjectType):
    class Meta:
        model = Submission
        fields = (
            "id",
            "assignment",
            "student",
            "content_markdown",
            "submitted_at",
            "updated_at",
            "grade",
        )


class GradeType(DjangoObjectType):
    class Meta:
        model = Grade
        fields = (
            "id",
            "submission",
            "grader",
            "score",
            "feedback_markdown",
            "graded_at",
        )


class LectureNoteType(DjangoObjectType):
    class Meta:
        model = LectureNote
        fields = (
            "id",
            "course",
            "author",
            "title",
            "description",
            "file",
            "is_published",
            "published_at",
            "updated_at",
        )


class SupportTicketType(DjangoObjectType):
    class Meta:
        model = SupportTicket
        fields = (
            "id",
            "requester",
            "course",
            "subject",
            "description",
            "status",
            "created_at",
            "updated_at",
            "messages",
        )


class ChatMessageType(DjangoObjectType):
    class Meta:
        model = ChatMessage
        fields = (
            "id",
            "ticket",
            "course",
            "author",
            "content",
            "created_at",
        )


class WhiteboardSessionType(DjangoObjectType):
    class Meta:
        model = WhiteboardSession
        fields = (
            "id",
            "course",
            "title",
            "created_by",
            "is_active",
            "strokes",
            "snapshot",
            "created_at",
            "updated_at",
            "events",
        )


class WhiteboardEventType(DjangoObjectType):
    class Meta:
        model = WhiteboardEvent
        fields = ("id", "session", "sender", "payload", "created_at")


class Query(graphene.ObjectType):
    """Root GraphQL query."""

    ping = graphene.String(description="Health check field")
    user_profile = graphene.Field(UserType)
    courses = graphene.List(CourseType, active_only=graphene.Boolean(default_value=False))
    course = graphene.Field(CourseType, id=graphene.ID(required=True))
    assignments = graphene.List(
        AssignmentType,
        course_id=graphene.ID(required=False),
        upcoming_only=graphene.Boolean(default_value=False),
    )
    submissions = graphene.List(
        SubmissionType,
        assignment_id=graphene.ID(required=False),
        student_id=graphene.ID(required=False),
    )
    lecture_notes = graphene.List(
        LectureNoteType,
        course_id=graphene.ID(required=False),
    )
    whiteboard_sessions = graphene.List(
        WhiteboardSessionType,
        course_id=graphene.ID(required=False),
        active_only=graphene.Boolean(default_value=False),
    )
    grades = graphene.List(
        GradeType,
        assignment_id=graphene.ID(required=False),
    )
    support_tickets = graphene.List(SupportTicketType)
    chat_messages = graphene.List(
        ChatMessageType,
        course_id=graphene.ID(required=False),
        ticket_id=graphene.ID(required=False),
    )

    def resolve_ping(self, info):  # noqa: D401
        return "pong"

    def resolve_user_profile(self, info):
        return require_authenticated_user(info)

    def resolve_courses(self, info, active_only=False):
        user = require_authenticated_user(info)
        qs = Course.objects.all().select_related("instructor").prefetch_related("students")
        if user.is_administrator or user.is_superuser:
            pass
        elif user.is_teacher:
            qs = qs.filter(Q(instructor=user) | Q(students=user)).distinct()
        else:
            qs = qs.filter(Q(students=user) | Q(instructor=user)).distinct()
        if active_only:
            today = timezone.now().date()
            qs = qs.filter(Q(end_date__isnull=True) | Q(end_date__gte=today))
        return qs

    def resolve_course(self, info, id):
        user = require_authenticated_user(info)
        try:
            course = Course.objects.select_related("instructor").get(pk=id)
        except Course.DoesNotExist as exc:  # pragma: no cover - defensive
            raise GraphQLError("Course not found.") from exc
        if user.is_administrator or user.is_superuser or course.instructor == user or user in course.students.all():
            return course
        raise GraphQLError("You do not have access to this course.")

    def resolve_assignments(self, info, course_id: Optional[str] = None, upcoming_only: bool = False):
        user = require_authenticated_user(info)
        qs = Assignment.objects.select_related("course", "author")
        if course_id:
            qs = qs.filter(course_id=course_id)
        if not (user.is_administrator or user.is_superuser):
            qs = qs.filter(
                Q(course__students=user)
                | Q(course__instructor=user)
                | Q(author=user)
            ).distinct()
        if upcoming_only:
            qs = qs.filter(Q(due_at__isnull=True) | Q(due_at__gte=timezone.now()))
        return qs

    def resolve_submissions(self, info, assignment_id: Optional[str] = None, student_id: Optional[str] = None):
        user = require_authenticated_user(info)
        qs = Submission.objects.select_related("assignment", "student", "assignment__course")
        if assignment_id:
            qs = qs.filter(assignment_id=assignment_id)
        if student_id:
            qs = qs.filter(student_id=student_id)
        if user.is_student:
            qs = qs.filter(student=user)
        elif user.is_teacher:
            qs = qs.filter(
                Q(assignment__course__instructor=user)
                | Q(student=user)
            ).distinct()
        return qs

    def resolve_lecture_notes(self, info, course_id: Optional[str] = None):
        user = require_authenticated_user(info)
        qs = LectureNote.objects.select_related("course", "author")
        if course_id:
            qs = qs.filter(course_id=course_id)
        if user.is_administrator or user.is_superuser:
            return qs
        return qs.filter(Q(course__students=user) | Q(course__instructor=user) | Q(author=user)).distinct()

    def resolve_whiteboard_sessions(self, info, course_id: Optional[str] = None, active_only: bool = False):
        user = require_authenticated_user(info)
        qs = WhiteboardSession.objects.select_related("course", "created_by")
        if course_id:
            qs = qs.filter(course_id=course_id)
        if active_only:
            qs = qs.filter(is_active=True)
        if user.is_administrator or user.is_superuser:
            return qs
        return qs.filter(Q(course__students=user) | Q(course__instructor=user) | Q(created_by=user)).distinct()

    def resolve_grades(self, info, assignment_id: Optional[str] = None):
        user = require_authenticated_user(info)
        qs = Grade.objects.select_related(
            "submission",
            "submission__assignment",
            "submission__student",
            "grader",
        )
        if assignment_id:
            qs = qs.filter(submission__assignment_id=assignment_id)
        if user.is_student:
            qs = qs.filter(submission__student=user)
        elif user.is_teacher:
            qs = qs.filter(
                Q(grader=user)
                | Q(submission__assignment__course__instructor=user)
            )
        return qs

    def resolve_support_tickets(self, info):
        user = require_authenticated_user(info)
        qs = SupportTicket.objects.select_related("requester", "course")
        if user.is_administrator or user.is_superuser:
            return qs
        if user.is_teacher:
            return qs.filter(Q(course__instructor=user) | Q(requester=user)).distinct()
        return qs.filter(requester=user)

    def resolve_chat_messages(self, info, course_id: Optional[str] = None, ticket_id: Optional[str] = None):
        user = require_authenticated_user(info)
        qs = ChatMessage.objects.select_related("author", "course", "ticket")
        if ticket_id:
            qs = qs.filter(ticket_id=ticket_id)
        if course_id:
            qs = qs.filter(course_id=course_id)
        if user.is_administrator or user.is_superuser:
            return qs
        return qs.filter(Q(author=user) | Q(course__students=user) | Q(course__instructor=user)).distinct()


class CourseInput(graphene.InputObjectType):
    id = graphene.ID()
    code = graphene.String(required=True)
    title = graphene.String(required=True)
    description = graphene.String()
    syllabus = graphene.String()
    start_date = graphene.Date()
    end_date = graphene.Date()


class AssignmentInput(graphene.InputObjectType):
    course_id = graphene.ID(required=True)
    title = graphene.String(required=True)
    instructions_markdown = graphene.String(required=True)
    due_at = graphene.DateTime()
    max_score = graphene.Float()


class UpdateProfileMutation(graphene.Mutation):
    class Arguments:
        first_name = graphene.String(required=False)
        last_name = graphene.String(required=False)

    user = graphene.Field(UserType)

    @classmethod
    def mutate(cls, root, info, first_name: Optional[str] = None, last_name: Optional[str] = None):
        user = require_authenticated_user(info)
        if first_name is not None:
            user.first_name = first_name
        if last_name is not None:
            user.last_name = last_name
        user.save(update_fields=[field for field in ["first_name", "last_name"] if field])
        return UpdateProfileMutation(user=user)


class CreateCourseMutation(graphene.Mutation):
    class Arguments:
        input = CourseInput(required=True)

    course = graphene.Field(CourseType)

    @classmethod
    def mutate(cls, root, info, input: CourseInput):
        user = require_authenticated_user(info)
        if not (user.is_teacher or user.is_administrator or user.is_superuser):
            raise GraphQLError("Only teachers or administrators can create courses.")
        course = Course.objects.create(
            code=input.code,
            title=input.title,
            description=input.description or "",
            syllabus=input.syllabus or "",
            start_date=input.start_date,
            end_date=input.end_date,
            instructor=user if user.is_teacher else user,
        )
        course.students.add(user)
        return CreateCourseMutation(course=course)


class UpdateCourseMutation(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        input = CourseInput(required=True)

    course = graphene.Field(CourseType)

    @classmethod
    def mutate(cls, root, info, id: str, input: CourseInput):
        user = require_authenticated_user(info)
        try:
            course = Course.objects.get(pk=id)
        except Course.DoesNotExist as exc:
            raise GraphQLError("Course not found.") from exc
        if not (user.is_administrator or user.is_superuser or course.instructor == user):
            raise GraphQLError("You do not have permission to update this course.")
        for field in ["code", "title", "description", "syllabus", "start_date", "end_date"]:
            value = getattr(input, field, None)
            if value is not None:
                setattr(course, field, value)
        course.save()
        return UpdateCourseMutation(course=course)


class EnrollInCourseMutation(graphene.Mutation):
    class Arguments:
        course_id = graphene.ID(required=True)

    course = graphene.Field(CourseType)

    @classmethod
    def mutate(cls, root, info, course_id: str):
        user = require_authenticated_user(info)
        try:
            course = Course.objects.get(pk=course_id)
        except Course.DoesNotExist as exc:
            raise GraphQLError("Course not found.") from exc
        course.students.add(user)
        return EnrollInCourseMutation(course=course)


class CreateAssignmentMutation(graphene.Mutation):
    class Arguments:
        input = AssignmentInput(required=True)

    assignment = graphene.Field(AssignmentType)

    @classmethod
    def mutate(cls, root, info, input: AssignmentInput):
        user = require_authenticated_user(info)
        if not (user.is_teacher or user.is_administrator or user.is_superuser):
            raise GraphQLError("Only teachers can create assignments.")
        try:
            course = Course.objects.get(pk=input.course_id)
        except Course.DoesNotExist as exc:
            raise GraphQLError("Course not found.") from exc
        if not (course.instructor == user or user.is_administrator or user.is_superuser):
            raise GraphQLError("You are not assigned to this course.")
        assignment = Assignment.objects.create(
            course=course,
            author=user,
            title=input.title,
            instructions_markdown=input.instructions_markdown,
            due_at=input.due_at,
            max_score=input.max_score or 100,
        )
        return CreateAssignmentMutation(assignment=assignment)


class SubmitAssignmentMutation(graphene.Mutation):
    class Arguments:
        assignment_id = graphene.ID(required=True)
        content_markdown = graphene.String(required=True)

    submission = graphene.Field(SubmissionType)

    @classmethod
    def mutate(cls, root, info, assignment_id: str, content_markdown: str):
        user = require_authenticated_user(info)
        if not user.is_student:
            raise GraphQLError("Only students can submit assignments.")
        try:
            assignment = Assignment.objects.select_related("course").get(pk=assignment_id)
        except Assignment.DoesNotExist as exc:
            raise GraphQLError("Assignment not found.") from exc
        if user not in assignment.course.students.all():
            raise GraphQLError("You are not enrolled in this course.")
        submission, _ = Submission.objects.update_or_create(
            assignment=assignment,
            student=user,
            defaults={"content_markdown": content_markdown, "updated_at": timezone.now()},
        )
        return SubmitAssignmentMutation(submission=submission)


class GradeSubmissionMutation(graphene.Mutation):
    class Arguments:
        submission_id = graphene.ID(required=True)
        score = graphene.Float(required=True)
        feedback_markdown = graphene.String(required=False)

    grade = graphene.Field(GradeType)

    @classmethod
    def mutate(cls, root, info, submission_id: str, score: float, feedback_markdown: Optional[str] = ""):
        user = require_authenticated_user(info)
        if not (user.is_teacher or user.is_administrator or user.is_superuser):
            raise GraphQLError("Only teachers can grade submissions.")
        try:
            submission = Submission.objects.select_related("assignment", "assignment__course").get(pk=submission_id)
        except Submission.DoesNotExist as exc:
            raise GraphQLError("Submission not found.") from exc
        if submission.assignment.course.instructor != user and not (user.is_administrator or user.is_superuser):
            raise GraphQLError("You do not teach this course.")
        grade, _ = Grade.objects.update_or_create(
            submission=submission,
            defaults={
                "grader": user,
                "score": score,
                "feedback_markdown": feedback_markdown or "",
            },
        )
        return GradeSubmissionMutation(grade=grade)


class UploadLectureNoteMutation(graphene.Mutation):
    class Arguments:
        course_id = graphene.ID(required=True)
        title = graphene.String(required=True)
        description = graphene.String(required=False)
        file_name = graphene.String(required=True)
        file_data = graphene.String(required=True, description="Base64 encoded file content")

    note = graphene.Field(LectureNoteType)

    @classmethod
    def mutate(
        cls,
        root,
        info,
        course_id: str,
        title: str,
        file_name: str,
        file_data: str,
        description: Optional[str] = "",
    ):
        user = require_authenticated_user(info)
        if not (user.is_teacher or user.is_administrator or user.is_superuser):
            raise GraphQLError("Only teachers can upload lecture notes.")
        try:
            course = Course.objects.get(pk=course_id)
        except Course.DoesNotExist as exc:
            raise GraphQLError("Course not found.") from exc
        if course.instructor != user and not (user.is_administrator or user.is_superuser):
            raise GraphQLError("You do not teach this course.")
        note = LectureNote.objects.create(
            course=course,
            author=user,
            title=title,
            description=description or "",
            file=None,
        )
        note.file.save(file_name, decode_base64_file(file_data, file_name), save=True)
        return UploadLectureNoteMutation(note=note)


class CreateSupportTicketMutation(graphene.Mutation):
    class Arguments:
        subject = graphene.String(required=True)
        description = graphene.String(required=True)
        course_id = graphene.ID(required=False)

    ticket = graphene.Field(SupportTicketType)

    @classmethod
    def mutate(cls, root, info, subject: str, description: str, course_id: Optional[str] = None):
        user = require_authenticated_user(info)
        course = None
        if course_id:
            try:
                course = Course.objects.get(pk=course_id)
            except Course.DoesNotExist as exc:
                raise GraphQLError("Course not found.") from exc
        ticket = SupportTicket.objects.create(
            requester=user,
            course=course,
            subject=subject,
            description=description,
        )
        return CreateSupportTicketMutation(ticket=ticket)


class PostChatMessageMutation(graphene.Mutation):
    class Arguments:
        message = graphene.String(required=True)
        course_id = graphene.ID(required=False)
        ticket_id = graphene.ID(required=False)

    chat_message = graphene.Field(ChatMessageType)

    @classmethod
    def mutate(
        cls,
        root,
        info,
        message: str,
        course_id: Optional[str] = None,
        ticket_id: Optional[str] = None,
    ):
        user = require_authenticated_user(info)
        if not message.strip():
            raise GraphQLError("Message cannot be empty.")
        course = None
        ticket = None
        if course_id:
            try:
                course = Course.objects.get(pk=course_id)
            except Course.DoesNotExist as exc:
                raise GraphQLError("Course not found.") from exc
        if ticket_id:
            try:
                ticket = SupportTicket.objects.get(pk=ticket_id)
            except SupportTicket.DoesNotExist as exc:
                raise GraphQLError("Ticket not found.") from exc
        chat_message = ChatMessage.objects.create(
            author=user,
            content=message,
            course=course,
            ticket=ticket,
        )
        return PostChatMessageMutation(chat_message=chat_message)


class CreateWhiteboardSessionMutation(graphene.Mutation):
    class Arguments:
        course_id = graphene.ID(required=True)
        title = graphene.String(required=True)

    session = graphene.Field(WhiteboardSessionType)

    @classmethod
    def mutate(cls, root, info, course_id: str, title: str):
        user = require_authenticated_user(info)
        if not (user.is_teacher or user.is_administrator or user.is_superuser):
            raise GraphQLError("Only teachers can create whiteboard sessions.")
        try:
            course = Course.objects.get(pk=course_id)
        except Course.DoesNotExist as exc:
            raise GraphQLError("Course not found.") from exc
        if course.instructor != user and not (user.is_administrator or user.is_superuser):
            raise GraphQLError("You do not teach this course.")
        session = WhiteboardSession.objects.create(
            course=course,
            title=title,
            created_by=user,
        )
        return CreateWhiteboardSessionMutation(session=session)


class SaveWhiteboardStateMutation(graphene.Mutation):
    class Arguments:
        session_id = graphene.ID(required=True)
        strokes = graphene.JSONString(required=True)
        snapshot = graphene.String(required=False)

    session = graphene.Field(WhiteboardSessionType)

    @classmethod
    def mutate(cls, root, info, session_id: str, strokes, snapshot: Optional[str] = ""):
        user = require_authenticated_user(info)
        try:
            session = WhiteboardSession.objects.select_related("course", "created_by").get(pk=session_id)
        except WhiteboardSession.DoesNotExist as exc:
            raise GraphQLError("Session not found.") from exc
        if user not in session.course.students.all() and user != session.course.instructor and not (
            user.is_administrator or user.is_superuser
        ):
            raise GraphQLError("You are not part of this session.")
        session.strokes = strokes
        if snapshot:
            session.snapshot = snapshot
        session.save(update_fields=["strokes", "snapshot", "updated_at"])
        WhiteboardEvent.objects.create(
            session=session,
            sender=user,
            payload={"strokes": strokes, "snapshot": snapshot, "saved_at": datetime.utcnow().isoformat()},
        )
        return SaveWhiteboardStateMutation(session=session)


class Mutation(graphene.ObjectType):
    update_profile = UpdateProfileMutation.Field()
    create_course = CreateCourseMutation.Field()
    update_course = UpdateCourseMutation.Field()
    enroll_in_course = EnrollInCourseMutation.Field()
    create_assignment = CreateAssignmentMutation.Field()
    submit_assignment = SubmitAssignmentMutation.Field()
    grade_submission = GradeSubmissionMutation.Field()
    upload_note = UploadLectureNoteMutation.Field()
    create_support_ticket = CreateSupportTicketMutation.Field()
    post_chat_message = PostChatMessageMutation.Field()
    create_whiteboard_session = CreateWhiteboardSessionMutation.Field()
    save_whiteboard_state = SaveWhiteboardStateMutation.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)

