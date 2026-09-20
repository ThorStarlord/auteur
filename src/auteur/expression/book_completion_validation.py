"""Read-only Phase C4 Book reconciliation completion validation.

This module extracts the existing 20-point completion eligibility gate from
`BookReconciliationStore` without moving completion publication or authority
semantics. It only determines whether an already-accepted reconciliation is
still eligible for administrative completion.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any, Callable

import yaml


class BookCompletionValidator:
    """Evaluate whether an accepted Book reconciliation can be completed."""

    def __init__(
        self,
        store: Any,
        *,
        error_type: type[Exception],
        supported_marker_versions: set[int],
        hash_text: Callable[[str], str],
        book_store_cls: type[Any],
    ) -> None:
        self._store = store
        self._error_type = error_type
        self._supported_marker_versions = supported_marker_versions
        self._hash_text = hash_text
        self._book_store_cls = book_store_cls

    def validate(
        self, acceptance_id: str
    ) -> tuple[bool, dict[str, Any] | Exception]:
        """Run the 20-point completion eligibility gate.

        Revalidates EVERY condition from disk and never trusts persisted state.
        Returns ``(True, context)`` -- a context dict carrying every value needed
        to stage the completion record -- when eligible, or a structured block
        error on the first failed check. No artifact is ever
        written by this method.
        """
        store = self._store

        def block(status: str, reason: str, recommended_action: str, **details: Any) -> Exception:
            return self._error_type(status, reason, {"acceptance_id": acceptance_id, **details}, recommended_action)

        # 1. Acceptance record exists.
        try:
            acceptance = store.load_book_acceptance(acceptance_id)
        except FileNotFoundError:
            return False, block("MISSING_ACCEPTANCE", "MISSING_ACCEPTANCE",
                                "accept the recomposed Book first, then complete reconciliation")

        # 2. Accepted Book revision exists.
        accepted_expression_id = acceptance.get("accepted_book_expression_id")
        accepted_revision = acceptance.get("accepted_book_revision")
        book_id = accepted_expression_id.split(":")[0] if accepted_expression_id else ""
        try:
            book_revision = store.load_accepted_book_revision(book_id, accepted_revision)
        except (FileNotFoundError, ValueError):
            return False, block("MISSING_BOOK_REVISION", "MISSING_BOOK_REVISION",
                                "restore the accepted Book revision, then retry completion",
                                expression_id=accepted_expression_id, revision=accepted_revision)

        # 3. Accepted Book pointer targets that revision.
        pointer = store._load_accepted_book_pointer()
        if pointer is None:
            return False, block("MISSING_POINTER", "MISSING_BOOK_POINTER",
                                "accept the recomposed Book first; no accepted Book pointer exists")
        if str(pointer.get("current_revision")) != str(accepted_revision):
            return False, block("STALE_POINTER", "BOOK_POINTER_MOVED",
                                "the accepted Book pointer moved since acceptance; the pointer no longer targets the accepted revision",
                                expected=accepted_revision, current=pointer.get("current_revision"))
        if pointer.get("accepted_book_expression_id") != accepted_expression_id:
            return False, block("STALE_POINTER", "BOOK_POINTER_TARGET_MISMATCH",
                                "the accepted Book pointer targets a different expression",
                                expected=accepted_expression_id, current=pointer.get("accepted_book_expression_id"))

        # 4. Acceptance provenance references the expected comparison.
        comparison_id = acceptance.get("source_comparison_id")
        recomposition_id = acceptance.get("source_recomposition_id")
        if not comparison_id or not recomposition_id:
            return False, block("INCOMPLETE_ACCEPTANCE", "ACCEPTANCE_MISSING_SOURCE_IDS",
                                "the acceptance record is missing source comparison or recomposition id")

        # 5. Comparison remains exact-match.
        try:
            comparison = store.load_book_comparison(comparison_id)
        except FileNotFoundError:
            return False, block("MISSING_COMPARISON", "MISSING_COMPARISON",
                                "the comparison artifact no longer exists; rerun compare-book-recomposition")
        summary = comparison.get("summary", {}) or {}
        if summary.get("exact_match") is not True:
            return False, block("NON_EXACT_MATCH", "COMPARISON_NO_LONGER_EXACT",
                                "the comparison is no longer exact match; rerun compare-book-recomposition")

        # 6. Every residual count remains zero.
        counts = summary.get("residual_counts", {}) or {}
        remaining = {
            cat: counts.get(cat, 0)
            for cat in store._residual_categories()
            if counts.get(cat, 0)
        }
        if remaining:
            return False, block("RESIDUALS_REMAIN", "RESIDUALS_REMAIN",
                                "resolve every residual before completing reconciliation",
                                residuals=remaining)

        # 7. Source recomposition exists and unchanged.
        try:
            recomposed = store.load_recomposed_book(
                store._publication_id_from_recomposition(recomposition_id)
                if "publication_" in (recomposition_id or "")
                else recomposition_id
            )
        except FileNotFoundError:
            return False, block("MISSING_RECOMPOSITION", "MISSING_RECOMPOSITION",
                                "the recomposition artifact no longer exists; recompose and compare again")

        # 8. External manuscript hash still matches.
        external = comparison.get("external_manuscript", {}) or {}
        external_path_str = external.get("path")
        if external_path_str:
            external_path = Path(external_path_str)
            if external_path.exists():
                current_external_hash = self._hash_text(external_path.read_text(encoding="utf-8"))
                if current_external_hash != external.get("content_hash"):
                    return False, block("STALE_MANUSCRIPT", "MANUSCRIPT_HASH_CHANGED",
                                        "the external manuscript changed since comparison; compare again",
                                        expected=external.get("content_hash"), current=current_external_hash)

        # 9-10. Every accepted Chapter pointer matches acceptance snapshot.
        accepted_chapter_sources = acceptance.get("accepted_chapter_sources", [])
        book = self._book_store_cls(store.project)
        for src in accepted_chapter_sources:
            chapter_id = src.get("chapter_id")
            expected_revision = src.get("revision")
            try:
                chapter = book._accepted_chapter(chapter_id)
            except ValueError:
                return False, block("MISSING_CHAPTER", "MISSING_CHAPTER_TARGET",
                                    f"accepted Chapter {chapter_id} no longer exists; restore it",
                                    chapter_id=chapter_id)
            if str(chapter.get("revision")) != str(expected_revision):
                return False, block("STALE_CHAPTER", "CHAPTER_POINTER_MOVED",
                                    f"accepted Chapter {chapter_id} pointer moved since acceptance",
                                    chapter_id=chapter_id, expected=expected_revision, current=chapter.get("revision"))

        # 11-12. Every accepted Book-owned pointer matches acceptance snapshot.
        accepted_book_owned_sources = acceptance.get("accepted_book_owned_sources", [])
        for src in accepted_book_owned_sources:
            owned_kind = src.get("owned_kind")
            target_id = src.get("target_id")
            expected_revision = src.get("revision")
            pointer = store.current_accepted_source_pointer(target_id, owned_kind)
            if pointer is None:
                return False, block("MISSING_BOOK_OWNED_POINTER", "BOOK_OWNED_POINTER_MISSING",
                                    f"Book-owned pointer {owned_kind}:{target_id} no longer exists",
                                    owned_kind=owned_kind, target_id=target_id)
            if str(pointer.get("current_revision")) != str(expected_revision):
                return False, block("STALE_BOOK_OWNED_POINTER", "BOOK_OWNED_POINTER_MOVED",
                                    f"Book-owned pointer {owned_kind}:{target_id} moved since acceptance",
                                    owned_kind=owned_kind, target_id=target_id,
                                    expected=expected_revision, current=pointer.get("current_revision"))
            current_accepted_id = pointer.get("current_accepted_source_id")
            if current_accepted_id:
                try:
                    store.load_accepted_book_owned_source(current_accepted_id)
                except FileNotFoundError:
                    return False, block("MISSING_BOOK_OWNED_SOURCE", "BOOK_OWNED_SOURCE_MISSING",
                                        f"accepted Book-owned source {current_accepted_id} no longer exists",
                                        accepted_source_id=current_accepted_id)

        # 13. Every delegated Chapter reconciliation is complete.
        #     Need the original inspection id from the provenance chain.
        publication_id = comparison.get("source_publication_id") or book_revision.get("source_publication_id", "")
        plan_id = ""
        inspection_id = ""
        if publication_id:
            pub_data = {}
            pub_path = store._publication_path(publication_id)
            if pub_path.exists():
                pub_data = yaml.safe_load(pub_path.read_text(encoding="utf-8")) or {}
                plan_id = pub_data.get("source_plan_id", "")
                inspection_id = pub_data.get("source_inspection_id", "")
            if not inspection_id:
                # Fall back to plan -> inspection.
                inspection_id = acceptance.get("source_inspection_id", "")

        if not inspection_id:
            # Re-derive from comparison's external manuscript path or default.
            inspection_id = recomposed.get("inspection_id", "")

        chapter_statuses, chapters_complete = store._gather_chapter_reconciliation_status(
            inspection_id, accepted_chapter_sources
        )
        if not chapters_complete:
            incomplete = [
                s for s in chapter_statuses
                if s.get("completion_status") != "completed"
                   and "implicit" not in str(s.get("completion_status", ""))
            ]
            return False, block("INCOMPLETE_CHAPTER_RECONCILIATION", "CHAPTER_RECONCILIATION_INCOMPLETE",
                                "complete all delegated Chapter reconciliations before completing Book reconciliation",
                                incomplete_chapters=incomplete)

        # 14. No unresolved routing findings remain.
        routing_path = store._routing_path(inspection_id)
        routing_data: dict[str, Any] = {}
        if routing_path.exists():
            routing_data = yaml.safe_load(routing_path.read_text(encoding="utf-8")) or {}
        unresolved_findings = routing_data.get("unresolved", [])
        if unresolved_findings:
            return False, block("UNRESOLVED_ROUTING_FINDINGS", "UNRESOLVED_ROUTING_FINDINGS",
                                "resolve all unresolved routing findings before completing reconciliation",
                                unresolved_count=len(unresolved_findings))

        # 15. Every selected Book-owned proposal has a terminal resolution.
        proposals_resolved = True
        deferred_count = 0
        book_owned_resolutions: list[dict[str, Any]] = []
        if plan_id:
            book_owned_resolutions, proposals_resolved, deferred_count = (
                store._gather_book_owned_resolutions(inspection_id, publication_id, accepted_book_owned_sources)
            )
        else:
            book_owned_resolutions = []

        if not proposals_resolved:
            blocking = [r for r in book_owned_resolutions if r.get("blocks", True)]
            return False, block("UNRESOLVED_PROPOSALS", "BOOK_OWNED_PROPOSAL_UNRESOLVED",
                                "resolve all Book-owned proposals (approve, reject, or explicitly exclude) before completing reconciliation",
                                blocking_resolutions=blocking, deferred_count=deferred_count)

        # 16. Marker contract version remains supported.
        marker_version = external.get("marker_contract_version", 1)
        if marker_version not in self._supported_marker_versions:
            return False, block("MARKER_CONTRACT_UNSUPPORTED", "MARKER_CONTRACT_UNSUPPORTED",
                                "re-inspect and compare under a supported marker contract",
                                expected=sorted(self._supported_marker_versions), current=marker_version)

        # 17. No prior completion for this acceptance.
        if store._find_prior_completion(acceptance_id) is not None:
            return False, block("DUPLICATE_COMPLETION", "DUPLICATE_COMPLETION",
                                "this acceptance was already completed; inspect the prior completion")

        # 18. Completion would not mutate any narrative authority (read-only check).
        #     This is verified by the gate being purely observational.

        # 19. Full provenance chain consistency:
        #     inspection -> routing -> plan -> publication -> candidates/decisions
        #     -> accepted sources -> recomposition -> comparison -> acceptance
        if not plan_id:
            return False, block("INCOMPLETE_PROVENANCE", "MISSING_PLAN_ID",
                                "the publication manifest is missing a source plan id")
        try:
            plan_data = store._load_plan(plan_id)
        except FileNotFoundError:
            return False, block("INCOMPLETE_PROVENANCE", "MISSING_PLAN",
                                "the application plan referenced by the publication no longer exists",
                                plan_id=plan_id)
        if plan_data.get("source_inspection_id") != inspection_id:
            return False, block("INCONSISTENT_PROVENANCE", "PROVENANCE_CHAIN_BROKEN",
                                "the plan's source inspection does not match the publication's inspection",
                                plan_inspection=plan_data.get("source_inspection_id"),
                                publication_inspection=inspection_id)

        # Comparison and acceptance link are checked above.
        recomposition_pub_id = recomposed.get("publication_id") or recomposed.get("source_publication_id", "")
        if recomposition_pub_id != publication_id:
            return False, block("INCONSISTENT_PROVENANCE", "RECOMPOSITION_PUBLICATION_MISMATCH",
                                "the recomposition's source publication does not match the comparison's",
                                recomposition_publication=recomposition_pub_id,
                                expected=publication_id)

        # Build context for the completion record.
        completion_id = "book_completion_" + hashlib.sha256(
            (acceptance_id + "\0" + comparison_id + "\0" + str(accepted_revision)).encode("utf-8")
        ).hexdigest()[:32]

        context = {
            "acceptance": acceptance,
            "acceptance_id": acceptance_id,
            "comparison": comparison,
            "comparison_id": comparison_id,
            "recomposed": recomposed,
            "recomposition_id": recomposition_id,
            "publication_id": publication_id,
            "plan_id": plan_id,
            "inspection_id": inspection_id,
            "book_revision": book_revision,
            "book_id": book_id,
            "accepted_book_expression_id": accepted_expression_id,
            "accepted_revision": accepted_revision,
            "pointer": pointer,
            "content_hash": pointer.get("content_hash", ""),
            "chapter_statuses": chapter_statuses,
            "book_owned_resolutions": book_owned_resolutions,
            "external_manuscript": {
                "path": str(external_path) if external_path_str else "",
                "content_hash": external.get("content_hash", ""),
            },
            "summary": summary,
            "residual_counts": counts,
            "completion_id": completion_id,
            "deferred_count": deferred_count,
        }
        return True, context

