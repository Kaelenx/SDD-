"""Business operations for study task tracking."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import date
import re

from .models import StudyTask, TaskNotFoundError, ValidationError, normalize_priority, normalize_status
from .store import JsonTaskRepository


PRIORITY_SORT = {"high": 0, "medium": 1, "low": 2}
TASK_ID_PATTERN = re.compile(r"^T(\d{4,})$")


@dataclass(frozen=True)
class TaskSummary:
    total: int
    pending: int
    done: int
    overdue: int


class StudyTaskService:
    """Coordinate validation, persistence, and study task use cases."""

    def __init__(
        self,
        repository: JsonTaskRepository,
        today_provider: Callable[[], date] = date.today,
    ) -> None:
        self.repository = repository
        self.today_provider = today_provider

    def add_task(
        self,
        title: str,
        due_date: str,
        course: str | None = None,
        priority: str | None = None,
    ) -> StudyTask:
        tasks = self.repository.load_all()
        task = StudyTask.new(
            task_id=self._next_task_id(tasks),
            title=title,
            due_date=due_date,
            created_at=self.today_provider().isoformat(),
            course=course,
            priority=priority,
        )
        tasks.append(task)
        self.repository.save_all(tasks)
        return task

    def list_tasks(
        self,
        status: str | None = None,
        priority: str | None = None,
        query: str | None = None,
    ) -> list[StudyTask]:
        tasks = self.repository.load_all()
        if status is not None:
            normalized_status = normalize_status(status)
            tasks = [task for task in tasks if task.status == normalized_status]
        if priority is not None:
            normalized_priority = normalize_priority(priority)
            tasks = [task for task in tasks if task.priority == normalized_priority]
        if query is not None and query.strip():
            normalized_query = query.strip().casefold()
            tasks = [
                task
                for task in tasks
                if normalized_query in task.title.casefold()
                or normalized_query in task.course.casefold()
                or normalized_query in task.id.casefold()
            ]
        return sorted(tasks, key=lambda task: (task.due_date, PRIORITY_SORT[task.priority], task.id))

    def complete_task(self, task_id: str) -> StudyTask:
        tasks = self.repository.load_all()
        task = self._find_task(tasks, task_id)
        if task.status == "done":
            return task

        completed = task.mark_done(self.today_provider().isoformat())
        updated_tasks = [completed if item.id == task.id else item for item in tasks]
        self.repository.save_all(updated_tasks)
        return completed

    def update_task(
        self,
        task_id: str,
        title: str,
        due_date: str,
        course: str | None = None,
        priority: str | None = None,
    ) -> StudyTask:
        tasks = self.repository.load_all()
        task = self._find_task(tasks, task_id)
        updated = task.update_details(
            title=title,
            course=course,
            due_date=due_date,
            priority=priority,
        )
        updated_tasks = [updated if item.id == task.id else item for item in tasks]
        self.repository.save_all(updated_tasks)
        return updated

    def delete_task(self, task_id: str) -> StudyTask:
        tasks = self.repository.load_all()
        task = self._find_task(tasks, task_id)
        self.repository.save_all([item for item in tasks if item.id != task.id])
        return task

    def summary(self) -> TaskSummary:
        tasks = self.repository.load_all()
        today = self.today_provider()
        pending = sum(1 for task in tasks if task.status == "pending")
        done = sum(1 for task in tasks if task.status == "done")
        overdue = sum(1 for task in tasks if task.is_overdue(today))
        return TaskSummary(total=len(tasks), pending=pending, done=done, overdue=overdue)

    def _find_task(self, tasks: list[StudyTask], task_id: str) -> StudyTask:
        if not isinstance(task_id, str) or not task_id.strip():
            raise ValidationError("task id is required")
        normalized_id = task_id.strip()
        for task in tasks:
            if task.id == normalized_id:
                return task
        raise TaskNotFoundError(f"task not found: {normalized_id}")

    def _next_task_id(self, tasks: list[StudyTask]) -> str:
        max_number = 0
        for task in tasks:
            match = TASK_ID_PATTERN.match(task.id)
            if match:
                max_number = max(max_number, int(match.group(1)))
        return f"T{max_number + 1:04d}"
