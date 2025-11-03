"""Question bank models."""

from django.db import models


class FreeResponseQuestion(models.Model):
    """Open-ended question authored for a course."""

    course = models.ForeignKey(
        "courses.Course",
        on_delete=models.CASCADE,
        related_name="free_response_questions",
    )
    question_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)
        verbose_name = "Free Response Question"
        verbose_name_plural = "Free Response Questions"

    def __str__(self) -> str:
        return self.question_text[:80]


class MultipleChoiceQuestion(models.Model):
    """Multiple-choice question with related options."""

    course = models.ForeignKey(
        "courses.Course",
        on_delete=models.CASCADE,
        related_name="multiple_choice_questions",
    )
    question_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)
        verbose_name = "Multiple Choice Question"
        verbose_name_plural = "Multiple Choice Questions"

    def __str__(self) -> str:
        return self.question_text[:80]


class MultipleChoiceOption(models.Model):
    """Answer option for a multiple-choice question."""

    question = models.ForeignKey(
        MultipleChoiceQuestion,
        on_delete=models.CASCADE,
        related_name="options",
    )
    order_index = models.PositiveIntegerField(default=0)
    option_text = models.TextField()
    is_correct = models.BooleanField(default=False)

    class Meta:
        ordering = ("question", "order_index")
        verbose_name = "Multiple Choice Option"
        verbose_name_plural = "Multiple Choice Options"

    def __str__(self) -> str:
        return self.option_text[:80]


__all__ = [
    "FreeResponseQuestion",
    "MultipleChoiceQuestion",
    "MultipleChoiceOption",
]

