"""End-to-end working-revision lifecycle for The Spring Ledger, through the Studio bridge CLI.

Usage: python run_walkthrough.py <repo_root> <scratch_dir>

Every product step runs as a separate `python -m auteur.beginner.studio_architecture` process,
so that recovery is tested across processes. Inputs are read read-only from the experimental
commits named below with `git show`. Nothing in those commits is modified.

Sequence: resume -> prepare -> complete-file (baseline W6) -> resume -> prepare --instruction ->
complete-file (Book 24 revision) -> show -> resume (review pending, not applied) -> apply-review ->
resume (fresh process, applied) -> apply-review again -> negative cases -> continuity check.
Each step's exit code, status and key fields are written to transcript.json. Full bridge output is
hashed, not copied, to keep the evidence small.
"""
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

REPO = Path(sys.argv[1]).resolve()
SCRATCH = Path(sys.argv[2]).resolve()
SRC = REPO / "src"
PR555 = "fa85b7f1c2fbfdf8d5b8b35f6ce64c27bf438e04"
PR551 = "3168963b7df262d81354d3fec2cf8ef2ec74cd4b"
CANVAS = "spring-ledger-lifecycle"
PROJECT = SCRATCH / "project"
W6_PATH = "experiments/spring-ledger-working-architecture/02-working-candidate-W6.json"
BOOK24_PATH = "experiments/spring-ledger-working-architecture/cold-start/output/book-24-candidate.corrected-2.json"
BOOK24_INSTRUCTION = (
    "Add the Book 24 function as Book-scoped nodes, links and one agent-proposed emotion target, "
    "keeping every existing element unchanged. The capability record bears on who can return labour "
    "without changing who is counted for draw; the Reading Hall declines attribution because the Balance "
    "Stones do not resolve local return."
)
ENV = dict(os.environ, PYTHONPATH=str(SRC), PYTHONUTF8="1")
SCRATCH.mkdir(parents=True, exist_ok=True)
transcript = []


def git_blob(commit, path):
    return subprocess.run(["git", "-C", str(REPO), "show", f"{commit}:{path}"],
                          capture_output=True, check=True).stdout


def bridge(*args, expect_exit=0):
    cmd = [sys.executable, "-m", "auteur.beginner.studio_architecture",
           "--project", str(PROJECT), "--canvas", CANVAS, *args]
    res = subprocess.run(cmd, capture_output=True, text=True, env=ENV, cwd=str(REPO))
    body = None
    if res.stdout.strip():
        try:
            body = json.loads(res.stdout)
        except json.JSONDecodeError:
            body = {"non_json_stdout": res.stdout[:300]}
    entry = {
        "action": " ".join(args[:3]) if args[0] != "apply-review" else "apply-review",
        "args": list(args),
        "exit_code": res.returncode,
        "expected_exit": expect_exit,
        "stderr_tail": res.stderr.strip().splitlines()[-1:] if res.stderr.strip() else [],
        "output_sha256": hashlib.sha256(res.stdout.encode("utf-8")).hexdigest(),
        "summary": summarise(args[0], body),
    }
    transcript.append(entry)
    if res.returncode != expect_exit:
        raise SystemExit(f"step {args[0]} exited {res.returncode}, expected {expect_exit}: {res.stderr[-400:]}")
    return body


def summarise(action, body):
    if not isinstance(body, dict):
        return None
    out = {"status": body.get("status"), "architecture_status": body.get("architecture_status")}
    if "candidate" in body and body["candidate"]:
        out["candidate_nodes"] = len(body["candidate"].get("nodes", []))
        out["candidate_request_sha256"] = body.get("candidate_request_sha256")
    if "architecture" in body and body["architecture"]:
        out["live_nodes"] = len(body["architecture"].get("nodes", []))
    if "review" in body and body["review"]:
        review = body["review"]
        out["review_request_sha256"] = review.get("request_sha256")
        out["changes"] = {k: {kk: len(vv) for kk, vv in v.items()} if isinstance(v, dict) else v
                          for k, v in review.get("changes", {}).items() if k in
                          ("nodes", "links", "emotion_targets", "phases", "summary_changed")}
    if "pending_review" in body:
        out["pending_review"] = None if body["pending_review"] is None else body["pending_review"].get("request_sha256")
    if "application" in body:
        out["application"] = body["application"]
    return out


