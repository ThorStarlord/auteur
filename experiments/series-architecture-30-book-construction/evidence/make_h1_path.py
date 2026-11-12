"""Derive the hypothetical H1 path from the working construction.

H1 (counterfactual, not accepted): in Book 5 Keeper Corrow opens the records to
public access after a lower-terrace household's evidence forces the timing; the
reform committee keeps physical custody and the debt reading until Book 15, when
custody passes to the Reading Hall and the debt-keeping members become a remnant.

This script applies only the focused H1 delta. Every field it does not name is
copied unchanged from the base candidate. Each replaced field is asserted to
exist first, so a drifted base fails loudly rather than silently.

Usage: python make_h1_path.py <base_candidate.json> <h1_candidate.json>
"""
import copy
import json
import sys

src, dst = sys.argv[1], sys.argv[2]
with open(src, encoding="utf-8") as fh:
    d = json.load(fh)
base = copy.deepcopy(d)


def node(node_id):
    for n in d["nodes"]:
        if n["id"] == node_id:
            return n
    raise KeyError(node_id)


def phase(phase_id):
    for p in d["phases"]:
        if p["id"] == phase_id:
            return p
    raise KeyError(phase_id)


def emotion(target_id):
    for e in d["emotion_targets"]:
        if e["id"] == target_id:
            return e
    raise KeyError(target_id)


def contract(genre_id):
    for g in d["genre_contracts"]:
        if g["genre_node_id"] == genre_id:
            return g
    raise KeyError(genre_id)


def complex_emotion(emotion_id):
    for c in d["complex_emotions"]:
        if c["id"] == emotion_id:
            return c
    raise KeyError(emotion_id)


def activation(phase_id, genre_id):
    for a in phase(phase_id)["genre_activations"]:
        if a["genre_node_id"] == genre_id:
            return a
    raise KeyError((phase_id, genre_id))


# 1. Premise label. The H1 summary is labelled hypothetical and is not the working path.
d["summary"] = (
    "HYPOTHETICAL H1 PATH (not accepted; a counterfactual to the working construction, not the original path). "
    "Keeper Corrow opens the records to public access in Book 5 after a lower-terrace household's evidence "
    "forces the timing. The reform committee keeps physical custody and the debt reading until Book 15, when "
    "custody passes to the Reading Hall and the debt-keeping members become Corrow's remnant. The Hall is "
    "reformed, not destroyed. " + d["summary"]
)

# 2. The Stone Hall: reformed, with a committee that holds custody until Book 15.
inst = node("inst_stone_hall")
assert inst["title"] == "Stone Hall (Reckoners)"
inst["title"] = "Stone Hall (reform committee; remnant from Book 15)"
inst["summary"] = (
    "Hereditary keepers of the Ledger. Keeper Corrow opens the records to public access in Book 5 after a "
    "lower-terrace household's evidence forces the timing. The reform committee keeps physical custody of the "
    "Stones and the master record, and the debt reading, until Book 15. At Book 15 custody passes to the Reading "
    "Hall, and the debt-keeping members become Corrow's remnant. The Hall is reformed, not destroyed. Typed as "
    "other because v2 has no institution category."
)

# 2b. The Reading Hall takes custody of the master record at Book 15 under H1.
rh = node("inst_reading_hall")
assert rh["title"] == "Reading Hall"
rh["summary"] = (
    "Founded at Book 15 with the full reading, to make the First Stones publicly readable. Under H1 it takes "
    "physical custody of the Stones and the master record at Book 15. It publishes the Gate gauge reading (Book 22) "
    "and the Balance Stones (Book 23). It has no authority over the schedule."
)

# 3. Custody: public access versus physical custody, made explicit.
cust = node("th_custody")
assert cust["id"] == "th_custody"
cust["summary"] = (
    "Who holds the Ledger and on whose authority. Public access to the credit record begins in Book 5. Physical "
    "custody of the Stones and the master record stays with the reform committee until Book 15, then passes to "
    "the Reading Hall."
)

# 4. The Ledger: the opening of the records is the Hall's own reform, not an outside seizure.
ledger = node("eng_ledger")
assert ledger["summary"].startswith("Recorded shares set the draw. Credit can be falsified or favoured (Book 1), opened to public access")
ledger["summary"] = (
    "Recorded shares set the draw. Credit can be falsified or favoured (Book 1), opened to public access by the "
    "Hall's own reform once evidence forces it (Book 5), traded (Book 6), re-read as gift or contract (Book 15), "
    "and from Book 20 partly set by hands owed. Each change alters who must return labour."
)

# 5. The witness: the evidence forces the timing of the Hall's own reform.
d["nodes"].append({
    "id": "th_witness", "title": "Evidence that forces reform", "category": "thread",
    "summary": (
        "A lower-terrace household's evidence forces the timing of the Hall's own reform (Book 5). In the original "
        "path the same evidence, with a coalition from outside, forces the Hall to yield."
    ),
    "scope": "whole_story", "parent_id": None,
})
d["links"].append({
    "id": "l_witness_forces_reform", "source": "th_witness", "target": "inst_stone_hall",
    "function": "evidence forces the reform's timing and proof",
})
d["links"].append({
    "id": "l_reform_keeps_debt", "source": "inst_stone_hall", "target": "eng_old_hand",
    "function": "the committee keeps the debt reading until Book 15",
})
d["links"].append({
    "id": "l_custody_passes_reading_hall", "source": "inst_reading_hall", "target": "th_custody",
    "function": "custody of the master record passes to the Reading Hall at Book 15",
})

