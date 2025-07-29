# tests/test_summarizer.py

import pytest
from generate_project_summary.summarizer import ProjectSummarizer

# 元からあったテスト：.gitignoreの基本的な動作を検証
def test_gitignore_handling(setup_project):
    """
    .gitignoreのルールに従ってファイルやディレクトリが無視されることを確認する。
    """
    # .gitignoreのルールを定義
    (setup_project / ".gitignore").write_text("*.log\n.venv/\ndocs/guide.md")
    

    summarizer = ProjectSummarizer(setup_project)
    output_file = setup_project / "summary.txt"
    summarizer.generate_project_summary(output_file=output_file)
    
    content = output_file.read_text(encoding="utf-8")
    
    # 無視された項目がディレクトリ構造に含まれていないことを確認
    assert "temp.log" not in content
    assert ".venv" not in content
    assert "guide.md" not in content
    # 無視されていない項目が含まれていることを確認
    assert "main.py" in content



def test_gitignore_handling(setup_project):
    """
    .gitignoreのルールに従ってファイルやディレクトリが無視されることを確認する。
    """
    summarizer = ProjectSummarizer(setup_project)
    output_file = setup_project / "summary.txt"
    summarizer.generate_project_summary(output_file=output_file)
    
    content = output_file.read_text(encoding="utf-8")
    
    # サマリーを「ディレクトリ構造」と「ファイル内容」のセクションに分割
    try:
        structure_part, contents_part = content.split("\n## File Contents\n\n", 1)
    except ValueError:
        pytest.fail("Output file is not in the expected format with '## File Contents'.")

    # --- チェック1：ディレクトリ構造セクションの検証 ---
    # 無視された項目が「ディレクトリ構造」に含まれていないことを確認
    assert "temp.log" not in structure_part
    assert ".venv" not in structure_part
    assert "guide.md" not in structure_part
    
    # 無視されていないファイルが「ディレクトリ構造」に含まれていることを確認
    assert "main.py" in structure_part
    assert ".gitignore" in structure_part # .gitignore自体は構造に含まれる

    # --- チェック2：ファイル内容セクションの検証 ---
    # .gitignoreファイルの内容が「ファイル内容」セクションに書き出されていることを確認
    # ここで ".venv/" が含まれているのは正しい動作
    assert "### .gitignore" in contents_part.replace('\\', '/')
    assert ".venv/" in contents_part


def test_binary_file_handling(setup_project):
    """
    バイナリファイルが正しく「(binary file)」として扱われるかテストする。
    """
    # テスト用のバイナリファイルを作成 (Nullバイトを含む)
    (setup_project / "app.ico").write_bytes(b"\x00\x01\x02\x00\x03")
    
    summarizer = ProjectSummarizer(setup_project)
    output_file = setup_project / "summary.txt"
    summarizer.generate_project_summary(output_file=output_file)
    
    content = output_file.read_text(encoding="utf-8")
    
    # ディレクトリ構造セクションで(binary file)と表示されているか確認
    assert "- app.ico (binary file)" in content
    # ファイル内容セクションにバイナリファイルの中身が出力されていないことを確認
    assert "### app.ico" not in content.replace("\\", "/")


def test_shift_jis_encoding_handling(setup_project):
    """
    Shift-JISでエンコードされたファイルの内容が正しく読み込まれるかテストする。
    """
    japanese_text = "これはShift-JISのテストです。"
    # Shift-JISでファイルに書き込み
    (setup_project / "sjis_document.txt").write_text(japanese_text, encoding="shift_jis")
    
    summarizer = ProjectSummarizer(setup_project)
    output_file = setup_project / "summary.txt"
    summarizer.generate_project_summary(output_file=output_file)
    
    content = output_file.read_text(encoding="utf-8")
    
    # ファイル内容セクションで、UTF-8に変換された日本語テキストが含まれていることを確認
    assert japanese_text in content


def test_additional_ignore_patterns_option(setup_project):
    """
    -i (--ignore) オプションで指定したパターンが無視されるかテストする。
    """
    (setup_project / "temp.tmp").touch()
    (setup_project / "main.py").touch()
    
    # コンストラクタに追加の無視パターンを渡す
    summarizer = ProjectSummarizer(setup_project, additional_ignore_patterns=["*.tmp"])
    output_file = setup_project / "summary.txt"
    summarizer.generate_project_summary(output_file=output_file)
    
    content = output_file.read_text(encoding="utf-8")
    
    assert "temp.tmp" not in content
    assert "main.py" in content


def test_file_types_option(setup_project):
    """
    -t (--type) オプションで指定した拡張子のファイルのみが含まれるかテストする。
    """
    (setup_project / "script.py").touch()
    (setup_project / "document.md").touch()
    
    # コンストラクタに含めるファイル拡張子を渡す
    summarizer = ProjectSummarizer(setup_project, file_types=[".py"])
    output_file = setup_project / "summary.txt"
    summarizer.generate_project_summary(output_file=output_file)
    
    content = output_file.read_text(encoding="utf-8")
    
    assert "script.py" in content
    assert "document.md" not in content