"""Sanitized deterministic hybrid premise fixture shared by beginner-flow tests."""

from __future__ import annotations

from pathlib import Path
import json

import yaml

from auteur.beginner.application import BeginnerWorkspaceApplication
from auteur.beginner.architecture_analysis import analysis_basis_fingerprint, premise_fingerprint
from auteur.beginner.architecture_models import (
    ArchitectureActivation,
    ArchitectureAlternative,
    ArchitectureCertainty,
    ArchitectureComponent,
    ArchitectureDerivation,
    ArchitectureEvidence,
    ArchitectureFacet,
    ArchitectureRole,
    NarrativeArchitectureAnalysis,
)
from auteur.beginner.contracts import (
    DimensionCategory,
    DimensionOrigin,
    DimensionStatus,
    WorkingComposition,
    WorkingDimension,
)
from auteur.beginner.discovery import DiscoveryRecommender
from auteur.beginner.discovery_models import (
    DiscoveryDirection,
    DiscoveryRecommendation,
    DiscoveryRecommendationStatus,
)
from auteur.blueprint import Genre, StoryMode, TargetExperience
from auteur.identity import HighLevelCentralEngine, StoryIdentity, StoryType
from auteur.llm import LLMRequest, LLMResponse
from auteur.story_design_packs.models import PackProvenance


HYBRID_MYSTERY_PREMISE = (
    "A celebrated masked superhero begins investigating inconsistencies around an intimate partner "
    "and a powerful rival. Each clue threatens the hero's secret public identity and changes how "
    "the hero understands trust, jealousy, and possible relationship betrayal. The story should "
    "remain a fair mystery while treating the private discoveries with erotic-betrayal tension "
    "and heightened melodramatic pressure."
)


REVISED_HYBRID_MYSTERY_PREMISE = (
    "A celebrated masked superhero begins investigating inconsistencies around an intimate partner "
    "and a powerful rival. Each clue threatens the hero's secret public identity and changes how "
    "the hero understands trust, jealousy, and possible relationship betrayal. The story should "
    "remain a fair mystery while treating the private discoveries as campy erotic-betrayal "
    "melodrama rather than psychological realism."
)


def _premise_evidence(label: str, excerpt: str) -> tuple[ArchitectureEvidence, ...]:
    return (ArchitectureEvidence(source_kind="premise", label=label, excerpt=excerpt),)


