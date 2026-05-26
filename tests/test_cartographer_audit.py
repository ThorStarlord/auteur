"""Tests for cartographer_audit — cross-layer validation of cartographer outline
against story engine.
"""
from __future__ import annotations

import pytest

from auteur.blueprint import StoryBlueprint
from auteur.cartographer_outline import (
    ArcAdvancement,
    CartographerOutline,
    ContractComplianceItem,
    OutlineScene,
    StateChange,
)
from auteur.structure.cartographer_audit import (
    _extract_keywords,
    audit_outline_vs_story_engine,
)
from auteur.structure.diagnostics import DiagnosticSeverity, StructureDiagnostic

_MINIMAL_DATA: dict = {
    "identity": {
        "title": "The Long Road",
        "author_intent": "A war veteran seeks redemption after betraying his unit.",
        "length_class": "novel",
        "genre": "literary",
        "mode": "tragic",
        "target_audience": "adult",
        "pov_type": "third_person_limited_single",
        "target_experience": {
            "primary": "catharsis",
            "progression": "guilt -> confrontation -> acceptance",
        },
    },
    "contract": {
        "content_rating": "R",
        "mandatory_ending_tone": "bittersweet",
    },
    "emotional_design": {
        "overall_emotional_arc": "guilt -> confrontation -> acceptance",
    },
    "theme": {
        "central_question": "Can a person be forgiven?",
        "thesis": "Redemption requires dismantling the self-lie.",
        "motifs": ["silence", "maps"],
    },
    "characters": [
        {
            "name": "Kael",
            "role": "protagonist",
            "arc_type": "growth",
            "arc_start_percentage": 0,
            "arc_end_percentage": 100,
        },
    ],
    "story_engine": {
        "main_thread": {
            "type": "main_plot",
            "want": {
                "author_text": "Kael wants to uncover the truth about the siege",
                "checkable_claims": [],
            },
            "resistance": {
                "author_text": "His former commander protects the lie",
                "checkable_claims": [],
            },
            "conflict": {
                "author_text": "Truth vs loyalty",
                "checkable_claims": [],
            },
            "stakes": {
                "author_text": "Kael's soul and his family name",
                "checkable_claims": [],
            },
            "change": {
                "author_text": "Kael accepts that redemption costs more than guilt",
                "checkable_claims": [],
            },
            "thematic_function": "Dramatises the thesis through Kael's journey.",
        },
        "threads": [
            {
                "name": "Kael_arc",
                "type": "character_arc",
                "want": {
                    "author_text": "Kael wants to reckon with his past",
                    "checkable_claims": [],
                },
                "resistance": {
                    "author_text": "Denial protects him from the truth",
                    "checkable_claims": [],
                },
                "conflict": {
                    "author_text": "Memory vs self-image",
                    "checkable_claims": [],
                },
                "stakes": {
                    "author_text": "His identity and peace of mind",
                    "checkable_claims": [],
                },
                "change": {
                    "author_text": "From denial to acceptance",
                    "checkable_claims": [],
                },
                "supports_main_by": ["pressures_change"],
                "thematic_function": "Mirrors the thesis of self-lie dismantling.",
            },
        ],
    },
}


@pytest.fixture
def blueprint_with_engine() -> StoryBlueprint:
    return StoryBlueprint.model_validate(_MINIMAL_DATA)


@pytest.fixture
def blueprint_no_engine() -> StoryBlueprint:
    data = dict(_MINIMAL_DATA)
    del data["story_engine"]
    return StoryBlueprint.model_validate(data)


def _scene(scene_id: str, summary: str = "", pov: str = "Kael",
           tension: int | None = None, tone: str | None = None,
           key_events: list[str] | None = None) -> OutlineScene:
    return OutlineScene(
        scene_id=scene_id,
        pov_character=pov,
        summary=summary,
        key_events=key_events or [],
        estimated_tension=tension,
        emotional_tone=tone,
    )


def _outline(scenes: list[OutlineScene] | None = None,
             thematic_reinforcement: str | None = None,
             conflict_report: str | None = None) -> CartographerOutline:
    return CartographerOutline(
        chapter_summary="Test chapter summary." if not conflict_report else None,
        scenes=scenes or [],
        thematic_reinforcement=thematic_reinforcement,
        conflict_report=conflict_report,
    )


class TestExtractKeywords:
    def test_removes_stop_words(self) -> None:
        result = _extract_keywords("the quick brown fox")
        assert "quick" in result
        assert "brown" in result
        assert "the" not in result

    def test_short_words_are_excluded(self) -> None:
        result = _extract_keywords("on at to the cat dog")
        assert result == []

    def test_maintains_case_insensitivity(self) -> None:
        result = _extract_keywords("THE QUICK BROWN FOX")
        assert "quick" in result


