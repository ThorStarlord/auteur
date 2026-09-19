"""Adapter from existing Story Discovery into the beginner journey."""

from __future__ import annotations

import hashlib
import json
from typing import Protocol

from auteur.cli_handlers import RecommendOpenEndedData, handle_identity_recommend
from auteur.llm import LLMClient, RetriableError
from auteur.story_discovery_recommend import recommend_candidate_outputs

from .architecture_analysis import analysis_basis_fingerprint
from .architecture_models import (
    ArchitectureActivation,
    ArchitectureCertainty,
    NarrativeArchitectureAnalysis,
)
from .discovery_models import (
    DiscoveryDirection,
    DiscoveryRecommendation,
    DiscoveryRecommendationStatus,
)


class DiscoveryRecommender(Protocol):
    def recommend(
        self,
        *,
        premise: str,
        analysis: NarrativeArchitectureAnalysis,
    ) -> DiscoveryRecommendation:
        raise NotImplementedError


class UnavailableDiscoveryRecommender:
    def __init__(self, reason: str = "No reasoning provider configured.") -> None:
        self.reason = reason

    def recommend(
        self,
        *,
        premise: str,
        analysis: NarrativeArchitectureAnalysis,
    ) -> DiscoveryRecommendation:
        del premise
        basis = analysis_basis_fingerprint(analysis)
        return DiscoveryRecommendation(
            recommendation_id=f"discovery:unavailable:{basis[:16]}",
            source_analysis_id=analysis.analysis_id,
            source_basis_fingerprint=basis,
            status=DiscoveryRecommendationStatus.UNAVAILABLE,
            recommended_direction_id=None,
            rationale=self.reason,
            directions=(),
        )


def _design_context(analysis: NarrativeArchitectureAnalysis) -> dict[str, object]:
    active = [
        {
            "component_id": component.component_id,
            "facet": component.facet.value,
            "label": component.label,
            "role": component.role.value,
            "certainty": component.certainty.value,
            "derivation": component.derivation.value,
            "rationale": component.rationale,
            "evidence": [
                {
                    "label": evidence.label,
                    "excerpt": evidence.excerpt,
                    "source_kind": evidence.source_kind,
                }
                for evidence in component.evidence
            ],
        }
        for component in analysis.components
        if component.activation is ArchitectureActivation.ACTIVE
    ]
    unresolved = [
        {
            "component_id": component.component_id,
            "facet": component.facet.value,
            "label": component.label,
            "alternatives": [alternative.label for alternative in component.alternatives],
            "rationale": component.rationale,
        }
        for component in analysis.components
        if component.certainty is ArchitectureCertainty.UNCERTAIN
    ]
    return {
        "architecture_summary": analysis.summary,
        "active_interpretation": active,
        "consequential_unresolved_interpretation": unresolved,
        "instruction": (
            "Treat active interpretation as derived working guidance, not canon. "
            "When unresolved components are coupled and materially change the engine, target experience, "
            "payoff, or Story Identity, resolve them as distinct coherent directions rather than independent checkboxes."
        ),
    }


def _architecture_summary(analysis: NarrativeArchitectureAnalysis) -> str:
    primary = [
        component.label
        for component in analysis.components
        if component.activation is ArchitectureActivation.ACTIVE and component.role.value == "primary"
    ]
    supporting = [
        component.label
        for component in analysis.components
        if component.activation is ArchitectureActivation.ACTIVE and component.role.value == "supporting"
    ]
    pieces: list[str] = []
    if primary:
        pieces.append("Primary: " + ", ".join(primary))
    if supporting:
        pieces.append("Supporting: " + ", ".join(supporting))
    return "; ".join(pieces) if pieces else analysis.summary


def _recommendation_id(
    basis: str,
    directions: tuple[DiscoveryDirection, ...],
    recommended_direction_id: str | None,
) -> str:
    payload = json.dumps(
        {
            "basis": basis,
            "directions": [direction.direction_id for direction in directions],
            "recommended": recommended_direction_id,
        },
        sort_keys=True,
        separators=(",", ":"),
    )
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]
    return f"discovery:{digest}"


