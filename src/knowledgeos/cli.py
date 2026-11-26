"""Installable Markdown Native workflow entry point."""

import argparse
from datetime import date
from hashlib import sha256
import json
from pathlib import Path
import re
import sys
import tomllib

from mcp.server.fastmcp.exceptions import ToolError
from markdown_native import NativeWiki, publish, read_file
from release_paths import protected_vault
from server import Wiki, make_server

from . import __version__
from .errors import ValidationError
from .schema import render_frontmatter
from .sections import _append_section


RAW = Path("10_Agent/raw/documents")
WIKI = Path("10_Agent/wiki")
READ_TOOLS = ("search_knowledge", "read_markdown", "note_metadata", "query_tags",
              "knowledge_links", "lint_knowledge", "propose_human_update")


def initialize(root):
    if root.resolve(strict=True) != root or root.is_relative_to(protected_vault()) or any(root.iterdir()):
        raise ValueError("init requires an empty canonical test root outside the protected vault")
    folders = (*(WIKI / name for name in ("concepts", "entities", "topics", "comparisons", "synthesis", "projects", "decisions")),
               RAW, Path("00_Human/Resources"), Path("20_Exchange/agent-to-agent/locks"), Path("30_System"), Path("90_Archive"))
    for folder in folders:
        (root / folder).mkdir(parents=True, exist_ok=True)
    return {"code": "TEST_ROOT_INITIALIZED"}


def scaffold(title, kind, sources):
    title = " ".join(title.split())
    if not title:
        raise ValueError("Title required")
    today = date.today().isoformat()
    meta = {"title": title, "type": kind, "owner": "agent", "status": "draft",
            "created_by": "knowledgeos", "created": today, "updated": today,
            "sources": sources, "related": [], "tags": []}
    return render_frontmatter(meta) + "\n# " + title + "\n"


def synthesis(wiki, args):
    notes = [wiki.read(path) for path in dict.fromkeys(args.inputs)]
    if len(notes) < 2:
        raise ValueError("Synthesis requires two distinct readable notes")
    links = [f"[[{note.path.removesuffix('.md')}]]" for note in notes]
    excerpts = []
    for link, note in zip(links, notes):
        summary = next((line.strip() for line in note.document.body.splitlines()
                        if line.strip() and not line.lstrip().startswith("#")), "")
        excerpts.append(f"- {link} — {summary[:240]}")
    markdown = (scaffold(args.title, "synthesis", links) + "\n## Inputs\n\n" + "\n".join(excerpts)
                + "\n\n## Agreements\n\n## Conflicts and uncertainty\n\n## Synthesis\n\n## Open questions\n")
    if not args.apply:
        return {"code": "DRAFT", "path": args.path, "markdown": markdown}
    return NativeWiki(wiki).change("create", args.path, markdown=markdown)


def ingest(wiki, args):
    source = args.file.absolute()
    if source.resolve(strict=True) != source:
        raise ValueError("Input must be a canonical regular file")
    original = read_file(source)
    if not original:
        raise ValueError("Expected a nonempty original")
    checksum = sha256(original).hexdigest()
    suffix = source.suffix.lower()
    relative = (RAW / (checksum + (suffix if re.fullmatch(r"\.[a-z0-9]{1,10}", suffix) else ".bin"))).as_posix()
    markdown = (scaffold(args.title, "source", [f"[[{relative}]]"])
                + f"\n## Provenance\n\n- Original file: {json.dumps(source.name, ensure_ascii=False)}"
                + f"\n- SHA-256: {checksum}\n\n## Summary\n")
    if not args.apply:
        return {"code": "DRAFT", "path": args.path, "original_path": relative, "markdown": markdown}
    native = NativeWiki(wiki)
    if read_file(native.target(args.path)) is not None:
        raise ValueError("CONFLICT: source page exists")
    folder = wiki.root / RAW
    if folder.resolve(strict=True) != folder or not folder.is_dir():
        raise ValueError("Expected an existing plain original-source directory")
    target = wiki.root / relative
    old = read_file(target)
    if old is None:
        try:
            publish(target, original, None)
        except FileExistsError:
            if read_file(target) != original:
                raise
    elif old != original:
        raise ValueError("CONFLICT: original digest path contains different bytes")
    return {**native.change("create", args.path, markdown=markdown), "original_path": relative}


