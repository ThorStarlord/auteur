"""Cartographer planning models — the input contract for the Cartographer.

Extracted from blueprint.py to separate the pipeline's projection layer
from the story specification schema.
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Self

from pydantic import BaseModel, Field

from auteur.blueprint import (
    ActStructure,
    ArcType,
    AuthorAudienceContract,
    Character,
    Genre,
    LengthClass,
    POVType,
    StoryBlueprint,
    TargetAudience,
)


class PlanningScope(str, Enum):
    FULL_STORY = "full_story"
    ACT = "act"
    CHAPTER = "chapter"
    CHARACTER_ARC_BEAT = "character_arc_beat"


class ArcDirective(BaseModel):
    character: str
    arc_type: ArcType
    current_pct: int
    next_milestone: str | None
    state_summary: str = Field(
        description="Compact summary of physical/emotional/location state."
    )


class PlanningCall(BaseModel):
    """Everything the Cartographer needs for one planning call. No hidden state."""

    scope: PlanningScope
    chapter_index: int | None = None
    act_index: int | None = None
    focus_character: str | None = None

    # Layer 1 + 2
    title: str
    length_class: LengthClass
    genre: Genre
    subgenre: str | None
    target_audience: TargetAudience
    pov_type: POVType
    act_structure: ActStructure
    estimated_chapters: int

    # Layer 3 (only the rules, flattened)
    contract_rules: list[str]
    forbidden_tropes: list[str]
    expected_elements: list[str]

    # Layer 4
    emotional_target: str

    # Layer 4 — structural forces (from story engine main_thread)
    story_engine_want: str | None = Field(
        default=None,
        description="The protagonist's core want from the story engine."
    )
    story_engine_resistance: str | None = Field(
        default=None,
        description="What opposes the want."
    )
    story_engine_conflict: str | None = Field(
        default=None,
        description="The collision between want and resistance."
    )
    story_engine_stakes: str | None = Field(
        default=None,
        description="What can be lost or gained."
    )
    story_engine_change: str | None = Field(
        default=None,
        description="How the protagonist transforms."
    )

    # Layer 4 — character contradictions (for conflict surfacing)
    character_contradictions: dict[str, list[str]] = Field(
        default_factory=dict,
        description="Character name -> list of contradiction labels."
    )

    # Layer 5
    arc_directives: list[ArcDirective]

    # Layer 6
    tension_target: int | None
    tension_target_label: str | None
    recent_tension_scores: list[int]

    # Theme
    thematic_beat: str

    @classmethod
    def for_chapter(
        cls, blueprint: StoryBlueprint, chapter_index: int
    ) -> Self:
        if chapter_index < 1 or chapter_index > (
            blueprint.structure.estimated_chapters or 0
        ):
            raise ValueError(
                f"chapter_index {chapter_index} outside "
                f"1..{blueprint.structure.estimated_chapters}."
            )

        act_idx = blueprint.current_act(chapter_index)
        emotional_target = _emotional_target_for_act(blueprint, act_idx)
        tension = blueprint.tension_waveform.target_for(chapter_index)
        contract = blueprint.contract

        engine = blueprint.story_engine
        contradictions = _collect_contradictions(blueprint)

        return cls(
            scope=PlanningScope.CHAPTER,
            chapter_index=chapter_index,
            act_index=act_idx,
            title=blueprint.identity.title,
            length_class=blueprint.identity.length_class,
            genre=blueprint.identity.genre,
            subgenre=blueprint.identity.subgenre,
            target_audience=blueprint.identity.target_audience,
            pov_type=blueprint.identity.pov_type,
            act_structure=blueprint.structure.act_structure,
            estimated_chapters=blueprint.structure.estimated_chapters or 0,
            contract_rules=_flatten_contract(contract),
            forbidden_tropes=list(contract.forbidden_tropes),
            expected_elements=list(contract.expected_elements),
            story_engine_want=engine.main_thread.want.author_text if engine else None,
            story_engine_resistance=engine.main_thread.resistance.author_text if engine else None,
            story_engine_conflict=engine.main_thread.conflict.author_text if engine else None,
            story_engine_stakes=engine.main_thread.stakes.author_text if engine else None,
            story_engine_change=engine.main_thread.change.author_text if engine else None,
            character_contradictions=contradictions,
            emotional_target=emotional_target,
            arc_directives=[
                _arc_directive(c) for c in blueprint.characters
            ],
            tension_target=tension.score if tension else None,
            tension_target_label=tension.label if tension else None,
            recent_tension_scores=blueprint.tension_waveform.recent(3),
            thematic_beat=blueprint.theme.central_question,
        )


def _emotional_target_for_act(
    blueprint: StoryBlueprint, act_index: int
) -> str:
    for t in blueprint.emotional_design.per_act_tones:
        if t.act_index == act_index:
            return t.tone
    return blueprint.emotional_design.overall_emotional_arc


def _flatten_contract(
    contract: AuthorAudienceContract,
) -> list[str]:
    rules = [
        f"content_rating = {contract.content_rating.value}",
        f"explicit_violence = {contract.explicit_violence}",
        f"explicit_sex = {contract.explicit_sex}",
        f"profanity = {contract.profanity}",
        f"on_page_torture = {contract.on_page_torture}",
        f"child_harm = {contract.child_harm}",
        f"mandatory_ending_tone = {contract.mandatory_ending_tone.value}",
    ]
    rules.extend(contract.custom_rules)
    return rules


def _collect_contradictions(blueprint: StoryBlueprint) -> dict[str, list[str]]:
    """Extract character contradictions from identity psychology data."""
    result: dict[str, list[str]] = {}
    for c in blueprint.characters:
        if c.identity is None:
            continue
        raw = c.identity if isinstance(c.identity, dict) else {}
        psychology = raw.get("psychology", {}) if isinstance(raw, dict) else {}
        if isinstance(psychology, dict):
            cons = psychology.get("contradictions", [])
            if isinstance(cons, list) and len(cons) >= 2:
                result[c.name] = cons
    return result


def _arc_directive(c: Character) -> ArcDirective:
    nxt = c.next_milestone()
    state = c.current_state
    state_bits = [
        f"location={state.location or '?'}",
        f"physical={state.physical or 'ok'}",
        f"emotional={state.emotional or '?'}",
    ]
    return ArcDirective(
        character=c.name,
        arc_type=c.arc_type,
        current_pct=c.current_arc_percentage,
        next_milestone=(nxt.description if nxt else None),
        state_summary=", ".join(state_bits),
    )
