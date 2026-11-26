"""Typed errors with stable CLI exit codes."""

from __future__ import annotations


class KnowledgeOSError(Exception):
    """Base error. Exit code 1 (general failure)."""

    exit_code = 1


class ConfigError(KnowledgeOSError):
    """Missing or invalid configuration. Exit code 2."""

    exit_code = 2


class VaultNotFoundError(ConfigError):
    """No KnowledgeOS vault could be located."""


class VaultStructureError(ConfigError):
    """A directory exists but does not look like a KnowledgeOS vault."""


class PathSecurityError(KnowledgeOSError):
    """A path escaped the vault or crossed a symlink/junction boundary. Exit code 3."""

    exit_code = 3


class PermissionDenied(KnowledgeOSError):
    """The policy engine refused the operation. Exit code 3."""

    exit_code = 3


class ValidationError(KnowledgeOSError):
    """Input or note validation failed. Exit code 1."""

    exit_code = 1


class ConflictError(KnowledgeOSError):
    """A file already exists and overwriting was not explicitly requested. Exit code 2."""

    exit_code = 2
