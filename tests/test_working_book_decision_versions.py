"""A Book decision keeps the Architecture version its question binding was written against.

A partial revision of an out-of-date Book keeps the Book's older Series baseline for the elements it does not
touch. A decision that revision introduces is bound to the question version the Architecture has now, so it must
name that version, not the Book's older baseline. The decision that was already there keeps the version it was
written against.
"""
import json
import shutil
import sys
from pathlib import Path

import pytest

from auteur.beginner.studio_architecture import _candidate, architecture_revision_chain
from auteur.beginner.studio_architecture_questions import text_digest
from auteur.beginner.studio_store import CanvasStore
from auteur.host_agent import HostAgentRequest, build_host_agent_response
from auteur.series.working_book_architecture import (
    book_apply_review,
    book_complete,
    book_prepare,
    book_series_references,
)

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))
import seed_book_impact_study as seed  # noqa: E402
from test_beginner_studio_book_impact import reconciled  # noqa: E402
from test_persistent_narrative_questions import assign_identities  # noqa: E402

# The targets a partial revision of Book 24 may change, as in the existing partial-revision test.
TARGETS = ("inh-gate-independence", "later-cohort-seat")


@pytest.fixture(scope="module")
def pristine(tmp_path_factory):
    root = tmp_path_factory.mktemp("decision-versions") / "impact"
    seed.seed_impact(root)
    return root


@pytest.fixture
def project(pristine, tmp_path):
    target = tmp_path / "impact"
    shutil.copytree(pristine, target)
    return target


def stored_book(project: Path, number: int) -> dict:
    path = project / ".auteur/beginner/studio/canvases" / seed.SPRING / "architecture/books" / str(number) / "current.json"
    return json.loads(path.read_text(encoding="utf-8"))


def respond(request: dict, artifact: dict) -> dict:
    return build_host_agent_response(HostAgentRequest(**request), json.dumps(artifact), runtime="test-agent").model_dump()


def references(store: CanvasStore) -> dict[str, dict]:
    return {ref["decision_id"]: ref for ref in book_series_references(store, 24)["question_references"]}


def test_a_decision_a_partial_revision_introduces_names_the_question_version_it_was_written_against(project):
    store = CanvasStore(project, seed.SPRING)
    seed.revise_architecture(store, "Give each open question a stable identity.", assign_identities)
    series = _candidate(store)
    index = len(series["candidate"]["open_questions"]) - 1
    question = series["candidate"]["open_questions"][index]
    identifier = series["candidate"]["open_question_ids"][index]
    before = stored_book(project, 24)
    kept = references(store)["dec-gate-table"]
    assert before["series_request_sha256"] != series["request_sha256"]  # Book 24 is out of date

    artifact = reconciled(project, 24)  # the agent stops citing the removed concept, as in the partial-revision test
    artifact["open_author_decisions"].append({
        "id": "dec-last-question",
        "text": "Whether the last open question is settled by Book 24.",
        "refs": [{"kind": "book_element", "id": "inh-gate-independence"}],
        "provenance": None,  # a new element carries explicit attribution, as a revision requires
        "attribution": "derived",  # an author decision is derived from its Series question and stays unresolved
        "epistemic_status": "unresolved",
        "interpretation": None,
        "series_question_index": index,
        "series_question_sha256": text_digest(question),
        "series_question_id": identifier,
    })
    prepared = book_prepare(store, 24, instruction="Record the decision the last open question calls for.",
                            targets=TARGETS)
    book_complete(store, 24, respond(prepared["request"], artifact))
    assert book_apply_review(store, 24, prepared["pending_request_sha256"])["currentness"] == "kept_baseline"

    refs = references(store)
    # The new decision was written against the version the Architecture has now.
    assert refs["dec-last-question"]["state"] == "current_wording", refs["dec-last-question"]
    assert refs["dec-last-question"]["question_id"] == identifier
    assert refs["dec-last-question"]["version_request_sha256"] == series["request_sha256"]
    # The decision that was already there still names the version it was written against.
    assert refs["dec-gate-table"]["version_request_sha256"] == kept["version_request_sha256"] == before["series_request_sha256"]


