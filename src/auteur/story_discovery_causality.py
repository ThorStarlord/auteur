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

_CAUSAL_DIVERSITY_SYSTEM = """You are Auteur's bounded causal-diversity assessor.

Compare the supplied causal-profile pairs. This is not a story-quality ranking,
not a creativity score, and not a request to choose a winner. Decide only whether
choosing one profile instead of the other would materially change the major
external actions, recurring pressure, reversals, scene families, or climax
mechanic the author would write.

Classifications:
- distinct: material causal difference is supported;
- near_duplicate: differences are mostly framing/interpretation while the major
  acts, reversals, and climax remain substantially the same;
- uncertain: evidence is insufficient for a defensible causal-distinctness claim.

Do not treat different titles, themes, metaphors, aesthetic adjectives, target
emotion wording, length, or complexity as causal difference by themselves. Do
not use a numeric similarity or creativity score. Return one assessment for every
supplied pair and no others.

Return JSON only with exactly one top-level key, assessments. Each assessment
must contain exactly:
- left_evidence_key
- right_evidence_key
- classification
- shared_causal_mechanics
- material_differences
- scene_consequence
- rationale
"""

_CAUSAL_GENERATION_GUIDANCE = """CAUSAL DISTINCTNESS GUIDANCE
This candidate should imply a materially different story engine, not merely a
different theme, metaphor, aesthetic frame, or emotional label. Make the causal
strategy concrete enough that a later assessor can identify different:
- protagonist/ensemble verbs;
- causal owner;
- recurring pressure system;
- reversal mechanics;
- climax resolution mechanic;
- major scene families.
Do not claim that the candidate is unique or superior; demonstrate its mechanics
through StoryIdentity commitments.

"""

CausalStatus = Literal[
    "diagnostic_only",
    "qualified",
    "not_adjudicable_near_duplicate",
    "not_adjudicable_uncertain",
    "malformed_analysis",
    "not_applicable_single_survivor",
]
PairwiseClassification = Literal["distinct", "near_duplicate", "uncertain"]


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


class PairwiseAssessment(BaseModel):
    """Content-keyed semantic comparison of two derived causal profiles."""

    model_config = ConfigDict(extra="forbid")

    left_evidence_key: str = Field(min_length=8)
    right_evidence_key: str = Field(min_length=8)
    classification: PairwiseClassification
    shared_causal_mechanics: list[str]
    material_differences: list[str]
    scene_consequence: str | None
    rationale: str


class PairwiseAssessmentRecord(PairwiseAssessment):
    """Pairwise assessment with candidate IDs restored for artifact traceability."""

    left_candidate_id: str
    right_candidate_id: str


class _DiversityResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    assessments: list[PairwiseAssessment]


class CausalAnalysis(BaseModel):
    """Serializable F3 causal-analysis artifact block."""

    model_config = ConfigDict(extra="forbid")

    schema_version: Literal[1] = 1
    status: CausalStatus = "diagnostic_only"
    profiles: dict[str, CausalProfileRecord]
    pairwise_assessments: list[PairwiseAssessmentRecord] = Field(default_factory=list)


class CausalGuidanceClient:
    """Add F3 generation guidance without exposing other candidates to generation."""

    def __init__(self, delegate: Any):
        self._delegate = delegate

    def complete(self, request: LLMRequest):
        if "expert, opinionated narrative compiler" in request.system:
            request = request.model_copy(
                update={"user": _CAUSAL_GENERATION_GUIDANCE + request.user}
            )
        return self._delegate.complete(request)


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


def _profile_without_key(profile: CausalProfileRecord) -> dict[str, Any]:
    return profile.model_dump(mode="json", exclude={"evidence_key"})


