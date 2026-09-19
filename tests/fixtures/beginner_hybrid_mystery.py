"""Sanitized deterministic hybrid-composition fixture."""

from __future__ import annotations

from pathlib import Path

from auteur.beginner.application import BeginnerWorkspaceApplication
from auteur.beginner.contracts import (
    DimensionCategory,
    DimensionOrigin,
    DimensionStatus,
    WorkingComposition,
    WorkingDimension,
)
from auteur.story_design_packs.models import PackProvenance


HYBRID_MYSTERY_PREMISE = (
    "A respected superhero discovers that a public institution is hiding a betrayal, "
    "and the explanation must remain non-supernatural."
)


def hybrid_composition() -> WorkingComposition:
    superhero = PackProvenance(pack_id="superhero", version="0.1.0", content_hash="sha256:superhero-fixture")
    return WorkingComposition(
        workspace_id="hybrid-mystery",
        composition_id="hybrid-composition-1",
        schema_version=1,
        dimensions=(
            WorkingDimension(
                dimension_id="superhero-world",
                category=DimensionCategory.SETTING_WORLD,
                origin=DimensionOrigin.DETECTED_FROM_PACK,
                status=DimensionStatus.CONFIRMED,
                label="Superhero public identity",
                source_provenance=(superhero,),
                confirmed_by_author=True,
            ),
            WorkingDimension(
                dimension_id="relationship-lens",
                category=DimensionCategory.RELATIONSHIP_THEMATIC,
                origin=DimensionOrigin.AUTHOR_DEFINED,
                status=DimensionStatus.CONFIRMED,
                label="Relationship betrayal tension",
                author_rationale="The mystery should pressure trust inside a relationship.",
                confirmed_by_author=True,
            ),
        ),
    )


def create_hybrid_app(tmp_path: Path) -> BeginnerWorkspaceApplication:
    app = BeginnerWorkspaceApplication(tmp_path, "hybrid-mystery")
    app.create_workspace(
        command_id="create-hybrid-mystery",
        project_id="hybrid-project",
        premise=HYBRID_MYSTERY_PREMISE,
        guidance_genre="mystery",
    )
    composition = app.projection().working_composition
    assert composition is not None
    for dimension in composition.dimensions:
        app.confirm_dimension(
            dimension_id=dimension.dimension_id,
            rationale=f"Confirmed {dimension.label} for the hybrid qualification fixture.",
            expected_session_version=app.projection().session_version,
        )
    return app
