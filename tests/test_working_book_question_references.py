"""A Working Book element may reference a persistent Series question (kind `series_question`).

The owner records the binding: the question's position and wording at the Series version the reference was checked
against, and that version. An agent names only the question's identity. A retained association keeps its binding and is
never restamped; a new one is checked against the Series version the revision is built on. The reference records an
association only: it never changes the element's attribution, status or authority.
"""
import json
import shutil
import sys
from pathlib import Path

import pytest

from auteur.beginner.studio_architecture import _candidate
from auteur.beginner.studio_architecture_question_projection import project_architecture_questions
from auteur.beginner.studio_architecture_questions import text_digest
from auteur.beginner.studio_store import CanvasStore
from auteur.host_agent import HostAgentRequest, build_host_agent_response
from auteur.series.working_book_architecture import (
    Ref,
    WorkingBookArchitecture,
    _inherited_provenance,
    book_apply_review,
    book_complete,
    book_positional_observations,
    book_prepare,
    book_project,
    book_series_references,
)

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))
sys.path.insert(0, str(REPO / "tests"))
import seed_book_impact_study as seed  # noqa: E402
from test_beginner_studio_book_impact import current, reconciled  # noqa: E402
from test_persistent_narrative_questions import assign_identities, identity_for  # noqa: E402

CONVERSION_INDEX = 5  # 1-based position 6 in Book 24's prose: "open question 6"
CONVERSION_ID = identity_for(CONVERSION_INDEX)
BLIND_SPOT = "cons-conversion-blind-spot"
# The elements the reconciled Book changes (it stops citing the removed concept), as the partial-revision test targets them.
TARGETS = ("inh-gate-independence", "later-cohort-seat", BLIND_SPOT)


@pytest.fixture(scope="module")
def pristine(tmp_path_factory):
    root = tmp_path_factory.mktemp("question-references") / "impact"
    seed.seed_impact(root)
    return root


@pytest.fixture
def project(pristine, tmp_path):
    target = tmp_path / "impact"
    shutil.copytree(pristine, target)
    return target


def store_of(project: Path) -> CanvasStore:
    return CanvasStore(project, seed.SPRING)


def respond(request: dict, artifact: dict) -> dict:
    return build_host_agent_response(HostAgentRequest(**request), json.dumps(artifact), runtime="test-agent").model_dump()


def element(artifact: dict, identifier: str) -> dict:
    for collection in ("series_consequences", "engines", "inherited", "later_possibilities", "assumptions",
                       "alternatives", "unresolved", "open_author_decisions", "agents", "local_resolution"):
        for item in artifact.get(collection) or []:
            if item.get("id") == identifier:
                return item
    raise AssertionError(identifier)


def add_question_reference(artifact: dict, identifier: str, question_id: str) -> None:
    element(artifact, identifier).setdefault("refs", []).append({"kind": "series_question", "id": question_id})


def make_explicit(item: dict) -> None:
    """A changed element uses the explicit form. The legacy `unresolved` label is restated as asserted working prose."""
    if item.get("provenance") is not None:
        item.pop("provenance")
        item["attribution"], item["epistemic_status"] = "agent_proposed", "asserted"


def associate_conversion(store: CanvasStore, project: Path):
    """Book 24 engages the conversion question through its blind-spot element, through a reviewed targeted revision."""
    seed.revise_architecture(store, "Give each open question a stable identity.", assign_identities)
    artifact = reconciled(project, 24)
    make_explicit(element(artifact, BLIND_SPOT))
    add_question_reference(artifact, BLIND_SPOT, CONVERSION_ID)
    prepared = book_prepare(store, 24, instruction="Record that the blind spot engages the conversion question.",
                            targets=TARGETS)
    book_complete(store, 24, respond(prepared["request"], artifact))
    return prepared["pending_request_sha256"]


def element_references(store: CanvasStore) -> list[dict]:
    return book_series_references(store, 24)["element_question_references"]


