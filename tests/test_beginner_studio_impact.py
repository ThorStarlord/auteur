"""Hypothetical Studio impact is read-only and uses actual dependency graph semantics."""
from __future__ import annotations

import pytest

from auteur.beginner.studio_impact import preview_studio_impact
from auteur.impact.graph import DependencyGraph
from auteur.impact.models import ArtifactRef


def test_registered_chain_only_and_no_mutation(tmp_path):
    graph = DependencyGraph()
    for name, accepted in (("story_identity", True), ("chapter_one", True), ("chapter_two", False), ("unrelated", True)):
        graph.add_node(ArtifactRef(artifact_id=name, artifact_type="chapter", accepted=accepted))
    graph.add_edge("story_identity", "chapter_one", kind="depends_on", source="provenance")
    graph.add_edge("chapter_one", "chapter_two", kind="depends_on", source="provenance")
    before = graph.to_dict()
    preview = preview_studio_impact(tmp_path, "story_identity", graph=graph)
    assert preview["mode"] == "HYPOTHETICAL / READ ONLY"
    assert [a["artifact_id"] for a in preview["affected"]] == ["chapter_one", "chapter_two"]
    assert preview["affected"][0]["direct"] is True
    assert preview["affected"][1]["direct"] is False
    assert preview["affected"][0]["accepted"] is True
    assert graph.to_dict() == before
    assert not list(tmp_path.iterdir())


def test_unknown_source_does_not_fabricate_impact(tmp_path):
    with pytest.raises(ValueError, match="not in registered"):
        preview_studio_impact(tmp_path, "missing", graph=DependencyGraph())
