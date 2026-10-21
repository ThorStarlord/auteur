#!/usr/bin/env python3
"""Read-only forensic capture of an Auteur Studio architecture project.

Copies one Studio canvas (and any accepted ``story_identity.yaml``) into a new
folder OUTSIDE the project, proves the copies are byte-identical, and analyses
only the copies. Nothing is ever written inside the project.

Output (one folder per canvas)::

    private/raw/...           byte copies of the project files. Never share.
    private/report-full.md    everything, including the Story Vision and all candidate text.
    shareable/report.md       provenance, integrity, structure and indicators. Free text is
                              redacted unless --share-labels / --share-text is given; the
                              Story Vision, working items and revision instructions are never
                              included (only their length and hash).
    shareable/evidence.json   the same data, machine-readable.
    SHA256SUMS.txt            hashes of every output file.

Standard library only; Python 3.10+.

    python tidal_forensic_capture.py --project "C:\\path\\to\\tidal-archive" --out "D:\\forensics"
    optional: --canvas ID  --auteur-repo "C:\\path\\to\\auteur"  --share-labels | --share-text  --redact TERM

Close Auteur Studio first so the project does not change while it is being read.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

STUDIO_MODULE = "src/auteur/beginner/studio_architecture.py"

# sha256 of the exact `_SYSTEM` string in each version pushed to ThorStarlord/auteur.
KNOWN_SYSTEM_PROMPTS = {
    "b3756886fa119ed827903b0d864b3cfa4836d3f9c2e7786c43a742edd76e21f8":
        "031eb693: original prompt (main 2026-10-14 to #472); no narrative design context",
    "42274805af64323f7e0c76d7b18edb2d2a7f485fbf442838b7197f6d10b4d76c":
        "8d4db52c: PR #471 branch head; original + provisional-defaults paragraph; no design context",
    "53dcb696e425e764160d1efc9887f112dfe658d85ad9bc24e953dade7e48c915":
        "5ecf597e: PR #472; ontology-grounded design context",
    "e33e64e14450b58cef230e75877a363614b2821768103a6ed4a45303ee723e47":
        "2260609f: PR #473; #472 context + provisional defaults",
    "ffa3c8075c8c706d29b159a13536b70b44597c0b9ff8a68a3b2cc75ed8ab19ad":
        "46c4334d: PR #475 first commit",
    "35b1f3409e0378a92e5819369666a31df2b93b5a5649ad4a2669d03b46d84466":
        "a6357839: main after #474/#475",
}
UNRECOGNIZED = ("unrecognized prompt version: a provenance question, not evidence of modification. "
                "It may come from a local or unpushed branch or an uncommitted working tree; "
                "rerun with --auteur-repo pointing at the checkout that served the request.")

BASE_CONCEPTS = ["character", "arc", "theme", "goal", "conflict", "payoff", "symbol",
                 "relationship", "beat", "setup", "revelation", "reversal"]
EXTRA_TERMS = ["want", "stakes", "resistance", "change", "pressure", "escalat", "renew", "motif"]
LINK_BUCKETS = [
    ("causal", r"cause|drive|generat|produc|trigger|force|creat|feed|fuel|activat|unlock|enabl|escalat|provok|compel|lead"),
    ("constraint", r"constrain|limit|block|restrict|gate|prevent|resist|oppos|threat|undermin|complicat|counter"),
    ("expressive", r"express|embod|manifest|dramati|test|question|reveal|explor|interrogat|symboli|mirror|echo"),
    ("support", r"support|reinforc|amplif|deepen|strengthen|sustain|enrich|heighten|intensif|ground|anchor"),
    ("contrast", r"contrast|counterpoint|juxtapos|tension|balanc"),
    ("structural", r"contain|frame|organi[sz]|structur|sequence|precede|follow|resolve|pay|set ?up|culminat|converge"),
]
# Free-text candidate fields; everything else is structural (ids, categories, roles, kinds, labels).
LABEL_FIELDS = {"title", "function"}
TEXT_FIELDS = {"summary", "intended_effect", "eliciting_condition", "aesthetic_strategy", "context",
               "narrative_engine", "structural_pattern", "mechanism", "risk", "reader_experience",
               "aesthetic", "narrative_function", "transition", "structural_function", "genre",
               "trope_functions", "aesthetic_strategies", "payoff_expectations", "open_questions"}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def canonical_sha(payload: dict) -> str:
    return sha256_bytes(json.dumps(payload, ensure_ascii=False, sort_keys=True,
                                   separators=(",", ":")).encode("utf-8"))


def norm(path: Path) -> str:
    return os.path.normcase(os.path.realpath(path))


def is_inside(child: Path, parent: Path) -> bool:
    c, p = norm(child), norm(parent)
    try:
        return os.path.commonpath([c, p]) == p
    except ValueError:  # different drives on Windows
        return False


def walk_files(root: Path) -> tuple[list[Path], list[dict]]:
    files, links = [], []
    for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
        for name in sorted(dirnames):
            if os.path.islink(os.path.join(dirpath, name)):
                links.append({"path": os.path.join(dirpath, name), "target": os.readlink(os.path.join(dirpath, name))})
        dirnames[:] = sorted(d for d in dirnames if not os.path.islink(os.path.join(dirpath, d)))
        for name in sorted(filenames):
            full = Path(dirpath) / name
            if full.is_symlink():
                links.append({"path": str(full), "target": os.readlink(full)})
            else:
                files.append(full)
    return files, links


def _copy(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def capture(project: Path, canvas_dir: Path, raw_root: Path) -> dict:
    files, links = walk_files(canvas_dir)
    identity = project / "story_identity.yaml"
    if identity.is_symlink():
        links.append({"path": str(identity), "target": os.readlink(identity)})
    elif identity.is_file():
        files.insert(0, identity)
    pre = {f: sha256_file(f) for f in files}
    entries = []
    for f in files:
        rel = f.relative_to(project)
        dst = raw_root / rel
        _copy(f, dst)
        entries.append({"path": rel.as_posix(), "bytes": dst.stat().st_size, "sha256_before": pre[f],
                        "sha256_copy": sha256_file(dst),
                        "mtime_utc": datetime.fromtimestamp(f.stat().st_mtime, timezone.utc).isoformat()})
    changed = []
    for entry, f in zip(entries, files):
        entry["sha256_after"] = sha256_file(f) if f.exists() else None
        if entry["sha256_after"] != entry["sha256_before"]:
            changed.append(entry["path"])
        elif entry["sha256_copy"] != entry["sha256_before"]:
            raise RuntimeError(f"copy of {entry['path']} differs from a stable source; capture aborted")
    return {"files": entries, "symlinks_not_followed": [{"path": str(Path(x["path"]).relative_to(project)),
                                                         "target": x["target"]} for x in links],
            "story_identity_present": identity.is_file(), "changed_during_capture": changed,
            "stable": not changed}


def system_prompts_from_git(repo: Path) -> dict[str, str]:
    """Map sha256(_SYSTEM) -> commit for every local commit that touched the Studio module."""
    def git(*args: str) -> str:
        return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True,
                              encoding="utf-8", check=True).stdout
    found = {}
    try:
        history = git("log", "--all", "--format=%H %ad %s", "--date=short", "--", STUDIO_MODULE)
    except (OSError, subprocess.CalledProcessError) as exc:
        sys.exit(f"could not read git history from --auteur-repo {repo}: {exc}")
    for line in history.splitlines():
        commit, label = line.split(" ", 1)
        try:
            tree = ast.parse(git("show", f"{commit}:{STUDIO_MODULE}"))
        except (subprocess.CalledProcessError, SyntaxError):
            continue
        for node in tree.body:
            if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == "_SYSTEM":
                digest = sha256_bytes(ast.literal_eval(node.value).encode("utf-8"))
                found.setdefault(digest, f"{commit[:8]} {label} (local git history)")
    return found


def describe_request(path: Path, local_prompts: dict[str, str]) -> dict:
    req = json.loads(path.read_text(encoding="utf-8"))
    body = {k: req.get(k) for k in ("schema", "candidate_id", "role", "system", "user", "settings")}
    user = json.loads(req["user"])
    working = user.get("working_context") or {}
    design = user.get("narrative_design_context") or {}
    identity = design.get("accepted_story_identity") or {}
    system_sha = sha256_bytes(req["system"].encode("utf-8"))
    vision = working.get("vision") or ""
    instruction = user.get("revision_instruction") or ""
    return {
        "dir": path.parent.name, "request_sha256": req.get("request_sha256"),
        "request_sha256_recomputes": canonical_sha(body) == req.get("request_sha256"),
        "created_at": req.get("created_at"), "operation": (req.get("settings") or {}).get("operation"),
        "source_sha256": (req.get("settings") or {}).get("source_sha256"),
        "system_sha256": system_sha, "system_words": len(req["system"].split()),
        "system_version": KNOWN_SYSTEM_PROMPTS.get(system_sha) or local_prompts.get(system_sha) or UNRECOGNIZED,
        "delivered": {"narrative_design_context": bool(design),
                      "principle_sources": [p.get("source_ref") for p in design.get("source_principles", [])],
                      "preference_vocabulary": sorted((design.get("architecture_preference_vocabulary") or {}).keys()),
                      "accepted_identity_fields": sorted(k for k, v in identity.items() if v not in (None, [], "")),
                      "working_items": len(working.get("working_items") or []),
                      "working_connections": len(working.get("working_connections") or []),
                      "previous_candidate": working.get("previous_candidate") is not None},
        "private": {"vision": vision, "revision_instruction": instruction},
        "vision_fingerprint": {"chars": len(vision), "sha256": sha256_bytes(vision.encode("utf-8"))},
        "instruction_fingerprint": {"chars": len(instruction), "sha256": sha256_bytes(instruction.encode("utf-8"))},
    }


def describe_response(path: Path) -> dict:
    res = json.loads(path.read_text(encoding="utf-8"))
    out = {k: res.get(k) for k in ("backend", "runtime", "model", "completed_at", "elapsed_seconds")}
    out.update(file=path.name, text_sha256=sha256_bytes((res.get("text") or "").encode("utf-8")))
    try:
        out["candidate"] = json.loads(res["text"])
    except (KeyError, TypeError, json.JSONDecodeError) as exc:
        out["candidate_error"] = f"response text is not candidate JSON: {exc}"
    return out


def bucket(function: str) -> str:
    return next((name for name, rx in LINK_BUCKETS if re.search(rx, function.lower())), "generic/other")


def analyze(c: dict) -> dict:
    nodes = c.get("nodes") or []
    by_id = {n.get("id"): n for n in nodes}

    def cat(nid: str) -> str:
        return by_id.get(nid, {}).get("category", "?")

    links = [lk for lk in c.get("links") or [] if lk.get("source") in by_id and lk.get("target") in by_id]
    contracts = c.get("genre_contracts") or []
    inter = c.get("genre_interactions") or []
    phases = c.get("phases") or []
    children = defaultdict(list)
    for n in nodes:
        if n.get("parent_id") in by_id:
            children[n["parent_id"]].append(n["id"])
    degree = Counter()
    for lk in links:
        degree[lk["source"]] += 1
        degree[lk["target"]] += 1
    in_inter = {e.get("source_genre_id") for e in inter} | {e.get("target_genre_id") for e in inter}
    pairs = {tuple(sorted((e.get("source_genre_id"), e.get("target_genre_id")))) for e in inter}
    engines = [n for n in nodes if n.get("category") == "engine"]
    engine_refs = {n["id"] for n in engines} | {(n.get("title") or "").lower() for n in engines}
    contract_names_engine = [ct.get("genre_node_id") for ct in contracts
                             if any(r and r in (ct.get("narrative_engine") or "").lower() for r in engine_refs)]
    engine_genre_links = [lk["id"] for lk in links if {cat(lk["source"]), cat(lk["target"])} == {"engine", "genre"}]
    themes = [n["id"] for n in nodes if n.get("category") == "theme"]
    buckets = Counter(bucket(lk.get("function") or "") for lk in links)
    titles = {(by_id.get(ct.get("genre_node_id"), {}).get("title") or "").lower(): ct.get("genre_node_id") for ct in contracts}
    ids = {p.get("id"): p for p in phases}
    phase_issues = []
    for p in phases:
        labels = [(g.get("genre") or "") for g in p.get("genres") or []]
        label_ids = {titles.get(g.lower(), g) for g in labels}
        acts = [a.get("genre_node_id") for a in p.get("genre_activations") or []]
        issue = {"labels_matching_no_contract": [g for g in labels if g.lower() not in titles and g not in titles.values()],
                 "activations_without_label": [a for a in acts if a not in label_ids],
                 "one_way_parallel_with": [q for q in p.get("parallel_with") or []
                                           if q in ids and p.get("id") not in (ids[q].get("parallel_with") or [])]}
        if any(issue.values()):
            phase_issues.append({"phase": p.get("id"), **issue})
    text = json.dumps(c, ensure_ascii=False).lower()
    looks_isolated_old = [n["id"] for n in nodes if not degree[n["id"]] and n["id"] not in in_inter]
    isolated = [i for i in looks_isolated_old if not by_id[i].get("parent_id") and not children.get(i)]
    return {
        "schema_version": c.get("schema_version"),
        "counts": {k: len(c.get(k) or []) for k in ("nodes", "links", "phases", "genre_contracts", "genre_interactions",
                                                    "emotion_targets", "complex_emotions", "open_questions")},
        "nodes_by_category": dict(Counter(n.get("category") for n in nodes)),
        "hierarchy": {"nodes_with_parent": sum(1 for n in nodes if n.get("parent_id")), "parents": dict(children)},
        "links": {"by_category_pair": dict(Counter(f"{cat(lk['source'])}->{cat(lk['target'])}" for lk in links)),
                  "function_buckets": dict(buckets)},
        "engines": {"engine_nodes": [n["id"] for n in engines], "contracts": len(contracts),
                    "contracts_naming_an_engine_node": contract_names_engine, "engine_genre_links": engine_genre_links,
                    "governing_contracts": [ct.get("genre_node_id") for ct in contracts if ct.get("role") == "governing"]},
        "themes": {"theme_nodes": themes, "unlinked": [t for t in themes if not degree[t]]},
        "genre_interactions": [f"{e.get('source_genre_id')} -{e.get('kind')}-> {e.get('target_genre_id')}" for e in inter],
        "emotion": {"by_role": dict(Counter(t.get("role") for t in c.get("emotion_targets") or [])),
                    "by_provenance": dict(Counter(t.get("provenance") for t in c.get("emotion_targets") or []))},
        "phases": {"orders": [p.get("order") for p in phases], "issues": phase_issues},
        "presentation_pre471": {
            "lines_drawn": len(links) + len(pairs), "reciprocal_interactions_collapsed": len(inter) - len(pairs),
            "parent_relations_not_drawn": sum(len(v) for v in children.values()),
            "nodes_drawn_with_no_line": looks_isolated_old, "nodes_semantically_unconnected": isolated},
        "term_counts": {t: len(re.findall(r"\b" + t, text)) for t in BASE_CONCEPTS + EXTRA_TERMS},
        "indicators": {
            "P1_engine_locus_split": bool(contracts) and not contract_names_engine and not engine_genre_links,
            "P2_generic_links": bool(links) and (buckets["generic/other"] + buckets["support"]) * 2 >= len(links),
            "P3_sparse_hierarchy": sum(1 for n in nodes if n.get("parent_id")) <= 1,
            "P4_unlinked_theme": any(not degree[t] for t in themes),
            "P6_open_questions": len(c.get("open_questions") or []),
        },
    }


def diff(old: dict, new: dict) -> dict:
    out = {}
    for field, key in (("nodes", "id"), ("links", "id"), ("phases", "id"), ("emotion_targets", "id"),
                       ("genre_contracts", "genre_node_id"), ("genre_interactions", "id")):
        a = {e.get(key): e for e in old.get(field) or []}
        b = {e.get(key): e for e in new.get(field) or []}
        out[field] = {"added": sorted(b.keys() - a.keys()), "removed": sorted(a.keys() - b.keys()),
                      "changed": sorted(k for k in a.keys() & b.keys() if a[k] != b[k])}
    out["summary_changed"] = old.get("summary") != new.get("summary")
    return out


def sanitize(value, level: str, redact: list[str], field: str = ""):
    if isinstance(value, dict):
        return {k: sanitize(v, level, redact, k) for k, v in value.items()}
    if isinstance(value, list):
        return [sanitize(v, level, redact, field) for v in value]
    if not isinstance(value, str):
        return value
    shared = (field in LABEL_FIELDS and level in ("labels", "text")) or (field in TEXT_FIELDS and level == "text")
    if field in LABEL_FIELDS | TEXT_FIELDS and not shared:
        return f"[{len(value)} chars sha256:{sha256_bytes(value.encode('utf-8'))[:12]}]"
    for i, term in enumerate(redact, 1):
        value = re.sub(re.escape(term), f"[REDACTED-{i}]", value, flags=re.IGNORECASE)
    return value


def outline(c: dict) -> list[str]:
    lines = [f"Summary: {c.get('summary')}", ""]
    for n in c.get("nodes") or []:
        lines.append(f"- node `{n.get('id')}` [{n.get('category')}] {n.get('title')}"
                     f"{' (parent ' + n['parent_id'] + ')' if n.get('parent_id') else ''}: {n.get('summary')}")
    for lk in c.get("links") or []:
        lines.append(f"- link `{lk.get('source')}` -[{lk.get('function')}]-> `{lk.get('target')}`")
    for ct in c.get("genre_contracts") or []:
        lines.append(f"- contract `{ct.get('genre_node_id')}` {ct.get('role')}: engine={ct.get('narrative_engine')} | "
                     f"structure={ct.get('structural_pattern')} | tropes={ct.get('trope_functions')} | "
                     f"payoffs={ct.get('payoff_expectations')}")
    for e in c.get("genre_interactions") or []:
        lines.append(f"- interaction `{e.get('source_genre_id')}` -{e.get('kind')}-> `{e.get('target_genre_id')}`: "
                     f"{e.get('mechanism')} (risk: {e.get('risk')})")
    for t in c.get("emotion_targets") or []:
        lines.append(f"- emotion `{t.get('id')}` {t.get('emotion')}/{t.get('role')}/{t.get('provenance')}: "
                     f"{t.get('intended_effect')} | {t.get('eliciting_condition')} | {t.get('aesthetic_strategy')}")
    for p in sorted(c.get("phases") or [], key=lambda p: p.get("order", 0)):
        lines.append(f"- phase {p.get('order')} `{p.get('id')}` {p.get('title')} genres={p.get('genres')}: "
                     f"{p.get('narrative_function')} | transition={p.get('transition')} | "
                     f"activations={[(a.get('genre_node_id'), a.get('structural_function')) for a in p.get('genre_activations') or []]}")
    lines += [f"- open question: {q}" for q in c.get("open_questions") or []]
    return lines


def render(evidence: dict, candidates: dict, *, private: bool, level: str, redact: list[str]) -> str:
    cap = evidence["capture"]
    md = [f"# Studio architecture forensic capture: `{evidence['canvas']}`", "",
          f"Captured {evidence['captured_at_utc']} from a read-only pass over the project. "
          f"Sharing level: {'private (full text)' if private else level}.", "",
          "## Integrity", "",
          f"- Files copied: {len(cap['files'])}; copies match a stable source: {cap['stable']}",
          f"- Changed during capture (recapture with Studio closed): {cap['changed_during_capture'] or 'none'}",
          f"- Symlinks recorded, not followed: {len(cap['symlinks_not_followed'])}",
          f"- story_identity.yaml present: {cap['story_identity_present']}", "",
          "Reading notes: an unrecognized prompt hash or a request hash that does not recompute is a "
          "provenance question (which code or format produced it), not evidence of modification. "
          "Indicators P1-P6 are heuristics that point a reviewer at candidate text; they are not verdicts.",
          "", "## Requests (chronological)", ""]
    for r in evidence["requests"]:
        md.append(f"- `{r['request_sha256'][:12]}` {r['operation']} {r['created_at']}; hash recomputes: "
                  f"{r['request_sha256_recomputes']}; prompt `{r['system_sha256'][:12]}` = {r['system_version']}")
        md.append(f"  - delivered: {json.dumps(r['delivered'])}")
        md.append(f"  - Story Vision {r['vision_fingerprint']}; revision instruction {r['instruction_fingerprint']}")
        for s in r.get("responses", []):
            md.append(f"  - {s['file']}: backend={s.get('backend')} runtime={s.get('runtime')} model={s.get('model')} "
                      f"completed={s.get('completed_at')}{' ERROR ' + s['candidate_error'] if s.get('candidate_error') else ''}")
        if private:
            md += ["", "  Story Vision delivered:", "", "```text", r["private"]["vision"], "```"]
            if r["private"]["revision_instruction"]:
                md += ["  Revision instruction:", "", "```text", r["private"]["revision_instruction"], "```"]
    md.append(f"\nStory Vision now equals the initial request's: {evidence['vision_unchanged_since_initial']}")
    for label, data in candidates.items():
        md += ["", f"## {label}", "", "```json", json.dumps(data["analysis"], indent=2, ensure_ascii=False), "```"]
        if "diff_from_initial" in data:
            md += ["", "Changes from the initial candidate:", "", "```json", json.dumps(data["diff_from_initial"]), "```"]
        if private or level != "structure":
            shown = data["candidate"] if private else sanitize(data["candidate"], level, redact)
            md += ["", "Outline:", ""] + outline(shown)
    return "\n".join(md) + "\n"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--project", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--canvas")
    ap.add_argument("--auteur-repo", type=Path, help="local auteur checkout, to identify unrecognized prompt versions")
    level = ap.add_mutually_exclusive_group()
    level.add_argument("--share-labels", action="store_true", help="share titles and link functions")
    level.add_argument("--share-text", action="store_true", help="share all candidate text (never the Story Vision)")
    ap.add_argument("--redact", action="append", default=[], help="term to mask in shared text; repeatable")
    args = ap.parse_args(argv)
    project = args.project.resolve()
    base = project / ".auteur" / "beginner" / "studio" / "canvases"
    if not base.is_dir():
        sys.exit(f"not an Auteur Studio project (missing {base})")
    if is_inside(args.out, project):
        sys.exit("refusing: --out must be outside the project so the original stays untouched")
    canvases = sorted(p for p in base.iterdir() if p.is_dir() and not p.is_symlink() and (p / "architecture").is_dir())
    canvases = [c for c in canvases if not args.canvas or c.name == args.canvas]
    if not canvases:
        sys.exit("no Studio canvas with an architecture/ folder found")
    share = "text" if args.share_text else "labels" if args.share_labels else "structure"
    local = system_prompts_from_git(args.auteur_repo) if args.auteur_repo else {}
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    for canvas in canvases:
        out = args.out.resolve() / f"{canvas.name}-{stamp}"
        out.mkdir(parents=True, exist_ok=False)
        raw = out / "private" / "raw"
        cap = capture(project, canvas, raw)
        arch = raw / canvas.relative_to(project) / "architecture"
        requests = []
        for req in sorted(arch.glob("requests/*/request.json")):
            entry = describe_request(req, local)
            entry["responses"] = [describe_response(req.parent / n) for n in ("response.json", "stale_response.json")
                                  if (req.parent / n).is_file()]
            entry["has_review"] = (req.parent / "review.json").is_file()
            requests.append(entry)
        requests.sort(key=lambda r: r["created_at"] or "")
        canvas_json = raw / canvas.relative_to(project) / "canvas.json"
        items = json.loads(canvas_json.read_text(encoding="utf-8")).get("items", []) if canvas_json.is_file() else []
        vision_now = next((i.get("content", "") for i in items if i.get("id") == "story-vision"), "")
        initial = next((r for r in requests if r["operation"] == "develop" and r["responses"]
                        and r["responses"][0]["file"] == "response.json"), None)
        candidates = {}
        if initial and "candidate" in initial["responses"][0]:
            candidates["Initial candidate"] = {"candidate": initial["responses"][0]["candidate"]}
        for r in requests:
            review = arch / "requests" / r["dir"] / "review.json"
            if r["has_review"]:
                candidates[f"Revision {r['request_sha256'][:12]} (staged review)"] = {
                    "candidate": json.loads(review.read_text(encoding="utf-8"))["candidate"]}
        if (arch / "current.json").is_file():
            candidates["Current working candidate"] = {
                "candidate": json.loads((arch / "current.json").read_text(encoding="utf-8"))["candidate"]}
        first = candidates.get("Initial candidate", {}).get("candidate")
        for label, data in candidates.items():
            data["analysis"] = analyze(data["candidate"])
            if first is not None and label != "Initial candidate":
                data["diff_from_initial"] = diff(first, data["candidate"])
        evidence = {"captured_at_utc": stamp, "canvas": canvas.name, "capture": cap, "requests": requests,
                    "vision_unchanged_since_initial": bool(initial) and initial["private"]["vision"] == vision_now}
        shareable_requests = [{k: v for k, v in r.items() if k != "private"} | {
            "responses": [{k: v for k, v in s.items() if k != "candidate"} for s in r["responses"]]} for r in requests]
        (out / "private" / "report-full.md").write_text(
            render(evidence, candidates, private=True, level="text", redact=[]), encoding="utf-8")
        (out / "shareable").mkdir()
        (out / "shareable" / "report.md").write_text(
            render(evidence | {"requests": shareable_requests}, candidates, private=False, level=share,
                   redact=args.redact), encoding="utf-8")
        (out / "shareable" / "evidence.json").write_text(json.dumps(
            evidence | {"requests": shareable_requests, "sharing_level": share,
                        "candidates": {k: {"analysis": v["analysis"], "diff_from_initial": v.get("diff_from_initial"),
                                           "sanitized": sanitize(v["candidate"], share, args.redact)}
                                       for k, v in candidates.items()}},
            indent=2, ensure_ascii=False), encoding="utf-8")
        sums = [f"{sha256_file(p)}  {p.relative_to(out).as_posix()}" for p in sorted(out.rglob("*")) if p.is_file()]
        (out / "SHA256SUMS.txt").write_text("\n".join(sums) + "\n", encoding="utf-8")
        print(f"captured {canvas.name} -> {out}" + ("" if cap["stable"] else
              "  WARNING: project changed during capture; close Studio and recapture"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
