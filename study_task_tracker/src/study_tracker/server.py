"""HTTP backend and static file server for the study task tracker."""

from __future__ import annotations

import argparse
from collections.abc import Callable
from datetime import date
import json
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

from .models import StudyTrackerError
from .service import StudyTaskService, TaskSummary
from .store import JsonTaskRepository


JsonObject = dict[str, Any]


def make_handler(
    data_file: str | Path,
    frontend_dir: str | Path,
    today_provider: Callable[[], date] = date.today,
) -> type[SimpleHTTPRequestHandler]:
    """Create a request handler bound to a data file and frontend directory."""

    data_path = Path(data_file)
    static_root = Path(frontend_dir)

    class StudyTrackerRequestHandler(SimpleHTTPRequestHandler):
        server_version = "StudyTrackerHTTP/0.1"

        def __init__(self, *args, **kwargs) -> None:
            super().__init__(*args, directory=str(static_root), **kwargs)

        def do_GET(self) -> None:
            parsed = urlparse(self.path)
            if parsed.path == "/api/health":
                self._send_json({"status": "ok"})
                return
            if parsed.path == "/api/tasks":
                query = parse_qs(parsed.query)
                status = query.get("status", [None])[0] or None
                priority = query.get("priority", [None])[0] or None
                search_query = query.get("q", [None])[0] or None
                self._handle_json(
                    lambda service: [
                        task.to_dict()
                        for task in service.list_tasks(
                            status=status,
                            priority=priority,
                            query=search_query,
                        )
                    ]
                )
                return
            if parsed.path == "/api/summary":
                self._handle_json(lambda service: summary_to_dict(service.summary()))
                return
            super().do_GET()

        def do_POST(self) -> None:
            parsed = urlparse(self.path)
            if parsed.path != "/api/tasks":
                self._send_json({"error": "not found"}, status=HTTPStatus.NOT_FOUND)
                return
            body = self._read_json_body()
            if body is None:
                return
            self._handle_json(
                lambda service: service.add_task(
                    title=body.get("title", ""),
                    course=body.get("course"),
                    due_date=body.get("due_date", ""),
                    priority=body.get("priority"),
                ).to_dict(),
                status=HTTPStatus.CREATED,
            )

        def do_PATCH(self) -> None:
            parsed = urlparse(self.path)
            task_id_for_complete = match_task_action(parsed.path, "complete")
            if task_id_for_complete is not None:
                self._handle_json(lambda service: service.complete_task(task_id_for_complete).to_dict())
                return

            task_id = match_task_path(parsed.path)
            if task_id is None:
                self._send_json({"error": "not found"}, status=HTTPStatus.NOT_FOUND)
                return
            body = self._read_json_body()
            if body is None:
                return
            self._handle_json(
                lambda service: service.update_task(
                    task_id=task_id,
                    title=body.get("title", ""),
                    course=body.get("course"),
                    due_date=body.get("due_date", ""),
                    priority=body.get("priority"),
                ).to_dict()
            )

        def do_DELETE(self) -> None:
            parsed = urlparse(self.path)
            task_id = match_task_path(parsed.path)
            if task_id is None:
                self._send_json({"error": "not found"}, status=HTTPStatus.NOT_FOUND)
                return
            self._handle_json(lambda service: service.delete_task(task_id).to_dict())

        def _service(self) -> StudyTaskService:
            return StudyTaskService(JsonTaskRepository(data_path), today_provider=today_provider)

        def _handle_json(
            self,
            operation: Callable[[StudyTaskService], Any],
            status: HTTPStatus = HTTPStatus.OK,
        ) -> None:
            try:
                payload = operation(self._service())
            except StudyTrackerError as exc:
                self._send_json({"error": str(exc)}, status=HTTPStatus.BAD_REQUEST)
                return
            self._send_json(payload, status=status)

        def _read_json_body(self) -> JsonObject | None:
            try:
                length = int(self.headers.get("Content-Length", "0"))
            except ValueError:
                self._send_json({"error": "invalid content length"}, status=HTTPStatus.BAD_REQUEST)
                return None
            try:
                raw_body = self.rfile.read(length).decode("utf-8") if length else "{}"
                body = json.loads(raw_body)
            except (UnicodeDecodeError, json.JSONDecodeError):
                self._send_json({"error": "request body must be valid JSON"}, status=HTTPStatus.BAD_REQUEST)
                return None
            if not isinstance(body, dict):
                self._send_json({"error": "request body must be a JSON object"}, status=HTTPStatus.BAD_REQUEST)
                return None
            return body

        def _send_json(self, payload: Any, status: HTTPStatus = HTTPStatus.OK) -> None:
            encoded = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(encoded)))
            self.end_headers()
            self.wfile.write(encoded)

        def log_message(self, format: str, *args) -> None:
            return

    return StudyTrackerRequestHandler


def match_task_path(path: str) -> str | None:
    parts = [part for part in path.split("/") if part]
    if len(parts) == 3 and parts[0] == "api" and parts[1] == "tasks":
        return parts[2]
    return None


def match_task_action(path: str, action: str) -> str | None:
    parts = [part for part in path.split("/") if part]
    if len(parts) == 4 and parts[0] == "api" and parts[1] == "tasks" and parts[3] == action:
        return parts[2]
    return None


def summary_to_dict(summary: TaskSummary) -> JsonObject:
    return {
        "total": summary.total,
        "pending": summary.pending,
        "done": summary.done,
        "overdue": summary.overdue,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the study task tracker web app.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", default=8765, type=int)
    parser.add_argument("--data-file", default="data/tasks.json", type=Path)
    parser.add_argument(
        "--frontend-dir",
        default=Path(__file__).resolve().parents[2] / "frontend",
        type=Path,
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    handler = make_handler(args.data_file, args.frontend_dir)
    httpd = ThreadingHTTPServer((args.host, args.port), handler)
    print(f"Study Task Tracker running at http://{args.host}:{args.port}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
    finally:
        httpd.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
