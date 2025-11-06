"""Common abstract models and utilities for reuse across apps."""

from __future__ import annotations

import datetime as _dt
from dataclasses import dataclass
from typing import Any, Dict, Optional

from django.db import models


@dataclass(frozen=True)
class DateTimeTimezoneValue:
    """Value object representing a UTC datetime paired with a timezone string."""

    utc_value: Optional[_dt.datetime]
    timezone: Optional[str]

    def as_dict(self) -> Dict[str, Optional[str]]:
        """Return the pair as a serialisable dictionary."""

        return {"utc_value": self.utc_value, "timezone": self.timezone}


class DateTimeTimezoneField:
    """Descriptor managing a UTC/timezone field pair on a Django model."""

    def __init__(self, utc_field: str, timezone_field: str):
        self.utc_field = utc_field
        self.timezone_field = timezone_field
        self.name: Optional[str] = None

    def __set_name__(self, owner: type[models.Model], name: str) -> None:
        self.name = name

    def __get__(self, instance: Optional[models.Model], owner: type[models.Model]):
        if instance is None:
            return self
        return DateTimeTimezoneValue(
            getattr(instance, self.utc_field),
            getattr(instance, self.timezone_field),
        )

    def __set__(self, instance: models.Model, value: Any) -> None:
        if value is None:
            setattr(instance, self.utc_field, None)
            setattr(instance, self.timezone_field, None)
            return

        if isinstance(value, DateTimeTimezoneValue):
            utc_value = value.utc_value
            timezone = value.timezone
        elif isinstance(value, dict):
            utc_value = value.get("utc_value")
            timezone = value.get("timezone")
        elif isinstance(value, (tuple, list)):
            try:
                utc_value, timezone = value
            except ValueError as exc:  # pragma: no cover - defensive
                raise ValueError(
                    "Iterable assigned to DateTimeTimezoneField must have exactly two elements"
                ) from exc
        else:  # pragma: no cover - defensive branch
            raise TypeError(
                "DateTimeTimezoneField expects DateTimeTimezoneValue, dict, tuple, list, or None"
            )

        setattr(instance, self.utc_field, utc_value)
        setattr(instance, self.timezone_field, timezone)

    def contribute_to_class(self, cls: type[models.Model], name: str) -> None:
        """Ensure descriptor binding when used via assignment in model class body."""

        self.__set_name__(cls, name)
        setattr(cls, name, self)


class BaseModelWithPermissions(models.Model):
    """Abstract base model providing default object-level permission hooks."""

    class Meta:
        abstract = True

    def can_view(self, user) -> bool:  # type: ignore[override]
        """Return whether the given user may view this object."""

        return bool(getattr(user, "is_authenticated", False))

    def can_edit(self, user) -> bool:  # type: ignore[override]
        """Return whether the given user may edit this object."""

        return bool(getattr(user, "is_staff", False))

    def can_delete(self, user) -> bool:  # type: ignore[override]
        """Return whether the given user may delete this object."""

        return self.can_edit(user)


class TimestampedModel(BaseModelWithPermissions):
    """Abstract base model providing timestamp fields for created and updated times."""

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


__all__ = [
    "BaseModelWithPermissions",
    "DateTimeTimezoneField",
    "DateTimeTimezoneValue",
    "TimestampedModel",
]

