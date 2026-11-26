"""Configuration loading and vault discovery.

Precedence for the vault path:
1. explicit ``--vault`` argument,
2. ``KNOWLEDGEOS_VAULT`` environment variable,
3. the current directory or one of its parents containing ``.knowledgeos/config.toml``,
4. the current directory or one of its parents that looks like a KnowledgeOS vault.

Configuration file precedence:
1. explicit ``--config`` / ``KNOWLEDGEOS_CONFIG``,
2. ``<vault>/.knowledgeos/config.toml``,
3. built-in defaults.
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any

from .layout import Layout, detect_layout

from .errors import ConfigError, VaultNotFoundError, VaultStructureError

try:  # Python 3.11+
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - exercised on Python 3.10 only
    try:
        import tomli as tomllib  # type: ignore[no-redef]
    except ModuleNotFoundError as exc:  # pragma: no cover
        raise ConfigError(
            "Python 3.10 requires the 'tomli' package: pip install tomli"
        ) from exc

CONFIG_DIR = ".knowledgeos"
CONFIG_FILE = "config.toml"
DEFAULT_AGENT_ID = "agent"

_AGENT_ID_RE = re.compile(r"^[a-z0-9][a-z0-9._-]{0,63}$")
_TOP_LEVEL_DIRS = {
    "human": "00_Human",
    "agent": "10_Agent",
    "exchange": "20_Exchange",
    "system": "30_System",
    "archive": "90_Archive",
}
_REQUIRED_DIRS = ("human", "agent", "exchange", "system")


@dataclass(frozen=True)
class Config:
    """Resolved configuration for one vault."""

    vault: Path
    agent_id: str = DEFAULT_AGENT_ID
    name: str = ""
    human_dir: str = "00_Human"
    agent_dir: str = "10_Agent"
    exchange_dir: str = "20_Exchange"
    system_dir: str = "30_System"
    archive_dir: str = "90_Archive"
    raw_subdir: str = "raw"
    wiki_subdir: str = "wiki"
    language: str = "en"
    max_results: int = 20
    require_write_request: bool = True
    lock_timeout: float = 10.0
    lock_stale_after: float = 300.0
    config_path: Path | None = None
    layout: Layout = Layout()

    # -- derived helpers -------------------------------------------------
    @property
    def human_path(self) -> Path:
        return self.vault / self.human_dir

    @property
    def agent_path(self) -> Path:
        return self.vault / self.agent_dir

    @property
    def raw_path(self) -> Path:
        return self.agent_path / self.raw_subdir

    @property
    def wiki_path(self) -> Path:
        return self.agent_path / self.wiki_subdir

    @property
    def exchange_path(self) -> Path:
        return self.vault / self.exchange_dir

    @property
    def system_path(self) -> Path:
        return self.vault / self.system_dir

    @property
    def archive_path(self) -> Path:
        return self.vault / self.archive_dir

    @property
    def write_requests_path(self) -> Path:
        return self.exchange_path / self.layout.path("20_Exchange/write-requests").name

    @property
    def index_path(self) -> Path:
        return self.wiki_path / self.layout.path("10_Agent/wiki/index.md").name

    @property
    def log_path(self) -> Path:
        return self.wiki_path / self.layout.path("10_Agent/wiki/log.md").name

    @property
    def schema_path(self) -> Path:
        return self.system_path.joinpath(*self.layout.path("30_System/schemas/frontmatter.schema.json").parts[1:])

    @property
    def gitignore_path(self) -> Path:
        return self.vault / ".gitignore"

    def with_overrides(
        self,
        *,
        agent_id: str | None = None,
        name: str | None = None,
        language: str | None = None,
    ) -> "Config":
        updates: dict[str, Any] = {}
        if agent_id is not None:
            updates["agent_id"] = normalize_agent_id(agent_id)
        if name is not None:
            updates["name"] = name
        if language is not None:
            updates["language"] = language
        return replace(self, **updates) if updates else self

    def region_dirs(self) -> dict[str, str]:
        return {
            "human": self.human_dir,
            "agent": self.agent_dir,
            "exchange": self.exchange_dir,
            "system": self.system_dir,
            "archive": self.archive_dir,
        }


def normalize_agent_id(value: str) -> str:
    value = (value or "").strip().lower().replace(" ", "-")
    if not value:
        raise ConfigError("Agent id must not be empty.")
    if not _AGENT_ID_RE.match(value):
        raise ConfigError(
            "Agent id must match ^[a-z0-9][a-z0-9._-]{0,63}$ "
            f"(received: {value!r})."
        )
    return value


def looks_like_vault(path: Path) -> bool:
    """A KnowledgeOS vault has the agent and system areas (paths configurable)."""
    if not path.is_dir():
        return False
    layout = detect_layout(path)
    markers = [
        path / layout.path("10_Agent"),
        path / layout.path("30_System"),
        path / "AGENTS.md",
    ]
    return all(marker.exists() for marker in markers)


def _discover_from(start: Path) -> Path | None:
    try:
        current = start.resolve()
    except OSError:
        current = start
    for candidate in (current, *current.parents):
        if (candidate / CONFIG_DIR / CONFIG_FILE).is_file():
            return candidate
        if looks_like_vault(candidate):
            return candidate
    return None


def discover_vault(start: Path | str | None = None) -> Path:
    """Locate a vault without requiring a config file."""
    env = os.environ.get("KNOWLEDGEOS_VAULT", "").strip()
    if env:
        candidate = Path(env).expanduser()
        if not candidate.is_dir():
            raise VaultNotFoundError(f"KNOWLEDGEOS_VAULT does not exist: {candidate}")
        return candidate.resolve()

    root = Path(start).expanduser() if start else Path.cwd()
    found = _discover_from(root)
    if found is None:
        raise VaultNotFoundError(
            "No KnowledgeOS vault found. Pass --vault PATH, set KNOWLEDGEOS_VAULT, "
            "or run `knowledgeos init <path>` to create one."
        )
    return found


def default_config(vault: Path | str) -> Config:
    return config_from_data(Path(vault).expanduser().resolve(), {})


def _read_toml(path: Path) -> dict[str, Any]:
    try:
        with path.open("rb") as handle:
            return tomllib.load(handle)
    except OSError as exc:
        raise ConfigError(f"Cannot read config file {path}: {exc}") from exc
    except tomllib.TOMLDecodeError as exc:
        raise ConfigError(f"Invalid TOML in {path}: {exc}") from exc


def _section(data: dict[str, Any], key: str) -> dict[str, Any]:
    value = data.get(key, {})
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise ConfigError(f"Config section [{key}] must be a table.")
    return value


def config_from_data(vault: Path, data: dict[str, Any], source: Path | None = None) -> Config:
    vault_cfg = _section(data, "vault")
    agent_cfg = _section(data, "agent")
    paths_cfg = _section(data, "paths")
    search_cfg = _section(data, "search")
    lock_cfg = _section(data, "locks")

    name = str(vault_cfg.get("name", "") or "")
    language = str(vault_cfg.get("language", "en") or "en")
    if language not in {"en", "zh-CN", "zh"}:
        language = "en"
    agent_id = normalize_agent_id(str(agent_cfg.get("id", DEFAULT_AGENT_ID)))

    resolved: dict[str, str] = {}
    layout = detect_layout(vault)
    for key, default in _TOP_LEVEL_DIRS.items():
        default = layout.path(default).name
        value = str(paths_cfg.get(key, default) or default).strip().strip("/\\")
        if not value or value in {".", ".."} or "/" in value or "\\" in value:
            raise ConfigError(f"paths.{key} must be a single top-level directory name.")
        if value.startswith("."):
            raise ConfigError(f"paths.{key} must not be a hidden directory.")
        resolved[key] = value

    try:
        max_results = int(search_cfg.get("max_results", 20))
        lock_timeout = float(lock_cfg.get("timeout_seconds", 10.0))
        lock_stale = float(lock_cfg.get("stale_after_seconds", 300.0))
    except (TypeError, ValueError) as exc:
        raise ConfigError(f"Invalid numeric config value: {exc}") from exc

    return Config(
        vault=vault.resolve(),
        agent_id=agent_id,
        name=name,
        human_dir=resolved["human"],
        agent_dir=resolved["agent"],
        exchange_dir=resolved["exchange"],
        system_dir=resolved["system"],
        archive_dir=resolved["archive"],
        language=language,
        max_results=max(1, min(max_results, 500)),
        require_write_request=bool(agent_cfg.get("require_write_request", True)),
        lock_timeout=max(0.0, lock_timeout),
        lock_stale_after=max(5.0, lock_stale),
        config_path=source,
        layout=layout,
        raw_subdir=layout.path("10_Agent/raw").name,
        wiki_subdir=layout.wiki.name,
    )


def load_config(
    vault: Path | str | None = None,
    config_path: Path | str | None = None,
    agent_id: str | None = None,
) -> Config:
    """Load configuration, discovering the vault when not given."""
    env_config = os.environ.get("KNOWLEDGEOS_CONFIG", "").strip()
    explicit_config = config_path or (env_config or None)

    if vault is not None:
        root = Path(vault).expanduser()
    elif explicit_config:
        config_file = Path(explicit_config).expanduser()
        root = config_file.parent.parent if config_file.parent.name == CONFIG_DIR else config_file.parent
    else:
        root = discover_vault()

    if not root.exists():
        raise VaultNotFoundError(f"Vault directory does not exist: {root}")
    if not root.is_dir():
        raise VaultStructureError(f"Vault path is not a directory: {root}")
    root = root.resolve()

    candidate = Path(explicit_config).expanduser() if explicit_config else root / CONFIG_DIR / CONFIG_FILE
    if explicit_config and not candidate.is_file():
        raise ConfigError(f"Config file not found: {candidate}")

    if candidate.is_file():
        config = config_from_data(root, _read_toml(candidate), candidate)
    else:
        if not looks_like_vault(root):
            raise VaultStructureError(
                f"{root} does not look like a KnowledgeOS vault (missing "
                 "standard Agent/System directories or AGENTS.md). "
                "Use `knowledgeos init --help` to install the framework."
            )
        config = default_config(root)

    env_agent = os.environ.get("KNOWLEDGEOS_AGENT", "").strip()
    effective_agent = agent_id or (env_agent or None)
    if effective_agent:
        config = config.with_overrides(agent_id=effective_agent)
    return config


def write_default_config(vault: Path, *, name: str = "", agent_id: str = DEFAULT_AGENT_ID) -> Path:
    """Write ``.knowledgeos/config.toml`` only if it does not exist."""
    from .errors import PermissionDenied as LegacyWriteDenied
    raise LegacyWriteDenied("LEGACY_WRITE_DISABLED: use the Broker-backed client")
    target = vault / CONFIG_DIR / CONFIG_FILE
    if target.exists():
        return target
    target.parent.mkdir(parents=True, exist_ok=True)
    agent_id = normalize_agent_id(agent_id)
    safe_name = (name or vault.name or "KnowledgeOS Vault").replace('"', "'")
    content = f"""# KnowledgeOS local configuration. Keep this file out of version control.
# Full reference: docs/configuration.md

[vault]
name = "{safe_name}"
language = "en"

[agent]
id = "{agent_id}"
# Human changes are proposals for manual application.
require_write_request = true

[paths]
human = "00_Human"
agent = "10_Agent"
exchange = "20_Exchange"
system = "30_System"
archive = "90_Archive"

[search]
max_results = 20

[locks]
timeout_seconds = 10
stale_after_seconds = 300
"""
    target.write_text(content, encoding="utf-8", newline="\n")
    return target
