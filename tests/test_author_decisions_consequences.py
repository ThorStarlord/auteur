"""TDD tests for the Author-Decision Consumer (mechanism B): consequences.

Binding contract (design revision 1, 2026-08):
- No alternative->character/thread/provenance relationship may be inferred from
  ids, labels, prose, token matching, fuzzy matching, or semantic similarity.
- Per-alternative consequences require an explicitly accepted relationship
  (default_references[].relates_to is currently the ONLY shipped explicit
  cross-reference mechanism).
- roster_slot / thread_carrier / blocked_provenance_relevance are
  decision-level (common) probes.
- COMMON_ONLY is a valid successful result (Case E is expected COMMON_ONLY;
  "signe_marriage" must NOT establish a relationship with "Signe").
- Common extraction preserves provenance (members + refs).
- No ranking, score, recommendation, verdict, mutation, or as-if propagation.

First batch is expected RED: the consequences module does not exist yet.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml as _yaml

from auteur.author_decisions import (
    AuthorDecision,
    DecisionValidationError,
    build_decision_context,
)

FIXTURES = Path(__file__).parent / "fixtures" / "author_decisions"
CASE_D = FIXTURES / "case-d"
CASE_E = FIXTURES / "case-e"


def load_identity(path: Path):
    from auteur.identity import StoryIdentity
    return StoryIdentity.from_yaml(path)


def load_blueprint(path: Path):
    from auteur.blueprint import StoryBlueprint
    return StoryBlueprint.from_yaml(path)


def case_ctx(case_dir: Path, decision_file: str):
    dec = AuthorDecision.from_yaml(case_dir / decision_file)
    identity = load_identity(case_dir / "story_identity.yaml")
    blueprint = load_blueprint(case_dir / "blueprint.yaml")
    return build_decision_context(dec, identity, blueprint)


def case_consequences(case_dir: Path, decision_file: str) -> dict:
    ctx = case_ctx(case_dir, decision_file)
    report = ctx.build_report()
    return report["consequences"]


D_DIR, D_DEC = CASE_D, "nine-chairs-structure.yaml"
E_DIR, E_DEC = CASE_E, "salt-of-the-earth-subplot-cut.yaml"


# ---------------------------------------------------------------------------
# Golden acceptance fixtures (design Q10 — recomputed under the no-inference rule)
# ---------------------------------------------------------------------------

def test_golden_case_d_consequences_exact():
    expected = _yaml.safe_load((CASE_D / "expected-consequences.yaml").read_text(encoding="utf-8"))
    assert case_consequences(D_DIR, D_DEC) == expected


def test_golden_case_e_consequences_exact():
    expected = _yaml.safe_load((CASE_E / "expected-consequences.yaml").read_text(encoding="utf-8"))
    assert case_consequences(E_DIR, E_DEC) == expected


def test_d_distinguishability_single_axis_declared_relationship():
    c = case_consequences(D_DIR, D_DEC)
    assert c["distinguishability"] == "SINGLE_AXIS"
    assert c["distinguishability_axes"] == ["declared_relationship"]
    assert c["distinguishability_note"] == "only this structural axis differs: declared_relationship"


def test_e_distinguishability_common_only():
    c = case_consequences(E_DIR, E_DEC)
    assert c["distinguishability"] == "COMMON_ONLY"
    assert c["distinguishability_axes"] == []
    assert c["distinguishability_note"] == (
        "all alternatives share these consequences; the current representation "
        "cannot distinguish them further"
    )


# ---------------------------------------------------------------------------
# Anti-inference (revision 1): no relationship manufactured from labels/ids
# ---------------------------------------------------------------------------

def test_e_alternative_signe_marriage_never_links_to_signe():
    c = case_consequences(E_DIR, E_DEC)
    by_target = {a["alternative_id"]: a["findings"] for a in c["alternatives"]}
    # The alternative lists must be empty: nothing is knowable per-alternative
    # because the artifact exposes no explicit alternative-entity relation.
    assert by_target["signe_marriage"] == []
    assert by_target["anders_debt"] == []
    assert by_target["marta_pregnancy"] == []
    # No roster/provenance finding may be scoped to an alternative at all.
    for alt in c["alternatives"]:
        for f in alt["findings"]:
            assert f["probe_id"] not in ("roster_slot", "blocked_provenance_relevance", "thread_carrier")


def test_d_alternative_distinction_derives_only_from_relates_to():
    c = case_consequences(D_DIR, D_DEC)
    by_target = {a["alternative_id"]: a["findings"] for a in c["alternatives"]}
    for f in by_target["nine_parallel_arcs"]:
        assert f["probe_id"] == "declared_relationship"
        assert f["target"] == "nine_parallel_arcs"
        assert f["refs"]["decision"].startswith("default_references[")
    assert by_target["one_structural_spine"] == []


# ---------------------------------------------------------------------------
# Probe unit tests
# ---------------------------------------------------------------------------

def test_explicit_alternative_relations_schema_capability():
    c = case_consequences(E_DIR, E_DEC)
    f = next(f for f in c["observations"] if f["probe_id"] == "explicit_alternative_relations")
    assert f["severity"] == "info"
    assert f["message"] == (
        "per-alternative roster/thread/provenance probes were not run: "
        "the AuthorDecision schema exposes no explicit alternative-entity relationship"
    )
    assert f["scope"] == "common"


def test_roster_slot_absent_warning_case_d():
    c = case_consequences(D_DIR, D_DEC)
    slots = [f for f in c["observations"] if f["probe_id"] == "roster_slot"]
    assert len(slots) == 9
    first = slots[0]
    assert first["severity"] == "warning"
    assert first["message"] == "required character Ansel (standing=equal) has no roster slot in the current Blueprint"
    assert first["refs"]["decision"] == "required_characters[0]"
    assert first["refs"]["identity"] == "characters[0]"
    assert first["refs"]["blueprint"] is None


def test_roster_slot_present_and_unlinked_case_e():
    c = case_consequences(E_DIR, E_DEC)
    slots = [f for f in c["observations"] if f["probe_id"] == "roster_slot"]
    present = next(f for f in slots if f["severity"] == "info")
    assert present["message"] == (
        "required character Signe (standing=protagonist) is represented in the "
        "roster as protagonist, arc growth"
    )
    unlinked = next(f for f in slots if "not linked" in f["message"])
    assert unlinked["message"] == "roster slot for Signe is not linked to an identity character"
    assert unlinked["severity"] == "warning"


def test_roster_slot_identity_missing_fails_closed():
    base = _yaml.safe_load((E_DIR / E_DEC).read_text(encoding="utf-8"))
    base["required_characters"] = [{"name": "Nobody", "standing": None}]
    dec = AuthorDecision.from_dict(base)
    ctx = build_decision_context(dec, load_identity(E_DIR / "story_identity.yaml"),
                                  load_blueprint(E_DIR / "blueprint.yaml"))
    c = ctx.build_report()["consequences"]
    f = next(f for f in c["observations"] if f["probe_id"] == "roster_slot")
    assert f["severity"] == "info"
    assert f["message"] == "probe not run: no identity character named Nobody"


def test_roster_slot_ambiguous_name_fails_closed():
    # Duplicate in the identity roster -> ambiguous identity name (blueprint probe skipped).
    identity = load_identity(E_DIR / "story_identity.yaml")
    identity.characters.append(identity.characters[0])
    dec = AuthorDecision.from_yaml(E_DIR / E_DEC)
    ctx = build_decision_context(dec, identity, load_blueprint(E_DIR / "blueprint.yaml"))
    msgs = [f["message"] for f in ctx.build_report()["consequences"]["observations"]
            if f["probe_id"] == "roster_slot"]
    assert "probe not run: ambiguous identity name Signe" in msgs
    # Duplicate in the blueprint roster only -> ambiguous roster name.
    bp = load_blueprint(E_DIR / "blueprint.yaml")
    bp.characters.append(bp.characters[0])
    ctx2 = build_decision_context(dec, load_identity(E_DIR / "story_identity.yaml"), bp)
    msgs2 = [f["message"] for f in ctx2.build_report()["consequences"]["observations"]
             if f["probe_id"] == "roster_slot"]
    assert "probe not run: ambiguous roster name Signe" in msgs2


def test_consequences_require_resolved_identity_and_blueprint():
    from auteur.author_decisions.consequences import build_consequences

    ctx = case_ctx(D_DIR, D_DEC)
    ctx.identity = None
    with pytest.raises(DecisionValidationError, match="resolved identity and blueprint"):
        build_consequences(ctx)


def test_thread_carrier_capability_statement():
    c = case_consequences(D_DIR, D_DEC)
    f = next(f for f in c["observations"] if f["probe_id"] == "thread_carrier")
    assert f["severity"] == "info"
    assert f["message"] == (
        "thread structure has 3 thread(s): Secondary Struggle, Relationship Echo, "
        "Secondary Subplot 3; the Blueprint exposes no explicit thread-to-character "
        "linkage, so thread carriers for decision characters cannot be verified"
    )


def test_thread_carrier_no_threads_fails_closed():
    bp = load_blueprint(E_DIR / "blueprint.yaml")
    bp.story_engine.threads = []
    dec = AuthorDecision.from_yaml(E_DIR / E_DEC)
    ctx2 = build_decision_context(dec, load_identity(E_DIR / "story_identity.yaml"), bp)
    c = ctx2.build_report()["consequences"]
    f = next(f for f in c["observations"] if f["probe_id"] == "thread_carrier")
    assert f["message"] == "probe not run: blueprint has no thread structure"


def test_declared_relationship_target_alternative_vs_common():
    c = case_consequences(D_DIR, D_DEC)
    alt_f = [f for a in c["alternatives"] for f in a["findings"]]
    assert len(alt_f) == 2
    msgs = {f["message"] for f in alt_f}
    assert msgs == {
        "declared relationship: identity.pov_type = third_person_limited_single "
        "[conflicts_with] relates_to nine_parallel_arcs",
        "declared relationship: structure.act_structure = three_act "
        "[conflicts_with] relates_to nine_parallel_arcs",
    }
    common_rel = [f for f in c["observations"] if f["probe_id"] == "declared_relationship"]
    assert len(common_rel) == 1
    assert common_rel[0]["message"] == (
        "declared relationship: characters = [Protagonist, Antagonist] "
        "[conflicts_with] relates_to not_this[3]"
    )


def test_e_declared_relationship_common_bittersweet():
    c = case_consequences(E_DIR, E_DEC)
    rel = [f for f in c["observations"] if f["probe_id"] == "declared_relationship"]
    assert len(rel) == 1
    assert rel[0]["message"] == (
        "declared relationship: contract.mandatory_ending_tone = bittersweet "
        "[conflicts_with] relates_to not_this[3]"
    )


def test_blocked_provenance_relevance_counts():
    c_d = case_consequences(D_DIR, D_DEC)
    f_d = next(f for f in c_d["observations"] if f["probe_id"] == "blocked_provenance_relevance")
    assert f_d["severity"] == "warning"
    assert f_d["message"].startswith("9 blocked propagation outcome(s) reference decision characters:")
    c_e = case_consequences(E_DIR, E_DEC)
    f_e = next(f for f in c_e["observations"] if f["probe_id"] == "blocked_provenance_relevance")
    assert f_e["severity"] == "info"
    assert f_e["message"] == "no blocked propagation outcomes reference decision characters"


def test_combination_direction_neutral_and_only_for_choose_k_of_n():
    c_e = case_consequences(E_DIR, E_DEC)
    f = next(f for f in c_e["observations"] if f["probe_id"] == "combination_direction")
    assert f["message"] == "combination membership is explicit; keep/cut interpretation is unspecified"
    for banned in ("retained", "removed", "selected for inclusion", "kept"):
        assert banned not in f["message"].lower()
    c_d = case_consequences(D_DIR, D_DEC)
    assert all(f["probe_id"] != "combination_direction" for f in c_d["observations"])


# ---------------------------------------------------------------------------
# Grouping: provenance-preserving common extraction
# ---------------------------------------------------------------------------

def test_observations_preserve_members_and_refs():
    c = case_consequences(D_DIR, D_DEC)
    all_alts = ["nine_parallel_arcs", "one_structural_spine"]
    for f in c["observations"]:
        assert f["scope"] == "common"
        assert f["discriminates"] is False
        assert f["members"] == all_alts
        assert f["target"] == ""
    ref_carrying = [f for f in c["observations"] if f["probe_id"] in
                    ("roster_slot", "declared_relationship", "blocked_provenance_relevance")]
    assert ref_carrying and all(f["refs"]["decision"] for f in ref_carrying)


def test_per_alternative_findings_discriminate():
    c = case_consequences(D_DIR, D_DEC)
    for alt in c["alternatives"]:
        for f in alt["findings"]:
            assert f["scope"] == "alternative"
            assert f["target"] == alt["alternative_id"]
            assert f["members"] == [alt["alternative_id"]]
            assert f["discriminates"] is True


def test_combinations_section_present_only_for_choose_k_of_n():
    c_e = case_consequences(E_DIR, E_DEC)
    assert [tuple(combo["combination"]) for combo in c_e["combinations"]] == [
        ("anders_debt", "marta_pregnancy"),
        ("anders_debt", "signe_marriage"),
        ("marta_pregnancy", "signe_marriage"),
    ]
    assert all(combo["findings"] == [] for combo in c_e["combinations"])
    c_d = case_consequences(D_DIR, D_DEC)
    assert "combinations" not in c_d


# ---------------------------------------------------------------------------
# Anti-ranking + determinism
# ---------------------------------------------------------------------------

def test_no_ranking_or_verdict_keys_anywhere():
    ctx = case_ctx(D_DIR, D_DEC)
    report = ctx.build_report()
    blob = json.dumps(report)
    for forbidden in ("rank", "score", "verdict", "recommended", "better", "preferable", "stronger"):
        assert forbidden not in blob


def test_determinism_byte_identical():
    a = json.dumps(case_consequences(D_DIR, D_DEC), sort_keys=True)
    b = json.dumps(case_consequences(D_DIR, D_DEC), sort_keys=True)
    assert a == b


def test_unresolvable_default_ref_fails_closed():
    base = _yaml.safe_load((D_DIR / D_DEC).read_text(encoding="utf-8"))
    base["default_references"] = [{"default_id": "no.such.field", "relates_to": "x"}]
    dec = AuthorDecision.from_dict(base)
    with pytest.raises(DecisionValidationError):
        build_decision_context(dec, load_identity(D_DIR / "story_identity.yaml"),
                               load_blueprint(D_DIR / "blueprint.yaml"))


# ---------------------------------------------------------------------------
# CLI surface: evaluate renders consequences; view stays unchanged
# ---------------------------------------------------------------------------

def _make_project(tmp_path, case_dir, decision_file):
    import shutil
    proj = tmp_path / "project"
    proj.mkdir(parents=True)
    shutil.copy(case_dir / "story_identity.yaml", proj / "story_identity.yaml")
    shutil.copy(case_dir / "blueprint.yaml", proj / "blueprint.yaml")
    ad = proj / "author_decisions"
    ad.mkdir()
    shutil.copy(case_dir / decision_file, ad / decision_file)
    return proj


def _run_cli(args, cwd):
    import subprocess
    import sys
    r = subprocess.run([sys.executable, "-m", "auteur.cli", *args], cwd=str(cwd),
                       capture_output=True, text=True, timeout=120)
    return r.returncode, r.stdout


def test_cli_evaluate_text_renders_consequences(tmp_path):
    proj = _make_project(tmp_path, D_DIR, D_DEC)
    rc, out = _run_cli([
        "decision", "evaluate", "nine-chairs-structure",
        "--identity", str(proj / "story_identity.yaml"),
        "--blueprint", str(proj / "blueprint.yaml"),
        "--project", str(proj),
    ], cwd=Path.cwd())
    assert rc == 0
    assert "Consequences:" in out
    assert "SINGLE_AXIS" in out
    assert "No consequence implies a recommendation; alternatives are not ranked." in out


def test_cli_evaluate_json_contains_consequences(tmp_path):
    proj = _make_project(tmp_path, E_DIR, E_DEC)
    rc, out = _run_cli([
        "decision", "evaluate", "salt-of-the-earth-subplot-cut",
        "--identity", str(proj / "story_identity.yaml"),
        "--blueprint", str(proj / "blueprint.yaml"),
        "--project", str(proj), "--json",
    ], cwd=Path.cwd())
    assert rc == 0
    assert "consequences:" in out
    assert "COMMON_ONLY" in out


def test_cli_view_unchanged_no_consequences(tmp_path):
    proj = _make_project(tmp_path, D_DIR, D_DEC)
    rc, out = _run_cli([
        "decision", "view", "nine-chairs-structure",
        "--identity", str(proj / "story_identity.yaml"),
        "--blueprint", str(proj / "blueprint.yaml"),
        "--project", str(proj),
    ], cwd=Path.cwd())
    assert rc == 0
    assert "Consequences:" not in out
    assert "RESOLVED" in out
