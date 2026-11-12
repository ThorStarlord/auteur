"""Working Book Architecture: develop, persist, fresh-process resume, and authority boundaries."""
from __future__ import annotations

import copy
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest
from pydantic import ValidationError

from auteur.beginner.persistence import BeginnerConcurrencyError
from auteur.beginner.studio_architecture import (
    apply_architecture_review, complete_architecture, prepare_architecture,
)
from auteur.beginner.studio_store import CanvasStore
from auteur.host_agent import HostAgentRequest, build_host_agent_response
from auteur.provenance.store import ArtifactStore
from auteur.series import working_book_architecture as wba
from auteur.series.vertical_slice_service import SeriesVerticalSliceService
from auteur.series.working_book_architecture import (
    WorkingBookArchitecture, book_complete, book_prepare, book_project, book_resume,
)

SRC = Path(__file__).resolve().parents[1] / "src"
QUESTIONS = [
    "Who may read the shared ledger?",
    "How much of the long return is promised?",
]


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def series_candidate() -> dict:
    return {
        "schema_version": 2,
        "summary": "A shared ledger governs the water commons across generations.",
        "nodes": [
            {"id": "rx_wonder", "title": "Wonder at the commons", "category": "reader_experience",
             "summary": "Readers feel the scale of shared water."},
            {"id": "eng_ledger", "title": "The ledger", "category": "engine",
             "summary": "Every withdrawal is recorded and can be disputed."},
            {"id": "str_long_return", "title": "The long return", "category": "structure",
             "summary": "A promised return that the Series must eventually confront."},
            {"id": "inst_gate", "title": "Gate table", "category": "other",
             "summary": "An institution that allots water at the gate."},
        ],
        "links": [{"id": "ledger_to_return", "source": "eng_ledger", "target": "str_long_return",
                   "function": "the ledger keeps the return open"}],
        "phases": [],
        "open_questions": list(QUESTIONS),
        "emotion_targets": [],
        "complex_emotions": [],
        "genre_contracts": [],
        "genre_interactions": [],
    }


BOOK_SOURCE = (
    "Book two turns the gate table into a question of trust. The council must decide whether "
    "the ledger may be read by the children who inherit it. The return stays promised."
)


def make_store(tmp_path: Path, *, series: bool = True) -> CanvasStore:
    store = CanvasStore(tmp_path, "book-canvas")
    store.create()
    store.apply(
        "create-item", expected_revision=0, command_id="vision-created",
        payload={"item": {"id": "story-vision", "kind": "note", "title": "Story Vision",
                          "content": "A shared water commons; wonder, belonging and a long return."},
                 "position": {"x": 20, "y": 50}},
    )
    store.apply(
        "create-item", expected_revision=store.load().revision, command_id="book-two-source",
        payload={"item": {"id": "book-2-source", "kind": "note", "title": "Book 2 source",
                          "group": "book-2", "content": BOOK_SOURCE},
                 "position": {"x": 20, "y": 200}},
    )
    if series:
        develop_series(store)
    return store


def respond(status: dict, data: dict) -> dict:
    request = HostAgentRequest(**status["request"])
    return build_host_agent_response(request, json.dumps(data), runtime="test", model="UNAVAILABLE").model_dump()


def develop_series(store: CanvasStore, candidate: dict | None = None) -> dict:
    status = prepare_architecture(store)
    return complete_architecture(store, respond(status, candidate or series_candidate()))


def revise_series(store: CanvasStore, candidate: dict) -> dict:
    """Change the working Series architecture through its real revision lifecycle: review, then apply."""
    status = prepare_architecture(store, "Revise the Series architecture for the Book tests.")
    finished = complete_architecture(store, respond(status, candidate))
    return apply_architecture_review(store, finished["review"]["request_sha256"])


