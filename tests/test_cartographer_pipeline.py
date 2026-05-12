"""Integration test: malformed Cartographer outlines are caught at the pipeline boundary."""

from pathlib import Path

import pytest

from auteur.llm import LLMResponse

SAMPLE_YAML = Path(__file__).parent.parent / "examples" / "sample_blueprint.yaml"


def _outline_without_scenes() -> str:
    """Valid YAML but missing the required 'scenes' key."""
    return """
scope: chapter
chapter_index: 1
chapter_summary: Kael returns to the tavern.
arc_pushes: []
contract_compliance: []
expected_elements_touched: []
forbidden_tropes_avoided: [chosen_one_prophecy]
estimated_chapter_tension: 4
thematic_reinforcement: Redemption costs.
conflict_report: null
"""


def test_malformed_outline_without_scenes_is_rejected(tmp_path):
    """When the Cartographer returns an outline without 'scenes', the
    pipeline should reject it with ValueError at the Cartographer boundary,
    without ever calling Bard."""
    target = tmp_path / "shattered_crown"

    from auteur.cli import main
    rc = main(["init", str(target), "--from", str(SAMPLE_YAML)])
    assert rc == 0

    scripted = [
        LLMResponse(text=_outline_without_scenes(), input_tokens=80, output_tokens=120),
    ]

    from unittest.mock import patch
    from auteur.llm.fake import FakeClient
    with patch("auteur.llm.factory.build_client", return_value=FakeClient(scripted)):
        with pytest.raises(ValueError, match="Cartographer outline validation error"):
            main(["draft", str(target), "1", "--max-iterations", "1"])

    # Verify no outline was written to disk
    assert not (target / "chapters" / "01" / "outline.yaml").exists(), (
        "The malformed outline should not be written to disk"
    )