def _expected_profile_pairs(
    profiles: dict[str, CausalProfileRecord],
) -> list[tuple[str, str]]:
    keys = [profile.evidence_key for profile in profiles.values()]
    if len(set(keys)) != len(keys):
        raise ValueError("causal evidence keys must be unique for semantic pair assessment")
    ordered = sorted(keys)
    return [
        (ordered[left], ordered[right])
        for left in range(len(ordered))
        for right in range(left + 1, len(ordered))
    ]


def build_causal_diversity_request(
    profiles: dict[str, CausalProfileRecord],
) -> tuple[LLMRequest, list[tuple[str, str]]]:
    """Build one stable set-level request covering every unordered profile pair."""

    if len(profiles) < 2:
        raise ValueError("causal diversity assessment requires at least two profiles")
    expected_pairs = _expected_profile_pairs(profiles)
    by_key = {profile.evidence_key: profile for profile in profiles.values()}
    pairs = [
        {
            "left_evidence_key": left,
            "right_evidence_key": right,
            "left_profile": _profile_without_key(by_key[left]),
            "right_profile": _profile_without_key(by_key[right]),
        }
        for left, right in expected_pairs
    ]
    request = LLMRequest(
        system=_CAUSAL_DIVERSITY_SYSTEM,
        user="CAUSAL PROFILE PAIRS\n" + json.dumps(pairs, indent=2, ensure_ascii=False),
        max_tokens=max(1400, 700 * len(expected_pairs)),
        temperature=0.1,
        model=None,
    )
    return request, expected_pairs


def parse_causal_diversity(
    text: str,
    expected_pairs: list[tuple[str, str]],
) -> list[PairwiseAssessment]:
    """Parse and verify complete pair coverage from the semantic assessor."""

    match = re.search(r"\{.*\}", text.strip(), re.DOTALL)
    if not match:
        raise ValueError("causal diversity response did not contain a JSON object")
    try:
        payload = json.loads(match.group(0))
        parsed = _DiversityResponse.model_validate(payload)
    except Exception as exc:
        raise ValueError(f"causal diversity response failed schema validation: {exc}") from exc

    expected = {tuple(sorted(pair)) for pair in expected_pairs}
    observed: list[tuple[str, str]] = [
        tuple(sorted((item.left_evidence_key, item.right_evidence_key)))
        for item in parsed.assessments
    ]
    if len(set(observed)) != len(observed):
        raise ValueError("causal diversity response contains duplicate pair assessments")
    if set(observed) != expected:
        raise ValueError("causal diversity response must cover exactly every expected pair")
    return parsed.assessments


def assess_causal_diversity(
    client: Any,
    profiles: dict[str, CausalProfileRecord],
) -> CausalAnalysis:
    """Assess semantic causal distinctness without assigning an artistic score."""

    if len(profiles) == 1:
        return CausalAnalysis(status="not_applicable_single_survivor", profiles=profiles)
    if len(profiles) < 1:
        raise ValueError("causal diversity assessment requires at least one profile")

    request, expected_pairs = build_causal_diversity_request(profiles)
    response = client.complete(request)
    assessments = parse_causal_diversity(response.text, expected_pairs)

    candidate_by_key = {
        profile.evidence_key: candidate_id
        for candidate_id, profile in profiles.items()
    }
    records: list[PairwiseAssessmentRecord] = []
    for assessment in assessments:
        left_id = candidate_by_key[assessment.left_evidence_key]
        right_id = candidate_by_key[assessment.right_evidence_key]
        records.append(
            PairwiseAssessmentRecord(
                **assessment.model_dump(mode="json"),
                left_candidate_id=left_id,
                right_candidate_id=right_id,
            )
        )

    classifications = {record.classification for record in records}
    if "near_duplicate" in classifications:
        status: CausalStatus = "not_adjudicable_near_duplicate"
    elif "uncertain" in classifications:
        status = "not_adjudicable_uncertain"
    else:
        status = "qualified"
    return CausalAnalysis(
        status=status,
        profiles=profiles,
        pairwise_assessments=records,
    )


