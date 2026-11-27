"""Question-linked Book elements as evidence for cross-question deliberation and opportunity discovery.

An element that records an association with a question is evidence that the element engages that question. It is never
evidence that the element answers, settles, develops or inherits from it, and two questions one element engages are not
thereby related. These tests build the associations through the Working Book owner's own reviewed path, then check what the
deliberation and discovery packets carry, how each item is labelled, and what a coding agent's answer may cite.
"""
import json
import sys
from pathlib import Path

import pytest
from pydantic import ValidationError

from auteur.beginner.studio_architecture import _candidate
from auteur.beginner.studio_architecture_deliberation import _spread, build_question_deliberation, deliberation_standing
from auteur.beginner.studio_architecture_discovery import (
    DiscoveredEvidence,
    _SYSTEM as DISCOVERY_SYSTEM,
    complete_architecture_discovery,
    prepare_architecture_discovery,
    project_architecture_discoveries,
)
from auteur.beginner.studio_store import CanvasStore
from auteur.host_agent import HostAgentRequest, build_host_agent_response
from auteur.series.working_book_architecture import book_apply_review, book_complete, book_prepare, book_series_references

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))
sys.path.insert(0, str(REPO / "tests"))
import seed_book_discovery_study as discovery  # noqa: E402
import seed_book_impact_study as impact  # noqa: E402
from test_beginner_studio_book_impact import reconciled  # noqa: E402
from test_persistent_narrative_questions import assign_identities, identity_for  # noqa: E402

CONVERSION = identity_for(5)  # open question 6 in one-based prose: the conversion settlement question
COMPACT = identity_for(6)
HESPER = identity_for(9)  # open question 10 in Book 24's prose
BLIND_SPOT = "cons-conversion-blind-spot"
HESPER_ELEMENT = "agent-hesper"


@pytest.fixture(scope="module")
def pristine(tmp_path_factory):
    root = tmp_path_factory.mktemp("engagements") / "discovery"
    discovery.seed_discovery(root)
    return root


@pytest.fixture
def project(pristine, tmp_path):
    import shutil

    target = tmp_path / "discovery"
    shutil.copytree(pristine, target)
    return target


def store_for(project: Path) -> CanvasStore:
    return CanvasStore(project, discovery.SPRING)


def record_path(project: Path, number: int) -> Path:
    return project / ".auteur/beginner/studio/canvases" / discovery.SPRING / "architecture/books" / str(number) / "current.json"


def artifact_of(project: Path, number: int) -> dict:
    return json.loads(json.dumps(json.loads(record_path(project, number).read_text(encoding="utf-8"))["artifact"]))


def respond(request: dict, artifact: dict) -> dict:
    return build_host_agent_response(HostAgentRequest(**request), json.dumps(artifact), runtime="engagement-test").model_dump()


def element(artifact: dict, identifier: str) -> dict:
    for collection in ("series_consequences", "engines", "agents", "inherited", "later_possibilities", "assumptions",
                       "alternatives", "unresolved", "local_resolution"):
        for item in artifact.get(collection) or []:
            if item.get("id") == identifier:
                return item
    raise AssertionError(identifier)


def make_explicit(item: dict) -> None:
    if item.get("provenance") is not None:
        item.pop("provenance")
        item["attribution"], item["epistemic_status"] = "agent_proposed", "asserted"


def associate(store, project: Path, number: int, identifier: str, questions: list[str]) -> None:
    """A reviewed revision that records the element's associations, through the owner: request, answer, review, apply.

    The request names the associations, so the owner adds the element to the revision's scope and states what was asked.
    """
    artifact = artifact_of(project, number)
    item = element(artifact, identifier)
    make_explicit(item)
    item.setdefault("refs", []).extend({"kind": "series_question", "id": question} for question in questions)
    prepared = book_prepare(store, number, associations=tuple(
        {"element_id": identifier, "question_id": question} for question in questions))
    book_complete(store, number, respond(prepared["request"], artifact))
    assert book_apply_review(store, number, prepared["pending_request_sha256"])["result"] == "applied"


def reconcile_whole_book(store, project: Path, number: int) -> None:
    """Book 25 still cites the concept the working Architecture removed: only a whole-Book revision brings it up to date."""
    artifact = reconciled(project, number)
    prepared = book_prepare(store, number, instruction="Stop citing the concept the working Architecture removed.",
                            holistic=True)
    book_complete(store, number, respond(prepared["request"], artifact))
    assert book_apply_review(store, number, prepared["pending_request_sha256"])["result"] == "applied"


