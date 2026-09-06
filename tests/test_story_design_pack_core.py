from pathlib import Path

import pytest

from auteur.story_design_packs import PackKind, StoryDesignPack, get_design_pack_registry
from auteur.story_design_packs.loader import load_story_design_pack


def test_all_v1_packs_load_with_stable_provenance():
    registry = get_design_pack_registry()
    rows = registry.list()
    assert {row["pack_id"] for row in rows} == {
        "superhero", "anti_hero", "hard_determinism", "corporate_superhuman_metropolis"
    }
    for row in rows:
        pack, digest = registry.get(row["pack_id"])
        assert isinstance(pack, StoryDesignPack)
        assert pack.pack_kind in set(PackKind)
        assert digest == row["content_hash"]
        assert digest == registry.get(row["pack_id"])[1]


def test_malformed_pack_and_unknown_kind_are_rejected():
    with pytest.raises(Exception):
        load_story_design_pack("pack_id: bad\npack_kind: unknown\n")


def test_multiline_raw_yaml_does_not_probe_it_as_a_filesystem_path(monkeypatch):
    raw_yaml = """pack_id: portable_test
pack_kind: genre
version: 0.1.0
schema_version: 1
display_name: Portable Test
description: A raw YAML document.
applicability:
  signals: [portable]
  description: Applies to portability tests.
design_options: []
"""

    original_is_file = Path.is_file

    def raise_for_document_paths(path: Path) -> bool:
        if "\n" in str(path):
            raise OSError("simulated ENAMETOOLONG")
        return original_is_file(path)

    monkeypatch.setattr(Path, "is_file", raise_for_document_paths)

    pack, digest = load_story_design_pack(raw_yaml)

    assert pack.pack_id == "portable_test"
    assert digest


def test_loader_accepts_path_objects_and_string_paths(tmp_path: Path):
    raw_yaml = """pack_id: path_test
pack_kind: genre
version: 0.1.0
schema_version: 1
display_name: Path Test
description: A path-backed YAML document.
applicability:
  signals: [path]
  description: Applies to path tests.
design_options: []
"""
    yaml_path = tmp_path / "pack.yaml"
    yaml_path.write_text(raw_yaml, encoding="utf-8")

    path_pack, path_digest = load_story_design_pack(yaml_path)
    string_pack, string_digest = load_story_design_pack(str(yaml_path))

    assert path_pack == string_pack
    assert path_digest == string_digest


def test_all_builtin_pack_hashes_are_stable():
    registry = get_design_pack_registry()
    first = {row["pack_id"]: row["content_hash"] for row in registry.list()}
    second = {pack_id: registry.get(pack_id)[1] for pack_id in first}

    assert second == first
    assert set(first) == {
        "superhero", "anti_hero", "hard_determinism", "corporate_superhuman_metropolis"
    }
