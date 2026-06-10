"""Backward-compatible server entry point.

New code should import from `study_tracker.web.http_server`.
"""

from .web.http_server import build_parser, main, make_handler, match_task_action, match_task_path

__all__ = ["build_parser", "main", "make_handler", "match_task_action", "match_task_path"]


if __name__ == "__main__":
    raise SystemExit(main())


if __name__ == "__main__":
    raise SystemExit(main())
