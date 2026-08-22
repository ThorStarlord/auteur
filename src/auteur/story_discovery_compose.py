"""Compose compatible Story Discovery mechanisms under one primary engine.

Composition is advisory candidate generation. It never promotes canonical state and
never changes the source Story Discovery recommendation.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from auteur.identity import StoryIdentity
from auteur.llm import LLMRequest
from auteur.story_discovery_causality import (
    CausalAnalysis,
    CausalProfileRecord,
    derive_causal_profile,
)
from auteur.story_discovery_craft import CraftAnalysis, CraftImpactRecord


_COMPOSITION_SYSTEM = """You are Auteur's bounded narrative composition architect.

Create one new StoryIdentity candidate by preserving the supplied PRIMARY ENGINE
and borrowing only the explicitly requested subordinate mechanisms from the
approved alternatives.

AUTHORITY AND HIERARCHY RULES
- This is candidate generation only. Never claim canonical state changed.
- The primary engine must continue to govern the story's decisive causal turns.
- The primary target-experience promise must remain the governing reader-experience center.
- Every borrowed mechanism has a bounded job and explicit forbidden ownership.
  Use the mechanism only for its job and never let it seize any forbidden ownership.
- Borrowed mechanisms may deepen motive, obstruction, consequence, reversal, or
  texture, but must remain subordinate to the primary engine and reader promise.
- Preserve every supplied primary hard constraint.
- Preserve the primary story type and governing target-experience promise.
- Preserve explicit architecture preferences exactly; omitted preferences remain omitted.
- Do not add a borrowed mechanism merely because it sounds attractive. Use only
  the mechanisms explicitly requested below.
- Do not use candidate self-advocacy, confidence, generated tradeoffs, provenance,
  or marketing claims as evidence.

Return one complete StoryIdentity as JSON only. Do not include commentary outside
the JSON object.
"""

_HIERARCHY_SYSTEM = """You are Auteur's bounded narrative hierarchy assessor.

Assess TWO independent hierarchy dimensions after subordinate mechanisms were borrowed.
This is not a quality score and you must not return an aggregate classification.

CAUSAL HIERARCHY asks whether the declared PRIMARY ENGINE still governs the major
external actions, recurring pressure, decisive reversals, and climax. A borrowed
mechanism is displaced when it takes ownership of decisive causation.

EXPERIENTIAL HIERARCHY asks whether the declared PRIMARY target-experience promise
still governs what the story repeatedly makes the reader anticipate, dread, grieve,
hope for, or interpret as thematically central. Inspect recurring scene emphasis,
emotional trajectory, thematic attention, and practical center of gravity. Merely
retaining the same target-experience label is not proof of preservation.

For each dimension classify:
- primary_preserved: the primary remains governing and borrowed mechanisms stay subordinate;
- primary_displaced: a borrowed mechanism has become governing in that dimension;
- uncertain: evidence is insufficient for a defensible hierarchy claim.

