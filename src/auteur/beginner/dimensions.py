"""Deterministic proposal and author-confirmation operations for composition."""

from __future__ import annotations

import hashlib
import re
from collections.abc import Iterable

from auteur.beginner.architecture_models import (
    ArchitectureActivation,
    ArchitectureDerivation,
    ArchitectureFacet,
    ArchitectureReviewState,
    ArchitectureRole,
    NarrativeArchitectureAnalysis,
)
from auteur.beginner.contracts import (
    DimensionCategory,
    DimensionOrigin,
    DimensionProposalSet,
    DimensionStatus,
    GuidanceActivation,
    WorkingComposition,
    WorkingDimension,
)
from auteur.story_design_packs.models import PackProvenance


def _stable_id(*parts: str) -> str:
    value = "|".join(part.strip().casefold() for part in parts)
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:16]


def _label_for(pack_id: str, category: DimensionCategory) -> str:
    labels = {
        DimensionCategory.PRIMARY_ENGINE: "Mystery investigation",
        DimensionCategory.SETTING_WORLD: "Superhero public identity",
        DimensionCategory.RELATIONSHIP_THEMATIC: "Relationship betrayal tension",
    }
    return labels.get(category, pack_id.replace("-", " ").title())


def _category_for(pack_id: str, guidance_genre: str) -> DimensionCategory | None:
    normalized = pack_id.casefold()
    if normalized == guidance_genre.casefold() or normalized == "mystery":
        return DimensionCategory.PRIMARY_ENGINE
    if "superhero" in normalized or "superhuman" in normalized:
        return DimensionCategory.SETTING_WORLD
    if any(token in normalized for token in ("relationship", "betrayal", "erotic")):
        return DimensionCategory.RELATIONSHIP_THEMATIC
    return None


def _premise_supports(premise: str, category: DimensionCategory) -> bool:
    """Keep supporting proposals tied to evidence in the author's premise."""
    text = premise.casefold()
    if category is DimensionCategory.PRIMARY_ENGINE:
        return True
    if category is DimensionCategory.SETTING_WORLD:
        return any(token in text for token in ("superhero", "superhuman", "masked hero", "cape", "heroic"))
    if category is DimensionCategory.RELATIONSHIP_THEMATIC:
        return any(
            token in text
            for token in (
                "betray",
                "marriage",
                "wife",
                "husband",
                "relationship",
                "jealous",
                "romance",
                "lover",
            )
        )
    return False


def propose_dimensions(
    premise: str,
    guidance_genre: str,
    available_sources: Iterable[PackProvenance],
) -> DimensionProposalSet:
    """Propose relevant dimensions without confirming or mutating canon."""
    sources = tuple(available_sources)
    if not premise.strip():
        raise ValueError("premise must not be blank")
    if not guidance_genre.strip():
        raise ValueError("guidance_genre must not be blank")

    proposals: list[WorkingDimension] = []
    seen_categories: set[DimensionCategory] = set()
    for source in sources:
        category = _category_for(source.pack_id, guidance_genre)
        if category is None or category in seen_categories or not _premise_supports(premise, category):
            continue
        seen_categories.add(category)
        proposals.append(
            WorkingDimension(
                dimension_id=f"detected:{_stable_id(source.pack_id, category.value)}",
                category=category,
                origin=DimensionOrigin.DETECTED_FROM_PACK,
                status=DimensionStatus.PROPOSED,
                label=_label_for(source.pack_id, category),
                detection_evidence=(f"premise evidence supports {category.value}: {source.pack_id}",),
                source_provenance=(source,),
            )
        )

    if _premise_supports(premise, DimensionCategory.RELATIONSHIP_THEMATIC) and DimensionCategory.RELATIONSHIP_THEMATIC not in seen_categories:
        proposals.append(
            WorkingDimension(
                dimension_id=f"inferred:{_stable_id(premise, DimensionCategory.RELATIONSHIP_THEMATIC.value)}",
                category=DimensionCategory.RELATIONSHIP_THEMATIC,
                origin=DimensionOrigin.INFERRED_FROM_STORY,
                status=DimensionStatus.PROPOSED,
                label="Relationship betrayal tension",
                detection_evidence=("premise evidence mentions relationship or betrayal pressure",),
            )
        )

    primary = _category_for(guidance_genre, guidance_genre)
    if primary is not None and primary not in seen_categories:
        source = PackProvenance(
            pack_id=guidance_genre,
            version="guidance",
            content_hash=hashlib.sha256(premise.encode("utf-8")).hexdigest(),
        )
        proposals.insert(
            0,
            WorkingDimension(
                dimension_id=f"detected:{_stable_id(guidance_genre, primary.value)}",
                category=primary,
                origin=DimensionOrigin.DETECTED_FROM_PACK,
                status=DimensionStatus.PROPOSED,
                label=_label_for(guidance_genre, primary),
                detection_evidence=(f"configured guidance genre: {guidance_genre}",),
                source_provenance=(source,),
            ),
        )

    proposals.sort(key=lambda item: (item.category != DimensionCategory.PRIMARY_ENGINE, item.dimension_id))
    return DimensionProposalSet(
        proposals=tuple(proposals),
        source_provenance=sources,
    )


