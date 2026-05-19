import pytest
from pathlib import Path
import yaml
from auteur.cli import main
from auteur.llm import LLMResponse
from auteur.llm.fake import FakeClient

def test_cli_identity_recommend_success(tmp_path, monkeypatch):
    identity_yaml_path = tmp_path / "story_identity.yaml"
    
    # Successful YAML output on the first try
    success_yaml = """
title: "The Silent Crown"
core_answer: "A tragic mystery about a detective who discovers the king is the killer."
target_experience:
  primary: "dread"
  progression: "curiosity -> suspicion -> dread"
  avoid:
    - "satisfaction"
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
  change: "The detective changes from an idealistic truth-seeker to a silent accomplice to preserve peace."
not_this:
  - "a standard whodunit"
open_questions:
  - "does the detective survive?"
confidence: 0.9
why_this_is_best: "Tragic ending fits the grim reality of the kingdom."
rejected_directions:
  - "heroic victory"
author_overrides: []
"""
    
    fake_response = LLMResponse(
        text=f"```yaml\n{success_yaml}\n```",
        input_tokens=100,
        output_tokens=100
    )
    
    fake_client = FakeClient([fake_response])
    
    # Monkeypatch build_client to return fake_client
    monkeypatch.setattr("auteur.llm.factory.build_client", lambda provider, model: fake_client)
    
    exit_code = main([
        "identity", "recommend",
        "A detective investigates a murder in a royal palace.",
        "--genre", "mystery",
        "--medium", "novel",
        "--mode", "tragic",
        "--output", str(identity_yaml_path)
    ])
    
    assert exit_code == 0
    assert identity_yaml_path.exists()
    
    with open(identity_yaml_path, "r", encoding="utf-8") as f:
        saved_data = yaml.safe_load(f)
    assert saved_data["title"] == "The Silent Crown"
    assert saved_data["story_type"]["genre"] == "mystery"
    assert saved_data["story_type"]["medium"] == "novel"
    assert saved_data["story_type"]["mode"] == "tragic"


def test_cli_identity_recommend_retry_loop(tmp_path, monkeypatch):
    identity_yaml_path = tmp_path / "story_identity_retry.yaml"
    
    # First response fails validation (duplicate want/change)
    fail_yaml = """
title: "The Silent Crown"
core_answer: "A tragic mystery."
target_experience:
  primary: "dread"
  progression: "rising"
  avoid: []
story_type:
  medium: "novel"
  mode: "tragic"
  genre: "mystery"
central_engine:
  want: "The detective wants to solve the murder."
  resistance: "The crown."
  conflict: "Conflict."
  stakes: "Stakes."
  change: "The detective wants to solve the murder." # Duplicate!
"""

    # Second response resolves the validation issue
    success_yaml = """
title: "The Silent Crown"
core_answer: "A tragic mystery."
target_experience:
  primary: "dread"
  progression: "rising"
  avoid: []
story_type:
  medium: "novel"
  mode: "tragic"
  genre: "mystery"
central_engine:
  want: "The detective wants to solve the murder."
  resistance: "The crown."
  conflict: "Conflict."
  stakes: "Stakes."
  change: "The detective changes completely."
"""

    resp_fail = LLMResponse(
        text=f"```yaml\n{fail_yaml}\n```",
        input_tokens=100,
        output_tokens=100
    )
    resp_success = LLMResponse(
        text=f"```yaml\n{success_yaml}\n```",
        input_tokens=200,
        output_tokens=200
    )
    
    fake_client = FakeClient([resp_fail, resp_success])
    monkeypatch.setattr("auteur.llm.factory.build_client", lambda provider, model: fake_client)
    
    exit_code = main([
        "identity", "recommend",
        "A detective investigates a murder.",
        "--output", str(identity_yaml_path)
    ])
    
    assert exit_code == 0
    assert identity_yaml_path.exists()
    
    with open(identity_yaml_path, "r", encoding="utf-8") as f:
        saved_data = yaml.safe_load(f)
    assert saved_data["central_engine"]["change"] == "The detective changes completely."


def test_cli_identity_recommend_max_retries_fail(tmp_path, monkeypatch):
    identity_yaml_path = tmp_path / "story_identity_fail.yaml"
    
    # All responses fail validation
    fail_yaml = """
title: "Failed Story"
core_answer: "A story."
target_experience:
  primary: "dread"
  progression: "rising"
  avoid: []
story_type:
  medium: "novel"
  mode: "tragic"
  genre: "mystery"
central_engine:
  want: "The detective wants to solve the murder."
  resistance: "The crown."
  conflict: "Conflict."
  stakes: "Stakes."
  change: "The detective wants to solve the murder."
"""
    
    responses = [
        LLMResponse(text=f"```yaml\n{fail_yaml}\n```", input_tokens=50, output_tokens=50)
        for _ in range(4)
    ]
    
    fake_client = FakeClient(responses)
    monkeypatch.setattr("auteur.llm.factory.build_client", lambda provider, model: fake_client)
    
    exit_code = main([
        "identity", "recommend",
        "A detective investigates a murder.",
        "--output", str(identity_yaml_path)
    ])
    
    assert exit_code == 1
    assert not identity_yaml_path.exists()
