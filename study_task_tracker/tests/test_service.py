import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from study_tracker.models import TaskNotFoundError, ValidationError
from study_tracker.service import StudyTaskService
from study_tracker.store import JsonTaskRepository


class StudyTaskServiceTest(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.data_file = Path(self.temp_dir.name) / "tasks.json"
        self.service = StudyTaskService(
            JsonTaskRepository(self.data_file),
            today_provider=lambda: date(2026, 6, 10),
        )

    def test_add_task_persists_normalized_task(self):
        task = self.service.add_task(
            "  完成单元测试  ",
            due_date="2026-06-12",
            course=" 软件工程 ",
            priority="HIGH",
            notes="  覆盖核心逻辑  ",
            estimated_hours="2.5",
        )

        self.assertEqual(task.id, "T0001")
        self.assertEqual(task.title, "完成单元测试")
        self.assertEqual(task.course, "软件工程")
        self.assertEqual(task.priority, "high")
        self.assertEqual(task.status, "pending")
        self.assertEqual(task.notes, "覆盖核心逻辑")
        self.assertEqual(task.estimated_hours, 2.5)

        loaded = self.service.list_tasks()
        self.assertEqual([item.id for item in loaded], ["T0001"])

    def test_add_task_generates_next_id_from_existing_tasks(self):
        self.service.add_task("任务一", due_date="2026-06-12")
        second = self.service.add_task("任务二", due_date="2026-06-13")

        self.assertEqual(second.id, "T0002")

    def test_add_task_rejects_blank_title(self):
        with self.assertRaises(ValidationError):
            self.service.add_task("  ", due_date="2026-06-12")

    def test_add_task_rejects_long_course(self):
        with self.assertRaises(ValidationError):
            self.service.add_task("任务", due_date="2026-06-12", course="课" * 41)

    def test_add_task_rejects_invalid_due_date(self):
        with self.assertRaises(ValidationError):
            self.service.add_task("任务", due_date="2026/06/12")

    def test_add_task_rejects_invalid_priority(self):
        with self.assertRaises(ValidationError):
            self.service.add_task("任务", due_date="2026-06-12", priority="urgent")

    def test_add_task_rejects_invalid_estimated_hours(self):
        with self.assertRaises(ValidationError):
            self.service.add_task("任务", due_date="2026-06-12", estimated_hours=80)

    def test_list_tasks_filters_by_status_and_sorts_by_due_date(self):
        later = self.service.add_task("后交", due_date="2026-06-14", priority="low")
        earlier = self.service.add_task("先交", due_date="2026-06-11", priority="medium")
        self.service.complete_task(later.id)

        pending = self.service.list_tasks(status="pending")

        self.assertEqual([task.id for task in pending], [earlier.id])

    def test_list_tasks_filters_by_priority_and_query(self):
        self.service.add_task("Python 练习", due_date="2026-06-12", course="编程", priority="high")
        self.service.add_task("英语阅读", due_date="2026-06-13", course="英语", priority="low")
        self.service.add_task("软件工程计划", due_date="2026-06-14", course="软件工程", priority="high")

        filtered = self.service.list_tasks(priority="high", query="软件")

        self.assertEqual([task.title for task in filtered], ["软件工程计划"])

    def test_update_task_changes_details_and_keeps_status(self):
        task = self.service.add_task("旧标题", due_date="2026-06-12", course="旧课程", priority="low")
        completed = self.service.complete_task(task.id)

        updated = self.service.update_task(
            completed.id,
            title="新标题",
            due_date="2026-06-20",
            course="新课程",
            priority="high",
            notes="新备注",
            estimated_hours=3,
        )

        self.assertEqual(updated.title, "新标题")
        self.assertEqual(updated.course, "新课程")
        self.assertEqual(updated.due_date, "2026-06-20")
        self.assertEqual(updated.priority, "high")
        self.assertEqual(updated.status, "done")
        self.assertEqual(updated.completed_at, "2026-06-10")
        self.assertEqual(updated.notes, "新备注")
        self.assertEqual(updated.estimated_hours, 3)

    def test_update_missing_task_raises(self):
        with self.assertRaises(TaskNotFoundError):
            self.service.update_task("T9999", title="任务", due_date="2026-06-12")

    def test_complete_task_marks_done_and_records_date(self):
        task = self.service.add_task("完成报告", due_date="2026-06-12")

        completed = self.service.complete_task(task.id)

        self.assertEqual(completed.status, "done")
        self.assertEqual(completed.completed_at, "2026-06-10")
        self.assertEqual(self.service.summary().done, 1)

    def test_complete_tasks_marks_multiple_tasks_done(self):
        first = self.service.add_task("任务一", due_date="2026-06-12")
        second = self.service.add_task("任务二", due_date="2026-06-13")

        completed = self.service.complete_tasks([first.id, second.id])

        self.assertEqual([task.status for task in completed], ["done", "done"])
        self.assertEqual(self.service.summary().done, 2)

    def test_complete_missing_task_raises(self):
        with self.assertRaises(TaskNotFoundError):
            self.service.complete_task("T9999")

    def test_delete_task_removes_existing_task(self):
        task = self.service.add_task("误建任务", due_date="2026-06-12")

        deleted = self.service.delete_task(task.id)

        self.assertEqual(deleted.id, task.id)
        self.assertEqual(self.service.list_tasks(), [])

    def test_delete_missing_task_raises(self):
        with self.assertRaises(TaskNotFoundError):
            self.service.delete_task("T9999")

    def test_summary_counts_pending_done_and_overdue(self):
        overdue = self.service.add_task("逾期任务", due_date="2026-06-09", estimated_hours=2)
        self.service.add_task("未完成任务", due_date="2026-06-11", estimated_hours=3)
        done = self.service.add_task("已完成任务", due_date="2026-06-09", estimated_hours=5)
        self.service.complete_task(done.id)

        summary = self.service.summary()

        self.assertEqual(summary.total, 3)
        self.assertEqual(summary.pending, 2)
        self.assertEqual(summary.done, 1)
        self.assertEqual(summary.overdue, 1)
        self.assertEqual(summary.completion_rate, 33)
        self.assertEqual(summary.total_estimated_hours, 10)
        self.assertEqual(summary.remaining_estimated_hours, 5)
        self.assertEqual(overdue.status, "pending")

    def test_course_summaries_group_tasks_by_course(self):
        self.service.add_task("软件任务一", due_date="2026-06-09", course="软件工程", estimated_hours=2)
        done = self.service.add_task("软件任务二", due_date="2026-06-12", course="软件工程", estimated_hours=4)
        self.service.add_task("英语任务", due_date="2026-06-12", course="英语", estimated_hours=3)
        self.service.complete_task(done.id)

        summaries = self.service.course_summaries()

        software = next(item for item in summaries if item.course == "软件工程")
        self.assertEqual(software.total, 2)
        self.assertEqual(software.pending, 1)
        self.assertEqual(software.done, 1)
        self.assertEqual(software.overdue, 1)
        self.assertEqual(software.remaining_estimated_hours, 2)


if __name__ == "__main__":
    unittest.main()
