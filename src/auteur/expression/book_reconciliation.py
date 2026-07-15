"""Read-only ownership routing for externally edited Book manuscripts."""

from __future__ import annotations

import hashlib
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from auteur.expression.book import BookExpressionStore
from auteur.expression.reconciliation import ReconciliationStore

CHAPTER = re.compile(r"^<!-- auteur:chapter id=([^ ]+) expression_revision=(\d+) -->$")
END_CHAPTER = re.compile(r"^<!-- auteur:end-chapter id=([^ ]+) -->$")
SEPARATOR = re.compile(r"^<!-- auteur:book-separator id=([^ ]+) revision=(\d+) -->$")
END_SEPARATOR = re.compile(r"^<!-- auteur:end-book-separator id=([^ ]+) -->$")


def _hash(text: str) -> str:
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()


class BookManuscriptParser:
    def parse(self, text: str) -> dict[str, Any]:
        chapters, separators, findings, owned = [], [], [], set()
        open_kind = open_id = None
        start = 0
        for number, line in enumerate(text.splitlines(), 1):
            marker = CHAPTER.match(line) or SEPARATOR.match(line)
            end = END_CHAPTER.match(line) or END_SEPARATOR.match(line)
            if "<!-- auteur:" in line and not marker and not end:
                findings.append({"classification": "malformed_marker", "line": number, "evidence": line, "recommended_action": "repair the internal Book marker"})
            if marker:
                kind = "chapter" if CHAPTER.match(line) else "separator"
                ident = marker.group(1)
                if open_kind:
                    findings.append({"classification": "malformed_marker", "line": number, "evidence": "nested marker", "recommended_action": "close the current marker before opening another"})
                open_kind, open_id, start = kind, ident, number
            elif end:
                kind = "chapter" if END_CHAPTER.match(line) else "separator"
                ident = end.group(1)
                if open_kind != kind or open_id != ident:
                    findings.append({"classification": "malformed_marker", "line": number, "evidence": "mismatched closing marker", "recommended_action": "match opening and closing marker IDs"})
                else:
                    lines = text.splitlines()
                    content = "\n".join(lines[start:number - 1]).strip()
                    item = {"id": ident, "text": content, "line_range": [start, number], "kind": kind}
                    (chapters if kind == "chapter" else separators).append(item)
                    owned.update(range(start - 1, number))
                open_kind = open_id = None
        if open_kind:
            findings.append({"classification": "malformed_marker", "line": len(text.splitlines()), "evidence": f"missing closing marker for {open_id}", "recommended_action": "add the matching closing marker"})
        if not chapters and not separators and not findings:
            findings.append({"classification": "markerless", "line_range": [1, len(text.splitlines())], "evidence": "no Book ownership markers", "recommended_action": "restore Book markers or map the manuscript manually"})
        return {"chapters": chapters, "separators": separators, "findings": findings}


