"""Developing a working Book through its own owner, as the Studio exposes it.

The Working Book Architecture owner prepares, validates, reviews and applies. The Studio adapter adds only
two author-facing guards before prepare (the Book is still the revision the author read, and a waiting
request is replaced only on request) and reports the owner's lifecycle in its own terms. Applying writes
the Book's own records and nothing else: not the working Architecture, the canvas, the Series plan or
the Directions.
"""
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from auteur.beginner.persistence import BeginnerConcurrencyError
from auteur.beginner.studio_book_development import (
    apply_book_revision, complete_book_revision, prepare_book_revision, preview_book_scope,
    project_book_development,
)
from auteur.beginner.studio_series_context import project_series_context
from auteur.beginner.studio_store import CanvasStore
from auteur.host_agent import HostAgentRequest, build_host_agent_response

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))
import seed_series_context_study as seed  # noqa: E402

CANVAS = seed.SPRING
TARGET = "eng-record-form"  # an Engine of Book 24 that records a reference to the Ledger engine (eng_ledger)
ADDED = " Refusing the count costs the cohort its season's water credit, entered where the Council can see it."


@pytest.fixture(scope="module")
def pristine(tmp_path_factory):
    root = tmp_path_factory.mktemp("book-dev") / "linked"
    seed.seed_spring(root)
    return root


@pytest.fixture
def project(pristine, tmp_path):
    import shutil
    target = tmp_path / "linked"
    shutil.copytree(pristine, target)
    return target


def book_dir(project: Path) -> Path:
    return project / ".auteur/beginner/studio/canvases" / CANVAS / "architecture/books/24"


def current(project: Path) -> dict:
    return json.loads((book_dir(project) / "current.json").read_text(encoding="utf-8"))


def explicit(element: dict) -> dict:
    """Restate a legacy element in the explicit form, as the owner requires for any changed element."""
    if "provenance" in element:
        element.pop("provenance")
        element["attribution"], element["epistemic_status"] = "agent_proposed", "asserted"
    return element


def revised(project: Path, edit) -> dict:
    artifact = json.loads(json.dumps(current(project)["artifact"]))
    edit(artifact)
    return artifact


def respond(view: dict, artifact: dict) -> dict:
    return build_host_agent_response(HostAgentRequest(**view["request"]), json.dumps(artifact),
                                     runtime="test-agent").model_dump()


def edit_target(artifact: dict) -> None:
    for element in artifact["engines"]:
        if element["id"] == TARGET:
            explicit(element)["text"] += ADDED


def prepare(project: Path, **extra) -> dict:
    view = project_book_development(project, CANVAS, 24)
    payload = {"instruction": "Make the cost of refusing the count visible.", "targets": [TARGET],
               "expected_book_request_sha256": view["book"]["request_sha256"], **extra}
    return prepare_book_revision(project, CANVAS, 24, payload)


def fingerprint_outside_book(project: Path) -> dict:
    """Every project file except this Book's own records and lock files."""
    book = book_dir(project)
    out = {}
    for path in sorted(project.rglob("*")):
        if path.is_file() and book not in path.parents and not path.name.endswith(".lock"):
            out[str(path.relative_to(project))] = hashlib.sha256(path.read_bytes()).hexdigest()
    return out


def cli(project: Path, *args: str) -> tuple[int, dict]:
    env = dict(os.environ, PYTHONPATH=str(REPO / "src"), PYTHONUTF8="1")
    result = subprocess.run(
        [sys.executable, "-m", "auteur.series.working_book_architecture", "--project", str(project),
         "--canvas", CANVAS, *args], capture_output=True, text=True, encoding="utf-8", env=env, check=False)
    return result.returncode, json.loads(result.stdout)


def test_projection_reads_the_book_its_elements_and_no_pending_request(project):
    view = project_book_development(project, CANVAS, 24)
    assert view["state"] == "working" and view["phase"] == "none" and view["authority"] == "working_noncanonical"
    assert view["book"]["title"] == "The Uncounted Crew" and view["book"]["revision_number"] == 0
    element = next(e for e in view["elements"] if e["id"] == TARGET)
    assert element["collection"] == "engines" and "eng_ledger" in element["series_refs"]
    assert element["commitment_authority"] == "agent_working"
    assert preview_book_scope(project, CANVAS, 24, {"targets": [TARGET]}) == {
        "targets": [TARGET], "dependents": ["edge-capability-hands", "edge-capability-lineage"],
        "permitted_ids": ["edge-capability-hands", "edge-capability-lineage", TARGET]}


