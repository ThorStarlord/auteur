"""Produce the hypothetical revised working candidate (H1 + witness-led repair R-A).

Edits are minimal and targeted: every field not listed here is copied unchanged from the original.
Usage: python make_revised_candidate.py <original.json> <revised.json>
"""
import json
import sys

src, dst = sys.argv[1], sys.argv[2]
d = json.load(open(src, encoding="utf-8"))
nodes = {n["id"]: n for n in d["nodes"]}
phases = {p["id"]: p for p in d["phases"]}
emos = {e["id"]: e for e in d["emotion_targets"]}
contracts = {g["genre_node_id"]: g for g in d["genre_contracts"]}

d["summary"] = (
    "HYPOTHETICAL REVISION (not accepted; author-proposed counterfactual for an architecture exercise). "
    "Counterfactual H1: the Stone Hall's own head, Keeper Corrow, opens the sealed records as a reform "
    "after a household's evidence forces the timing; the Hall is reformed rather than destroyed and "
    "its committee keeps the debt reading. Repair R-A keeps Idrun's agency as the witness whose evidence "
    "forces the reform. " + d["summary"]
)
nodes["inst_stone_hall"]["title"] = "Stone Hall (reform committee and remnant)"
nodes["inst_stone_hall"]["summary"] = (
    "Hereditary keepers of the Ledger. Keeper Corrow opens the sealed records as a reform (Book 5) after "
    "household evidence forces the timing. The committee keeps the debt reading to protect its own "
    "legitimacy, and Dorran carries the reform as messenger. The Hall is reformed, not destroyed."
)
nodes["eng_ledger"]["summary"] = (
    "Recorded shares set the draw. Credit can be falsified or favoured (Book 1), opened by the Hall's own "
    "reform once evidence forces it (Book 5), traded under the reform's rules (Book 6), and re-read as "
    "gift or contract (Book 15). Each change alters who must return labour."
)
nodes["th_custody"]["summary"] = (
    "Who holds the Ledger and on whose authority. Custody passes from a sealed house to a reform committee "
    "(Book 5) and then to a plural body (Book 15 onward)."
)
nodes["th_witness"] = {
    "id": "th_witness", "title": "Evidence that forces reform", "category": "thread",
    "summary": "A lower-terrace household's record and its wild channel force the Hall to open its records. "
               "Evidence, not seizure, is the protagonist's lever. Added by revision R-A.",
}
d["nodes"].append(nodes["th_witness"])
d["links"].append({"id": "l_witness_forces_reform", "source": "th_witness", "target": "inst_stone_hall",
                   "function": "evidence forces the reform's timing and proof"})
d["links"].append({"id": "l_reform_keeps_debt", "source": "inst_stone_hall", "target": "eng_old_hand",
                   "function": "the reform committee keeps the debt reading to protect its own legitimacy"})

phases["ph_1_reckoned_water"]["narrative_function"] = (
    "The Ledger governs. A lower-terrace household's record exposes falsified credit and a wild channel "
    "(Book 1). The Stone Hall's head, Keeper Corrow, opens the sealed records as a reform to protect the "
    "Hall's standing against thinning (Book 5), but only after the household's evidence forces the timing. "
    "The Hall is reformed, not destroyed; its committee keeps the debt reading. Dorran carries the reform "
    "as messenger rather than defecting."
)
phases["ph_1_reckoned_water"]["transition"] = (
    "Records open, so shares become tradable; the reform committee, not the tenders, sets the first rules of sale."
)
phases["ph_2_the_turn"]["narrative_function"] = (
    "The Source governs. The reform's sale rules let the Mill Compact buy shares; draw separates from return "
    "and the upper cistern thins (Book 6). Quillmark's tenders and the Terrace Council oppose rules the reform "
    "committee approved. Partial readings of the Stones (Book 8) are authored by the committee and contested by scholars."
)
phases["ph_3_old_hand"]["narrative_function"] = (
    "The Old Hand governs. The complete reading of the First Stones (Book 15) makes the first compact a gift. "
    "The reform committee must now choose between its legitimacy as the debt-keeping Hall and the gift "
    "reading that would undo it; the Council and the Compact press their readings. The Unmeasured Return is "
    "tried in Lower Ammen; its surfeit in the high terraces forces a stewardship tally. The Reading Hall is founded."
)

emos["et_anger_at_hidden_credit"]["intended_effect"] = (
    "unease that an institution must be forced into correcting itself, and that its correction still costs the wronged"
)
emos["et_anger_at_hidden_credit"]["eliciting_condition"] = (
    "the falsified lower-terrace share in Book 1, and the committee's partial correction in Book 5"
)

contracts["gn_political_institutional"]["narrative_engine"] = (
    "institutions reform or resist from within; legitimacy is contested by people who once held it"
)
contracts["gn_political_institutional"]["trope_functions"] = [
    "the reform that protects the reformer", "the compromise that feeds a new market",
]

d["open_questions"].append(
    "Does reform from within stay credible under Books 15 and 30, or does the Hall become a benevolent "
    "authority that the finale must then oppose? (Introduced by hypothetical H1.)"
)
json.dump(d, open(dst, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("wrote", dst, "nodes", len(d["nodes"]), "links", len(d["links"]), "phases", len(d["phases"]))
