"""End-to-end smoke test for Engine v1 against the sample blueprint.

Iteration 1 violates a forbidden trope; iteration 2 fixes it. The test
asserts: final.md is written, bible records the event and tension, and
the chapter directory contains every expected artifact.
"""

import json
from pathlib import Path
from unittest.mock import patch

from auteur.cli import main
from auteur.llm import LLMResponse


SAMPLE_YAML = Path(__file__).parent.parent / "examples" / "sample_blueprint.yaml"


def _outline(tension: int = 4) -> str:
    return f"""
scope: chapter
chapter_index: 1
chapter_summary: Kael returns to the tavern with a broken arm.
scenes:
  - scene_id: s1
    pov_character: Kael
    location: taverntown
    summary: He nurses a drink and reflects.
    key_events: [drinks, broods, refuses Lira's offer of help]
    character_state_changes: []
    arc_advancements: []
    estimated_tension: {tension}
    emotional_tone: subtle unease
arc_pushes: []
contract_compliance: []
expected_elements_touched: []
forbidden_tropes_avoided: [chosen_one_prophecy, resurrected_hero, deus_ex_machina_rescue]
estimated_chapter_tension: {tension}
thematic_reinforcement: redemption costs more than Kael wants to admit.
conflict_report: null
"""


def _all_pass_critics():
    return [LLMResponse(text="findings: []", input_tokens=1, output_tokens=1) for _ in range(5)]


def _failing_contract_then_pass_others():
    fail = LLMResponse(
        text="""findings:
  - severity: error
    rule: forbidden_trope:chosen_one_prophecy
    evidence: "scene 1: a prophecy named him chosen heir"
    requested_change: "remove all prophecy framing"
""",
        input_tokens=5,
        output_tokens=20,
    )
    others = [LLMResponse(text="findings: []", input_tokens=1, output_tokens=1) for _ in range(4)]
    return [fail, *others]


def test_engine_v1_smoke_fail_then_pass(tmp_path):
    target = tmp_path / "shattered_crown"
    rc = main(["init", str(target), "--from", str(SAMPLE_YAML)])
    assert rc == 0

    scripted = [
        LLMResponse(text=_outline(), input_tokens=80, output_tokens=120),
        LLMResponse(text="The first draft, with a prophecy...", input_tokens=20, output_tokens=10),
        *_failing_contract_then_pass_others(),
        LLMResponse(text="The second draft, prophecy excised. Just Kael at the tavern.",
                    input_tokens=25, output_tokens=15),
        *_all_pass_critics(),
    ]

    from auteur.llm.fake import FakeClient
    with patch("auteur.cli._build_client", return_value=FakeClient(scripted)):
        rc = main(["draft", str(target), "1", "--max-iterations", "3"])

    assert rc == 0

    chapter_dir = target / "chapters" / "01"
    assert (chapter_dir / "outline.yaml").exists()
    assert (chapter_dir / "draft_v1.md").exists()
    assert (chapter_dir / "validation_v1.json").exists()
    assert (chapter_dir / "draft_v2.md").exists()
    assert (chapter_dir / "validation_v2.json").exists()
    assert (chapter_dir / "final.md").exists()

    val_v1 = json.loads((chapter_dir / "validation_v1.json").read_text(encoding="utf-8"))
    val_v2 = json.loads((chapter_dir / "validation_v2.json").read_text(encoding="utf-8"))
    assert val_v1["passed"] is False
    assert val_v2["passed"] is True

    bible = json.loads((target / "bible.json").read_text(encoding="utf-8"))
    assert len(bible["events"]) == 1
    assert bible["events"][0]["chapter_index"] == 1
    assert bible["realized_tension"] == [4]
