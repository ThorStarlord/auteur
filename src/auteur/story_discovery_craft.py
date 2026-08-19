"""Grounded craft-impact analysis for Story Discovery.

F4 consumes qualified F3 causal profiles and explains how choosing one engine over
another changes the actual writing problem. Analysis remains advisory and
non-canonical.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field, field_validator

from auteur.llm import LLMRequest
from auteur.story_discovery_causality import CausalProfileRecord


_CRAFT_IMPACT_SYSTEM = """You are Auteur's bounded creative-writing architecture explainer.

Compare one recommended primary engine with one alternative using only the
supplied author intent, StoryIdentity commitments, and qualified causal profiles.
Explain what choosing the alternative would change in the actual craft of the
story. This is not a quality score and not a request to advocate for either
candidate.

Keep these layers distinct:
- causal strategy / causal ownership;
- external actions;
- pressure system and scene families;
- story texture / aesthetic emphasis;
- reader experience;
- thematic consequence.

Reader experience is hierarchical. The primary emotional promise governs;
secondary emotions may support or contrast with it; trajectory describes change
over time. Do not invent secondary emotions or architecture preferences that were
not explicitly supplied.

Architecture preferences are authorial architecture constraints, not emotions.
Maximalist + mixed causation may support multiple compatible mechanisms, but
primary_with_layers still requires one legible governing engine.

If evidence is insufficient, use null/empty values and record the gap rather than
inventing a scene, feeling, theme, or composition claim.

