"""Print a compact, read-only view of one stored synthesis result (argv: project, request sha, optional width)."""
import json
import sys
from pathlib import Path

from auteur.beginner.studio_architecture_synthesis import _root
from auteur.beginner.studio_store import CanvasStore

project, sha = Path(sys.argv[1]), sys.argv[2]
width = int(sys.argv[3]) if len(sys.argv) > 3 else 220
store = CanvasStore(project, "wandering-islands")
result = json.loads((_root(store) / "requests" / sha / "result.json").read_text(encoding="utf-8"))["answer"]


def cut(value, n=width):
    text = " ".join(str(value).split())
    return text if len(text) <= n else text[: n - 1] + "…"


print("SHA", sha)
print("KEYS", list(result.keys()))
for stage in result.get("trajectory", []):
    print(f"S{stage.get('id', '?')} book={stage.get('book')} {stage.get('horizon')} basis={stage.get('basis')}")
    print("   dev:", cut(stage.get("development")))
    print("   becomes:", cut(stage.get("becomes_available")))
    print("   changes:", cut(stage.get("changes")))
for rel in result.get("relations", []):
    print(f"R {rel.get('kind')} {rel.get('between')} dep={rel.get('dependence')}: {cut(rel.get('reason'))}")
if result.get("culmination"):
    cul = result["culmination"]
    print("CULMINATION:", cut(cul.get("statement"), 300))
    print("   necessary:", cut(cul.get("necessary"), 300))
    print("   enrichment:", cut(cul.get("enrichment"), 300))
    print("   standalone:", cut(cul.get("standalone_value"), 300))
for path in result.get("alternative_paths", []):
    print("A", path.get("viability"), "|", cut(path.get("ordering")))
    print("   effect:", cut(path.get("effect")))
for opp in result.get("opportunities", []):
    print("O", opp.get("developments") or opp.get("between") or "", "|", cut(opp.get("text") or opp.get("statement") or opp))
print("READER:", cut(result.get("reader_experience"), 400))
print("OPEN:", [cut(item, 160) for item in result.get("open_decisions", [])])
print("UNCERTAINTY:", [cut(item, 160) for item in (result.get("uncertainty") if isinstance(result.get("uncertainty"), list) else [result.get("uncertainty")])])
