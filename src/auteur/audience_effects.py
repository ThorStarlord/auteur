"""Mass-Appeal Narrative Architecture (MANA) audience-effect diagnostics.

MANA is a read-only, cross-cutting projection over Auteur's existing narrative
architecture. It does not create canon, validate artistic quality, score mass
appeal, or select a winning story direction.

The initial slice is intentionally evidence-bounded: StoryBlueprint evidence can
support Identity- and Structure-stage findings. Realization-, Expression-, and
completed-work claims remain explicitly not yet assessable until those evidence
surfaces are supplied by a later integration.
"""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, ConfigDict

from auteur.blueprint import StoryBlueprint


class AudienceEvidenceStage(str, Enum):
    IDENTITY = "identity"
    STRUCTURE = "structure"
    REALIZATION = "realization"
    EXPRESSION = "expression"
    COMPLETE = "complete"


class AudienceEffectDimension(str, Enum):
    NARRATIVE_LEGIBILITY = "narrative_legibility"
    MOTIVATIONAL_ATTACHMENT = "motivational_attachment"
    PREDICTIVE_ENGAGEMENT = "predictive_engagement"
    CONSEQUENTIAL_PROGRESSION = "consequential_progression"
    GROUNDED_CREDIBILITY = "grounded_credibility"
    EMOTIONAL_LEGIBILITY = "emotional_legibility"
    AFFECTIVE_COMMITMENT = "affective_commitment"
    PAYOFF_ARCHITECTURE = "payoff_architecture"
    MEMORABILITY = "memorability"
    TRANSMISSION = "transmission"


class AudienceEffectState(str, Enum):
    SUPPORTED = "supported"
    TENSION = "tension"
    UNESTABLISHED = "unestablished"
    NOT_YET_ASSESSABLE = "not_yet_assessable"


class EpistemicBasis(str, Enum):
    EMPIRICAL = "empirical"
    THEORETICAL = "theoretical"
    HEURISTIC = "heuristic"
    PROJECT_EVIDENCE = "project_evidence"


