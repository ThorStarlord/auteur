"""Print a compact view of the accepted Wandering Islands architecture and its persistent questions (read-only)."""
import json
import sys
from pathlib import Path

from auteur.beginner.studio_architecture import _candidate
from auteur.beginner.studio_architecture_question_projection import project_architecture_questions
from auteur.beginner.studio_store import CanvasStore

project = Path(sys.argv[1])
store = CanvasStore(project, "wandering-islands")
current = _candidate(store)
cand = current["candidate"]
print("request_sha256:", current["request_sha256"])
print("keys:", sorted(cand.keys()))
print("nodes:", len(cand["nodes"]))
for node in cand["nodes"]:
    text = node.get("text") or node.get("statement") or node.get("description") or ""
    print(f"  {node['id']} [{node.get('kind')}] {node.get('title', '')} :: {str(text)[:150]}")
print("phases:", [(p.get("id"), p.get("title") or p.get("name")) for p in cand.get("phases", [])])
print("interpretations:")
for item in cand.get("interpretations", []):
    print(f"  {item['id']} affects={item['affects']} decision={item.get('author_decision_required')}")
questions = project_architecture_questions(store)
rows = questions.get("questions") or questions.get("items") or []
print("persistent questions:", len(rows))
for row in rows[:30]:
    print("  ", json.dumps(row, ensure_ascii=False)[:260])
