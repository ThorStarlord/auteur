"""Representation correction for Book 24 (Cases 1, 2 and 4). Only labels change, and one interpretation is recorded.

The wording of every statement is copied from the working record. Each legacy label is restated in the explicit
form that its source tag supports. Nothing receives an invented reversal, and nothing becomes an author decision.
"""
import json
import sys
from pathlib import Path

project = Path(sys.argv[1])
out = Path(sys.argv[2])
record = json.loads((project / ".auteur/beginner/studio/canvases/spring-ledger/architecture/books/24/current.json")
                    .read_text(encoding="utf-8"))
artifact = record["artifact"]

# Case 1: an untagged source assertion is an assertion of unknown attribution, not an unanswered question.
# Case 2: an agent-proposed assumption with no known reversal stays provisional, with the reversal unknown.
# Case 4: a source-derived statement keeps its source reference, and the agent's contribution is recorded apart.
ATTRIBUTION = {
    "inh-gate-independence": ("unattributed", "asserted"),
    "inh-date": ("derived", "asserted"),
    "assume-p3": ("agent_proposed", "asserted"),
    "assume-p4": ("agent_proposed", "asserted"),
    "assume-p5": ("agent_proposed", "asserted"),
    "assume-p7": ("agent_proposed", "asserted"),
    "assume-p8": ("agent_proposed", "asserted"),
    "assume-p9": ("agent_proposed", "asserted"),
    "assume-p10": ("agent_proposed", "asserted"),
}
INTERPRETATION = {
    "inh-date": "Agent contribution: the valley now knows how long it has, so the labour question cannot wait for Books 27 to 29.",
}


def walk(node):
    if isinstance(node, dict):
        if "id" in node and "text" in node and node["id"] in ATTRIBUTION:
            yield node
        for value in node.values():
            yield from walk(value)
    elif isinstance(node, list):
        for value in node:
            yield from walk(value)


changed = []
for item in walk(artifact):
    attribution, status = ATTRIBUTION[item["id"]]
    item.pop("provenance", None)
    item["attribution"] = attribution
    item["epistemic_status"] = status
    if item["id"] in INTERPRETATION:
        item["interpretation"] = INTERPRETATION[item["id"]]
    changed.append(item["id"])

out.write_text(json.dumps(artifact, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("labelled:", sorted(changed))
print("targets:", len(changed), "->", out)
