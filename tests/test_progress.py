from io import StringIO
from pathlib import Path

from generate_project_summary.progress import StderrProgressReporter


class FakeClock:
    def __init__(self, value=0.0):
        self.value = value

    def __call__(self):
        return self.value


def test_progress_reporter_stays_silent_before_threshold():
    stderr = StringIO()
    clock = FakeClock(0.0)
    reporter = StderrProgressReporter(stderr=stderr, clock=clock, threshold_seconds=2.0)

    reporter({"event": "count_start"})
    clock.value = 1.9
    reporter({"event": "count_progress", "counted_files": 3})
    reporter(
        {
            "event": "done",
            "processed_files": 0,
            "total_files": 0,
            "output_file": "summary.txt",
        }
    )

    assert stderr.getvalue() == ""


def test_progress_reporter_writes_to_stderr_after_threshold():
    stderr = StringIO()
    clock = FakeClock(0.0)
    reporter = StderrProgressReporter(stderr=stderr, clock=clock, threshold_seconds=2.0)

    reporter({"event": "count_start"})
    clock.value = 2.1
    reporter({"event": "count_progress", "counted_files": 4})
    reporter({"event": "process_start", "total_files": 4})
    reporter(
        {
            "event": "file_processed",
            "processed_files": 1,
            "total_files": 4,
            "path": Path("src/main.py"),
        }
    )
    reporter({"event": "write_start", "output_file": "summary.txt"})
    reporter(
        {
            "event": "done",
            "processed_files": 4,
            "total_files": 4,
            "output_file": "summary.txt",
        }
    )

    output = stderr.getvalue()
    assert "Scanning files... 4" in output
    assert "Preparing summary... 1/4 files (src/main.py)" in output
    assert "Writing output... summary.txt" in output
    assert "Done. Processed 4/4 files: summary.txt" in output
