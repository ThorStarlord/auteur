# tests/test_critic_contract.py
from pathlib import Path

from auteur.blueprint import StoryBlueprint
from auteur.bible import StoryBible
from auteur.critic.contract import render as render_contract, SYSTEM_PROMPT
from auteur.critic.base import run_critic
from auteur.llm import LLMResponse
from auteur.llm.fake import FakeClient


SAMPLE_YAML = Path(__file__).parent.parent / "examples" / "sample_blueprint.yaml"


def _sample_outline() -> dict:
    return {
        "scope": "chapter",
        "chapter_index": 1,
        "scenes": [{"scene_id": "s1", "pov_character": "Kael", "summary": "Kael rides into town."}],
    }


def test_contract_critic_renders_prompt_with_required_sections(tmp_path):
    blueprint = StoryBlueprint.from_yaml(SAMPLE_YAML)
    bible = StoryBible(tmp_path / "b.json")
    bible.upsert_character("Kael", location="taverntown", physical="broken_arm")

    fake_response = """findings: []"""
    client = FakeClient([LLMResponse(text=fake_response, input_tokens=10, output_tokens=2)])

    findings = run_critic(render_contract, llm=client, critic_name="contract", 
        draft="A long prose chapter about Kael.",
        outline=_sample_outline(),
        blueprint=blueprint,
        bible=bible,
        chapter_index=1,
    )

    assert findings == []
    assert len(client.calls) == 1
    user = client.calls[0].user
    assert "CONTRACT RULES" in user
    assert "FORBIDDEN TROPES" in user
    assert "BIBLE CONTEXT" in user
    assert "DRAFT" in user
    # Bible state surfaced
    assert "broken_arm" in user


def test_contract_critic_parses_error_finding(tmp_path):
    blueprint = StoryBlueprint.from_yaml(SAMPLE_YAML)
    bible = StoryBible(tmp_path / "b.json")
    bible.upsert_character("Kael", location="taverntown", physical="broken_arm")

    fake_response = """findings:
  - severity: error
    rule: "forbidden_trope:chosen_one_prophecy"
    evidence: "scene 2: 'the prophecy named him chosen heir'"
    requested_change: "remove all prophecy framing"
"""
    client = FakeClient([LLMResponse(text=fake_response, input_tokens=10, output_tokens=20)])

    findings = run_critic(render_contract, llm=client, critic_name="contract", 
        draft="...",
        outline=_sample_outline(),
        blueprint=blueprint,
        bible=bible,
        chapter_index=1,
    )

    assert len(findings) == 1
    assert findings[0].critic == "contract"
    assert findings[0].severity == "error"
    assert "chosen_one_prophecy" in findings[0].rule


def test_contract_critic_uses_low_temperature(tmp_path):
    blueprint = StoryBlueprint.from_yaml(SAMPLE_YAML)
    bible = StoryBible(tmp_path / "b.json")
    client = FakeClient([LLMResponse(text="findings: []", input_tokens=1, output_tokens=1)])

    run_critic(render_contract, llm=client, critic_name="contract", 
        draft="x",
        outline=_sample_outline(),
        blueprint=blueprint,
        bible=bible,
        chapter_index=1,
    )

    assert client.calls[0].temperature == 0.0


def test_contract_critic_system_prompt_mentions_word_count_drift():
    assert "word_count" in SYSTEM_PROMPT or "pacing" in SYSTEM_PROMPT
