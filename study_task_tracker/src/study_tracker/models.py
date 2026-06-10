"""Domain models and validation rules for study tasks."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
import re
from typing import Any


PRIORITIES = {"low", "medium", "high"}
STATUSES = {"pending", "done"}
DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")


class StudyTrackerError(Exception):
    """Base exception for expected application errors."""


class ValidationError(StudyTrackerError):
    """Raised when user input or persisted task data is invalid."""


class TaskNotFoundError(StudyTrackerError):
    """Raised when a task ID cannot be found."""


class StorageError(StudyTrackerError):
    """Raised when task data cannot be read or written safely."""


def parse_iso_date(value: str, field_name: str) -> date:
    """Parse and validate a strict YYYY-MM-DD date string."""
    if not isinstance(value, str) or not DATE_PATTERN.match(value):
        raise ValidationError(f"{field_name} must use YYYY-MM-DD format")
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise ValidationError(f"{field_name} must be a real calendar date") from exc


def normalize_title(title: str) -> str:
    if not isinstance(title, str):
        raise ValidationError("title must be text")
    normalized = title.strip()
    if not normalized:
        raise ValidationError("title is required")
    if len(normalized) > 80:
        raise ValidationError("title must be at most 80 characters")
    return normalized


def normalize_course(course: str | None) -> str:
    if course is None:
        return "General"
    if not isinstance(course, str):
        raise ValidationError("course must be text")
    normalized = course.strip() or "General"
    if len(normalized) > 40:
        raise ValidationError("course must be at most 40 characters")
    return normalized


def normalize_priority(priority: str | None) -> str:
    if priority is None:
        return "medium"
    if not isinstance(priority, str):
        raise ValidationError("priority must be text")
    normalized = priority.strip().lower()
    if normalized not in PRIORITIES:
        raise ValidationError("priority must be one of: low, medium, high")
    return normalized


def normalize_status(status: str) -> str:
    if not isinstance(status, str):
        raise ValidationError("status must be text")
    normalized = status.strip().lower()
    if normalized not in STATUSES:
        raise ValidationError("status must be pending or done")
    return normalized


@dataclass(frozen=True)
class StudyTask:
    id: str
    title: str
    course: str
    due_date: str
    priority: str
    status: str
    created_at: str
    completed_at: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.id, str) or not self.id.strip():
            raise ValidationError("id is required")
        object.__setattr__(self, "id", self.id.strip())
        object.__setattr__(self, "title", normalize_title(self.title))
        object.__setattr__(self, "course", normalize_course(self.course))
        object.__setattr__(self, "due_date", parse_iso_date(self.due_date, "due_date").isoformat())
        object.__setattr__(self, "priority", normalize_priority(self.priority))
        object.__setattr__(self, "status", normalize_status(self.status))
        object.__setattr__(self, "created_at", parse_iso_date(self.created_at, "created_at").isoformat())
        if self.completed_at is not None:
            object.__setattr__(
                self,
                "completed_at",
                parse_iso_date(self.completed_at, "completed_at").isoformat(),
            )
        if self.status == "pending" and self.completed_at is not None:
            raise ValidationError("pending tasks cannot have completed_at")

    @classmethod
    def new(
        cls,
        task_id: str,
        title: str,
        due_date: str,
        created_at: str,
        course: str | None = None,
        priority: str | None = None,
    ) -> "StudyTask":
        return cls(
            id=task_id,
            title=title,
            course=normalize_course(course),
            due_date=due_date,
            priority=normalize_priority(priority),
            status="pending",
            created_at=created_at,
            completed_at=None,
        )

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "StudyTask":
        required = {"id", "title", "course", "due_date", "priority", "status", "created_at"}
        missing = sorted(required - set(raw))
        if missing:
            raise ValidationError(f"missing task fields: {', '.join(missing)}")
        return cls(
            id=raw["id"],
            title=raw["title"],
            course=raw["course"],
            due_date=raw["due_date"],
            priority=raw["priority"],
            status=raw["status"],
            created_at=raw["created_at"],
            completed_at=raw.get("completed_at"),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "course": self.course,
            "due_date": self.due_date,
            "priority": self.priority,
            "status": self.status,
            "created_at": self.created_at,
            "completed_at": self.completed_at,
        }

    def mark_done(self, completed_at: str) -> "StudyTask":
        return StudyTask(
            id=self.id,
            title=self.title,
            course=self.course,
            due_date=self.due_date,
            priority=self.priority,
            status="done",
            created_at=self.created_at,
            completed_at=completed_at,
        )

    def update_details(
        self,
        title: str,
        course: str | None,
        due_date: str,
        priority: str | None,
    ) -> "StudyTask":
        return StudyTask(
            id=self.id,
            title=title,
            course=normalize_course(course),
            due_date=due_date,
            priority=normalize_priority(priority),
            status=self.status,
            created_at=self.created_at,
            completed_at=self.completed_at,
        )

    def is_overdue(self, today: date) -> bool:
        return self.status == "pending" and parse_iso_date(self.due_date, "due_date") < today
