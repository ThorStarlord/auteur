from pathlib import Path

import yaml

from auteur.cli import main
from auteur.genre_builder.builder import build_custom_genre_contract
from auteur.genre_builder.parser import parse_genre_brief
from auteur.llm import LLMResponse
from auteur.llm.fake import FakeClient


VALID_DISCOVERY_YAML = """
title: "The Silent Crown"
core_answer: "A tragic mystery about a detective who discovers the king is the killer."
target_experience:
  primary: "dread"
  progression: "curiosity -> suspicion -> dread"
  avoid: []
story_type:
  medium: "novel"
  mode: "tragic"
  genre: "mystery"
  subgenres: []
  target_audience: "adult"
  length_class: null
central_engine:
  want: "The detective wants to solve the murder."
  resistance: "The crown blocks the investigation."
  conflict: "Continuing the investigation exposes the detective to treason charges."
  stakes: "The detective's life and the truth."
  change: "The detective becomes a silent accomplice to preserve peace."
not_this: []
open_questions: []
confidence: 0.9
recommendation_mode: "open_ended"
best_basis: "genre_aligned"
why_this_is_best: "The mystery contract is clear and the political pressure gives it force."
rejected_directions: []
author_overrides: []
"""


CUSTOM_GENRE_BRIEF = """# Genre
Cozy Political Fantasy

# Emotional Promise
The reader should feel civic restoration through clever public repair.

# Core Truth
Communities can heal when power is made accountable.

# Required Tropes
- intimate political stakes

# Optional Tropes
- magical bureaucracy

# Forbidden Mismatches
- nihilistic ending

# Common Failures
- politics becomes exposition

# Scope
minimum_viable_length: novella
default_length: novel
narrative_runway: medium
recommended_complexity: focused
mechanical_load: medium
worldbuilding_load: medium
cast_load: medium

# Setup Requirements
- show the community wound
"""


def test_story_discovery_run_writes_discovery_artifacts(tmp_path, monkeypatch):
    output_dir = tmp_path / "story_discovery"
    summary_json = (
        '{"summary": "A crown mystery.", "tradeoffs": ["formal investigation"], '
        '"risks": ["politics may dominate"], "best_for": ["mystery readers"]}'
    )
    other_genre_yaml = VALID_DISCOVERY_YAML.replace('genre: "mystery"', 'genre: "other"')
    responses = [
        LLMResponse(text=f"```yaml\n{other_genre_yaml}\n```", input_tokens=100, output_tokens=100),
        LLMResponse(text=f"```yaml\n{VALID_DISCOVERY_YAML}\n```", input_tokens=100, output_tokens=100),
        LLMResponse(text=f"```yaml\n{VALID_DISCOVERY_YAML}\n```", input_tokens=100, output_tokens=100),
        LLMResponse(text=summary_json, input_tokens=50, output_tokens=50),
        LLMResponse(text=summary_json, input_tokens=50, output_tokens=50),
        LLMResponse(text=summary_json, input_tokens=50, output_tokens=50),
    ]
    fake_client = FakeClient(responses)
    monkeypatch.setattr("auteur.llm.factory.build_client", lambda provider, model, **kwargs: fake_client)

    exit_code = main([
        "story-discovery",
        "run",
        "A detective investigates a royal murder.",
        "--output",
        str(output_dir),
    ])

    assert exit_code == 0
    assert (output_dir / "candidate_1.yaml").exists()
    assert (output_dir / "candidate_2.yaml").exists()
    assert (output_dir / "candidate_3.yaml").exists()
    assert (output_dir / "comparison.md").exists()
    assert (output_dir / "discovery_report.yaml").exists()
    report = yaml.safe_load((output_dir / "discovery_report.yaml").read_text(encoding="utf-8"))
    assert report["candidate_count"] == 3
    assert report["design_lenses"] == ["emotional_payoff", "commercial_clarity", "thematic_coherence"]
    assert report["comparison"][0]["contract_fit_status"] in {"strong", "mixed", "weak"}
    assert "Story Discovery Comparison" in (output_dir / "comparison.md").read_text(encoding="utf-8")


def test_story_discovery_accept_promotes_candidate(tmp_path):
    discovery_dir = tmp_path / "story_discovery"
    discovery_dir.mkdir()
    candidate = discovery_dir / "candidate_1.yaml"
    candidate.write_text(VALID_DISCOVERY_YAML, encoding="utf-8")
    output = tmp_path / "story_identity.yaml"

    exit_code = main([
        "story-discovery",
        "accept",
        str(candidate),
        "--output",
        str(output),
        "--keep-candidates",
    ])

    assert exit_code == 0
    assert output.exists()
    promoted = yaml.safe_load(output.read_text(encoding="utf-8"))
    assert promoted["title"] == "The Silent Crown"
    assert discovery_dir.exists()


def test_story_discovery_project_uses_project_local_custom_genre_prompt_guidance(tmp_path, monkeypatch):
    project = tmp_path / "project"
    custom_dir = project / "genres" / "custom"
    custom_dir.mkdir(parents=True)
    custom = build_custom_genre_contract(parse_genre_brief(CUSTOM_GENRE_BRIEF))
    custom = custom.model_copy(update={"custom_genre_id": "other"})
    (custom_dir / "other.yaml").write_text(
        yaml.safe_dump(custom.model_dump(mode="json"), sort_keys=False),
        encoding="utf-8",
    )
    output_dir = tmp_path / "story_discovery"
    summary_json = '{"summary": "A crown mystery.", "tradeoffs": [], "risks": [], "best_for": []}'
    responses = [
        LLMResponse(text=f"```yaml\n{VALID_DISCOVERY_YAML}\n```", input_tokens=100, output_tokens=100),
        LLMResponse(text=summary_json, input_tokens=50, output_tokens=50),
    ]
    fake_client = FakeClient(responses)
    monkeypatch.setattr("auteur.llm.factory.build_client", lambda provider, model, **kwargs: fake_client)

    exit_code = main([
        "story-discovery",
        "run",
        "A council intrigue in a warm city.",
        "--output",
        str(output_dir),
        "--candidates",
        "1",
        "--genre",
        "other",
        "--project",
        str(project),
    ])

    assert exit_code == 0
    assert "Cozy Political Fantasy" in fake_client.calls[0].system
    assert "civic restoration" in fake_client.calls[0].system
