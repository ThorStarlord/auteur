from pathlib import Path

import pytest

from auteur.project import Project
from auteur.blueprint import StoryBlueprint
from auteur.pipeline import PipelineRunner
from auteur.llm import LLMResponse
from auteur.llm.fake import FakeClient


SAMPLE_YAML = Path(__file__).parent.parent / "examples" / "sample_blueprint.yaml"


def _cartographer_outline_yaml(tension: int = 4) -> str:
    return f"""
scope: chapter
chapter_index: 1
chapter_summary: Kael returns to the tavern.
scenes:
  - scene_id: s1
    pov_character: Kael
    location: taverntown
    summary: He nurses a drink.
    key_events: [drinks, broods]
    character_state_changes: []
    arc_advancements: []
    estimated_tension: 4
    emotional_tone: subtle unease
arc_pushes: []
contract_compliance: []
expected_elements_touched: []
forbidden_tropes_avoided: [chosen_one_prophecy, resurrected_hero, deus_ex_machina_rescue]
estimated_chapter_tension: {tension}
thematic_reinforcement: redemption costs more than Kael wants to pay
conflict_report: null
"""


def _scripted_draft_iteration(*, fail: bool):
    bard = LLMResponse(text="The prose of Kael at the tavern.", input_tokens=20, output_tokens=10)
    if fail:
        contract = LLMResponse(text="""findings:
  - severity: error
    rule: forbidden_trope:chosen_one_prophecy
    evidence: "scene 1: a prophecy named him"
    requested_change: "remove the prophecy framing"
""", input_tokens=5, output_tokens=10)
    else:
        contract = LLMResponse(text="findings: []", input_tokens=5, output_tokens=2)
    others = [LLMResponse(text="findings: []", input_tokens=1, output_tokens=1) for _ in range(4)]
    return [bard, contract, *others]


def test_draft_chapter_happy_path(tmp_path):
    blueprint = StoryBlueprint.from_yaml(SAMPLE_YAML)
    project = Project.init(tmp_path / "novel", blueprint)

    cartographer = LLMResponse(text=_cartographer_outline_yaml(), input_tokens=50, output_tokens=80)
    iteration = _scripted_draft_iteration(fail=False)
    client = FakeClient([cartographer, *iteration])

    runner = PipelineRunner(blueprint, bible=project.bible)
    result = runner.draft_chapter(1, llm=client, project=project, max_iterations=3)

    assert result.accepted is True
    assert result.iterations == 1
    assert result.final_path is not None and result.final_path.exists()
    assert (project.chapter_dir(1) / "outline.yaml").exists()
    assert (project.chapter_dir(1) / "draft_v1.md").exists()
    assert (project.chapter_dir(1) / "validation_v1.json").exists()
    assert project.bible.data["events"][-1]["chapter_index"] == 1
    assert project.bible.data["realized_tension"] == [4]


def test_draft_chapter_fail_then_pass_path(tmp_path):
    blueprint = StoryBlueprint.from_yaml(SAMPLE_YAML)
    project = Project.init(tmp_path / "novel", blueprint)

    cartographer = LLMResponse(text=_cartographer_outline_yaml(), input_tokens=50, output_tokens=80)
    fail_iter = _scripted_draft_iteration(fail=True)
    pass_iter = _scripted_draft_iteration(fail=False)
    client = FakeClient([cartographer, *fail_iter, *pass_iter])

    runner = PipelineRunner(blueprint, bible=project.bible)
    result = runner.draft_chapter(1, llm=client, project=project, max_iterations=3)

    assert result.accepted is True
    assert result.iterations == 2
    assert (project.chapter_dir(1) / "draft_v1.md").exists()
    assert (project.chapter_dir(1) / "draft_v2.md").exists()
    assert (project.chapter_dir(1) / "final.md").exists()


def test_draft_chapter_exhaustion_path(tmp_path):
    blueprint = StoryBlueprint.from_yaml(SAMPLE_YAML)
    project = Project.init(tmp_path / "novel", blueprint)

    cartographer = LLMResponse(text=_cartographer_outline_yaml(), input_tokens=50, output_tokens=80)
    fail_iter_1 = _scripted_draft_iteration(fail=True)
    fail_iter_2 = _scripted_draft_iteration(fail=True)
    fail_iter_3 = _scripted_draft_iteration(fail=True)
    client = FakeClient([cartographer, *fail_iter_1, *fail_iter_2, *fail_iter_3])

    runner = PipelineRunner(blueprint, bible=project.bible)
    result = runner.draft_chapter(1, llm=client, project=project, max_iterations=3)

    assert result.accepted is False
    assert result.iterations == 3
    assert not (project.chapter_dir(1) / "final.md").exists()
    assert project.bible.data["events"] == []
    assert project.bible.data["realized_tension"] == []


def test_draft_chapter_conflict_report_short_circuits(tmp_path):
    blueprint = StoryBlueprint.from_yaml(SAMPLE_YAML)
    project = Project.init(tmp_path / "novel", blueprint)

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
conflict_report: "tension target 3 conflicts with required arc milestone (betrayal)"
"""
    client = FakeClient([LLMResponse(text=conflict_yaml, input_tokens=5, output_tokens=10)])

    runner = PipelineRunner(blueprint, bible=project.bible)
    result = runner.draft_chapter(1, llm=client, project=project, max_iterations=3)

    assert result.accepted is False
    assert result.iterations == 0
    assert result.conflict_report == "tension target 3 conflicts with required arc milestone (betrayal)"
    assert (project.chapter_dir(1) / "outline.yaml").exists()
    assert not (project.chapter_dir(1) / "draft_v1.md").exists()
