"""A working Book discovery brought to Architecture inquiry, and optionally to a reviewed Architecture revision.

The discovery study project (``scripts/seed_book_discovery_study.py``) is Spring Ledger after the #635 run:
Book 24 records an unresolved question ``unk-tally-hours`` that cites the Ledger engine (``eng_ledger``).
The inquiry owner verifies the Book element against the revision the author read, anchors only on concepts it
records, and keeps it apart from the author's question; the revision owner carries it forward from a selected
alternative and says whether it is still current. Nothing here writes a Book, the canvas or the Series.
"""
import copy
import hashlib
import json
import shutil
import sys
from pathlib import Path

import pytest

from auteur.beginner.persistence import BeginnerConcurrencyError
from auteur.beginner.studio_architecture import (
    apply_architecture_review, complete_architecture, prepare_architecture, project_architecture,
)
from auteur.beginner.studio_architecture_inquiry import (
    complete_architecture_inquiry, prepare_architecture_inquiry, project_architecture_inquiry,
)
from auteur.beginner.studio_series_context import project_series_context
from auteur.beginner.studio_store import CanvasStore
from auteur.host_agent import HostAgentRequest, build_host_agent_response
from auteur.series.working_book_architecture import book_element_evidence

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))
import seed_book_discovery_study as seed  # noqa: E402

CANVAS = seed.SPRING
QUESTION = "Book 24 leaves open whether the Council's tally is the ledger's hours column. Should the Ledger engine decide it?"


@pytest.fixture(scope="module")
def pristine(tmp_path_factory):
    root = tmp_path_factory.mktemp("book-discovery") / "discovery"
    seed.seed_discovery(root)
    return root


@pytest.fixture
def project(pristine, tmp_path):
    target = tmp_path / "discovery"
    shutil.copytree(pristine, target)
    return target


def store_of(project):
    return CanvasStore(project, CANVAS)


def snapshot(root: Path, *, skip: Path | None = None) -> dict[str, str]:
    return {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(root.rglob("*")) if p.is_file() and not p.name.endswith(".lock")
            and (skip is None or skip not in p.parents)}


def arch_dir(project):
    return project / ".auteur/beginner/studio/canvases" / CANVAS / "architecture"


def book_dir(project, n=24):
    return arch_dir(project) / "books" / str(n)


def evidence_ref(project, n=24, element=seed.DISCOVERY):
    seen = book_element_evidence(store_of(project), n, element)
    return {"book_number": n, "element_id": element, "expected_book_request_sha256": seen["book_request_sha256"],
            "expected_element_content_sha256": seen["element"]["content_sha256"]}


def intent(project, operation="explore", anchors=(("node", seed.LEDGER),), text=QUESTION, evidence=True):
    current = project_architecture(store_of(project))
    payload = {"version": 1, "canvas_id": CANVAS, "operation": operation,
               "expected_candidate_request_sha256": current["candidate_request_sha256"],
               "anchors": [{"kind": k, "id": i} for k, i in anchors], "author_text": text}
    if evidence:
        payload["book_evidence"] = evidence if isinstance(evidence, dict) else evidence_ref(project)
    return payload


def answer(view, *, hypotheses=2):
    result = {"schema_version": 1, "analysis": "The tally question rests on what the Ledger engine counts.",
              "recorded_observations": [{"kind": "node", "id": seed.LEDGER,
                                         "claim": "The Ledger engine now records hours beside the mark."}],
              "hypotheses": [
                  {"title": "The tally is the hours column", "divergence_axis": "causal_engine",
                   "description": "The Council reads draw straight from the ledger's hours; refusing the count removes a hand from draw."},
                  {"title": "The tally is a separate count", "divergence_axis": "social_scale",
                   "description": "The Council keeps its own tally that feeds the ledger; the column and the tally can disagree."},
              ][:hypotheses],
              "uncertainties": ["Whether any Book depends on the two counts agreeing."]}
    return build_host_agent_response(HostAgentRequest(**view["request"]), json.dumps(result), runtime="test-agent").model_dump()


def ask(project, **kw):
    return prepare_architecture_inquiry(store_of(project), intent(project, **kw))


def edit_book_element(project, n=24, element=seed.DISCOVERY, suffix=" (edited)", holistic=False):
    """Change the working Book through its own owner: a targeted revision of one element, applied."""
    from auteur.beginner.studio_book_development import (
        apply_book_revision, complete_book_revision, prepare_book_revision, project_book_development)
    view = project_book_development(project, CANVAS, n)
    scope = {"holistic": True} if holistic else {"targets": [element]}
    view = prepare_book_revision(project, CANVAS, n, {"instruction": "Sharpen it.", **scope,
                                                      "expected_book_request_sha256": view["book"]["request_sha256"]})
    artifact = json.loads((book_dir(project, n) / "current.json").read_text(encoding="utf-8"))["artifact"]
    for item in artifact["unresolved"]:
        if item["id"] == element:
            item["text"] += suffix
    view = complete_book_revision(project, CANVAS, n, build_host_agent_response(
        HostAgentRequest(**view["request"]), json.dumps(artifact), runtime="test").model_dump())
    apply_book_revision(project, CANVAS, n, {"request_sha256": view["pending"]["request_sha256"]})


