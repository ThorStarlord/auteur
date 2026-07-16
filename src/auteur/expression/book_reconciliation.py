"""Read-only ownership routing for externally edited Book manuscripts.

Phase A implements read-only inspection and ownership routing. Phase B adds
Book-owned proposal planning (derived, deterministic application plans) and
atomic publication of unaccepted, noncanonical Book candidates. Publication is
NOT acceptance: no accepted Book pointer, Chapter Expression, Structure,
Identity, Blueprint, Realization, or Scene is ever mutated.
"""

from __future__ import annotations

import hashlib
import json
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

# Book-owned proposal types (produced by Phase A routing) map deterministically
# to durable, unaccepted candidate artifact types published in Phase B.
PROPOSAL_CANDIDATE_TYPES = {
    "book_separator_patch": "book_separator_candidate",
    "book_order_change_proposal": "book_order_candidate",
    "book_title_patch": "book_title_rendering_candidate",
    "book_title_change_proposal": "book_title_rendering_candidate",
    "book_insertion_proposal": "book_inserted_material_candidate",
    "book_inserted_material_patch": "book_inserted_material_candidate",
}
PROPOSAL_TRANSFORMATION = ("expression.propose_book_change", 1)
INSPECTION_TRANSFORMATION = ("expression.inspect_book_manuscript", 1)
PUBLICATION_TRANSFORMATION = {"id": "expression.publish_book_application", "version": 1}


def _hash(text: str) -> str:
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()


