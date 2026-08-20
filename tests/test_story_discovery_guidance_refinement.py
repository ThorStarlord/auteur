from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from auteur.cli import parse_args
from auteur.story_discovery_guidance import (
    BriefLifecycleState,
    guide_working_brief,
    inspect_working_brief,
    intent_aware_run_matches_brief,
)
from auteur.story_discovery_edit import edit_working_brief
from auteur.story_discovery_refinement import refine_working_brief


def _feed(*answers: str):
    values = iter(answers)

    def _reader(_prompt: str) -> str:
        return next(values)

    return _reader


def _seed_minimum(tmp_path: Path):
    return guide_working_brief(
        tmp_path,
        input_fn=_feed(
            "A damaged station AI must decide which trapped crew to wake.",
            "science fiction",
            "adult",
            "grief becoming costly agency",
        ),
        output_fn=lambda _text: None,
    )


def test_start_parser_exposes_refine_and_edit_as_distinct_modes() -> None:
    refine = parse_args(["story-discovery", "start", "--project", ".", "--refine"])
    edit = parse_args(["story-discovery", "start", "--project", ".", "--edit"])

    assert refine.command == "story-discovery"
    assert refine.story_discovery_command == "start"
    assert refine.refine is True
    assert refine.edit is False
    assert edit.edit is True
    assert edit.refine is False

    with pytest.raises(SystemExit):
        parse_args(["story-discovery", "start", "--refine", "--edit"])


def test_refine_adds_rich_existing_intent_with_writer_facing_architecture_aliases(
    tmp_path: Path,
) -> None:
    _seed_minimum(tmp_path)

    brief = refine_working_brief(
        tmp_path,
        input_fn=_feed(
            "dread, hard-won tenderness",
            "nihilistic inevitability",
            "yes",
            "grief -> pressure -> chosen responsibility",
            "grief",
            "pressure",
            "chosen responsibility",
            "richly interconnected",
            "several interacting causes",
            "one main engine with substantial supporting layers",
            "novel",
            "procedural",
            "No supernatural rescue.",
            "The station remains physically failing.",
            "",
        ),
        output_fn=lambda _text: None,
    )

    declared = brief.declared_intent()
    assert brief.target_experience is not None
    assert brief.target_experience.secondary_palette == ["dread", "hard-won tenderness"]
    assert brief.target_experience.avoided_experiences == ["nihilistic inevitability"]
    assert brief.target_experience.emotional_trajectory is not None
    assert brief.target_experience.emotional_trajectory.ending == "chosen responsibility"
    assert declared["architecture_preferences"] == {
        "complexity": "maximalist",
        "causal_distribution": "mixed",
        "engine_hierarchy": "primary_with_layers",
    }
    assert declared["story_type"]["medium"] == "novel"
    assert declared["story_type"]["mode"] == "procedural"
    assert brief.hard_constraints == [
        "No supernatural rescue.",
        "The station remains physically failing.",
    ]


def test_refine_not_sure_keeps_optional_intent_unknown(tmp_path: Path) -> None:
    brief = _seed_minimum(tmp_path)

    refined = refine_working_brief(
        tmp_path,
        input_fn=_feed(
            "not sure",
            "not sure",
            "not sure",
            "not sure",
            "not sure",
            "not sure",
            "not sure",
            "not sure",
            "not sure",
        ),
        output_fn=lambda _text: None,
    )

    declared = refined.declared_intent()
    assert declared == brief.declared_intent()
    assert "architecture_preferences" not in declared
    assert "hard_constraints" not in declared
    assert "medium" not in declared["story_type"]
    assert "mode" not in declared["story_type"]
    target = declared["target_experience"]
    assert "secondary_palette" not in target
    assert "avoided_experiences" not in target
    assert "emotional_trajectory" not in target


