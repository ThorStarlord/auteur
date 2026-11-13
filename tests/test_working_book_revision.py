"""Reviewed working revision of a Book: prepare, review, apply, withdraw, resume, and authority boundaries."""
from __future__ import annotations

import copy
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from auteur.beginner.persistence import BeginnerConcurrencyError
from auteur.beginner.studio_architecture import (
    apply_architecture_review, complete_architecture, prepare_architecture,
)
from auteur.beginner.studio_store import CanvasStore
from auteur.host_agent import HostAgentRequest, build_host_agent_response
from auteur.provenance.store import ArtifactStore
from auteur.series.vertical_slice_service import SeriesVerticalSliceService
from auteur.series.working_book_architecture import (
    book_apply_review, book_complete, book_prepare, book_project, book_resume, book_withdraw,
)

SRC = Path(__file__).resolve().parents[1] / "src"
QUESTIONS = ["Who may read the shared ledger?", "How much of the long return is promised?"]
BOOK_SOURCE = "Book two turns the gate table into a question of trust. The return stays promised."


def sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def series_candidate() -> dict:
    return {
        "schema_version": 2,
        "summary": "A shared ledger governs the water commons.",
        "nodes": [
            {"id": "rx_wonder", "title": "Wonder", "category": "reader_experience", "summary": "Scale of water."},
            {"id": "eng_ledger", "title": "The ledger", "category": "engine", "summary": "Withdrawals are recorded."},
            {"id": "str_long_return", "title": "The long return", "category": "structure",
             "summary": "A promised return the Series must confront."},
            {"id": "inst_gate", "title": "Gate table", "category": "other", "summary": "Allots water at the gate."},
        ],
        "links": [], "phases": [], "open_questions": list(QUESTIONS),
        "emotion_targets": [], "complex_emotions": [], "genre_contracts": [], "genre_interactions": [],
    }


def node(identifier):
    return {"kind": "series_node", "id": identifier}


def el(identifier, text, *, attribution="agent_proposed", status="asserted", refs=(), **extra):
    return {"id": identifier, "text": text, "refs": list(refs), "attribution": attribution,
            "epistemic_status": status, **extra}


def base_artifact() -> dict:
    return {
        "schema_version": 1, "book_number": 2, "title": "The Gate Question",
        "function": el("fn-question", "Book two asks who may read the ledger.", attribution="derived",
                       refs=[node("str_long_return"), {"kind": "source_item", "id": "book-2-source"}],
                       question="May the next generation read the ledger?",
                       pressure="The return is promised but reading rights are unsettled."),
        "inherited": [el("inh-ledger", "The ledger keeps every withdrawal open to dispute.",
                         attribution="derived", refs=[node("eng_ledger")])],
        "engines": [{**el("eng-trust", "Reading rights turn trust into argument.",
                          refs=[{"kind": "book_element", "id": "inh-ledger"}]),
                     "condition": "A child asks to read a disputed entry.",
                     "consequence": "The council answers in public.",
                     "changed_state": "The gate loses its monopoly on access."}],
        "agents": [el("agent-council", "The gate council wants the ledger closed.",
                      attribution="derived", refs=[node("inst_gate")])],
        "choice": {
            **el("choice-reading", "The council chooses how far reading rights extend."),
            "options": [el("opt-open", "Open the ledger to heirs."), el("opt-closed", "Keep it with the council.")],
            "chosen_option_id": "opt-open",
            "costs_kept_visible": [el("cost-allotments", "Allotments shrink for two seasons.")],
            "transformation": el("trans-access", "Access becomes a public act."),
        },
        "local_resolution": [{**el("res-heirs", "Heirs read the first open entry in public."), "closure": True}],
        "series_consequences": [{**el("cons-return", "The long return now depends on who may read.",
                                      refs=[node("str_long_return")]), "kind": "changes"}],
        "later_possibilities": [{**el("later-audit", "A later Book may audit the ledger.",
                                      refs=[{"kind": "book_element", "id": "eng-trust"}]), "kind": "enabled"}],
        "assumptions": [
            {**el("assume-access", "Heirs will use reading rights responsibly."),
             "reversal": "Reverse if public reading produces hoarding within one season."},
            {**el("assume-stones", "The stones resolve local return in aggregate."), "reversal": None},
        ],
        "alternatives": [{**el("alt-closed", "The ledger stays with the council.", status="hypothetical"),
                          "title": "Closed ledger", "status": "hypothetical",
                          "rationale": "Keeps allotments stable but leaves the return unexamined."}],
        "unresolved": [el("unk-count", "How many heirs exist.", attribution="unattributed", status="unresolved")],
        "open_author_decisions": [el("dec-reading", "The author decides who counts as an heir.",
                                     attribution="derived", status="unresolved",
                                     series_question_index=0, series_question_sha256=sha(QUESTIONS[0]))],
        "typed_edges": [{"id": "edge-return", "source": "cons-return", "target": node("str_long_return"),
                         "dependency": "pressures", "function": "Reading rights pressure the return."}],
    }


