"""JSON persistence for study tasks."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

from .models import StorageError, StudyTask, ValidationError


class JsonTaskRepository:
    """Store tasks in a local JSON file."""

    def __init__(self, path: str | Path = "tasks.json") -> None:
        self.path = Path(path)

    def load_all(self) -> list[StudyTask]:
        if not self.path.exists():
            return []

        try:
            text = self.path.read_text(encoding="utf-8")
        except OSError as exc:
            raise StorageError(f"cannot read data file: {self.path}") from exc

        if not text.strip():
            return []

        try:
            raw_tasks = json.loads(text)
        except json.JSONDecodeError as exc:
            raise StorageError(f"data file is not valid JSON: {self.path}") from exc

        if not isinstance(raw_tasks, list):
            raise StorageError("data file must contain a JSON array")

        tasks: list[StudyTask] = []
        for index, raw_task in enumerate(raw_tasks, start=1):
            if not isinstance(raw_task, dict):
                raise StorageError(f"task #{index} must be a JSON object")
            try:
                tasks.append(StudyTask.from_dict(raw_task))
            except (TypeError, ValidationError) as exc:
                raise StorageError(f"task #{index} is invalid: {exc}") from exc
        return tasks

    def save_all(self, tasks: Iterable[StudyTask]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = [task.to_dict() for task in tasks]
        temp_path = self.path.with_suffix(self.path.suffix + ".tmp")
        try:
            temp_path.write_text(
                json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            temp_path.replace(self.path)
        except OSError as exc:
            raise StorageError(f"cannot write data file: {self.path}") from exc
