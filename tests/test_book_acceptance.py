"""Phase C3: explicit, atomic Book acceptance.

``accept_recomposed_book`` accepts a comparison result (not an arbitrary
recomposition path) as canonical only after a 20-point revalidation proves an
exact match with zero residuals. On success it creates an IMMUTABLE accepted Book
revision (authority=accepted, lifecycle=accepted, role=book_expression,
canonical=true) byte-identical to the recomposition, an immutable acceptance
record (authority=decision, evidence for the authority crossing), and moves the
accepted Book pointer atomically (last, via compare-and-swap).

These tests cover the core acceptance model, the two readiness states, the
20-point gate, freshness/tamper/pointer revalidation, the 30 semantic scenarios,
atomic rollback, duplicate/concurrent handling, dogfood scenarios, and CLI
integration. Reconciliation completion, Chapter reconciliation closing, and any
deletion of proposals/candidates/decisions/recompositions/comparisons are OUT OF
SCOPE and not implemented in this slice; several tests assert their absence.
"""

from __future__ import annotations

import hashlib
import re
from pathlib import Path

import yaml

from auteur.canonical_story import CanonicalStoryBootstrap
from auteur.expression.book import BookExpressionStore
from auteur.expression.composition import ChapterExpressionStore
from auteur.expression.book_reconciliation import (
    AcceptanceBlockedError,
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
    tag = hashlib.sha256(sep.encode()).hexdigest()[:8]
    edited = project / f"edited_sep_{tag}.md"
    edited.write_text(original.replace("\n---\n", f"\n{sep}\n"), encoding="utf-8")
    return edited


def _faithful_manuscript(project: Path) -> Path:
    out = project / "external_faithful.md"
    out.write_text(_book_md(project).read_text(encoding="utf-8"), encoding="utf-8")
    return out


def _publish_separator(store: BookReconciliationStore, book_id: str, project: Path, sep: str = "***") -> tuple[dict, str]:
    inspection = store.inspect(_separator_edit(project, sep), book_id)
    routed = store.route(inspection["inspection_id"])
    plan = store.plan(inspection["inspection_id"], [routed["book_proposals"][0]])
    publication = store.publish(plan["plan_id"])
    return publication, publication["published_candidates"][0]


def _recompose_default(store: BookReconciliationStore, book_id: str, project: Path) -> tuple[dict, str]:
    """A recomposition equal to the pristine accepted Book (no approvals)."""
    publication, _candidate = _publish_separator(store, book_id, project, "***")
    ok, recomposed = store.recompose_book_from_accepted_sources(publication["publication_id"])
    assert ok
    return recomposed, publication["publication_id"]


def _recompose_with_separator(store: BookReconciliationStore, book_id: str, project: Path, sep: str) -> tuple[dict, str]:
    publication, candidate = _publish_separator(store, book_id, project, sep)
    store.decide_candidate(candidate, "approved", "approved")
    ok, recomposed = store.recompose_book_from_accepted_sources(publication["publication_id"])
    assert ok
    return recomposed, publication["publication_id"]


def _ready_comparison(store: BookReconciliationStore, book_id: str, project: Path) -> dict:
    """An exact-match comparison ready for acceptance (pristine, faithful copy)."""
    recomposed, _pub = _recompose_default(store, book_id, project)
    ok, report = store.compare_book_recomposition(recomposed["recomposition_id"], _faithful_manuscript(project))
    assert ok
    assert report["summary"]["ready_for_acceptance"] is True
    return report


def _ready_comparison_with_separator(store: BookReconciliationStore, book_id: str, project: Path, sep: str = "***") -> tuple[dict, str]:
    """An exact-match comparison whose recomposition consumes an approved separator."""
    recomposed, publication_id = _recompose_with_separator(store, book_id, project, sep)
    ok, report = store.compare_book_recomposition(recomposed["recomposition_id"], _separator_edit(project, sep))
    assert ok
    assert report["summary"]["ready_for_acceptance"] is True
    return report, publication_id


def _accepted_pointer_path(project: Path) -> Path:
    return project / "book" / "expression" / "accepted-book-pointer.yaml"


def _acceptances_dir(project: Path) -> Path:
    return project / "book" / "expression" / "reconciliation" / "acceptances"


def _pointer_files(project: Path) -> dict[str, str]:
    directory = project / "book" / "expression" / "reconciliation" / "accepted-sources" / "pointers"
    snap = {}
    if directory.exists():
        for path in sorted(directory.glob("*.yaml")):
            snap[path.name] = hashlib.sha256(path.read_bytes()).hexdigest()
    return snap


def _chapter_accepted_files(project: Path) -> dict[str, str]:
    snap = {}
    for path in sorted(project.glob("chapters/*/expression/accepted.yaml")):
        snap[str(path.relative_to(project))] = hashlib.sha256(path.read_bytes()).hexdigest()
    return snap


# ----------------------------------------------------------------------------
# Core model
# ----------------------------------------------------------------------------

def test_two_readiness_flags_present_in_comparison(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    report = _ready_comparison(store, book_id, project)
    summary = report["summary"]
    assert summary["ready_for_review"] is True
    assert summary["ready_for_acceptance"] is True
    # Backwards-compatible C2 alias equals ready_for_review.
    assert summary["ready_for_book_acceptance"] == summary["ready_for_review"]


def test_book_owned_residual_ready_for_review_not_acceptance(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    recomposed, _pub = _recompose_default(store, book_id, project)
    ok, report = store.compare_book_recomposition(recomposed["recomposition_id"], _separator_edit(project, "==="))
    assert ok
    assert report["summary"]["ready_for_review"] is True
    assert report["summary"]["ready_for_acceptance"] is False


def test_acceptance_produces_accepted_artifact(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    report = _ready_comparison(store, book_id, project)
    ok, result = store.accept_recomposed_book(report["comparison_id"])
    assert ok
    revision = result["accepted_book_revision"]
    assert revision["authority"] == "accepted"
    assert revision["lifecycle"] == "accepted"
    assert revision["role"] == "book_expression"
    assert revision["canonical"] is True
    assert revision["transformation"] == {"id": "expression.accept_recomposed_book", "version": 1}


def test_book_revision_increments(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    report = _ready_comparison(store, book_id, project)
    # Base accepted Book is revision 1; acceptance mints revision 2.
    assert report["source_book_revision"] == 1
    ok, result = store.accept_recomposed_book(report["comparison_id"])
    assert ok
    assert result["accepted_book_revision"]["revision"] == 2
    assert result["acceptance_record"]["previous_book_revision"] == 1


def test_acceptance_record_full_provenance(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    report = _ready_comparison(store, book_id, project)
    ok, result = store.accept_recomposed_book(report["comparison_id"], reason="looks good")
    assert ok
    record = result["acceptance_record"]
    assert record["artifact_type"] == "book_reconciliation_acceptance"
    assert record["authority"] == "decision"
    assert record["lifecycle"] == "decided"
    assert record["source_comparison_id"] == report["comparison_id"]
    assert record["source_recomposition_id"] == report["source_recomposition_id"]
    assert record["reason"] == "looks good"
    transition = record["pointer_transition"]
    assert transition["previous_pointer_id"] is None
    assert transition["current_pointer_id"]
    assert transition["current_pointer_target"] == 2


def test_pointer_moves_exactly_once(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    report = _ready_comparison(store, book_id, project)
    store.accept_recomposed_book(report["comparison_id"])
    pointer = store.current_accepted_book_pointer()
    assert pointer is not None
    assert pointer["current_revision"] == 2
    assert len(pointer["history"]) == 1
    # Duplicate attempt does not move the pointer again.
    store.accept_recomposed_book(report["comparison_id"])
    pointer = store.current_accepted_book_pointer()
    assert len(pointer["history"]) == 1


def test_accepted_revision_stored_at_expected_path(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    report = _ready_comparison(store, book_id, project)
    ok, result = store.accept_recomposed_book(report["comparison_id"])
    assert ok
    revision = result["accepted_book_revision"]
    path = project / "book" / "expression" / f"book_{revision['book_id']}_v002_accepted.yaml"
    assert path.exists()
    loaded = store.load_accepted_book_revision(revision["book_id"], 2)
    assert loaded["canonical"] is True
    assert loaded["content_hash"] == revision["content_hash"]


def test_acceptance_record_stored_at_expected_path(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    report = _ready_comparison(store, book_id, project)
    ok, result = store.accept_recomposed_book(report["comparison_id"])
    assert ok
    acceptance_id = result["acceptance_record"]["acceptance_id"]
    path = _acceptances_dir(project) / f"{acceptance_id}.yaml"
    assert path.exists()
    assert store.load_book_acceptance(acceptance_id)["acceptance_id"] == acceptance_id


def test_content_byte_identical_to_recomposition_render(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    recomposed, publication_id = _recompose_default(store, book_id, project)
    ok, report = store.compare_book_recomposition(recomposed["recomposition_id"], _faithful_manuscript(project))
    assert ok
    ok, result = store.accept_recomposed_book(report["comparison_id"])
    assert ok
    rendered = store._render_recomposition_text(store.load_recomposed_book(publication_id))
    assert result["accepted_book_revision"]["content"] == rendered
    assert result["accepted_book_revision"]["content_hash"] == "sha256:" + hashlib.sha256(rendered.encode()).hexdigest()


# ----------------------------------------------------------------------------
# Immutability & evidence preservation
# ----------------------------------------------------------------------------

def test_new_revision_is_immutable(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    report = _ready_comparison(store, book_id, project)
    ok, result = store.accept_recomposed_book(report["comparison_id"])
    assert ok
    path = project / "book" / "expression" / f"book_{result['accepted_book_revision']['book_id']}_v002_accepted.yaml"
    before = path.read_bytes()
    # A duplicate acceptance must not rewrite the immutable revision.
    store.accept_recomposed_book(report["comparison_id"])
    assert path.read_bytes() == before


def test_prior_revision_preserved(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    report = _ready_comparison(store, book_id, project)
    prior_accepted = project / "book" / "expression" / "accepted.yaml"
    prior_v1 = project / "book" / "expression" / "book_v001.yaml"
    before = (prior_accepted.read_bytes(), prior_v1.read_bytes())
    store.accept_recomposed_book(report["comparison_id"])
    assert (prior_accepted.read_bytes(), prior_v1.read_bytes()) == before


def test_recomposition_remains_derived(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    recomposed, publication_id = _recompose_default(store, book_id, project)
    ok, report = store.compare_book_recomposition(recomposed["recomposition_id"], _faithful_manuscript(project))
    assert ok
    store.accept_recomposed_book(report["comparison_id"])
    reloaded = store.load_recomposed_book(publication_id)
    assert reloaded["authority"] == "derived"
    assert reloaded["lifecycle"] == "proposed"
    assert reloaded["role"] == "reconciliation_recomposition"


def test_comparison_remains_derived(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    report = _ready_comparison(store, book_id, project)
    store.accept_recomposed_book(report["comparison_id"])
    reloaded = store.load_book_comparison(report["comparison_id"])
    assert reloaded["authority"] == "derived"
    assert reloaded["lifecycle"] == "evaluated"


def test_chapter_and_book_owned_pointers_unchanged(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    report, _pub = _ready_comparison_with_separator(store, book_id, project, "***")
    before_pointers = _pointer_files(project)
    before_chapters = _chapter_accepted_files(project)
    store.accept_recomposed_book(report["comparison_id"])
    assert _pointer_files(project) == before_pointers
    assert _chapter_accepted_files(project) == before_chapters


def test_no_reconciliation_completion_artifact(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    recomposed, publication_id = _recompose_default(store, book_id, project)
    ok, report = store.compare_book_recomposition(recomposed["recomposition_id"], _faithful_manuscript(project))
    assert ok
    store.accept_recomposed_book(report["comparison_id"])
    # No completion artifact of any kind is produced.
    for path in project.rglob("*"):
        assert "completion" not in path.name.lower()
    # Evidence remains present (nothing deleted).
    assert store.load_recomposed_book(publication_id)
    assert store.load_book_comparison(report["comparison_id"])
    manifest = store.inspect_book_publication(publication_id)
    assert manifest.get("acceptance_status") == "none"


# ----------------------------------------------------------------------------
# Readiness / residual gates
# ----------------------------------------------------------------------------

def test_exact_match_accepts(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    report = _ready_comparison(store, book_id, project)
    ok, result = store.accept_recomposed_book(report["comparison_id"])
    assert ok
    assert "accepted_book_revision" in result


def test_book_owned_residual_blocks(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    recomposed, _pub = _recompose_default(store, book_id, project)
    ok, report = store.compare_book_recomposition(recomposed["recomposition_id"], _separator_edit(project, "==="))
    assert ok
    ok, error = store.accept_recomposed_book(report["comparison_id"])
    assert not ok
    assert error.status in {"NON_EXACT_MATCH", "RESIDUALS_REMAIN"}
    assert not _accepted_pointer_path(project).exists()


def test_chapter_owned_residual_blocks(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    recomposed, _pub = _recompose_default(store, book_id, project)
    text = _book_md(project).read_text(encoding="utf-8")
    pattern = re.compile(r"(<!-- auteur:chapter id=chapter_01 [^>]*-->\n)(.*?)(\n<!-- auteur:end-chapter id=chapter_01 -->)", re.DOTALL)
    edited = pattern.sub(lambda m: m.group(1) + m.group(2) + " EDIT" + m.group(3), text)
    manuscript = project / "external_chapter.md"
    manuscript.write_text(edited, encoding="utf-8")
    ok, report = store.compare_book_recomposition(recomposed["recomposition_id"], manuscript)
    assert ok
    ok, error = store.accept_recomposed_book(report["comparison_id"])
    assert not ok
    assert error.status in {"NON_EXACT_MATCH", "RESIDUALS_REMAIN"}


def test_structural_residual_blocks(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    recomposed, _pub = _recompose_default(store, book_id, project)
    content = _book_md(project).read_text(encoding="utf-8")
    c1 = re.search(r"<!-- auteur:chapter id=chapter_01 expression_revision=1 -->.*?<!-- auteur:end-chapter id=chapter_01 -->", content, re.DOTALL).group(0)
    manuscript = project / "external_missing.md"
    manuscript.write_text("# The Lantern at Low Water\n\n" + c1 + "\n", encoding="utf-8")
    ok, report = store.compare_book_recomposition(recomposed["recomposition_id"], manuscript)
    assert ok
    ok, error = store.accept_recomposed_book(report["comparison_id"])
    assert not ok
    assert error.status in {"NON_EXACT_MATCH", "RESIDUALS_REMAIN"}


def test_marker_residual_blocks(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    recomposed, _pub = _recompose_default(store, book_id, project)
    content = _book_md(project).read_text(encoding="utf-8")
    manuscript = project / "external_malformed.md"
    manuscript.write_text(content.rstrip("\n") + "\n\n<!-- auteur:chapter this is broken\n", encoding="utf-8")
    ok, report = store.compare_book_recomposition(recomposed["recomposition_id"], manuscript)
    assert ok
    ok, error = store.accept_recomposed_book(report["comparison_id"])
    assert not ok
    assert error.status in {"NON_EXACT_MATCH", "RESIDUALS_REMAIN"}


def test_unresolved_residual_blocks(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    recomposed, _pub = _recompose_default(store, book_id, project)
    content = _book_md(project).read_text(encoding="utf-8")
    stripped = re.sub(r"^<!-- auteur:.*?-->\s*$", "", content, flags=re.MULTILINE)
    manuscript = project / "external_markerless.md"
    manuscript.write_text(stripped, encoding="utf-8")
    ok, report = store.compare_book_recomposition(recomposed["recomposition_id"], manuscript)
    assert ok
    ok, error = store.accept_recomposed_book(report["comparison_id"])
    assert not ok
    assert error.status in {"NON_EXACT_MATCH", "RESIDUALS_REMAIN"}


def test_forged_readiness_flag_with_residual_blocks(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    recomposed, _pub = _recompose_default(store, book_id, project)
    ok, report = store.compare_book_recomposition(recomposed["recomposition_id"], _separator_edit(project, "==="))
    assert ok
    # Forge the persisted readiness flags to True even though a residual remains.
    path = store._comparison_path(report["comparison_id"])
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    data["summary"]["ready_for_acceptance"] = True
    data["summary"]["ready_for_review"] = True
    data["summary"]["ready_for_book_acceptance"] = True
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    ok, error = store.accept_recomposed_book(report["comparison_id"])
    assert not ok  # counts are revalidated; the forged flag is not trusted
    assert error.status in {"NON_EXACT_MATCH", "RESIDUALS_REMAIN"}


# ----------------------------------------------------------------------------
# Freshness / tamper / pointer revalidation
# ----------------------------------------------------------------------------

def test_missing_comparison_blocks(tmp_path: Path) -> None:
    project, _book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    ok, error = store.accept_recomposed_book("book_comparison_does_not_exist")
    assert not ok
    assert isinstance(error, AcceptanceBlockedError)
    assert error.status == "MISSING_COMPARISON"


def test_missing_recomposition_blocks(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    recomposed, publication_id = _recompose_default(store, book_id, project)
    ok, report = store.compare_book_recomposition(recomposed["recomposition_id"], _faithful_manuscript(project))
    assert ok
    store._recomposition_path(publication_id).unlink()
    ok, error = store.accept_recomposed_book(report["comparison_id"])
    assert not ok
    assert error.status == "MISSING_RECOMPOSITION"


def test_tampered_comparison_blocks(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    report = _ready_comparison(store, book_id, project)
    path = store._comparison_path(report["comparison_id"])
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    # Alter a finding id: the id no longer re-derives from stored content.
    data["findings"][0]["finding_id"] = "finding_tampered"
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    ok, error = store.accept_recomposed_book(report["comparison_id"])
    assert not ok
    assert error.reason == "COMPARISON_TAMPERED"


def test_tampered_recomposition_blocks(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    recomposed, publication_id = _recompose_default(store, book_id, project)
    ok, report = store.compare_book_recomposition(recomposed["recomposition_id"], _faithful_manuscript(project))
    assert ok
    path = store._recomposition_path(publication_id)
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    data["separator"] = "TAMPERED"  # body changed, content_hash not updated
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    ok, error = store.accept_recomposed_book(report["comparison_id"])
    assert not ok
    assert error.reason == "RECOMPOSITION_TAMPERED"


def test_external_manuscript_changed_blocks(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    recomposed, _pub = _recompose_default(store, book_id, project)
    manuscript = _faithful_manuscript(project)
    ok, report = store.compare_book_recomposition(recomposed["recomposition_id"], manuscript)
    assert ok
    manuscript.write_text(manuscript.read_text(encoding="utf-8") + "\nEXTRA\n", encoding="utf-8")
    ok, error = store.accept_recomposed_book(report["comparison_id"])
    assert not ok
    assert error.status == "STALE_MANUSCRIPT"
    assert error.reason == "MANUSCRIPT_HASH_CHANGED"


def test_missing_external_manuscript_blocks(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    recomposed, _pub = _recompose_default(store, book_id, project)
    manuscript = _faithful_manuscript(project)
    ok, report = store.compare_book_recomposition(recomposed["recomposition_id"], manuscript)
    assert ok
    manuscript.unlink()
    ok, error = store.accept_recomposed_book(report["comparison_id"])
    assert not ok
    assert error.status == "MISSING_MANUSCRIPT"


def test_stale_chapter_blocks(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    recomposed, _pub = _recompose_default(store, book_id, project)
    ok, report = store.compare_book_recomposition(recomposed["recomposition_id"], _faithful_manuscript(project))
    assert ok
    cs = ChapterExpressionStore(project)
    cs.accept(cs.compose("chapter_01").artifact_id)  # accepted Chapter advances
    ok, error = store.accept_recomposed_book(report["comparison_id"])
    assert not ok
    assert error.status in {"STALE_RECOMPOSITION", "STALE_COMPARISON", "STALE_CHAPTER", "STALE_BOOK_POINTER"}


def test_book_owned_pointer_moved_blocks(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    report, _pub = _ready_comparison_with_separator(store, book_id, project, "***")
    # A different publication approves a DIFFERENT separator for the same element,
    # moving the global separator pointer away from the recomposition's snapshot.
    publication2, candidate2 = _publish_separator(store, book_id, project, "###")
    store.decide_candidate(candidate2, "approved", "moved")
    ok, error = store.accept_recomposed_book(report["comparison_id"])
    assert not ok
    assert error.status in {"STALE_COMPARISON", "STALE_BOOK_POINTER"}


def test_chapter_pointer_moved_blocks(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    report = _ready_comparison(store, book_id, project)
    # Tamper the comparison's recorded Chapter pointer revision so it no longer
    # matches the accepted Book (backstop check 13, revalidated from disk).
    path = store._comparison_path(report["comparison_id"])
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    data["chapter_sources"][0]["revision"] = 999
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    ok, error = store.accept_recomposed_book(report["comparison_id"])
    assert not ok
    assert error.status == "STALE_BOOK_POINTER"
    assert error.reason == "CHAPTER_POINTER_MOVED"


def test_book_pointer_moved_blocks(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    report = _ready_comparison(store, book_id, project)
    # Tamper the comparison's base Book snapshot: acceptance revalidates the
    # current accepted Book against it and blocks on any drift (check 12).
    path = store._comparison_path(report["comparison_id"])
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    data["source_book_revision"] = 99
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    ok, error = store.accept_recomposed_book(report["comparison_id"])
    assert not ok
    assert error.status == "STALE_BOOK_POINTER"
    assert error.reason == "BOOK_REVISION_CHANGED"


def test_block_writes_no_artifact(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    recomposed, _pub = _recompose_default(store, book_id, project)
    ok, report = store.compare_book_recomposition(recomposed["recomposition_id"], _separator_edit(project, "==="))
    assert ok
    ok, error = store.accept_recomposed_book(report["comparison_id"])
    assert not ok
    assert error.result["visible_outputs_created"] is False
    assert not _accepted_pointer_path(project).exists()
    assert not _acceptances_dir(project).exists() or not list(_acceptances_dir(project).glob("*.yaml"))


# ----------------------------------------------------------------------------
# Scenarios 1-30
# ----------------------------------------------------------------------------

def test_scenario_01_exact_match_accepts(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    report = _ready_comparison(store, book_id, project)
    ok, result = store.accept_recomposed_book(report["comparison_id"])
    assert ok and result["accepted_book_revision"]["canonical"] is True


def test_scenario_02_book_owned_residual_blocks(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    recomposed, _pub = _recompose_default(store, book_id, project)
    ok, report = store.compare_book_recomposition(recomposed["recomposition_id"], _separator_edit(project, "==="))
    assert ok
    ok, error = store.accept_recomposed_book(report["comparison_id"])
    assert not ok and not _accepted_pointer_path(project).exists()


def test_scenario_03_chapter_owned_blocks(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    recomposed, _pub = _recompose_default(store, book_id, project)
    text = _book_md(project).read_text(encoding="utf-8")
    pattern = re.compile(r"(<!-- auteur:chapter id=chapter_02 [^>]*-->\n)(.*?)(\n<!-- auteur:end-chapter id=chapter_02 -->)", re.DOTALL)
    manuscript = project / "external_s03.md"
    manuscript.write_text(pattern.sub(lambda m: m.group(1) + m.group(2) + " S03" + m.group(3), text), encoding="utf-8")
    ok, report = store.compare_book_recomposition(recomposed["recomposition_id"], manuscript)
    assert ok and not store.accept_recomposed_book(report["comparison_id"])[0]


def test_scenario_04_structural_blocks(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    recomposed, _pub = _recompose_default(store, book_id, project)
    content = _book_md(project).read_text(encoding="utf-8")
    extra = "<!-- auteur:chapter id=chapter_99 expression_revision=1 -->\nUnknown.\n<!-- auteur:end-chapter id=chapter_99 -->"
    manuscript = project / "external_s04.md"
    manuscript.write_text(content.rstrip("\n") + "\n\n" + extra + "\n", encoding="utf-8")
    ok, report = store.compare_book_recomposition(recomposed["recomposition_id"], manuscript)
    assert ok and not store.accept_recomposed_book(report["comparison_id"])[0]


def test_scenario_05_marker_blocks(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    recomposed, _pub = _recompose_default(store, book_id, project)
    content = _book_md(project).read_text(encoding="utf-8")
    manuscript = project / "external_s05.md"
    manuscript.write_text(content.rstrip("\n") + "\n\n<!-- auteur:chapter broken\n", encoding="utf-8")
    ok, report = store.compare_book_recomposition(recomposed["recomposition_id"], manuscript)
    assert ok and not store.accept_recomposed_book(report["comparison_id"])[0]


def test_scenario_06_unresolved_blocks(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    recomposed, _pub = _recompose_default(store, book_id, project)
    content = _book_md(project).read_text(encoding="utf-8")
    manuscript = project / "external_s06.md"
    manuscript.write_text(re.sub(r"^<!-- auteur:.*?-->\s*$", "", content, flags=re.MULTILINE), encoding="utf-8")
    ok, report = store.compare_book_recomposition(recomposed["recomposition_id"], manuscript)
    assert ok and not store.accept_recomposed_book(report["comparison_id"])[0]


def test_scenario_07_forged_flag_blocks(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    recomposed, _pub = _recompose_default(store, book_id, project)
    ok, report = store.compare_book_recomposition(recomposed["recomposition_id"], _separator_edit(project, "==="))
    assert ok
    path = store._comparison_path(report["comparison_id"])
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    data["summary"]["ready_for_acceptance"] = True
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    assert not store.accept_recomposed_book(report["comparison_id"])[0]


def test_scenario_08_stale_comparison_blocks(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    recomposed, publication_id = _recompose_default(store, book_id, project)
    ok, report = store.compare_book_recomposition(recomposed["recomposition_id"], _faithful_manuscript(project))
    assert ok
    # Recomposition no longer proposed -> C2 comparison-freshness gate fails.
    path = store._recomposition_path(publication_id)
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    data["lifecycle"] = "accepted"
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    ok, error = store.accept_recomposed_book(report["comparison_id"])
    assert not ok and error.status in {"STALE_COMPARISON", "STALE_RECOMPOSITION"}


def test_scenario_09_stale_recomposition_blocks(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    recomposed, publication_id = _recompose_default(store, book_id, project)
    ok, report = store.compare_book_recomposition(recomposed["recomposition_id"], _faithful_manuscript(project))
    assert ok
    path = store._recomposition_path(publication_id)
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    data["title_rendering"] = "MUTATED"  # tamper without re-hashing
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    ok, error = store.accept_recomposed_book(report["comparison_id"])
    assert not ok and error.status == "STALE_RECOMPOSITION"


def test_scenario_10_external_manuscript_changed_blocks(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    recomposed, _pub = _recompose_default(store, book_id, project)
    manuscript = _faithful_manuscript(project)
    ok, report = store.compare_book_recomposition(recomposed["recomposition_id"], manuscript)
    assert ok
    manuscript.write_text("CHANGED", encoding="utf-8")
    assert not store.accept_recomposed_book(report["comparison_id"])[0]


def test_scenario_11_chapter_pointer_moved_blocks(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    report = _ready_comparison(store, book_id, project)
    cs = ChapterExpressionStore(project)
    cs.accept(cs.compose("chapter_01").artifact_id)
    assert not store.accept_recomposed_book(report["comparison_id"])[0]


def test_scenario_12_book_owned_pointer_moved_blocks(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    report, _pub = _ready_comparison_with_separator(store, book_id, project, "***")
    publication2, candidate2 = _publish_separator(store, book_id, project, "###")
    store.decide_candidate(candidate2, "approved", "moved")
    assert not store.accept_recomposed_book(report["comparison_id"])[0]


def test_scenario_13_book_pointer_moved_blocks(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    report = _ready_comparison(store, book_id, project)
    path = store._comparison_path(report["comparison_id"])
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    data["source_book_hash"] = "sha256:deadbeef"
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    ok, error = store.accept_recomposed_book(report["comparison_id"])
    assert not ok and error.status == "STALE_BOOK_POINTER"


def test_scenario_14_missing_pointer_target_blocks(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    recomposed, publication_id = _recompose_default(store, book_id, project)
    ok, report = store.compare_book_recomposition(recomposed["recomposition_id"], _faithful_manuscript(project))
    assert ok
    store._recomposition_path(publication_id).unlink()
    ok, error = store.accept_recomposed_book(report["comparison_id"])
    assert not ok and error.status == "MISSING_RECOMPOSITION"


def test_scenario_15_tampered_comparison_blocks(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    report = _ready_comparison(store, book_id, project)
    path = store._comparison_path(report["comparison_id"])
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    data["external_manuscript"]["content_hash"] = "sha256:forged"
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    ok, error = store.accept_recomposed_book(report["comparison_id"])
    assert not ok and error.reason == "COMPARISON_TAMPERED"


def test_scenario_16_tampered_recomposition_blocks(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    recomposed, publication_id = _recompose_default(store, book_id, project)
    ok, report = store.compare_book_recomposition(recomposed["recomposition_id"], _faithful_manuscript(project))
    assert ok
    path = store._recomposition_path(publication_id)
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    data["separator"] = "XXX"
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    ok, error = store.accept_recomposed_book(report["comparison_id"])
    assert not ok and error.reason == "RECOMPOSITION_TAMPERED"


def test_scenario_17_new_revision_immutable(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    report = _ready_comparison(store, book_id, project)
    ok, result = store.accept_recomposed_book(report["comparison_id"])
    path = project / "book" / "expression" / f"book_{result['accepted_book_revision']['book_id']}_v002_accepted.yaml"
    before = path.read_bytes()
    store.accept_recomposed_book(report["comparison_id"])  # duplicate
    assert path.read_bytes() == before


def test_scenario_18_prior_revision_preserved(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    report = _ready_comparison(store, book_id, project)
    v1 = project / "book" / "expression" / "book_v001.yaml"
    before = v1.read_bytes()
    store.accept_recomposed_book(report["comparison_id"])
    assert v1.read_bytes() == before


def test_scenario_19_pointer_moves_once(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    report = _ready_comparison(store, book_id, project)
    store.accept_recomposed_book(report["comparison_id"])
    assert len(store.current_accepted_book_pointer()["history"]) == 1


def test_scenario_20_chapter_pointers_unchanged(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    report = _ready_comparison(store, book_id, project)
    before = _chapter_accepted_files(project)
    store.accept_recomposed_book(report["comparison_id"])
    assert _chapter_accepted_files(project) == before


def test_scenario_21_book_owned_pointers_unchanged(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    report, _pub = _ready_comparison_with_separator(store, book_id, project, "***")
    before = _pointer_files(project)
    store.accept_recomposed_book(report["comparison_id"])
    assert _pointer_files(project) == before


def test_scenario_22_recomposition_remains_derived(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    recomposed, publication_id = _recompose_default(store, book_id, project)
    ok, report = store.compare_book_recomposition(recomposed["recomposition_id"], _faithful_manuscript(project))
    store.accept_recomposed_book(report["comparison_id"])
    assert store.load_recomposed_book(publication_id)["authority"] == "derived"


def test_scenario_23_comparison_remains_derived(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    report = _ready_comparison(store, book_id, project)
    store.accept_recomposed_book(report["comparison_id"])
    assert store.load_book_comparison(report["comparison_id"])["authority"] == "derived"


def test_scenario_24_duplicate_no_second_revision(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    report = _ready_comparison(store, book_id, project)
    store.accept_recomposed_book(report["comparison_id"])
    ok, result = store.accept_recomposed_book(report["comparison_id"])
    assert ok and result["status"] == "duplicate"
    revisions = list((project / "book" / "expression").glob("book_*_v*_accepted.yaml"))
    assert len(revisions) == 1
    assert len(list(_acceptances_dir(project).glob("*.yaml"))) == 1


def test_scenario_25_failure_before_pointer_rolls_back(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    report = _ready_comparison(store, book_id, project)
    # Pre-create the acceptance record file so staged validation fails (shadowing)
    # BEFORE any publish moves happen.
    ok, ctx = store._validate_acceptance_gate(report["comparison_id"])
    assert ok
    dest = _acceptances_dir(project) / f"{ctx['acceptance_id']}.yaml"
    dest.parent.mkdir(parents=True, exist_ok=True)
    # A record with the same acceptance_id but no matching source_comparison_id:
    # not a duplicate, so staged validation must catch the shadow before publish.
    dest.write_text(yaml.safe_dump({"acceptance_id": ctx["acceptance_id"]}, sort_keys=False), encoding="utf-8")
    ok, error = store.accept_recomposed_book(report["comparison_id"])
    # The pre-existing record is treated as a prior acceptance? It lacks
    # source_comparison_id, so it is NOT a duplicate; staged validation blocks it.
    assert not ok
    assert error.status == "STAGING_INVALID"
    assert not _accepted_pointer_path(project).exists()
    assert not list((project / "book" / "expression").glob("book_*_v*_accepted.yaml"))


def test_scenario_26_failure_during_moves_rolls_back(tmp_path: Path, monkeypatch) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    report = _ready_comparison(store, book_id, project)
    import shutil as _shutil

    calls = {"n": 0}
    real_move = _shutil.move

    def failing_move(src, dst):
        calls["n"] += 1
        if calls["n"] == 2:  # fail on the acceptance-record move (before pointer)
            raise OSError("simulated move failure")
        return real_move(src, dst)

    monkeypatch.setattr("auteur.expression.book_reconciliation.shutil.move", failing_move)
    try:
        store.accept_recomposed_book(report["comparison_id"])
        raised = False
    except OSError:
        raised = True
    assert raised
    assert not _accepted_pointer_path(project).exists()
    assert not list((project / "book" / "expression").glob("book_*_v*_accepted.yaml"))
    assert not list(_acceptances_dir(project).glob("*.yaml"))


def test_scenario_27_failure_during_pointer_restores_prior(tmp_path: Path, monkeypatch) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    # First, a successful acceptance so a prior pointer exists.
    report1 = _ready_comparison(store, book_id, project)
    store.accept_recomposed_book(report1["comparison_id"])
    prior_bytes = _accepted_pointer_path(project).read_bytes()

    # A second acceptance that fails exactly at the atomic pointer replace.
    report2 = _ready_comparison(store, book_id, project)

    from pathlib import Path as _Path
    real_replace = _Path.replace

    def failing_replace(self, target):
        if _Path(target).name == "accepted-book-pointer.yaml":
            raise OSError("simulated pointer replace failure")
        return real_replace(self, target)

    monkeypatch.setattr(_Path, "replace", failing_replace)
    try:
        store.accept_recomposed_book(report2["comparison_id"])
        raised = False
    except OSError:
        raised = True
    assert raised
    # Prior pointer restored byte-for-byte; the failed revision rolled back.
    assert _accepted_pointer_path(project).read_bytes() == prior_bytes
    assert not (project / "book" / "expression" / f"book_{book_id.split(':')[0]}_v003_accepted.yaml").exists()


def test_scenario_28_concurrent_pointer_change_aborts(tmp_path: Path, monkeypatch) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    report = _ready_comparison(store, book_id, project)

    real_stage = store._stage_acceptance

    def rogue_stage(*args, **kwargs):
        # Simulate a concurrent writer moving the pointer after the gate ran.
        path = store._accepted_book_pointer_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(yaml.safe_dump({"pointer_id": "rogue", "current_revision": 99, "history": []}, sort_keys=False), encoding="utf-8")
        return real_stage(*args, **kwargs)

    monkeypatch.setattr(store, "_stage_acceptance", rogue_stage)
    ok, error = store.accept_recomposed_book(report["comparison_id"])
    assert not ok
    assert error.status == "POINTER_CHANGED"
    assert error.reason == "BOOK_POINTER_CHANGED"
    # No accepted revision or record leaked; the rogue pointer remains.
    assert not list((project / "book" / "expression").glob("book_*_v*_accepted.yaml"))
    assert not list(_acceptances_dir(project).glob("*.yaml"))


def test_scenario_29_provenance_complete(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    report, publication_id = _ready_comparison_with_separator(store, book_id, project, "***")
    ok, result = store.accept_recomposed_book(report["comparison_id"])
    assert ok
    revision = result["accepted_book_revision"]
    for key in ("source_recomposition_id", "source_recomposition_hash", "source_comparison_id",
                "source_comparison_hash", "source_publication_id", "accepted_chapter_sources",
                "accepted_book_owned_sources", "previous_accepted_book", "acceptance_id"):
        assert key in revision
    assert revision["source_publication_id"] == publication_id
    assert all("pointer_id" in c for c in revision["accepted_chapter_sources"])
    assert any(s["owned_kind"] == "separator" for s in revision["accepted_book_owned_sources"])


def test_scenario_30_no_reconciliation_completion(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    recomposed, publication_id = _recompose_default(store, book_id, project)
    ok, report = store.compare_book_recomposition(recomposed["recomposition_id"], _faithful_manuscript(project))
    store.accept_recomposed_book(report["comparison_id"])
    manifest = store.inspect_book_publication(publication_id)
    assert manifest.get("acceptance_status") == "none"
    for path in project.rglob("*"):
        assert "completion" not in path.name.lower()


# ----------------------------------------------------------------------------
# Dogfood scenarios
# ----------------------------------------------------------------------------

def test_dogfood_1_exact_match_accepts(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    report = _ready_comparison(store, book_id, project)
    ok, result = store.accept_recomposed_book(report["comparison_id"], reason="Approved after exact reconciliation")
    assert ok
    assert result["accepted_book_revision"]["revision"] == 2
    assert store.current_accepted_book_pointer()["current_revision"] == 2


def test_dogfood_2_book_owned_residual_blocks(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    recomposed, _pub = _recompose_default(store, book_id, project)
    ok, report = store.compare_book_recomposition(recomposed["recomposition_id"], _separator_edit(project, "~~~"))
    assert ok
    ok, error = store.accept_recomposed_book(report["comparison_id"])
    assert not ok
    assert not _accepted_pointer_path(project).exists()


def test_dogfood_3_stale_comparison_blocks(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    recomposed, _pub = _recompose_default(store, book_id, project)
    manuscript = _faithful_manuscript(project)
    ok, report = store.compare_book_recomposition(recomposed["recomposition_id"], manuscript)
    assert ok
    manuscript.write_text(manuscript.read_text(encoding="utf-8") + "\nDRIFT\n", encoding="utf-8")
    assert not store.accept_recomposed_book(report["comparison_id"])[0]


def test_dogfood_4_concurrent_pointer_change(tmp_path: Path, monkeypatch) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    report = _ready_comparison(store, book_id, project)
    real_stage = store._stage_acceptance

    def rogue_stage(*args, **kwargs):
        path = store._accepted_book_pointer_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(yaml.safe_dump({"pointer_id": "rogue2", "current_revision": 50, "history": []}, sort_keys=False), encoding="utf-8")
        return real_stage(*args, **kwargs)

    monkeypatch.setattr(store, "_stage_acceptance", rogue_stage)
    ok, error = store.accept_recomposed_book(report["comparison_id"])
    assert not ok and error.status == "POINTER_CHANGED"


def test_dogfood_5_duplicate_acceptance(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    report = _ready_comparison(store, book_id, project)
    ok1, first = store.accept_recomposed_book(report["comparison_id"])
    ok2, second = store.accept_recomposed_book(report["comparison_id"])
    assert ok1 and ok2
    assert second["status"] == "duplicate"
    assert second["prior_acceptance_id"] == first["acceptance_record"]["acceptance_id"]


def test_dogfood_6_full_acceptance_chain(tmp_path: Path) -> None:
    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    recomposed, publication_id = _recompose_default(store, book_id, project)
    ok, report = store.compare_book_recomposition(recomposed["recomposition_id"], _faithful_manuscript(project))
    assert ok and report["summary"]["ready_for_acceptance"] is True
    ok, result = store.accept_recomposed_book(report["comparison_id"])
    assert ok
    assert store.current_accepted_book_pointer()["accepted_book_expression_id"] == result["accepted_book_revision"]["book_expression_id"]
    # Evidence chain preserved end to end.
    assert store.load_recomposed_book(publication_id)["authority"] == "derived"
    assert store.load_book_comparison(report["comparison_id"])["authority"] == "derived"


# ----------------------------------------------------------------------------
# CLI integration
# ----------------------------------------------------------------------------

def test_cli_accept_success(tmp_path: Path, capsys) -> None:
    from auteur.cli import main

    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    report = _ready_comparison(store, book_id, project)
    rc = main(["expression", "accept-recomposed-book", report["comparison_id"],
               "--reason", "ok", "--project", str(project)])
    out = capsys.readouterr().out
    assert rc == 0
    assert "Book accepted: yes" in out
    assert "Accepted revision: 2" in out
    assert "Accepted Book pointer moved: yes" in out
    assert "Reconciliation completed: no" in out


def test_cli_accept_blocked(tmp_path: Path, capsys) -> None:
    from auteur.cli import main

    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    recomposed, _pub = _recompose_default(store, book_id, project)
    ok, report = store.compare_book_recomposition(recomposed["recomposition_id"], _separator_edit(project, "==="))
    assert ok
    rc = main(["expression", "accept-recomposed-book", report["comparison_id"], "--project", str(project)])
    out = capsys.readouterr().out
    assert rc == 1
    assert "blocked" in out.lower()
    assert "No accepted Book revision" in out


def test_cli_accept_json(tmp_path: Path, capsys) -> None:
    from auteur.cli import main

    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    report = _ready_comparison(store, book_id, project)
    rc = main(["expression", "accept-recomposed-book", report["comparison_id"], "--project", str(project), "--json"])
    out = capsys.readouterr().out
    assert rc == 0
    assert "acceptance_record" in out
    assert "book_expression" in out


def test_cli_inspect_acceptance(tmp_path: Path, capsys) -> None:
    from auteur.cli import main

    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    report = _ready_comparison(store, book_id, project)
    ok, result = store.accept_recomposed_book(report["comparison_id"])
    acceptance_id = result["acceptance_record"]["acceptance_id"]
    rc = main(["expression", "inspect-book-acceptance", acceptance_id, "--project", str(project)])
    out = capsys.readouterr().out
    assert rc == 0
    assert acceptance_id in out
    assert "Accepted Book" in out


def test_cli_inspect_acceptance_json_shows_provenance(tmp_path: Path, capsys) -> None:
    from auteur.cli import main

    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    report = _ready_comparison(store, book_id, project)
    ok, result = store.accept_recomposed_book(report["comparison_id"])
    acceptance_id = result["acceptance_record"]["acceptance_id"]
    rc = main(["expression", "inspect-book-acceptance", acceptance_id, "--project", str(project), "--json"])
    out = capsys.readouterr().out
    assert rc == 0
    assert "pointer_transition" in out
    assert "source_comparison_id" in out


def test_cli_accept_duplicate(tmp_path: Path, capsys) -> None:
    from auteur.cli import main

    project, book_id = _make_book(tmp_path)
    store = BookReconciliationStore(project)
    report = _ready_comparison(store, book_id, project)
    store.accept_recomposed_book(report["comparison_id"])
    rc = main(["expression", "accept-recomposed-book", report["comparison_id"], "--project", str(project)])
    out = capsys.readouterr().out
    assert rc == 0
    assert "duplicate" in out.lower()