def test_the_whole_loop_through_the_owner_and_its_cli_changes_only_the_book(project):
    outside = fingerprint_outside_book(project)
    view = prepare(project)
    assert view["phase"] == "awaiting_coding_agent" and view["book"]["revision_number"] == 0
    assert view["pending"]["permitted_ids"] == ["edge-capability-hands", "edge-capability-lineage", TARGET]
    assert "book-show --book 24" in view["handoff"]["show"] and "book-complete-file" in view["handoff"]["complete"]
    # The coding agent's side, in a fresh process, through the owner's own commands.
    code, shown = cli(project, "book-show", "--book", "24")
    assert code == 0 and shown["status"] == "awaiting_host_agent"
    assert shown["pending_request_sha256"] == view["pending"]["request_sha256"]
    candidate = project / "revised.json"
    candidate.write_text(json.dumps(revised(project, edit_target)), encoding="utf-8")
    code, completed = cli(project, "book-complete-file", "--book", "24", "--candidate", str(candidate))
    assert code == 0 and completed["status"] == "review_ready"
    candidate.unlink()
    view = project_book_development(project, CANVAS, 24)
    review = view["review"]
    assert view["phase"] == "review_ready" and review["applicable"] and "candidate" not in review
    assert [c["id"] for c in review["changes"]["changed"]] == [TARGET]
    assert {c["id"] for c in review["consequence_candidates"]} == {"edge-capability-hands", "edge-capability-lineage"}
    assert all(s["series_state"] == "unchanged" for s in review["series_consequences"])
    assert current(project)["artifact"] != revised(project, edit_target)  # still the baseline until Apply
    applied = apply_book_revision(project, CANVAS, 24, {"request_sha256": review["request_sha256"]})
    assert applied["application"]["result"] == "applied" and applied["phase"] == "none"
    assert applied["book"]["revision_number"] == 1
    assert applied["book"]["last_applied"]["changed"] == [TARGET]
    assert fingerprint_outside_book(project) == outside  # Architecture, canvas and every other plan untouched
    again = apply_book_revision(project, CANVAS, 24, {"request_sha256": review["request_sha256"]})
    assert again["application"]["result"] == "already_applied" and again["book"]["revision_number"] == 1
    code, resumed = cli(project, "book-resume", "--book", "24")  # fresh-process recovery
    assert code == 0 and resumed["revision"]["number"] == 1 and resumed["freshness"] == "ready"
    text = next(e["text"] for e in resumed["artifact"]["engines"] if e["id"] == TARGET)
    assert text.endswith(ADDED)
    context = project_series_context(project, CANVAS)
    book = context["sources"]["working_books"]["books"][0]
    assert book["revision_number"] == 1 and book["last_applied"]["changed"] == [TARGET]
    assert book["development"] is None


def test_prepare_refuses_a_book_that_changed_since_it_was_read(project):
    stale_read = project_book_development(project, CANVAS, 24)["book"]["request_sha256"]
    view = prepare(project)
    apply_book_revision(project, CANVAS, 24, {"request_sha256": complete_book_revision(
        project, CANVAS, 24, respond(view, revised(project, edit_target)))["pending"]["request_sha256"]})
    with pytest.raises(BeginnerConcurrencyError, match="changed since you read it"):
        prepare_book_revision(project, CANVAS, 24, {"instruction": "x", "targets": [TARGET],
                                                    "expected_book_request_sha256": stale_read})


def test_a_waiting_request_is_replaced_only_on_request_and_its_review_is_then_superseded(project):
    first = prepare(project)
    first = complete_book_revision(project, CANVAS, 24, respond(first, revised(project, edit_target)))
    with pytest.raises(BeginnerConcurrencyError, match="confirm that this request replaces it"):
        prepare(project)
    second = prepare(project, replace_pending_request_sha256=first["pending"]["request_sha256"])
    assert second["phase"] == "awaiting_coding_agent"
    assert second["pending"]["request_sha256"] != first["pending"]["request_sha256"]
    with pytest.raises(BeginnerConcurrencyError, match="superseded"):
        apply_book_revision(project, CANVAS, 24, {"request_sha256": first["pending"]["request_sha256"]})
    assert current(project)["request_sha256"] == first["book"]["request_sha256"]