class AudienceEffectFinding(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    dimension: AudienceEffectDimension
    state: AudienceEffectState
    evidence_stage: AudienceEvidenceStage
    summary: str
    evidence: tuple[str, ...] = ()
    limitations: tuple[str, ...] = ()
    epistemic_basis: tuple[EpistemicBasis, ...] = (
        EpistemicBasis.PROJECT_EVIDENCE,
        EpistemicBasis.HEURISTIC,
    )


class AudienceEffectGuidance(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    dimension: AudienceEffectDimension
    action: str
    reason: str
    authority_status: str = "DERIVED / NOT CANON"
    epistemic_basis: tuple[EpistemicBasis, ...] = (
        EpistemicBasis.HEURISTIC,
        EpistemicBasis.PROJECT_EVIDENCE,
    )


class AudienceEffectReport(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    schema_version: int = 1
    architecture: str = "mass_appeal_narrative_architecture"
    authority_status: str = "DERIVED / NOT CANON"
    available_evidence_stage: AudienceEvidenceStage
    findings: tuple[AudienceEffectFinding, ...]
    guidance: tuple[AudienceEffectGuidance, ...] = ()
    claim_ceiling: str = (
        "Qualitative audience-effect architecture analysis only; not a calibrated "
        "probability, artistic-quality verdict, commercial forecast, validator, or score."
    )


def infer_audience_evidence_stage(blueprint: StoryBlueprint) -> AudienceEvidenceStage:
    """Return the highest audience-effect stage supported by Blueprint evidence."""
    if blueprint.story_engine is not None:
        return AudienceEvidenceStage.STRUCTURE
    return AudienceEvidenceStage.IDENTITY


def _not_yet(
    dimension: AudienceEffectDimension,
    required_stage: AudienceEvidenceStage,
    available_stage: AudienceEvidenceStage,
) -> AudienceEffectFinding:
    return AudienceEffectFinding(
        dimension=dimension,
        state=AudienceEffectState.NOT_YET_ASSESSABLE,
        evidence_stage=available_stage,
        summary=f"{dimension.value.replace('_', ' ').title()} requires later-stage evidence.",
        evidence=(),
        limitations=(
            f"Current evidence reaches {available_stage.value}; this dimension requires "
            f"{required_stage.value} evidence.",
        ),
    )


def _narrative_legibility(blueprint: StoryBlueprint, stage: AudienceEvidenceStage) -> AudienceEffectFinding:
    evidence = (
        f"genre = {blueprint.identity.genre.value}",
        f"target_audience = {blueprint.identity.target_audience.value}",
        f"author_intent = {blueprint.identity.author_intent}",
    )
    if blueprint.story_engine is None:
        return AudienceEffectFinding(
            dimension=AudienceEffectDimension.NARRATIVE_LEGIBILITY,
            state=AudienceEffectState.SUPPORTED,
            evidence_stage=stage,
            summary=(
                "The Identity gives the audience-facing concept a recognizable genre, audience, "
                "and author-intent frame."
            ),
            evidence=evidence,
            limitations=(
                "A governing causal engine is not yet available, so scene-to-scene legibility "
                "cannot be inferred.",
            ),
        )

    main = blueprint.story_engine.main_thread
    return AudienceEffectFinding(
        dimension=AudienceEffectDimension.NARRATIVE_LEGIBILITY,
        state=AudienceEffectState.SUPPORTED,
        evidence_stage=stage,
        summary=(
            "The story has both an audience-facing identity and a legible governing engine "
            "with explicit want, resistance, and conflict."
        ),
        evidence=evidence
        + (
            f"want = {main.want.author_text}",
            f"resistance = {main.resistance.author_text}",
            f"conflict = {main.conflict.author_text}",
        ),
    )


def _motivational_attachment(
    blueprint: StoryBlueprint,
    stage: AudienceEvidenceStage,
) -> AudienceEffectFinding:
    if blueprint.story_engine is None:
        return AudienceEffectFinding(
            dimension=AudienceEffectDimension.MOTIVATIONAL_ATTACHMENT,
            state=AudienceEffectState.UNESTABLISHED,
            evidence_stage=stage,
            summary=(
                "The Blueprint does not yet contain explicit structural want and stakes "
                "evidence for motivational attachment."
            ),
            evidence=(f"author_intent = {blueprint.identity.author_intent}",),
            limitations=(
                "Author intent alone is not treated as proof that the audience will understand "
                "what value is pursued, protected, threatened, or lost.",
            ),
        )

    main = blueprint.story_engine.main_thread
    return AudienceEffectFinding(
        dimension=AudienceEffectDimension.MOTIVATIONAL_ATTACHMENT,
        state=AudienceEffectState.SUPPORTED,
        evidence_stage=stage,
        summary=(
            "The governing engine names both a pursued outcome and what can be lost, giving "
            "the audience a concrete motivational value to track."
        ),
        evidence=(
            f"want = {main.want.author_text}",
            f"stakes = {main.stakes.author_text}",
        ),
        limitations=(
            "This establishes structural support, not evidence that real readers will care.",
        ),
    )


def _predictive_engagement(
    blueprint: StoryBlueprint,
    stage: AudienceEvidenceStage,
) -> AudienceEffectFinding:
    if blueprint.story_engine is None:
        return _not_yet(
            AudienceEffectDimension.PREDICTIVE_ENGAGEMENT,
            AudienceEvidenceStage.STRUCTURE,
            stage,
        )

    main = blueprint.story_engine.main_thread
    evidence = (
        f"want = {main.want.author_text}",
        f"resistance = {main.resistance.author_text}",
        f"conflict = {main.conflict.author_text}",
    )
    if blueprint.tension_waveform.target_curve:
        evidence += (
            f"tension_targets = {len(blueprint.tension_waveform.target_curve)}",
        )
        state = AudienceEffectState.SUPPORTED
        summary = (
            "Goal, resistance, conflict, and planned pressure variation give the audience "
            "enough structure to form and revise outcome expectations."
        )
        limitations = (
            "A Blueprint cannot prove that individual scenes preserve useful uncertainty.",
        )
    else:
        state = AudienceEffectState.TENSION
        summary = (
            "The governing conflict creates a forward outcome question, but the Blueprint "
            "does not yet show an explicit pressure/tension progression."
        )
        limitations = (
            "Predictive engagement is inferred from structural forces rather than realized scene sequence.",
        )
    return AudienceEffectFinding(
        dimension=AudienceEffectDimension.PREDICTIVE_ENGAGEMENT,
        state=state,
        evidence_stage=stage,
        summary=summary,
        evidence=evidence,
        limitations=limitations,
    )


def _consequential_progression(
    blueprint: StoryBlueprint,
    stage: AudienceEvidenceStage,
) -> AudienceEffectFinding:
    if blueprint.story_engine is None:
        return _not_yet(
            AudienceEffectDimension.CONSEQUENTIAL_PROGRESSION,
            AudienceEvidenceStage.STRUCTURE,
            stage,
        )

    main = blueprint.story_engine.main_thread
    evidence = (
        f"change = {main.change.author_text}",
        f"resistance = {main.resistance.author_text}",
    )
    if blueprint.tension_waveform.target_curve:
        evidence += (
            f"planned_tension_targets = {len(blueprint.tension_waveform.target_curve)}",
        )
    return AudienceEffectFinding(
        dimension=AudienceEffectDimension.CONSEQUENTIAL_PROGRESSION,
        state=AudienceEffectState.TENSION,
        evidence_stage=stage,
        summary=(
            "The structure declares change and pressure, but a Blueprint alone does not prove "
            "that each major attempt changes the next option set rather than merely repeating obstacles."
        ),
        evidence=evidence,
        limitations=(
            "Event-level cause/consequence chaining belongs to later Structure detail and Realization evidence.",
        ),
    )


def _emotional_legibility(
    blueprint: StoryBlueprint,
    stage: AudienceEvidenceStage,
) -> AudienceEffectFinding:
    target = blueprint.identity.target_experience
    emotional_arc = blueprint.emotional_design.overall_emotional_arc
    if target is None:
        return AudienceEffectFinding(
            dimension=AudienceEffectDimension.EMOTIONAL_LEGIBILITY,
            state=AudienceEffectState.TENSION,
            evidence_stage=stage,
            summary=(
                "The Blueprint has an emotional design, but no explicit reader-facing target "
                "experience anchors what the audience is meant to feel."
            ),
            evidence=(f"overall_emotional_arc = {emotional_arc}",),
            limitations=(
                "Character emotion and authorial mood language are not substitutes for a reader-experience promise.",
            ),
        )

    return AudienceEffectFinding(
        dimension=AudienceEffectDimension.EMOTIONAL_LEGIBILITY,
        state=AudienceEffectState.SUPPORTED,
        evidence_stage=stage,
        summary=(
            "Reader-facing emotional promise and macro emotional design are both explicit."
        ),
        evidence=(
            f"target_experience.primary = {target.primary}",
            f"target_experience.progression = {target.progression}",
            f"overall_emotional_arc = {emotional_arc}",
        ),
        limitations=(
            "This does not establish whether realized scenes or prose successfully produce the intended feeling.",
        ),
    )


def _payoff_architecture(
    blueprint: StoryBlueprint,
    stage: AudienceEvidenceStage,
) -> AudienceEffectFinding:
    if blueprint.story_engine is None:
        return _not_yet(
            AudienceEffectDimension.PAYOFF_ARCHITECTURE,
            AudienceEvidenceStage.STRUCTURE,
            stage,
        )

    main = blueprint.story_engine.main_thread
    climax_targets = tuple(
        target.label
        for target in blueprint.tension_waveform.target_curve
        if "climax" in target.label.casefold()
    )
    expected = tuple(blueprint.contract.expected_elements)
    evidence = (
        f"governing_change = {main.change.author_text}",
        f"expected_elements = {len(expected)}",
        f"explicit_climax_targets = {len(climax_targets)}",
    )

    if climax_targets or expected:
        return AudienceEffectFinding(
            dimension=AudienceEffectDimension.PAYOFF_ARCHITECTURE,
            state=AudienceEffectState.SUPPORTED,
            evidence_stage=stage,
            summary=(
                "The structure contains explicit expectation-discharge markers through a governing "
                "change plus declared climax or expected-element commitments."
            ),
            evidence=evidence + tuple(f"climax = {label}" for label in climax_targets),
            limitations=(
                "A Blueprint cannot establish that the audience noticed every setup or found the realized payoff satisfying.",
            ),
        )

    return AudienceEffectFinding(
        dimension=AudienceEffectDimension.PAYOFF_ARCHITECTURE,
        state=AudienceEffectState.TENSION,
        evidence_stage=stage,
        summary=(
            "The governing engine declares change, but the Blueprint does not expose explicit "
            "climax or expected-element markers that make promise discharge easy to inspect."
        ),
        evidence=evidence,
        limitations=(
            "Absence of these markers does not prove the story lacks payoff; the plan may encode it elsewhere.",
        ),
    )


def _grounded_credibility(stage: AudienceEvidenceStage) -> AudienceEffectFinding:
    return _not_yet(
        AudienceEffectDimension.GROUNDED_CREDIBILITY,
        AudienceEvidenceStage.REALIZATION,
        stage,
    )


def _affective_commitment(stage: AudienceEvidenceStage) -> AudienceEffectFinding:
    return _not_yet(
        AudienceEffectDimension.AFFECTIVE_COMMITMENT,
        AudienceEvidenceStage.EXPRESSION,
        stage,
    )


def _memorability(stage: AudienceEvidenceStage) -> AudienceEffectFinding:
    return _not_yet(
        AudienceEffectDimension.MEMORABILITY,
        AudienceEvidenceStage.COMPLETE,
        stage,
    )


def _transmission(stage: AudienceEvidenceStage) -> AudienceEffectFinding:
    return _not_yet(
        AudienceEffectDimension.TRANSMISSION,
        AudienceEvidenceStage.COMPLETE,
        stage,
    )


_GUIDANCE = {
    AudienceEffectDimension.NARRATIVE_LEGIBILITY: (
        "State the governing story question in one audience-readable sentence.",
        "Legibility improves when genre/audience framing and the causal engine point toward the same central problem.",
    ),
    AudienceEffectDimension.MOTIVATIONAL_ATTACHMENT: (
        "Connect the protagonist's want and stakes to a concrete value the audience can recognize.",
        "A goal becomes consequential when the audience can name what is gained, protected, threatened, or lost.",
    ),
    AudienceEffectDimension.PREDICTIVE_ENGAGEMENT: (
        "Name the unresolved variable the audience should keep predicting, then make major turns revise it.",
        "Useful uncertainty requires enough information to predict and enough change to keep prediction nontrivial.",
    ),
    AudienceEffectDimension.CONSEQUENTIAL_PROGRESSION: (
        "Make each major attempt alter the next available choices, costs, or beliefs.",
        "Escalation is stronger when consequences transform the situation rather than merely increasing obstacle size.",
    ),
    AudienceEffectDimension.EMOTIONAL_LEGIBILITY: (
        "Declare the reader-facing target experience and connect it to the macro emotional progression.",
        "Auteur already separates reader promise from character felt state; the diagnostic should preserve that distinction.",
    ),
    AudienceEffectDimension.PAYOFF_ARCHITECTURE: (
        "Name the major narrative promises and identify where each is intended to discharge.",
        "Payoff becomes inspectable when expected category and planned resolution are explicit without prescribing exact execution.",
    ),
}


def propose_audience_effect_guidance(
    findings: tuple[AudienceEffectFinding, ...],
) -> tuple[AudienceEffectGuidance, ...]:
    """Return noncanonical guidance for currently assessable tensions/gaps only."""
    guidance: list[AudienceEffectGuidance] = []
    for finding in findings:
        if finding.state not in {
            AudienceEffectState.TENSION,
            AudienceEffectState.UNESTABLISHED,
        }:
            continue
        spec = _GUIDANCE.get(finding.dimension)
        if spec is None:
            continue
        action, reason = spec
        guidance.append(
            AudienceEffectGuidance(
                dimension=finding.dimension,
                action=action,
                reason=reason,
            )
        )
    return tuple(guidance)


def analyze_audience_effects(blueprint: StoryBlueprint) -> AudienceEffectReport:
    """Build a read-only MANA report from the evidence present in a StoryBlueprint."""
    stage = infer_audience_evidence_stage(blueprint)
    findings = (
        _narrative_legibility(blueprint, stage),
        _motivational_attachment(blueprint, stage),
        _predictive_engagement(blueprint, stage),
        _consequential_progression(blueprint, stage),
        _grounded_credibility(stage),
        _emotional_legibility(blueprint, stage),
        _affective_commitment(stage),
        _payoff_architecture(blueprint, stage),
        _memorability(stage),
        _transmission(stage),
    )
    return AudienceEffectReport(
        available_evidence_stage=stage,
        findings=findings,
        guidance=propose_audience_effect_guidance(findings),
    )
