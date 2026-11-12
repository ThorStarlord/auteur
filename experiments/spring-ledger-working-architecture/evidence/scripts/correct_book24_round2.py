"""Second correction round for the Book 24 function and candidate.

Corrects the new defect introduced by round 1 (the 'public gauge' is the Book 23 Balance Stones, not the
Book 22 Gate gauge), the two partly fixed items (the Reading Hall framing, the surge-route wording), and the
Hesper belief tension. Writes -2 files beside the round-1 files. Every replacement asserts its exact text.
"""
import json
import sys
from pathlib import Path

base = Path(sys.argv[1])
repo_src = Path(sys.argv[2])
fn_in = base / "book-24-function.corrected.md"
fn_out = base / "book-24-function.corrected-2.md"
cd_in = base / "book-24-candidate.corrected.json"
cd_out = base / "book-24-candidate.corrected-2.json"


def replace_exact(text, old, new, count=1):
    found = text.count(old)
    assert found == count, ("expected %d occurrence(s), found %d" % (count, found), old[:90])
    return text.replace(old, new)


fn = fn_in.read_text(encoding="utf-8")
fn = replace_exact(fn,
    "**The public gauge** (`eng_source`; 01 §2.2). The gauge is the Source's own state, and it does not depend on the Gate.",
    "**The Balance Stones** (`eng_source`; 01 §2.2). The Stones are the Source's public measure, cut in Book 23 and published "
    "by the Reading Hall. They do not depend on the Gate.")
fn = replace_exact(fn, "*Consequence:* the public gauge shows the return, in aggregate.",
    "*Consequence:* the Balance Stones show the return, in aggregate.")
fn = replace_exact(fn, "the gauge (aggregate balance) and craft-marks", "the Balance Stones (aggregate balance) and craft-marks")
fn = replace_exact(fn, "[Derived: publishes the gauge, no schedule authority]", "[Derived: publishes the Balance Stones, no schedule authority]")
fn = replace_exact(fn, "Asked to certify the crew from the gauge, it declines", "Asked to certify the crew from the Stones, it declines")
fn = replace_exact(fn, "because the gauge does not resolve local return (P3).", "because the Stones do not resolve local return (P3).")
fn = replace_exact(fn, "After the thaw, the gauge shows the crew's return", "After the thaw, the Balance Stones show the crew's return")
fn = replace_exact(fn, "It is separate from the debt ledger, the tally and the gauge.", "It is separate from the debt ledger, the tally and the Balance Stones.")
fn = replace_exact(fn,
    "The Reading Hall has defined a limit on itself.** It reads aggregate balance and will not attribute it to persons.",
    "The Reading Hall declines to attribute balance to persons** while the Stones cannot resolve local return (P3).")
fn = replace_exact(fn, "The gauge shows it in aggregate.", "The Balance Stones show it in aggregate.")
fn = replace_exact(fn,
    "Return labour shows on the gauge in aggregate, without attribution. This follows from `eng_source`, but the gauge's resolution is not established.",
    "Return labour shows on the Balance Stones in aggregate, without attribution. This follows from `eng_source`, but the Stones' "
    "resolution of local return is not established.")
fn = replace_exact(fn, "Any channel except the Long Return's surge route would serve.", "Any channel the crew can work would serve.")
fn = replace_exact(fn, "Whether the gauge can resolve local return at all (P3).", "Whether the Balance Stones can resolve local return at all (P3).")
fn = replace_exact(fn, "derived from Book 23 belief]", "derived from the cohort's Book 23 belief, which her household's burden complicates]")
fn_out.write_text(fn, encoding="utf-8")

cand = json.loads(cd_in.read_text(encoding="utf-8"))
nodes = {n["id"]: n for n in cand["nodes"]}
links = {l["id"]: l for l in cand["links"]}
nodes["str_b24_uncounted_crew"]["summary"] = replace_exact(
    nodes["str_b24_uncounted_crew"]["summary"],
    "the public gauge shows the return in aggregate but not by household",
    "the Balance Stones show the return in aggregate but not by household")
assert links["l_b24_crew_gauge"]["function"] == "uncounted labour shows on the gauge in aggregate, not by household"
links["l_b24_crew_gauge"]["function"] = "uncounted labour shows on the Balance Stones in aggregate, not by household"
assert links["l_b24_reading_hall_declines"]["function"] == (
    "declines to attribute gauge balance to named hands, which the gauge does not resolve")
links["l_b24_reading_hall_declines"]["function"] = (
    "declines to attribute Balance Stones readings to named hands, which the Stones do not resolve")
assert all(len(l["function"]) <= 120 for l in cand["links"])
cd_out.write_text(json.dumps(cand, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

sys.path.insert(0, str(repo_src))
from auteur.beginner.studio_architecture import ArchitectureCandidate  # noqa: E402
ArchitectureCandidate.model_validate(cand)
print("round-2 function written:", fn_out.name, len(fn.split()), "words")
print("round-2 candidate validates; nodes/links changed: 1 node summary, 2 link functions")
