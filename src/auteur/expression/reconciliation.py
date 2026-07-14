from __future__ import annotations

import difflib
import hashlib
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from auteur.expression.composition import (
    ChapterExpressionStore,
    END_MARKER_RE,
    END_TRANSITION_MARKER_RE,
    MARKER_RE,
    TRANSITION_MARKER_RE,
)


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

    @staticmethod
    def _transition_blocks(text: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        blocks, malformed = [], []
        current = None
        for line_no, line in enumerate(text.splitlines(), 1):
            start, end = TRANSITION_MARKER_RE.match(line), END_TRANSITION_MARKER_RE.match(line)
            if start:
                if current is not None:
                    malformed.append({"line": line_no, "evidence": line})
                current = {"transition_id": start.group(1), "revision": int(start.group(2)), "start_line": line_no, "lines": []}
            elif end:
                if current is None or current["transition_id"] != end.group(1):
                    malformed.append({"line": line_no, "evidence": line})
                elif current is not None:
                    current["end_line"] = line_no
                    current["text"] = "\n".join(current["lines"]).strip()
                    blocks.append(current)
                    current = None
            elif current is not None:
                current["lines"].append(line)
        if current is not None:
            malformed.append({"line": current["start_line"], "evidence": "missing transition closing marker"})
        return blocks, malformed

    def inspect(self, manuscript: Path, against: str) -> dict[str, Any]:
        assembly = self.composition.inspect(against)
        text = Path(manuscript).read_text(encoding="utf-8")
        imported_hash = _hash(text)
        blocks, malformed = self._blocks(text)
        transition_blocks, malformed_transitions = self._transition_blocks(text)
        marker_report = self.composition.inspect_markers(text)
        inspection_id = f"inspection_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')}"
        findings: list[dict[str, Any]] = []
        expected = {item["scene_id"]: item for item in assembly.source_scenes}
        actual_ids = [block["scene_id"] for block in blocks]
        expected_order = [item["scene_id"] for item in assembly.source_scenes]
        markerless = not blocks
        if markerless:
            findings.append(self._finding(inspection_id, "markerless", "unresolved", None, imported_hash, "Scene and transition ownership cannot be established", ["restore markers", "manually map sections", "retain Chapter-local divergence", "discard the import"], detail={"primary_finding": True, "consequences": [{"code": "scene_mapping_unavailable", "scene_ids": expected_order}, {"code": "transition_mapping_unavailable", "transition_ids": [item["transition_id"] for item in assembly.transitions]}]}))
        for item in malformed + marker_report.get("findings", []):
            if item.get("code") != "unresolved_divergence":
                findings.append(self._finding(inspection_id, "malformed", "unresolved", None, imported_hash, item.get("message", "Malformed marker"), [item.get("recommended_action", "repair the marker")]))
        for item in malformed_transitions:
            findings.append(self._finding(inspection_id, "transition_malformed", "unresolved", None, imported_hash, item.get("evidence", "Malformed transition marker"), ["repair the transition marker"], owner="Chapter transition"))
        for scene_id, item in ({} if markerless else expected).items():
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
                matcher = difflib.SequenceMatcher(None, source_text.splitlines(), block["text"].splitlines())
                changed_lines = sum(1 for tag, *_ in matcher.get_opcodes() if tag != "equal")
                fact_terms = r"\b(decided|revealed|killed|stole|met|learned|discovered|outcome|knowledge|event)\b"
                structured_facts = sorted(set(re.findall(fact_terms, block["text"], re.IGNORECASE)) - set(re.findall(fact_terms, source_text, re.IGNORECASE)))
                metrics = {"changed_character_ratio": round(1 - ratio, 4), "changed_line_ratio": round(changed_lines / max(len(source_text.splitlines()), 1), 4), "paragraph_count_before": len([p for p in source_text.split("\n\n") if p.strip()]), "paragraph_count_after": len([p for p in block["text"].split("\n\n") if p.strip()]), "marker_boundaries_stable": True, "patch_fragment_count": sum(1 for tag, *_ in matcher.get_opcodes() if tag != "equal"), "structured_fact_findings": [{"code": "possible_canonical_fact_change", "term": term} for term in structured_facts], "classification_reason": "possible canonical fact change; structural review required" if structured_facts else ("localized edit with stable Scene ownership" if ratio >= 0.55 else "extensive rewrite or fragmented patch")}
                findings.append(self._finding(inspection_id, classification, "review_required", scene_id, item["expression_content_hash"], f"Scene section changed ({len(block['text'].split())} observed words)", [action], observed_hash=_hash(block["text"]), owner=owner, source_revision=item["expression_revision"], detail={"original": source_text, "replacement": block["text"], "change_metrics": metrics}))
        block_by_id = {block["scene_id"]: block for block in blocks}
        marked_transitions: dict[str, list[dict[str, Any]]] = {}
        for block in transition_blocks:
            marked_transitions.setdefault(block["transition_id"], []).append(block)
        for transition in ([] if markerless else assembly.transitions):
            before, after = transition["before_scene"], transition["after_scene"]
            if before not in block_by_id or after not in block_by_id:
                continue
            start = block_by_id[before]["end_line"]
            end = block_by_id[after]["start_line"] - 1
            gap = "\n".join(text.splitlines()[start:end]).strip()
            expected_transition = str(transition.get("text", "")).strip()
            marked = marked_transitions.get(transition["transition_id"], [])
            if len(marked) > 1:
                findings.append(self._finding(inspection_id, "transition_duplicated", "error", transition["transition_id"], transition["content_hash"], "Transition section appears more than once", ["remove the duplicate or map it manually"], owner="Chapter transition", source_revision=transition["revision"]))
                continue
            observed = marked[0]["text"] if marked else gap
            if marked and marked[0]["revision"] != transition["revision"]:
                findings.append(self._finding(inspection_id, "transition_malformed", "unresolved", transition["transition_id"], transition["content_hash"], "Transition marker revision does not match the assembly manifest", ["restore the manifest revision in the marker"], owner="Chapter transition", source_revision=transition["revision"], detail={"observed_revision": marked[0]["revision"], "expected_revision": transition["revision"]}))
                continue
            nonblank_lines = [line for line in observed.splitlines() if line.strip()]
            if not observed:
                classification = "transition_missing"
            elif observed == expected_transition:
                classification = "unchanged_transition"
            elif not marked and len(nonblank_lines) > 1:
                classification = "unresolved_transition_gap"
            else:
                classification = "transition_modified"
            if classification != "unchanged_transition":
                actions = ["create a transition patch proposal", "review possible new event ownership"] if classification == "transition_modified" else ["restore the transition", "map the gap manually"]
                findings.append(self._finding(inspection_id, classification, "review_required", transition["transition_id"], transition["content_hash"], "Chapter-owned transition changed" if classification == "transition_modified" else "Chapter transition ownership is unresolved", actions, observed_hash=_hash(observed), owner="Chapter transition", source_revision=transition["revision"], detail={"original": expected_transition, "replacement": observed}))
        if set(actual_ids) == set(expected_order) and actual_ids != expected_order:
            findings.append(self._finding(inspection_id, "moved", "review_required", None, imported_hash, f"Scene order changed from {' → '.join(expected_order)} to {' → '.join(actual_ids)}", ["create a Structure proposal", "retain Chapter-local order divergence"], detail={"previous_order": expected_order, "current_order": actual_ids}))
        outside = "" if markerless else self._outside_text(text, blocks, transition_blocks, assembly.transitions)
        if outside.strip():
            findings.append(self._finding(inspection_id, "unsourced", "review_required", None, imported_hash, "Text exists outside known Scene ownership", ["assign it as a transition", "retain Chapter-local divergence", "map it manually"], detail={"text": outside}))
        if len([item for item in findings if item["classification"] == "modified"]) > 1:
            findings.append(self._finding(inspection_id, "cross_boundary", "review_required", None, imported_hash, "Multiple owned sections changed; automatic ownership is unsafe", ["retain Chapter-local divergence", "map text manually", "create replacement candidates"]))
        if not markerless and not findings:
            report_status = "no_changes"
        else:
            report_status = "unresolved" if any(item["severity"] in {"error", "unresolved"} for item in findings) else "inspected"
        primary = {"classification": "markerless", "severity": "unresolved", "summary": "Scene and transition ownership cannot be established."} if markerless else None
        consequences = [{"code": "scene_mapping_unavailable", "scene_ids": expected_order}, {"code": "transition_mapping_unavailable", "transition_ids": [item["transition_id"] for item in assembly.transitions]}] if markerless else []
        report = {"inspection_id": inspection_id, "source_assembly": {"artifact_id": assembly.artifact_id, "revision": assembly.revision, "content_hash": assembly.content_hash}, "external_manuscript": {"path": str(Path(manuscript)), "content_hash": imported_hash, "marker_state": marker_report["status"]}, "recognized_transitions": [{"transition_id": item["transition_id"], "owner": "Chapter transition", "classification": "unchanged_transition" if not markerless else "unmapped"} for item in assembly.transitions], "findings": findings, "status": report_status, "created_at": datetime.now(timezone.utc).isoformat()}
        if primary is not None:
            report["primary_finding"] = primary
            report["consequences"] = consequences
        root = self._root(against)
        self._write_atomic(root / "inspections" / f"{inspection_id}.yaml", report)
        run = {"run_id": f"reconcile_{inspection_id.removeprefix('inspection_')}", "transformation": {"id": "expression.reconcile_chapter", "version": 1}, "source_assembly": report["source_assembly"], "external_manuscript": report["external_manuscript"], "inspection_report_id": inspection_id, "proposal_ids": [], "mapping_ids": [], "divergence_ids": [], "status": report["status"], "created_at": report["created_at"]}
        self._write_atomic(root / "runs" / f"{run['run_id']}.yaml", run)
        return report

    @staticmethod
    def _outside_text(text: str, blocks: list[dict[str, Any]], transition_blocks: list[dict[str, Any]], transitions: list[dict[str, Any]]) -> str:
        lines = text.splitlines()
        owned = set()
        for block in blocks:
            owned.update(range(block["start_line"] - 1, block["end_line"]))
        for block in transition_blocks:
            owned.update(range(block["start_line"] - 1, block["end_line"]))
        for transition in transitions:
            before = next((item for item in blocks if item["scene_id"] == transition["before_scene"]), None)
            after = next((item for item in blocks if item["scene_id"] == transition["after_scene"]), None)
            if before and after:
                expected = str(transition.get("text", "")).strip()
                start, end = before["end_line"], after["start_line"] - 1
                gap = "\n".join(lines[start:end]).strip()
                # Adjacent gaps belong to the declared Chapter transition even
                # when their content changed; classification owns the delta.
                owned.update(range(start, end))
        markers = (MARKER_RE, END_MARKER_RE, TRANSITION_MARKER_RE, END_TRANSITION_MARKER_RE)
        return "\n".join(line for index, line in enumerate(lines) if index not in owned and not any(pattern.match(line) for pattern in markers))

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
        existing_ids = report.get("proposal_ids", [])
        if existing_ids:
            existing = []
            for proposal_id in existing_ids:
                proposal_path = root / "proposals" / f"{proposal_id}.yaml"
                if proposal_path.exists():
                    existing.append(yaml.safe_load(proposal_path.read_text(encoding="utf-8")) or {})
            return {"inspection_id": inspection_id, "proposal_ids": existing_ids, "proposals": existing, "status": report.get("status", "proposals_created")}
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
