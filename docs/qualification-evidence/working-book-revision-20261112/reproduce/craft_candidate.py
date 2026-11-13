"""Hypothetical working revision: a craft-mark alone no longer satisfies the lineage's proof-of-training condition.

The premise is recorded as a hypothetical assumption, not as canon. Statements that depend on it are conditional on it.
Series references, author decisions and source-derived statements keep their wording; only where an interpretation is
the working contribution does the text change. Writes two candidates: the clean revision, and a probe that also edits
an element outside the declared scope, to show the review blocking it.
"""
import copy
import json
import sys
from pathlib import Path

project = Path(sys.argv[1])
out = Path(sys.argv[2])
record = json.loads((project / ".auteur/beginner/studio/canvases/spring-ledger/architecture/books/24/current.json")
                    .read_text(encoding="utf-8"))
base = record["artifact"]

PREMISE = "assume-witnessed-mark"
COLLECTIONS = ["inherited", "engines", "agents", "local_resolution", "series_consequences", "later_possibilities",
               "assumptions", "alternatives", "unresolved", "open_author_decisions"]


def find(artifact, identifier):
    """Return the element dict and the list that holds it."""
    for key in COLLECTIONS:
        for item in artifact.get(key, []):
            if item["id"] == identifier:
                return item, artifact[key]
    if artifact["function"]["id"] == identifier:
        return artifact["function"], None
    choice = artifact["choice"]
    if choice["id"] == identifier:
        return choice, None
    for key in ("options", "costs_kept_visible"):
        for item in choice[key]:
            if item["id"] == identifier:
                return item, choice[key]
    if choice["transformation"]["id"] == identifier:
        return choice["transformation"], None
    for edge in artifact["typed_edges"]:
        if edge["id"] == identifier:
            return edge, artifact["typed_edges"]
    raise KeyError(identifier)


def restate(identifier, *, text=None, attribution="agent_proposed", status="asserted", extra_refs=(),
            interpretation=None, function=None, reversal=None, keep_refs=True):
    artifact = counterfactual
    item, _ = find(artifact, identifier)
    item.pop("provenance", None)
    if text is not None:
        item["text"] = text
    item["attribution"] = attribution
    item["epistemic_status"] = status
    if not keep_refs:
        item["refs"] = []
    for ref in extra_refs:
        if ref not in item["refs"]:
            item["refs"].append(ref)
    if interpretation is not None:
        item["interpretation"] = interpretation
    if function is not None:
        item["function"] = function
    if reversal is not None:
        item["reversal"] = reversal
    return item


def book_ref(identifier):
    return {"kind": "book_element", "id": identifier}


counterfactual = copy.deepcopy(base)

# The premise: a hypothetical working assumption, with the reversal it would be undone by.
counterfactual["assumptions"].append({
    "id": PREMISE, "text": "Hypothetical working premise, not canon: a craft-mark alone no longer satisfies the lineage's "
                            "proof-of-training condition. The mark must also carry a lineage hand's attestation that the "
                            "repair was done as taught.",
    "refs": [book_ref("eng-record-form")], "attribution": "agent_proposed", "epistemic_status": "hypothetical",
    "reversal": "Reverse if the lineage again accepts a craft-mark alone as proof of training.",
})

restate("eng-record-form", status="conditional", extra_refs=[book_ref(PREMISE)],
        text="Lineage hands and the cohort meet the Right's training condition through a craft-mark that a lineage hand attests. "
             "The record shows who can repair, not who owes. Under the working premise the mark no longer proves training alone.")
engine = find(counterfactual, "eng-record-form")[0]
engine["choice"] = "The craft-mark, attested by a lineage hand at the repair."
engine["consequence"] = ("Under the working premise the condition is met only where a lineage hand attests the mark; the "
                         "cohort's own mark is necessary but not sufficient.")
engine["changed_state"] = ("The valley holds the same four kinds of record. A craft-mark counts as training only with an "
                           "attestation.")

restate("choice-craft-mark", status="asserted",
        text="The setting is unchanged. Hesper's third path still records capability, but a repair counts as training only "
             "when a lineage hand attests it.")
