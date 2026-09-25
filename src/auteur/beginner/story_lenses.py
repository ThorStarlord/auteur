"""Composable read-only Story Lens projections for the Beginner first screen.

Story Lenses are a product projection over NarrativeArchitectureAnalysis. They
never become a second narrative model and never grant authority. Direct lenses
reference existing architecture components; synthesized lenses derive bounded
structural/reader-facing interpretations from those same components.
"""

from __future__ import annotations

from enum import Enum
from typing import Literal

from pydantic import BaseModel, ConfigDict

from .architecture_models import (
    ArchitectureActivation,
    ArchitectureAlternative,
    ArchitectureEvidence,
    ArchitectureFacet,
    ArchitectureReviewState,
    ArchitectureRole,
    NarrativeArchitectureAnalysis,
)


class StoryLensType(str, Enum):
    STORY_ENGINE = "story_engine"
    AESTHETIC_FRAMING = "aesthetic_framing"
    COMMON_TROPES = "common_tropes"
    STRUCTURAL_SHAPE = "structural_shape"
    READER_EXPERIENCE = "reader_experience"


class StoryLensState(str, Enum):
    INFERRED = "inferred"
    AUTHOR_CONFIRMED = "author_confirmed"
    AUTHOR_MODIFIED = "author_modified"
    UNESTABLISHED = "unestablished"
    STALE = "stale"


