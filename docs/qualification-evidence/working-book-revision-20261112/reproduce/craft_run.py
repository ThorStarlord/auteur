"""Clean Book 24 walkthrough on the final code: develop, representation revision, counterfactual, probes, withdrawal.

Every Book step is a real CLI call in a separate process. Every output is written to out/. Probes are labelled as
probes and are not counted as evidence of acceptance. Usage: python craft_run.py <scratch dir> <repo src dir>
"""
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

SCR = Path(sys.argv[1])
SRC = Path(sys.argv[2])
REPO_DOC = SRC.parent / "docs/qualification-evidence/working-book-architecture-20261112/book-24-candidate.json"
PROJ = SCR / "craft2" / "project"
OUT = SCR / "craft2" / "out"
CANVAS = "spring-ledger"
OUT.mkdir(parents=True, exist_ok=True)
ENV = dict(os.environ, PYTHONPATH=str(SRC), PYTHONUTF8="1")
MODULE = "auteur.series.working_book_architecture"
EPOCH = "2026-11-13T00:00:00+00:00"


def book(*args, name):
    result = subprocess.run([sys.executable, "-m", MODULE, "--project", str(PROJ), "--canvas", CANVAS, *args],
                            capture_output=True, text=True, env=ENV, cwd=str(SRC.parent))
    (OUT / f"{name}.json").write_text(result.stdout or "{}", encoding="utf-8")
    try:
        payload = json.loads(result.stdout or "{}")
    except json.JSONDecodeError:
        payload = {"error": result.stderr[-400:]}
    return result.returncode, payload


def python(script, *args):
    subprocess.run([sys.executable, str(SCR / "craft" / script), *args], check=True, env=ENV)


