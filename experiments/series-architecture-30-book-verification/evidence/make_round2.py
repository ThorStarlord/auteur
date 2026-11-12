"""Round 2 corrections: derive W4 from W3 (round 1), then H1v3 from W4.

Usage: python make_round2.py <worktree_root> <corrections_dir>

Round 1 outputs (03-working-candidate-v3.json, 09-h1v2-from-w3.json) are read and not changed.
Round 2 corrects what the first finding-specific verification found partly fixed or newly
defective. Each change asserts the exact text it replaces. H1 is re-derived from W4 with the
recorded script make_h1_path.py in a temporary directory, then the H1 corrections are applied.
"""
import copy
import json
import pathlib
import subprocess
import sys
import tempfile

root = pathlib.Path(sys.argv[1]).resolve()
corr = pathlib.Path(sys.argv[2]).resolve()
exp_rel = "experiments/series-architecture-30-book-construction"
py = sys.executable


def by_id(items, key, ident):
    matches = [x for x in items if x[key] == ident]
    assert len(matches) == 1, (key, ident)
    return matches[0]


def replace_exact(current, old, new):
    assert current.count(old) == 1, ("expected exactly one occurrence", old[:70])
    return current.replace(old, new)


w3 = json.loads((corr / "03-working-candidate-v3.json").read_text(encoding="utf-8"))
w4 = copy.deepcopy(w3)

# W4-1 (round 1 finding F-1, partly fixed): the surfeit follows the Source's balance rule, not a claimed labour path.
hollow = by_id(w4["nodes"], "id", "str_hollow_gate")
hollow["summary"] = replace_exact(
    hollow["summary"],
    "In the Book 15 trial the high cistern showed surfeit, which the original defines as too much return, or stored "
    "water with no draw. The construction assumes that the trial's uncounted return labour fed the high channels "
    "beyond the Turn's count, so stored water rose with no draw to match it. Release draws the cistern down and "
    "cannot raise it.",
    "In the Book 15 trial the high cistern showed surfeit. The Source responds to the balance between draw and return, "
    "and surfeit is too much return, or stored water with no draw. The construction assumes that the trial's uncounted "
    "return exceeded the draw the Turn counted, so the surplus showed in the high cistern. The original does not name "
    "this mechanism, and the author may reject it. Release draws the cistern down and cannot raise it.")

# W4-2 (round 1 finding F-3, partly fixed): the Book 15 phase no longer assigns the surfeit to the record.
ph3 = by_id(w4["phases"], "id", "ph_3_old_hand")
ph3["narrative_function"] = replace_exact(
    ph3["narrative_function"],
    "The stewardship tally records care, not debt, so the high terraces are not surfeited.",
    "The stewardship tally records care, not debt, and the counted Turn's labour keeps the high terraces from surfeit.")
assert len(ph3["narrative_function"]) <= 1000

# W4-3 (round 1 finding F-5, partly fixed): the original's Book 30 Compact settlement is named as an open choice.
ph5 = by_id(w4["phases"], "id", "ph_5_unmeasured")
ph5["narrative_function"] = replace_exact(
    ph5["narrative_function"],
    "The original's adopted outcome is closest to A; its Compact settlement stays open.",
    "The original's adopted outcome is closest to A; its share-plot settlement is an open choice.")
assert len(ph5["narrative_function"]) <= 1000, len(ph5["narrative_function"])

# W4-4 (round 1 terminology observation): one candidate instance of "upper cistern" becomes "high cistern".
ph2 = by_id(w4["phases"], "id", "ph_2_the_turn")
act = by_id(ph2["genre_activations"], "genre_node_id", "gn_political_institutional")
act["structural_function"] = replace_exact(
    act["structural_function"], "the upper cistern thins (Book 6)", "the high cistern thins (Book 6)")