def test_book_evidence_reaches_the_inquiry_apart_from_the_question_and_writes_only_the_inquiry(project):
    outside = snapshot(project, skip=arch_dir(project) / "inquiries")
    view = ask(project)
    assert view["status"] == "awaiting_host_agent" and view["book_evidence_status"] == "current"
    packet = json.loads(view["request"]["user"])
    assert packet["author_question"] == QUESTION  # the Book's words are not put into the author's question
    evidence = packet["book_evidence"]
    assert evidence["authority"] == "working_book_observation_noncanonical"
    assert evidence["element"]["id"] == seed.DISCOVERY and evidence["element"]["epistemic_status"] == "unresolved"
    assert evidence["element"]["attribution"] == "agent_proposed"
    assert evidence["book"]["revision_number"] == 1 and evidence["book"]["written_against_current_architecture"]
    assert evidence["cited_architecture_concepts"] == [
        {"node_id": seed.LEDGER, "status": "unchanged", "present": True, "title": "Ledger engine", "used_as_anchor": True}]
    assert "book_evidence" in view["request"]["system"] or "legitimate answer that the observation should stay local" in view["request"]["system"]
    settings = view["request"]["settings"]["book_evidence"]
    assert settings["book_number"] == 24 and settings["element_id"] == seed.DISCOVERY
    assert snapshot(project, skip=arch_dir(project) / "inquiries") == outside


def test_only_concepts_the_element_records_can_anchor_its_evidence(project):
    # A concept the element only names in its wording, or does not mention, is not a recorded reference.
    with pytest.raises(ValueError, match="every anchor must be a current Architecture concept the element records"):
        ask(project, anchors=(("node", "eng_source"),))
    with pytest.raises(ValueError, match="every anchor must be"):
        ask(project, anchors=(("node", seed.LEDGER), ("node", "th_custody")), operation="compare")


def test_a_removed_concept_cannot_anchor_and_an_element_with_no_current_concept_is_unsupported(project):
    """Book 25 was never reconciled, so two of its elements still record the removed Gate Table."""
    removed = seed.impact.REMOVED_NODE
    # inh-gate-independence records the Gate Table and the Hollow Gate: the Hollow Gate can anchor,
    # the Gate Table is reported as removed and is never recreated.
    ref = evidence_ref(project, 25, "inh-gate-independence")
    with pytest.raises(ValueError, match="no longer has; it can be read as historical evidence but cannot anchor"):
        ask(project, anchors=(("node", removed),), evidence=ref)
    view = ask(project, anchors=(("node", "str_hollow_gate"),), evidence=ref)
    cited = json.loads(view["request"]["user"])["book_evidence"]["cited_architecture_concepts"]
    assert {c["node_id"]: c["status"] for c in cited} == {removed: "removed", "str_hollow_gate": "unchanged"}
    assert "inst_gate_table" not in {n["id"] for n in json.loads(view["request"]["user"])["working_candidate"]["nodes"]}
    # later-cohort-seat records only the Gate Table: there is no current concept to ask about.
    with pytest.raises(ValueError, match="records no reference to a concept the current working architecture has"):
        ask(project, anchors=(("node", seed.LEDGER),), evidence=evidence_ref(project, 25, "later-cohort-seat"))


def test_a_book_that_changed_since_it_was_read_is_refused(project):
    ref = evidence_ref(project)
    edit_book_element(project)
    with pytest.raises(BeginnerConcurrencyError, match="changed since you read it"):
        ask(project, evidence=ref)


def test_a_waiting_inquiry_goes_stale_when_its_book_evidence_changes_and_its_answer_is_refused(project):
    view = ask(project)
    edit_book_element(project)
    stale = project_architecture_inquiry(store_of(project))
    assert stale["status"] == "stale" and stale["book_evidence_status"] == "changed"
    folder = arch_dir(project) / "inquiries/requests" / view["request_sha256"]
    with pytest.raises(BeginnerConcurrencyError, match="working Book element this inquiry was asked about changed"):
        complete_architecture_inquiry(store_of(project), answer(view))
    assert (folder / "stale_response.json").is_file() and not (folder / "result.json").exists()


