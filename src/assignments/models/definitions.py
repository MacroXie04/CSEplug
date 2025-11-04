"""Backwards-compatible exports for legacy imports."""

from .assignment import Assignment, AssignmentExtension
from .questions import AssignmentQuestion
from .submissions import Submission, SubmissionOutcome

__all__ = [
    "Assignment",
    "AssignmentExtension",
    "AssignmentQuestion",
    "Submission",
    "SubmissionOutcome",
]