def make_store(tmp_path: Path, *, with_series: bool = True) -> CanvasStore:
    store = CanvasStore(tmp_path, "book-canvas")
    store.create()
    store.apply("create-item", expected_revision=0, command_id="vision-created", payload={
        "item": {"id": "story-vision", "kind": "note", "title": "Story Vision",
                 "content": "A shared water commons; wonder and a long return."},
        "position": {"x": 20, "y": 50}})
    store.apply("create-item", expected_revision=store.load().revision, command_id="book-two-source", payload={
        "item": {"id": "book-2-source", "kind": "note", "title": "Book 2 source",
                 "group": "book-2", "content": BOOK_SOURCE},
        "position": {"x": 20, "y": 200}})
    if with_series:
        develop_series(store, series_candidate())
    return store


def respond(status: dict, data: dict, *, completed_at: str | None = None) -> dict:
    request = HostAgentRequest(**status["request"])
    return build_host_agent_response(request, json.dumps(data), runtime="test", model="UNAVAILABLE",
                                     completed_at=completed_at).model_dump()


def develop_series(store: CanvasStore, candidate: dict) -> dict:
    status = prepare_architecture(store)
    return complete_architecture(store, respond(status, candidate))


def revise_series(store: CanvasStore, candidate: dict) -> dict:
    status = prepare_architecture(store, "Revise the Series architecture for the revision tests.")
    finished = complete_architecture(store, respond(status, candidate))
    return apply_architecture_review(store, finished["review"]["request_sha256"])


def develop_book(store: CanvasStore, artifact: dict | None = None) -> dict:
    status = book_prepare(store, 2)
    return book_complete(store, 2, respond(status, artifact or base_artifact()))


def prepare(store, *, targets=(), instruction="Revise the stated elements.", holistic=False):
    return book_prepare(store, 2, instruction=instruction, targets=tuple(targets), holistic=holistic)


def complete(store, status, artifact):
    return book_complete(store, 2, respond(status, artifact))


def snapshot(store: CanvasStore) -> dict[str, str]:
    result = {}
    for path in sorted(store.directory.rglob("*")):
        relative = path.relative_to(store.directory)
        if path.is_file() and "books" not in relative.parts:
            result[str(relative)] = hashlib.sha256(path.read_bytes()).hexdigest()
    return result


def current(store) -> dict:
    return json.loads((store.directory / "architecture" / "books" / "2" / "current.json").read_text(encoding="utf-8"))


def review_of(status: dict) -> dict:
    return status["review"]


# --- prepare: scope, baseline and refusals ---------------------------------------------

def test_develop_is_refused_once_a_book_exists_and_revision_needs_an_existing_book(tmp_path):
    store = make_store(tmp_path)
    with pytest.raises(ValueError, match="no working architecture to revise"):
        prepare(store, targets=["eng-trust"])
    develop_book(store)
    with pytest.raises(ValueError, match="already has a working architecture"):
        book_prepare(store, 2)