def test_a_completed_answer_keeps_its_book_evidence_as_history_when_the_book_changes(project):
    view = ask(project)
    done = complete_architecture_inquiry(store_of(project), answer(view))
    assert done["status"] == "ready" and done["result"]["book_evidence"]["element"]["id"] == seed.DISCOVERY
    edit_book_element(project)
    later = project_architecture_inquiry(store_of(project))
    assert later["status"] == "ready" and later["book_evidence_status"] == "changed"


def test_an_unreadable_book_is_refused_plainly(project):
    ref = evidence_ref(project)
    (book_dir(project) / "current.json").write_text("{damaged", encoding="utf-8")
    with pytest.raises(ValueError, match="cannot be read"):
        ask(project, evidence=ref)


def test_the_no_change_outcome_leaves_the_architecture_and_every_book_as_they_were(project):
    before = snapshot(project, skip=arch_dir(project) / "inquiries")
    view = ask(project)
    complete_architecture_inquiry(store_of(project), answer(view))
    # The author reads the alternatives and develops none of them.
    assert snapshot(project, skip=arch_dir(project) / "inquiries") == before
    assert project_architecture(store_of(project))["status"] == "ready"


def test_a_selected_alternative_carries_its_book_evidence_into_a_reviewed_revision_and_on_to_impact(project):
    store = store_of(project)
    view = ask(project)
    done = complete_architecture_inquiry(store, answer(view))
    sha = done["request_sha256"]
    books_before = snapshot(arch_dir(project) / "books")
    instruction = "Develop h2: the Council keeps its own tally that feeds the ledger."
    current = project_architecture(store)
    prepared = prepare_architecture(store, instruction, graph_intent={
        "version": 1, "canvas_id": CANVAS, "operation": "revise",
        "expected_candidate_request_sha256": current["candidate_request_sha256"],
        "anchors": [{"kind": "node", "id": seed.LEDGER}], "author_text": instruction},
        selected_alternative={"inquiry_request_sha256": sha, "hypothesis_id": "h2"})
    packet = json.loads(prepared["request"]["user"])
    chosen = packet["selected_creative_alternative"]
    assert chosen["hypothesis_id"] == "h2" and chosen["authority"] == "noncanonical_creative_alternative"
    assert chosen["book_evidence"]["element"]["id"] == seed.DISCOVERY
    assert chosen["book_evidence"]["status_at_revision"] == "current"
    revised = copy.deepcopy(json.loads((arch_dir(project) / "current.json").read_text(encoding="utf-8"))["candidate"])
    next(n for n in revised["nodes"] if n["id"] == seed.LEDGER)["summary"] += (
        " The Council keeps its own tally of hands, which feeds the hours column; the two can disagree.")
    complete_architecture(store, build_host_agent_response(HostAgentRequest(**prepared["request"]),
                                                           json.dumps(revised), runtime="test").model_dump())
    review = project_architecture(store)
    assert review["status"] == "review_ready"
    assert review["review"]["selected_creative_alternative"]["book_evidence"]["book"]["book_number"] == 24
    assert snapshot(arch_dir(project) / "books") == books_before  # nothing about a Book changed yet
    apply_architecture_review(store, review["review"]["request_sha256"])
    # The Book that supplied the discovery is not modified or reconciled; it now cites a changed concept.
    assert snapshot(arch_dir(project) / "books") == books_before
    books = {b["book_number"]: b for b in project_series_context(project, CANVAS)["sources"]["working_books"]["books"]}
    for n in (24, 25):
        assert {r["node_id"]: r["status"] for r in books[n]["references"]}[seed.LEDGER] == "changed"
    assert books[24]["freshness"] == "stale" and books[24]["revision_number"] == 1


def test_a_revision_from_an_alternative_whose_book_changed_marks_the_evidence_historical(project):
    store = store_of(project)
    view = ask(project)
    sha = complete_architecture_inquiry(store, answer(view))["request_sha256"]
    edit_book_element(project)
    instruction = "Develop h1."
    current = project_architecture(store)
    prepared = prepare_architecture(store, instruction, graph_intent={
        "version": 1, "canvas_id": CANVAS, "operation": "revise",
        "expected_candidate_request_sha256": current["candidate_request_sha256"],
        "anchors": [{"kind": "node", "id": seed.LEDGER}], "author_text": instruction},
        selected_alternative={"inquiry_request_sha256": sha, "hypothesis_id": "h1"})
    chosen = json.loads(prepared["request"]["user"])["selected_creative_alternative"]
    assert chosen["book_evidence"]["status_at_revision"] == "changed"
    assert chosen["book_evidence"]["status_note"].startswith("Historical:")


def test_an_architecture_change_makes_the_inquiry_stale(project):
    view = ask(project)
    seed.impact.reword_unrelated(store_of(project))
    assert project_architecture_inquiry(store_of(project))["status"] == "stale"
    with pytest.raises(BeginnerConcurrencyError, match="inquiry baseline or design context changed"):
        complete_architecture_inquiry(store_of(project), answer(view))