restate("opt-craft-mark", status="asserted",
        text="A third path Hesper proposes: teacher and learner each cut a mark on the channel stone. A lineage hand attests "
             "the repair, because under the working premise the mark alone is not proof of training.")
restate("trans-hesper-idrun", status="conditional", extra_refs=[book_ref(PREMISE)],
        text="Hesper moves from 'abundance needs no work' to 'the work is real and the water sees it, but people need not "
             "count it'. Under the working premise her route still needs a lineage hand's attestation, so her independence "
             "is partial. The granddaughter sets evidence against the record, and the evidence is an attested mark.")

counterfactual["choice"]["costs_kept_visible"].append({
    "id": "cost-lineage-attestation",
    "text": "Each attested repair needs a lineage hand present at the work, so the uncounted crew is not fully independent "
            "of the lineage under the working premise.",
    "refs": [book_ref("choice-craft-mark")], "attribution": "agent_proposed", "epistemic_status": "conditional",
})
counterfactual["choice"]["costs_kept_visible"][-1]["refs"].append(book_ref(PREMISE))

restate("res-craft-mark-provisional", status="conditional", extra_refs=[book_ref(PREMISE)], attribution="agent_proposed",
        text="Ysa Trant accepts a craft-mark as proof of training only with a lineage hand's attestation. The Council accepts "
             "the attested pair as meeting the Right's condition for one review cycle. The mark alone does not settle the "
             "condition.")
restate("res-first-group", status="conditional", extra_refs=[book_ref(PREMISE)], attribution="agent_proposed",
        text="A first group of outside-lineage hands is trained through attested repairs. The size is unstated, and the group "
             "narrows the labour gap without closing it.")

restate("cons-capability-record", status="conditional", extra_refs=[book_ref(PREMISE)], attribution="agent_proposed",
        text="A capability record shows who can repair. Under the working premise a repair counts toward training only with a "
             "lineage attestation. The record does not change who is counted for draw.")
restate("cons-labour-readiness", status="conditional", extra_refs=[book_ref(PREMISE)], attribution="agent_proposed",
        text="Labour readiness has begun: trained people exist where a lineage hand attests their repairs, and a visible "
             "shortfall remains.")
restate("later-finale-capability", status="conditional", extra_refs=[book_ref(PREMISE)], attribution="agent_proposed",
        text="Any finale mechanism can draw on the capability record, but under the working premise the record also needs a "
             "lineage attestation. Pair-hands under A, rota under B and the pre-drawn panel under C each then need a lineage "
             "hand present. None of them is chosen here.")
restate("later-books-25-26", status="asserted", attribution="agent_proposed",
        text="Books 25 and 26 receive two pressures: whether attestations can be withheld or favoured, and hand-light draw "
             "against the conversion, now with a concrete case.")

restate("assume-p5", status="asserted", attribution="agent_proposed", reversal=None,
        text="The craft-mark is a record of capability, cut by teacher and learner on the channel stone and held by no "
             "institution. Under the working premise it is not sufficient proof of training alone.")
restate("assume-p6", status="asserted", attribution="agent_proposed", reversal=None,
        text="The Council accepts attested craft-marks for one review cycle. This does not decide author-reserved choice 7.")

restate("inh-right-condition", attribution="derived", status="asserted",
        interpretation="Working counterfactual: under the premise the training condition is met only where a lineage hand "
                       "attests the training.")

for edge in counterfactual["typed_edges"]:
    if edge["id"] == "edge-capability-hands":
        edge["function"] = "The attested mark shows who can give return labour; it does not change who is counted for draw."
    if edge["id"] == "edge-capability-lineage":
        edge["function"] = "A lineage attestation is needed for a mark to count as training, which tests the lineages' monopoly on attesting repairs."

# Probe: the same candidate, with one element outside the declared scope also edited.
probe = copy.deepcopy(counterfactual)
find(probe, "assume-p4")[0]["text"] = "Gift-hands without skill can damage a channel through the silted section, and the valley checks each season."

out.write_text(json.dumps(counterfactual, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
(out.parent / "craft-probe-unexpected.json").write_text(json.dumps(probe, ensure_ascii=False, indent=2) + "\n",
                                                       encoding="utf-8")
print("wrote", out, "and probe")
