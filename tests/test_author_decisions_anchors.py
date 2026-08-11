"""TDD tests for B4: decision-local structural anchors (approved design
2026-08-structural-anchors-b4.md @ 89c1b00).

Binding invariants under test:
- anchors are decision-scoped author context, never canonical Blueprint truth;
- anchors + combination_direction are explicitly authored and accepted through
  the existing decision accept boundary;
- no prose extraction / name matching / fuzzy linking / automatic anchor
  creation / automatic conversion of M1 bindings into anchors;
- absence of direction means "membership semantics are unspecified";
- with no anchors authored, Case D/E M1 behavior is byte-identical (no-op
  control);
- deterministic consequences stay non-ranking / non-verdict.
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


def base_e_dict():
    return _yaml.safe_load((CASE_E / "salt-of-the-earth-subplot-cut.yaml").read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------------

def test_anchored_artifact_parses():
    dec = AuthorDecision.from_yaml(CASE_E / "salt-of-the-earth-subplot-cut-with-anchors.yaml")
    assert len(dec.structural_anchors) == 3
    assert dec.structural_anchors[2].anchor_id == "signe_marriage"
    assert dec.structural_anchors[2].participants == ["identity.characters[0]"]
    assert dec.structural_anchors[2].bears_on[0].ref == "blueprint.contract.mandatory_ending_tone"
    assert dec.combination_direction == "kept"


def test_no_anchors_defaults_empty():
    dec = AuthorDecision.from_yaml(CASE_E / "salt-of-the-earth-subplot-cut.yaml")
    assert dec.structural_anchors == []
    assert dec.combination_direction is None


def test_duplicate_anchor_id_rejected():
    data = base_e_dict()
    data["structural_anchors"] = [
        {"anchor_id": "a", "participants": []},
        {"anchor_id": "a", "participants": []},
    ]
    with pytest.raises(DecisionValidationError, match="duplicate"):
        AuthorDecision.from_dict(data)


def test_duplicate_refs_rejected():
    data = base_e_dict()
    data["structural_anchors"] = [
        {"anchor_id": "a", "participants": ["identity.characters[0]", "identity.characters[0]"]},
    ]
    with pytest.raises(DecisionValidationError, match="duplicate"):
        AuthorDecision.from_dict(data)
    data["structural_anchors"] = [
        {"anchor_id": "a", "bears_on": [
            {"ref": "blueprint.contract.mandatory_ending_tone"},
            {"ref": "blueprint.contract.mandatory_ending_tone"},
        ]},
    ]
    with pytest.raises(DecisionValidationError, match="duplicate"):
        AuthorDecision.from_dict(data)


def test_unknown_kind_and_relationship_rejected():
    data = base_e_dict()
    data["structural_anchors"] = [{"anchor_id": "a", "kind": "thread"}]
    with pytest.raises(DecisionValidationError):
        AuthorDecision.from_dict(data)
    data = base_e_dict()
    data["structural_anchors"] = [{"anchor_id": "a", "bears_on": [{"ref": "x", "relationship": "pressures"}]}]
    with pytest.raises(DecisionValidationError):
        AuthorDecision.from_dict(data)


def test_anchor_extra_fields_forbidden():
    data = base_e_dict()
    data["structural_anchors"] = [{"anchor_id": "a", "beats": ["beat1"]}]
    with pytest.raises(DecisionValidationError):
        AuthorDecision.from_dict(data)


def test_direction_validated():
    data = base_e_dict()
    data["combination_direction"] = "cut"
    assert AuthorDecision.from_dict(data).combination_direction == "cut"
    data["combination_direction"] = "maybe"
    with pytest.raises(DecisionValidationError):
        AuthorDecision.from_dict(data)


def test_anchor_id_safe_grammar():
    for bad in ("bad id", "../escape", "", "a" * 200):
        data = base_e_dict()
        data["structural_anchors"] = [{"anchor_id": bad}]
        with pytest.raises(DecisionValidationError):
            AuthorDecision.from_dict(data)


def test_one_of_with_direction_accepted():
    """combination_direction now extends to one_of (approved design
    2026-08-choice-shape-composition.md); the schema no longer rejects it."""
    data = base_e_dict()
    data["combination"] = {"rule": "one_of", "k": None}
    data["combination_direction"] = "kept"
    dec = AuthorDecision.from_dict(data)
    assert dec.combination_direction == "kept"
    data["combination_direction"] = "cut"
    dec = AuthorDecision.from_dict(data)
    assert dec.combination_direction == "cut"


# ---------------------------------------------------------------------------
# Context: decision root + fail-closed resolution
# ---------------------------------------------------------------------------

def test_resolved_anchors_exact():
    dec = AuthorDecision.from_yaml(CASE_E / "salt-of-the-earth-subplot-cut-with-anchors.yaml")
    ctx = ctx_for(dec, CASE_E)
    assert len(ctx.resolved_anchors) == 3
    ra = {r.anchor_id: r for r in ctx.resolved_anchors}
    assert ra["signe_marriage"].participants[0][0].name == "Signe"
    assert ra["signe_marriage"].bears_on[0][1] == "bittersweet"
    assert ctx.combination_direction == "kept"


def test_decision_root_resolves_anchor():
    dec = AuthorDecision.from_yaml(CASE_E / "salt-of-the-earth-subplot-cut-with-anchors.yaml")
    ctx = ctx_for(dec, CASE_E)
    rb = {r.alternative_id: r for r in ctx.resolved_bindings}
    # bindings in the anchored fixture target anchors via stable anchor_id
    assert rb["signe_marriage"].entity_ref == "decision.structural_anchors[id=signe_marriage]"
    assert rb["signe_marriage"].entity.anchor_id == "signe_marriage"


def test_anchor_ref_stable_under_reorder():
    """R2.1: reordering anchors must not change what a stable anchor_id ref
    resolves to."""
    data = base_e_dict()
    data["structural_anchors"] = [
        {"anchor_id": "marta_pregnancy", "participants": ["identity.characters[2]"]},
        {"anchor_id": "signe_marriage", "participants": ["identity.characters[0]"]},
        {"anchor_id": "anders_debt", "participants": ["identity.characters[1]"]},
    ]
    data["alternative_bindings"] = [
        {"alternative_id": "signe_marriage",
         "references": [{"entity_ref": "decision.structural_anchors[id=signe_marriage]"}]},
    ]
    ctx = ctx_for(AuthorDecision.from_dict(data), CASE_E)
    rb = ctx.resolved_bindings[0]
    assert rb.entity.anchor_id == "signe_marriage"
    assert rb.entity.participants == ["identity.characters[0]"]


def test_positional_anchor_ref_rejected():
    """R2.1: structural_anchors[N] positional refs are rejected — anchor
    identity is the anchor_id only."""
    data = base_e_dict()
    data["structural_anchors"] = [{"anchor_id": "a", "participants": []}]
    data["alternative_bindings"] = [
        {"alternative_id": "signe_marriage",
         "references": [{"entity_ref": "decision.structural_anchors[0]"}]},
    ]
    with pytest.raises(DecisionValidationError, match="positional"):
        ctx_for(AuthorDecision.from_dict(data), CASE_E)


def test_carrier_positive_path_thread_accepted():
    """R2.2 positive path: a thread-like carrier resolves and is reported
    per-alternative when the anchor is bound."""
    data = base_e_dict()
    data["structural_anchors"] = [
        {"anchor_id": "a", "carrier_refs": ["blueprint.story_engine.threads[0]"]},
    ]
    data["alternative_bindings"] = [
        {"alternative_id": "signe_marriage",
         "references": [{"entity_ref": "decision.structural_anchors[id=a]"}]},
    ]
    dec = AuthorDecision.from_dict(data)
    cons = ctx_for(dec, CASE_E).build_report()["consequences"]
    per_alt = {a["alternative_id"]: a["findings"] for a in cons["alternatives"]}
    assert any("carried by" in f["message"] for f in per_alt["signe_marriage"])


def test_unknown_anchor_id_ref_fails_closed():
    data = base_e_dict()
    data["structural_anchors"] = [{"anchor_id": "a", "participants": []}]
    data["alternative_bindings"] = [
        {"alternative_id": "signe_marriage",
         "references": [{"entity_ref": "decision.structural_anchors[id=no_such]"}]},
    ]
    with pytest.raises(DecisionValidationError, match="unknown anchor_id"):
        ctx_for(AuthorDecision.from_dict(data), CASE_E)


def test_anchor_id_ref_never_falls_back_to_names():
    """R2.1: the anchor_id lookup is exact-id-only; a character named like the
    anchor must not resolve in its place."""
    data = base_e_dict()
    data["structural_anchors"] = [{"anchor_id": "a", "participants": []}]
    data["alternative_bindings"] = [
        {"alternative_id": "signe_marriage",
         "references": [{"entity_ref": "decision.structural_anchors[id=Signe]"}]},
    ]
    with pytest.raises(DecisionValidationError, match="unknown anchor_id"):
        ctx_for(AuthorDecision.from_dict(data), CASE_E)


def test_unresolvable_anchor_ref_fails_closed():
    data = base_e_dict()
    data["structural_anchors"] = [{"anchor_id": "a", "participants": ["identity.characters[99]"]}]
    with pytest.raises(DecisionValidationError):
        ctx_for(AuthorDecision.from_dict(data), CASE_E)
    data = base_e_dict()
    data["structural_anchors"] = [{"anchor_id": "a", "carrier_refs": ["blueprint.no_such[0]"]}]
    with pytest.raises(DecisionValidationError):
        ctx_for(AuthorDecision.from_dict(data), CASE_E)
    data = base_e_dict()
    data["structural_anchors"] = [{"anchor_id": "a", "bears_on": [{"ref": "blueprint.no_such"}]}]
    with pytest.raises(DecisionValidationError):
        ctx_for(AuthorDecision.from_dict(data), CASE_E)


def test_participants_semantic_type_rejected():
    """R2.2: participants must be character entities; a scalar/contract value
    fails closed instead of becoming an accepted meaningless relationship."""
    data = base_e_dict()
    data["structural_anchors"] = [
        {"anchor_id": "a", "participants": ["blueprint.contract.mandatory_ending_tone"]},
    ]
    with pytest.raises(DecisionValidationError, match="non-character"):
        ctx_for(AuthorDecision.from_dict(data), CASE_E)


def test_carrier_semantic_type_rejected():
    """R2.2: carrier_refs must be thread-like carriers; an identity character
    fails closed."""
    data = base_e_dict()
    data["structural_anchors"] = [
        {"anchor_id": "a", "carrier_refs": ["identity.characters[0]"]},
    ]
    with pytest.raises(DecisionValidationError, match="non-thread"):
        ctx_for(AuthorDecision.from_dict(data), CASE_E)


def test_bears_on_semantic_type_rejected():
    """R2.2: bears_on must resolve to scalar/constraint-like values the
    consumer can render; an entity (character) fails closed."""
    data = base_e_dict()
    data["structural_anchors"] = [
        {"anchor_id": "a", "bears_on": [{"ref": "blueprint.characters[0]"}]},
    ]
    with pytest.raises(DecisionValidationError, match="cannot render"):
        ctx_for(AuthorDecision.from_dict(data), CASE_E)


# ---------------------------------------------------------------------------
# Consumer: Case E anchored golden; Case D no-op control; absence semantics
# ---------------------------------------------------------------------------

def test_case_e_anchored_golden():
    dec = AuthorDecision.from_yaml(CASE_E / "salt-of-the-earth-subplot-cut-with-anchors.yaml")
    cons = ctx_for(dec, CASE_E).build_report()["consequences"]
    per_alt = {a["alternative_id"]: a["findings"] for a in cons["alternatives"]}
    signe = per_alt["signe_marriage"]
    # entity_link ref routing: decision-root bindings point at the DECISION slot
    link = [f for f in signe if f["probe_id"] == "entity_link"][0]
    assert link["refs"]["decision"] == "alternative_bindings[signe_marriage]"
    assert link["refs"]["identity"] is None and link["refs"]["blueprint"] is None
    assert any("represented in the roster as protagonist" in f["message"] for f in signe)
    assert any("no carrier declared for anchor signe_marriage" in f["message"] for f in signe)
    assert any("bears on blueprint.contract.mandatory_ending_tone = bittersweet" in f["message"] for f in signe)
    # direction is decision-level: reported as a common observation
    assert any("authored combination direction" in o["message"] and "kept" in o["message"]
               for o in cons["observations"])
    for alt in ("anders_debt", "marta_pregnancy"):
        fs = per_alt[alt]
        assert any("has no roster slot" in f["message"] for f in fs)
        assert any("bears on blueprint.contract.mandatory_ending_tone = bittersweet" in f["message"] for f in fs)
    # per-combination kept/cut derivation (direction=kept, k=2)
    combos = cons["combinations"]
    by_members = {tuple(c["combination"]): c for c in combos}
    assert by_members[("anders_debt", "marta_pregnancy")]["kept"] == ["anders_debt", "marta_pregnancy"]
    assert by_members[("anders_debt", "marta_pregnancy")]["cut"] == ["signe_marriage"]
    assert by_members[("marta_pregnancy", "signe_marriage")]["cut"] == ["anders_debt"]


def test_case_e_anchored_golden_direction_cut():
    """R2.3: direction=cut -> members CUT, complement KEPT."""
    data = _yaml.safe_load((CASE_E / "salt-of-the-earth-subplot-cut-with-anchors.yaml").read_text(encoding="utf-8"))
    data["combination_direction"] = "cut"
    dec = AuthorDecision.from_dict(data)
    cons = ctx_for(dec, CASE_E).build_report()["consequences"]
    by_members = {tuple(c["combination"]): c for c in cons["combinations"]}
    assert by_members[("anders_debt", "marta_pregnancy")]["cut"] == ["anders_debt", "marta_pregnancy"]
    assert by_members[("anders_debt", "marta_pregnancy")]["kept"] == ["signe_marriage"]
    assert by_members[("marta_pregnancy", "signe_marriage")]["cut"] == ["marta_pregnancy", "signe_marriage"]


def test_direction_absent_membership_unspecified():
    dec = AuthorDecision.from_yaml(CASE_E / "salt-of-the-earth-subplot-cut.yaml")
    cons = ctx_for(dec, CASE_E).build_report()["consequences"]
    assert any("keep/cut interpretation is unspecified" in o["message"] for o in cons["observations"])


def test_question_wording_never_infers_direction():
    """R2.3: the frozen question says "which subplot must be cut" but the
    artifact has no combination_direction -> membership only, no inference,
    no kept/cut keys in combinations."""
    dec = AuthorDecision.from_yaml(CASE_E / "salt-of-the-earth-subplot-cut.yaml")
    cons = ctx_for(dec, CASE_E).build_report()["consequences"]
    assert any("keep/cut interpretation is unspecified" in o["message"] for o in cons["observations"])
    for c in cons["combinations"]:
        assert "kept" not in c and "cut" not in c


def test_case_d_no_op_control():
    """Unanchored fixtures must reproduce the shipped golden expectations
    byte-for-byte (anchors + direction default empty/None -> inert)."""
    for case_dir, decision_name in (
        (CASE_D, "nine-chairs-structure.yaml"),
        (CASE_E, "salt-of-the-earth-subplot-cut.yaml"),
    ):
        dec = AuthorDecision.from_yaml(case_dir / decision_name)
        cons = ctx_for(dec, case_dir).build_report()["consequences"]
        golden = _yaml.safe_load((case_dir / "expected-consequences.yaml").read_text(encoding="utf-8"))
        assert cons == golden


def test_empty_anchor_fields_absence_semantics():
    """Explicit-empty anchor fields are reported per-alternative when bound;
    an unbound anchor reports nothing (never inferred)."""
    data = base_e_dict()
    data["structural_anchors"] = [
        {"anchor_id": "empty_anchor", "participants": [], "carrier_refs": [], "bears_on": []},
    ]
    data["alternative_bindings"] = [
        {"alternative_id": "signe_marriage",
         "references": [{"entity_ref": "decision.structural_anchors[id=empty_anchor]"}]},
    ]
    dec = AuthorDecision.from_dict(data)
    cons = ctx_for(dec, CASE_E).build_report()["consequences"]
    per_alt = {a["alternative_id"]: a["findings"] for a in cons["alternatives"]}
    signe = per_alt["signe_marriage"]
    assert any("no participants declared for anchor empty_anchor" in f["message"] for f in signe)
    assert any("no carrier declared for anchor empty_anchor" in f["message"] for f in signe)
    assert any("bears on nothing declared" in f["message"] for f in signe)
    # unbound alternatives carry NO anchor-derived findings at all
    assert all(f["probe_id"] in ("binding_absence",) for f in per_alt["anders_debt"])


# ---------------------------------------------------------------------------
# Acceptance-record value serialization
# ---------------------------------------------------------------------------

def test_record_value_yaml_safe():
    from auteur.author_decisions.cli import _record_value
    import enum
    from auteur.author_decisions.models import StructuralAnchor

    class _E(enum.Enum):
        v = "kept"

    assert _record_value("bittersweet") == "bittersweet"
    assert _record_value(_E.v) == "kept"
    model = StructuralAnchor(anchor_id="a")
    assert _record_value(model) == model.model_dump()


# ---------------------------------------------------------------------------
# CLI surface
# ---------------------------------------------------------------------------

def test_accept_records_resolved_anchors(tmp_path):
    import shutil
    import subprocess
    import sys
    proj = tmp_path / "p"
    proj.mkdir(parents=True)
    for name in ("story_identity.yaml", "blueprint.yaml"):
        shutil.copy(CASE_E / name, proj / name)
    ad = proj / "author_decisions"
    ad.mkdir()
    shutil.copy(CASE_E / "salt-of-the-earth-subplot-cut-with-anchors.yaml",
                ad / "salt-of-the-earth-subplot-cut.yaml")
    r = subprocess.run(
        [sys.executable, "-m", "auteur.cli", "decision", "accept",
         "salt-of-the-earth-subplot-cut", "--identity", "story_identity.yaml",
         "--blueprint", "blueprint.yaml", "--project", "."],
        cwd=str(proj), capture_output=True, text=True, timeout=120,
    )
    assert r.returncode == 0, r.stderr
    record = _yaml.safe_load((ad / ".acceptance" / "salt-of-the-earth-subplot-cut.yaml").read_text(encoding="utf-8"))
    ra = record["resolved_anchors"]
    assert len(ra) == 3
    by_id = {e["anchor_id"]: e for e in ra}
    assert by_id["signe_marriage"]["bears_on"][0]["ref"] == "blueprint.contract.mandatory_ending_tone"
    assert record["combination_direction"] == "kept"


def test_evaluate_anchored_decision_exit0(tmp_path):
    import shutil
    import subprocess
    import sys
    proj = tmp_path / "p"
    proj.mkdir(parents=True)
    for name in ("story_identity.yaml", "blueprint.yaml"):
        shutil.copy(CASE_E / name, proj / name)
    ad = proj / "author_decisions"
    ad.mkdir()
    shutil.copy(CASE_E / "salt-of-the-earth-subplot-cut-with-anchors.yaml",
                ad / "salt-of-the-earth-subplot-cut.yaml")
    r = subprocess.run(
        [sys.executable, "-m", "auteur.cli", "decision", "evaluate",
         "salt-of-the-earth-subplot-cut", "--identity", "story_identity.yaml",
         "--blueprint", "blueprint.yaml", "--project", "."],
        cwd=str(proj), capture_output=True, text=True, timeout=120,
    )
    assert r.returncode == 0, r.stderr
    assert "bears on blueprint.contract.mandatory_ending_tone = bittersweet" in r.stdout
    assert "kept" in r.stdout
    assert "No verdict is rendered" in r.stdout
