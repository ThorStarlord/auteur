"""TDD tests for M1: explicit alternative/entity bindings (approved design
rev 2 @ 9bb9450, docs/design/2026-08-alternative-entity-binding.md).

Authority invariants under test:
- bindings are explicit authored rows; no inference from labels/names/prose;
- relationship vocabulary is exactly {concerns, conflicts_with};
- absent binding = "not supplied", never "concerns nothing";
- invalid/unresolvable bindings fail closed with zero partial content;
- existing decisions without bindings remain byte-compatible.
"""
from __future__ import annotations

from pathlib import Path

import pytest
import yaml as _yaml

from auteur.author_decisions import (
    AuthorDecision,
    build_decision_context,
    DecisionValidationError,
)
from auteur.blueprint import StoryBlueprint
from auteur.identity import StoryIdentity

FIXTURES = Path(__file__).parent / "fixtures" / "author_decisions"
CASE_D = FIXTURES / "case-d"
CASE_E = FIXTURES / "case-e"


def load_identity(case_dir: Path):
    return StoryIdentity.from_yaml(case_dir / "story_identity.yaml")


def load_blueprint(case_dir: Path):
    return StoryBlueprint.from_yaml(case_dir / "blueprint.yaml")


def ctx_for(decision, case_dir: Path):
    return build_decision_context(decision, load_identity(case_dir), load_blueprint(case_dir))


# ---------------------------------------------------------------------------
# Schema: bindings parse + validation (expected RED until models exist)
# ---------------------------------------------------------------------------

def test_bound_artifacts_parse():
    dec = AuthorDecision.from_yaml(CASE_E / "salt-of-the-earth-subplot-cut-with-bindings.yaml")
    assert len(dec.alternative_bindings) == 3
    assert dec.alternative_bindings[2].alternative_id == "signe_marriage"
    assert dec.alternative_bindings[2].references[0].entity_ref == "identity.characters[0]"
    assert dec.alternative_bindings[2].references[0].relationship.value == "concerns"


def test_no_bindings_defaults_empty():
    dec = AuthorDecision.from_yaml(CASE_E / "salt-of-the-earth-subplot-cut.yaml")
    assert dec.alternative_bindings == []


def test_unknown_alternative_id_rejected():
    data = _yaml.safe_load((CASE_E / "salt-of-the-earth-subplot-cut.yaml").read_text(encoding="utf-8"))
    data["alternative_bindings"] = [
        {"alternative_id": "no_such_alt", "references": [{"entity_ref": "identity.characters[0]"}]}
    ]
    with pytest.raises(DecisionValidationError, match="alternative"):
        AuthorDecision.from_dict(data)


def test_duplicate_binding_block_rejected():
    data = _yaml.safe_load((CASE_E / "salt-of-the-earth-subplot-cut.yaml").read_text(encoding="utf-8"))
    data["alternative_bindings"] = [
        {"alternative_id": "signe_marriage", "references": [{"entity_ref": "identity.characters[0]"}]},
        {"alternative_id": "signe_marriage", "references": [{"entity_ref": "identity.characters[1]"}]},
    ]
    with pytest.raises(DecisionValidationError, match="duplicate|bind"):
        AuthorDecision.from_dict(data)


def test_duplicate_identical_reference_rejected():
    data = _yaml.safe_load((CASE_E / "salt-of-the-earth-subplot-cut.yaml").read_text(encoding="utf-8"))
    data["alternative_bindings"] = [
        {"alternative_id": "signe_marriage", "references": [
            {"entity_ref": "identity.characters[0]", "relationship": "concerns"},
            {"entity_ref": "identity.characters[0]", "relationship": "concerns"},
        ]},
    ]
    with pytest.raises(DecisionValidationError, match="duplicate"):
        AuthorDecision.from_dict(data)


def test_conflicting_relationship_declaration_rejected():
    data = _yaml.safe_load((CASE_E / "salt-of-the-earth-subplot-cut.yaml").read_text(encoding="utf-8"))
    data["alternative_bindings"] = [
        {"alternative_id": "signe_marriage", "references": [
            {"entity_ref": "identity.characters[0]", "relationship": "concerns"},
            {"entity_ref": "identity.characters[0]", "relationship": "conflicts_with"},
        ]},
    ]
    with pytest.raises(DecisionValidationError, match="conflict"):
        AuthorDecision.from_dict(data)


