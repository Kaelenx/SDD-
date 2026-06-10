"""Run unit tests and print a simple line coverage report using only stdlib."""

from __future__ import annotations

import ast
import os
from pathlib import Path
import sys
import threading
import unittest


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
TESTS = ROOT / "tests"
SRC_RESOLVED = os.path.normcase(os.path.abspath(SRC))
SRC_PREFIX = SRC_RESOLVED + os.sep


def executable_lines(path: Path) -> set[int]:
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(path))
    lines: set[int] = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.stmt, ast.ExceptHandler)) and hasattr(node, "lineno"):
            lines.add(node.lineno)
    return lines


def run_tests() -> unittest.result.TestResult:
    sys.path.insert(0, str(SRC))
    suite = unittest.defaultTestLoader.discover(str(TESTS))
    runner = unittest.TextTestRunner(verbosity=2)
    return runner.run(suite)


def run_tests_with_source_tracing() -> tuple[unittest.result.TestResult, dict[tuple[str, int], int]]:
    counts: dict[tuple[str, int], int] = {}
    filename_cache: dict[str, str] = {}

    def normalized_filename(filename: str) -> str:
        cached = filename_cache.get(filename)
        if cached is None:
            cached = os.path.normcase(os.path.abspath(filename))
            filename_cache[filename] = cached
        return cached

    def source_trace(frame, event, arg):
        if event == "line":
            filename = normalized_filename(frame.f_code.co_filename)
            counts[(filename, frame.f_lineno)] = counts.get((filename, frame.f_lineno), 0) + 1
        return source_trace

    def global_trace(frame, event, arg):
        if event != "call":
            return None
        filename_text = normalized_filename(frame.f_code.co_filename)
        if filename_text == SRC_RESOLVED or filename_text.startswith(SRC_PREFIX):
            return source_trace
        return None

    sys.settrace(global_trace)
    threading.settrace(global_trace)
    try:
        result = run_tests()
    finally:
        sys.settrace(None)
        threading.settrace(None)
    return result, counts


def main() -> int:
    result, counts = run_tests_with_source_tracing()

    source_files = sorted(SRC.rglob("*.py"))
    total_executable = 0
    total_executed = 0

    print("\nCoverage report")
    print("File                                      Lines    Hit   Cover")
    print("--------------------------------------------------------------")

    for path in source_files:
        path_key = os.path.normcase(os.path.abspath(path))
        executable = executable_lines(path)
        executed = {
            lineno
            for (filename, lineno), count in counts.items()
            if count > 0 and filename == path_key and lineno in executable
        }
        total = len(executable)
        hit = len(executed)
        total_executable += total
        total_executed += hit
        percent = 100.0 if total == 0 else hit / total * 100
        display = path.relative_to(ROOT).as_posix()
        print(f"{display:<40} {total:>5} {hit:>6} {percent:>6.1f}%")

    print("--------------------------------------------------------------")
    total_percent = 100.0 if total_executable == 0 else total_executed / total_executable * 100
    print(f"{'TOTAL':<40} {total_executable:>5} {total_executed:>6} {total_percent:>6.1f}%")

    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
