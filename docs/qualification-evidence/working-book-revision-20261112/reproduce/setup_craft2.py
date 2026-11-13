"""Disposable Spring Ledger canvas: vision, intentions, Book 24 source, and the W6 Series baseline via the Studio bridge."""
import json, os, re, subprocess, sys
from pathlib import Path

ROOT = Path("H:/GithubRepositories/auteur-book-revision")
SCR = Path(sys.argv[1])
PKG = SCR / "spring"
PROJ = SCR / "craft2" / "project"
CANVAS = "spring-ledger"
OUT = SCR / "craft2" / "out"
OUT.mkdir(parents=True, exist_ok=True)
env = dict(os.environ, PYTHONPATH=str(ROOT / "src"), PYTHONUTF8="1")
sys.path.insert(0, str(ROOT / "src"))

from auteur.beginner.studio_store import CanvasStore  # noqa: E402

def run(module, *args, capture=None):
    cmd = [sys.executable, "-m", module, "--project", str(PROJ), "--canvas", CANVAS, *args]
    res = subprocess.run(cmd, capture_output=True, text=True, env=env, cwd=str(ROOT))
    if capture:
        Path(capture).write_text(res.stdout, encoding="utf-8")
    if res.returncode != 0:
        print("FAILED", args, res.stdout[-800:], res.stderr[-800:])
        raise SystemExit(1)
    return res.stdout

identity = ("The Spring Ledger is a long-form fantasy Series exploring a shared water commons, the institutions that govern it, "
            "the meanings attached to obligation, and the consequences of changing collective practices. Its identity should preserve "
            "wonder, discovery, everyday belonging, meaningful relationships, institutional transformation, material consequences, and "
            "the possibility of hopeful flourishing. Do not turn it into a generic escalating-villain epic.")
intent_md = (PKG / "03-author-intentions.md").read_text(encoding="utf-8")
intents = re.findall(r"### (.+?)\n\nRecord `(intention-[0-9a-f]+)`\n\n> (.+?)\n", intent_md)
assert len(intents) >= 4, intents
intents = intents[:4]
vision = identity + "\n\n" + "\n\n".join(f"{title}: {directive}" for title, _id, directive in intents)

store = CanvasStore(PROJ, CANVAS)
store.create()
store.apply("create-item", expected_revision=0, command_id="vision-created", payload={
    "item": {"id": "story-vision", "kind": "note", "title": "Story Vision", "content": vision},
    "position": {"x": 20, "y": 50}})
fn = (PKG / "book-24-function.corrected-2.md").read_text(encoding="utf-8")
store.apply("create-item", expected_revision=store.load().revision, command_id="book-24-source", payload={
    "item": {"id": "book-24-source", "kind": "note", "title": "Book 24 cold-start function (noncanonical source)",
             "group": "book-24", "content": fn},
    "position": {"x": 20, "y": 200}})
task = (PKG / "00-task.md").read_text(encoding="utf-8")
block = re.search(r"((?:^> .*\n?)+)", task, re.M).group(1)
responsibility = "\n".join(line[2:] for line in block.splitlines() if line.startswith("> "))
store.apply("create-item", expected_revision=store.load().revision, command_id="book-24-responsibility", payload={
    "item": {"id": "book-24-responsibility", "kind": "note", "title": "Author's Book 24 responsibility (verbatim)",
             "group": "book-24", "content": responsibility},
    "position": {"x": 20, "y": 380}})
(OUT / "responsibility.txt").write_text(responsibility, encoding="utf-8")

d = OUT / "intent"; d.mkdir(exist_ok=True)
for i, (title, _id, directive) in enumerate(intents, 1):
    (d / f"directive-{i}.txt").write_text(directive, encoding="utf-8")
    run("auteur.beginner.studio_architecture", "keep-intention", "--title", title,
        "--directive-file", str(d / f"directive-{i}.txt"), capture=str(OUT / f"keep-{i}.json"))

run("auteur.beginner.studio_architecture", "prepare", capture=str(OUT / "series-prepare.json"))
run("auteur.beginner.studio_architecture", "complete-file", "--candidate", str(PKG / "02-working-candidate-W6.json"),
    capture=str(OUT / "series-complete.json"))
print("series status:", json.loads((OUT / "series-complete.json").read_text(encoding="utf-8")).get("status"))
print("intentions:", len(intents), "responsibility chars:", len(responsibility), "source chars:", len(fn))
