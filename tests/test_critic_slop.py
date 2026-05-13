from pathlib import Path

from auteur.blueprint import StoryBlueprint
from auteur.bible import StoryBible
from auteur.critic.slop import render as render_slop, SLOP_PHRASES
from auteur.critic.base import run_critic
from auteur.llm import LLMResponse
from auteur.llm.fake import FakeClient


SAMPLE_YAML = Path(__file__).parent.parent / "examples" / "sample_blueprint.yaml"


def test_slop_critic_passes_clean_prose(tmp_path):
    blueprint = StoryBlueprint.from_yaml(SAMPLE_YAML)
    bible = StoryBible(tmp_path / "b.json")
    client = FakeClient([LLMResponse(text="findings: []", input_tokens=1, output_tokens=1)])

    findings = run_critic(render_slop, llm=client, critic_name="slop", 
        draft="Kael drew his blade. The cold wind cut through his cloak.",
        outline={"scope": "chapter"},
        blueprint=blueprint,
        bible=bible,
        chapter_index=1,
    )

    assert findings == []


def test_slop_critic_flags_clichés(tmp_path):
    blueprint = StoryBlueprint.from_yaml(SAMPLE_YAML)
    bible = StoryBible(tmp_path / "b.json")
    fake = """findings:
  - severity: warning
    rule: slop:cliche
    evidence: "'a testament to her courage'"
    requested_change: "show the courage in a concrete action"
"""
    client = FakeClient([LLMResponse(text=fake, input_tokens=1, output_tokens=10)])

    findings = run_critic(render_slop, llm=client, critic_name="slop", 
        draft="Her stance was a testament to her courage.",
        outline={"scope": "chapter"},
        blueprint=blueprint,
        bible=bible,
        chapter_index=1,
    )

    assert findings and findings[0].critic == "slop"


def test_slop_phrases_list_is_nonempty():
    assert isinstance(SLOP_PHRASES, list) and len(SLOP_PHRASES) >= 5
    assert all(isinstance(p, str) for p in SLOP_PHRASES)


def test_slop_critic_includes_phrase_list_in_prompt(tmp_path):
    blueprint = StoryBlueprint.from_yaml(SAMPLE_YAML)
    bible = StoryBible(tmp_path / "b.json")
    client = FakeClient([LLMResponse(text="findings: []", input_tokens=1, output_tokens=1)])

    run_critic(render_slop, llm=client, critic_name="slop", 
        draft="x",
        outline={"scope": "chapter"},
        blueprint=blueprint,
        bible=bible,
        chapter_index=1,
    )

    user = client.calls[0].user
    for phrase in SLOP_PHRASES[:3]:
        assert phrase in user
