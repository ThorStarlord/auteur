r"""TDD tests for the F3 polish pass (standing delegated authority, 2026-08-12;
post-merge observations recorded @ 914e87c on discovery/f3-elicitation).

Scope (reuse/extension of shipped F3 behavior - no escalation triggers):
1. the VALID OUTCOMES render must not emit a literal `\` line-continuation;
2. `--refs` given with `--record unranked/undecided` must warn (stderr), not
   silently ignore — behavior of the record itself is unchanged.

Unchanged invariants (regression): render still verbatim-composed; record
ordered/unranked/undecided semantics unchanged; fail-closed + refusal paths
unchanged.
"""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

import yaml as _yaml

PY = sys.executable
FIXTURES = Path(__file__).parent / "fixtures" / "author_decisions"
CASE = FIXTURES / "case-goal-significance"


def _run(args, cwd: Path):
    return subprocess.run(
        [PY, "-m", "auteur.cli", "decision", "elicit", *args],
        cwd=str(cwd), capture_output=True, text=True, timeout=120,
    )


def _project(tmp_path, decision_name: str) -> Path:
    proj = tmp_path / "p"
    proj.mkdir(parents=True, exist_ok=True)
    shutil.copy(CASE / "story_identity.yaml", proj / "story_identity.yaml")
    shutil.copy(CASE / "blueprint.yaml", proj / "blueprint.yaml")
    ad = proj / "author_decisions"
    ad.mkdir()
    shutil.copy(CASE / decision_name, ad / "goal-significance-absent.yaml")
    return proj


# ---------------------------------------------------------------------------
# Fix 1: VALID OUTCOMES must not render a literal backslash
# ---------------------------------------------------------------------------

def test_valid_outcomes_render_has_no_literal_backslash(tmp_path):
    proj = _project(tmp_path, "absent.yaml")
    r = _run(["goal-significance-absent",
              "--identity", "story_identity.yaml",
              "--blueprint", "blueprint.yaml", "--project", "."], proj)
    assert r.returncode == 0, r.stderr
    block = r.stdout[r.stdout.index("VALID OUTCOMES"):]
    assert "\\" not in block
    # the command text is still present and unambiguous
    assert "--record ordered <REF1> <REF2>" in block
    assert "--record unranked" in block
    assert "--record undecided" in block


# ---------------------------------------------------------------------------
# Fix 2: --refs with --record unranked/undecided warns instead of silent ignore
# ---------------------------------------------------------------------------

def test_refs_with_unranked_warns_and_records(tmp_path):
    proj = _project(tmp_path, "absent.yaml")
    r = _run(["goal-significance-absent",
              "--identity", "story_identity.yaml",
              "--blueprint", "blueprint.yaml", "--project", ".",
              "--record", "unranked",
              "--refs", "blueprint.contract.mandatory_ending_tone",
              "blueprint.identity.pov_type"], proj)
    assert r.returncode == 0, r.stderr
    assert "--refs" in r.stderr.lower()  # warning emitted
    data = _yaml.safe_load(
        (proj / "author_decisions" / "goal-significance-absent.yaml").read_text(encoding="utf-8"))
    assert data["goal_significance"] == {"unranked": True}  # record unaffected


def test_refs_with_undecided_warns_and_writes_nothing(tmp_path):
    proj = _project(tmp_path, "absent.yaml")
    before = (proj / "author_decisions" / "goal-significance-absent.yaml").read_bytes()
    r = _run(["goal-significance-absent",
              "--identity", "story_identity.yaml",
              "--blueprint", "blueprint.yaml", "--project", ".",
              "--record", "undecided",
              "--refs", "blueprint.contract.mandatory_ending_tone",
              "blueprint.identity.pov_type"], proj)
    assert r.returncode == 0, r.stderr
    assert "--refs" in r.stderr.lower()
    after = (proj / "author_decisions" / "goal-significance-absent.yaml").read_bytes()
    assert after == before


def test_refs_with_ordered_no_warning(tmp_path):
    proj = _project(tmp_path, "absent.yaml")
    r = _run(["goal-significance-absent",
              "--identity", "story_identity.yaml",
              "--blueprint", "blueprint.yaml", "--project", ".",
              "--record", "ordered",
              "--refs", "blueprint.contract.mandatory_ending_tone",
              "blueprint.identity.pov_type"], proj)
    assert r.returncode == 0, r.stderr
    assert "--refs" not in r.stderr.lower()
    data = _yaml.safe_load(
        (proj / "author_decisions" / "goal-significance-absent.yaml").read_text(encoding="utf-8"))
    assert data["goal_significance"]["ordered"] == [
        "blueprint.contract.mandatory_ending_tone",
        "blueprint.identity.pov_type",
    ]