def test_requires_and_preserves_rejected():
    for rel in ("requires", "preserves"):
        data = _yaml.safe_load((CASE_E / "salt-of-the-earth-subplot-cut.yaml").read_text(encoding="utf-8"))
        data["alternative_bindings"] = [
            {"alternative_id": "signe_marriage", "references": [
                {"entity_ref": "identity.characters[0]", "relationship": rel},
            ]},
        ]
        with pytest.raises(DecisionValidationError):
            AuthorDecision.from_dict(data)


def test_binding_extra_fields_forbidden():
    data = _yaml.safe_load((CASE_E / "salt-of-the-earth-subplot-cut.yaml").read_text(encoding="utf-8"))
    data["alternative_bindings"] = [
        {"alternative_id": "signe_marriage", "references": [
            {"entity_ref": "identity.characters[0]", "relationship": "concerns", "sneaky": True},
        ]},
    ]
    with pytest.raises(DecisionValidationError):
        AuthorDecision.from_dict(data)


# ---------------------------------------------------------------------------
# Context: thin resolution of ONLY bound entities; fail closed
# ---------------------------------------------------------------------------

def test_resolved_bindings_exact_paths():
    dec = AuthorDecision.from_yaml(CASE_E / "salt-of-the-earth-subplot-cut-with-bindings.yaml")
    ctx = ctx_for(dec, CASE_E)
    rb = ctx.resolved_bindings
    assert len(rb) == 3
    by_alt = {r.alternative_id: r for r in rb}
    assert by_alt["signe_marriage"].entity_ref == "identity.characters[0]"
    assert by_alt["signe_marriage"].entity.name == "Signe"


def test_bogus_entity_ref_fails_closed():
    data = _yaml.safe_load((CASE_E / "salt-of-the-earth-subplot-cut.yaml").read_text(encoding="utf-8"))
    data["alternative_bindings"] = [
        {"alternative_id": "signe_marriage", "references": [{"entity_ref": "identity.characters[999]"}]},
    ]
    with pytest.raises(DecisionValidationError, match="index|range"):
        ctx_for(AuthorDecision.from_dict(data), CASE_E)


def test_negative_and_malformed_indices_rejected():
    """Strict index grammar: [-1] would silently bind the LAST entity via int();
    [ 1] / [+1] / [1_0] are malformed. All fail closed."""
    for ref in ("identity.characters[-1]", "identity.characters[ 1]",
                "identity.characters[+1]", "identity.characters[1_0]"):
        data = _yaml.safe_load((CASE_E / "salt-of-the-earth-subplot-cut.yaml").read_text(encoding="utf-8"))
        data["alternative_bindings"] = [
            {"alternative_id": "signe_marriage", "references": [{"entity_ref": ref}]},
        ]
        with pytest.raises(DecisionValidationError):
            ctx_for(AuthorDecision.from_dict(data), CASE_E)


def test_non_identity_blueprint_root_rejected():
    data = _yaml.safe_load((CASE_E / "salt-of-the-earth-subplot-cut.yaml").read_text(encoding="utf-8"))
    data["alternative_bindings"] = [
        {"alternative_id": "signe_marriage", "references": [{"entity_ref": "universe.characters[0]"}]},
    ]
    with pytest.raises(DecisionValidationError, match="root|identity|blueprint"):
        ctx_for(AuthorDecision.from_dict(data), CASE_E)


# ---------------------------------------------------------------------------
# Consumer: golden D/E with bindings; anti-inference; absence; combinations
# ---------------------------------------------------------------------------

