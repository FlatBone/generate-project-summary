# tests/conftest.py
import pytest
from pathlib import Path

@pytest.fixture
def setup_project(tmp_path):
    """
    テスト用のプロジェクトディレクトリとファイルを作成するフィクスチャ
    """
    project_dir = tmp_path / "test_project"
    project_dir.mkdir()

    # テストで必要となるファイルとディレクトリを作成
    (project_dir / "main.py").write_text("def main():\n    pass")
    (project_dir / "README.md").write_text("# Test Project")
    (project_dir / "temp.log").write_text("log entry")

    # .gitignoreで無視されるべきディレクトリとファイル
    venv_dir = project_dir / ".venv"
    venv_dir.mkdir()
    (venv_dir / "lib").touch()

    docs_dir = project_dir / "docs"
    docs_dir.mkdir()
    (docs_dir / "guide.md").write_text("A guide.")

    # .gitignoreファイル自体も作成
    (project_dir / ".gitignore").write_text("*.log\n.venv/\ndocs/guide.md")

    # 作成したプロジェクトディレクトリのパスをテストに渡す
    return project_dir