"""Deterministic proposal and author-confirmation operations for composition."""

from __future__ import annotations

import hashlib
import re
from collections.abc import Iterable

from auteur.beginner.contracts import (
    DimensionCategory,
    DimensionOrigin,
    DimensionProposalSet,
    DimensionStatus,
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
        label=label,
        author_rationale=rationale,
        confirmed_by_author=True,
    )
    return composition.model_copy(update={"dimensions": composition.dimensions + (dimension,)})