def test_case_d_bound_golden():
    dec = AuthorDecision.from_yaml(CASE_D / "nine-chairs-structure-with-bindings.yaml")
    cons = ctx_for(dec, CASE_D).build_report()["consequences"]
    per_alt = {a["alternative_id"]: a["findings"] for a in cons["alternatives"]}
    assert cons["distinguishability"] == "MULTIPLE_AXES"
    # axes: M1 binding probes + the shipped declared_relationship axis (the
    # frozen artifact's default_references target nine_parallel_arcs)
    assert cons["distinguishability_axes"] == [
        "blocked_provenance_relevance", "declared_relationship", "entity_link", "roster_slot"]
    # nine_parallel_arcs: 9 roster warnings (Ansel's warning is per-alternative
    # in BOTH alternatives because each finding's decision ref points at its own
    # binding block, so the shipped common-lifting does not merge them) + 1
    # blocked relevance (9 outcomes) + 9 entity links + 2 shipped
    # declared_relationship findings from the frozen default_references
    n9 = per_alt["nine_parallel_arcs"]
    assert len([f for f in n9 if f["probe_id"] == "roster_slot"]) == 9
    assert len([f for f in n9 if f["probe_id"] == "entity_link"]) == 9
    assert len([f for f in n9 if f["probe_id"] == "declared_relationship"]) == 2
    assert [f for f in n9 if f["probe_id"] == "blocked_provenance_relevance"][0]["severity"] == "warning"
    # one_structural_spine: 1 roster warning (Ansel, bound-scope) + 1 blocked
    # relevance (1 outcome) + 1 entity link
    spine = per_alt["one_structural_spine"]
    assert len([f for f in spine if f["probe_id"] == "roster_slot"]) == 1
    assert len([f for f in spine if f["probe_id"] == "entity_link"]) == 1
    assert "characters[0].undergoes_central_change" in [f for f in spine if f["probe_id"] == "blocked_provenance_relevance"][0]["message"]
    # decision-ref provenance: the bound Ansel findings point at their own
    # binding blocks, never at the artifact's required_characters row
    ans = [f for f in per_alt["nine_parallel_arcs"] if f["probe_id"] == "roster_slot" and "Ansel" in f["message"]][0]
    assert ans["refs"]["decision"] == "alternative_bindings[nine_parallel_arcs][0]"
    # the decision-level roster warning (standing=equal, from required_characters)
    # remains a separate common observation
    assert any(o["probe_id"] == "roster_slot" and "standing=equal" in o["message"] for o in cons["observations"])


def test_case_e_bound_golden_and_anti_inference():
    dec = AuthorDecision.from_yaml(CASE_E / "salt-of-the-earth-subplot-cut-with-bindings.yaml")
    cons = ctx_for(dec, CASE_E).build_report()["consequences"]
    per_alt = {a["alternative_id"]: a["findings"] for a in cons["alternatives"]}
    assert cons["distinguishability"] == "MULTIPLE_AXES"
    signe = per_alt["signe_marriage"]
    # roster: represented as protagonist + unlinked-to-identity warning
    assert any("represented in the roster as protagonist" in f["message"] for f in signe if f["probe_id"] == "roster_slot")
    assert any("not linked to an identity character" in f["message"] for f in signe if f["probe_id"] == "roster_slot")
    # entity link: authored relationship, resolved to Signe
    link = [f for f in signe if f["probe_id"] == "entity_link"]
    assert len(link) == 1
    assert "signe_marriage" in link[0]["message"] and "Signe" in link[0]["message"]
    # anders/marta: roster warning (no slot) + entity link, NO roster-info for Signe
    for alt in ("anders_debt", "marta_pregnancy"):
        fs = per_alt[alt]
        assert any(f["probe_id"] == "roster_slot" and "has no roster slot" in f["message"] for f in fs)
        assert len([f for f in fs if f["probe_id"] == "entity_link"]) == 1


def test_anti_inference_unbound_artifacts_unchanged():
    """Frozen unbound artifacts must reproduce the shipped golden expectations
    exactly (byte-compatible consequences): no binding-derived consequences may
    appear when no binding was authored."""
    for case_dir, decision_name, golden_name in (
        (CASE_D, "nine-chairs-structure.yaml", "expected-consequences.yaml"),
        (CASE_E, "salt-of-the-earth-subplot-cut.yaml", "expected-consequences.yaml"),
    ):
        dec = AuthorDecision.from_yaml(case_dir / decision_name)
        cons = ctx_for(dec, case_dir).build_report()["consequences"]
        golden = _yaml.safe_load((case_dir / golden_name).read_text(encoding="utf-8"))
        assert cons == golden


def test_absence_finding_for_unbound_alternative():
    """Alternative without a binding gets the absence finding; never an
    inferred relationship."""
    data = _yaml.safe_load((CASE_E / "salt-of-the-earth-subplot-cut.yaml").read_text(encoding="utf-8"))
    data["alternative_bindings"] = [
        {"alternative_id": "signe_marriage", "references": [{"entity_ref": "identity.characters[0]"}]},
    ]
    cons = ctx_for(AuthorDecision.from_dict(data), CASE_E).build_report()["consequences"]
    per_alt = {a["alternative_id"]: a["findings"] for a in cons["alternatives"]}
    for alt in ("anders_debt", "marta_pregnancy"):
        fs = per_alt[alt]
        assert len(fs) == 1
        assert fs[0]["probe_id"] == "binding_absence"
        assert "no explicit binding" in fs[0]["message"]
        assert fs[0]["scope"] == "alternative"
    # bound alternative has NO absence finding and DOES have the entity link
    signe = per_alt["signe_marriage"]
    assert not any(f["probe_id"] == "binding_absence" for f in signe)
    assert any(f["probe_id"] == "entity_link" for f in signe)


