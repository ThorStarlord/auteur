from __future__ import annotations

from auteur.beginner.discovery import StoryDiscoveryRecommender, UnavailableDiscoveryRecommender
from auteur.beginner.discovery_models import DiscoveryRecommendationStatus
from auteur.llm import LLMRequest, RetriableError
from tests.fixtures.beginner_hybrid_mystery import (
    HYBRID_ANALYSIS,
    HYBRID_MYSTERY_PREMISE,
    HybridStoryDiscoveryClient,
)


def test_beginner_discovery_returns_one_recommended_direction_and_real_alternatives() -> None:
    scripted_client = HybridStoryDiscoveryClient()
    service = StoryDiscoveryRecommender(client=scripted_client)
    result = service.recommend(premise=HYBRID_MYSTERY_PREMISE, analysis=HYBRID_ANALYSIS)
    assert result.status is DiscoveryRecommendationStatus.READY
    assert result.recommended_direction_id is not None
    assert len(result.directions) >= 2
    recommended = result.direction(result.recommended_direction_id)
    assert recommended.identity_candidate.story_type.genre.value == "mystery"
    assert "superhero" in recommended.architecture_summary.casefold()
    assert result.authority_status == "DERIVED / NOT CANON"


def test_discovery_unavailable_does_not_invent_story_directions() -> None:
    result = UnavailableDiscoveryRecommender(
        reason="No reasoning provider configured."
    ).recommend(premise=HYBRID_MYSTERY_PREMISE, analysis=HYBRID_ANALYSIS)
    assert result.status is DiscoveryRecommendationStatus.UNAVAILABLE
    assert result.directions == ()
    assert result.recommended_direction_id is None


class AlwaysRetriableErrorClient:
    def complete(self, request: LLMRequest):
        del request
        raise RetriableError("provider unavailable")


def test_story_discovery_provider_failure_returns_unavailable() -> None:
    service = StoryDiscoveryRecommender(client=AlwaysRetriableErrorClient())
    result = service.recommend(
        premise=HYBRID_MYSTERY_PREMISE,
        analysis=HYBRID_ANALYSIS,
    )
    assert result.status is DiscoveryRecommendationStatus.UNAVAILABLE
    assert result.recommended_direction_id is None
    assert result.directions == ()
    assert "temporarily unavailable" in result.rationale.casefold()


def test_design_context_marks_analysis_as_derived_not_canon() -> None:
    client = HybridStoryDiscoveryClient()
    StoryDiscoveryRecommender(client=client).recommend(
        premise=HYBRID_MYSTERY_PREMISE,
        analysis=HYBRID_ANALYSIS,
    )
    generation_request = client.calls[0]
    assert "derived working guidance, not canon" in generation_request.system.casefold()
    assert "erotic betrayal melodrama" in generation_request.system.casefold()
