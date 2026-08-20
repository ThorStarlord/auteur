from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from auteur.cli import main, parse_args
from auteur.narrative_ontology.architecture_preferences import (
    ComplexityPreference,
    NarrativeArchitecturePreferences,
)
from auteur.story_discovery_brief import DiscoveryBrief
from auteur.story_discovery_guidance import (
    BriefLifecycleState,
    guide_working_brief,
    inspect_working_brief,
    intent_aware_run_matches_brief,
)


def _feed(*answers: str):
    values = iter(answers)

    def _reader(_prompt: str) -> str:
        return next(values)

    return _reader


def _write_yaml(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")


def test_start_is_first_class_story_discovery_command() -> None:
    args = parse_args(["story-discovery", "start", "--project", "."])

    assert args.command == "story-discovery"
    assert args.story_discovery_command == "start"
    assert args.project == Path(".")
    assert args.brief is None
    assert args.premise is None


def test_fresh_guided_capture_writes_minimum_adequate_brief_and_preserves_omissions(
    tmp_path: Path,
) -> None:
    transcript: list[str] = []
    brief = guide_working_brief(
        tmp_path,
        input_fn=_feed(
            "A damaged station AI must decide which trapped crew to wake.",
            "science fiction",
            "adult",
            "grief becoming costly agency",
        ),
        output_fn=transcript.append,
    )

    path = tmp_path / "story_discovery" / "brief.yaml"
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert brief.story_type is not None
    assert brief.story_type.genre.value == "sci_fi"
    assert brief.story_type.target_audience.value == "adult"
    assert brief.target_experience is not None
    assert brief.target_experience.primary == "grief becoming costly agency"
    assert payload["story_type"] == {"genre": "sci_fi", "target_audience": "adult"}
    assert "architecture_preferences" not in payload
    assert "hard_constraints" not in payload
    assert inspect_working_brief(tmp_path).state is BriefLifecycleState.ADEQUATE


def test_resume_asks_only_fields_still_missing(tmp_path: Path) -> None:
    _write_yaml(
        tmp_path / "story_discovery" / "brief.yaml",
        {
            "premise": "An elevator murder should be physically impossible.",
            "story_type": {"genre": "mystery"},
        },
    )
    prompts: list[str] = []
    answers = iter(["adult", "claustrophobic suspicion"])

    def _reader(prompt: str) -> str:
        prompts.append(prompt)
        return next(answers)

    brief = guide_working_brief(tmp_path, input_fn=_reader, output_fn=lambda _text: None)

    assert len(prompts) == 2
    assert brief.premise == "An elevator murder should be physically impossible."
    assert brief.story_type is not None
    assert brief.story_type.genre.value == "mystery"
    assert brief.story_type.target_audience.value == "adult"


def test_invalid_enum_reprompts_without_persisting_invalid_state(tmp_path: Path) -> None:
    answers = iter(["A premise.", "not-a-genre", "mystery", "adult", "suspicion"])
    transcript: list[str] = []

    guide_working_brief(
        tmp_path,
        input_fn=lambda _prompt: next(answers),
        output_fn=transcript.append,
    )

    payload = yaml.safe_load((tmp_path / "story_discovery" / "brief.yaml").read_text())
    assert payload["story_type"]["genre"] == "mystery"
    assert any("didn't recognize" in line for line in transcript)


def test_existing_optional_commitments_survive_resume_unchanged(tmp_path: Path) -> None:
    preferences = NarrativeArchitecturePreferences(complexity=ComplexityPreference.MAXIMALIST)
    _write_yaml(
        tmp_path / "story_discovery" / "brief.yaml",
        {
            "premise": "A premise.",
            "story_type": {"genre": "mystery"},
            "architecture_preferences": preferences.model_dump(mode="json", exclude_none=True),
            "hard_constraints": ["No supernatural explanation."],
        },
    )

    brief = guide_working_brief(
        tmp_path,
        input_fn=_feed("adult", "suspicion"),
        output_fn=lambda _text: None,
    )

    assert brief.architecture_preferences == preferences
    assert brief.hard_constraints == ["No supernatural explanation."]


def test_invalid_existing_brief_is_fail_closed_and_not_overwritten(tmp_path: Path) -> None:
    path = tmp_path / "story_discovery" / "brief.yaml"
    path.parent.mkdir(parents=True)
    original = "premise: [broken\n"
    path.write_text(original, encoding="utf-8")

    with pytest.raises(ValueError, match="Cannot safely resume invalid"):
        guide_working_brief(tmp_path, input_fn=_feed("ignored"))

    assert path.read_text(encoding="utf-8") == original
    assert inspect_working_brief(tmp_path).state is BriefLifecycleState.INVALID


def test_premise_flag_can_seed_new_brief_from_project_relative_file(tmp_path: Path) -> None:
    premise_file = tmp_path / "premise.txt"
    premise_file.write_text("A sealed-room mystery.", encoding="utf-8")

    brief = guide_working_brief(
        tmp_path,
        premise="premise.txt",
        input_fn=_feed("mystery", "adult", "mounting suspicion"),
        output_fn=lambda _text: None,
    )

    assert brief.premise == "A sealed-room mystery."


def test_premise_flag_does_not_silently_replace_existing_brief(tmp_path: Path) -> None:
    _write_yaml(tmp_path / "story_discovery" / "brief.yaml", {"premise": "Original."})

    with pytest.raises(ValueError, match="will not silently replace"):
        guide_working_brief(tmp_path, premise="Replacement.")

    loaded = DiscoveryBrief.from_yaml(tmp_path / "story_discovery" / "brief.yaml")
    assert loaded.premise == "Original."


def test_matching_run_uses_declared_content_not_brief_source_path(tmp_path: Path) -> None:
    brief = guide_working_brief(
        tmp_path,
        input_fn=_feed("A premise.", "mystery", "adult", "suspicion"),
        output_fn=lambda _text: None,
    )
    _write_yaml(
        tmp_path / "story_discovery" / "discovery_set.yaml",
        {
            "intent_mode": "intent_aware",
            "declared_author_intent": brief.declared_intent(),
            "source_brief_path": "some/old/location.yaml",
        },
    )

    assert intent_aware_run_matches_brief(tmp_path, brief) is True


def test_changed_declared_content_makes_existing_run_stale(tmp_path: Path) -> None:
    brief = guide_working_brief(
        tmp_path,
        input_fn=_feed("A premise.", "mystery", "adult", "suspicion"),
        output_fn=lambda _text: None,
    )
    _write_yaml(
        tmp_path / "story_discovery" / "discovery_set.yaml",
        {
            "intent_mode": "intent_aware",
            "declared_author_intent": brief.declared_intent(),
        },
    )
    changed_payload = brief.declared_intent()
    changed_payload["target_experience"] = {"primary_emotional_promise": "relief"}
    changed = DiscoveryBrief.model_validate(changed_payload)

    assert intent_aware_run_matches_brief(tmp_path, changed) is False


def test_interruption_preserves_last_successful_answer(tmp_path: Path, monkeypatch, capsys) -> None:
    answers = iter(["A premise.", "mystery"])

    def _interrupt(_prompt: str) -> str:
        try:
            return next(answers)
        except StopIteration:
            raise KeyboardInterrupt from None

    monkeypatch.setattr("builtins.input", _interrupt)

    exit_code = main(["story-discovery", "start", "--project", str(tmp_path)])
    captured = capsys.readouterr()

    assert exit_code == 130
    assert "brief has been saved" in captured.err
    payload = yaml.safe_load((tmp_path / "story_discovery" / "brief.yaml").read_text())
    assert payload["premise"] == "A premise."
    assert payload["story_type"]["genre"] == "mystery"
    assert "target_audience" not in payload["story_type"]


def test_start_never_constructs_provider(tmp_path: Path, monkeypatch) -> None:
    def _explode(*_args, **_kwargs):
        raise AssertionError("guided brief capture must remain provider-free")

    monkeypatch.setattr("auteur.llm.factory.build_client", _explode)

    brief = guide_working_brief(
        tmp_path,
        input_fn=_feed("A premise.", "mystery", "adult", "suspicion"),
        output_fn=lambda _text: None,
    )

    assert brief.story_type is not None
    assert brief.story_type.genre.value == "mystery"


def test_cli_inadequate_brief_recovery_is_writer_facing_and_pre_provider(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    path = tmp_path / "brief.yaml"
    path.write_text("premise: A premise.\n", encoding="utf-8")

    def _explode(*_args, **_kwargs):
        raise AssertionError("provider must not be constructed for inadequate intent")

    monkeypatch.setattr("auteur.llm.factory.build_client", _explode)

    exit_code = main(
        ["story-discovery", "run", "--brief", str(path), "--recommend"]
    )
    captured = capsys.readouterr()

    assert exit_code == 1
    assert "do not yet know enough" in captured.err
    assert "Continue the brief" in captured.err
    assert "story_type.genre" in captured.err
    assert "story_type.target_audience" in captured.err
    assert "target_experience" in captured.err
