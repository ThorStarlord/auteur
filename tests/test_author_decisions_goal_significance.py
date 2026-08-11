"""TDD tests for F1: decision-scoped authored goal significance (approved
design 2026-08-cross-goal-significance-f1.md @ 9ec4ef0).

Binding invariants under test:
- goal_significance is optional and decision-scoped only;
- ordered contains EXACTLY two distinct participating goal refs, most
  significant first — purely author-authored relative significance;
- Auteur never generates, infers, extends, scores, completes, or applies the
  ordering to rank alternatives;
- unranked: true = affirmative intentional non-precedence — never
  unknown/undecided/missing;
- genuinely unsettled significance is NOT representable by F1 (absent field);
- absent significance preserves existing behavior;
- every ref must use the explicit-root grammar, be unique, participate in this
  decision's represented tradeoff (a bears_on ref), and resolve via the shared
  anchor/target resolution; stale/unknown/duplicate/unrelated/3+ fail closed;
- CENTRAL INVARIANT: deterministic consequence content is byte-identical with
  and without goal_significance; F1 adds only the provenance-labeled
  observation through the probe/view surface.
"""
from __future__ import annotations

import shutil
import subprocess
import sys
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

PY = sys.executable
FIXTURES = Path(__file__).parent / "fixtures" / "author_decisions"
CASE = FIXTURES / "case-goal-significance"
CASE_ONE_OF = FIXTURES / "case-one-of"
CASE_D = FIXTURES / "case-d"
CASE_E = FIXTURES / "case-e"


def load_identity(case_dir: Path):
    return StoryIdentity.from_yaml(case_dir / "story_identity.yaml")


def load_blueprint(case_dir: Path):
    return StoryBlueprint.from_yaml(case_dir / "blueprint.yaml")


def ctx_for(decision, case_dir: Path):
    return build_decision_context(decision, load_identity(case_dir), load_blueprint(case_dir))


def decision_for(name: str):
    return AuthorDecision.from_yaml(CASE / name)


def report_for(name: str):
    return ctx_for(decision_for(name), CASE).build_report()["consequences"]


def without_goal_significance_obs(cons):
    """Consequences with the goal_significance observation removed (probe only)."""
    return {
        **cons,
        "observations": [o for o in cons["observations"]
                         if o.get("probe_id") != "goal_significance"],
    }


def has_goal_significance_obs(cons):
    return any(o.get("probe_id") == "goal_significance" for o in cons["observations"])


# ---------------------------------------------------------------------------
# Schema: parse
# ---------------------------------------------------------------------------

def test_ordered_parses():
    dec = decision_for("ordered-ab.yaml")
    assert dec.goal_significance is not None
    assert dec.goal_significance.ordered == [
        "blueprint.contract.mandatory_ending_tone",
        "blueprint.identity.pov_type",
    ]
    assert dec.goal_significance.unranked is None


def test_ordered_reversed_parses():
    dec = decision_for("ordered-ba.yaml")
    assert dec.goal_significance.ordered == [
        "blueprint.identity.pov_type",
        "blueprint.contract.mandatory_ending_tone",
    ]


def test_unranked_parses():
    dec = decision_for("unranked.yaml")
    assert dec.goal_significance.unranked is True
    assert dec.goal_significance.ordered is None


def test_absent_is_none():
    for name in ("absent.yaml", "unsettled-prose.yaml", "misleading-prose.yaml"):
        assert decision_for(name).goal_significance is None


# ---------------------------------------------------------------------------
# Schema: fail closed
# ---------------------------------------------------------------------------

def base_dict():
    return _yaml.safe_load((CASE / "absent.yaml").read_text(encoding="utf-8"))


def test_both_ordered_and_unranked_rejected():
    data = base_dict()
    data["goal_significance"] = {
        "ordered": ["blueprint.contract.mandatory_ending_tone", "blueprint.identity.pov_type"],
        "unranked": True,
    }
    with pytest.raises(DecisionValidationError):
        AuthorDecision.from_dict(data)


def test_unranked_false_rejected():
    data = base_dict()
    data["goal_significance"] = {"unranked": False}
    with pytest.raises(DecisionValidationError):
        AuthorDecision.from_dict(data)