def test_the_legacy_reference_shape_and_record_serialization_are_unchanged(project):
    assert Ref(kind="series_node", id="th_hands_and_draw").model_dump(mode="json") == {
        "kind": "series_node", "id": "th_hands_and_draw"}
    stored = current(project, 24)["artifact"]
    assert WorkingBookArchitecture.model_validate_json(json.dumps(stored)).model_dump(mode="json") == stored


def test_a_new_association_is_bound_to_the_identity_bearing_version_it_was_checked_on(project):
    store = store_of(project)
    sha = associate_conversion(store, project)
    review = book_project(store, 24)["review"]
    assert review["applicable"], review["unexpected_changes"]
    added = review["question_associations"]["added"]
    assert [(item["element_id"], item["question_id"]) for item in added] == [(BLIND_SPOT, CONVERSION_ID)]
    # The review says where the association stands and what the element's own authority is, before Apply.
    assert added[0]["standing"]["state"] == "current_wording"
    assert added[0]["commitment_authority"] == "agent_working"

    assert book_apply_review(store, 24, sha)["result"] == "applied"
    series = _candidate(store)
    (row,) = [item for item in element_references(store) if item["element_id"] == BLIND_SPOT]
    assert row["question_id"] == CONVERSION_ID
    assert row["state"] == "current_wording"
    assert row["version_request_sha256"] == series["request_sha256"]
    assert row["recorded_index"] == CONVERSION_INDEX
    assert row["recorded_text"] == series["candidate"]["open_questions"][CONVERSION_INDEX]
    # Authority is unchanged by the association: it is still the element's own working status.
    assert (row["attribution"], row["epistemic_status"], row["commitment_authority"]) == (
        "agent_proposed", "asserted", "agent_working")
    assert row["collection"] == "series_consequences"


def test_the_owner_refuses_an_identity_the_version_does_not_hold(project):
    store = store_of(project)
    seed.revise_architecture(store, "Give each open question a stable identity.", assign_identities)
    artifact = reconciled(project, 24)
    add_question_reference(artifact, BLIND_SPOT, "q-not-an-open-question")
    prepared = book_prepare(store, 24, instruction="Attach a reference.", targets=TARGETS)
    with pytest.raises(ValueError, match="not an open question identity"):
        book_complete(store, 24, respond(prepared["request"], artifact))


def test_the_owner_refuses_a_binding_the_response_asserts_against_the_version(project):
    store = store_of(project)
    seed.revise_architecture(store, "Give each open question a stable identity.", assign_identities)
    artifact = reconciled(project, 24)
    add_question_reference(artifact, BLIND_SPOT, CONVERSION_ID)
    element(artifact, BLIND_SPOT)["refs"][-1].update(series_question_index=CONVERSION_INDEX + 1,
                                                    series_question_sha256="0" * 64)
    prepared = book_prepare(store, 24, instruction="Attach a reference.", targets=TARGETS)
    with pytest.raises(ValueError, match="recorded by the owner"):
        book_complete(store, 24, respond(prepared["request"], artifact))


def test_a_version_without_identities_cannot_hold_a_question_reference(project):
    store = store_of(project)
    artifact = reconciled(project, 24)
    add_question_reference(artifact, BLIND_SPOT, CONVERSION_ID)
    prepared = book_prepare(store, 24, instruction="Attach a reference.", targets=TARGETS)
    with pytest.raises(ValueError, match="identit"):
        book_complete(store, 24, respond(prepared["request"], artifact))


@pytest.mark.parametrize("place", ["decision", "edge_target", "name_source"])
def test_a_question_reference_is_refused_where_it_would_be_a_second_owner_or_a_dependency(project, place):
    store = store_of(project)
    seed.revise_architecture(store, "Give each open question a stable identity.", assign_identities)
    artifact = reconciled(project, 24)
    reference = {"kind": "series_question", "id": CONVERSION_ID}
    if place == "decision":
        decision = element(artifact, "dec-gate-table")
        decision.setdefault("refs", []).append(reference)
    elif place == "edge_target":
        artifact["typed_edges"].append({"id": "edge-question", "source": BLIND_SPOT, "target": reference,
                                        "dependency": "depends_on", "function": "x"})
    else:
        agent = artifact["agents"][0]
        agent.update(name=None, name_source=reference)
    prepared = book_prepare(store, 24, instruction="Attach a reference.", targets=TARGETS)
    with pytest.raises(ValueError, match="cannot"):
        book_complete(store, 24, respond(prepared["request"], artifact))


