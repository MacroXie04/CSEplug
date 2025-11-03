"""GraphQL schema entrypoint."""

import graphene
from django.contrib.auth import get_user_model
from django.db import models
from graphene_django import DjangoObjectType

from assignments.models import Assignment, AssignmentExtension, AssignmentQuestion
from assets.models import Asset
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
from support.models import SupportTicket, ChatMessage
from whiteboard.models import WhiteboardSession, WhiteboardStroke

from .permissions import get_user_or_error, check_course_membership

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
            "questions",
            "extensions",
        )


class AssignmentQuestionType(DjangoObjectType):
    class Meta:
        model = AssignmentQuestion
        fields = (
            "id",
            "assignment",
            "order_index",
            "type",
            "weight",
            "title",
            "free_response_question",
            "multiple_choice_question",
        )


class AssignmentExtensionType(DjangoObjectType):
    class Meta:
        model = AssignmentExtension
        fields = ("id", "assignment", "user", "due_at", "created_at")


class AssetType(DjangoObjectType):
    class Meta:
        model = Asset
        fields = ("id", "uploader", "course", "book", "name", "type", "url", "thumbnail_url", "created_at", "updated_at")


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


class SupportTicketType(DjangoObjectType):
    class Meta:
        model = SupportTicket
        fields = ("id", "requester", "course", "subject", "description", "status", "created_at", "updated_at", "messages")


class ChatMessageType(DjangoObjectType):
    class Meta:
        model = ChatMessage
        fields = ("id", "ticket", "course", "author", "content", "created_at")


