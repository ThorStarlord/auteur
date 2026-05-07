# tests/test_critic_tension.py
from pathlib import Path

from auteur.blueprint import StoryBlueprint
from auteur.bible import StoryBible
from auteur.critic.tension import run as run_tension
from auteur.llm import LLMResponse
from auteur.llm.fake import FakeClient


SAMPLE_YAML = Path(__file__).parent.parent / "examples" / "sample_blueprint.yaml"


def test_tension_critic_passes_when_within_tolerance(tmp_path):
    blueprint = StoryBlueprint.from_yaml(SAMPLE_YAML)
    bible = StoryBible(tmp_path / "b.json")
    outline = {"scope": "chapter", "estimated_chapter_tension": 4}
    client = FakeClient([LLMResponse(text="findings: []", input_tokens=1, output_tokens=1)])

    findings = run_tension(
        draft="A quiet conversation by the hearth.",
        outline=outline,
        blueprint=blueprint,
        bible=bible,
        chapter_index=1,
        llm=client,
    )

    assert findings == []


def test_tension_critic_flags_severe_drift(tmp_path):
    blueprint = StoryBlueprint.from_yaml(SAMPLE_YAML)
    bible = StoryBible(tmp_path / "b.json")
    outline = {"scope": "chapter", "estimated_chapter_tension": 9}
    fake = """findings:
  - severity: error
    rule: "tension:drift"
    evidence: "the draft is a contemplative bonding scene; no conflict appears"
    requested_change: "rewrite to deliver active conflict; bring in the antagonist"
"""
    client = FakeClient([LLMResponse(text=fake, input_tokens=1, output_tokens=10)])

    findings = run_tension(
        draft="They sat by the river and reflected on their friendship.",
        outline=outline,
        blueprint=blueprint,
        bible=bible,
        chapter_index=22,
        llm=client,
    )

    assert findings and findings[0].severity == "error"


def test_tension_critic_includes_target_in_prompt(tmp_path):
    blueprint = StoryBlueprint.from_yaml(SAMPLE_YAML)
    bible = StoryBible(tmp_path / "b.json")
    outline = {"scope": "chapter", "estimated_chapter_tension": 9}
    client = FakeClient([LLMResponse(text="findings: []", input_tokens=1, output_tokens=1)])

    run_tension(
        draft="x",
        outline=outline,
        blueprint=blueprint,
        bible=bible,
        chapter_index=22,  # midpoint_battle in sample
        llm=client,
    )

    user = client.calls[0].user
    assert "9" in user  # target from outline
    assert "midpoint_battle" in user  # waveform label
