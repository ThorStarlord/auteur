"""Probe: assert a finale claim outright, depending on the finale decision. Must be refused (Case 3)."""
import json
import sys
from pathlib import Path

project = Path(sys.argv[1])
out = Path(sys.argv[2])
record = json.loads((project / ".auteur/beginner/studio/canvases/spring-ledger/architecture/books/24/current.json")
                    .read_text(encoding="utf-8"))
artifact = record["artifact"]
for key in ("later_possibilities",):
    for item in artifact[key]:
        if item["id"] == "later-finale-capability":
            item["epistemic_status"] = "asserted"
            item["refs"].append({"kind": "book_element", "id": "dec-finale-mechanism"})
out.write_text(json.dumps(artifact, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("probe written", out)