def book_artifact(book: int = 2) -> dict:
    return {
        "schema_version": 1,
        "book_number": book,
        "title": "The Gate Question",
        "function": {
            "id": "fn-question", "provenance": "derived",
            "text": "Book two asks whether the ledger belongs to the inheritors.",
            "question": "May the next generation read the ledger?",
            "pressure": "The return is promised but the reading rights are unsettled.",
            "refs": [{"kind": "series_node", "id": "str_long_return"},
                     {"kind": "source_item", "id": "book-2-source"}],
        },
        "inherited": [{
            "id": "inh-ledger", "provenance": "derived",
            "text": "The ledger keeps every withdrawal open to dispute.",
            "refs": [{"kind": "series_node", "id": "eng_ledger"}],
        }],
        "engines": [{
            "id": "eng-trust", "provenance": "agent_proposed",
            "text": "Reading rights convert trust into an argument.",
            "condition": "A child asks to read a disputed entry.",
            "consequence": "The council must answer in public.",
            "changed_state": "The gate table loses its monopoly on access.",
            "refs": [{"kind": "series_node", "id": "inst_gate"}],
        }],
        "agents": [{
            "id": "agent-council", "provenance": "derived",
            "text": "The gate council wants the ledger closed to protect its allotments.",
            "refs": [{"kind": "series_node", "id": "inst_gate"}],
        }],
        "choice": {
            "id": "choice-reading", "provenance": "agent_proposed",
            "text": "The council chooses how far reading rights extend.",
            "options": [
                {"id": "opt-open", "provenance": "agent_proposed", "text": "Open the ledger to heirs."},
                {"id": "opt-closed", "provenance": "agent_proposed", "text": "Keep the ledger with the council."},
            ],
            "chosen_option_id": "opt-open",
            "costs_kept_visible": [{"id": "cost-allotments", "provenance": "derived",
                                    "text": "Allotments shrink for two seasons."}],
            "transformation": {"id": "trans-access", "provenance": "agent_proposed",
                               "text": "Access becomes a public act rather than a privilege."},
        },
        "local_resolution": [{"id": "res-heirs", "provenance": "agent_proposed", "closure": True,
                              "text": "Heirs read the first open entry in public."}],
        "series_consequences": [{
            "id": "cons-return", "provenance": "derived", "kind": "changes",
            "text": "The long return now depends on who can read the ledger.",
            "refs": [{"kind": "series_node", "id": "str_long_return"}],
        }],
        "later_possibilities": [{"id": "later-audit", "provenance": "agent_proposed",
                                 "kind": "enabled", "text": "A later Book may audit the ledger."}],
        "assumptions": [{"id": "assume-access", "provenance": "agent_proposed",
                         "text": "Heirs will use reading rights responsibly.",
                         "reversal": "Reverse if public reading produces hoarding within one season."}],
        "alternatives": [{"id": "alt-closed", "provenance": "hypothetical", "title": "Closed ledger",
                          "status": "hypothetical", "text": "The ledger stays with the council.",
                          "rationale": "Keeps allotments stable but leaves the return unexamined."}],
        "unresolved": [{"id": "unk-scale", "provenance": "unresolved",
                        "text": "The source does not say how many heirs exist."}],
        "open_author_decisions": [{"id": "dec-reading", "provenance": "unresolved",
                                   "text": "The author decides who counts as an heir.",
                                   "series_question_index": 0,
                                   "series_question_sha256": _sha(QUESTIONS[0])}],
        "typed_edges": [{"id": "edge-return", "source": "cons-return",
                         "target": {"kind": "series_node", "id": "str_long_return"},
                         "dependency": "pressures",
                         "function": "Reading rights pressure the promised return."}],
    }


def develop_book(store: CanvasStore, artifact: dict | None = None) -> dict:
    status = book_prepare(store, 2)
    request = HostAgentRequest(**status["request"])
    response = build_host_agent_response(
        request, json.dumps(artifact or book_artifact()), runtime="test", model="UNAVAILABLE",
    ).model_dump()
    return book_complete(store, 2, response)


def snapshot(store: CanvasStore) -> dict[str, str]:
    """Digest every canvas file outside the Book architecture records."""
    result = {}
    for path in sorted(store.directory.rglob("*")):
        relative = path.relative_to(store.directory)
        if path.is_file() and "books" not in relative.parts:
            result[str(relative)] = hashlib.sha256(path.read_bytes()).hexdigest()
    return result


# --- schema and authority ----------------------------------------------------------------

def test_reduced_artifact_validates():
    artifact = WorkingBookArchitecture.model_validate_json(json.dumps(book_artifact()))
    assert artifact.book_number == 2
    assert artifact.choice.chosen_option_id == "opt-open"


@pytest.mark.parametrize("mutate", [
    lambda a: a["inherited"][0].update(provenance="author_fixed"),
    lambda a: a["inherited"][0].update(provenance="accepted"),
    lambda a: a["inherited"][0].update(provenance="unlabelled"),
    lambda a: a["inherited"][0].update(provenance="author_declared"),
    lambda a: a["assumptions"][0].update(reversal=None),
    lambda a: a["agents"][0].update(name="Idrun Sallow"),
    lambda a: a["alternatives"][0].update(provenance="derived"),
    lambda a: a["function"].update(refs=[{"kind": "source_item", "id": "book-2-source"}]),
    lambda a: a["choice"].update(chosen_option_id="opt-missing"),
    lambda a: a["typed_edges"][0].update(dependency="causes"),
])
def test_schema_rejects_agent_authority_and_unsupported_claims(mutate):
    artifact = copy.deepcopy(book_artifact())
    mutate(artifact)
    with pytest.raises(ValidationError):
        WorkingBookArchitecture.model_validate_json(json.dumps(artifact))