class Query(graphene.ObjectType):
    """Root GraphQL query."""

    # Health & auth
    ping = graphene.String(description="Health check")
    me = graphene.Field(UserType)

    # Courses
    user_courses_connection = graphene.List(CourseMembershipType)
    course = graphene.Field(CourseType, id=graphene.ID(required=True))
    course_memberships = graphene.List(CourseMembershipType, course_id=graphene.ID())

    # Assignments
    assignments_connection = graphene.List(AssignmentType, course_id=graphene.ID())
    assignment = graphene.Field(AssignmentType, id=graphene.ID(required=True))
    assignment_question = graphene.Field(AssignmentQuestionType, id=graphene.ID(required=True))
    user_assignments_connection = graphene.List(AssignmentType, course_id=graphene.ID())
    user_assignment = graphene.Field(AssignmentType, id=graphene.ID(required=True))
    user_assignment_question = graphene.Field(AssignmentQuestionType, id=graphene.ID(required=True))

    # Question bank
    course_free_response_questions_connection = graphene.List(FreeResponseQuestionType, course_id=graphene.ID(required=True))
    course_multiple_choice_questions_connection = graphene.List(MultipleChoiceQuestionType, course_id=graphene.ID(required=True))

    # Submissions
    user_submissions = graphene.List(SubmissionType, assignment_question_id=graphene.ID())
    user_submission_latest = graphene.Field(SubmissionType, assignment_question_id=graphene.ID(required=True))

    # Books
    books_connection = graphene.List(BookType, course_id=graphene.ID())
    book = graphene.Field(BookType, id=graphene.ID(required=True))
    book_chapter = graphene.Field(BookChapterType, id=graphene.ID(required=True))

    # Assets
    course_assets = graphene.List(AssetType, course_id=graphene.ID(required=True))

    # Notes
    notes_pages = graphene.List(NotesPageType, course_id=graphene.ID(required=True))
    notes_page = graphene.Field(NotesPageType, id=graphene.ID(required=True))

    # Decks
    decks_connection = graphene.List(DeckType, course_id=graphene.ID())
    deck = graphene.Field(DeckType, id=graphene.ID(required=True))

    # Whiteboard
    whiteboard_sessions = graphene.List(WhiteboardSessionType, course_id=graphene.ID())
    whiteboard_session = graphene.Field(WhiteboardSessionType, id=graphene.ID(required=True))
    whiteboard_strokes = graphene.List(WhiteboardStrokeType, session_id=graphene.ID(required=True))

    # Support
    support_tickets = graphene.List(SupportTicketType, course_id=graphene.ID())
    support_ticket = graphene.Field(SupportTicketType, id=graphene.ID(required=True))
    course_chat_messages = graphene.List(ChatMessageType, course_id=graphene.ID(required=True))

    # Assignment Extensions
    assignment_extensions = graphene.List(AssignmentExtensionType, assignment_id=graphene.ID(required=True))
    user_assignment_extension = graphene.Field(AssignmentExtensionType, assignment_id=graphene.ID(required=True), user_id=graphene.ID())

    def resolve_ping(self, info, **kwargs):  # noqa: D401
        return "pong"

    def resolve_me(self, info, **kwargs):
        user = info.context.user
        return user if user.is_authenticated else None

    def resolve_user_courses_connection(self, info, **kwargs):
        user = get_user_or_error(info)
        return CourseMembership.objects.filter(user=user).select_related("course").order_by("-joined_at")

    def resolve_course(self, info, id, **kwargs):
        user = get_user_or_error(info)
        try:
            course = Course.objects.get(pk=id)
        except Course.DoesNotExist:
            raise graphene.GraphQLError("Course not found.")
        check_course_membership(user, course)
        return course

    def resolve_course_memberships(self, info, course_id=None, **kwargs):
        user = get_user_or_error(info)
        qs = CourseMembership.objects.select_related("course", "user")
        if course_id:
            qs = qs.filter(course_id=course_id)
            try:
                course = Course.objects.get(pk=course_id)
            except Course.DoesNotExist:
                raise graphene.GraphQLError("Course not found.")
            check_course_membership(user, course)
        return qs

    def resolve_assignments_connection(self, info, course_id=None, **kwargs):
        qs = Assignment.objects.select_related("course").prefetch_related("questions")
        if course_id:
            qs = qs.filter(course_id=course_id)
        return qs

    def resolve_assignment(self, info, id, **kwargs):
        user = get_user_or_error(info)
        try:
            assignment = Assignment.objects.select_related("course").prefetch_related("questions").get(pk=id)
        except Assignment.DoesNotExist:
            raise graphene.GraphQLError("Assignment not found.")
        check_course_membership(user, assignment.course)
        return assignment

    def resolve_assignment_question(self, info, id, **kwargs):
        user = get_user_or_error(info)
        try:
            aq = AssignmentQuestion.objects.select_related(
                "assignment", "assignment__course", "free_response_question", "multiple_choice_question"
            ).get(pk=id)
        except AssignmentQuestion.DoesNotExist:
            raise graphene.GraphQLError("Assignment question not found.")
        check_course_membership(user, aq.assignment.course)
        return aq

    def resolve_user_assignments_connection(self, info, course_id=None, **kwargs):
        user = get_user_or_error(info)
        qs = Assignment.objects.select_related("course").prefetch_related("questions")
        if course_id:
            qs = qs.filter(course_id=course_id)
            try:
                course = Course.objects.get(pk=course_id)
            except Course.DoesNotExist:
                raise graphene.GraphQLError("Course not found.")
            check_course_membership(user, course)
        return qs

    def resolve_user_assignment(self, info, id, **kwargs):
        return self.resolve_assignment(info, id, **kwargs)

    def resolve_user_assignment_question(self, info, id, **kwargs):
        return self.resolve_assignment_question(info, id, **kwargs)

    def resolve_course_free_response_questions_connection(self, info, course_id, **kwargs):
        user = get_user_or_error(info)
        try:
            course = Course.objects.get(pk=course_id)
        except Course.DoesNotExist:
            raise graphene.GraphQLError("Course not found.")
        check_course_membership(user, course)
        return FreeResponseQuestion.objects.filter(course=course)

    def resolve_course_multiple_choice_questions_connection(self, info, course_id, **kwargs):
        user = get_user_or_error(info)
        try:
            course = Course.objects.get(pk=course_id)
        except Course.DoesNotExist:
            raise graphene.GraphQLError("Course not found.")
        check_course_membership(user, course)
        return MultipleChoiceQuestion.objects.filter(course=course).prefetch_related("options")

    def resolve_user_submissions(self, info, assignment_question_id=None, **kwargs):
        user = get_user_or_error(info)
        qs = Submission.objects.filter(user=user).select_related("assignment_question", "multiple_choice_option")
        if assignment_question_id:
            qs = qs.filter(assignment_question_id=assignment_question_id)
        return qs

    def resolve_user_submission_latest(self, info, assignment_question_id, **kwargs):
        user = get_user_or_error(info)
        return (
            Submission.objects.filter(user=user, assignment_question_id=assignment_question_id)
            .select_related("assignment_question", "multiple_choice_option")
            .order_by("-created_at")
            .first()
        )

    def resolve_books_connection(self, info, course_id=None, **kwargs):
        qs = Book.objects.select_related("course").prefetch_related("chapters")
        if course_id:
            qs = qs.filter(course_id=course_id)
        return qs

    def resolve_book(self, info, id, **kwargs):
        user = get_user_or_error(info)
        try:
            book = Book.objects.select_related("course").prefetch_related("chapters").get(pk=id)
        except Book.DoesNotExist:
            raise graphene.GraphQLError("Book not found.")
        check_course_membership(user, book.course)
        return book

    def resolve_book_chapter(self, info, id, **kwargs):
        user = get_user_or_error(info)
        try:
            chapter = BookChapter.objects.select_related("book", "book__course").get(pk=id)
        except BookChapter.DoesNotExist:
            raise graphene.GraphQLError("Chapter not found.")
        check_course_membership(user, chapter.book.course)
        return chapter

    def resolve_course_assets(self, info, course_id, **kwargs):
        user = get_user_or_error(info)
        try:
            course = Course.objects.get(pk=course_id)
        except Course.DoesNotExist:
            raise graphene.GraphQLError("Course not found.")
        check_course_membership(user, course)
        return Asset.objects.filter(course=course).select_related("uploader")

    def resolve_notes_pages(self, info, course_id, **kwargs):
        user = get_user_or_error(info)
        try:
            course = Course.objects.get(pk=course_id)
        except Course.DoesNotExist:
            raise graphene.GraphQLError("Course not found.")
        check_course_membership(user, course)
        return NotesPage.objects.filter(course=course).select_related("author").prefetch_related("shapes")

    def resolve_notes_page(self, info, id, **kwargs):
        user = get_user_or_error(info)
        try:
            page = NotesPage.objects.select_related("course", "author").prefetch_related("shapes").get(pk=id)
        except NotesPage.DoesNotExist:
            raise graphene.GraphQLError("Notes page not found.")
        check_course_membership(user, page.course)
        return page

    def resolve_decks_connection(self, info, course_id=None, **kwargs):
        qs = Deck.objects.select_related("course")
        if course_id:
            qs = qs.filter(course_id=course_id)
        return qs

    def resolve_deck(self, info, id, **kwargs):
        user = get_user_or_error(info)
        try:
            deck = Deck.objects.select_related("course").get(pk=id)
        except Deck.DoesNotExist:
            raise graphene.GraphQLError("Deck not found.")
        check_course_membership(user, deck.course)
        return deck

    def resolve_whiteboard_sessions(self, info, course_id=None, **kwargs):
        user = get_user_or_error(info)
        qs = WhiteboardSession.objects.select_related("course", "instructor")
        if course_id:
            qs = qs.filter(course_id=course_id)
            try:
                course = Course.objects.get(pk=course_id)
            except Course.DoesNotExist:
                raise graphene.GraphQLError("Course not found.")
            check_course_membership(user, course)
        return qs.order_by("-created_at")

    def resolve_whiteboard_session(self, info, id, **kwargs):
        user = get_user_or_error(info)
        try:
            session = WhiteboardSession.objects.select_related("course", "instructor").get(pk=id)
        except WhiteboardSession.DoesNotExist:
            raise graphene.GraphQLError("Whiteboard session not found.")
        check_course_membership(user, session.course)
        return session

    def resolve_whiteboard_strokes(self, info, session_id, **kwargs):
        user = get_user_or_error(info)
        try:
            session = WhiteboardSession.objects.select_related("course").get(pk=session_id)
        except WhiteboardSession.DoesNotExist:
            raise graphene.GraphQLError("Whiteboard session not found.")
        check_course_membership(user, session.course)
        return WhiteboardStroke.objects.filter(session=session).select_related("user").order_by("ts")

    def resolve_support_tickets(self, info, course_id=None, **kwargs):
        user = get_user_or_error(info)
        qs = SupportTicket.objects.select_related("requester", "course").prefetch_related("messages")
        if course_id:
            qs = qs.filter(course_id=course_id)
            try:
                course = Course.objects.get(pk=course_id)
            except Course.DoesNotExist:
                raise graphene.GraphQLError("Course not found.")
            check_course_membership(user, course)
        else:
            # Return only user's own tickets if no course filter
            qs = qs.filter(requester=user)
        return qs.order_by("-created_at")

    def resolve_support_ticket(self, info, id, **kwargs):
        user = get_user_or_error(info)
        try:
            ticket = SupportTicket.objects.select_related("requester", "course").prefetch_related("messages").get(pk=id)
        except SupportTicket.DoesNotExist:
            raise graphene.GraphQLError("Support ticket not found.")
        # Check if user is the requester or a course member (if ticket has a course)
        if ticket.requester != user:
            if ticket.course:
                check_course_membership(user, ticket.course)
            elif not user.is_superuser:
                raise graphene.GraphQLError("You don't have permission to view this ticket.")
        return ticket

    def resolve_course_chat_messages(self, info, course_id, **kwargs):
        user = get_user_or_error(info)
        try:
            course = Course.objects.get(pk=course_id)
        except Course.DoesNotExist:
            raise graphene.GraphQLError("Course not found.")
        check_course_membership(user, course)
        return ChatMessage.objects.filter(course=course, ticket__isnull=True).select_related("author").order_by("created_at")

    def resolve_assignment_extensions(self, info, assignment_id, **kwargs):
        user = get_user_or_error(info)
        try:
            assignment = Assignment.objects.select_related("course").get(pk=assignment_id)
        except Assignment.DoesNotExist:
            raise graphene.GraphQLError("Assignment not found.")
        check_course_membership(user, assignment.course, [CourseMembership.Roles.INSTRUCTOR, CourseMembership.Roles.TEACHING_ASSISTANT])
        return AssignmentExtension.objects.filter(assignment=assignment).select_related("user")

    def resolve_user_assignment_extension(self, info, assignment_id, user_id=None, **kwargs):
        user = get_user_or_error(info)
        try:
            assignment = Assignment.objects.select_related("course").get(pk=assignment_id)
        except Assignment.DoesNotExist:
            raise graphene.GraphQLError("Assignment not found.")
        check_course_membership(user, assignment.course)
        
        # If user_id provided, get extension for that user (instructors only)
        if user_id:
            check_course_membership(user, assignment.course, [CourseMembership.Roles.INSTRUCTOR, CourseMembership.Roles.TEACHING_ASSISTANT])
            target_user_id = user_id
        else:
            # Otherwise get extension for current user
            target_user_id = user.id
        
        return AssignmentExtension.objects.filter(assignment=assignment, user_id=target_user_id).select_related("user").first()


