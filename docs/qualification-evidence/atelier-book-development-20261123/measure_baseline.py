"""Measure the same author task on a revision of main: revise one Book 24 element that refers to the Ledger engine.

Usage: PYTHONPATH=<main checkout>/src python measure_baseline.py <main sha> <out.json>
It seeds a disposable Spring Ledger project, then does the task the only way main offers: the Working Book CLI.
A deterministic stand-in plays the coding agent. It records which steps exist and how much JSON the author must read.
"""
import json, os, subprocess, sys, tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "scripts"))
import seed_series_context_study as seed  # noqa: E402

sha, out = sys.argv[1], Path(sys.argv[2])
project = Path(tempfile.mkdtemp()) / "linked"
seed.seed_spring(project)
env = dict(os.environ, PYTHONUTF8="1")
base = [sys.executable, "-m", "auteur.series.working_book_architecture", "--project", str(project), "--canvas", seed.SPRING]


def run(*args):
    r = subprocess.run([*base, *args], capture_output=True, text=True, encoding="utf-8", env=env)
    return r.returncode, r.stdout


steps = []
code, text = run("book-prepare", "--book", "24", "--instruction", "Make the cost of refusing the count visible.",
                 "--target", "eng-record-form")
steps.append({"who": "author, in a terminal", "command": "book-prepare --instruction --target", "exit": code, "output_chars": len(text)})
current = json.loads((project / ".auteur/beginner/studio/canvases" / seed.SPRING / "architecture/books/24/current.json").read_text(encoding="utf-8"))
artifact = current["artifact"]
for element in artifact["engines"]:
    if element["id"] == "eng-record-form":
        element.pop("provenance", None); element["attribution"] = "agent_proposed"; element["epistemic_status"] = "asserted"
        element["text"] += " (revised)"
candidate = project.parent / "candidate.json"; candidate.write_text(json.dumps(artifact), encoding="utf-8")
code, text = run("book-complete-file", "--book", "24", "--candidate", str(candidate))
review = json.loads(text)["review"]
steps.append({"who": "coding agent", "command": "book-complete-file", "exit": code, "output_chars": len(text),
              "review_json_chars": len(json.dumps(review, indent=2, ensure_ascii=False))})
code, text = run("book-apply-review", "--book", "24", "--request-sha256", review["request_sha256"])
steps.append({"who": "author, in a terminal, copying a 64-character identity", "command": "book-apply-review --request-sha256",
              "exit": code, "output_chars": len(text)})
import auteur  # the package the CLI runs (PYTHONPATH), not this checkout
package = Path(auteur.__file__).parent
studio_has_route = (package / "beginner/studio_book_development.py").exists()
out.write_text(json.dumps({
    "revision": sha, "package": str(package), "task": "revise Book 24 element eng-record-form, which records a reference to eng_ledger",
    "studio_route_for_book_development": studio_has_route,
    "steps": steps,
    "review_format": "raw JSON with element ids (changes, preserved ids, consequence candidates, series consequences)",
    "atlas_return": "not applicable: the work happens outside the Studio",
}, indent=2), encoding="utf-8")
print(out.read_text(encoding="utf-8"))
