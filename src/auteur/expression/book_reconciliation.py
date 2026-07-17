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


DECISION_TRANSFORMATION = {"id": "expression.decide_book_candidate", "version": 1}
# Candidate decisions are *workflow* decisions, not narrative acceptance.
# ``approve`` means "use this candidate in the next recomposition"; the later,
# separate acceptance of a recomposed Book ("accept") is out of scope in this
# slice. ``defer`` is NONTERMINAL: a deferred candidate can later be approved or
# rejected. Decisions form an append-only history and the latest one supersedes
# all priors (see ``decide_candidate`` / ``_latest_decision_for_candidate``).
DECISION_STATUSES = ("approved", "rejected", "deferred")

ACCEPTED_SOURCE_TRANSFORMATION = {"id": "expression.accept_book_owned_source", "version": 1}
# Approving a Book-owned candidate materializes a durable *accepted Book-owned
# source*: the candidate itself stays a candidate, but its approval produces an
# ``authority=accepted`` artifact that a future recomposition reads. Each
# candidate type maps to one owned "kind".
ACCEPTED_SOURCE_KIND = {
    "book_separator_candidate": "separator",
    "book_order_candidate": "order",
    "book_title_rendering_candidate": "title",
    "book_inserted_material_candidate": "material",
}

RECOMPOSITION_TRANSFORMATION = {"id": "expression.recompose_book_from_accepted_sources", "version": 1}
# Phase C1: pointer-based Book recomposition derives a noncanonical recomposed
# Book by assembling the current accepted Chapter Expression pointers with the
# current accepted Book-owned source pointers. It is READ-ONLY over accepted
# sources: it never moves the accepted Book pointer, never accepts a candidate,
# never completes reconciliation, and never reads unpublished candidates.

POINTER_TRANSFORMATION = {"id": "expression.point_accepted_book_source", "version": 1}
# The *current accepted-source pointer* is the ONLY mutable tier of the accepted
# authority model. Approving a candidate moves the pointer to the newly created
# immutable revision; deferring or rejecting records author intent but never
# touches the pointer. Recomposition resolves the pointer (not decisions) to find
# the current accepted revision for each Book-owned element.

COMPARISON_TRANSFORMATION = {"id": "expression.compare_book_recomposition", "version": 1}
# Phase C2: a READ-ONLY, deterministic comparison between a pointer-based Book
# recomposition (Phase C1) and an external manuscript. It NEVER accepts the Book,
# never moves the accepted Book pointer, never mutates any source, never completes
# reconciliation, and never generates automatic proposals. Its only output is a
# derived, evaluated, noncanonical comparison report classifying every divergence
# by ownership (Book-owned / Chapter-owned / structural / marker / unresolved).
SUPPORTED_MARKER_CONTRACT_VERSIONS = {1}
# The six residual categories a comparison classifies every finding into. Only
# ``exact_match`` and ``book_owned_residual`` are compatible with Book acceptance
# readiness; the other four are blocking residuals.
COMPARISON_CATEGORIES = (
    "exact_match",
    "book_owned_residual",
    "chapter_owned_residual",
    "structural_residual",
    "marker_residual",
    "unresolved_residual",
)


class MarkerContract:
    """The Phase A Book marker contract, used to validate and route markers.

    A comparison routes each external span to a Book or Chapter target using this
    contract. ``is_valid`` enforces the marker grammar (a recognized ``kind`` and a
    well-formed id); ``route`` maps a parsed element to ``("chapter", id)`` or
    ``("book", owned_kind)``. The contract is versioned so an unsupported manuscript
    contract blocks the comparison rather than being silently misinterpreted.
    """

    CHAPTER_ID = re.compile(r"^chapter_\w+$")
    SEPARATOR_ID = re.compile(r"^separator_\w+$")

    def __init__(self, version: int) -> None:
        self.version = version

    @property
    def is_supported(self) -> bool:
        return self.version in SUPPORTED_MARKER_CONTRACT_VERSIONS

    def is_valid(self, marker: dict[str, Any] | None) -> bool:
        if not isinstance(marker, dict):
            return False
        kind = marker.get("kind")
        ident = marker.get("id")
        if kind == "chapter":
            return bool(ident) and bool(self.CHAPTER_ID.match(str(ident)))
        if kind == "separator":
            return bool(ident) and bool(self.SEPARATOR_ID.match(str(ident)))
        return False

    def route(self, marker: dict[str, Any], known_chapters: set[str]) -> tuple[str, str, str]:
        """Route a valid marker to its ownership target.

        Returns ``(ownership, target, confidence)`` where ownership is
        ``chapter`` | ``book`` | ``unresolved``.
        """
        kind = marker.get("kind")
        ident = str(marker.get("id"))
        if kind == "chapter":
            if ident in known_chapters:
                return "chapter", ident, "certain"
            # A well-formed Chapter marker the accepted Book does not know is a
            # structural problem (an extra/unknown Chapter), not a Chapter edit.
            return "structural", ident, "probable"
        if kind == "separator":
            return "book", "separator", "certain"
        return "unresolved", "unknown_marker", "ambiguous"


class ComparisonBlockedError(Exception):
    """Raised/returned when a read-only Book comparison is blocked (never partial).

    Comparison is gated by a 12-point freshness validation. When any check fails,
    this error is returned (comparison writes NO artifact, partial or otherwise)
    carrying a structured block. ``result`` is the full structured dict; flattened
    attributes are provided for ergonomic access:

    - ``status``  -- ``ready`` never blocks; otherwise one of
                     ``blocked_stale_recomposition``, ``blocked_stale_manuscript``,
                     ``blocked_missing_recomposition``,
                     ``blocked_missing_external_manuscript``,
                     ``blocked_missing_publication``, ``blocked_pointer_moved``,
                     or a propagated Phase C1 recomposition block status.
    - ``reason``  -- the primary (first) failure code.
    - ``details`` -- structured ``{reasons: [...], recomposition_id, ...}``.
    - ``recommended_action`` -- the primary recommended remediation.
    """

    def __init__(
        self,
        status: str,
        recomposition_id: str,
        message: str,
        reasons: list[dict[str, Any]],
    ) -> None:
        primary = reasons[0] if reasons else {}
        self.status = status
        self.reason = primary.get("code", status)
        self.recommended_action = primary.get(
            "recommended_action", "recompose from fresh accepted sources, then compare again"
        )
        self.details = {"reasons": reasons, "recomposition_id": recomposition_id}
        self.result = {
            "status": status,
            "recomposition_id": recomposition_id,
            "message": message,
            "reasons": reasons,
            "visible_outputs_created": False,
        }
        super().__init__(message)


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


class BookFreshnessRejectError(ValueError):
    """Raised/returned when a candidate decision is blocked by stale sources.

    ``result`` carries a structured rejection: ``status='rejected_stale'``, the
    freshness ``reasons`` (each ``{code, expected, current, recommended_action}``),
    and ``visible_outputs_created=False`` -- a stale decision creates nothing.
    """

    def __init__(self, result: dict[str, Any]):
        self.result = result
        super().__init__(result.get("message", "book candidate decision rejected"))


class CandidateNotFoundError(ValueError):
    """Raised when a decision targets a published candidate that does not exist."""


