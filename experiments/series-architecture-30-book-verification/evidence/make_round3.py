"""Round 3 corrections: derive W5 from W4, then H1v4 from W5. The last round of verification.

Usage: python make_round3.py <worktree_root> <corrections_dir>

Round 2 outputs (04-working-candidate-v4.json, 10-h1v3-from-w4.json) are read and not changed.
Round 3 corrects what the second finding-specific verification found: a contradiction in the
surfeit logic (W4-1 says surfeit is too much return; W4-2 and the Turn node say labour holds it
off), the Book 30 Compact wording, and a terminology slip that the H1 path reintroduces.
Each change asserts the exact current text it replaces. H1 is re-derived from W5 with the
recorded script make_h1_path.py, then the H1 corrections are applied.
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


w4 = json.loads((corr / "04-working-candidate-v4.json").read_text(encoding="utf-8"))
w5 = copy.deepcopy(w4)

# W5-1: the Turn's labour matches return to draw; that keeps surfeit off, so it is no longer "labour holds it".
turn = by_id(w5["nodes"], "id", "str_measured_turn")
turn["summary"] = replace_exact(
    turn["summary"],
    "The counted Turn's labour holds the high cistern against surfeit.",
    "The counted Turn matches return to draw, which keeps the high cistern from surfeit.")

# W5-2: the same claim in the Book 15 phase.
ph3 = by_id(w5["phases"], "id", "ph_3_old_hand")
ph3["narrative_function"] = replace_exact(
    ph3["narrative_function"],
    "and the counted Turn's labour keeps the high terraces from surfeit.",
    "and the counted Turn matches return to draw, which keeps the high terraces from surfeit.")
assert len(ph3["narrative_function"]) <= 1000

# W5-3: the original's Book 30 Compact settlement is committed there and open here.
ph5 = by_id(w5["phases"], "id", "ph_5_unmeasured")
ph5["narrative_function"] = replace_exact(
    ph5["narrative_function"],
    "The original's adopted outcome is closest to A; its share-plot settlement is an open choice.",
    "The original's outcome is closest to A; its share-plot settlement is committed there; open here.")
assert len(ph5["narrative_function"]) <= 1000, len(ph5["narrative_function"])

(corr / "05-working-candidate-v5.json").write_text(json.dumps(w5, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

# ---------- H1 derived from W5 by the recorded script, then the H1 corrections ----------
with tempfile.TemporaryDirectory() as scratch:
    base = pathlib.Path(scratch) / "w5-base.json"
    base.write_text(json.dumps(w5, ensure_ascii=False, indent=2), encoding="utf-8")
    h1_raw = pathlib.Path(scratch) / "h1-from-w5.json"
    subprocess.run([py, str(root / exp_rel / "evidence" / "make_h1_path.py"), str(base), str(h1_raw)],
                   check=True, capture_output=True)
    h1 = json.loads(h1_raw.read_text(encoding="utf-8"))

# H1-1 (carried from round 2): the finale consequence is declared, labelled for the author to confirm.
gn = by_id(h1["genre_contracts"], "genre_node_id", "gn_political_institutional")
gn["payoff_expectations"][1] = replace_exact(
    gn["payoff_expectations"][1],
    "in Book 30 the record has one public keeper, and no single body holds both the record and the Gate schedule",
    "in Book 30 the Reading Hall is the single public keeper of the record, an H1 consequence that reopens the "
    "finale's plural-record commitment (for the author to confirm), and no single body holds both the record and the "
    "Gate schedule")

# H1-2 (carried from round 2): the summary lists the Book 1-15 changes, including the remnant's timing and Book 12.
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
rest = w5["summary"].replace(
    "Books 1-15 keep the original's events.",
    "Under H1, Books 1-15 change as stated above; the working construction's Books 1-15 are the original's.")
assert rest != w5["summary"]
h1["summary"] = prefix + rest
assert len(h1["summary"]) <= 3000, len(h1["summary"])

# H1-3 (carried from round 1): the open question is about the transfer, and the rest of it is kept.
h1["open_questions"][14] = replace_exact(
    h1["open_questions"][14],
    "Under H1: does reform from within stay credible under Books 15 and 30, or does the Hall become a benevolent "
    "authority that the finale must oppose?",
    "Under H1: what causes the custody transfer at Book 15, and does the Reading Hall, as the single public keeper of "
    "the record, become the custodial authority the finale must check?")

# H1-4 (round 2 terminology slip, reintroduced by the H1 script): "upper" becomes "high" in the H1 activation.
ph2 = by_id(h1["phases"], "id", "ph_2_the_turn")
act = by_id(ph2["genre_activations"], "genre_node_id", "gn_political_institutional")
act["structural_function"] = replace_exact(
    act["structural_function"], "the upper cistern thins (Book 6)", "the high cistern thins (Book 6)")

(corr / "11-h1v4-from-w5.json").write_text(json.dumps(h1, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

# ---------- schema and product review ----------
sys.path.insert(0, str(root / "src"))
from auteur.beginner.studio_architecture import ArchitectureCandidate  # noqa: E402
from auteur.beginner.studio_architecture_review import build_architecture_review  # noqa: E402

for doc in (w5, h1):
    ArchitectureCandidate.model_validate(doc)
print("schema: W5 and H1v4 validate")
rev45 = build_architecture_review(w4, w5, "Round 3 corrections (verification experiment)")
rev5h = build_architecture_review(w5, h1, "H1v4 corrections (verification experiment)")
(corr / "review-w4-to-w5.json").write_text(json.dumps(rev45, ensure_ascii=False, indent=2), encoding="utf-8")
(corr / "review-w5-to-h1v4.json").write_text(json.dumps(rev5h, ensure_ascii=False, indent=2), encoding="utf-8")
for name, rev in [("W4 to W5", rev45), ("W5 to H1v4", rev5h)]:
    print(name, "changed:", [(c["kind"], c["id"], c["change"]) for c in rev["changed_components"]])
print("W5 summary chars:", len(w5["summary"]), "H1v4 summary chars:", len(h1["summary"]))
print("ph_5 narrative chars:", len(ph5["narrative_function"]), "ph_3 narrative chars:", len(ph3["narrative_function"]))
