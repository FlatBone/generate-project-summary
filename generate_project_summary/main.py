from pathlib import Path
import fnmatch


def is_binary(file_path):
    with open(file_path, "rb") as file:
        return b"\0" in file.read(1024)


def read_file_contents(file_path):
    encodings = ["utf-8", "shift_jis"]
    for encoding in encodings:
        try:
            with open(file_path, "r", encoding=encoding) as file:
                print(f"Reading file: {file_path}")
                return file.read()
        except UnicodeDecodeError:
            pass
    return ""


def is_ignored(
    path,
    project_dir,
    gitignore_patterns,
    summaryignore_patterns,
    additional_ignore_patterns,
):
    try:
        relative_path = path.relative_to(project_dir)
    except ValueError:
        # path が project_dir のサブパスでない場合、相対パスを '.' とする
        relative_path = Path(".")
    for pattern in (
        gitignore_patterns + summaryignore_patterns + additional_ignore_patterns
    ):
        pattern = f"*{pattern}*"
        if fnmatch.fnmatch(str(relative_path), pattern) or fnmatch.fnmatch(
            f"/{relative_path}", pattern
        ):
            return True
    return False


def generate_project_summary(project_dir):
    project_dir = Path(project_dir).resolve()
    project_name = project_dir.name
    summary = f"# {project_name}\n\n## Directory Structure\n\n"

    gitignore_patterns = read_gitignore(project_dir)
    print(f"gitignore_patterns: {gitignore_patterns}")
    summaryignore_patterns = read_summaryignore(project_dir)
    print(f"summaryignore_patterns: {summaryignore_patterns}")
    additional_ignore_patterns = [
        "generate_project_summary.py",
        ".summaryignore",
        f"{project_name}_project_summary.txt",
        ".git",
    ]

    file_contents_section = "\n## File Contents\n\n"

    def traverse_directory(root: Path, level: int):
        nonlocal summary, file_contents_section
        indent = "  " * level
        relative_path = root.relative_to(project_dir)
        if not is_ignored(
            relative_path,
            project_dir,
            gitignore_patterns,
            summaryignore_patterns,
            additional_ignore_patterns,
        ):
            summary += f"{indent}- {root.name}/\n"

            subindent = "  " * (level + 1)
            for item_path in root.iterdir():
                if item_path.is_dir():
                    if not is_ignored(
                        item_path,
                        project_dir,
                        gitignore_patterns,
                        summaryignore_patterns,
                        additional_ignore_patterns,
                    ):
                        traverse_directory(item_path, level + 1)
                else:
                    if not is_ignored(
                        item_path,
                        project_dir,
                        gitignore_patterns,
                        summaryignore_patterns,
                        additional_ignore_patterns,
                    ):
                        if not is_binary(item_path):
                            summary += f"{subindent}- {item_path.name}\n"
                            content = read_file_contents(item_path)
                            if content.strip():
                                # ファイル名をプロジェクト名からの相対パスで表示
                                relative_file_path = item_path.relative_to(project_dir)
                                file_contents_section += f"### {relative_file_path}\n\n```\n{content}\n```\n\n"
                        else:
                            summary += f"{subindent}- {item_path} (binary file)\n"

    traverse_directory(project_dir, 0)

    with open(f"{project_name}_project_summary.txt", "w", encoding="utf-8") as file:
        file.write(summary + file_contents_section)


def read_gitignore(project_dir: Path) -> list:
    gitignore_path = project_dir / ".gitignore"
    if gitignore_path.exists():
        with open(gitignore_path, "r", encoding="utf-8") as file:
            patterns = [
                line.strip()
                for line in file
                if line.strip() and not line.startswith("#")
            ]
            expanded_patterns = []
            for pattern in patterns:
                expanded_patterns.append(pattern)
                if "/" in pattern:
                    expanded_patterns.append(pattern.replace("/", "\\"))
                if "\\" in pattern:
                    expanded_patterns.append(pattern.replace("\\", "/"))
            return expanded_patterns
    return []


def read_summaryignore(project_dir: Path) -> list:
    summaryignore_path = project_dir / ".summaryignore"
    if summaryignore_path.exists():
        with open(summaryignore_path, "r", encoding="utf-8") as file:
            patterns = [
                line.strip()
                for line in file
                if line.strip() and not line.startswith("#")
            ]
            expanded_patterns = []
            for pattern in patterns:
                expanded_patterns.append(pattern)
                if "/" in pattern:
                    expanded_patterns.append(pattern.replace("/", "\\"))
                if "\\" in pattern:
                    expanded_patterns.append(pattern.replace("\\", "/"))
            return expanded_patterns
    return []


def main():
    project_directory = input(
        "Enter the project directory path (leave blank for current directory): "
    )
    if not project_directory:
        project_directory = Path.cwd()
    generate_project_summary(project_directory)


if __name__ == "__main__":
    main()