def test_ordered_single_ref_rejected():
    data = base_dict()
    data["goal_significance"] = {"ordered": ["blueprint.contract.mandatory_ending_tone"]}
    with pytest.raises(DecisionValidationError):
        AuthorDecision.from_dict(data)


def test_ordered_three_refs_rejected():
    data = base_dict()
    data["goal_significance"] = {"ordered": [
        "blueprint.contract.mandatory_ending_tone",
        "blueprint.identity.pov_type",
        "blueprint.structure.act_structure",
    ]}
    with pytest.raises(DecisionValidationError):
        AuthorDecision.from_dict(data)


def test_ordered_duplicate_refs_rejected():
    data = base_dict()
    data["goal_significance"] = {"ordered": [
        "blueprint.contract.mandatory_ending_tone",
        "blueprint.contract.mandatory_ending_tone",
    ]}
    with pytest.raises(DecisionValidationError):
        AuthorDecision.from_dict(data)


def test_ref_without_explicit_root_rejected():
    data = base_dict()
    data["goal_significance"] = {"ordered": [
        "contract.mandatory_ending_tone",
        "blueprint.identity.pov_type",
    ]}
    with pytest.raises(DecisionValidationError):
        AuthorDecision.from_dict(data)


def test_unrelated_goal_ref_rejected():
    """A ref not participating in this decision's bears_on tradeoff is rejected."""
    data = base_dict()
    data["goal_significance"] = {"ordered": [
        "blueprint.characters",
        "blueprint.identity.pov_type",
    ]}
    with pytest.raises(DecisionValidationError):
        AuthorDecision.from_dict(data)


def test_stale_ref_fails_closed_at_context_build():
    """A goal_significance ref that passes schema (it is a bears_on ref) but
    does not resolve in the current story must fail closed at context build.
    Resolution runs through the shared anchor/bears_on machinery, so a stale
    ref surfaces as DecisionValidationError there - the F1 declaration never
    reaches the report."""
    data = base_dict()
    stale = "blueprint.contract.nonexistent_goal"
    data["structural_anchors"][0]["bears_on"].append(
        {"ref": stale, "relationship": "bears_on", "nature": "sustains"}
    )
    data["goal_significance"] = {"ordered": [
        "blueprint.contract.mandatory_ending_tone", stale,
    ]}
    dec = AuthorDecision.from_dict(data)  # schema: both refs are bears_on refs
    with pytest.raises(DecisionValidationError):
        ctx_for(dec, CASE)


def test_numeric_weights_rejected():
    data = base_dict()
    data["goal_significance"] = {
        "weights": {"blueprint.contract.mandatory_ending_tone": 0.8},
    }
    with pytest.raises(DecisionValidationError):
        AuthorDecision.from_dict(data)


def test_unknown_field_rejected():
    data = base_dict()
    data["goal_significance"] = {
        "ordered": ["blueprint.contract.mandatory_ending_tone", "blueprint.identity.pov_type"],
        "why": "because",
    }
    with pytest.raises(DecisionValidationError):
        AuthorDecision.from_dict(data)


# ---------------------------------------------------------------------------
# Probe: provenance-labeled echo, never use
# ---------------------------------------------------------------------------

def test_ordered_observation_message():
    cons = report_for("ordered-ab.yaml")
    obs = next(o for o in cons["observations"] if o.get("probe_id") == "goal_significance")
    assert obs["message"] == (
        "authored goal significance (this decision): "
        "blueprint.contract.mandatory_ending_tone > blueprint.identity.pov_type"
    )
    assert obs["refs"]["decision"] == "goal_significance"
    assert obs["scope"] == "common"
    assert obs["discriminates"] is False


def test_ordered_reversed_observation_message():
    cons = report_for("ordered-ba.yaml")
    obs = next(o for o in cons["observations"] if o.get("probe_id") == "goal_significance")
    assert obs["message"] == (
        "authored goal significance (this decision): "
        "blueprint.identity.pov_type > blueprint.contract.mandatory_ending_tone"
    )