def test_an_architecture_change_after_prepare_makes_the_request_stale_and_unusable(project):
    view = prepare(project)
    seed.remove_node(CanvasStore(project, CANVAS), seed.REMOVED_NODE)  # an applied Architecture revision
    stale = project_book_development(project, CANVAS, 24)
    assert stale["phase"] == "stale" and stale["pending"]["context_changed"]
    before = current(project)
    with pytest.raises(BeginnerConcurrencyError, match="changed after this request"):
        complete_book_revision(project, CANVAS, 24, respond(view, revised(project, edit_target)))
    assert project_book_development(project, CANVAS, 24)["pending"]["stale_response_kept"]
    assert current(project) == before


def test_a_review_made_stale_by_an_architecture_change_cannot_be_applied(project):
    view = prepare(project)
    view = complete_book_revision(project, CANVAS, 24, respond(view, revised(project, edit_target)))
    assert view["phase"] == "review_ready"
    seed.remove_node(CanvasStore(project, CANVAS), seed.REMOVED_NODE)
    assert project_book_development(project, CANVAS, 24)["phase"] == "stale"
    before = current(project)
    with pytest.raises(BeginnerConcurrencyError, match="working context changed"):
        apply_book_revision(project, CANVAS, 24, {"request_sha256": view["pending"]["request_sha256"]})
    assert current(project) == before


def test_changes_outside_the_permitted_elements_block_apply(project):
    view = prepare(project)

    def beyond(artifact):
        edit_target(artifact)
        explicit(artifact["engines"][0])["text"] += " (changed outside the request)"
    view = complete_book_revision(project, CANVAS, 24, respond(view, revised(project, beyond)))
    assert view["phase"] == "review_blocked" and not view["review"]["applicable"]
    assert [u["id"] for u in view["review"]["unexpected_changes"]] == [current(project)["artifact"]["engines"][0]["id"]]
    before = current(project)
    with pytest.raises(ValueError, match="unexpected changes block application"):
        apply_book_revision(project, CANVAS, 24, {"request_sha256": view["pending"]["request_sha256"]})
    assert current(project) == before


def test_an_invalid_response_is_refused_and_leaves_the_request_open(project):
    view = prepare(project)

    def broken(artifact):
        edit_target(artifact)
        artifact["engines"][0]["attribution"] = "accepted"
    with pytest.raises(ValueError, match="Working Book contract"):
        complete_book_revision(project, CANVAS, 24, respond(view, revised(project, broken)))
    after = project_book_development(project, CANVAS, 24)
    assert after["phase"] == "awaiting_coding_agent" and after["review"] is None


def test_a_revision_cannot_settle_an_author_decision(project):
    decision = current(project)["artifact"]["open_author_decisions"][0]["id"]
    view = project_book_development(project, CANVAS, 24)
    view = prepare_book_revision(project, CANVAS, 24, {
        "instruction": "Decide it.", "targets": [decision], "expected_book_request_sha256": view["book"]["request_sha256"]})

    def settle(artifact):
        element = artifact["open_author_decisions"][0]
        explicit(element)["epistemic_status"] = "asserted"
        element["text"] += " Decided."
    before = current(project)
    with pytest.raises(ValueError, match="must be derived from its Series question and unresolved|cannot be settled"):
        complete_book_revision(project, CANVAS, 24, respond(view, revised(project, settle)))
    assert current(project) == before
    assert project_book_development(project, CANVAS, 24)["phase"] == "awaiting_coding_agent"


def test_missing_and_damaged_books_offer_nothing(project):
    assert project_book_development(project, CANVAS, 23)["state"] == "no_book"
    (book_dir(project) / "current.json").write_text("{not json", encoding="utf-8")
    view = project_book_development(project, CANVAS, 24)
    assert view["state"] == "unreadable" and "elements" not in view
    context = project_series_context(project, CANVAS)
    assert context["sources"]["working_books"]["books"][0]["state"] == "unreadable"


def test_prepare_validates_its_payload(project):
    sha = project_book_development(project, CANVAS, 24)["book"]["request_sha256"]
    with pytest.raises(ValueError, match="expected_book_request_sha256"):
        prepare_book_revision(project, CANVAS, 24, {"instruction": "x", "targets": [TARGET]})
    with pytest.raises(ValueError, match="list of element ids"):
        prepare_book_revision(project, CANVAS, 24, {"instruction": "x", "targets": TARGET,
                                                    "expected_book_request_sha256": sha})
    with pytest.raises(ValueError, match="unknown target elements"):
        prepare_book_revision(project, CANVAS, 24, {"instruction": "x", "targets": ["nope"],
                                                    "expected_book_request_sha256": sha})
    with pytest.raises(ValueError, match="request_sha256"):
        apply_book_revision(project, CANVAS, 24, {"request_sha256": "latest"})
    assert project_book_development(project, CANVAS, 24)["phase"] == "none"
