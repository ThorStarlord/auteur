"""R01/R02: inherited claims must not acquire authority from an agent proposal.

Source existence is not source authority. A Book may inherit from the working
Series architecture, but a claim grounded only in agent-proposed Series nodes is
not an author-established commitment and must not be asserted as one.
"""
from __future__ import annotations

import copy
import json

import pytest

import test_series_working_book_architecture as harness

from auteur.series.working_book_architecture import (
    book_complete, book_prepare, book_resume,
)


def _artifact_with_inherited(**overrides):
    artifact = copy.deepcopy(harness.book_artifact())
    item = {
        "id": "inh-double-ledger",
        "attribution": "derived",
        "epistemic_status": "asserted",
        "text": (
            "An unofficial obligation ledger runs alongside the public record, "
            "partial and inadmissible."
        ),
        "refs": [{"kind": "series_node", "id": "eng_ledger"}],
    }
    item.update(overrides)
    artifact["inherited"].append(item)
    return artifact


def _complete(store, artifact):
    status = book_prepare(store, 2)
    return book_complete(store, 2, harness.respond(status, artifact))


def test_claim_backed_only_by_agent_series_nodes_cannot_be_asserted(tmp_path):
    store = harness.make_store(tmp_path)
    with pytest.raises(ValueError) as error:
        _complete(store, _artifact_with_inherited())
    assert "inherited" in str(error.value).lower()
    assert "inh-double-ledger" in str(error.value)


def test_the_same_claim_is_admitted_when_marked_conditional(tmp_path):
    store = harness.make_store(tmp_path)
    _complete(store, _artifact_with_inherited(attribution="agent_proposed"))
    resume = book_resume(store, 2)
    basis = resume["inherited_provenance"]["items"]
    row = next(item for item in basis if item["id"] == "inh-double-ledger")
    assert row["source_basis"] == "working_series_proposal"
    assert row["author_grounded"] is False


def test_a_claim_backed_by_author_source_may_be_asserted(tmp_path):
    store = harness.make_store(tmp_path)
    artifact = _artifact_with_inherited(
        id="inh-victory-anchor",
        refs=[
            {"kind": "source_item", "id": "book-2-source"},
            {"kind": "series_node", "id": "eng_ledger"},
        ],
    )
    _complete(store, artifact)
    basis = book_resume(store, 2)["inherited_provenance"]["items"]
    row = next(item for item in basis if item["id"] == "inh-victory-anchor")
    assert row["source_basis"] == "author_source"
    assert row["author_grounded"] is True


def test_legacy_provenance_form_is_not_newly_rejected(tmp_path):
    """Historical artifacts keep their original meaning; the rule applies to the explicit form."""
    store = harness.make_store(tmp_path)
    artifact = copy.deepcopy(harness.book_artifact())
    artifact["inherited"].append({
        "id": "inh-legacy",
        "provenance": "derived",
        "text": "Legacy inherited claim kept for compatibility.",
        "refs": [{"kind": "series_node", "id": "eng_ledger"}],
    })
    _complete(store, artifact)
    basis = book_resume(store, 2)["inherited_provenance"]["items"]
    row = next(item for item in basis if item["id"] == "inh-legacy")
    assert row["source_basis"] == "working_series_proposal"
    assert row["legacy_form"] is True


def test_accepted_identity_is_untouched_by_the_new_rule(tmp_path):
    store = harness.make_store(tmp_path)
    _complete(store, _artifact_with_inherited(attribution="agent_proposed"))
    assert not (store.project_root / "story_identity.yaml").exists()
