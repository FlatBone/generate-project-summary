from pathlib import Path
from .summarizer import ProjectSummarizer

def main():
    project_directory = input(
        "Enter the project directory path (leave blank for current directory): "
    )
    if not project_directory:
        project_directory = Path.cwd()

    summarizer = ProjectSummarizer(project_directory)
    summarizer.generate_project_summary()

if __name__ == "__main__":
    main()
