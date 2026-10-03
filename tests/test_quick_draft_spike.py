from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from auteur.cli import main
from auteur.cli_parser import build_parser
from auteur.llm import LLMResponse
from auteur.quick_draft import (
    DEFAULT_LENSES,
    STATUS,
    parse_quick_draft_args,
    prepare_quick_draft_shape_handoff,
    project_quick_draft_discoveries,
    project_quick_draft_session,
    run_quick_draft,
    save_quick_draft_revision,
)


PREMISE = (
    "Detective Miller learns that every suspect remembers a murder differently, "
    "and one version implicates him."
)
FIRST_SCENE = (
    "Miller interviews Suspect Vance, who calmly describes Miller committing "
    "the murder that Miller is supposed to investigate."
)


class FakeDraftLLM:
    def __init__(self) -> None:
        self.requests = []

    def complete(self, request):
        self.requests.append(request)
        return LLMResponse(
            text=(
                "# Chapter 1\n\n"
                "Vance did not look frightened. That was the first thing Miller noticed.\n\n"
                '\"You were holding the knife,\" Vance said.'
            ),
            input_tokens=120,
            output_tokens=45,
        )


def test_quick_draft_parser_accepts_exactly_two_story_inputs() -> None:
    args = parse_quick_draft_args([PREMISE, FIRST_SCENE])
    assert args.premise == PREMISE
    assert args.first_scene == FIRST_SCENE

    with pytest.raises(SystemExit):
        parse_quick_draft_args([PREMISE])
    with pytest.raises(SystemExit):
        parse_quick_draft_args([PREMISE, FIRST_SCENE, "extra decision"])


def test_quick_draft_creates_only_provisional_scaffolding_and_one_scene_draft(
    tmp_path: Path,
) -> None:
    llm = FakeDraftLLM()

    result = run_quick_draft(
        PREMISE,
        FIRST_SCENE,
        project_root=tmp_path,
        llm=llm,
        provider_label="fake",
    )

    assert result.draft_path.is_file()
    assert result.scaffold_path.is_file()
    assert len(llm.requests) == 1
    assert result.elapsed_seconds < 30.0

    draft = result.draft_path.read_text(encoding="utf-8")
    assert "Vance did not look frightened" in draft

    scaffold = yaml.safe_load(result.scaffold_path.read_text(encoding="utf-8"))
    assert scaffold["status"] == STATUS
    assert scaffold["authority"] == {
        "story_setup": "not_accepted",
        "structure": "not_accepted",
        "scene_draft": "working_only",
        "canon_acceptance": "deferred_until_after_draft",
        "structural_reconciliation": "deferred_until_after_draft",
    }
    assert scaffold["inputs"]["premise"] == PREMISE
    assert scaffold["inputs"]["first_scene_intent"] == FIRST_SCENE
    assert scaffold["draft"]["status"] == "draft_ready"
    assert scaffold["draft"]["accepted"] is False
    assert scaffold["draft"]["review_status"] == "not_reviewed"
    assert scaffold["draft"]["thirty_second_target_met"] is True

    lenses = scaffold["inferred_scaffolding"]["lenses"]
    assert [entry["name"] for entry in lenses] == list(DEFAULT_LENSES)
    assert {entry["status"] for entry in lenses} == {STATUS}
    identity = scaffold["inferred_scaffolding"]["identity_container"]
    assert identity["status"] == STATUS
    assert identity["target_experience"]["status"] == STATUS
    assert identity["story_type"]["status"] == STATUS
    assert identity["central_engine"]["status"] == STATUS
    assert scaffold["inferred_scaffolding"]["scene_plan"]["status"] == STATUS

    # The spike must not impersonate normal accepted project state.
    assert not (tmp_path / "story_identity.yaml").exists()
    assert not (tmp_path / "blueprint.yaml").exists()
    assert not (tmp_path / "bible.json").exists()
    assert not (tmp_path / "chapters" / "01" / "final.md").exists()
    assert not list(tmp_path.glob("**/validation_v*.json"))

    request = llm.requests[0]
    assert PREMISE in request.user
    assert FIRST_SCENE in request.user
    assert request.max_tokens == 1800


def test_quick_draft_cli_prints_draft_before_any_acceptance(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    llm = FakeDraftLLM()
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        "auteur.quick_draft._build_quick_draft_client",
        lambda: (llm, "fake"),
    )

    rc = main(["quick-draft", PREMISE, FIRST_SCENE])
    out = capsys.readouterr().out

    assert rc == 0
    assert "Quick Draft — working scene" in out
    assert "Nothing below is accepted story material yet." in out
    assert "Vance did not look frightened" in out
    assert "Story setup decisions and story updates are deferred" in out
    assert len(llm.requests) == 1

    sessions = list((tmp_path / ".auteur" / "quick_draft").iterdir())
    assert len(sessions) == 1
    assert (sessions[0] / "scene_draft.md").is_file()
    assert (sessions[0] / "scaffold.yaml").is_file()


def test_quick_draft_scaffold_is_explicitly_inferred_provisional(
    tmp_path: Path,
) -> None:
    llm = FakeDraftLLM()
    result = run_quick_draft(
        "A courier discovers the package she is delivering contains tomorrow's newspaper.",
        "She opens the paper and sees a photograph of herself being arrested tonight.",
        project_root=tmp_path,
        llm=llm,
        provider_label="fake",
    )
    text = result.scaffold_path.read_text(encoding="utf-8")

    assert "status: inferred_provisional" in text
    assert "story_setup: not_accepted" in text
    assert "structure: not_accepted" in text
    assert "canon_acceptance: deferred_until_after_draft" in text