def parser():
    cli = argparse.ArgumentParser(prog="knowledgeos", description=__doc__)
    cli.add_argument("--version", action="version", version=__version__)
    cli.add_argument("--vault", type=Path)
    cli.add_argument("--config", type=Path)
    cli.add_argument("--human-read", action="append", default=[])
    sub = cli.add_subparsers(dest="operation", required=True)
    for name in ("init", "doctor", "sync"):
        sub.add_parser(name)
    sub.add_parser("inspect").add_argument("tool", choices=READ_TOOLS)
    sub.add_parser("query").add_argument("query")
    for name in ("create", "update", "delete", "restore", "archive", "append-section", "ingest", "synthesize"):
        p = sub.add_parser(name)
        p.add_argument("path")
        if name in {"update", "delete", "restore", "archive", "append-section"}:
            p.add_argument("--expected-sha256", required=name != "restore")
        if name == "restore":
            p.add_argument("--backup-sha256", required=True)
        if name == "append-section":
            p.add_argument("--heading", required=True)
        if name in {"ingest", "synthesize"}:
            p.add_argument("--title", required=True)
            p.add_argument("--apply", action="store_true", help="Write to an approved test root")
        if name == "ingest":
            p.add_argument("--file", type=Path, required=True)
        if name == "synthesize":
            p.add_argument("--from", dest="inputs", nargs="+", required=True)
    return cli


def run(args):
    config = {}
    if args.config:
        with args.config.open("rb") as stream:
            config = tomllib.load(stream)
    root = args.vault or (Path(config["vault"]) if "vault" in config else None)
    if root is None:
        raise ValueError("Set --vault or vault in the local --config file")
    root = root.absolute()
    op = args.operation
    if op == "init":
        return initialize(root)
    wiki = Wiki(root, tuple(args.human_read or config.get("human_read", ())))
    if op == "doctor":
        notes, skipped, _ = wiki.snapshot()
        return {"code": "READ_READY", "notes": len(notes), "skipped": skipped, "scopes": list(map(str, wiki.scopes))}
    if op in {"query", "inspect"}:
        name, request = ("search_knowledge", {"query": args.query}) if op == "query" else (args.tool, json.load(sys.stdin))
        tool = make_server(wiki)._tool_manager.get_tool(name)
        return tool.fn(**dict(tool.fn_metadata.arg_model.model_validate(request)))
    if op == "ingest":
        return ingest(wiki, args)
    if op == "synthesize":
        return synthesis(wiki, args)
    native = NativeWiki(wiki)
    if op == "sync":
        return native.sync()
    markdown = None
    if op in {"archive", "append-section"}:
        native.target(args.path)
        note = wiki.read(args.path)
        if note.sha256 != args.expected_sha256:
            raise ValueError("CONFLICT: note hash has changed")
        old = note.document.text.replace("\r\n", "\n")
        if op == "archive":
            match = re.match(r"\A---\n(.*?)\n---(?=\n|$)", old, re.DOTALL)
            if not match or not note.document.has_frontmatter or note.document.error:
                raise ValueError("Archive requires valid frontmatter")
            front = re.sub(r"(?m)^status:[^\n]*$", "status: archived", match[1])
            if not re.search(r"(?m)^status: archived$", front):
                front += "\nstatus: archived"
            markdown = old[:match.start(1)] + front + old[match.end(1):]
        else:
            markdown = _append_section(old, args.heading, sys.stdin.buffer.read().decode("utf-8"))
        op = "update"
    elif op in {"create", "update"}:
        markdown = sys.stdin.buffer.read().decode("utf-8")
    return native.change(op, args.path, getattr(args, "expected_sha256", None), markdown,
                         getattr(args, "backup_sha256", None))


def main():
    try:
        result = run(parser().parse_args())
    except (OSError, ValueError, TypeError, ValidationError, ToolError) as exc:
        print(json.dumps({"code": "REJECTED", "detail": str(exc)}, ensure_ascii=True), file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=True))
    return 0
