"""Candidate Decisions (Decision Lifecycle) for published Book candidates.

Model A (nonterminal, append-only). An author approves, rejects, or defers each
published, unaccepted Book candidate. Deferring is nonterminal: a deferred
candidate can later be approved or rejected. Decisions are append-only; the
latest decision per candidate supersedes all priors and is the only one that
counts for recomposition. Approving a candidate materializes a durable accepted
Book-owned source (authority=accepted) that a future recomposition reads --
"approve" is a workflow decision, NOT narrative acceptance of a recomposed Book.

Deciding a candidate is NOT recomposition and NOT acceptance: no accepted Book
pointer, Chapter Expression, Structure, Identity, Blueprint, Realization, or
Scene is ever mutated, and no Book is recomposed. Recomposition (out of scope in
this slice) is blocked whenever the accepted Book changed after approval.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

import pytest
import yaml

from auteur.canonical_story import CanonicalStoryBootstrap
from auteur.expression.book import BookExpressionStore, BookPreviewNotAcceptableError
from auteur.expression.composition import ChapterExpressionStore
from auteur.expression.book_reconciliation import (
    BookReconciliationStore,
    CandidateNotFoundError,
)


# ----------------------------------------------------------------------------
# Fixtures / helpers (mirrors tests/test_book_reconciliation_application.py)
# ----------------------------------------------------------------------------

def _make_book(tmp_path: Path) -> tuple[Path, str]:
    bootstrap = CanonicalStoryBootstrap(Path("examples/canonical_story"))
    bootstrap.copy_to(tmp_path)
    bootstrap.accept_native_identity_and_structure(tmp_path)
    bootstrap.accept_scene_realizations(tmp_path)
    bootstrap.bootstrap_expressions(tmp_path)
    bootstrap.bootstrap_second_chapter(tmp_path)
    book = BookExpressionStore(tmp_path).compose(
        ["chapter_01", "chapter_02"], title="The Lantern at Low Water"
    )
    BookExpressionStore(tmp_path).accept(book["book_expression_id"])
    return tmp_path, book["book_expression_id"]


def _book_md(project: Path) -> Path:
    return project / "book" / "expression" / "book_v001.md"


def _separator_edit(project: Path, sep: str = "***") -> Path:
    original = _book_md(project).read_text(encoding="utf-8")
    tag = hashlib.sha256(sep.encode()).hexdigest()[:8]
    edited = project / f"edited_sep_{tag}.md"
    edited.write_text(original.replace("\n---\n", f"\n{sep}\n"), encoding="utf-8")
    return edited


def _reorder_edit(project: Path) -> Path:
    import re

    content = _book_md(project).read_text(encoding="utf-8")
    c2 = re.search(r"<!-- auteur:chapter id=chapter_02 expression_revision=1 -->.*?<!-- auteur:end-chapter id=chapter_02 -->", content, re.DOTALL).group(0)
    c1 = re.search(r"<!-- auteur:chapter id=chapter_01 expression_revision=1 -->.*?<!-- auteur:end-chapter id=chapter_01 -->", content, re.DOTALL).group(0)
    sep = re.search(r"<!-- auteur:book-separator id=separator_01 revision=1 -->.*?<!-- auteur:end-book-separator id=separator_01 -->", content, re.DOTALL).group(0)
    edited = project / "edited_reorder.md"
    edited.write_text("# The Lantern at Low Water\n\n" + c2 + "\n\n" + sep + "\n\n" + c1, encoding="utf-8")
    return edited


def _publish_separator(store: BookReconciliationStore, book_id: str, project: Path) -> tuple[dict, str]:
    inspection = store.inspect(_separator_edit(project), book_id)
    routed = store.route(inspection["inspection_id"])
    plan = store.plan(inspection["inspection_id"], [routed["book_proposals"][0]])
    publication = store.publish(plan["plan_id"])
    return publication, publication["published_candidates"][0]


def _publish_order(store: BookReconciliationStore, book_id: str, project: Path) -> tuple[dict, str]:
    inspection = store.inspect(_reorder_edit(project), book_id)
    routed = store.route(inspection["inspection_id"])
    plan = store.plan(inspection["inspection_id"], [routed["book_proposals"][0]])
    publication = store.publish(plan["plan_id"])
    return publication, publication["published_candidates"][0]


def _publish_material(store: BookReconciliationStore, book_id: str, project: Path) -> tuple[dict, str]:
    """Publish an inserted-material candidate.

    Derived from a separator inspection whose proposal is retyped to an inserted
    material proposal, which the plan supports and maps to a
    ``book_inserted_material_candidate``.
    """
    inspection = store.inspect(_separator_edit(project, "+++"), book_id)
    routed = store.route(inspection["inspection_id"])
    proposal_id = routed["book_proposals"][0]
    path = store._proposal_path(proposal_id)
    proposal = yaml.safe_load(path.read_text(encoding="utf-8"))
    proposal["proposal_type"] = "book_insertion_proposal"
    path.write_text(yaml.safe_dump(proposal, sort_keys=False), encoding="utf-8")
    plan = store.plan(inspection["inspection_id"], [proposal_id])
    publication = store.publish(plan["plan_id"])
    return publication, publication["published_candidates"][0]


def _preview_dict(project: Path, book_id: str) -> dict:
    return {
        "book_expression_id": f"{book_id}:application_preview",
        "authority": "derived",
        "lifecycle": "proposed",
        "role": "application_preview",
        "canonical": False,
    }


def _pointer_snapshot(project: Path) -> dict[str, str]:
    paths = {
        "book_accepted": project / "book" / "expression" / "accepted.yaml",
        "book_v001": project / "book" / "expression" / "book_v001.yaml",
        "structure": project / "book" / "structure.yaml",
        "chapter_01_accepted": project / "chapters" / "01" / "expression" / "accepted.yaml",
        "chapter_02_accepted": project / "chapters" / "02" / "expression" / "accepted.yaml",
        "story_identity": project / ".auteur" / "state" / "artifacts" / "story_identity.yaml",
        "blueprint": project / ".auteur" / "state" / "artifacts" / "blueprint.yaml",
    }
    snapshot = {}
    for name, path in paths.items():
        if path.exists():
            snapshot[name] = hashlib.sha256(path.read_bytes()).hexdigest()
    return snapshot


# ----------------------------------------------------------------------------
# 1. Preview acceptance blocking (metadata-based, not path-based)
# ----------------------------------------------------------------------------

def test_preview_cannot_be_accepted_metadata_validation(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    preview = _preview_dict(project, book_id)  # authority=derived
    with pytest.raises(BookPreviewNotAcceptableError) as excinfo:
        BookExpressionStore(project).accept(preview)
    assert "derived and proposed" in str(excinfo.value)


def test_preview_role_blocks_acceptance(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    # authority passes, but application_preview role blocks.
    artifact = {"authority": "accepted", "role": "application_preview", "lifecycle": "accepted"}
    with pytest.raises(BookPreviewNotAcceptableError):
        BookExpressionStore(project).accept(artifact)


def test_preview_lifecycle_proposed_blocks_acceptance(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    # authority and role pass, but proposed lifecycle blocks.
    artifact = {"authority": "accepted", "role": "book_manuscript", "lifecycle": "proposed"}
    with pytest.raises(BookPreviewNotAcceptableError):
        BookExpressionStore(project).accept(artifact)


# ----------------------------------------------------------------------------
# 2. Decision model (Model A: append-only, nonterminal defer)
# ----------------------------------------------------------------------------

def test_decision_id_deterministic(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    first = store._decision_id("cand_x", "approved", "reason text", 1)
    second = store._decision_id("cand_x", "approved", "reason text", 1)
    assert first == second
    _, candidate_id = _publish_separator(store, book_id, project)
    ok, decision = store.decide_candidate(candidate_id, "approved", "author approved")
    assert ok
    assert decision["decision_id"] == store._decision_id(candidate_id, "approved", "author approved", 1)


def test_multiple_decisions_allowed_append_only(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    _, candidate_id = _publish_separator(store, book_id, project)
    # A second decision with any status is now ALLOWED (Model A). No error.
    ok1, first = store.decide_candidate(candidate_id, "deferred", "think about it")
    ok2, second = store.decide_candidate(candidate_id, "approved", "ok, use it")
    assert ok1 and ok2
    assert first["decision_id"] != second["decision_id"]
    history = store._decision_history_for_candidate(candidate_id)
    assert [d["decision"]["status"] for d in history] == ["deferred", "approved"]
    assert [d["decision_sequence"] for d in history] == [1, 2]


def test_defer_is_nonterminal_then_approve(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    _, candidate_id = _publish_separator(store, book_id, project)
    store.decide_candidate(candidate_id, "deferred", "later")
    ok, decision = store.decide_candidate(candidate_id, "approved", "decided to keep")
    assert ok
    latest = store._latest_decision_for_candidate(candidate_id)
    assert latest["decision"]["status"] == "approved"
    assert latest["supersedes"] is not None


def test_latest_decision_supersedes_priors(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    _, candidate_id = _publish_separator(store, book_id, project)
    store.decide_candidate(candidate_id, "deferred", "d")
    store.decide_candidate(candidate_id, "approved", "a")
    _, third = store.decide_candidate(candidate_id, "rejected", "r")
    latest = store._latest_decision_for_candidate(candidate_id)
    assert latest["decision"]["status"] == "rejected"
    assert latest["decision_id"] == third["decision_id"]
    assert latest["decision_sequence"] == 3


def test_supersedes_pointer_chains_history(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    _, candidate_id = _publish_separator(store, book_id, project)
    _, first = store.decide_candidate(candidate_id, "deferred", "d")
    _, second = store.decide_candidate(candidate_id, "approved", "a")
    assert first["supersedes"] is None
    assert second["supersedes"] == first["decision_id"]


def test_decision_history_audit_trail_preserved(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    _, candidate_id = _publish_separator(store, book_id, project)
    store.decide_candidate(candidate_id, "deferred", "d")
    store.decide_candidate(candidate_id, "approved", "a")
    trail = store.book_candidate_decision_history(candidate_id)
    assert trail["active_status"] == "approved"
    assert len(trail["decisions"]) == 2  # full history preserved, never pruned
    assert [d["decision"]["status"] for d in trail["decisions"]] == ["deferred", "approved"]


def test_decision_preserves_candidate_hash(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    _, candidate_id = _publish_separator(store, book_id, project)
    candidate = store.load_book_candidate(candidate_id)
    expected = "sha256:" + hashlib.sha256(yaml.safe_dump(candidate, sort_keys=True).encode()).hexdigest()
    ok, decision = store.decide_candidate(candidate_id, "approved", "keep hash")
    assert ok
    assert decision["source_candidate_hash"] == expected
    assert decision["source_candidate_id"] == candidate_id


def test_decision_authority_is_decision(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    _, candidate_id = _publish_separator(store, book_id, project)
    ok, decision = store.decide_candidate(candidate_id, "approved", "r")
    assert ok
    assert decision["authority"] == "decision"
    assert decision["artifact_type"] == "book_candidate_decision"


def test_decision_lifecycle_is_decided(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    _, candidate_id = _publish_separator(store, book_id, project)
    ok, decision = store.decide_candidate(candidate_id, "deferred", "r")
    assert ok
    assert decision["lifecycle"] == "decided"
    assert decision["decision"]["status"] == "deferred"


# ----------------------------------------------------------------------------
# 3. Accepted Book-owned sources (materialized on approval)
# ----------------------------------------------------------------------------

def test_approval_creates_accepted_source_separator(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    _, candidate_id = _publish_separator(store, book_id, project)
    ok, decision = store.decide_candidate(candidate_id, "approved", "approved")
    assert ok
    assert "accepted_source_id" in decision
    source = store.load_accepted_book_owned_source(decision["accepted_source_id"])
    assert source["authority"] == "accepted"
    assert source["lifecycle"] == "accepted"
    assert source["owned_kind"] == "separator"
    assert source["source_decision_id"] == decision["decision_id"]
    assert source["source_candidate_id"] == candidate_id


def test_accepted_source_kind_for_order(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    _, candidate_id = _publish_order(store, book_id, project)
    ok, decision = store.decide_candidate(candidate_id, "approved", "approved")
    assert ok
    source = store.load_accepted_book_owned_source(decision["accepted_source_id"])
    assert source["owned_kind"] == "order"


def test_reject_and_defer_create_no_accepted_source(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    _, candidate_id = _publish_separator(store, book_id, project)
    _, rejected = store.decide_candidate(candidate_id, "rejected", "no")
    assert "accepted_source_id" not in rejected
    _, deferred = store.decide_candidate(candidate_id, "deferred", "later")
    assert "accepted_source_id" not in deferred


def test_active_accepted_sources_reflect_latest_decision(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    publication, candidate_id = _publish_separator(store, book_id, project)
    store.decide_candidate(candidate_id, "approved", "a")
    assert len(store.active_accepted_sources(publication["publication_id"])) == 1
    # Superseding the approval with a rejection deactivates the accepted source.
    store.decide_candidate(candidate_id, "rejected", "changed my mind")
    assert store.active_accepted_sources(publication["publication_id"]) == []


def test_reapproval_bumps_accepted_source_revision(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    _, candidate_id = _publish_separator(store, book_id, project)
    _, first = store.decide_candidate(candidate_id, "approved", "a1")
    _, second = store.decide_candidate(candidate_id, "approved", "a2")
    r1 = store.load_accepted_book_owned_source(first["accepted_source_id"])
    r2 = store.load_accepted_book_owned_source(second["accepted_source_id"])
    assert r1["revision"] == 1
    assert r2["revision"] == 2


# ----------------------------------------------------------------------------
# 4. Freshness validation at decision time
# ----------------------------------------------------------------------------

def test_decide_stale_book_revision_rejected(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    _, candidate_id = _publish_separator(store, book_id, project)
    cs = ChapterExpressionStore(project)
    cs.accept(cs.compose("chapter_01").artifact_id)
    ok, result = store.decide_candidate(candidate_id, "approved", "r")
    assert ok is False
    assert result["status"] == "rejected_stale"
    assert any(reason["code"] == "BOOK_OR_CHAPTER_REVISION_CHANGED" for reason in result["reasons"])


def test_decide_stale_candidate_source_changed_rejected(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    _, candidate_id = _publish_separator(store, book_id, project)
    path = store.root / "candidates" / f"{candidate_id}.yaml"
    candidate = yaml.safe_load(path.read_text(encoding="utf-8"))
    candidate["source_book_hash"] = "sha256:not_the_real_hash"
    path.write_text(yaml.safe_dump(candidate, sort_keys=False), encoding="utf-8")
    ok, result = store.decide_candidate(candidate_id, "approved", "r")
    assert ok is False
    assert any(reason["code"] == "BOOK_HASH_CHANGED" for reason in result["reasons"])


def test_decide_stale_plan_changed_rejected(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    _, candidate_id = _publish_separator(store, book_id, project)
    candidate = store.load_book_candidate(candidate_id)
    plan_path = store._plan_path(candidate["source_plan_id"])
    plan = yaml.safe_load(plan_path.read_text(encoding="utf-8"))
    plan["transformation"] = {"id": "expression.publish_book_application", "version": 9}
    plan_path.write_text(yaml.safe_dump(plan, sort_keys=False), encoding="utf-8")
    ok, result = store.decide_candidate(candidate_id, "approved", "r")
    assert ok is False
    assert any(reason["code"] == "PLAN_CHANGED" for reason in result["reasons"])


def test_decide_stale_inspection_changed_rejected(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    _, candidate_id = _publish_separator(store, book_id, project)
    candidate = store.load_book_candidate(candidate_id)
    inspection_path = store._inspection_path(candidate["source_inspection_id"])
    report = yaml.safe_load(inspection_path.read_text(encoding="utf-8"))
    report["provenance"]["transformation"] = {"id": "expression.inspect_book_manuscript", "version": 9}
    inspection_path.write_text(yaml.safe_dump(report, sort_keys=False), encoding="utf-8")
    ok, result = store.decide_candidate(candidate_id, "approved", "r")
    assert ok is False
    assert any(reason["code"] == "INSPECTION_CHANGED" for reason in result["reasons"])


def test_decide_stale_structured_response(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    _, candidate_id = _publish_separator(store, book_id, project)
    cs = ChapterExpressionStore(project)
    cs.accept(cs.compose("chapter_02").artifact_id)
    ok, result = store.decide_candidate(candidate_id, "approved", "r")
    assert ok is False
    assert result["status"] == "rejected_stale"
    assert result["visible_outputs_created"] is False
    assert result["reasons"]
    for reason in result["reasons"]:
        assert set(reason) >= {"code", "expected", "current", "recommended_action"}
    # No decision record was written.
    assert store._latest_decision_for_candidate(candidate_id) is None


# ----------------------------------------------------------------------------
# 5. Decision API
# ----------------------------------------------------------------------------

def test_decide_separator_approved(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    _, candidate_id = _publish_separator(store, book_id, project)
    ok, decision = store.decide_candidate(candidate_id, "approved", "Author approved separator")
    assert ok
    assert decision["decision"]["status"] == "approved"
    assert decision["decision"]["reason"] == "Author approved separator"


def test_decide_order_rejected(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    _, candidate_id = _publish_order(store, book_id, project)
    ok, decision = store.decide_candidate(candidate_id, "rejected", "Reorder creates confusion")
    assert ok
    assert decision["decision"]["status"] == "rejected"


def test_decide_material_deferred(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    _, candidate_id = _publish_material(store, book_id, project)
    ok, decision = store.decide_candidate(candidate_id, "deferred", "Needs author review")
    assert ok
    assert decision["decision"]["status"] == "deferred"
    assert decision["candidate_type"] == "book_inserted_material_candidate"


def test_decide_invalid_status_rejected(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    _, candidate_id = _publish_separator(store, book_id, project)
    # "accepted" is intentionally NOT a candidate-decision status (reserved for
    # Book acceptance); only approved/rejected/deferred are valid here.
    with pytest.raises(ValueError):
        store.decide_candidate(candidate_id, "accepted", "r")
    with pytest.raises(ValueError):
        store.decide_candidate(candidate_id, "maybe", "r")


def test_decide_no_candidate_rejected(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    with pytest.raises(CandidateNotFoundError):
        store.decide_candidate("book_candidate_does_not_exist", "approved", "r")


def test_decide_unknown_reason_approved(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    _, candidate_id = _publish_separator(store, book_id, project)
    ok, decision = store.decide_candidate(candidate_id, "approved", "any free-form reason 42 ~!@")
    assert ok
    assert decision["decision"]["reason"] == "any free-form reason 42 ~!@"


# ----------------------------------------------------------------------------
# 6. Preview regeneration (decision-aware, latest wins)
# ----------------------------------------------------------------------------

def test_preview_regenerated_after_separator_approved(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    publication, candidate_id = _publish_separator(store, book_id, project)
    ok, _ = store.decide_candidate(candidate_id, "approved", "approved")
    assert ok
    preview = store.load_book_preview(publication["publication_id"])
    assert preview["decision_aware"] is True
    # The approved separator candidate is the source the preview draws on.
    assert [s["candidate_id"] for s in preview["candidate_sources"]] == [candidate_id]
    assert any(d["candidate_id"] == candidate_id and d["status"] == "approved" for d in preview["applied_decisions"])


def test_preview_regenerated_after_order_approved(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    publication, candidate_id = _publish_order(store, book_id, project)
    ok, _ = store.decide_candidate(candidate_id, "approved", "approved")
    assert ok
    preview = store.load_book_preview(publication["publication_id"])
    assert preview["decision_aware"] is True
    assert [s["chapter_id"] for s in preview["accepted_chapter_sources"]] == ["chapter_02", "chapter_01"]


def test_preview_excludes_rejected_candidates(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    publication, candidate_id = _publish_separator(store, book_id, project)
    ok, _ = store.decide_candidate(candidate_id, "rejected", "no")
    assert ok
    preview = store.load_book_preview(publication["publication_id"])
    assert preview["candidate_sources"] == []
    assert preview["applied_proposals"] == []
    assert any(d["candidate_id"] == candidate_id and d["status"] == "rejected" for d in preview["applied_decisions"])


def test_preview_excludes_deferred_candidates(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    publication, candidate_id = _publish_separator(store, book_id, project)
    ok, _ = store.decide_candidate(candidate_id, "deferred", "later")
    assert ok
    preview = store.load_book_preview(publication["publication_id"])
    assert preview["candidate_sources"] == []
    assert any(d["candidate_id"] == candidate_id and d["status"] == "deferred" for d in preview["applied_decisions"])


def test_preview_reflects_superseding_defer_then_approve(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    publication, candidate_id = _publish_separator(store, book_id, project)
    store.decide_candidate(candidate_id, "deferred", "later")
    # After deferral the preview excludes the candidate...
    preview = store.load_book_preview(publication["publication_id"])
    assert preview["candidate_sources"] == []
    # ...then approving supersedes the deferral and the preview includes it.
    store.decide_candidate(candidate_id, "approved", "changed my mind")
    preview = store.load_book_preview(publication["publication_id"])
    assert [s["candidate_id"] for s in preview["candidate_sources"]] == [candidate_id]
    assert any(d["candidate_id"] == candidate_id and d["status"] == "approved" for d in preview["applied_decisions"])


def test_preview_freshness_current_after_decision(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    publication, candidate_id = _publish_separator(store, book_id, project)
    ok, _ = store.decide_candidate(candidate_id, "approved", "approved")
    assert ok
    preview = store.load_book_preview(publication["publication_id"])
    assert preview["freshness"]["status"] == "fresh"
    # Still derived / proposed / noncanonical -- never accepted.
    assert preview["authority"] == "derived"
    assert preview["lifecycle"] == "proposed"
    assert preview["canonical"] is False


# ----------------------------------------------------------------------------
# 7. Recomposition freshness (Book-change gate; recomposition itself out of scope)
# ----------------------------------------------------------------------------

def test_recomposition_ready_when_book_unchanged(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    publication, candidate_id = _publish_separator(store, book_id, project)
    store.decide_candidate(candidate_id, "approved", "approved")
    result = store.assess_recomposition_freshness(publication["publication_id"])
    assert result["status"] == "ready"
    assert result["active_approvals"] == 1


def test_recomposition_blocked_when_book_changed_after_approval(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    publication, candidate_id = _publish_separator(store, book_id, project)
    store.decide_candidate(candidate_id, "approved", "approved")
    # Book changes after approval (a Chapter is recomposed and accepted).
    cs = ChapterExpressionStore(project)
    cs.accept(cs.compose("chapter_01").artifact_id)
    result = store.assess_recomposition_freshness(publication["publication_id"])
    assert result["status"] == "blocked_stale_book"
    assert result["visible_outputs_created"] is False
    assert any(r["code"] in {"BOOK_OR_CHAPTER_REVISION_CHANGED", "BOOK_REVISION_CHANGED", "BOOK_HASH_CHANGED"} for r in result["reasons"])
    for reason in result["reasons"]:
        assert set(reason) >= {"code", "expected", "current", "recommended_action"}


def test_recomposition_ready_when_only_rejected(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    publication, candidate_id = _publish_separator(store, book_id, project)
    store.decide_candidate(candidate_id, "rejected", "no")
    # No active approvals => nothing to block, even if the Book later changes.
    cs = ChapterExpressionStore(project)
    cs.accept(cs.compose("chapter_01").artifact_id)
    result = store.assess_recomposition_freshness(publication["publication_id"])
    assert result["status"] == "ready"
    assert result["active_approvals"] == 0


# ----------------------------------------------------------------------------
# 8. Dogfood scenarios (A/B/C)
# ----------------------------------------------------------------------------

def test_dogfood_scenario_a_defer_then_approve(tmp_path: Path) -> None:
    """A: defer -> approve the same candidate (nonterminal two-step workflow)."""
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    before = _pointer_snapshot(project)
    publication, candidate_id = _publish_separator(store, book_id, project)
    ok, deferred = store.decide_candidate(candidate_id, "deferred", "I'll think about this")
    assert ok and deferred["decision"]["status"] == "deferred"
    # Nonterminal: the same candidate can be decided again.
    ok, approved = store.decide_candidate(candidate_id, "approved", "OK, I'll use it")
    assert ok and approved["decision"]["status"] == "approved"
    assert approved["supersedes"] == deferred["decision_id"]
    # Active state advanced pending -> deferred -> approved; preview uses it now.
    preview = store.load_book_preview(publication["publication_id"])
    assert [s["candidate_id"] for s in preview["candidate_sources"]] == [candidate_id]
    # Approval materialized an accepted Book-owned source; pointers untouched.
    assert "accepted_source_id" in approved
    assert _pointer_snapshot(project) == before


def test_dogfood_scenario_b_approve_then_book_change_blocks_recomposition(tmp_path: Path) -> None:
    """B: approve -> Book changes -> recomposition blocked."""
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    publication, candidate_id = _publish_separator(store, book_id, project)
    ok, _ = store.decide_candidate(candidate_id, "approved", "Author approved separator")
    assert ok
    assert store.assess_recomposition_freshness(publication["publication_id"])["status"] == "ready"
    # The accepted Book advances after the decision.
    cs = ChapterExpressionStore(project)
    cs.accept(cs.compose("chapter_02").artifact_id)
    result = store.assess_recomposition_freshness(publication["publication_id"])
    assert result["status"] == "blocked_stale_book"
    assert "Re-approve" in result["reasons"][0]["recommended_action"] or any(
        "Re-approve" in r["recommended_action"] for r in result["reasons"]
    )


def test_dogfood_scenario_c_multiple_approvals_latest_wins(tmp_path: Path) -> None:
    """C: multiple approvals of the same candidate; latest decision wins."""
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    before = _pointer_snapshot(project)
    publication, candidate_id = _publish_separator(store, book_id, project)
    _, first = store.decide_candidate(candidate_id, "approved", "first pass")
    _, second = store.decide_candidate(candidate_id, "approved", "second, better reason")
    latest = store._latest_decision_for_candidate(candidate_id)
    assert latest["decision_id"] == second["decision_id"]
    assert latest["decision"]["reason"] == "second, better reason"
    # Full history preserved; only one accepted source is active (the latest).
    assert len(store._decision_history_for_candidate(candidate_id)) == 2
    active = store.active_accepted_sources(publication["publication_id"])
    assert len(active) == 1
    assert active[0]["source_decision_id"] == second["decision_id"]
    assert _pointer_snapshot(project) == before


# ----------------------------------------------------------------------------
# 9. Authority / mutation invariants
# ----------------------------------------------------------------------------

def test_decide_no_book_pointer_change(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    _, candidate_id = _publish_separator(store, book_id, project)
    accepted = project / "book" / "expression" / "accepted.yaml"
    before = accepted.read_bytes()
    store.decide_candidate(candidate_id, "approved", "r")
    assert accepted.read_bytes() == before


def test_decide_no_structure_mutation(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    _, candidate_id = _publish_order(store, book_id, project)
    structure = project / "book" / "structure.yaml"
    before = structure.read_bytes()
    store.decide_candidate(candidate_id, "approved", "r")
    assert structure.read_bytes() == before


def test_decide_no_chapter_mutation(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    _, candidate_id = _publish_separator(store, book_id, project)
    accepted = {
        "chapter_01": project / "chapters" / "01" / "expression" / "accepted.yaml",
        "chapter_02": project / "chapters" / "02" / "expression" / "accepted.yaml",
    }
    before = {name: path.read_bytes() for name, path in accepted.items() if path.exists()}
    store.decide_candidate(candidate_id, "approved", "r")
    after = {name: path.read_bytes() for name, path in accepted.items() if path.exists()}
    assert after == before