Respect every borrow's bounded job and forbidden ownership as explicit hierarchy
constraints. Return JSON only with exactly two top-level keys: causal and experiential.
Each value must contain exactly:
- classification
- rationale
- primary_evidence_preserved
- borrowed_evidence_subordinate
- risks
"""

HierarchyClassification = Literal["primary_preserved", "primary_displaced", "uncertain"]
_DEFAULT_FORBIDDEN_OWNERSHIP = (
    "governing external objective",
    "decisive reversal chain",
    "climax",
    "governing reader-experience promise",
)


class BorrowRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    candidate_id: str = Field(min_length=1)
    mechanism: str = Field(min_length=1)
    job: str | None = None
    forbidden_ownership: list[str] = Field(default_factory=list)

    @field_validator("candidate_id", "mechanism")
    @classmethod
    def _trim(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("borrow candidate and mechanism must be non-empty")
        return value

    @field_validator("job")
    @classmethod
    def _trim_optional_job(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = " ".join(value.split())
        return value or None

    @field_validator("forbidden_ownership")
    @classmethod
    def _normalize_forbidden_ownership(cls, values: list[str]) -> list[str]:
        normalized: list[str] = []
        for value in values:
            text = " ".join(value.split())
            if text and text not in normalized:
                normalized.append(text)
        return normalized


class HierarchyDimensionAssessment(BaseModel):
    model_config = ConfigDict(extra="forbid")

    classification: HierarchyClassification
    rationale: str = Field(min_length=1)
    primary_evidence_preserved: list[str]
    borrowed_evidence_subordinate: list[str]
    risks: list[str]


class _HierarchyResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    causal: HierarchyDimensionAssessment
    experiential: HierarchyDimensionAssessment


def _aggregate_hierarchy_classification(
    causal: HierarchyClassification,
    experiential: HierarchyClassification,
) -> HierarchyClassification:
    dimensions = {causal, experiential}
    if "primary_displaced" in dimensions:
        return "primary_displaced"
    if "uncertain" in dimensions:
        return "uncertain"
    return "primary_preserved"


class HierarchyAssessment(BaseModel):
    """Aggregate hierarchy result plus optional v2 dimensional evidence.

    The flat fields preserve the v1 report/read surface. New v2 reports also carry
    explicit causal and experiential assessments; aggregate classification is derived
    deterministically rather than trusted from the model.
    """

    model_config = ConfigDict(extra="forbid")

    classification: HierarchyClassification
    rationale: str = Field(min_length=1)
    primary_mechanics_preserved: list[str]
    borrowed_mechanics_subordinate: list[str]
    risks: list[str]
    causal: HierarchyDimensionAssessment | None = None
    experiential: HierarchyDimensionAssessment | None = None


class CompositionReport(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: Literal[1, 2] = 2
    status: Literal["candidate_only"] = "candidate_only"
    primary_candidate_id: str
    borrowed: list[BorrowRequest]
    primary_evidence_key: str
    borrowed_evidence_keys: dict[str, str]
    hierarchy_assessment: HierarchyAssessment
    composed_causal_profile: CausalProfileRecord
    output_candidate: str

    @model_validator(mode="after")
    def _validate_versioned_contract(self) -> "CompositionReport":
        if self.schema_version == 1:
            return self
        hierarchy = self.hierarchy_assessment
        if hierarchy.causal is None or hierarchy.experiential is None:
            raise ValueError("schema_version 2 requires causal and experiential hierarchy assessments")
        aggregate = _aggregate_hierarchy_classification(
            hierarchy.causal.classification,
            hierarchy.experiential.classification,
        )
        if hierarchy.classification != aggregate:
            raise ValueError("schema_version 2 hierarchy aggregate is inconsistent with dimensions")
        for borrow in self.borrowed:
            if borrow.job is None or not borrow.forbidden_ownership:
                raise ValueError(
                    "schema_version 2 borrowed mechanisms require a bounded job and forbidden ownership"
                )
        return self


def _err(message: str) -> None:
    print(f"Error: {message}", file=sys.stderr)


def parse_borrow_spec(raw: str) -> BorrowRequest:
    """Parse `candidate_id:requested mechanism`, splitting only on the first colon."""

    if ":" not in raw:
        raise ValueError(
            "--borrow must use candidate_id:mechanism, for example "
            "candidate_2:secret intervention layer"
        )
    candidate_id, mechanism = raw.split(":", 1)
    return BorrowRequest(candidate_id=candidate_id, mechanism=mechanism)


def _with_policy_boundary(borrow: BorrowRequest) -> BorrowRequest:
    """Attach a deterministic subordinate job and forbidden-ownership policy."""

    return borrow.model_copy(
        update={
            "job": (
                "Use this requested mechanism only as a subordinate complication, pressure, "
                f"or texture layer: {borrow.mechanism}"
            ),
            "forbidden_ownership": list(_DEFAULT_FORBIDDEN_OWNERSHIP),
        }
    )


def _load_identity(path: Path) -> StoryIdentity:
    try:
        return StoryIdentity.from_yaml(path)
    except Exception as exc:
        raise ValueError(f"failed to load StoryIdentity candidate {path}: {exc}") from exc


def _bounded_identity(identity: StoryIdentity) -> dict[str, Any]:
    """Return story commitments only; omit recommendation self-advocacy/provenance."""

    return {
        "core_answer": identity.core_answer,
        "target_experience": identity.target_experience.model_dump(mode="json"),
        "story_type": identity.story_type.model_dump(mode="json"),
        "central_engine": identity.central_engine.model_dump(mode="json"),
        "not_this": list(identity.not_this),
        "open_questions": list(identity.open_questions),
        "author_overrides": list(identity.author_overrides),
        "hard_constraints": list(getattr(identity, "hard_constraints", [])),
        "architecture_preferences": (
            identity.architecture_preferences.model_dump(mode="json")
            if getattr(identity, "architecture_preferences", None) is not None
            else None
        ),
    }


def _load_run_evidence(
    discovery_dir: Path,
) -> tuple[dict[str, Any], CausalAnalysis, CraftAnalysis]:
    report_path = discovery_dir / "discovery_report.yaml"
    if not report_path.exists():
        raise ValueError(f"Story Discovery report not found: {report_path}")
    report = yaml.safe_load(report_path.read_text(encoding="utf-8")) or {}
    try:
        causal = CausalAnalysis.model_validate(report.get("causal_analysis"))
    except Exception as exc:
        raise ValueError("Story Discovery run has no valid F3 causal analysis") from exc
    if causal.status != "qualified":
        raise ValueError(
            "Story Discovery composition requires a causally qualified recommendation set; "
            f"found {causal.status!r}"
        )
    try:
        craft = CraftAnalysis.model_validate(report.get("craft_analysis"))
    except Exception as exc:
        raise ValueError("Story Discovery run has no valid F4 craft analysis") from exc
    if craft.status != "complete":
        raise ValueError("Story Discovery craft analysis is not complete")
    return report, causal, craft


def _validate_requests(
    discovery_dir: Path,
    primary_id: str,
    raw_borrows: list[str],
    causal: CausalAnalysis,
    craft: CraftAnalysis,
) -> tuple[StoryIdentity, list[tuple[BorrowRequest, StoryIdentity, CraftImpactRecord]]]:
    if not raw_borrows:
        raise ValueError("at least one --borrow candidate_id:mechanism is required")
    if craft.primary_candidate_id != primary_id:
        raise ValueError(
            "F5 currently composes under the primary engine that F4 analyzed; "
            f"expected {craft.primary_candidate_id!r}, got {primary_id!r}"
        )
    if primary_id not in causal.profiles:
        raise ValueError(f"primary candidate has no F3 causal profile: {primary_id}")
    primary_path = discovery_dir / f"{primary_id}.yaml"
    if not primary_path.exists():
        raise ValueError(f"primary candidate not found: {primary_path}")
    primary = _load_identity(primary_path)

    borrows = [_with_policy_boundary(parse_borrow_spec(raw)) for raw in raw_borrows]
    ids = [borrow.candidate_id for borrow in borrows]
    if primary_id in ids:
        raise ValueError("the primary candidate cannot be borrowed from itself")
    if len(set(ids)) != len(ids):
        raise ValueError("each borrowed candidate may be supplied only once")

    resolved: list[tuple[BorrowRequest, StoryIdentity, CraftImpactRecord]] = []
    for borrow in borrows:
        if borrow.candidate_id not in causal.profiles:
            raise ValueError(
                f"borrowed candidate has no F3 causal profile: {borrow.candidate_id}"
            )
        impact = craft.impacts.get(borrow.candidate_id)
        if impact is None:
            raise ValueError(
                f"borrowed candidate has no F4 craft impact from primary {primary_id}: "
                f"{borrow.candidate_id}"
            )
        if impact.composability != "compatible_as_secondary":
            raise ValueError(
                f"borrowed candidate {borrow.candidate_id} is not approved as a subordinate "
                f"mechanism: {impact.composability}"
            )
        candidate_path = discovery_dir / f"{borrow.candidate_id}.yaml"
        if not candidate_path.exists():
            raise ValueError(f"borrowed candidate not found: {candidate_path}")
        resolved.append((borrow, _load_identity(candidate_path), impact))
    return primary, resolved


def build_composition_request(
    primary_id: str,
    primary: StoryIdentity,
    borrows: list[tuple[BorrowRequest, StoryIdentity, CraftImpactRecord]],
    causal: CausalAnalysis,
    *,
    declared_author_intent: dict[str, Any] | None,
) -> LLMRequest:
    evidence = {
        "declared_author_intent": declared_author_intent,
        "primary": {
            "candidate_id": primary_id,
            "story_commitments": _bounded_identity(primary),
            "causal_profile": causal.profiles[primary_id].model_dump(mode="json"),
        },
        "borrowed": [
            {
                "candidate_id": borrow.candidate_id,
                "requested_mechanism": borrow.mechanism,
                "job": borrow.job,
                "forbidden_ownership": borrow.forbidden_ownership,
                "story_commitments": _bounded_identity(identity),
                "causal_profile": causal.profiles[borrow.candidate_id].model_dump(mode="json"),
                "craft_impact": impact.model_dump(
                    mode="json",
                    exclude={
                        "primary_candidate_id",
                        "compared_candidate_id",
                        "primary_evidence_key",
                        "compared_evidence_key",
                    },
                ),
            }
            for borrow, identity, impact in borrows
        ],
    }
    return LLMRequest(
        system=_COMPOSITION_SYSTEM,
        user="BOUNDED COMPOSITION EVIDENCE\n" + json.dumps(evidence, indent=2, ensure_ascii=False),
        max_tokens=4200,
        temperature=0.2,
        model=None,
    )


def _parse_story_identity(text: str) -> StoryIdentity:
    stripped = text.strip()
    match = re.search(r"\{.*\}", stripped, re.DOTALL)
    if match:
        raw: Any = json.loads(match.group(0))
    else:
        fence = re.search(r"```(?:yaml|yml)?\s*(.*?)```", stripped, re.DOTALL | re.IGNORECASE)
        candidate = fence.group(1) if fence else stripped
        try:
            raw = yaml.safe_load(candidate)
        except yaml.YAMLError as exc:
            raise ValueError(f"composition response was not valid JSON/YAML: {exc}") from exc
    if not isinstance(raw, dict):
        raise ValueError("composition response must contain one StoryIdentity mapping")
    try:
        return StoryIdentity.model_validate(raw)
    except Exception as exc:
        raise ValueError(f"composition response is not a valid StoryIdentity: {exc}") from exc


def _validate_preserved_commitments(primary: StoryIdentity, composed: StoryIdentity) -> None:
    mismatches: list[str] = []
    if composed.story_type != primary.story_type:
        mismatches.append("story_type")
    if composed.target_experience.primary != primary.target_experience.primary:
        mismatches.append("target_experience.primary")
    if composed.architecture_preferences != primary.architecture_preferences:
        mismatches.append("architecture_preferences")
    if list(composed.hard_constraints) != list(primary.hard_constraints):
        mismatches.append("hard_constraints")
    if mismatches:
        raise ValueError(
            "composed candidate changed preserved primary commitments: " + ", ".join(mismatches)
        )

    diagnostics = composed.validate_identity()
    errors = [
        diagnostic
        for diagnostic in diagnostics
        if (
            diagnostic.severity.value.lower() == "error"
            if hasattr(diagnostic.severity, "value")
            else str(diagnostic.severity).lower() == "error"
        )
    ]
    if errors:
        details = "; ".join(f"{d.rule}: {d.message}" for d in errors)
        raise ValueError(f"composed candidate failed StoryIdentity validation: {details}")


def _resolve_composition_premise(
    report: dict[str, Any],
    primary: StoryIdentity,
) -> str:
    """Prefer the author's source premise when re-profiling a composed candidate."""

    declared = report.get("declared_author_intent")
    if isinstance(declared, dict):
        premise = declared.get("premise")
        if isinstance(premise, str) and premise.strip():
            return premise.strip()

    premise_summary = report.get("premise_summary")
    if isinstance(premise_summary, str) and premise_summary.strip():
        return premise_summary.strip()

    return primary.core_answer


