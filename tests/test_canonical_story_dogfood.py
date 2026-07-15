import importlib.util
from pathlib import Path


def _runner():
    path = Path("scripts/dogfood-canonical-story.py")
    spec = importlib.util.spec_from_file_location("canonical_dogfood", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_canonical_story_dogfood_uses_temporary_workspace():
    result = _runner().run()
    assert result["project"] == "The Lantern at Low Water"
    assert result["copied_to_temporary_workspace"] is True
    assert result["required_artifacts_present"] is True
    assert result["critic_statuses"] == ["success"]
    assert result["accepted_scene_realizations"] == 5
    assert result["accepted_identity"] is True
    assert result["accepted_blueprint"] is True
    assert result["accepted_chapter_structure"] is True
    assert result["accepted_scene_expressions"] == 5
    assert result["accepted_chapter_expression"]
    assert result["accepted_transitions"] == 1
    assert "Top concerns:" in result["review_text"]
    assert result["derived_artifacts_written_to"] == "temporary workspace only"
    assert "publication" in result["untraversed_stages"]