def hybrid_analysis() -> NarrativeArchitectureAnalysis:
    return NarrativeArchitectureAnalysis(
        analysis_id="analysis:hybrid-mystery:1",
        premise_fingerprint="fixture-premise-fingerprint",
        analyzer_id="beginner-architecture",
        analyzer_version="1",
        provider_id="fixture",
        model_id="fixture-model",
        summary="A superhero relationship-betrayal mystery.",
        components=(
            ArchitectureComponent(
                component_id="genre:mystery",
                facet=ArchitectureFacet.GENRE_CONSTELLATION,
                label="Mystery",
                normalized_concept="mystery",
                derivation=ArchitectureDerivation.PREMISE_EXPLICIT,
                role=ArchitectureRole.PRIMARY,
                certainty=ArchitectureCertainty.CLEAR,
                rationale="The premise explicitly asks to remain a fair mystery.",
                evidence=_premise_evidence("genre", "fair mystery"),
            ),
            ArchitectureComponent(
                component_id="engine:investigation-revelation",
                facet=ArchitectureFacet.NARRATIVE_ENGINE,
                label="Investigation and revelation",
                normalized_concept="investigation_revelation",
                derivation=ArchitectureDerivation.MODEL_INFERENCE,
                role=ArchitectureRole.PRIMARY,
                certainty=ArchitectureCertainty.CLEAR,
                rationale="The protagonist investigates inconsistencies and accumulates clues.",
                evidence=_premise_evidence("engine", "begins investigating inconsistencies"),
            ),
            ArchitectureComponent(
                component_id="genre:superhero",
                facet=ArchitectureFacet.GENRE_CONSTELLATION,
                label="Superhero fiction",
                normalized_concept="superhero",
                derivation=ArchitectureDerivation.PREMISE_EXPLICIT,
                role=ArchitectureRole.SUPPORTING,
                certainty=ArchitectureCertainty.CLEAR,
                rationale="The protagonist is explicitly a masked superhero.",
                evidence=_premise_evidence("genre", "masked superhero"),
            ),
            ArchitectureComponent(
                component_id="world:public-identity",
                facet=ArchitectureFacet.SETTING_WORLD,
                label="Superhero public identity",
                normalized_concept="public_identity",
                derivation=ArchitectureDerivation.MODEL_INFERENCE,
                role=ArchitectureRole.SUPPORTING,
                certainty=ArchitectureCertainty.CLEAR,
                rationale="Clues threaten the boundary between the hero's private and public selves.",
                evidence=_premise_evidence("world", "secret public identity"),
            ),
            ArchitectureComponent(
                component_id="relationship:betrayal",
                facet=ArchitectureFacet.RELATIONSHIP_DYNAMIC,
                label="Relationship betrayal",
                normalized_concept="relationship_betrayal",
                derivation=ArchitectureDerivation.PREMISE_EXPLICIT,
                role=ArchitectureRole.SUPPORTING,
                certainty=ArchitectureCertainty.CLEAR,
                rationale="Possible intimate betrayal is an explicit pressure in the premise.",
                evidence=_premise_evidence("relationship", "possible relationship betrayal"),
            ),
            ArchitectureComponent(
                component_id="framing:erotic-betrayal-melodrama",
                facet=ArchitectureFacet.AESTHETIC_FRAMING,
                label="Erotic betrayal melodrama",
                normalized_concept="erotic_betrayal_melodrama",
                derivation=ArchitectureDerivation.MODEL_INFERENCE,
                role=ArchitectureRole.SUPPORTING,
                certainty=ArchitectureCertainty.UNCERTAIN,
                activation=ArchitectureActivation.SUPPRESSED,
                rationale="The premise supports erotic-betrayal tension and heightened melodrama but not a settled camp treatment.",
                evidence=_premise_evidence("framing", "erotic-betrayal tension"),
                alternatives=(
                    ArchitectureAlternative(
                        label="Campy erotic melodrama",
                        rationale="The premise supports heightened spectacle but does not fully settle comic-camp treatment.",
                    ),
                ),
            ),
            ArchitectureComponent(
                component_id="character:investigator",
                facet=ArchitectureFacet.CHARACTER_FUNCTION,
                label="Protagonist / investigator",
                normalized_concept="protagonist_investigator",
                derivation=ArchitectureDerivation.MODEL_INFERENCE,
                role=ArchitectureRole.SUPPORTING,
                certainty=ArchitectureCertainty.CLEAR,
                rationale="The superhero performs the investigation.",
                evidence=_premise_evidence("character", "superhero begins investigating"),
            ),
            ArchitectureComponent(
                component_id="character:intimate-uncertainty",
                facet=ArchitectureFacet.CHARACTER_FUNCTION,
                label="Intimate partner / uncertainty",
                normalized_concept="intimate_partner_uncertainty",
                derivation=ArchitectureDerivation.MODEL_INFERENCE,
                role=ArchitectureRole.SUPPORTING,
                certainty=ArchitectureCertainty.LIKELY,
                rationale="The intimate partner is a focal source of uncertainty.",
                evidence=_premise_evidence("character", "intimate partner"),
            ),
            ArchitectureComponent(
                component_id="character:rival-disruptor",
                facet=ArchitectureFacet.CHARACTER_FUNCTION,
                label="Rival / disruptor",
                normalized_concept="rival_disruptor",
                derivation=ArchitectureDerivation.MODEL_INFERENCE,
                role=ArchitectureRole.SUPPORTING,
                certainty=ArchitectureCertainty.LIKELY,
                rationale="The powerful rival destabilizes the relationship and investigation.",
                evidence=_premise_evidence("character", "powerful rival"),
            ),
            ArchitectureComponent(
                component_id="trope:secret-identity",
                facet=ArchitectureFacet.TROPE_FAMILY,
                label="Secret identity",
                normalized_concept="secret_identity",
                derivation=ArchitectureDerivation.CURATED_MATCH,
                role=ArchitectureRole.SUPPORTING,
                certainty=ArchitectureCertainty.CLEAR,
                rationale="The premise explicitly invokes a threatened secret public identity.",
                evidence=_premise_evidence("trope", "secret public identity"),
            ),
            ArchitectureComponent(
                component_id="trope:suspicious-behavior",
                facet=ArchitectureFacet.TROPE_FAMILY,
                label="Suspicious behavior",
                normalized_concept="suspicious_behavior",
                derivation=ArchitectureDerivation.CURATED_MATCH,
                role=ArchitectureRole.SUPPORTING,
                certainty=ArchitectureCertainty.LIKELY,
                rationale="Inconsistencies around the partner and rival create suspicious behavior.",
                evidence=_premise_evidence("trope", "inconsistencies"),
            ),
            ArchitectureComponent(
                component_id="trope:revelation-confrontation",
                facet=ArchitectureFacet.TROPE_FAMILY,
                label="Revelation / confrontation",
                normalized_concept="revelation_confrontation",
                derivation=ArchitectureDerivation.MODEL_INFERENCE,
                role=ArchitectureRole.SUPPORTING,
                certainty=ArchitectureCertainty.LIKELY,
                rationale="A fair mystery built on accumulating clues tends toward revelation and confrontation.",
                evidence=_premise_evidence("trope", "Each clue"),
            ),
        ),
    )


