import pytest
from generate_project_summary.summarizer import ProjectSummarizer

def test_gitignore_and_os_path_handling(setup_project):
    """
    .gitignoreのテスト。無視された項目が「ディレクトリ構造」に含まれないことを確認しつつ、
    .gitignoreファイル自体は「ファイル内容」に含まれることを許容する。
    """
    # .gitignoreには標準的なUnix形式のセパレータを使用する
    (setup_project / ".gitignore").write_text("*.log\n.venv/\ndocs/guide.md")
    
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
    # 無視されたファイルやディレクトリが「ディレクトリ構造」に含まれていないことを確認
    assert "temp.log" not in structure_part
    assert ".venv/" not in structure_part
    assert "guide.md" not in structure_part
    
    # 無視されていないファイルが「ディレクトリ構造」に含まれていることを確認
    assert "main.py" in structure_part
    assert "README.md" in structure_part
    assert ".gitignore" in structure_part # .gitignore自体は構造に含まれるべき

    # --- チェック2：ファイル内容セクションの検証 ---
    # .gitignoreファイルの内容が「ファイル内容」セクションに書き出されていることを確認
    assert "### .gitignore" in contents_part.replace('\\', '/') # Windowsパス対策
    # .gitignoreの中身として '.venv/' という文字列が含まれているのは正しい
    assert ".venv/" in contents_part