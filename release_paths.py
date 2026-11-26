"""Publication-safe configuration for the local protected-vault guard."""

import os
from pathlib import Path


def protected_vault() -> Path:
    value = os.environ.get("KNOWLEDGEOS_PROTECTED_VAULT")
    if not value or not Path(value).is_absolute():
        raise ValueError("Set KNOWLEDGEOS_PROTECTED_VAULT to the existing protected vault path before enabling writes")
    return Path(value).resolve(strict=True)
