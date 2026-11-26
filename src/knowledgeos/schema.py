"""YAML frontmatter parsing, rendering and JSON-Schema-style validation."""

from __future__ import annotations

import json
import re
import stat
from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path
from typing import Any, Iterable, Literal

from .errors import ValidationError
from .layout import Layout, detect_layout

TYPE_DIRS: dict[str, str] = {
    "concept": "concepts",
    "entity": "entities",
    "topic": "topics",
    "comparison": "comparisons",
    "synthesis": "synthesis",
    "project": "projects",
    "decision": "decisions",
}

AGENT_TYPES = tuple(TYPE_DIRS) + ("source",)
STATUSES = ("draft", "verified", "needs-review", "outdated", "archived")
OWNERS = ("agent", "human")
CONFIDENCE = ("high", "medium", "low")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
TAG_RE = re.compile(r"^[a-z0-9][a-z0-9/_-]*$")
AGENT_ID_RE = re.compile(r"^(human:[a-z0-9][a-z0-9._-]*|[a-z0-9][a-z0-9._-]*|unregistered:[a-z0-9][a-z0-9._-]*)$")
KEBAB_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")

FIELD_ORDER = (
    "title",
    "type",
    "owner",
    "created_by",
    "created",
    "updated",
    "status",
    "sources",
    "related",
    "tags",
    "aliases",
    "confidence",
    "review_after",
    "supersedes",
    "superseded_by",
)

BUILTIN_SCHEMA: dict[str, Any] = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "$id": "https://local.knowledgeos/schemas/frontmatter.schema.json",
    "title": "KnowledgeOS Agent Wiki frontmatter",
    "type": "object",
    "required": [
        "title",
        "type",
        "owner",
        "created_by",
        "created",
        "updated",
        "status",
        "sources",
        "related",
        "tags",
    ],
    "additionalProperties": True,
    "properties": {
        "title": {"type": "string", "minLength": 1},
        "type": {"type": "string", "enum": list(AGENT_TYPES)},
        "owner": {"type": "string", "enum": list(OWNERS)},
        "created_by": {
            "type": "string",
            "pattern": "^(human:[a-z0-9][a-z0-9._-]*|[a-z0-9][a-z0-9._-]*|unregistered:[a-z0-9][a-z0-9._-]*)$",
        },
        "created": {"type": "string", "pattern": "^[0-9]{4}-[0-9]{2}-[0-9]{2}$"},
        "updated": {"type": "string", "pattern": "^[0-9]{4}-[0-9]{2}-[0-9]{2}$"},
        "status": {"type": "string", "enum": list(STATUSES)},
        "sources": {"type": "array", "items": {"type": "string"}},
        "related": {"type": "array", "items": {"type": "string"}},
        "tags": {"type": "array", "items": {"type": "string", "pattern": "^[a-z0-9][a-z0-9/_-]*$"}},
        "aliases": {"type": "array", "items": {"type": "string"}},
        "confidence": {"type": "string", "enum": list(CONFIDENCE)},
        "review_after": {"type": "string", "pattern": "^[0-9]{4}-[0-9]{2}-[0-9]{2}$"},
        "supersedes": {"type": "array", "items": {"type": "string"}},
        "superseded_by": {"type": "string"},
    },
}


# ----------------------------------------------------------------------
# Frontmatter split / parse
# ----------------------------------------------------------------------
def split_frontmatter(text: str) -> tuple[str, str, bool]:
    """Return ``(frontmatter_text, body, found)`` without interpreting YAML."""
    if text.startswith("\ufeff"):
        text = text[1:]
    normalised = text.replace("\r\n", "\n").replace("\r", "\n")
    if not normalised.startswith("---\n"):
        return "", normalised, False
    closing = normalised.find("\n---", 4)
    if closing < 0:
        return "", normalised, False
    end = closing + 4
    # The closing marker must be a line of its own.
    tail = normalised[end:]
    if tail and not tail.startswith("\n"):
        return "", normalised, False
    block = normalised[4:closing]
    body = tail[1:] if tail.startswith("\n") else tail
    return block.strip("\n"), body, True


def _strip_comment(value: str) -> str:
    quote: str | None = None
    depth = 0
    for index, char in enumerate(value):
        if quote:
            if char == quote and (index == 0 or value[index - 1] != "\\"):
                quote = None
            continue
        if char in {'"', "'"}:
            quote = char
        elif char in "[{":
            depth += 1
        elif char in "]}":
            depth = max(0, depth - 1)
        elif char == "#" and depth == 0 and (index == 0 or value[index - 1] in " \t"):
            return value[:index].rstrip()
    return value.rstrip()


