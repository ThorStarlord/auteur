"""Bounded causal-analysis evidence for Story Discovery.

F3 treats causal analysis as derived recommendation evidence. It is deliberately
separate from canonical StoryIdentity, candidate self-advocacy, and artistic
quality scoring.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any, Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field, field_validator

from auteur.llm import LLMRequest


_CAUSAL_PROFILER_SYSTEM = """You are Auteur's bounded narrative-causality profiler.

Describe the causal mechanics implied by one Story Discovery candidate. This is
not a quality judgment and not a recommendation. Use only the supplied bounded
story evidence and prior author intent. Do not reward complexity, novelty,
length, confidence, labels, or rhetoric.

Focus on what would materially change the major scenes the author writes:
- primary causal strategy;
- causal ownership;
- recurring external action pattern;
- pressure system;
- reversal mechanics;
- climax mechanic;
- representative scene families.

If the evidence does not support a field, use null for a scalar, an empty list
for a list, and record the gap in evidence_gaps. Do not invent missing mechanics.

Return JSON only with exactly these keys:
- primary_strategy
- causal_owner
- external_action_pattern
- pressure_system
- reversal_mechanics
- climax_mechanic
- scene_families
- evidence_gaps
"""


class CausalProfile(BaseModel):
    """Derived description of the causal mechanics implied by one candidate."""

    model_config = ConfigDict(extra="forbid")

    primary_strategy: str | None
    causal_owner: str | None
    external_action_pattern: list[str]
    pressure_system: str | None
    reversal_mechanics: list[str]
    climax_mechanic: str | None
    scene_families: list[str]
    evidence_gaps: list[str]

    @field_validator(
        "primary_strategy",
        "causal_owner",
        "pressure_system",
        "climax_mechanic",
        mode="before",
    )
    @classmethod
    def _normalize_optional_text(cls, value: Any) -> Any:
        if value is None:
            return None
        if not isinstance(value, str):
            return value
        normalized = " ".join(value.split())
        return normalized or None

    @field_validator(
        "external_action_pattern",
        "reversal_mechanics",
        "scene_families",
        "evidence_gaps",
    )
    @classmethod
    def _normalize_text_lists(cls, values: list[str]) -> list[str]:
        normalized: list[str] = []
        for value in values:
            text = " ".join(value.split())
            if text:
                normalized.append(text)
        return normalized


class CausalProfileRecord(CausalProfile):
    """A causal profile plus a stable content-derived evidence key."""

    evidence_key: str = Field(min_length=8)


class CausalAnalysis(BaseModel):
    """Serializable F3 causal-analysis artifact block."""

    model_config = ConfigDict(extra="forbid")

    schema_version: Literal[1] = 1
    status: Literal["diagnostic_only"] = "diagnostic_only"
    profiles: dict[str, CausalProfileRecord]


def _model_dump(value: Any) -> dict[str, Any]:
    if value is None:
        return {}
    if hasattr(value, "model_dump"):
        return value.model_dump(mode="json")
    if isinstance(value, dict):
        return dict(value)
    return dict(vars(value))


def _bounded_contract_evidence(identity: Any) -> dict[str, Any] | None:
    contract = getattr(identity, "genre_contract_snapshot", None)
    if contract is None:
        return None
    data = _model_dump(contract)
    keep = (
        "genre_id",
        "display_name",
        "core_truth",
        "audience_product",
        "primary_excitement_beats",
        "scope_profile",
        "setup_contract",
    )
    return {key: data.get(key) for key in keep if key in data}


def bounded_causal_evidence(
    candidate_output: Any,
    premise_text: str,
    *,
    declared_author_intent: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Return only evidence allowed to influence the causal profiler.

    Candidate IDs, titles, lenses, confidence, summaries, tradeoffs, risks,
    best-for claims, why-this-is-best text, rejected directions, and generation
    provenance are intentionally absent.
    """

    identity = candidate_output.identity
    evidence: dict[str, Any] = {
        "premise": premise_text,
        "declared_author_intent": declared_author_intent,
        "candidate_commitments": {
            "core_answer": identity.core_answer,
            "central_engine": _model_dump(identity.central_engine),
            "story_type": _model_dump(identity.story_type),
            "not_this": list(getattr(identity, "not_this", [])),
            "open_questions": list(getattr(identity, "open_questions", [])),
            "author_overrides": list(getattr(identity, "author_overrides", [])),
            "hard_constraints": list(getattr(identity, "hard_constraints", [])),
            "genre_contract": _bounded_contract_evidence(identity),
        },
    }
    return evidence


