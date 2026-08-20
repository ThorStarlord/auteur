"""Derived, provider-free Story Discovery project state.

This module interprets the working Discovery Brief and persisted Phase F/G
artifacts without mutating project state or invoking an LLM. It is the single
source of truth for Story Discovery workflow/review routing.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any

import yaml

from auteur.story_discovery_causality import CausalAnalysis
from auteur.story_discovery_compose import CompositionReport
from auteur.story_discovery_craft import CraftAnalysis
from auteur.story_discovery_guidance import BriefLifecycleState, inspect_working_brief


class StoryDiscoveryStateKind(str, Enum):
    NO_BRIEF = "no_brief"
    INVALID_BRIEF = "invalid_brief"
    INCOMPLETE_BRIEF = "incomplete_brief"
    READY_TO_DISCOVER = "ready_to_discover"
    DISCOVERY_INVALID = "discovery_invalid"
    NON_ADJUDICABLE = "non_adjudicable"
    RECOMMENDATION_AVAILABLE = "recommendation_available"
    COMPOSED_CANDIDATE_AVAILABLE = "composed_candidate_available"


@dataclass(frozen=True)
class StoryDiscoveryProjectState:
    kind: StoryDiscoveryStateKind
    brief_state: BriefLifecycleState
    intent_mode: str | None = None
    run_matches_current_brief: bool = False
    causal_status: str | None = None
    recommended_candidate_id: str | None = None
    recommended_candidate_path: Path | None = None
    craft_status: str | None = None
    compatible_secondary_candidate_ids: tuple[str, ...] = ()
    composed_candidate_path: Path | None = None
    composition_report_path: Path | None = None
    problems: tuple[str, ...] = ()

    @property
    def has_recommendation(self) -> bool:
        return self.recommended_candidate_id is not None

    @property
    def can_compose(self) -> bool:
        return bool(self.compatible_secondary_candidate_ids)

    @property
    def has_composed_candidate(self) -> bool:
        return self.composed_candidate_path is not None

    @property
    def is_non_adjudicable(self) -> bool:
        return self.kind is StoryDiscoveryStateKind.NON_ADJUDICABLE


def _load_mapping(path: Path) -> tuple[dict[str, Any] | None, str | None]:
    try:
        payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except (OSError, yaml.YAMLError) as exc:
        return None, str(exc)
    if not isinstance(payload, dict):
        return None, "artifact must contain a YAML mapping"
    return payload, None


def _safe_candidate_path(discovery_dir: Path, candidate_id: object) -> tuple[str | None, Path | None]:
    if not isinstance(candidate_id, str) or not candidate_id.strip():
        return None, None
    normalized = candidate_id.strip()
    if Path(normalized).name != normalized:
        return None, None
    path = discovery_dir / f"{normalized}.yaml"
    if not path.is_file():
        return None, None
    return normalized, path


def _run_matches_current_brief(brief: object | None, discovery_set: dict[str, Any]) -> bool:
    if brief is None:
        return True
    declared = getattr(brief, "declared_intent")()
    return (
        discovery_set.get("intent_mode") == "intent_aware"
        and discovery_set.get("declared_author_intent") == declared
    )


def _parse_causal(discovery_set: dict[str, Any]) -> tuple[CausalAnalysis | None, str | None]:
    raw = discovery_set.get("causal_analysis")
    if raw is None:
        return None, None
    try:
        return CausalAnalysis.model_validate(raw), None
    except Exception as exc:
        return None, str(exc)


def _parse_craft(discovery_set: dict[str, Any]) -> tuple[CraftAnalysis | None, str | None]:
    raw = discovery_set.get("craft_analysis")
    if raw is None:
        return None, None
    try:
        return CraftAnalysis.model_validate(raw), None
    except Exception as exc:
        return None, str(exc)


def _compatible_secondary_ids(
    craft: CraftAnalysis | None,
    winner: str,
    discovery_dir: Path,
) -> tuple[str, ...]:
    if craft is None or craft.status != "complete" or craft.primary_candidate_id != winner:
        return ()
    compatible = [
        candidate_id
        for candidate_id, impact in craft.impacts.items()
        if (
            impact.composability == "compatible_as_secondary"
            and candidate_id != winner
            and (discovery_dir / f"{candidate_id}.yaml").is_file()
        )
    ]
    return tuple(sorted(compatible))


def _current_composition(
    discovery_dir: Path,
    winner: str,
    causal: CausalAnalysis | None,
) -> tuple[Path | None, Path | None, str | None]:
    report_path = discovery_dir / "composition_report.yaml"
    candidate_path = discovery_dir / "composed_candidate.yaml"
    if not report_path.exists() and not candidate_path.exists():
        return None, None, None
    if not report_path.is_file() or not candidate_path.is_file():
        return None, None, "composition artifacts are incomplete"

    raw, error = _load_mapping(report_path)
    if raw is None:
        return None, None, f"composition report is invalid: {error}"
    try:
        report = CompositionReport.model_validate(raw)
    except Exception as exc:
        return None, None, f"composition report is invalid: {exc}"

    if report.primary_candidate_id != winner:
        return None, None, "composition belongs to a different primary recommendation"
    if report.hierarchy_assessment.classification != "primary_preserved":
        return None, None, "composition does not preserve the current primary engine"
    if causal is None or winner not in causal.profiles:
        return None, None, "composition cannot be matched to current causal evidence"
    if report.primary_evidence_key != causal.profiles[winner].evidence_key:
        return None, None, "composition primary evidence is stale"

    for candidate_id, evidence_key in report.borrowed_evidence_keys.items():
        profile = causal.profiles.get(candidate_id)
        if profile is None or profile.evidence_key != evidence_key:
            return None, None, f"composition evidence is stale for {candidate_id}"

    return candidate_path, report_path, None


def classify_story_discovery_project(project_root: str | Path) -> StoryDiscoveryProjectState:
    """Derive the current Story Discovery state from project-local artifacts only."""

    root = Path(project_root)
    brief_status = inspect_working_brief(root)
    if brief_status.state is BriefLifecycleState.INVALID:
        return StoryDiscoveryProjectState(
            kind=StoryDiscoveryStateKind.INVALID_BRIEF,
            brief_state=brief_status.state,
            problems=((brief_status.error or "working brief is invalid"),),
        )
    if brief_status.state is BriefLifecycleState.INCOMPLETE:
        return StoryDiscoveryProjectState(
            kind=StoryDiscoveryStateKind.INCOMPLETE_BRIEF,
            brief_state=brief_status.state,
        )

    discovery_dir = root / "story_discovery"
    set_path = discovery_dir / "discovery_set.yaml"
    if not set_path.exists():
        kind = (
            StoryDiscoveryStateKind.READY_TO_DISCOVER
            if brief_status.state is BriefLifecycleState.ADEQUATE
            else StoryDiscoveryStateKind.NO_BRIEF
        )
        return StoryDiscoveryProjectState(kind=kind, brief_state=brief_status.state)

    discovery_set, set_error = _load_mapping(set_path)
    if discovery_set is None:
        if brief_status.state is BriefLifecycleState.ADEQUATE:
            return StoryDiscoveryProjectState(
                kind=StoryDiscoveryStateKind.DISCOVERY_INVALID,
                brief_state=brief_status.state,
                problems=(f"discovery set is invalid: {set_error}",),
            )
        return StoryDiscoveryProjectState(
            kind=StoryDiscoveryStateKind.NO_BRIEF,
            brief_state=brief_status.state,
            problems=(f"ignored invalid legacy discovery set: {set_error}",),
        )

    brief = brief_status.brief
    matches = _run_matches_current_brief(brief, discovery_set)
    intent_mode = discovery_set.get("intent_mode")
    intent_mode = intent_mode if isinstance(intent_mode, str) else None
    if brief_status.state is BriefLifecycleState.ADEQUATE and not matches:
        return StoryDiscoveryProjectState(
            kind=StoryDiscoveryStateKind.READY_TO_DISCOVER,
            brief_state=brief_status.state,
            intent_mode=intent_mode,
            run_matches_current_brief=False,
        )

    causal, causal_error = _parse_causal(discovery_set)
    causal_status = causal.status if causal is not None else None
    if causal_error is not None:
        return StoryDiscoveryProjectState(
            kind=StoryDiscoveryStateKind.DISCOVERY_INVALID,
            brief_state=brief_status.state,
            intent_mode=intent_mode,
            run_matches_current_brief=matches,
            problems=(f"causal analysis is invalid: {causal_error}",),
        )
    if causal_status in {
        "not_adjudicable_near_duplicate",
        "not_adjudicable_uncertain",
    }:
        return StoryDiscoveryProjectState(
            kind=StoryDiscoveryStateKind.NON_ADJUDICABLE,
            brief_state=brief_status.state,
            intent_mode=intent_mode,
            run_matches_current_brief=matches,
            causal_status=causal_status,
        )
    if causal_status == "malformed_analysis":
        return StoryDiscoveryProjectState(
            kind=StoryDiscoveryStateKind.DISCOVERY_INVALID,
            brief_state=brief_status.state,
            intent_mode=intent_mode,
            run_matches_current_brief=matches,
            causal_status=causal_status,
            problems=("causal analysis is malformed",),
        )

    winner, winner_path = _safe_candidate_path(
        discovery_dir,
        discovery_set.get("recommended_candidate_id"),
    )
    if causal_status == "qualified" and winner is None:
        return StoryDiscoveryProjectState(
            kind=StoryDiscoveryStateKind.DISCOVERY_INVALID,
            brief_state=brief_status.state,
            intent_mode=intent_mode,
            run_matches_current_brief=matches,
            causal_status=causal_status,
            problems=("qualified discovery has no usable recommended candidate",),
        )
    if winner is None:
        kind = (
            StoryDiscoveryStateKind.READY_TO_DISCOVER
            if brief_status.state is BriefLifecycleState.ADEQUATE
            else StoryDiscoveryStateKind.NO_BRIEF
        )
        return StoryDiscoveryProjectState(
            kind=kind,
            brief_state=brief_status.state,
            intent_mode=intent_mode,
            run_matches_current_brief=matches,
            causal_status=causal_status,
        )

    craft, craft_error = _parse_craft(discovery_set)
    craft_status = craft.status if craft is not None else None
    problems: list[str] = []
    if craft_error is not None:
        problems.append(f"craft analysis is invalid: {craft_error}")
        craft = None
        craft_status = None
    compatible = _compatible_secondary_ids(craft, winner, discovery_dir)

    composed_path, composition_report_path, composition_error = _current_composition(
        discovery_dir,
        winner,
        causal,
    )
    if composition_error is not None:
        problems.append(composition_error)

    kind = (
        StoryDiscoveryStateKind.COMPOSED_CANDIDATE_AVAILABLE
        if composed_path is not None
        else StoryDiscoveryStateKind.RECOMMENDATION_AVAILABLE
    )
    return StoryDiscoveryProjectState(
        kind=kind,
        brief_state=brief_status.state,
        intent_mode=intent_mode,
        run_matches_current_brief=matches,
        causal_status=causal_status,
        recommended_candidate_id=winner,
        recommended_candidate_path=winner_path,
        craft_status=craft_status,
        compatible_secondary_candidate_ids=compatible,
        composed_candidate_path=composed_path,
        composition_report_path=composition_report_path,
        problems=tuple(problems),
    )
