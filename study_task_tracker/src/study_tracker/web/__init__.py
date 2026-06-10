"""Web adapter exports."""

from .http_server import build_parser, main, make_handler, match_task_action, match_task_path

__all__ = ["build_parser", "main", "make_handler", "match_task_action", "match_task_path"]
