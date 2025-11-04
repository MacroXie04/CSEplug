"""GraphQL mutations for CSE Plug."""

from typing import Optional

import graphene
from django.contrib.auth import authenticate, get_user_model
from graphql import GraphQLError

from accounts.auth.services import (
    blacklist_refresh_token,
    clear_jwt_cookies,
    generate_tokens,
    set_jwt_cookies,
)
from accounts.auth.constants import REFRESH_COOKIE_NAME
from assignments.models import Assignment, AssignmentExtension, AssignmentQuestion
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

from .permissions import check_course_membership, get_user_or_error

User = get_user_model()


# ============================================================================
# Authentication Mutations
# ============================================================================


class UpdateProfileMutation(graphene.Mutation):
    """Update current user's profile information."""

    class Arguments:
        first_name = graphene.String()
        last_name = graphene.String()

    user = graphene.Field("graphql_api.schema.UserType")

    @classmethod
    def mutate(cls, root, info, **kwargs):
        user = get_user_or_error(info)
        if "first_name" in kwargs:
            user.first_name = kwargs["first_name"]
        if "last_name" in kwargs:
            user.last_name = kwargs["last_name"]
        user.save()
        return UpdateProfileMutation(user=user)


class LoginMutation(graphene.Mutation):
    """Login with email and password, returns user and sets JWT cookies."""

    class Arguments:
        email = graphene.String(required=True)
        password = graphene.String(required=True)

    user = graphene.Field("graphql_api.schema.UserType")
    success = graphene.Boolean()

    @classmethod
    def mutate(cls, root, info, email: str, password: str):
        user = authenticate(info.context, email=email, password=password)
        if not user:
            raise GraphQLError("Invalid email or password.")

        access_token, refresh_token = generate_tokens(user)
        response = info.context
        set_jwt_cookies(response, access_token, refresh_token)

        return LoginMutation(user=user, success=True)


class RefreshMutation(graphene.Mutation):
    """Refresh access token using refresh token from cookie."""

    success = graphene.Boolean()

    @classmethod
    def mutate(cls, root, info):
        request = info.context
        raw_refresh = request.COOKIES.get(REFRESH_COOKIE_NAME)
        if not raw_refresh:
            raise GraphQLError("Refresh token missing.")

        from rest_framework_simplejwt.tokens import RefreshToken
        from rest_framework_simplejwt.exceptions import TokenError

        try:
            refresh = RefreshToken(raw_refresh)
        except TokenError as exc:
            raise GraphQLError("Invalid refresh token.") from exc

        try:
            user = User.objects.get(pk=refresh["user_id"])
        except User.DoesNotExist as exc:
            raise GraphQLError("User not found.") from exc

        blacklist_refresh_token(raw_refresh)
        new_access, new_refresh = generate_tokens(user)
        set_jwt_cookies(info.context, new_access, new_refresh)

        return RefreshMutation(success=True)


class LogoutMutation(graphene.Mutation):
    """Logout and clear JWT cookies."""

    success = graphene.Boolean()

    @classmethod
    def mutate(cls, root, info):
        user = get_user_or_error(info)
        raw_refresh = info.context.COOKIES.get(REFRESH_COOKIE_NAME)
        blacklist_refresh_token(raw_refresh)
        clear_jwt_cookies(info.context)
        return LogoutMutation(success=True)


# ============================================================================
# Course Mutations
# ============================================================================


class CourseCreateMutation(graphene.Mutation):
    class Arguments:
        title = graphene.String(required=True)
        description = graphene.String()
        syllabus = graphene.String()
        policy = graphene.String()
        start_date = graphene.Date()
        end_date = graphene.Date()

    course = graphene.Field("graphql_api.schema.CourseType")

    @classmethod
    def mutate(cls, root, info, title: str, **kwargs):
        user = get_user_or_error(info)
        course = Course.objects.create(
            title=title,
            description=kwargs.get("description", ""),
            syllabus=kwargs.get("syllabus", ""),
            policy=kwargs.get("policy", ""),
            start_date=kwargs.get("start_date"),
            end_date=kwargs.get("end_date"),
        )
        CourseMembership.objects.create(course=course, user=user, role=CourseMembership.Roles.INSTRUCTOR)
        return CourseCreateMutation(course=course)


