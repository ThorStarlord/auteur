"""TDD tests for F3: consequence-focused elicitation for genuinely unsettled
cross-goal significance (approved design 2026-08-f3-elicitation.md @ 37bc784;
mechanism M1 — decision elicit, agent-selected under delegated authority).

Binding invariants under test:
- render mode shows the ALREADY-COMPOSED concrete losses (verbatim
  nature_consequence findings grouped per cut) plus the consequence-focused
  question and the three valid outcomes; nothing is inferred from prose;
- render is byte-identical for artifacts differing only in question/criterion
  prose (anti-inference);
- directionless one_of has no composed losses and the render says so honestly;
- record ordered/unranked writes the EXISTING F1 goal_significance field via
  atomic write after fail-closed validation (refs: explicit root, exactly-2
  distinct, participate in this decision's bears_on tradeoff);
- record undecided writes NOTHING (genuinely undecided is a valid outcome,
  never converted to unranked);
- record is refused when goal_significance is already present;
- no manufactured ranking or recommendation anywhere;
- CENTRAL INVARIANT: composed consequences stay byte-identical (minus the F1
  observation) with and without the recorded field.
"""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

import yaml as _yaml

from auteur.author_decisions import AuthorDecision

PY = sys.executable
FIXTURES = Path(__file__).parent / "fixtures" / "author_decisions"
CASE = FIXTURES / "case-goal-significance"
CASE_ONE_OF = FIXTURES / "case-one-of"


def _run(args, cwd: Path):
    return subprocess.run(
        [PY, "-m", "auteur.cli", "decision", "elicit", *args],
        cwd=str(cwd), capture_output=True, text=True, timeout=120,
    )


def _run_eval(decision_id: str, cwd: Path):
    return subprocess.run(
        [PY, "-m", "auteur.cli", "decision", "evaluate", decision_id,
         "--identity", "story_identity.yaml", "--blueprint", "blueprint.yaml",
         "--project", ".", "--json"],
        cwd=str(cwd), capture_output=True, text=True, timeout=120,
    )


def _decision_id(fixture: Path) -> str:
    data = _yaml.safe_load(fixture.read_text(encoding="utf-8"))
    return data["decision_id"]


def _project(tmp_path, decision_name: str, src_case: Path = CASE, extra: list[str] | None = None) -> Path:
    """Copy the case fixtures + one decision artifact into a scratch project,
    renaming the artifact to its decision_id (the CLI resolves
    author_decisions/<decision_id>.yaml). ``extra`` copies additional decision
    artifacts (by fixture name) into the same dir, also renamed by decision_id."""
    proj = tmp_path / "p"
    proj.mkdir(parents=True, exist_ok=True)
    shutil.copy(src_case / "story_identity.yaml", proj / "story_identity.yaml")
    shutil.copy(src_case / "blueprint.yaml", proj / "blueprint.yaml")
    ad = proj / "author_decisions"
    ad.mkdir()
    src = src_case / decision_name
    shutil.copy(src, ad / f"{_decision_id(src)}.yaml")
    for name in extra or []:
        e = src_case / name
        shutil.copy(e, ad / f"{_decision_id(e)}.yaml")
    return proj


def _decision_yaml(proj: Path, decision_name: str) -> dict:
    src = CASE / decision_name
    return _yaml.safe_load((proj / "author_decisions" / f"{_decision_id(src)}.yaml").read_text(encoding="utf-8"))


def _artifact_bytes(proj: Path, decision_name: str) -> bytes:
    src = CASE / decision_name
    return (proj / "author_decisions" / f"{_decision_id(src)}.yaml").read_bytes()


# ---------------------------------------------------------------------------
# Render mode: consequence-focused surface, verbatim composed losses
# ---------------------------------------------------------------------------

def test_render_shows_composed_losses_and_question(tmp_path):
    proj = _project(tmp_path, "absent.yaml")
    r = _run(["goal-significance-absent",
              "--identity", "story_identity.yaml",
              "--blueprint", "blueprint.yaml", "--project", "."], proj)
    assert r.returncode == 0, r.stderr
    assert "If you CUT marta_pregnancy, you remove:" in r.stdout
    assert "cut alternative marta_pregnancy removes its declared sustaining relationship to blueprint.contract.mandatory_ending_tone = bittersweet" in r.stdout
    assert "cut alternative marta_pregnancy removes its declared pressuring relationship to blueprint.identity.pov_type = third_person_limited_single" in r.stdout
    assert "If you CUT signe_marriage, you remove:" in r.stdout
    assert "cut alternative signe_marriage removes its declared sustaining relationship to blueprint.identity.pov_type = third_person_limited_single" in r.stdout
    assert "Which of these concrete losses would you regret more?" in r.stdout
    assert "VALID OUTCOMES" in r.stdout
    # no recommendation, no ranking of alternatives
    assert "recommend" not in r.stdout.lower()