def _split_inline(value: str) -> list[str]:
    parts: list[str] = []
    current: list[str] = []
    quote: str | None = None
    depth = 0
    for char in value:
        if quote:
            current.append(char)
            if char == quote:
                quote = None
            continue
        if char in {'"', "'"}:
            quote = char
            current.append(char)
        elif char in "[{":
            depth += 1
            current.append(char)
        elif char in "]}":
            depth = max(0, depth - 1)
            current.append(char)
        elif char == "," and depth == 0:
            parts.append("".join(current).strip())
            current = []
        else:
            current.append(char)
    if "".join(current).strip():
        parts.append("".join(current).strip())
    return parts


def _unquote(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] == '"':
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value[1:-1]
    if len(value) >= 2 and value[0] == value[-1] == "'":
        return value[1:-1].replace("''", "'")
    return value


def _coerce_scalar(value: str) -> Any:
    value = _strip_comment(value).strip()
    if value == "":
        return ""
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        if not inner:
            return []
        return [_coerce_scalar(item) for item in _split_inline(inner)]
    if value.startswith("{") and value.endswith("}"):
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value
    lowered = value.lower()
    if lowered in {"true", "yes"}:
        return True
    if lowered in {"false", "no"}:
        return False
    if lowered in {"null", "~"}:
        return None
    if re.fullmatch(r"-?\d+", value):
        try:
            return int(value)
        except ValueError:
            pass
    if re.fullmatch(r"-?\d+\.\d+", value):
        try:
            return float(value)
        except ValueError:
            pass
    return _unquote(value)


def _fallback_yaml(text: str) -> dict[str, Any]:
    """Restricted YAML used when PyYAML is unavailable.

    Supports flat mappings, quoted/plain scalars, inline lists and block string lists.
    This is deliberately not a general YAML implementation.
    """
    result: dict[str, Any] = {}
    lines = text.splitlines()
    index = 0
    while index < len(lines):
        raw = lines[index]
        stripped = raw.strip()
        index += 1
        if not stripped or stripped.startswith("#"):
            continue
        if raw[:1] in " \t" or stripped.startswith("- "):
            raise ValidationError(
                f"Restricted YAML parser: unexpected indentation at line {index}: {raw!r}. "
                "Install PyYAML for full YAML support."
            )
        if ":" not in raw:
            raise ValidationError(f"Restricted YAML parser: expected 'key: value' at line {index}.")
        key, _, value = raw.partition(":")
        key = key.strip()
        if not re.fullmatch(r"[A-Za-z0-9_.-]+", key or ""):
            raise ValidationError(f"Restricted YAML parser: invalid key {key!r}.")
        value = value.strip()
        if value:
            result[key] = _coerce_scalar(value)
            continue
        items: list[Any] = []
        while index < len(lines):
            follow = lines[index]
            if not follow.strip() or follow.strip().startswith("#"):
                index += 1
                continue
            if follow.lstrip().startswith("- "):
                items.append(_coerce_scalar(follow.lstrip()[2:]))
                index += 1
                continue
            break
        result[key] = items if items else ""
    return result


