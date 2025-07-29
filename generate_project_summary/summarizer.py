from pathlib import Path
import fnmatch
from .ignore_patterns import IgnorePatterns

class ProjectSummarizer:
    def __init__(self, project_dir, additional_ignore_patterns=None, file_types=None):
        """
        Args:
            project_dir (str or Path): プロジェクトのディレクトリパス
            additional_ignore_patterns (list, optional): 追加の無視パターンリスト
            file_types (list, optional): 含めるファイル拡張子（例：['.py', '.md']）
        """
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
        if additional_ignore_patterns:
            self.additional_ignore.extend(additional_ignore_patterns)
        self.file_types = file_types or []  # Empty list means all files are included
        self.summary_content = ""
        self.file_contents_section = "\n## File Contents\n\n"

    def generate_project_summary(self, output_file=None):
        """
        プロジェクトの要約を生成してファイルに書き出す

        Args:
            output_file (str, optional): 出力ファイル名。デフォルトは <project_name>_project_summary.txt
        """
        self.summary_content = f"# {self.project_name}\n\n## Directory Structure\n\n"
        self._traverse_directory(self.project_dir, 0)
        output_file = output_file or f"{self.project_name}_project_summary.txt"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(self.summary_content + self.file_contents_section)

    def _traverse_directory(self, root: Path, level: int):
        """ディレクトリを再帰的に走査し、構造の要約を作成する。"""
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
        """個々のファイルを処理し、要約に追加する。"""
        if self.file_types and file_path.suffix not in self.file_types:
            return  # Skip files not matching specified types
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
        """
        無視パターンに基づいてパスを無視すべきかどうかをチェックする。
        .gitignoreの挙動を模倣し、クロスプラットフォームで動作するように修正。
        """
        try:
            # WindowsでもLinuxでも比較できるように、パス区切り文字を'/'に正規化する
            relative_path_str = str(path.relative_to(self.project_dir)).replace('\\', '/')
        except ValueError:
            # プロジェクトディレクトリ外など、通常は発生しないケース
            return False

        patterns = (
            self.gitignore.patterns
            + self.summaryignore.patterns
            + self.additional_ignore
        )

        for p in patterns:
            # パターンも正規化
            p_norm = p.replace('\\', '/').strip()
            if not p_norm:
                continue

            # ケース1: パターンが'/'で終わる場合 (例: 'venv/', 'docs/')
            # これはディレクトリとその中身全てを無視するパターン
            if p_norm.endswith('/'):
                dir_pattern = p_norm.rstrip('/')
                # パスがそのディレクトリ自身か、そのディレクトリから始まるかをチェック
                if relative_path_str == dir_pattern or relative_path_str.startswith(dir_pattern + '/'):
                    return True
                continue

            # ケース2: パターンに'/'が含まれない場合 (例: '*.log', '__pycache__')
            # これはパスのどの部分（ファイル名やディレクトリ名）にでもマッチする
            if '/' not in p_norm:
                if fnmatch.fnmatch(path.name, p_norm):
                    return True
                continue

            # ケース3: パターンに'/'が含まれる場合 (例: 'src/main.py')
            # これはプロジェクトルートからの相対パスとしてマッチするかをチェック
            if fnmatch.fnmatch(relative_path_str, p_norm):
                return True

        return False

    @staticmethod
    def _is_binary(file_path: Path) -> bool:
        """1024バイトで始まるかどうかでバイナリファイルかどうかをチェックする。"""
        with open(file_path, "rb") as f:
            return b"\0" in f.read(1024)

    @staticmethod
    def _read_file_contents(file_path: Path) -> str:
        """文字コードに応じてファイルの内容を読み取る。デコードできない場合は空の文字列を返す。"""
        for enc in ["utf-8", "shift_jis"]:
            try:
                with open(file_path, "r", encoding=enc) as f:
                    return f.read()
            except UnicodeDecodeError:
                continue
        return ""  # Return empty string if decoding fails
