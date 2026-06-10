import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from study_tracker.models import StorageError, StudyTask
from study_tracker.store import JsonTaskRepository


class JsonTaskRepositoryTest(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.data_file = Path(self.temp_dir.name) / "tasks.json"
        self.repository = JsonTaskRepository(self.data_file)

    def test_repository_returns_empty_when_file_missing(self):
        self.assertEqual(self.repository.load_all(), [])

    def test_repository_saves_and_loads_tasks(self):
        task = StudyTask.new(
            task_id="T0001",
            title="完成计划",
            due_date="2026-06-10",
            created_at="2026-06-10",
            course="软件工程",
            priority="medium",
        )

        self.repository.save_all([task])
        loaded = self.repository.load_all()

        self.assertEqual(len(loaded), 1)
        self.assertEqual(loaded[0].to_dict(), task.to_dict())

    def test_repository_treats_empty_file_as_empty_list(self):
        self.data_file.write_text("   ", encoding="utf-8")

        self.assertEqual(self.repository.load_all(), [])

    def test_repository_rejects_invalid_json(self):
        self.data_file.write_text("{not-json", encoding="utf-8")

        with self.assertRaises(StorageError):
            self.repository.load_all()

    def test_repository_rejects_non_array_json(self):
        self.data_file.write_text('{"id": "T0001"}', encoding="utf-8")

        with self.assertRaises(StorageError):
            self.repository.load_all()

    def test_repository_rejects_invalid_task_shape(self):
        self.data_file.write_text('[{"id": "T0001"}]', encoding="utf-8")

        with self.assertRaises(StorageError):
            self.repository.load_all()


if __name__ == "__main__":
    unittest.main()
