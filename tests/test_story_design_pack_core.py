from auteur.story_design_packs import PackKind, StoryDesignPack, get_design_pack_registry


def test_all_v1_packs_load_with_stable_provenance():
    registry = get_design_pack_registry()
    rows = registry.list()
    assert {row["pack_id"] for row in rows} == {
        "superhero", "anti_hero", "hard_determinism", "corporate_superhuman_metropolis",
        "rivals_allies", "investigation",
    }
    for row in rows:
        pack, digest = registry.get(row["pack_id"])
        assert isinstance(pack, StoryDesignPack)
        assert pack.pack_kind in set(PackKind)
        assert digest == row["content_hash"]
        assert digest == registry.get(row["pack_id"])[1]


def test_malformed_pack_and_unknown_kind_are_rejected():
    from auteur.story_design_packs.loader import load_story_design_pack
    import pytest

    with pytest.raises(Exception):
        load_story_design_pack("pack_id: bad\npack_kind: unknown\n")