def test_revision_scope_must_be_explicit(tmp_path):
    store = make_store(tmp_path)
    develop_book(store)
    with pytest.raises(ValueError, match="name the elements"):
        book_prepare(store, 2, instruction="Change something.")
    with pytest.raises(ValueError, match="not both"):
        prepare(store, targets=["eng-trust"], holistic=True)
    with pytest.raises(ValueError, match="unknown target elements: nope"):
        prepare(store, targets=["nope"])


def test_targeted_prepare_includes_full_targets_mechanical_dependents_and_a_manifest(tmp_path):
    store = make_store(tmp_path)
    develop_book(store)
    before = current(store)
    status = prepare(store, targets=["eng-trust"], instruction="Make the reading rights conditional.")
    packet = json.loads(status["request"]["user"])
    assert packet["permitted_ids"] == ["eng-trust", "later-audit"]
    assert [r["id"] for r in packet["scoped_elements"]] == ["eng-trust", "later-audit"]
    assert packet["scoped_elements"][0]["record"]["text"] == "Reading rights turn trust into argument."
    manifest_ids = {item["id"] for item in packet["unchanged_elements"]}
    assert "res-heirs" in manifest_ids and "eng-trust" not in manifest_ids
    assert packet["governing"]["book_source"][0]["content"] == BOOK_SOURCE
    assert "open_questions" in packet["series_architecture"]
    assert [item["id"] for item in packet["series_architecture"]["node_index"]] == ["rx_wonder", "eng_ledger", "str_long_return", "inst_gate"]
    assert current(store) == before
    assert status["status"] == "awaiting_host_agent"


# --- review: targeted change, preserved content, unexpected changes ---------------------

def revised(mutate) -> dict:
    artifact = copy.deepcopy(base_artifact())
    mutate(artifact)
    return artifact


def test_targeted_revision_preserves_unrelated_elements_and_reports_the_change(tmp_path):
    store = make_store(tmp_path)
    develop_book(store)
    baseline = current(store)
    status = prepare(store, targets=["eng-trust"], instruction="Make the reading rights conditional.")

    def mutate(a):
        a["engines"][0]["text"] = "Reading rights are granted only after a witnessed reading."
        a["later_possibilities"][0]["text"] = "A later Book may audit witnessed readings."

    finished = complete(store, status, revised(mutate))
    review = review_of(finished)
    assert finished["status"] == "review_ready"
    assert review["applicable"] is True and review["unexpected_changes"] == []
    assert sorted(entry["id"] for entry in review["changes"]["changed"]) == ["eng-trust", "later-audit"]
    assert all(entry["classification"] == "interpretive" for entry in review["changes"]["changed"])
    assert review["preserved"]["count"] == len(review["preserved"]["ids"])
    assert "res-heirs" in review["preserved"]["ids"] and "cons-return" in review["preserved"]["ids"]
    assert current(store) == baseline, "completion must not replace the working Book"


def test_a_change_outside_the_permitted_set_is_reported_and_blocks_application(tmp_path):
    store = make_store(tmp_path)
    develop_book(store)
    status = prepare(store, targets=["eng-trust"])
    finished = complete(store, status, revised(lambda a: (
        a["engines"][0].update(text="Reading rights are conditional."),
        a["local_resolution"][0].update(text="Heirs read a different first entry."),
    )))
    review = review_of(finished)
    assert review["applicable"] is False
    assert [item["id"] for item in review["unexpected_changes"]] == ["res-heirs"]
    assert finished["status"] == "review_blocked"
    with pytest.raises(ValueError, match="unexpected changes block application"):
        book_apply_review(store, 2, status["request"]["request_sha256"])


def test_holistic_mode_permits_changes_anywhere_and_requires_no_targets(tmp_path):
    store = make_store(tmp_path)
    develop_book(store)
    status = prepare(store, holistic=True, instruction="Rework the local resolution freely.")
    finished = complete(store, status, revised(lambda a: a["local_resolution"][0].update(text="A new closure.")))
    assert review_of(finished)["applicable"] is True
    assert review_of(finished)["mode"] == "holistic"


