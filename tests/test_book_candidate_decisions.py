"""Candidate Decisions (Decision Lifecycle) for published Book candidates.

Covers explicit metadata-based preview-acceptance blocking, the immutable
candidate decision model (accept/reject/defer), the live freshness gate run at
decision time, and decision-aware preview regeneration. Deciding a candidate is
NOT recomposition and NOT acceptance: no accepted Book pointer, Chapter
Expression, Structure, Identity, Blueprint, Realization, or Scene is ever
mutated, and no Book is recomposed.
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
    DuplicateDecisionError,
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
# 2. Decision model
# ----------------------------------------------------------------------------

def test_decision_id_deterministic(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    first = store._decision_id("cand_x", "accepted", "reason text")
    second = store._decision_id("cand_x", "accepted", "reason text")
    assert first == second
    _, candidate_id = _publish_separator(store, book_id, project)
    ok, decision = store.decide_candidate(candidate_id, "accepted", "author approved")
    assert ok
    assert decision["decision_id"] == store._decision_id(candidate_id, "accepted", "author approved")


def test_decision_immutable_no_duplicate(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    _, candidate_id = _publish_separator(store, book_id, project)
    ok, _ = store.decide_candidate(candidate_id, "accepted", "first")
    assert ok
    # A second decision with any status is rejected: decisions are terminal.
    with pytest.raises(DuplicateDecisionError):
        store.decide_candidate(candidate_id, "rejected", "second")


def test_decision_preserves_candidate_hash(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    _, candidate_id = _publish_separator(store, book_id, project)
    candidate = store.load_book_candidate(candidate_id)
    expected = "sha256:" + hashlib.sha256(yaml.safe_dump(candidate, sort_keys=True).encode()).hexdigest()
    ok, decision = store.decide_candidate(candidate_id, "accepted", "keep hash")
    assert ok
    assert decision["source_candidate_hash"] == expected
    assert decision["source_candidate_id"] == candidate_id


def test_decision_authority_is_decision(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    _, candidate_id = _publish_separator(store, book_id, project)
    ok, decision = store.decide_candidate(candidate_id, "accepted", "r")
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
# 3. Freshness validation at decision time
# ----------------------------------------------------------------------------

def test_decide_stale_book_revision_rejected(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    _, candidate_id = _publish_separator(store, book_id, project)
    cs = ChapterExpressionStore(project)
    cs.accept(cs.compose("chapter_01").artifact_id)
    ok, result = store.decide_candidate(candidate_id, "accepted", "r")
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
    ok, result = store.decide_candidate(candidate_id, "accepted", "r")
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
    ok, result = store.decide_candidate(candidate_id, "accepted", "r")
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
    ok, result = store.decide_candidate(candidate_id, "accepted", "r")
    assert ok is False
    assert any(reason["code"] == "INSPECTION_CHANGED" for reason in result["reasons"])


def test_decide_stale_structured_response(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    _, candidate_id = _publish_separator(store, book_id, project)
    cs = ChapterExpressionStore(project)
    cs.accept(cs.compose("chapter_02").artifact_id)
    ok, result = store.decide_candidate(candidate_id, "accepted", "r")
    assert ok is False
    assert result["status"] == "rejected_stale"
    assert result["visible_outputs_created"] is False
    assert result["reasons"]
    for reason in result["reasons"]:
        assert set(reason) >= {"code", "expected", "current", "recommended_action"}
    # No decision record was written.
    assert store._decision_for_candidate(candidate_id) is None


# ----------------------------------------------------------------------------
# 4. Decision API
# ----------------------------------------------------------------------------

def test_decide_separator_accepted(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    _, candidate_id = _publish_separator(store, book_id, project)
    ok, decision = store.decide_candidate(candidate_id, "accepted", "Author approved separator")
    assert ok
    assert decision["decision"]["status"] == "accepted"
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
    with pytest.raises(ValueError):
        store.decide_candidate(candidate_id, "maybe", "r")


def test_decide_no_candidate_rejected(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    with pytest.raises(CandidateNotFoundError):
        store.decide_candidate("book_candidate_does_not_exist", "accepted", "r")


def test_decide_unknown_reason_accepted(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    _, candidate_id = _publish_separator(store, book_id, project)
    ok, decision = store.decide_candidate(candidate_id, "accepted", "any free-form reason 42 ~!@")
    assert ok
    assert decision["decision"]["reason"] == "any free-form reason 42 ~!@"


# ----------------------------------------------------------------------------
# 5. Preview regeneration (decision-aware)
# ----------------------------------------------------------------------------

def test_preview_regenerated_after_separator_accepted(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    publication, candidate_id = _publish_separator(store, book_id, project)
    ok, _ = store.decide_candidate(candidate_id, "accepted", "approved")
    assert ok
    preview = store.load_book_preview(publication["publication_id"])
    assert preview["decision_aware"] is True
    # The accepted separator candidate is the source the preview draws on.
    assert [s["candidate_id"] for s in preview["candidate_sources"]] == [candidate_id]
    assert any(d["candidate_id"] == candidate_id and d["status"] == "accepted" for d in preview["applied_decisions"])


def test_preview_regenerated_after_order_accepted(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    publication, candidate_id = _publish_order(store, book_id, project)
    ok, _ = store.decide_candidate(candidate_id, "accepted", "approved")
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


def test_preview_freshness_current_after_decision(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    publication, candidate_id = _publish_separator(store, book_id, project)
    ok, _ = store.decide_candidate(candidate_id, "accepted", "approved")
    assert ok
    preview = store.load_book_preview(publication["publication_id"])
    assert preview["freshness"]["status"] == "fresh"
    # Still derived / proposed / noncanonical -- never accepted.
    assert preview["authority"] == "derived"
    assert preview["lifecycle"] == "proposed"
    assert preview["canonical"] is False


# ----------------------------------------------------------------------------
# 6. Dogfood scenarios (A/B/C)
# ----------------------------------------------------------------------------

def test_dogfood_scenario_a_separator_accepted(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    before = _pointer_snapshot(project)
    publication, candidate_id = _publish_separator(store, book_id, project)
    ok, decision = store.decide_candidate(candidate_id, "accepted", "Author approved separator")
    assert ok and decision["decision"]["status"] == "accepted"
    # Decision immutable: re-deciding is refused.
    with pytest.raises(DuplicateDecisionError):
        store.decide_candidate(candidate_id, "accepted", "again")
    # Preview now uses the accepted separator candidate.
    preview = store.load_book_preview(publication["publication_id"])
    assert [s["candidate_id"] for s in preview["candidate_sources"]] == [candidate_id]
    # Book pointer unchanged.
    assert _pointer_snapshot(project) == before


def test_dogfood_scenario_b_order_rejected(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    structure_before = (project / "book" / "structure.yaml").read_bytes()
    publication, candidate_id = _publish_order(store, book_id, project)
    ok, decision = store.decide_candidate(candidate_id, "rejected", "Reorder creates confusion")
    assert ok and decision["decision"]["status"] == "rejected"
    # Book order remains the previous accepted order; the rejected candidate is
    # excluded from the regenerated preview.
    preview = store.load_book_preview(publication["publication_id"])
    assert [s["chapter_id"] for s in preview["accepted_chapter_sources"]] == ["chapter_01", "chapter_02"]
    assert preview["candidate_sources"] == []
    # No Book Structure mutation.
    assert (project / "book" / "structure.yaml").read_bytes() == structure_before


def test_dogfood_scenario_c_material_deferred(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    before = _pointer_snapshot(project)
    publication, candidate_id = _publish_material(store, book_id, project)
    ok, decision = store.decide_candidate(candidate_id, "deferred", "Needs author review with external copy")
    assert ok and decision["decision"]["status"] == "deferred"
    # Deferred candidate is not included in the preview.
    preview = store.load_book_preview(publication["publication_id"])
    assert preview["candidate_sources"] == []
    # Book pointer unchanged.
    assert _pointer_snapshot(project) == before


# ----------------------------------------------------------------------------
# 7. Authority / mutation invariants
# ----------------------------------------------------------------------------

def test_decide_no_book_pointer_change(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    _, candidate_id = _publish_separator(store, book_id, project)
    accepted = project / "book" / "expression" / "accepted.yaml"
    before = accepted.read_bytes()
    store.decide_candidate(candidate_id, "accepted", "r")
    assert accepted.read_bytes() == before


def test_decide_no_structure_mutation(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    _, candidate_id = _publish_order(store, book_id, project)
    structure = project / "book" / "structure.yaml"
    before = structure.read_bytes()
    store.decide_candidate(candidate_id, "accepted", "r")
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
    store.decide_candidate(candidate_id, "accepted", "r")
    after = {name: path.read_bytes() for name, path in accepted.items() if path.exists()}
    assert after == before