def test_choose_k_of_n_with_bindings_renders_combinations():
    """Combination rendering (bug #59 fixed path) works with M1 findings."""
    dec = AuthorDecision.from_yaml(CASE_E / "salt-of-the-earth-subplot-cut-with-bindings.yaml")
    cons = ctx_for(dec, CASE_E).build_report()["consequences"]
    combos = cons["combinations"]
    assert len(combos) == 3
    by_members = {tuple(c["combination"]): c["findings"] for c in combos}
    # union of member findings AFTER shipped common-lifting: the identical
    # blocked-provenance info ("no blocked propagation outcomes...") is lifted
    # to common, so per-alt counts are roster+link for anders/marta and
    # roster-info+unlinked-warning+link for signe.
    assert len(by_members[("anders_debt", "signe_marriage")]) == 2 + 3
    assert len(by_members[("anders_debt", "marta_pregnancy")]) == 2 + 2


# ---------------------------------------------------------------------------
# CLI surface
# ---------------------------------------------------------------------------

def test_create_scaffolds_empty_bindings(tmp_path):
    import subprocess
    import sys
    proj = tmp_path / "p"
    proj.mkdir()
    r = subprocess.run(
        [sys.executable, "-m", "auteur.cli", "decision", "create", "d1",
         "--question", "Q?", "--alternative", "A", "--alternative", "B",
         "--criterion", "C", "--project", "."],
        cwd=str(proj), capture_output=True, text=True, timeout=120,
    )
    assert r.returncode == 0
    data = _yaml.safe_load((proj / "author_decisions" / "d1.yaml").read_text(encoding="utf-8"))
    assert data["alternative_bindings"] == []


def test_accept_records_resolved_bindings(tmp_path):
    import shutil
    import subprocess
    import sys
    proj = tmp_path / "p"
    proj.mkdir(parents=True)
    for name in ("story_identity.yaml", "blueprint.yaml"):
        shutil.copy(CASE_E / name, proj / name)
    ad = proj / "author_decisions"
    ad.mkdir()
    shutil.copy(CASE_E / "salt-of-the-earth-subplot-cut-with-bindings.yaml",
                ad / "salt-of-the-earth-subplot-cut.yaml")
    r = subprocess.run(
        [sys.executable, "-m", "auteur.cli", "decision", "accept",
         "salt-of-the-earth-subplot-cut", "--identity", "story_identity.yaml",
         "--blueprint", "blueprint.yaml", "--project", "."],
        cwd=str(proj), capture_output=True, text=True, timeout=120,
    )
    assert r.returncode == 0, r.stderr
    record = _yaml.safe_load((ad / ".acceptance" / "salt-of-the-earth-subplot-cut.yaml").read_text(encoding="utf-8"))
    rb = record["resolved_bindings"]
    assert len(rb) == 3
    by_alt = {e["alternative_id"]: e for e in rb}
    assert by_alt["signe_marriage"]["entity_ref"] == "identity.characters[0]"
    assert by_alt["signe_marriage"]["relationship"] == "concerns"


def test_evaluate_bound_decision_exit0(tmp_path):
    import shutil
    import subprocess
    import sys
    proj = tmp_path / "p"
    proj.mkdir(parents=True)
    for name in ("story_identity.yaml", "blueprint.yaml"):
        shutil.copy(CASE_E / name, proj / name)
    ad = proj / "author_decisions"
    ad.mkdir()
    shutil.copy(CASE_E / "salt-of-the-earth-subplot-cut-with-bindings.yaml",
                ad / "salt-of-the-earth-subplot-cut.yaml")
    r = subprocess.run(
        [sys.executable, "-m", "auteur.cli", "decision", "evaluate",
         "salt-of-the-earth-subplot-cut", "--identity", "story_identity.yaml",
         "--blueprint", "blueprint.yaml", "--project", "."],
        cwd=str(proj), capture_output=True, text=True, timeout=120,
    )
    assert r.returncode == 0, r.stderr
    assert "MULTIPLE_AXES" in r.stdout
    assert "signe_marriage" in r.stdout and "Signe" in r.stdout
