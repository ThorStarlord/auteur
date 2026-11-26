"""The working Architecture's question history, read through the owners, on the Spring Ledger study.

The projection presents what each revision recorded: a continuing question's identity and its formulations, the reason each
revision records for a change, wording that has no identity, a question no longer open, and every version that cannot be
read named as a gap. Books refer to a question only by its recorded identity. Reading changes nothing.
"""
import json
import shutil
import sys
from pathlib import Path

import pytest

from auteur.beginner.studio_architecture import _candidate, architecture_revision_chain
from auteur.beginner.studio_architecture_question_projection import project_architecture_questions
from auteur.beginner.studio_store import CanvasStore

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))
sys.path.insert(0, str(REPO / "tests"))
import seed_book_discovery_study as discovery  # noqa: E402
import seed_book_impact_study as impact  # noqa: E402
from test_persistent_narrative_questions import assign_identities, identity_for  # noqa: E402
from test_persistent_question_journey import reconcile  # noqa: E402

GATE = 14
GATE_ID = identity_for(GATE)


@pytest.fixture(scope="module")
def pristine(tmp_path_factory):
    root = tmp_path_factory.mktemp("question-projection") / "discovery"
    discovery.seed_discovery(root)
    return root


@pytest.fixture
def project(pristine, tmp_path):
    target = tmp_path / "discovery"
    shutil.copytree(pristine, target)
    return target


def question(view, identifier):
    return next(q for q in view["questions"] + view["no_longer_open"] if q["id"] == identifier)


def ledger_store(project: Path) -> CanvasStore:
    return CanvasStore(project, discovery.SPRING)


def reword_gate(candidate):
    index = candidate["open_question_ids"].index(GATE_ID)
    candidate["open_questions"][index] += " Revised: whether the Council may pass through it."


def snapshot(directory: Path) -> dict[str, bytes]:
    return {str(path.relative_to(directory)): path.read_bytes() for path in sorted(directory.rglob("*")) if path.is_file()}


def test_a_question_keeps_its_identity_through_a_rewording_and_shows_the_reason_each_revision_records(project):
    store = ledger_store(project)
    impact.revise_architecture(store, "Give each open question a stable identity.", assign_identities)
    reconcile(store, project, 24)
    impact.revise_architecture(store, "Reword the Gate Table question.", reword_gate)

    view = project_architecture_questions(store)
    assert view["available"] and view["current"]["numbered"] and view["history"]["chain_complete"]
    gate = question(view, GATE_ID)
    assert gate["standing"] == "continuing" and gate["index"] == GATE
    assert gate["history"]["complete"] and gate["history"]["introduced_in_recorded_history"]
    assert gate["history"]["legacy_versions_before"] == 2

    kinds = [(span["kind"], span["change"]) for span in gate["spans"]]
    assert kinds == [("no_identity", None), ("present", "introduced"), ("present", "reworded")], kinds
    introduced, reworded = gate["spans"][1], gate["spans"][2]
    assert introduced["reason"]["instruction"] == "Give each open question a stable identity."
    assert reworded["reason"]["instruction"] == "Reword the Gate Table question."
    assert reworded["previous"]["text"] == introduced["text"] and reworded["text"] != introduced["text"]
    assert reworded["index"] == introduced["index"] == GATE

    # The Book that recorded the decision before the rewording is named by identity, with its own recorded version.
    book = next(b for b in gate["books"] if b["book_number"] == 24)
    assert book["state"] == "reworded" and book["question_id"] == GATE_ID and book["anchorable"]
    assert book["recorded"]["text"] == introduced["text"] and book["recorded"]["revision_number"] == 3
    assert book["decision_text"]


def test_unchanged_revisions_form_one_span_that_keeps_every_version(project):
    store = ledger_store(project)
    impact.revise_architecture(store, "Give each open question a stable identity.", assign_identities)
    impact.revise_architecture(store, "Clarify the summary.", lambda c: c.__setitem__("summary", c["summary"] + " Clarified."))
    view = project_architecture_questions(store)
    gate = question(view, GATE_ID)
    present = [span for span in gate["spans"] if span["kind"] == "present"]
    assert len(present) == 1 and present[0]["change"] == "introduced"
    introduced = present[0]["from_revision"]
    # The identity-introducing revision and the unrelated one after it share one span: the wording did not change.
    assert [v["revision_number"] for v in present[0]["versions"]] == [introduced, introduced + 1]
    assert present[0]["to_revision"] == introduced + 1 == view["current"]["revision_number"]


