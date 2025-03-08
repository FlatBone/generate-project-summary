# Generate Project Summary

このPythonスクリプトは、プロジェクトのフォルダ構造を走査し、ファイルとその内容のMarkdownファイルを作成することでプロジェクトのサマリーを生成します。プロジェクトの構造とファイルの内容を1つのMarkdownファイルにまとめて文書化するのに便利な方法を提供します。

## 特徴

- プロジェクトのフォルダ構造のMarkdownサマリーを生成します。
- 各ファイルの内容をサマリーに含めます（バイナリファイルは`(binary file)`と表示されます）。
- `.gitignore`と`.summaryignore`ファイルを使用して、特定のファイルとフォルダを除外できます。
- UTF-8とShift-JISのエンコーディングを試すことで、ファイルのエンコーディング問題を処理します。
- 生成されたサマリーを`<project_name>_project_summary.txt`という名前のファイルに保存します。
- [uithub](https://uithub.com/)では対応していない、Git管理外のプロジェクトや1ステップ必要なプライベートリポジトリに対応しています。

## 使用方法

1. 以下のいずれかの方法でプロジェクトを入手してください：

   - **リポジトリをクローン**:

   ```
   git clone https://github.com/NEXTAltair/generate-project-summary.git
   cd generate-project-summary
   pip install .
   ```

   - **GitHubから直接インストール**:

   ```
   pip install git+https://github.com/NEXTAltair/generate-project-summary.git
   ```
2. ターミナルまたはコマンドプロンプトを開き、スクリプトを実行します：

   ```
   generate-project-summary
   ```

   または

   ```
   gen-pro
   ```
3. プロンプトが表示されたら、プロジェクトディレクトリのパスを入力してください。
   パスが指定されない場合、現在のディレクトリがデフォルトとして使用されます。
   絶対パス、相対パスに対応しています。

   ```
   Enter the project directory path (leave blank for current directory):
   ```
4. プロジェクトのサマリーが`<project_name>_project_summary.txt`という名前で現在のディレクトリに保存されます。

``````
# your_project

## Directory Structure

- your_project/
  - your_project/
    - main.py
    - __init__.py
  - LICENSE
  - pyproject.toml
  - README.md
  - sample.ico

## File Contents


### your_project\main.py

```

def main():
    # main処理

if __name__ == "__main__":
    main()

```


### LICENSE

```
MIT License

```

### pyproject.toml

```
# 依存関係の設定

```

### README.md

```
# your_project


```


``````

## ファイルとフォルダの除外

プロジェクトのルートディレクトリに`.gitignore`と`.summaryignore`ファイルを作成することで、プロジェクトのサマリーから特定のファイルやフォルダを除外できます。これらのファイルには、除外したいパターンやファイル/フォルダ名を1行に1つずつ記述します。

- `.gitignore`: Gitなどのバージョン管理システムで除外するファイルやフォルダを指定します。
- `.summaryignore`: このスクリプト専用のファイルで、サマリーから追加で除外したいファイルやフォルダを指定します。

例えば：

```
# .gitignoreの例:下記を追加することをおすすめします。
*_project_summary.txt

# .summaryignore の例
__pycache__
*.pyc
venv/
```

## オプション一覧

コマンド実行時に以下のオプションを指定できます。
複数のオプションを組み合わせて使用することも可能です。


| オプション | 説明 (日本語) |
| ---------- | ------------- |
| `-d, --directory [PATH]` | `-d` のみ指定するとカレントディレクトリを使用して対話なしで実行できます。<br>対象のプロジェクトディレクトリを指定すると対話なしで実行できます。 |
| `-o, --output FILE`| 出力ファイル名を指定できます。|
| `-i, --ignore PATTERN`| 無視するファイル/フォルダのパターンを追加指定できます。<br>複数回使用可能 (`-i '*.log' -i 'temp/'`)。|
| `-t, --type EXT`| 対象とするファイル拡張子を指定します。<br>デフォルトは全てのファイルが対象です。<br>複数回使用可能 (`-t .py -t .md`)。|

### 使用例 / Examples

#### 1. カレントディレクトリを対象に対話なしで実行する

```sh
gen-pro -d
```

#### 2. 特定のディレクトリを指定して対話なしで実行する

対話なしで特定のディレクトリを指定できます。相対パス、絶対パスに対応しています。


```sh
gen-pro -d src
```

Windows でバックスラッシュ (`\`) を含むパスを指定する場合、シェルの種類に注意してください：
- **CMD (コマンドプロンプト)**: `gen-pro -d D:\project\src` のようにクォートなしで動作します。
- **bash (例: Git Bash)**: `gen-pro -d "D:\project\src"` のようにクォートで囲む必要があります。クォートしないと `\` が正しく解釈されず、エラーが発生する可能性があります。

#### 3. 出力ファイル名を変更する

出力ファイル名を指定できます。

```sh
gen-pro -o summary.txt
```

#### 4. 無視するパターンを追加する

.gitignore、.summaryignoreだけでなく、一時的に対象外にできます。
.log、tempフォルダを無視したい場合

```sh
gen-pro -i '*.log' -i 'temp/'
```

#### 5. 解析対象のファイル拡張子を指定する

.pyと.mdのみ対象にしたい場合

```sh
gen-pro -t .py -t .md
```

#### 6. 複数のオプションを組み合わせる

複数のオプションを自由に組み合わせることで、柔軟な設定が可能です。
対話なしで`src`フォルダを対象に、`.log`を無視して、`.py`と`.md`のみを`summary.txt`というファイル名で作成したい場合

```sh
gen-pro -d src -i '*.log' -t .py -t .md -o summary.txt
```

## 依存関係

このスクリプトは外部の依存関係を必要としません。Pythonの組み込みの`os`と`fnmatch`モジュールを使用します。

## 貢献

貢献は大歓迎です！問題を見つけたり、改善のための提案がある場合は、GitHubリポジトリでissueを開いたり、プルリクエストを送信してください。

## ライセンス

このプロジェクトは[MITライセンス](LICENSE)の下でライセンスされています。

---

# Generate Project Summary

This Python script generates a project summary by traversing the project's folder structure and creating a Markdown file with the files and their contents. It provides a convenient way to document your project's structure and file contents in a single Markdown file.

## Features

- Generates a Markdown summary of the project’s folder structure.
- Includes the contents of each file in the summary (Binary files are displayed as `(binary file)`).
- Allows exclusion of specific files and folders using `.gitignore` and `.summaryignore` files.
- Handles file encoding issues by attempting UTF-8 and Shift-JIS encoding.
- Saves the generated summary to a file named `<project_name>_project_summary.txt`.
- Supports projects not managed by Git or private repositories requiring a single step, which are not supported by [uithub](https://uithub.com/).

## Usage

1. Obtain the project using one of the following methods:

   - **Clone the repository**:

   ```
   git clone https://github.com/NEXTAltair/generate-project-summary.git
   cd generate-project-summary
   pip install .
   ```

   - **Install directly from GitHub**:

   ```
   pip install git+https://github.com/NEXTAltair/generate-project-summary.git
   ```
2. Open a terminal or command prompt and run the script:

   ```
   generate-project-summary
   ```

   or

   ```
   gen-pro
   ```
3. When prompted, enter the project directory path. If no path is specified, the current directory will be used by default. Supports both absolute and relative paths.

   ```
   Enter the project directory path (leave blank for current directory):
   ```
4. The project summary will be saved in the current directory as `<project_name>_project_summary.txt`.

``````
# Example Output
# your_project

## Directory Structure

- your_project/
  - your_project/
    - main.py
    - __init__.py
  - LICENSE
  - pyproject.toml
  - README.md

## File Contents

### your_project\main.py
```
def main():
    # main processing

if __name__ == "__main__":
    main()
```

### LICENSE
```
MIT License
```

### pyproject.toml
```
# Dependency configuration
```

### README.md
```
# your_project
```

### sample.ico (binary file)

``````

## Ignoring Files and Folders

You can exclude specific files and folders from the project summary by creating `.gitignore` and `.summaryignore` files in the project’s root directory. List the patterns or file/folder names to exclude, one per line.

- `.gitignore`: Specifies files and folders to exclude from version control systems like Git.
- `.summaryignore`: A script-specific file for additional exclusions from the summary.

For example:

```
# .gitignore example: We recommend adding the following
*_project_summary.txt

# .summaryignore example
__pycache__
*.pyc
venv/
```

Here’s the English translation of the "オプション一覧" (List of Options) section from your provided text:

---

## List of Options

The following options can be specified when running the command. You can also combine multiple options as needed.

| Options                  | Description (English)                                                                                                                                 |
| ------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| `-d, --directory [PATH]` | If only `-d` is specified, it runs non-interactively using the current directory.<br>Specifying a target project directory runs it non-interactively. |
| `-o, --output FILE`      | Allows you to specify the output file name.                                                                                                           |
| `-i, --ignore PATTERN`   | Adds patterns for files/folders to ignore.<br>Can be used multiple times (e.g., `-i '*.log' -i 'temp/'`).                                             |
| `-t, --type EXT`         | Specifies the file extensions to include.<br>By default, all files are included.<br>Can be used multiple times (e.g., `-t .py -t .md`).               |

### Usage Examples

#### 1. Run non-interactively targeting the current directory
```
gen-pro -d
```

#### 2. Run non-interactively targeting a specific directory
You can specify a particular directory to run the script non-interactively. Both relative and absolute paths are supported.

```sh
gen-pro -d src
```

When specifying a path with backslashes (`\`) on Windows, pay attention to the type of shell you are using:
- **CMD (Command Prompt)**: Works without quotes, e.g., `gen-pro -d D:\project\src`.
- **bash (e.g., Git Bash)**: Requires quotes, e.g., `gen-pro -d "D:\project\src"`. Without quotes, the `\` may not be interpreted correctly, potentially causing errors.


#### 3. Change the output file name
Specify a custom output file name:
```
gen-pro -o summary.txt
```

#### 4. Add patterns to ignore
Temporarily exclude additional patterns beyond `.gitignore` and `.summaryignore`. For example, to ignore `.log` files and the `temp/` folder:
```
gen-pro -i '*.log' -i 'temp/'
```

#### 5. Specify target file extensions
Target only `.py` and `.md` files:
```
gen-pro -t .py -t .md
```

#### 6. Combine multiple options
Flexibly combine options. For example, to target the `src` folder non-interactively, ignore `.log` files, include only `.py` and `.md` files, and save as `summary.txt`:
```
gen-pro -d src -i '*.log' -t .py -t .md -o summary.txt
```

---

Let me know if you need further adjustments!

## Dependencies

This script does not require any external dependencies. It uses Python's built-in `os` and `fnmatch` modules.

## Contributing

Contributions are welcome! If you find any issues or have suggestions for improvements, please open an issue or submit a pull request on the GitHub repository.

## License

This project is licensed under the [MIT License](LICENSE).