class TestAuditOutlineVsStoryEngine:
    def test_returns_empty_when_outline_is_none(self, blueprint_with_engine: StoryBlueprint) -> None:
        result = audit_outline_vs_story_engine(blueprint_with_engine, None)
        assert len(result) == 0

    def test_returns_warning_when_no_story_engine(self, blueprint_no_engine: StoryBlueprint) -> None:
        outline = _outline(conflict_report="Input contradiction — cannot plan this chapter.")
        result = audit_outline_vs_story_engine(blueprint_no_engine, outline)
        assert len(result) == 1
        assert result[0].rule == "cartographer.story_engine_missing"

    def test_no_diagnostics_when_outline_enacts_threads(self, blueprint_with_engine: StoryBlueprint) -> None:
        outline = _outline(
            scenes=[
                _scene("s1", "Kael seeks the truth about the siege", key_events=["confrontation", "truth"]),
            ],
            thematic_reinforcement="Kael begins dismantling his self-lie.",
        )
        result = audit_outline_vs_story_engine(blueprint_with_engine, outline)
        thread_diags = [d for d in result if "thread" in d.rule]
        assert len(thread_diags) == 0

    def test_warns_when_main_thread_unseen(self, blueprint_with_engine: StoryBlueprint) -> None:
        outline = _outline(
            scenes=[
                _scene("s1", "Kael drinks at a tavern", key_events=["drinking", "brooding"]),
            ],
        )
        result = audit_outline_vs_story_engine(blueprint_with_engine, outline)
        matching = [d for d in result if d.rule == "cartographer.thread.main_thread_unseen"]
        assert len(matching) >= 1

    def test_warns_when_thread_carriers_absent(self, blueprint_with_engine: StoryBlueprint) -> None:
        outline = _outline(
            scenes=[
                _scene("s1", "A stranger appears", pov="Stranger", key_events=["arrival"]),
            ],
        )
        result = audit_outline_vs_story_engine(blueprint_with_engine, outline)
        matching = [d for d in result if d.rule == "cartographer.thread.subordinate_threads_absent"]
        assert len(matching) >= 1

    def test_informs_when_contradiction_unsurfaced(self, blueprint_with_engine: StoryBlueprint) -> None:
        data = dict(_MINIMAL_DATA)
        data["characters"][0]["identity"] = {
            "psychology": {
                "contradictions": ["brave_but_cowardly", "honest_but_deceitful"],
            }
        }
        bp = StoryBlueprint.model_validate(data)
        outline = _outline(
            scenes=[
                _scene("s1", "Kael walks through a field", key_events=["walking", "thinking"]),
            ],
        )
        result = audit_outline_vs_story_engine(bp, outline)
        matching = [d for d in result if d.rule == "cartographer.character.contradiction_unsurfaced"]
        assert len(matching) == 1

    def test_informs_when_thesis_unreinforced(self, blueprint_with_engine: StoryBlueprint) -> None:
        outline = _outline(
            scenes=[
                _scene("s1", "Kael seeks the truth", key_events=["investigation"]),
            ],
            thematic_reinforcement="This chapter shows Kael being active.",
        )
        result = audit_outline_vs_story_engine(blueprint_with_engine, outline)
        matching = [d for d in result if d.rule == "cartographer.theme.thesis_unreinforced"]
        assert len(matching) == 1

    def test_thesis_reinforced_when_matched(self, blueprint_with_engine: StoryBlueprint) -> None:
        outline = _outline(
            scenes=[
                _scene("s1", "Kael seeks the truth", key_events=["confrontation"]),
            ],
            thematic_reinforcement="Kael begins dismantling his self-lie.",
        )
        result = audit_outline_vs_story_engine(blueprint_with_engine, outline)
        matching = [d for d in result if d.rule == "cartographer.theme.thesis_unreinforced"]
        assert len(matching) == 0

    def test_warns_on_low_tension_with_high_energy_tone(self, blueprint_with_engine: StoryBlueprint) -> None:
        outline = _outline(
            scenes=[
                _scene("s1", "A battle erupts", tension=2, tone="violent battle explosion"),
            ],
        )
        result = audit_outline_vs_story_engine(blueprint_with_engine, outline)
        matching = [d for d in result if d.rule == "cartographer.character.scene_energy_mismatch"]
        assert len(matching) == 1

    def test_warns_on_high_tension_with_low_energy_tone(self, blueprint_with_engine: StoryBlueprint) -> None:
        outline = _outline(
            scenes=[
                _scene("s1", "Quiet reflection", tension=9, tone="calm peaceful bonding"),
            ],
        )
        result = audit_outline_vs_story_engine(blueprint_with_engine, outline)
        matching = [d for d in result if d.rule == "cartographer.character.scene_energy_mismatch"]
        assert len(matching) == 1

    def test_no_energy_mismatch_when_aligned(self, blueprint_with_engine: StoryBlueprint) -> None:
        outline = _outline(
            scenes=[
                _scene("s1", "A tense standoff", tension=8, tone="intense confrontation"),
                _scene("s2", "Quiet recovery", tension=2, tone="calm reflective"),
            ],
        )
        result = audit_outline_vs_story_engine(blueprint_with_engine, outline)
        matching = [d for d in result if d.rule == "cartographer.character.scene_energy_mismatch"]
        assert len(matching) == 0

    def test_no_mismatch_when_tension_or_tone_missing(self, blueprint_with_engine: StoryBlueprint) -> None:
        outline = _outline(
            scenes=[
                _scene("s1", "A scene", tension=None, tone=None),
            ],
        )
        result = audit_outline_vs_story_engine(blueprint_with_engine, outline)
        matching = [d for d in result if d.rule == "cartographer.character.scene_energy_mismatch"]
        assert len(matching) == 0

    def test_repair_options_have_preserve_and_challenge(self, blueprint_with_engine: StoryBlueprint) -> None:
        outline = _outline(conflict_report="Cannot plan — contradictory inputs.")
        result = audit_outline_vs_story_engine(blueprint_with_engine, outline)
        for d in result:
            if d.repair_options:
                assert isinstance(d.repair_options.preserve_intent, list)
                assert isinstance(d.repair_options.challenge_intent, list)