def test_a_retained_association_keeps_its_binding_through_a_reorder_and_a_holistic_revision(project):
    store = store_of(project)
    sha = associate_conversion(store, project)
    assert book_apply_review(store, 24, sha)["result"] == "applied"
    bound = element_references(store)[0]["version_request_sha256"]

    def reorder(candidate):
        questions, identities = candidate["open_questions"], candidate["open_question_ids"]
        for listing in (questions, identities):
            listing[CONVERSION_INDEX], listing[CONVERSION_INDEX + 1] = listing[CONVERSION_INDEX + 1], listing[CONVERSION_INDEX]

    seed.revise_architecture(store, "Reorder two questions.", reorder)
    artifact = json.loads(json.dumps(current(project, 24)["artifact"]))
    prepared = book_prepare(store, 24, instruction="Bring the Book to the current Architecture.", holistic=True)
    book_complete(store, 24, respond(prepared["request"], artifact))
    assert book_apply_review(store, 24, prepared["pending_request_sha256"])["result"] == "applied"

    (row,) = [item for item in element_references(store) if item["element_id"] == BLIND_SPOT]
    assert row["version_request_sha256"] == bound  # never restamped to the latest version
    assert row["state"] == "moved"
    assert row["recorded_index"] == CONVERSION_INDEX
    assert row["current_index"] == CONVERSION_INDEX + 1


def test_a_removed_question_leaves_the_book_readable_and_reports_no_longer_open(project):
    store = store_of(project)
    sha = associate_conversion(store, project)
    assert book_apply_review(store, 24, sha)["result"] == "applied"

    def retire(candidate):
        index = candidate["open_question_ids"].index(CONVERSION_ID)
        del candidate["open_questions"][index]
        del candidate["open_question_ids"][index]

    seed.revise_architecture(store, "Retire the conversion question.", retire)
    (row,) = [item for item in element_references(store) if item["element_id"] == BLIND_SPOT]
    assert row["state"] == "removed"
    assert row["question_id"] == CONVERSION_ID
    # The Book is still readable, and its stored association is exactly what was recorded.
    blind = element(current(project, 24)["artifact"], BLIND_SPOT)
    assert any(ref.get("kind") == "series_question" and ref["id"] == CONVERSION_ID for ref in blind["refs"])


def test_the_question_reading_lists_the_element_engagement_under_the_books_own_collection(project):
    store = store_of(project)
    sha = associate_conversion(store, project)
    assert book_apply_review(store, 24, sha)["result"] == "applied"
    question = next(item for item in project_architecture_questions(store)["questions"] if item["id"] == CONVERSION_ID)
    assert question["books"] == []  # decisions only: no decision names this question in this test
    engagements = question["engagements"]
    assert [(entry["book_number"], entry["element_id"], entry["collection"]) for entry in engagements] == [
        (24, BLIND_SPOT, "series_consequences")]
    assert engagements[0]["state"] == "current_wording"
    assert engagements[0]["epistemic_status"] == "asserted"


def test_positional_prose_resolves_at_the_recorded_version_without_becoming_a_binding(project):
    store = store_of(project)
    observations = book_positional_observations(store, 24)
    by_element = {item["element_id"]: item for item in observations["observations"]}
    blind = by_element[BLIND_SPOT]
    assert blind["phrase"] == "open question 6"
    assert blind["position"] == 6 and blind["numbering"] == "one_based"
    assert blind["referent_index"] == CONVERSION_INDEX
    assert blind["referent_text"].startswith("Is the Book 20 hands-to-draw conversion")
    assert blind["state"] == "resolved"
    assert blind["identity_at_read_version"] is None  # the version it was written against carries no identities
    assert blind["binding"] == "none"
    # Nothing is written: the record and its references are as they were.
    assert element_references(store) == []


