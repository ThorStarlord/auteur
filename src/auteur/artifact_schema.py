"""Shared compatibility guard for versioned YAML/JSON artifact envelopes."""

from __future__ import annotations

from typing import Any, Mapping

CURRENT_ARTIFACT_SCHEMA = 1


def require_supported_schema(data: Mapping[str, Any], *, current: int = CURRENT_ARTIFACT_SCHEMA) -> int:
    """Return the artifact schema version or fail closed for future versions."""
    version = data.get("schema_version", current)
    if isinstance(version, bool) or not isinstance(version, int) or version < 1:
        raise ValueError(f"invalid schema_version: {version!r}")
    if version > current:
        raise ValueError(f"unsupported schema_version: {version}; current is {current}")
    return version
