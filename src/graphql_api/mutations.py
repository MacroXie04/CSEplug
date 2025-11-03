"""GraphQL mutations for CSE Plug."""

from typing import Optional

import graphene
from django.contrib.auth import authenticate, get_user_model
from graphql import GraphQLError

from accounts.services import (
    blacklist_refresh_token,
    clear_jwt_cookies,
    generate_tokens,
    set_jwt_cookies,
)
from accounts.constants import REFRESH_COOKIE_NAME
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

