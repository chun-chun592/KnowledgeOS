"""Read-only reconciliation of a durable PREPARED projection receipt."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import os
from pathlib import Path, PurePosixPath
from typing import Literal

from mcp.server.fastmcp.exceptions import ToolError

from server import MAX_BYTES, checked_handle, is_link, safe_name


@dataclass(frozen=True)
class FileEvidence:
    identity: tuple[int, int]
    digest: str


@dataclass(frozen=True)
class PreparedProjection:
    target: str
    staged: str
    root_identity: tuple[int, int]
    parent_identity: tuple[int, int]
    request_digest: str
    previous: FileEvidence | None
    replacement: FileEvidence


def identity(stat_result: os.stat_result) -> tuple[int, int]:
    key = stat_result.st_dev, stat_result.st_ino
    if not key[1]:
        raise ValueError("Filesystem did not supply an object identity")
    return key


def _observe(path: Path) -> FileEvidence | None:
    snapshot = observe_bytes(path)
    return snapshot[0] if snapshot is not None else None


def observe_bytes(path: Path) -> tuple[FileEvidence, bytes] | None:
    try:
        if is_link(path):
            raise ValueError("Linked leaf")
    except FileNotFoundError:
        return None
    try:
        with path.open("rb") as stream:
            checked_handle(stream, path)
            before = os.fstat(stream.fileno())
            payload = stream.read(MAX_BYTES + 1)
            after = os.fstat(stream.fileno())
        if len(payload) > MAX_BYTES or (
            before.st_size, before.st_mtime_ns
        ) != (after.st_size, after.st_mtime_ns):
            raise ValueError("Unstable or oversized leaf")
        if identity(path.lstat()) != identity(after):
            raise ValueError("Leaf changed during inspection")
        return FileEvidence(identity(after), sha256(payload).hexdigest()), payload
    except FileNotFoundError:
        raise ValueError("Leaf disappeared during inspection") from None


def reconcile(
    root: Path, receipt: PreparedProjection, canonical_request: bytes
) -> Literal["PROJECTED", "PREPARED", "NEEDS_REVIEW"]:
    """Classify evidence only. An unchanged PREPARED target grants no retry authority."""
    if sha256(canonical_request).hexdigest() != receipt.request_digest:
        return "NEEDS_REVIEW"
    if not all(safe_name(p) for p in (receipt.target, receipt.staged)):
        return "NEEDS_REVIEW"
    target_rel, staged_rel = map(PurePosixPath, (receipt.target, receipt.staged))
    if target_rel.suffix.casefold() != ".md" or (
        target_rel.parent != staged_rel.parent
        or target_rel.as_posix().casefold() == staged_rel.as_posix().casefold()
        or receipt.previous is not None and receipt.previous.identity == receipt.replacement.identity
    ):
        return "NEEDS_REVIEW"
    root = root.absolute()
    target, staged = root.joinpath(*target_rel.parts), root.joinpath(*staged_rel.parts)
    try:
        def stable_directories() -> bool:
            return (
                root.resolve(strict=True) == root
                and not any(is_link(p) for p in target.parents if p.is_relative_to(root))
                and identity(root.stat()) == receipt.root_identity
                and identity(target.parent.stat()) == receipt.parent_identity
            )

        if not stable_directories():
            return "NEEDS_REVIEW"
        final, pending = _observe(target), _observe(staged)
        if not stable_directories():
            return "NEEDS_REVIEW"
        if final == receipt.replacement and pending is None:
            return "PROJECTED"
        if final == receipt.previous and pending == receipt.replacement:
            return "PREPARED"
    except (OSError, ValueError, ToolError):
        return "NEEDS_REVIEW"
    return "NEEDS_REVIEW"
