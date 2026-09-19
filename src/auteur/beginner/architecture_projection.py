"""Read-only story-orientation projections shared by Navigator and Story Map."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from .architecture_models import (
    ArchitectureAlternative,
    ArchitectureEvidence,
    ArchitectureFacet,
    NarrativeArchitectureAnalysis,
)
from .contracts import AcceptedMilestoneReference


FACET_LABELS = {
    ArchitectureFacet.GENRE_CONSTELLATION: "Genre / story traditions",
    ArchitectureFacet.NARRATIVE_ENGINE: "Main story machinery",
    ArchitectureFacet.CHARACTER_FUNCTION: "Character functions",
    ArchitectureFacet.AESTHETIC_FRAMING: "Framing",
    ArchitectureFacet.TROPE_FAMILY: "Trope families",
    ArchitectureFacet.RELATIONSHIP_DYNAMIC: "Emotional & relationship dynamics",
    ArchitectureFacet.SETTING_WORLD: "World & setting logic",
    ArchitectureFacet.THEME_MOTIF: "Themes & motifs",
}


class ArchitectureComponentProjection(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    component_id: str
    label: str
    role: str
    certainty: str
    derivation: str
    activation: str
    review_state: str
    rationale: str | None = None
    evidence: tuple[ArchitectureEvidence, ...] = ()
    alternatives: tuple[ArchitectureAlternative, ...] = ()


class ArchitectureFacetProjection(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    facet: str
    label: str
    components: tuple[ArchitectureComponentProjection, ...]


class StoryOrientationProjection(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    heading: str = "Here is what Auteur sees"
    summary: str
    analysis_id: str | None
    analysis_stale: bool
    authority_status: str
    navigator_facets: tuple[ArchitectureFacetProjection, ...]
    story_map_facets: tuple[ArchitectureFacetProjection, ...]
    availability_note: str | None = None
    next_action_label: str


def _component_projection(component, *, expanded: bool) -> ArchitectureComponentProjection:
    return ArchitectureComponentProjection(
        component_id=component.component_id,
        label=component.label,
        role=component.role.value,
        certainty=component.certainty.value,
        derivation=component.derivation.value,
        activation=component.activation.value,
        review_state=component.review_state.value,
        rationale=component.rationale if expanded else None,
        evidence=component.evidence if expanded else (),
        alternatives=component.alternatives if expanded else (),
    )


def _facet_projections(
    analysis: NarrativeArchitectureAnalysis,
    *,
    expanded: bool,
) -> tuple[ArchitectureFacetProjection, ...]:
    facets: list[ArchitectureFacetProjection] = []
    for facet in ArchitectureFacet:
        components = tuple(
            component
            for component in analysis.components
            if component.facet is facet
            and (
                expanded
                or (
                    component.activation.value == "active"
                    and component.role.value in {"primary", "supporting"}
                )
            )
        )
        if not components:
            continue
        facets.append(
            ArchitectureFacetProjection(
                facet=facet.value,
                label=FACET_LABELS[facet],
                components=tuple(
                    _component_projection(component, expanded=expanded)
                    for component in components
                ),
            )
        )
    return tuple(facets)


def _next_action(
    analysis_current: bool,
    accepted_milestones: tuple[AcceptedMilestoneReference, ...],
) -> str:
    if not analysis_current:
        return "Review what Auteur sees"
    accepted = {reference.milestone_id for reference in accepted_milestones}
    if "story_identity" in accepted:
        return "Plan the story"
    if "story_direction" in accepted:
        return "Review Story Identity"
    return "Continue with this interpretation"


def build_story_orientation(
    *,
    analysis: NarrativeArchitectureAnalysis | None,
    analysis_current: bool,
    accepted_milestones: tuple[AcceptedMilestoneReference, ...],
) -> StoryOrientationProjection | None:
    if analysis is None:
        return None
    return StoryOrientationProjection(
        summary=analysis.summary,
        analysis_id=analysis.analysis_id,
        analysis_stale=analysis.stale or not analysis_current,
        authority_status=analysis.authority_status,
        navigator_facets=_facet_projections(analysis, expanded=False),
        story_map_facets=_facet_projections(analysis, expanded=True),
        availability_note=analysis.availability_note,
        next_action_label=_next_action(analysis_current, accepted_milestones),
    )