def causal_analysis_payload(
    profiles: dict[str, CausalProfileRecord],
    *,
    status: CausalStatus = "diagnostic_only",
    pairwise_assessments: list[PairwiseAssessmentRecord] | None = None,
) -> dict[str, Any]:
    return CausalAnalysis(
        status=status,
        profiles=profiles,
        pairwise_assessments=pairwise_assessments or [],
    ).model_dump(mode="json")


def persist_causal_analysis(
    output_dir: Path,
    profiles: dict[str, CausalProfileRecord] | None = None,
    *,
    analysis: CausalAnalysis | None = None,
    artifact_names: tuple[str, ...] = ("discovery_report.yaml",),
) -> None:
    """Persist derived causal evidence without touching candidate Identity YAML."""

    if analysis is None:
        if profiles is None:
            raise ValueError("profiles or analysis is required")
        analysis = CausalAnalysis(profiles=profiles)
    payload = analysis.model_dump(mode="json")
    for artifact_name in artifact_names:
        path = output_dir / artifact_name
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        data["causal_analysis"] = payload
        path.write_text(
            yaml.safe_dump(data, sort_keys=False, allow_unicode=True),
            encoding="utf-8",
        )


def append_causal_comparison(output_dir: Path, analysis: CausalAnalysis) -> None:
    """Append bounded F3 diagnostics to comparison.md."""

    path = output_dir / "comparison.md"
    lines = ["", "## Causal Distinctness", "", f"Status: `{analysis.status}`", ""]
    for candidate_id, profile in analysis.profiles.items():
        actions = " → ".join(profile.external_action_pattern) or "unknown"
        lines.extend(
            [
                f"### {candidate_id}",
                f"- Primary strategy: {profile.primary_strategy or 'unknown'}",
                f"- Causal owner: {profile.causal_owner or 'unknown'}",
                f"- Action pattern: {actions}",
                f"- Pressure system: {profile.pressure_system or 'unknown'}",
                f"- Climax mechanic: {profile.climax_mechanic or 'unknown'}",
                "",
            ]
        )
    if analysis.pairwise_assessments:
        lines.extend(["### Pairwise assessment", ""])
        for assessment in analysis.pairwise_assessments:
            lines.append(
                f"- `{assessment.left_candidate_id}` vs `{assessment.right_candidate_id}`: "
                f"**{assessment.classification}** — {assessment.scene_consequence or assessment.rationale}"
            )
        lines.append("")
    path.write_text(path.read_text(encoding="utf-8") + "\n".join(lines), encoding="utf-8")


def non_adjudicable_surface_lines(
    analysis: CausalAnalysis,
    candidate_outputs: list[Any],
    output_dir: Path,
) -> list[str]:
    """Render a useful search result without pretending a comparative winner exists."""

    if analysis.status == "not_adjudicable_near_duplicate":
        reason = (
            "these interpretations are not causally distinct enough to justify a meaningful comparative choice"
        )
    elif analysis.status == "not_adjudicable_uncertain":
        reason = (
            "the available causal evidence is too uncertain to justify a meaningful comparative choice"
        )
    else:
        reason = "the causal analysis did not qualify this set for comparative recommendation"

    lines = [
        "Story Discovery",
        "",
        f"NO RECOMMENDATION YET — {reason}.",
        "",
        "Causal interpretations",
    ]
    for candidate_output in candidate_outputs:
        profile = analysis.profiles[candidate_output.candidate_id]
        lines.append(
            f"- {candidate_output.identity.title} (`{candidate_output.candidate_id}`): "
            f"{profile.primary_strategy or 'causal strategy uncertain'}"
        )
    lines.extend(
        [
            "",
            "Nothing has been accepted yet.",
            "",
            "Review the causal comparison:",
            f"  {output_dir / 'comparison.md'}",
            "",
            "You may revise the premise/brief and run Story Discovery again, or explicitly choose a candidate after reviewing it.",
        ]
    )
    return lines
