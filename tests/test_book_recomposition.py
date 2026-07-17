"""Phase C1: pointer-based Book recomposition.

Recomposition derives a noncanonical recomposed Book by assembling the current
accepted Chapter Expression pointers with the current accepted Book-owned source
pointers (Tier 3). The result is authority=derived, lifecycle=proposed,
role=reconciliation_recomposition, canonical=false. It is READ-ONLY over accepted
sources: it never moves the accepted Book pointer, never accepts a candidate,
never completes reconciliation, never treats decisions as narrative sources, and
never reads unpublished candidates.

These tests cover the core model, the freshness gate (stale Chapter, stale Book,
missing targets), deterministic source resolution, the 15 semantic scenarios, and
the 7 dogfood scenarios. Comparison, Book acceptance, and reconciliation
completion are explicitly OUT OF SCOPE and not implemented here.
"""

from __future__ import annotations

import hashlib
import re
from pathlib import Path

import pytest
import yaml

from auteur.canonical_story import CanonicalStoryBootstrap
from auteur.expression.book import BookExpressionStore
from auteur.expression.composition import ChapterExpressionStore
from auteur.expression.book_reconciliation import (
    BookReconciliationStore,
    RecompositionBlockedError,
)


# ----------------------------------------------------------------------------
# Fixtures / helpers (mirror tests/test_book_candidate_decisions.py)
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
    content = _book_md(project).read_text(encoding="utf-8")
    c2 = re.search(r"<!-- auteur:chapter id=chapter_02 expression_revision=1 -->.*?<!-- auteur:end-chapter id=chapter_02 -->", content, re.DOTALL).group(0)
    c1 = re.search(r"<!-- auteur:chapter id=chapter_01 expression_revision=1 -->.*?<!-- auteur:end-chapter id=chapter_01 -->", content, re.DOTALL).group(0)
    sep = re.search(r"<!-- auteur:book-separator id=separator_01 revision=1 -->.*?<!-- auteur:end-book-separator id=separator_01 -->", content, re.DOTALL).group(0)
    edited = project / "edited_reorder.md"
    edited.write_text("# The Lantern at Low Water\n\n" + c2 + "\n\n" + sep + "\n\n" + c1, encoding="utf-8")
    return edited


def _publish_separator(store: BookReconciliationStore, book_id: str, project: Path, sep: str = "***") -> tuple[dict, str]:
    inspection = store.inspect(_separator_edit(project, sep), book_id)
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


def _retyped_publish(store: BookReconciliationStore, book_id: str, project: Path, proposal_type: str, sep: str, *, clear_original: bool = False) -> tuple[dict, str]:
    """Publish a candidate whose proposal is retyped to ``proposal_type``.

    Inspection naturally produces only separator/order proposals, so title and
    inserted-material candidates are derived by retyping a separator proposal --
    the same technique the decision tests use for material candidates.
    """
    inspection = store.inspect(_separator_edit(project, sep), book_id)
    routed = store.route(inspection["inspection_id"])
    proposal_id = routed["book_proposals"][0]
    path = store._proposal_path(proposal_id)
    proposal = yaml.safe_load(path.read_text(encoding="utf-8"))
    proposal["proposal_type"] = proposal_type
    if clear_original:
        proposal["original"] = None
    path.write_text(yaml.safe_dump(proposal, sort_keys=False), encoding="utf-8")
    plan = store.plan(inspection["inspection_id"], [proposal_id])
    publication = store.publish(plan["plan_id"])
    return publication, publication["published_candidates"][0]


def _publish_title(store: BookReconciliationStore, book_id: str, project: Path) -> tuple[dict, str]:
    return _retyped_publish(store, book_id, project, "book_title_change_proposal", "TITLE-RENDER", clear_original=True)


def _publish_material(store: BookReconciliationStore, book_id: str, project: Path, sep: str = "+++") -> tuple[dict, str]:
    return _retyped_publish(store, book_id, project, "book_insertion_proposal", sep)


