"""Replay the author-declared admission rule against the recorded agent-first evidence.

Run from the repository root:  PYTHONPATH=src python docs/qualification-evidence/provenance-authority-20261112/replay_historical_labels.py
Each pair is a recorded host-agent request (its exact packet) and the candidate the agent returned for it.
The rule must admit every historical author_declared label that the recorded author text supports.
"""
import json
from pathlib import Path

from auteur.beginner.studio_architecture import ArchitectureCandidate, _validate_author_provenance
from auteur.host_agent import HostAgentRequest

EVIDENCE = Path("docs/qualification-evidence/agent-first-ontology-20261103")
PAIRS = [
    ("rich-vision-request.json", "rich-vision-candidate.json", "develop"),
    ("revision-request.json", "rich-vision-revised-candidate.json", "revision of rich-vision"),
    ("concept-revision-request.json", "concept-revision-candidate.json", "concept-aware revision"),
    ("sparse-vision-request.json", "sparse-vision-candidate.json", "sparse develop"),
]
rows = []
for request_name, candidate_name, role in PAIRS:
    request = HostAgentRequest(**json.loads((EVIDENCE / request_name).read_text(encoding="utf-8")))
    packet = json.loads(request.user)
    candidate = ArchitectureCandidate.model_validate(json.loads((EVIDENCE / candidate_name).read_text(encoding="utf-8")))
    labelled = sorted(t.id for t in candidate.emotion_targets if t.provenance == "author_declared")
    try:
        _validate_author_provenance(candidate, packet)
        verdict = "admitted"
    except ValueError as exc:
        verdict = f"rejected: {exc}"
    rows.append({"request": request_name, "candidate": candidate_name, "role": role,
                 "author_declared_ids": labelled, "verdict": verdict})
print(json.dumps(rows, indent=2, ensure_ascii=False))

# Mutation checks on the same recorded packet: the rule must refuse unsupported author claims.
import copy

request = HostAgentRequest(**json.loads((EVIDENCE / "revision-request.json").read_text(encoding="utf-8")))
packet = json.loads(request.user)
base = json.loads((EVIDENCE / "rich-vision-revised-candidate.json").read_text(encoding="utf-8"))
mutations = {}
promoted = copy.deepcopy(base)
next(t for t in promoted["emotion_targets"] if t["id"] == "grief")["provenance"] = "author_declared"
mutations["promote agent_proposed 'grief' to author_declared"] = promoted
added = copy.deepcopy(base)
added["emotion_targets"].append({**added["emotion_targets"][0], "id": "awe", "provenance": "author_declared"})
mutations["add new author_declared awe (not in the recorded Vision)"] = added
checks = []
for label, mutated in mutations.items():
    try:
        _validate_author_provenance(ArchitectureCandidate.model_validate(mutated), packet)
        verdict = "admitted"
    except ValueError as exc:
        verdict = f"rejected: {exc}"
    checks.append({"mutation": label, "verdict": verdict})
print(json.dumps(checks, indent=2, ensure_ascii=False))
