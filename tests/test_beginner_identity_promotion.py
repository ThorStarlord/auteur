from __future__ import annotations

from auteur.beginner.promotion import identity_semantic_projection
from auteur.identity import StoryIdentity
from tests.fixtures.beginner_hybrid_mystery import (
    HYBRID_SELECTED_IDENTITY,
    app_after_direction_acceptance,
)


def test_identity_preview_starts_from_selected_discovery_candidate(tmp_path) -> None:
    app = app_after_direction_acceptance(tmp_path)
    preview = app.projection().mapping_preview
    assert preview is not None
    assert preview.candidate_identity.core_answer == HYBRID_SELECTED_IDENTITY.core_answer
    assert (
        preview.candidate_identity.central_engine.conflict
        == HYBRID_SELECTED_IDENTITY.central_engine.conflict
    )
    assert preview.current_identity != preview.candidate_identity
    assert preview.ready_to_accept is True


def test_accepting_identity_is_first_canonical_identity_write(tmp_path) -> None:
    app = app_after_direction_acceptance(tmp_path)
    before = app.projection()
    assert before.mapping_preview is not None
    assert not (tmp_path / "story_identity.yaml").exists()
    result = app.accept_story_identity(
        command_id="accept-identity",
        expected_session_version=before.session_version,
    )
    assert result.accepted is True
    canonical = StoryIdentity.from_yaml(tmp_path / "story_identity.yaml")
    assert (
        canonical.central_engine.conflict
        == before.mapping_preview.candidate_identity.central_engine.conflict
    )


def test_identity_semantic_projection_excludes_advisory_metadata() -> None:
    projection = identity_semantic_projection(HYBRID_SELECTED_IDENTITY)
    assert set(projection) == {
        "core_answer",
        "target_experience",
        "story_type",
        "central_engine",
        "architecture_preferences",
        "hard_constraints",
        "not_this",
        "open_questions",
        "characters",
        "genre_profile",
    }
    advisory_change = HYBRID_SELECTED_IDENTITY.model_copy(
        update={
            "confidence": 0.1,
            "why_this_is_best": "Different advisory rationale.",
            "alternatives": ["Different generated alternative."],
        }
    )
    assert identity_semantic_projection(advisory_change) == projection


def test_promotion_preview_classifies_visible_loss_and_provenance(tmp_path) -> None:
    preview = app_after_direction_acceptance(tmp_path).projection().mapping_preview
    assert preview is not None
    assert "core_answer" in preview.becomes_canonical
    assert preview.preserved_as_provenance
    assert isinstance(preview.unresolved_not_representable, tuple)