def test_a_decision_written_before_versions_were_recorded_keeps_the_baseline_across_a_partial_revision(project):
    """A stored decision with no recorded version is bound to the Book's baseline, and a partial revision does not
    rebind it to the Architecture the Book was not written against."""
    store = CanvasStore(project, seed.SPRING)
    path = project / ".auteur/beginner/studio/canvases" / seed.SPRING / "architecture/books/24/current.json"
    record = json.loads(path.read_text(encoding="utf-8"))
    for decision in record["artifact"]["open_author_decisions"]:
        decision.pop("series_question_version", None)  # the shape stored before this field existed
    path.write_text(json.dumps(record), encoding="utf-8")
    baseline = record["series_request_sha256"]
    assert references(store)["dec-gate-table"]["version_request_sha256"] == baseline

    seed.revise_architecture(store, "Give each open question a stable identity.", assign_identities)
    artifact = reconciled(project, 24)
    prepared = book_prepare(store, 24, instruction="Bring the Book to the current Architecture where it cites it.",
                            targets=TARGETS)
    book_complete(store, 24, respond(prepared["request"], artifact))
    assert book_apply_review(store, 24, prepared["pending_request_sha256"])["currentness"] == "kept_baseline"

    assert references(store)["dec-gate-table"]["version_request_sha256"] == baseline


def test_two_books_that_refer_to_one_continuing_question_each_name_it_through_their_own_decision(project):
    store = CanvasStore(project, seed.SPRING)
    seed.revise_architecture(store, "Give each open question a stable identity.", assign_identities)
    series = _candidate(store)
    index = len(series["candidate"]["open_questions"]) - 1
    question = series["candidate"]["open_questions"][index]
    identifier = series["candidate"]["open_question_ids"][index]

    for number in (24, 25):
        artifact = reconciled(project, number)
        artifact["open_author_decisions"].append({
            "id": f"dec-last-question-{number}",
            "text": f"Book {number} decides what the last open question asks of it.",
            "refs": [{"kind": "book_element", "id": "inh-gate-independence"}],
            "provenance": None,
            "attribution": "derived",
            "epistemic_status": "unresolved",
            "interpretation": None,
            "series_question_index": index,
            "series_question_sha256": text_digest(question),
            "series_question_id": identifier,
        })
        prepared = book_prepare(store, number, instruction="Record what the continuing question asks of this Book.",
                                targets=TARGETS)
        book_complete(store, number, respond(prepared["request"], artifact))
        assert book_apply_review(store, number, prepared["pending_request_sha256"])["currentness"] == "kept_baseline"

    for number in (24, 25):
        refs = {r["decision_id"]: r for r in book_series_references(store, number)["question_references"]}
        ref = refs[f"dec-last-question-{number}"]
        assert ref["state"] == "current_wording" and ref["question_id"] == identifier, (number, ref)
        assert ref["version_request_sha256"] == series["request_sha256"], (number, ref)


def test_a_holistic_reconciliation_records_each_decision_it_rebinds_and_keeps_its_wording_and_index(project):
    """The legacy decision gains its current identity by a whole-Book revision, and the review keeps the earlier version."""
    store = CanvasStore(project, seed.SPRING)
    before = stored_book(project, 24)
    gate_before = next(d for d in before["artifact"]["open_author_decisions"] if d["id"] == "dec-gate-table")
    seed.revise_architecture(store, "Give each open question a stable identity.", assign_identities)
    series = _candidate(store)
    prepared = book_prepare(store, 24, instruction="Bring Book 24 up to date with the Architecture.", holistic=True)
    book_complete(store, 24, respond(prepared["request"], reconciled(project, 24)))
    applied = book_apply_review(store, 24, prepared["pending_request_sha256"])
    assert applied["currentness"] == "current"

    after = stored_book(project, 24)
    gate_after = next(d for d in after["artifact"]["open_author_decisions"] if d["id"] == "dec-gate-table")
    # The wording and the position the decision names are exactly as recorded.
    assert gate_after["series_question_index"] == gate_before["series_question_index"]
    assert gate_after["series_question_sha256"] == gate_before["series_question_sha256"]
    # The review keeps the version it was bound to before, and the version it was checked against.
    review_path = (project / ".auteur/beginner/studio/canvases" / seed.SPRING / "architecture/books/24/requests"
                   / prepared["pending_request_sha256"] / "review.json")
    review = json.loads(review_path.read_text(encoding="utf-8"))
    change = next(c for c in review["decision_versions"] if c["decision_id"] == "dec-gate-table")
    assert change["from_request_sha256"] == before["series_request_sha256"]
    assert change["to_request_sha256"] == series["request_sha256"]
    assert change["question_id_before"] is None
    assert change["question_id_after"] == series["candidate"]["open_question_ids"][gate_after["series_question_index"]]
    assert after["applied_review"]["decision_versions"] == review["decision_versions"]
    # The current binding is valid and names the identity at that position, with no claim about earlier history.
    ref = references(store)["dec-gate-table"]
    assert ref["state"] == "current_wording"
    assert ref["question_id"] == series["candidate"]["open_question_ids"][gate_after["series_question_index"]]
    assert ref["version_request_sha256"] == series["request_sha256"]


