"""Architecture-to-Book impact, as the Studio reads it, and reconciliation through the Book's own owner.

The impact study project (``scripts/seed_book_impact_study.py``) holds six Books after two applied
working-Architecture revisions: Book 24 records a concept that changed and one that was removed; Book 25
records the same and its own source changed; Book 26 records only unchanged concepts; Book 27 has only a
prepared develop request; Book 28 only source items; Book 29 a damaged record. Reading never writes.
"""
import hashlib
import json
import shutil
import sys
from pathlib import Path

import pytest

from auteur.beginner.persistence import BeginnerConcurrencyError
from auteur.beginner.studio_book_development import (
    apply_book_revision, complete_book_revision, prepare_book_revision, project_book_development,
)
from auteur.beginner.studio_series_context import project_series_context
from auteur.beginner.studio_store import CanvasStore
from auteur.host_agent import HostAgentRequest, build_host_agent_response
from auteur.series.working_book_architecture import (
    book_apply_review, book_complete, book_prepare, book_series_references,
)

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))
import seed_book_impact_study as seed  # noqa: E402

CANVAS = seed.SPRING
CHANGED, REMOVED = seed.CHANGED_NODE, seed.REMOVED_NODE


@pytest.fixture(scope="module")
def pristine(tmp_path_factory):
    root = tmp_path_factory.mktemp("book-impact") / "impact"
    seed.seed_impact(root)
    return root


@pytest.fixture
def project(pristine, tmp_path):
    target = tmp_path / "impact"
    shutil.copytree(pristine, target)
    return target


def working(project: Path) -> dict:
    return project_series_context(project, CANVAS)["sources"]["working_books"]


def book(project: Path, number: int) -> dict:
    return next(b for b in working(project)["books"] if b["book_number"] == number)


def by_status(entry: dict) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    for ref in entry["references"]:
        out.setdefault(ref["status"], []).append(ref["node_id"])
    return out


def snapshot(root: Path, *, skip: Path | None = None) -> dict[str, str]:
    return {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(root.rglob("*")) if p.is_file() and not p.name.endswith(".lock")
            and (skip is None or skip not in p.parents)}


def books_dir(project: Path) -> Path:
    return project / ".auteur/beginner/studio/canvases" / CANVAS / "architecture/books"


def current(project: Path, number: int) -> dict:
    return json.loads((books_dir(project) / str(number) / "current.json").read_text(encoding="utf-8"))


def respond(request: dict, artifact: dict) -> dict:
    return build_host_agent_response(HostAgentRequest(**request), json.dumps(artifact), runtime="test-agent").model_dump()


def reconciled(project: Path, number: int) -> dict:
    """The coding agent's whole-Book answer: stop citing the removed concept; restate what it changes."""
    artifact = json.loads(json.dumps(current(project, number)["artifact"]))

    def visit(node):
        if isinstance(node, dict):
            refs = node.get("refs")
            if isinstance(refs, list) and any(r.get("id") == REMOVED for r in refs):
                node["refs"] = [r for r in refs if r.get("id") != REMOVED] or [{"kind": "series_node", "id": "str_hollow_gate"}]
                if {"kind": "series_node", "id": "str_hollow_gate"} not in node["refs"]:
                    node["refs"].append({"kind": "series_node", "id": "str_hollow_gate"})
                if "provenance" in node:
                    node.pop("provenance")
                    node["attribution"], node["epistemic_status"] = "agent_proposed", "asserted"
            for value in node.values():
                visit(value)
        elif isinstance(node, list):
            for value in node:
                visit(value)
    visit(artifact)
    return artifact


def test_each_book_reports_its_recorded_impact_and_nothing_else(project):
    w = working(project)
    assert w["architecture_revisions"] == 3
    b24, b25, b26 = book(project, 24), book(project, 25), book(project, 26)
    # Case B and C: a recorded concept changed, another no longer resolves.
    assert by_status(b24)["changed"] == [CHANGED] and by_status(b24)["removed"] == [REMOVED]
    assert len(by_status(b24)["unchanged"]) == 19 and "unrecorded" not in by_status(b24)
    assert b24["architecture_revisions_since"] == 2 and b24["series_changed"] and not b24["source_changed"]
    # Case D on top: Book 25's own source changed, reported apart from the Architecture.
    assert by_status(b25)["changed"] == [CHANGED] and b25["source_changed"]
    # Case A: the Architecture changed; every recorded concept is unchanged. Still out of date.
    assert set(by_status(b26)) == {"unchanged"} and b26["series_changed"] and b26["freshness"] == "stale"
    assert b26["architecture_revisions_since"] == 1
    # Not a working Book: a prepared request, source items only, and a damaged record.
    assert w["without_working_book"] == [{"book_number": 27, "requested": True}, {"book_number": 28, "requested": False}]
    b29 = book(project, 29)
    assert b29["state"] == "unreadable" and "reason" in b29 and "references" not in b29