@pytest.fixture
def engaged(project):
    """Identities are given, then Books 24 and 25 engage the conversion settlement question through their blind spot."""
    store = store_for(project)
    impact.revise_architecture(store, "Give each open question a stable identity.", assign_identities)
    reconcile_whole_book(store, project, 25)
    associate(store, project, 24, BLIND_SPOT, [CONVERSION])
    associate(store, project, 25, BLIND_SPOT, [CONVERSION])
    return store


def engagements(packet: dict, question_id: str) -> list[dict]:
    return next(row for row in packet["questions"] if row["id"] == question_id)["engagements"]


def test_a_question_lists_each_element_that_engages_it_as_an_element_and_never_as_a_decision(engaged, project):
    packet = build_question_deliberation(engaged, [CONVERSION, HESPER])
    rows = engagements(packet, CONVERSION)
    assert [(row["book_number"], row["element_id"]) for row in rows] == [(24, BLIND_SPOT), (25, BLIND_SPOT)]
    for row in rows:
        assert row["basis"] == "book_element_association"
        assert row["authority"] == "working_book_element_noncanonical"
        assert row["attribution"] is not None and row["commitment_authority"]  # the element's own authority, unchanged
        assert row["standing"] == "current_wording"
        assert row["recorded"]["index"] == 5
    # The decision-only `books` field keeps its meaning: no element association is repackaged as a decision.
    assert all(entry["basis"] == "book_decision" for entry in next(q for q in packet["questions"] if q["id"] == CONVERSION)["books"])


def test_several_books_engaging_one_question_are_spread_so_that_no_single_book_takes_the_allowance():
    entries = [{"book_number": 1, "element_id": f"e{i}"} for i in range(6)] + [{"book_number": 2, "element_id": "x"}]
    chosen, omitted = _spread(entries, 4)
    assert [(entry["book_number"], entry["element_id"]) for entry in chosen] == [(1, "e0"), (2, "x"), (1, "e1"), (1, "e2")]
    assert omitted == 3
    assert _spread(entries, 20)[1] == 0


def test_an_element_that_records_two_selected_questions_is_a_fact_about_its_record_not_a_relation(engaged, project):
    associate(engaged, project, 24, BLIND_SPOT, [COMPACT])  # the element now records two associations
    packet = build_question_deliberation(engaged, [CONVERSION, COMPACT])
    (co,) = [row for row in packet["co_references"] if row["basis"] == "recorded_element_co_reference"]
    assert (co["book_number"], co["element_id"]) == (24, BLIND_SPOT)
    assert co["question_ids"] == sorted([CONVERSION, COMPACT])
    assert "does not say the questions are related" in co["note"]


def test_positional_names_are_not_tied_to_a_question_when_their_version_recorded_no_identity(engaged):
    packet = build_question_deliberation(engaged, [CONVERSION, HESPER])
    assert packet["positional_observations"] == []  # the versions the prose was written against carry no identities
    (gap,) = [row for row in packet["named_gaps"] if row.get("gap") == "positional_names_untied"]
    assert gap["count"] >= 2
    assert "not shown as one" in gap["note"]


def test_a_changed_element_is_reported_by_the_standing_of_its_engagement(engaged, project):
    packet = build_question_deliberation(engaged, [CONVERSION, HESPER])
    artifact = artifact_of(project, 24)
    element(artifact, BLIND_SPOT)["text"] += " The finale must now answer it."
    prepared = book_prepare(engaged, 24, instruction="Sharpen the blind spot's wording.", targets=(BLIND_SPOT,))
    book_complete(engaged, 24, respond(prepared["request"], artifact))
    assert book_apply_review(engaged, 24, prepared["pending_request_sha256"])["result"] == "applied"

    standing = {(row["book_number"], row["element_id"], row["question_id"]): row["standing"]
                for row in deliberation_standing(engaged, packet) if row["kind"] == "book_element_association"}
    assert standing[(24, BLIND_SPOT, CONVERSION)] == "element_changed"
    assert standing[(25, BLIND_SPOT, CONVERSION)] == "current"


