import json
from pathlib import Path
from unittest.mock import patch

import pytest

from auteur.cli import main
from auteur.llm import LLMResponse


SAMPLE_YAML = Path(__file__).parent.parent / "examples" / "sample_blueprint.yaml"


def _outline_yaml(tension: int = 4) -> str:
    return f"""
scope: chapter
chapter_index: 1
chapter_summary: A quiet return to the tavern.
scenes: [{{scene_id: s1, pov_character: Kael, location: taverntown, summary: drinks alone, key_events: [], character_state_changes: [], arc_advancements: [], estimated_tension: 4, emotional_tone: subtle unease}}]
arc_pushes: []
contract_compliance: []
expected_elements_touched: []
forbidden_tropes_avoided: [chosen_one_prophecy, resurrected_hero, deus_ex_machina_rescue]
estimated_chapter_tension: {tension}
thematic_reinforcement: redemption costs
conflict_report: null
"""


def test_cli_init_creates_project(tmp_path):
    target = tmp_path / "novel"
    rc = main(["init", str(target), "--from", str(SAMPLE_YAML)])
    assert rc == 0
    assert (target / "blueprint.yaml").exists()
    assert (target / "bible.json").exists()
    assert (target / "chapters").is_dir()


def test_cli_init_refuses_existing(tmp_path):
    target = tmp_path / "novel"
    main(["init", str(target), "--from", str(SAMPLE_YAML)])
    rc = main(["init", str(target), "--from", str(SAMPLE_YAML)])
    assert rc == 1


def test_cli_plan_still_works(tmp_path, capsys):
    rc = main(["plan", str(SAMPLE_YAML), "1"])
    assert rc == 0
    out = capsys.readouterr().out
    assert "SYSTEM PROMPT" in out


def _patch_client(scripted):
    from auteur.llm.fake import FakeClient
    return patch("auteur.cli._build_client", return_value=FakeClient(scripted))


def test_cli_draft_happy_path(tmp_path, capsys):
    target = tmp_path / "novel"
    main(["init", str(target), "--from", str(SAMPLE_YAML)])

    scripted = [
        LLMResponse(text=_outline_yaml(), input_tokens=50, output_tokens=80),
        LLMResponse(text="Chapter 1 prose.", input_tokens=20, output_tokens=10),
        *[LLMResponse(text="findings: []", input_tokens=1, output_tokens=1) for _ in range(5)],
    ]

    with _patch_client(scripted):
        rc = main(["draft", str(target), "1"])

    assert rc == 0
    assert (target / "chapters" / "01" / "final.md").exists()


def test_cli_draft_exhausted_returns_2(tmp_path):
    target = tmp_path / "novel"
    main(["init", str(target), "--from", str(SAMPLE_YAML)])

    fail_iter = [
        LLMResponse(text="The draft.", input_tokens=10, output_tokens=4),
        LLMResponse(text="""findings:
  - severity: error
    rule: forbidden_trope:chosen_one_prophecy
    evidence: x
    requested_change: y
""", input_tokens=5, output_tokens=10),
        *[LLMResponse(text="findings: []", input_tokens=1, output_tokens=1) for _ in range(4)],
    ]
    scripted = [LLMResponse(text=_outline_yaml(), input_tokens=50, output_tokens=80)] + fail_iter * 3

    with _patch_client(scripted):
        rc = main(["draft", str(target), "1", "--max-iterations", "3"])

    assert rc == 2


def test_cli_draft_conflict_returns_3(tmp_path):
    target = tmp_path / "novel"
    main(["init", str(target), "--from", str(SAMPLE_YAML)])

    conflict_yaml = """
scope: chapter
chapter_index: 1
chapter_summary: null
scenes: []
arc_pushes: []
contract_compliance: []
expected_elements_touched: []
forbidden_tropes_avoided: []
estimated_chapter_tension: null
thematic_reinforcement: null
conflict_report: "incompatible inputs"
"""
    scripted = [LLMResponse(text=conflict_yaml, input_tokens=5, output_tokens=10)]

    with _patch_client(scripted):
        rc = main(["draft", str(target), "1"])

    assert rc == 3


def test_cli_accept_promotes_latest_draft(tmp_path):
    target = tmp_path / "novel"
    main(["init", str(target), "--from", str(SAMPLE_YAML)])

    chapter_dir = target / "chapters" / "01"
    chapter_dir.mkdir(parents=True, exist_ok=True)
    (chapter_dir / "draft_v1.md").write_text("v1", encoding="utf-8")
    (chapter_dir / "draft_v2.md").write_text("v2 final", encoding="utf-8")
    (chapter_dir / "outline.yaml").write_text("estimated_chapter_tension: 4\nchapter_summary: ok\n", encoding="utf-8")

    rc = main(["accept", str(target), "1"])
    assert rc == 0
    assert (chapter_dir / "final.md").read_text(encoding="utf-8") == "v2 final"
    bible = json.loads((target / "bible.json").read_text(encoding="utf-8"))
    assert bible["realized_tension"] == [4]