def _publish_all_kinds(store: BookReconciliationStore, book_id: str, project: Path) -> tuple[dict, list[str]]:
    """Publish separator + order + title + material candidates in ONE publication.

    A publication only owns the candidates it published, so a multi-source
    recomposition requires all four Book-owned kinds in a single plan. The four
    proposals are cloned from one inspection's proposal with distinct targets so
    the plan has no duplicate-target conflict; each maps to a distinct owned kind.
    """
    inspection = store.inspect(_separator_edit(project, "***"), book_id)
    routed = store.route(inspection["inspection_id"])
    base = yaml.safe_load(store._proposal_path(routed["book_proposals"][0]).read_text(encoding="utf-8"))
    base_id = base["proposal_id"]
    specs = [
        ("order", "book_order_change_proposal", "book_01", "chapter_01, chapter_02", "chapter_02, chapter_01"),
        ("separator", "book_separator_patch", "separator_01", "---", "***"),
        ("title", "book_title_change_proposal", "title_01", None, "TITLE-RENDER"),
        ("material", "book_insertion_proposal", "material_01", None, "+++material"),
    ]
    proposal_ids = []
    for tag, ptype, target, original, proposed in specs:
        clone = dict(base)
        clone["proposal_id"] = f"{base_id}_{tag}"
        clone["proposal_type"] = ptype
        clone["target"] = target
        clone["original"] = original
        clone["proposed"] = proposed
        store._proposal_path(clone["proposal_id"]).write_text(yaml.safe_dump(clone, sort_keys=False), encoding="utf-8")
        proposal_ids.append(clone["proposal_id"])
    plan = store.plan(inspection["inspection_id"], proposal_ids)
    publication = store.publish(plan["plan_id"])
    return publication, publication["published_candidates"]


def _canonical_snapshot(project: Path) -> dict[str, str]:
    """Hashes of every canonical/accepted artifact that recomposition must not move."""
    paths = {
        "book_accepted": project / "book" / "expression" / "accepted.yaml",
        "book_v001_yaml": project / "book" / "expression" / "book_v001.yaml",
        "book_v001_md": project / "book" / "expression" / "book_v001.md",
        "structure": project / "book" / "structure.yaml",
        "chapter_01_accepted": project / "chapters" / "01" / "expression" / "accepted.yaml",
        "chapter_02_accepted": project / "chapters" / "02" / "expression" / "accepted.yaml",
    }
    snap = {}
    for name, path in paths.items():
        if path.exists():
            snap[name] = hashlib.sha256(path.read_bytes()).hexdigest()
    return snap


def _pointer_files(project: Path) -> dict[str, str]:
    directory = project / "book" / "expression" / "reconciliation" / "accepted-sources" / "pointers"
    snap = {}
    if directory.exists():
        for path in sorted(directory.glob("*.yaml")):
            snap[path.name] = hashlib.sha256(path.read_bytes()).hexdigest()
    return snap


# ----------------------------------------------------------------------------
# Core model
# ----------------------------------------------------------------------------

