"""Local Markdown operations with application-level scope and derived metadata."""

from release_paths import protected_vault

import argparse
from contextlib import ExitStack, contextmanager
from datetime import datetime, timedelta, timezone
from hashlib import sha256
import json
import os
from pathlib import Path, PurePosixPath
import sys
from tempfile import NamedTemporaryFile
from uuid import uuid4

from server import MAX_BYTES, Wiki, checked_handle, is_link, safe_name
from knowledgeos.index_format import render_block
from knowledgeos.schema import load_schema, parse_text, validate_document
from mcp.server.fastmcp.exceptions import ToolError


def digest(data):
    return sha256(data).hexdigest()


def read_file(path):
    try:
        if is_link(path):
            raise ValueError("linked file")
    except FileNotFoundError:
        return None
    with path.open("rb") as stream:
        checked_handle(stream, path)
        before = os.fstat(stream.fileno())
        data = stream.read()
        after = os.fstat(stream.fileno())
    current = path.lstat()
    if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns) or not os.path.samestat(after, current):
        raise ValueError("file changed during read")
    return data


def publish(path, data, previous):
    with NamedTemporaryFile(dir=path.parent, prefix=".native-", delete=False) as stage:
        staged = Path(stage.name)
        try:
            stage.write(data)
            stage.flush()
            os.fsync(stage.fileno())
        except BaseException:
            stage.close()
            staged.unlink()
            raise
    try:
        if read_file(path) != previous:
            raise ValueError("CONFLICT: target changed before publication")
        if previous is None:
            os.link(staged, path)
        else:
            os.replace(staged, path)
    finally:
        staged.unlink(missing_ok=True)


