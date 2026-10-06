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



def test_render_bard_prompt_preserves_author_context_authority_labels(tmp_path):
    blueprint = StoryBlueprint.from_yaml(SAMPLE_YAML)
    bible = StoryBible(tmp_path / "b.json")
    context = {
        "schema": "beginner_author_context_v1",
        "current_plan": {
            "chapter_index": 6,
            "role": "Expose forecasting misuse",
            "authority": "planning_context",
        },
        "accepted_expression": [{
            "chapter_index": 2,
            "text": "Sister Beatrice connects the convent to the forecasting office.",
            "source_ref": "chapters/02/final.md",
            "authority": "accepted_expression",
            "relevance_reasons": ["current_plan_overlap:convent"],
        }],
        "accepted_state": {
            "record_provenance": {
                "value": "unresolved",
                "chapter_index": 5,
                "source_ref": "bible.json#/events/6",
                "authority": "accepted",
            },
        },
        "pending_updates": [{
            "summary": "Forecasting origin: keep unresolved",
            "source_ref": ".auteur/beginner/reconciliation/5.json#/proposal_items/0",
            "chapter_index": 5,
            "authority": "suggested",
            "blocking": False,
        }],
        "uncertainty": [],
    }

    _, user = render_bard_prompt(
        outline=OUTLINE,
        bible=bible,
        blueprint=blueprint,
        chapter_index=6,
        prior_draft=None,
        findings=None,
        author_context=context,
    )

    assert "AUTHOR CONTEXT — PROVENANCE PRESERVED" in user
    assert "accepted_expression" in user
    assert "Sister Beatrice" in user
    assert '"authority": "suggested"' in user
    assert '"record_provenance"' in user
    assert "Do not promote Suggested or Needs-attention" in user


def test_draft_chapter_forwards_author_context_to_llm(tmp_path):
    blueprint = StoryBlueprint.from_yaml(SAMPLE_YAML)
    bible = StoryBible(tmp_path / "b.json")
    client = FakeClient([LLMResponse(text="The chapter prose.", input_tokens=10, output_tokens=4)])
    context = {
        "schema": "beginner_author_context_v1",
        "accepted_expression": [{
            "chapter_index": 5,
            "text": "The pump disaster was already prevented.",
            "source_ref": "chapters/05/final.md",
            "authority": "accepted_expression",
        }],
        "pending_updates": [],
    }

    prose = draft_chapter(
        outline=OUTLINE,
        bible=bible,
        blueprint=blueprint,
        chapter_index=6,
        llm=client,
        author_context=context,
    )

    assert prose == "The chapter prose."
    assert "AUTHOR CONTEXT — PROVENANCE PRESERVED" in client.calls[0].user
    assert "pump disaster was already prevented" in client.calls[0].user
