"""Backward-compatible domain imports.

New code should import from `study_tracker.domain.task`.
"""

from .domain.task import *  # noqa: F401,F403
