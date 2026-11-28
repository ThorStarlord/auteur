import json, sys
from pathlib import Path
from auteur.beginner.studio_architecture_synthesis import project_architecture_synthesis
from auteur.beginner.studio_store import CanvasStore
store = CanvasStore(Path(sys.argv[1]), "wandering-islands")
view = project_architecture_synthesis(store)
print("top keys:", sorted(view.keys()))
rows = view.get("history") or view.get("syntheses") or []
for row in rows:
    print(row["request_sha256"][:12], row["standing"], row["status"], "culmination" if row["inputs"].get("culmination") else "plain", "result" if row["result"] else "-")