def _replace_dimension(
    composition: WorkingComposition,
    dimension_id: str,
    transform,
) -> WorkingComposition:
    dimensions = tuple(
        transform(dimension) if dimension.dimension_id == dimension_id else dimension
        for dimension in composition.dimensions
    )
    if not any(dimension.dimension_id == dimension_id for dimension in composition.dimensions):
        raise ValueError(f"unknown dimension: {dimension_id}")
    return composition.model_copy(update={"dimensions": dimensions})


def confirm_dimension(
    composition: WorkingComposition,
    dimension_id: str,
    *,
    label: str | None = None,
    rationale: str | None = None,
) -> WorkingComposition:
    return _replace_dimension(
        composition,
        dimension_id,
        lambda dimension: dimension.model_copy(
            update={
                "label": label or dimension.label,
                "author_rationale": rationale,
                "status": DimensionStatus.CONFIRMED,
                "activation": GuidanceActivation.ACTIVE,
                "confirmed_by_author": True,
            }
        ),
    )


def reject_dimension(
    composition: WorkingComposition,
    dimension_id: str,
    *,
    rationale: str | None = None,
) -> WorkingComposition:
    return _replace_dimension(
        composition,
        dimension_id,
        lambda dimension: dimension.model_copy(
            update={
                "author_rationale": rationale,
                "status": DimensionStatus.REJECTED,
                "activation": GuidanceActivation.SUPPRESSED,
                "confirmed_by_author": False,
            }
        ),
    )


def add_author_dimension(
    composition: WorkingComposition,
    *,
    category: DimensionCategory,
    label: str,
    rationale: str,
) -> WorkingComposition:
    if not label.strip() or not rationale.strip():
        raise ValueError("author-defined dimensions require label and rationale")
    normalized = re.sub(r"[^a-z0-9]+", "-", label.casefold()).strip("-")
    dimension = WorkingDimension(
        dimension_id=f"author:{normalized or _stable_id(label, category.value)}",
        category=category,
        origin=DimensionOrigin.AUTHOR_DEFINED,
        status=DimensionStatus.CONFIRMED,
        activation=GuidanceActivation.ACTIVE,
        label=label,
        author_rationale=rationale,
        confirmed_by_author=True,
    )
    return composition.model_copy(update={"dimensions": composition.dimensions + (dimension,)})



def _category_from_component(
    facet: ArchitectureFacet,
    role: ArchitectureRole,
) -> DimensionCategory | None:
    if facet is ArchitectureFacet.NARRATIVE_ENGINE:
        return DimensionCategory.PRIMARY_ENGINE if role is ArchitectureRole.PRIMARY else None
    if facet is ArchitectureFacet.GENRE_CONSTELLATION:
        return DimensionCategory.GENRE_SUBGENRE
    if facet is ArchitectureFacet.AESTHETIC_FRAMING:
        return DimensionCategory.EMOTIONAL_AESTHETIC
    if facet is ArchitectureFacet.RELATIONSHIP_DYNAMIC:
        return DimensionCategory.RELATIONSHIP_THEMATIC
    if facet is ArchitectureFacet.SETTING_WORLD:
        return DimensionCategory.SETTING_WORLD
    return None


