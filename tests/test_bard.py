from pathlib import Path

from auteur.blueprint import StoryBlueprint
from auteur.bible import StoryBible
from auteur.bard import render_bard_prompt, postprocess_draft, draft_chapter
from auteur.critic import CriticFinding
from auteur.llm import LLMResponse
from auteur.llm.fake import FakeClient


SAMPLE_YAML = Path(__file__).parent.parent / "examples" / "sample_blueprint.yaml"

OUTLINE = {
    "scope": "chapter",
    "chapter_index": 1,
    "chapter_summary": "Kael returns to the tavern with broken arm.",
    "scenes": [{"scene_id": "s1", "pov_character": "Kael", "summary": "He drinks alone."}],
    "estimated_chapter_tension": 4,
}


def test_render_bard_prompt_draft_mode(tmp_path):
    blueprint = StoryBlueprint.from_yaml(SAMPLE_YAML)
    bible = StoryBible(tmp_path / "b.json")
    bible.upsert_character("Kael", location="taverntown", physical="broken_arm")

    system, user = render_bard_prompt(
        outline=OUTLINE,
        bible=bible,
        blueprint=blueprint,
        chapter_index=1,
        prior_draft=None,
        findings=None,
    )

    assert "POV" in system
    assert "OUTLINE" in user
    assert "Kael" in user
    assert "broken_arm" in user
    assert "REWRITE TASK" not in user


def test_render_bard_prompt_rewrite_mode_includes_findings(tmp_path):
    blueprint = StoryBlueprint.from_yaml(SAMPLE_YAML)
    bible = StoryBible(tmp_path / "b.json")
    finding = CriticFinding(
        critic="contract",
        severity="error",
        rule="forbidden_trope:chosen_one_prophecy",
        evidence="scene 2: prophecy reveal",
        requested_change="remove all prophecy framing",
    )

    system, user = render_bard_prompt(
        outline=OUTLINE,
        bible=bible,
        blueprint=blueprint,
        chapter_index=1,
        prior_draft="The previous draft text.",
        findings=[finding],
    )

    assert "REWRITE TASK" in user
    assert "previous draft text" in user.lower()
    assert "chosen_one_prophecy" in user
    assert "remove all prophecy framing" in user


def test_postprocess_draft_strips_code_fences():
    raw = "```markdown\nThe chapter prose.\n```"
    assert postprocess_draft(raw) == "The chapter prose."


def test_postprocess_draft_trims_whitespace():
    assert postprocess_draft("\n\n  The prose.  \n\n") == "The prose."


def test_postprocess_draft_passes_through_clean_markdown():
    raw = "# Chapter 1\n\nThe prose."
    assert postprocess_draft(raw) == "# Chapter 1\n\nThe prose."


def test_draft_chapter_calls_llm_with_rendered_prompt(tmp_path):
    blueprint = StoryBlueprint.from_yaml(SAMPLE_YAML)
    bible = StoryBible(tmp_path / "b.json")
    bible.upsert_character("Kael", location="taverntown", physical="broken_arm")
    client = FakeClient([LLMResponse(text="The chapter prose.", input_tokens=10, output_tokens=4)])

    prose = draft_chapter(
        outline=OUTLINE,
        bible=bible,
        blueprint=blueprint,
        chapter_index=1,
        llm=client,
    )

    assert prose == "The chapter prose."
    assert len(client.calls) == 1
    assert "Kael" in client.calls[0].user
