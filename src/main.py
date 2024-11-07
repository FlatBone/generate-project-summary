import generate_project_summary
from pathlib import Path

if __name__ == "__main__":
    project_directory = input(
        "Enter the project directory path (leave blank for current directory): "
    )
    if not project_directory:
        project_directory = Path.cwd()
    generate_project_summary.generate_project_summary(project_directory)