class BookReconciliationStore:
    def __init__(self, project: Path) -> None:
        self.project = Path(project)
        self.root = self.project / "book" / "expression" / "reconciliation"

    def _inspection_path(self, inspection_id: str) -> Path:
        return self.root / "inspections" / f"{inspection_id}.yaml"

    def _load_inspection(self, inspection_id: str) -> dict[str, Any]:
        path = next(self.root.glob(f"inspections/{inspection_id}.yaml"), None)
        if path is None: raise FileNotFoundError(f"Book inspection not found: {inspection_id}")
        return yaml.safe_load(path.read_text(encoding="utf-8")) or {}

    def inspect(self, manuscript: Path, against: str) -> dict[str, Any]:
        book = BookExpressionStore(self.project)
        metadata = book._load(against)
        source_text = book._path(metadata["revision"], "md").read_text(encoding="utf-8")
        external = Path(manuscript).read_text(encoding="utf-8")
        parsed = BookManuscriptParser().parse(external)
        expected = {item["chapter_id"]: item for item in metadata["chapters"]}
        chapter_findings, book_findings, unresolved = [], [], []
        for finding in parsed["findings"]:
            (unresolved if finding["classification"] in {"markerless", "malformed_marker"} else book_findings).append(finding)
        if any(item["classification"] == "markerless" for item in parsed["findings"]):
            unresolved = [{"finding_id": "unresolved:markerless", **parsed["findings"][0]}]
        seen = []
        for item in parsed["chapters"]:
            chapter_id = item["id"]; seen.append(chapter_id)
            if chapter_id not in expected:
                unresolved.append({"finding_id": f"unresolved:unknown:{chapter_id}", "classification": "unknown_chapter", "line_range": item["line_range"], "evidence": chapter_id, "recommended_action": "map the Chapter explicitly"}); continue
            original = book._chapter_text(book._accepted_chapter(chapter_id))
            if item["text"] != original:
                chapter_findings.append({"finding_id": f"chapter:{chapter_id}", "chapter_id": chapter_id, "source_chapter_expression": expected[chapter_id]["chapter_expression_id"], "source_revision": expected[chapter_id]["accepted_revision"], "source_hash": expected[chapter_id]["content_hash"], "classification": "modified", "change_summary": "Chapter wording changed", "original_text_hash": _hash(original), "edited_text_hash": _hash(item["text"]), "route": "chapter_reconciliation", "edited_text": item["text"]})
        if seen != [item["chapter_id"] for item in metadata["chapters"]] and seen:
            book_findings.append({"finding_id": "book:order", "owner": "book_expression", "target_id": metadata["book_id"], "classification": "order_changed", "source_revision": metadata["revision"], "source_hash": _hash(source_text), "original_text": ", ".join(item["chapter_id"] for item in metadata["chapters"]), "edited_text": ", ".join(seen), "recommended_proposal": "book_order_change_proposal"})
        # Detect cross-chapter text movement: multiple chapters modified, order unchanged
        modified_chapters = [f["chapter_id"] for f in chapter_findings if f["classification"] == "modified"]
        order_changed = any(f["classification"] == "order_changed" for f in book_findings)
        if len(modified_chapters) > 1 and not order_changed:
            unresolved.append({"finding_id": "unresolved:cross_boundary_move", "classification": "cross_boundary_move", "evidence": "Multiple chapters have text changes; text appears to have moved across chapter boundaries", "recommended_action": "Manually map the text movements or retain the divergence", "affected_chapters": modified_chapters, "severity": "unresolved"})
        # Only check separators if the manuscript is marked (not markerless)
        # Markerless manuscripts can't have meaningful separator checks since we lack ownership information
        is_markerless = any(item["classification"] == "markerless" for item in parsed["findings"])
        if not is_markerless:
            expected_separators = max(len(metadata["chapters"]) - 1, 0)
            if len(parsed["separators"]) != expected_separators:
                book_findings.append({"finding_id": "book:separator", "owner": "book_expression", "target_id": "separator_01", "classification": "separator_changed", "source_revision": metadata["revision"], "source_hash": _hash(source_text), "recommended_proposal": "book_separator_patch"})
            elif any(item["text"] != metadata["book_owned_content"].get("separator", "---") for item in parsed["separators"]):
                book_findings.append({"finding_id": "book:separator", "owner": "book_expression", "target_id": "separator_01", "classification": "separator_changed", "source_revision": metadata["revision"], "source_hash": _hash(source_text), "original_text": metadata["book_owned_content"].get("separator", "---"), "edited_text": parsed["separators"][0]["text"], "recommended_proposal": "book_separator_patch"})
        if any(item["classification"] in {"markerless", "cross_boundary_move"} for item in unresolved):
            status = "unresolved"
        elif chapter_findings or book_findings or unresolved:
            status = "changed"
        else: status = "no_changes"
        inspection_id = "inspection_" + datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S%f")
        report = {"inspection_id": inspection_id, "artifact_type": "book_edit_inspection", "authority": "derived", "lifecycle": "generated", "book_expression_id": against, "book_revision": metadata["revision"], "book_content_hash": _hash(source_text), "external_manuscript": {"path": str(manuscript), "content_hash": _hash(external)}, "marker_contract": {"version": 1}, "status": status, "chapter_findings": chapter_findings, "book_findings": book_findings, "unresolved_findings": unresolved, "provenance": {"transformation": {"id": "expression.inspect_book_manuscript", "version": 1}, "accepted_book": against, "accepted_chapters": metadata["chapters"], "created_at": datetime.now(timezone.utc).isoformat()}, "freshness": {"status": "fresh", "reasons": []}}
        self._inspection_path(inspection_id).parent.mkdir(parents=True, exist_ok=True)
        self._inspection_path(inspection_id).write_text(yaml.safe_dump(report, sort_keys=False), encoding="utf-8")
        return report

    def route(self, inspection_id: str) -> dict[str, Any]:
        report = self._load_inspection(inspection_id)
        book = BookExpressionStore(self.project)
        if book.inspect(report["book_expression_id"])["freshness"] != "fresh":
            report["status"] = "stale"
            report["freshness"] = {"status": "stale", "reasons": ["BOOK_OR_CHAPTER_REVISION_CHANGED"]}
            self._inspection_path(inspection_id).write_text(yaml.safe_dump(report, sort_keys=False), encoding="utf-8")
            return {"routing_id": None, "status": "stale", "chapter_routes": [], "book_proposals": [], "unresolved": []}
        staged = self.root / "staging" / inspection_id
        final = self.root / "routing" / f"routing_{inspection_id}.yaml"
        routes, proposals, delegated_paths = [], [], []
        try:
            for finding in report["chapter_findings"]:
                manuscript = Path(report["external_manuscript"]["path"])
                delegated = ReconciliationStore(self.project).inspect(manuscript, finding["source_chapter_expression"])
                delegated_paths.append(next(self.project.glob(f"chapters/*/expression/reconciliation/inspections/{delegated['inspection_id']}.yaml")))
                routes.append({"chapter_id": finding["chapter_id"], "chapter_inspection_id": delegated["inspection_id"], "parent_book_inspection_id": inspection_id})
            for index, finding in enumerate(report["book_findings"], 1):
                proposal_id = f"proposal_{inspection_id}_{index:03d}"
                proposal = {"proposal_id": proposal_id, "artifact_type": "book_expression_proposal", "authority": "derived", "lifecycle": "proposed", "book_expression_id": report["book_expression_id"], "source_book_revision": report["book_revision"], "source_book_hash": report["book_content_hash"], "source_inspection_id": inspection_id, "proposal_type": finding["recommended_proposal"], "target": finding.get("target_id"), "expected_revision": report["book_revision"], "expected_hash": report["book_content_hash"], "original": finding.get("original_text"), "proposed": finding.get("edited_text"), "evidence": finding, "transformation": {"id": "expression.propose_book_change", "version": 1}, "created_at": datetime.now(timezone.utc).isoformat(), "freshness": "fresh"}
                staged.mkdir(parents=True, exist_ok=True); (staged / f"{proposal_id}.yaml").write_text(yaml.safe_dump(proposal, sort_keys=False), encoding="utf-8"); proposals.append(proposal_id)
            final.parent.mkdir(parents=True, exist_ok=True); manifest = {"routing_id": f"routing_{inspection_id}", "source_inspection_id": inspection_id, "source_book_expression": report["book_expression_id"], "external_manuscript_hash": report["external_manuscript"]["content_hash"], "chapter_routes": routes, "book_proposals": proposals, "unresolved": report["unresolved_findings"], "status": "unresolved" if report["unresolved_findings"] else "routed", "created_at": datetime.now(timezone.utc).isoformat()}; final.write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")
            proposal_dir = self.root / "proposals"; proposal_dir.mkdir(parents=True, exist_ok=True)
            for path in staged.glob("*.yaml"): path.replace(proposal_dir / path.name)
            return manifest
        except Exception:
            if final.exists(): final.unlink()
            if staged.exists(): shutil.rmtree(staged)
            for path in delegated_paths:
                if path.exists(): path.unlink()
            raise