class BookPublicationRejected(ValueError):
    """Raised when a Book application plan cannot be published.

    ``result`` carries the structured rejection: a ``status`` (for example
    ``rejected_stale`` or ``rejected_duplicate``), the freshness ``reasons``,
    and ``visible_outputs_created=False`` -- a stale or duplicate plan publishes
    nothing.
    """

    def __init__(self, result: dict[str, Any]):
        self.result = result
        super().__init__(result.get("message", "book publication rejected"))


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
            # Suppress the per-chapter "modified" findings: when text has moved
            # across chapter boundaries we cannot cleanly attribute edits to
            # individual chapters, and routing each chapter to independent
            # reconciliation would risk duplicating or losing the moved text.
            # The single cross_boundary_move finding requires manual mapping.
            chapter_findings = [f for f in chapter_findings if f["classification"] != "modified"]
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
        proposal_dir = self.root / "proposals"
        routes, proposals, delegated_paths = [], [], []
        try:
            for finding in report["chapter_findings"]:
                manuscript = Path(report["external_manuscript"]["path"])
                delegated = ReconciliationStore(self.project).inspect(manuscript, finding["source_chapter_expression"])
                delegated_paths.append(next(self.project.glob(f"chapters/*/expression/reconciliation/inspections/{delegated['inspection_id']}.yaml")))
                routes.append({"chapter_id": finding["chapter_id"], "chapter_inspection_id": delegated["inspection_id"], "parent_book_inspection_id": inspection_id})
            staged.mkdir(parents=True, exist_ok=True)
            for index, finding in enumerate(report["book_findings"], 1):
                proposal_id = f"proposal_{inspection_id}_{index:03d}"
                proposal = {"proposal_id": proposal_id, "artifact_type": "book_expression_proposal", "authority": "derived", "lifecycle": "proposed", "book_expression_id": report["book_expression_id"], "source_book_revision": report["book_revision"], "source_book_hash": report["book_content_hash"], "source_inspection_id": inspection_id, "proposal_type": finding["recommended_proposal"], "target": finding.get("target_id"), "expected_revision": report["book_revision"], "expected_hash": report["book_content_hash"], "original": finding.get("original_text"), "proposed": finding.get("edited_text"), "evidence": finding, "transformation": {"id": "expression.propose_book_change", "version": 1}, "created_at": datetime.now(timezone.utc).isoformat(), "freshness": "fresh"}
                (staged / f"{proposal_id}.yaml").write_text(yaml.safe_dump(proposal, sort_keys=False), encoding="utf-8"); proposals.append(proposal_id)
            manifest = {"routing_id": f"routing_{inspection_id}", "source_inspection_id": inspection_id, "source_book_expression": report["book_expression_id"], "external_manuscript_hash": report["external_manuscript"]["content_hash"], "chapter_routes": routes, "book_proposals": proposals, "unresolved": report["unresolved_findings"], "status": "unresolved" if report["unresolved_findings"] else "routed", "created_at": datetime.now(timezone.utc).isoformat()}
            staged_manifest = staged / "manifest.yaml"
            staged_manifest.write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")

            # Validation pass: every artifact this routing is supposed to produce
            # must exist in staging before anything is moved into place. This
            # catches partial-write failures before they can become partial
            # published state.
            expected_files = {f"{proposal_id}.yaml" for proposal_id in proposals} | {"manifest.yaml"}
            actual_files = {path.name for path in staged.glob("*.yaml")}
            if actual_files != expected_files:
                raise RuntimeError(
                    f"Staged routing outputs incomplete for {inspection_id}: "
                    f"expected {sorted(expected_files)}, found {sorted(actual_files)}"
                )

            # Commit: move every staged artifact into its final, visible
            # location. If any move in this batch fails, we roll back every
            # artifact already moved so the routing never becomes partially
            # visible -- either every proposal and the manifest appear
            # together, or none of them do.
            proposal_dir.mkdir(parents=True, exist_ok=True)
            final.parent.mkdir(parents=True, exist_ok=True)
            moved: list[Path] = []
            try:
                for proposal_id in proposals:
                    name = f"{proposal_id}.yaml"
                    dest = proposal_dir / name
                    shutil.move(str(staged / name), str(dest))
                    moved.append(dest)
                shutil.move(str(staged_manifest), str(final))
                moved.append(final)
            except Exception:
                for path in moved:
                    if path.exists(): path.unlink()
                raise
            if staged.exists(): shutil.rmtree(staged, ignore_errors=True)
            return manifest
        except Exception:
            if final.exists(): final.unlink()
            if staged.exists(): shutil.rmtree(staged, ignore_errors=True)
            for path in delegated_paths:
                if path.exists(): path.unlink()
            raise

    # ------------------------------------------------------------------
    # Phase B: Book-owned proposal planning and atomic publication.
    #
    # A plan is a derived, deterministic description of a chosen set of
    # Book-owned proposals; it creates no candidates, no preview, and changes
    # no pointer. Publication stages durable, unaccepted candidates plus a
    # noncanonical preview and a publication manifest, revalidates every live
    # dependency, and either makes them all visible together or none at all.
    # ------------------------------------------------------------------

    def _proposal_path(self, proposal_id: str) -> Path:
        return self.root / "proposals" / f"{proposal_id}.yaml"

    def _load_proposal(self, proposal_id: str) -> dict[str, Any] | None:
        path = self._proposal_path(proposal_id)
        if not path.exists():
            return None
        return yaml.safe_load(path.read_text(encoding="utf-8")) or {}

    def _plan_path(self, plan_id: str) -> Path:
        return self.root / "plans" / f"{plan_id}.yaml"

    def _load_plan(self, plan_id: str) -> dict[str, Any]:
        path = self._plan_path(plan_id)
        if not path.exists():
            raise FileNotFoundError(f"Book application plan not found: {plan_id}")
        return yaml.safe_load(path.read_text(encoding="utf-8")) or {}

    @staticmethod
    def _is_fresh(value: Any) -> bool:
        """Accept both the string ``"fresh"`` and ``{"status": "fresh"}`` forms."""
        if isinstance(value, dict):
            return value.get("status") == "fresh"
        return value == "fresh"

    @staticmethod
    def _candidate_id(plan_id: str, proposal_id: str) -> str:
        digest = hashlib.sha256((plan_id + proposal_id).encode("utf-8")).hexdigest()
        return f"book_candidate_{digest[:32]}"

    @staticmethod
    def _current_order(metadata: dict[str, Any]) -> list[str]:
        return [item["chapter_id"] for item in metadata["chapters"]]

    def _book_source_text(self, book: BookExpressionStore, metadata: dict[str, Any]) -> str:
        return book._path(metadata["revision"], "md").read_text(encoding="utf-8")

    def plan(self, inspection_id: str, proposal_ids: list[str]) -> dict[str, Any]:
        """Persist a derived, deterministic Book application plan.

        The plan validates each selected Book-owned proposal (support, freshness,
        source match, transformation), detects conflicts (duplicate targets,
        conflicting orders), and records planned candidate outputs. It creates no
        candidate, no preview, and never changes a pointer.
        """
        report = self._load_inspection(inspection_id)
        book_id = report["book_expression_id"]
        source_book_revision = report["book_revision"]
        source_book_hash = report["book_content_hash"]
        external_manuscript_hash = report["external_manuscript"]["content_hash"]

        plan_id = "book_application_set_" + hashlib.sha256(
            (inspection_id + "\0" + "\0".join(proposal_ids)).encode("utf-8")
        ).hexdigest()[:16]

        proposals: list[dict[str, Any]] = []
        validations: list[dict[str, Any]] = []
        conflicts: list[dict[str, Any]] = []
        seen_ids: set[str] = set()
        targets: dict[str, list[str]] = {}

        for proposal_id in proposal_ids:
            if proposal_id in seen_ids:
                conflicts.append({"conflict_code": "duplicate_proposal_selection", "proposal_ids": [proposal_id], "target_id": None, "summary": "The same proposal was selected more than once.", "recommended_action": "Select each proposal once."})
                continue
            seen_ids.add(proposal_id)
            proposal = self._load_proposal(proposal_id)
            if proposal is None:
                validations.append({"proposal_id": proposal_id, "classification": "unresolved", "reasons": ["proposal does not exist"], "proposal_type": None, "target_id": None})
                continue
            proposals.append(proposal)
            classification, reasons = self._classify_proposal(proposal, inspection_id, source_book_revision, source_book_hash)
            validations.append({"proposal_id": proposal_id, "classification": classification, "reasons": reasons, "proposal_type": proposal.get("proposal_type"), "target_id": proposal.get("target")})
            targets.setdefault(proposal.get("target"), []).append(proposal_id)

        for target, ids in targets.items():
            if len(ids) > 1:
                conflicts.append({"conflict_code": "duplicate_targets", "proposal_ids": ids, "target_id": target, "summary": "Multiple selected proposals target the same Book element.", "recommended_action": "Select one proposal per Book target."})
        order_proposals = [p["proposal_id"] for p in proposals if p.get("proposal_type") == "book_order_change_proposal"]
        if len(order_proposals) > 1:
            conflicts.append({"conflict_code": "conflicting_orders", "proposal_ids": order_proposals, "target_id": book_id, "summary": "Multiple Chapter-order proposals were selected.", "recommended_action": "Select one Chapter-order proposal."})

        fresh_ids = {item["proposal_id"] for item in validations if item["classification"] == "fresh"}
        planned_outputs = []
        for proposal in proposals:
            if proposal["proposal_id"] not in fresh_ids:
                continue
            candidate_type = PROPOSAL_CANDIDATE_TYPES[proposal["proposal_type"]]
            planned_outputs.append({
                "output_type": candidate_type,
                "target_id": proposal.get("target"),
                "source_proposal_id": proposal["proposal_id"],
                "planned_candidate_id": self._candidate_id(plan_id, proposal["proposal_id"]),
                "original": proposal.get("original"),
                "proposed": proposal.get("proposed"),
            })

        reasons: list[str] = []
        if not proposal_ids:
            status = "not_ready"
            reasons.append("no proposals selected")
        elif conflicts:
            status = "conflicted"
            reasons.extend(sorted({item["conflict_code"] for item in conflicts}))
        elif any(item["classification"] == "unsupported" for item in validations):
            status = "unsupported"
            reasons.append("one or more selected proposals are unsupported")
        elif any(item["classification"] in {"invalid", "unresolved"} for item in validations):
            status = "not_ready"
            reasons.append("one or more selected proposals are invalid or unresolved")
        elif any(item["classification"] == "stale" for item in validations):
            status = "stale"
            reasons.append("one or more selected proposals are stale")
        else:
            status = "ready"

        plan = {
            "plan_id": plan_id,
            "artifact_type": "book_reconciliation_plan",
            "authority": "derived",
            "lifecycle": "planned",
            "source_inspection_id": inspection_id,
            "source_book_expression": book_id,
            "source_book_revision": source_book_revision,
            "source_book_hash": source_book_hash,
            "external_manuscript_hash": external_manuscript_hash,
            "selected_proposals": proposal_ids,
            "planned_outputs": planned_outputs,
            "conflicts": conflicts,
            "freshness_results": validations,
            "readiness": {"status": status, "reasons": reasons},
            "transformation": dict(PUBLICATION_TRANSFORMATION),
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        self._plan_path(plan_id).parent.mkdir(parents=True, exist_ok=True)
        self._plan_path(plan_id).write_text(yaml.safe_dump(plan, sort_keys=False), encoding="utf-8")
        return plan

    def _classify_proposal(self, proposal: dict[str, Any], inspection_id: str, source_book_revision: Any, source_book_hash: Any) -> tuple[str, list[str]]:
        kind = proposal.get("proposal_type")
        if kind not in PROPOSAL_CANDIDATE_TYPES:
            return "unsupported", [f"proposal type is not supported: {kind}"]
        if proposal.get("transformation", {}).get("id") != PROPOSAL_TRANSFORMATION[0] or proposal.get("transformation", {}).get("version") != PROPOSAL_TRANSFORMATION[1]:
            return "unsupported", ["transformation contract is unsupported"]
        if proposal.get("lifecycle") != "proposed":
            return "invalid", [f"proposal lifecycle is not applicable: {proposal.get('lifecycle')}"]
        if proposal.get("source_inspection_id") != inspection_id:
            return "invalid", ["proposal belongs to a different inspection"]
        if not self._is_fresh(proposal.get("freshness")):
            return "stale", ["proposal is no longer fresh"]
        if proposal.get("source_book_revision") != source_book_revision or proposal.get("source_book_hash") != source_book_hash:
            return "stale", ["proposal source Book revision or hash differs from inspection"]
        book = BookExpressionStore(self.project)
        try:
            inspected = book.inspect(proposal["book_expression_id"])
        except FileNotFoundError:
            return "stale", ["source Book Manuscript is unavailable"]
        metadata = inspected["metadata"]
        if inspected["freshness"] != "fresh":
            return "stale", ["source Book Manuscript is stale"]
        if metadata["revision"] != source_book_revision or _hash(self._book_source_text(book, metadata)) != source_book_hash:
            return "stale", ["accepted Book revision or hash changed"]
        target_reason = self._target_current(proposal, metadata)
        if target_reason is not None:
            return "stale", [target_reason]
        return "fresh", []

    def _target_current(self, proposal: dict[str, Any], metadata: dict[str, Any]) -> str | None:
        """Return a stale reason if the proposal target no longer matches, else None."""
        kind = proposal.get("proposal_type")
        if kind == "book_order_change_proposal":
            if proposal.get("target") != metadata["book_id"]:
                return "order proposal target is not the Book"
            if proposal.get("original") != ", ".join(self._current_order(metadata)):
                return "accepted Chapter order changed"
        elif kind in {"book_separator_patch"}:
            expected_separators = max(len(metadata["chapters"]) - 1, 0)
            if expected_separators < 1:
                return "Book has no separator target"
            current = metadata["book_owned_content"].get("separator", "---")
            if proposal.get("original") is not None and proposal.get("original") != current:
                return "accepted separator changed"
        elif kind in {"book_title_patch", "book_title_change_proposal"}:
            current = metadata["book_owned_content"].get("title", "")
            if proposal.get("original") is not None and proposal.get("original") != current:
                return "accepted Book title changed"
        return None

    def show_book_plan(self, plan_id: str) -> dict[str, Any]:
        return self._load_plan(plan_id)

    def _preview_signature(self, metadata: dict[str, Any], applied: dict[str, str]) -> tuple[str, str, list[str]]:
        """Effective (title, separator, order) after applying candidate sources."""
        title = applied.get("title", metadata["book_owned_content"].get("title", ""))
        separator = applied.get("separator", metadata["book_owned_content"].get("separator", "---"))
        if "order" in applied:
            order = applied["order"].split(", ")
        else:
            order = self._current_order(metadata)
        return title, separator, order

    def _build_preview(self, plan: dict[str, Any], metadata: dict[str, Any], candidates: list[dict[str, Any]], publication_id: str) -> dict[str, Any]:
        applied: dict[str, str] = {}
        candidate_sources = []
        applied_proposals = []
        for candidate in candidates:
            candidate_sources.append({"candidate_id": candidate["candidate_id"], "candidate_type": candidate["artifact_type"], "target_id": candidate["target_id"], "authority": "candidate", "lifecycle": "proposed"})
            applied_proposals.append(candidate["source_proposal_id"])
            if candidate["artifact_type"] == "book_separator_candidate":
                applied["separator"] = candidate["proposed"]
            elif candidate["artifact_type"] == "book_order_candidate":
                applied["order"] = candidate["proposed"]
            elif candidate["artifact_type"] == "book_title_rendering_candidate":
                applied["title"] = candidate["proposed"]
        title, separator, order = self._preview_signature(metadata, applied)
        by_id = {item["chapter_id"]: item for item in metadata["chapters"]}
        accepted_chapter_sources = [
            {"chapter_id": chapter_id, "chapter_expression_id": by_id[chapter_id]["chapter_expression_id"], "accepted_revision": by_id[chapter_id]["accepted_revision"], "content_hash": by_id[chapter_id]["content_hash"]}
            for chapter_id in order if chapter_id in by_id
        ]
        signature = json.dumps({"title": title, "separator": separator, "order": order, "chapters": [(item["chapter_id"], item["content_hash"]) for item in accepted_chapter_sources]}, sort_keys=True)
        content_hash = _hash(signature)
        return {
            "source_plan_id": plan["plan_id"],
            "source_inspection_id": plan["source_inspection_id"],
            "source_book_expression": plan["source_book_expression"],
            "book_expression_id": f"{plan['source_book_expression']}:application_preview",
            "revision": plan["source_book_revision"],
            "content_hash": content_hash,
            "candidate_sources": candidate_sources,
            "accepted_chapter_sources": accepted_chapter_sources,
            "applied_proposals": applied_proposals,
            "authority": "derived",
            "lifecycle": "proposed",
            "role": "application_preview",
            "canonical": False,
            "publication_id": publication_id,
        }

    def publish(self, plan_id: str) -> dict[str, Any]:
        """Publish a ready Book plan transactionally into unaccepted candidates.

        Stages all candidates, the preview, and the manifest outside their final
        paths; revalidates every live dependency; then moves everything into
        place atomically. Any failure rolls back so that all outputs are visible
        or none are. Publication never accepts a candidate or changes a pointer.
        """
        plan = self._load_plan(plan_id)
        publication_id = "book_publication_" + plan_id.removeprefix("book_application_set_")
        publication_path = self.root / "publications" / f"{publication_id}.yaml"
        preview_path = self.root / "previews" / f"{publication_id}.yaml"
        candidates_dir = self.root / "candidates"

        if publication_path.exists():
            raise BookPublicationRejected({"status": "rejected_duplicate", "message": f"Book application plan has already been published: {plan_id}", "publication_id": publication_id, "reasons": [{"code": "PLAN_ALREADY_PUBLISHED", "recommended_action": "inspect the existing publication"}], "visible_outputs_created": False})

        validation = self._final_revalidate(plan)
        if validation["status"] != "ready":
            raise BookPublicationRejected(validation)

        book = BookExpressionStore(self.project)
        inspected = book.inspect(plan["source_book_expression"])
        metadata = inspected["metadata"]

        candidates: list[dict[str, Any]] = []
        for proposal_id in plan["selected_proposals"]:
            proposal = self._load_proposal(proposal_id)
            candidate_id = self._candidate_id(plan_id, proposal_id)
            candidates.append({
                "candidate_id": candidate_id,
                "artifact_type": PROPOSAL_CANDIDATE_TYPES[proposal["proposal_type"]],
                "authority": "candidate",
                "lifecycle": "proposed",
                "book_expression_id": plan["source_book_expression"],
                "target_id": proposal.get("target"),
                "source_book_revision": plan["source_book_revision"],
                "source_book_hash": plan["source_book_hash"],
                "original": proposal.get("original"),
                "proposed": proposal.get("proposed"),
                "source_inspection_id": plan["source_inspection_id"],
                "source_proposal_id": proposal_id,
                "source_plan_id": plan_id,
                "publication_id": publication_id,
                "transformation": dict(PUBLICATION_TRANSFORMATION),
                "created_at": datetime.now(timezone.utc).isoformat(),
                "freshness": {"status": "fresh", "reasons": []},
            })

        preview = self._build_preview(plan, metadata, candidates, publication_id)
        manifest = {
            "publication_id": publication_id,
            "artifact_type": "book_reconciliation_publication",
            "authority": "derived",
            "lifecycle": "published",
            "source_plan_id": plan_id,
            "source_inspection_id": plan["source_inspection_id"],
            "source_book_expression": plan["source_book_expression"],
            "source_book_revision": plan["source_book_revision"],
            "source_book_hash": plan["source_book_hash"],
            "external_manuscript_hash": plan["external_manuscript_hash"],
            "published_candidates": [item["candidate_id"] for item in candidates],
            "preview": {"book_expression_id": preview["book_expression_id"], "revision": preview["revision"], "content_hash": preview["content_hash"], "authority": "derived", "lifecycle": "proposed", "role": "application_preview"},
            "acceptance_status": "none",
            "accepted_book_pointer_changed": False,
            "transformation": dict(PUBLICATION_TRANSFORMATION),
            "created_at": datetime.now(timezone.utc).isoformat(),
            "freshness": {"status": "fresh", "reasons": []},
        }

        staging = self.root / "staging" / publication_id
        try:
            if staging.exists():
                shutil.rmtree(staging, ignore_errors=True)
            staging.mkdir(parents=True, exist_ok=True)
            for candidate in candidates:
                (staging / f"{candidate['candidate_id']}.yaml").write_text(yaml.safe_dump(candidate, sort_keys=False), encoding="utf-8")
            (staging / "preview.yaml").write_text(yaml.safe_dump(preview, sort_keys=False), encoding="utf-8")
            (staging / "manifest.yaml").write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")

            # Validation pass: every planned candidate is staged, IDs and targets
            # match the plan, no conflicts, and the preview draws only on accepted
            # Chapter sources plus Book-owned candidates (no Chapter-local
            # proposals). Nothing canonical or accepted is touched.
            expected_files = {f"{item['candidate_id']}.yaml" for item in candidates} | {"preview.yaml", "manifest.yaml"}
            actual_files = {path.name for path in staging.glob("*.yaml")}
            if actual_files != expected_files:
                raise RuntimeError(f"Staged publication outputs incomplete for {publication_id}: expected {sorted(expected_files)}, found {sorted(actual_files)}")
            planned_ids = {item["planned_candidate_id"] for item in plan["planned_outputs"]}
            staged_ids = {item["candidate_id"] for item in candidates}
            if planned_ids != staged_ids:
                raise RuntimeError(f"Staged candidate ids diverge from plan: planned {sorted(planned_ids)}, staged {sorted(staged_ids)}")
            for candidate in candidates:
                if candidate["target_id"] not in {item["target_id"] for item in plan["planned_outputs"]}:
                    raise RuntimeError(f"Candidate target not present in plan: {candidate['target_id']}")
            if any(source.get("source_kind") == "chapter_local_proposal" for source in preview["candidate_sources"]):
                raise RuntimeError("preview must not include Chapter-local proposals")

            # Commit: move every staged output into its final, visible location.
            # If any move fails, unlink each artifact already moved so the
            # publication never becomes partially visible.
            candidates_dir.mkdir(parents=True, exist_ok=True)
            preview_path.parent.mkdir(parents=True, exist_ok=True)
            publication_path.parent.mkdir(parents=True, exist_ok=True)
            moved: list[Path] = []
            try:
                for candidate in candidates:
                    name = f"{candidate['candidate_id']}.yaml"
                    dest = candidates_dir / name
                    shutil.move(str(staging / name), str(dest))
                    moved.append(dest)
                shutil.move(str(staging / "preview.yaml"), str(preview_path))
                moved.append(preview_path)
                shutil.move(str(staging / "manifest.yaml"), str(publication_path))
                moved.append(publication_path)
            except Exception:
                for path in moved:
                    if path.exists():
                        path.unlink()
                raise
            if staging.exists():
                shutil.rmtree(staging, ignore_errors=True)
            return manifest
        except Exception:
            if publication_path.exists():
                publication_path.unlink()
            if preview_path.exists():
                preview_path.unlink()
            if staging.exists():
                shutil.rmtree(staging, ignore_errors=True)
            raise

    def _final_revalidate(self, plan: dict[str, Any]) -> dict[str, Any]:
        """Live freshness gate run immediately before staging.

        Every live dependency is revalidated from disk; persisted readiness is
        never trusted. Returns ``status='ready'`` only when nothing changed,
        otherwise ``status='rejected_stale'`` with structured reasons and
        ``visible_outputs_created=False``.
        """
        reasons: list[dict[str, Any]] = []

        def add(code: str, **extra: Any) -> None:
            reasons.append({"code": code, "recommended_action": extra.pop("recommended_action", "create a new Book reconciliation plan"), **extra})

        if plan.get("lifecycle") != "planned" or plan.get("readiness", {}).get("status") != "ready":
            add("PLAN_NOT_READY")
        if plan.get("transformation", {}).get("id") != PUBLICATION_TRANSFORMATION["id"] or plan.get("transformation", {}).get("version") != PUBLICATION_TRANSFORMATION["version"]:
            add("PLAN_TRANSFORMATION_CHANGED")

        inspection_id = plan.get("source_inspection_id")
        try:
            report = self._load_inspection(inspection_id)
        except FileNotFoundError:
            report = {}
            add("INSPECTION_MISSING", inspection_id=inspection_id)
        if report:
            transformation = report.get("provenance", {}).get("transformation", {})
            if (transformation.get("id"), transformation.get("version")) != INSPECTION_TRANSFORMATION:
                add("INSPECTION_TRANSFORMATION_CHANGED")
            if report.get("marker_contract", {}).get("version") != 1:
                add("MARKER_CONTRACT_CHANGED")

        book = BookExpressionStore(self.project)
        metadata: dict[str, Any] = {}
        try:
            inspected = book.inspect(plan.get("source_book_expression"))
            metadata = inspected["metadata"]
            if inspected["freshness"] != "fresh":
                add("BOOK_OR_CHAPTER_REVISION_CHANGED", detail=inspected.get("stale_sources"))
            if metadata.get("revision") != plan.get("source_book_revision"):
                add("BOOK_REVISION_CHANGED", expected=plan.get("source_book_revision"), current=metadata.get("revision"))
            elif _hash(self._book_source_text(book, metadata)) != plan.get("source_book_hash"):
                add("BOOK_HASH_CHANGED")
            current_order = self._current_order(metadata)
        except FileNotFoundError:
            add("BOOK_MISSING")
            current_order = []

        manuscript_ref = report.get("external_manuscript", {}) if report else {}
        if manuscript_ref.get("path"):
            manuscript = Path(manuscript_ref["path"])
            if not manuscript.exists():
                add("MANUSCRIPT_HASH_CHANGED", recommended_action="restore the imported manuscript and create a new plan")
            elif _hash(manuscript.read_text(encoding="utf-8")) != plan.get("external_manuscript_hash"):
                add("MANUSCRIPT_HASH_CHANGED")

        targets: dict[str, list[str]] = {}
        for proposal_id in plan.get("selected_proposals", []):
            proposal = self._load_proposal(proposal_id)
            if proposal is None:
                add("TARGET_MISSING", proposal_id=proposal_id)
                continue
            if proposal.get("lifecycle") != "proposed":
                add("PROPOSAL_STATUS_CHANGED", proposal_id=proposal_id, current_status=proposal.get("lifecycle"))
            if not self._is_fresh(proposal.get("freshness")):
                add("PROPOSAL_STATUS_CHANGED", proposal_id=proposal_id, current_status=proposal.get("freshness"))
            if proposal.get("transformation", {}).get("version") != PROPOSAL_TRANSFORMATION[1] or proposal.get("transformation", {}).get("id") != PROPOSAL_TRANSFORMATION[0]:
                add("TRANSFORMATION_VERSION_CHANGED", proposal_id=proposal_id)
            if proposal.get("proposal_type") not in PROPOSAL_CANDIDATE_TYPES:
                add("PROPOSAL_UNSUPPORTED", proposal_id=proposal_id)
            if proposal.get("source_inspection_id") != inspection_id:
                add("SOURCE_INSPECTION_CHANGED", proposal_id=proposal_id)
            if proposal.get("source_book_revision") != plan.get("source_book_revision") or proposal.get("source_book_hash") != plan.get("source_book_hash"):
                add("SOURCE_BOOK_CHANGED", proposal_id=proposal_id)
            target = proposal.get("target")
            targets.setdefault(target, []).append(proposal_id)
            if metadata:
                reason = self._target_current(proposal, metadata)
                if reason is not None:
                    code = "SEPARATOR_CHANGED" if "separator" in reason else ("CHAPTER_ORDER_CHANGED" if "order" in reason else "TARGET_CHANGED")
                    add(code, proposal_id=proposal_id, detail=reason)
                if proposal.get("proposal_type") == "book_order_change_proposal":
                    proposed_order = (proposal.get("proposed") or "").split(", ")
                    if sorted(proposed_order) != sorted(current_order):
                        add("TARGET_IDS_INVALID", proposal_id=proposal_id, detail="proposed order references unknown Chapters")
                elif proposal.get("target") and proposal.get("proposal_type") == "book_separator_patch":
                    if max(len(metadata["chapters"]) - 1, 0) < 1:
                        add("TARGET_IDS_INVALID", proposal_id=proposal_id, detail="no separator target exists")

        for target, ids in targets.items():
            if len(ids) > 1:
                add("DUPLICATE_TARGETS", target_id=target, proposal_ids=ids)
        order_proposals = [pid for pid in plan.get("selected_proposals", []) if (self._load_proposal(pid) or {}).get("proposal_type") == "book_order_change_proposal"]
        if len(order_proposals) > 1:
            add("CONFLICTING_ORDERS", proposal_ids=order_proposals)

        if reasons:
            return {"status": "rejected_stale", "message": "Book application plan is stale", "reasons": reasons, "visible_outputs_created": False}
        return {"status": "ready", "message": "publication dependencies are fresh", "reasons": [], "visible_outputs_created": False}

    def inspect_book_publication(self, publication_id: str) -> dict[str, Any]:
        path = self.root / "publications" / f"{publication_id}.yaml"
        if not path.exists():
            raise FileNotFoundError(f"Book publication not found: {publication_id}")
        return yaml.safe_load(path.read_text(encoding="utf-8")) or {}

    def load_book_preview(self, publication_id: str) -> dict[str, Any]:
        path = self.root / "previews" / f"{publication_id}.yaml"
        if not path.exists():
            raise FileNotFoundError(f"Book preview not found: {publication_id}")
        return yaml.safe_load(path.read_text(encoding="utf-8")) or {}

    def load_book_candidate(self, candidate_id: str) -> dict[str, Any]:
        path = self.root / "candidates" / f"{candidate_id}.yaml"
        if not path.exists():
            raise FileNotFoundError(f"Book candidate not found: {candidate_id}")
        return yaml.safe_load(path.read_text(encoding="utf-8")) or {}
