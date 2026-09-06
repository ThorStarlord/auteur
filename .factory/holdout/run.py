#!/usr/bin/env python3
"""HOLDOUT SCENARIOS for the auteur factory. Lives in `.factory/holdout/` -
the builder cannot read this directory (tool deny + diff guard), which is the
only property that makes any of this evidence.

Rules followed here: written BEFORE the work they will ever judge; duplicated,
never imported, from harness/ (only process management is shared); composed,
not isolated; inputs that appear nowhere else in this repository.

The three scenarios, and what each is for:
  1. environment-tripwire - the stale-install class, live: the gate must import
     the tree it is validating, never a leftover install from another checkout
     or worktree. This exact failure killed a real gate run (a unit run
     graded against last month's code from a dead worktree). It must stay failed.
  2. invalid-accept-rejected - the authority invariant from the other side: a
     candidate that fails validation must never become canonical state, and the
     prior absence must survive the attempt.
  3. fresh-premise-integrity - the fail-closed state machine: on a project with
     a brief and no run output, review must refuse with its documented error
     rather than rendering a recommendation. Values unique to this file.

Emits `HOLDOUT_PASSED scenarios=N assertions=M`. The count is the point.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

# Same belt-and-suspenders as harness/e2e.py: evidence must survive any stdio
# encoding (see that file's comment).
try:
    sys.stdout.reconfigure(errors="backslashreplace")
except Exception:                                              # noqa: BLE001
    pass

_HARNESS = Path(__file__).resolve().parent.parent.parent / "harness"
sys.path.insert(0, str(_HARNESS))
from appproc import make_driver                                # noqa: E402

CONFIG = json.loads((_HARNESS / "harness.config.json").read_text(encoding="utf-8"))
ROOT = Path(__file__).resolve().parent.parent.parent

ASSERTIONS = 0
FAILURES: list[str] = []

# The invalid candidate. Embedded here rather than read from harness/fixtures/
# so its exact bytes appear NOWHERE the builder can read: the same valid
# identity with the `title` field removed, which the promote validation must
# reject. Verified against the real accept path (exit 1, no file written).
INVALID_CANDIDATE = """\
core_answer: 'The Closed Circle, With Blood Debts: a controlled fixture candidate.'
target_experience:
  primary: painful dramatic irony with fragile hope
  progression: unease -> dread -> bittersweet agency
  secondary:
  - tenderness
  - hope
  avoid: []
  primary_emotional_promise: painful dramatic irony with fragile hope
  secondary_palette:
  - tenderness
  - hope
  avoided_experiences: []
  emotional_trajectory: null
  genre_emotion_stack: null
  pov_experience_contracts: null
story_type:
  medium: novel
  mode: other
  genre: sci_fi
  subgenres: []
  target_audience: adult
  length_class: null
central_engine:
  want: Rebuild the city and protect the surviving community.
  resistance: Incomplete knowledge and hidden interventions complicate recovery.
  conflict: A woman rebuilds a city after a disaster without learning her brother
    caused it.
  stakes: Failure exposes the city to another collapse.
  change: She earns practical agency without learning the forbidden truth.
architecture_preferences:
  complexity: maximalist
  causal_distribution: mixed
  engine_hierarchy: primary_with_layers
