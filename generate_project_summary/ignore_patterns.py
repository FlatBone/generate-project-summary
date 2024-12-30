class IgnorePatterns:
    """
    .gitignoreや.summaryignoreのパターンを読み込むクラス
    """
    def __init__(self, file_path):
        self.patterns = []
        if file_path.exists():
            self._read_ignore_file(file_path)

    def _read_ignore_file(self, file_path):
        """
        .gitignoreや.summaryignoreのパターンを読み込む
        Args:
            file_path (path): .gitignoreや.summaryignoreのパス
        """
        with open(file_path, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip() and not line.startswith("#")]
        for pattern in lines:
            self.patterns.append(pattern)
            # OSごとの区切り差分対策としてパターン置換も加える
            # Note: Win以外では未テスト
            if "/" in pattern:
                self.patterns.append(pattern.replace("/", "\\"))
            if "\\" in pattern:
                self.patterns.append(pattern.replace("\\", "/"))