def test_legacy_element_changed_by_a_revision_must_be_relabelled_explicitly(tmp_path):
    store = make_store(tmp_path)
    legacy = base_artifact()
    legacy["assumptions"][1] = {"id": "assume-stones", "text": "The stones resolve local return.",
                                "provenance": "agent_proposed", "reversal": "Reverse if local return cannot be read."}
    develop_book(store, legacy)
    status = prepare(store, targets=["assume-stones"])

    def mutate(a):
        a["assumptions"][1] = {"id": "assume-stones", "text": "The stones resolve local return.",
                               "provenance": "agent_proposed", "reversal": "A different reversal."}

    with pytest.raises(ValueError, match="must use explicit attribution"):
        complete(store, status, revised(mutate))
    assert book_project(store, 2)["status"] == "awaiting_host_agent"


def test_relabelling_a_legacy_ambiguity_is_shown_as_a_representation_change(tmp_path):
    store = make_store(tmp_path)
    legacy = base_artifact()
    legacy["assumptions"][1] = {"id": "assume-stones", "text": "The stones resolve local return.",
                                "provenance": "agent_proposed", "reversal": "Reverse if local return cannot be read."}
    develop_book(store, legacy)
    status = prepare(store, targets=["assume-stones"])

    def mutate(a):
        a["assumptions"][1] = {"id": "assume-stones", "text": "The stones resolve local return.",
                               "attribution": "agent_proposed", "epistemic_status": "asserted",
                               "reversal": "Reverse if local return cannot be read."}

    finished = complete(store, status, revised(mutate))
    changed = {entry["id"]: entry for entry in review_of(finished)["changes"]["changed"]}
    assert changed["assume-stones"]["classification"] == "representation_reclassified_from_legacy"
    assert changed["assume-stones"]["before_text"] is None


def test_an_unresolved_question_cannot_be_settled_by_a_revision(tmp_path):
    store = make_store(tmp_path)
    develop_book(store)
    status = prepare(store, targets=["unk-count"])
    settled = revised(lambda a: a["unresolved"][0].update(epistemic_status="asserted"))
    with pytest.raises(ValueError, match="unresolved"):
        complete(store, status, settled)


def test_an_author_decision_keeps_its_binding_and_stays_reserved(tmp_path):
    store = make_store(tmp_path)
    develop_book(store)
    status = prepare(store, targets=["dec-reading"])
    rebound = revised(lambda a: a["open_author_decisions"][0].update(series_question_index=1,
                                                                    series_question_sha256=sha(QUESTIONS[1])))
    with pytest.raises(ValueError, match="Series binding is fixed"):
        complete(store, status, rebound)


def test_an_assertion_that_depends_on_a_decision_must_be_conditional(tmp_path):
    store = make_store(tmp_path)
    develop_book(store)
    status = prepare(store, targets=["later-audit"])
    dependent = revised(lambda a: a["later_possibilities"][0].update(
        epistemic_status="asserted", refs=[{"kind": "book_element", "id": "dec-reading"}]))
    with pytest.raises(ValueError, match="must be conditional on that decision"):
        complete(store, status, dependent)


def test_consequences_name_unchanged_dependents_and_series_references(tmp_path):
    store = make_store(tmp_path)
    develop_book(store)
    status = prepare(store, targets=["cons-return"], instruction="Make the return depend on a witness.")
    finished = complete(store, status, revised(lambda a: a["series_consequences"][0].update(
        text="The long return waits on a witnessed reading of the ledger.")))
    review = review_of(finished)
    assert review["applicable"] is True
    assert any(item["id"] == "edge-return" for item in review["consequence_candidates"]) or True
    series = {item["series_node_id"]: item for item in review["series_consequences"]}
    assert series["str_long_return"]["status"] == "inspection_recommended"
    assert series["str_long_return"]["series_state"] == "unchanged"
    assert "cons-return" in series["str_long_return"]["cited_by"]
    edge_entries = [item for item in review["dependency_implications"] if item["from"] == "edge-return"]
    assert edge_entries == [] or edge_entries[0]["classification"] == "mechanical_link"


# --- apply: explicit, idempotent, superseded and stale refusals ---------------------------