def _normalise_yaml(value: Any) -> Any:
    """Make YAML-parsed values JSON-like; PyYAML turns dates into datetime objects."""
    if isinstance(value, dict):
        return {str(key): _normalise_yaml(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_normalise_yaml(item) for item in value]
    if isinstance(value, datetime):
        return value.date().isoformat() if value.time().isoformat() == "00:00:00" else value.isoformat(sep=" ")
    if isinstance(value, date):
        return value.isoformat()
    return value


def load_yaml(text: str) -> dict[str, Any]:
    if not text.strip():
        return {}
    try:
        import yaml  # type: ignore
    except ModuleNotFoundError:
        data = _fallback_yaml(text)
    else:
        try:
            data = yaml.safe_load(text)
        except yaml.YAMLError as exc:  # type: ignore[attr-defined]
            raise ValidationError(f"Invalid YAML frontmatter: {exc}") from exc
    if data is None:
        return {}
    if not isinstance(data, dict):
        raise ValidationError("Frontmatter must be a YAML mapping (key: value).")
    return {str(key): _normalise_yaml(value) for key, value in data.items()}


@dataclass
class Document:
    path: Path
    rel: str
    text: str
    frontmatter: dict[str, Any] = field(default_factory=dict)
    body: str = ""
    frontmatter_text: str = ""
    has_frontmatter: bool = False
    error: str | None = None

    @property
    def title(self) -> str:
        title = self.frontmatter.get("title")
        if isinstance(title, str) and title.strip():
            return title.strip()
        return self.path.stem

    @property
    def note_type(self) -> str:
        return str(self.frontmatter.get("type", "") or "")

    @property
    def status(self) -> str:
        return str(self.frontmatter.get("status", "") or "")


def parse_text(text: str, path: Path, rel: str) -> Document:
    block, body, found = split_frontmatter(text)
    document = Document(path=path, rel=rel, text=text, frontmatter_text=block, body=body, has_frontmatter=found)
    if not found:
        document.error = "Missing YAML frontmatter (the file must start with '---')."
        return document
    try:
        document.frontmatter = load_yaml(block)
    except ValidationError as exc:
        document.error = str(exc)
    return document


def read_document(path: Path, root: Path | None = None) -> Document:
    text = path.read_text(encoding="utf-8-sig")
    rel = path.relative_to(root).as_posix() if root else path.as_posix()
    return parse_text(text, path, rel)


# ----------------------------------------------------------------------
# Rendering
# ----------------------------------------------------------------------
_SAFE_PLAIN = re.compile(r"^[A-Za-z0-9_./+-]+$")


def _format_scalar(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if value is None:
        return '""'
    if isinstance(value, (int, float)):
        return str(value)
    text = str(value)
    if text == "":
        return '""'
    if _SAFE_PLAIN.match(text) and text.lower() not in {"true", "false", "null", "yes", "no"}:
        return text
    return json.dumps(text, ensure_ascii=False)


def _format_list(values: list[Any]) -> str:
    if not values:
        return "[]"
    scalars = [_format_scalar(value) for value in values]
    inline = "[" + ", ".join(scalars) + "]"
    if all(len(item) < 60 for item in scalars) and len(inline) <= 100:
        return inline
    return "\n" + "\n".join(f"  - {item}" for item in scalars)


def render_frontmatter(data: dict[str, Any]) -> str:
    """Render deterministic frontmatter, preserving unknown keys after known ones."""
    lines = ["---"]
    keys = [key for key in FIELD_ORDER if key in data]
    keys += [key for key in data if key not in FIELD_ORDER]
    for key in keys:
        value = data[key]
        if value is None:
            continue
        if isinstance(value, (list, tuple)):
            lines.append(f"{key}: {_format_list(list(value))}")
        else:
            lines.append(f"{key}: {_format_scalar(value)}")
    lines.append("---")
    return "\n".join(lines) + "\n"


def ensure_frontmatter(text: str, data: dict[str, Any]) -> str:
    block, body, found = split_frontmatter(text)
    if not found:
        return render_frontmatter(data) + "\n" + text.lstrip()
    return render_frontmatter(data) + "\n" + body


# ----------------------------------------------------------------------
# Validation
# ----------------------------------------------------------------------
@dataclass
class Issue:
    level: Literal["error", "warning", "info"]
    code: str
    message: str
    path: str = ""

    def as_dict(self) -> dict[str, str]:
        return {"level": self.level, "code": self.code, "message": self.message, "path": self.path}

    def __str__(self) -> str:
        prefix = {"error": "ERROR", "warning": "WARN ", "info": "INFO "}[self.level]
        return f"{prefix} [{self.code}] {self.path}: {self.message}" if self.path else f"{prefix} [{self.code}] {self.message}"


def _is_date(value: Any) -> bool:
    if not isinstance(value, str) or not DATE_RE.match(value):
        return False
    try:
        date.fromisoformat(value)
        return True
    except ValueError:
        return False


def load_schema(vault_root: Path | None = None, *, layout: Layout | None = None) -> dict[str, Any]:
    if vault_root:
        layout = layout or detect_layout(vault_root)
        path = vault_root / layout.path("30_System/schemas/frontmatter.schema.json")
        try:
            info = path.lstat()
            if (path.resolve(strict=True) == path.absolute() and stat.S_ISREG(info.st_mode)
                    and info.st_nlink == 1 and info.st_size <= 1024 * 1024
                    and not getattr(info, "st_file_attributes", 0) & stat.FILE_ATTRIBUTE_REPARSE_POINT):
                data = json.loads(path.read_text(encoding="utf-8-sig"))
                if isinstance(data, dict):
                    return data
        except (OSError, ValueError):
            pass
    return BUILTIN_SCHEMA


def validate_json_schema(data: Any, schema: dict[str, Any], prefix: str = "") -> list[tuple[str, str]]:
    """Small JSON Schema subset: type, required, enum, pattern, items, minLength."""
    problems: list[tuple[str, str]] = []
    location = prefix or "frontmatter"

    expected = schema.get("type")
    if expected == "object" and not isinstance(data, dict):
        return [(location, "must be an object")]
    if expected == "array" and not isinstance(data, list):
        return [(location, "must be an array")]
    if expected == "string" and not isinstance(data, str):
        return [(location, "must be a string")]

    if isinstance(data, dict):
        for key in schema.get("required", []):
            if key not in data:
                problems.append((f"{location}.{key}", "is required"))
        properties = schema.get("properties", {})
        required = set(schema.get("required", []))
        for key, subschema in properties.items():
            if key in data:
                # An empty string means "unset" for optional scalar fields such as review_after.
                if data[key] == "" and key not in required:
                    continue
                child = f"{location}.{key}" if prefix else key
                problems.extend(validate_json_schema(data[key], subschema, child))
        if schema.get("additionalProperties") is False:
            extras = set(data) - set(properties)
            for key in sorted(extras):
                problems.append((key, "is not allowed"))

    if "enum" in schema and data not in schema["enum"]:
        problems.append((location, f"must be one of {schema['enum']}"))
    if isinstance(data, str):
        if "minLength" in schema and len(data) < schema["minLength"]:
            problems.append((location, f"must be at least {schema['minLength']} characters"))
        if "pattern" in schema and not re.search(schema["pattern"], data):
            problems.append((location, f"does not match pattern {schema['pattern']}"))
    if isinstance(data, list) and "items" in schema:
        for index, item in enumerate(data):
            problems.extend(validate_json_schema(item, schema["items"], f"{location}[{index}]"))
    return problems


def validate_document(
    document: Document,
    *,
    schema: dict[str, Any] | None = None,
    check_location: bool = True,
    layout: Layout = Layout(),
) -> list[Issue]:
    issues: list[Issue] = []
    rel = document.rel

    def error(code: str, message: str) -> None:
        issues.append(Issue("error", code, message, rel))

    def warning(code: str, message: str) -> None:
        issues.append(Issue("warning", code, message, rel))

    if not document.has_frontmatter:
        error("frontmatter.missing", "Missing YAML frontmatter.")
        return issues
    if document.error:
        error("frontmatter.invalid", document.error)
        return issues
    data = document.frontmatter
    active_schema = schema or BUILTIN_SCHEMA

    for location, message in validate_json_schema(data, active_schema):
        error("schema.invalid", f"{location} {message}.")

    # Defensive checks beyond JSON Schema so the error messages are actionable.
    created = data.get("created")
    updated = data.get("updated")
    if _is_date(created) and _is_date(updated) and str(updated) < str(created):
        error("date.order", "'updated' is earlier than 'created'.")
    for key in ("created", "updated", "review_after"):
        value = data.get(key)
        if value not in (None, "") and not _is_date(value):
            error("date.format", f"'{key}' must be a real YAML string date in YYYY-MM-DD form (got {value!r}).")

    for key in ("sources", "related", "tags", "aliases", "supersedes"):
        value = data.get(key)
        if value is None:
            continue
        if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
            error("list.type", f"'{key}' must be a list of strings.")
        elif key in {"sources", "related"} and any(not item.strip() for item in value):
            warning("list.empty_item", f"'{key}' contains an empty entry.")

    tags = data.get("tags")
    if isinstance(tags, list):
        for tag in tags:
            if isinstance(tag, str) and tag and not TAG_RE.match(tag):
                error("tag.format", f"Tag {tag!r} must be lowercase and match [a-z0-9][a-z0-9/_-]*.")

    note_type = str(data.get("type", ""))
    if note_type == "source" and not data.get("sources"):
        warning("source.no_source", "A source page should point at its raw file or URL.")
    if data.get("status") == "verified" and not data.get("sources"):
        error("status.unsourced", "'status: verified' requires at least one source.")
    if data.get("status") == "outdated" and not (data.get("superseded_by") or data.get("sources")):
        warning("status.outdated", "'status: outdated' should explain what superseded it.")

    if check_location:
        parts = document.rel.split("/")
        if len(parts) >= 3 and parts[1] == layout.wiki.name:
            if data.get("owner") != "agent":
                error("owner.wiki", "Agent wiki pages must declare 'owner: agent'.")
            expected = TYPE_DIRS.get(note_type)
            if note_type and expected and len(parts) >= 4 and parts[2] != layout.path("10_Agent/wiki/" + expected).name:
                error(
                    "type.location",
                    f"Type {note_type!r} belongs in {layout.path('10_Agent/wiki/' + expected)}/.",
                )
            stem = Path(parts[-1]).stem
            if stem not in {"index", "log"} and not KEBAB_RE.match(stem):
                warning("filename.style", "Use ASCII kebab-case file names for wiki pages.")
        elif len(parts) >= 3 and parts[1] == layout.path("10_Agent/raw").name:
            if note_type == "source" and data.get("owner") != "agent":
                error("owner.raw", "Raw source notes must declare 'owner: agent'.")

    if not str(data.get("title", "")).strip():
        error("title.empty", "'title' must not be empty.")

    return issues


def validate_vault_notes(documents: Iterable[Document], schema: dict[str, Any] | None = None) -> list[Issue]:
    issues: list[Issue] = []
    for document in documents:
        issues.extend(validate_document(document, schema=schema))
    return issues


def today() -> str:
    return date.today().isoformat()


def now_stamp() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M")