class CourseUpdateMutation(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        title = graphene.String()
        description = graphene.String()
        syllabus = graphene.String()
        policy = graphene.String()
        start_date = graphene.Date()
        end_date = graphene.Date()

    course = graphene.Field("graphql_api.schema.CourseType")

    @classmethod
    def mutate(cls, root, info, id: str, **kwargs):
        user = get_user_or_error(info)
        try:
            course = Course.objects.get(pk=id)
        except Course.DoesNotExist as exc:
            raise GraphQLError("Course not found.") from exc

        check_course_membership(user, course, [CourseMembership.Roles.INSTRUCTOR])

        for field in ["title", "description", "syllabus", "policy", "start_date", "end_date"]:
            value = kwargs.get(field)
            if value is not None:
                setattr(course, field, value)
        course.save()
        return CourseUpdateMutation(course=course)


class CourseDeleteMutation(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    success = graphene.Boolean()

    @classmethod
    def mutate(cls, root, info, id: str):
        user = get_user_or_error(info)
        try:
            course = Course.objects.get(pk=id)
        except Course.DoesNotExist as exc:
            raise GraphQLError("Course not found.") from exc

        check_course_membership(user, course, [CourseMembership.Roles.INSTRUCTOR])
        course.delete()
        return CourseDeleteMutation(success=True)


# ============================================================================
# Assignment Mutations
# ============================================================================


class AssignmentCreateMutation(graphene.Mutation):
    class Arguments:
        course_id = graphene.ID(required=True)
        title = graphene.String(required=True)
        instructions_md = graphene.String()
        points = graphene.Float()
        publish_at = graphene.DateTime()
        due_at = graphene.DateTime()

    assignment = graphene.Field("graphql_api.schema.AssignmentType")

    @classmethod
    def mutate(cls, root, info, course_id: str, title: str, **kwargs):
        user = get_user_or_error(info)
        try:
            course = Course.objects.get(pk=course_id)
        except Course.DoesNotExist as exc:
            raise GraphQLError("Course not found.") from exc

        check_course_membership(user, course, [CourseMembership.Roles.INSTRUCTOR, CourseMembership.Roles.TEACHING_ASSISTANT])

        assignment = Assignment.objects.create(
            course=course,
            title=title,
            instructions_md=kwargs.get("instructions_md", ""),
            points=kwargs.get("points", 100),
            publish_at=kwargs.get("publish_at"),
            due_at=kwargs.get("due_at"),
        )
        return AssignmentCreateMutation(assignment=assignment)


class AssignmentUpdateMutation(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        title = graphene.String()
        instructions_md = graphene.String()
        points = graphene.Float()
        publish_at = graphene.DateTime()
        due_at = graphene.DateTime()

    assignment = graphene.Field("graphql_api.schema.AssignmentType")

    @classmethod
    def mutate(cls, root, info, id: str, **kwargs):
        user = get_user_or_error(info)
        try:
            assignment = Assignment.objects.select_related("course").get(pk=id)
        except Assignment.DoesNotExist as exc:
            raise GraphQLError("Assignment not found.") from exc

        check_course_membership(
            user, assignment.course, [CourseMembership.Roles.INSTRUCTOR, CourseMembership.Roles.TEACHING_ASSISTANT]
        )

        for field in ["title", "instructions_md", "points", "publish_at", "due_at"]:
            value = kwargs.get(field)
            if value is not None:
                setattr(assignment, field, value)
        assignment.save()
        return AssignmentUpdateMutation(assignment=assignment)


class AssignmentDeleteMutation(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    success = graphene.Boolean()

    @classmethod
    def mutate(cls, root, info, id: str):
        user = get_user_or_error(info)
        try:
            assignment = Assignment.objects.select_related("course").get(pk=id)
        except Assignment.DoesNotExist as exc:
            raise GraphQLError("Assignment not found.") from exc

        check_course_membership(user, assignment.course, [CourseMembership.Roles.INSTRUCTOR])
        assignment.delete()
        return AssignmentDeleteMutation(success=True)


# ============================================================================
# Assignment Question Mutations
# ============================================================================


class AssignmentQuestionFRCreateMutation(graphene.Mutation):
    class Arguments:
        assignment_id = graphene.ID(required=True)
        question_id = graphene.ID(required=True)
        weight = graphene.Float()
        order_index = graphene.Int()
        title = graphene.String()

    assignment_question = graphene.Field("graphql_api.schema.AssignmentQuestionType")

    @classmethod
    def mutate(cls, root, info, assignment_id: str, question_id: str, **kwargs):
        user = get_user_or_error(info)
        try:
            assignment = Assignment.objects.select_related("course").get(pk=assignment_id)
            question = FreeResponseQuestion.objects.get(pk=question_id, course=assignment.course)
        except (Assignment.DoesNotExist, FreeResponseQuestion.DoesNotExist) as exc:
            raise GraphQLError("Assignment or question not found.") from exc

        check_course_membership(
            user, assignment.course, [CourseMembership.Roles.INSTRUCTOR, CourseMembership.Roles.TEACHING_ASSISTANT]
        )

        aq = AssignmentQuestion.objects.create(
            assignment=assignment,
            type=AssignmentQuestion.QuestionType.FREE_RESPONSE,
            free_response_question=question,
            weight=kwargs.get("weight", 1),
            order_index=kwargs.get("order_index", 0),
            title=kwargs.get("title", ""),
        )
        return AssignmentQuestionFRCreateMutation(assignment_question=aq)


class AssignmentQuestionMCCreateMutation(graphene.Mutation):
    class Arguments:
        assignment_id = graphene.ID(required=True)
        question_id = graphene.ID(required=True)
        weight = graphene.Float()
        order_index = graphene.Int()
        title = graphene.String()

    assignment_question = graphene.Field("graphql_api.schema.AssignmentQuestionType")

    @classmethod
    def mutate(cls, root, info, assignment_id: str, question_id: str, **kwargs):
        user = get_user_or_error(info)
        try:
            assignment = Assignment.objects.select_related("course").get(pk=assignment_id)
            question = MultipleChoiceQuestion.objects.get(pk=question_id, course=assignment.course)
        except (Assignment.DoesNotExist, MultipleChoiceQuestion.DoesNotExist) as exc:
            raise GraphQLError("Assignment or question not found.") from exc

        check_course_membership(
            user, assignment.course, [CourseMembership.Roles.INSTRUCTOR, CourseMembership.Roles.TEACHING_ASSISTANT]
        )

        aq = AssignmentQuestion.objects.create(
            assignment=assignment,
            type=AssignmentQuestion.QuestionType.MULTIPLE_CHOICE,
            multiple_choice_question=question,
            weight=kwargs.get("weight", 1),
            order_index=kwargs.get("order_index", 0),
            title=kwargs.get("title", ""),
        )
        return AssignmentQuestionMCCreateMutation(assignment_question=aq)


# ============================================================================
# Submission & Grading Mutations
# ============================================================================


class SubmissionCreateMutation(graphene.Mutation):
    class Arguments:
        assignment_question_id = graphene.ID(required=True)
        free_response_text = graphene.String()
        multiple_choice_option_id = graphene.ID()

    submission = graphene.Field("graphql_api.schema.SubmissionType")

    @classmethod
    def mutate(cls, root, info, assignment_question_id: str, **kwargs):
        user = get_user_or_error(info)
        try:
            aq = AssignmentQuestion.objects.select_related("assignment", "assignment__course").get(pk=assignment_question_id)
        except AssignmentQuestion.DoesNotExist as exc:
            raise GraphQLError("Assignment question not found.") from exc

        check_course_membership(user, aq.assignment.course)

        submission, _ = Submission.objects.update_or_create(
            user=user,
            assignment_question=aq,
            defaults={
                "free_response_text": kwargs.get("free_response_text", ""),
                "multiple_choice_option_id": kwargs.get("multiple_choice_option_id"),
            },
        )
        return SubmissionCreateMutation(submission=submission)


class SubmissionOutcomeUpdateMutation(graphene.Mutation):
    class Arguments:
        submission_id = graphene.ID(required=True)
        score = graphene.Float(required=True)
        feedback_md = graphene.String()

    outcome = graphene.Field("graphql_api.schema.SubmissionOutcomeType")

    @classmethod
    def mutate(cls, root, info, submission_id: str, score: float, **kwargs):
        user = get_user_or_error(info)
        try:
            submission = Submission.objects.select_related(
                "assignment_question", "assignment_question__assignment", "assignment_question__assignment__course"
            ).get(pk=submission_id)
        except Submission.DoesNotExist as exc:
            raise GraphQLError("Submission not found.") from exc

        course = submission.assignment_question.assignment.course
        check_course_membership(user, course, [CourseMembership.Roles.INSTRUCTOR, CourseMembership.Roles.TEACHING_ASSISTANT])

        outcome, _ = SubmissionOutcome.objects.update_or_create(
            submission=submission,
            defaults={
                "grader": user,
                "score": score,
                "feedback_md": kwargs.get("feedback_md", ""),
                "is_evaluated": True,
            },
        )
        return SubmissionOutcomeUpdateMutation(outcome=outcome)


# ============================================================================
# Question Bank Mutations
# ============================================================================


class FRQuestionCreateMutation(graphene.Mutation):
    class Arguments:
        course_id = graphene.ID(required=True)
        question_text = graphene.String(required=True)

    question = graphene.Field("graphql_api.schema.FreeResponseQuestionType")

    @classmethod
    def mutate(cls, root, info, course_id: str, question_text: str):
        user = get_user_or_error(info)
        try:
            course = Course.objects.get(pk=course_id)
        except Course.DoesNotExist as exc:
            raise GraphQLError("Course not found.") from exc

        check_course_membership(user, course, [CourseMembership.Roles.INSTRUCTOR, CourseMembership.Roles.TEACHING_ASSISTANT])

        question = FreeResponseQuestion.objects.create(course=course, question_text=question_text)
        return FRQuestionCreateMutation(question=question)


class MCQuestionCreateMutation(graphene.Mutation):
    class Arguments:
        course_id = graphene.ID(required=True)
        question_text = graphene.String(required=True)

    question = graphene.Field("graphql_api.schema.MultipleChoiceQuestionType")

    @classmethod
    def mutate(cls, root, info, course_id: str, question_text: str):
        user = get_user_or_error(info)
        try:
            course = Course.objects.get(pk=course_id)
        except Course.DoesNotExist as exc:
            raise GraphQLError("Course not found.") from exc

        check_course_membership(user, course, [CourseMembership.Roles.INSTRUCTOR, CourseMembership.Roles.TEACHING_ASSISTANT])

        question = MultipleChoiceQuestion.objects.create(course=course, question_text=question_text)
        return MCQuestionCreateMutation(question=question)


class MCOptionCreateMutation(graphene.Mutation):
    class Arguments:
        question_id = graphene.ID(required=True)
        option_text = graphene.String(required=True)
        is_correct = graphene.Boolean()
        order_index = graphene.Int()

    option = graphene.Field("graphql_api.schema.MultipleChoiceOptionType")

    @classmethod
    def mutate(cls, root, info, question_id: str, option_text: str, **kwargs):
        user = get_user_or_error(info)
        try:
            question = MultipleChoiceQuestion.objects.select_related("course").get(pk=question_id)
        except MultipleChoiceQuestion.DoesNotExist as exc:
            raise GraphQLError("Question not found.") from exc

        check_course_membership(
            user, question.course, [CourseMembership.Roles.INSTRUCTOR, CourseMembership.Roles.TEACHING_ASSISTANT]
        )

        option = MultipleChoiceOption.objects.create(
            question=question,
            option_text=option_text,
            is_correct=kwargs.get("is_correct", False),
            order_index=kwargs.get("order_index", 0),
        )
        return MCOptionCreateMutation(option=option)


# ============================================================================
# Book Mutations
# ============================================================================


class BookCreateMutation(graphene.Mutation):
    class Arguments:
        course_id = graphene.ID(required=True)
        title = graphene.String(required=True)
        description = graphene.String()

    book = graphene.Field("graphql_api.schema.BookType")

    @classmethod
    def mutate(cls, root, info, course_id: str, title: str, **kwargs):
        user = get_user_or_error(info)
        try:
            course = Course.objects.get(pk=course_id)
        except Course.DoesNotExist as exc:
            raise GraphQLError("Course not found.") from exc

        check_course_membership(user, course, [CourseMembership.Roles.INSTRUCTOR, CourseMembership.Roles.TEACHING_ASSISTANT])

        book = Book.objects.create(course=course, title=title, description=kwargs.get("description", ""))
        return BookCreateMutation(book=book)


class BookChapterCreateMutation(graphene.Mutation):
    class Arguments:
        book_id = graphene.ID(required=True)
        title = graphene.String(required=True)
        markdown_text = graphene.String()
        order_index = graphene.Int()

    chapter = graphene.Field("graphql_api.schema.BookChapterType")

    @classmethod
    def mutate(cls, root, info, book_id: str, title: str, **kwargs):
        user = get_user_or_error(info)
        try:
            book = Book.objects.select_related("course").get(pk=book_id)
        except Book.DoesNotExist as exc:
            raise GraphQLError("Book not found.") from exc

        check_course_membership(user, book.course, [CourseMembership.Roles.INSTRUCTOR, CourseMembership.Roles.TEACHING_ASSISTANT])

        chapter = BookChapter.objects.create(
            book=book,
            title=title,
            markdown_text=kwargs.get("markdown_text", ""),
            order_index=kwargs.get("order_index", 0),
        )
        return BookChapterCreateMutation(chapter=chapter)


# ============================================================================
# Notes Page Mutations
# ============================================================================


class NotesPageCreateMutation(graphene.Mutation):
    class Arguments:
        course_id = graphene.ID(required=True)
        data = graphene.JSONString()
        thumbnail_src = graphene.String()
        thumbnail_dark_src = graphene.String()

    page = graphene.Field("graphql_api.schema.NotesPageType")

    @classmethod
    def mutate(cls, root, info, course_id: str, **kwargs):
        user = get_user_or_error(info)
        try:
            course = Course.objects.get(pk=course_id)
        except Course.DoesNotExist as exc:
            raise GraphQLError("Course not found.") from exc

        check_course_membership(user, course, [CourseMembership.Roles.INSTRUCTOR, CourseMembership.Roles.TEACHING_ASSISTANT])

        max_order = NotesPage.objects.filter(course=course).aggregate(models.Max("order_index"))["order_index__max"] or 0
        page = NotesPage.objects.create(
            course=course,
            author=user,
            order_index=max_order + 1,
            data=kwargs.get("data", {}),
            thumbnail_src=kwargs.get("thumbnail_src", ""),
            thumbnail_dark_src=kwargs.get("thumbnail_dark_src", ""),
        )
        return NotesPageCreateMutation(page=page)


class NotesPageDeleteMutation(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    success = graphene.Boolean()

    @classmethod
    def mutate(cls, root, info, id: str):
        user = get_user_or_error(info)
        try:
            page = NotesPage.objects.select_related("course").get(pk=id)
        except NotesPage.DoesNotExist as exc:
            raise GraphQLError("Notes page not found.") from exc

        check_course_membership(user, page.course, [CourseMembership.Roles.INSTRUCTOR, CourseMembership.Roles.TEACHING_ASSISTANT])
        page.delete()
        return NotesPageDeleteMutation(success=True)


# ============================================================================
# Support System Mutations
# ============================================================================


class SupportTicketCreateMutation(graphene.Mutation):
    class Arguments:
        course_id = graphene.ID()
        subject = graphene.String(required=True)
        description = graphene.String(required=True)

    ticket = graphene.Field("graphql_api.schema.SupportTicketType")

    @classmethod
    def mutate(cls, root, info, subject: str, description: str, **kwargs):
        user = get_user_or_error(info)
        course_id = kwargs.get("course_id")
        course = None
        
        if course_id:
            try:
                course = Course.objects.get(pk=course_id)
            except Course.DoesNotExist as exc:
                raise GraphQLError("Course not found.") from exc
            check_course_membership(user, course)
        
        ticket = SupportTicket.objects.create(
            requester=user,
            course=course,
            subject=subject,
            description=description,
            status=SupportTicket.Status.OPEN,
        )
        return SupportTicketCreateMutation(ticket=ticket)


class SupportTicketUpdateMutation(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        status = graphene.String()

    ticket = graphene.Field("graphql_api.schema.SupportTicketType")

    @classmethod
    def mutate(cls, root, info, id: str, **kwargs):
        user = get_user_or_error(info)
        try:
            ticket = SupportTicket.objects.select_related("course").get(pk=id)
        except SupportTicket.DoesNotExist as exc:
            raise GraphQLError("Support ticket not found.") from exc

        # Check permissions: owner or course staff
        if ticket.requester != user:
            if ticket.course:
                check_course_membership(user, ticket.course, [CourseMembership.Roles.INSTRUCTOR, CourseMembership.Roles.TEACHING_ASSISTANT])
            elif not user.is_superuser:
                raise GraphQLError("Permission denied.")

        if "status" in kwargs:
            status = kwargs["status"]
            if status not in [choice.value for choice in SupportTicket.Status]:
                raise GraphQLError(f"Invalid status. Must be one of: {[s.value for s in SupportTicket.Status]}")
            ticket.status = status
        
        ticket.save()
        return SupportTicketUpdateMutation(ticket=ticket)


class ChatMessageCreateMutation(graphene.Mutation):
    class Arguments:
        ticket_id = graphene.ID()
        course_id = graphene.ID()
        content = graphene.String(required=True)

    message = graphene.Field("graphql_api.schema.ChatMessageType")

    @classmethod
    def mutate(cls, root, info, content: str, **kwargs):
        user = get_user_or_error(info)
        ticket_id = kwargs.get("ticket_id")
        course_id = kwargs.get("course_id")
        
        ticket = None
        course = None
        
        if ticket_id:
            try:
                ticket = SupportTicket.objects.select_related("course").get(pk=ticket_id)
            except SupportTicket.DoesNotExist as exc:
                raise GraphQLError("Support ticket not found.") from exc
            # Check if user can post to this ticket
            if ticket.requester != user and ticket.course:
                check_course_membership(user, ticket.course)
            course = ticket.course
        elif course_id:
            try:
                course = Course.objects.get(pk=course_id)
            except Course.DoesNotExist as exc:
                raise GraphQLError("Course not found.") from exc
            check_course_membership(user, course)
        else:
            raise GraphQLError("Either ticket_id or course_id must be provided.")
        
        message = ChatMessage.objects.create(
            ticket=ticket,
            course=course,
            author=user,
            content=content,
        )
        return ChatMessageCreateMutation(message=message)


# ============================================================================
# Whiteboard Mutations
# ============================================================================


class WhiteboardSessionCreateMutation(graphene.Mutation):
    class Arguments:
        course_id = graphene.ID(required=True)
        title = graphene.String(required=True)

    session = graphene.Field("graphql_api.schema.WhiteboardSessionType")

    @classmethod
    def mutate(cls, root, info, course_id: str, title: str):
        user = get_user_or_error(info)
        try:
            course = Course.objects.get(pk=course_id)
        except Course.DoesNotExist as exc:
            raise GraphQLError("Course not found.") from exc

        check_course_membership(user, course, [CourseMembership.Roles.INSTRUCTOR, CourseMembership.Roles.TEACHING_ASSISTANT])

        session = WhiteboardSession.objects.create(
            course=course,
            instructor=user,
            title=title,
            is_active=True,
        )
        return WhiteboardSessionCreateMutation(session=session)


class WhiteboardSessionUpdateMutation(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        title = graphene.String()
        is_active = graphene.Boolean()

    session = graphene.Field("graphql_api.schema.WhiteboardSessionType")

    @classmethod
    def mutate(cls, root, info, id: str, **kwargs):
        user = get_user_or_error(info)
        try:
            session = WhiteboardSession.objects.select_related("course").get(pk=id)
        except WhiteboardSession.DoesNotExist as exc:
            raise GraphQLError("Whiteboard session not found.") from exc

        check_course_membership(user, session.course, [CourseMembership.Roles.INSTRUCTOR, CourseMembership.Roles.TEACHING_ASSISTANT])

        if "title" in kwargs:
            session.title = kwargs["title"]
        if "is_active" in kwargs:
            session.is_active = kwargs["is_active"]
        
        session.save()
        return WhiteboardSessionUpdateMutation(session=session)


class WhiteboardSessionDeleteMutation(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    success = graphene.Boolean()

    @classmethod
    def mutate(cls, root, info, id: str):
        user = get_user_or_error(info)
        try:
            session = WhiteboardSession.objects.select_related("course").get(pk=id)
        except WhiteboardSession.DoesNotExist as exc:
            raise GraphQLError("Whiteboard session not found.") from exc

        check_course_membership(user, session.course, [CourseMembership.Roles.INSTRUCTOR])
        session.delete()
        return WhiteboardSessionDeleteMutation(success=True)


class WhiteboardStrokeCreateMutation(graphene.Mutation):
    class Arguments:
        session_id = graphene.ID(required=True)
        data = graphene.JSONString(required=True)

    stroke = graphene.Field("graphql_api.schema.WhiteboardStrokeType")

    @classmethod
    def mutate(cls, root, info, session_id: str, data: dict):
        user = get_user_or_error(info)
        try:
            session = WhiteboardSession.objects.select_related("course").get(pk=session_id)
        except WhiteboardSession.DoesNotExist as exc:
            raise GraphQLError("Whiteboard session not found.") from exc

        check_course_membership(user, session.course)

        if not session.is_active:
            raise GraphQLError("This whiteboard session is not active.")

        stroke = WhiteboardStroke.objects.create(
            session=session,
            user=user,
            data=data,
        )
        return WhiteboardStrokeCreateMutation(stroke=stroke)


# ============================================================================
# Course Membership Mutations
# ============================================================================


class CourseMembershipAddMutation(graphene.Mutation):
    class Arguments:
        course_id = graphene.ID(required=True)
        user_email = graphene.String(required=True)
        role = graphene.String(required=True)

    membership = graphene.Field("graphql_api.schema.CourseMembershipType")

    @classmethod
    def mutate(cls, root, info, course_id: str, user_email: str, role: str):
        user = get_user_or_error(info)
        try:
            course = Course.objects.get(pk=course_id)
        except Course.DoesNotExist as exc:
            raise GraphQLError("Course not found.") from exc

        check_course_membership(user, course, [CourseMembership.Roles.INSTRUCTOR])

        # Validate role
        if role not in [r.value for r in CourseMembership.Roles]:
            raise GraphQLError(f"Invalid role. Must be one of: {[r.value for r in CourseMembership.Roles]}")

        # Find target user
        try:
            target_user = User.objects.get(email=user_email)
        except User.DoesNotExist as exc:
            raise GraphQLError(f"User with email '{user_email}' not found.") from exc

        # Create or update membership
        membership, created = CourseMembership.objects.update_or_create(
            course=course,
            user=target_user,
            defaults={"role": role},
        )
        
        return CourseMembershipAddMutation(membership=membership)


class CourseMembershipRemoveMutation(graphene.Mutation):
    class Arguments:
        course_id = graphene.ID(required=True)
        user_id = graphene.ID(required=True)

    success = graphene.Boolean()

    @classmethod
    def mutate(cls, root, info, course_id: str, user_id: str):
        user = get_user_or_error(info)
        try:
            course = Course.objects.get(pk=course_id)
        except Course.DoesNotExist as exc:
            raise GraphQLError("Course not found.") from exc

        check_course_membership(user, course, [CourseMembership.Roles.INSTRUCTOR])

        try:
            membership = CourseMembership.objects.get(course=course, user_id=user_id)
        except CourseMembership.DoesNotExist as exc:
            raise GraphQLError("Membership not found.") from exc

        # Prevent removing the last instructor
        if membership.role == CourseMembership.Roles.INSTRUCTOR:
            instructor_count = CourseMembership.objects.filter(
                course=course, role=CourseMembership.Roles.INSTRUCTOR
            ).count()
            if instructor_count <= 1:
                raise GraphQLError("Cannot remove the last instructor from the course.")

        membership.delete()
        return CourseMembershipRemoveMutation(success=True)


class CourseMembershipUpdateRoleMutation(graphene.Mutation):
    class Arguments:
        course_id = graphene.ID(required=True)
        user_id = graphene.ID(required=True)
        role = graphene.String(required=True)

    membership = graphene.Field("graphql_api.schema.CourseMembershipType")

    @classmethod
    def mutate(cls, root, info, course_id: str, user_id: str, role: str):
        user = get_user_or_error(info)
        try:
            course = Course.objects.get(pk=course_id)
        except Course.DoesNotExist as exc:
            raise GraphQLError("Course not found.") from exc

        check_course_membership(user, course, [CourseMembership.Roles.INSTRUCTOR])

        # Validate role
        if role not in [r.value for r in CourseMembership.Roles]:
            raise GraphQLError(f"Invalid role. Must be one of: {[r.value for r in CourseMembership.Roles]}")

        try:
            membership = CourseMembership.objects.get(course=course, user_id=user_id)
        except CourseMembership.DoesNotExist as exc:
            raise GraphQLError("Membership not found.") from exc

        # Prevent changing role if it would leave no instructors
        if membership.role == CourseMembership.Roles.INSTRUCTOR and role != CourseMembership.Roles.INSTRUCTOR:
            instructor_count = CourseMembership.objects.filter(
                course=course, role=CourseMembership.Roles.INSTRUCTOR
            ).count()
            if instructor_count <= 1:
                raise GraphQLError("Cannot change role: this is the last instructor in the course.")

        membership.role = role
        membership.save()
        return CourseMembershipUpdateRoleMutation(membership=membership)


# ============================================================================
# Assignment Extension Mutations
# ============================================================================


class AssignmentExtensionCreateMutation(graphene.Mutation):
    class Arguments:
        assignment_id = graphene.ID(required=True)
        user_id = graphene.ID(required=True)
        due_at = graphene.DateTime(required=True)

    extension = graphene.Field("graphql_api.schema.AssignmentExtensionType")

    @classmethod
    def mutate(cls, root, info, assignment_id: str, user_id: str, due_at):
        user = get_user_or_error(info)
        try:
            assignment = Assignment.objects.select_related("course").get(pk=assignment_id)
        except Assignment.DoesNotExist as exc:
            raise GraphQLError("Assignment not found.") from exc

        check_course_membership(user, assignment.course, [CourseMembership.Roles.INSTRUCTOR, CourseMembership.Roles.TEACHING_ASSISTANT])

        try:
            target_user = User.objects.get(pk=user_id)
        except User.DoesNotExist as exc:
            raise GraphQLError("User not found.") from exc

        # Verify target user is enrolled in the course
        check_course_membership(target_user, assignment.course)

        extension, created = AssignmentExtension.objects.update_or_create(
            assignment=assignment,
            user=target_user,
            defaults={"due_at": due_at},
        )
        return AssignmentExtensionCreateMutation(extension=extension)


# ============================================================================
# Asset Mutations
# ============================================================================


class AssetCreateMutation(graphene.Mutation):
    class Arguments:
        course_id = graphene.ID()
        book_id = graphene.ID()
        name = graphene.String(required=True)
        type = graphene.String(required=True)
        url = graphene.String(required=True)
        thumbnail_url = graphene.String()

    asset = graphene.Field("graphql_api.schema.AssetType")

    @classmethod
    def mutate(cls, root, info, name: str, type: str, url: str, **kwargs):
        from assets.models import Asset
        
        user = get_user_or_error(info)
        course_id = kwargs.get("course_id")
        book_id = kwargs.get("book_id")
        
        course = None
        book = None
        
        if course_id:
            try:
                course = Course.objects.get(pk=course_id)
            except Course.DoesNotExist as exc:
                raise GraphQLError("Course not found.") from exc
            check_course_membership(user, course, [CourseMembership.Roles.INSTRUCTOR, CourseMembership.Roles.TEACHING_ASSISTANT])
        
        if book_id:
            try:
                book = Book.objects.select_related("course").get(pk=book_id)
            except Book.DoesNotExist as exc:
                raise GraphQLError("Book not found.") from exc
            check_course_membership(user, book.course, [CourseMembership.Roles.INSTRUCTOR, CourseMembership.Roles.TEACHING_ASSISTANT])
            course = book.course
        
        if not course and not book:
            raise GraphQLError("Either course_id or book_id must be provided.")
        
        asset = Asset.objects.create(
            uploader=user,
            course=course,
            book=book,
            name=name,
            type=type,
            url=url,
            thumbnail_url=kwargs.get("thumbnail_url", ""),
        )
        return AssetCreateMutation(asset=asset)


class AssetDeleteMutation(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    success = graphene.Boolean()

    @classmethod
    def mutate(cls, root, info, id: str):
        from assets.models import Asset
        
        user = get_user_or_error(info)
        try:
            asset = Asset.objects.select_related("course", "book__course").get(pk=id)
        except Asset.DoesNotExist as exc:
            raise GraphQLError("Asset not found.") from exc

        course = asset.course or (asset.book.course if asset.book else None)
        if course:
            check_course_membership(user, course, [CourseMembership.Roles.INSTRUCTOR, CourseMembership.Roles.TEACHING_ASSISTANT])
        else:
            # If no course, only uploader or superuser can delete
            if asset.uploader != user and not user.is_superuser:
                raise GraphQLError("Permission denied.")
        
        asset.delete()
        return AssetDeleteMutation(success=True)


# ============================================================================
# Deck Mutations
# ============================================================================


class DeckCreateMutation(graphene.Mutation):
    class Arguments:
        course_id = graphene.ID(required=True)
        title = graphene.String(required=True)
        embed_code = graphene.String()

    deck = graphene.Field("graphql_api.schema.DeckType")

    @classmethod
    def mutate(cls, root, info, course_id: str, title: str, **kwargs):
        user = get_user_or_error(info)
        try:
            course = Course.objects.get(pk=course_id)
        except Course.DoesNotExist as exc:
            raise GraphQLError("Course not found.") from exc

        check_course_membership(user, course, [CourseMembership.Roles.INSTRUCTOR, CourseMembership.Roles.TEACHING_ASSISTANT])

        deck = Deck.objects.create(
            course=course,
            title=title,
            embed_code=kwargs.get("embed_code", ""),
        )
        return DeckCreateMutation(deck=deck)


class DeckUpdateMutation(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        title = graphene.String()
        embed_code = graphene.String()

    deck = graphene.Field("graphql_api.schema.DeckType")

    @classmethod
    def mutate(cls, root, info, id: str, **kwargs):
        user = get_user_or_error(info)
        try:
            deck = Deck.objects.select_related("course").get(pk=id)
        except Deck.DoesNotExist as exc:
            raise GraphQLError("Deck not found.") from exc

        check_course_membership(user, deck.course, [CourseMembership.Roles.INSTRUCTOR, CourseMembership.Roles.TEACHING_ASSISTANT])

        if "title" in kwargs:
            deck.title = kwargs["title"]
        if "embed_code" in kwargs:
            deck.embed_code = kwargs["embed_code"]
        
        deck.save()
        return DeckUpdateMutation(deck=deck)


class DeckDeleteMutation(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    success = graphene.Boolean()

    @classmethod
    def mutate(cls, root, info, id: str):
        user = get_user_or_error(info)
        try:
            deck = Deck.objects.select_related("course").get(pk=id)
        except Deck.DoesNotExist as exc:
            raise GraphQLError("Deck not found.") from exc

        check_course_membership(user, deck.course, [CourseMembership.Roles.INSTRUCTOR])
        deck.delete()
        return DeckDeleteMutation(success=True)