def _origin_from_derivation(derivation: ArchitectureDerivation) -> DimensionOrigin:
    if derivation is ArchitectureDerivation.CURATED_MATCH:
        return DimensionOrigin.DETECTED_FROM_PACK
    if derivation is ArchitectureDerivation.AUTHOR_ADDED:
        return DimensionOrigin.AUTHOR_DEFINED
    return DimensionOrigin.INFERRED_FROM_STORY


def _activation_from_architecture(activation: ArchitectureActivation) -> GuidanceActivation:
    return (
        GuidanceActivation.ACTIVE
        if activation is ArchitectureActivation.ACTIVE
        else GuidanceActivation.SUPPRESSED
    )


def composition_from_analysis(
    *,
    workspace_id: str,
    analysis: NarrativeArchitectureAnalysis,
    prior: WorkingComposition | None,
) -> WorkingComposition:
    """Project material active interpretation components into Working Composition."""
    projected: list[WorkingDimension] = []
    for component in analysis.components:
        if component.activation is not ArchitectureActivation.ACTIVE:
            continue
        if component.role not in {ArchitectureRole.PRIMARY, ArchitectureRole.SUPPORTING}:
            continue
        category = _category_from_component(component.facet, component.role)
        if category is None:
            continue
        reviewed = component.review_state is not ArchitectureReviewState.UNREVIEWED
        evidence = tuple(
            item.excerpt or item.label
            for item in component.evidence
            if (item.excerpt or item.label).strip()
        )
        projected.append(
            WorkingDimension(
                dimension_id=f"architecture:{component.component_id}",
                category=category,
                origin=_origin_from_derivation(component.derivation),
                status=DimensionStatus.CONFIRMED if reviewed else DimensionStatus.PROPOSED,
                activation=_activation_from_architecture(component.activation),
                label=component.label,
                author_rationale=component.author_rationale,
                detection_evidence=evidence or (component.rationale,),
                source_provenance=component.source_provenance,
                confirmed_by_author=reviewed,
            )
        )

    projected_ids = {item.dimension_id for item in projected}
    preserved_author_dimensions = ()
    if prior is not None:
        preserved_author_dimensions = tuple(
            item
            for item in prior.dimensions
            if item.origin is DimensionOrigin.AUTHOR_DEFINED and item.dimension_id not in projected_ids
        )

    source_by_key = {
        (source.pack_id, source.version, source.content_hash): source
        for source in analysis.source_provenance
    }
    for dimension in projected:
        for source in dimension.source_provenance:
            source_by_key[(source.pack_id, source.version, source.content_hash)] = source

    return WorkingComposition(
        workspace_id=workspace_id,
        composition_id=(
            prior.composition_id if prior is not None else f"composition:{workspace_id}:1"
        ),
        schema_version=1,
        revision_id=prior.revision_id if prior is not None else None,
        base_canonical_refs=prior.base_canonical_refs if prior is not None else (),
        source_provenance=tuple(source_by_key.values()),
        dimensions=tuple(projected) + preserved_author_dimensions,
        tensions=prior.tensions if prior is not None else (),
        mapping_records=prior.mapping_records if prior is not None else (),
        unmapped_remainders=prior.unmapped_remainders if prior is not None else (),
    )


def active_dimensions(composition: WorkingComposition) -> tuple[WorkingDimension, ...]:
    """Dimensions eligible to influence guidance/mapping independent of author confirmation."""
    return tuple(
        dimension
        for dimension in composition.dimensions
        if dimension.activation is GuidanceActivation.ACTIVE
        and dimension.status not in {DimensionStatus.REJECTED, DimensionStatus.SUPERSEDED}
    )