hard_constraints:
- the protagonist never learns the brother caused the disaster
not_this: []
open_questions: []
confidence: null
alternatives: []
recommendation_mode: opinionated
best_basis: genre_aligned
why_this_is_best: null
rejected_directions: []
author_overrides: []
characters: []
"""

# A premise that appears nowhere else in this repository (checked at write
# time). If the machinery below ever depends onfixture values, this scenario
# is the one that notices.
FRESH_PREMISE = "A lighthouse keeper discovers that the tide is a debt collector."
FRESH_ANSWERS = "\n".join([
    FRESH_PREMISE,
    "mystery",
    "adult",
    "dread with a dry wit",
]) + "\n"


def expect(name: str, ok: bool, detail: str = "") -> None:
    global ASSERTIONS
    ASSERTIONS += 1
    if not ok:
        FAILURES.append(f"{name}: {detail}")


def scenario_environment_tripwire(app) -> None:
    """The interpreter must resolve the product from THIS tree.

    Kills the stale-install class: an editable install from another checkout
    or a long-dead worktree silently redirecting every check at old code.
    """
    p = subprocess.run([sys.executable, "-c",
                        "import auteur; print(auteur.__file__)"],
                       capture_output=True, text=True, timeout=60)
    got = (p.stdout or "").strip()
    expect("auteur resolves inside this repo",
           p.returncode == 0 and got.startswith(str(ROOT)),
           f"rc={p.returncode} auteur.__file__={got!r} root={ROOT}")
    rc, out, err = app.run("ontology list")
    expect("the CLI answers from this tree",
           rc == 0 and "Character" in out,
           f"rc={rc} tail={(out + err)[-200:]!r}")


def scenario_invalid_accept_rejected(app) -> None:
    """A candidate that fails validation must never become canonical state."""
    journey = Path(tempfile.mkdtemp(prefix="holdout-reject-"))
    try:
        bad = journey / "bad-candidate.yaml"
        bad.write_text(INVALID_CANDIDATE, encoding="utf-8")
        ident = journey / "story_identity.yaml"
        rc, out, err = app.run(
            f'story-discovery accept "{bad}" --output "{ident}"')
        expect("accepting an invalid candidate fails",
               rc != 0, f"rc={rc} - an invalid candidate was ACCEPTED")
        expect("no canonical state after a refused accept",
               not ident.exists(),
               "story_identity.yaml exists despite the refusal")
    finally:
        shutil.rmtree(journey, ignore_errors=True)


def scenario_fresh_premise_integrity(app) -> None:
    """The state gate fires honestly on a project with no run output.

    A fresh project has a brief and nothing else. `review` must REFUSE with
    the documented state error - not render a recommendation, not crash, and
    above all not touch canonical state. This is the fail-closed state machine
    doing its job, and it is asserted here rather than assumed.
    """
    journey = Path(tempfile.mkdtemp(prefix="holdout-fresh-"))
    try:
        rc, out, err = app.run(f'story-discovery start --project "{journey}"',
                               stdin=FRESH_ANSWERS)
        expect("fresh start succeeds", rc == 0, f"rc={rc}")
        brief = journey / "story_discovery" / "brief.yaml"
        expect("fresh brief exists", brief.exists())
        expect("the fresh premise is preserved",
               FRESH_PREMISE in " ".join(brief.read_text(encoding="utf-8").split()))
        rc, out, err = app.run(f'story-discovery review --project "{journey}"')
        expect("review refuses without run output",
               rc != 0 and "needs a fresh Story Discovery run" in (out + err),
               f"rc={rc} tail={(out + err)[-300:]!r}")
        expect("no canonical state on the fresh journey",
               not (journey / "story_identity.yaml").exists())
    finally:
        shutil.rmtree(journey, ignore_errors=True)


SCENARIOS = [
    scenario_environment_tripwire,
    scenario_invalid_accept_rejected,
    scenario_fresh_premise_integrity,
]


def main() -> int:
    with make_driver(CONFIG) as app:
        for fn in SCENARIOS:
            try:
                fn(app)
            except Exception as e:                             # noqa: BLE001
                FAILURES.append(f"{fn.__name__} raised {type(e).__name__}: {e}")

    if FAILURES:
        for f in FAILURES:
            print(f"  HOLDOUT_FAIL  {f}", flush=True)
        print(f"HOLDOUT_FAILED scenarios={len(SCENARIOS)} assertions={ASSERTIONS} "
              f"failures={len(FAILURES)}", flush=True)
        return 1

    print(f"HOLDOUT_PASSED scenarios={len(SCENARIOS)} assertions={ASSERTIONS}",
          flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