def test_changed_and_removed_concepts_carry_the_version_the_book_recorded(project):
    refs = {r["node_id"]: r for r in book(project, 24)["references"]}
    changed, removed = refs[CHANGED], refs[REMOVED]
    assert changed["recorded"]["title"] == "Ledger engine" and changed["fields_changed"] == ["summary"]
    assert changed["current"]["summary"] == changed["recorded"]["summary"] + seed.LEDGER_REWORDING
    assert changed["recorded"]["found_in"]["record"] == "book_request"
    assert removed["current"] is None and removed["recorded"]["title"] == "Gate Table" and not removed["present"]
    # The exact citing elements, as recorded; nothing is added from wording.
    assert sorted(e["id"] for e in removed["elements"]) == ["inh-gate-independence", "later-cohort-seat"]
    assert "eng-record-form" in {e["id"] for e in changed["elements"]}
    assert "th_reading" not in refs  # the second revision changed it, and no Book records it


def test_a_recorded_version_is_used_only_when_its_fingerprint_matches(project):
    store = CanvasStore(project, CANVAS)
    request_dir = books_dir(project) / "24" / "requests" / current(project, 24)["request_sha256"]
    # Without the Book's own request, the Architecture's revision chain still holds the version it recorded.
    shutil.rmtree(request_dir)
    refs = {r["node_id"]: r for r in book_series_references(store, 24)["references"]}
    assert refs[CHANGED]["recorded"]["found_in"]["record"] == "architecture_revision"
    assert refs[REMOVED]["recorded"]["title"] == "Gate Table"
    # A fingerprint that matches no kept version gives no version: nothing is reconstructed.
    record = current(project, 24)
    record["series_nodes"][REMOVED] = "0" * 64
    (books_dir(project) / "24" / "current.json").write_text(json.dumps(record), encoding="utf-8")
    refs = {r["node_id"]: r for r in book_series_references(store, 24)["references"]}
    assert refs[REMOVED]["status"] == "removed" and refs[REMOVED]["recorded"] is None


def test_reading_the_impact_writes_nothing(project):
    before = snapshot(project)
    working(project)
    project_book_development(project, CANVAS, 24)
    assert snapshot(project) == before


def test_reconciling_one_book_through_its_owner_brings_only_that_book_up_to_date(project):
    others = {n: snapshot(books_dir(project) / str(n)) for n in (25, 26, 29)}
    outside = snapshot(project, skip=books_dir(project))
    view = project_book_development(project, CANVAS, 24)
    # The Studio offers an out-of-date Book only a whole-Book revision.
    with pytest.raises(BeginnerConcurrencyError, match="only a whole-Book revision"):
        prepare_book_revision(project, CANVAS, 24, {"instruction": "Only this.", "targets": ["eng-record-form"],
                                                    "expected_book_request_sha256": view["book"]["request_sha256"]})
    view = prepare_book_revision(project, CANVAS, 24, {
        "instruction": "Reconcile Book 24 with the revised working Architecture.", "holistic": True,
        "expected_book_request_sha256": view["book"]["request_sha256"]})
    # Preparing and completing change nothing the impact reads.
    assert by_status(book(project, 24))["removed"] == [REMOVED]
    view = complete_book_revision(project, CANVAS, 24, respond(view["request"], reconciled(project, 24)))
    assert view["phase"] == "review_ready" and book(project, 24)["freshness"] == "stale"
    applied = apply_book_revision(project, CANVAS, 24, {"request_sha256": view["pending"]["request_sha256"]})
    assert applied["application"] == {"result": "applied", "request_sha256": view["pending"]["request_sha256"],
                                      "currentness": "current"}
    after = book(project, 24)
    assert after["freshness"] == "ready" and set(by_status(after)) == {"unchanged"}
    assert REMOVED not in {r["node_id"] for r in after["references"]}
    assert after["last_applied"]["currentness"] == "current" and after["architecture_revisions_since"] == 0
    assert {n: snapshot(books_dir(project) / str(n)) for n in (25, 26, 29)} == others
    assert snapshot(project, skip=books_dir(project)) == outside
    assert by_status(book(project, 25))["removed"] == [REMOVED]


