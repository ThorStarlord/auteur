"""Adapters for using pack priors in existing Story Discovery artifacts."""
from __future__ import annotations

from typing import Any

from .composition import compose_packs
from .tutor import tutor_recommend
from .tutor import tutorize_diagnostic


def build_story_design_context(pack_ids: list[str] | None) -> dict[str, Any] | None:
    """Return serializable derived context, or None for legacy discovery."""
    if not pack_ids:
        return None
    return compose_packs(pack_ids).model_dump(mode="json")


def build_discovery_tutor_guidance(pack_ids: list[str] | None, *, premise: str, decision: str = "next creative decision") -> dict[str, Any] | None:
    if not pack_ids:
        return None
    return tutor_recommend(pack_ids, premise=premise, decision=decision).model_dump(mode="json")


def build_diagnostic_tutor_guidance(diagnostic: object, *, story_context: str = "this story") -> dict[str, Any]:
    return tutorize_diagnostic(diagnostic, story_context=story_context).model_dump(mode="json")
