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
            # パターンをそのままリストに追加するだけにする
            self.patterns = [line.strip() for line in f if line.strip() and not line.startswith("#")]
