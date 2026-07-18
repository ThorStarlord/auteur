"""Phase B: Book-owned proposal planning and atomic publication.

Covers the derived application plan, the durable/unaccepted/noncanonical
candidate model, the noncanonical preview, the live freshness gate, the
all-or-nothing publication transaction, the publication manifest, and duplicate
and stale handling. Publication is NOT acceptance: no accepted Book pointer,
Chapter Expression, Structure, Identity, Blueprint, Realization, or Scene is
ever mutated.
"""

from __future__ import annotations

import hashlib
import re
import shutil
from pathlib import Path
from unittest import mock

import pytest
import yaml

from auteur.canonical_story import CanonicalStoryBootstrap
from auteur.expression.book import BookExpressionStore
from auteur.expression.composition import ChapterExpressionStore
from auteur.expression.book_reconciliation import (
    BookPublicationRejected,
    BookReconciliationStore,
)


# ----------------------------------------------------------------------------
# Fixtures / helpers
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
    # The separator glyph itself is unsafe in a Windows filename, so hash it.
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


def _separator_proposal(store: BookReconciliationStore, book_id: str, project: Path, sep: str = "***") -> tuple[str, str]:
    inspection = store.inspect(_separator_edit(project, sep), book_id)
    routed = store.route(inspection["inspection_id"])
    return inspection["inspection_id"], routed["book_proposals"][0]


def _order_proposal(store: BookReconciliationStore, book_id: str, project: Path) -> tuple[str, str]:
    inspection = store.inspect(_reorder_edit(project), book_id)
    routed = store.route(inspection["inspection_id"])
    return inspection["inspection_id"], routed["book_proposals"][0]


def _pointer_snapshot(project: Path) -> dict[str, str]:
    """Content hashes of every canonical/accepted pointer that must not move."""
    paths = {
        "book_accepted": project / "book" / "expression" / "accepted.yaml",
        "book_v001": project / "book" / "expression" / "book_v001.yaml",
        "structure": project / "book" / "structure.yaml",
        "chapter_01_accepted": project / "chapters" / "01" / "expression" / "accepted.yaml",
        "chapter_02_accepted": project / "chapters" / "02" / "expression" / "accepted.yaml",
        "story_identity": project / ".auteur" / "state" / "artifacts" / "story_identity.yaml",
        "blueprint": project / ".auteur" / "state" / "artifacts" / "blueprint.yaml",
        "chapter_01_outline": project / ".auteur" / "state" / "artifacts" / "chapter_01.yaml",
        "chapter_02_outline": project / ".auteur" / "state" / "artifacts" / "chapter_02.yaml",
    }
    snapshot = {}
    for name, path in paths.items():
        if path.exists():
            snapshot[name] = hashlib.sha256(path.read_bytes()).hexdigest()
    return snapshot


def _publication_id(plan_id: str) -> str:
    return "book_publication_" + plan_id.removeprefix("book_application_set_")


# ----------------------------------------------------------------------------
# 1. Planning
# ----------------------------------------------------------------------------

