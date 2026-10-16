"""Existing authored genre YAML is evidence; registry defaults are not."""
from __future__ import annotations

import importlib.util
from pathlib import Path

MODULE = Path(__file__).parents[1] / "src/auteur/beginner/studio_full_evidence.py"
spec = importlib.util.spec_from_file_location("studio_full_evidence_isolated", MODULE)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

VALID = """genre_id: epic_fantasy
display_name: Epic Fantasy
audience_product: Awe and wonder
required_tropes: [journey, fellowship]
optional_tropes: [found family]
default_engine_biases: [responsibility]
"""


def checked(raw):
    assert isinstance(raw, dict)
    if raw.get("genre_id") != "epic_fantasy":
        raise ValueError("unexpected genre id")
    return raw


def test_source_matched_legacy_genre_has_real_bytes_and_hash(tmp_path):
    p=tmp_path/"epic_fantasy.yaml"
    p.write_text(VALID,encoding="utf-8")
    candidate={"nodes":[{"id":"epic","title":"Epic Fantasy","category":"genre"},
                        {"id":"hero","title":"Heroic Fantasy","category":"genre"}]}
    found=module.project_legacy_genre_evidence(candidate,data_dir=tmp_path,validate_contract=checked)
    assert len(found)==1 and found[0]["genreId"]=="epic"
    assert found[0]["sourceKind"]=="legacy_contract"
    assert found[0]["sourceRef"]=="genres/data/epic_fantasy.yaml"
    assert found[0]["contract"]["required_tropes"]==["journey","fellowship"]
    assert len(found[0]["contentHash"])==64
    assert found[0].get("verified") is not True


def test_missing_genre_yml_does_not_trigger_registry_fallback(tmp_path):
    assert module.project_legacy_genre_evidence(
        {"nodes":[{"id":"g","title":"Heroic Fantasy","category":"genre"}]},
        data_dir=tmp_path,validate_contract=checked)==[]


def test_mismatching_claimed_genre_is_not_reported(tmp_path):
    (tmp_path/"epic_fantasy.yaml").write_text(VALID.replace("epic_fantasy","mystery"),encoding="utf-8")
    assert module.project_legacy_genre_evidence(
        {"nodes":[{"id":"g","title":"Epic Fantasy","category":"genre"}]},
        data_dir=tmp_path,validate_contract=lambda x:x)==[]


def test_malformed_contract_is_not_silent_verification(tmp_path):
    (tmp_path/"epic_fantasy.yaml").write_text("[not valid yaml",encoding="utf-8")
    assert module.project_legacy_genre_evidence(
        {"nodes":[{"id":"g","title":"Epic Fantasy","category":"genre"}]},
        data_dir=tmp_path,validate_contract=checked)==[]


def test_no_traversal_fuzzy_match_or_trope_title_match(tmp_path):
    (tmp_path/"epic_fantasy.yaml").write_text(VALID,encoding="utf-8")
    nodes=[{"id":"a","title":"../../epic_fantasy","category":"genre"},
           {"id":"b","title":"Epic Fantasy Retelling","category":"genre"},
           {"id":"c","title":"Epic Fantasy","category":"trope"}]
    assert module.project_legacy_genre_evidence({"nodes":nodes},
        data_dir=tmp_path,validate_contract=checked)==[]


def test_bounded_scan_no_file_writes(tmp_path):
    path=tmp_path/"epic_fantasy.yaml"
    path.write_text(VALID,encoding="utf-8")
    before=path.read_bytes()
    nodes=[{"id":f"g{i}","title":"Epic Fantasy","category":"genre"} for i in range(80)]
    found=module.project_legacy_genre_evidence({"nodes":nodes},
        data_dir=tmp_path,validate_contract=checked)
    assert len(found)<=14 and path.read_bytes()==before