def test_a_partial_revision_of_an_out_of_date_book_does_not_record_it_as_current(project):
    """The owner's invariant, through its own entry points (the CLI path calls these without expectations)."""
    store = CanvasStore(project, CANVAS)
    before = current(project, 24)
    # Every reference in a revised Book must resolve, so a partial revision of Book 24 has to include the
    # two elements that cite the removed concept; it changes only those.
    prepared = book_prepare(store, 24, instruction="Stop citing the Gate table.",
                            targets=("inh-gate-independence", "later-cohort-seat"))
    book_complete(store, 24, respond(prepared["request"], reconciled(project, 24)))
    sha = prepared["pending_request_sha256"]
    result = book_apply_review(store, 24, sha)
    assert result["result"] == "applied" and result["currentness"] == "kept_baseline"
    after = current(project, 24)
    assert after["revision_number"] == 1 and after["request_sha256"] == sha
    assert after["series_request_sha256"] == before["series_request_sha256"]
    assert after["source_sha256"] == before["source_sha256"]
    assert after["series_nodes"][CHANGED] == before["series_nodes"][CHANGED]
    assert after["lineage"][-1]["currentness"] == "kept_baseline"
    # The Book changed, and it is still out of date: every recorded impact is still shown.
    view = book(project, 24)
    assert view["freshness"] == "stale" and by_status(view)["changed"] == [CHANGED]
    assert "removed" not in by_status(view) and view["last_applied"]["currentness"] == "kept_baseline"
    assert view["architecture_revisions_since"] == 2
    assert book_apply_review(store, 24, sha)["result"] == "already_applied"
    assert current(project, 24) == after


def test_a_reconciliation_made_stale_before_apply_promotes_nothing(project):
    view = project_book_development(project, CANVAS, 26)
    view = prepare_book_revision(project, CANVAS, 26, {
        "instruction": "Bring Book 26 up to date.", "holistic": True,
        "expected_book_request_sha256": view["book"]["request_sha256"]})
    view = complete_book_revision(project, CANVAS, 26, respond(view["request"], current(project, 26)["artifact"]))
    before = current(project, 26)
    seed.reword_unrelated(CanvasStore(project, CANVAS))  # the Architecture changes again
    stale = project_book_development(project, CANVAS, 26)
    assert stale["phase"] == "stale"
    with pytest.raises(BeginnerConcurrencyError, match="working context changed"):
        apply_book_revision(project, CANVAS, 26, {"request_sha256": view["pending"]["request_sha256"]})
    assert current(project, 26) == before and book(project, 26)["freshness"] == "stale"
    assert book(project, 26)["architecture_revisions_since"] == 2


def test_a_partial_revision_never_records_a_concept_the_book_had_no_fingerprint_for(project):
    """A concept the Book already cited without a kept fingerprint stays unrecorded; it is not made 'unchanged'."""
    store = CanvasStore(project, CANVAS)
    record = current(project, 24)
    del record["series_nodes"]["eng_old_hand"]
    (books_dir(project) / "24" / "current.json").write_text(json.dumps(record), encoding="utf-8")
    assert by_status(book(project, 24))["unrecorded"] == ["eng_old_hand"]
    prepared = book_prepare(store, 24, instruction="Stop citing the Gate table.",
                            targets=("inh-gate-independence", "later-cohort-seat"))
    book_complete(store, 24, respond(prepared["request"], reconciled(project, 24)))
    assert book_apply_review(store, 24, prepared["pending_request_sha256"])["currentness"] == "kept_baseline"
    assert "eng_old_hand" not in current(project, 24)["series_nodes"]
    assert by_status(book(project, 24))["unrecorded"] == ["eng_old_hand"]


def test_a_revision_history_that_cannot_be_read_whole_says_so(project):
    arch = project / ".auteur/beginner/studio/canvases" / CANVAS / "architecture"
    newest = json.loads((arch / "current.json").read_text(encoding="utf-8"))["request_sha256"]
    (arch / "requests" / newest / "review.json").write_text("{damaged", encoding="utf-8")
    w = working(project)
    b24 = next(b for b in w["books"] if b["book_number"] == 24)
    assert b24["architecture_revisions_since"] is None and b24["architecture_chain_complete"] is False
    assert by_status(b24)["changed"] == [CHANGED]  # the comparison with the current Architecture still holds


def test_without_a_working_architecture_nothing_is_said_about_any_concept(project):
    arch = project / ".auteur/beginner/studio/canvases" / CANVAS / "architecture"
    (arch / "current.json").unlink()
    refs = book_series_references(CanvasStore(project, CANVAS), 26)["references"]
    assert {r["status"] for r in refs} == {"architecture_unavailable"}
