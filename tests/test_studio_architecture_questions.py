"""Persistent identity for open Architecture questions: the pure rules, without any store.

These pin the consequential cases from the question-continuity responsibility: identity survives reordering and
rewording, new and replaced questions get new identities, removal is never presented as an answer, identities are
never recycled, identical wording under different identities is not merged, and unreadable history is not guessed at.
"""
import pytest

from auteur.beginner.studio_architecture_questions import (
    identity_problems, question_changes, question_history, relate_to_current, text_digest,
)

GATE = "Does the stewardship tally count care or debt?"
ROUTE = "Which hand is left out of the count first?"
TERRACE = "Does the Terrace Council keep the tally?"


def candidate(questions, ids=None):
    body = {"schema_version": 2, "open_questions": list(questions)}
    if ids is not None:
        body["open_question_ids"] = list(ids)
    return body


def test_a_legacy_candidate_without_identities_is_readable_and_has_no_problems_to_report():
    legacy = candidate([GATE, ROUTE])
    assert identity_problems(legacy, None, []) == []
    changes = question_changes(None, legacy)
    assert changes["identity_introduced"] is False
    assert [row["status"] for row in changes["questions"]] == ["no_identity", "no_identity"]


def test_identities_are_introduced_at_a_version_without_claiming_history_for_them():
    prior = candidate([GATE, ROUTE])
    proposed = candidate([GATE, ROUTE], ["q-gate", "q-route"])
    assert identity_problems(proposed, prior, [prior]) == []
    changes = question_changes(prior, proposed)
    assert changes["identity_introduced"] is True
    assert [row["status"] for row in changes["questions"]] == ["introduced", "introduced"]


def test_reordering_keeps_the_identity_and_is_reported_as_moved():
    prior = candidate([GATE, ROUTE], ["q-gate", "q-route"])
    proposed = candidate([ROUTE, GATE], ["q-route", "q-gate"])
    assert identity_problems(proposed, prior, [prior]) == []
    statuses = {row["id"]: row["status"] for row in question_changes(prior, proposed)["questions"]}
    assert statuses == {"q-route": "moved", "q-gate": "moved"}


def test_rewording_keeps_the_identity_and_keeps_the_earlier_wording_for_review():
    reworded = "Does the stewardship tally count care, or only debt that the Council owes?"
    prior = candidate([GATE], ["q-gate"])
    proposed = candidate([reworded], ["q-gate"])
    assert identity_problems(proposed, prior, [prior]) == []
    row = question_changes(prior, proposed)["questions"][0]
    assert row["id"] == "q-gate" and row["status"] == "reworded"
    assert row["previous_text"] == GATE and row["text"] == reworded


def test_a_new_question_gets_a_new_identity_and_a_removed_one_is_recorded_as_removed_not_answered():
    prior = candidate([GATE, ROUTE], ["q-gate", "q-route"])
    proposed = candidate([GATE, TERRACE], ["q-gate", "q-terrace"])
    assert identity_problems(proposed, prior, [prior]) == []
    changes = question_changes(prior, proposed)
    assert [row["status"] for row in changes["questions"]] == ["unchanged", "introduced"]
    assert changes["removed"] == [{"id": "q-route", "previous_index": 1, "previous_text": ROUTE}]


def test_a_retired_identity_cannot_name_a_different_question():
    v1 = candidate([GATE], ["q-gate"])
    v2 = candidate([], [])
    v3 = candidate([TERRACE], ["q-gate"])
    problems = identity_problems(v3, v2, [v2, v1])
    assert any("already used by an earlier version" in problem and "q-gate" in problem for problem in problems)


def test_dropping_identities_after_they_were_introduced_is_rejected():
    prior = candidate([GATE], ["q-gate"])
    proposed = candidate([GATE])
    problems = identity_problems(proposed, prior, [prior])
    assert problems and "keep open_question_ids" in problems[0]


def test_duplicate_identities_and_mismatched_lengths_are_rejected():
    prior = candidate([GATE, ROUTE], ["q-gate", "q-route"])
    dup = candidate([GATE, ROUTE], ["q-gate", "q-gate"])
    short = candidate([GATE, ROUTE], ["q-gate"])
    assert any("used more than once" in problem for problem in identity_problems(dup, prior, [prior]))
    assert any("one id for each" in problem for problem in identity_problems(short, prior, [prior]))


def test_an_invalid_identity_is_rejected():
    proposed = candidate([GATE], ["gate"])
    assert any("not a valid open question id" in problem for problem in identity_problems(proposed, None, []))


def test_identical_wording_under_two_identities_is_allowed_and_not_merged():
    proposed = candidate([GATE, GATE], ["q-gate-a", "q-gate-b"])
    assert identity_problems(proposed, None, []) == []
    history = question_history([("s2", proposed)])
    assert set(history) == {"q-gate-a", "q-gate-b"}


def test_an_unreadable_earlier_version_blocks_introducing_identities_it_cannot_rule_out():
    proposed = candidate([GATE], ["q-gate"])
    problems = identity_problems(proposed, None, [None])
    assert problems and "cannot be read" in problems[0]


def test_question_history_is_ordered_oldest_first_and_skips_unreadable_versions():
    v1 = candidate([GATE], ["q-gate"])
    v2 = candidate([ROUTE, GATE], ["q-route", "q-gate"])
    versions = [("sha-2", v2), ("sha-x", None), ("sha-1", v1)]
    history = question_history(versions)
    assert [entry["request_sha256"] for entry in history["q-gate"]] == ["sha-1", "sha-2"]
    assert [entry["index"] for entry in history["q-gate"]] == [0, 1]
    assert history["q-gate"][0]["text_sha256"] == text_digest(GATE)


def test_a_recorded_version_relates_to_the_current_architecture_without_inference_from_wording():
    recorded = {"index": 0, "text": GATE}
    current = candidate([ROUTE, "Does the stewardship tally count care, or only debt?"], ["q-route", "q-gate"])
    assert relate_to_current("q-gate", recorded, current)["status"] == "moved_and_reworded"
    assert relate_to_current("q-gate", recorded, candidate([GATE], ["q-gate"]))["status"] == "current_wording"
    assert relate_to_current("q-gate", recorded, candidate([TERRACE], ["q-terrace"]))["status"] == "removed"
    assert relate_to_current(None, recorded, current)["status"] == "identity_not_established"
    # Identical wording held by a different identity is a different question.
    assert relate_to_current("q-route", recorded, candidate([GATE], ["q-other"]))["status"] == "removed"