def test_an_engagement_carries_the_typed_dependencies_the_book_records_for_its_element(engaged, project):
    rows = engagements(build_question_deliberation(engaged, [CONVERSION, HESPER]), CONVERSION)
    (book_24,) = [row for row in rows if row["book_number"] == 24]
    recorded = [edge for edge in artifact_of(project, 24)["typed_edges"]
                if edge["source"] == BLIND_SPOT or (edge["target"]["kind"] == "book_element" and edge["target"]["id"] == BLIND_SPOT)]
    assert len(book_24["dependencies"]) == min(len(recorded), 2)
    assert {dep["dependency"] for dep in book_24["dependencies"]} <= {edge["dependency"] for edge in recorded}


def test_the_discovery_packet_carries_engagements_and_the_answer_must_cite_an_engaged_question(engaged):
    def possibility(questions, evidence, basis):
        return {
            "title": "A blind spot that the conversion question names", "kind": "productive_tension",
            "possibility": "The blind spot could make the settlement question a stage rather than a settlement.",
            "significance": "It would change how the finale reads the Book 20 conversion.",
            "questions": questions, "evidence": evidence, "basis": basis,
            "assumptions": [], "counterevidence": [], "gains": None, "costs": None,
            "next_investigation": "Ask what the blind spot costs the hand-light households.",
        }

    request = prepare_architecture_discovery(engaged, goal="Where do the conversion and Hesper's motive meet?")["pending"]["request"]
    packet = json.loads(request["user"])["discovery_packet"]
    shown = next(row for row in packet["questions"] if row["id"] == CONVERSION)["book_element_associations"]
    assert [(row["book_number"], row["element_id"]) for row in shown] == [(24, BLIND_SPOT), (25, BLIND_SPOT)]
    assert all(row["element_text"] for row in shown)

    engaged_ok = {"ref_kind": "book_element", "ref_id": BLIND_SPOT, "book_number": 24, "note": "It engages the conversion."}
    response = {"schema_version": 1, "coverage_note": "Read the two questions and the Book elements that engage them.",
                "possibilities": [possibility([CONVERSION, HESPER], [engaged_ok], "speculative")],
                "no_possibility_reason": None, "uncertainties": []}
    complete_architecture_discovery(engaged, build_host_agent_response(
        HostAgentRequest(**request), json.dumps(response), runtime="engagement-test").model_dump())
    (row,) = project_architecture_discoveries(engaged)["discoveries"]
    assert row["possibilities"][0]["evidence"][0]["ref_kind"] == "book_element"


def test_an_element_is_refused_as_evidence_for_a_question_it_does_not_engage(engaged):
    request = prepare_architecture_discovery(engaged, goal=None)["pending"]["request"]
    # The blind spot engages the conversion question only. A possibility on Hesper and Compact cannot cite it.
    not_engaged = {"ref_kind": "book_element", "ref_id": BLIND_SPOT, "book_number": 24, "note": "Read against Hesper."}
    response = {"schema_version": 1, "coverage_note": "Read the questions.",
                "possibilities": [{
                    "title": "Hesper and the blind spot", "kind": "thematic_resonance",
                    "possibility": "Hesper's motive and the blind spot could share a cause.",
                    "significance": "It would tie two questions together.", "questions": [HESPER, COMPACT],
                    "evidence": [not_engaged], "basis": "speculative", "assumptions": [], "counterevidence": [],
                    "gains": None, "costs": None, "next_investigation": "Ask whether they share a cause.",
                }], "no_possibility_reason": None, "uncertainties": []}
    with pytest.raises(ValueError, match="cons-conversion-blind-spot"):
        complete_architecture_discovery(engaged, build_host_agent_response(
            HostAgentRequest(**request), json.dumps(response), runtime="engagement-test").model_dump())


def test_a_grounded_possibility_cannot_rest_on_a_book_element_alone():
    evidence = DiscoveredEvidence(ref_kind="book_element", ref_id=BLIND_SPOT, book_number=24, note="It engages the question.")
    assert evidence.ref_kind == "book_element"
    with pytest.raises(ValidationError):
        DiscoveredEvidence(ref_kind="book_element", ref_id=BLIND_SPOT, note="No book number is named.")


def test_the_discovery_instruction_says_an_association_is_engagement_and_not_significance():
    assert "book_element" in DISCOVERY_SYSTEM
    assert "An association is evidence that an element engages the question." in DISCOVERY_SYSTEM
    assert "not evidence that the element matters more" in DISCOVERY_SYSTEM