def test_render_is_byte_identical_for_prose_only_variants(tmp_path):
    """Anti-inference: unsettled prose and absent prose render identically."""
    p1 = _project(tmp_path / "a", "unsettled-prose.yaml")
    p2 = _project(tmp_path / "b", "absent.yaml")
    r1 = _run(["goal-significance-unsettled-prose",
               "--identity", "story_identity.yaml",
               "--blueprint", "blueprint.yaml", "--project", "."], p1)
    r2 = _run(["goal-significance-absent",
               "--identity", "story_identity.yaml",
               "--blueprint", "blueprint.yaml", "--project", "."], p2)
    assert r1.returncode == 0 and r2.returncode == 0
    # The authored Question line is echoed verbatim and legitimately differs;
    # everything after it (composed losses + elicitation question + outcomes)
    # must be byte-identical — prose is never parsed into significance.
    marker = "CONCRETE CONSEQUENCES"
    assert r1.stdout[r1.stdout.index(marker):] == r2.stdout[r2.stdout.index(marker):]
    proj = _project(tmp_path, "one-of-directionless.yaml", src_case=CASE_ONE_OF)
    r = _run(["one-of-directionless",
              "--identity", "story_identity.yaml",
              "--blueprint", "blueprint.yaml", "--project", "."], proj)
    assert r.returncode == 0, r.stderr
    assert "If you CUT" not in r.stdout
    assert "no composed consequences" in r.stdout.lower() or "nothing to elicit" in r.stdout.lower()


# ---------------------------------------------------------------------------
# Record mode: explicit author action into the EXISTING F1 field
# ---------------------------------------------------------------------------

def test_record_ordered_writes_f1_field(tmp_path):
    proj = _project(tmp_path, "absent.yaml")
    r = _run(["goal-significance-absent",
              "--identity", "story_identity.yaml",
              "--blueprint", "blueprint.yaml", "--project", ".",
              "--record", "ordered",
              "--refs", "blueprint.contract.mandatory_ending_tone",
              "blueprint.identity.pov_type"], proj)
    assert r.returncode == 0, r.stderr
    data = _decision_yaml(proj, "absent.yaml")
    assert data["goal_significance"]["ordered"] == [
        "blueprint.contract.mandatory_ending_tone",
        "blueprint.identity.pov_type",
    ]
    # reload through the schema: valid F1 field
    dec = AuthorDecision.from_yaml(proj / "author_decisions" / "goal-significance-absent.yaml")
    assert dec.goal_significance.ordered == [
        "blueprint.contract.mandatory_ending_tone",
        "blueprint.identity.pov_type",
    ]


def test_record_unranked_writes_f1_field(tmp_path):
    proj = _project(tmp_path, "absent.yaml")
    r = _run(["goal-significance-absent",
              "--identity", "story_identity.yaml",
              "--blueprint", "blueprint.yaml", "--project", ".",
              "--record", "unranked"], proj)
    assert r.returncode == 0, r.stderr
    data = _decision_yaml(proj, "absent.yaml")
    assert data["goal_significance"] == {"unranked": True}
    dec = AuthorDecision.from_yaml(proj / "author_decisions" / "goal-significance-absent.yaml")
    assert dec.goal_significance.unranked is True


def test_record_undecided_writes_nothing(tmp_path):
    proj = _project(tmp_path, "absent.yaml")
    before = _artifact_bytes(proj, "absent.yaml")
    r = _run(["goal-significance-absent",
              "--identity", "story_identity.yaml",
              "--blueprint", "blueprint.yaml", "--project", ".",
              "--record", "undecided"], proj)
    assert r.returncode == 0, r.stderr
    after = _artifact_bytes(proj, "absent.yaml")
    assert after == before  # genuinely undecided: nothing written
    assert "undecided" in r.stdout.lower()
    data = _decision_yaml(proj, "absent.yaml")
    assert "goal_significance" not in data


