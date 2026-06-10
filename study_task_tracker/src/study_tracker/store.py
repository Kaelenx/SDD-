"""Backward-compatible infrastructure imports.

New code should import from `study_tracker.infrastructure.json_repository`.
"""

from .infrastructure.json_repository import JsonTaskRepository

__all__ = ["JsonTaskRepository"]
