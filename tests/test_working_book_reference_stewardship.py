"""Reference stewardship: an author can act on a positional observation through the reviewed Working Book workflow.

The owner reads a positional name at the Series version the element's own prose was written against. It offers what the
author can do, in the owner's terms: a proposal only where the recorded history names an identity that is still open, a
choice where the version named none, and no action where the placement cannot carry an association. A requested
association is checked by the owner, its element joins the revision's scope, and the review states whether the response
recorded it. Nothing is applied, inferred or settled here.
"""
import json
import sys

import pytest

from auteur.beginner.studio_architecture import _candidate
from auteur.series.working_book_architecture import (
    book_apply_review,
    book_complete,
    book_observation_stewardship,
    book_positional_observations,
    book_prepare,
    book_project,
)

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
from test_working_book_question_references import (  # noqa: E402  (helpers and fixtures, not tests)
    BLIND_SPOT,
    CONVERSION_ID,
    CONVERSION_INDEX,
    TARGETS,
    element,
    make_explicit,
    pristine,  # noqa: F401  (fixture)
    project,  # noqa: F401  (fixture)
    respond,
    store_of,
)
import seed_book_impact_study as seed  # noqa: E402
from test_beginner_studio_book_impact import current, reconciled  # noqa: E402
from test_persistent_narrative_questions import assign_identities  # noqa: E402


def observation(store, element_id: str) -> dict:
    """The first positional name an element's prose makes. Its rows share one origin: the prose field is one text."""
    rows = [item for item in book_observation_stewardship(store, 24)["observations"] if item["element_id"] == element_id]
    assert rows, element_id
    return rows[0]


def give_identities(store) -> None:
    seed.revise_architecture(store, "Give each open question a stable identity.", assign_identities)


def test_an_identity_less_version_offers_a_choice_and_never_a_proposal(project):
    store = store_of(project)
    give_identities(store)
    row = observation(store, BLIND_SPOT)
    stewardship = row["adoption"]
    # The prose was written against a version that named no identities, so nothing identifies the question it names.
    assert row["identity_at_read_version"] is None
    assert stewardship["state"] == "identity_not_recorded_at_read_version"
    assert stewardship["recordable"] is True
    assert stewardship["proposed_question_id"] is None
    conversion = stewardship["choices"][CONVERSION_INDEX]
    assert conversion["id"] == CONVERSION_ID
    assert conversion["text"].startswith("Is the Book 20 hands-to-draw conversion")


def test_a_prose_rewrite_reads_at_the_version_that_wrote_it_and_proposes_its_recorded_identity(project):
    store = store_of(project)
    give_identities(store)
    artifact = reconciled(project, 24)
    make_explicit(element(artifact, BLIND_SPOT))
    element(artifact, BLIND_SPOT)["text"] += " The finale must answer open question 6."
    prepared = book_prepare(store, 24, instruction="Sharpen the blind spot's reference to open question 6.",
                            targets=TARGETS)
    sha = prepared["pending_request_sha256"]
    book_complete(store, 24, respond(prepared["request"], artifact))
    assert book_apply_review(store, 24, sha)["result"] == "applied"

    row = observation(store, BLIND_SPOT)
    # The rewritten prose is written by the applied revision, so that revision's version is the one it reads at.
    assert row["origin"]["basis"] == "written_in_this_version"
    assert row["origin"]["request_sha256"] == sha
    assert row["read_basis"] == "element_origin"
    # The read is at the version the rewrite was written against (the identity-bearing one), not the Book-wide version: a
    # partial revision of an out-of-date Book keeps the baseline on the Book, and the prose still records its own origin.
    assert row["read_at_request_sha256"] == _candidate(store)["request_sha256"]
    assert current(project, 24)["series_request_sha256"] != row["read_at_request_sha256"]
    assert row["identity_at_read_version"] == CONVERSION_ID
    assert row["adoption"]["state"] == "recordable"
    assert row["adoption"]["proposed_question_id"] == CONVERSION_ID


def test_an_unchanged_prose_still_reads_at_its_origin_and_says_so(project):
    store = store_of(project)
    row = observation(store, BLIND_SPOT)
    # Book 24's blind-spot prose was not rewritten by any later revision, so the Book's recorded version is its origin.
    assert row["read_basis"] in ("element_origin", "book_recorded_version")
    assert row["referent_index"] == CONVERSION_INDEX
    assert row["other_reading"]["numbering"] == "zero_based"
    assert row["other_reading"]["referent_index"] == 6  # the other reading of "open question 6" names index 6


def test_a_requested_association_is_checked_and_reported_in_its_review(project):
    store = store_of(project)
    give_identities(store)
    artifact = reconciled(project, 24)
    make_explicit(element(artifact, BLIND_SPOT))
    prepared = book_prepare(store, 24, targets=TARGETS,
                            associations=({"element_id": BLIND_SPOT, "question_id": CONVERSION_ID},))
    request = prepared["request"]
    packet = json.loads(request["user"])
    (asked,) = packet["requested_question_associations"]
    assert (asked["element_id"], asked["question_id"], asked["question_index"]) == (BLIND_SPOT, CONVERSION_ID, CONVERSION_INDEX)
    assert asked["observed_positions"][0]["phrase"] == "open question 6"
    assert request["settings"]["requested_question_associations"] == [
        {"element_id": BLIND_SPOT, "question_id": CONVERSION_ID}]
    # The owner put the association into the request's own instruction, with the explicit-form rule.
    assert "may record an association with " + CONVERSION_ID in packet["instruction"]
    assert BLIND_SPOT in packet["permitted_ids"]

    element(artifact, BLIND_SPOT).setdefault("refs", []).append({"kind": "series_question", "id": CONVERSION_ID})
    book_complete(store, 24, respond(request, artifact))
    review = book_project(store, 24)["review"]
    assert review["applicable"], review["unexpected_changes"]
    assert [(row["element_id"], row["question_id"], row["established"]) for row in review["requested_question_associations"]] == [
        (BLIND_SPOT, CONVERSION_ID, True)]
    # The review names the question's own wording, so the author reads what was asked, not only its identity.
    assert review["requested_question_associations"][0]["question_text"].startswith("Is the Book 20 hands-to-draw conversion")


