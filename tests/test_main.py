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



def test_main_name_type_only_mode(monkeypatch, tmp_path):
    (tmp_path / "main.py").write_text("print('hello')", encoding="utf-8")
    output_file = tmp_path / "summary.txt"

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "generate-project-summary",
            "-d",
            str(tmp_path),
            "--name-type-only",
            "-o",
            str(output_file),
        ],
    )

    main()

    summary = output_file.read_text(encoding="utf-8")
    assert "main.py (text file)" in summary
    assert "## File Contents" not in summary



def test_main_name_type_only_short_option(monkeypatch, tmp_path):
    (tmp_path / "main.py").write_text("print('hello')", encoding="utf-8")
    output_file = tmp_path / "summary_short.txt"

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "generate-project-summary",
            "-d",
            str(tmp_path),
            "-n",
            "-o",
            str(output_file),
        ],
    )

    main()

    summary = output_file.read_text(encoding="utf-8")
    assert "main.py (text file)" in summary
    assert "## File Contents" not in summary
