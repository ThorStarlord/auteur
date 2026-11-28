"""Fresh authentic consequence chain on a new Spring Ledger study: each stage prepares its request through the owner, a fresh agent
answers it, and the answer is completed through the owner. Nothing is replayed.

Stages:
  seed                 seed a new study
  discover-prepare     write the discovery request for an agent
  discover-complete    complete it with the agent's unedited answer
  investigate          prepare the inquiry for a possibility and write its request
  inquiry-complete     complete the inquiry with the agent's unedited answer
  revise-prepare       prepare a revision of the selected alternative and write its request
  revise-complete      complete the revision candidate with the agent's unedited answer
  consequence-prepare  prepare the consequence analysis of the pending revision and write its request
  consequence-complete complete the analysis with the agent's unedited answer
"""
import json
import sys
from pathlib import Path

REPO = Path("H:/GithubRepositories/auteur/.worktrees/grounded-creative-synthesis")
sys.path.insert(0, str(REPO / "scripts"))
sys.path.insert(0, str(REPO / "src"))

import consequence_exercise as ce  # noqa: E402
from auteur.beginner.studio_architecture_discovery import (  # noqa: E402
    complete_architecture_discovery, prepare_architecture_discovery, project_architecture_discoveries,
)

ROOT = Path("C:/Users/Admin/AppData/Local/Temp/claude/e91f3203f308aeba/bd7bca2c-32f1-43e5-ad86-8d497e2b3639/scratchpad/g2")
STUDY = ROOT / "study" / "discovery"
OUT = ROOT / "out"
GOAL = "What promising creative opportunities am I overlooking?"
RUNTIME = "fresh-subagent-grounded-chain"


def write(name, data):
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / name
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) if not isinstance(data, str) else data, encoding="utf-8")
    print("wrote", path)
    return path


def main():
    stage = sys.argv[1]
    arg = sys.argv[2] if len(sys.argv) > 2 else None
    if stage == "seed":
        ce.seed(ROOT / "study")
    elif stage == "discover-prepare":
        store = ce.store_at(STUDY)
        prepare_architecture_discovery(store, goal=GOAL, orientation="full")
        pending = project_architecture_discoveries(store)["pending"]
        write("request-discovery.json", pending["request"])
    elif stage == "discover-complete":
        store = ce.store_at(STUDY)
        pending = project_architecture_discoveries(store)["pending"]
        text = Path(arg).read_text(encoding="utf-8")
        complete_architecture_discovery(store, ce.envelope(pending["request"], text, RUNTIME))
        newest = project_architecture_discoveries(store)["discoveries"][0]
        write("result-discovery.json", newest)
        print("possibilities:", [(p["id"], p["title"]) for p in newest["possibilities"]])
    elif stage == "investigate":
        discovery_sha = json.loads((OUT / "result-discovery.json").read_text(encoding="utf-8"))["request_sha256"]
        ce.investigate(STUDY, discovery_sha, OUT)
    elif stage == "inquiry-complete":
        ce.inquiry_complete(STUDY, Path(arg), OUT)
    elif stage == "revise-prepare":
        inquiry_sha = json.loads((OUT / "inquiry-request-deliberation.json").read_text(encoding="utf-8"))["request_sha256"]
        instruction = Path(arg).read_text(encoding="utf-8").strip()
        ce.revise_prepare(STUDY, inquiry_sha, instruction, OUT)
    elif stage == "revise-complete":
        ce.revise_complete(STUDY, Path(arg), OUT)
    elif stage == "consequence-prepare":
        ce.consequence_prepare(STUDY, OUT)
    elif stage == "consequence-complete":
        ce.consequence_complete(STUDY, Path(arg), OUT)
    else:
        raise SystemExit(f"unknown stage {stage}")


if __name__ == "__main__":
    main()