class StoryDiscoveryRecommender:
    """Reuse Story Discovery search and judgment without writing files or canon."""

    def __init__(self, *, client: LLMClient, requested_candidates: int = 3) -> None:
        if requested_candidates < 2:
            raise ValueError("beginner Discovery requires at least two requested candidates")
        self.client = client
        self.requested_candidates = requested_candidates

    def recommend(
        self,
        *,
        premise: str,
        analysis: NarrativeArchitectureAnalysis,
    ) -> DiscoveryRecommendation:
        basis = analysis_basis_fingerprint(analysis)
        try:
            result = handle_identity_recommend(
                client=self.client,
                premise_text=premise,
                recommend_mode="open_ended",
                candidates_count=self.requested_candidates,
                strict_candidate_count=False,
                design_context=_design_context(analysis),
            )
        except RetriableError:
            result = None

        if result is None or not result.is_success or not isinstance(result.data, RecommendOpenEndedData):
            return DiscoveryRecommendation(
                recommendation_id=f"discovery:unavailable:{basis[:16]}",
                source_analysis_id=analysis.analysis_id,
                source_basis_fingerprint=basis,
                status=DiscoveryRecommendationStatus.UNAVAILABLE,
                recommended_direction_id=None,
                rationale="Rich story-direction search is temporarily unavailable.",
                directions=(),
            )

        candidate_outputs = result.data.candidates
        if not candidate_outputs:
            return DiscoveryRecommendation(
                recommendation_id=f"discovery:unavailable:{basis[:16]}",
                source_analysis_id=analysis.analysis_id,
                source_basis_fingerprint=basis,
                status=DiscoveryRecommendationStatus.UNAVAILABLE,
                recommended_direction_id=None,
                rationale="Rich story-direction search is temporarily unavailable.",
                directions=(),
            )

        try:
            judgment = recommend_candidate_outputs(
                client=self.client,
                premise_text=premise,
                candidate_outputs=candidate_outputs,
                requested_candidates=self.requested_candidates,
                genre=None,
                medium=None,
                mode=None,
            )
        except (RetriableError, ValueError):
            return DiscoveryRecommendation(
                recommendation_id=f"discovery:unavailable:{basis[:16]}",
                source_analysis_id=analysis.analysis_id,
                source_basis_fingerprint=basis,
                status=DiscoveryRecommendationStatus.UNAVAILABLE,
                recommended_direction_id=None,
                rationale="Rich story-direction search is temporarily unavailable.",
                directions=(),
            )

        candidate_to_direction = {
            candidate.candidate_id: f"direction:{candidate.candidate_id}"
            for candidate in candidate_outputs
        }
        architecture_summary = _architecture_summary(analysis)
        source_component_ids = tuple(component.component_id for component in analysis.components)
        directions = tuple(
            DiscoveryDirection(
                direction_id=candidate_to_direction[candidate.candidate_id],
                title=candidate.identity.title,
                summary=candidate.identity.core_answer,
                identity_candidate=candidate.identity,
                architecture_summary=architecture_summary,
                tradeoffs=tuple(candidate.candidate.tradeoffs),
                risks=tuple(candidate.candidate.risks),
                source_analysis_id=analysis.analysis_id,
                source_component_ids=source_component_ids,
            )
            for candidate in candidate_outputs
        )
        recommended_direction_id = (
            candidate_to_direction[judgment.recommended_candidate_id]
            if judgment.recommended_candidate_id is not None
            else None
        )
        status = (
            DiscoveryRecommendationStatus.READY
            if judgment.status == "recommended"
            else DiscoveryRecommendationStatus.NEEDS_AUTHOR_CHOICE
        )
        recommendation_id = _recommendation_id(
            basis,
            directions,
            recommended_direction_id,
        )
        return DiscoveryRecommendation(
            recommendation_id=recommendation_id,
            source_analysis_id=analysis.analysis_id,
            source_basis_fingerprint=basis,
            status=status,
            recommended_direction_id=recommended_direction_id,
            rationale=judgment.rationale,
            directions=directions,
        )
