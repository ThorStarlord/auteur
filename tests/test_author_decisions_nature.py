"""TDD tests for N1: closed relationship-nature vocabulary on anchor bears_on
(approved design 2026-08-relationship-nature-n1.md @ 0af6dd8).

Binding invariants under test:
- nature belongs to the anchor->target relationship, not the anchor globally;
- vocabulary is EXACTLY {sustains, pressures} in this slice;
- nature is explicit author-owned input; hard anti-inference regressions prove
  it is never derived from names/prose/question/direction/target values/roles/
  thread vocabulary;
- no nature authored == "nature not explicitly supplied"; existing bears_on
  relevance unchanged;
- consumer composes nature x kept/cut deterministically (4 pinned forms),
  non-ranking / non-verdict;
- backward compatible: pre-N1 anchored fixture byte-identical; Case D unchanged.
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


def n1_decision():
    return AuthorDecision.from_yaml(CASE_E / "salt-of-the-earth-subplot-cut-with-nature.yaml")


# ---------------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------------

def test_nature_parses_per_relationship():
    dec = n1_decision()
    by_id = {a.anchor_id: a for a in dec.structural_anchors}
    assert by_id["anders_debt"].bears_on[0].nature.value == "pressures"
    assert by_id["marta_pregnancy"].bears_on[0].nature.value == "sustains"
    assert by_id["signe_marriage"].bears_on[0].nature is None  # not supplied


def test_unknown_nature_rejected():
    data = base_e_dict()
    data["structural_anchors"] = [
        {"anchor_id": "a", "bears_on": [
            {"ref": "blueprint.contract.mandatory_ending_tone", "nature": "resolves"}]},
    ]
    with pytest.raises(DecisionValidationError):
        AuthorDecision.from_dict(data)


def test_nature_extra_fields_forbidden():
    data = base_e_dict()
    data["structural_anchors"] = [
        {"anchor_id": "a", "bears_on": [
            {"ref": "blueprint.contract.mandatory_ending_tone", "nature": "sustains", "why": "x"}]},
    ]
    with pytest.raises(DecisionValidationError):
        AuthorDecision.from_dict(data)


def test_duplicate_target_nature_declaration_rejected():
    """Contradictory nature for the same anchor->target is excluded by the
    existing duplicate-bears_on-ref rule."""
    data = base_e_dict()
    data["structural_anchors"] = [
        {"anchor_id": "a", "bears_on": [
            {"ref": "blueprint.contract.mandatory_ending_tone", "nature": "sustains"},
            {"ref": "blueprint.contract.mandatory_ending_tone", "nature": "pressures"},
        ]},
    ]
    with pytest.raises(DecisionValidationError, match="duplicate"):
        AuthorDecision.from_dict(data)


# ---------------------------------------------------------------------------
# Authority: anti-inference regressions
# ---------------------------------------------------------------------------

def test_nature_never_derived_from_anything():
    """No nature authored anywhere -> no nature consequence, regardless of
    names, prose, question, direction, target values, roles, or threads."""
    dec = AuthorDecision.from_yaml(CASE_E / "salt-of-the-earth-subplot-cut-with-anchors.yaml")
    cons = ctx_for(dec, CASE_E).build_report()["consequences"]
    all_messages = [o["message"] for o in cons["observations"]]
    for a in cons["alternatives"]:
        all_messages += [f["message"] for f in a["findings"]]
    assert not any("nature" in m for m in all_messages)
    # the pre-N1 anchored fixture still reports plain bears_on
    assert any("bears on blueprint.contract.mandatory_ending_tone = bittersweet" in m
               and "nature" not in m for m in all_messages)


def test_nature_not_derived_from_direction_or_prose():
    """An artifact with combination_direction + question prose about pressure
    but NO authored nature still yields NO nature consequence."""
    data = base_e_dict()
    data["combination_direction"] = "kept"
    data["structural_anchors"] = [
        {"anchor_id": "a", "bears_on": [
            {"ref": "blueprint.contract.mandatory_ending_tone"}]},
    ]
    dec = AuthorDecision.from_dict(data)
    cons = ctx_for(dec, CASE_E).build_report()["consequences"]
    all_messages = [o["message"] for o in cons["observations"]]
    for a in cons["alternatives"]:
        all_messages += [f["message"] for f in a["findings"]]
    assert not any("nature" in m for m in all_messages)


# ---------------------------------------------------------------------------
# Consumer: nature-labeled bears_on + composed kept/cut (4 pinned forms)
# ---------------------------------------------------------------------------

def test_nature_labeled_bears_on():
    cons = ctx_for(n1_decision(), CASE_E).build_report()["consequences"]
    per_alt = {a["alternative_id"]: a["findings"] for a in cons["alternatives"]}
    assert any("nature: pressures" in f["message"] for f in per_alt["anders_debt"])
    assert any("nature: sustains" in f["message"] for f in per_alt["marta_pregnancy"])
    # signe: no nature authored -> plain bears_on, no nature label
    assert not any("nature" in f["message"] for f in per_alt["signe_marriage"])


def test_composed_consequences_cut_sustains():
    cons = ctx_for(n1_decision(), CASE_E).build_report()["consequences"]
    combos = cons["combinations"]
    by_members = {tuple(c["combination"]): c for c in combos}
    cut_marta = by_members[("anders_debt", "signe_marriage")]
    assert any("cut alternative marta_pregnancy removes its declared sustaining relationship to "
               "blueprint.contract.mandatory_ending_tone = bittersweet" in f["message"]
               for f in cut_marta["findings"])


def test_composed_consequences_cut_pressures():
    cons = ctx_for(n1_decision(), CASE_E).build_report()["consequences"]
    by_members = {tuple(c["combination"]): c for c in cons["combinations"]}
    cut_anders = by_members[("marta_pregnancy", "signe_marriage")]
    assert any("cut alternative anders_debt removes its declared pressuring relationship to "
               "blueprint.contract.mandatory_ending_tone = bittersweet" in f["message"]
               for f in cut_anders["findings"])


def test_composed_consequences_kept_forms():
    cons = ctx_for(n1_decision(), CASE_E).build_report()["consequences"]
    by_members = {tuple(c["combination"]): c for c in cons["combinations"]}
    kept_both = by_members[("anders_debt", "marta_pregnancy")]
    assert any("kept alternative anders_debt preserves its declared pressuring relationship to "
               "blueprint.contract.mandatory_ending_tone = bittersweet" in f["message"]
               for f in kept_both["findings"])
    assert any("kept alternative marta_pregnancy preserves its declared sustaining relationship to "
               "blueprint.contract.mandatory_ending_tone = bittersweet" in f["message"]
               for f in kept_both["findings"])


def test_composed_consequences_direction_cut():
    """direction=cut inverts the composition: combo members are CUT (remove),
    the complement is KEPT (preserve)."""
    data = _yaml.safe_load((CASE_E / "salt-of-the-earth-subplot-cut-with-nature.yaml").read_text(encoding="utf-8"))
    data["combination_direction"] = "cut"
    cons = ctx_for(AuthorDecision.from_dict(data), CASE_E).build_report()["consequences"]
    by_members = {tuple(c["combination"]): c for c in cons["combinations"]}
    cut_both = by_members[("anders_debt", "marta_pregnancy")]
    assert any("cut alternative anders_debt removes its declared pressuring relationship to "
               "blueprint.contract.mandatory_ending_tone = bittersweet" in f["message"]
               for f in cut_both["findings"])
    assert any("cut alternative marta_pregnancy removes its declared sustaining relationship to "
               "blueprint.contract.mandatory_ending_tone = bittersweet" in f["message"]
               for f in cut_both["findings"])
    # kept complement (signe) has no authored nature -> no composed consequence
    assert not any("preserves its declared" in f["message"] for f in cut_both["findings"])


def test_no_direction_no_composition():
    """Nature echoes at relationship level only when direction is absent."""
    data = _yaml.safe_load((CASE_E / "salt-of-the-earth-subplot-cut-with-nature.yaml").read_text(encoding="utf-8"))
    data["combination_direction"] = None
    dec = AuthorDecision.from_dict(data)
    cons = ctx_for(dec, CASE_E).build_report()["consequences"]
    all_messages = [o["message"] for o in cons["observations"]]
    for a in cons["alternatives"]:
        all_messages += [f["message"] for f in a["findings"]]
    assert any("nature: pressures" in m for m in all_messages)  # relationship-level echo
    assert not any("removes its declared" in m or "preserves its declared" in m for m in all_messages)


def test_golden_discriminator_no_verdict():
    """Cut consequences for Anders vs Marta differ deterministically; no
    verdict on which should be cut; signe retains protagonist distinction."""
    cons = ctx_for(n1_decision(), CASE_E).build_report()["consequences"]
    by_members = {tuple(c["combination"]): c for c in cons["combinations"]}
    cut_marta_msgs = [f["message"] for f in by_members[("anders_debt", "signe_marriage")]["findings"]
                      if "declared sustaining" in f["message"]]
    cut_anders_msgs = [f["message"] for f in by_members[("marta_pregnancy", "signe_marriage")]["findings"]
                       if "declared pressuring" in f["message"]]
    assert len(cut_marta_msgs) == 1 and len(cut_anders_msgs) == 1
    assert "sustaining" in cut_marta_msgs[0] and "pressuring" in cut_anders_msgs[0]
    # no verdict: the report contains no recommendation/ranking language
    assert cons["distinguishability"] == "MULTIPLE_AXES"
    all_messages = [o["message"] for o in cons["observations"]]
    for a in cons["alternatives"]:
        all_messages += [f["message"] for f in a["findings"]]
    for c in cons["combinations"]:
        all_messages += [f["message"] for f in c["findings"]]
    assert not any("recommend" in m.lower() for m in all_messages)
    assert not any("therefore cut" in m.lower() for m in all_messages)


# ---------------------------------------------------------------------------
# CLI surface
# ---------------------------------------------------------------------------

def test_evaluate_nature_decision_exit0(tmp_path):
    """Text renderer shows nature labels + composed consequences; closing
    lines still refuse a verdict."""
    import shutil
    import subprocess
    import sys

    proj = tmp_path / "p"
    proj.mkdir(parents=True)
    for name in ("story_identity.yaml", "blueprint.yaml"):
        shutil.copy(CASE_E / name, proj / name)
    ad = proj / "author_decisions"
    ad.mkdir()
    shutil.copy(CASE_E / "salt-of-the-earth-subplot-cut-with-nature.yaml",
                ad / "salt-of-the-earth-subplot-cut.yaml")
    r = subprocess.run(
        [sys.executable, "-m", "auteur.cli", "decision", "evaluate",
         "salt-of-the-earth-subplot-cut", "--identity", "story_identity.yaml",
         "--blueprint", "blueprint.yaml", "--project", "."],
        cwd=str(proj), capture_output=True, text=True, timeout=120,
    )
    assert r.returncode == 0, r.stderr
    assert "nature: pressures" in r.stdout
    assert "cut alternative marta_pregnancy removes its declared sustaining relationship" in r.stdout
    assert "No verdict is rendered" in r.stdout


# ---------------------------------------------------------------------------
# Backward compatibility
# ---------------------------------------------------------------------------

def test_pre_n1_anchored_fixture_unchanged():
    dec = AuthorDecision.from_yaml(CASE_E / "salt-of-the-earth-subplot-cut-with-anchors.yaml")
    cons = ctx_for(dec, CASE_E).build_report()["consequences"]
    # the pre-N1 anchored fixture carries no golden file; assert the report
    # shape is preserved: plain bears_on messages, no nature anywhere
    all_messages = [o["message"] for o in cons["observations"]]
    for a in cons["alternatives"]:
        all_messages += [f["message"] for f in a["findings"]]
    assert not any("nature" in m for m in all_messages)
    assert any("bears on blueprint.contract.mandatory_ending_tone = bittersweet" in m for m in all_messages)


def test_case_d_no_op_control():
    for case_dir, decision_name in (
        (CASE_D, "nine-chairs-structure.yaml"),
        (CASE_E, "salt-of-the-earth-subplot-cut.yaml"),
    ):
        dec = AuthorDecision.from_yaml(case_dir / decision_name)
        cons = ctx_for(dec, case_dir).build_report()["consequences"]
        golden = _yaml.safe_load((case_dir / "expected-consequences.yaml").read_text(encoding="utf-8"))
        assert cons == golden
