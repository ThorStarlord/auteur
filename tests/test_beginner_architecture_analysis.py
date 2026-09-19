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


import json

from auteur.beginner.architecture_analysis import (
    ArchitectureAnalysisError,
    DeterministicArchitectureAnalyzer,
    ProviderArchitectureAnalyzer,
    ResilientArchitectureAnalyzer,
    analysis_basis_fingerprint,
    premise_fingerprint,
)
from auteur.llm import LLMResponse
from tests.fixtures.beginner_hybrid_mystery import HYBRID_MYSTERY_PREMISE


class FakeClient:
    def __init__(self, responses: list[LLMResponse]) -> None:
        self.responses = list(responses)
        self.requests = []

    def complete(self, request):
        self.requests.append(request)
        return self.responses.pop(0)


def _valid_provider_json() -> str:
    return json.dumps(
        {
            "summary": "A superhero relationship-betrayal mystery.",
            "components": [
                {
                    "facet": "genre_constellation",
                    "label": "Mystery",
                    "role": "primary",
                    "certainty": "clear",
                    "rationale": "The premise explicitly calls for a fair mystery.",
                    "evidence": [{"label": "genre", "excerpt": "fair mystery"}],
                    "alternatives": [],
                },
                {
                    "facet": "aesthetic_framing",
                    "label": "Erotic betrayal melodrama",
                    "role": "supporting",
                    "certainty": "uncertain",
                    "rationale": "The premise supports heightened betrayal framing.",
                    "evidence": [{"label": "framing", "excerpt": "erotic-betrayal tension"}],
                    "alternatives": [
                        {
                            "label": "Campy erotic melodrama",
                            "rationale": "Heightened spectacle is plausible but not settled.",
                        }
                    ],
                },
            ],
        }
    )


def test_provider_analysis_returns_one_coherent_interpretation_with_component_alternative() -> None:
    client = FakeClient([LLMResponse(text=_valid_provider_json(), input_tokens=10, output_tokens=20)])
    analyzer = ProviderArchitectureAnalyzer(
        client=client,
        analyzer_id="beginner-architecture",
        analyzer_version="1",
        model_id="fixture-model",
    )
    analysis = analyzer.analyze(premise=HYBRID_MYSTERY_PREMISE, source_provenance=())
    assert analysis.summary == "A superhero relationship-betrayal mystery."
    framing = next(c for c in analysis.components if c.facet is ArchitectureFacet.AESTHETIC_FRAMING)
    assert framing.label == "Erotic betrayal melodrama"
    assert [alt.label for alt in framing.alternatives] == ["Campy erotic melodrama"]
    assert framing.activation is ArchitectureActivation.SUPPRESSED
    assert framing.derivation is ArchitectureDerivation.MODEL_INFERENCE


def test_provider_evidence_excerpt_must_come_from_premise() -> None:
    payload = json.loads(_valid_provider_json())
    payload["components"][0]["evidence"][0]["excerpt"] = "invented quote"
    client = FakeClient([LLMResponse(text=json.dumps(payload), input_tokens=1, output_tokens=1)])
    analyzer = ProviderArchitectureAnalyzer(client, "beginner-architecture", "1", "fixture-model")
    with pytest.raises(ArchitectureAnalysisError, match="evidence excerpt"):
        analyzer.analyze(premise="A hero investigates betrayal.", source_provenance=())


def test_provider_does_not_get_to_assign_derivation_or_authority() -> None:
    payload = json.loads(_valid_provider_json())
    payload["components"][0]["derivation"] = "author_added"
    client = FakeClient([LLMResponse(text=json.dumps(payload), input_tokens=1, output_tokens=1)])
    analyzer = ProviderArchitectureAnalyzer(client, "beginner-architecture", "1", "fixture-model")
    with pytest.raises(ArchitectureAnalysisError, match="malformed"):
        analyzer.analyze(premise=HYBRID_MYSTERY_PREMISE, source_provenance=())


def test_deterministic_fallback_does_not_invent_erotic_psychology() -> None:
    analysis = DeterministicArchitectureAnalyzer().analyze(
        premise="A superhero investigates a relationship betrayal.",
        source_provenance=(),
    )
    labels = {component.label.casefold() for component in analysis.components}
    assert "superhero fiction" in labels
    assert "mystery" in labels
    assert "relationship betrayal" in labels
    assert not any("erotic" in label for label in labels)
    assert analysis.availability_note is not None


def test_resilient_analyzer_falls_back_after_malformed_rich_analysis() -> None:
    primary = ProviderArchitectureAnalyzer(
        FakeClient([LLMResponse(text="{not json", input_tokens=1, output_tokens=1)]),
        "beginner-architecture",
        "1",
        "fixture-model",
    )
    analyzer = ResilientArchitectureAnalyzer(
        primary=primary,
        fallback=DeterministicArchitectureAnalyzer(),
    )
    analysis = analyzer.analyze(
        premise="A superhero investigates a relationship betrayal.",
        source_provenance=(),
    )
    assert analysis.availability_note == (
        "Rich narrative interpretation was unavailable; showing the bounded explicit-signal fallback."
    )
    assert not any("erotic" in component.label.casefold() for component in analysis.components)


def test_analysis_fingerprints_are_stable_and_semantic() -> None:
    first = premise_fingerprint("A hero   investigates.\n")
    second = premise_fingerprint("A hero investigates.")
    assert first == second
    assert analysis_basis_fingerprint(HYBRID_ANALYSIS) == analysis_basis_fingerprint(HYBRID_ANALYSIS)
