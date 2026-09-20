"""Read-only Phase C3 Book acceptance validation.

This module extracts the existing 20-point acceptance gate from
`BookReconciliationStore` without moving any authority-bearing behavior.
It validates contemporary repository state and returns the same structured
ready/block result; staging, publication, pointer movement, rollback, and
acceptance semantics remain owned by the reconciliation facade.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable


class BookAcceptanceValidator:
    """Evaluate whether a recomposed Book is still eligible for acceptance."""

    def __init__(
        self,
        store: Any,
        *,
        error_type: type[Exception],
        comparison_transformation: dict[str, Any],
        supported_comparison_versions: set[int],
        supported_marker_versions: set[int],
        hash_text: Callable[[str], str],
        book_store_cls: type[Any],
    ) -> None:
        self._store = store
        self._error_type = error_type
        self._comparison_transformation = comparison_transformation
        self._supported_comparison_versions = supported_comparison_versions
        self._supported_marker_versions = supported_marker_versions
        self._hash_text = hash_text
        self._book_store_cls = book_store_cls

    def validate(
        self, comparison_id: str
    ) -> tuple[bool, dict[str, Any] | Exception]:
        store = self._store
        """Run the 20-point acceptance gate; block atomically on the first failure.

        Revalidates EVERY condition from disk and never trusts the persisted
        ``ready_for_acceptance`` flag. Returns ``(True, context)`` -- a context dict
        carrying every value acceptance needs to stage artifacts -- when ready, or
        ``(False, self._error_type)`` on the first failed check. No artifact is
        ever written by this method.
        """
        def block(status: str, reason: str, recommended_action: str, **details: Any) -> self._error_type:
            return self._error_type(status, reason, {"comparison_id": comparison_id, **details}, recommended_action)

        # 1. Comparison exists on disk.
        try:
            comparison = store.load_book_comparison(comparison_id)
        except FileNotFoundError:
            return False, block("MISSING_COMPARISON", "MISSING_COMPARISON",
                                "run compare-book-recomposition to produce the comparison, then accept")

        # 2. Comparison is derived.
        if comparison.get("authority") != "derived":
            return False, block("STALE_COMPARISON", "COMPARISON_NOT_DERIVED",
                                "re-run the comparison; only a derived comparison can be accepted",
                                expected="derived", current=comparison.get("authority"))
        # 3. Comparison is evaluated.
        if comparison.get("lifecycle") != "evaluated":
            return False, block("STALE_COMPARISON", "COMPARISON_NOT_EVALUATED",
                                "re-run the comparison; only an evaluated comparison can be accepted",
                                expected="evaluated", current=comparison.get("lifecycle"))
        # 4. Comparison transformation version is supported.
        transformation = comparison.get("transformation", {}) or {}
        if transformation.get("id") != self._comparison_transformation["id"] or transformation.get("version") not in self._supported_comparison_versions:
            return False, block("STALE_COMPARISON", "COMPARISON_TRANSFORMATION_UNSUPPORTED",
                                "re-run the comparison under a supported transformation contract",
                                expected=self._comparison_transformation, current=transformation)
        # 5. Comparison content hash is valid (matches stored content).
        recomputed_comparison_id = store._recompute_comparison_id(comparison)
        if recomputed_comparison_id != comparison.get("comparison_id"):
            return False, block("STALE_COMPARISON", "COMPARISON_TAMPERED",
                                "re-run the comparison; its stored content no longer matches its id",
                                expected=comparison.get("comparison_id"), current=recomputed_comparison_id)

        recomposition_id = comparison.get("source_recomposition_id")
        publication_id = comparison.get("source_publication_id")

        # 6. Source recomposition exists on disk.
        try:
            recomposed = store.load_recomposed_book(publication_id)
        except FileNotFoundError:
            return False, block("MISSING_RECOMPOSITION", "MISSING_RECOMPOSITION",
                                "run recompose-book-from-accepted, then compare and accept",
                                recomposition_id=recomposition_id)
        if recomposed.get("recomposition_id") != recomposition_id:
            return False, block("STALE_RECOMPOSITION", "RECOMPOSITION_ID_MISMATCH",
                                "recompose and compare again; the stored recomposition differs from the comparison source",
                                expected=recomposition_id, current=recomposed.get("recomposition_id"))

        # 7. Recomposition content hash is valid (matches stored content).
        recomputed_recomposition_hash = store._recomposition_content_hash(store._recomposition_body_view(recomposed))
        if recomputed_recomposition_hash != recomposed.get("content_hash"):
            return False, block("STALE_RECOMPOSITION", "RECOMPOSITION_TAMPERED",
                                "recompose the Book from accepted sources, then compare and accept",
                                expected=recomposed.get("content_hash"), current=recomputed_recomposition_hash)

        # 8. Recomposition freshness gate passes (Phase C1).
        ready_c1, gate_c1 = store._validate_recomposition_freshness(publication_id, None)
        if not ready_c1:
            b = gate_c1.result
            return False, block("STALE_RECOMPOSITION", b.get("reasons", [{}])[0].get("code", "RECOMPOSITION_STALE"),
                                b.get("reasons", [{}])[0].get("recommended_action", "recompose from fresh accepted sources, then compare and accept"),
                                phase="C1", propagated_status=b.get("status"), reasons=b.get("reasons", []))

        # 9. Comparison freshness gate passes (Phase C2). Revalidates recomposition
        #    tamper, live pointer drift, and Book-revision match against the current
        #    accepted sources.
        ready_c2, gate_c2 = store._validate_comparison_freshness(recomposition_id, publication_id)
        if not ready_c2:
            b = gate_c2.result
            return False, block("STALE_COMPARISON", b.get("reasons", [{}])[0].get("code", "COMPARISON_STALE"),
                                b.get("reasons", [{}])[0].get("recommended_action", "recompose and compare again, then accept"),
                                phase="C2", propagated_status=b.get("status"), reasons=b.get("reasons", []))

        # 10. External manuscript still exists at the comparison path.
        external = comparison.get("external_manuscript", {}) or {}
        external_path = Path(external["path"]) if external.get("path") else None
        if external_path is None or not external_path.exists():
            return False, block("MISSING_MANUSCRIPT", "MISSING_MANUSCRIPT",
                                "restore the external manuscript at the comparison path, then compare and accept",
                                path=str(external_path) if external_path else None)
        # 11. External manuscript hash still matches the comparison snapshot.
        external_text = external_path.read_text(encoding="utf-8")
        external_hash = self._hash_text(external_text)
        if external_hash != external.get("content_hash"):
            return False, block("STALE_MANUSCRIPT", "MANUSCRIPT_HASH_CHANGED",
                                "the external manuscript changed since comparison; compare again, then accept",
                                expected=external.get("content_hash"), current=external_hash)

        # Live accepted Book metadata for pointer/source checks.
        book = self._book_store_cls(store.project)
        source_book_expression = recomposed.get("source_book_expression")
        try:
            metadata = book.inspect(source_book_expression)["metadata"]
        except FileNotFoundError:
            return False, block("STALE_BOOK_POINTER", "BOOK_MISSING",
                                "restore the accepted Book, then compare and accept",
                                expected=source_book_expression, current=None)
        book_id = metadata.get("book_id")
        current_book_hash = self._hash_text(store._book_source_text(book, metadata))

        # 12. Accepted Book revision and pointer have not moved (same as comparison source).
        if str(metadata.get("revision")) != str(comparison.get("source_book_revision")):
            return False, block("STALE_BOOK_POINTER", "BOOK_REVISION_CHANGED",
                                "the accepted Book advanced since comparison; recompose and compare again",
                                expected=comparison.get("source_book_revision"), current=metadata.get("revision"))
        if current_book_hash != comparison.get("source_book_hash"):
            return False, block("STALE_BOOK_POINTER", "BOOK_HASH_CHANGED",
                                "the accepted Book content changed since comparison; recompose and compare again",
                                expected=comparison.get("source_book_hash"), current=current_book_hash)

        by_id = {item["chapter_id"]: item for item in metadata["chapters"]}

        # 13. Every accepted Chapter pointer unchanged (same id, same revision).
        # 14. Every accepted Chapter target exists and hash matches (not deleted/modified).
        accepted_chapter_sources: list[dict[str, Any]] = []
        for source in comparison.get("chapter_sources", []):
            chapter_id = source.get("chapter_id")
            reference = by_id.get(chapter_id)
            if reference is None:
                return False, block("STALE_BOOK_POINTER", "CHAPTER_POINTER_MOVED",
                                    "a Chapter left the accepted Book since comparison; recompose and compare again",
                                    chapter_id=chapter_id)
            if str(reference.get("accepted_revision")) != str(source.get("revision")) or reference.get("chapter_expression_id") != source.get("accepted_expression_id"):
                return False, block("STALE_BOOK_POINTER", "CHAPTER_POINTER_MOVED",
                                    "a Chapter pointer moved since comparison; recompose and compare again",
                                    chapter_id=chapter_id, expected=source.get("revision"), current=reference.get("accepted_revision"))
            try:
                live_chapter = book._accepted_chapter(chapter_id)
            except ValueError:
                return False, block("STALE_CHAPTER", "MISSING_CHAPTER_TARGET",
                                    "restore the accepted Chapter Expression, then recompose and compare again",
                                    chapter_id=chapter_id)
            if live_chapter.get("content_hash") != source.get("content_hash"):
                return False, block("STALE_CHAPTER", "CHAPTER_TARGET_CHANGED",
                                    "an accepted Chapter changed since comparison; recompose and compare again",
                                    chapter_id=chapter_id, expected=source.get("content_hash"), current=live_chapter.get("content_hash"))
            accepted_chapter_sources.append({
                "chapter_id": chapter_id,
                "expression_id": reference.get("chapter_expression_id"),
                "revision": reference.get("accepted_revision"),
                "content_hash": reference.get("content_hash"),
                "pointer_id": reference.get("chapter_expression_id"),
            })

        # 15. Every Book-owned pointer unchanged (same id, same revision).
        # 16. Every Book-owned accepted revision exists and hash matches.
        accepted_book_owned_sources: list[dict[str, Any]] = []
        for source in comparison.get("book_owned_sources", []):
            pointer_id = source.get("pointer_id")
            accepted_revision_id = source.get("accepted_revision_id")
            pointer = store._load_pointer_by_id(pointer_id) if pointer_id else None
            if pointer is None:
                return False, block("STALE_BOOK_POINTER", "BOOK_OWNED_POINTER_MOVED",
                                    "a Book-owned pointer is missing since comparison; recompose and compare again",
                                    pointer_id=pointer_id)
            if pointer.get("current_accepted_source_id") != accepted_revision_id:
                return False, block("STALE_BOOK_POINTER", "BOOK_OWNED_POINTER_MOVED",
                                    "a Book-owned pointer moved since comparison; recompose and compare again",
                                    pointer_id=pointer_id, expected=accepted_revision_id, current=pointer.get("current_accepted_source_id"))
            try:
                accepted_revision = store.load_accepted_book_owned_source(accepted_revision_id)
            except FileNotFoundError:
                return False, block("STALE_BOOK_POINTER", "MISSING_BOOK_OWNED_TARGET",
                                    "restore the accepted Book-owned revision, then recompose and compare again",
                                    accepted_revision_id=accepted_revision_id)
            live_owned_hash = self._hash_text(accepted_revision.get("proposed") or "")
            if live_owned_hash != source.get("content_hash"):
                return False, block("STALE_BOOK_POINTER", "BOOK_OWNED_TARGET_CHANGED",
                                    "a Book-owned accepted revision changed since comparison; recompose and compare again",
                                    accepted_revision_id=accepted_revision_id, expected=source.get("content_hash"), current=live_owned_hash)
            accepted_book_owned_sources.append({
                "owned_kind": accepted_revision.get("owned_kind"),
                "target_id": accepted_revision.get("target_id"),
                "pointer_id": pointer_id,
                "accepted_revision_id": accepted_revision_id,
                "revision": accepted_revision.get("revision"),
                "content_hash": source.get("content_hash"),
            })

        # 17. Marker contract version remains supported.
        marker_version = external.get("marker_contract_version")
        if marker_version not in self._supported_marker_versions:
            return False, block("MARKER_CONTRACT_UNSUPPORTED", "MARKER_CONTRACT_UNSUPPORTED",
                                "re-inspect and compare under a supported marker contract, then accept",
                                expected=sorted(self._supported_marker_versions), current=marker_version)

        summary = comparison.get("summary", {}) or {}
        counts = summary.get("residual_counts", {}) or {}

        # 18. exact_match is true (not false, not null). Revalidated from counts.
        exact_match = counts.get("exact_match", 0) > 0 and sum(counts.values()) == counts.get("exact_match", 0)
        if summary.get("exact_match") is not True or not exact_match:
            return False, block("NON_EXACT_MATCH", "NON_EXACT_MATCH",
                                "only an exact-match comparison can be accepted; resolve differences first",
                                exact_match=summary.get("exact_match"), residual_counts=counts)

        # 19. Every residual count is zero (do NOT trust ready_for_acceptance flag).
        remaining = {category: counts.get(category, 0) for category in store._residual_categories() if counts.get(category, 0)}
        if remaining:
            return False, block("RESIDUALS_REMAIN", "RESIDUALS_REMAIN",
                                "resolve every residual (including Book-owned) before acceptance",
                                residuals=remaining)

        # 20. No previous acceptance exists for this comparison (no duplicate).
        if store._find_prior_acceptance(comparison_id) is not None:
            return False, block("DUPLICATE_ACCEPTANCE", "DUPLICATE_ACCEPTANCE",
                                "this comparison was already accepted; inspect the prior acceptance")

        # Pointer baseline + revision numbering. The new revision is based on the
        # current accepted Book pointer (Phase C3), NOT the recomposition's stored
        # revision alone. On first acceptance the baseline is the compose-time
        # accepted Book revision (the comparison source).
        pointer = store._load_accepted_book_pointer()
        if pointer is not None:
            baseline_revision = int(pointer["current_revision"])
            previous_accepted_book = {
                "expression_id": pointer.get("accepted_book_expression_id"),
                "revision": pointer.get("current_revision"),
                "content_hash": pointer.get("content_hash"),
            }
            expected_previous_pointer_id = pointer.get("pointer_id")
        else:
            baseline_revision = int(comparison.get("source_book_revision"))
            previous_accepted_book = {
                "expression_id": source_book_expression,
                "revision": comparison.get("source_book_revision"),
                "content_hash": comparison.get("source_book_hash"),
            }
            expected_previous_pointer_id = None
        new_revision = baseline_revision + 1

        content = store._render_recomposition_text(recomposed)
        content_hash = self._hash_text(content)
        source_comparison_hash = self._hash_text(yaml.safe_dump(comparison, sort_keys=True))
        accepted_book_expression_id = f"{book_id}:accepted_v{new_revision:03d}"
        acceptance_id = "book_acceptance_" + hashlib.sha256(
            (
                comparison_id + "\0" + str(recomposed.get("content_hash")) + "\0"
                + str(new_revision) + "\0" + str(previous_accepted_book.get("content_hash"))
            ).encode("utf-8")
        ).hexdigest()[:32]
        new_pointer_id = "accepted_book_pointer_" + hashlib.sha256(
            (accepted_book_expression_id + "\0" + str(new_revision) + "\0" + acceptance_id).encode("utf-8")
        ).hexdigest()[:16]

        context = {
            "comparison": comparison,
            "comparison_id": comparison_id,
            "source_comparison_hash": source_comparison_hash,
            "recomposed": recomposed,
            "recomposition_id": recomposition_id,
            "source_recomposition_hash": recomposed.get("content_hash"),
            "publication_id": publication_id,
            "metadata": metadata,
            "book_id": book_id,
            "source_book_expression": source_book_expression,
            "content": content,
            "content_hash": content_hash,
            "new_revision": new_revision,
            "accepted_book_expression_id": accepted_book_expression_id,
            "acceptance_id": acceptance_id,
            "new_pointer_id": new_pointer_id,
            "expected_previous_pointer_id": expected_previous_pointer_id,
            "previous_accepted_book": previous_accepted_book,
            "accepted_chapter_sources": accepted_chapter_sources,
            "accepted_book_owned_sources": accepted_book_owned_sources,
        }
        return True, context