def test_refinement_makes_previous_intent_aware_run_stale_by_content(tmp_path: Path) -> None:
    original = _seed_minimum(tmp_path)
    discovery_dir = tmp_path / "story_discovery"
    (discovery_dir / "discovery_set.yaml").write_text(
        yaml.safe_dump(
            {
                "intent_mode": "intent_aware",
                "declared_author_intent": original.declared_intent(),
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    assert intent_aware_run_matches_brief(tmp_path, original) is True

    refined = refine_working_brief(
        tmp_path,
        input_fn=_feed(
            "dread",
            "not sure",
            "not sure",
            "not sure",
            "not sure",
            "not sure",
            "not sure",
            "not sure",
            "not sure",
        ),
        output_fn=lambda _text: None,
    )

    assert intent_aware_run_matches_brief(tmp_path, refined) is False


def test_edit_can_intentionally_make_brief_incomplete_again(tmp_path: Path) -> None:
    _seed_minimum(tmp_path)

    edited = edit_working_brief(
        tmp_path,
        input_fn=_feed("genre", "not sure", "done"),
        output_fn=lambda _text: None,
    )

    assert edited.story_type is not None
    assert edited.story_type.genre is None
    assert edited.story_type.target_audience is not None
    assert inspect_working_brief(tmp_path).state is BriefLifecycleState.INCOMPLETE
    payload = yaml.safe_load((tmp_path / "story_discovery" / "brief.yaml").read_text())
    assert "genre" not in payload["story_type"]


def test_edit_clear_primary_removes_target_experience_as_one_valid_unit(tmp_path: Path) -> None:
    _seed_minimum(tmp_path)
    refine_working_brief(
        tmp_path,
        input_fn=_feed(
            "dread",
            "not sure",
            "not sure",
            "not sure",
            "not sure",
            "not sure",
            "not sure",
            "not sure",
            "not sure",
        ),
        output_fn=lambda _text: None,
    )

    edited = edit_working_brief(
        tmp_path,
        input_fn=_feed("primary", "clear", "done"),
        output_fn=lambda _text: None,
    )

    assert edited.target_experience is None
    assert inspect_working_brief(tmp_path).state is BriefLifecycleState.INCOMPLETE
    payload = yaml.safe_load((tmp_path / "story_discovery" / "brief.yaml").read_text())
    assert "target_experience" not in payload


def test_edit_emotional_trajectory_is_atomic_on_interruption(tmp_path: Path) -> None:
    _seed_minimum(tmp_path)
    before = (tmp_path / "story_discovery" / "brief.yaml").read_text(encoding="utf-8")
    answers = iter(["trajectory", "rise then fall", "fear"])

    def _interrupt(_prompt: str) -> str:
        try:
            return next(answers)
        except StopIteration:
            raise KeyboardInterrupt from None

    with pytest.raises(KeyboardInterrupt):
        edit_working_brief(tmp_path, input_fn=_interrupt, output_fn=lambda _text: None)

    assert (tmp_path / "story_discovery" / "brief.yaml").read_text(encoding="utf-8") == before


def test_edit_replaces_hard_constraints_with_literal_author_text(tmp_path: Path) -> None:
    _seed_minimum(tmp_path)

    edited = edit_working_brief(
        tmp_path,
        input_fn=_feed(
            "constraints",
            "No supernatural explanation — ever.",
            "The killer never leaves the elevator.",
            "",
            "done",
        ),
        output_fn=lambda _text: None,
    )

    assert edited.hard_constraints == [
        "No supernatural explanation — ever.",
        "The killer never leaves the elevator.",
    ]


def test_refine_and_edit_remain_provider_free(tmp_path: Path, monkeypatch) -> None:
    _seed_minimum(tmp_path)

    def _explode(*_args, **_kwargs):
        raise AssertionError("G1b guidance must never construct an LLM provider")

    monkeypatch.setattr("auteur.llm.factory.build_client", _explode)

    refine_working_brief(
        tmp_path,
        input_fn=_feed(
            "not sure",
            "not sure",
            "not sure",
            "not sure",
            "not sure",
            "not sure",
            "not sure",
            "not sure",
            "not sure",
        ),
        output_fn=lambda _text: None,
    )
    edit_working_brief(
        tmp_path,
        input_fn=_feed("genre", "mystery", "done"),
        output_fn=lambda _text: None,
    )
