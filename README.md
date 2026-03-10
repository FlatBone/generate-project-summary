# Generate Project Summary

`generate-project-summary` is a CLI tool that scans a project directory and exports its structure and file contents into a single Markdown-style text file. It is useful when you want to share a codebase with AI tools, review a repository quickly, or keep a lightweight snapshot of a project's contents.

## Features

- Generates a directory tree for the target project.
- Includes file contents in the output.
- Marks binary files as `(binary file)`.
- Respects `.gitignore` and `.summaryignore`.
- Supports additional ignore patterns with CLI options.
- Supports file type filtering such as `.py` and `.md`.
- Attempts `utf-8`, `utf-8-sig`, and `shift_jis` when reading text files.
- Skips symlinks and junctions to avoid traversing outside the project.
- Omits very large text files from the contents section.

## Installation

Install from PyPI:

```bash
pip install generate-project-summary
```

## Quick Start

Run interactively:

```bash
generate-project-summary
```

or:

```bash
gen-pro
```

When prompted, enter the target project directory. Press Enter to use the current directory.

## Output

By default, the tool writes a file named `<project_name>_project_summary.txt` in the current working directory.

Example structure:

````markdown
# your_project

## Directory Structure

- your_project/
  - generate_project_summary/
    - main.py
    - summarizer.py
  - README.md
  - pyproject.toml

## File Contents

### generate_project_summary/main.py

```python
def main():
    ...
```
````

## Command Options

| Option | Description |
| --- | --- |
| `-d`, `--directory [PATH]` | Run non-interactively. `-d` alone uses the current directory. `-d path` uses the specified directory. |
| `-o`, `--output FILE` | Set the output file name. |
| `-i`, `--ignore PATTERN` | Add ignore patterns. Can be used multiple times. |
| `-t`, `--type EXT` | Include only specific file extensions. Can be used multiple times. |
| `-n`, `--name-type-only` | Output only directory/file names and file kind without embedding file contents. |

## Examples

Use the current directory without prompts:

```bash
gen-pro -d
```

Target a specific directory:

```bash
gen-pro -d src
```

Save to a custom file:

```bash
gen-pro -o summary.txt
```

Ignore temporary files:

```bash
gen-pro -i '*.log' -i 'temp/'
```

Include only Python and Markdown files:

```bash
gen-pro -t .py -t .md
```

Combine multiple options:

```bash
gen-pro -d src -i '*.log' -t .py -t .md -o summary.txt
```

Output structure and file kinds only:

```bash
gen-pro -d src -n -o summary.txt
```

## Ignore Files

You can exclude files and folders by creating ignore files in the project root.

- `.gitignore`: patterns already used by Git
- `.summaryignore`: project-summary specific exclusions

Example:

```gitignore
*_project_summary.txt
__pycache__/
*.pyc
.venv/
```

## Notes

- On Windows shells that treat backslashes specially, quote absolute paths when needed.
- Binary files are listed in the tree but their contents are not embedded.
- Large text files are listed and marked as omitted.

## Development

Run tests with your project environment:

```bash
pytest -q
```

## License

MIT