def test_unranked_observation_message():
    cons = report_for("unranked.yaml")
    obs = next(o for o in cons["observations"] if o.get("probe_id") == "goal_significance")
    assert obs["message"] == (
        "authored goal significance (this decision): unranked — "
        "no goal has authored precedence; non-ranking is intentional"
    )


def test_no_observation_when_absent_or_prose_only():
    for name in ("absent.yaml", "unsettled-prose.yaml", "misleading-prose.yaml"):
        assert not has_goal_significance_obs(report_for(name)), name


# ---------------------------------------------------------------------------
# CENTRAL INVARIANT: consequences byte-identical with/without goal_significance
# ---------------------------------------------------------------------------

def test_ordered_consequences_byte_identical_to_absent():
    with_gs = report_for("ordered-ab.yaml")
    assert without_goal_significance_obs(with_gs) == report_for("absent.yaml")


def test_unranked_consequences_byte_identical_to_absent():
    with_gs = report_for("unranked.yaml")
    assert without_goal_significance_obs(with_gs) == report_for("absent.yaml")


def test_ordered_reversed_consequences_byte_identical_to_absent():
    with_gs = report_for("ordered-ba.yaml")
    assert without_goal_significance_obs(with_gs) == report_for("absent.yaml")


def test_no_consequence_branches_on_significance():
    """The goal_significance observation is the ONLY delta."""
    for name in ("ordered-ab.yaml", "ordered-ba.yaml", "unranked.yaml"):
        with_gs = report_for(name)
        absent = report_for("absent.yaml")
        assert set(with_gs) == set(absent)
        for key in ("alternatives", "combinations", "distinguishability"):
            assert with_gs[key] == absent[key], (name, key)


# ---------------------------------------------------------------------------
# Goldens + backward compatibility
# ---------------------------------------------------------------------------

def test_ordered_golden():
    cons = report_for("ordered-ab.yaml")
    golden = _yaml.safe_load((CASE / "expected-consequences-ordered.yaml").read_text(encoding="utf-8"))
    assert cons == golden


def test_unranked_golden():
    cons = report_for("unranked.yaml")
    golden = _yaml.safe_load((CASE / "expected-consequences-unranked.yaml").read_text(encoding="utf-8"))
    assert cons == golden


def test_existing_goldens_byte_identical():
    existing = [
        (CASE_D, "nine-chairs-structure.yaml", "expected-consequences.yaml"),
        (CASE_E, "salt-of-the-earth-subplot-cut.yaml", "expected-consequences.yaml"),
        (CASE_ONE_OF, "one-of-kept.yaml", "expected-consequences-kept.yaml"),
        (CASE_ONE_OF, "one-of-cut.yaml", "expected-consequences-cut.yaml"),
    ]
    for case_dir, decision_name, golden_name in existing:
        dec = AuthorDecision.from_yaml(case_dir / decision_name)
        cons = ctx_for(dec, case_dir).build_report()["consequences"]
        golden = _yaml.safe_load((case_dir / golden_name).read_text(encoding="utf-8"))
        assert cons == golden, decision_name


# ---------------------------------------------------------------------------
# CLI view surface
# ---------------------------------------------------------------------------

def test_view_shows_authored_goal_significance(tmp_path):
    proj = tmp_path / "p"
    proj.mkdir()
    shutil.copy(CASE / "story_identity.yaml", proj / "story_identity.yaml")
    shutil.copy(CASE / "blueprint.yaml", proj / "blueprint.yaml")
    ad = proj / "author_decisions"
    ad.mkdir()
    shutil.copy(CASE / "ordered-ab.yaml", ad / "goal-significance-ordered-ab.yaml")
    r = subprocess.run(
        [PY, "-m", "auteur.cli", "decision", "view", "goal-significance-ordered-ab",
         "--identity", "story_identity.yaml", "--blueprint", "blueprint.yaml", "--project", "."],
        cwd=str(proj), capture_output=True, text=True, timeout=120)
    assert r.returncode == 0, r.stderr
    assert "Goal significance (authored, decision-scoped)" in r.stdout
    assert "blueprint.contract.mandatory_ending_tone" in r.stdout
