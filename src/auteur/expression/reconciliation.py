from __future__ import annotations

import difflib
import hashlib
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from auteur.expression.composition import ChapterExpressionStore, MARKER_RE, END_MARKER_RE


def _hash(value: str) -> str:
    return "sha256:" + hashlib.sha256(value.encode("utf-8")).hexdigest()


class ReconciliationStore:
    """Inspection and proposal artifacts; never applies canonical changes."""

    def __init__(self, project: Path):
        self.project = Path(project)
        self.composition = ChapterExpressionStore(project)

    def _root(self, assembly: str) -> Path:
        metadata = self.composition.inspect(assembly)
        return self.composition.chapter_dir(metadata.source_chapter["artifact_id"]) / "reconciliation"

    def _write_atomic(self, path: Path, payload: dict[str, Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        temp = path.with_name(path.name + ".tmp")
        try:
            temp.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")
            temp.replace(path)
        except Exception:
            if temp.exists():
                temp.unlink()
            raise

    @staticmethod
    def _blocks(text: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        blocks, malformed = [], []
        lines = text.splitlines()
        current: dict[str, Any] | None = None
        for line_no, line in enumerate(lines, 1):
            start, end = MARKER_RE.match(line), END_MARKER_RE.match(line)
            if start:
                if current is not None:
                    malformed.append({"classification": "malformed", "line": line_no, "evidence": line})
                current = {"scene_id": start.group(1), "expression_revision": int(start.group(2)), "start_line": line_no, "lines": []}
            elif end:
                if current is None or current["scene_id"] != end.group(1):
                    malformed.append({"classification": "malformed", "line": line_no, "evidence": line})
                elif current is not None:
                    current["end_line"] = line_no
                    current["text"] = "\n".join(current["lines"]).strip()
                    blocks.append(current)
                    current = None
            elif current is not None:
                current["lines"].append(line)
        if current is not None:
            malformed.append({"classification": "malformed", "line": current["start_line"], "evidence": "missing closing marker"})
        return blocks, malformed

    def inspect(self, manuscript: Path, against: str) -> dict[str, Any]:
        assembly = self.composition.inspect(against)
        text = Path(manuscript).read_text(encoding="utf-8")
        imported_hash = _hash(text)
        blocks, malformed = self._blocks(text)
        marker_report = self.composition.inspect_markers(text)
        inspection_id = f"inspection_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')}"
        findings: list[dict[str, Any]] = []
        expected = {item["scene_id"]: item for item in assembly.source_scenes}
        actual_ids = [block["scene_id"] for block in blocks]
        expected_order = [item["scene_id"] for item in assembly.source_scenes]
        if not blocks:
            findings.append(self._finding(inspection_id, "markerless", "unresolved", None, imported_hash, "No reliable Scene ownership can be established", ["restore markers", "manually map sections", "retain Chapter-local divergence", "discard the import"]))
        for item in malformed + marker_report.get("findings", []):
            if item.get("code") != "unresolved_divergence":
                findings.append(self._finding(inspection_id, "malformed", "unresolved", None, imported_hash, item.get("message", "Malformed marker"), [item.get("recommended_action", "repair the marker")]))
        for scene_id, item in expected.items():
            occurrences = [block for block in blocks if block["scene_id"] == scene_id]
            if not occurrences:
                findings.append(self._finding(inspection_id, "missing", "review_required", scene_id, item["expression_content_hash"], "Scene section is missing", ["restore the section", "retain omission as Chapter divergence"]))
                continue
            if len(occurrences) > 1:
                findings.append(self._finding(inspection_id, "duplicated", "error", scene_id, item["expression_content_hash"], "Scene section appears more than once", ["remove the duplicate or map it manually"]))
                continue
            block = occurrences[0]
            source_path = self.composition._scene_path(scene_id).parent / scene_id / f"prose_v{item['expression_revision']:03d}.md"
            source_text = source_path.read_text(encoding="utf-8").strip()
            if block["text"] != source_text:
                ratio = difflib.SequenceMatcher(None, source_text, block["text"]).ratio()
                classification = "modified"
                owner = "Scene Expression" if ratio >= 0.55 else "Scene Expression candidate"
                action = "create a Scene Expression patch proposal" if ratio >= 0.55 else "create a replacement Scene Expression candidate proposal"
                findings.append(self._finding(inspection_id, classification, "review_required", scene_id, item["expression_content_hash"], f"Scene section changed ({len(block['text'].split())} observed words)", [action], observed_hash=_hash(block["text"]), owner=owner, source_revision=item["expression_revision"], detail={"original": source_text, "replacement": block["text"]}))
        block_by_id = {block["scene_id"]: block for block in blocks}
        for transition in assembly.transitions:
            before, after = transition["before_scene"], transition["after_scene"]
            if before not in block_by_id or after not in block_by_id:
                continue
            start = block_by_id[before]["end_line"]
            end = block_by_id[after]["start_line"] - 1
            gap = "\n".join(text.splitlines()[start:end]).strip()
            expected_transition = str(transition.get("text", "")).strip()
            if gap != expected_transition:
                findings.append(self._finding(inspection_id, "transition_modified", "review_required", transition["transition_id"], transition["content_hash"], "Chapter-owned transition changed", ["create a transition patch proposal", "review possible new event ownership"], observed_hash=_hash(gap), owner="Chapter transition", source_revision=transition["revision"], detail={"original": expected_transition, "replacement": gap}))
        if set(actual_ids) == set(expected_order) and actual_ids != expected_order:
            findings.append(self._finding(inspection_id, "moved", "review_required", None, imported_hash, f"Scene order changed from {' → '.join(expected_order)} to {' → '.join(actual_ids)}", ["create a Structure proposal", "retain Chapter-local order divergence"], detail={"previous_order": expected_order, "current_order": actual_ids}))
        outside = self._outside_text(text, blocks)
        if outside.strip():
            findings.append(self._finding(inspection_id, "unsourced", "review_required", None, imported_hash, "Text exists outside known Scene ownership", ["assign it as a transition", "retain Chapter-local divergence", "map it manually"], detail={"text": outside}))
        if len([item for item in findings if item["classification"] == "modified"]) > 1:
            findings.append(self._finding(inspection_id, "cross_boundary", "review_required", None, imported_hash, "Multiple owned sections changed; automatic ownership is unsafe", ["retain Chapter-local divergence", "map text manually", "create replacement candidates"]))
        report = {"inspection_id": inspection_id, "source_assembly": {"artifact_id": assembly.artifact_id, "revision": assembly.revision, "content_hash": assembly.content_hash}, "external_manuscript": {"path": str(Path(manuscript)), "content_hash": imported_hash, "marker_state": marker_report["status"]}, "findings": findings, "status": "unresolved" if any(item["severity"] in {"error", "unresolved"} for item in findings) else "inspected", "created_at": datetime.now(timezone.utc).isoformat()}
        root = self._root(against)
        self._write_atomic(root / "inspections" / f"{inspection_id}.yaml", report)
        run = {"run_id": f"reconcile_{inspection_id.removeprefix('inspection_')}", "transformation": {"id": "expression.reconcile_chapter", "version": 1}, "source_assembly": report["source_assembly"], "external_manuscript": report["external_manuscript"], "inspection_report_id": inspection_id, "proposal_ids": [], "mapping_ids": [], "divergence_ids": [], "status": report["status"], "created_at": report["created_at"]}
        self._write_atomic(root / "runs" / f"{run['run_id']}.yaml", run)
        return report

    @staticmethod
    def _outside_text(text: str, blocks: list[dict[str, Any]]) -> str:
        lines = text.splitlines()
        owned = set()
        for block in blocks:
            owned.update(range(block["start_line"] - 1, block["end_line"]))
        return "\n".join(line for index, line in enumerate(lines) if index not in owned and not MARKER_RE.match(line) and not END_MARKER_RE.match(line))

    @staticmethod
    def _finding(inspection_id: str, classification: str, severity: str, section: str | None, expected_hash: str, evidence: str, actions: list[str], *, owner: str = "unresolved", source_revision: int | None = None, observed_hash: str | None = None, detail: Any = None, **extra: Any) -> dict[str, Any]:
        result = {"finding_id": f"{inspection_id}:{classification}:{section or 'chapter'}:{len(evidence)}", "classification": classification, "severity": severity, "owner": owner, "source_section": section, "source_revision": source_revision, "expected_hash": expected_hash, "observed_hash": observed_hash, "evidence": evidence, "recommended_actions": actions}
        if detail is not None:
            result["detail"] = detail
        result.update(extra)
        return result

    def propose(self, inspection_id: str) -> dict[str, Any]:
        path = next(self.project.glob(f"chapters/*/expression/reconciliation/inspections/{inspection_id}.yaml"), None)
        if path is None:
            raise FileNotFoundError(f"inspection not found: {inspection_id}")
        report = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        root = path.parent.parent
        proposals, ids = [], []
        for index, finding in enumerate(report.get("findings", []), 1):
            if finding["classification"] not in {"modified", "transition_modified"} or not finding.get("detail", {}).get("original"):
                continue
            proposal_id = f"proposal_{inspection_id.removeprefix('inspection_')}_{index:03d}"
            if finding["classification"] == "transition_modified":
                kind = "transition_patch"
            else:
                kind = "scene_expression_patch" if finding["owner"] == "Scene Expression" else "scene_expression_replacement_candidate"
            proposal = {"proposal_id": proposal_id, "proposal_type": kind, "target_artifact_id": finding.get("source_section"), "target_artifact_type": finding.get("owner"), "target_revision": finding.get("source_revision"), "target_content_hash": finding.get("expected_hash"), "source_assembly": report["source_assembly"], "external_manuscript": report["external_manuscript"], "source_inspection": inspection_id, "original_text": finding["detail"]["original"], "replacement_text": finding["detail"]["replacement"], "transformation": {"id": "expression.reconcile_chapter", "version": 1}, "status": "proposed", "created_at": datetime.now(timezone.utc).isoformat()}
            self._write_atomic(root / "proposals" / f"{proposal_id}.yaml", proposal)
            proposals.append(proposal); ids.append(proposal_id)
        report["proposal_ids"] = ids
        report["status"] = "proposals_created" if ids else report.get("status", "inspected")
        self._write_atomic(path, report)
        return {"inspection_id": inspection_id, "proposal_ids": ids, "proposals": proposals, "status": report["status"]}

    def proposal_status(self, proposal_id: str) -> dict[str, Any]:
        path = next(self.project.glob(f"chapters/*/expression/reconciliation/proposals/{proposal_id}.yaml"), None)
        if path is None:
            raise FileNotFoundError(f"proposal not found: {proposal_id}")
        proposal = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        stale_reasons = []
        if proposal.get("proposal_type") != "transition_patch" and proposal.get("target_artifact_id"):
            try:
                metadata, _ = self.composition._accepted_scene(proposal["target_artifact_id"])
                if metadata.get("revision") != proposal.get("target_revision") or metadata.get("content_hash") != proposal.get("target_content_hash"):
                    stale_reasons.append("target Scene Expression changed")
            except (FileNotFoundError, ValueError) as exc:
                stale_reasons.append(str(exc))
        try:
            assembly = self.composition.inspect(proposal["source_assembly"]["artifact_id"])
            if assembly.content_hash != proposal["source_assembly"].get("content_hash"):
                stale_reasons.append("source Chapter assembly changed")
            if self.composition.status(assembly.artifact_id)["freshness"] == "stale":
                stale_reasons.append("source Chapter assembly is stale")
        except FileNotFoundError:
            stale_reasons.append("source Chapter assembly unavailable")
        manuscript = Path(proposal["external_manuscript"]["path"])
        if manuscript.exists() and _hash(manuscript.read_text(encoding="utf-8")) != proposal["external_manuscript"].get("content_hash"):
            stale_reasons.append("external manuscript changed")
        return {"proposal_id": proposal_id, "status": "stale" if stale_reasons else proposal.get("status", "proposed"), "stale_reasons": stale_reasons, "proposal": proposal}

    def show(self, identifier: str) -> dict[str, Any]:
        matches = list(self.project.glob(f"chapters/*/expression/reconciliation/**/*.yaml"))
        for path in matches:
            data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
            if data.get("inspection_id") == identifier or data.get("proposal_id") == identifier or data.get("run_id") == identifier:
                return data
        raise FileNotFoundError(f"reconciliation artifact not found: {identifier}")
