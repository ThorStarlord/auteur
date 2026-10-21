#!/usr/bin/env python3
"""Read-only forensic capture of one Auteur Studio canvas (standard library, Python 3.10+).

Copies the canvas and any story_identity.yaml to a new folder outside the project and reads only the copies.
  private/    raw copies, full evidence, pseudonym table. Never share.
  shareable/  report.md + evidence.json: IDs, requests, canvas and unknown path segments become consistent
              pseudonyms; no hashes of private content or symlink targets; candidate text masked by default;
              never the Story Vision, working items or revision instructions. --share-labels and --share-text
              DO expose creative material (titles, link functions, genre labels, or all candidate prose).
              Link targets are never recorded, even privately.
A source that changes, disappears or appears during the read DISQUALIFIES the capture (status,
DISQUALIFIED.txt, exit code 3). Detection compares before and after, so a change undone in between is
invisible: close Studio first. Symlinks and Windows junctions are never followed on any supported Python.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import re
import shutil
import stat
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

STUDIO_MODULE = "src/auteur/beginner/studio_architecture.py"
# sha256 of the exact `_SYSTEM` string in each version pushed to ThorStarlord/auteur.
KNOWN_SYSTEM_PROMPTS = {
    "b3756886fa119ed827903b0d864b3cfa4836d3f9c2e7786c43a742edd76e21f8": "031eb693 original prompt (to #472); no design context",
    "42274805af64323f7e0c76d7b18edb2d2a7f485fbf442838b7197f6d10b4d76c": "8d4db52c PR #471 head; no design context",
    "53dcb696e425e764160d1efc9887f112dfe658d85ad9bc24e953dade7e48c915": "5ecf597e PR #472; ontology-grounded context",
    "e33e64e14450b58cef230e75877a363614b2821768103a6ed4a45303ee723e47": "2260609f PR #473; #472 context + provisional defaults",
    "35b1f3409e0378a92e5819369666a31df2b93b5a5649ad4a2669d03b46d84466": "a6357839 main after #474/#475",
}
UNRECOGNIZED = ("unrecognized prompt version: a provenance question, not evidence of modification "
                "(local branch or uncommitted tree?); rerun with --auteur-repo")
STRUCTURAL = {".auteur", "beginner", "studio", "canvases", "architecture", "requests", "request.json",
              "response.json", "stale_response.json", "review.json", "current.json", "latest_request.json",
              "canvas.json", ".canvas.lock", "story_identity.yaml"}
# Which candidate fields hold references, and to what kind of object.
REFS = {"nodes": {"id": "node", "parent_id": "node"}, "links": {"id": "link", "source": "node", "target": "node"},
        "phases": {"id": "phase", "parallel_with": "phase"}, "emotion_targets": {"id": "emotion"},
        "complex_emotions": {"id": "complex"}, "genre_activations": {"genre_node_id": "node"},
        "genre_contracts": {"genre_node_id": "node", "emotion_target_ids": "emotion", "complex_emotion_ids": "complex"},
        "genre_interactions": {"id": "interaction", "source_genre_id": "node", "target_genre_id": "node"}}
KEEP = {"schema_version", "category", "role", "kind", "emotion", "provenance", "basic_emotions", "order"}
# Windows IsReparseTagNameSurrogate: the reparse point names another location (symlink, junction,
# WSL link). Cloud-file placeholders lack this bit and are captured normally.
NAME_SURROGATE = 0x20000000
LABELS = {"title", "function", "genre"}


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()  # Studio artifacts are small JSON files


def is_inside(child: Path, parent: Path) -> bool:
    c, p = (os.path.normcase(os.path.realpath(x)) for x in (child, parent))
    try:
        return os.path.commonpath([c, p]) == p
    except ValueError:  # different Windows drives
        return False


class Pseudonyms:
    """Consistent per-capture pseudonyms (N01, L01, R01, ...); the table stays in private/."""
    PREFIX = {"node": "N", "link": "L", "phase": "P", "emotion": "E", "complex": "X", "interaction": "I",
              "request": "R", "canvas": "C", "path": "F"}

    def __init__(self) -> None:
        self.table: dict[tuple[str, str], str] = {}
        self.counts: Counter = Counter()

    def __call__(self, kind: str, value):
        if value is not None and (kind, value) not in self.table:
            self.counts[kind] += 1
            self.table[(kind, value)] = f"{self.PREFIX[kind]}{self.counts[kind]:02d}"
        return None if value is None else self.table[(kind, value)]


def _copy(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def _is_link(path: Path, lstat=os.lstat) -> bool:
    """Symlink or junction without os.path.isjunction (3.12+); lstat does not traverse on Windows 3.8+."""
    try:
        st = lstat(path)
    except FileNotFoundError:
        return False
    return stat.S_ISLNK(st.st_mode) or bool(getattr(st, "st_reparse_tag", 0) & NAME_SURROGATE)


def _inventory(project: Path, canvas: Path) -> tuple[list[Path], list[Path]]:
    identity = project / "story_identity.yaml"
    links = [identity] if _is_link(identity) else []
    files = [identity] if identity.is_file() and not links else []
    for dirpath, dirnames, filenames in os.walk(canvas, followlinks=False):
        for name in sorted(dirnames + filenames):
            full = Path(dirpath, name)
            if _is_link(full):
                links.append(full)
            elif name in filenames:
                files.append(full)
        dirnames[:] = sorted(d for d in dirnames if not _is_link(Path(dirpath, d)))
    return files, links


def capture(project: Path, canvas: Path, raw: Path) -> dict:
    files, links = _inventory(project, canvas)
    before = {f: sha256_file(f) for f in files}
    entries = []
    for f in files:
        rel = f.relative_to(project)
        _copy(f, raw / rel)
        entries.append({"path": rel.as_posix(), "bytes": f.stat().st_size, "sha256": before[f],
                        "copy_sha256": sha256_file(raw / rel)})
    reasons = []
    for e, f in zip(entries, files):
        e["stable"] = f.exists() and sha256_file(f) == e["sha256"]
        if not e["stable"]:
            reasons.append(("source changed or vanished during capture", e["path"]))
        elif e["copy_sha256"] != e["sha256"]:
            reasons.append(("copy differs from a stable source", e["path"]))
    for late in sorted(set(sum(_inventory(project, canvas), [])) - set(files + links)):
        reasons.append(("appeared during capture", late.relative_to(project).as_posix()))
    return {"files": entries, "links_not_followed": [p.relative_to(project).as_posix() for p in links],
            "story_identity_present": (project / "story_identity.yaml").is_file(), "reasons": reasons}


def system_prompts_from_git(repo: Path) -> dict[str, dict]:
    """sha256(_SYSTEM) -> commit and date for local commits touching the Studio module."""
    def git(*args: str) -> str:
        return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True,
                              encoding="utf-8", check=True).stdout
    try:
        history = git("log", "--all", "--format=%H|%ad", "--date=short", "--", STUDIO_MODULE).splitlines()
    except (OSError, subprocess.CalledProcessError) as exc:
        sys.exit(f"could not read git history from --auteur-repo {repo}: {exc}")
    found: dict[str, dict] = {}
    for commit, date in (line.split("|", 1) for line in history):
        try:
            tree = ast.parse(git("show", f"{commit}:{STUDIO_MODULE}"))
        except (subprocess.CalledProcessError, SyntaxError):
            continue
        for node in tree.body:
            if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == "_SYSTEM":
                digest = hashlib.sha256(ast.literal_eval(node.value).encode("utf-8")).hexdigest()
                found.setdefault(digest, {"commit": commit[:8], "date": date})  # the subject is never recorded
    return found


def describe_request(path: Path, local: dict[str, dict]) -> dict:
    req = json.loads(path.read_text(encoding="utf-8"))
    body = {k: req.get(k) for k in ("schema", "candidate_id", "role", "system", "user", "settings")}
    user = json.loads(req["user"])
    working, design = user.get("working_context") or {}, user.get("narrative_design_context") or {}
    identity = design.get("accepted_story_identity") or {}
    system_sha = hashlib.sha256(req["system"].encode("utf-8")).hexdigest()
    match = local.get(system_sha)
    responses = []
    for name in ("response.json", "stale_response.json"):
        if (path.parent / name).is_file():
            res = json.loads((path.parent / name).read_text(encoding="utf-8"))
            entry = {"file": name, **{k: res.get(k) for k in ("backend", "runtime", "model", "completed_at")}}
            try:
                entry["candidate"] = json.loads(res["text"])
            except (KeyError, TypeError, json.JSONDecodeError) as exc:
                entry["candidate_error"] = f"response text is not candidate JSON: {type(exc).__name__}"
            responses.append(entry)
    return {
        "dir": path.parent.name, "request_sha256": req.get("request_sha256"), "created_at": req.get("created_at"),
        "recomputes": hashlib.sha256(json.dumps(body, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
                                     .encode("utf-8")).hexdigest() == req.get("request_sha256"),
        "operation": (req.get("settings") or {}).get("operation"), "system_sha256": system_sha,
        "prompt": KNOWN_SYSTEM_PROMPTS.get(system_sha)
        or (match and f"local commit {match['commit']} ({match['date']})") or UNRECOGNIZED,
        "delivered": {"narrative_design_context": bool(design),
                      "principle_sources": [p.get("source_ref") for p in design.get("source_principles", [])],
                      "accepted_identity_fields": sorted(k for k, v in identity.items() if v not in (None, [], "")),
                      "working_items": len(working.get("working_items") or []),
                      "working_connections": len(working.get("working_connections") or []),
                      "previous_candidate": working.get("previous_candidate") is not None},
        "vision": working.get("vision") or "", "instruction": user.get("revision_instruction") or "",
        "responses": responses, "has_review": (path.parent / "review.json").is_file(),
    }


def canon(value):
    """Drop schema defaults so a raw response and a stored model dump compare equal."""
    if isinstance(value, dict):
        return {k: canon(v) for k, v in value.items()
                if v not in (None, [], {}) and not (k == "scope" and v == "whole_story")}
    return [canon(v) for v in value] if isinstance(value, list) else value


def sanitize(value, ref, lab, field: str = "", refs: dict | None = None):
    """Pseudonymize every reference field, keep enumerations, pass text through `lab`."""
    if isinstance(value, list):
        return [sanitize(v, ref, lab, field, refs) for v in value]
    if isinstance(value, str):
        return lab(field, value)
    if not isinstance(value, dict):
        return value
    out = {}
    for k, v in value.items():
        if refs and k in refs:
            out[k] = [ref(refs[k], x) for x in v] if isinstance(v, list) else ref(refs[k], v)
        else:
            out[k] = v if k in KEEP else sanitize(v, ref, lab, k, REFS.get(k))
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--project", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path, help="parent folder outside the project")
    ap.add_argument("--canvas", help="required when more than one canvas has an architecture")
    ap.add_argument("--auteur-repo", type=Path, help="local auteur checkout, to identify unrecognized prompts")
    level = ap.add_mutually_exclusive_group()
    level.add_argument("--share-labels", action="store_true", help="share titles, link functions, genre labels (creative material)")
    level.add_argument("--share-text", action="store_true", help="share all candidate prose (creative material)")
    ap.add_argument("--redact", action="append", default=[], help="term to mask in shared text; repeatable")
    args = ap.parse_args(argv)
    if sys.version_info < (3, 10):
        sys.exit("Python 3.10 or newer is required")
    project = args.project.resolve()
    base = project / ".auteur" / "beginner" / "studio" / "canvases"
    if not base.is_dir():
        sys.exit(f"not an Auteur Studio project (missing {base})")
    if is_inside(args.out, project) or is_inside(args.out, base):
        sys.exit("refusing: --out must be outside the project so the original stays untouched")
    found = [p for p in sorted(base.iterdir()) if p.is_dir() and not _is_link(p) and (p / "architecture").is_dir()]
    found = [p for p in found if p.name == args.canvas] if args.canvas else found
    if len(found) != 1:
        sys.exit(f"capture exactly one canvas; found: {', '.join(p.name for p in found) or 'none'}. Pass --canvas ID")
    canvas, share = found[0], "text" if args.share_text else "labels" if args.share_labels else "none"
    local = system_prompts_from_git(args.auteur_repo) if args.auteur_repo else {}
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out = args.out.resolve() / f"auteur-capture-{stamp}"
    (out / "shareable").mkdir(parents=True, exist_ok=False)
    cap = capture(project, canvas, out / "private" / "raw")
    arch = out / "private" / "raw" / canvas.relative_to(project) / "architecture"
    reqs = sorted((describe_request(p, local) for p in arch.glob("requests/*/request.json")),
                  key=lambda r: r["created_at"] or "")
    cands = [(s["file"], r["request_sha256"], s["candidate"]) for r in reqs for s in r["responses"] if "candidate" in s]
    cands += [("staged revision", r["request_sha256"], json.loads(
        (arch / "requests" / r["dir"] / "review.json").read_text(encoding="utf-8"))["candidate"]) for r in reqs if r["has_review"]]
    if (arch / "current.json").is_file():
        current = json.loads((arch / "current.json").read_text(encoding="utf-8"))
        cands.append(("current working", current.get("request_sha256"), current["candidate"]))
    canvas_json = arch.parent / "canvas.json"
    items = json.loads(canvas_json.read_text(encoding="utf-8")).get("items", []) if canvas_json.is_file() else []
    vision_now = next((i.get("content", "") for i in items if i.get("id") == "story-vision"), None)
    status = "DISQUALIFIED: diagnostic only, not forensic evidence" if cap["reasons"] else "VALID"
    terms = [re.compile(re.escape(t), re.IGNORECASE) for t in args.redact]
    ps = Pseudonyms()

    def lab(field, value):
        if not (share == "text" or (share == "labels" and field in LABELS)):
            return f"[masked: {len(value)} chars]"
        for i, rx in enumerate(terms, 1):
            value = rx.sub(f"[REDACTED-{i}]", value)
        return value

    def safe_path(rel: str) -> str:
        return "/".join(s if s in STRUCTURAL else ps("canvas", s) if s == canvas.name else
                        ps("request", s) if re.fullmatch(r"[0-9a-f]{64}", s) else ps("path", s)
                        for s in rel.split("/"))

    shared = {
        "forensic_status": status, "disqualifying_reasons": [f"{why}: {safe_path(p)}" for why, p in cap["reasons"]],
        "captured_at_utc": stamp, "canvas": ps("canvas", canvas.name), "sharing_level": share,
        "contains_creative_material": share != "none",
        "files": [{"path": safe_path(e["path"]), "bytes": e["bytes"], "stable": e["stable"]} for e in cap["files"]],
        "links_not_followed": len(cap["links_not_followed"]), "story_identity_present": cap["story_identity_present"],
        "requests": [{"request": ps("request", r["request_sha256"]), "created_at": r["created_at"],
                      "operation": r["operation"], "recomputes": r["recomputes"], "system_sha256": r["system_sha256"],
                      "prompt": r["prompt"], "delivered": r["delivered"], "story_vision_chars": len(r["vision"]),
                      "story_vision_equals_canvas_now": r["vision"] == vision_now,
                      "instruction_chars": len(r["instruction"]), "has_review": r["has_review"],
                      "responses": [{k: v for k, v in s.items() if k != "candidate"} for s in r["responses"]]}
                     for r in reqs],
        "candidates": [{"source": kind, "request": ps("request", sha), "candidate": sanitize(canon(c), ps, lab)}
                       for kind, sha, c in cands],
    }
    full = {"forensic_status": status, "canvas": canvas.name, "capture": cap, "requests": reqs,
            "story_vision_now": vision_now, "candidates": [{"source": k, "request": s, "candidate": c} for k, s, c in cands],
            "pseudonyms": [{"kind": k, "original": v, "pseudonym": p} for (k, v), p in ps.table.items()]}
    (out / "private" / "evidence-full.json").write_text(json.dumps(full, indent=2, ensure_ascii=False), encoding="utf-8")
    (out / "shareable" / "evidence.json").write_text(json.dumps(shared, indent=2, ensure_ascii=False), encoding="utf-8")
    lines = [f"# Auteur Studio forensic capture: {status}", "",
             f"Canvas {shared['canvas']}, captured {stamp}, sharing level `{share}`; IDs are per-capture pseudonyms.",
             "An unrecognized prompt or a hash that does not recompute is a provenance question, not tampering.",
             *([f"WARNING: level `{share}` exposes creative material; pseudonyms hide identifiers, not content."]
               if share != "none" else []), ""]
    lines += [f"- {r['request']} {r['operation']} {r['created_at']}: prompt {r['system_sha256'][:12]} = {r['prompt']}; "
              f"recomputes={r['recomputes']}; design context={r['delivered']['narrative_design_context']}; "
              f"models={[s.get('model') for s in r['responses']]}" for r in shared["requests"]]
    lines += [f"- reason: {why}" for why in shared["disqualifying_reasons"]]
    (out / "shareable" / "report.md").write_text("\n".join(lines) + "\n\nData: evidence.json\n", encoding="utf-8")
    if cap["reasons"]:
        (out / "DISQUALIFIED.txt").write_text("\n".join([status, *shared["disqualifying_reasons"]]) + "\n", encoding="utf-8")
    for folder, target in ((out / "shareable", out / "shareable"), (out, out / "private")):
        listed = [p for p in sorted(folder.rglob("*")) if p.is_file() and p.name != "SHA256SUMS.txt"]
        (target / "SHA256SUMS.txt").write_text(
            "".join(f"{sha256_file(p)}  {p.relative_to(folder).as_posix()}\n" for p in listed), encoding="utf-8")
    print(f"captured canvas {canvas.name} -> {out}: {status}"
          + (f"\nshareable/ contains creative material (level {share}); review it before sharing" if share != "none" else ""))
    return 3 if cap["reasons"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
