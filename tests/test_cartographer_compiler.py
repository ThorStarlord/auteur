"""Tests for the Cartographer compiler subcommand — Phase 2 TDD tests.

Verifies end-to-end outline compilation from blueprint, including multi-chapter LLM mocking,
unified YAML construction, and auto-splitting into chapters.
"""
from __future__ import annotations

from pathlib import Path
import yaml
import pytest

from auteur.project import Project
from auteur.blueprint import StoryBlueprint
from auteur.cartographer_compiler import compile_outline
from auteur.llm.fake import FakeClient
from auteur.llm import LLMResponse

SAMPLE_YAML = Path(__file__).parent.parent / "examples" / "sample_blueprint.yaml"


def _mock_cartographer_outline(chapter_index: int) -> str:
    blueprint = StoryBlueprint.from_yaml(SAMPLE_YAML)
    target = blueprint.tension_waveform.target_for(chapter_index)
    tension = target.score if target else 4
    return f"""
scope: chapter
chapter_index: {chapter_index}
chapter_summary: Kael returns to the tavern.
scenes:
  - scene_id: s1
    pov_character: Kael
    location: Tavern
    summary: He nurses a drink.
    key_events: []
    character_state_changes:
      - character: Kael
        field: location
        before: null
        after: Tavern
    arc_advancements: []
    estimated_tension: {tension}
    emotional_tone: subtle unease
arc_pushes: []
contract_compliance: []
expected_elements_touched: []
forbidden_tropes_avoided: []
estimated_chapter_tension: {tension}
thematic_reinforcement: theme
conflict_report: null
"""


def test_compile_outline_generates_unified_outline_and_splits_chapters(tmp_path):
    """compile_outline should compile all blueprint chapters, output a unified file,
    and programmatically split them into chapters/{idx:02d}/outline.yaml."""
    blueprint = StoryBlueprint.from_yaml(SAMPLE_YAML)
    project = Project.init(tmp_path / "test_novel", blueprint)
    
    # 2 chapters in the sample blueprint (let's verify or pad)
    num_chapters = blueprint.structure.estimated_chapters or 2
    
    # Set up FakeClient responses (one outline per chapter)
    responses = [
        LLMResponse(text=_mock_cartographer_outline(i), input_tokens=10, output_tokens=20)
        for i in range(1, num_chapters + 1)
    ]
    client = FakeClient(responses)
    
    output_path = project.path / "cartographer_outline.yaml"
    
    # Run compiler
    compile_outline(
        project_path=project.path,
        blueprint_path=SAMPLE_YAML,
        output_path=output_path,
        split_output=True,
        llm=client
    )
    
    # Verify unified outline file exists on disk
    assert output_path.exists()
    unified_data = yaml.safe_load(output_path.read_text(encoding="utf-8"))
    assert unified_data["total_chapters"] == num_chapters
    assert len(unified_data["chapters"]) == num_chapters
    
    # Verify split chapter outline exists on disk
    ch1_outline = project.path / "chapters" / "01" / "outline.yaml"
    assert ch1_outline.exists()
    ch1_data = yaml.safe_load(ch1_outline.read_text(encoding="utf-8"))
    assert ch1_data["chapter_index"] == 1
    assert len(ch1_data["scenes"]) == 1


def test_cartographer_cli_compile_and_validate(tmp_path):
    """Calling the CLI commands 'cartographer compile' and 'cartographer validate'
    directly via main() should work and route properly."""
    from auteur.cli import main
    blueprint = StoryBlueprint.from_yaml(SAMPLE_YAML)
    project = Project.init(tmp_path / "test_cli_novel", blueprint)
    
    from unittest.mock import patch
    num_chapters = blueprint.structure.estimated_chapters or 2
    responses = [
        LLMResponse(text=_mock_cartographer_outline(i), input_tokens=10, output_tokens=20)
        for i in range(1, num_chapters + 1)
    ]
    client = FakeClient(responses)
    
    output_path = project.path / "cartographer_outline.yaml"
    
    with patch("auteur.llm.factory.build_client", return_value=client):
        # Run compiler command via main
        argv = [
            "cartographer",
            "compile",
            str(SAMPLE_YAML),
            "--output",
            str(output_path),
            "--provider",
            "anthropic"
        ]
        rc = main(argv)
        assert rc == 0
        
    assert output_path.exists()
    
    # Run validator command via main
    argv_val = [
        "cartographer",
        "validate",
        str(output_path),
        "--blueprint",
        str(SAMPLE_YAML)
    ]
    rc_val = main(argv_val)
    assert rc_val == 0
