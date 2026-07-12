from pathlib import Path

from auteur.blueprint import StoryBlueprint
from auteur.cli import main
from auteur.editing.handlers import handle_edit_review
from auteur.llm import LLMResponse
from auteur.llm.fake import FakeClient
from auteur.pipeline import PipelineRunner
from auteur.project import Project


SAMPLE_IDENTITY = Path(__file__).parent.parent / "examples" / "story_identity.yaml"
SAMPLE_BLUEPRINT = Path(__file__).parent.parent / "examples" / "sample_blueprint.yaml"


def _outline_yaml() -> str:
    return """
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
estimated_chapter_tension: 4
thematic_reinforcement: redemption costs more than Kael wants to pay
conflict_report: null
"""


def _draft_responses() -> list[LLMResponse]:
    prose = LLMResponse(
        text="Kael nursed a drink while the tavern kept its secrets.",
        input_tokens=20,
        output_tokens=10,
    )
    empty = [LLMResponse(text="findings: []", input_tokens=1, output_tokens=1) for _ in range(5)]
    return [prose, *empty]


def test_accepted_identity_flows_through_draft_editing_and_roundtrip(tmp_path):
    identity = tmp_path / "story_identity.yaml"
    identity.write_bytes(SAMPLE_IDENTITY.read_bytes())
    blueprint_path = tmp_path / "blueprint.yaml"

    assert main(["identity", "validate", str(identity)]) == 0
    assert main(["blueprint", "seed", str(identity), "--output", str(blueprint_path)]) == 0

    blueprint = StoryBlueprint.from_yaml(SAMPLE_BLUEPRINT)
    project = Project.init(tmp_path / "project", blueprint)
    outline_responses = [LLMResponse(text=_outline_yaml(), input_tokens=5, output_tokens=10)]

    # The fake client covers the drafting path after an already accepted identity.
    client = FakeClient([*outline_responses, *_draft_responses()])
    result = PipelineRunner(blueprint, bible=project.bible).draft_chapter(
        1, llm=client, project=project, max_iterations=1
    )
    assert result.accepted
    assert (project.path / "chapters/01/outline.yaml").exists()
    assert (project.path / "chapters/01/draft_v1.md").exists()
    assert (project.path / "chapters/01/final.md").exists()

    review = handle_edit_review(project.path, 1, "aiisms")
    assert review.is_success

    exported = project.path / "edited.md"
    exported.write_text(
        (project.path / "chapters/01/draft_v1.md").read_text(encoding="utf-8")
        + "\nEdited by the author.\n",
        encoding="utf-8",
    )
    assert main(["import", "chapter", str(project.path), "1", str(exported)]) == 0

    import_runs = list((project.path / "imports/chapter_01").iterdir())
    assert len(import_runs) == 1
    assert (import_runs[0] / "diff_report.json").exists()
    assert (import_runs[0] / "drift_report.json").exists()
