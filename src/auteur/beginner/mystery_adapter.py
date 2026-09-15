"""A small deterministic qualification shell over Auteur's Mystery knowledge."""

from __future__ import annotations

import json

from auteur.beginner.guidance import (
    EvidenceReference,
    QualificationCard,
    QualificationInventory,
    QualificationStage,
    register_evidence_source,
    register_guidance_adapter,
)
from auteur.mystery.core_templates import HowdunitTemplate
from auteur.mystery.validation import RuleSet


class _HowdunitEvidenceSource:
    _template = HowdunitTemplate()
    _rule_ids = {rule.rule_id for rule in RuleSet("howdunit").rules}

    def validate(self, reference: EvidenceReference) -> None:
        if reference.source == "HowdunitTemplate":
            assert reference.phase is not None
            if reference.field != self._template.phases[reference.phase]:
                raise ValueError("evidence field does not match HowdunitTemplate phase")
            labels = {option.label for option in self._template.options[reference.phase]}
            if not set(reference.option_labels) <= labels:
                raise ValueError("evidence contains an unsupported Howdunit option")
        elif reference.rule_id not in self._rule_ids:
            raise ValueError("evidence contains an unknown Howdunit rule")


register_evidence_source("HowdunitTemplate", _HowdunitEvidenceSource())
register_evidence_source("RuleSet", _HowdunitEvidenceSource())


class MysteryGuidanceAdapter:
    genre = "mystery"

    @staticmethod
    def inventory() -> QualificationInventory:
        template = HowdunitTemplate()
        rule_ids = {rule.rule_id for rule in RuleSet("howdunit").rules}
        for card in _MYSTERY_CARDS:
            validate_mystery_card_evidence(card)
            for reference in card.evidence_references:
                if reference.source == "HowdunitTemplate":
                    assert reference.phase is not None
                    if reference.field != template.phases[reference.phase]:
                        raise ValueError("evidence field does not match HowdunitTemplate phase")
                    labels = {option.label for option in template.options[reference.phase]}
                    if not set(reference.option_labels) <= labels:
                        raise ValueError("evidence contains an unsupported Howdunit option")
                elif reference.rule_id not in rule_ids:
                    raise ValueError("evidence contains an unknown Howdunit rule")
        return QualificationInventory(cards=_MYSTERY_CARDS)


def _evidence(phase: int, options: tuple[str, ...], recommendation: str, rule_id: str | None = None) -> tuple[EvidenceReference, ...]:
    field = {
        2: "genre_contract", 3: "scope", 4: "structural_forces",
        5: "investigation_style", 6: "pacing_rhythm", 7: "clue_distribution",
        8: "solution_density", 9: "fairness_confidence",
    }[phase]
    references = (
        EvidenceReference(claim="decision", source="HowdunitTemplate", phase=phase, field=field, option_labels=options),
        EvidenceReference(claim="recommendation", source="HowdunitTemplate", phase=phase, field=field, option_labels=(recommendation,)),
        EvidenceReference(claim="option", source="HowdunitTemplate", phase=phase, field=field, option_labels=options),
        EvidenceReference(claim="consequence", source="HowdunitTemplate", phase=phase, field=field, option_labels=options),
    )
    if rule_id is not None:
        return references + (EvidenceReference(claim="consequence", source="RuleSet", rule_id=rule_id),)
    return references