class RecompositionBlockedError(ValueError):
    """Raised/returned when pointer-based Book recomposition is blocked.

    Recomposition is gated by comprehensive freshness validation. When any check
    fails, this error is returned (never raised into a partial artifact) carrying
    a structured block. ``result`` is the full structured dict; the flattened
    attributes are provided for ergonomic access:

    - ``status``   -- one of ``blocked_stale_chapter``, ``blocked_stale_book``,
                      ``blocked_missing_target`` (``ready`` never blocks).
    - ``reason``   -- the primary (first) failure code.
    - ``details``  -- structured ``{reasons: [...], publication_id, ...}``.
    - ``recommended_action`` -- the primary recommended remediation.

    Approving a candidate snapshots the Book revision/hash it was decided
    against; if any Chapter or the accepted Book advances afterward, the accepted
    sources no longer describe the current Book and recomposition must not run
    (no partial or stale recomposition is ever produced) until the author
    re-decides.
    """

    def __init__(self, result: dict[str, Any]):
        self.result = result
        reasons = result.get("reasons", []) or []
        primary = reasons[0] if reasons else {}
        self.status: str = result.get("status", "blocked")
        self.reason: str = primary.get("code", result.get("status", "blocked"))
        self.details: dict[str, Any] = {
            "reasons": reasons,
            "publication_id": result.get("publication_id"),
        }
        self.recommended_action: str = primary.get(
            "recommended_action", result.get("message", "recompose from fresh accepted sources")
        )
        super().__init__(result.get("message", "recomposition blocked"))


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

    # ------------------------------------------------------------------
    # Candidate Decisions (Decision Lifecycle) -- Model A (append-only).
    #
    # An author independently approves, rejects, or defers each published,
    # unaccepted Book candidate. Decisions are an APPEND-ONLY history: a
    # candidate may be decided more than once (for example deferred, then later
    # approved). Each decision is an immutable record carrying a
    # ``decision_sequence`` and a ``supersedes`` pointer; the LATEST decision
    # (highest sequence) is the active one and supersedes all priors. Prior
    # records are never deleted -- they are the audit trail.
    #
    # ``approve`` is a workflow decision meaning "use this candidate in the next
    # recomposition"; it materializes a durable accepted Book-owned source that a
    # future recomposition reads. It is NOT narrative acceptance of a recomposed
    # Book. Deciding a candidate never recomposes the Book, never accepts a
    # candidate as canonical, and never moves the accepted Book pointer. The only
    # visible side effects are the new decision record, an accepted Book-owned
    # source (on approval), and a regenerated, still-derived preview.
    # ------------------------------------------------------------------

    def _decisions_dir(self) -> Path:
        return self.root / "decisions"

    def _decision_path(self, decision_id: str) -> Path:
        return self._decisions_dir() / f"{decision_id}.yaml"

    @staticmethod
    def _decision_id(candidate_id: str, decision_status: str, reason: str, sequence: int = 1) -> str:
        digest = hashlib.sha256(
            (candidate_id + "\0" + decision_status + "\0" + (reason or "") + "\0" + str(sequence)).encode("utf-8")
        ).hexdigest()
        return f"book_candidate_decision_{digest[:32]}"

    def _load_decision(self, decision_id: str) -> dict[str, Any] | None:
        path = self._decision_path(decision_id)
        if not path.exists():
            return None
        return yaml.safe_load(path.read_text(encoding="utf-8")) or {}

    def _decision_history_for_candidate(self, candidate_id: str) -> list[dict[str, Any]]:
        """Every decision recorded for a candidate, ordered by decision_sequence."""
        directory = self._decisions_dir()
        history: list[dict[str, Any]] = []
        if not directory.exists():
            return history
        for path in sorted(directory.glob("*.yaml")):
            data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
            if data.get("candidate_id") == candidate_id:
                history.append(data)
        history.sort(key=lambda d: d.get("decision_sequence", 0))
        return history

    def _latest_decision_for_candidate(self, candidate_id: str) -> dict[str, Any] | None:
        """The active (latest, highest-sequence) decision, or None if undecided."""
        history = self._decision_history_for_candidate(candidate_id)
        return history[-1] if history else None

    def _decisions_for_publication(self, publication_id: str) -> dict[str, dict[str, Any]]:
        """Latest active decision per candidate for a publication.

        History is append-only, so a candidate can have several records; only the
        highest-sequence decision counts. Entries are keyed by candidate id.
        """
        directory = self._decisions_dir()
        latest: dict[str, dict[str, Any]] = {}
        if not directory.exists():
            return latest
        for path in sorted(directory.glob("*.yaml")):
            data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
            if data.get("publication_id") != publication_id:
                continue
            candidate_id = data.get("candidate_id")
            existing = latest.get(candidate_id)
            if existing is None or data.get("decision_sequence", 0) > existing.get("decision_sequence", 0):
                latest[candidate_id] = data
        return latest

    def show_book_candidate_decision(self, decision_id: str) -> dict[str, Any]:
        decision = self._load_decision(decision_id)
        if decision is None:
            raise FileNotFoundError(f"Book candidate decision not found: {decision_id}")
        return decision

    def book_candidate_decision_history(self, candidate_id: str) -> dict[str, Any]:
        """Full append-only decision history for a candidate plus its active state.

        ``decisions`` is the ordered history (oldest first); ``active_status`` and
        ``active_decision_id`` describe the superseding latest decision, if any.
        """
        history = self._decision_history_for_candidate(candidate_id)
        active = history[-1] if history else None
        return {
            "candidate_id": candidate_id,
            "decisions": history,
            "active_status": active["decision"]["status"] if active else "undecided",
            "active_decision_id": active["decision_id"] if active else None,
        }

    def _validate_candidate_freshness(self, candidate: dict[str, Any]) -> tuple[bool, list[dict[str, Any]]]:
        """Live revalidation of every dependency a decision would rest on.

        Persisted candidate freshness is never trusted; every source is
        re-read from disk. Returns ``(is_fresh, reasons)`` where each reason is a
        structured ``{code, expected, current, recommended_action}``.
        """
        reasons: list[dict[str, Any]] = []

        def add(code: str, *, expected: Any = None, current: Any = None,
                recommended_action: str = "publish a fresh Book candidate and decide again") -> None:
            reasons.append({"code": code, "expected": expected, "current": current, "recommended_action": recommended_action})

        # Candidate must still be a proposed, unaccepted candidate.
        if candidate.get("authority") != "candidate":
            add("CANDIDATE_AUTHORITY_CHANGED", expected="candidate", current=candidate.get("authority"))
        if candidate.get("lifecycle") != "proposed":
            add("CANDIDATE_NOT_PROPOSED", expected="proposed", current=candidate.get("lifecycle"))

        # Source plan must still exist and carry the same transformation.
        plan_id = candidate.get("source_plan_id")
        plan: dict[str, Any] = {}
        if not plan_id or not self._plan_path(plan_id).exists():
            add("PLAN_MISSING", expected=plan_id, current=None)
        else:
            plan = self._load_plan(plan_id)
            transformation = plan.get("transformation", {})
            if (transformation.get("id"), transformation.get("version")) != (PUBLICATION_TRANSFORMATION["id"], PUBLICATION_TRANSFORMATION["version"]):
                add("PLAN_CHANGED", expected=PUBLICATION_TRANSFORMATION, current=transformation)

        # Source publication must still exist.
        publication_id = candidate.get("publication_id")
        publication_path = self.root / "publications" / f"{publication_id}.yaml"
        if not publication_id or not publication_path.exists():
            add("PUBLICATION_MISSING", expected=publication_id, current=None)

        # Source inspection must still be locatable and unchanged.
        inspection_id = candidate.get("source_inspection_id")
        report: dict[str, Any] = {}
        try:
            report = self._load_inspection(inspection_id)
        except FileNotFoundError:
            add("INSPECTION_MISSING", expected=inspection_id, current=None)
        if report:
            transformation = report.get("provenance", {}).get("transformation", {})
            if (transformation.get("id"), transformation.get("version")) != INSPECTION_TRANSFORMATION:
                add("INSPECTION_CHANGED", expected=INSPECTION_TRANSFORMATION, current=transformation)

        # Source proposal must still exist (no orphaned reference).
        proposal_id = candidate.get("source_proposal_id")
        proposal = self._load_proposal(proposal_id) if proposal_id else None
        if proposal_id and proposal is None:
            add("PROPOSAL_MISSING", expected=proposal_id, current=None)

        # Book revision/hash must match; the target must still exist.
        book = BookExpressionStore(self.project)
        try:
            inspected = book.inspect(candidate.get("book_expression_id"))
            metadata = inspected["metadata"]
            if inspected["freshness"] != "fresh":
                add("BOOK_OR_CHAPTER_REVISION_CHANGED", expected="fresh", current=inspected["freshness"])
            if metadata.get("revision") != candidate.get("source_book_revision"):
                add("BOOK_REVISION_CHANGED", expected=candidate.get("source_book_revision"), current=metadata.get("revision"))
            elif _hash(self._book_source_text(book, metadata)) != candidate.get("source_book_hash"):
                add("BOOK_HASH_CHANGED", expected=candidate.get("source_book_hash"), current=_hash(self._book_source_text(book, metadata)))
            if proposal is not None:
                target_reason = self._target_current(proposal, metadata)
                if target_reason is not None:
                    add("TARGET_CHANGED", expected="unchanged target", current=target_reason)
        except FileNotFoundError:
            add("BOOK_MISSING", expected=candidate.get("book_expression_id"), current=None)

        return (not reasons), reasons

    def decide_candidate(
        self,
        candidate_id: str,
        decision_status: str,
        reason: str,
        *,
        decided_by: str = "author",
    ) -> tuple[bool, dict[str, Any]]:
        """Append an immutable decision for a published Book candidate (Model A).

        Decisions are append-only: a candidate may be decided any number of times
        (for example ``deferred`` then later ``approved``). Each call records a new
        immutable decision carrying a ``decision_sequence`` and a ``supersedes``
        pointer to the prior active decision; the latest decision is the active
        one. Returns ``(True, decision)`` on success, or ``(False, error.result)``
        on a structured stale rejection. Raises ``CandidateNotFoundError`` for an
        unknown candidate and ``ValueError`` for an invalid status. Approving a
        candidate materializes an accepted Book-owned source but never recomposes
        the Book, never accepts a recomposed Book, and never moves any pointer.
        """
        if decision_status not in DECISION_STATUSES:
            raise ValueError(f"decision status must be one of {DECISION_STATUSES}: {decision_status}")

        # 1. Locate the candidate.
        try:
            candidate = self.load_book_candidate(candidate_id)
        except FileNotFoundError as exc:
            raise CandidateNotFoundError(str(exc)) from exc

        # 2. Determine this decision's place in the append-only history. The prior
        #    active (latest) decision, if any, is superseded by this one.
        history = self._decision_history_for_candidate(candidate_id)
        previous = history[-1] if history else None
        sequence = (previous["decision_sequence"] + 1) if previous else 1
        supersedes = previous["decision_id"] if previous else None

        # 3. Live freshness gate (never trusts persisted candidate freshness).
        is_fresh, freshness_reasons = self._validate_candidate_freshness(candidate)
        if not is_fresh:
            error = BookFreshnessRejectError({
                "status": "rejected_stale",
                "message": "Book candidate is stale; no decision was recorded",
                "candidate_id": candidate_id,
                "reasons": freshness_reasons,
                "visible_outputs_created": False,
            })
            return False, error.result

        # 4. Create the immutable decision record.
        now = datetime.now(timezone.utc).isoformat()
        decision_id = self._decision_id(candidate_id, decision_status, reason, sequence)
        candidate_hash = _hash(yaml.safe_dump(candidate, sort_keys=True))
        decision = {
            "decision_id": decision_id,
            "artifact_type": "book_candidate_decision",
            "authority": "decision",
            "lifecycle": "decided",
            "candidate_id": candidate_id,
            "book_expression_id": candidate.get("book_expression_id"),
            "candidate_type": candidate.get("artifact_type"),
            "publication_id": candidate.get("publication_id"),
            "source_plan_id": candidate.get("source_plan_id"),
            "decision": {
                "status": decision_status,
                "reason": reason,
                "decided_by": decided_by,
                "decided_at": now,
            },
            "decision_sequence": sequence,
            "supersedes": supersedes,
            "source_candidate_id": candidate_id,
            "source_candidate_revision": candidate.get("revision", 1),
            "source_candidate_hash": candidate_hash,
            # Snapshot of the Book this decision was made against. Recomposition
            # compares this against the current Book (see
            # ``assess_recomposition_freshness``) and blocks on any mismatch.
            "source_book_revision": candidate.get("source_book_revision"),
            "source_book_hash": candidate.get("source_book_hash"),
            "transformation": dict(DECISION_TRANSFORMATION),
            "created_at": now,
            "decided_at": now,
            "freshness": {"status": "fresh", "reasons": []},
        }

        # 5. On approval, materialize a durable accepted Book-owned source (Tier 2:
        #    immutable, revisioned) AND move the current accepted-source pointer
        #    (Tier 3: the only mutable tier) to that new revision. Deferral and
        #    rejection deliberately touch NEITHER: they record author intent in the
        #    decision history (Tier 1) but never revoke or move accepted authority.
        #    An accepted source is distinct from the candidate and carries
        #    authority=accepted; the candidate itself stays a candidate.
        if decision_status == "approved":
            accepted_source = self._create_accepted_source(candidate, decision, now)
            decision["accepted_source_id"] = accepted_source["accepted_source_id"]
            decision["accepted_source_path"] = str(self._accepted_source_path(accepted_source["accepted_source_id"]))
            pointer = self._advance_accepted_source_pointer(candidate, accepted_source, decision, now)
            decision["pointer_moved"] = True
            decision["pointer"] = {
                "owned_kind": pointer["owned_kind"],
                "element_id": pointer["element_id"],
                "current_revision": pointer["current_revision"],
                "current_accepted_source_id": pointer["current_accepted_source_id"],
            }
        else:
            # Defer/reject: pointer untouched. Recorded explicitly so the decision
            # record proves the accepted authority was neither moved nor revoked.
            decision["pointer_moved"] = False

        # 6. Persist the decision immutably (append; never overwrite an existing).
        decision_path = self._decision_path(decision_id)
        if decision_path.exists():
            raise ValueError(f"decision already exists (duplicate status+reason+sequence): {decision_id}")
        decision_path.parent.mkdir(parents=True, exist_ok=True)
        decision_path.write_text(yaml.safe_dump(decision, sort_keys=False), encoding="utf-8")

        # 7. Regenerate the preview from the current accepted-source pointers.
        publication_id = candidate.get("publication_id")
        if publication_id:
            self._generate_decision_aware_preview(publication_id)

        return True, decision

    # ------------------------------------------------------------------
    # Tier 2: accepted Book-owned sources (immutable, revisioned).
    #
    # Approving a candidate produces a durable, accepted Book-owned source in
    # ``book/expression/reconciliation/accepted-sources/``. It is authority
    # ``accepted``, references the candidate and the deciding decision, and is
    # immutable once written -- each approval mints a new revision, never
    # overwriting a prior one. Recomposition reads these via the Tier 3 pointer,
    # never via decisions directly. Materializing an accepted source does NOT move
    # the accepted Book pointer or mutate any
    # Chapter/Structure/Identity/Blueprint/Realization/Scene.
    # ------------------------------------------------------------------

    def _accepted_sources_dir(self) -> Path:
        return self.root / "accepted-sources"

    def _accepted_source_path(self, accepted_source_id: str) -> Path:
        return self._accepted_sources_dir() / f"{accepted_source_id}.yaml"

    def _accepted_source_revision(self, book_id: str, target_id: Any, kind: str) -> int:
        """Next revision for an accepted source over the same Book target/kind."""
        directory = self._accepted_sources_dir()
        if not directory.exists():
            return 1
        revisions = [0]
        for path in sorted(directory.glob("*.yaml")):
            data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
            if data.get("book_expression_id") == book_id and data.get("owned_kind") == kind and data.get("target_id") == target_id:
                revisions.append(data.get("revision", 0))
        return max(revisions) + 1

    def _create_accepted_source(self, candidate: dict[str, Any], decision: dict[str, Any], now: str) -> dict[str, Any]:
        candidate_type = candidate.get("artifact_type")
        kind = ACCEPTED_SOURCE_KIND.get(candidate_type, "unknown")
        book_id = candidate.get("book_expression_id")
        target_id = candidate.get("target_id")
        revision = self._accepted_source_revision(book_id, target_id, kind)
        accepted_source_id = f"book_accepted_{kind}_v{revision:03d}_" + hashlib.sha256(
            decision["decision_id"].encode("utf-8")
        ).hexdigest()[:16]
        artifact = {
            "accepted_source_id": accepted_source_id,
            "artifact_type": "accepted_book_owned_source",
            "owned_kind": kind,
            "authority": "accepted",
            "lifecycle": "accepted",
            "book_expression_id": book_id,
            "target_id": target_id,
            "revision": revision,
            "source_decision_id": decision["decision_id"],
            "source_candidate_id": candidate.get("candidate_id"),
            "candidate_type": candidate_type,
            "publication_id": candidate.get("publication_id"),
            "source_book_revision": candidate.get("source_book_revision"),
            "source_book_hash": candidate.get("source_book_hash"),
            "original": candidate.get("original"),
            "proposed": candidate.get("proposed"),
            "transformation": dict(ACCEPTED_SOURCE_TRANSFORMATION),
            "created_at": now,
        }
        path = self._accepted_source_path(accepted_source_id)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(yaml.safe_dump(artifact, sort_keys=False), encoding="utf-8")
        return artifact

    def load_accepted_book_owned_source(self, accepted_source_id: str) -> dict[str, Any]:
        path = self._accepted_source_path(accepted_source_id)
        if not path.exists():
            raise FileNotFoundError(f"Accepted Book-owned source not found: {accepted_source_id}")
        return yaml.safe_load(path.read_text(encoding="utf-8")) or {}

    # ------------------------------------------------------------------
    # Tier 3: current accepted-source pointers.
    #
    # A pointer is the ONLY mutable tier. There is one pointer per Book-owned
    # element -- keyed by ``(owned_kind, element_id)`` where ``element_id`` is the
    # Book target the accepted source revises (for example ``separator_01`` or the
    # Book id for an order). Approving a candidate advances that element's pointer
    # to the freshly materialized immutable revision and appends to the pointer's
    # own update history; deferral and rejection leave the pointer exactly where
    # it is. Recomposition resolves pointers -- never decisions -- to find the
    # current accepted revision for each element.
    # ------------------------------------------------------------------

    def _pointers_dir(self) -> Path:
        return self._accepted_sources_dir() / "pointers"

    @staticmethod
    def _pointer_key(owned_kind: str, element_id: Any) -> str:
        digest = hashlib.sha256(f"{owned_kind}\0{element_id}".encode("utf-8")).hexdigest()[:16]
        return f"book_pointer_{owned_kind}_{digest}"

    def _pointer_path(self, owned_kind: str, element_id: Any) -> Path:
        return self._pointers_dir() / f"{self._pointer_key(owned_kind, element_id)}.yaml"

    def _advance_accepted_source_pointer(
        self, candidate: dict[str, Any], accepted_source: dict[str, Any], decision: dict[str, Any], now: str
    ) -> dict[str, Any]:
        """Move an element's current pointer to a newly accepted revision (approval only).

        Overwrites the mutable ``current_*`` fields and appends one entry to the
        pointer's append-only ``history``. The immutable revision it references
        (Tier 2) is created separately and never modified here.
        """
        owned_kind = accepted_source["owned_kind"]
        element_id = accepted_source["target_id"]
        book_id = accepted_source["book_expression_id"]
        path = self._pointer_path(owned_kind, element_id)
        existing = yaml.safe_load(path.read_text(encoding="utf-8")) if path.exists() else None
        history = (existing or {}).get("history", []) if isinstance(existing, dict) else []
        entry = {
            "revision": accepted_source["revision"],
            "accepted_source_id": accepted_source["accepted_source_id"],
            "decision_id": decision["decision_id"],
            "decision_sequence": decision["decision_sequence"],
            "publication_id": candidate.get("publication_id"),
            "decided_at": now,
            "reason": decision["decision"]["reason"],
        }
        pointer = {
            "pointer_id": self._pointer_key(owned_kind, element_id),
            "artifact_type": "current_accepted_source_pointer",
            "authority": "pointer",
            "lifecycle": "current",
            "owned_kind": owned_kind,
            "element_id": element_id,
            "book_expression_id": book_id,
            "current_revision": accepted_source["revision"],
            "current_accepted_source_id": accepted_source["accepted_source_id"],
            "active_decision_id": decision["decision_id"],
            "decision_sequence": decision["decision_sequence"],
            "publication_id": candidate.get("publication_id"),
            "source_book_revision": accepted_source.get("source_book_revision"),
            "source_book_hash": accepted_source.get("source_book_hash"),
            "decided_at": now,
            "reason": decision["decision"]["reason"],
            "transformation": dict(POINTER_TRANSFORMATION),
            "updated_at": now,
            "history": history + [entry],
        }
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(yaml.safe_dump(pointer, sort_keys=False), encoding="utf-8")
        return pointer

    def current_accepted_source_pointer(self, element_id: Any, owned_kind: str) -> dict[str, Any] | None:
        """Return the current pointer for a Book-owned element, or ``None`` if none exists.

        A pointer exists once the element has ever been approved; deferral and
        rejection never create or remove it. ``None`` means the element has never
        crossed the accepted-authority boundary.
        """
        path = self._pointer_path(owned_kind, element_id)
        if not path.exists():
            return None
        return yaml.safe_load(path.read_text(encoding="utf-8")) or None

    def current_accepted_source(self, element_id: Any, owned_kind: str) -> dict[str, Any] | None:
        """Resolve an element's pointer to its current immutable accepted revision.

        This is what recomposition consumes: it reads the pointer, then loads the
        immutable revision the pointer names. Returns ``None`` when no pointer
        exists.
        """
        pointer = self.current_accepted_source_pointer(element_id, owned_kind)
        if pointer is None:
            return None
        return self.load_accepted_book_owned_source(pointer["current_accepted_source_id"])

    def _all_pointers(self) -> list[dict[str, Any]]:
        directory = self._pointers_dir()
        pointers: list[dict[str, Any]] = []
        if not directory.exists():
            return pointers
        for path in sorted(directory.glob("*.yaml")):
            data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
            if data.get("artifact_type") == "current_accepted_source_pointer":
                pointers.append(data)
        return pointers

    def current_accepted_sources(self, publication_id: str) -> list[dict[str, Any]]:
        """Accepted Book-owned sources a recomposition of this publication would consume.

        Pointer-based, NOT decision-based: an element is included when its current
        pointer names an accepted revision that originated from this publication.
        Because deferral and rejection never move the pointer, an ``approve`` here
        followed by a later ``defer``/``reject`` still returns the revision -- the
        accepted authority is not revoked. An element whose pointer was later moved
        by a different publication's approval drops out (that publication now owns
        the element).
        """
        sources: list[dict[str, Any]] = []
        for pointer in self._all_pointers():
            source = self.current_accepted_source(pointer["element_id"], pointer["owned_kind"])
            if source is not None and source.get("publication_id") == publication_id:
                sources.append(source)
        return sources

    # Backwards-compatible alias. Historically this returned the decision-derived
    # active set; it is now pointer-derived so defer/reject no longer revoke.
    def active_accepted_sources(self, publication_id: str) -> list[dict[str, Any]]:
        return self.current_accepted_sources(publication_id)

    def accepted_source_history(self, element_id: Any, owned_kind: str) -> list[dict[str, Any]]:
        """Every immutable accepted revision ever written for an element (Tier 2).

        Ordered by revision. Includes revisions no longer current -- accepted
        history is never deleted.
        """
        book_id_filter = None  # element identity is (owned_kind, element_id)
        directory = self._accepted_sources_dir()
        revisions: list[dict[str, Any]] = []
        if not directory.exists():
            return revisions
        for path in sorted(directory.glob("*.yaml")):
            data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
            if data.get("artifact_type") != "accepted_book_owned_source":
                continue
            if data.get("owned_kind") == owned_kind and data.get("target_id") == element_id:
                if book_id_filter is None or data.get("book_expression_id") == book_id_filter:
                    revisions.append(data)
        revisions.sort(key=lambda d: d.get("revision", 0))
        return revisions

    def pointer_history(self, element_id: Any, owned_kind: str) -> list[dict[str, Any]]:
        """Ordered log of every time an element's pointer moved (Tier 3 history).

        Each entry records the revision, the immutable accepted source it moved
        to, and the approving decision. Deferrals and rejections never appear --
        they never move the pointer -- so this shows only authority-boundary
        crossings, distinct from the full decision history (Tier 1).
        """
        pointer = self.current_accepted_source_pointer(element_id, owned_kind)
        if pointer is None:
            return []
        return list(pointer.get("history", []))

    def assess_recomposition_freshness(self, publication_id: str) -> dict[str, Any]:
        """Freshness gate a future recomposition MUST pass before running.

        Approving a candidate snapshots the Book revision/hash it was decided
        against. If the accepted Book advances afterward (Scenario A), the
        approval no longer describes the current Book: this returns
        ``status='blocked_stale_book'`` with structured reasons so recomposition
        is refused until the author re-decides for the new Book. Returns
        ``status='ready'`` when every active approval still matches the current
        Book. This method is read-only and recomposes nothing.
        """
        reasons: list[dict[str, Any]] = []

        def add(code: str, **extra: Any) -> None:
            reasons.append({
                "code": code,
                "expected": extra.get("expected"),
                "current": extra.get("current"),
                "recommended_action": extra.get(
                    "recommended_action",
                    "Book changed since decision. Re-approve or create a new decision.",
                ),
            })

        try:
            manifest = self.inspect_book_publication(publication_id)
        except FileNotFoundError:
            add("PUBLICATION_MISSING", expected=publication_id, current=None,
                recommended_action="publish a fresh Book plan and decide again")
            return {"status": "blocked_stale_book", "publication_id": publication_id,
                    "reasons": reasons, "visible_outputs_created": False,
                    "message": "recomposition blocked: publication missing"}

        book = BookExpressionStore(self.project)
        book_id = manifest.get("source_book_expression")
        try:
            inspected = book.inspect(book_id)
            metadata = inspected["metadata"]
            current_revision = metadata.get("revision")
            current_hash = _hash(self._book_source_text(book, metadata))
            book_fresh = inspected["freshness"] == "fresh"
        except FileNotFoundError:
            metadata = {}
            current_revision = current_hash = None
            book_fresh = False
            add("BOOK_MISSING", expected=book_id, current=None,
                recommended_action="restore the accepted Book and decide again")

        # Pointer-based, NOT decision-based: the gate checks every accepted source
        # this publication currently points to (the exact set recomposition would
        # consume). A pointer that a later defer/reject did NOT move is still
        # checked -- because its revision is still current. Each accepted source
        # carries the Book revision/hash it was approved against.
        current_sources = self.current_accepted_sources(publication_id)
        for source in current_sources:
            if metadata:
                if not book_fresh:
                    add("BOOK_OR_CHAPTER_REVISION_CHANGED", expected="fresh", current=inspected["freshness"])
                if source.get("source_book_revision") != current_revision:
                    add("BOOK_REVISION_CHANGED", expected=source.get("source_book_revision"), current=current_revision)
                elif source.get("source_book_hash") not in (None, current_hash):
                    add("BOOK_HASH_CHANGED", expected=source.get("source_book_hash"), current=current_hash)

        if reasons:
            return {"status": "blocked_stale_book", "publication_id": publication_id,
                    "reasons": reasons, "visible_outputs_created": False,
                    "message": "recomposition blocked: Book changed since decision"}
        return {"status": "ready", "publication_id": publication_id, "reasons": [],
                "active_approvals": len(current_sources),
                "active_pointers": len(current_sources),
                "message": "Book unchanged since every current accepted source"}

    def _generate_decision_aware_preview(self, publication_id: str) -> dict[str, Any]:
        """Regenerate a publication's preview from the current accepted-source pointers.

        Pointer-based, NOT raw-decision-based: a candidate is applied when its
        element's current pointer names an accepted revision that originated from
        this publication's candidate. Because deferral and rejection never move a
        pointer, a candidate approved and then deferred/rejected stays applied --
        the preview mirrors exactly what recomposition (which also reads pointers)
        would produce. Candidates never approved (still undecided, or only ever
        deferred/rejected) have no pointer and are excluded. The preview is rebuilt
        from accepted Chapter sources plus pointer-current Book-owned candidates and
        remains derived, proposed, and noncanonical. No Book Expression is modified
        or accepted.
        """
        manifest = self.inspect_book_publication(publication_id)
        plan = self._load_plan(manifest["source_plan_id"])
        book = BookExpressionStore(self.project)
        inspected = book.inspect(plan["source_book_expression"])
        metadata = inspected["metadata"]
        decisions = self._decisions_for_publication(publication_id)

        # Candidate ids the current pointers resolve to for this publication.
        pointer_current_candidate_ids = {
            source.get("source_candidate_id")
            for source in self.current_accepted_sources(publication_id)
        }
        current_pointers = [
            {
                "owned_kind": p["owned_kind"],
                "element_id": p["element_id"],
                "current_revision": p["current_revision"],
                "current_accepted_source_id": p["current_accepted_source_id"],
                "active_decision_id": p["active_decision_id"],
            }
            for p in self._all_pointers()
            if (self.current_accepted_source(p["element_id"], p["owned_kind"]) or {}).get("publication_id") == publication_id
        ]

        applied_candidates: list[dict[str, Any]] = []
        applied_decisions: list[dict[str, Any]] = []
        for candidate_id in manifest.get("published_candidates", []):
            decision = decisions.get(candidate_id)
            status = decision["decision"]["status"] if decision else "undecided"
            pointer_current = candidate_id in pointer_current_candidate_ids
            applied_decisions.append({"candidate_id": candidate_id, "status": status, "pointer_current": pointer_current})
            if pointer_current:
                applied_candidates.append(self.load_book_candidate(candidate_id))

        preview = self._build_preview(plan, metadata, applied_candidates, publication_id)
        preview["decision_aware"] = True
        preview["pointer_based"] = True
        preview["applied_decisions"] = applied_decisions
        preview["current_pointers"] = current_pointers
        fresh = inspected["freshness"] == "fresh" and metadata.get("revision") == plan.get("source_book_revision")
        preview["freshness"] = {"status": "fresh" if fresh else "stale", "reasons": [] if fresh else ["source Book changed since publication"]}

        preview_path = self.root / "previews" / f"{publication_id}.yaml"
        preview_path.parent.mkdir(parents=True, exist_ok=True)
        preview_path.write_text(yaml.safe_dump(preview, sort_keys=False), encoding="utf-8")
        return preview

    # ------------------------------------------------------------------
    # Phase C1: pointer-based Book recomposition.
    #
    # Recomposition derives a candidate recomposed Book by assembling the current
    # accepted Chapter Expression pointers with the current accepted Book-owned
    # source pointers (Tier 3). The result is authority=derived, lifecycle=
    # proposed, role=reconciliation_recomposition, canonical=false. It is
    # READ-ONLY over accepted sources: it never moves the accepted Book pointer,
    # never accepts a candidate, never completes reconciliation, never treats
    # decisions as narrative sources, and never reads unpublished candidates.
    #
    # Recomposition is gated by comprehensive freshness validation and is atomic:
    # any validation failure blocks with a structured RecompositionBlockedError
    # and NO artifact (partial or stale) is written. Given the same publication,
    # the same pointers, and the same Book state, recomposition is deterministic
    # (a timestamp-independent content_hash is identical byte-for-byte).
    # ------------------------------------------------------------------

    def _recompositions_dir(self) -> Path:
        return self.root / "recompositions"

    def _recomposition_path(self, publication_id: str) -> Path:
        return self._recompositions_dir() / f"{publication_id}_recomposed.yaml"

    def _load_pointer_by_id(self, pointer_id: str) -> dict[str, Any] | None:
        """Locate a current accepted-source pointer by its ``pointer_id``.

        Pointers are keyed on disk by ``(owned_kind, element_id)``; this scans
        every current pointer and returns the one whose id matches, or ``None``.
        """
        for pointer in self._all_pointers():
            if pointer.get("pointer_id") == pointer_id:
                return pointer
        return None

    def _block(self, status: str, publication_id: str, message: str, reasons: list[dict[str, Any]]) -> RecompositionBlockedError:
        return RecompositionBlockedError({
            "status": status,
            "publication_id": publication_id,
            "message": message,
            "reasons": reasons,
            "visible_outputs_created": False,
        })

    # -- Source resolution layer ------------------------------------------------

    def _resolve_chapter_for_recomposition(
        self, chapter_id: str, publication_id: str
    ) -> tuple[bool, dict[str, Any] | RecompositionBlockedError]:
        """Resolve a Chapter from its current Chapter Expression pointer and validate freshness.

        The "Chapter Expression pointer" is the accepted Book's reference to the
        Chapter Expression (``chapter_expression_id`` + ``accepted_revision`` +
        ``content_hash``). The pointer target must exist (the accepted Chapter
        Expression) and must be fresh (its current content hash must match).
        """
        book = BookExpressionStore(self.project)
        manifest = self.inspect_book_publication(publication_id)
        try:
            metadata = book.inspect(manifest["source_book_expression"])["metadata"]
        except FileNotFoundError:
            return False, self._block("blocked_missing_target", publication_id, "recomposition blocked: accepted Book missing", [{"code": "BOOK_MISSING", "expected": manifest.get("source_book_expression"), "current": None, "recommended_action": "restore the accepted Book and recompose again"}])
        reference = next((item for item in metadata["chapters"] if item["chapter_id"] == chapter_id), None)
        if reference is None:
            return False, self._block("blocked_missing_target", publication_id, "recomposition blocked: Chapter pointer missing", [{"code": "MISSING_CHAPTER_POINTER", "expected": chapter_id, "current": None, "recommended_action": "recompose the accepted Book so the Chapter pointer is restored"}])
        try:
            current = book._accepted_chapter(chapter_id)
        except ValueError:
            return False, self._block("blocked_missing_target", publication_id, "recomposition blocked: Chapter revision missing", [{"code": "MISSING_REVISION", "expected": reference.get("chapter_expression_id"), "current": None, "recommended_action": "restore the accepted Chapter Expression and recompose again"}])
        if current["revision"] != reference["accepted_revision"] or current["content_hash"] != reference["content_hash"]:
            return False, self._block("blocked_stale_chapter", publication_id, "recomposition blocked: Chapter changed since accepted", [{"code": "STALE_CHAPTER", "chapter_id": chapter_id, "expected": reference["accepted_revision"], "current": current["revision"], "recommended_action": "recompose the accepted Book from the current Chapter, then recompose reconciliation"}])
        return True, {
            "chapter_id": chapter_id,
            "chapter_expression_id": reference["chapter_expression_id"],
            "pointer_id": reference["chapter_expression_id"],
            "accepted_revision": reference["accepted_revision"],
            "content_hash": reference["content_hash"],
        }

    def _resolve_owned_for_recomposition(
        self, pointer_id: str, publication_id: str
    ) -> tuple[bool, dict[str, Any] | RecompositionBlockedError]:
        """Resolve a Book-owned source from its current pointer; validate target exists and is fresh."""
        pointer = self._load_pointer_by_id(pointer_id)
        if pointer is None:
            return False, self._block("blocked_missing_target", publication_id, "recomposition blocked: Book-owned pointer missing", [{"code": "MISSING_POINTER", "expected": pointer_id, "current": None, "recommended_action": "re-approve the Book-owned candidate to restore its pointer"}])
        try:
            source = self.load_accepted_book_owned_source(pointer["current_accepted_source_id"])
        except FileNotFoundError:
            return False, self._block("blocked_missing_target", publication_id, "recomposition blocked: accepted Book-owned revision missing", [{"code": "MISSING_REVISION", "expected": pointer.get("current_accepted_source_id"), "current": None, "recommended_action": "re-approve the Book-owned candidate to materialize its accepted revision"}])
        return True, {"pointer": pointer, "source": source}

    def _resolve_separator_for_recomposition(self, separator_pointer_id: str, publication_id: str) -> tuple[bool, Any]:
        return self._resolve_owned_for_recomposition(separator_pointer_id, publication_id)

    def _resolve_order_for_recomposition(self, order_pointer_id: str, publication_id: str) -> tuple[bool, Any]:
        return self._resolve_owned_for_recomposition(order_pointer_id, publication_id)

    def _resolve_title_for_recomposition(self, title_pointer_id: str, publication_id: str) -> tuple[bool, Any]:
        return self._resolve_owned_for_recomposition(title_pointer_id, publication_id)

    def _resolve_material_for_recomposition(self, material_pointer_id: str, publication_id: str) -> tuple[bool, Any]:
        return self._resolve_owned_for_recomposition(material_pointer_id, publication_id)

    # -- Freshness gate ---------------------------------------------------------

    def _validate_recomposition_freshness(
        self, publication_id: str, current_book: dict[str, Any] | None,
        book_revision_required: str | None = None,
    ) -> tuple[bool, str | RecompositionBlockedError]:
        """Validate every pointer and target is fresh before recomposition runs.

        Returns ``(True, "")`` when recomposition is ready, or ``(False, error)``
        with a structured :class:`RecompositionBlockedError` when blocked. Blocks
        immediately and atomically -- never produces partial or stale output.
        Ordering: missing/incomplete publication and Book first, then Chapter
        pointers (missing target then staleness), then Book-owned pointers, then
        the Book-revision approval-snapshot match.
        """
        # 1. Publication exists and is complete (accepted|published).
        try:
            manifest = self.inspect_book_publication(publication_id)
        except FileNotFoundError:
            return False, self._block("blocked_missing_target", publication_id, "recomposition blocked: publication missing", [{"code": "PUBLICATION_MISSING", "expected": publication_id, "current": None, "recommended_action": "publish a Book reconciliation plan before recomposing"}])
        if manifest.get("lifecycle") not in {"published", "accepted"} and manifest.get("acceptance_status") not in {"accepted"}:
            return False, self._block("blocked_missing_target", publication_id, "recomposition blocked: publication not complete", [{"code": "PUBLICATION_NOT_COMPLETE", "expected": "published|accepted", "current": manifest.get("lifecycle"), "recommended_action": "complete publication before recomposing"}])

        book = BookExpressionStore(self.project)
        book_id = manifest.get("source_book_expression")
        try:
            inspected = book.inspect(book_id)
        except FileNotFoundError:
            return False, self._block("blocked_missing_target", publication_id, "recomposition blocked: accepted Book missing", [{"code": "BOOK_MISSING", "expected": book_id, "current": None, "recommended_action": "restore the accepted Book and recompose again"}])
        metadata = inspected["metadata"]
        current_revision = metadata.get("revision")
        current_hash = _hash(self._book_source_text(book, metadata))

        if book_revision_required is not None and str(current_revision) != str(book_revision_required):
            return False, self._block("blocked_stale_book", publication_id, "recomposition blocked: required Book revision does not match", [{"code": "STALE_BOOK_REVISION", "expected": book_revision_required, "current": current_revision, "recommended_action": "recompose against the current Book revision or re-decide candidates"}])

        # 2-4. Chapter pointers: exist, target exists, fresh. Missing targets
        #      (blocked_missing_target) take precedence over staleness
        #      (blocked_stale_chapter) so the author fixes the harder failure first.
        order = self._current_order(metadata)
        for chapter_id in order:
            ok, result = self._resolve_chapter_for_recomposition(chapter_id, publication_id)
            if not ok:
                return False, result

        # 5-7. Book-owned pointers for this publication: exist, target exists, fresh.
        #      Iterate pointers directly (each pointer carries its origin
        #      publication_id) rather than current_accepted_sources, which would
        #      raise while eagerly resolving a deleted revision -- the very
        #      missing-target case this check must report as a structured block.
        for pointer in self._all_pointers():
            if pointer.get("publication_id") != publication_id:
                continue
            ok, result = self._resolve_owned_for_recomposition(pointer["pointer_id"], publication_id)
            if not ok:
                return False, result

        # 8. Current Book must match every approval snapshot. Approving a candidate
        #    snapshots the Book revision/hash it was decided against; if the
        #    accepted Book advanced afterward, the approval no longer describes the
        #    current Book and recomposition is blocked until the author re-decides.
        gate = self.assess_recomposition_freshness(publication_id)
        if gate["status"] != "ready":
            reasons = gate.get("reasons", []) or [{"code": "STALE_BOOK_REVISION", "recommended_action": "re-approve or create a new decision for the current Book"}]
            return False, self._block("blocked_stale_book", publication_id, gate.get("message", "recomposition blocked: Book changed since decision"), reasons)

        return True, ""

    # -- Assembly ---------------------------------------------------------------

    def _assemble_recomposition(
        self, publication_id: str, manifest: dict[str, Any], metadata: dict[str, Any],
    ) -> dict[str, Any]:
        """Deterministically resolve every source into the recomposed Book body.

        Order resolution: an order pointer (if present) overrides the accepted
        Book order; otherwise the accepted Book order is used. Separator, title,
        and inserted-material pointers are each resolved independently. Returns
        the fully resolved body plus the ``source_pointers`` map. Deterministic:
        no timestamps enter the returned structure.
        """
        default_title = metadata["book_owned_content"].get("title", "")
        default_separator = metadata["book_owned_content"].get("separator", "---")

        separator_pointer_id = order_pointer_id = title_pointer_id = None
        inserted_material_pointer_ids: list[str] = []
        applied_separator = applied_order = applied_title = None
        insertions: list[dict[str, Any]] = []

        # Group this publication's current owned pointers by kind (pointer-based,
        # NOT decision-based: defer/reject after an approval leave the pointer, so
        # the accepted revision it names is still consumed).
        for source in self.current_accepted_sources(publication_id):
            pointer = self.current_accepted_source_pointer(source.get("target_id"), source.get("owned_kind"))
            kind = source.get("owned_kind")
            pid = pointer["pointer_id"]
            if kind == "separator":
                separator_pointer_id = pid
                applied_separator = source.get("proposed")
            elif kind == "order":
                order_pointer_id = pid
                applied_order = source.get("proposed")
            elif kind == "title":
                title_pointer_id = pid
                applied_title = source.get("proposed")
            elif kind == "material":
                inserted_material_pointer_ids.append(pid)
                insertions.append({"pointer_id": pid, "accepted_source_id": source.get("accepted_source_id"), "target_id": source.get("target_id"), "revision": source.get("revision"), "content": source.get("proposed")})

        title = applied_title if applied_title is not None else default_title
        separator = applied_separator if applied_separator is not None else default_separator
        if applied_order is not None:
            order = [item.strip() for item in applied_order.split(",")]
        else:
            order = self._current_order(metadata)

        by_id = {item["chapter_id"]: item for item in metadata["chapters"]}
        chapters = []
        chapter_pointers = []
        for chapter_id in order:
            ok, resolved = self._resolve_chapter_for_recomposition(chapter_id, publication_id)
            # Freshness already validated; resolution here cannot fail. Guard anyway.
            reference = resolved if ok else by_id.get(chapter_id, {})
            chapters.append({
                "chapter_id": chapter_id,
                "chapter_expression_id": reference.get("chapter_expression_id"),
                "accepted_revision": reference.get("accepted_revision"),
                "content_hash": reference.get("content_hash"),
            })
            chapter_pointers.append({"chapter_id": chapter_id, "pointer_id": reference.get("pointer_id") or reference.get("chapter_expression_id")})

        insertions.sort(key=lambda item: (str(item.get("target_id")), str(item.get("pointer_id"))))
        inserted_material_pointer_ids = sorted(inserted_material_pointer_ids)

        body = {
            "title_rendering": title,
            "separator": separator,
            "order": order,
            "chapters": chapters,
            "insertions": insertions,
            "source_pointers": {
                "chapters": chapter_pointers,
                "book_owned": {
                    "separator_pointer_id": separator_pointer_id,
                    "order_pointer_id": order_pointer_id,
                    "title_rendering_pointer_id": title_pointer_id,
                    "inserted_material_pointer_ids": inserted_material_pointer_ids,
                },
            },
        }
        return body

    @staticmethod
    def _recomposition_content_hash(body: dict[str, Any]) -> str:
        """Timestamp-independent content hash guaranteeing deterministic output.

        Hashes only the resolved narrative content (title, separator, order,
        Chapter identities+hashes, insertions) with stable JSON serialization.
        Excludes ``recomposed_at`` and any provenance so repeated recomposition
        over identical state yields a byte-identical hash.
        """
        signature = json.dumps({
            "title_rendering": body["title_rendering"],
            "separator": body["separator"],
            "order": body["order"],
            "chapters": [(item["chapter_id"], item["content_hash"]) for item in body["chapters"]],
            "insertions": [(item.get("target_id"), item.get("content")) for item in body["insertions"]],
            "source_pointers": body["source_pointers"],
        }, sort_keys=True)
        return _hash(signature)

    def recompose_book_from_accepted_sources(
        self, publication_id: str, book_revision_required: str | None = None,
    ) -> tuple[bool, dict[str, Any] | RecompositionBlockedError]:
        """Recompose a noncanonical Book from current accepted Chapter and Book-owned pointers.

        Assembles a derived, proposed, noncanonical recomposed Book from the
        current accepted Chapter Expression pointers plus the current accepted
        Book-owned source pointers. Returns ``(True, recomposed_book_dict)`` on
        success or ``(False, RecompositionBlockedError)`` on any stale/missing
        block. READ-ONLY over accepted sources: it never moves the accepted Book
        pointer, never accepts a candidate, never completes reconciliation, never
        treats decisions as narrative sources, and never reads unpublished
        candidates. Deterministic: the persisted ``content_hash`` is identical for
        identical state. Atomic: on any block, no artifact is written.
        """
        # Freshness gate first; nothing is written unless every check passes.
        ready, gate = self._validate_recomposition_freshness(publication_id, None, book_revision_required)
        if not ready:
            return False, gate

        manifest = self.inspect_book_publication(publication_id)
        book = BookExpressionStore(self.project)
        metadata = book.inspect(manifest["source_book_expression"])["metadata"]

        body = self._assemble_recomposition(publication_id, manifest, metadata)
        content_hash = self._recomposition_content_hash(body)
        # Snapshots of the Book revision each active approval was decided against.
        approval_snapshots = [
            {"owned_kind": source.get("owned_kind"), "target_id": source.get("target_id"), "book_revision_at_approval": source.get("source_book_revision"), "book_hash_at_approval": source.get("source_book_hash")}
            for source in self.current_accepted_sources(publication_id)
        ]

        recomposed = {
            "recomposition_id": f"book_recomposition_{publication_id}",
            "artifact_type": "book_reconciliation_recomposition",
            "authority": "derived",
            "lifecycle": "proposed",
            "role": "reconciliation_recomposition",
            "canonical": False,
            "book_expression_id": f"{manifest['source_book_expression']}:recomposition",
            "source_book_expression": manifest["source_book_expression"],
            "source_book_revision": metadata.get("revision"),
            "content_hash": content_hash,
            "title_rendering": body["title_rendering"],
            "separator": body["separator"],
            "order": body["order"],
            "chapters": body["chapters"],
            "insertions": body["insertions"],
            "source_pointers": body["source_pointers"],
            "inspection_id": manifest.get("source_inspection_id"),
            "publication_id": publication_id,
            "recomposed_at": datetime.now(timezone.utc).isoformat(),
            "provenance": {
                "method": "pointer_based_recomposition",
                "transformation": dict(RECOMPOSITION_TRANSFORMATION),
                "book_revision_at_approval": approval_snapshots,
                "validation_status": "fresh",
                "accepted_book_pointer_changed": False,
            },
        }

        self._store_recomposed_book(recomposed)
        return True, recomposed

    def _store_recomposed_book(self, recomposed: dict[str, Any]) -> Path:
        """Persist the recomposed Book as a transient derived artifact (atomic write).

        Stored under ``recompositions/`` -- NOT in accepted-sources. This is a
        noncanonical, proposed artifact; writing it changes no pointer and accepts
        nothing. The write is atomic (temp + replace) so a reader never observes a
        partially written recomposition.
        """
        path = self._recomposition_path(recomposed["publication_id"])
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(".yaml.tmp")
        try:
            tmp.write_text(yaml.safe_dump(recomposed, sort_keys=False), encoding="utf-8")
            tmp.replace(path)
        except Exception:
            if tmp.exists():
                tmp.unlink()
            raise
        return path

    def load_recomposed_book(self, publication_id: str) -> dict[str, Any]:
        """Load the most recent recomposition artifact for a publication."""
        path = self._recomposition_path(publication_id)
        if not path.exists():
            raise FileNotFoundError(f"Book recomposition not found: {publication_id}")
        return yaml.safe_load(path.read_text(encoding="utf-8")) or {}

    # ------------------------------------------------------------------
    # Phase C2: read-only, deterministic recomposition-vs-manuscript comparison.
    #
    # ``compare_book_recomposition`` evaluates whether a Phase C1 pointer-based
    # recomposition matches an external manuscript and classifies every divergence
    # by ownership. It is authority=derived, lifecycle=evaluated,
    # role=reconciliation_comparison, canonical=false. It NEVER accepts the Book,
    # moves the accepted Book pointer, mutates any source, moves any accepted
    # pointer, completes reconciliation, or generates automatic proposals.
    #
    # Comparison is gated by a 12-point freshness validation and is atomic: any
    # failure blocks with a structured ComparisonBlockedError and NO report (partial
    # or otherwise) is written. Given the same recomposition, the same external
    # manuscript, and the same marker contract, comparison is deterministic: the
    # persisted report -- including comparison_id and every finding_id -- is
    # byte-identical on repeat (no timestamps enter the artifact).
    # ------------------------------------------------------------------

    def _comparisons_dir(self) -> Path:
        return self.root / "comparisons"

    def _comparison_path(self, comparison_id: str) -> Path:
        return self._comparisons_dir() / f"{comparison_id}.yaml"

    @staticmethod
    def _publication_id_from_recomposition(recomposition_id: str) -> str:
        return recomposition_id.removeprefix("book_recomposition_")

    @staticmethod
    def _recomposition_body_view(recomposed: dict[str, Any]) -> dict[str, Any]:
        """Rebuild the exact body shape ``_recomposition_content_hash`` hashes.

        Used to re-derive the content hash from a stored recomposition's own fields
        so tampering (a mutated field whose stored ``content_hash`` was not updated)
        is detected.
        """
        return {
            "title_rendering": recomposed.get("title_rendering", ""),
            "separator": recomposed.get("separator", "---"),
            "order": recomposed.get("order", []),
            "chapters": recomposed.get("chapters", []),
            "insertions": recomposed.get("insertions", []),
            "source_pointers": recomposed.get("source_pointers", {}),
        }

    def _render_recomposition_text(self, recomposed: dict[str, Any]) -> str:
        """Render a recomposition into a marked manuscript identical to compose().

        The rendering mirrors ``BookExpressionStore.compose`` byte-for-byte (title
        heading, Chapter markers, inter-Chapter separators) so a faithful external
        manuscript compares as an exact match. Chapter prose is resolved from the
        current accepted Chapter Expression (freshness already validated).
        """
        book = BookExpressionStore(self.project)
        title = recomposed.get("title_rendering") or ""
        separator = recomposed.get("separator", "---")
        sections: list[str] = []
        for item in recomposed.get("chapters", []):
            chapter_id = item["chapter_id"]
            revision = item.get("accepted_revision")
            text = book._chapter_text(book._accepted_chapter(chapter_id))
            sections.append(
                f"<!-- auteur:chapter id={chapter_id} expression_revision={revision} -->\n"
                f"{text}\n<!-- auteur:end-chapter id={chapter_id} -->"
            )
        out = f"# {title}\n\n" if title else ""
        pieces: list[str] = []
        for index, section in enumerate(sections):
            if index:
                pieces.append(
                    f"<!-- auteur:book-separator id=separator_{index:02d} revision=1 -->\n"
                    f"{separator}\n<!-- auteur:end-book-separator id=separator_{index:02d} -->"
                )
            pieces.append(section)
        out += "\n\n".join(pieces) + "\n"
        return out

    @staticmethod
    def _external_title(text: str) -> str | None:
        """The manuscript's leading ``# `` heading, or None if absent."""
        for line in text.splitlines():
            if line.strip() == "":
                continue
            if line.startswith("# "):
                return line[2:].strip()
            return None
        return None

    def _determine_ownership(
        self,
        element_kind: str,
        element_id: str,
        contract: MarkerContract,
        known_chapters: set[str],
    ) -> tuple[str, str, str]:
        """Route a parsed external element to (ownership, target, confidence).

        Marker-based, using the Phase A marker contract: an invalid marker is a
        ``marker_residual``; a valid one routes to a Chapter, a Book-owned element,
        an unknown-Chapter ``structural`` problem, or ``unresolved``.
        """
        marker = {"kind": element_kind, "id": element_id}
        if not contract.is_valid(marker):
            return "marker", element_id, "certain"
        return contract.route(marker, known_chapters)

    @staticmethod
    def _recommend_action(category: str, detail: str = "") -> str:
        return {
            "exact_match": "no action: recomposition and external manuscript agree",
            "book_owned_residual": "accept the Book if this Book-owned difference is intended, or re-approve the Book-owned source",
            "chapter_owned_residual": "reconcile the Chapter prose difference through Chapter reconciliation before Book acceptance",
            "structural_residual": "restore the missing/duplicate/reordered Chapter boundary, then recompose and compare again",
            "marker_residual": "repair the Book marker or manuscript marker contract, then compare again",
            "unresolved_residual": "manually map the ambiguous or cross-boundary content; it cannot be attributed safely",
        }.get(category, "review this difference before Book acceptance")

    def _validate_comparison_freshness(
        self, recomposition_id: str, publication_id: str
    ) -> tuple[bool, dict[str, Any] | ComparisonBlockedError]:
        """Run the 12-point freshness gate; block atomically on any failure.

        Checks 1-10 (recomposition present, derived, proposed, untampered, Phase C1
        fresh, publication present, Chapter pointers unchanged, Book-owned pointers
        unchanged, pointer targets present, Book revision matches the recomposition
        snapshot). Checks 11-12 (external manuscript present + hash captured) are
        performed by the caller once the manuscript path is resolved. Returns
        ``(True, recomposed)`` when ready, else ``(False, ComparisonBlockedError)``.
        """
        # 1. Recomposition exists on disk.
        try:
            recomposed = self.load_recomposed_book(publication_id)
        except FileNotFoundError:
            return False, ComparisonBlockedError(
                "blocked_missing_recomposition", recomposition_id,
                "comparison blocked: recomposition missing",
                [{"code": "MISSING_RECOMPOSITION", "expected": recomposition_id, "current": None,
                  "recommended_action": "run recompose-book-from-accepted before comparing"}],
            )

        # 2-3. Recomposition is derived and proposed.
        if recomposed.get("authority") != "derived":
            return False, ComparisonBlockedError(
                "blocked_stale_recomposition", recomposition_id,
                "comparison blocked: recomposition is not derived",
                [{"code": "RECOMPOSITION_NOT_DERIVED", "expected": "derived", "current": recomposed.get("authority"),
                  "recommended_action": "recompose the Book, then compare again"}],
            )
        if recomposed.get("lifecycle") != "proposed":
            return False, ComparisonBlockedError(
                "blocked_stale_recomposition", recomposition_id,
                "comparison blocked: recomposition is not proposed",
                [{"code": "RECOMPOSITION_NOT_PROPOSED", "expected": "proposed", "current": recomposed.get("lifecycle"),
                  "recommended_action": "recompose the Book, then compare again"}],
            )

        # 4. Recomposition hash matches its own stored content (not tampered).
        recomputed = self._recomposition_content_hash(self._recomposition_body_view(recomposed))
        if recomputed != recomposed.get("content_hash"):
            return False, ComparisonBlockedError(
                "blocked_stale_recomposition", recomposition_id,
                "comparison blocked: recomposition content hash does not match its body",
                [{"code": "RECOMPOSITION_TAMPERED", "expected": recomposed.get("content_hash"), "current": recomputed,
                  "recommended_action": "recompose the Book from accepted sources, then compare again"}],
            )

        # 5, 6, 9. Phase C1 freshness gate: publication complete, Chapter pointers
        #          and Book-owned pointer targets present and fresh, approval
        #          snapshots match the current Book.
        ready, gate = self._validate_recomposition_freshness(publication_id, None)
        if not ready:
            block = gate.result
            return False, ComparisonBlockedError(
                block.get("status", "blocked_stale_recomposition"), recomposition_id,
                block.get("message", "comparison blocked: recomposition is no longer fresh"),
                block.get("reasons", []),
            )

        # 7, 8, 10. The recomposition must still describe the CURRENT accepted
        #           sources: re-assemble from live pointers and Book state and
        #           compare the deterministic content hash. Any drift (a Chapter
        #           pointer advanced, a Book-owned pointer moved to different
        #           content, the Book revision changed) blocks -- a stale
        #           recomposition must never be compared as if current.
        manifest = self.inspect_book_publication(publication_id)
        book = BookExpressionStore(self.project)
        metadata = book.inspect(manifest["source_book_expression"])["metadata"]
        if str(metadata.get("revision")) != str(recomposed.get("source_book_revision")):
            return False, ComparisonBlockedError(
                "blocked_stale_recomposition", recomposition_id,
                "comparison blocked: accepted Book revision changed since recomposition",
                [{"code": "BOOK_REVISION_CHANGED", "expected": recomposed.get("source_book_revision"),
                  "current": metadata.get("revision"),
                  "recommended_action": "recompose the Book against the current revision, then compare again"}],
            )
        live_hash = self._recomposition_content_hash(
            self._assemble_recomposition(publication_id, manifest, metadata)
        )
        if live_hash != recomposed.get("content_hash"):
            return False, ComparisonBlockedError(
                "blocked_pointer_moved", recomposition_id,
                "comparison blocked: accepted pointers changed since recomposition",
                [{"code": "ACCEPTED_POINTER_MOVED", "expected": recomposed.get("content_hash"), "current": live_hash,
                  "recommended_action": "recompose the Book from the current accepted pointers, then compare again"}],
            )

        return True, recomposed

    def compare_book_recomposition(
        self, recomposition_id: str, external_manuscript_path: Path | str | None = None
    ) -> tuple[bool, dict[str, Any] | ComparisonBlockedError]:
        """Compare a pointer-based recomposition against an external manuscript.

        Read-only and deterministic. Returns ``(True, comparison_report)`` on
        success or ``(False, ComparisonBlockedError)`` on any stale/missing block.
        The report is authority=derived, lifecycle=evaluated,
        role=reconciliation_comparison, canonical=false and classifies every
        divergence by ownership. It NEVER accepts the Book, moves any pointer,
        mutates any source, completes reconciliation, or generates proposals. On any
        block, NO report is written.
        """
        publication_id = self._publication_id_from_recomposition(recomposition_id)

        # Freshness checks 1-10.
        ready, gate = self._validate_comparison_freshness(recomposition_id, publication_id)
        if not ready:
            return False, gate
        recomposed = gate  # type: ignore[assignment]

        # Marker contract (from the source inspection) must be supported.
        inspection: dict[str, Any] = {}
        try:
            inspection = self._load_inspection(recomposed.get("inspection_id"))
        except FileNotFoundError:
            inspection = {}
        marker_version = inspection.get("marker_contract", {}).get("version", 1)
        contract = MarkerContract(marker_version)
        if not contract.is_supported:
            return False, ComparisonBlockedError(
                "blocked_stale_recomposition", recomposition_id,
                "comparison blocked: unsupported marker contract",
                [{"code": "UNSUPPORTED_MARKER_CONTRACT", "expected": sorted(SUPPORTED_MARKER_CONTRACT_VERSIONS),
                  "current": marker_version,
                  "recommended_action": "re-inspect the manuscript under a supported marker contract"}],
            )

        # 11. External manuscript exists at the resolved path.
        default_path = inspection.get("external_manuscript", {}).get("path")
        external_path = Path(external_manuscript_path) if external_manuscript_path else (
            Path(default_path) if default_path else None
        )
        if external_path is None or not external_path.exists():
            return False, ComparisonBlockedError(
                "blocked_missing_external_manuscript", recomposition_id,
                "comparison blocked: external manuscript missing",
                [{"code": "MISSING_EXTERNAL_MANUSCRIPT", "expected": str(external_path) if external_path else None,
                  "current": None,
                  "recommended_action": "restore the external manuscript or pass --external-manuscript PATH"}],
            )

        # 12. Capture the external manuscript hash at comparison time.
        external_text = external_path.read_text(encoding="utf-8")
        external_hash = _hash(external_text)

        # Deterministic comparison engine.
        recomposed_text = self._render_recomposition_text(recomposed)
        external_parsed = BookManuscriptParser().parse(external_text)
        findings, residual_counts = self._build_comparison_findings(
            recomposed, recomposed_text, external_text, external_parsed, contract
        )

        book = BookExpressionStore(self.project)
        metadata = book.inspect(recomposed["source_book_expression"])["metadata"]
        source_book_hash = _hash(self._book_source_text(book, metadata))

        chapter_sources = [
            {
                "chapter_id": item.get("chapter_id"),
                "accepted_expression_id": item.get("chapter_expression_id"),
                "revision": item.get("accepted_revision"),
                "content_hash": item.get("content_hash"),
            }
            for item in recomposed.get("chapters", [])
        ]
        book_owned_sources = [
            {
                "pointer_id": (self.current_accepted_source_pointer(source.get("target_id"), source.get("owned_kind")) or {}).get("pointer_id"),
                "accepted_revision_id": source.get("accepted_source_id"),
                "owned_kind": source.get("owned_kind"),
                "content_hash": _hash(source.get("proposed") or ""),
            }
            for source in self.current_accepted_sources(publication_id)
        ]

        total = sum(residual_counts.values())
        ready_for_acceptance = (
            residual_counts["unresolved_residual"] == 0
            and residual_counts["chapter_owned_residual"] == 0
            and residual_counts["structural_residual"] == 0
            and residual_counts["marker_residual"] == 0
        )
        exact_match = residual_counts["exact_match"] > 0 and total == residual_counts["exact_match"]

        comparison_id = "book_comparison_" + hashlib.sha256(
            (
                recomposition_id + "\0" + external_hash + "\0" + str(contract.version) + "\0"
                + "|".join(sorted(item["finding_id"] for item in findings))
            ).encode("utf-8")
        ).hexdigest()[:32]

        report = {
            "authority": "derived",
            "lifecycle": "evaluated",
            "role": "reconciliation_comparison",
            "canonical": False,
            "comparison_id": comparison_id,
            "source_recomposition_id": recomposition_id,
            "source_recomposition_hash": recomposed.get("content_hash"),
            "source_publication_id": publication_id,
            "external_manuscript": {
                "path": str(external_path),
                "content_hash": external_hash,
                "marker_contract_version": contract.version,
            },
            "source_book_revision": recomposed.get("source_book_revision"),
            "source_book_hash": source_book_hash,
            "chapter_sources": chapter_sources,
            "book_owned_sources": book_owned_sources,
            "summary": {
                "exact_match": exact_match,
                "ready_for_book_acceptance": ready_for_acceptance,
                "residual_counts": residual_counts,
            },
            "findings": findings,
            "transformation": dict(COMPARISON_TRANSFORMATION),
        }
        self._store_comparison_report(report)
        return True, report

    def _build_comparison_findings(
        self,
        recomposed: dict[str, Any],
        recomposed_text: str,
        external_text: str,
        external_parsed: dict[str, Any],
        contract: MarkerContract,
    ) -> tuple[list[dict[str, Any]], dict[str, int]]:
        """Structured, marker-aware classification of every divergence.

        The recomposition is the source of truth. Each Book-owned aspect (title,
        separator, Chapter order), each Chapter's prose, and each Book-owned
        insertion is compared to the external manuscript and classified into one of
        the six residual categories. Deterministic: no timestamps or ordering
        nondeterminism enter the findings.
        """
        findings: list[dict[str, Any]] = []
        counts = {category: 0 for category in COMPARISON_CATEGORIES}

        def emit(category: str, external_span: tuple[int, int], recomposed_span: tuple[int, int],
                 marker: str | None, routing_target: str, confidence: str, reason: str) -> None:
            finding_id = "finding_" + hashlib.sha256(
                (
                    category + "\0" + str(external_span) + "\0" + str(recomposed_span) + "\0"
                    + str(routing_target) + "\0" + reason
                ).encode("utf-8")
            ).hexdigest()[:32]
            counts[category] += 1
            findings.append({
                "finding_id": finding_id,
                "category": category,
                "external_span": {"start_line": external_span[0], "end_line": external_span[1]},
                "recomposed_span": {"start_line": recomposed_span[0], "end_line": recomposed_span[1]},
                "ownership_analysis": {"marker": marker, "routing_target": routing_target, "confidence": confidence},
                "reason": reason,
                "recommended_action": self._recommend_action(category, reason),
            })

        external_lines = external_text.count("\n") + 1
        recomposed_parsed = BookManuscriptParser().parse(recomposed_text)
        rec_chapter_span = {item["id"]: tuple(item["line_range"]) for item in recomposed_parsed["chapters"]}

        # 1. Markerless / malformed marker contract violations. A markerless
        #    manuscript is unresolved and short-circuits structural/content
        #    attribution (there is no ownership information to route by).
        markerless = False
        for finding in external_parsed["findings"]:
            classification = finding.get("classification")
            if classification == "markerless":
                markerless = True
                emit("unresolved_residual", (1, external_lines), (1, recomposed_text.count("\n") + 1),
                     None, "book", "ambiguous", "external manuscript has no Book ownership markers")
            elif classification == "malformed_marker":
                line = finding.get("line", 0)
                emit("marker_residual", (line, line), (0, 0), None, "book", "certain",
                     "malformed Book marker in external manuscript")
        if markerless:
            return findings, counts

        recomposed_order = list(recomposed.get("order", []))
        known_chapters = set(recomposed_order)

        # 2. Duplicate Chapter markers -> marker contract violation.
        seen: dict[str, int] = {}
        for item in external_parsed["chapters"]:
            seen[item["id"]] = seen.get(item["id"], 0) + 1
        for chapter_id, occurrences in seen.items():
            if occurrences > 1:
                span = next(tuple(item["line_range"]) for item in external_parsed["chapters"] if item["id"] == chapter_id)
                _own, target, confidence = self._determine_ownership("chapter", chapter_id, contract, known_chapters)
                emit("marker_residual", span, rec_chapter_span.get(chapter_id, (0, 0)),
                     chapter_id, chapter_id, "certain",
                     f"Chapter marker {chapter_id} appears more than once")

        ext_chapter_ids = [item["id"] for item in external_parsed["chapters"]]
        ext_chapter_text = {item["id"]: item["text"] for item in external_parsed["chapters"]}
        ext_spans = {item["id"]: tuple(item["line_range"]) for item in external_parsed["chapters"]}

        # 3. Extra/unknown Chapters (in external, unknown to the recomposition).
        for chapter_id in ext_chapter_ids:
            ownership, target, confidence = self._determine_ownership("chapter", chapter_id, contract, known_chapters)
            if ownership == "structural":
                emit("structural_residual", ext_spans[chapter_id], (0, 0), chapter_id, chapter_id, confidence,
                     f"external manuscript contains a Chapter the accepted Book does not know: {chapter_id}")

        # 4. Missing Chapters (in the recomposition, absent from external).
        for chapter_id in recomposed_order:
            if chapter_id not in seen:
                emit("structural_residual", (0, 0), rec_chapter_span.get(chapter_id, (0, 0)),
                     chapter_id, chapter_id, "certain",
                     f"external manuscript is missing Chapter {chapter_id}")

        matched = [cid for cid in recomposed_order if seen.get(cid) == 1]
        ext_matched_order = [cid for cid in ext_chapter_ids if cid in set(matched)]
        sets_equal = set(matched) == set(ext_chapter_ids) and all(seen.get(c) == 1 for c in ext_chapter_ids)

        # 5. Chapter order (Book-owned) -- only meaningful when the Chapter sets
        #    agree; otherwise the missing/extra findings already explain it.
        order_changed = False
        if sets_equal and ext_matched_order != matched:
            order_changed = True
            emit("book_owned_residual", (1, external_lines), (1, recomposed_text.count("\n") + 1),
                 None, "order", "certain",
                 f"Chapter order differs: external {ext_matched_order} vs recomposed {matched}")

        # 6. Title (Book-owned).
        ext_title = self._external_title(external_text)
        rec_title = recomposed.get("title_rendering") or ""
        if (ext_title or "") == rec_title:
            emit("exact_match", (1, 1), (1, 1), None, "title", "certain", "title rendering identical")
        else:
            emit("book_owned_residual", (1, 1), (1, 1), None, "title", "certain",
                 f"title rendering differs: external {ext_title!r} vs recomposed {rec_title!r}")

        # 7. Separator (Book-owned).
        rec_separator = recomposed.get("separator", "---")
        ext_separators = external_parsed["separators"]
        expected_separators = max(len(matched) - 1, 0)
        sep_span = tuple(ext_separators[0]["line_range"]) if ext_separators else (0, 0)
        if len(ext_separators) != expected_separators or any(item["text"] != rec_separator for item in ext_separators):
            emit("book_owned_residual", sep_span, (0, 0), "separator", "separator", "certain",
                 "separator differs from recomposition")
        else:
            emit("exact_match", sep_span, (0, 0), "separator", "separator", "certain", "separator identical")

        # 8. Per-Chapter prose (Chapter-owned) for Chapters present in both exactly
        #    once. Cross-boundary movement (>1 Chapter changed with order unchanged)
        #    cannot be attributed to individual Chapters and is unresolved.
        chapter_diffs: list[tuple[str, tuple[int, int]]] = []
        for chapter_id in matched:
            if chapter_id not in ext_chapter_text:
                continue
            rec_text = self._chapter_prose(recomposed, chapter_id)
            if ext_chapter_text[chapter_id] == rec_text:
                emit("exact_match", ext_spans[chapter_id], rec_chapter_span.get(chapter_id, (0, 0)),
                     chapter_id, chapter_id, "certain", f"Chapter {chapter_id} prose identical")
            else:
                chapter_diffs.append((chapter_id, ext_spans[chapter_id]))

        if len(chapter_diffs) > 1 and not order_changed and sets_equal:
            spans = [span for _cid, span in chapter_diffs]
            lo = min(span[0] for span in spans)
            hi = max(span[1] for span in spans)
            emit("unresolved_residual", (lo, hi), (0, 0), None, "book", "ambiguous",
                 "multiple Chapters changed with order unchanged: content appears to have moved across Chapter boundaries")
        else:
            for chapter_id, span in chapter_diffs:
                emit("chapter_owned_residual", span, rec_chapter_span.get(chapter_id, (0, 0)),
                     chapter_id, chapter_id, "certain", f"Chapter {chapter_id} prose differs")

        # 9. Book-owned inserted material: each recomposition insertion must appear
        #    verbatim in the external manuscript.
        for insertion in recomposed.get("insertions", []):
            content = insertion.get("content")
            if content and content in external_text:
                emit("exact_match", (0, 0), (0, 0), "material", "material", "certain",
                     f"inserted material {insertion.get('target_id')} present")
            elif content:
                emit("book_owned_residual", (0, 0), (0, 0), "material", "material", "probable",
                     f"inserted material {insertion.get('target_id')} missing from external manuscript")

        return findings, counts

    def _chapter_prose(self, recomposed: dict[str, Any], chapter_id: str) -> str:
        """The accepted Chapter prose the recomposition renders for a Chapter."""
        book = BookExpressionStore(self.project)
        return book._chapter_text(book._accepted_chapter(chapter_id))

    def _store_comparison_report(self, report: dict[str, Any]) -> Path:
        """Persist the comparison report atomically (temp + replace).

        Stored under ``comparisons/``. Writing it accepts nothing, moves no pointer,
        and mutates no source. The write is atomic so a reader never observes a
        partially written report. The content is fully deterministic (no timestamp),
        so a repeated comparison over identical state overwrites with identical bytes.
        """
        path = self._comparison_path(report["comparison_id"])
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(".yaml.tmp")
        try:
            tmp.write_text(yaml.safe_dump(report, sort_keys=False), encoding="utf-8")
            tmp.replace(path)
        except Exception:
            if tmp.exists():
                tmp.unlink()
            raise
        return path

    def load_book_comparison(self, comparison_id: str) -> dict[str, Any]:
        """Load a stored Book comparison report."""
        path = self._comparison_path(comparison_id)
        if not path.exists():
            raise FileNotFoundError(f"Book comparison not found: {comparison_id}")
        return yaml.safe_load(path.read_text(encoding="utf-8")) or {}
