from pathlib import Path

from auteur.blueprint import StoryBlueprint
from auteur.bible import StoryBible
from auteur.critic.theme import render as render_theme
from auteur.critic.base import run_critic
from auteur.llm import LLMResponse
from auteur.llm.fake import FakeClient


SAMPLE_YAML = Path(__file__).parent.parent / "examples" / "sample_blueprint.yaml"


def test_theme_critic_emits_only_warnings(tmp_path):
    blueprint = StoryBlueprint.from_yaml(SAMPLE_YAML)
    bible = StoryBible(tmp_path / "b.json")
    fake = """findings:
  - severity: warning
    rule: theme:no_motif_present
    evidence: "no broken-crowns / wounded-hands / rings-that-whisper imagery"
    requested_change: "weave at least one motif into a sensory beat"
"""
    client = FakeClient([LLMResponse(text=fake, input_tokens=1, output_tokens=10)])

    findings = run_critic(render_theme, llm=client, critic_name="theme", 
        draft="A long chapter about sailing.",
        outline={"scope": "chapter"},
        blueprint=blueprint,
        bible=bible,
        chapter_index=1,
    )

    assert findings and findings[0].severity == "warning"


def test_theme_critic_prompt_includes_central_question_and_motifs(tmp_path):
    blueprint = StoryBlueprint.from_yaml(SAMPLE_YAML)
    bible = StoryBible(tmp_path / "b.json")
    client = FakeClient([LLMResponse(text="findings: []", input_tokens=1, output_tokens=1)])

    run_critic(render_theme, llm=client, critic_name="theme", 
        draft="x",
        outline={"scope": "chapter"},
        blueprint=blueprint,
        bible=bible,
        chapter_index=1,
    )

    user = client.calls[0].user
    assert "redemption" in user.lower()
    assert "broken crowns" in user
