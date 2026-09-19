from __future__ import annotations

from pydantic import ValidationError
import pytest

from auteur.beginner.architecture_models import (
    ArchitectureActivation,
    ArchitectureAlternative,
    ArchitectureCertainty,
    ArchitectureComponent,
    ArchitectureDerivation,
    ArchitectureFacet,
    ArchitectureReviewState,
    ArchitectureRole,
    NarrativeArchitectureAnalysis,
)
from auteur.beginner.contracts import SessionEnvelope
from tests.fixtures.beginner_hybrid_mystery import HYBRID_ANALYSIS


def test_component_keeps_epistemic_axes_independent() -> None:
    component = ArchitectureComponent(
        component_id="framing:camp",
        facet=ArchitectureFacet.AESTHETIC_FRAMING,
        label="Campy melodrama",
        derivation=ArchitectureDerivation.MODEL_INFERENCE,
        role=ArchitectureRole.SUPPORTING,
        certainty=ArchitectureCertainty.CLEAR,
        activation=ArchitectureActivation.ACTIVE,
        review_state=ArchitectureReviewState.AUTHOR_CONFIRMED,
        rationale="The author confirmed a model-inferred framing.",
    )
    assert component.derivation is ArchitectureDerivation.MODEL_INFERENCE
    assert component.certainty is ArchitectureCertainty.CLEAR
    assert component.review_state is ArchitectureReviewState.AUTHOR_CONFIRMED
    assert component.authority_status == "DERIVED / NOT CANON"


def test_component_alternatives_require_uncertainty() -> None:
    with pytest.raises(ValidationError, match="alternatives are only valid"):
        ArchitectureComponent(
            component_id="framing:camp",
            facet=ArchitectureFacet.AESTHETIC_FRAMING,
            label="Campy melodrama",
            derivation=ArchitectureDerivation.MODEL_INFERENCE,
            role=ArchitectureRole.SUPPORTING,
            certainty=ArchitectureCertainty.CLEAR,
            rationale="Ambiguity must be explicit.",
            alternatives=(ArchitectureAlternative(label="Psychological realism", rationale="Alternate framing."),),
        )


def test_analysis_rejects_duplicate_component_ids() -> None:
    component = HYBRID_ANALYSIS.components[0]
    with pytest.raises(ValidationError, match="component IDs must be unique"):
        NarrativeArchitectureAnalysis(
            analysis_id="duplicate",
            premise_fingerprint="fingerprint",
            analyzer_id="test",
            analyzer_version="1",
            summary="Duplicate fixture.",
            components=(component, component),
        )


def test_hybrid_fixture_keeps_consequential_uncertainty_suppressed() -> None:
    framing = next(
        component
        for component in HYBRID_ANALYSIS.components
        if component.facet is ArchitectureFacet.AESTHETIC_FRAMING
    )
    assert framing.certainty is ArchitectureCertainty.UNCERTAIN
    assert framing.activation is ArchitectureActivation.SUPPRESSED
    assert framing.authority_status == "DERIVED / NOT CANON"


def test_legacy_session_envelope_without_analysis_remains_valid() -> None:
    original = SessionEnvelope.new(project_id="project", guidance_genre="mystery", premise="A mystery.")
    payload = original.model_dump(mode="json")
    payload.pop("architecture_analysis", None)
    loaded = SessionEnvelope.model_validate(payload)
    assert loaded.architecture_analysis is None