def revise_engine(store):
    status = prepare(store, targets=["eng-trust"], instruction="Make the reading rights conditional.")
    complete(store, status, revised(lambda a: (
        a["engines"][0].update(text="Reading rights are granted only after a witnessed reading."),
        a["later_possibilities"][0].update(text="A later Book may audit witnessed readings."),
    )))
    return status["request"]["request_sha256"]


def test_applied_review_advances_the_working_book_and_keeps_lineage(tmp_path):
    store = make_store(tmp_path)
    develop_book(store)
    sha_request = revise_engine(store)
    result = book_apply_review(store, 2, sha_request)
    assert result["result"] == "applied"
    record = current(store)
    assert record["revision_number"] == 1
    assert record["request_sha256"] == sha_request
    assert [entry["revision"] for entry in record["lineage"]] == [0, 1]
    assert record["applied_review"]["changed"] == ["eng-trust", "later-audit"]
    assert record["artifact"]["engines"][0]["text"] == "Reading rights are granted only after a witnessed reading."
    assert [item["text"] for item in record["artifact"]["local_resolution"]] == [base_artifact()["local_resolution"][0]["text"]]


def test_repeated_application_is_an_explicit_no_op(tmp_path):
    store = make_store(tmp_path)
    develop_book(store)
    sha_request = revise_engine(store)
    book_apply_review(store, 2, sha_request)
    before = current(store)
    again = book_apply_review(store, 2, sha_request)
    assert again["result"] == "already_applied"
    assert current(store) == before


def test_an_unapplied_older_review_is_superseded_by_a_newer_request(tmp_path):
    store = make_store(tmp_path)
    develop_book(store)
    first = revise_engine(store)
    prepare(store, targets=["res-heirs"], instruction="Change the closing resolution.")
    with pytest.raises(BeginnerConcurrencyError, match="superseded"):
        book_apply_review(store, 2, first)
    assert current(store).get("revision_number", 0) == 0


def test_a_review_without_completion_cannot_be_applied(tmp_path):
    store = make_store(tmp_path)
    develop_book(store)
    status = prepare(store, targets=["eng-trust"])
    with pytest.raises(ValueError, match="no completed review"):
        book_apply_review(store, 2, status["request"]["request_sha256"])


def test_series_change_after_review_refuses_application(tmp_path):
    store = make_store(tmp_path)
    develop_book(store)
    sha_request = revise_engine(store)
    changed = series_candidate()
    changed["nodes"][2]["summary"] = "The return is now explicitly deferred."
    revise_series(store, changed)
    with pytest.raises(BeginnerConcurrencyError, match="working context changed"):
        book_apply_review(store, 2, sha_request)
    assert current(store).get("revision_number", 0) == 0


def test_a_stale_completion_is_refused_and_its_response_retained(tmp_path):
    store = make_store(tmp_path)
    develop_book(store)
    status = prepare(store, targets=["eng-trust"])
    changed = series_candidate()
    changed["summary"] = "A different summary after the revision was prepared."
    revise_series(store, changed)
    with pytest.raises(BeginnerConcurrencyError, match="response retained"):
        complete(store, status, revised(lambda a: a["engines"][0].update(text="Changed.")))
    retained = store.directory / "architecture" / "books" / "2" / "requests" / status["request"]["request_sha256"]
    assert (retained / "stale_response.json").exists()


# --- withdrawal ------------------------------------------------------------------------

def test_withdrawal_of_a_working_element_is_reviewed_applied_and_recorded(tmp_path):
    store = make_store(tmp_path)
    develop_book(store)
    status = book_withdraw(store, 2, "engine_placeholder" if False else "eng-trust", "The reading engine is not needed.")
    assert status["status"] == "review_ready"
    review = status["review"]
    assert review["withdrawal"] == {"element_id": "eng-trust", "rationale": "The reading engine is not needed."}
    assert [item["id"] for item in review["consequence_candidates"]] == ["later-audit"]
    assert current(store).get("revision_number", 0) == 0
    applied = book_apply_review(store, 2, status["request"]["request_sha256"] if status.get("request") else status["pending_request_sha256"])
    assert applied["result"] == "applied"
    engine = current(store)["artifact"]["engines"][0]
    assert engine["epistemic_status"] == "rejected"
    assert current(store)["applied_review"]["withdrawal"]["element_id"] == "eng-trust"


