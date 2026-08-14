"""TDD tests for Accepted-Outcome: `chosen` membership field on AuthorDecision
(approved design 2026-08-accepted-outcome.md; mechanism M1, agent-selected under
the standing delegated-authority envelope).

Binding invariants:
- chosen is optional (None = open, status quo) and echo-only;
- members must be declared alternative_ids; cardinality matches the combination
  rule (one_of -> exactly 1; choose_k_of_n -> exactly k);
- combination_direction alone never implies membership (operation != member);
- chosen never mutates canonical state, never drives propagation, never ranks;
- composed consequences are byte-identical with/without chosen;
- acceptance records chosen when present; open decisions unchanged;
- existing artifacts parse/evaluate byte-identical (none carry chosen).
"""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

import yaml as _yaml

from auteur.author_decisions import AuthorDecision, DecisionValidationError

PY = sys.executable
FIXTURES = Path(__file__).parent / "fixtures" / "author_decisions"
CASE = FIXTURES / "case-goal-significance"


def _decision_dict(tmp_path, overrides: dict | None = None) -> dict:
    src = CASE / "absent.yaml"
    data = _yaml.safe_load(src.read_text(encoding="utf-8"))
    data.pop("goal_significance", None)
    if overrides:
        data.update(overrides)
    return data


# ---------------------------------------------------------------------------
# Parse: chosen present
# ---------------------------------------------------------------------------

def test_chosen_one_of_parses():
    data = _decision_dict(None)
    data["chosen"] = ["signe_marriage"]
    dec = AuthorDecision.from_dict(data)
    assert dec.chosen == ["signe_marriage"]


def test_chosen_absent_is_none():
    data = _decision_dict(None)
    dec = AuthorDecision.from_dict(data)
    assert dec.chosen is None


def test_chosen_choose_k_of_n_parses():
    data = _decision_dict(None)
    data["combination"] = {"rule": "choose_k_of_n", "k": 2}
    data["chosen"] = ["marta_pregnancy", "signe_marriage"]
    dec = AuthorDecision.from_dict(data)
    assert dec.chosen == ["marta_pregnancy", "signe_marriage"]


# ---------------------------------------------------------------------------
# Fail closed
# ---------------------------------------------------------------------------

def test_chosen_unknown_member_rejected():
    data = _decision_dict(None)
    data["chosen"] = ["not_an_alternative"]
    try:
        AuthorDecision.from_dict(data)
    except DecisionValidationError:
        pass
    else:
        raise AssertionError("unknown chosen member should be rejected")


def test_chosen_one_of_two_members_rejected():
    data = _decision_dict(None)
    data["chosen"] = ["marta_pregnancy", "signe_marriage"]  # one_of -> exactly 1
    try:
        AuthorDecision.from_dict(data)
    except DecisionValidationError:
        pass
    else:
        raise AssertionError("one_of with 2 chosen should be rejected")


def test_chosen_choose_k_wrong_count_rejected():
    data = _decision_dict(None)
    data["combination"] = {"rule": "choose_k_of_n", "k": 2}
    data["chosen"] = ["marta_pregnancy"]  # k=2 -> exactly 2
    try:
        AuthorDecision.from_dict(data)
    except DecisionValidationError:
        pass
    else:
        raise AssertionError("choose_k_of_n with wrong chosen count should be rejected")


def test_chosen_duplicate_members_rejected():
    data = _decision_dict(None)
    data["combination"] = {"rule": "choose_k_of_n", "k": 2}
    data["chosen"] = ["marta_pregnancy", "marta_pregnancy"]
    try:
        AuthorDecision.from_dict(data)
    except DecisionValidationError:
        pass
    else:
        raise AssertionError("duplicate chosen members should be rejected")


# ---------------------------------------------------------------------------
# Direction does not imply membership; echo-only; central invariant
# ---------------------------------------------------------------------------

def test_direction_alone_does_not_surface_membership(tmp_path):
    """combination_direction=cut with no chosen must not imply any member."""
    proj = tmp_path / "p"
    proj.mkdir(parents=True, exist_ok=True)
    shutil.copy(CASE / "story_identity.yaml", proj / "story_identity.yaml")
    shutil.copy(CASE / "blueprint.yaml", proj / "blueprint.yaml")
    ad = proj / "author_decisions"
    ad.mkdir()
    shutil.copy(CASE / "absent.yaml", ad / "goal-significance-absent.yaml")
    r = subprocess.run(
        [PY, "-m", "auteur.cli", "decision", "view", "goal-significance-absent",
         "--identity", "story_identity.yaml", "--blueprint", "blueprint.yaml",
         "--project", ".", "--json"],
        cwd=str(proj), capture_output=True, text=True, timeout=120)
    assert r.returncode == 0, r.stderr
    out = _yaml.safe_load(r.stdout)
    assert out["authored"].get("chosen") is None


def test_view_surfaces_chosen(tmp_path):
    proj = tmp_path / "p"
    proj.mkdir(parents=True, exist_ok=True)
    shutil.copy(CASE / "story_identity.yaml", proj / "story_identity.yaml")
    shutil.copy(CASE / "blueprint.yaml", proj / "blueprint.yaml")
    ad = proj / "author_decisions"
    ad.mkdir()
    src = CASE / "absent.yaml"
    data = _yaml.safe_load(src.read_text(encoding="utf-8"))
    data["chosen"] = ["signe_marriage"]
    (ad / "goal-significance-absent.yaml").write_text(
        _yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    r = subprocess.run(
        [PY, "-m", "auteur.cli", "decision", "view", "goal-significance-absent",
         "--identity", "story_identity.yaml", "--blueprint", "blueprint.yaml",
         "--project", ".", "--json"],
        cwd=str(proj), capture_output=True, text=True, timeout=120)
    assert r.returncode == 0, r.stderr
    out = _yaml.safe_load(r.stdout)
    assert out["authored"]["chosen"] == ["signe_marriage"]


def test_consequences_byte_identical_with_and_without_chosen(tmp_path):
    """chosen is echo-only: composed consequences identical to the absent artifact."""
    proj = tmp_path / "p"
    proj.mkdir(parents=True, exist_ok=True)
    shutil.copy(CASE / "story_identity.yaml", proj / "story_identity.yaml")
    shutil.copy(CASE / "blueprint.yaml", proj / "blueprint.yaml")
    ad = proj / "author_decisions"
    ad.mkdir()
    base = _yaml.safe_load((CASE / "absent.yaml").read_text(encoding="utf-8"))
    (ad / "goal-significance-absent.yaml").write_text(
        _yaml.safe_dump(base, sort_keys=False), encoding="utf-8")
    with_chosen = dict(base)
    with_chosen["chosen"] = ["signe_marriage"]
    with_chosen["decision_id"] = "goal-significance-absent-chosen"
    (ad / "goal-significance-absent-chosen.yaml").write_text(
        _yaml.safe_dump(with_chosen, sort_keys=False), encoding="utf-8")

    def _eval(dec_id):
        rr = subprocess.run(
            [PY, "-m", "auteur.cli", "decision", "evaluate", dec_id,
             "--identity", "story_identity.yaml", "--blueprint", "blueprint.yaml",
             "--project", ".", "--json"],
            cwd=str(proj), capture_output=True, text=True, timeout=120)
        assert rr.returncode == 0, rr.stderr
        return _yaml.safe_load(rr.stdout)["consequences"]

    assert _eval("goal-significance-absent") == _eval("goal-significance-absent-chosen")
