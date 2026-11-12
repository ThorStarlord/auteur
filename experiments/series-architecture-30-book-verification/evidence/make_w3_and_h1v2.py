"""Derive the corrected candidate W3 from W2, then the corrected H1 (H1v2) from W3.

Usage: python make_w3_and_h1v2.py <worktree_root> <out_dir>

W2 is read from the committed PR #553 file and is not changed. Every correction asserts the
exact current text it replaces, so a drifted base fails loudly. The recorded H1 script,
make_h1_path.py, derives H1 from W3 in a temporary directory. H1v2 then applies the H1
corrections (H1-1 to H1-3) to that derivation. Review objects are written with the product's
own build_architecture_review, so the W2 to W3 and W3 to H1v2 changes are recorded by the product.
"""
import copy
import json
import pathlib
import subprocess
import sys
import tempfile

root = pathlib.Path(sys.argv[1]).resolve()
out = pathlib.Path(sys.argv[2]).resolve()
out.mkdir(parents=True, exist_ok=True)
exp_rel = "experiments/series-architecture-30-book-construction"
commit = "aaae0eaaddfbfa98ccb6d239fc01cef5ffe3d478"
py = sys.executable


def blob(path):
    return subprocess.run(["git", "-C", str(root), "show", f"{commit}:{path}"],
                          capture_output=True, check=True).stdout


def by_id(items, key, ident):
    matches = [x for x in items if x[key] == ident]
    assert len(matches) == 1, (key, ident)
    return matches[0]


def replace_exact(current, old, new):
    assert current.count(old) == 1, ("expected exactly one occurrence", old[:60])
    return current.replace(old, new)


# ---------- W3: corrections to the final candidate W2 ----------
w2 = json.loads(blob(f"{exp_rel}/03-working-candidate-v2.json").decode("utf-8"))
w3 = copy.deepcopy(w2)

# W3-1 (R8): the Book 15 surfeit is not caused by a release to the lower channels.
hollow = by_id(w3["nodes"], "id", "str_hollow_gate")
old = ("The sluice that divides the high cistern's release between the upper and lower channels. "
       "The Council has set its schedule since the Turn. In the Book 15 trial the schedule carried release "
       "to the lower channels, and the high cistern showed surfeit. The construction reads the surfeit as "
       "that release's effect, which the original does not name. The schedule is the object of the Book 21 conflict.")
new = ("The sluice that divides the high cistern's release between the upper and lower channels. "
       "The Council has set its schedule since the Turn. In the Book 15 trial the high cistern showed surfeit, "
       "which the original defines as too much return, or stored water with no draw. The construction assumes "
       "that the trial's uncounted return labour fed the high channels beyond the Turn's count, so stored water "
       "rose with no draw to match it. Release draws the cistern down and cannot raise it. "
       "The schedule is the object of the Book 21 conflict.")
assert hollow["summary"] == old
hollow["summary"] = new

# W3-2 (R11, R17): labour matched to shares, and the tally records the labour rather than holding water.
turn = by_id(w3["nodes"], "id", "str_measured_turn")
old = ("Draw matched to labour in the high terraces, run by the Council since the Turn in Book 6. "
       "The stewardship tally, from Book 15, is kept as a record of care for this practice. "
       "It holds the high cistern against surfeit.")
new = ("Labour matched to shares in the high terraces, run by the Council since the Turn in Book 6: each share "
       "returns labour by rota, and draw still follows shares. The counted Turn's labour holds the high cistern "
       "against surfeit. The stewardship tally, from Book 15, records that labour as a record of care for this "
       "practice; it does not hold the water.")
assert turn["summary"] == old
turn["summary"] = new

# W3-2b (R11): the claim is not "since Book 6".
ph4 = by_id(w3["phases"], "id", "ph_4_settled_water")
ph4["narrative_function"] = replace_exact(
    ph4["narrative_function"],
    "It makes hands set part of draw for the first time since Book 6, and it gives lineage crews a claim on draw.",
    "It makes hands set part of draw for the first time in the series, and it gives lineage crews a claim on draw.")

# W3-3 (R12): the original's word is "split".
hall = by_id(w3["nodes"], "id", "inst_stone_hall")
hall["summary"] = replace_exact(
    hall["summary"],
    "Under this working path the Hall dissolves in Book 5, and a remnant",
    "Under this working path the Hall splits in Book 5, as the original has it, and a remnant")

# W3-4 (R15): the original's adopted outcome is A, and the Compact's settlement stays open.
ph5 = by_id(w3["phases"], "id", "ph_5_unmeasured")
ph5["narrative_function"] = replace_exact(
    ph5["narrative_function"],
    "and the Compact's settlement is a clause of B or C.",
    "and the Compact's settlement is a clause of B or C. The original's adopted outcome is closest to A; "
    "its Compact settlement stays open.")
# The phase narrative is capped at 1000 characters by the schema. The first draft of this
# addition was longer and failed validation (recorded in w3-changes.md).
assert len(ph5["narrative_function"]) <= 1000, len(ph5["narrative_function"])