def test_a_response_that_does_not_record_the_requested_association_says_so(project):
    store = store_of(project)
    give_identities(store)
    artifact = reconciled(project, 24)
    make_explicit(element(artifact, BLIND_SPOT))
    prepared = book_prepare(store, 24, targets=TARGETS,
                            associations=({"element_id": BLIND_SPOT, "question_id": CONVERSION_ID},))
    # The coding agent judges that the element does not engage the question: it adds no reference.
    book_complete(store, 24, respond(prepared["request"], artifact))
    review = book_project(store, 24)["review"]
    assert [(row["element_id"], row["question_id"], row["established"]) for row in review["requested_question_associations"]] == [
        (BLIND_SPOT, CONVERSION_ID, False)]
    assert review["question_associations"]["added"] == []


@pytest.mark.parametrize("kwargs, message", [
    ({"element_id": "dec-gate-table", "question_id": CONVERSION_ID}, "is a decision"),
    ({"element_id": BLIND_SPOT, "question_id": "q-not-an-open-question"}, "not an open question"),
    ({"element_id": "no-such-element", "question_id": CONVERSION_ID}, "unknown element"),
])
def test_the_owner_refuses_an_association_it_cannot_check(project, kwargs, message):
    store = store_of(project)
    give_identities(store)
    with pytest.raises(ValueError, match=message):
        book_prepare(store, 24, associations=(kwargs,))


def test_an_association_needs_identities_in_the_current_architecture(project):
    store = store_of(project)
    with pytest.raises(ValueError, match="no identities"):
        book_prepare(store, 24, associations=({"element_id": BLIND_SPOT, "question_id": CONVERSION_ID},))


def test_an_already_recorded_association_is_refused_and_shown_as_recorded(project):
    store = store_of(project)
    give_identities(store)
    artifact = reconciled(project, 24)
    make_explicit(element(artifact, BLIND_SPOT))
    element(artifact, BLIND_SPOT).setdefault("refs", []).append({"kind": "series_question", "id": CONVERSION_ID})
    prepared = book_prepare(store, 24, instruction="Record the blind spot's question association.", targets=TARGETS)
    book_complete(store, 24, respond(prepared["request"], artifact))
    assert book_apply_review(store, 24, prepared["pending_request_sha256"])["result"] == "applied"
    with pytest.raises(ValueError, match="already records"):
        book_prepare(store, 24, associations=({"element_id": BLIND_SPOT, "question_id": CONVERSION_ID},))
    assert observation(store, BLIND_SPOT)["adoption"]["state"] == "identity_not_recorded_at_read_version"
    assert observation(store, BLIND_SPOT)["adoption"]["held_question_ids"] == [CONVERSION_ID]


def test_a_positional_name_in_a_typed_edge_is_not_offered_for_association(project):
    store = store_of(project)
    give_identities(store)
    path = project / ".auteur/beginner/studio/canvases" / seed.SPRING / "architecture/books/24/current.json"
    record = json.loads(path.read_text(encoding="utf-8"))
    edge = record["artifact"]["typed_edges"][0]
    edge["function"] = "Makes open question 6 concrete along this edge."
    path.write_text(json.dumps(record), encoding="utf-8")
    rows = [item for item in book_observation_stewardship(store, 24)["observations"] if item["element_id"] == edge["id"]]
    (row,) = rows
    assert row["adoption"]["state"] == "not_recordable"
    assert row["adoption"]["recordable"] is False
    assert "typed edge" in row["adoption"]["reason"]


def test_a_decision_is_not_offered_an_element_association(project):
    store = store_of(project)
    give_identities(store)
    path = project / ".auteur/beginner/studio/canvases" / seed.SPRING / "architecture/books/24/current.json"
    record = json.loads(path.read_text(encoding="utf-8"))
    decision = record["artifact"]["open_author_decisions"][0]
    decision["text"] = "Settle open question 6 before the finale. Does it hold?"
    path.write_text(json.dumps(record), encoding="utf-8")
    rows = [item for item in book_observation_stewardship(store, 24)["observations"] if item["element_id"] == decision["id"]]
    (row,) = rows
    assert row["adoption"]["state"] == "not_recordable"
    assert "decision" in row["adoption"]["reason"]


def test_the_observation_read_is_unchanged_by_the_stewardship_view(project):
    store = store_of(project)
    plain = book_positional_observations(store, 24)["observations"]
    viewed = book_observation_stewardship(store, 24)["observations"]
    assert [{k: v for k, v in row.items() if k != "adoption"} for row in viewed] == plain
