import shutil
from pathlib import Path
from types import SimpleNamespace

import pytest
from mcp.server.fastmcp.exceptions import ToolError

from knowledgeos.cli import ingest, initialize, parser, run, scaffold
from knowledgeos.config import looks_like_vault
from knowledgeos.layout import LOCALES, Layout, detect_layout
from markdown_native import NativeWiki
from server import Wiki, make_server


@pytest.mark.parametrize("locale", LOCALES)
def test_localized_workflow(tmp_path, locale, monkeypatch):
    protected = tmp_path / "protected-fixture"
    protected.mkdir()
    monkeypatch.setenv("KNOWLEDGEOS_PROTECTED_VAULT", str(protected))
    layout = Layout(locale)
    root = tmp_path / "测试知识库"
    shutil.copytree(Path("vault-template") / locale, root)
    rel = lambda name: layout.path(name).as_posix()
    assert detect_layout(root) == layout
    assert looks_like_vault(root)
    scope = rel("00_Human/Resources")
    human = scope + "/人工笔记.md"
    (root / human).write_text("# Original Human", encoding="utf-8")
    denied = rel("00_Human/Daily") + "/私人笔记.md"
    (root / denied).write_text("# Private", encoding="utf-8")
    args = ["--vault", str(root), "--human-read", scope]
    assert run(parser().parse_args(args + ["doctor"]))["locale"] == locale
    wiki = Wiki(root, (scope,))
    native = NativeWiki(wiki)
    tools = make_server(wiki, native_write=True)._tool_manager
    call = lambda name, **kwargs: tools.get_tool(name).fn(**kwargs)
    with pytest.raises(ToolError):
        wiki.read(denied)
    with pytest.raises(ValueError):
        native.target(human)
    with pytest.raises(ValueError):
        native.target(rel("10_Agent/wiki/index.md"))
    proposal = call("propose_human_update", path=human, expected_sha256=wiki.read(human).sha256,
                    markdown="# Edited")
    assert proposal["code"] == "MANUAL_APPLY_REQUIRED" and "+# Edited" in proposal["diff"]
    assert (root / human).read_text(encoding="utf-8") == "# Original Human"

    original = tmp_path / "原始资料.txt"
    original.write_text("source fixture", encoding="utf-8")
    source = rel("10_Agent/wiki") + "/source.md"
    result = ingest(wiki, SimpleNamespace(file=original, path=source, title="来源", apply=True))
    assert result["code"] == "NATIVE_APPLIED"
    assert result["original_path"].startswith(rel("10_Agent/raw/documents") + "/")
    note = rel("10_Agent/wiki/concepts") + "/unicode-note.md"
    content = scaffold("跨语言知识", "concept", [f"[[{source}]]"]) + f"\n[来源](../source.md)\n"
    assert call("native_note_change", operation="create", path=note, markdown=content)["code"] == "NATIVE_APPLIED"
    before = wiki.read(note).sha256
    assert run(parser().parse_args(args + ["query", "跨语言知识"]))["total"] == 1
    assert call("read_markdown", path=note)["sha256"] == before
    issues = call("lint_knowledge")["items"]
    assert all(issue["kind"] == "not_resolved_in_scope" and issue["path"] == source for issue in issues), issues
    assert any(x["target"] == note for x in call("knowledge_links", path=source)["items"])
    assert native.change("update", note, before, content + "\nMore")["code"] == "NATIVE_APPLIED"
    changed = wiki.read(note).sha256
    assert native.change("restore", note, changed, backup_sha256=before)["code"] == "NATIVE_APPLIED"
    assert wiki.read(note).sha256 == before
    archived = run(parser().parse_args(args + ["archive", note, "--expected-sha256", before]))
    assert archived["code"] == "NATIVE_APPLIED"
    assert wiki.read(note).document.status == "archived"
    assert note.removesuffix(".md") in (root / rel("10_Agent/wiki/index.md")).read_text(encoding="utf-8")
    assert "native_local" in (root / rel("10_Agent/wiki/log.md")).read_text(encoding="utf-8")
    assert not list((root / rel("20_Exchange/agent-to-agent/locks")).glob("*.lock.md"))


def test_init_and_mixed_layout(tmp_path, monkeypatch):
    monkeypatch.setenv("KNOWLEDGEOS_PROTECTED_VAULT", str(tmp_path.parent / "protected-fixture"))
    (tmp_path.parent / "protected-fixture").mkdir(exist_ok=True)
    initialize(tmp_path, "zh-CN")
    assert detect_layout(tmp_path).locale == "zh-CN"
    (tmp_path / "00_Human").mkdir()
    with pytest.raises(ValueError, match="Ambiguous"):
        Wiki(tmp_path)