def test_recomposition_produces_derived_artifact(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    publication, candidate_id = _publish_separator(store, book_id, project)
    store.decide_candidate(candidate_id, "approved", "approved")
    ok, recomposed = store.recompose_book_from_accepted_sources(publication["publication_id"])
    assert ok
    assert recomposed["authority"] == "derived"
    assert recomposed["lifecycle"] == "proposed"
    assert recomposed["role"] == "reconciliation_recomposition"
    assert recomposed["canonical"] is False
    assert recomposed["publication_id"] == publication["publication_id"]
    assert recomposed["inspection_id"] == publication["source_inspection_id"]
    assert "recomposed_at" in recomposed
    assert "source_pointers" in recomposed


def test_recomposition_uses_approved_separator_pointer(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    publication, candidate_id = _publish_separator(store, book_id, project, "***")
    store.decide_candidate(candidate_id, "approved", "approved")
    ok, recomposed = store.recompose_book_from_accepted_sources(publication["publication_id"])
    assert ok
    assert recomposed["separator"] == "***"
    assert recomposed["source_pointers"]["book_owned"]["separator_pointer_id"] is not None


def test_empty_pointer_set_reproduces_current_book(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    # Publish but do NOT approve: no pointer is created, so recomposition uses
    # the current accepted Book defaults (order + separator + title).
    publication, _candidate_id = _publish_separator(store, book_id, project, "***")
    ok, recomposed = store.recompose_book_from_accepted_sources(publication["publication_id"])
    assert ok
    assert recomposed["separator"] == "---"  # default, candidate NOT applied
    assert recomposed["title_rendering"] == "The Lantern at Low Water"
    assert recomposed["order"] == ["chapter_01", "chapter_02"]
    assert recomposed["source_pointers"]["book_owned"]["separator_pointer_id"] is None


def test_repeated_recomposition_is_deterministic(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    publication, candidate_id = _publish_separator(store, book_id, project)
    store.decide_candidate(candidate_id, "approved", "approved")
    _ok1, first = store.recompose_book_from_accepted_sources(publication["publication_id"])
    _ok2, second = store.recompose_book_from_accepted_sources(publication["publication_id"])
    assert first["content_hash"] == second["content_hash"]


def test_stored_artifact_readable_and_matches_return(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    publication, candidate_id = _publish_separator(store, book_id, project)
    store.decide_candidate(candidate_id, "approved", "approved")
    ok, recomposed = store.recompose_book_from_accepted_sources(publication["publication_id"])
    assert ok
    loaded = store.load_recomposed_book(publication["publication_id"])
    assert loaded["content_hash"] == recomposed["content_hash"]
    assert loaded["role"] == "reconciliation_recomposition"
    # Stored in recompositions/, NOT accepted-sources/.
    expected = project / "book" / "expression" / "reconciliation" / "recompositions" / f"{publication['publication_id']}_recomposed.yaml"
    assert expected.exists()


def test_recomposition_never_moves_accepted_book_pointer(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    publication, candidate_id = _publish_separator(store, book_id, project)
    store.decide_candidate(candidate_id, "approved", "approved")
    before_canonical = _canonical_snapshot(project)
    before_pointers = _pointer_files(project)
    ok, recomposed = store.recompose_book_from_accepted_sources(publication["publication_id"])
    assert ok
    assert recomposed["provenance"]["accepted_book_pointer_changed"] is False
    assert _canonical_snapshot(project) == before_canonical
    assert _pointer_files(project) == before_pointers


# ----------------------------------------------------------------------------
# Freshness validation
# ----------------------------------------------------------------------------

def test_stale_chapter_blocks(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    publication, candidate_id = _publish_separator(store, book_id, project)
    store.decide_candidate(candidate_id, "approved", "approved")
    # A Chapter is recomposed + accepted after approval: its content hash advances.
    cs = ChapterExpressionStore(project)
    cs.accept(cs.compose("chapter_01").artifact_id)
    ok, error = store.recompose_book_from_accepted_sources(publication["publication_id"])
    assert not ok
    assert isinstance(error, RecompositionBlockedError)
    assert error.status == "blocked_stale_chapter"
    assert error.reason == "STALE_CHAPTER"
    assert not store._recomposition_path(publication["publication_id"]).exists()


def test_stale_book_snapshot_blocks(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    publication, candidate_id = _publish_separator(store, book_id, project)
    _ok, decision = store.decide_candidate(candidate_id, "approved", "approved")
    # Simulate the owned source having been approved against an older Book
    # revision, while Chapters stay fresh: only the Book-snapshot check should fire.
    src_path = Path(decision["accepted_source_path"])
    src = yaml.safe_load(src_path.read_text(encoding="utf-8"))
    src["source_book_revision"] = 0
    src_path.write_text(yaml.safe_dump(src, sort_keys=False), encoding="utf-8")
    ok, error = store.recompose_book_from_accepted_sources(publication["publication_id"])
    assert not ok
    assert error.status == "blocked_stale_book"


def test_required_book_revision_mismatch_blocks(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    publication, candidate_id = _publish_separator(store, book_id, project)
    store.decide_candidate(candidate_id, "approved", "approved")
    ok, error = store.recompose_book_from_accepted_sources(publication["publication_id"], book_revision_required="999")
    assert not ok
    assert error.status == "blocked_stale_book"
    assert error.reason == "STALE_BOOK_REVISION"


def test_missing_chapter_pointer_target_blocks(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    publication, candidate_id = _publish_separator(store, book_id, project)
    store.decide_candidate(candidate_id, "approved", "approved")
    # Remove chapter_01's accepted Chapter Expression: its pointer target vanishes.
    accepted = project / "chapters" / "01" / "expression" / "accepted.yaml"
    accepted.unlink()
    ok, error = store.recompose_book_from_accepted_sources(publication["publication_id"])
    assert not ok
    assert error.status == "blocked_missing_target"
    assert error.reason == "MISSING_REVISION"


def test_missing_book_owned_pointer_target_blocks(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    publication, candidate_id = _publish_separator(store, book_id, project)
    _ok, decision = store.decide_candidate(candidate_id, "approved", "approved")
    # Delete the immutable accepted revision the pointer names.
    Path(decision["accepted_source_path"]).unlink()
    ok, error = store.recompose_book_from_accepted_sources(publication["publication_id"])
    assert not ok
    assert error.status == "blocked_missing_target"
    assert error.reason == "MISSING_REVISION"


def test_missing_publication_blocks(tmp_path: Path) -> None:
    project, _book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    ok, error = store.recompose_book_from_accepted_sources("book_publication_does_not_exist")
    assert not ok
    assert error.status == "blocked_missing_target"
    assert error.reason == "PUBLICATION_MISSING"


def test_block_error_carries_structured_details(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    publication, candidate_id = _publish_separator(store, book_id, project)
    store.decide_candidate(candidate_id, "approved", "approved")
    cs = ChapterExpressionStore(project)
    cs.accept(cs.compose("chapter_01").artifact_id)
    ok, error = store.recompose_book_from_accepted_sources(publication["publication_id"])
    assert not ok
    assert error.details["publication_id"] == publication["publication_id"]
    assert error.recommended_action
    for reason in error.result["reasons"]:
        assert "code" in reason and "recommended_action" in reason
    assert error.result["visible_outputs_created"] is False


# ----------------------------------------------------------------------------
# Source resolution
# ----------------------------------------------------------------------------

def test_order_pointer_reorders_chapters(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    publication, candidate_id = _publish_order(store, book_id, project)
    store.decide_candidate(candidate_id, "approved", "approved")
    ok, recomposed = store.recompose_book_from_accepted_sources(publication["publication_id"])
    assert ok
    assert recomposed["order"] == ["chapter_02", "chapter_01"]
    assert [c["chapter_id"] for c in recomposed["chapters"]] == ["chapter_02", "chapter_01"]
    assert recomposed["source_pointers"]["book_owned"]["order_pointer_id"] is not None


def test_title_pointer_applied(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    publication, candidate_id = _publish_title(store, book_id, project)
    store.decide_candidate(candidate_id, "approved", "approved")
    ok, recomposed = store.recompose_book_from_accepted_sources(publication["publication_id"])
    assert ok
    assert recomposed["title_rendering"] == "TITLE-RENDER"
    assert recomposed["source_pointers"]["book_owned"]["title_rendering_pointer_id"] is not None


def test_material_pointer_included(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    publication, candidate_id = _publish_material(store, book_id, project)
    store.decide_candidate(candidate_id, "approved", "approved")
    ok, recomposed = store.recompose_book_from_accepted_sources(publication["publication_id"])
    assert ok
    assert len(recomposed["insertions"]) == 1
    assert recomposed["source_pointers"]["book_owned"]["inserted_material_pointer_ids"]


def test_sources_resolved_independently(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    # Separator + order approved in one publication each; the recomposition of the
    # separator publication resolves only its own owned pointer, but the order
    # pointer (a different element) is global, so both apply to a recomposition of
    # a publication that owns both is covered in the mixed-sources scenario below.
    pub_sep, cand_sep = _publish_separator(store, book_id, project)
    store.decide_candidate(cand_sep, "approved", "sep")
    ok, recomposed = store.recompose_book_from_accepted_sources(pub_sep["publication_id"])
    assert ok
    assert recomposed["separator"] == "***"
    assert recomposed["order"] == ["chapter_01", "chapter_02"]  # no order pointer


# ----------------------------------------------------------------------------
# Scenarios 1-15
# ----------------------------------------------------------------------------

def test_scenario_1_no_book_owned_pointers(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    publication, _candidate_id = _publish_separator(store, book_id, project)
    ok, recomposed = store.recompose_book_from_accepted_sources(publication["publication_id"])
    assert ok
    assert recomposed["order"] == ["chapter_01", "chapter_02"]
    assert recomposed["separator"] == "---"


def test_scenario_2_accepted_separator_pointer(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    publication, candidate_id = _publish_separator(store, book_id, project, "###")
    store.decide_candidate(candidate_id, "approved", "approved")
    ok, recomposed = store.recompose_book_from_accepted_sources(publication["publication_id"])
    assert ok and recomposed["separator"] == "###"


def test_scenario_3_accepted_order_pointer(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    publication, candidate_id = _publish_order(store, book_id, project)
    store.decide_candidate(candidate_id, "approved", "approved")
    ok, recomposed = store.recompose_book_from_accepted_sources(publication["publication_id"])
    assert ok and recomposed["order"] == ["chapter_02", "chapter_01"]


def test_scenario_4_accepted_title_pointer(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    publication, candidate_id = _publish_title(store, book_id, project)
    store.decide_candidate(candidate_id, "approved", "approved")
    ok, recomposed = store.recompose_book_from_accepted_sources(publication["publication_id"])
    assert ok and recomposed["title_rendering"] == "TITLE-RENDER"


def test_scenario_5_accepted_material_pointer(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    publication, candidate_id = _publish_material(store, book_id, project)
    store.decide_candidate(candidate_id, "approved", "approved")
    ok, recomposed = store.recompose_book_from_accepted_sources(publication["publication_id"])
    assert ok and len(recomposed["insertions"]) == 1


def test_scenario_6_defer_after_approve_uses_v001(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    publication, candidate_id = _publish_separator(store, book_id, project, "***")
    store.decide_candidate(candidate_id, "approved", "approve")
    _ok, r1 = store.recompose_book_from_accepted_sources(publication["publication_id"])
    store.decide_candidate(candidate_id, "deferred", "on second thought, later")
    ok, r2 = store.recompose_book_from_accepted_sources(publication["publication_id"])
    # Defer does not move the pointer: the approved v001 separator still applies.
    assert ok
    assert r2["separator"] == "***"
    assert r1["content_hash"] == r2["content_hash"]


def test_scenario_7_reject_after_approve_uses_v001(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    publication, candidate_id = _publish_separator(store, book_id, project, "***")
    store.decide_candidate(candidate_id, "approved", "approve")
    _ok, r1 = store.recompose_book_from_accepted_sources(publication["publication_id"])
    store.decide_candidate(candidate_id, "rejected", "actually no")
    ok, r2 = store.recompose_book_from_accepted_sources(publication["publication_id"])
    # Reject does not move the pointer: the approved v001 separator still applies.
    assert ok
    assert r2["separator"] == "***"
    assert r1["content_hash"] == r2["content_hash"]


def test_scenario_8_new_approval_moves_pointer(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    publication, candidate_id = _publish_separator(store, book_id, project, "***")
    store.decide_candidate(candidate_id, "approved", "state A")
    ptr_before = store.current_accepted_source_pointer("separator_01", "separator")
    store.decide_candidate(candidate_id, "approved", "state B")
    ptr_after = store.current_accepted_source_pointer("separator_01", "separator")
    assert ptr_after["current_revision"] == ptr_before["current_revision"] + 1
    ok, recomposed = store.recompose_book_from_accepted_sources(publication["publication_id"])
    assert ok
    assert recomposed["source_pointers"]["book_owned"]["separator_pointer_id"] == ptr_after["pointer_id"]


def test_scenario_9_missing_target_fails(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    publication, candidate_id = _publish_separator(store, book_id, project)
    _ok, decision = store.decide_candidate(candidate_id, "approved", "approved")
    Path(decision["accepted_source_path"]).unlink()
    ok, error = store.recompose_book_from_accepted_sources(publication["publication_id"])
    assert not ok and error.reason == "MISSING_REVISION"


def test_scenario_10_stale_chapter_fails(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    publication, candidate_id = _publish_separator(store, book_id, project)
    store.decide_candidate(candidate_id, "approved", "approved")
    cs = ChapterExpressionStore(project)
    cs.accept(cs.compose("chapter_02").artifact_id)
    ok, error = store.recompose_book_from_accepted_sources(publication["publication_id"])
    assert not ok and error.status == "blocked_stale_chapter"


def test_scenario_11_stale_book_fails(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    publication, candidate_id = _publish_separator(store, book_id, project)
    ok, error = store.recompose_book_from_accepted_sources(publication["publication_id"], book_revision_required="2")
    assert not ok and error.status == "blocked_stale_book"


def test_scenario_12_mixed_book_owned_sources(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    publication, candidates = _publish_all_kinds(store, book_id, project)
    for candidate_id in candidates:
        store.decide_candidate(candidate_id, "approved", "approved")
    ok, recomposed = store.recompose_book_from_accepted_sources(publication["publication_id"])
    assert ok
    owned = recomposed["source_pointers"]["book_owned"]
    # Each element resolves independently within the one owning publication.
    assert owned["separator_pointer_id"] is not None
    assert owned["order_pointer_id"] is not None
    assert owned["title_rendering_pointer_id"] is not None
    assert owned["inserted_material_pointer_ids"]
    assert recomposed["separator"] == "***"
    assert recomposed["order"] == ["chapter_02", "chapter_01"]
    assert recomposed["title_rendering"] == "TITLE-RENDER"
    assert len(recomposed["insertions"]) == 1


def test_scenario_13_no_canonical_pointer_changes(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    publication, candidate_id = _publish_separator(store, book_id, project)
    store.decide_candidate(candidate_id, "approved", "approved")
    before = _canonical_snapshot(project)
    store.recompose_book_from_accepted_sources(publication["publication_id"])
    assert _canonical_snapshot(project) == before


def test_scenario_14_deterministic_repeats(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    publication, candidate_id = _publish_order(store, book_id, project)
    store.decide_candidate(candidate_id, "approved", "approved")
    hashes = {store.recompose_book_from_accepted_sources(publication["publication_id"])[1]["content_hash"] for _ in range(3)}
    assert len(hashes) == 1


def test_scenario_15_atomic_failure(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    publication, candidate_id = _publish_separator(store, book_id, project)
    store.decide_candidate(candidate_id, "approved", "approved")
    cs = ChapterExpressionStore(project)
    cs.accept(cs.compose("chapter_01").artifact_id)
    ok, _error = store.recompose_book_from_accepted_sources(publication["publication_id"])
    assert not ok
    # No partial artifact written on block.
    assert not store._recomposition_path(publication["publication_id"]).exists()


# ----------------------------------------------------------------------------
# Dogfood scenarios (7)
# ----------------------------------------------------------------------------

def test_dogfood_1_only_chapter_pointers(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    publication, _candidate_id = _publish_separator(store, book_id, project)
    ok, recomposed = store.recompose_book_from_accepted_sources(publication["publication_id"])
    assert ok and recomposed["order"] == ["chapter_01", "chapter_02"]


def test_dogfood_2_separator_approved(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    publication, candidate_id = _publish_separator(store, book_id, project, "~~~")
    store.decide_candidate(candidate_id, "approved", "approved")
    ok, recomposed = store.recompose_book_from_accepted_sources(publication["publication_id"])
    assert ok and recomposed["separator"] == "~~~"


def test_dogfood_3_order_approved(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    publication, candidate_id = _publish_order(store, book_id, project)
    store.decide_candidate(candidate_id, "approved", "approved")
    ok, recomposed = store.recompose_book_from_accepted_sources(publication["publication_id"])
    assert ok and recomposed["order"] == ["chapter_02", "chapter_01"]


def test_dogfood_4_title_approved(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    publication, candidate_id = _publish_title(store, book_id, project)
    store.decide_candidate(candidate_id, "approved", "approved")
    ok, recomposed = store.recompose_book_from_accepted_sources(publication["publication_id"])
    assert ok and recomposed["title_rendering"] == "TITLE-RENDER"


def test_dogfood_5_deferred_then_approve(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    publication, candidate_id = _publish_separator(store, book_id, project, "***")
    # First approval -> v001; recompose uses v001.
    store.decide_candidate(candidate_id, "approved", "v001")
    ptr1 = store.current_accepted_source_pointer("separator_01", "separator")
    _ok, first = store.recompose_book_from_accepted_sources(publication["publication_id"])
    assert first["source_pointers"]["book_owned"]["separator_pointer_id"] == ptr1["pointer_id"]
    assert ptr1["current_revision"] == 1
    # Second approval -> v002; recompose now uses v002.
    store.decide_candidate(candidate_id, "approved", "v002")
    ptr2 = store.current_accepted_source_pointer("separator_01", "separator")
    _ok, second = store.recompose_book_from_accepted_sources(publication["publication_id"])
    assert ptr2["current_revision"] == 2
    assert second["provenance"]["book_revision_at_approval"]  # snapshots recorded


def test_dogfood_6_book_changed_post_approval_blocked(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    publication, candidate_id = _publish_separator(store, book_id, project)
    store.decide_candidate(candidate_id, "approved", "approved")
    cs = ChapterExpressionStore(project)
    cs.accept(cs.compose("chapter_01").artifact_id)
    ok, error = store.recompose_book_from_accepted_sources(publication["publication_id"])
    assert not ok
    assert error.status in {"blocked_stale_chapter", "blocked_stale_book"}
    assert error.recommended_action


def test_dogfood_7_multiple_sources(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    publication, candidates = _publish_all_kinds(store, book_id, project)
    for candidate_id in candidates:
        store.decide_candidate(candidate_id, "approved", "approved")
    ok, recomposed = store.recompose_book_from_accepted_sources(publication["publication_id"])
    assert ok
    assert recomposed["separator"] == "***"
    assert recomposed["order"] == ["chapter_02", "chapter_01"]
    assert recomposed["title_rendering"] == "TITLE-RENDER"


# ----------------------------------------------------------------------------
# CLI integration
# ----------------------------------------------------------------------------

def test_cli_recompose_success(tmp_path: Path, capsys) -> None:
    from auteur.cli import main

    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    publication, candidate_id = _publish_separator(store, book_id, project, "***")
    store.decide_candidate(candidate_id, "approved", "approved")
    rc = main(["expression", "recompose-book-from-accepted", publication["publication_id"], "--project", str(project)])
    out = capsys.readouterr().out
    assert rc == 0
    assert "derived, noncanonical" in out
    assert "Accepted Book pointer changed: no" in out
    # Artifact was stored.
    assert store._recomposition_path(publication["publication_id"]).exists()


def test_cli_recompose_blocked_shows_structured_error(tmp_path: Path, capsys) -> None:
    from auteur.cli import main

    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    publication, candidate_id = _publish_separator(store, book_id, project)
    store.decide_candidate(candidate_id, "approved", "approved")
    cs = ChapterExpressionStore(project)
    cs.accept(cs.compose("chapter_01").artifact_id)
    rc = main(["expression", "recompose-book-from-accepted", publication["publication_id"], "--project", str(project)])
    out = capsys.readouterr().out
    assert rc == 1
    assert "blocked" in out.lower()
    assert "No recomposition artifact was created." in out


def test_cli_show_recomposition(tmp_path: Path, capsys) -> None:
    from auteur.cli import main

    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    publication, candidate_id = _publish_separator(store, book_id, project, "***")
    store.decide_candidate(candidate_id, "approved", "approved")
    store.recompose_book_from_accepted_sources(publication["publication_id"])
    rc = main(["expression", "show-book-recomposition", publication["publication_id"], "--project", str(project), "--json"])
    out = capsys.readouterr().out
    assert rc == 0
    assert "reconciliation_recomposition" in out
