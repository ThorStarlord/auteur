"""Sanitized deterministic hybrid premise fixture shared by beginner-flow tests."""

from __future__ import annotations

from pathlib import Path

from auteur.beginner.application import BeginnerWorkspaceApplication
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
from auteur.story_design_packs.models import PackProvenance


HYBRID_MYSTERY_PREMISE = (
    "A celebrated masked superhero begins investigating inconsistencies around an intimate partner "
    "and a powerful rival. Each clue threatens the hero's secret public identity and changes how "
    "the hero understands trust, jealousy, and possible relationship betrayal. The story should "
    "remain a fair mystery while treating the private discoveries with erotic-betrayal tension "
    "and heightened melodramatic pressure."
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
