"""The author's journey on a persistent question, through the owners.

An author asks about the question a Book decision refers to. The coding agent offers alternatives, which change
nothing. The author selects one and asks for a reviewed Architecture revision, which rewords the question while keeping
its identity. The review shows the change before Apply; Apply is explicit. Each Book whose decision refers to the
question then reports the change against its own recorded version. No Book is rewritten, no decision is answered or
accepted, and nothing is settled on the author's behalf.
"""
import copy
import json
import shutil
import sys
from pathlib import Path

import pytest

from auteur.beginner.studio_architecture import (
    _candidate,
    apply_architecture_review,
    complete_architecture,
    prepare_architecture,
    project_architecture,
)
from auteur.beginner.studio_architecture_inquiry import (
    complete_architecture_inquiry,
    prepare_architecture_inquiry,
    project_architecture_inquiry,
)
from auteur.beginner.studio_store import CanvasStore
from auteur.host_agent import HostAgentRequest, build_host_agent_response
from auteur.series.working_book_architecture import (
    book_apply_review,
    book_complete,
    book_element_evidence,
    book_prepare,
    book_series_references,
)

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))
sys.path.insert(0, str(REPO / "tests"))
import seed_book_discovery_study as discovery  # noqa: E402
import seed_book_impact_study as impact  # noqa: E402
from test_beginner_studio_book_impact import reconciled  # noqa: E402
from test_persistent_narrative_questions import assign_identities, identity_for  # noqa: E402

GATE = 14  # the Gate Table question's position in the Spring Ledger study
GATE_ID = identity_for(GATE)
REWORDED = " Whether the Council may pass through it, as the mechanism reading asks."


@pytest.fixture(scope="module")
def pristine(tmp_path_factory):
    root = tmp_path_factory.mktemp("question-journey") / "discovery"
    discovery.seed_discovery(root)
    return root


@pytest.fixture
def project(pristine, tmp_path):
    target = tmp_path / "discovery"
    shutil.copytree(pristine, target)
    return target


def reconcile(store: CanvasStore, project: Path, number: int) -> None:
    """A whole-Book revision against the current Architecture, as the Book's own owner runs it."""
    prepared = book_prepare(store, number, instruction="Bring the Book up to date with the Architecture.", holistic=True)
    book_complete(store, number, build_host_agent_response(
        HostAgentRequest(**prepared["request"]), json.dumps(reconciled(project, number)), runtime="journey").model_dump())
    assert book_apply_review(store, number, prepared["pending_request_sha256"])["currentness"] == "current"


def decision(store: CanvasStore, number: int, decision_id: str = "dec-gate-table") -> dict:
    return next(r for r in book_series_references(store, number)["question_references"] if r["decision_id"] == decision_id)