def test_book_evidence_is_only_for_the_current_architecture(project):
    payload = intent(project)
    payload["target"] = "pending_review"
    with pytest.raises(ValueError, match="current working architecture, not to a pending revision"):
        prepare_architecture_inquiry(store_of(project), payload)


def test_a_later_inquiry_sees_an_earlier_book_answer_labelled_and_with_its_live_status(project):
    view = ask(project)
    complete_architecture_inquiry(store_of(project), answer(view))
    edit_book_element(project)
    later = prepare_architecture_inquiry(store_of(project), intent(project, operation="explain", evidence=False,
                                                                     text="What does the Ledger engine record now?"))
    packet = json.loads(later["request"]["user"])
    prior = packet["prior_exchanges"][-1]
    assert prior["book_evidence"] == {"book_number": 24, "element_id": seed.DISCOVERY, "revision_number": 1,
                                      "status": "changed", "authority": "working_book_observation_noncanonical"}
    assert "historical when its status is changed or unreadable" in later["request"]["system"]
    assert "book_evidence" not in packet  # the later question itself brought none


def test_an_applied_revision_reports_its_book_evidence_as_it_stands_now(project):
    from auteur.beginner.studio_architecture import project_architecture_resume
    store = store_of(project)
    sha = complete_architecture_inquiry(store, answer(ask(project)))["request_sha256"]
    instruction = "Develop h2."
    current = project_architecture(store)
    prepared = prepare_architecture(store, instruction, graph_intent={
        "version": 1, "canvas_id": CANVAS, "operation": "revise",
        "expected_candidate_request_sha256": current["candidate_request_sha256"],
        "anchors": [{"kind": "node", "id": seed.LEDGER}], "author_text": instruction},
        selected_alternative={"inquiry_request_sha256": sha, "hypothesis_id": "h2"})
    assert "selected_creative_alternative.book_evidence is the working Book element" in prepared["request"]["system"]
    revised = copy.deepcopy(json.loads((arch_dir(project) / "current.json").read_text(encoding="utf-8"))["candidate"])
    next(n for n in revised["nodes"] if n["id"] == seed.LEDGER)["summary"] += " The tally feeds the column."
    complete_architecture(store, build_host_agent_response(HostAgentRequest(**prepared["request"]),
                                                           json.dumps(revised), runtime="test").model_dump())
    apply_architecture_review(store, project_architecture(store)["review"]["request_sha256"])
    row = project_architecture_resume(store)["creative_adoption_lineage"][0]
    assert row["book_evidence"]["status_at_revision"] == "current" and row["book_evidence"]["status_now"] == "current"
    assert "when this revision was prepared" in row["book_evidence"]["status_note"]
    edit_book_element(project, holistic=True)  # Book 24 is out of date after the revision: whole-Book only
    row = project_architecture_resume(store)["creative_adoption_lineage"][0]
    assert row["book_evidence"]["status_at_revision"] == "current" and row["book_evidence"]["status_now"] == "changed"


def test_a_typed_link_is_not_brought_as_an_observation(project):
    from auteur.series.working_book_architecture import book_elements
    edge = next(e for e in book_elements(store_of(project), 24) if e["collection"] == "typed_edges" and e["series_refs"])
    with pytest.raises(ValueError, match="typed link of Book 24, not an observation"):
        ask(project, anchors=(("node", edge["series_refs"][0]),), evidence=evidence_ref(project, 24, edge["id"]))


def test_the_cli_takes_book_and_element_together_and_refuses_a_damaged_book_plainly(project, tmp_path):
    import subprocess
    env = dict(__import__("os").environ, PYTHONPATH=str(REPO / "src"), PYTHONUTF8="1")
    question = tmp_path / "q.txt"
    question.write_text("Does this belong to the Architecture?", encoding="utf-8")
    base = [sys.executable, "-m", "auteur.beginner.studio_architecture_inquiry", "--project", str(project),
            "--canvas", CANVAS, "prepare", "--op", "explain", "--anchor", f"node:{seed.LEDGER}", "--text-file", str(question)]
    lonely = subprocess.run([*base, "--element", seed.DISCOVERY], capture_output=True, text=True, env=env)
    assert lonely.returncode != 0 and "--book and --element go together" in lonely.stderr
    (book_dir(project) / "current.json").write_text("{damaged", encoding="utf-8")
    damaged = subprocess.run([*base, "--book", "24", "--element", seed.DISCOVERY], capture_output=True, text=True,
                             encoding="utf-8", env=env)
    assert damaged.returncode == 1 and json.loads(damaged.stdout)["result"] == "rejected" and "Traceback" not in damaged.stderr
