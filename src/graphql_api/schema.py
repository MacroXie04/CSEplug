"""GraphQL schema entrypoint (temporary minimal schema)."""

import graphene
from django.contrib.auth import get_user_model
from graphene_django import DjangoObjectType

from assignments.models import Assignment
from books.models import Book, BookChapter
from courses.models import Course, CourseMembership
from decks.models import Deck
from grading.models import SubmissionOutcome
from notes.models import NotesPage, NotesShape
from questions.models import (
    FreeResponseQuestion,
    MultipleChoiceOption,
    MultipleChoiceQuestion,
)
from submissions.models import Submission
from whiteboard.models import WhiteboardSession, WhiteboardStroke

User = get_user_model()


class UserType(DjangoObjectType):
    class Meta:
        model = User
        fields = ("id", "email", "first_name", "last_name")


class CourseType(DjangoObjectType):
    class Meta:
        model = Course
        fields = (
            "id",
            "title",
            "description",
            "syllabus",
            "policy",
            "start_date",
            "end_date",
            "created_at",
            "updated_at",
        )


class CourseMembershipType(DjangoObjectType):
    class Meta:
        model = CourseMembership
        fields = ("id", "course", "user", "role", "joined_at")


class AssignmentType(DjangoObjectType):
    class Meta:
        model = Assignment
        fields = (
            "id",
            "course",
            "title",
            "instructions_md",
            "instructions_html",
            "points",
            "publish_at",
            "due_at",
            "created_at",
            "updated_at",
        )


class SubmissionType(DjangoObjectType):
    class Meta:
        model = Submission
        fields = (
            "id",
            "user",
            "assignment_question",
            "free_response_text",
            "multiple_choice_option",
            "created_at",
        )


class SubmissionOutcomeType(DjangoObjectType):
    class Meta:
        model = SubmissionOutcome
        fields = (
            "id",
            "submission",
            "grader",
            "score",
            "feedback_md",
            "feedback_html",
            "is_evaluated",
            "updated_at",
        )


class BookType(DjangoObjectType):
    class Meta:
        model = Book
        fields = ("id", "course", "title", "description", "created_at", "updated_at")


class BookChapterType(DjangoObjectType):
    class Meta:
        model = BookChapter
        fields = (
            "id",
            "book",
            "order_index",
            "title",
            "markdown_text",
            "html",
            "toc",
            "created_at",
            "updated_at",
        )


class DeckType(DjangoObjectType):
    class Meta:
        model = Deck
        fields = ("id", "course", "title", "embed_code", "created_at", "updated_at")


class FreeResponseQuestionType(DjangoObjectType):
    class Meta:
        model = FreeResponseQuestion
        fields = ("id", "course", "question_text", "created_at", "updated_at")


class MultipleChoiceQuestionType(DjangoObjectType):
    class Meta:
        model = MultipleChoiceQuestion
        fields = ("id", "course", "question_text", "created_at", "updated_at", "options")


class MultipleChoiceOptionType(DjangoObjectType):
    class Meta:
        model = MultipleChoiceOption
        fields = ("id", "question", "order_index", "option_text", "is_correct")


class NotesPageType(DjangoObjectType):
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


class NotesShapeType(DjangoObjectType):
    class Meta:
        model = NotesShape
        fields = ("id", "page", "data", "version", "created_at")


class WhiteboardSessionType(DjangoObjectType):
    class Meta:
        model = WhiteboardSession
        fields = ("id", "course", "instructor", "title", "is_active", "created_at", "updated_at")


class WhiteboardStrokeType(DjangoObjectType):
    class Meta:
        model = WhiteboardStroke
        fields = ("id", "session", "user", "data", "ts")


class Query(graphene.ObjectType):
    """Minimal placeholder query set. Future work will expand this schema."""

    ping = graphene.String(description="Health check")
    me = graphene.Field(UserType)
    courses = graphene.List(CourseType)
    course_memberships = graphene.List(CourseMembershipType, course_id=graphene.ID())
    assignments = graphene.List(AssignmentType, course_id=graphene.ID())
    submissions = graphene.List(SubmissionType, assignment_id=graphene.ID())

    def resolve_ping(self, info, **kwargs):  # noqa: D401
        return "pong"

    def resolve_me(self, info, **kwargs):
        user = info.context.user
        return user if user.is_authenticated else None

    def resolve_courses(self, info, **kwargs):
        return Course.objects.all()

    def resolve_course_memberships(self, info, course_id=None, **kwargs):
        qs = CourseMembership.objects.select_related("course", "user")
        if course_id:
            qs = qs.filter(course_id=course_id)
        return qs

    def resolve_assignments(self, info, course_id=None, **kwargs):
        qs = Assignment.objects.select_related("course")
        if course_id:
            qs = qs.filter(course_id=course_id)
        return qs

    def resolve_submissions(self, info, assignment_id=None, **kwargs):
        qs = Submission.objects.select_related("assignment_question", "user")
        if assignment_id:
            qs = qs.filter(assignment_question__assignment_id=assignment_id)
        return qs


class Mutation(graphene.ObjectType):
    pass


schema = graphene.Schema(query=Query, mutation=Mutation)
