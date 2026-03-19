from pathlib import Path
import stat

from .ignore_patterns import IgnorePatterns


class ProjectSummarizer:
    DEFAULT_MAX_TEXT_FILE_BYTES = 1_000_000
    TEXT_ENCODINGS = ("utf-8", "utf-8-sig", "shift_jis")

    def __init__(
        self,
        project_dir,
        additional_ignore_patterns=None,
        file_types=None,
        name_type_only=False,
        progress_callback=None,
    ):
        """
        Args:
            project_dir (str or Path): プロジェクトのディレクトリパス
            additional_ignore_patterns (list, optional): 追加の無視パターンリスト
            file_types (list, optional): 含めるファイル拡張子（例：['.py', '.md']）
            name_type_only (bool, optional): True の場合、ディレクトリ/ファイル名とテキスト・バイナリ種別のみ出力
        """
        self.project_dir = Path(project_dir).resolve()
        self.project_name = self.project_dir.name
        self.gitignore = IgnorePatterns(self.project_dir / ".gitignore")
        self.summaryignore = IgnorePatterns(self.project_dir / ".summaryignore")

        internal_patterns = [
            ".summaryignore",
            f"{self.project_name}_project_summary.txt",
            ".git/",
        ]
        if additional_ignore_patterns:
            internal_patterns.extend(additional_ignore_patterns)
        self.additional_ignore = IgnorePatterns(patterns=internal_patterns)

        self.file_types = file_types or []
        self.name_type_only = name_type_only
        self.progress_callback = progress_callback
        self.summary_content = ""
        self.file_contents_section = "\n## File Contents\n\n"
        self.skipped_items = []
        self.max_text_file_bytes = self.DEFAULT_MAX_TEXT_FILE_BYTES
        self.total_files = 0
        self.processed_files = 0

    def generate_project_summary(self, output_file=None):
        """
        プロジェクトの要約を生成してファイルに書き出す

        Args:
            output_file (str, optional): 出力ファイル名。デフォルトは <project_name>_project_summary.txt
        """
        self.summary_content = f"# {self.project_name}\n\n## Directory Structure\n\n"
        self.file_contents_section = "\n## File Contents\n\n"
        self.skipped_items = []
        self.total_files = 0
        self.processed_files = 0
        self._notify_progress("count_start")
        self._count_target_files(self.project_dir)
        self._notify_progress("process_start", total_files=self.total_files)
        self._traverse_directory(self.project_dir, 0)
        output_file = output_file or f"{self.project_name}_project_summary.txt"

        skipped_section = ""
        if self.skipped_items:
            skipped_lines = "\n".join(f"- {item}" for item in self.skipped_items)
            skipped_section = f"\n## Skipped Items\n\n{skipped_lines}\n"

        with open(output_file, "w", encoding="utf-8") as f:
            self._notify_progress("write_start", output_file=output_file)
            content_sections = [self.summary_content]
            if not self.name_type_only:
                content_sections.append(self.file_contents_section)
            content_sections.append(skipped_section)
            f.write("".join(content_sections))
        self._notify_progress(
            "done",
            output_file=output_file,
            total_files=self.total_files,
            processed_files=self.processed_files,
        )

    def _count_target_files(self, root: Path):
        relative_path = root.relative_to(self.project_dir)
        if self._is_ignored(relative_path, is_dir=True):
            return

        try:
            items = sorted(root.iterdir(), key=lambda item: item.name.lower())
        except OSError:
            return

        for item_path in items:
            item_relative_path = item_path.relative_to(self.project_dir)

            if self._is_linklike(item_path):
                continue

            try:
                is_dir = item_path.is_dir()
            except OSError:
                continue

            if self._is_ignored(item_relative_path, is_dir=is_dir):
                continue

            if is_dir:
                self._count_target_files(item_path)
                continue

            if self.file_types and item_path.suffix not in self.file_types:
                continue

            self.total_files += 1
            self._notify_progress("count_progress", counted_files=self.total_files)

    def _traverse_directory(self, root: Path, level: int):
        """ディレクトリを再帰的に走査し、構造の要約を作成する。"""
        indent = "  " * level
        relative_path = root.relative_to(self.project_dir)
        if self._is_ignored(relative_path, is_dir=True):
            return

        self.summary_content += f"{indent}- {root.name}/\n"

        try:
            items = sorted(root.iterdir(), key=lambda item: item.name.lower())
        except OSError as exc:
            self._record_skip(relative_path, f"directory could not be read: {exc}")
            return

        for item_path in items:
            item_relative_path = item_path.relative_to(self.project_dir)

            if self._is_linklike(item_path):
                self._record_skip(item_relative_path, "symbolic links and junctions are skipped")
                continue

            try:
                is_dir = item_path.is_dir()
            except OSError as exc:
                self._record_skip(item_relative_path, f"path type could not be determined: {exc}")
                continue

            if self._is_ignored(item_relative_path, is_dir=is_dir):
                continue

            if is_dir:
                self._traverse_directory(item_path, level + 1)
            else:
                self._handle_file(item_path, level + 1)

    def _handle_file(self, file_path: Path, level: int):
        """個々のファイルを処理し、要約に追加する。"""
        if self.file_types and file_path.suffix not in self.file_types:
            return

        indent = "  " * level
        rel_path = file_path.relative_to(self.project_dir)
        self.processed_files += 1
        self._notify_progress(
            "file_processed",
            path=rel_path,
            processed_files=self.processed_files,
            total_files=self.total_files,
        )

        try:
            is_binary = self._is_binary(file_path)
        except OSError as exc:
            self.summary_content += f"{indent}- {file_path.name} (unreadable)\n"
            self._record_skip(rel_path, f"file could not be inspected: {exc}")
            return

        if is_binary:
            self.summary_content += f"{indent}- {file_path.name} (binary file)\n"
            return

        if self.name_type_only:
            self.summary_content += f"{indent}- {file_path.name} (text file)\n"
            return

        try:
            file_size = file_path.stat().st_size
        except OSError as exc:
            self.summary_content += f"{indent}- {file_path.name} (unreadable)\n"
            self._record_skip(rel_path, f"file size could not be read: {exc}")
            return

        if file_size > self.max_text_file_bytes:
            self.summary_content += (
                f"{indent}- {file_path.name} (text file omitted: exceeds {self.max_text_file_bytes} bytes)\n"
            )
            self.file_contents_section += (
                f"### {rel_path}\n\n"
                f"(omitted: file is larger than {self.max_text_file_bytes} bytes)\n\n"
            )
            self._record_skip(rel_path, "file contents omitted because the file is too large")
            return

        content = self._read_file_contents(file_path)
        if content is None:
            self.summary_content += f"{indent}- {file_path.name} (unreadable text file)\n"
            self._record_skip(rel_path, "file could not be decoded with supported encodings")
            return

        self.summary_content += f"{indent}- {file_path.name}\n"
        if content.strip():
            self.file_contents_section += f"### {rel_path}\n\n```\n{content}\n```\n\n"

    def _is_ignored(self, path: Path, is_dir: bool) -> bool:
        """無視パターンに基づいてパスを無視すべきかどうかをチェックする。"""
        try:
            relative_path = path.relative_to(self.project_dir)
        except ValueError:
            relative_path = path

        return any(
            ignore_patterns.matches(relative_path, is_dir=is_dir)
            for ignore_patterns in (
                self.gitignore,
                self.summaryignore,
                self.additional_ignore,
            )
        )

    def _record_skip(self, path: Path, reason: str):
        path_text = Path(path).as_posix() if str(path) else "."
        self.skipped_items.append(f"{path_text}: {reason}")

    def _notify_progress(self, event_name: str, **payload):
        if self.progress_callback is None:
            return

        event = {"event": event_name}
        event.update(payload)
        self.progress_callback(event)

    @staticmethod
    def _is_linklike(path: Path) -> bool:
        try:
            if path.is_symlink():
                return True
            path_stat = path.stat(follow_symlinks=False)
        except OSError:
            return False

        file_attributes = getattr(path_stat, "st_file_attributes", 0)
        reparse_point = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)
        return bool(file_attributes & reparse_point)

    @staticmethod
    def _is_binary(file_path: Path) -> bool:
        """1024バイトで始まるかどうかでバイナリファイルかどうかをチェックする。"""
        with open(file_path, "rb") as f:
            return b"\0" in f.read(1024)

    def _read_file_contents(self, file_path: Path):
        """文字コードに応じてファイルの内容を読み取る。デコードできない場合は None を返す。"""
        for enc in self.TEXT_ENCODINGS:
            try:
                with open(file_path, "r", encoding=enc) as f:
                    return f.read()
            except (OSError, UnicodeDecodeError):
                continue
        return None