def test_a_removed_question_is_no_longer_open_never_answered(project):
    store = ledger_store(project)
    impact.revise_architecture(store, "Give each open question a stable identity.", assign_identities)

    def remove_gate(candidate):
        index = candidate["open_question_ids"].index(GATE_ID)
        del candidate["open_questions"][index]
        del candidate["open_question_ids"][index]

    impact.revise_architecture(store, "Remove the Gate Table question, as the Book now settles it elsewhere.", remove_gate)
    view = project_architecture_questions(store)
    assert GATE_ID not in [q["id"] for q in view["questions"]]
    gone = question(view, GATE_ID)
    assert gone["standing"] == "no_longer_open" and gone["text"] and gone["index"] == GATE
    absent = next(span for span in gone["spans"] if span["kind"] == "absent")
    assert absent["change"] == "removed"
    assert absent["reason"]["instruction"].startswith("Remove the Gate Table question")
    assert absent["previous"]["text"] == gone["text"]


def test_wording_without_identity_stays_wording_and_is_not_attached_to_any_question(project):
    store = ledger_store(project)
    view = project_architecture_questions(store)
    assert view["current"]["numbered"] is True or view["current"]["numbered"] is False
    assert view["questions"] and all(q["standing"] == "wording_only" and q["id"] is None for q in view["questions"])
    assert all(q["books"] == [] for q in view["questions"])
    assert view["no_longer_open"] == []
    # Book decisions that refer to wording without an identity are counted, never joined to a question.
    assert view["books"]["wording_only_references"]
    assert view["books"]["unattributed_references"] == []


def test_a_version_that_cannot_be_read_is_a_named_gap_and_is_not_dropped(project):
    store = ledger_store(project)
    impact.revise_architecture(store, "Give each open question a stable identity.", assign_identities)
    impact.revise_architecture(store, "Reword the Gate Table question.", reword_gate)
    chain = architecture_revision_chain(store)
    middle = chain["requests"][1]  # the identity-introducing revision
    folder = project / ".auteur/beginner/studio/canvases" / discovery.SPRING / "architecture/requests" / middle
    review = json.loads((folder / "review.json").read_text(encoding="utf-8"))
    review.pop("candidate", None)
    (folder / "review.json").write_text(json.dumps(review), encoding="utf-8")
    (folder / "response.json").write_text("{}", encoding="utf-8")

    view = project_architecture_questions(store)
    assert view["history"]["unreadable_versions"] == 1 and view["history"]["chain_complete"]
    gate = question(view, GATE_ID)
    assert not gate["history"]["complete"]
    assert "unreadable_before_first_recorded" in gate["history"]["gaps"]
    assert gate["history"]["introduced_in_recorded_history"] is False
    unreadable = [span for span in gate["spans"] if span["kind"] == "unreadable"]
    assert len(unreadable) == 1 and unreadable[0]["versions"][0]["request_sha256"] == middle
    # The later rewording is still shown, but the change across the gap is not claimed.
    after = gate["spans"][-1]
    assert after["kind"] == "present" and after["change"] == "unverified"


def test_an_incomplete_revision_chain_is_said_and_revision_numbers_are_withheld(project):
    store = ledger_store(project)
    impact.revise_architecture(store, "Give each open question a stable identity.", assign_identities)
    impact.revise_architecture(store, "Reword the Gate Table question.", reword_gate)
    chain = architecture_revision_chain(store)
    older = chain["requests"][1]
    folder = project / ".auteur/beginner/studio/canvases" / discovery.SPRING / "architecture/requests" / older
    (folder / "review.json").unlink()

    view = project_architecture_questions(store)
    assert view["history"]["chain_complete"] is False
    assert view["current"]["numbered"] is False and view["current"]["revision_number"] is None
    gate = question(view, GATE_ID)
    assert "chain_incomplete" in gate["history"]["gaps"] and not gate["history"]["complete"]


def test_books_are_read_by_identity_and_a_damaged_book_is_named_not_hidden(project):
    store = ledger_store(project)
    impact.revise_architecture(store, "Give each open question a stable identity.", assign_identities)
    reconcile(store, project, 24)
    reconcile(store, project, 25)
    view = project_architecture_questions(store)
    gate = question(view, GATE_ID)
    assert sorted(b["book_number"] for b in gate["books"]) == [24, 25]
    assert all(b["state"] == "current_wording" for b in gate["books"])
    assert all(isinstance(b["records_identity"], bool) for b in gate["books"])
    # Decisions that refer to other questions in those Books are attached to those questions only.
    attached = {(b["book_number"], b["decision_id"]) for q in view["questions"] for b in q["books"]}
    assert (24, "dec-gate-table") in attached and (25, "dec-gate-table") in attached


def test_reading_changes_nothing_on_disk(project):
    store = ledger_store(project)
    impact.revise_architecture(store, "Give each open question a stable identity.", assign_identities)
    reconcile(store, project, 24)
    before = snapshot(project)
    project_architecture_questions(store)
    project_architecture_questions(store)
    assert snapshot(project) == before


def test_reading_a_legacy_architecture_introduces_no_identity(project):
    store = ledger_store(project)
    before = _candidate(store)["candidate"]
    view = project_architecture_questions(store)
    assert not before.get("open_question_ids")
    assert all(q["id"] is None for q in view["questions"])
    assert _candidate(store)["candidate"] == before
