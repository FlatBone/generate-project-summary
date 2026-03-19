import sys
import time
from pathlib import Path


class StderrProgressReporter:
    SPINNER_FRAMES = ("|", "/", "-", "\\")

    def __init__(self, stderr=None, clock=None, threshold_seconds=2.0):
        self.stderr = stderr if stderr is not None else sys.stderr
        self.clock = clock if clock is not None else time.monotonic
        self.threshold_seconds = threshold_seconds
        self.start_time = None
        self.spinner_index = 0
        self.last_rendered_width = 0
        self.has_rendered = False

    def __call__(self, event):
        event_name = event["event"]
        if event_name == "count_start":
            self.start_time = self.clock()
        if event_name == "done":
            self._finish(event)
            return

        message = self._build_message(event)
        if message is None:
            return
        self._render(message)

    def _build_message(self, event):
        event_name = event["event"]
        frame = self._next_spinner_frame()

        if event_name == "count_start":
            return f"{frame} Scanning files..."
        if event_name == "count_progress":
            return f"{frame} Scanning files... {event['counted_files']}"
        if event_name == "process_start":
            return f"{frame} Preparing summary... 0/{event['total_files']} files"
        if event_name == "file_processed":
            path_text = Path(event["path"]).as_posix()
            return (
                f"{frame} Preparing summary... "
                f"{event['processed_files']}/{event['total_files']} files "
                f"({path_text})"
            )
        if event_name == "write_start":
            return f"{frame} Writing output... {event['output_file']}"
        return None

    def _render(self, message):
        if self.start_time is None:
            return
        if (self.clock() - self.start_time) < self.threshold_seconds:
            return

        padded_message = message.ljust(self.last_rendered_width)
        self.stderr.write(f"\r{padded_message}")
        self.stderr.flush()
        self.last_rendered_width = len(message)
        self.has_rendered = True

    def _finish(self, event):
        if not self.has_rendered:
            return

        message = (
            f"Done. Processed {event['processed_files']}/{event['total_files']} files: "
            f"{event['output_file']}"
        )
        padded_message = message.ljust(self.last_rendered_width)
        self.stderr.write(f"\r{padded_message}\n")
        self.stderr.flush()
        self.last_rendered_width = len(message)

    def _next_spinner_frame(self):
        frame = self.SPINNER_FRAMES[self.spinner_index]
        self.spinner_index = (self.spinner_index + 1) % len(self.SPINNER_FRAMES)
        return frame