(corr / "04-working-candidate-v4.json").write_text(json.dumps(w4, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

# ---------- H1 derived from W4, then round-2 H1 corrections ----------
with tempfile.TemporaryDirectory() as scratch:
    base = pathlib.Path(scratch) / "w4-base.json"
    base.write_text(json.dumps(w4, ensure_ascii=False, indent=2), encoding="utf-8")
    h1_raw = pathlib.Path(scratch) / "h1-from-w4.json"
    subprocess.run([py, str(root / exp_rel / "evidence" / "make_h1_path.py"), str(base), str(h1_raw)],
                   check=True, capture_output=True)
    h1 = json.loads(h1_raw.read_text(encoding="utf-8"))

# H1-1 (round 1, F-12): declared consequence; the label is the author's to confirm, not "author-reserved".
gn = by_id(h1["genre_contracts"], "genre_node_id", "gn_political_institutional")
gn["payoff_expectations"][1] = replace_exact(
    gn["payoff_expectations"][1],
    "in Book 30 the record has one public keeper, and no single body holds both the record and the Gate schedule",
    "in Book 30 the Reading Hall is the single public keeper of the record, an H1 consequence that reopens the "
    "finale's plural-record commitment (for the author to confirm), and no single body holds both the record and the "
    "Gate schedule")

# H1-2 (round 1 F-13, partly fixed): the summary also lists the remnant's timing and Book 12's reading.
prefix = (
    "HYPOTHETICAL H1 PATH (not accepted; a counterfactual to the working construction). Under H1, Books 1-15 change "
    "in these ways. In Book 5 Keeper Corrow opens the records to public access, after a lower-terrace household's "
    "evidence forces the timing. The reform committee keeps physical custody of the Stones and the master record, and "
    "the debt reading, until Book 15. Dorran carries the reform as messenger and does not defect; his Book 1 status is "
    "not yet specified. Book 8's reading is authored by the committee, Book 12's reading is made under its custody, and "
    "the sale rules are the committee's. The Hall's sole custody, which the original says is never restored, is held by "
    "the committee from Book 5 to Book 15. The original's Book 5 split is replaced by the remnant forming at Book 15. "
    "The Book 15 transfer to the Reading Hall is asserted; its cause is not yet specified. The finale consequence (one "
    "public keeper in Book 30) is declared in the finale payoff. The custody-until-Book-15 structure comes from the "
    "revision instruction, not from the author-proposed premise; its sanction is not recorded. "
)
rest = w4["summary"].replace(
    "Books 1-15 keep the original's events.",
    "Under H1, Books 1-15 change as stated above; the working construction's Books 1-15 are the original's.")
assert rest != w4["summary"]
h1["summary"] = prefix + rest
assert len(h1["summary"]) <= 3000, len(h1["summary"])

# H1-3 (round 1, F-15): the question is about the transfer; the rest of the question is kept.
h1["open_questions"][14] = replace_exact(
    h1["open_questions"][14],
    "Under H1: does reform from within stay credible under Books 15 and 30, or does the Hall become a benevolent "
    "authority that the finale must oppose?",
    "Under H1: what causes the custody transfer at Book 15, and does the Reading Hall, as the single public keeper of "
    "the record, become the custodial authority the finale must check?")

(corr / "10-h1v3-from-w4.json").write_text(json.dumps(h1, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

# ---------- schema and product review ----------
sys.path.insert(0, str(root / "src"))
from auteur.beginner.studio_architecture import ArchitectureCandidate  # noqa: E402
from auteur.beginner.studio_architecture_review import build_architecture_review  # noqa: E402

for label, doc in [("W4", w4), ("H1v3", h1)]:
    ArchitectureCandidate.model_validate(doc)
print("schema: W4 and H1v3 validate")
rev34 = build_architecture_review(w3, w4, "Round 2 corrections (verification experiment)")
rev4h = build_architecture_review(w4, h1, "H1v3 corrections (verification experiment)")
(corr / "review-w3-to-w4.json").write_text(json.dumps(rev34, ensure_ascii=False, indent=2), encoding="utf-8")
(corr / "review-w4-to-h1v3.json").write_text(json.dumps(rev4h, ensure_ascii=False, indent=2), encoding="utf-8")
for name, rev in [("W3 to W4", rev34), ("W4 to H1v3", rev4h)]:
    print(name, "changed:", [(c["kind"], c["id"], c["change"]) for c in rev["changed_components"]])
    print(name, "preserved counts:", rev["preserved"]["counts"])
print("W4 summary chars:", len(w4["summary"]), "H1v3 summary chars:", len(h1["summary"]))
print("ph_5 narrative chars:", len(by_id(w4["phases"], "id", "ph_5_unmeasured")["narrative_function"]))
print("ph_3 narrative chars:", len(by_id(w4["phases"], "id", "ph_3_old_hand")["narrative_function"]))
