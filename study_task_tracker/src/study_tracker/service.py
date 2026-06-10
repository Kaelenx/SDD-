"""Backward-compatible application imports.

New code should import from `study_tracker.application.task_service`.
"""

from .application.task_service import CourseSummary, StudyTaskService, TaskSummary

__all__ = ["CourseSummary", "StudyTaskService", "TaskSummary"]
