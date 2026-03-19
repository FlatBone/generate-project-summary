import pytest

from generate_project_summary.summarizer import ProjectSummarizer


def test_gitignore_handling(setup_project):
    summarizer = ProjectSummarizer(setup_project)
    output_file = setup_project / "summary.txt"
    summarizer.generate_project_summary(output_file=output_file)

    content = output_file.read_text(encoding="utf-8")

    assert "temp.log" not in content
    assert "main.py" in content

    structure_part, contents_part = content.split("\n## File Contents\n\n", 1)
    assert ".gitignore" in structure_part
    assert ".venv" not in structure_part
    assert "guide.md" not in structure_part
    assert "### .gitignore" in contents_part.replace("\\", "/")
    assert ".venv/" in contents_part


def test_binary_file_handling(setup_project):
    (setup_project / "app.ico").write_bytes(b"\x00\x01\x02\x00\x03")

    summarizer = ProjectSummarizer(setup_project)
    output_file = setup_project / "summary.txt"
    summarizer.generate_project_summary(output_file=output_file)

    content = output_file.read_text(encoding="utf-8")
    assert "- app.ico (binary file)" in content
    assert "### app.ico" not in content.replace("\\", "/")


def test_shift_jis_encoding_handling(setup_project):
    japanese_text = "これはShift-JISのテストです。"
    (setup_project / "sjis_document.txt").write_text(japanese_text, encoding="shift_jis")

    summarizer = ProjectSummarizer(setup_project)
    output_file = setup_project / "summary.txt"
    summarizer.generate_project_summary(output_file=output_file)

    content = output_file.read_text(encoding="utf-8")
    assert japanese_text in content


def test_additional_ignore_patterns_option(setup_project):
    (setup_project / "temp.tmp").touch()
    (setup_project / "main.py").touch()

    summarizer = ProjectSummarizer(setup_project, additional_ignore_patterns=["*.tmp"])
    output_file = setup_project / "summary.txt"
    summarizer.generate_project_summary(output_file=output_file)

    content = output_file.read_text(encoding="utf-8")
    assert "temp.tmp" not in content
    assert "main.py" in content


def test_file_types_option(setup_project):
    (setup_project / "script.py").touch()
    (setup_project / "document.md").touch()

    summarizer = ProjectSummarizer(setup_project, file_types=[".py"])
    output_file = setup_project / "summary.txt"
    summarizer.generate_project_summary(output_file=output_file)

    content = output_file.read_text(encoding="utf-8")
    assert "script.py" in content
    assert "document.md" not in content


def test_git_directory_ignore_does_not_hide_dot_github(tmp_path):
    (tmp_path / ".git").mkdir()
    (tmp_path / ".git" / "config").write_text("secret", encoding="utf-8")
    (tmp_path / ".github").mkdir()
    (tmp_path / ".github" / "workflow.yml").write_text("name: ci", encoding="utf-8")

    output_file = tmp_path / "summary.txt"
    summarizer = ProjectSummarizer(tmp_path)
    summarizer.generate_project_summary(output_file=output_file)

    summary = output_file.read_text(encoding="utf-8")
    assert ".git/" not in summary
    assert ".github/" in summary
    assert "workflow.yml" in summary


def test_large_text_file_is_omitted_from_contents(tmp_path):
    (tmp_path / "large.txt").write_text(
        "a" * (ProjectSummarizer.DEFAULT_MAX_TEXT_FILE_BYTES + 1),
        encoding="utf-8",
    )

    output_file = tmp_path / "summary.txt"
    summarizer = ProjectSummarizer(tmp_path)
    summarizer.generate_project_summary(output_file=output_file)

    summary = output_file.read_text(encoding="utf-8")
    assert "large.txt (text file omitted:" in summary
    assert "(omitted: file is larger than" in summary


def test_symlinked_directory_is_skipped(tmp_path):
    external_dir = tmp_path.parent / "external"
    external_dir.mkdir(exist_ok=True)
    (external_dir / "secret.txt").write_text("outside", encoding="utf-8")
    link_path = tmp_path / "linked"

    try:
        link_path.symlink_to(external_dir, target_is_directory=True)
    except (OSError, NotImplementedError):
        pytest.skip("symlink creation is not available in this environment")

    output_file = tmp_path / "summary.txt"
    summarizer = ProjectSummarizer(tmp_path)
    summarizer.generate_project_summary(output_file=output_file)

    summary = output_file.read_text(encoding="utf-8")
    assert "secret.txt" not in summary
    assert "linked: symbolic links and junctions are skipped" in summary


def test_name_type_only_mode_outputs_only_names_and_file_kind(tmp_path):
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "main.py").write_text("print('hi')", encoding="utf-8")
    (tmp_path / "data.bin").write_bytes(b"\x00\x01\x02")

    output_file = tmp_path / "summary.txt"
    summarizer = ProjectSummarizer(tmp_path, name_type_only=True)
    summarizer.generate_project_summary(output_file=output_file)

    summary = output_file.read_text(encoding="utf-8")
    assert "- src/" in summary
    assert "- main.py (text file)" in summary
    assert "- data.bin (binary file)" in summary
    assert "## File Contents" not in summary
    assert "### src/main.py" not in summary


def test_summarizer_reports_progress_events(tmp_path):
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "main.py").write_text("print('hi')", encoding="utf-8")
    (tmp_path / "README.md").write_text("# demo", encoding="utf-8")

    events = []
    summarizer = ProjectSummarizer(tmp_path, progress_callback=events.append)
    summarizer.generate_project_summary(output_file=tmp_path / "summary.txt")

    assert events[0]["event"] == "count_start"
    assert any(event["event"] == "count_progress" for event in events)
    assert any(
        event["event"] == "process_start" and event["total_files"] == 2
        for event in events
    )
    file_events = [event for event in events if event["event"] == "file_processed"]
    assert len(file_events) == 2
    assert file_events[-1]["processed_files"] == 2
    assert events[-1]["event"] == "done"
