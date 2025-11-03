"""GraphQL permission decorators and helpers."""

from functools import wraps
from typing import Callable

from graphql import GraphQLError

from courses.models import CourseMembership


def require_auth(resolver: Callable) -> Callable:
    """Decorator to require authenticated user."""

    @wraps(resolver)
    def wrapper(root, info, *args, **kwargs):
        user = info.context.user
        if not user or not user.is_authenticated:
            raise GraphQLError("Authentication required.")
        return resolver(root, info, *args, **kwargs)

    return wrapper


def require_roles(*allowed_roles: str) -> Callable:
    """Decorator to require specific course membership roles."""

    def decorator(resolver: Callable) -> Callable:
        @wraps(resolver)
        def wrapper(root, info, *args, **kwargs):
            user = info.context.user
            if not user or not user.is_authenticated:
                raise GraphQLError("Authentication required.")

            course_id = kwargs.get("course_id") or kwargs.get("courseId")
            if not course_id:
                if user.is_superuser:
                    return resolver(root, info, *args, **kwargs)
                raise GraphQLError(f"Course ID required to verify roles: {allowed_roles}")

            membership = CourseMembership.objects.filter(course_id=course_id, user=user).first()
            if not membership and not user.is_superuser:
                raise GraphQLError("You are not a member of this course.")

            if user.is_superuser or (membership and membership.role in allowed_roles):
                return resolver(root, info, *args, **kwargs)

            raise GraphQLError(f"Permission denied. Required roles: {allowed_roles}")

        return wrapper

    return decorator


def get_user_or_error(info):
    """Get authenticated user or raise error."""
    user = info.context.user
    if not user or not user.is_authenticated:
        raise GraphQLError("Authentication required.")
    return user


def check_course_membership(user, course, roles: list[str] | None = None) -> CourseMembership | None:
    """Check if user is a member of the course with optional role filtering."""
    if user.is_superuser:
        return None

    membership = CourseMembership.objects.filter(course=course, user=user).first()
    if not membership:
        raise GraphQLError("You are not a member of this course.")

    if roles and membership.role not in roles:
        raise GraphQLError(f"Permission denied. Required roles: {roles}")

    return membership

