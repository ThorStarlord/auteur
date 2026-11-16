"""R06: verify the original findings against the repaired implementation.

Each test either confirms the original failure is prevented, or records a precise
limitation that remains. A limitation is recorded as a test rather than a
paragraph so it cannot be quietly forgotten.
"""
from __future__ import annotations

import copy
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

import test_series_working_book_architecture as harness

from auteur.beginner.studio_architecture import (
    ArchitectureCandidate, complete_architecture, prepare_architecture,
)
from auteur.series.working_book_architecture import (
    WorkingBookArchitecture, book_complete, book_prepare, book_resume,
)

SRC = Path(__file__).resolve().parents[1] / "src"


def _complete(store, artifact):
    status = book_prepare(store, 2)
    return book_complete(store, 2, harness.respond(status, artifact))


def test_the_original_failure_is_prevented(tmp_path):
    store = harness.make_store(tmp_path)
    artifact = copy.deepcopy(harness.book_artifact())
    artifact["inherited"].append({
        "id": "inh-double-ledger",
        "attribution": "derived",
        "epistemic_status": "asserted",
        "text": "An unofficial obligation ledger runs alongside the public record.",
        "refs": [{"kind": "series_node", "id": "eng_ledger"}],
    })
    with pytest.raises(ValueError) as error:
        _complete(store, artifact)
    assert "inh-double-ledger" in str(error.value)


def test_agent_proposed_creative_material_remains_available(tmp_path):
    store = harness.make_store(tmp_path)
    artifact = copy.deepcopy(harness.book_artifact())
    artifact["inherited"].append({
        "id": "inh-invention",
        "attribution": "agent_proposed",
        "epistemic_status": "asserted",
        "text": "An unofficial obligation ledger runs alongside the public record.",
        "refs": [{"kind": "series_node", "id": "eng_ledger"}],
    })
    _complete(store, artifact)
    items = {
        item["id"]: item
        for item in book_resume(store, 2)["inherited_provenance"]["items"]
    }
    assert items["inh-invention"]["author_grounded"] is False
    assert items["inh-invention"]["source_basis"] == "working_series_proposal"


def test_known_limitation_a_cited_but_unrelated_author_source_still_passes(tmp_path):
    """Residual limitation: reference validity is not semantic support.

    A claim may cite a real author source item that does not actually support it.
    The validator cannot establish entailment, so the claim is admitted as derived.
    Recorded here rather than presented as solved.
    """
    store = harness.make_store(tmp_path)
    artifact = copy.deepcopy(harness.book_artifact())
    artifact["inherited"].append({
        "id": "inh-unsupported",
        "attribution": "derived",
        "epistemic_status": "asserted",
        "text": "The archive was founded by a hereditary council of nine.",
        "refs": [
            {"kind": "source_item", "id": "book-2-source"},
            {"kind": "series_node", "id": "eng_ledger"},
        ],
    })
    _complete(store, artifact)
    items = {
        item["id"]: item
        for item in book_resume(store, 2)["inherited_provenance"]["items"]
    }
    # Author-grounded by reference, even though the source does not entail the claim.
    assert items["inh-unsupported"]["source_basis"] == "author_source"


def test_a_genuinely_fresh_process_recovers_objective_and_premise_status(tmp_path):
    store = harness.make_store(tmp_path, series=False)
    status = prepare_architecture(store)
    complete_architecture(store, harness.respond(status, harness.series_candidate()))

    script = (
        "import json, sys\n"
        "from auteur.beginner.studio_architecture import project_architecture_resume\n"
        "from auteur.beginner.studio_store import CanvasStore\n"
        "r = project_architecture_resume(CanvasStore(sys.argv[1], sys.argv[2]))\n"
        "print(json.dumps({'objective': r.get('governing_objective'),"
        " 'premise': r.get('premise_status'),"
        " 'status': r.get('architecture_status')}))\n"
    )
    env = dict(os.environ)
    env["PYTHONPATH"] = str(SRC)
    completed = subprocess.run(
        [sys.executable, "-c", script, str(tmp_path), "book-canvas"],
        capture_output=True, text=True, env=env, timeout=180,
    )
    assert completed.returncode == 0, completed.stderr
    payload = json.loads(completed.stdout.strip().splitlines()[-1])
    assert payload["objective"]["authority"] == "author_expressed"
    assert payload["premise"]["authority"] == "working_architecture_not_canon"
    assert payload["status"] == "ready"


def test_the_contract_represents_the_historical_rejections():
    schema = ArchitectureCandidate.model_json_schema()
    assert schema["additionalProperties"] is False  # invented fields
    # The historical mistake used GenreParticipation's vocabulary on GenreContract.
    contract_role = schema["$defs"]["GenreContract"]["properties"]["role"]["enum"]
    assert contract_role == ["governing", "supporting", "tertiary", "local"]
    participation_role = schema["$defs"]["GenreParticipation"]["properties"]["role"]["enum"]
    assert "locally_dominant" in participation_role
    book = WorkingBookArchitecture.model_json_schema()
    assert book["properties"]["series_consequences"]["maxItems"] == 16
    assert book["properties"]["later_possibilities"]["maxItems"] == 16


def test_the_validator_still_rejects_an_historical_shape(tmp_path):
    store = harness.make_store(tmp_path, series=False)
    status = prepare_architecture(store)
    candidate = harness.series_candidate()
    candidate["genre_contracts"] = [{
        "genre_node_id": "n-wonder", "role": "locally_dominant",
        "narrative_engine": "x", "payoff_expectations": ["y"],
    }]
    with pytest.raises(Exception):
        complete_architecture(store, harness.respond(status, candidate))