def test_named_agent_with_visible_source_is_admitted():
    artifact = copy.deepcopy(book_artifact())
    artifact["agents"][0].update(name="Gate Keeper", name_source={"kind": "source_item", "id": "story-vision"})
    WorkingBookArchitecture.model_validate_json(json.dumps(artifact))


def test_develop_persists_validated_book_and_no_accepted_or_series_state_changes(tmp_path, monkeypatch):
    store = make_store(tmp_path)
    before = snapshot(store)

    def refuse(*_args, **_kwargs):
        raise AssertionError("no Book command may reach an accept path")

    monkeypatch.setattr(ArtifactStore, "accept", refuse)
    monkeypatch.setattr(SeriesVerticalSliceService, "accept_book_direction", refuse)
    finished = develop_book(store)
    assert finished["status"] == "ready"
    assert finished["artifact"]["title"] == "The Gate Question"
    assert snapshot(store) == before
    assert not (tmp_path / "story_identity.yaml").exists()


# --- lifecycle --------------------------------------------------------------------------

def test_fresh_process_resume_recovers_the_book_and_its_identity(tmp_path):
    store = make_store(tmp_path)
    finished = develop_book(store)
    env = dict(os.environ, PYTHONPATH=str(SRC), PYTHONUTF8="1")
    completed = subprocess.run(
        [sys.executable, "-m", "auteur.series.working_book_architecture",
         "--project", str(tmp_path), "--canvas", "book-canvas", "book-resume", "--book", "2"],
        capture_output=True, text=True, env=env, timeout=120,
    )
    assert completed.returncode == 0, completed.stderr
    recovered = json.loads(completed.stdout)
    assert recovered["freshness"] == "ready"
    assert recovered["semantic_impact"] == "clear"
    assert recovered["artifact"] == finished["artifact"]
    packet = recovered["packet"]
    assert packet["identity"]["question"] == "May the next generation read the ledger?"
    assert packet["revision_identity"]["content_sha256"] == wba._digest(finished["artifact"])
    assert [c["id"] for c in packet["series_constraints"]] == ["eng_ledger", "inst_gate", "str_long_return"]
    assert all(c["status"] == "present" for c in packet["series_constraints"])
    assert packet["open_author_decisions"][0]["reference_stale"] is False


def test_identical_response_is_idempotent_and_a_different_one_is_refused(tmp_path):
    store = make_store(tmp_path)
    request = HostAgentRequest(**book_prepare(store, 2)["request"])

    def reply(artifact: dict) -> dict:
        return build_host_agent_response(
            request, json.dumps(artifact), runtime="test", model="UNAVAILABLE",
            completed_at="2026-11-12T00:00:00+00:00",
        ).model_dump()

    first = book_complete(store, 2, reply(book_artifact()))
    again = book_complete(store, 2, reply(book_artifact()))
    assert again == first
    different = copy.deepcopy(book_artifact())
    different["function"]["question"] = "A different question."
    with pytest.raises(BeginnerConcurrencyError):
        book_complete(store, 2, reply(different))


def test_series_change_after_prepare_refuses_completion_and_retains_evidence(tmp_path):
    store = make_store(tmp_path)
    status = book_prepare(store, 2)
    changed = series_candidate()
    changed["summary"] = "A different Series summary written after the Book request."
    revise_series(store, changed)
    request = HostAgentRequest(**status["request"])
    response = build_host_agent_response(request, json.dumps(book_artifact()), runtime="test", model="UNAVAILABLE").model_dump()
    with pytest.raises(BeginnerConcurrencyError, match="response retained as stale evidence"):
        book_complete(store, 2, response)
    stale = store.directory / "architecture" / "books" / "2" / "requests" / request.request_sha256 / "stale_response.json"
    assert stale.exists()
    assert book_project(store, 2)["artifact"] is None