# ---------------------------------------------------------------------------
# Record mode: fail closed
# ---------------------------------------------------------------------------

def test_record_ordered_invalid_ref_rejected_file_unchanged(tmp_path):
    proj = _project(tmp_path, "absent.yaml")
    before = _artifact_bytes(proj, "absent.yaml")
    r = _run(["goal-significance-absent",
              "--identity", "story_identity.yaml",
              "--blueprint", "blueprint.yaml", "--project", ".",
              "--record", "ordered",
              "--refs", "blueprint.characters",  # not a bears_on participant
              "blueprint.identity.pov_type"], proj)
    assert r.returncode != 0
    assert _artifact_bytes(proj, "absent.yaml") == before


def test_record_ordered_wrong_ref_count_rejected(tmp_path):
    proj = _project(tmp_path, "absent.yaml")
    r = _run(["goal-significance-absent",
              "--identity", "story_identity.yaml",
              "--blueprint", "blueprint.yaml", "--project", ".",
              "--record", "ordered",
              "--refs", "blueprint.contract.mandatory_ending_tone"], proj)
    assert r.returncode != 0


def test_record_refused_when_significance_present(tmp_path):
    proj = _project(tmp_path, "ordered-ab.yaml")
    before = _artifact_bytes(proj, "ordered-ab.yaml")
    r = _run(["goal-significance-ordered-ab",
              "--identity", "story_identity.yaml",
              "--blueprint", "blueprint.yaml", "--project", ".",
              "--record", "ordered",
              "--refs", "blueprint.identity.pov_type",
              "blueprint.contract.mandatory_ending_tone"], proj)
    assert r.returncode != 0
    assert _artifact_bytes(proj, "ordered-ab.yaml") == before


def test_record_undecided_with_significance_present_is_refused(tmp_path):
    proj = _project(tmp_path, "ordered-ab.yaml")
    before = _artifact_bytes(proj, "ordered-ab.yaml")
    r = _run(["goal-significance-ordered-ab",
              "--identity", "story_identity.yaml",
              "--blueprint", "blueprint.yaml", "--project", ".",
              "--record", "undecided"], proj)
    assert r.returncode != 0
    assert _artifact_bytes(proj, "ordered-ab.yaml") == before


def test_elicit_nonexistent_decision_clean_error(tmp_path):
    proj = _project(tmp_path, "absent.yaml")
    r = _run(["does-not-exist",
              "--identity", "story_identity.yaml",
              "--blueprint", "blueprint.yaml", "--project", "."], proj)
    assert r.returncode != 0
    assert "no author decision artifact" in r.stderr


# ---------------------------------------------------------------------------
# Central invariant: composed consequences byte-identical (minus F1 obs)
# ---------------------------------------------------------------------------

def test_record_ordered_preserves_composed_consequences(tmp_path):
    """After recording ordered via elicit on one artifact, its evaluate report
    is byte-identical (minus the goal_significance observation) to a sibling
    artifact that was never recorded."""
    proj = _project(tmp_path, "absent.yaml", extra=["unsettled-prose.yaml"])
    baseline_id = "goal-significance-unsettled-prose"  # never recorded, same facts
    r = _run(["goal-significance-absent",
              "--identity", "story_identity.yaml",
              "--blueprint", "blueprint.yaml", "--project", ".",
              "--record", "ordered",
              "--refs", "blueprint.contract.mandatory_ending_tone",
              "blueprint.identity.pov_type"], proj)
    assert r.returncode == 0, r.stderr

    eval_r = _run_eval("goal-significance-absent", proj)
    assert eval_r.returncode == 0, eval_r.stderr
    cons = _yaml.safe_load(eval_r.stdout)["consequences"]
    obs = [o for o in cons["observations"] if o.get("probe_id") == "goal_significance"]
    assert len(obs) == 1
    stripped = {**cons, "observations": [
        o for o in cons["observations"] if o.get("probe_id") != "goal_significance"
    ]}

    eval_absent = _run_eval(baseline_id, proj)
    assert eval_absent.returncode == 0, eval_absent.stderr
    absent_cons = _yaml.safe_load(eval_absent.stdout)["consequences"]
    assert stripped == absent_cons
