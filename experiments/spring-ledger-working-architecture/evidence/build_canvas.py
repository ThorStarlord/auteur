"""Build a disposable Studio project for the consolidated architecture, using main's bridge CLI.

Usage: python build_canvas.py <worktree_root> <scratch_project_root> <canvas_id>

Records, in order: the canvas and its story vision (the author's identity text plus the four
verbatim directives), the four author intentions, the W6 baseline through prepare and
complete-file, and the five provisional concepts. Then it captures the cold-start access
surfaces with `show`, `resume` and `intentions`. All product output is written to
<scratch>/<canvas>-run/. Nothing is written into the repository.
"""
import json
import os
import subprocess
import sys
from pathlib import Path

root = Path(sys.argv[1]).resolve()
proj = Path(sys.argv[2]).resolve()
canvas = sys.argv[3]
pkg = root / "experiments" / "spring-ledger-working-architecture"
out = proj.parent / f"{canvas}-run"
out.mkdir(parents=True, exist_ok=True)
env = dict(os.environ, PYTHONPATH=str(root / "src"), PYTHONUTF8="1")
bridge = [sys.executable, "-m", "auteur.beginner.studio_architecture", "--project", str(proj), "--canvas", canvas]
SRC = "3168963b7df262d81354d3fec2cf8ef2ec74cd4b"


def run(args, capture=None):
    res = subprocess.run(bridge + args, capture_output=True, text=True, env=env, cwd=str(root))
    if res.returncode != 0:
        raise SystemExit(f"bridge failed: {args}\n{res.stderr}")
    if capture:
        Path(capture).write_text(res.stdout, encoding="utf-8")
    return res.stdout


def git_json(path):
    return json.loads(subprocess.run(["git", "-C", str(root), "show", f"{SRC}:{path}"],
                                     capture_output=True, check=True, text=True).stdout)


intents = [git_json(f"experiments/series-architecture-30-book-v1/evidence/intention-{n}.json")["intention"]
           for n in range(1, 5)]
identity = ("The Spring Ledger is a long-form fantasy Series exploring a shared water commons, the institutions that govern it, "
            "the meanings attached to obligation, and the consequences of changing collective practices. Its identity should preserve "
            "wonder, discovery, everyday belonging, meaningful relationships, institutional transformation, material consequences, and "
            "the possibility of hopeful flourishing. Do not turn it into a generic escalating-villain epic.")
vision = identity + "\n\n" + "\n\n".join(f"{i['title']}: {i['directive']}" for i in intents)

from auteur.beginner.studio_store import CanvasStore  # noqa: E402
store = CanvasStore(proj, canvas)
store.create()
store.apply("create-item", expected_revision=0, command_id="vision-created", payload={
    "item": {"id": "story-vision", "kind": "note", "title": "Story Vision", "content": vision},
    "position": {"x": 20, "y": 50}})

d = out / "intent"
d.mkdir(exist_ok=True)
for i, rec in enumerate(intents, 1):
    (d / f"directive-{i}.txt").write_text(rec["directive"], encoding="utf-8")
    run(["keep-intention", "--title", rec["title"], "--directive-file", str(d / f"directive-{i}.txt")],
        capture=str(out / f"keep-{i}.json"))

run(["prepare"], capture=str(out / "baseline-prepare.json"))
run(["complete-file", "--candidate", str(pkg / "02-working-candidate-W6.json")],
    capture=str(out / "baseline-complete.json"))

for concept in sorted((pkg / "evidence" / "concepts").glob("*.json")):
    run(["record-concept", "--concept", str(concept)], capture=str(out / f"concept-{concept.stem}.json"))

run(["show"], capture=str(out / "show.json"))
run(["resume"], capture=str(out / "resume.json"))
run(["intentions"], capture=str(out / "intentions.json"))
print("canvas built:", canvas, "->", out)