HYBRID_ANALYSIS = hybrid_analysis()


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


def create_hybrid_app(
    tmp_path: Path,
    *,
    discovery_recommender: DiscoveryRecommender | None = None,
) -> BeginnerWorkspaceApplication:
    resolved_discovery = discovery_recommender or CountingDiscoveryRecommender()
    app = BeginnerWorkspaceApplication(
        tmp_path,
        "hybrid-mystery",
        architecture_analyzer=StaticArchitectureAnalyzer(HYBRID_ANALYSIS),
        discovery_recommender=resolved_discovery,
    )
    app.create_workspace(
        command_id="create-hybrid-mystery",
        project_id="hybrid-project",
        premise=HYBRID_MYSTERY_PREMISE,
        guidance_genre="mystery",
    )
    return app



class StaticArchitectureAnalyzer:
    def __init__(self, analysis: NarrativeArchitectureAnalysis = HYBRID_ANALYSIS) -> None:
        self.analysis = analysis

    def analyze(
        self,
        *,
        premise: str,
        source_provenance: tuple[PackProvenance, ...],
    ) -> NarrativeArchitectureAnalysis:
        return self.analysis.model_copy(
            update={"premise_fingerprint": premise_fingerprint(premise)}
        )


class CountingArchitectureAnalyzer(StaticArchitectureAnalyzer):
    def __init__(self, analysis: NarrativeArchitectureAnalysis = HYBRID_ANALYSIS) -> None:
        super().__init__(analysis)
        self.calls = 0

    def analyze(
        self,
        *,
        premise: str,
        source_provenance: tuple[PackProvenance, ...],
    ) -> NarrativeArchitectureAnalysis:
        self.calls += 1
        return super().analyze(premise=premise, source_provenance=source_provenance)



HYBRID_SELECTED_IDENTITY = StoryIdentity(
    title="The Hero Who Needs the Truth",
    core_answer=(
        "A masked hero investigates apparent intimate betrayal while every clue "
        "also threatens the boundary between private trust and public identity."
    ),
    target_experience=TargetExperience(
        primary="jealous uncertainty",
        progression="suspicion -> evidence -> painful revelation",
        avoid=[],
    ),
    story_type=StoryType(
        mode=StoryMode.PROCEDURAL,
        genre=Genre.MYSTERY,
        subgenres=["superhero"],
    ),
    central_engine=HighLevelCentralEngine(
        want="Discover what is really happening between the partner and rival.",
        resistance="Secret identities, ambiguous evidence, and fear of what the truth means.",
        conflict="The need for certainty collides with love, jealousy, and heroic reputation.",
        stakes="The relationship, the hero's self-image, and public identity may all collapse.",
        change="The hero must choose how to live with the truth once certainty arrives.",
    ),
)