def test_the_author_journey_from_a_question_to_an_applied_revision_and_its_impact(project):
    store = CanvasStore(project, discovery.SPRING)
    impact.revise_architecture(store, "Give each open question a stable identity.", assign_identities)
    reconcile(store, project, 24)
    reconcile(store, project, 25)
    assert decision(store, 24)["state"] == "current_wording" and decision(store, 25)["state"] == "current_wording"

    # 1. The author asks about the question Book 24's decision refers to, with that decision as evidence.
    series = _candidate(store)
    old_text = series["candidate"]["open_questions"][GATE]
    evidence = book_element_evidence(store, 24, "dec-gate-table")
    view = prepare_architecture_inquiry(store, {
        "canvas_id": store.canvas_id, "target": "current", "operation": "explore",
        "expected_candidate_request_sha256": series["request_sha256"],
        "anchors": [{"kind": "question", "id": GATE_ID}],
        "author_text": "Does the decision still ask what the Architecture now asks? Consider other readings.",
        "book_evidence": {"book_number": 24, "element_id": "dec-gate-table",
                          "expected_book_request_sha256": evidence["book_request_sha256"],
                          "expected_element_content_sha256": evidence["element"]["content_sha256"]},
    })
    inquiry_sha = view["request"]["request_sha256"]

    # 2. The coding agent offers alternatives. The inquiry is advisory: the Architecture does not move.
    result = {
        "schema_version": 1,
        "analysis": "The question asks whether the Gate Table is accepted, or how it decides who may pass.",
        "recorded_observations": [{"kind": "question", "id": GATE_ID,
                                   "claim": "The Architecture records this question as open."}],
        "hypotheses": [
            {"title": "A standing question", "divergence_axis": "social_scale",
             "description": "The Gate Table stays open for the Council; the question is about standing."},
            {"title": "A mechanism question", "divergence_axis": "causal_engine",
             "description": "The Gate Table is a mechanism whose acceptance decides which hands may pass."},
        ],
        "uncertainties": ["Whether any Book depends on the Gate Table being accepted."],
    }
    complete_architecture_inquiry(store, build_host_agent_response(
        HostAgentRequest(**view["request"]), json.dumps(result), runtime="journey").model_dump())
    assert _candidate(store)["candidate"] == series["candidate"]
    alternatives = {row["id"]: row["title"] for row in project_architecture_inquiry(store)["result"]["hypotheses"]}
    assert alternatives == {"h1": "A standing question", "h2": "A mechanism question"}

    # 3. The author selects the second alternative and asks for a reviewed revision that carries it out.
    waiting = prepare_architecture(store, instruction="Reword the Gate Table question as the mechanism reading asks.",
                                   selected_alternative={"inquiry_request_sha256": inquiry_sha, "hypothesis_id": "h2"})
    revised = copy.deepcopy(series["candidate"])
    revised["open_questions"][GATE] = old_text + REWORDED
    complete_architecture(store, build_host_agent_response(
        HostAgentRequest(**waiting["request"]), json.dumps(revised), runtime="journey").model_dump())

    # 4. Before Apply the review shows the question change, and the Architecture is still the one it was.
    pending = project_architecture(store)
    row = next(r for r in pending["question_changes"]["questions"] if r["id"] == GATE_ID)
    assert row["status"] == "reworded" and row["previous_text"] == old_text
    assert _candidate(store)["candidate"]["open_questions"][GATE] == old_text
    books_before = {n: json.dumps(json.loads((project / ".auteur/beginner/studio/canvases" / discovery.SPRING
                                              / "architecture/books" / str(n) / "current.json").read_text(encoding="utf-8")),
                                 sort_keys=True) for n in (24, 25)}

    # 5. Explicit Apply. Books are not rewritten, and their decisions keep the version they were checked against.
    applied = apply_architecture_review(store, waiting["request"]["request_sha256"])
    assert _candidate(store)["candidate"]["open_questions"][GATE] == old_text + REWORDED
    assert _candidate(store)["candidate"]["open_question_ids"][GATE] == GATE_ID
    for number in (24, 25):
        record = json.loads((project / ".auteur/beginner/studio/canvases" / discovery.SPRING
                             / "architecture/books" / str(number) / "current.json").read_text(encoding="utf-8"))
        assert json.dumps(record, sort_keys=True) == books_before[number]

        # 6. Cross-Book impact: each Book reports the rewording against the version its decision was checked against.
        reference = decision(store, number)
        assert reference["state"] == "reworded", reference
        assert reference["question_id"] == GATE_ID
        assert reference["version_request_sha256"] == series["request_sha256"]
        assert reference["recorded_text"] == old_text
        assert reference["current_text"] == old_text + REWORDED

        # Authority: the decision is still an unresolved author decision; nothing was answered or accepted.
        entry = next(d for d in record["artifact"]["open_author_decisions"] if d["id"] == "dec-gate-table")
        # A legacy decision records "unresolved" as its provenance; a current one as its epistemic status.
        assert entry["provenance"] in (None, "unresolved") and entry["epistemic_status"] in (None, "unresolved")
        assert entry["attribution"] in (None, "derived")

    assert applied is not None