def test_plan_fresh_separator_proposal_is_ready(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    inspection_id, proposal_id = _separator_proposal(store, book_id, project)
    plan = store.plan(inspection_id, [proposal_id])
    assert plan["artifact_type"] == "book_reconciliation_plan"
    assert plan["authority"] == "derived"
    assert plan["lifecycle"] == "planned"
    assert plan["readiness"]["status"] == "ready"
    assert plan["planned_outputs"][0]["output_type"] == "book_separator_candidate"


def test_plan_fresh_order_proposal_is_ready(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    inspection_id, proposal_id = _order_proposal(store, book_id, project)
    plan = store.plan(inspection_id, [proposal_id])
    assert plan["readiness"]["status"] == "ready"
    assert plan["planned_outputs"][0]["output_type"] == "book_order_candidate"


def test_plan_records_source_fields(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    report = store._load_inspection(_separator_proposal(store, book_id, project)[0])
    plan = store.plan(report["inspection_id"], list(store.route(report["inspection_id"])["book_proposals"]))
    assert plan["source_book_expression"] == book_id
    assert plan["source_book_revision"] == report["book_revision"]
    assert plan["source_book_hash"] == report["book_content_hash"]
    assert plan["external_manuscript_hash"] == report["external_manuscript"]["content_hash"]


def test_plan_compatible_mix_one_plan_multiple_outputs(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    # A separator + Chapter wording edit routes to a Book proposal plus a
    # delegated Chapter inspection; select only the Book proposal for planning.
    original = _book_md(project).read_text(encoding="utf-8")
    edited = project / "mixed.md"
    edited.write_text(
        original.replace("\n---\n", "\n***\n").replace(
            "The river wind carries Tomas's warning up the tower.",
            "The river wind carries Tomas's solemn warning up the tower.",
        ),
        encoding="utf-8",
    )
    inspection = store.inspect(edited, book_id)
    routed = store.route(inspection["inspection_id"])
    plan = store.plan(inspection["inspection_id"], routed["book_proposals"])
    assert plan["readiness"]["status"] == "ready"
    assert len(plan["planned_outputs"]) == len(routed["book_proposals"]) == 1


def test_plan_rejects_unresolved_missing_proposal(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    inspection_id, _ = _separator_proposal(store, book_id, project)
    plan = store.plan(inspection_id, ["proposal_does_not_exist"])
    assert plan["readiness"]["status"] == "not_ready"
    assert plan["freshness_results"][0]["classification"] == "unresolved"


def test_plan_rejects_unsupported_proposal_type(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    inspection_id, proposal_id = _separator_proposal(store, book_id, project)
    path = store._proposal_path(proposal_id)
    proposal = yaml.safe_load(path.read_text(encoding="utf-8"))
    proposal["proposal_type"] = "book_footnote_patch"
    path.write_text(yaml.safe_dump(proposal, sort_keys=False), encoding="utf-8")
    plan = store.plan(inspection_id, [proposal_id])
    assert plan["readiness"]["status"] == "unsupported"


def test_plan_rejects_stale_proposal(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    inspection_id, proposal_id = _separator_proposal(store, book_id, project)
    path = store._proposal_path(proposal_id)
    proposal = yaml.safe_load(path.read_text(encoding="utf-8"))
    proposal["source_book_hash"] = "sha256:stale"
    path.write_text(yaml.safe_dump(proposal, sort_keys=False), encoding="utf-8")
    plan = store.plan(inspection_id, [proposal_id])
    assert plan["readiness"]["status"] == "stale"


def test_plan_rejects_duplicate_targets(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    inspection_id, proposal_id = _separator_proposal(store, book_id, project)
    # Clone the proposal under a second id targeting the same separator.
    path = store._proposal_path(proposal_id)
    proposal = yaml.safe_load(path.read_text(encoding="utf-8"))
    second_id = proposal_id + "_dup"
    proposal["proposal_id"] = second_id
    store._proposal_path(second_id).write_text(yaml.safe_dump(proposal, sort_keys=False), encoding="utf-8")
    plan = store.plan(inspection_id, [proposal_id, second_id])
    assert plan["readiness"]["status"] == "conflicted"
    assert any(c["conflict_code"] == "duplicate_targets" for c in plan["conflicts"])


def test_plan_rejects_conflicting_orders(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    inspection_id, proposal_id = _order_proposal(store, book_id, project)
    path = store._proposal_path(proposal_id)
    proposal = yaml.safe_load(path.read_text(encoding="utf-8"))
    second_id = proposal_id + "_alt"
    proposal["proposal_id"] = second_id
    proposal["target"] = "book_02"  # distinct target so it is the order conflict, not duplicate_targets
    store._proposal_path(second_id).write_text(yaml.safe_dump(proposal, sort_keys=False), encoding="utf-8")
    plan = store.plan(inspection_id, [proposal_id, second_id])
    assert plan["readiness"]["status"] == "conflicted"
    assert any(c["conflict_code"] == "conflicting_orders" for c in plan["conflicts"])


def test_plan_rejects_duplicate_proposal_selection(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    inspection_id, proposal_id = _separator_proposal(store, book_id, project)
    plan = store.plan(inspection_id, [proposal_id, proposal_id])
    assert plan["readiness"]["status"] == "conflicted"
    assert any(c["conflict_code"] == "duplicate_proposal_selection" for c in plan["conflicts"])


def test_plan_rejects_source_mismatch_proposal(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    inspection_id, proposal_id = _separator_proposal(store, book_id, project)
    path = store._proposal_path(proposal_id)
    proposal = yaml.safe_load(path.read_text(encoding="utf-8"))
    proposal["source_inspection_id"] = "inspection_other"
    path.write_text(yaml.safe_dump(proposal, sort_keys=False), encoding="utf-8")
    plan = store.plan(inspection_id, [proposal_id])
    assert plan["readiness"]["status"] == "not_ready"
    assert plan["freshness_results"][0]["classification"] == "invalid"


def test_plan_rejects_transformation_mismatch(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    inspection_id, proposal_id = _separator_proposal(store, book_id, project)
    path = store._proposal_path(proposal_id)
    proposal = yaml.safe_load(path.read_text(encoding="utf-8"))
    proposal["transformation"] = {"id": "expression.propose_book_change", "version": 2}
    path.write_text(yaml.safe_dump(proposal, sort_keys=False), encoding="utf-8")
    plan = store.plan(inspection_id, [proposal_id])
    assert plan["readiness"]["status"] == "unsupported"


def test_plan_empty_selection_not_ready(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    inspection_id, _ = _separator_proposal(store, book_id, project)
    plan = store.plan(inspection_id, [])
    assert plan["readiness"]["status"] == "not_ready"
    assert plan["planned_outputs"] == []


def test_plan_candidate_ids_are_deterministic(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    inspection_id, proposal_id = _separator_proposal(store, book_id, project)
    plan = store.plan(inspection_id, [proposal_id])
    expected = "book_candidate_" + hashlib.sha256((plan["plan_id"] + proposal_id).encode()).hexdigest()[:32]
    assert plan["planned_outputs"][0]["planned_candidate_id"] == expected


def test_plan_id_and_candidate_id_stable_across_calls(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    inspection_id, proposal_id = _separator_proposal(store, book_id, project)
    first = store.plan(inspection_id, [proposal_id])
    second = store.plan(inspection_id, [proposal_id])
    assert first["plan_id"] == second["plan_id"]
    assert first["planned_outputs"][0]["planned_candidate_id"] == second["planned_outputs"][0]["planned_candidate_id"]


def test_plan_creates_no_candidate_no_preview_no_pointer(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    inspection_id, proposal_id = _separator_proposal(store, book_id, project)
    before = _pointer_snapshot(project)
    store.plan(inspection_id, [proposal_id])
    assert not (store.root / "candidates").exists()
    assert not (store.root / "previews").exists()
    assert not (store.root / "publications").exists()
    assert _pointer_snapshot(project) == before


def test_plan_persisted_and_reloadable(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    inspection_id, proposal_id = _separator_proposal(store, book_id, project)
    plan = store.plan(inspection_id, [proposal_id])
    assert store.show_book_plan(plan["plan_id"])["plan_id"] == plan["plan_id"]


# ----------------------------------------------------------------------------
# 2. Candidate model
# ----------------------------------------------------------------------------

def _publish(store: BookReconciliationStore, book_id: str, project: Path, order: bool = False) -> dict:
    inspection_id, proposal_id = (_order_proposal if order else _separator_proposal)(store, book_id, project)
    plan = store.plan(inspection_id, [proposal_id])
    return store.publish(plan["plan_id"])


def test_candidate_is_durable(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    publication = _publish(store, book_id, project)
    candidate_id = publication["published_candidates"][0]
    assert (store.root / "candidates" / f"{candidate_id}.yaml").exists()


def test_candidate_is_unaccepted(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    publication = _publish(store, book_id, project)
    candidate = store.load_book_candidate(publication["published_candidates"][0])
    assert candidate["authority"] == "candidate"
    assert candidate["lifecycle"] == "proposed"


def test_candidate_is_noncanonical_with_provenance(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    publication = _publish(store, book_id, project)
    candidate = store.load_book_candidate(publication["published_candidates"][0])
    assert candidate["artifact_type"] == "book_separator_candidate"
    assert candidate["source_proposal_id"]
    assert candidate["source_inspection_id"]
    assert candidate["source_plan_id"]
    assert candidate["publication_id"] == publication["publication_id"]
    assert candidate["transformation"] == {"id": "expression.publish_book_application", "version": 1}
    assert candidate["original"] == "---"
    assert candidate["proposed"] == "***"


def test_order_candidate_type_and_content(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    publication = _publish(store, book_id, project, order=True)
    candidate = store.load_book_candidate(publication["published_candidates"][0])
    assert candidate["artifact_type"] == "book_order_candidate"
    assert candidate["original"] == "chapter_01, chapter_02"
    assert candidate["proposed"] == "chapter_02, chapter_01"


def test_candidate_does_not_update_accepted_book_state(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    before = _pointer_snapshot(project)
    _publish(store, book_id, project)
    assert _pointer_snapshot(project) == before


# ----------------------------------------------------------------------------
# 3. Preview
# ----------------------------------------------------------------------------

def test_preview_uses_accepted_chapter_sources(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    publication = _publish(store, book_id, project)
    preview = store.load_book_preview(publication["publication_id"])
    assert len(preview["accepted_chapter_sources"]) == 2
    metadata = BookExpressionStore(project).inspect(book_id)["metadata"]
    accepted_ids = {c["chapter_expression_id"] for c in metadata["chapters"]}
    assert {s["chapter_expression_id"] for s in preview["accepted_chapter_sources"]} == accepted_ids


def test_preview_uses_book_candidate_sources(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    publication = _publish(store, book_id, project)
    preview = store.load_book_preview(publication["publication_id"])
    assert len(preview["candidate_sources"]) == 1
    assert preview["candidate_sources"][0]["candidate_type"] == "book_separator_candidate"


def test_preview_is_derived_and_cannot_accept(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    publication = _publish(store, book_id, project)
    preview = store.load_book_preview(publication["publication_id"])
    assert preview["authority"] == "derived"
    assert preview["lifecycle"] == "proposed"
    assert preview["role"] == "application_preview"
    assert preview["canonical"] is False
    # Candidate-backed preview is not a canonical Book Expression and must not
    # be acceptable through the Book Expression store.
    with pytest.raises(FileNotFoundError):
        BookExpressionStore(project).accept(preview["book_expression_id"])


def test_order_preview_reflects_candidate_order(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    publication = _publish(store, book_id, project, order=True)
    preview = store.load_book_preview(publication["publication_id"])
    assert [s["chapter_id"] for s in preview["accepted_chapter_sources"]] == ["chapter_02", "chapter_01"]


def test_preview_contains_no_chapter_local_proposals(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    publication = _publish(store, book_id, project)
    preview = store.load_book_preview(publication["publication_id"])
    assert all(s.get("source_kind") != "chapter_local_proposal" for s in preview["candidate_sources"])


# ----------------------------------------------------------------------------
# 4. Publication transaction / manifest
# ----------------------------------------------------------------------------

def test_publication_manifest_schema(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    publication = _publish(store, book_id, project)
    assert publication["artifact_type"] == "book_reconciliation_publication"
    assert publication["authority"] == "derived"
    assert publication["lifecycle"] == "published"
    assert publication["preview"]["role"] == "application_preview"
    assert publication["acceptance_status"] == "none"
    assert publication["accepted_book_pointer_changed"] is False
    assert publication["transformation"] == {"id": "expression.publish_book_application", "version": 1}


def test_publication_all_outputs_visible_together(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    publication = _publish(store, book_id, project)
    pub_id = publication["publication_id"]
    assert (store.root / "publications" / f"{pub_id}.yaml").exists()
    assert (store.root / "previews" / f"{pub_id}.yaml").exists()
    for candidate_id in publication["published_candidates"]:
        assert (store.root / "candidates" / f"{candidate_id}.yaml").exists()
    assert not (store.root / "staging" / pub_id).exists()


def test_publication_no_pointer_change(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    before = _pointer_snapshot(project)
    _publish(store, book_id, project)
    assert _pointer_snapshot(project) == before


def test_publication_does_not_mutate_source_book_md(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    original = _book_md(project).read_text(encoding="utf-8")
    _publish(store, book_id, project)
    assert _book_md(project).read_text(encoding="utf-8") == original


def test_publication_failure_rolls_back_all(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    inspection_id, proposal_id = _separator_proposal(store, book_id, project)
    plan = store.plan(inspection_id, [proposal_id])
    pub_id = _publication_id(plan["plan_id"])
    with mock.patch("auteur.expression.book_reconciliation.shutil.move", side_effect=OSError("boom")):
        with pytest.raises(OSError):
            store.publish(plan["plan_id"])
    assert not (store.root / "publications" / f"{pub_id}.yaml").exists()
    assert not (store.root / "previews" / f"{pub_id}.yaml").exists()
    assert not (store.root / "staging" / pub_id).exists()
    assert not list((store.root / "candidates").glob("*.yaml")) if (store.root / "candidates").exists() else True


def test_publication_failure_on_last_move_rolls_back(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    inspection_id, proposal_id = _separator_proposal(store, book_id, project)
    plan = store.plan(inspection_id, [proposal_id])
    pub_id = _publication_id(plan["plan_id"])
    real_move = shutil.move
    calls = {"n": 0}

    def flaky(src, dst, *a, **k):
        calls["n"] += 1
        # candidate move, preview move succeed; manifest move (3rd) fails.
        if calls["n"] >= 3:
            raise OSError("fail on manifest move")
        return real_move(src, dst, *a, **k)

    with mock.patch("auteur.expression.book_reconciliation.shutil.move", side_effect=flaky):
        with pytest.raises(OSError):
            store.publish(plan["plan_id"])
    assert calls["n"] >= 3
    assert not (store.root / "publications" / f"{pub_id}.yaml").exists()
    assert not (store.root / "previews" / f"{pub_id}.yaml").exists()
    assert not list((store.root / "candidates").glob("*.yaml")) if (store.root / "candidates").exists() else True
    assert not (store.root / "staging" / pub_id).exists()


def test_publication_success_leaves_no_staging(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    publication = _publish(store, book_id, project)
    assert not (store.root / "staging" / publication["publication_id"]).exists()


def test_publish_missing_plan_raises(tmp_path: Path) -> None:
    project, _ = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    with pytest.raises(FileNotFoundError):
        store.publish("book_application_set_missing")


# ----------------------------------------------------------------------------
# 5. Freshness gate (live dependencies block publication)
# ----------------------------------------------------------------------------

def _ready_plan(store: BookReconciliationStore, book_id: str, project: Path, order: bool = False) -> dict:
    inspection_id, proposal_id = (_order_proposal if order else _separator_proposal)(store, book_id, project)
    return store.plan(inspection_id, [proposal_id])


def _assert_rejected(store: BookReconciliationStore, plan_id: str, code: str | None = None) -> dict:
    with pytest.raises(BookPublicationRejected) as excinfo:
        store.publish(plan_id)
    result = excinfo.value.result
    assert result["status"] == "rejected_stale"
    assert result["visible_outputs_created"] is False
    if code is not None:
        assert any(reason["code"] == code for reason in result["reasons"]), result["reasons"]
    return result


def test_freshness_blocks_on_book_revision_change(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    plan = _ready_plan(store, book_id, project)
    cs = ChapterExpressionStore(project)
    cs.accept(cs.compose("chapter_01").artifact_id)
    _assert_rejected(store, plan["plan_id"], "BOOK_OR_CHAPTER_REVISION_CHANGED")


def test_freshness_blocks_on_book_hash_change(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    plan = _ready_plan(store, book_id, project)
    plan_path = store._plan_path(plan["plan_id"])
    data = yaml.safe_load(plan_path.read_text(encoding="utf-8"))
    data["source_book_hash"] = "sha256:not_the_real_hash"
    plan_path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    _assert_rejected(store, plan["plan_id"], "BOOK_HASH_CHANGED")


def test_freshness_blocks_on_chapter_revision_change(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    plan = _ready_plan(store, book_id, project)
    cs = ChapterExpressionStore(project)
    cs.accept(cs.compose("chapter_02").artifact_id)
    _assert_rejected(store, plan["plan_id"], "BOOK_OR_CHAPTER_REVISION_CHANGED")


def test_freshness_blocks_on_chapter_order_change(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    plan = _ready_plan(store, book_id, project)
    structure = project / "book" / "structure.yaml"
    data = yaml.safe_load(structure.read_text(encoding="utf-8"))
    data["chapters"] = list(reversed(data["chapters"]))
    structure.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    _assert_rejected(store, plan["plan_id"], "BOOK_OR_CHAPTER_REVISION_CHANGED")


def test_freshness_blocks_on_separator_change(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    plan = _ready_plan(store, book_id, project)
    # Mutate the proposal so its recorded original separator no longer matches
    # the accepted Book, simulating a separator that changed after planning.
    proposal_id = plan["selected_proposals"][0]
    path = store._proposal_path(proposal_id)
    proposal = yaml.safe_load(path.read_text(encoding="utf-8"))
    proposal["original"] = "###"
    path.write_text(yaml.safe_dump(proposal, sort_keys=False), encoding="utf-8")
    _assert_rejected(store, plan["plan_id"], "SEPARATOR_CHANGED")


def test_freshness_blocks_on_external_manuscript_change(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    inspection_id, proposal_id = _separator_proposal(store, book_id, project)
    plan = store.plan(inspection_id, [proposal_id])
    report = store._load_inspection(inspection_id)
    Path(report["external_manuscript"]["path"]).write_text("changed manuscript text", encoding="utf-8")
    _assert_rejected(store, plan["plan_id"], "MANUSCRIPT_HASH_CHANGED")


def test_freshness_blocks_on_marker_contract_change(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    plan = _ready_plan(store, book_id, project)
    inspection_path = store._inspection_path(plan["source_inspection_id"])
    report = yaml.safe_load(inspection_path.read_text(encoding="utf-8"))
    report["marker_contract"] = {"version": 2}
    inspection_path.write_text(yaml.safe_dump(report, sort_keys=False), encoding="utf-8")
    _assert_rejected(store, plan["plan_id"], "MARKER_CONTRACT_CHANGED")


def test_freshness_blocks_on_inspection_transformation_change(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    plan = _ready_plan(store, book_id, project)
    inspection_path = store._inspection_path(plan["source_inspection_id"])
    report = yaml.safe_load(inspection_path.read_text(encoding="utf-8"))
    report["provenance"]["transformation"] = {"id": "expression.inspect_book_manuscript", "version": 9}
    inspection_path.write_text(yaml.safe_dump(report, sort_keys=False), encoding="utf-8")
    _assert_rejected(store, plan["plan_id"], "INSPECTION_TRANSFORMATION_CHANGED")


def test_freshness_blocks_on_proposal_transformation_change(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    plan = _ready_plan(store, book_id, project)
    proposal_id = plan["selected_proposals"][0]
    path = store._proposal_path(proposal_id)
    proposal = yaml.safe_load(path.read_text(encoding="utf-8"))
    proposal["transformation"] = {"id": "expression.propose_book_change", "version": 5}
    path.write_text(yaml.safe_dump(proposal, sort_keys=False), encoding="utf-8")
    _assert_rejected(store, plan["plan_id"], "TRANSFORMATION_VERSION_CHANGED")


def test_freshness_blocks_on_proposal_lifecycle_change(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    plan = _ready_plan(store, book_id, project)
    proposal_id = plan["selected_proposals"][0]
    path = store._proposal_path(proposal_id)
    proposal = yaml.safe_load(path.read_text(encoding="utf-8"))
    proposal["lifecycle"] = "rejected"
    path.write_text(yaml.safe_dump(proposal, sort_keys=False), encoding="utf-8")
    _assert_rejected(store, plan["plan_id"], "PROPOSAL_STATUS_CHANGED")


def test_freshness_blocks_on_missing_proposal(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    plan = _ready_plan(store, book_id, project)
    store._proposal_path(plan["selected_proposals"][0]).unlink()
    _assert_rejected(store, plan["plan_id"], "TARGET_MISSING")


def test_freshness_does_not_trust_persisted_readiness(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    inspection_id, proposal_id = _separator_proposal(store, book_id, project)
    plan = store.plan(inspection_id, ["proposal_missing"])  # not_ready
    # Force persisted readiness to a lie; the live gate must still reject.
    plan_path = store._plan_path(plan["plan_id"])
    data = yaml.safe_load(plan_path.read_text(encoding="utf-8"))
    data["readiness"] = {"status": "ready", "reasons": []}
    plan_path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    _assert_rejected(store, plan["plan_id"])


def test_freshness_blocks_on_plan_transformation_change(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    plan = _ready_plan(store, book_id, project)
    plan_path = store._plan_path(plan["plan_id"])
    data = yaml.safe_load(plan_path.read_text(encoding="utf-8"))
    data["transformation"] = {"id": "expression.publish_book_application", "version": 7}
    plan_path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    _assert_rejected(store, plan["plan_id"], "PLAN_TRANSFORMATION_CHANGED")


# ----------------------------------------------------------------------------
# 6. Stale plan publishes nothing (no outputs, no preview, no manifest)
# ----------------------------------------------------------------------------

def test_stale_plan_creates_no_outputs(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    plan = _ready_plan(store, book_id, project)
    cs = ChapterExpressionStore(project)
    cs.accept(cs.compose("chapter_01").artifact_id)
    _assert_rejected(store, plan["plan_id"])
    pub_id = _publication_id(plan["plan_id"])
    assert not (store.root / "publications" / f"{pub_id}.yaml").exists()
    assert not (store.root / "previews" / f"{pub_id}.yaml").exists()
    assert not (store.root / "staging" / pub_id).exists()
    assert not (store.root / "candidates").exists() or not list((store.root / "candidates").glob("*.yaml"))


def test_stale_plan_rejected_before_staging(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    plan = _ready_plan(store, book_id, project)
    cs = ChapterExpressionStore(project)
    cs.accept(cs.compose("chapter_01").artifact_id)
    # A stale plan must be rejected without shutil.move ever being called.
    with mock.patch("auteur.expression.book_reconciliation.shutil.move", side_effect=AssertionError("must not stage")):
        with pytest.raises(BookPublicationRejected):
            store.publish(plan["plan_id"])


def test_stale_plan_after_book_recompose_lists_reasons(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    plan = _ready_plan(store, book_id, project, order=True)
    cs = ChapterExpressionStore(project)
    cs.accept(cs.compose("chapter_01").artifact_id)
    result = _assert_rejected(store, plan["plan_id"])
    assert result["reasons"]


# ----------------------------------------------------------------------------
# 7. Duplicate handling
# ----------------------------------------------------------------------------

def test_duplicate_publication_rejected(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    inspection_id, proposal_id = _separator_proposal(store, book_id, project)
    plan = store.plan(inspection_id, [proposal_id])
    store.publish(plan["plan_id"])
    with pytest.raises(BookPublicationRejected) as excinfo:
        store.publish(plan["plan_id"])
    assert excinfo.value.result["status"] == "rejected_duplicate"
    assert excinfo.value.result["visible_outputs_created"] is False


def test_duplicate_publication_preserves_original(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    inspection_id, proposal_id = _separator_proposal(store, book_id, project)
    plan = store.plan(inspection_id, [proposal_id])
    first = store.publish(plan["plan_id"])
    pub_path = store.root / "publications" / f"{first['publication_id']}.yaml"
    original_bytes = pub_path.read_bytes()
    with pytest.raises(BookPublicationRejected):
        store.publish(plan["plan_id"])
    assert pub_path.read_bytes() == original_bytes


def test_duplicate_publication_no_extra_candidates(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    inspection_id, proposal_id = _separator_proposal(store, book_id, project)
    plan = store.plan(inspection_id, [proposal_id])
    store.publish(plan["plan_id"])
    before = sorted((store.root / "candidates").glob("*.yaml"))
    with pytest.raises(BookPublicationRejected):
        store.publish(plan["plan_id"])
    assert sorted((store.root / "candidates").glob("*.yaml")) == before


# ----------------------------------------------------------------------------
# 8. Independent candidates remain fresh after publication
# ----------------------------------------------------------------------------

def test_inspect_book_publication_roundtrips(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    publication = _publish(store, book_id, project)
    loaded = store.inspect_book_publication(publication["publication_id"])
    assert loaded["publication_id"] == publication["publication_id"]
    assert loaded["published_candidates"] == publication["published_candidates"]


def test_inspect_missing_publication_raises(tmp_path: Path) -> None:
    project, _ = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    with pytest.raises(FileNotFoundError):
        store.inspect_book_publication("book_publication_missing")


def test_independent_candidate_remains_fresh_after_publication(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    publication = _publish(store, book_id, project)
    candidate = store.load_book_candidate(publication["published_candidates"][0])
    # Publishing does not change the source Book, so the candidate's recorded
    # freshness stays fresh and its source hash still matches the accepted Book.
    assert candidate["freshness"]["status"] == "fresh"
    metadata = BookExpressionStore(project).inspect(book_id)["metadata"]
    source_text = (project / "book" / "expression" / f"book_v{metadata['revision']:03d}.md").read_text(encoding="utf-8")
    assert candidate["source_book_hash"] == "sha256:" + hashlib.sha256(source_text.encode()).hexdigest()


# ----------------------------------------------------------------------------
# 9. Mutation invariants (no upstream layer changes)
# ----------------------------------------------------------------------------

def test_no_identity_blueprint_structure_scene_mutation(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    watched = {
        "story_identity": project / ".auteur" / "state" / "artifacts" / "story_identity.yaml",
        "blueprint": project / ".auteur" / "state" / "artifacts" / "blueprint.yaml",
        "chapter_01_outline": project / ".auteur" / "state" / "artifacts" / "chapter_01.yaml",
        "chapter_02_outline": project / ".auteur" / "state" / "artifacts" / "chapter_02.yaml",
        "scene_01_01": project / "chapters" / "01" / "scenes" / "scene_01_01.yaml",
        "scene_02_01": project / "chapters" / "02" / "scenes" / "scene_02_01.yaml",
    }
    before = {name: path.read_bytes() for name, path in watched.items() if path.exists()}
    _publish(store, book_id, project)
    after = {name: path.read_bytes() for name, path in watched.items() if path.exists()}
    assert after == before


def test_no_chapter_expression_pointer_mutation(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    accepted = {
        "chapter_01": project / "chapters" / "01" / "expression" / "accepted.yaml",
        "chapter_02": project / "chapters" / "02" / "expression" / "accepted.yaml",
    }
    before = {name: path.read_bytes() for name, path in accepted.items() if path.exists()}
    _publish(store, book_id, project)
    after = {name: path.read_bytes() for name, path in accepted.items() if path.exists()}
    assert after == before


def test_no_accepted_book_pointer_mutation(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    accepted = project / "book" / "expression" / "accepted.yaml"
    before = accepted.read_bytes()
    _publish(store, book_id, project)
    assert accepted.read_bytes() == before


# ----------------------------------------------------------------------------
# 10. Publication is not acceptance (no accept-candidate surface)
# ----------------------------------------------------------------------------

def test_store_exposes_no_candidate_acceptance_surface() -> None:
    forbidden = {
        "accept_book_candidate",
        "accept_book_publication",
        "apply_book_proposal",
        "recompose_book_reconciliation",
        "decide_book_candidate",
    }
    assert forbidden.isdisjoint(set(dir(BookReconciliationStore)))