class StoryLensItem(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    component_id: str
    label: str
    role: str
    certainty: str
    activation: str
    review_state: str
    rationale: str
    evidence: tuple[ArchitectureEvidence, ...] = ()
    alternatives: tuple[ArchitectureAlternative, ...] = ()


class StoryLensProjection(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    lens_id: str
    lens_type: StoryLensType
    title: str
    eyebrow: str
    summary: str
    detail: str
    state: StoryLensState
    authority_status: Literal["DERIVED / NOT CANON"] = "DERIVED / NOT CANON"
    source_component_ids: tuple[str, ...] = ()
    items: tuple[StoryLensItem, ...] = ()
    related_lens_ids: tuple[str, ...] = ()
    refinement_mode: Literal["direct", "through_sources", "none"] = "none"


class StoryLensDiagnostics(BaseModel):
    """Actionable local interpretation health, deliberately not usage analytics."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    schema_version: Literal[1] = 1
    analysis_id: str
    analyzer_id: str
    source_mode: Literal["provider", "deterministic_fallback"]
    stale: bool
    active_component_count: int
    suppressed_component_count: int
    author_adjustment_count: int
    unestablished_lens_ids: tuple[str, ...]
    needs_attention_lens_ids: tuple[str, ...]


_DIRECT_LENS_CONFIG: tuple[
    tuple[StoryLensType, str, str, ArchitectureFacet, tuple[str, ...]],
    ...,
] = (
    (
        StoryLensType.STORY_ENGINE,
        "Main story engine",
        "What keeps generating story pressure",
        ArchitectureFacet.NARRATIVE_ENGINE,
        (
            StoryLensType.STRUCTURAL_SHAPE.value,
            StoryLensType.READER_EXPERIENCE.value,
            StoryLensType.COMMON_TROPES.value,
        ),
    ),
    (
        StoryLensType.AESTHETIC_FRAMING,
        "Emotional & aesthetic framing",
        "How the story is meant to feel",
        ArchitectureFacet.AESTHETIC_FRAMING,
        (
            StoryLensType.READER_EXPERIENCE.value,
            StoryLensType.COMMON_TROPES.value,
        ),
    ),
    (
        StoryLensType.COMMON_TROPES,
        "Common tropes",
        "Recurring situations and expectations",
        ArchitectureFacet.TROPE_FAMILY,
        (
            StoryLensType.STORY_ENGINE.value,
            StoryLensType.STRUCTURAL_SHAPE.value,
            StoryLensType.AESTHETIC_FRAMING.value,
        ),
    ),
)


_PATTERN_LIBRARY: tuple[
    tuple[tuple[str, ...], str, str, str, str],
    ...,
] = (
    (
        ("investigation", "mystery", "revelation"),
        "Progressive revelation",
        "A central question produces accumulating clues or contradictions, competing explanations, and a later revelation or confrontation.",
        "Curiosity → suspicion → hypothesis → revelation",
        "The reader is invited to notice inconsistencies, form explanations, revise them, and experience payoff when hidden causes become legible.",
    ),
    (
        ("danger", "pursuit", "thriller"),
        "Escalating pursuit",
        "Pressure rises through threat, pursuit, narrowing options, and confrontation rather than through a static sequence of obstacles.",
        "Anticipation → pressure → urgency → release",
        "The reader experience is driven by shrinking time or safety margins and increasingly consequential choices.",
    ),
    (
        ("dread", "monstrous", "horror"),
        "Encroaching threat",
        "Normality loses safety as the threat becomes harder to explain, avoid, or contain, culminating in confrontation, survival, or irreversible knowledge.",
        "Unease → dread → fear → confrontation",
        "The reader should feel safety erode as uncertainty becomes threat and threat becomes unavoidable consequence.",
    ),
    (
        ("desire", "courtship", "romance", "commitment"),
        "Relationship progression",
        "Attraction or desire meets obstacles, misunderstanding, vulnerability, and a consequential choice about intimacy or commitment.",
        "Attraction → uncertainty → intimacy → commitment choice",
        "The reader tracks changing emotional proximity and the cost of becoming more or less vulnerable.",
    ),
    (
        ("public/private", "identity pressure", "superhero"),
        "Dual-life collision",
        "Public and private obligations intensify until the separation between identities becomes difficult to preserve and consequences cross the boundary.",
        "Aspiration → pressure → exposure anxiety → consequence",
        "The reader experiences the gap between who the protagonist appears to be and what competing identities demand.",
    ),
    (
        ("wonder", "fantastic", "speculative"),
        "Discovery and consequence",
        "The story introduces an extraordinary rule or possibility, tests its boundaries, and turns understanding that rule into escalating consequence.",
        "Curiosity → awe → rule discovery → consequence",
        "The reader learns the world's unusual possibilities alongside the protagonist and then sees those possibilities acquire costs.",
    ),
)


def _components_for(
    analysis: NarrativeArchitectureAnalysis,
    facet: ArchitectureFacet,
) -> tuple:
    return tuple(component for component in analysis.components if component.facet is facet)


def _active_components(
    analysis: NarrativeArchitectureAnalysis,
    facet: ArchitectureFacet,
) -> tuple:
    return tuple(
        component
        for component in _components_for(analysis, facet)
        if component.activation is ArchitectureActivation.ACTIVE
        and component.role in {ArchitectureRole.PRIMARY, ArchitectureRole.SUPPORTING}
    )


def _item(component) -> StoryLensItem:
    return StoryLensItem(
        component_id=component.component_id,
        label=component.label,
        role=component.role.value,
        certainty=component.certainty.value,
        activation=component.activation.value,
        review_state=component.review_state.value,
        rationale=component.rationale,
        evidence=component.evidence,
        alternatives=component.alternatives,
    )


def _component_state(components: tuple, *, stale: bool) -> StoryLensState:
    if stale:
        return StoryLensState.STALE
    active = tuple(
        component
        for component in components
        if component.activation is ArchitectureActivation.ACTIVE
        and component.role in {ArchitectureRole.PRIMARY, ArchitectureRole.SUPPORTING}
    )
    if not active:
        return StoryLensState.UNESTABLISHED
    if any(component.review_state is ArchitectureReviewState.AUTHOR_MODIFIED for component in active):
        return StoryLensState.AUTHOR_MODIFIED
    if active and all(
        component.review_state is ArchitectureReviewState.AUTHOR_CONFIRMED
        for component in active
    ):
        return StoryLensState.AUTHOR_CONFIRMED
    return StoryLensState.INFERRED


def _labels(components: tuple) -> tuple[str, ...]:
    return tuple(component.label for component in components)


def _join(labels: tuple[str, ...]) -> str:
    if not labels:
        return ""
    if len(labels) == 1:
        return labels[0]
    if len(labels) == 2:
        return f"{labels[0]} · {labels[1]}"
    return " · ".join(labels)


def _direct_lens(
    analysis: NarrativeArchitectureAnalysis,
    *,
    lens_type: StoryLensType,
    title: str,
    eyebrow: str,
    facet: ArchitectureFacet,
    related_lens_ids: tuple[str, ...],
    stale: bool,
) -> StoryLensProjection:
    components = _components_for(analysis, facet)
    active = _active_components(analysis, facet)
    state = _component_state(components, stale=stale)
    if active:
        summary = _join(_labels(active))
        detail = " ".join(component.rationale for component in active)
    elif components:
        summary = "Not established yet"
        detail = (
            "Auteur has possible interpretations for this lens, but they remain "
            "suppressed or uncertain until the author keeps, restores, or replaces them."
        )
    else:
        summary = "Not established yet"
        detail = (
            "The premise does not yet support a bounded interpretation for this lens. "
            "Auteur should leave it open rather than manufacture certainty."
        )
    return StoryLensProjection(
        lens_id=lens_type.value,
        lens_type=lens_type,
        title=title,
        eyebrow=eyebrow,
        summary=summary,
        detail=detail,
        state=state,
        source_component_ids=tuple(component.component_id for component in components),
        items=tuple(_item(component) for component in components),
        related_lens_ids=related_lens_ids,
        refinement_mode="direct",
    )


def _pattern_basis(analysis: NarrativeArchitectureAnalysis) -> tuple[str, tuple[str, ...]]:
    components = (
        *_active_components(analysis, ArchitectureFacet.NARRATIVE_ENGINE),
        *_active_components(analysis, ArchitectureFacet.GENRE_CONSTELLATION),
    )
    ordered = sorted(
        components,
        key=lambda component: (
            component.role is not ArchitectureRole.PRIMARY,
            component.component_id,
        ),
    )
    text = " ".join(component.label.casefold() for component in ordered)
    return text, tuple(component.component_id for component in ordered)


def _matched_pattern(analysis: NarrativeArchitectureAnalysis):
    text, component_ids = _pattern_basis(analysis)
    for keywords, structure_title, structure_detail, reader_summary, reader_detail in _PATTERN_LIBRARY:
        if any(keyword in text for keyword in keywords):
            return (
                structure_title,
                structure_detail,
                reader_summary,
                reader_detail,
                component_ids,
            )
    return None


def _structural_lens(
    analysis: NarrativeArchitectureAnalysis,
    *,
    stale: bool,
) -> StoryLensProjection:
    match = _matched_pattern(analysis)
    if match is None:
        state = StoryLensState.STALE if stale else StoryLensState.UNESTABLISHED
        return StoryLensProjection(
            lens_id=StoryLensType.STRUCTURAL_SHAPE.value,
            lens_type=StoryLensType.STRUCTURAL_SHAPE,
            title="Structural shape",
            eyebrow="A likely story pattern, not an outline",
            summary="Not established yet",
            detail=(
                "The current premise interpretation does not support one bounded structural "
                "shape. Story Discovery should preserve materially different possibilities."
            ),
            state=state,
            related_lens_ids=(
                StoryLensType.STORY_ENGINE.value,
                StoryLensType.COMMON_TROPES.value,
            ),
            refinement_mode="through_sources",
        )
    structure_title, structure_detail, _reader_summary, _reader_detail, component_ids = match
    return StoryLensProjection(
        lens_id=StoryLensType.STRUCTURAL_SHAPE.value,
        lens_type=StoryLensType.STRUCTURAL_SHAPE,
        title="Structural shape",
        eyebrow="A likely story pattern, not an outline",
        summary=structure_title,
        detail=structure_detail,
        state=StoryLensState.STALE if stale else StoryLensState.INFERRED,
        source_component_ids=component_ids,
        related_lens_ids=(
            StoryLensType.STORY_ENGINE.value,
            StoryLensType.COMMON_TROPES.value,
            StoryLensType.READER_EXPERIENCE.value,
        ),
        refinement_mode="through_sources",
    )


def _reader_lens(
    analysis: NarrativeArchitectureAnalysis,
    *,
    stale: bool,
) -> StoryLensProjection:
    match = _matched_pattern(analysis)
    framing = _labels(_active_components(analysis, ArchitectureFacet.AESTHETIC_FRAMING))
    if match is None:
        state = StoryLensState.STALE if stale else StoryLensState.UNESTABLISHED
        return StoryLensProjection(
            lens_id=StoryLensType.READER_EXPERIENCE.value,
            lens_type=StoryLensType.READER_EXPERIENCE,
            title="Reader experience",
            eyebrow="The emotional progression Auteur currently expects",
            summary="Not established yet",
            detail=(
                "The premise does not yet support one bounded reader-experience progression. "
                "Auteur should keep this open until the engine or framing becomes clearer."
            ),
            state=state,
            related_lens_ids=(
                StoryLensType.STORY_ENGINE.value,
                StoryLensType.AESTHETIC_FRAMING.value,
            ),
            refinement_mode="through_sources",
        )
    _structure_title, _structure_detail, reader_summary, reader_detail, component_ids = match
    if framing:
        reader_detail += f" The active aesthetic framing is {_join(framing)}."
        component_ids = tuple(
            dict.fromkeys(
                (*component_ids, *(
                    component.component_id
                    for component in _active_components(
                        analysis, ArchitectureFacet.AESTHETIC_FRAMING
                    )
                ))
            )
        )
    return StoryLensProjection(
        lens_id=StoryLensType.READER_EXPERIENCE.value,
        lens_type=StoryLensType.READER_EXPERIENCE,
        title="Reader experience",
        eyebrow="The emotional progression Auteur currently expects",
        summary=reader_summary,
        detail=reader_detail,
        state=StoryLensState.STALE if stale else StoryLensState.INFERRED,
        source_component_ids=component_ids,
        related_lens_ids=(
            StoryLensType.STORY_ENGINE.value,
            StoryLensType.AESTHETIC_FRAMING.value,
            StoryLensType.STRUCTURAL_SHAPE.value,
        ),
        refinement_mode="through_sources",
    )


def build_story_lenses(
    *,
    analysis: NarrativeArchitectureAnalysis,
    analysis_current: bool,
) -> tuple[tuple[StoryLensProjection, ...], StoryLensDiagnostics]:
    """Project the complete default first-screen lens set from one analysis."""

    stale = analysis.stale or not analysis_current
    direct = tuple(
        _direct_lens(
            analysis,
            lens_type=lens_type,
            title=title,
            eyebrow=eyebrow,
            facet=facet,
            related_lens_ids=related,
            stale=stale,
        )
        for lens_type, title, eyebrow, facet, related in _DIRECT_LENS_CONFIG
    )
    by_id = {lens.lens_id: lens for lens in direct}
    lenses = (
        by_id[StoryLensType.STORY_ENGINE.value],
        by_id[StoryLensType.AESTHETIC_FRAMING.value],
        by_id[StoryLensType.COMMON_TROPES.value],
        _structural_lens(analysis, stale=stale),
        _reader_lens(analysis, stale=stale),
    )
    active_count = sum(
        component.activation is ArchitectureActivation.ACTIVE
        for component in analysis.components
    )
    suppressed_count = len(analysis.components) - active_count
    unestablished = tuple(
        lens.lens_id
        for lens in lenses
        if lens.state is StoryLensState.UNESTABLISHED
    )
    needs_attention = tuple(
        lens.lens_id
        for lens in lenses
        if lens.state in {StoryLensState.UNESTABLISHED, StoryLensState.STALE}
        or any(item.certainty == "uncertain" for item in lens.items)
    )
    diagnostics = StoryLensDiagnostics(
        analysis_id=analysis.analysis_id,
        analyzer_id=analysis.analyzer_id,
        source_mode=(
            "deterministic_fallback"
            if analysis.provider_id is None
            else "provider"
        ),
        stale=stale,
        active_component_count=active_count,
        suppressed_component_count=suppressed_count,
        author_adjustment_count=len(analysis.adjustments),
        unestablished_lens_ids=unestablished,
        needs_attention_lens_ids=needs_attention,
    )
    return lenses, diagnostics
