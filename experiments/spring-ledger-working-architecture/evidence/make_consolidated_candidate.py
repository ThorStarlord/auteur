"""Derive the consolidated working candidate (W6) from W5 at its source commit.

Usage: python make_consolidated_candidate.py <worktree_root> <out_json>

W5 is read with `git show` from the PR #554 head, so the derivation is traceable to that commit.
Every change asserts the exact text it replaces. Changes are consolidation edits only:
no new architecture, and no change to any emotion target, node, link, phase or genre contract
except the labels named below. Each change is listed in 04-provenance.md.
"""
import copy
import json
import subprocess
import sys

root, out = sys.argv[1], sys.argv[2]
W5_COMMIT = "d6dd636d62e23c0138ae0a561bf329332852124c"
W5_PATH = "experiments/series-architecture-30-book-verification/corrections/05-working-candidate-v5.json"
raw = subprocess.run(["git", "-C", root, "show", f"{W5_COMMIT}:{W5_PATH}"],
                     capture_output=True, check=True).stdout.decode("utf-8")
w5 = json.loads(raw)
w6 = copy.deepcopy(w5)


def replace_exact(current, old, new):
    assert current.count(old) == 1, ("expected one occurrence", old[:70])
    return current.replace(old, new)


# 1. Summary: a status summary that agrees with the prose architecture. No preference for C.
w6["summary"] = (
    "The Spring Ledger, consolidated working architecture W6, derived from W5 (PR #554, commit "
    f"{W5_COMMIT[:8]}). Working and noncanonical; not author-approved. The author-fixed intentions are recorded "
    "separately as Studio intentions. The prose architecture is 01-series-architecture.md in the package. "
    "The Series keeps five arcs, the three co-governing engines (Ledger, Source, Old Hand), the Arc IV conflicts, "
    "Book 23's inheritance and the Book 30 finale. Books 1-15 keep the original's events; Book 1 reads the "
    "share-marks as evidence, and the first partial reading of the script is Book 8. The Hollow Gate, the Gate "
    "Table, the Special Draw Right and the Book 15 surfeit mechanism are agent-proposed construction additions. "
    "Finale Alternatives A, B and C are not chosen, and each states its costs. Not decided: whether shared accounting "
    "binds; which finale alternative is preferred; the Compact's settlement; whether the Hollow Gate and Gate Table are "
    "accepted; the reform stance; the flood's losses; the Special Draw Right's status. The high cistern's storage is "
    "not established, and no value for it is canon. The Harrow Lowe gate is inherited from the original and is "
    "recorded as a provisional concept, not in this candidate."
)
assert len(w6["summary"]) <= 3000, len(w6["summary"])

# 2. Alternative C: remove the working-direction label, so the candidate states no preferred finale.
c_node = next(n for n in w6["nodes"] if n["id"] == "alt_c_ratified_trigger")
c_node["title"] = replace_exact(c_node["title"], "Finale Alternative C (not chosen; working direction for testing)",
                                "Finale Alternative C (not chosen)")
c_node["summary"] = replace_exact(c_node["summary"], "Ratified in Books 27-29", "Ratified in Books 27-29")

# 3. Open questions: merge two overlapping pairs without losing content; add the two author reservations
#    the mission names that W5 never listed. The list stays at the schema cap of 16.
q = list(w6["open_questions"])
assert len(q) == 16
assert q[4].startswith("Is the lineage Special Draw Right revocable") and q[11].startswith("Who carries the Turn")
assert q[7].startswith("Which channel takes") and q[13].startswith("Is the Book 30 flood survived")
assert q[8].startswith("Does a Balance Stones threshold exist")
q[4] = ("Is the lineage Special Draw Right revocable or permanent, what training condition does it carry, and who "
        "carries the Turn when the maintenance lineages end? Not decided.")
q[7] = ("Which channel takes the Long Return's surge, does any household flood, and does the flood cost lives or lasting "
        "losses? These are author choices and are not decided.")
q[8] = ("Does a Balance Stones threshold exist (Alternative C), who reads it, and which body ratifies it? Not decided.")
for i in sorted([11, 13], reverse=True):
    del q[i]
q.append("Are the Hollow Gate and the Gate Table accepted parts of the world? Not decided; both are construction additions.")
q.append("What can the high cistern physically store above its tolerance? Not established; Alternatives B and C depend on it.")
assert len(q) == 16, len(q)
w6["open_questions"] = q

(open(out, "w", encoding="utf-8")).write(json.dumps(w6, ensure_ascii=False, indent=2) + "\n")
print("W6 written:", out, "summary chars", len(w6["summary"]), "open questions", len(q))
