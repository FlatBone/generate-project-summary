import argparse
from pathlib import Path
from .summarizer import ProjectSummarizer

def main():
    parser = argparse.ArgumentParser(
        description="Generate a project summary."
    )
    parser.add_argument(
        "-d", "--directory",
        type=str,
        nargs="?",
        const="",
        default=None,
        help=(
            "Specify the project directory path.\n"
            "-d alone: Targets the current directory without interaction.\n"
            "-d with path: Targets the specified path without interaction."
        )
    )
    parser.add_argument(
        "-o", "--output",
        type=str,
        default=None,
        help="Specify the output file name (default: <project_name>_project_summary.txt)."
    )
    parser.add_argument(
        "-i", "--ignore",
        action="append",
        default=[],
        help="Specify additional patterns to ignore (can be used multiple times). E.g., -i '*.log' -i 'temp/'"
    )
    parser.add_argument(
        "-t", "--type",
        action="append",
        default=[],
        help="Specify file types to include (e.g., .py, .md). Default: all files."
    )
    args = parser.parse_args()

    # プロジェクトディレクトリを決定するロジック
    if args.directory is None:
        # 引数が全く指定されなかった場合、対話的に入力を求める
        project_directory = input(
            "Enter the project directory path (leave blank for current directory): "
        )
        project_directory = Path(project_directory) if project_directory.strip() else Path.cwd()
    else:
        # -d が指定された場合
        project_directory = Path(args.directory)

    summarizer = ProjectSummarizer(
        project_directory,
        additional_ignore_patterns=args.ignore,
        file_types=args.type
    )
    summarizer.generate_project_summary(output_file=args.output)

if __name__ == "__main__":
    main()
