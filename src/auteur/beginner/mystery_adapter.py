"""A small deterministic qualification shell over Auteur's Mystery knowledge."""

from __future__ import annotations

from enum import Enum
from typing import ClassVar

from pydantic import BaseModel, ConfigDict, Field, model_validator


class QualificationStage(str, Enum):
    DISCOVER = "discover"
    STORY_IDENTITY = "story_identity"
    STRUCTURE = "structure"


class QualificationCard(BaseModel):
    """One beginner-facing decision projected from existing Mystery concepts."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    card_id: str = Field(min_length=1)
    stage: QualificationStage
    title: str = Field(min_length=1)
    question: str = Field(min_length=1)
    source_subject: str = Field(min_length=1)
    options: tuple[str, ...] = Field(min_length=2)
    recommendation: str = Field(min_length=1)
    narrative_principle: str = Field(min_length=1)
    warnings_or_tensions: tuple[str, ...] = Field(min_length=1)
    evidence_references: tuple[str, ...] = Field(min_length=1)

    @model_validator(mode="before")
    @classmethod
    def reject_coercible_fields(cls, data: object) -> object:
        if isinstance(data, dict):
            if "stage" in data and type(data["stage"]) is not QualificationStage:
                raise ValueError("stage must be a QualificationStage")
            for field_name in ("options", "warnings_or_tensions", "evidence_references"):
                if field_name in data and type(data[field_name]) is not tuple:
                    raise ValueError(f"{field_name} must be a tuple")
        return data

    @model_validator(mode="after")
    def recommendation_is_an_option(self) -> QualificationCard:
        if self.recommendation not in self.options:
            raise ValueError("recommendation must be one of the card options")
        return self


class QualificationInventory(BaseModel):
    """Immutable, sealed inventory for the Beginner Mystery slice."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    cards: tuple[QualificationCard, ...]
    _expected_counts: ClassVar[dict[QualificationStage, int]] = {
        QualificationStage.DISCOVER: 3,
        QualificationStage.STORY_IDENTITY: 4,
        QualificationStage.STRUCTURE: 3,
    }

    @model_validator(mode="before")
    @classmethod
    def reject_coercible_cards(cls, data: object) -> object:
        if isinstance(data, dict) and "cards" in data and type(data["cards"]) is not tuple:
            raise ValueError("cards must be a tuple")
        return data

    @model_validator(mode="after")
    def validate_inventory(self) -> QualificationInventory:
        ids = [card.card_id for card in self.cards]
        if len(ids) != len(set(ids)):
            raise ValueError("qualification card IDs must be unique")
        counts = {stage: sum(card.stage is stage for card in self.cards) for stage in self._expected_counts}
        if counts != self._expected_counts:
            raise ValueError("qualification inventory has the wrong stage counts")
        return self

    @property
    def stage_counts(self) -> dict[QualificationStage, int]:
        return {stage: sum(card.stage is stage for card in self.cards) for stage in self._expected_counts}

    def card(self, card_id: str) -> QualificationCard:
        for card in self.cards:
            if card.card_id == card_id:
                return card
        raise KeyError(card_id)


_MYSTERY_CARDS: tuple[QualificationCard, ...] = (
    QualificationCard(
        card_id="discover.mystery-question",
        stage=QualificationStage.DISCOVER,
        title="The central mystery question",
        question="What question must the investigation answer?",
        source_subject="Mystery core question",
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
        source_subject="Investigator motivation and want",
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
        source_subject="Mystery scope",
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
        source_subject="Story Identity structural forces: want",
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
        source_subject="Story Identity structural forces: resistance",
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
        source_subject="Story Identity structural forces: stakes",
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
        source_subject="Story Identity structural forces: change",
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
        source_subject="Clue distribution",
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
        source_subject="Solution density and derivability",
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
        source_subject="Reveal and restored order",
        options=("Justice is served", "Relationships are reinterpreted", "Order is restored with a cost"),
        recommendation="Relationships are reinterpreted",
        narrative_principle="A reveal is an event in the story world, not only an answer for the audience.",
        warnings_or_tensions=("A consequence-free reveal can make the investigation feel ornamental.", "A costly reveal may resist a fully comforting resolution."),
        evidence_references=("auteur.mystery.core_templates:HowdunitTemplate.phases[4]", "auteur.mystery.validation:RuleSet:howdunit.structure.red_herring_coherence"),
    ),
)


def mystery_qualification_inventory() -> QualificationInventory:
    """Return the stable Mystery beginner inventory."""
    return QualificationInventory(cards=_MYSTERY_CARDS)