class Mutation(graphene.ObjectType):
    """Root GraphQL mutations."""

    # Import mutations from mutations module
    from .mutations import (
        AssignmentCreateMutation,
        AssignmentDeleteMutation,
        AssignmentExtensionCreateMutation,
        AssignmentQuestionFRCreateMutation,
        AssignmentQuestionMCCreateMutation,
        AssignmentUpdateMutation,
        AssetCreateMutation,
        AssetDeleteMutation,
        BookChapterCreateMutation,
        BookCreateMutation,
        ChatMessageCreateMutation,
        CourseMembershipAddMutation,
        CourseMembershipRemoveMutation,
        CourseMembershipUpdateRoleMutation,
        CourseCreateMutation,
        CourseDeleteMutation,
        CourseUpdateMutation,
        DeckCreateMutation,
        DeckDeleteMutation,
        DeckUpdateMutation,
        FRQuestionCreateMutation,
        LoginMutation,
        LogoutMutation,
        MCOptionCreateMutation,
        MCQuestionCreateMutation,
        NotesPageCreateMutation,
        NotesPageDeleteMutation,
        RefreshMutation,
        SubmissionCreateMutation,
        SubmissionOutcomeUpdateMutation,
        SupportTicketCreateMutation,
        SupportTicketUpdateMutation,
        UpdateProfileMutation,
        WhiteboardSessionCreateMutation,
        WhiteboardSessionDeleteMutation,
        WhiteboardSessionUpdateMutation,
        WhiteboardStrokeCreateMutation,
    )

    # Auth
    login = LoginMutation.Field()
    refresh = RefreshMutation.Field()
    logout = LogoutMutation.Field()
    update_profile = UpdateProfileMutation.Field()

    # Courses
    course_create = CourseCreateMutation.Field()
    course_update = CourseUpdateMutation.Field()
    course_delete = CourseDeleteMutation.Field()

    # Assignments
    assignment_create = AssignmentCreateMutation.Field()
    assignment_update = AssignmentUpdateMutation.Field()
    assignment_delete = AssignmentDeleteMutation.Field()
    assignment_question_free_response_create = AssignmentQuestionFRCreateMutation.Field()
    assignment_question_multiple_choice_create = AssignmentQuestionMCCreateMutation.Field()

    # Questions
    course_free_response_question_create = FRQuestionCreateMutation.Field()
    course_multiple_choice_question_create = MCQuestionCreateMutation.Field()
    course_multiple_choice_option_create = MCOptionCreateMutation.Field()

    # Submissions & grading
    assignment_submission_create = SubmissionCreateMutation.Field()
    assignment_submission_outcome_update = SubmissionOutcomeUpdateMutation.Field()

    # Books
    book_create = BookCreateMutation.Field()
    book_chapter_create = BookChapterCreateMutation.Field()

    # Notes
    notes_page_create = NotesPageCreateMutation.Field()
    notes_page_delete = NotesPageDeleteMutation.Field()

    # Support
    support_ticket_create = SupportTicketCreateMutation.Field()
    support_ticket_update = SupportTicketUpdateMutation.Field()
    chat_message_create = ChatMessageCreateMutation.Field()

    # Whiteboard
    whiteboard_session_create = WhiteboardSessionCreateMutation.Field()
    whiteboard_session_update = WhiteboardSessionUpdateMutation.Field()
    whiteboard_session_delete = WhiteboardSessionDeleteMutation.Field()
    whiteboard_stroke_create = WhiteboardStrokeCreateMutation.Field()

    # Course membership
    course_membership_add = CourseMembershipAddMutation.Field()
    course_membership_remove = CourseMembershipRemoveMutation.Field()
    course_membership_update_role = CourseMembershipUpdateRoleMutation.Field()

    # Assignment extensions
    assignment_extension_create = AssignmentExtensionCreateMutation.Field()

    # Assets
    asset_create = AssetCreateMutation.Field()
    asset_delete = AssetDeleteMutation.Field()

    # Decks
    deck_create = DeckCreateMutation.Field()
    deck_update = DeckUpdateMutation.Field()
    deck_delete = DeckDeleteMutation.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