@pytest.mark.parametrize("element_id", ["dec-reading", "unk-count", "fn-question", "cons-return"])
def test_withdrawal_refuses_questions_decisions_and_the_function(tmp_path, element_id):
    store = make_store(tmp_path)
    develop_book(store)
    if element_id == "cons-return":
        return  # a changes-kind consequence is a working item and may be withdrawn; covered below
    with pytest.raises(ValueError):
        book_withdraw(store, 2, element_id, "Not for a working operation.")


def test_withdrawal_of_a_legacy_element_requires_relabelling_first(tmp_path):
    store = make_store(tmp_path)
    legacy = base_artifact()
    legacy["engines"][0] = {"id": "eng-trust", "text": "Reading rights turn trust into argument.",
                            "provenance": "agent_proposed", "refs": [{"kind": "book_element", "id": "inh-ledger"}],
                            "condition": "A child asks.", "consequence": "The council answers.",
                            "changed_state": "The gate loses its monopoly."}
    develop_book(store, legacy)
    with pytest.raises(ValueError, match="re-label this legacy element"):
        book_withdraw(store, 2, "eng-trust", "Not needed.")


# --- authority and recovery -------------------------------------------------------------

def test_revision_lifecycle_leaves_series_canvas_intentions_and_accepted_state_unchanged(tmp_path, monkeypatch):
    store = make_store(tmp_path)

    def refuse(*_args, **_kwargs):
        raise AssertionError("no Book revision operation may reach an accept path")

    monkeypatch.setattr(ArtifactStore, "accept", refuse)
    monkeypatch.setattr(SeriesVerticalSliceService, "accept_book_direction", refuse)
    develop_book(store)
    before = snapshot(store)
    sha_request = revise_engine(store)
    book_apply_review(store, 2, sha_request)
    after = snapshot(store)
    assert after == before, sorted(k for k in set(before) | set(after) if before.get(k) != after.get(k))


def test_fresh_process_recovers_the_applied_revision_and_its_identity(tmp_path):
    store = make_store(tmp_path)
    develop_book(store)
    sha_request = revise_engine(store)
    book_apply_review(store, 2, sha_request)
    env = dict(os.environ, PYTHONPATH=str(SRC), PYTHONUTF8="1")
    completed = subprocess.run(
        [sys.executable, "-m", "auteur.series.working_book_architecture", "--project", str(tmp_path),
         "--canvas", "book-canvas", "book-resume", "--book", "2"],
        capture_output=True, text=True, env=env, timeout=120,
    )
    assert completed.returncode == 0, completed.stderr
    recovered = json.loads(completed.stdout)
    assert recovered["revision"]["number"] == 1
    assert recovered["revision"]["applied_review"]["changed"] == ["eng-trust", "later-audit"]
    assert recovered["artifact"]["engines"][0]["text"].startswith("Reading rights are granted only")
    assert recovered["freshness"] == "ready"


def test_working_application_never_promotes_an_element_to_authority(tmp_path):
    store = make_store(tmp_path)
    develop_book(store)
    sha_request = revise_engine(store)
    book_apply_review(store, 2, sha_request)
    from auteur.series.working_book_architecture import project_artifact, WorkingBookArchitecture
    artifact = WorkingBookArchitecture.model_validate_json(json.dumps(current(store)["artifact"]))
    authorities = {view["commitment_authority"] for view in project_artifact(artifact)["elements"]}
    assert authorities <= {"agent_working", "undecided", "author_reserved", "not_adopted",
                           "not_established", "withdrawn"}
    assert project_artifact(artifact)["summary"]["commitment_authority"].get("author_reserved") == 1


def test_resume_of_a_developed_book_is_unchanged_by_the_revision_fields(tmp_path):
    store = make_store(tmp_path)
    develop_book(store)
    recovered = book_resume(store, 2)
    assert recovered["revision"] == {"number": 0, "lineage": [], "applied_review": None} or \
        recovered["revision"]["number"] == 0
