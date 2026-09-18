from auteur.beginner.contracts import (
    DimensionCategory,
    DimensionOrigin,
    DimensionStatus,
    WorkingComposition,
)
from auteur.beginner.dimensions import (
    add_author_dimension,
    confirm_dimension,
    propose_dimensions,
    reject_dimension,
)
from auteur.story_design_packs.models import PackProvenance


HYBRID_MYSTERY_PREMISE = (
    "A respected superhero investigates a betrayal in his marriage as small "
    "inconsistencies suggest a hidden conspiracy."
)


def qualification_sources() -> tuple[PackProvenance, ...]:
    return (
        PackProvenance(pack_id="mystery", version="domain", content_hash="sha256:mystery"),
        PackProvenance(pack_id="superhero", version="0.1.0", content_hash="sha256:superhero"),
        PackProvenance(pack_id="relationship-betrayal", version="author", content_hash="sha256:relationship"),
    )


def empty_composition() -> WorkingComposition:
    return WorkingComposition(
        workspace_id="workspace-1",
        composition_id="composition-1",
        schema_version=1,
        dimensions=(),
    )


def test_proposes_mystery_superhero_and_relationship_dimensions() -> None:
    proposals = propose_dimensions(
        premise=HYBRID_MYSTERY_PREMISE,
        guidance_genre="mystery",
        available_sources=qualification_sources(),
    )

    assert [item.category for item in proposals.proposals] == [
        DimensionCategory.PRIMARY_ENGINE,
        DimensionCategory.SETTING_WORLD,
        DimensionCategory.RELATIONSHIP_THEMATIC,
    ]
    assert all(item.status is DimensionStatus.PROPOSED for item in proposals.proposals)
    assert all(item.detection_evidence for item in proposals.proposals)
    assert all(item.origin is DimensionOrigin.DETECTED_FROM_PACK for item in proposals.proposals)


def test_confirmation_changes_only_working_dimension_state() -> None:
    proposals = propose_dimensions(
        premise=HYBRID_MYSTERY_PREMISE,
        guidance_genre="mystery",
        available_sources=qualification_sources(),
    )
    composition = empty_composition().model_copy(update={"dimensions": proposals.proposals})

    confirmed = confirm_dimension(
        composition,
        proposals.proposals[0].dimension_id,
        rationale="Mystery remains the primary engine.",
    )

    assert confirmed.dimensions[0].status is DimensionStatus.CONFIRMED
    assert confirmed.dimensions[0].confirmed_by_author is True
    assert confirmed.dimensions[0].author_rationale == "Mystery remains the primary engine."
    assert confirmed.workspace_id == composition.workspace_id


def test_rejection_preserves_provenance_and_author_dimension_keeps_exact_label() -> None:
    proposals = propose_dimensions(
        premise=HYBRID_MYSTERY_PREMISE,
        guidance_genre="mystery",
        available_sources=qualification_sources(),
    )
    rejected = reject_dimension(
        empty_composition().model_copy(update={"dimensions": proposals.proposals}),
        proposals.proposals[1].dimension_id,
    )
    authored = add_author_dimension(
        empty_composition(),
        category=DimensionCategory.RELATIONSHIP_THEMATIC,
        label="Erotic betrayal tension",
        rationale="The marriage is the emotional pressure point.",
    )

    rejected_dimension = next(
        dimension for dimension in rejected.dimensions
        if dimension.dimension_id == proposals.proposals[1].dimension_id
    )
    assert rejected_dimension.status is DimensionStatus.REJECTED
    assert rejected_dimension.source_provenance
    assert authored.dimensions[0].label == "Erotic betrayal tension"
    assert authored.dimensions[0].origin is DimensionOrigin.AUTHOR_DEFINED
    assert authored.dimensions[0].status is DimensionStatus.CONFIRMED


def test_detection_does_not_propose_unrelated_supporting_dimensions() -> None:
    proposals = propose_dimensions(
        premise="A detective solves a locked-room murder in a remote hotel.",
        guidance_genre="mystery",
        available_sources=qualification_sources(),
    )

    assert [item.category for item in proposals.proposals] == [DimensionCategory.PRIMARY_ENGINE]
