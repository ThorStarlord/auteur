"""TDD tests for F3: referent-level thematic contribution with explicit
operative-state authority (approved design hardening @ 0623b48).

Binding invariants (hardened):
- operative is an explicit canonical current-state fact, NEVER derived from
  chosen/combination_direction, NEVER a second statement of the outcome;
- default operative = None (unset = not explicitly declared, honest
  non-assertion); finding fires ONLY on explicit False;
- contribution text is opaque; Auteur reasons about presence/absence only;
- decision contribution --add / --operative yes|no|unset are explicit author acts;
- structural_referent.contribution_non_operative (INFO, REPRESENTATION) composes
  non-operative + declared contribution into "contribution absent from the
  operative story";
- no thread aggregator / theme.* changes; thread stays declared and untouched;
- F1 stays decision-local; chosen alone produces no contribution-state mutation;
- no prose/name/fuzzy/LLM inference; backward compatible; restoration possible.
"""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

import yaml as _yaml

from auteur.blueprint import StoryBlueprint
from auteur.structure.analyzer import analyze_structure

PY = sys.executable
FIXTURES = Path(__file__).parent / "fixtures" / "author_decisions"
CASE = FIXTURES / "case-goal-significance"


def _project(tmp_path) -> Path:
    proj = tmp_path / "p"
    proj.mkdir(parents=True, exist_ok=True)
    shutil.copy(CASE / "story_identity.yaml", proj / "story_identity.yaml")
    shutil.copy(CASE / "blueprint.yaml", proj / "blueprint.yaml")
    ad = proj / "author_decisions"
    ad.mkdir()
    data = _yaml.safe_load((CASE / "absent.yaml").read_text(encoding="utf-8"))
    data.pop("goal_significance", None)
    (ad / "goal-significance-absent.yaml").write_text(
        _yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    return proj


def _promote(proj: Path, anchor: str = "signe_marriage"):
    return subprocess.run(
        [PY, "-m", "auteur.cli", "decision", "promote", "goal-significance-absent",
         "--anchor", anchor, "--identity", "story_identity.yaml",
         "--blueprint", "blueprint.yaml", "--project", "."],
        cwd=str(proj), capture_output=True, text=True, timeout=120)


def _contribution(proj: Path, *args: str):
    return subprocess.run(
        [PY, "-m", "auteur.cli", "decision", "contribution",
         "goal-significance-absent", *args,
         "--identity", "story_identity.yaml",
         "--blueprint", "blueprint.yaml", "--project", "."],
        cwd=str(proj), capture_output=True, text=True, timeout=120)


def _blueprint(proj: Path) -> StoryBlueprint:
    return StoryBlueprint.from_yaml(proj / "blueprint.yaml")


def _referent(proj_or_bp, referent_id: str = "signe_marriage"):
    bp = proj_or_bp if isinstance(proj_or_bp, StoryBlueprint) else _blueprint(proj_or_bp)
    return next((r for r in bp.structural_referents if r.referent_id == referent_id),
                None)


def _loss_findings(blueprint: StoryBlueprint):
    return [d for d in analyze_structure(blueprint)
            if d.rule == "structural_referent.contribution_non_operative"]


CONTRIBUTION = ("supplies the relational counterweight that keeps the "
                "bittersweet ending emotionally credible")


def _promoted_with_contribution(proj: Path, *, operative_args=None):
    r = _promote(proj)
    assert r.returncode == 0, r.stderr
    r = _contribution(proj, "--add", CONTRIBUTION)
    assert r.returncode == 0, r.stderr
    if operative_args is not None:
        r = _contribution(proj, "--operative", operative_args)
        assert r.returncode == 0, r.stderr
    return _blueprint(proj)


# ---------------------------------------------------------------------------
# Control A: schema + default state
# ---------------------------------------------------------------------------

def test_referent_defaults_unset_operative_and_no_contributions(tmp_path):
    """Existing promoted referent: thematic_contributions=[] and
    operative=None (unset) — backward compatible, no assertion."""
    proj = _project(tmp_path)
    r = _promote(proj)
    assert r.returncode == 0, r.stderr
    ref = _referent(proj)
    assert ref.thematic_contributions == []
    assert ref.operative is None
    assert ref.contribution_provenance is None


def test_blueprint_roundtrip_preserves_contributions_and_operative(tmp_path):
    proj = _project(tmp_path)
    _promote(proj)
    _contribution(proj, "--add", CONTRIBUTION)
    _contribution(proj, "--operative", "no")
    bp = _blueprint(proj)
    ref = _referent(bp, "signe_marriage")
    assert ref.thematic_contributions == [CONTRIBUTION]
    assert ref.operative is False
    # fresh load from disk
    bp2 = StoryBlueprint.from_yaml(proj / "blueprint.yaml")
    ref2 = _referent(bp2, "signe_marriage")
    assert ref2.thematic_contributions == [CONTRIBUTION]
    assert ref2.operative is False


# ---------------------------------------------------------------------------
# Controls 1-3: operative -> no finding; non-operative -> finding; None -> none
# ---------------------------------------------------------------------------

def test_operative_true_no_loss_finding(tmp_path):
    proj = _project(tmp_path)
    bp = _promoted_with_contribution(proj, operative_args="yes")
    assert _loss_findings(bp) == []


def test_operative_false_emits_loss_finding(tmp_path):
    proj = _project(tmp_path)
    bp = _promoted_with_contribution(proj, operative_args="no")
    findings = _loss_findings(bp)
    assert len(findings) == 1
    f = findings[0]
    assert f.severity.value == "info"
    assert f.layer.value == "representation"
    assert "signe_marriage" in f.message
    assert "absent from the operative story" in f.message
    assert "1" in f.message  # contribution count
    assert f.evidence  # referent_id / operative: false / contribution_count


def test_operative_unset_no_finding_and_no_assertion(tmp_path):
    """operative=None (unset): NO loss finding — Auteur asserts nothing about
    current operation (honest non-assertion)."""
    proj = _project(tmp_path)
    bp = _promoted_with_contribution(proj)  # no --operative call -> None
    assert bp is not None
    ref = _referent(bp, "signe_marriage")
    assert ref.operative is None
    assert _loss_findings(bp) == []


def test_operative_unset_via_flag_no_finding(tmp_path):
    proj = _project(tmp_path)
    bp = _promoted_with_contribution(proj, operative_args="unset")
    assert _loss_findings(bp) == []


# ---------------------------------------------------------------------------
# Control 4: no contribution -> no invented finding (even if non-operative)
# ---------------------------------------------------------------------------

def test_no_contribution_no_finding_even_non_operative(tmp_path):
    proj = _project(tmp_path)
    r = _promote(proj)
    assert r.returncode == 0, r.stderr
    r = _contribution(proj, "--operative", "no")
    assert r.returncode == 0, r.stderr
    bp = _blueprint(proj)
    ref = _referent(bp, "signe_marriage")
    assert ref.operative is False
    assert ref.thematic_contributions == []
    assert _loss_findings(bp) == []


# ---------------------------------------------------------------------------
# Control 5: two referents -> one non-operative does not erase the other
# ---------------------------------------------------------------------------

def test_two_referents_one_non_operative_keeps_other(tmp_path):
    proj = _project(tmp_path)
    for anchor, contrib in (("signe_marriage", CONTRIBUTION),
                            ("marta_pregnancy", "carries the land-debt stakes")):
        r = _promote(proj, anchor=anchor)
        assert r.returncode == 0, r.stderr
        r = _contribution(proj, "--referent", anchor, "--add", contrib)
        assert r.returncode == 0, r.stderr
    r = _contribution(proj, "--referent", "signe_marriage", "--operative", "no")
    assert r.returncode == 0, r.stderr
    bp = _blueprint(proj)
    findings = _loss_findings(bp)
    assert len(findings) == 1
    assert "signe_marriage" in findings[0].message
    # marta still operative
    marta = _referent(bp, "marta_pregnancy")
    assert marta.operative is None
    assert marta.thematic_contributions == ["carries the land-debt stakes"]


# ---------------------------------------------------------------------------
# Control 6: pressures relationship coexists with a valuable contribution
# ---------------------------------------------------------------------------

def test_pressures_nature_and_contribution_coexist(tmp_path):
    """The anchored signe_marriage already declares bears_on pressures the
    ending (fixture). Adding a contribution must preserve both."""
    proj = _project(tmp_path)
    bp = _promoted_with_contribution(proj, operative_args="no")
    ref = _referent(bp, "signe_marriage")
    assert ref.thematic_contributions == [CONTRIBUTION]
    assert ref.operative is False
    # the decision anchor's bears_on/nature are untouched (decision-local)
    from auteur.author_decisions.models import AuthorDecision
    dec = AuthorDecision.from_yaml(proj / "author_decisions" /
                                   "goal-significance-absent.yaml")
    anchor = next(a for a in dec.structural_anchors
                  if a.anchor_id == "signe_marriage")
    natures = {b.relationship.value for b in anchor.bears_on}
    assert "bears_on" in natures
    # promoted referent does NOT carry bears_on (durable subset unchanged)
    assert not hasattr(ref, "bears_on")


# ---------------------------------------------------------------------------
# Control 7: thread remains declared and untouched
# ---------------------------------------------------------------------------

def test_thread_story_engine_untouched(tmp_path):
    proj = _project(tmp_path)
    before = _yaml.safe_load((proj / "blueprint.yaml").read_text(encoding="utf-8"))
    _promoted_with_contribution(proj, operative_args="no")
    after = _yaml.safe_load((proj / "blueprint.yaml").read_text(encoding="utf-8"))
    assert after["story_engine"] == before["story_engine"]
    assert after["identity"] == before["identity"]
    assert after["contract"] == before["contract"]


# ---------------------------------------------------------------------------
# Control 8: F1 stays decision-local
# ---------------------------------------------------------------------------

def test_f1_significance_stays_decision_local(tmp_path):
    proj = _project(tmp_path)
    _promoted_with_contribution(proj, operative_args="no")
    dec_data = _yaml.safe_load(
        (proj / "author_decisions" / "goal-significance-absent.yaml")
        .read_text(encoding="utf-8"))
    assert "goal_significance" not in dec_data  # absent fixture: no F1 authored
    bp = _blueprint(proj)
    assert not hasattr(bp, "goal_significance")


# ---------------------------------------------------------------------------
# Control 9: chosen alone produces no contribution-state mutation
# ---------------------------------------------------------------------------

def test_chosen_alone_never_mutates_contribution_state(tmp_path):
    """A decision artifact with chosen=[] + combination_direction=cut, when
    promoted, must NOT set operative or contributions automatically."""
    proj = _project(tmp_path)
    data = _yaml.safe_load((CASE / "absent.yaml").read_text(encoding="utf-8"))
    data["chosen"] = ["signe_marriage"]
    (proj / "author_decisions" / "goal-significance-absent.yaml").write_text(
        _yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    r = _promote(proj)
    assert r.returncode == 0, r.stderr
    ref = _referent(proj)
    assert ref.operative is None
    assert ref.thematic_contributions == []
    # and the promote output does not claim an operative change
    assert "operative" not in r.stdout.lower()


# ---------------------------------------------------------------------------
# Control 10: no prose inference — two different opaque texts behave identically
# ---------------------------------------------------------------------------

def test_opaque_texts_never_parsed(tmp_path):
    proj = _project(tmp_path)
    text_a = "completely arbitrary prose number one"
    text_b = "completely arbitrary prose number two"
    _promote(proj)
    _contribution(proj, "--add", text_a)
    _contribution(proj, "--add", text_b)
    _contribution(proj, "--operative", "no")
    bp = _blueprint(proj)
    findings = _loss_findings(bp)
    assert len(findings) == 1
    assert "2" in findings[0].message  # 2 contributions declared
    # the prose itself never appears in the finding (presence/absence only)
    assert text_a not in findings[0].message
    assert text_b not in findings[0].message


# ---------------------------------------------------------------------------
# Control 11: backward compatible — old blueprint with no referents loads
# ---------------------------------------------------------------------------

def test_old_blueprint_without_referents_backward_compatible(tmp_path):
    proj = _project(tmp_path)
    bp = _blueprint(proj)  # fixture blueprint has no structural_referents
    assert bp.structural_referents == []
    assert _loss_findings(bp) == []


# ---------------------------------------------------------------------------
# Control 12: restoration representable
# ---------------------------------------------------------------------------

def test_restoration_operative_yes_removes_finding(tmp_path):
    proj = _project(tmp_path)
    _promote(proj)
    _contribution(proj, "--add", CONTRIBUTION)
    _contribution(proj, "--operative", "no")
    bp = _blueprint(proj)
    assert len(_loss_findings(bp)) == 1
    r = _contribution(proj, "--operative", "yes")
    assert r.returncode == 0, r.stderr
    bp2 = _blueprint(proj)
    assert _loss_findings(bp2) == []
    ref = _referent(bp2)
    assert ref.operative is True


# ---------------------------------------------------------------------------
# Action fail-closed semantics
# ---------------------------------------------------------------------------

def test_contribution_unknown_referent_fails_closed(tmp_path):
    proj = _project(tmp_path)
    r = _promote(proj)
    assert r.returncode == 0, r.stderr
    r = _contribution(proj, "--referent", "does_not_exist", "--add", CONTRIBUTION)
    assert r.returncode == 1
    assert "does_not_exist" in r.stderr


def test_contribution_empty_text_fails_closed(tmp_path):
    proj = _project(tmp_path)
    _promote(proj)
    r = _contribution(proj, "--add", "")
    assert r.returncode == 1


def test_contribution_unknown_decision_fails_closed(tmp_path):
    proj = _project(tmp_path)
    r = subprocess.run(
        [PY, "-m", "auteur.cli", "decision", "contribution", "no-such-decision",
         "--referent", "x", "--add", CONTRIBUTION,
         "--identity", "story_identity.yaml",
         "--blueprint", "blueprint.yaml", "--project", "."],
        cwd=str(proj), capture_output=True, text=True, timeout=120)
    assert r.returncode == 1


def test_contribution_add_idempotent_on_exact_duplicate(tmp_path):
    proj = _project(tmp_path)
    _promote(proj)
    _contribution(proj, "--add", CONTRIBUTION)
    r = _contribution(proj, "--add", CONTRIBUTION)
    assert r.returncode == 0, r.stderr
    ref = _referent(proj)
    assert ref.thematic_contributions == [CONTRIBUTION]  # no duplicate


def test_contribution_provenance_recorded(tmp_path):
    proj = _project(tmp_path)
    _promote(proj)
    _contribution(proj, "--add", CONTRIBUTION)
    _contribution(proj, "--operative", "no")
    ref = _referent(proj)
    assert ref.contribution_provenance is not None
    assert ref.contribution_provenance.declared_in_decision_id == \
        "goal-significance-absent"
    assert ref.contribution_provenance.declared_at  # ISO timestamp


def test_contribution_requires_mode_flag(tmp_path):
    proj = _project(tmp_path)
    _promote(proj)
    r = _contribution(proj)  # no --add / --operative
    assert r.returncode == 1
