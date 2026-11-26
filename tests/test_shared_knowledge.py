from hashlib import sha256

import pytest
from mcp.server.fastmcp.exceptions import ToolError

from knowledgeos.cli import initialize, scaffold
from knowledgeos.layout import LOCALES, Layout
from markdown_native import NativeWiki
from server import Wiki, make_server


@pytest.mark.parametrize("locale", LOCALES)
def test_shared_create_is_append_only(tmp_path, monkeypatch, locale):
    vault = tmp_path / "vault"
    vault.mkdir()
    protected = tmp_path / "protected"
    protected.mkdir()
    monkeypatch.setenv("KNOWLEDGEOS_PROTECTED_VAULT", str(protected))
    initialize(vault, locale)
    layout = Layout(locale)
    path = layout.path("15_Shared/concepts/shared-test.md").as_posix()
    index = vault / layout.path("15_Shared/index.md")
    log = vault / layout.path("15_Shared/log.md")
    index_before, log_before = index.read_bytes(), log.read_bytes()
    human_path = layout.path("00_Human/Resources/private.md").as_posix()
    (vault / human_path).write_text("# Private", encoding="utf-8")
    wiki = Wiki(vault)
    native = NativeWiki(wiki)
    markdown = scaffold("Shared test", "concept", []).replace("owner: agent", "owner: shared")
    assert native.change("create", path, markdown=markdown)["code"] == "NATIVE_APPLIED"
    base = sha256(markdown.encode()).hexdigest()
    assert wiki.read(path).sha256 == base
    assert wiki.snapshot("shared")[0]
    assert wiki.read(path).metadata()["subject"] == "shared"
    assert not wiki.snapshot("human")[0]
    assert index.read_bytes().startswith(index_before)
    assert log.read_bytes().startswith(log_before)
    state = (index.read_bytes(), log.read_bytes())
    with pytest.raises(ValueError, match="already exists"):
        native.change("create", path, markdown=markdown)
    for operation in ("update", "delete", "move", "restore"):
        with pytest.raises(ValueError, match="SHARED_WRITE_AUTHORIZATION_REQUIRED"):
            native.change(operation, path, base, markdown)
    for meta in (index, log):
        with pytest.raises(ValueError, match="PATH_DENIED"):
            native.change("create", meta.relative_to(vault).as_posix(), markdown=markdown)
    with pytest.raises(ValueError, match="PATH_DENIED"):
        native.change("create", human_path, markdown=markdown)
    with pytest.raises(ValueError, match="PATH_DENIED"):
        native.change("create", layout.path("90_Archive/archived.md").as_posix(), markdown=markdown)
    proposal = make_server(wiki)._tool_manager.get_tool("propose_shared_update").fn
    draft = proposal(path, base, markdown + "\nChanges\n")
    assert draft["code"] == "MANUAL_APPLY_REQUIRED"
    assert draft["base_sha256"] == base and draft["request_id"]
    assert (index.read_bytes(), log.read_bytes()) == state
    assert wiki.read(path).sha256 == base
    with pytest.raises(ToolError, match="hash has changed"):
        proposal(path, "0" * 64, markdown)
    assert Wiki(vault, (layout.path("00_Human/Resources").as_posix(),)).read(human_path)
    monkeypatch.setenv("KNOWLEDGEOS_PROTECTED_VAULT", str(vault))
    with pytest.raises(ValueError, match="separate approved local root"):
        NativeWiki(Wiki(vault))


def test_old_vault_is_readable_without_shared(tmp_path):
    (tmp_path / "10_Agent/wiki").mkdir(parents=True)
    assert [path.as_posix() for path in Wiki(tmp_path).scopes] == ["10_Agent/wiki"]
