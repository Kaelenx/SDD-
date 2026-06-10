"""JSON serializers for web responses."""

from __future__ import annotations

from typing import Any

from ..application.task_service import CourseSummary, TaskSummary


JsonObject = dict[str, Any]


def summary_to_dict(summary: TaskSummary) -> JsonObject:
    return {
        "total": summary.total,
        "pending": summary.pending,
        "done": summary.done,
        "overdue": summary.overdue,
        "completion_rate": summary.completion_rate,
        "total_estimated_hours": summary.total_estimated_hours,
        "remaining_estimated_hours": summary.remaining_estimated_hours,
    }


def course_summary_to_dict(summary: CourseSummary) -> JsonObject:
    return {
        "course": summary.course,
        "total": summary.total,
        "pending": summary.pending,
        "done": summary.done,
        "overdue": summary.overdue,
        "remaining_estimated_hours": summary.remaining_estimated_hours,
    }
