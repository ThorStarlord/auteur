# tests/test_critic_arc.py
from pathlib import Path

from auteur.blueprint import StoryBlueprint
from auteur.bible import StoryBible
from auteur.critic.arc import render as render_arc
from auteur.critic.base import run_critic
from auteur.llm import LLMResponse
from auteur.llm.fake import FakeClient


SAMPLE_YAML = Path(__file__).parent.parent / "examples" / "sample_blueprint.yaml"


def _outline_with_arc_advancement():
    return {
        "scope": "chapter",
        "chapter_index": 7,
        "scenes": [{"scene_id": "s1", "pov_character": "Kael", "summary": "Kael deceives a merchant."}],
        "arc_pushes": [{"character": "Kael", "milestone_touched": "First minor deception without guilt.", "delta_pct": 5}],
    }


def test_arc_critic_passes_when_milestone_supported(tmp_path):
    blueprint = StoryBlueprint.from_yaml(SAMPLE_YAML)
    bible = StoryBible(tmp_path / "b.json")
    client = FakeClient([LLMResponse(text="findings: []", input_tokens=5, output_tokens=2)])

    findings = run_critic(render_arc, llm=client, critic_name="arc", 
        draft="Kael lied to the merchant without flinching, untroubled.",
        outline=_outline_with_arc_advancement(),
        blueprint=blueprint,
        bible=bible,
        chapter_index=7,
    )

    assert findings == []


def test_arc_critic_flags_unsupported_milestone(tmp_path):
    blueprint = StoryBlueprint.from_yaml(SAMPLE_YAML)
    bible = StoryBible(tmp_path / "b.json")
    fake = """findings:
  - severity: error
    rule: "arc:milestone_unsupported"
    evidence: "no scene in the draft shows Kael deceiving anyone"
    requested_change: "add a scene where Kael lies without remorse"
"""
    client = FakeClient([LLMResponse(text=fake, input_tokens=5, output_tokens=20)])

    findings = run_critic(render_arc, llm=client, critic_name="arc", 
        draft="Kael spent the day repairing his cart.",
        outline=_outline_with_arc_advancement(),
        blueprint=blueprint,
        bible=bible,
        chapter_index=7,
    )

    assert len(findings) == 1
    assert findings[0].critic == "arc"
    assert findings[0].severity == "error"


def test_arc_critic_user_message_includes_arc_directives(tmp_path):
    blueprint = StoryBlueprint.from_yaml(SAMPLE_YAML)
    bible = StoryBible(tmp_path / "b.json")
    client = FakeClient([LLMResponse(text="findings: []", input_tokens=1, output_tokens=1)])

    run_critic(render_arc, llm=client, critic_name="arc", 
        draft="x",
        outline=_outline_with_arc_advancement(),
        blueprint=blueprint,
        bible=bible,
        chapter_index=7,
    )

    user = client.calls[0].user
    assert "Kael" in user
    assert "corruption" in user
    assert "First minor deception" in user