def _craft_impact_for_hierarchy(impact: CraftImpactRecord) -> dict[str, Any]:
    return impact.model_dump(
        mode="json",
        exclude={
            "primary_candidate_id",
            "compared_candidate_id",
            "primary_evidence_key",
            "compared_evidence_key",
        },
    )


def build_hierarchy_request(
    primary_id: str,
    primary: StoryIdentity,
    composed: StoryIdentity,
    primary_profile: CausalProfileRecord,
    composed_profile: CausalProfileRecord,
    borrows: list[tuple[BorrowRequest, StoryIdentity, CraftImpactRecord]],
    causal: CausalAnalysis,
    *,
    declared_author_intent: dict[str, Any] | None,
) -> LLMRequest:
    evidence = {
        "declared_author_intent": declared_author_intent,
        "primary": {
            "candidate_id": primary_id,
            "story_commitments": _bounded_identity(primary),
            "causal_profile": primary_profile.model_dump(mode="json"),
        },
        "composed": {
            "story_commitments": _bounded_identity(composed),
            "causal_profile": composed_profile.model_dump(mode="json"),
        },
        "borrowed_mechanisms": [
            {
                "candidate_id": borrow.candidate_id,
                "requested_mechanism": borrow.mechanism,
                "job": borrow.job,
                "forbidden_ownership": borrow.forbidden_ownership,
                "source_profile": causal.profiles[borrow.candidate_id].model_dump(mode="json"),
                "craft_impact": _craft_impact_for_hierarchy(impact),
            }
            for borrow, _identity, impact in borrows
        ],
    }
    return LLMRequest(
        system=_HIERARCHY_SYSTEM,
        user="BOUNDED DUAL-HIERARCHY EVIDENCE\n" + json.dumps(evidence, indent=2, ensure_ascii=False),
        max_tokens=2200,
        temperature=0.1,
        model=None,
    )