_MYSTERY_CARDS: tuple[QualificationCard, ...] = (
    QualificationCard(
        card_id="discover.story-experience",
        stage=QualificationStage.DISCOVER,
        title="The mystery experience",
        question="Which mystery experience or lens should the story promise?",
        source_subject="Howdunit genre_contract",
        options=("Detective procedural", "Police/investigation procedural", "Locked-room puzzle", "Intricate puzzle structure"),
        recommendation="Detective procedural",
        narrative_principle="The genre contract tells the reader what kind of investigation to expect.",
        warnings_or_tensions=("A vague question makes clues feel decorative.", "A question that is too narrow can flatten the human stakes."),
        downstream_consequences=("The selected genre contract determines the investigation mode presented to the reader.",),
        evidence_references=_evidence(2, ("Detective procedural", "Police/investigation procedural", "Locked-room puzzle", "Intricate puzzle structure"), "Detective procedural"),
    ),
    QualificationCard(
        card_id="discover.personal-stakes",
        stage=QualificationStage.DISCOVER,
        title="The personal consequence",
        question="Which personal consequence should the investigation carry?",
        source_subject="Howdunit structural_forces",
        options=("Stakes: Justice served", "Stakes: Order restored"),
        recommendation="Stakes: Justice served",
        narrative_principle="Structural forces define what the investigation must restore.",
        warnings_or_tensions=("Curiosity alone may not sustain pressure.", "Strong obligation can narrow alternative choices."),
        downstream_consequences=("The selected stakes determine what remains unresolved until the solution.",),
        evidence_references=_evidence(4, ("Stakes: Justice served", "Stakes: Order restored"), "Stakes: Justice served"),
    ),
    QualificationCard(
        card_id="discover.investigation-approach",
        stage=QualificationStage.DISCOVER,
        title="The investigation approach",
        question="Which investigation approach should guide the inquiry?",
        source_subject="Howdunit investigation_style",
        options=("Logical deduction", "Intuitive investigation", "By-the-book procedure"),
        recommendation="Logical deduction",
        narrative_principle="The investigation-style phase defines how the inquiry proceeds.",
        warnings_or_tensions=("Expansion increases discovery opportunities and continuity load.", "A contained scope needs depth rather than just fewer locations."),
        downstream_consequences=("The selected approach determines whether deductions, intuition, or procedure leads the inquiry.",),
        evidence_references=_evidence(5, ("Logical deduction", "Intuitive investigation", "By-the-book procedure"), "Logical deduction"),
    ),
    QualificationCard(
        card_id="story_identity.protagonist-want",
        stage=QualificationStage.STORY_IDENTITY,
        title="The protagonist's want",
        question="Which practical investigation want should drive the protagonist?",
        source_subject="Howdunit structural_forces want options",
        options=("Want: Solve the puzzle", "Want: Identify the culprit", "Want: Restore order"),
        recommendation="Want: Solve the puzzle",
        narrative_principle="The structural-forces phase defines the protagonist's want.",
        warnings_or_tensions=("A purely procedural want can underplay personal change.", "A personal want must not erase the mystery's logic."),
        downstream_consequences=("The selected want gives the protagonist a goal beyond the investigation's bare procedure.",),
        evidence_references=_evidence(4, ("Want: Solve the puzzle", "Want: Identify the culprit", "Want: Restore order"), "Want: Solve the puzzle"),
    ),
    QualificationCard(
        card_id="story_identity.relationship-pressure",
        stage=QualificationStage.STORY_IDENTITY,
        title="The resistance to truth",
        question="Which relationship or conflict pressure should shape the investigation?",
        source_subject="Howdunit structural_forces conflict options",
        options=("Conflict: Deduction vs. misdirection", "Conflict: Logic vs. chaos"),
        recommendation="Conflict: Deduction vs. misdirection",
        narrative_principle="The structural-forces conflict field defines the pressure shaping the investigation.",
        warnings_or_tensions=("Misdirection without fair signals feels arbitrary.", "Too many false leads can dilute the central question."),
        downstream_consequences=("The selected conflict determines whether misdirection or chaos opposes deduction.",),
        evidence_references=_evidence(4, ("Conflict: Deduction vs. misdirection", "Conflict: Logic vs. chaos"), "Conflict: Deduction vs. misdirection"),
    ),
    QualificationCard(
        card_id="story_identity.information-contract",
        stage=QualificationStage.STORY_IDENTITY,
        title="The reader's knowledge contract",
        question="How confident should the reader be that the mystery can be solved fairly?",
        source_subject="Howdunit fairness_confidence",
        options=("High confidence reader could solve it", "Medium confidence (possible on rereads)", "Challenging but fair puzzle"),
        recommendation="Challenging but fair puzzle",
        narrative_principle="Fairness confidence sets the knowledge contract between reader and mystery.",
        warnings_or_tensions=("External stakes alone may feel impersonal.", "Escalating stakes should remain credible for the chosen scope."),
        downstream_consequences=("The selected fairness confidence determines how solvable the mystery is for the reader.",),
        evidence_references=_evidence(9, ("High confidence reader could solve it", "Medium confidence (possible on rereads)", "Challenging but fair puzzle"), "Challenging but fair puzzle"),
    ),
    QualificationCard(
        card_id="story_identity.truth-opposition",
        stage=QualificationStage.STORY_IDENTITY,
        title="The truth's opposition",
        question="Which resistance should protect the hidden truth?",
        source_subject="Howdunit structural_forces resistance options",
        options=("Resistance: Misleading clues", "Resistance: False suspects", "Resistance: Hidden motives"),
        recommendation="Resistance: Misleading clues",
        narrative_principle="The structural-forces resistance field defines what protects the truth.",
        warnings_or_tensions=("Clarity is not the same as comfort.", "A static investigator can make a clever solution feel emotionally empty."),
        downstream_consequences=("The selected resistance determines what obstructs the next inference.",),
        evidence_references=_evidence(4, ("Resistance: Misleading clues", "Resistance: False suspects", "Resistance: Hidden motives"), "Resistance: Misleading clues"),
    ),
    QualificationCard(
        card_id="structure.investigation-disruption",
        stage=QualificationStage.STRUCTURE,
        title="Disruption pacing",
        question="What pacing rhythm should govern the investigation's disruption?",
        source_subject="Howdunit pacing_rhythm",
        options=("Clues accelerate toward solution", "Steady rhythm of discovery", "Forward progress with setbacks"),
        recommendation="Steady rhythm of discovery",
        narrative_principle="The pacing-rhythm phase defines how discovery changes the investigation's momentum.",
        warnings_or_tensions=("A tight solution needs early evidence.", "A generous solution can reduce the reader's participation."),
        downstream_consequences=("The selected rhythm determines whether discovery accelerates, stays steady, or meets setbacks.",),
        evidence_references=_evidence(6, ("Clues accelerate toward solution", "Steady rhythm of discovery", "Forward progress with setbacks"), "Steady rhythm of discovery"),
    ),
    QualificationCard(
        card_id="structure.clue-distribution",
        stage=QualificationStage.STRUCTURE,
        title="Clue and reversal distribution",
        question="How should major clues and reversals be distributed?",
        source_subject="Howdunit clue_distribution",
        options=("Heavy clues early, light late", "Even clue distribution", "Light clues early, heavy late"),
        recommendation="Even clue distribution",
        narrative_principle="The clue-distribution phase sets when evidence reaches the reader.",
        warnings_or_tensions=("A consequence-free reveal can make the investigation feel ornamental.", "A costly reveal may resist a fully comforting resolution."),
        downstream_consequences=("The selected distribution determines when the reader can reason from the evidence.",),
        evidence_references=_evidence(7, ("Heavy clues early, light late", "Even clue distribution", "Light clues early, heavy late"), "Even clue distribution", "howdunit.structure.solution_derivable"),
    ),
    QualificationCard(
        card_id="structure.final-revelation",
        stage=QualificationStage.STRUCTURE,
        title="Solution and revelation density",
        question="How directly should the final revelation follow from the clues?",
        source_subject="Howdunit solution_density",
        options=("Solution barely derivable from clues", "Solution is one of several reasonable readings", "Solution obvious once clues are gathered"),
        recommendation="Solution is one of several reasonable readings",
        narrative_principle="Solution density defines how directly the final revelation follows from evidence.",
        warnings_or_tensions=("A tight solution needs early evidence.", "A generous solution can reduce the reader's participation."),
        downstream_consequences=("The selected density determines how much reasoning the final revelation asks of the reader.",),
        evidence_references=_evidence(8, ("Solution barely derivable from clues", "Solution is one of several reasonable readings", "Solution obvious once clues are gathered"), "Solution is one of several reasonable readings", "howdunit.structure.solution_derivable"),
    ),
)


_CANONICAL_CARD_DEFINITIONS = {
    card.card_id: json.dumps(card.model_dump(mode="json"), sort_keys=True, separators=(",", ":"))
    for card in _MYSTERY_CARDS
}


def validate_mystery_card_evidence(card: QualificationCard) -> None:
    """Reject any mutation of a canonical card definition, including evidence."""
    expected = _CANONICAL_CARD_DEFINITIONS.get(card.card_id)
    actual = json.dumps(card.model_dump(mode="json"), sort_keys=True, separators=(",", ":"))
    if expected is None or actual != expected:
        raise ValueError(f"canonical card definition does not match card {card.card_id}")


def mystery_qualification_inventory() -> QualificationInventory:
    """Return the stable Mystery beginner inventory."""
    return MYSTERY_GUIDANCE_ADAPTER.inventory()


MYSTERY_GUIDANCE_ADAPTER = MysteryGuidanceAdapter()


def register_mystery_guidance_adapter() -> None:
    """Register the built-in Mystery adapter at the package boundary."""
    register_guidance_adapter(MYSTERY_GUIDANCE_ADAPTER)