def snapshot(name):
    files = {}
    for path in sorted(PROJ.rglob("*")):
        if path.is_file():
            files[path.relative_to(PROJ).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    (OUT / f"{name}.json").write_text(json.dumps(files, indent=2, sort_keys=True), encoding="utf-8")
    return files


def changed(before, after):
    return sorted(k for k in set(before) | set(after) if before.get(k) != after.get(k))


summary = {"steps": []}


def record(label, code, payload, **extra):
    entry = {"step": label, "exit": code, **extra}
    if "status" in payload:
        entry["status"] = payload["status"]
    if "result" in payload:
        entry["result"] = payload["result"]
    if "error" in payload:
        entry["error"] = payload["error"][:300]
    summary["steps"].append(entry)
    print(json.dumps(entry, ensure_ascii=False)[:400])


CRAFT_TARGETS = ["eng-record-form", "choice-craft-mark", "opt-craft-mark", "trans-hesper-idrun",
                 "res-craft-mark-provisional", "res-first-group", "cons-capability-record", "cons-labour-readiness",
                 "later-finale-capability", "later-books-25-26", "assume-p5", "assume-p6", "inh-right-condition"]
REP_TARGETS = ["inh-gate-independence", "inh-date", "assume-p3", "assume-p4", "assume-p5", "assume-p7",
               "assume-p8", "assume-p9", "assume-p10"]
CRAFT_INSTRUCTION = ("Hypothetical working revision, not canon: a craft-mark alone no longer satisfies the lineage's "
                     "proof-of-training condition. Revise the elements this changes. Keep unrelated elements, Series "
                     "references and author decisions as they are. Do not choose a finale or an accepted ending.")
REP_INSTRUCTION = ("Representation correction only, with no change to any statement's wording. Restate each listed "
                   "element's source attribution and working status in the explicit form. An untagged source assertion "
                   "is asserted with unknown attribution, not an open question. An assumption without a known reversal "
                   "stays asserted, with the reversal unknown. A source-derived statement keeps its source reference, "
                   "and the agent's contribution is recorded as interpretation.")


def targets(names):
    flat = []
    for name in names:
        flat += ["--target", name]
    return flat


# 1. Disposable canvas: W6 Series baseline, intentions, Book 24 source (scratch setup, not Book operations).
subprocess.run([sys.executable, str(SCR / "craft" / "setup_craft2.py"), str(SCR)], check=True, env=ENV)
summary["canvas"] = "disposable canvas built from the W6 baseline and the Book 24 source items"

# 2. Develop the Book 24 working architecture from the recorded candidate (legacy form, accepted by develop).
code, payload = book("book-prepare", "--book", "24", name="01-develop-prepare")
record("develop prepare", code, payload)
code, payload = book("book-complete-file", "--book", "24", "--candidate", str(REPO_DOC), name="02-develop-complete")
record("develop complete", code, payload)
code, resume = book("book-resume", "--book", "24", name="03-resume-baseline")
record("resume baseline", code, resume, revision=resume.get("revision", {}).get("number"),
       semantics=resume.get("packet", {}).get("semantics"))
snap0 = snapshot("snap-00-baseline")

# 3. Representation correction (Cases 1, 2 and 4).
python("rev1_candidate.py", str(PROJ), str(OUT / "rev1-candidate.json"))
code, payload = book("book-prepare", "--book", "24", "--instruction", REP_INSTRUCTION, *targets(REP_TARGETS),
                     name="04-rep-prepare")
record("representation prepare", code, payload)
snap_rep_before = snapshot("snap-01-before-representation")
code, payload = book("book-complete-file", "--book", "24", "--candidate", str(OUT / "rev1-candidate.json"),
                     name="05-rep-complete")
record("representation complete", code, payload, applicable=payload.get("review", {}).get("applicable"))
rep_sha = payload.get("review", {}).get("request_sha256")
code, payload = book("book-apply-review", "--book", "24", "--request-sha256", rep_sha, name="06-rep-apply")
record("representation apply", code, payload)
code, payload = book("book-apply-review", "--book", "24", "--request-sha256", rep_sha, name="07-rep-apply-again")
record("representation re-apply", code, payload)
code, resume = book("book-resume", "--book", "24", name="08-resume-after-representation")
record("resume after representation", code, resume, revision=resume.get("revision", {}).get("number"))
snap_rep_after = snapshot("snap-02-after-representation")
summary["representation_audit"] = changed(snap_rep_before, snap_rep_after)

# 4. Counterfactual: a craft-mark alone no longer satisfies the proof-of-training condition.
python("craft_candidate.py", str(PROJ), str(OUT / "craft-candidate.json"))
code, payload = book("book-prepare", "--book", "24", "--instruction", CRAFT_INSTRUCTION, *targets(CRAFT_TARGETS),
                     name="09-craft-prepare-probe")
record("counterfactual prepare (probe attempt)", code, payload)
code, payload = book("book-complete-file", "--book", "24", "--candidate", str(OUT / "craft-probe-unexpected.json"),
                     name="10-craft-probe-complete")
record("PROBE out-of-scope edit: completion", code, payload,
       applicable=payload.get("review", {}).get("applicable"),
       unexpected=[u["id"] for u in payload.get("review", {}).get("unexpected_changes", [])])
probe_sha = payload.get("review", {}).get("request_sha256")
code, payload = book("book-apply-review", "--book", "24", "--request-sha256", probe_sha, name="11-craft-probe-apply")
record("PROBE apply of blocked review", code, payload)

code, payload = book("book-prepare", "--book", "24", "--instruction", CRAFT_INSTRUCTION, *targets(CRAFT_TARGETS),
                     name="12-craft-prepare")
record("counterfactual prepare (corrected attempt)", code, payload)
snap_craft_before = snapshot("snap-03-before-counterfactual")
code, payload = book("book-complete-file", "--book", "24", "--candidate", str(OUT / "craft-candidate.json"),
                     name="13-craft-complete")
review = payload.get("review", {})
record("counterfactual complete", code, payload, applicable=review.get("applicable"))
craft_sha = review.get("request_sha256")
code, payload = book("book-apply-review", "--book", "24", "--request-sha256", craft_sha, name="14-craft-apply")
record("counterfactual apply", code, payload)
code, payload = book("book-apply-review", "--book", "24", "--request-sha256", craft_sha, name="15-craft-apply-again")
record("counterfactual re-apply", code, payload)
code, resume = book("book-resume", "--book", "24", name="16-resume-after-counterfactual")
record("resume after counterfactual", code, resume, revision=resume.get("revision", {}).get("number"),
       semantics=resume.get("packet", {}).get("semantics"))
snap_craft_after = snapshot("snap-04-after-counterfactual")
summary["counterfactual_audit"] = changed(snap_craft_before, snap_craft_after)

# 5. Probes against the applied counterfactual. Each must be refused.
code, payload = book("book-withdraw", "--book", "24", "--element", "assume-witnessed-mark",
                     "--rationale", "Probe: withdraw the working premise while statements rest on it.",
                     name="17-probe-withdraw-premise")
record("PROBE withdraw premise with dependents", code, payload)

python("probe_decision.py", str(PROJ), str(OUT / "probe-decision.json"))
code, payload = book("book-prepare", "--book", "24", "--instruction", "Probe: a finale claim asserted outright.",
                     "--target", "later-finale-capability", name="18-probe-decision-prepare")
code, payload = book("book-complete-file", "--book", "24", "--candidate", str(OUT / "probe-decision.json"),
                     name="19-probe-decision-complete")
record("PROBE assert a decision-dependent claim", code, payload)

# 6. A deliberate working withdrawal, through the same reviewed path.
snap_wd_before = snapshot("snap-05-before-withdrawal")
code, payload = book("book-withdraw", "--book", "24", "--element", "later-books-25-26",
                     "--rationale", "The Books 25 and 26 pressure is outside this working counterfactual; the revision "
                                    "does not decide it.", name="20-withdraw-prepare")
record("withdrawal prepare", code, payload, applicable=payload.get("review", {}).get("applicable"))
wd_sha = payload.get("pending_request_sha256")
code, payload = book("book-apply-review", "--book", "24", "--request-sha256", wd_sha, name="21-withdraw-apply")
record("withdrawal apply", code, payload)
code, resume = book("book-resume", "--book", "24", name="22-resume-final")
record("resume final (fresh process)", code, resume, revision=resume.get("revision", {}).get("number"))
snap_wd_after = snapshot("snap-06-after-withdrawal")
summary["withdrawal_audit"] = changed(snap_wd_before, snap_wd_after)

summary["final_lineage"] = [(x["revision"], x["operation"], x["content_sha256"][:12])
                            for x in resume.get("revision", {}).get("lineage", [])]
(OUT / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
print("done")
