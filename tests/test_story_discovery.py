from pathlib import Path

import yaml

from auteur.cli import main
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


def test_story_discovery_run_writes_discovery_artifacts(tmp_path, monkeypatch):
    output_dir = tmp_path / "story_discovery"
    summary_json = (
        '{"summary": "A crown mystery.", "tradeoffs": ["formal investigation"], '
        '"risks": ["politics may dominate"], "best_for": ["mystery readers"]}'
    )
    responses = [
        LLMResponse(text=f"```yaml\n{VALID_DISCOVERY_YAML}\n```", input_tokens=100, output_tokens=100),
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