# W3-5 (R9, R16): record what is not decided.
w3["summary"] = replace_exact(
    w3["summary"],
    "Whether shared accounting binds, the flood, the Compact's fate and the stance toward reform are not decided here.",
    "Whether shared accounting binds, the flood, the Compact's fate and the stance toward reform are not decided here. "
    "Also not decided: whether the Hollow Gate and the Gate Table are accepted parts of the world, and which body "
    "ratifies the instrument that Alternative C depends on.")
assert len(w3["summary"]) <= 3000, len(w3["summary"])

(out / "03-working-candidate-v3.json").write_text(json.dumps(w3, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

# ---------- H1 derived from W3 by the recorded script, then H1v2 corrections ----------
with tempfile.TemporaryDirectory() as scratch:
    base = pathlib.Path(scratch) / "w3-base.json"
    base.write_text(json.dumps(w3, ensure_ascii=False, indent=2), encoding="utf-8")
    h1_raw = pathlib.Path(scratch) / "h1-from-w3.json"
    subprocess.run([py, str(root / exp_rel / "evidence" / "make_h1_path.py"), str(base), str(h1_raw)],
                   check=True, capture_output=True)
    h1 = json.loads(h1_raw.read_text(encoding="utf-8"))

# H1-1 (R1): the finale consequence is declared as an H1 consequence that reopens an author commitment.
gn = by_id(h1["genre_contracts"], "genre_node_id", "gn_political_institutional")
gn["payoff_expectations"][1] = replace_exact(
    gn["payoff_expectations"][1],
    "in Book 30 the record has one public keeper, and no single body holds both the record and the Gate schedule",
    "in Book 30 the Reading Hall is the single public keeper of the record, an H1 consequence that reopens the "
    "finale's plural-record commitment (author-reserved), and no single body holds both the record and the Gate schedule")

# H1-2 (R2, R5, R9): the summary lists the Book 1-15 changes, and declares the unsanctioned structure.
prefix = (
    "HYPOTHETICAL H1 PATH (not accepted; a counterfactual to the working construction). Under H1, Books 1-15 change "
    "in these ways. In Book 5 Keeper Corrow opens the records to public access, after a lower-terrace household's "
    "evidence forces the timing. The reform committee keeps physical custody of the Stones and the master record, and "
    "the debt reading, until Book 15. Dorran carries the reform as messenger and does not defect; his Book 1 status is "
    "not yet specified. Book 8's reading is authored by the committee, and the sale rules are the committee's. The "
    "Hall's sole custody, which the original says is never restored, is held by the committee from Book 5 to Book 15. "
    "The Book 15 transfer to the Reading Hall is asserted; its cause is not yet specified. The finale consequence (one "
    "public keeper in Book 30) is declared in the finale payoff. The custody-until-Book-15 structure comes from the "
    "revision instruction, not from the author-proposed premise; its sanction is not recorded. "
)
rest = w3["summary"].replace(
    "Books 1-15 keep the original's events.",
    "Under H1, Books 1-15 change as stated above; the working construction's Books 1-15 are the original's.")
assert rest != w3["summary"]
h1["summary"] = prefix + rest
assert len(h1["summary"]) <= 3000, len(h1["summary"])

# H1-3 (R8): the open question is about the transfer and the Reading Hall, not about the Hall's future opposition.
h1["open_questions"][14] = replace_exact(
    h1["open_questions"][14],
    "Under H1: does reform from within stay credible under Books 15 and 30, or does the Hall become a benevolent "
    "authority that the finale must oppose?",
    "Under H1: what causes the custody transfer at Book 15, and does the Reading Hall, as the single public keeper of "
    "the record, become the custodial authority the finale must check?")

(out / "09-h1v2-from-w3.json").write_text(json.dumps(h1, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

# ---------- product review objects, recorded by the product's own review builder ----------
sys.path.insert(0, str(root / "src"))
from auteur.beginner.studio_architecture import ArchitectureCandidate  # noqa: E402
from auteur.beginner.studio_architecture_review import build_architecture_review  # noqa: E402

for label, doc in [("w2", w2), ("w3", w3), ("h1v2", h1)]:
    ArchitectureCandidate.model_validate(doc)
print("schema: W2, W3 and H1v2 validate")
rev23 = build_architecture_review(w2, w3, "W3 corrections (verification experiment)")
rev3h = build_architecture_review(w3, h1, "H1v2 corrections (verification experiment)")
(out / "review-w2-to-w3.json").write_text(json.dumps(rev23, ensure_ascii=False, indent=2), encoding="utf-8")
(out / "review-w3-to-h1v2.json").write_text(json.dumps(rev3h, ensure_ascii=False, indent=2), encoding="utf-8")
for name, rev in [("W2 to W3", rev23), ("W3 to H1v2", rev3h)]:
    comps = [(c["kind"], c["id"], c["change"]) for c in rev["changed_components"]]
    print(name, "changed:", comps)
    print(name, "preserved counts:", rev["preserved"]["counts"])