def test_a_retained_association_refuses_a_binding_the_response_changes(project):
    store = store_of(project)
    sha = associate_conversion(store, project)
    assert book_apply_review(store, 24, sha)["result"] == "applied"
    artifact = json.loads(json.dumps(current(project, 24)["artifact"]))
    held = next(ref for ref in element(artifact, BLIND_SPOT)["refs"] if ref.get("kind") == "series_question")
    held["series_question_index"] = CONVERSION_INDEX + 1
    prepared = book_prepare(store, 24, instruction="Keep the association.", holistic=True)
    with pytest.raises(ValueError, match="recorded by the owner"):
        book_complete(store, 24, respond(prepared["request"], artifact))


def test_the_same_question_is_associated_with_one_element_once(project):
    store = store_of(project)
    seed.revise_architecture(store, "Give each open question a stable identity.", assign_identities)
    artifact = reconciled(project, 24)
    add_question_reference(artifact, BLIND_SPOT, CONVERSION_ID)
    add_question_reference(artifact, BLIND_SPOT, CONVERSION_ID)
    prepared = book_prepare(store, 24, instruction="Attach a reference.", targets=TARGETS)
    with pytest.raises(ValueError, match="more than once"):
        book_complete(store, 24, respond(prepared["request"], artifact))


def test_an_inherited_claim_whose_only_reference_is_a_question_has_no_basis(project):
    store = store_of(project)
    sha = associate_conversion(store, project)
    assert book_apply_review(store, 24, sha)["result"] == "applied"
    artifact = WorkingBookArchitecture.model_validate_json(json.dumps(current(project, 24)["artifact"]))
    inherited = next(item for item in artifact.inherited if item.id == "inh-uneven-draw")
    inherited.refs = [Ref(kind="series_question", id=CONVERSION_ID,
                          series_question_index=CONVERSION_INDEX, series_question_sha256="0" * 64,
                          series_question_version=_candidate(store)["request_sha256"])]
    view = _inherited_provenance(artifact, _candidate(store)["candidate"], set())
    (basis,) = [item["source_basis"] for item in view["items"] if item["id"] == "inh-uneven-draw"]
    assert basis == "unreferenced"


def test_an_association_whose_recorded_binding_no_longer_matches_still_names_its_question(project):
    store = store_of(project)
    sha = associate_conversion(store, project)
    assert book_apply_review(store, 24, sha)["result"] == "applied"
    path = project / ".auteur/beginner/studio/canvases" / seed.SPRING / "architecture/books/24/current.json"
    record = json.loads(path.read_text(encoding="utf-8"))
    held = next(ref for ref in element(record["artifact"], BLIND_SPOT)["refs"] if ref.get("kind") == "series_question")
    held["series_question_sha256"] = "0" * 64
    path.write_text(json.dumps(record), encoding="utf-8")
    (row,) = [item for item in element_references(store) if item["element_id"] == BLIND_SPOT]
    assert row["state"] == "binding_mismatch"
    assert row["question_id"] == CONVERSION_ID


def test_positional_prose_in_a_typed_edge_is_observed_too(project):
    store = store_of(project)
    path = project / ".auteur/beginner/studio/canvases" / seed.SPRING / "architecture/books/24/current.json"
    record = json.loads(path.read_text(encoding="utf-8"))
    edge = record["artifact"]["typed_edges"][0]
    edge["function"] = "Makes open question 6 concrete along this edge."
    path.write_text(json.dumps(record), encoding="utf-8")
    rows = [item for item in book_positional_observations(store, 24)["observations"] if item["element_id"] == edge["id"]]
    assert [(item["collection"], item["field"], item["position"]) for item in rows] == [("typed_edges", "function", 6)]
    assert rows[0]["binding"] == "none"

