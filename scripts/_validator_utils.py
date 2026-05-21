"""Shared utility functions for artifact validators.

All functions are pure (no side effects, no CLI). Importable by any validator.
"""

import os
import re

import yaml


def format_error(code: str, message: str) -> str:
    """Format a validation error as 'CODE: message'."""
    return f"{code}: {message}"


def load_yaml(path: str) -> dict | None:
    """Load and parse a YAML file. Returns None if the file is missing."""
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def resolve_repo_root(given: str, script_dir: str) -> str:
    """Resolve --repo-root argument relative to the script directory."""
    if os.path.isabs(given):
        return given
    return os.path.normpath(os.path.join(script_dir, given))


def load_weakness_types(repo_root: str) -> list[str]:
    """Parse bolded terms from weakness-types.md reference file."""
    path = os.path.join(repo_root, "skills", "repo-sensemaker", "references", "weakness-types.md")
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as f:
        return re.findall(r"\*\*(.+?)\*\*", f.read())


def _registry_path(repo_root: str, filename: str) -> str:
    """Build a path to a file in the workflow-orchestrator references directory."""
    return os.path.join(repo_root, "skills", "workflow-orchestrator", "references", filename)


def load_workflow_registry(repo_root: str) -> dict | None:
    """Load workflow-registry.yaml from the repo."""
    return load_yaml(_registry_path(repo_root, "workflow-registry.yaml"))


def load_artifact_contracts(repo_root: str) -> dict | None:
    """Load artifact-contracts.yaml from the repo."""
    return load_yaml(_registry_path(repo_root, "artifact-contracts.yaml"))


def load_skill_registry(repo_root: str) -> dict | None:
    """Load skill-registry.yaml from the repo."""
    return load_yaml(_registry_path(repo_root, "skill-registry.yaml"))
