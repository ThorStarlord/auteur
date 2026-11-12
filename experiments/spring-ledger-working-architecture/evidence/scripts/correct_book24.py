"""Apply the critique's required and recommended corrections to the Book 24 function and candidate.

The agent's originals are kept unchanged. Corrected files are written beside them with a
.corrected suffix. Every replacement asserts the exact text it changes.
"""
import json
import sys
from pathlib import Path

base = Path(sys.argv[1])
repo_src = Path(sys.argv[2])
fn_in = base / "book-24-function.md"
fn_out = base / "book-24-function.corrected.md"
cd_in = base / "book-24-candidate.json"
cd_out = base / "book-24-candidate.corrected.json"


def replace_exact(text, old, new):
    assert text.count(old) == 1, ("expected exactly one occurrence", old[:80], text.count(old))
    return text.replace(old, new)


fn = fn_in.read_text(encoding="utf-8")
fn = replace_exact(
    fn,
    "**The public gauge** (`eng_source`; `l_reading_separate_schedule`).",
    "**The public gauge** (`eng_source`; 01 §2.2). The gauge is the Source's own state, and it does not depend on the Gate.",
)  # F5
fn = replace_exact(
    fn,
    "Gift without skill also fails, as the gift reading's physical caveat predicts (01 §2.3).",
    "Gift without skill also fails. This is a new physical assumption (P4), not a consequence of the caveat in 01 §2.3, "
    "which concerns gift without return and gift with unequal hands.",
)  # F6
fn = replace_exact(
    fn,
    "it refuses to attribute aggregate balance to named hands, because that would make it a ledger-keeper.",
    "it declines to attribute aggregate balance to named hands, because the gauge does not resolve local return (P3). "
    "Whether the Hall should keep any person-level record is not settled here, and B's deficit-record cost (01 §6) is unchanged.",
)  # F3
fn = replace_exact(
    fn,
    "Her motive is her own, and it does not carry the author's preference for the Turn (open question 10; 01 §8.11).",
    "Her motive is designed to be judged against open question 10 (01 §8.11). Whether it is independent of the author's "
    "preference remains the author's decision.",
)  # F2
fn = replace_exact(
    fn,
    "the granddaughter repeats her grandmother's Book 1 act, evidence cut in stone, against her grandmother's institution.",
    "the granddaughter, as her grandmother did in Book 1, sets evidence against an institution's record; here the evidence "
    "is a craft-mark on the water, not a share-mark.",
)  # F6
fn = replace_exact(
    fn,
    "The governing variable (`th_hands_and_draw`) gains a third term: who *can* return labour, beside who gives it and who is counted for draw.",
    "The Ledger engine gains a capability record, which bears on the governing variable (`th_hands_and_draw`) by showing who is "
    "able to give return labour. It does not change who is counted for draw.",
)  # F1
fn = replace_exact(
    fn,
    "The surge route is author-reserved (01 §8.6), so it is avoided.",
    "The surge route is author-reserved (01 §8.6). This Book neither designates the Lowfen as the surge route nor excludes it.",
)  # F4
fn_out.write_text(fn, encoding="utf-8")

# Candidate: the two link functions that carry F1 and F3. Everything else is unchanged.
cand = json.loads(cd_in.read_text(encoding="utf-8"))
links = {l["id"]: l for l in cand["links"]}
assert links["l_b24_mark_variable"]["function"] == (
    "adds who can return labour beside who gives it and who is counted")
links["l_b24_mark_variable"]["function"] = "bears on who can return labour; does not change who is counted for draw"
assert links["l_b24_reading_hall_declines"]["function"] == "declines to attribute gauge balance to named hands"
links["l_b24_reading_hall_declines"]["function"] = (
    "declines to attribute gauge balance to named hands, which the gauge does not resolve")
assert all(len(l["function"]) <= 120 for l in cand["links"])
cd_out.write_text(json.dumps(cand, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

# Validate the corrected candidate on current main's schema.
sys.path.insert(0, str(repo_src))
from auteur.beginner.studio_architecture import ArchitectureCandidate  # noqa: E402
ArchitectureCandidate.model_validate(cand)
print("corrected function:", fn_out.name, len(fn.split()), "words")
print("corrected candidate validates; links changed: 2")
