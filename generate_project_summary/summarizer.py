from pathlib import Path
import fnmatch
from .ignore_patterns import IgnorePatterns

class ProjectSummarizer:
    def __init__(self, project_dir):
        self.project_dir = Path(project_dir).resolve()
        self.project_name = self.project_dir.name
        self.gitignore = IgnorePatterns(self.project_dir / ".gitignore")
        self.summaryignore = IgnorePatterns(self.project_dir / ".summaryignore")
        self.additional_ignore = [
            "generate_project_summary.py",
            ".summaryignore",
            f"{self.project_name}_project_summary.txt",
            ".git",
        ]
        self.summary_content = ""
        self.file_contents_section = "\n## File Contents\n\n"

    def generate_project_summary(self):
        self.summary_content = f"# {self.project_name}\n\n## Directory Structure\n\n"
        self._traverse_directory(self.project_dir, 0)
        with open(f"{self.project_name}_project_summary.txt", "w", encoding="utf-8") as f:
            f.write(self.summary_content + self.file_contents_section)

    def _traverse_directory(self, root: Path, level: int):
        indent = "  " * level
        relative_path = root.relative_to(self.project_dir)
        if not self._is_ignored(relative_path):
            self.summary_content += f"{indent}- {root.name}/\n"
            for item_path in root.iterdir():
                if item_path.is_dir():
                    if not self._is_ignored(item_path):
                        self._traverse_directory(item_path, level + 1)
                else:
                    if not self._is_ignored(item_path):
                        self._handle_file(item_path, level + 1)

    def _handle_file(self, file_path: Path, level: int):
        indent = "  " * level
        if self._is_binary(file_path):
            self.summary_content += f"{indent}- {file_path.name} (binary file)\n"
        else:
            self.summary_content += f"{indent}- {file_path.name}\n"
            content = self._read_file_contents(file_path)
            if content.strip():
                rel_path = file_path.relative_to(self.project_dir)
                self.file_contents_section += (
                    f"### {rel_path}\n\n```\n{content}\n```\n\n"
                )

    def _is_ignored(self, path: Path) -> bool:
        try:
            relative_path = path.relative_to(self.project_dir)
        except ValueError:
            relative_path = Path(".")
        patterns = (
            self.gitignore.patterns
            + self.summaryignore.patterns
            + self.additional_ignore
        )
        for p in patterns:
            p = f"*{p}*"
            if fnmatch.fnmatch(str(relative_path), p) or fnmatch.fnmatch(f"/{relative_path}", p):
                return True
        return False

    @staticmethod
    def _is_binary(file_path: Path) -> bool:
        with open(file_path, "rb") as f:
            return b"\0" in f.read(1024)

    @staticmethod
    def _read_file_contents(file_path: Path) -> str:
        for enc in ["utf-8", "shift_jis"]:
            try:
                with open(file_path, "r", encoding=enc) as f:
                    return f.read()
            except UnicodeDecodeError:
                continue
        return ""
