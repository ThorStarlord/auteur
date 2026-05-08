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


def test_cli_structure_diagnose_prints_json_report_for_clean_blueprint(capsys):
    rc = main(["structure", "diagnose", str(SAMPLE_YAML)])

    assert rc == 0
    report = json.loads(capsys.readouterr().out)
    assert report["diagnostics"] == []


def test_cli_structure_diagnose_writes_json_report_to_output_path(tmp_path):
    output_path = tmp_path / "structure" / "diagnostics" / "report.json"

    rc = main(["structure", "diagnose", str(SAMPLE_YAML), "--output", str(output_path)])

    assert rc == 0
    assert json.loads(output_path.read_text(encoding="utf-8")) == {"diagnostics": []}


def test_cli_structure_diagnose_returns_4_for_error_diagnostics(tmp_path, capsys):
    blueprint_path = tmp_path / "missing_story_engine.yaml"
    blueprint_path.write_text(
        """
identity:
  title: Test Story
  author_intent: A test premise.
  length_class: novel
  genre: literary
  target_audience: adult
  pov_type: third_person_limited_single
contract:
  content_rating: PG
  mandatory_ending_tone: open
emotional_design:
  overall_emotional_arc: quiet pressure
theme:
  central_question: What does truth cost?
  thesis: Truth costs belonging.
  motifs: []
""",
        encoding="utf-8",
    )

    rc = main(["structure", "diagnose", str(blueprint_path)])

    assert rc == 4
    report = json.loads(capsys.readouterr().out)
    assert report["diagnostics"][0]["rule"] == "story_engine.missing"


def test_cli_structure_diagnose_returns_0_for_warning_only_report(tmp_path, capsys):
    blueprint_path = tmp_path / "warning_only.yaml"
    blueprint_path.write_text(
        """
identity:
  title: Test Story
  author_intent: A test premise.
  length_class: novel
  genre: literary
  target_audience: adult
  pov_type: third_person_limited_single
story_engine:
  main_thread:
    want:
      author_text: The protagonist wants to expose the town's founding lie.
      checkable_claims: []
    resistance:
      author_text: The town needs the lie to survive.
      checkable_claims: []
    conflict:
      author_text: Revealing truth saves conscience but destroys home.
      checkable_claims: []
    stakes:
      author_text: Each step toward truth costs a relationship.
      checkable_claims: []
    change:
      author_text: The protagonist learns truth may require exile.
      checkable_claims: []
    thematic_function: Tests that truth costs belonging through the main plot.
  threads:
    - name: Political pressure
      type: political
      want:
        author_text: The mayor wants to keep the founding crime buried.
        checkable_claims: []
      resistance:
        author_text: The protagonist keeps finding witnesses.
        checkable_claims: []
      conflict:
        author_text: Order depends on a public lie.
        checkable_claims: []
      stakes:
        author_text: Exposure may collapse the town's fragile peace.
        checkable_claims: []
      change:
        author_text: The bargain moves from rumor to open coercion.
        checkable_claims: []
      supports_main_by: [escalates]
      thematic_function: Shows that truth costs belonging at civic scale.
contract:
  content_rating: PG
  mandatory_ending_tone: open
emotional_design:
  overall_emotional_arc: quiet pressure
theme:
  central_question: What does truth cost?
  thesis: Truth costs belonging.
  motifs: []
""",
        encoding="utf-8",
    )

    rc = main(["structure", "diagnose", str(blueprint_path)])

    assert rc == 0
    report = json.loads(capsys.readouterr().out)
    assert report["diagnostics"][0]["severity"] == "warning"
    assert report["diagnostics"][0]["rule"] == "structure.subplot_budget.missing"


def test_cli_structure_diagnose_missing_blueprint_returns_1(tmp_path, capsys):
    missing_path = tmp_path / "missing.yaml"

    rc = main(["structure", "diagnose", str(missing_path)])

    assert rc == 1
    assert "Error: blueprint not found" in capsys.readouterr().err


def test_cli_structure_diagnose_malformed_blueprint_returns_1(tmp_path, capsys):
    blueprint_path = tmp_path / "malformed.yaml"
    blueprint_path.write_text("identity: [", encoding="utf-8")

    rc = main(["structure", "diagnose", str(blueprint_path)])

    assert rc == 1
    assert "Error: invalid blueprint" in capsys.readouterr().err


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


def test_cli_retry_continues_from_latest_failed_draft(tmp_path):
    target = tmp_path / "novel"
    main(["init", str(target), "--from", str(SAMPLE_YAML)])

    chapter_dir = target / "chapters" / "01"
    chapter_dir.mkdir(parents=True, exist_ok=True)
    (chapter_dir / "outline.yaml").write_text(_outline_yaml(), encoding="utf-8")
    for version in range(1, 4):
        (chapter_dir / f"draft_v{version}.md").write_text(f"old v{version}", encoding="utf-8")
        validation = {
            "chapter_index": 1,
            "iteration": version,
            "passed": False,
            "findings": [
                {
                    "critic": "contract",
                    "severity": "error",
                    "rule": "forbidden_trope:chosen_one_prophecy",
                    "evidence": "prophecy framing",
                    "requested_change": "remove prophecy framing",
                }
            ],
        }
        (chapter_dir / f"validation_v{version}.json").write_text(json.dumps(validation), encoding="utf-8")

    scripted = [LLMResponse(text="findings: []", input_tokens=1, output_tokens=1) for _ in range(7)]
    with _patch_client(scripted):
        rc = main(["retry", str(target), "1", "--max-iterations", "1"])

    assert rc == 0
    assert (chapter_dir / "draft_v1.md").read_text(encoding="utf-8") == "old v1"
    assert (chapter_dir / "draft_v4.md").exists()
    assert (chapter_dir / "validation_v4.json").exists()
