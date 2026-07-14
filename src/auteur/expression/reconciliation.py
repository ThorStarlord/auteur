from __future__ import annotations

import difflib
import hashlib
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml
from auteur.provenance import Lifecycle

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
            if kind == "transition_patch":
                transition = next((item for item in self.composition.inspect(report["source_assembly"]["artifact_id"]).transitions if item.get("transition_id") == finding.get("source_section")), None)
                if transition is None:
                    continue
                proposal["boundary"] = {"before_scene": transition["before_scene"], "after_scene": transition["after_scene"]}
                proposal["source_transition"] = {"transition_id": transition["transition_id"], "revision": transition["revision"], "content_hash": transition["content_hash"], "before_scene": transition["before_scene"], "after_scene": transition["after_scene"]}
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

    SUPPORTED_APPLICATION_TYPES = {
        "scene_expression_patch",
        "scene_expression_replacement_candidate",
        "transition_patch",
    }
    SUPPORTED_TRANSFORMATION = ("expression.reconcile_chapter", 1)

    def _proposal_path(self, proposal_id: str) -> Path | None:
        return next(self.project.glob(f"chapters/*/expression/reconciliation/proposals/{proposal_id}.yaml"), None)

    def _load_plan(self, plan_id: str) -> dict[str, Any]:
        path = next(self.project.glob(f"chapters/*/expression/reconciliation/plans/{plan_id}.yaml"), None)
        if path is None:
            raise FileNotFoundError(f"application plan not found: {plan_id}")
        return yaml.safe_load(path.read_text(encoding="utf-8")) or {}

    def plan(self, inspection_id: str, proposal_ids: list[str]) -> dict[str, Any]:
        """Persist a deterministic, noncanonical application-set plan."""
        inspection_path = next(self.project.glob(f"chapters/*/expression/reconciliation/inspections/{inspection_id}.yaml"), None)
        if inspection_path is None:
            raise FileNotFoundError(f"inspection not found: {inspection_id}")
        inspection = yaml.safe_load(inspection_path.read_text(encoding="utf-8")) or {}
        assembly_ref = inspection.get("source_assembly", {})
        manuscript_ref = inspection.get("external_manuscript", {})
        proposals: list[dict[str, Any]] = []
        validations: list[dict[str, Any]] = []
        conflicts: list[dict[str, Any]] = []
        seen: set[str] = set()
        for proposal_id in proposal_ids:
            if proposal_id in seen:
                conflicts.append({"conflict_code": "duplicate_proposal_selection", "proposal_ids": [proposal_id], "target_artifact": None, "target_section": None, "summary": "The same proposal was selected more than once.", "recommended_action": "Select each proposal once."})
                continue
            seen.add(proposal_id)
            path = self._proposal_path(proposal_id)
            if path is None:
                validations.append({"proposal_id": proposal_id, "classification": "invalid", "reasons": ["proposal does not exist"]})
                continue
            proposal = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
            proposals.append(proposal)
            reasons: list[str] = []
            classification = "fresh"
            kind = proposal.get("proposal_type")
            if kind not in self.SUPPORTED_APPLICATION_TYPES:
                classification, reasons = "unsupported", [f"proposal type is not supported: {kind}"]
            elif proposal.get("status") in {"rejected", "superseded", "stale"}:
                classification, reasons = "stale", [f"proposal status is no longer applicable: {proposal.get('status')}" ]
            elif proposal.get("status") not in {"proposed", "review_required"}:
                classification, reasons = "invalid", [f"proposal status is not applicable: {proposal.get('status')}" ]
            elif proposal.get("source_inspection") != inspection_id:
                classification, reasons = "invalid", ["proposal belongs to a different inspection"]
            elif proposal.get("transformation", {}).get("id") != self.SUPPORTED_TRANSFORMATION[0] or proposal.get("transformation", {}).get("version") != self.SUPPORTED_TRANSFORMATION[1]:
                classification, reasons = "unsupported", ["transformation contract is unsupported"]
            else:
                try:
                    assembly = self.composition.inspect(assembly_ref["artifact_id"])
                    if proposal.get("source_assembly") != assembly_ref:
                        classification, reasons = "stale", ["proposal source Chapter assembly differs from inspection"]
                    elif proposal.get("external_manuscript") != manuscript_ref:
                        classification, reasons = "stale", ["proposal imported manuscript differs from inspection"]
                    elif assembly.revision != assembly_ref.get("revision") or assembly.content_hash != assembly_ref.get("content_hash"):
                        classification, reasons = "stale", ["source Chapter assembly revision or hash changed"]
                    elif manuscript_ref.get("path") and (not Path(manuscript_ref["path"]).exists() or _hash(Path(manuscript_ref["path"]).read_text(encoding="utf-8")) != manuscript_ref.get("content_hash")):
                        classification, reasons = "stale", ["imported manuscript hash changed"]
                    elif kind == "transition_patch":
                        if not proposal.get("boundary", {}).get("before_scene") or not proposal.get("boundary", {}).get("after_scene"):
                            classification, reasons = "invalid", ["transition proposal is missing a boundary"]
                        else:
                            transition = next((item for item in assembly.transitions if item.get("transition_id") == proposal.get("target_artifact_id")), None)
                        if classification != "fresh" and classification != "stale" and classification != "invalid":
                            transition = None
                        if transition is None and classification == "fresh":
                            classification, reasons = "invalid", ["target transition does not exist"]
                        elif transition is not None and proposal.get("boundary") != {"before_scene": transition.get("before_scene"), "after_scene": transition.get("after_scene")}:
                            classification, reasons = "stale", ["transition proposal boundary changed"]
                        elif transition.get("revision") != proposal.get("target_revision") or transition.get("content_hash") != proposal.get("target_content_hash"):
                            classification, reasons = "stale", ["target transition revision or hash changed"]
                    else:
                        metadata, _ = self.composition._accepted_scene(proposal["target_artifact_id"])
                        if metadata.get("revision") != proposal.get("target_revision") or metadata.get("content_hash") != proposal.get("target_content_hash"):
                            classification, reasons = "stale", ["target Scene Expression revision or hash changed"]
                except (KeyError, FileNotFoundError, ValueError) as exc:
                    classification, reasons = "invalid", [str(exc)]
            validations.append({"proposal_id": proposal_id, "classification": classification, "reasons": reasons, "proposal_type": kind})

        for left_index, left in enumerate(proposals):
            for right in proposals[left_index + 1:]:
                if left.get("source_assembly") != right.get("source_assembly"):
                    conflicts.append({"conflict_code": "different_source_assemblies", "proposal_ids": [left["proposal_id"], right["proposal_id"]], "target_artifact": None, "target_section": None, "summary": "Selected proposals were generated from different Chapter assemblies.", "recommended_action": "Select proposals from one inspection assembly."})
                if left.get("external_manuscript", {}).get("content_hash") != right.get("external_manuscript", {}).get("content_hash"):
                    conflicts.append({"conflict_code": "different_imported_manuscripts", "proposal_ids": [left["proposal_id"], right["proposal_id"]], "target_artifact": None, "target_section": None, "summary": "Selected proposals were generated from different imported manuscripts.", "recommended_action": "Select proposals from one imported manuscript."})
                same_target = left.get("target_artifact_id") == right.get("target_artifact_id")
                if same_target and left.get("proposal_type") != "transition_patch" and right.get("proposal_type") != "transition_patch":
                    code = "scene_patch_replacement_conflict" if left.get("proposal_type") != right.get("proposal_type") else "overlapping_scene_patches"
                    conflicts.append({"conflict_code": code, "proposal_ids": [left["proposal_id"], right["proposal_id"]], "target_artifact": left.get("target_artifact_id"), "target_section": left.get("target_artifact_id"), "summary": "Selected Scene proposals target the same Scene.", "recommended_action": "Select one compatible Scene proposal."})
                if same_target and left.get("proposal_type") == right.get("proposal_type") == "transition_patch":
                    conflicts.append({"conflict_code": "transition_revision_conflict", "proposal_ids": [left["proposal_id"], right["proposal_id"]], "target_artifact": left.get("target_artifact_id"), "target_section": left.get("target_artifact_id"), "summary": "Selected transition patches target the same transition revision.", "recommended_action": "Select one transition patch."})

        fresh = {item["proposal_id"] for item in validations if item["classification"] == "fresh"}
        planned_outputs = []
        for proposal in proposals:
            if proposal["proposal_id"] not in fresh: continue
            if proposal["proposal_type"] == "transition_patch":
                planned_outputs.append({"output_type": "chapter_transition_candidate", "target_transition": proposal["target_artifact_id"], "boundary": proposal.get("boundary"), "source_transition_revision": proposal["target_revision"], "planned_candidate_id": f"planned:{proposal['proposal_id']}", "planned_revision": int(proposal["target_revision"]) + 1})
            else:
                item = {"output_type": "scene_expression_candidate", "target_scene": proposal["target_artifact_id"], "source_expression_revision": proposal["target_revision"], "planned_candidate_id": f"planned:{proposal['proposal_id']}"}
                if proposal["proposal_type"] == "scene_expression_replacement_candidate": item["mode"] = "replacement"
                item["planned_revision"] = int(proposal["target_revision"]) + 1
                planned_outputs.append(item)
        if conflicts: readiness = "conflicted"
        elif any(item["classification"] == "unsupported" for item in validations): readiness = "unsupported"
        elif any(item["classification"] == "invalid" for item in validations): readiness = "not_ready"
        elif any(item["classification"] == "stale" for item in validations): readiness = "stale"
        else: readiness = "ready"
        preview_sources = []
        expected_scene_order, expected_transition_order = [], []
        try:
            assembly = self.composition.inspect(assembly_ref["artifact_id"])
            planned_by_target = {item.get("target_scene", item.get("target_transition")): item for item in planned_outputs}
            for item in assembly.source_scenes:
                expected_scene_order.append(item["scene_id"])
                preview_sources.append({"section_id": item["scene_id"], "source_kind": "planned_candidate" if item["scene_id"] in planned_by_target else "accepted_scene_expression", "source_revision": planned_by_target.get(item["scene_id"], {}).get("planned_revision", item["expression_revision"]), "planned_candidate": planned_by_target.get(item["scene_id"], {}).get("planned_candidate_id")})
            for item in assembly.transitions:
                expected_transition_order.append(item["transition_id"])
                preview_sources.append({"section_id": item["transition_id"], "source_kind": "planned_candidate" if item["transition_id"] in planned_by_target else "accepted_transition", "source_revision": planned_by_target.get(item["transition_id"], {}).get("planned_revision", item["revision"]), "planned_candidate": planned_by_target.get(item["transition_id"], {}).get("planned_candidate_id")})
        except (KeyError, FileNotFoundError, ValueError):
            pass
        if not proposal_ids: readiness = "not_ready"
        plan_id = "application_set_" + hashlib.sha256((inspection_id + "\0" + "\0".join(proposal_ids)).encode()).hexdigest()[:16]
        plan = {"application_set_id": plan_id, "source_inspection": inspection_id, "source_assembly": assembly_ref, "proposal_ids": proposal_ids, "status": "planned", "readiness": readiness, "targets": [p.get("target_artifact_id") for p in proposals], "conflicts": conflicts, "freshness_results": validations, "planned_outputs": planned_outputs, "recomposition_preview": {"preview_sources": preview_sources, "expected_scene_order": expected_scene_order, "expected_transition_order": expected_transition_order, "blocking_gaps": [] if expected_scene_order else ["source Chapter assembly unavailable"], "label": "application_preview", "canonical": False}, "created_at": datetime.now(timezone.utc).isoformat()}
        root = inspection_path.parent.parent
        self._write_atomic(root / "plans" / f"{plan_id}.yaml", plan)
        return plan

    def show_plan(self, plan_id: str) -> dict[str, Any]:
        return self._load_plan(plan_id)

    def publish(self, plan_id: str) -> dict[str, Any]:
        """Publish a ready plan transactionally into unaccepted candidates."""
        plan = self._load_plan(plan_id)
        if plan.get("readiness") != "ready":
            raise ValueError("application plan is not ready for publication")
        root = next(self.project.glob(f"chapters/*/expression/reconciliation/plans/{plan_id}.yaml")).parent.parent
        publication_id = "publication_" + plan_id.removeprefix("application_set_")
        publication_path = root / "publications" / f"{publication_id}.yaml"
        if publication_path.exists():
            raise ValueError(f"application plan has already been published: {plan_id}")
        proposals = []
        for proposal_id in plan.get("proposal_ids", []):
            path = self._proposal_path(proposal_id)
            if path is None:
                raise ValueError(f"proposal not found: {proposal_id}")
            proposals.append(yaml.safe_load(path.read_text(encoding="utf-8")) or {})
        created: list[Path] = []
        scene_overrides: dict[str, Path] = {}
        assembly = self.composition.inspect(plan["source_assembly"]["artifact_id"])
        chapter_id = assembly.source_chapter["artifact_id"]
        transitions = self.composition.load_transitions(chapter_id)
        try:
            from auteur.expression.pilot import ExpressionStore
            expression_store = ExpressionStore(self.project)
            for proposal in proposals:
                if proposal["proposal_type"] in {"scene_expression_patch", "scene_expression_replacement_candidate"}:
                    scene_path = self.composition._scene_path(proposal["target_artifact_id"])
                    candidate = expression_store.generate(scene_path, proposal["replacement_text"], executor={"kind": "reconciliation-publication"})
                    metadata_path = expression_store._metadata_path(candidate.candidate_id)
                    metadata = yaml.safe_load(metadata_path.read_text(encoding="utf-8")) or {}
                    metadata.update({"lifecycle": Lifecycle.PROPOSED.value, "authority": "draft", "transformation": {"id": "expression.publish_application", "version": 1}, "realization_evidence": {"application_plan": plan_id, "source_reconciliation": proposal.get("source_inspection")}})
                    metadata_path.write_text(yaml.safe_dump(metadata, sort_keys=False), encoding="utf-8")
                    prose_path = metadata_path.with_suffix(".md")
                    created.extend([prose_path, metadata_path])
                    scene_overrides[proposal["target_artifact_id"]] = prose_path
                    scene_overrides[f"__metadata__:{proposal['target_artifact_id']}"] = metadata_path
                elif proposal["proposal_type"] == "transition_patch":
                    boundary = proposal.get("boundary") or {}
                    boundary_key = f"{boundary.get('before_scene')}->{boundary.get('after_scene')}"
                    target_key = next((key for key, value in transitions.items() if value.get("transition_id") == proposal["target_artifact_id"]), None)
                    if not boundary.get("before_scene") or not boundary.get("after_scene") or target_key is None:
                        raise ValueError("transition candidate has missing or invalid boundary")
                    target = transitions.get(target_key, {})
                    if target.get("before_scene") != boundary["before_scene"] or target.get("after_scene") != boundary["after_scene"]:
                        raise ValueError("transition candidate boundary does not match source transition")
                    target = dict(target)
                    revision = int(proposal["target_revision"]) + 1
                    candidate_id = f"transition_candidate_{proposal['target_artifact_id']}_v{revision:03d}"
                    target.update({"candidate_id": candidate_id, "artifact_type": "chapter_transition_candidate", "transition_id": proposal["target_artifact_id"], "revision": revision, "lifecycle": Lifecycle.PROPOSED.value, "authority": "candidate", "boundary": boundary, "source_transition": proposal.get("source_transition"), "text": proposal["replacement_text"], "content_hash": _hash(proposal["replacement_text"]), "transformation": {"id": "expression.publish_application", "version": 1}, "source_application_plan": plan_id, "source_reconciliation": proposal.get("source_inspection"), "source_proposal": proposal["proposal_id"]})
                    transition_dir = self.composition.chapter_dir(chapter_id) / "transition_candidates"
                    md_path, yaml_path = transition_dir / f"{proposal['target_artifact_id']}_v{revision:03d}.md", transition_dir / f"{proposal['target_artifact_id']}_v{revision:03d}.yaml"
                    transition_dir.mkdir(parents=True, exist_ok=True)
                    md_path.write_text(proposal["replacement_text"], encoding="utf-8")
                    yaml_path.write_text(yaml.safe_dump(target, sort_keys=False), encoding="utf-8")
                    created.extend([md_path, yaml_path])
                    transitions[boundary_key] = target
                    if target_key != boundary_key:
                        transitions.pop(target_key, None)
            chapter = self.composition.compose(chapter_id, transitions=transitions, scene_overrides=scene_overrides, persist_transitions=False, lifecycle=Lifecycle.PROPOSED, authority="draft", transformation={"id": "expression.publish_application", "version": 1, "application_plan": plan_id, "source_reconciliation": plan["source_inspection"]})
            chapter_meta = self.composition._metadata_path(chapter.artifact_id)
            chapter_md = chapter_meta.with_suffix(".md")
            created.extend([chapter_meta, chapter_md])
            publication = {"publication_id": publication_id, "application_plan": plan_id, "source_reconciliation": plan["source_inspection"], "published_candidates": [str(path.relative_to(self.project)) for path in created], "chapter_expression": chapter.artifact_id, "transformation": {"id": "expression.publish_application", "version": 1}, "status": "published", "created_at": datetime.now(timezone.utc).isoformat()}
            self._write_atomic(publication_path, publication)
            created.append(publication_path)
            return publication
        except Exception:
            for path in reversed(created):
                if path.exists(): path.unlink()
            for parent in {path.parent for path in created}:
                if parent.exists() and not any(parent.iterdir()): parent.rmdir()
            raise

    def inspect_publication(self, publication_id: str) -> dict[str, Any]:
        path = next(self.project.glob(f"chapters/*/expression/reconciliation/publications/{publication_id}.yaml"), None)
        if path is None:
            raise FileNotFoundError(f"publication not found: {publication_id}")
        return yaml.safe_load(path.read_text(encoding="utf-8")) or {}