HYBRID_RELATIONSHIP_IDENTITY = HYBRID_SELECTED_IDENTITY.model_copy(
    update={
        "title": "Trust Under Siege",
        "core_answer": (
            "A relationship-centered psychological drama in which investigation matters "
            "mainly because suspicion changes intimacy and trust."
        ),
        "story_type": HYBRID_SELECTED_IDENTITY.story_type.model_copy(
            update={"mode": StoryMode.INTIMATE}
        ),
        "central_engine": HighLevelCentralEngine(
            want="Preserve the relationship without remaining willfully blind.",
            resistance="Longing, self-deception, and contradictory intimate signals.",
            conflict="The desire for intimacy collides with mounting evidence of betrayal.",
            stakes="Trust may be destroyed even if the feared betrayal is misunderstood.",
            change="The protagonist learns that intimacy cannot be preserved by refusing uncertainty.",
        ),
    }
)

HYBRID_CAMPY_IDENTITY = HYBRID_SELECTED_IDENTITY.model_copy(
    update={
        "title": "Masks, Rivals, and Scandal",
        "core_answer": (
            "A heightened superhero melodrama where escalating suspicious encounters "
            "turn private jealousy into public spectacle."
        ),
        "story_type": HYBRID_SELECTED_IDENTITY.story_type.model_copy(
            update={"mode": StoryMode.COMIC}
        ),
        "central_engine": HighLevelCentralEngine(
            want="Expose the rival before the scandal consumes the hero's relationship.",
            resistance="Public spectacle, theatrical misunderstandings, and secret identities.",
            conflict="The hero's need to control the narrative fuels ever-larger confrontations.",
            stakes="Romance, reputation, and heroic legitimacy become part of the same scandal.",
            change="The hero gives up controlling appearances and confronts the relationship directly.",
        ),
    }
)

HYBRID_DISCOVERY = DiscoveryRecommendation(
    recommendation_id="hybrid-discovery-1",
    source_analysis_id=HYBRID_ANALYSIS.analysis_id,
    source_basis_fingerprint=analysis_basis_fingerprint(HYBRID_ANALYSIS),
    status=DiscoveryRecommendationStatus.READY,
    recommended_direction_id="direction-investigative-betrayal",
    rationale=(
        "Investigation is the strongest causal engine while superhero identity and "
        "relationship betrayal make each clue carry public and intimate consequences."
    ),
    directions=(
        DiscoveryDirection(
            direction_id="direction-investigative-betrayal",
            title=HYBRID_SELECTED_IDENTITY.title,
            summary=HYBRID_SELECTED_IDENTITY.core_answer,
            identity_candidate=HYBRID_SELECTED_IDENTITY,
            architecture_summary="Mystery primary; superhero and relationship-betrayal support.",
            tradeoffs=("Requires fair clue logic while preserving intimate ambiguity.",),
            source_analysis_id=HYBRID_ANALYSIS.analysis_id,
            source_component_ids=tuple(
                component.component_id for component in HYBRID_ANALYSIS.components
            ),
        ),
        DiscoveryDirection(
            direction_id="direction-relationship-drama",
            title=HYBRID_RELATIONSHIP_IDENTITY.title,
            summary=HYBRID_RELATIONSHIP_IDENTITY.core_answer,
            identity_candidate=HYBRID_RELATIONSHIP_IDENTITY,
            architecture_summary="Relationship drama primary; mystery as uncertainty mechanism.",
            tradeoffs=("Reduces puzzle centrality in exchange for deeper psychological focus.",),
            source_analysis_id=HYBRID_ANALYSIS.analysis_id,
            source_component_ids=tuple(
                component.component_id for component in HYBRID_ANALYSIS.components
            ),
        ),
        DiscoveryDirection(
            direction_id="direction-campy-melodrama",
            title=HYBRID_CAMPY_IDENTITY.title,
            summary=HYBRID_CAMPY_IDENTITY.core_answer,
            identity_candidate=HYBRID_CAMPY_IDENTITY,
            architecture_summary="Campy superhero melodrama primary; mystery as suspense support.",
            tradeoffs=("Heightened spectacle weakens detailed psychological realism.",),
            source_analysis_id=HYBRID_ANALYSIS.analysis_id,
            source_component_ids=tuple(
                component.component_id for component in HYBRID_ANALYSIS.components
            ),
        ),
    ),
)


