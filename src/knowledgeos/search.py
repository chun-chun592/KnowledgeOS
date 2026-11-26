"""Keyword search and link resolution.

Deliberately no embeddings or vector database: v0.1 uses transparent scoring over
frontmatter and body text, works offline, and is easy to audit.
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Sequence

from .paths import Vault
from .schema import Document, read_document

WIKILINK_RE = re.compile(r"\[\[([^\]|#]+)(?:#[^\]|]*)?(?:\|[^\]]*)?\]\]")
HEADING_RE = re.compile(r"^#{1,6}\s+(.+)$", re.MULTILINE)

DEFAULT_REGIONS = ("human", "agent")
META_FILES = {"index.md", "log.md", "readme.md"}


@dataclass
class SearchHit:
    rel: str
    title: str
    score: int
    note_type: str
    status: str
    updated: str
    tags: list[str]
    snippet: str
    matched: list[str] = field(default_factory=list)

    def as_dict(self) -> dict[str, object]:
        return {
            "path": self.rel,
            "title": self.title,
            "score": self.score,
            "type": self.note_type,
            "status": self.status,
            "updated": self.updated,
            "tags": self.tags,
            "snippet": self.snippet,
            "matched": self.matched,
        }


@dataclass
class LinkIndex:
    """Resolves Obsidian wikilinks against paths, stems, titles and aliases."""

    paths: set[str] = field(default_factory=set)
    stems: set[str] = field(default_factory=set)
    titles: set[str] = field(default_factory=set)
    aliases: set[str] = field(default_factory=set)
    attachments: set[str] = field(default_factory=set)

    @classmethod
    def build(cls, vault: Vault) -> "LinkIndex":
        index = cls()
        for path in vault.iter_markdown(["all"]):
            rel = path.relative_to(vault.root).as_posix()
            index.paths.add(rel.casefold())
            index.paths.add(rel[:-3].casefold() if rel.lower().endswith(".md") else rel.casefold())
            index.stems.add(path.stem.casefold())
            try:
                document = read_document(path, vault.root)
            except (OSError, UnicodeDecodeError):
                continue
            title = document.frontmatter.get("title")
            if isinstance(title, str) and title.strip():
                index.titles.add(title.strip().casefold())
            aliases = document.frontmatter.get("aliases")
            if isinstance(aliases, list):
                for alias in aliases:
                    if isinstance(alias, str) and alias.strip():
                        index.aliases.add(alias.strip().casefold())
        for path in vault.root.rglob("*"):
            if path.is_file() and path.suffix.lower() not in {".md", ".canvas"}:
                try:
                    rel = path.relative_to(vault.root).as_posix()
                except ValueError:
                    continue
                if rel.split("/", 1)[0] in {".git", ".obsidian", ".knowledgeos"}:
                    continue
                index.attachments.add(rel.casefold())
                index.attachments.add(path.name.casefold())
                index.attachments.add(Path(rel).with_suffix("").as_posix().casefold())
                index.attachments.add(path.stem.casefold())
        return index

    def exists(self, target: str) -> bool:
        normalised = target.strip().replace("\\", "/").lstrip("/")
        if not normalised:
            return False
        candidates = {normalised.casefold(), normalised.removesuffix(".md").casefold()}
        if normalised in self.paths or normalised.casefold() in self.paths:
            return True
        if candidates & self.stems or candidates & self.titles or candidates & self.aliases:
            return True
        if candidates & self.attachments:
            return True
        # Obsidian also resolves a path suffix (e.g. [[concepts/foo]] for 10_Agent/wiki/concepts/foo.md).
        for path in self.paths:
            if path.endswith("/" + normalised.casefold()) or path.endswith(
                "/" + normalised.removesuffix(".md").casefold()
            ):
                return True
        return False

    def resolve(self, target: str) -> str | None:
        normalised = target.strip().replace("\\", "/").lstrip("/")
        folded = normalised.casefold()
        for candidate in (folded, folded.removesuffix(".md")):
            if candidate in self.paths:
                for path in self.paths:
                    if path == candidate or path == candidate + ".md":
                        return path
        return None


def extract_links(text: str) -> list[str]:
    """Extract wikilink targets, ignoring fenced code blocks and inline code."""
    text = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
    text = re.sub(r"`[^`\n]*`", "", text)
    links: list[str] = []
    for match in WIKILINK_RE.finditer(text):
        target = match.group(1).strip()
        # Markdown tables escape the alias separator as ``\|``; the trailing
        # backslash is not part of the target.
        target = target.rstrip("\\").strip()
        if target:
            links.append(target)
    return links


def _document_paths(
    vault: Vault,
    regions: Sequence[str],
    *,
    include_meta: bool,
    include_templates: bool,
) -> Iterable[Path]:
    for path in vault.iter_markdown(regions):
        rel = path.relative_to(vault.root)
        parts = rel.parts
        lower = path.name.lower()
        if not include_meta and lower in META_FILES:
            continue
        if not include_templates and "templates" in parts:
            continue
        if not include_templates and "reports" in parts:
            continue
        yield path


def _summary(document: Document, limit: int = 120) -> str:
    for line in document.body.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith(("#", "|", "```", ">", "-", "*", "<!--")):
            continue
        text = re.sub(r"\[\[([^\]|]+)\|([^\]]+)\]\]", r"\2", stripped)
        text = re.sub(r"\[\[([^\]]+)\]\]", r"\1", text)
        text = re.sub(r"[*_`]", "", text)
        if text:
            return text[:limit].strip()
    return ""


def _snippet(body: str, terms: Sequence[str], width: int = 90) -> str:
    # Headings repeat the title and make poor context windows; search body prose first.
    prose = "\n".join(line for line in body.splitlines() if not line.lstrip().startswith("#"))
    flat = re.sub(r"\s+", " ", prose).strip() or re.sub(r"\s+", " ", body).strip()
    lowered = flat.casefold()
    position = -1
    for term in terms:
        position = lowered.find(term.casefold())
        if position >= 0:
            break
    if position < 0:
        return flat[: width * 2].strip()
    start = max(0, position - width // 2)
    end = min(len(flat), position + width)
    prefix = "…" if start > 0 else ""
    suffix = "…" if end < len(flat) else ""
    return f"{prefix}{flat[start:end].strip()}{suffix}"


def _query_terms(query: str) -> list[str]:
    terms = [term for term in re.split(r"\s+", query.strip()) if term]
    return terms[:12]


def search(
    vault: Vault,
    query: str,
    *,
    regions: Sequence[str] | None = None,
    types: Sequence[str] | None = None,
    tags: Sequence[str] | None = None,
    statuses: Sequence[str] | None = None,
    limit: int | None = None,
    include_meta: bool = False,
) -> list[SearchHit]:
    query = query.strip()
    if not query:
        raise ValueError("Query must not be empty.")
    terms = _query_terms(query)
    regions = list(regions or DEFAULT_REGIONS)
    type_filter = {value.lower() for value in types or []}
    tag_filter = {value.lower().lstrip("#") for value in tags or []}
    status_filter = {value.lower() for value in statuses or []}
    hits: list[SearchHit] = []

    for path in _document_paths(vault, regions, include_meta=include_meta, include_templates=False):
        try:
            document = read_document(path, vault.root)
        except (OSError, UnicodeDecodeError):
            continue
        data = document.frontmatter
        note_type = str(data.get("type", "") or "")
        status = str(data.get("status", "") or "")
        doc_tags = [str(tag) for tag in data.get("tags", [])] if isinstance(data.get("tags"), list) else []
        if type_filter and note_type.lower() not in type_filter:
            continue
        if status_filter and status.lower() not in status_filter:
            continue
        if tag_filter and not tag_filter.issubset({tag.casefold() for tag in doc_tags}):
            continue

        title = document.title
        aliases = [str(alias) for alias in data.get("aliases", [])] if isinstance(data.get("aliases"), list) else []
        headings = [match.group(1) for match in HEADING_RE.finditer(document.body)]
        body = document.body
        body_lower = body.casefold()
        title_lower = title.casefold()
        aliases_lower = [alias.casefold() for alias in aliases]
        tags_lower = [tag.casefold() for tag in doc_tags]

        score = 0
        matched: list[str] = []
        for term in terms:
            folded = term.casefold()
            if folded == title_lower:
                score += 120
                matched.append("title=exact")
            elif title_lower.startswith(folded):
                score += 70
                matched.append("title=prefix")
            elif folded in title_lower:
                score += 45
                matched.append("title")
            if any(folded == alias for alias in aliases_lower):
                score += 90
                matched.append("alias=exact")
            elif any(folded in alias for alias in aliases_lower):
                score += 40
                matched.append("alias")
            if any(folded == tag for tag in tags_lower):
                score += 55
                matched.append("tag")
            elif any(folded in tag for tag in tags_lower):
                score += 25
                matched.append("tag=partial")
            if any(folded in heading.casefold() for heading in headings):
                score += 25
                matched.append("heading")
            occurrences = body_lower.count(folded)
            if occurrences:
                score += min(48, 8 + int(math.log2(occurrences + 1) * 10))
                matched.append(f"body×{occurrences}")
            if folded in document.rel.casefold():
                score += 10
                matched.append("path")

        if score <= 0:
            continue
        if status == "verified":
            score += 8
        elif status == "archived":
            score -= 20
        if data.get("confidence") == "high":
            score += 3
        hits.append(
            SearchHit(
                rel=document.rel,
                title=title,
                score=score,
                note_type=note_type,
                status=status,
                updated=str(data.get("updated", "") or ""),
                tags=doc_tags,
                snippet=_snippet(body, terms),
                matched=sorted(set(matched)),
            )
        )

    hits.sort(key=lambda hit: (-hit.score, hit.rel))
    effective_limit = limit if limit is not None else vault.config.max_results
    return hits[: max(1, effective_limit)]


def related_notes(vault: Vault, rel: str, limit: int = 10) -> list[str]:
    """Return outgoing links of a note (useful for graph inspection)."""
    document = read_document(vault.resolve(rel), vault.root)
    links = extract_links(document.body)
    unique: list[str] = []
    for link in links:
        if link not in unique:
            unique.append(link)
    return unique[:limit]