class NativeWiki:
    def __init__(self, wiki):
        self.wiki = wiki
        self.root = wiki.root
        self.layout = wiki.layout
        self.base = self.root / self.layout.wiki
        self.index = self.layout.path("10_Agent/wiki/index.md")
        self.log = self.layout.path("10_Agent/wiki/log.md")
        self.state = self.base / ".knowledgeos-native"
        real = protected_vault().resolve()
        if (self.root.resolve().is_relative_to(real)
                or os.path.lexists(self.root / ".knowledgeos-r6-synthetic")):
            raise ValueError("Native writes require a separate approved local root")

    @contextmanager
    def locked(self, *notes, shared=False):
        if self.base.resolve(strict=True) != self.base:
            raise ValueError("unsafe wiki directory")
        self.state.mkdir(exist_ok=True)
        if is_link(self.state) or not self.state.is_dir():
            raise ValueError("unsafe native state directory")
        lock = self.state / "lock"
        lock.mkdir()
        try:
            with ExitStack() as stack:
                folder = self.root / self.layout.path("20_Exchange/agent-to-agent/locks")
                if os.path.lexists(folder):
                    if folder.resolve(strict=True) != folder or is_link(folder) or not folder.is_dir():
                        raise ValueError("unsafe shared lease directory")
                    now = datetime.now(timezone.utc)
                    metadata = ("15_Shared/index.md", "15_Shared/log.md") if shared else ("10_Agent/wiki/index.md", "10_Agent/wiki/log.md")
                    for relative in sorted(set(notes) | {self.layout.path(name).as_posix() for name in metadata}):
                        path = folder / (relative.replace("/", "-").replace(".", "-") + ".lock.md")
                        payload = ("---\nlock: true\npath: " + json.dumps(relative) + "\nowner: knowledgeos-native\n"
                                   f"acquired: {now.isoformat()}\nexpires: {(now + timedelta(minutes=15)).isoformat()}\n"
                                   "intent: Native Markdown update or projection sync\n---\n").encode()
                        with path.open("xb") as stream:
                            stream.write(payload)
                        stack.callback(self.release_lease, path, payload)
                yield
        finally:
            lock.rmdir()

    @staticmethod
    def release_lease(path, payload):
        if read_file(path) == payload:
            path.unlink()

    def target(self, path):
        rel = PurePosixPath(path)
        if (not safe_name(path) or self.layout.wiki not in rel.parents or rel.suffix != ".md"
                or rel.name.casefold() in self.layout.meta):
            raise ValueError("PATH_DENIED: expected an Agent Markdown note")
        target = self.root / path
        if target.parent.resolve(strict=True) != target.parent:
            raise ValueError("PATH_DENIED: unsafe note parent")
        return target

    def backup(self, data):
        key = digest(data)
        path = self.state / (key + ".bak")
        existing = read_file(path)
        if existing is None:
            publish(path, data, None)
        elif existing != data:
            raise ValueError("backup checksum mismatch")
        return key

    def event(self, path, before, after, origin, operation):
        return {"event_id": uuid4().hex, "utc": datetime.now(timezone.utc).isoformat(),
                "path": path, "before": before, "after": after,
                "origin": origin, "operation": operation}

    def sync_locked(self, local_event=None):
        state_file = self.state / "state.json"
        original = read_file(state_file)
        record = json.loads(original) if original is not None else {"observed": {}, "events": []}
        notes, skipped, _ = self.wiki.snapshot("agent")
        if skipped:
            raise ValueError("incomplete wiki scan; sync deferred")
        observed = {}
        documents = []
        for note in notes:
            relative = PurePosixPath(note.path)
            if relative.name.casefold() in self.layout.meta:
                continue
            data = read_file(self.root / note.path)
            if data is None or digest(data) != note.sha256:
                raise ValueError("note changed during sync")
            observed[note.path] = self.backup(data)
            documents.append(note.document)
        baseline = record["observed"]
        if local_event is not None:
            path = local_event["path"]
            if local_event["after"] != observed.get(path):
                raise ValueError("local change could not be verified during sync")
            record["events"].append(local_event)
            if local_event["after"] is None:
                baseline.pop(path, None)
            else:
                baseline[path] = local_event["after"]
        for path in sorted(observed.keys() | baseline.keys()):
            before, after = baseline.get(path), observed.get(path)
            if before != after:
                operation = "baseline" if original is None else ("delete" if after is None else "create" if before is None else "update")
                record["events"].append(self.event(path, before, after, "observed_filesystem", operation))
        record["observed"] = observed
        payload = json.dumps(record, ensure_ascii=False, indent=2).encode()
        if payload != original:
            publish(state_file, payload, original)
        log = ["    " + json.dumps(event, ensure_ascii=False) for event in record["events"]]
        self.project(self.index.name, "index", render_block(documents).splitlines()[1:-1])
        self.project(self.log.name, "native-observations", log)
        return {"code": "NATIVE_SYNCED", "notes": len(observed), "events": len(record["events"])}

    def project(self, name, block, rows):
        path = self.base / name
        previous = read_file(path)
        text = previous.decode("utf-8") if previous is not None else f"# Agent Wiki {name[:-3].title()}\n"
        start, end = (f"<!-- knowledgeos:{block}:{edge} -->" for edge in ("start", "end"))
        eol = "\r\n" if "\r\n" in text else "\n"
        body = eol.join([start, *rows, end])
        if start not in text and end not in text:
            updated = text + eol * 2 + body + eol
        elif text.count(start) == text.count(end) == 1 and text.index(start) < text.index(end):
            updated = text[:text.index(start)] + body + text[text.index(end) + len(end):]
        else:
            raise ValueError(f"malformed managed block: {name}")
        if updated != text:
            if previous is not None:
                self.backup(previous)
            publish(path, updated.encode(), previous)

    def sync(self):
        with self.locked():
            return self.sync_locked()

    def create_shared(self, path, markdown):
        rel = PurePosixPath(path)
        target = self.root / rel
        if (not safe_name(path) or self.layout.shared not in rel.parents
                or len(rel.parts) != 3 or rel.suffix != ".md"
                or rel.name.casefold() in self.layout.meta or target.parent.resolve(strict=True) != target.parent):
            raise ValueError("PATH_DENIED: expected a Shared Markdown knowledge path")
        if not markdown or len(markdown.encode()) > MAX_BYTES:
            raise ValueError("Expected Markdown within the scoped read limit")
        doc = parse_text(markdown, target, path)
        issues = validate_document(doc, schema=load_schema(self.root, layout=self.layout), layout=self.layout)
        if any(issue.level == "error" for issue in issues):
            raise ValueError("; ".join(str(issue) for issue in issues if issue.level == "error"))
        data = markdown.encode()
        event = self.event(path, None, digest(data), "native_local", "create")
        index = self.root / self.layout.path("15_Shared/index.md")
        log = self.root / self.layout.path("15_Shared/log.md")
        with self.locked(path, shared=True):
            if read_file(target) is not None:
                raise ValueError("CONFLICT: destination already exists")
            previous_index, previous_log = read_file(index), read_file(log)
            if previous_index is None or previous_log is None:
                raise ValueError("Shared index and log must already exist")
            index_entry = f"\n- [[{path.removesuffix('.md')}]]\n".encode()
            log_entry = ("\n    " + json.dumps(event, ensure_ascii=False) + "\n").encode()
            for previous in (previous_index, previous_log):
                self.backup(previous)
            publish(target, data, None)
            try:
                publish(index, previous_index + index_entry, previous_index)
                publish(log, previous_log + log_entry, previous_log)
            except (OSError, ValueError, ToolError):
                return {"code": "NATIVE_SYNC_PENDING", "event": event}
        return {"code": "NATIVE_APPLIED", "event": event}

    def change(self, operation, path, expected_sha256=None, markdown=None, backup_sha256=None):
        if self.layout.shared in PurePosixPath(path).parents:
            if operation != "create" or expected_sha256 is not None or backup_sha256 is not None:
                raise ValueError("SHARED_WRITE_AUTHORIZATION_REQUIRED: use a confirmed native proposal")
            return self.create_shared(path, markdown)
        if operation not in {"create", "update", "delete", "restore"}:
            raise ValueError("unknown local operation")
        target = self.target(path)
        with self.locked(path):
            self.sync_locked()
            previous = read_file(target)
            before = digest(previous) if previous is not None else None
            if (operation == "create" and before is not None or operation in {"update", "delete"} and before is None
                    or expected_sha256 != before):
                raise ValueError("CONFLICT: original SHA-256 or absence differs")
            if operation == "restore":
                state = json.loads(read_file(self.state / "state.json"))
                if not backup_sha256 or len(backup_sha256) != 64 or any(c not in "0123456789abcdef" for c in backup_sha256) or not any(
                    event["path"] == path and backup_sha256 in (event["before"], event["after"])
                    for event in state["events"]
                ):
                    raise ValueError("backup not associated with this note")
                data = read_file(self.state / (backup_sha256 + ".bak"))
                if data is None or digest(data) != backup_sha256:
                    raise ValueError("backup unavailable or corrupt")
            elif operation != "delete":
                if not markdown or not markdown.strip():
                    raise ValueError("Markdown is required")
                data = markdown.encode("utf-8")
                if len(data) > MAX_BYTES:
                    raise ValueError("Markdown exceeds the scoped read limit")
            else:
                data = None
            if previous is not None:
                self.backup(previous)
            after = self.backup(data) if data is not None else None
            if data is None:
                if read_file(target) != previous:
                    raise ValueError("CONFLICT: note changed before deletion")
                target.unlink()
            else:
                publish(target, data, previous)
            event = self.event(path, before, after, "native_local", operation)
            try:
                self.sync_locked(event)
            except (OSError, ValueError, ToolError):
                return {"code": "NATIVE_SYNC_PENDING", "event": event}
            return {"code": "NATIVE_APPLIED", "event": event}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vault", type=Path, required=True)
    parser.add_argument("operation", choices=("sync", "create", "update", "delete", "restore"))
    parser.add_argument("--path")
    parser.add_argument("--expected-sha256")
    parser.add_argument("--backup-sha256")
    args = parser.parse_args()
    try:
        native = NativeWiki(Wiki(args.vault))
        if args.operation == "sync":
            result = native.sync()
        else:
            if not args.path:
                parser.error("--path is required for a note operation")
            markdown = sys.stdin.buffer.read().decode("utf-8") if args.operation in {"create", "update"} else None
            result = native.change(args.operation, args.path, args.expected_sha256, markdown, args.backup_sha256)
        print(json.dumps(result, ensure_ascii=False))
    except (OSError, ValueError, ToolError) as exc:
        print(json.dumps({"code": "NATIVE_REJECTED", "detail": str(exc)}, ensure_ascii=False))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
