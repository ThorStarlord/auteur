"""TDD tests for A2: surface F3 elicitation availability in `decision view`
(approved design 2026-08-a2-surface-elicitation.md @ 94b09f8; mechanism M1,
agent-selected under the standing delegated-authority envelope).

Binding invariants under test:
- eligibility state is deterministic from the resolved report + F1 field:
  unsettled (no goal_significance + composed combinations) /
  no_composed_consequences (no goal_significance + no combinations) /
  declared (goal_significance present);
- text: unsettled shows the exact `decision elicit` invocation; declared shows
  no extra hint; no_composed_consequences shows the honest note;
- JSON: state from the closed set; command present iff unsettled;
- no identity/blueprint -> no elicitation section (authored-only unchanged);
- anti-inference: unsettled prose vs absent render identical hints;
- the hint never ranks, recommends, or infers from prose.
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
CASE_ONE_OF = FIXTURES / "case-one-of"


def _run(args, cwd: Path):
    return subprocess.run(
        [PY, "-m", "auteur.cli", "decision", *args],
        cwd=str(cwd), capture_output=True, text=True, timeout=120,
    )


def _project(tmp_path, decision_name: str, src_case: Path = CASE) -> Path:
    proj = tmp_path / "p"
    proj.mkdir(parents=True, exist_ok=True)
    shutil.copy(src_case / "story_identity.yaml", proj / "story_identity.yaml")
    shutil.copy(src_case / "blueprint.yaml", proj / "blueprint.yaml")
    ad = proj / "author_decisions"
    ad.mkdir()
    src = src_case / decision_name
    data = _yaml.safe_load(src.read_text(encoding="utf-8"))
    shutil.copy(src, ad / f"{data['decision_id']}.yaml")
    return proj


def _view_text(proj: Path, decision_id: str) -> str:
    r = _run(["view", decision_id,
              "--identity", "story_identity.yaml",
              "--blueprint", "blueprint.yaml", "--project", "."], proj)
    assert r.returncode == 0, r.stderr
    return r.stdout


def _view_json(proj: Path, decision_id: str) -> dict:
    r = _run(["view", decision_id,
              "--identity", "story_identity.yaml",
              "--blueprint", "blueprint.yaml", "--project", ".", "--json"], proj)
    assert r.returncode == 0, r.stderr
    return _yaml.safe_load(r.stdout)


# ---------------------------------------------------------------------------
# Control 1: unsettled + composed -> available hint + invocation
# ---------------------------------------------------------------------------

def test_view_unsettled_shows_elicitation_available(tmp_path):
    proj = _project(tmp_path, "absent.yaml")
    out = _view_text(proj, "goal-significance-absent")
    assert "Elicitation (F3): available" in out
    assert "auteur decision elicit goal-significance-absent" in out
    assert "--identity story_identity.yaml" in out
    assert "--blueprint blueprint.yaml" in out


def test_view_unsettled_json_state_and_command(tmp_path):
    proj = _project(tmp_path, "absent.yaml")
    data = _view_json(proj, "goal-significance-absent")
    elic = data["authored"]["elicitation"]
    assert elic["state"] == "unsettled"
    assert "auteur decision elicit goal-significance-absent" in elic["command"]


# ---------------------------------------------------------------------------
# Control 2/3: declared (unranked / ordered) -> no hint, JSON state declared
# ---------------------------------------------------------------------------

def test_view_unranked_no_hint_state_declared(tmp_path):
    proj = _project(tmp_path, "unranked.yaml")
    out = _view_text(proj, "goal-significance-unranked")
    assert "Elicitation (F3)" not in out
    data = _view_json(proj, "goal-significance-unranked")
    assert data["authored"]["elicitation"]["state"] == "declared"
    assert "command" not in data["authored"]["elicitation"]


def test_view_ordered_no_hint_state_declared(tmp_path):
    proj = _project(tmp_path, "ordered-ab.yaml")
    out = _view_text(proj, "goal-significance-ordered-ab")
    assert "Elicitation (F3)" not in out
    data = _view_json(proj, "goal-significance-ordered-ab")
    assert data["authored"]["elicitation"]["state"] == "declared"
    assert "command" not in data["authored"]["elicitation"]


# ---------------------------------------------------------------------------
# Control 4: directionless one_of -> honest note, state no_composed_consequences
# ---------------------------------------------------------------------------

def test_view_directionless_honest_note(tmp_path):
    proj = _project(tmp_path, "one-of-directionless.yaml", src_case=CASE_ONE_OF)
    out = _view_text(proj, "one-of-directionless")
    assert "Elicitation (F3)" in out
    assert "not applicable" in out
    data = _view_json(proj, "one-of-directionless")
    assert data["authored"]["elicitation"]["state"] == "no_composed_consequences"
    assert "command" not in data["authored"]["elicitation"]


# ---------------------------------------------------------------------------
# Control 5: no identity/blueprint -> no elicitation section (regression)
# ---------------------------------------------------------------------------

def test_view_without_resolution_has_no_elicitation_section(tmp_path):
    proj = _project(tmp_path, "absent.yaml")
    r = _run(["view", "goal-significance-absent", "--project", "."], proj)
    assert r.returncode == 0, r.stderr
    assert "Elicitation (F3)" not in r.stdout


# ---------------------------------------------------------------------------
# Control 7: anti-inference — unsettled prose vs absent, identical hints
# ---------------------------------------------------------------------------

def test_view_unsettled_prose_and_absent_hints_identical(tmp_path):
    p1 = _project(tmp_path / "a", "unsettled-prose.yaml")
    p2 = _project(tmp_path / "b", "absent.yaml")
    out1 = _view_text(p1, "goal-significance-unsettled-prose")
    out2 = _view_text(p2, "goal-significance-absent")
    # The hint semantics are identical: both are unsettled; the only difference
    # is the decision_id embedded in the invocation (inherently per-decision).
    marker = "Elicitation (F3)"
    tail1 = out1[out1.index(marker):].replace("goal-significance-unsettled-prose", "<id>")
    tail2 = out2[out2.index(marker):].replace("goal-significance-absent", "<id>")
    assert tail1 == tail2


# ---------------------------------------------------------------------------
# Control 8: existing view behavior unchanged for declared/absent w/o resolution
# ---------------------------------------------------------------------------

def test_view_authored_lines_still_present(tmp_path):
    proj = _project(tmp_path, "absent.yaml")
    out = _view_text(proj, "goal-significance-absent")
    assert "=== AUTHORED: goal-significance-absent ===" in out
    assert "Goal significance (authored, decision-scoped): None" in out
