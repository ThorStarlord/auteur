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
        title="The investigation mode",
        question="Which investigation mode should the story use?",
        source_subject="Howdunit genre_contract",
        options=("Detective procedural", "Police/investigation procedural", "Locked-room puzzle"),
        recommendation="Detective procedural",
        narrative_principle="The genre contract tells the reader what kind of investigation to expect.",
        warnings_or_tensions=("A vague question makes clues feel decorative.", "A question that is too narrow can flatten the human stakes."),
        downstream_consequences=("The selected genre contract determines the investigation mode presented to the reader.",),
        evidence_references=("auteur.mystery.core_templates:HowdunitTemplate.phases[2]", "auteur.mystery.core_templates:HowdunitTemplate.phases[4]"),
    ),
    QualificationCard(
        card_id="discover.investigation-motivation",
        stage=QualificationStage.DISCOVER,
        title="The investigation's driving want",
        question="Which want drives the investigator beyond the case mechanics?",
        source_subject="Howdunit structural_forces",
        options=("Want: Solve the puzzle", "Want: Identify the culprit", "Want: Restore order"),
        recommendation="Want: Solve the puzzle",
        narrative_principle="Structural forces give the investigation a character-driven want.",
        warnings_or_tensions=("Curiosity alone may not sustain pressure.", "Strong obligation can narrow alternative choices."),
        downstream_consequences=("The selected want determines what the investigator pursues beyond the case mechanics.",),
        evidence_references=("auteur.mystery.core_templates:HowdunitTemplate.phases[4]", "auteur.mystery.core_templates:HowdunitTemplate.options[4]"),
    ),
    QualificationCard(
        card_id="discover.inquiry-scope",
        stage=QualificationStage.DISCOVER,
        title="The inquiry's scope",
        question="How contained or expansive should the inquiry be?",
        source_subject="Howdunit scope",
        options=("Single crime, contained", "Multi-faceted crime, wider cast", "Serial crimes, city-scale investigation"),
        recommendation="Single crime, contained",
        narrative_principle="The template's scope controls how contained or expansive the investigation is.",
        warnings_or_tensions=("Expansion increases discovery opportunities and continuity load.", "A contained scope needs depth rather than just fewer locations."),
        downstream_consequences=("The selected scope determines whether the investigation is contained, wider-cast, or city-scale.",),
        evidence_references=("auteur.mystery.core_templates:HowdunitTemplate.phases[3]", "auteur.mystery.core_templates:HowdunitTemplate.options[3]"),
    ),
    QualificationCard(
        card_id="story-identity.protagonist-want",
        stage=QualificationStage.STORY_IDENTITY,
        title="The protagonist's want",
        question="Which want drives the protagonist beyond merely solving the case?",
        source_subject="Howdunit structural_forces want options",
        options=("Want: Solve the puzzle", "Want: Identify the culprit", "Want: Restore order"),
        recommendation="Want: Solve the puzzle",
        narrative_principle="The structural-forces phase defines the protagonist's want.",
        warnings_or_tensions=("A purely procedural want can underplay personal change.", "A personal want must not erase the mystery's logic."),
        downstream_consequences=("The selected want gives the protagonist a goal beyond the investigation's bare procedure.",),
        evidence_references=("auteur.mystery.core_templates:HowdunitTemplate.options[4]", "auteur.mystery.core_templates:HowdunitTemplate.phases[4]"),
    ),
    QualificationCard(
        card_id="story-identity.resistance",
        stage=QualificationStage.STORY_IDENTITY,
        title="The resistance to truth",
        question="What makes the truth difficult to reach?",
        source_subject="Howdunit structural_forces resistance options",
        options=("Resistance: Misleading clues", "Resistance: False suspects", "Resistance: Hidden motives"),
        recommendation="Resistance: Misleading clues",
        narrative_principle="The structural-forces phase defines what obstructs the route to truth.",
        warnings_or_tensions=("Misdirection without fair signals feels arbitrary.", "Too many false leads can dilute the central question."),
        downstream_consequences=("The selected resistance determines what obstructs the next inference.",),
        evidence_references=("auteur.mystery.core_templates:HowdunitTemplate.options[4]", "auteur.mystery.validation:RuleSet:howdunit.structure.red_herring_coherence"),
    ),
    QualificationCard(
        card_id="story-identity.stakes",
        stage=QualificationStage.STORY_IDENTITY,
        title="What the answer changes",
        question="What is at stake if the answer stays hidden?",
        source_subject="Howdunit structural_forces stakes options",
        options=("Stakes: Justice served", "Stakes: Order restored"),
        recommendation="Stakes: Justice served",
        narrative_principle="The structural-forces phase defines what the solution must restore.",
        warnings_or_tensions=("External stakes alone may feel impersonal.", "Escalating stakes should remain credible for the chosen scope."),
        downstream_consequences=("The selected stakes determine what remains unresolved until the solution.",),
        evidence_references=("auteur.mystery.core_templates:HowdunitTemplate.options[4]", "auteur.mystery.core_templates:HowdunitTemplate.phases[4]"),
    ),
    QualificationCard(
        card_id="story-identity.change",
        stage=QualificationStage.STORY_IDENTITY,
        title="The meaning of discovery",
        question="How does understanding the truth change the protagonist?",
        source_subject="Howdunit structural_forces change options",
        options=("Change: From confusion to clarity", "Change: From suspicion to certainty"),
        recommendation="Change: From confusion to clarity",
        narrative_principle="The structural-forces phase defines how discovery changes the protagonist.",
        warnings_or_tensions=("Clarity is not the same as comfort.", "A static investigator can make a clever solution feel emotionally empty."),
        downstream_consequences=("The selected change determines the protagonist's movement after understanding the truth.",),
        evidence_references=("auteur.mystery.core_templates:HowdunitTemplate.options[4]", "auteur.mystery.core_templates:HowdunitTemplate.phases[4]"),
    ),
    QualificationCard(
        card_id="structure.clue-distribution",
        stage=QualificationStage.STRUCTURE,
        title="Clue distribution",
        question="When should the reader receive the information needed to reason?",
        source_subject="Howdunit clue_distribution and solution_derivable",
        options=("Heavy clues early, light late", "Even clue distribution", "Light clues early, heavy late"),
        recommendation="Even clue distribution",
        narrative_principle="The clue-distribution phase sets when evidence reaches the reader.",
        warnings_or_tensions=("Late clues can create surprise but threaten fair play.", "Early clues require stronger misdirection and interpretation."),
        downstream_consequences=("The selected distribution determines when the reader can reason from the evidence.",),
        evidence_references=("auteur.mystery.core_templates:HowdunitTemplate.phases[7]", "auteur.mystery.validation:RuleSet:howdunit.structure.solution_derivable"),
    ),
    QualificationCard(
        card_id="structure.solution-density",
        stage=QualificationStage.STRUCTURE,
        title="Solution density",
        question="How tightly should the solution follow from the clues?",
        source_subject="Howdunit solution_density and solution_derivable",
        options=("Solution barely derivable from clues", "Solution is one of several reasonable readings", "Solution obvious once clues are gathered"),
        recommendation="Solution is one of several reasonable readings",
        narrative_principle="The solution-density phase sets how directly the answer follows from clues.",
        warnings_or_tensions=("A tight solution needs early evidence.", "A generous solution can reduce the reader's participation."),
        downstream_consequences=("The selected density determines how directly the solution follows from the clues.",),
        evidence_references=("auteur.mystery.core_templates:HowdunitTemplate.phases[8]", "auteur.mystery.validation:RuleSet:howdunit.structure.solution_derivable"),
    ),
    QualificationCard(
        card_id="structure.reveal-consequences",
        stage=QualificationStage.STRUCTURE,
        title="Reveal consequences",
        question="What changes when the hidden truth is revealed?",
        source_subject="Howdunit structural_forces and red_herring_coherence",
        options=("Change: From confusion to clarity", "Change: From suspicion to certainty"),
        recommendation="Change: From suspicion to certainty",
        narrative_principle="The structural-forces change field defines the protagonist's altered understanding.",
        warnings_or_tensions=("A consequence-free reveal can make the investigation feel ornamental.", "A costly reveal may resist a fully comforting resolution."),
        downstream_consequences=("The selected change determines how the protagonist understands the revealed truth.",),
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