Return JSON only with exactly these keys:
- craft_layers_changed
- causal_ownership_shift
- external_action_shift
- scene_family_shift
- pressure_texture_shift
- reader_experience_shift
- thematic_effect
- gain
- give_up
- composability
- composition_note
- primary_risk
- evidence_gaps
"""

CraftLayer = Literal[
    "causal_strategy",
    "causal_ownership",
    "external_action",
    "pressure_system",
    "scene_families",
    "story_texture",
    "reader_experience",
    "theme",
]
Composability = Literal[
    "compatible_as_secondary",
    "requires_reframing",
    "mutually_exclusive_with_primary",
    "uncertain",
]
PrimaryPromiseEffect = Literal[
    "preserved",
    "preserved_but_reweighted",
    "strengthened",
    "weakened",
    "threatened",
    "changed",
    "unknown",
]


class ExternalActionShift(BaseModel):
    model_config = ConfigDict(extra="forbid")

    add_or_emphasize: list[str]
    de_emphasize: list[str]


class ReaderExperienceShift(BaseModel):
    model_config = ConfigDict(extra="forbid")

    primary_promise_effect: PrimaryPromiseEffect
    secondary_palette_effect: list[str]
    trajectory_effect: str | None


class CraftImpact(BaseModel):
    """Derived craft consequence of choosing an alternative engine."""

    model_config = ConfigDict(extra="forbid")

    craft_layers_changed: list[CraftLayer]
    causal_ownership_shift: str | None
    external_action_shift: ExternalActionShift
    scene_family_shift: list[str]
    pressure_texture_shift: str | None
    reader_experience_shift: ReaderExperienceShift
    thematic_effect: str | None
    gain: str | None
    give_up: str | None
    composability: Composability
    composition_note: str | None
    primary_risk: str | None
    evidence_gaps: list[str]

    @field_validator("craft_layers_changed")
    @classmethod
    def _dedupe_layers(cls, values: list[CraftLayer]) -> list[CraftLayer]:
        return list(dict.fromkeys(values))


class CraftImpactRecord(CraftImpact):
    """Craft impact with traceability restored after content-bounded analysis."""

    primary_candidate_id: str
    compared_candidate_id: str
    primary_evidence_key: str = Field(min_length=8)
    compared_evidence_key: str = Field(min_length=8)


class CraftAnalysis(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: Literal[1] = 1
    status: Literal["diagnostic_only", "complete"] = "diagnostic_only"
    primary_candidate_id: str
    impacts: dict[str, CraftImpactRecord]


def _dump(value: Any) -> dict[str, Any]:
    if value is None:
        return {}
    if hasattr(value, "model_dump"):
        return value.model_dump(mode="json")
    if isinstance(value, dict):
        return dict(value)
    return dict(vars(value))


def _candidate_craft_commitments(candidate_output: Any) -> dict[str, Any]:
    """Candidate commitments allowed into the explainer; no self-advocacy."""

    identity = candidate_output.identity
    return {
        "core_answer": identity.core_answer,
        "central_engine": _dump(identity.central_engine),
        "story_type": _dump(identity.story_type),
        "target_experience": _dump(identity.target_experience),
        "not_this": list(getattr(identity, "not_this", [])),
        "open_questions": list(getattr(identity, "open_questions", [])),
        "author_overrides": list(getattr(identity, "author_overrides", [])),
        "hard_constraints": list(getattr(identity, "hard_constraints", [])),
    }


def build_craft_impact_request(
    primary_output: Any,
    alternative_output: Any,
    primary_profile: CausalProfileRecord,
    alternative_profile: CausalProfileRecord,
    premise_text: str,
    *,
    declared_author_intent: dict[str, Any] | None = None,
) -> LLMRequest:
    """Build a content-bounded winner/alternative craft explanation request."""

    evidence = {
        "premise": premise_text,
        "declared_author_intent": declared_author_intent,
        "primary": {
            "story_commitments": _candidate_craft_commitments(primary_output),
            "causal_profile": primary_profile.model_dump(mode="json"),
        },
        "alternative": {
            "story_commitments": _candidate_craft_commitments(alternative_output),
            "causal_profile": alternative_profile.model_dump(mode="json"),
        },
    }
    return LLMRequest(
        system=_CRAFT_IMPACT_SYSTEM,
        user="BOUNDED CRAFT EVIDENCE\n" + json.dumps(evidence, indent=2, ensure_ascii=False),
        max_tokens=1800,
        temperature=0.1,
        model=None,
    )


def parse_craft_impact(text: str) -> CraftImpact:
    match = re.search(r"\{.*\}", text.strip(), re.DOTALL)
    if not match:
        raise ValueError("craft-impact response did not contain a JSON object")
    try:
        payload = json.loads(match.group(0))
        return CraftImpact.model_validate(payload)
    except Exception as exc:
        raise ValueError(f"craft-impact response failed schema validation: {exc}") from exc


def derive_craft_impact(
    client: Any,
    primary_output: Any,
    alternative_output: Any,
    primary_profile: CausalProfileRecord,
    alternative_profile: CausalProfileRecord,
    premise_text: str,
    *,
    declared_author_intent: dict[str, Any] | None = None,
) -> CraftImpactRecord:
    request = build_craft_impact_request(
        primary_output,
        alternative_output,
        primary_profile,
        alternative_profile,
        premise_text,
        declared_author_intent=declared_author_intent,
    )
    response = client.complete(request)
    impact = parse_craft_impact(response.text)
    return CraftImpactRecord(
        **impact.model_dump(mode="json"),
        primary_candidate_id=primary_output.candidate_id,
        compared_candidate_id=alternative_output.candidate_id,
        primary_evidence_key=primary_profile.evidence_key,
        compared_evidence_key=alternative_profile.evidence_key,
    )


def derive_craft_impacts(
    client: Any,
    winner: str,
    candidate_outputs: list[Any],
    profiles: dict[str, CausalProfileRecord],
    premise_text: str,
    *,
    declared_author_intent: dict[str, Any] | None = None,
) -> CraftAnalysis:
    by_id = {candidate_output.candidate_id: candidate_output for candidate_output in candidate_outputs}
    if winner not in by_id:
        raise ValueError("craft analysis winner must be one of the surviving candidates")
    if set(by_id) != set(profiles):
        raise ValueError("craft analysis requires one causal profile per surviving candidate")

    primary = by_id[winner]
    impacts: dict[str, CraftImpactRecord] = {}
    for candidate_id, alternative in by_id.items():
        if candidate_id == winner:
            continue
        impacts[candidate_id] = derive_craft_impact(
            client,
            primary,
            alternative,
            profiles[winner],
            profiles[candidate_id],
            premise_text,
            declared_author_intent=declared_author_intent,
        )
    return CraftAnalysis(
        status="complete",
        primary_candidate_id=winner,
        impacts=impacts,
    )


def persist_craft_analysis(
    output_dir: Path,
    analysis: CraftAnalysis,
    *,
    artifact_names: tuple[str, ...] = ("discovery_report.yaml",),
) -> None:
    payload = analysis.model_dump(mode="json")
    for artifact_name in artifact_names:
        path = output_dir / artifact_name
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        data["craft_analysis"] = payload
        path.write_text(
            yaml.safe_dump(data, sort_keys=False, allow_unicode=True),
            encoding="utf-8",
        )
