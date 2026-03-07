from pathlib import PurePosixPath
import fnmatch


class IgnorePatterns:
    """
    .gitignore / .summaryignore 風の簡易パターンを読み込むクラス
    """

    def __init__(self, file_path=None, patterns=None):
        self.patterns = []
        if patterns:
            for pattern in patterns:
                self.add_pattern(pattern)
        if file_path and file_path.exists():
            self._read_ignore_file(file_path)

    def add_pattern(self, pattern):
        normalized = pattern.strip().replace("\\", "/")
        if normalized and normalized not in self.patterns:
            self.patterns.append(normalized)

    def matches(self, relative_path, is_dir=False):
        normalized_path = PurePosixPath(str(relative_path).replace("\\", "/"))
        for pattern in self.patterns:
            if self._matches_pattern(pattern, normalized_path, is_dir):
                return True
        return False

    @staticmethod
    def _matches_pattern(pattern, relative_path, is_dir):
        path_str = relative_path.as_posix()
        if path_str == ".":
            path_str = ""

        anchored = pattern.startswith("/")
        if anchored:
            pattern = pattern.lstrip("/")

        directory_only = pattern.endswith("/")
        if directory_only:
            if not is_dir:
                return False
            pattern = pattern.rstrip("/")

        if not pattern:
            return False

        basename = relative_path.name if path_str else ""

        if "/" not in pattern:
            if basename and fnmatch.fnmatch(basename, pattern):
                return True
            return bool(path_str) and fnmatch.fnmatch(path_str, pattern)

        candidate = path_str
        if directory_only:
            candidate = f"{path_str}/" if path_str else ""
            pattern = f"{pattern}/"

        if anchored:
            return fnmatch.fnmatch(candidate, pattern)

        return fnmatch.fnmatch(candidate, pattern) or fnmatch.fnmatch(
            candidate, f"*/{pattern}"
        )

    def _read_ignore_file(self, file_path):
        """
        .gitignoreや.summaryignoreのパターンを読み込む
        Args:
            file_path (path): .gitignoreや.summaryignoreのパス
        """
        lines = []
        for encoding in ("utf-8", "utf-8-sig", "shift_jis"):
            try:
                with open(file_path, "r", encoding=encoding) as f:
                    lines = [
                        line.strip()
                        for line in f
                        if line.strip() and not line.lstrip().startswith("#")
                    ]
                break
            except UnicodeDecodeError:
                continue

        for pattern in lines:
            self.add_pattern(pattern)