def test_quick_draft_is_visible_in_top_level_help() -> None:
    help_text = build_parser().format_help()
    assert "quick-draft" in help_text
    assert "Experimental two-input path" in help_text


def test_identical_quick_drafts_do_not_collide_on_session_directory(
    tmp_path: Path,
) -> None:
    first = run_quick_draft(
        PREMISE,
        FIRST_SCENE,
        project_root=tmp_path,
        llm=FakeDraftLLM(),
        provider_label="fake",
    )
    second = run_quick_draft(
        PREMISE,
        FIRST_SCENE,
        project_root=tmp_path,
        llm=FakeDraftLLM(),
        provider_label="fake",
    )

    assert first.session_id != second.session_id
    assert first.session_dir.is_dir()
    assert second.session_dir.is_dir()

def test_quick_draft_cli_reports_provider_failure_without_traceback(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.chdir(tmp_path)

    def fail_provider():
        raise RuntimeError("no drafting provider configured")

    monkeypatch.setattr(
        "auteur.quick_draft._build_quick_draft_client",
        fail_provider,
    )

    rc = main(["quick-draft", PREMISE, FIRST_SCENE])
    captured = capsys.readouterr()

    assert rc == 1
    assert "Quick Draft could not start: no drafting provider configured" in captured.out
    assert "Traceback" not in captured.out
    assert "Traceback" not in captured.err

def test_quick_draft_keeps_ambiguous_pov_and_location_uncommitted(
    tmp_path: Path,
) -> None:
    llm = FakeDraftLLM()
    result = run_quick_draft(
        "Someone wakes with a key that should not exist.",
        "They try the key on the only locked door in the apartment.",
        project_root=tmp_path,
        llm=llm,
        provider_label="fake",
    )
    scaffold = yaml.safe_load(result.scaffold_path.read_text(encoding="utf-8"))
    scene = scaffold["inferred_scaffolding"]["scene_plan"]

    assert scene["status"] == STATUS
    assert scene["pov_character"] == ""
    assert scene["location"] == ""
    request = llm.requests[0]
    assert "Unspecified viewpoint" not in request.user
    assert "Infer naturally from the premise" not in request.user


def test_quick_draft_edits_preserve_history_and_surface_new_elements(
    tmp_path: Path,
) -> None:
    llm = FakeDraftLLM()
    result = run_quick_draft(
        PREMISE,
        FIRST_SCENE,
        project_root=tmp_path,
        llm=llm,
        provider_label="fake",
    )
    edited_text = (
        "At the abandoned seaside convent, Sister Beatrice tells Detective Miller "
        "that Suspect Vance slept there."
    )
    projection = save_quick_draft_revision(
        tmp_path,
        result.session_id,
        edited_text,
    )

    assert projection["draft"]["edit_count"] == 1
    assert projection["draft_text"].strip() == edited_text
    revisions = list((result.session_dir / "revisions").glob("scene_draft_v*.md"))
    assert len(revisions) == 1
    assert "Vance did not look frightened" in revisions[0].read_text(encoding="utf-8")

    discoveries = project_quick_draft_discoveries(tmp_path, result.session_id)
    values = {item["value"] for item in discoveries["discoveries"]}
    assert "Sister Beatrice" in values
    assert any("abandoned seaside convent" in value.lower() for value in values)

    loaded = project_quick_draft_session(tmp_path, result.session_id)
    assert loaded["draft_text"].strip() == edited_text

def test_quick_draft_shape_handoff_carries_only_explicitly_selected_discoveries(
    tmp_path: Path,
) -> None:
    result = run_quick_draft(
        PREMISE,
        FIRST_SCENE,
        project_root=tmp_path,
        llm=FakeDraftLLM(),
        provider_label="fake",
    )
    save_quick_draft_revision(
        tmp_path,
        result.session_id,
        (
            "At the abandoned seaside convent, Sister Beatrice tells Detective Miller "
            "that Suspect Vance slept there."
        ),
    )
    discoveries = project_quick_draft_discoveries(tmp_path, result.session_id)["discoveries"]
    sister = next(item for item in discoveries if item["value"] == "Sister Beatrice")

    path = prepare_quick_draft_shape_handoff(
        tmp_path,
        result.session_id,
        "workspace-quick",
        [sister],
    )
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))

    assert payload["canonical"] is False
    assert payload["status"] == "working_context"
    assert payload["workspace_id"] == "workspace-quick"
    assert payload["selected_discoveries"] == [sister]
    assert "abandoned seaside convent" not in {
        item["value"] for item in payload["selected_discoveries"]
    }
    assert (result.session_dir / "shape_handoff.yaml").is_file()


def test_quick_draft_shape_handoff_rejects_stale_or_invented_discovery(
    tmp_path: Path,
) -> None:
    result = run_quick_draft(
        PREMISE,
        FIRST_SCENE,
        project_root=tmp_path,
        llm=FakeDraftLLM(),
        provider_label="fake",
    )

    with pytest.raises(ValueError, match="not current"):
        prepare_quick_draft_shape_handoff(
            tmp_path,
            result.session_id,
            "workspace-quick",
            [{"kind": "place", "value": "Invented Castle"}],
        )

