from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from auteur.cli import main
from auteur.llm import LLMResponse
from auteur.quick_draft import (
    DEFAULT_LENSES,
    STATUS,
    parse_quick_draft_args,
    run_quick_draft,
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
    assert "Story setup acceptance and structural reconciliation are deferred" in out
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
