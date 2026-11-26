import asyncio
import os
import subprocess
import sys
from pathlib import Path

import pytest
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


PROGRAM = Path(__file__).resolve().parents[1] / "server.py"
PREFIX = "10_Agent/wiki/"


@pytest.fixture
def fixture(tmp_path):
    wiki = tmp_path / PREFIX
    wiki.mkdir(parents=True)
    (tmp_path / "00_Human").mkdir()
    (tmp_path / "00_Human/private.md").write_text("outside-scope-token", encoding="utf-8")
    files = {
        "agent.md": "---\ntitle: AI Agent\ntags: [agent]\n---\nAI Agent uses [[MCP]] and [[Missing]]. ![[image.png]]",
        "mcp.md": "---\ntitle: MCP\ntags: [agent, protocols]\n---\nMCP exposes [[Skills]].",
        "skills.md": "---\ntitle: Skills\n---\nSkill workflow and guidance.",
        "duplicate.md": "---\ntitle: Copy\n---\nSkill workflow and guidance.",
        "untyped.md": "No properties.",
        "中文.md": "---\ntitle: 知识关系\n---\n中文搜索可用。",
    }
    for name, body in files.items():
        (wiki / name).write_text(body, encoding="utf-8")
    (wiki / "image.png").write_bytes(b"fixture")
    os.link(tmp_path / "00_Human/private.md", wiki / "linked.md")
    if os.name == "nt":
        # A junction is permitted on ordinary Windows developer accounts.
        result = subprocess.run(
            ["cmd.exe", "/d", "/c", "mklink", "/J", str(wiki / "junction"), str(tmp_path / "00_Human")],
            capture_output=True, check=False,
        )
        assert result.returncode == 0, result.stderr
    else:
        (wiki / "junction").symlink_to(tmp_path / "00_Human", target_is_directory=True)
    return tmp_path


def test_scoped_tool_protocol(fixture):
    async def exercise():
        params = StdioServerParameters(command=sys.executable, args=["-B", str(PROGRAM), "--vault", str(fixture)],
                                       env={"PYTHONPATH": os.environ["PYTHONPATH"]})
        async with stdio_client(params) as (reader, writer):
            async with ClientSession(reader, writer) as client:
                await client.initialize()
                tools = {tool.name: tool for tool in (await client.list_tools()).tools}
                assert len(tools) == 9 and "propose_human_update" in tools
                assert all(tool.annotations.readOnlyHint for tool in tools.values())
                assert "query" in tools["search_knowledge"].inputSchema["required"]

                async def call(tool, **arguments):
                    result = await client.call_tool(tool, arguments)
                    assert not result.isError, result.content
                    return result.structuredContent

                hits = await call("search_knowledge", query="AI Agent", limit=1)
                assert hits["items"][0]["path"] == PREFIX + "agent.md"
                assert hits["next_offset"] == 1
                assert (await call("search_knowledge", query="中文"))["total"] == 1
                assert (await call("search_knowledge", query="outside-scope-token"))["total"] == 0
                assert (await call("query_tags", prefix="agent"))["items"] == [{"tag": "agent", "count": 2}]
                note = await call("read_markdown", path=PREFIX + "agent.md")
                assert note["properties"]["title"] == "AI Agent"
                assert (await call("note_metadata", path=PREFIX + "agent.md"))["sha256"] == note["sha256"]
                relations = (await call("knowledge_links", path=PREFIX + "agent.md"))["items"]
                assert any(e.get("status") == "attachment" for e in relations)
                assert any(e["direction"] == "related" and e["target"] == PREFIX + "skills.md" for e in relations)
                reverse = (await call("knowledge_links", path=PREFIX + "mcp.md"))["items"]
                assert {"direction": "backlink", "target": PREFIX + "agent.md"} in reverse
                kinds = {issue["kind"] for issue in (await call("lint_knowledge"))["items"]}
                assert {"duplicate_body", "properties", "not_resolved_in_scope"} <= kinds
                assert (await call("write_capability"))["code"] == "READ_ONLY"
                assert (await call("check_change", path=PREFIX + "agent.md", operation="update",
                                   expected_sha256=note["sha256"]))["may_submit"] is False
                assert (await call("check_change", path="00_Human/private.md", operation="update"))["code"] == "HUMAN_WRITE_AUTHORIZATION_REQUIRED"
                assert (await call("check_change", path=PREFIX + "new.md", operation="create"))["code"] == "SECURE_WRITER_UNAVAILABLE"
                assert (await client.call_tool("check_change", {"path": PREFIX + "agent.md", "operation": "update",
                                                                "expected_sha256": "0" * 64})).isError
                for path in ("00_Human/private.md", PREFIX + "linked.md", PREFIX + "junction/private.md",
                             PREFIX + "../README.md", PREFIX + "agent.md:hidden", str(fixture / "00_Human/private.md")):
                    result = await client.call_tool("read_markdown", {"path": path})
                    assert result.isError and "PATH_DENIED" in result.content[0].text
                assert (await client.call_tool("search_knowledge", {"query": "agent", "limit": -1})).isError
                assert (await client.call_tool("read_markdown", {"path": PREFIX + "agent.md", "expected_sha256": "wrong"})).isError

    before = {p: p.read_bytes() for p in fixture.rglob("*.md") if p.parent.name != "junction"}
    asyncio.run(exercise())
    assert {p: p.read_bytes() for p in fixture.rglob("*.md") if p.parent.name != "junction"} == before


def test_operator_scoped_human_read(fixture):
    granted = fixture / "00_Human" / "Shared"
    granted.mkdir()
    (granted / "shared.md").write_text("---\ntitle: Shared\ntags: [visible]\n---\nAI Agent [[MCP]].", encoding="utf-8")
    (fixture / "00_Human" / "private.md").write_text("---\ntitle: Private\ntags: [secret]\n---\nAI Agent private.", encoding="utf-8")

    async def exercise():
        params = StdioServerParameters(command=sys.executable,
                                       args=["-B", str(PROGRAM), "--vault", str(fixture),
                                             "--human-read", "00_Human/Shared"],
                                       env={"PYTHONPATH": os.environ["PYTHONPATH"]})
        async with stdio_client(params) as (reader, writer):
            async with ClientSession(reader, writer) as client:
                await client.initialize()
                results = await client.call_tool("search_knowledge", {"query": "AI Agent", "subject": "all"})
                found = results.structuredContent["items"]
                assert {n["subject"] for n in found} == {"human", "agent"}
                assert {n["path"] for n in found if n["subject"] == "human"} == {"00_Human/Shared/shared.md"}
                tags = await client.call_tool("query_tags", {"subject": "human"})
                assert tags.structuredContent["items"] == [{"tag": "visible", "count": 1}]
                cross = await client.call_tool("knowledge_links", {"path": PREFIX + "mcp.md"})
                assert {"direction": "backlink", "target": "00_Human/Shared/shared.md"} in cross.structuredContent["items"]
                denied = await client.call_tool("read_markdown", {"path": "00_Human/private.md"})
                assert denied.isError and "PATH_DENIED" in denied.content[0].text
                result = await client.call_tool("check_change", {"path": "00_Human/Shared/shared.md", "operation": "update"})
                assert result.structuredContent["code"] == "HUMAN_WRITE_AUTHORIZATION_REQUIRED"

    before = (granted / "shared.md").read_bytes()
    asyncio.run(exercise())
    assert (granted / "shared.md").read_bytes() == before