def write_intentions():
    intents = [json.loads(git_blob(PR551, f"experiments/series-architecture-30-book-v1/evidence/intention-{n}.json"))["intention"]
               for n in range(1, 5)]
    identity = ("The Spring Ledger is a long-form fantasy Series exploring a shared water commons, the institutions "
                "that govern it, the meanings attached to obligation, and the consequences of changing collective "
                "practices. Its identity should preserve wonder, discovery, everyday belonging, meaningful "
                "relationships, institutional transformation, material consequences, and the possibility of hopeful "
                "flourishing. Do not turn it into a generic escalating-villain epic.")
    vision = identity + "\n\n" + "\n\n".join(f"{i['title']}: {i['directive']}" for i in intents)
    sys.path.insert(0, str(SRC))
    from auteur.beginner.studio_store import CanvasStore
    store = CanvasStore(PROJECT, CANVAS)
    store.create()
    store.apply("create-item", expected_revision=0, command_id="vision-created", payload={
        "item": {"id": "story-vision", "kind": "note", "title": "Story Vision", "content": vision},
        "position": {"x": 20, "y": 50}})
    directives = SCRATCH / "directives"
    directives.mkdir(exist_ok=True)
    for index, rec in enumerate(intents, 1):
        path = directives / f"{index}.txt"
        path.write_text(rec["directive"], encoding="utf-8")
        bridge("keep-intention", "--title", rec["title"], "--directive-file", str(path))


def candidate_file(name, data):
    path = SCRATCH / name
    path.write_bytes(data)
    return str(path)


def main():
    w6 = git_blob(PR555, W6_PATH)
    book24 = git_blob(PR555, BOOK24_PATH)
    write_intentions()
    bridge("resume")
    bridge("prepare")
    baseline = bridge("complete-file", "--candidate", candidate_file("w6.json", w6))
    assert baseline["status"] == "ready"
    before = bridge("resume")
    assert before["pending_review"] is None and len(before["architecture"]["nodes"]) == 32

    bridge("prepare", "--instruction", BOOK24_INSTRUCTION)
    revision = bridge("complete-file", "--candidate", candidate_file("book24.json", book24))
    assert revision["status"] == "review_ready"
    review_sha = revision["review"]["request_sha256"]
    show_pending = bridge("show")
    assert show_pending["status"] == "review_ready"
    pending = bridge("resume")
    assert pending["pending_review"]["request_sha256"] == review_sha
    assert len(pending["architecture"]["nodes"]) == 32, "a pending revision must not change the live architecture"

    applied = bridge("apply-review", "--request-sha256", review_sha)
    assert applied["application"]["result"] == "applied"
    recovered = bridge("resume")
    assert recovered["pending_review"] is None
    assert len(recovered["architecture"]["nodes"]) == 34
    assert recovered["candidate_request_sha256"] == review_sha

    again = bridge("apply-review", "--request-sha256", review_sha)
    assert again["application"]["result"] == "already_applied"

    bridge("prepare", "--instruction", "A later revision that supersedes the applied one.")
    superseded = bridge("apply-review", "--request-sha256", review_sha, expect_exit=1)
    assert superseded["application"]["result"] == "rejected" and "superseded" in superseded["application"]["error"]
    bridge("apply-review", "--request-sha256", "a" * 64, expect_exit=1)
    bridge("apply-review", "--request-sha256", "not-a-sha", expect_exit=1)

    continuity = continuity_check(w6, bridge("resume"))
    (SCRATCH / "continuity.json").write_text(json.dumps(continuity, indent=2), encoding="utf-8")
    (SCRATCH / "transcript.json").write_text(json.dumps(transcript, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({"steps": len(transcript), "continuity": continuity["verdict"]}, indent=2))


def continuity_check(w6_bytes, recovered):
    """Verify the recovered architecture keeps W6's Series-level commitments and adds only Book 24 elements."""
    base = json.loads(w6_bytes)
    live = recovered["architecture"]
    base_nodes = {n["id"]: n for n in base["nodes"]}
    live_nodes = {n["id"]: n for n in live["nodes"]}
    added = sorted(set(live_nodes) - set(base_nodes))
    unchanged_engines = all(live_nodes[i] == base_nodes[i] for i in ["eng_ledger", "eng_source", "eng_old_hand"])
    governing = live_nodes["th_hands_and_draw"]["summary"] == base_nodes["th_hands_and_draw"]["summary"]
    finale_unchanged = all(live_nodes[i] == base_nodes[i] for i in ["alt_a_reciprocal", "alt_b_allotted", "alt_c_ratified_trigger"])
    open_q_same = live["open_questions"] == base["open_questions"]
    not_chosen = all("not chosen" in live_nodes[i]["title"].lower() for i in ["alt_a_reciprocal", "alt_b_allotted", "alt_c_ratified_trigger"])
    provenance_kept = all(e["provenance"] == "agent_proposed" for e in live["emotion_targets"])
    no_author_declared = all(e["provenance"] != "author_declared" for e in live["emotion_targets"])
    checks = {
        "added_nodes": added,
        "engines_unchanged": unchanged_engines,
        "governing_variable_summary_unchanged": governing,
        "finale_alternatives_unchanged": finale_unchanged,
        "finale_alternatives_still_not_chosen": not_chosen,
        "open_questions_unchanged": open_q_same,
        "emotion_provenance_agent_proposed": provenance_kept,
        "no_author_declared_provenance": no_author_declared,
        "capability_record_present": "str_b24_capability_mark" in live_nodes,
    }
    checks["verdict"] = "pass" if all(v is True for k, v in checks.items() if k not in ("added_nodes", "verdict")) else "fail"
    return checks


if __name__ == "__main__":
    main()
