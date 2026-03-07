import sys
from pathlib import Path

import pytest

from generate_project_summary.main import main


def test_main_rejects_file_path(monkeypatch, tmp_path):
    target_file = Path(tmp_path) / "target.txt"
    target_file.write_text("data", encoding="utf-8")

    monkeypatch.setattr(sys, "argv", ["generate-project-summary", "-d", str(target_file)])

    with pytest.raises(NotADirectoryError):
        main()
