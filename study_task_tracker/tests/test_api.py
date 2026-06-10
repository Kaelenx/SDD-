import json
import sys
import tempfile
import threading
import unittest
from datetime import date
from http.server import ThreadingHTTPServer
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from study_tracker.server import make_handler


class ApiTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp_dir = tempfile.TemporaryDirectory()
        cls.data_file = Path(cls.temp_dir.name) / "tasks.json"
        handler = make_handler(
            cls.data_file,
            ROOT / "frontend",
            today_provider=lambda: date(2026, 6, 10),
        )
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
        cls.base_url = f"http://127.0.0.1:{cls.server.server_port}"
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=5)
        cls.temp_dir.cleanup()

    def setUp(self):
        if self.data_file.exists():
            self.data_file.unlink()

    def request_json(self, method, path, body=None):
        data = None if body is None else json.dumps(body).encode("utf-8")
        request = Request(
            self.base_url + path,
            data=data,
            method=method,
            headers={"Content-Type": "application/json"},
        )
        with urlopen(request, timeout=5) as response:
            return response.status, json.loads(response.read().decode("utf-8"))

    def test_health_endpoint(self):
        status, payload = self.request_json("GET", "/api/health")

        self.assertEqual(status, 200)
        self.assertEqual(payload, {"status": "ok"})

    def test_create_list_complete_delete_task(self):
        created_status, task = self.request_json(
            "POST",
            "/api/tasks",
            {
                "title": "完成前后端作业",
                "course": "软件工程",
                "due_date": "2026-06-12",
                "priority": "high",
                "notes": "接口联调",
                "estimated_hours": 2.5,
            },
        )
        list_status, tasks = self.request_json("GET", "/api/tasks")
        complete_status, completed = self.request_json("PATCH", f"/api/tasks/{task['id']}/complete")
        summary_status, summary = self.request_json("GET", "/api/summary")
        delete_status, deleted = self.request_json("DELETE", f"/api/tasks/{task['id']}")

        self.assertEqual(created_status, 201)
        self.assertEqual(task["id"], "T0001")
        self.assertEqual(task["notes"], "接口联调")
        self.assertEqual(task["estimated_hours"], 2.5)
        self.assertEqual(list_status, 200)
        self.assertEqual(len(tasks), 1)
        self.assertEqual(complete_status, 200)
        self.assertEqual(completed["status"], "done")
        self.assertEqual(summary_status, 200)
        self.assertEqual(summary["done"], 1)
        self.assertEqual(delete_status, 200)
        self.assertEqual(deleted["id"], "T0001")

    def test_filter_pending_tasks(self):
        self.request_json("POST", "/api/tasks", {"title": "任务一", "due_date": "2026-06-12"})
        _, second = self.request_json("POST", "/api/tasks", {"title": "任务二", "due_date": "2026-06-13"})
        self.request_json("PATCH", f"/api/tasks/{second['id']}/complete")

        status, tasks = self.request_json("GET", "/api/tasks?status=pending")

        self.assertEqual(status, 200)
        self.assertEqual([task["title"] for task in tasks], ["任务一"])

    def test_filter_by_priority_and_search_query(self):
        self.request_json(
            "POST",
            "/api/tasks",
            {"title": "Python 练习", "course": "编程", "due_date": "2026-06-12", "priority": "high"},
        )
        self.request_json(
            "POST",
            "/api/tasks",
            {"title": "英语阅读", "course": "英语", "due_date": "2026-06-13", "priority": "low"},
        )

        status, tasks = self.request_json("GET", "/api/tasks?priority=high&q=python")

        self.assertEqual(status, 200)
        self.assertEqual([task["title"] for task in tasks], ["Python 练习"])

    def test_update_task_endpoint(self):
        _, task = self.request_json("POST", "/api/tasks", {"title": "旧标题", "due_date": "2026-06-12"})

        status, updated = self.request_json(
            "PATCH",
            f"/api/tasks/{task['id']}",
            {
                "title": "新标题",
                "course": "软件工程",
                "due_date": "2026-06-20",
                "priority": "high",
                "notes": "补充说明",
                "estimated_hours": 4,
            },
        )

        self.assertEqual(status, 200)
        self.assertEqual(updated["title"], "新标题")
        self.assertEqual(updated["course"], "软件工程")
        self.assertEqual(updated["due_date"], "2026-06-20")
        self.assertEqual(updated["priority"], "high")
        self.assertEqual(updated["notes"], "补充说明")
        self.assertEqual(updated["estimated_hours"], 4)

    def test_course_stats_endpoint(self):
        self.request_json(
            "POST",
            "/api/tasks",
            {"title": "软件任务", "course": "软件工程", "due_date": "2026-06-09", "estimated_hours": 2},
        )
        _, english = self.request_json(
            "POST",
            "/api/tasks",
            {"title": "英语任务", "course": "英语", "due_date": "2026-06-12", "estimated_hours": 3},
        )
        self.request_json("PATCH", f"/api/tasks/{english['id']}/complete")

        status, courses = self.request_json("GET", "/api/courses")

        self.assertEqual(status, 200)
        software = next(item for item in courses if item["course"] == "软件工程")
        self.assertEqual(software["pending"], 1)
        self.assertEqual(software["overdue"], 1)
        self.assertEqual(software["remaining_estimated_hours"], 2)

    def test_bulk_complete_endpoint(self):
        _, first = self.request_json("POST", "/api/tasks", {"title": "任务一", "due_date": "2026-06-12"})
        _, second = self.request_json("POST", "/api/tasks", {"title": "任务二", "due_date": "2026-06-13"})

        status, completed = self.request_json(
            "PATCH",
            "/api/tasks/bulk-complete",
            {"task_ids": [first["id"], second["id"]]},
        )

        self.assertEqual(status, 200)
        self.assertEqual([task["status"] for task in completed], ["done", "done"])

    def test_export_endpoint_returns_tasks_summary_and_courses(self):
        self.request_json("POST", "/api/tasks", {"title": "导出任务", "course": "软件工程", "due_date": "2026-06-12"})

        status, payload = self.request_json("GET", "/api/export")

        self.assertEqual(status, 200)
        self.assertIn("summary", payload)
        self.assertIn("courses", payload)
        self.assertEqual(payload["tasks"][0]["title"], "导出任务")

    def test_invalid_update_returns_bad_request(self):
        _, task = self.request_json("POST", "/api/tasks", {"title": "任务", "due_date": "2026-06-12"})

        with self.assertRaises(HTTPError) as context:
            self.request_json("PATCH", f"/api/tasks/{task['id']}", {"title": "", "due_date": "2026-06-12"})

        self.assertEqual(context.exception.code, 400)

    def test_invalid_payload_returns_bad_request(self):
        with self.assertRaises(HTTPError) as context:
            self.request_json("POST", "/api/tasks", {"title": "", "due_date": "2026-06-12"})

        self.assertEqual(context.exception.code, 400)

    def test_static_frontend_serves_index(self):
        with urlopen(self.base_url + "/", timeout=5) as response:
            html = response.read().decode("utf-8")

        self.assertEqual(response.status, 200)
        self.assertIn("学习任务追踪器", html)


if __name__ == "__main__":
    unittest.main()
