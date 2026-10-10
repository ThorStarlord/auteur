"""Source-bound relationship projection remains read-only and honest."""
from __future__ import annotations

from auteur.beginner.studio_projection import project_studio_graph


def test_declared_relationships_source_and_authority(tmp_path):
    source = tmp_path / "relations.yaml"
    source.write_text(
        "relations:\n  - id: r1\n    from_character: Bea\n    to_character: Vance\n"
        "    public_role: distrusts\n    private_truth: Protects a hidden secret\n", encoding="utf-8"
    )
    before = source.read_bytes()
    graph = project_studio_graph(tmp_path)
    assert len(graph["nodes"]) == 2 and len(graph["edges"]) == 1
    edge = graph["edges"][0]
    assert edge["label"] == "distrusts"
    assert edge["authority"] == "RELATIONS SOURCE"
    assert edge["source_ref"] == "relations.yaml#/relations/0"
    assert graph["relations_sha256"] and edge["source_sha256"] == graph["relations_sha256"]
    assert source.read_bytes() == before


def test_missing_or_invalid_relations_are_not_invented(tmp_path):
    empty = project_studio_graph(tmp_path)
    assert empty["nodes"] == [] and empty["edges"] == []
    (tmp_path / "relations.yaml").write_text("relations: [invalid relation]", encoding="utf-8")
    invalid = project_studio_graph(tmp_path)
    assert not invalid["nodes"] and invalid["warnings"]


def test_story_lenses_have_working_authority_and_source_identity(tmp_path):
    graph = project_studio_graph(tmp_path, workspace_id="story-1", session_version=5, story_orientation={
        "story_lenses": [
            {"lens_id": "story_engine", "title": "Main engine", "summary": "Mystery",
             "state": "inferred", "related_lens_ids": ["reader_experience"], "source_component_ids": ["engine-1"]},
            {"lens_id": "reader_experience", "title": "Reader experience",
             "state": "unestablished", "related_lens_ids": [], "source_component_ids": []},
        ]
    })
    assert graph["session_version"] == 5
    assert len(graph["nodes"]) == 2
    assert graph["nodes"][1]["status"] == "unestablished"
    assert graph["nodes"][0]["authority"] == "DERIVED / NOT CANON"
    assert graph["edges"][0]["target"] == "lens:reader_experience"