def test_source_change_after_prepare_refuses_completion(tmp_path):
    store = make_store(tmp_path)
    status = book_prepare(store, 2)
    store.apply(
        "create-item", expected_revision=store.load().revision, command_id="book-two-addendum",
        payload={"item": {"id": "book-2-addendum", "kind": "note", "title": "Addendum",
                          "group": "book-2", "content": "A later note the Book never saw."},
                 "position": {"x": 20, "y": 400}},
    )
    request = HostAgentRequest(**status["request"])
    response = build_host_agent_response(request, json.dumps(book_artifact()), runtime="test", model="UNAVAILABLE").model_dump()
    with pytest.raises(BeginnerConcurrencyError, match="changed after this request"):
        book_complete(store, 2, response)


def test_unresolved_series_reference_is_refused_and_not_persisted(tmp_path):
    store = make_store(tmp_path)
    status = book_prepare(store, 2)
    artifact = copy.deepcopy(book_artifact())
    artifact["inherited"][0]["refs"] = [{"kind": "series_node", "id": "eng_missing"}]
    request = HostAgentRequest(**status["request"])
    response = build_host_agent_response(request, json.dumps(artifact), runtime="test", model="UNAVAILABLE").model_dump()
    with pytest.raises(ValueError, match="eng_missing"):
        book_complete(store, 2, response)
    assert book_project(store, 2)["status"] == "awaiting_host_agent"


def test_wrong_open_question_hash_is_refused(tmp_path):
    store = make_store(tmp_path)
    status = book_prepare(store, 2)
    artifact = copy.deepcopy(book_artifact())
    artifact["open_author_decisions"][0]["series_question_sha256"] = _sha("A reworded question?")
    request = HostAgentRequest(**status["request"])
    response = build_host_agent_response(request, json.dumps(artifact), runtime="test", model="UNAVAILABLE").model_dump()
    with pytest.raises(ValueError, match="text changed"):
        book_complete(store, 2, response)


def test_develop_requires_a_current_series_architecture(tmp_path):
    store = make_store(tmp_path, series=False)
    with pytest.raises(BeginnerConcurrencyError, match="Series working architecture"):
        book_prepare(store, 2)


def test_develop_refuses_to_replace_an_existing_book(tmp_path):
    store = make_store(tmp_path)
    develop_book(store)
    with pytest.raises(ValueError, match="already has a working architecture"):
        book_prepare(store, 2)


def test_resume_reports_series_change_as_stale_with_semantic_impact(tmp_path):
    store = make_store(tmp_path)
    develop_book(store)
    changed = series_candidate()
    changed["nodes"][2]["summary"] = "The return is now explicitly deferred."
    revise_series(store, changed)
    recovered = book_resume(store, 2)
    assert recovered["freshness"] == "stale"
    assert recovered["series_changed"] is True
    assert recovered["semantic_impact"] == "suspect"


def test_resume_reports_removed_referenced_node_as_contradictory(tmp_path):
    store = make_store(tmp_path)
    develop_book(store)
    changed = series_candidate()
    changed["nodes"] = [node for node in changed["nodes"] if node["id"] != "str_long_return"]
    changed["links"] = []
    revise_series(store, changed)
    assert book_resume(store, 2)["semantic_impact"] == "contradictory"


def test_packet_constraints_hold_only_series_ids_within_budget(tmp_path):
    store = make_store(tmp_path)
    develop_book(store)
    packet = book_resume(store, 2)["packet"]
    constraint_ids = {c["id"] for c in packet["series_constraints"]}
    assert constraint_ids <= {node["id"] for node in series_candidate()["nodes"]}
    assert len(json.dumps(packet, ensure_ascii=False)) < 6000


def test_cli_develop_and_refusals_use_exit_codes_and_structured_output(tmp_path, capsys):
    store = make_store(tmp_path)
    base = ["--project", str(tmp_path), "--canvas", "book-canvas"]
    assert wba.main([*base, "book-complete-file", "--book", "2", "--candidate", str(tmp_path / "none.json")]) == 1
    assert json.loads(capsys.readouterr().out)["result"] == "rejected"
    assert wba.main([*base, "book-prepare", "--book", "2"]) == 0
    capsys.readouterr()
    candidate = tmp_path / "book-2.json"
    candidate.write_text(json.dumps(book_artifact()), encoding="utf-8")
    assert wba.main([*base, "book-complete-file", "--book", "2", "--candidate", str(candidate)]) == 0
    assert json.loads(capsys.readouterr().out)["status"] == "ready"
    assert wba.main([*base, "book-prepare", "--book", "2"]) == 1
    assert "already has a working architecture" in json.loads(capsys.readouterr().out)["error"]
    assert store.load().items  # the canvas survives the CLI operations
