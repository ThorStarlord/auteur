"""The end-to-end path: the discovery journey as a real author takes it.

R1.1: premise in -> guided brief -> frozen search output in place ->
recommended direction reviewed -> explicit accept -> canonical
story_identity.yaml exists, and is absent at every step before acceptance.

ARCHITECTURE OF THIS JOURNEY, stated honestly because the gate depends on it:

The journey has two halves. The first half (start, refine) is fully live: the
real interactive brief Q&A, answered as a user answers it. The second half
begins where the LLM-backed `run` subcommand would search - and that half is
FROZEN: harness/fixtures/ carries candidate_1.yaml, candidate_2.yaml and
discovery_set.yaml, generated once via the product's own constructors from a
brief built with these exact answers, then verified through this same journey
(review renders RECOMMENDED, accept lands byte-identical content).

Why frozen is legitimate here rather than a cheat: the multi-engine search
needs provider keys and is nondeterministic, so it cannot prove anything
unattended; everything DOWNSTREAM of its persisted output - recommendation
rendering, winner selection, validation, atomic promotion - runs live on every
lap. The fixture is "what was asked"; the gate asserts "what the code does
now". The LLM surface itself is covered by the project's live-eval tests and
by human review, never by this gate.

Three rules: assert what a user would notice; COUNT THE STEPS (STEPS is the
floor the gate ratchets); RETURN None ON FAILURE, having printed why.
"""
from __future__ import annotations

import shutil
import sys
import tempfile
import yaml
from pathlib import Path

# Belt and suspenders for Windows consoles: the dispatch environment is supposed
# to run with PYTHONIOENCODING=utf-8 (see factory/config.sh), but a check must
# never die printing its own evidence. Reconfigure stdout to survive any stdio
# encoding instead of crashing on the first non-ASCII detail string.
try:
    sys.stdout.reconfigure(errors="backslashreplace")
except Exception:                                              # noqa: BLE001
    pass

HERE = Path(__file__).resolve().parent
FIX = HERE / "fixtures"

STEPS = 0

PREMISE = ("A woman rebuilds a city after a disaster "
           "without learning her brother caused it.")
TITLE_1 = "The Closed Circle, With Blood Debts"

START_ANSWERS = "\n".join([
    PREMISE,
    "science fiction",
    "adult",
    "painful dramatic irony with fragile hope",
]) + "\n"

REFINE_ANSWERS = "\n".join([
    "tenderness, hope",
    "nihilism",
    "yes",
    "rising pressure",
    "unease",
    "dread",
    "bittersweet agency",
    "richly interconnected",
    "several interacting causes",
    "one main engine with substantial supporting layers",
    "not sure",
    "not sure",
    "the protagonist never learns the brother caused the disaster",
    "",
]) + "\n"


def check(name: str, ok: bool, detail: str = "") -> bool:
    global STEPS
    STEPS += 1
    if ok:
        print(f"  ok    {name}", flush=True)
        return True
    print(f"  FAIL  {name}  {detail}", flush=True)
    return False


def run_e2e(app) -> int | None:
    """Drive the journey. Returns the assertion count, or None on failure."""
    global STEPS
    STEPS = 0
    journey = Path(tempfile.mkdtemp(prefix="harness-journey-"))
    try:
        return _journey(app, journey)
    except Exception as e:                              # noqa: BLE001
        print(f"  FAIL  journey raised {type(e).__name__}: {e}", flush=True)
        return None
    finally:
        shutil.rmtree(journey, ignore_errors=True)


def _journey(app, journey: Path) -> int | None:
    ident = journey / "story_identity.yaml"
    disc = journey / "story_discovery"

    # --- the author starts a discovery ----------------------------------
    rc, out, err = app.run(f'story-discovery start --project "{journey}"',
                           stdin=START_ANSWERS)
    if not check("the brief is created", rc == 0,
                 f"rc={rc} tail={(out + err)[-300:]!r}"):
        return None
    brief = disc / "brief.yaml"
    if not check("brief.yaml exists", brief.exists()):
        return None
    # YAML folding may wrap the premise across lines; compare normalized.
    flat = " ".join(brief.read_text(encoding="utf-8").split())
    if not check("the premise is preserved in the brief", PREMISE in flat):
        return None
    if not check("no canonical state before acceptance (start)",
                 not ident.exists()):
        return None

    # --- the author refines -----------------------------------------------
    rc, out, err = app.run(f'story-discovery start --project "{journey}" --refine',
                           stdin=REFINE_ANSWERS)
    if not check("the brief is refined", rc == 0,
                 f"rc={rc} tail={(out + err)[-300:]!r}"):
        return None

    # --- the frozen search output lands where `run` would have put it ------
    # (see module docstring for why frozen is legitimate here)
    for name in ("discovery_set.yaml", "candidate_1.yaml", "candidate_2.yaml"):
        shutil.copy(FIX / name, disc / name)
    staged = all((disc / n).exists()
                 for n in ("discovery_set.yaml", "candidate_1.yaml",
                           "candidate_2.yaml"))
    if not check("the search output is staged", staged):
        return None

    # --- the author reviews the recommendation ------------------------------
    rc, out, err = app.run(f'story-discovery review --project "{journey}"')
    if not check("review renders", rc == 0, f"rc={rc}"):
        return None
    if not check("review recommends the winning direction",
                 "Recommended story direction" in out,
                 f"tail={out[-300:]!r}"):
        return None
    if not check("review's accept path names candidate_1",
                 "story_discovery/candidate_1.yaml" in out,
                 f"tail={out[-300:]!r}"):
        return None
    if not check("no canonical state before acceptance (review)",
                 not ident.exists()):
        return None

    # --- the author accepts ---------------------------------------------------
    rc, out, err = app.run(
        f'story-discovery accept "{disc / "candidate_1.yaml"}" '
        f'--output "{ident}"')
    if not check("accept succeeds", rc == 0,
                 f"rc={rc} tail={(out + err)[-300:]!r}"):
        return None
    if not check("story_identity.yaml exists after accept", ident.exists()):
        return None
    want = yaml.safe_load((FIX / "candidate_1.yaml").read_text(encoding="utf-8"))
    got = yaml.safe_load(ident.read_text(encoding="utf-8"))
    if not check("the accepted identity is the candidate, field for field",
                 want == got):
        return None
    if not check("the title a user would look for is present",
                 TITLE_1 in ident.read_text(encoding="utf-8")):
        return None

    return STEPS