def _establish(store, project):
    """Identities on the current Architecture, and Book 24 written against them (the decision names its identity)."""
    seed.revise_architecture(store, "Give each open question a stable identity.", assign_identities)
    prepared = book_prepare(store, 24, instruction="Bring Book 24 up to date with the Architecture.", holistic=True)
    book_complete(store, 24, respond(prepared["request"], reconciled(project, 24)))
    assert book_apply_review(store, 24, prepared["pending_request_sha256"])["currentness"] == "current"


def test_a_book_can_still_be_revised_after_a_question_it_cites_is_reworded(project):
    """A cited question reworded by the Architecture is reported on the decision; it never blocks the Book's revision."""
    store = CanvasStore(project, seed.SPRING)
    _establish(store, project)
    index = stored_book(project, 24)["artifact"]["open_author_decisions"]
    index = next(d for d in index if d["id"] == "dec-gate-table")["series_question_index"]

    def reword(candidate):
        candidate["open_questions"][index] += " Revised."

    seed.revise_architecture(store, "Reword the Gate Table question.", reword)
    prepared = book_prepare(store, 24, instruction="Bring Book 24 up to date with the Architecture.", holistic=True)
    book_complete(store, 24, respond(prepared["request"], reconciled(project, 24)))  # must not refuse
    assert book_apply_review(store, 24, prepared["pending_request_sha256"])["currentness"] == "current"
    ref = references(store)["dec-gate-table"]
    assert ref["state"] == "reworded", ref
    assert ref["question_id"] == _candidate(store)["candidate"]["open_question_ids"][index]
    assert ref["version_request_sha256"] != _candidate(store)["request_sha256"]  # still the version it was checked against


def test_a_recorded_question_identity_cannot_be_changed_by_a_revision(project):
    store = CanvasStore(project, seed.SPRING)
    _establish(store, project)
    identifier = _candidate(store)["candidate"]["open_question_ids"]
    gate_index = next(d for d in stored_book(project, 24)["artifact"]["open_author_decisions"]
                      if d["id"] == "dec-gate-table")["series_question_index"]
    # The decision gains its identity, which the Series question at its position carries.
    artifact = reconciled(project, 24)
    gate = next(d for d in artifact["open_author_decisions"] if d["id"] == "dec-gate-table")
    # A changed decision takes the form a revision requires: derived from its Series question, and unresolved.
    gate.update({"provenance": None, "attribution": "derived", "epistemic_status": "unresolved",
                 "series_question_id": identifier[gate_index]})
    prepared = book_prepare(store, 24, instruction="Record the identity the decision names.", holistic=True)
    book_complete(store, 24, respond(prepared["request"], artifact))
    assert book_apply_review(store, 24, prepared["pending_request_sha256"])["currentness"] == "current"
    assert references(store)["dec-gate-table"]["question_id"] == identifier[gate_index]
    # Once recorded, the identity cannot name another question by a later revision.
    artifact = reconciled(project, 24)
    next(d for d in artifact["open_author_decisions"] if d["id"] == "dec-gate-table")["series_question_id"] = "q-elsewhere"
    prepared = book_prepare(store, 24, instruction="Try to name another question.", holistic=True)
    with pytest.raises(ValueError, match="cannot be changed"):
        book_complete(store, 24, respond(prepared["request"], artifact))


def test_identities_are_refused_while_the_revision_history_cannot_be_read(project):
    store = CanvasStore(project, seed.SPRING)
    chain = architecture_revision_chain(store)
    middle = chain["requests"][1]
    review = project / ".auteur/beginner/studio/canvases" / seed.SPRING / "architecture/requests" / middle / "review.json"
    review.unlink()
    assert architecture_revision_chain(store)["complete"] is False
    with pytest.raises(ValueError, match="cannot be read"):
        seed.revise_architecture(store, "Give each open question a stable identity.", assign_identities)


def test_a_decision_with_no_identity_or_version_keeps_the_shape_it_always_had():
    from auteur.series.working_book_architecture import DecisionElement
    raw = {"id": "dec-legacy", "text": "A decision written before identities.", "refs": [],
           "provenance": "unresolved", "attribution": None, "epistemic_status": None, "interpretation": None,
           "series_question_index": 1, "series_question_sha256": "a" * 64}
    dumped = DecisionElement.model_validate(raw).model_dump(mode="json")
    assert "series_question_id" not in dumped and "series_question_version" not in dumped
    assert set(dumped) == set(raw)
