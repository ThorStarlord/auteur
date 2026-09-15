"""A small deterministic qualification shell over Auteur's Mystery knowledge."""

from __future__ import annotations

from auteur.beginner.guidance import (
    QualificationCard,
    QualificationInventory,
    QualificationStage,
    register_guidance_adapter,
)


class MysteryGuidanceAdapter:
    genre = "mystery"

    @staticmethod
    def inventory() -> QualificationInventory:
        return QualificationInventory(cards=_MYSTERY_CARDS)


_MYSTERY_CARDS: tuple[QualificationCard, ...] = (
    QualificationCard(
        card_id="discover.mystery-question",
        stage=QualificationStage.DISCOVER,
        title="The central mystery question",
        question="What question must the investigation answer?",
        source_subject="Howdunit genre_contract and structural_forces",
        options=("Who caused the disruption?", "What hidden truth explains it?", "Can order be restored?"),
        recommendation="What hidden truth explains it?",
        narrative_principle="A mystery gives every discovery meaning by orienting it toward a question.",
        warnings_or_tensions=("A vague question makes clues feel decorative.", "A question that is too narrow can flatten the human stakes."),
        evidence_references=("auteur.mystery.core_templates:HowdunitTemplate.phases[2]", "auteur.mystery.core_templates:HowdunitTemplate.phases[4]"),
    ),
    QualificationCard(
        card_id="discover.investigation-motivation",
        stage=QualificationStage.DISCOVER,
        title="Why this investigation happens",
        question="Why must this protagonist pursue the answer?",
        source_subject="Howdunit structural_forces",
        options=("Personal obligation", "A threat to someone or something valued", "A need to restore justice"),
        recommendation="Personal obligation",
        narrative_principle="Investigation becomes story when finding the truth costs the investigator something.",
        warnings_or_tensions=("Curiosity alone may not sustain pressure.", "Strong obligation can narrow alternative choices."),
        evidence_references=("auteur.mystery.core_templates:HowdunitTemplate.phases[4]", "auteur.mystery.core_templates:HowdunitTemplate.options[4]"),
    ),
    QualificationCard(
        card_id="discover.inquiry-scope",
        stage=QualificationStage.DISCOVER,
        title="The inquiry's scope",
        question="How contained or expansive should the inquiry be?",
        source_subject="Howdunit scope",
        options=("A single contained crime", "A wider cast and connected evidence", "A serial or city-scale investigation"),
        recommendation="A single contained crime",
        narrative_principle="Scope sets the reader's map of suspects, clues, and available attention.",
        warnings_or_tensions=("Expansion increases discovery opportunities and continuity load.", "A contained scope needs depth rather than just fewer locations."),
        evidence_references=("auteur.mystery.core_templates:HowdunitTemplate.phases[3]", "auteur.mystery.core_templates:HowdunitTemplate.options[3]"),
    ),
    QualificationCard(
        card_id="story-identity.protagonist-want",
        stage=QualificationStage.STORY_IDENTITY,
        title="The protagonist's want",
        question="What does the protagonist want beyond merely solving the case?",
        source_subject="Howdunit structural_forces want options",
        options=("Solve the puzzle", "Identify the culprit", "Restore order"),
        recommendation="Solve the puzzle",
        narrative_principle="A concrete want turns deduction into a character-driven line of action.",
        warnings_or_tensions=("A purely procedural want can underplay personal change.", "A personal want must not erase the mystery's logic."),
        evidence_references=("auteur.mystery.core_templates:HowdunitTemplate.options[4]", "auteur.mystery.core_templates:HowdunitTemplate.phases[4]"),
    ),
    QualificationCard(
        card_id="story-identity.resistance",
        stage=QualificationStage.STORY_IDENTITY,
        title="The resistance to truth",
        question="What makes the truth difficult to reach?",
        source_subject="Howdunit structural_forces resistance options",
        options=("Misleading clues", "False suspects", "Hidden motives"),
        recommendation="Misleading clues",
        narrative_principle="Resistance should obstruct the next inference, not merely delay the plot.",
        warnings_or_tensions=("Misdirection without fair signals feels arbitrary.", "Too many false leads can dilute the central question."),
        evidence_references=("auteur.mystery.core_templates:HowdunitTemplate.options[4]", "auteur.mystery.validation:RuleSet:howdunit.structure.red_herring_coherence"),
    ),
    QualificationCard(
        card_id="story-identity.stakes",
        stage=QualificationStage.STORY_IDENTITY,
        title="What the answer changes",
        question="What is at stake if the answer stays hidden?",
        source_subject="Howdunit structural_forces stakes options",
        options=("Justice remains unresolved", "Order remains broken", "An innocent person remains endangered"),
        recommendation="Justice remains unresolved",
        narrative_principle="Stakes make the solution matter after the final clue is understood.",
        warnings_or_tensions=("External stakes alone may feel impersonal.", "Escalating stakes should remain credible for the chosen scope."),
        evidence_references=("auteur.mystery.core_templates:HowdunitTemplate.options[4]", "auteur.mystery.core_templates:HowdunitTemplate.phases[4]"),
    ),
    QualificationCard(
        card_id="story-identity.change",
        stage=QualificationStage.STORY_IDENTITY,
        title="The meaning of discovery",
        question="How does understanding the truth change the protagonist?",
        source_subject="Howdunit structural_forces change options",
        options=("Confusion to clarity", "Suspicion to certainty", "Certainty to a more difficult truth"),
        recommendation="Confusion to clarity",
        narrative_principle="The answer should change what the protagonist can see, choose, or accept.",
        warnings_or_tensions=("Clarity is not the same as comfort.", "A static investigator can make a clever solution feel emotionally empty."),
        evidence_references=("auteur.mystery.core_templates:HowdunitTemplate.options[4]", "auteur.mystery.core_templates:HowdunitTemplate.phases[4]"),
    ),
    QualificationCard(
        card_id="structure.clue-distribution",
        stage=QualificationStage.STRUCTURE,
        title="Clue distribution",
        question="When should the reader receive the information needed to reason?",
        source_subject="Howdunit clue_distribution and solution_derivable",
        options=("Heavy clues early", "Even clue distribution", "Light clues early and heavy late"),
        recommendation="Even clue distribution",
        narrative_principle="Fairness comes from giving the reader a usable trail before the reveal.",
        warnings_or_tensions=("Late clues can create surprise but threaten fair play.", "Early clues require stronger misdirection and interpretation."),
        evidence_references=("auteur.mystery.core_templates:HowdunitTemplate.phases[7]", "auteur.mystery.validation:RuleSet:howdunit.structure.solution_derivable"),
    ),
    QualificationCard(
        card_id="structure.solution-density",
        stage=QualificationStage.STRUCTURE,
        title="Solution density",
        question="How tightly should the solution follow from the clues?",
        source_subject="Howdunit solution_density and solution_derivable",
        options=("Barely derivable", "Several reasonable readings", "Obvious once clues gather"),
        recommendation="Several reasonable readings",
        narrative_principle="A satisfying solution is surprising in hindsight without being unsupported.",
        warnings_or_tensions=("A tight solution needs early evidence.", "A generous solution can reduce the reader's participation."),
        evidence_references=("auteur.mystery.core_templates:HowdunitTemplate.phases[8]", "auteur.mystery.validation:RuleSet:howdunit.structure.solution_derivable"),
    ),
    QualificationCard(
        card_id="structure.reveal-consequences",
        stage=QualificationStage.STRUCTURE,
        title="Reveal consequences",
        question="What changes when the hidden truth is revealed?",
        source_subject="Howdunit structural_forces and red_herring_coherence",
        options=("Justice is served", "Relationships are reinterpreted", "Order is restored with a cost"),
        recommendation="Relationships are reinterpreted",
        narrative_principle="A reveal is an event in the story world, not only an answer for the audience.",
        warnings_or_tensions=("A consequence-free reveal can make the investigation feel ornamental.", "A costly reveal may resist a fully comforting resolution."),
        evidence_references=("auteur.mystery.core_templates:HowdunitTemplate.phases[4]", "auteur.mystery.validation:RuleSet:howdunit.structure.red_herring_coherence"),
    ),
)


def mystery_qualification_inventory() -> QualificationInventory:
    """Return the stable Mystery beginner inventory."""
    return MYSTERY_GUIDANCE_ADAPTER.inventory()


MYSTERY_GUIDANCE_ADAPTER = MysteryGuidanceAdapter()


def register_mystery_guidance_adapter() -> None:
    """Register the built-in Mystery adapter at the package boundary."""
    register_guidance_adapter(MYSTERY_GUIDANCE_ADAPTER)