def causal_evidence_key(evidence: dict[str, Any]) -> str:
    """Build a stable opaque key from bounded content evidence."""

    encoded = json.dumps(
        evidence,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()[:20]


def build_causal_profile_request(
    candidate_output: Any,
    premise_text: str,
    *,
    declared_author_intent: dict[str, Any] | None = None,
) -> tuple[LLMRequest, str]:
    """Build one content-bounded profiler request and its stable evidence key."""

    evidence = bounded_causal_evidence(
        candidate_output,
        premise_text,
        declared_author_intent=declared_author_intent,
    )
    evidence_key = causal_evidence_key(evidence)
    request = LLMRequest(
        system=_CAUSAL_PROFILER_SYSTEM,
        user=(
            "BOUNDED STORY EVIDENCE\n"
            + json.dumps(evidence, indent=2, ensure_ascii=False)
        ),
        max_tokens=1200,
        temperature=0.1,
        model=None,
    )
    return request, evidence_key


def parse_causal_profile(text: str) -> CausalProfile:
    """Parse strict profiler JSON and fail closed on malformed output."""

    match = re.search(r"\{.*\}", text.strip(), re.DOTALL)
    if not match:
        raise ValueError("causal profiler response did not contain a JSON object")
    try:
        payload = json.loads(match.group(0))
    except json.JSONDecodeError as exc:
        raise ValueError(f"causal profiler response contained invalid JSON: {exc}") from exc
    try:
        return CausalProfile.model_validate(payload)
    except Exception as exc:
        raise ValueError(f"causal profiler response failed schema validation: {exc}") from exc


def derive_causal_profile(
    client: Any,
    candidate_output: Any,
    premise_text: str,
    *,
    declared_author_intent: dict[str, Any] | None = None,
) -> CausalProfileRecord:
    """Derive one causal profile without mutating the candidate."""

    request, evidence_key = build_causal_profile_request(
        candidate_output,
        premise_text,
        declared_author_intent=declared_author_intent,
    )
    response = client.complete(request)
    profile = parse_causal_profile(response.text)
    return CausalProfileRecord(evidence_key=evidence_key, **profile.model_dump(mode="json"))


def derive_causal_profiles(
    client: Any,
    candidate_outputs: list[Any],
    premise_text: str,
    *,
    declared_author_intent: dict[str, Any] | None = None,
) -> dict[str, CausalProfileRecord]:
    """Derive profiles while keeping candidate IDs as traceability labels only."""

    profiles: dict[str, CausalProfileRecord] = {}
    for candidate_output in candidate_outputs:
        profiles[candidate_output.candidate_id] = derive_causal_profile(
            client,
            candidate_output,
            premise_text,
            declared_author_intent=declared_author_intent,
        )
    return profiles


def causal_analysis_payload(
    profiles: dict[str, CausalProfileRecord],
) -> dict[str, Any]:
    return CausalAnalysis(profiles=profiles).model_dump(mode="json")


def persist_causal_analysis(
    output_dir: Path,
    profiles: dict[str, CausalProfileRecord],
    *,
    artifact_names: tuple[str, ...] = ("discovery_report.yaml",),
) -> None:
    """Persist diagnostic causal evidence without touching candidate Identity YAML."""

    payload = causal_analysis_payload(profiles)
    for artifact_name in artifact_names:
        path = output_dir / artifact_name
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        data["causal_analysis"] = payload
        path.write_text(
            yaml.safe_dump(data, sort_keys=False, allow_unicode=True),
            encoding="utf-8",
        )
