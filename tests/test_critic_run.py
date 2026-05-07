from pathlib import Path

from auteur.blueprint import StoryBlueprint
from auteur.bible import StoryBible
from auteur.critic import run_critics
from auteur.llm import LLMResponse
from auteur.llm.fake import FakeClient


SAMPLE_YAML = Path(__file__).parent.parent / "examples" / "sample_blueprint.yaml"


def _scripted_all_pass():
    return [LLMResponse(text="findings: []", input_tokens=1, output_tokens=1) for _ in range(5)]


def test_run_critics_aggregates_all_passes(tmp_path):
    blueprint = StoryBlueprint.from_yaml(SAMPLE_YAML)
    bible = StoryBible(tmp_path / "b.json")
    client = FakeClient(_scripted_all_pass())

    report = run_critics(
        draft="ok prose",
        outline={"scope": "chapter", "scenes": [{"pov_character": "Kael"}], "estimated_chapter_tension": 4},
        blueprint=blueprint,
        bible=bible,
        chapter_index=1,
        iteration=1,
        llm=client,
    )

    assert report.passed is True
    assert report.findings == []
    assert report.chapter_index == 1
    assert report.iteration == 1
    assert len(client.calls) == 5


def test_run_critics_passed_false_on_any_error(tmp_path):
    blueprint = StoryBlueprint.from_yaml(SAMPLE_YAML)
    bible = StoryBible(tmp_path / "b.json")

    contract_error = """findings:
  - severity: error
    rule: forbidden_trope:chosen_one_prophecy
    evidence: "scene 2"
    requested_change: "remove"
"""
    others_pass = "findings: []"
    client = FakeClient([
        LLMResponse(text=contract_error, input_tokens=1, output_tokens=5),
        LLMResponse(text=others_pass, input_tokens=1, output_tokens=1),
        LLMResponse(text=others_pass, input_tokens=1, output_tokens=1),
        LLMResponse(text=others_pass, input_tokens=1, output_tokens=1),
        LLMResponse(text=others_pass, input_tokens=1, output_tokens=1),
    ])

    report = run_critics(
        draft="prose",
        outline={"scope": "chapter", "scenes": [{"pov_character": "Kael"}], "estimated_chapter_tension": 4},
        blueprint=blueprint,
        bible=bible,
        chapter_index=1,
        iteration=2,
        llm=client,
    )

    assert report.passed is False
    assert len(report.findings) == 1
    assert report.findings[0].critic == "contract"


def test_run_critics_passed_true_when_only_warnings(tmp_path):
    blueprint = StoryBlueprint.from_yaml(SAMPLE_YAML)
    bible = StoryBible(tmp_path / "b.json")

    warn = """findings:
  - severity: warning
    rule: slop:cliche
    evidence: "x"
    requested_change: "y"
"""
    client = FakeClient([
        LLMResponse(text="findings: []", input_tokens=1, output_tokens=1),
        LLMResponse(text="findings: []", input_tokens=1, output_tokens=1),
        LLMResponse(text="findings: []", input_tokens=1, output_tokens=1),
        LLMResponse(text=warn, input_tokens=1, output_tokens=5),
        LLMResponse(text="findings: []", input_tokens=1, output_tokens=1),
    ])

    report = run_critics(
        draft="prose",
        outline={"scope": "chapter", "scenes": [{"pov_character": "Kael"}], "estimated_chapter_tension": 4},
        blueprint=blueprint,
        bible=bible,
        chapter_index=1,
        iteration=1,
        llm=client,
    )

    assert report.passed is True
    assert len(report.findings) == 1
    assert report.findings[0].severity == "warning"