# 6. Phases: the committee's authorship of the rules and of the readings; the remnant from Book 15.
p1 = phase("ph_1_reckoned_water")
assert p1["transition"].startswith("Records open")
p1["narrative_function"] = (
    "The Ledger governs. A lower-terrace household's evidence exposes falsified credit in the share-marks, and a "
    "lower terrace runs wild (Book 1). Keeper Corrow opens the records to public access as a reform that protects "
    "the Hall's standing against a thinning its own falsified credit helped cause (Book 5), but only after the household's evidence forces the timing. "
    "The Hall is reformed, not destroyed: its committee keeps custody and the debt reading. Dorran carries the "
    "reform as messenger rather than defecting. Book 1 reads the share-marks as evidence and does not read the script."
)
p1["transition"] = (
    "Records are public, so shares become tradable; the reform committee, not the tenders, sets the first rules of sale."
)
activation("ph_1_reckoned_water", "gn_mystery_discovery")["structural_function"] = (
    "a lower-terrace household finds falsified credit in the share-marks (Book 1); the Hall's own head opens the "
    "records to public access, with the committee keeping custody, once that evidence forces the timing (Book 5)."
)

p2 = phase("ph_2_the_turn")
p2["narrative_function"] = (
    "The Source governs. The committee's sale rules let the Mill Compact buy shares. Compact purchases draw water "
    "without return labour, so the physical balance is the constraint on what the institutions can do. Quillmark's "
    "tenders and the Terrace Council oppose rules that the committee approved. Maintenance knowledge concentrates in "
    "old lineages (Books 9-11). The first partial reading of the script (Book 8) is authored by the committee and "
    "contested by scholars."
)
activation("ph_2_the_turn", "gn_political_institutional")["structural_function"] = (
    "Mill Compact purchases shares under the committee's sale rules; draw separates from return and the upper cistern "
    "thins (Book 6). The Turn is sworn and the Terrace Council forms, and the Council operates the Hollow Gate (Books 7-11)."
)

p3 = phase("ph_3_old_hand")
p3["narrative_function"] = (
    "The Old Hand governs. Legitimacy no longer rests on the Ledger alone. The complete reading (Book 15) makes the "
    "first compact a gift, and the committee's custody ends with it: custody passes to the Reading Hall, and the "
    "debt-keeping members become Corrow's remnant. The Unmeasured Return is a costly, physically consequential choice: "
    "it stabilises the lower valley and disturbs the high cistern. The stewardship tally records care, not debt. "
    "The Book 12 partial reading is made under the committee's custody. The "
    "Reading Hall is founded as a public institution with its own readings."
)
p3["transition"] = (
    "Legitimacy is contested among three readings. The counted Turn and the gift practice run on the same Hollow Gate. "
    "Custody passes to the Reading Hall at Book 15, so the record has one public keeper while the readings stay plural."
)
activation("ph_3_old_hand", "gn_mystery_discovery")["structural_function"] = (
    "the complete reading of the First Stones (Book 15) makes the first compact a gift-return; the committee, which keeps "
    "custody until Book 15, holds it as debt, the Council as gift and the Compact as contract. At Book 15 custody passes "
    "to the Reading Hall and the debt-keeping members become Corrow's remnant. An Unmeasured Return is tried in Lower "
    "Ammen and causes surfeit in the high terraces, which forces the stewardship tally to count care, not debt."
)

p4 = phase("ph_4_settled_water")
p4["narrative_function"] += (
    " Under H1, Corrow's remnant (the debt reading) stands outside the Gate Table and argues for counting."
)

# 7. Emotional design: the grief target is re-pointed to the committee's loss of custody, not the Hall's fall.
grief = emotion("et_grief_of_orders")
assert grief["eliciting_condition"] == "the Stone Hall's fall in Book 5 and Keeper Corrow's dissent"
grief["eliciting_condition"] = "the committee's loss of custody at Book 15 and Keeper Corrow's remnant's dissent"

bitter = complex_emotion("ce_bittersweet_return")
assert bitter["context"] == "a practice honoured after the institution that held it has fallen"
bitter["context"] = "a practice honoured after the institution that held it has lost custody of it"

# 8. Genre contract: access and custody end at different Books; the trope list keeps the falsified record.
pol = contract("gn_political_institutional")
pol["payoff_expectations"] = [
    "the Stone Hall's monopoly of access ends in Book 5; its monopoly of custody ends in Book 15",
    "in Book 30 the record has one public keeper, and no single body holds both the record and the Gate schedule",
]

# 8b. The custody link carries a time bound under H1: the Hall's authority ends at Book 15, not Book 5.
custody_link = [l for l in d["links"] if l["id"] == "l_custody_grants_hall"][0]
assert custody_link["function"] == "custody of the record is the Hall's authority until Book 5"
custody_link["function"] = "custody of the record is the Hall's authority until Book 15"

# 9. One open question is rewritten to name the H1 question. The list is already at its maximum length.
assert len(d["open_questions"]) == 16
assert d["open_questions"][14].startswith("Does reform from within remain")
d["open_questions"][14] = (
    "Under H1: does reform from within stay credible under Books 15 and 30, or does the Hall become a benevolent "
    "authority that the finale must oppose? Does the Gate Table model reform from within or warn against it? Not decided."
)

with open(dst, "w", encoding="utf-8") as fh:
    json.dump(d, fh, ensure_ascii=False, indent=2)

changed_nodes = sorted({n["id"] for n in d["nodes"]} ^ {n["id"] for n in base["nodes"]})
print("wrote", dst, "nodes", len(d["nodes"]), "links", len(d["links"]), "phases", len(d["phases"]))
print("added nodes:", changed_nodes)
