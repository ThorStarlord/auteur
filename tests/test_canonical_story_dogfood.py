import importlib.util
import hashlib
from pathlib import Path


def _runner():
    path = Path("scripts/dogfood-canonical-story.py")
    spec = importlib.util.spec_from_file_location("canonical_dogfood", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_canonical_story_dogfood_uses_temporary_workspace():
    reference = Path("examples/canonical_story/external_edit.md")
    before = hashlib.sha256(reference.read_bytes()).hexdigest()
    result = _runner().run()
    after = hashlib.sha256(reference.read_bytes()).hexdigest()
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
    assert result["accepted_second_chapter"] == "chapter_02:expression_v001"
    assert result["book_initial"]["freshness_after_chapter_revision"] == "stale"
    assert result["book_recomposed"] == result["accepted_book"]
    assert result["book_export_clean"] is True
    assert "Top concerns:" in result["review_text"]
    assert result["derived_artifacts_written_to"] == "temporary workspace only"
    assert result["untraversed_stages"] == []
    reconciliation = result["reconciliation"]
    assert reconciliation["publication_status"] == "published"
    assert set(reconciliation["decisions"].values()) == {"accepted", "rejected", "deferred"}
    assert list(reconciliation["decisions"].values()).count("accepted") == 1
    assert list(reconciliation["decisions"].values()).count("rejected") == 1
    assert list(reconciliation["decisions"].values()).count("deferred") == 4
    assert reconciliation["recomposed_chapter_expression"] == reconciliation["accepted_chapter_expression"]
    assert reconciliation["completion_status"] == "partially_reconciled"
    assert before == after