def _unique(values: list[str]) -> list[str]:
    result: list[str] = []
    for value in values:
        if value not in result:
            result.append(value)
    return result


def parse_hierarchy_assessment(text: str) -> HierarchyAssessment:
    match = re.search(r"\{.*\}", text.strip(), re.DOTALL)
    if not match:
        raise ValueError("hierarchy assessment did not contain a JSON object")
    try:
        response = _HierarchyResponse.model_validate(json.loads(match.group(0)))
    except Exception as exc:
        raise ValueError(f"hierarchy assessment failed schema validation: {exc}") from exc

    classification = _aggregate_hierarchy_classification(
        response.causal.classification,
        response.experiential.classification,
    )
    rationale = (
        f"Causal hierarchy: {response.causal.rationale} "
        f"Experiential hierarchy: {response.experiential.rationale}"
    )
    return HierarchyAssessment(
        classification=classification,
        rationale=rationale,
        primary_mechanics_preserved=response.causal.primary_evidence_preserved,
        borrowed_mechanics_subordinate=response.causal.borrowed_evidence_subordinate,
        risks=_unique(response.causal.risks + response.experiential.risks),
        causal=response.causal,
        experiential=response.experiential,
    )


def dispatch_story_discovery_compose(args: Any) -> int:
    discovery_dir = Path(args.discovery_dir)
    if not discovery_dir.is_dir():
        _err(f"Story Discovery directory not found: {discovery_dir}")
        return 1

    try:
        report, causal, craft = _load_run_evidence(discovery_dir)
        primary, resolved = _validate_requests(
            discovery_dir,
            args.primary,
            list(args.borrow or []),
            causal,
            craft,
        )
    except Exception as exc:
        _err(str(exc))
        return 1

    from auteur.llm.factory import build_client

    client = build_client(args.provider, args.model, agent_type="identity")
    declared = report.get("declared_author_intent")
    premise_text = _resolve_composition_premise(report, primary)
    borrow_requests = [borrow for borrow, _, _ in resolved]
    try:
        response = client.complete(
            build_composition_request(
                args.primary,
                primary,
                resolved,
                causal,
                declared_author_intent=declared,
            )
        )
        composed = _parse_story_identity(response.text)
        _validate_preserved_commitments(primary, composed)

        composed_output = SimpleNamespace(
            candidate_id="composed_candidate",
            identity=composed,
        )
        composed_profile = derive_causal_profile(
            client,
            composed_output,
            premise_text,
            declared_author_intent=declared,
        )
        hierarchy_response = client.complete(
            build_hierarchy_request(
                args.primary,
                primary,
                composed,
                causal.profiles[args.primary],
                composed_profile,
                resolved,
                causal,
                declared_author_intent=declared,
            )
        )
        hierarchy = parse_hierarchy_assessment(hierarchy_response.text)
        if hierarchy.classification != "primary_preserved":
            raise ValueError(
                "composition hierarchy did not preserve the primary engine and reader-experience center: "
                f"{hierarchy.classification} — {hierarchy.rationale}"
            )
    except Exception as exc:
        _err(f"Failed to compose Story Discovery candidate: {exc}")
        return 1

    output = Path(args.output) if args.output is not None else discovery_dir / "composed_candidate.yaml"
    output.parent.mkdir(parents=True, exist_ok=True)
    report_path = (
        discovery_dir / "composition_report.yaml"
        if args.output is None
        else output.with_name(output.stem + "_composition_report.yaml")
    )
    composed.to_yaml(output)
    composition_report = CompositionReport(
        schema_version=2,
        primary_candidate_id=args.primary,
        borrowed=borrow_requests,
        primary_evidence_key=causal.profiles[args.primary].evidence_key,
        borrowed_evidence_keys={
            borrow.candidate_id: causal.profiles[borrow.candidate_id].evidence_key
            for borrow in borrow_requests
        },
        hierarchy_assessment=hierarchy,
        composed_causal_profile=composed_profile,
        output_candidate=str(output),
    )
    report_path.write_text(
        yaml.safe_dump(
            composition_report.model_dump(mode="json"),
            sort_keys=False,
            allow_unicode=True,
        ),
        encoding="utf-8",
    )

    print(f"COMPOSED CANDIDATE — {composed.title}")
    print(f"Primary engine retained: {args.primary}")
    print("Borrowed subordinate mechanisms:")
    for borrow in borrow_requests:
        print(f"- {borrow.candidate_id}: {borrow.mechanism}")
    print("\nNothing has been accepted yet.")
    print("\nAccept this composed candidate explicitly:")
    print(f"  auteur story-discovery accept {output} --output story_identity.yaml")
    print(f"\nComposition report: {report_path}")
    return 0