class CountingDiscoveryRecommender:
    def __init__(self, result: DiscoveryRecommendation = HYBRID_DISCOVERY) -> None:
        self.result = result
        self.calls = 0

    def recommend(
        self,
        *,
        premise: str,
        analysis: NarrativeArchitectureAnalysis,
    ) -> DiscoveryRecommendation:
        del premise
        self.calls += 1
        return self.result.model_copy(
            update={
                "source_analysis_id": analysis.analysis_id,
                "source_basis_fingerprint": analysis_basis_fingerprint(analysis),
                "directions": tuple(
                    direction.model_copy(update={"source_analysis_id": analysis.analysis_id})
                    for direction in self.result.directions
                ),
            }
        )


class HybridStoryDiscoveryClient:
    def __init__(self) -> None:
        self._candidate_index = 0
        self.calls: list[LLMRequest] = []

    def complete(self, request: LLMRequest) -> LLMResponse:
        self.calls.append(request)

        if "comparative narrative architect" in request.system:
            payload = {
                "recommendation_status": "recommended",
                "recommendation_basis": "advisory_artistic_preference",
                "recommended_candidate_id": "candidate_1",
                "recommendation_rationale": (
                    "Candidate 1 keeps investigation causal while making superhero identity "
                    "and intimate betrayal consequential."
                ),
                "candidate_tradeoffs": {
                    "candidate_2": "Candidate 2 makes relationship psychology primary.",
                    "candidate_3": "Candidate 3 makes spectacle and melodrama primary.",
                },
            }
            return LLMResponse(
                text=json.dumps(payload),
                input_tokens=1,
                output_tokens=1,
            )

        if "summarizing a story identity" in request.system:
            return LLMResponse(
                text=json.dumps(
                    {
                        "summary": "A distinct hybrid-story direction.",
                        "tradeoffs": ["One governing engine must remain legible."],
                        "risks": ["Supporting dimensions can crowd the primary engine."],
                        "best_for": ["A hybrid mystery with consequential relationship stakes."],
                    }
                ),
                input_tokens=1,
                output_tokens=1,
            )

        identities = (
            HYBRID_SELECTED_IDENTITY,
            HYBRID_RELATIONSHIP_IDENTITY,
            HYBRID_CAMPY_IDENTITY,
        )
        identity = identities[self._candidate_index]
        self._candidate_index += 1
        return LLMResponse(
            text=yaml.safe_dump(identity.model_dump(mode="json"), sort_keys=False),
            input_tokens=1,
            output_tokens=1,
        )



def app_at_discovery(tmp_path: Path) -> BeginnerWorkspaceApplication:
    app = create_hybrid_app(
        tmp_path,
        discovery_recommender=CountingDiscoveryRecommender(HYBRID_DISCOVERY),
    )
    app.continue_from_architecture(
        command_id="hybrid-continue-architecture",
        expected_session_version=app.projection().session_version,
    )
    return app


def app_after_direction_acceptance(tmp_path: Path) -> BeginnerWorkspaceApplication:
    app = app_at_discovery(tmp_path)
    app.select_story_direction(
        direction_id="direction-investigative-betrayal",
        command_id="hybrid-select-direction",
        expected_session_version=app.projection().session_version,
    )
    app.accept_story_direction(
        command_id="hybrid-accept-direction",
        expected_session_version=app.projection().session_version,
    )
    return app
