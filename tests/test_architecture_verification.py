"""Claim-basis verification and owner-derived changes, on the Spring Ledger study.

A verification judges one claim of a completed synthesis against the exact evidence that synthesis was given. It is read-only for every
record, it binds to the synthesis request and result, and it is stale once that evidence has changed. Its judgement can enter a follow-up
synthesis as one criticism, with its identity. The changes between two syntheses are derived from their stored answers.
"""
import json
import sys
from pathlib import Path

import pytest

from auteur.beginner import studio_architecture as arch
from auteur.beginner.persistence import BeginnerConcurrencyError
from auteur.beginner.studio_architecture_consequence import _digest
from auteur.beginner.studio_architecture_synthesis import (
    complete_architecture_synthesis, derived_changes, prepare_architecture_synthesis, project_architecture_synthesis,
)
from auteur.beginner.studio_architecture_verification import (
    ROOM_CHARS, ClaimVerification, _SYSTEM_VERIFY,
    claims_of, complete_claim_verification, dependents_of, prepare_claim_verification, project_claim_verifications,
)

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tests"))
import test_architecture_consequence as consequence  # noqa: E402
from test_architecture_synthesis import (  # noqa: E402
    complete, prepared, question_selection, replay, text_of, valid_answer,
)

# The consequence suite's fixtures, re-bound here so pytest registers them for this module.
edit_vision = consequence.edit_vision
pristine = consequence.pristine
project = consequence.project
snapshot = consequence.snapshot
store_for = consequence.store_for


def records_without_judgements(project: Path) -> dict[str, bytes]:
    """The narrative and Architecture records. Synthesis and verification requests are judgements, not records."""
    return {path: data for path, data in snapshot(project).items() if "synthesis" not in Path(path).parts}


def completed_synthesis(store, **overrides):
    """A synthesis of the compact question whose valid answer is stored; returns the synthesis request sha and its user payload."""
    result = prepared(store, **overrides)
    user = json.loads(result["request"]["user"])
    complete(store, result["request"], valid_answer(user))
    return result["request"]["request_sha256"], user


def verdict(user: dict, claim: str = "s1", **overrides) -> dict:
    """A well-formed judgement: the first development's own wording carries the premise, and the verifier says so."""
    cited = user["developments"][0]["evidence"]
    base = {
        "schema_version": 2, "claim": claim, "evidence_register": "established", "judgment": "supported",
        "affects": "asserted_condition", "reasoning": "The cited development states the condition in its own words.",
        "evidence": [cited], "quote": text_of(user, cited)[:40], "alternative_reading": None, "would_settle": None,
        "creative_room": "The household may still refuse the duty; the refusal would be a proposal, not a record.",
    }
    base.update(overrides)
    return base


def verify(store, synthesis_sha, claim="s1", answer=None, **overrides):
    prepared_verification = prepare_claim_verification(store, synthesis_request_sha256=synthesis_sha, claim=claim)
    request = prepared_verification["request"]
    payload = answer if answer is not None else verdict(json.loads(request["user"]), claim, **overrides)
    return request, complete_claim_verification(store, replay_verification(request, payload))


def replay_verification(request: dict, payload: dict) -> dict:
    from auteur.host_agent import HostAgentRequest, build_host_agent_response
    return build_host_agent_response(HostAgentRequest(**request), json.dumps(payload), runtime="verification-test").model_dump()


# --- The claims and the load-bearing rule ------------------------------------------------------------------------------------------

def test_every_checkable_claim_is_named_by_reference_and_its_uses_are_the_records_own(project):
    store = store_for(project)
    _sha, user = completed_synthesis(store)
    answer = valid_answer(user)
    answer["relations"] = [{"kind": "enables", "between": ["s1", "s2"], "dependence": "causal", "reason": "The duty must be carried first.",
                            "evidence": [user["developments"][0]["evidence"]], "quote": text_of(user, user["developments"][0]["evidence"])[:40]}]
    answer["opportunities"] = [{"text": "A later household could carry the duty.", "between": ["d1", "s2"],
                                "evidence": [user["developments"][0]["evidence"]], "quote": text_of(user, user["developments"][0]["evidence"])[:40]}]
    claims = claims_of(answer)
    assert set(claims) == {"s1", "s2", "r1", "a1", "o1"}, "every stage, relation, alternative path and opportunity has a reference"
    uses = dependents_of(answer, claims)
    assert uses["s1"]["load_bearing"] is True, "an enabling relation makes its premise load-bearing"
    assert uses["s2"]["load_bearing"] is True
    assert uses["s1"]["used_by"] == ["r1"]


def test_an_unrelated_stage_is_not_load_bearing_and_nothing_is_scored(project):
    store = store_for(project)
    _sha, user = completed_synthesis(store)
    claims = claims_of(valid_answer(user))
    uses = dependents_of(valid_answer(user), claims)
    assert uses["s1"] == {"used_by": [], "load_bearing": False}


# --- Preparation, binding and the packet ---------------------------------------------------------------------------------------------

def test_a_verification_is_bound_to_the_synthesis_and_carries_the_exact_evidence_it_read(project):
    store = store_for(project)
    synthesis_sha, user = completed_synthesis(store)
    result = prepare_claim_verification(store, synthesis_request_sha256=synthesis_sha, claim="s1")
    request = result["request"]
    packet = json.loads(request["user"])
    assert request["settings"]["operation"] == "verify_synthesis_claim"
    assert request["settings"]["synthesis_request_sha256"] == synthesis_sha
    assert request["settings"]["claim"] == "s1"
    assert packet["allowed_evidence"] == [item["id"] for item in user["evidence"]], "the verifier sees everything the synthesis saw"
    assert packet["evidence"] == user["evidence"], "the exact text the synthesis read, not a fresh reading"
    assert "answer" not in packet and "reasoning" not in json.dumps(packet.get("claim", {})), "the verifier does not see the synthesis's reasoning"
    assert result["verification"]["standing"] == "current" and result["verification"]["status"] == "awaiting_host_agent"


def test_the_same_claim_prepared_twice_is_the_same_request(project):
    store = store_for(project)
    synthesis_sha, _user = completed_synthesis(store)
    first = prepare_claim_verification(store, synthesis_request_sha256=synthesis_sha, claim="s1")["request"]["request_sha256"]
    second = prepare_claim_verification(store, synthesis_request_sha256=synthesis_sha, claim="s1")["request"]["request_sha256"]
    assert first == second


def test_a_claim_the_synthesis_does_not_hold_is_refused_by_name(project):
    store = store_for(project)
    synthesis_sha, _user = completed_synthesis(store)
    with pytest.raises(ValueError, match="no claim 'r3'"):
        prepare_claim_verification(store, synthesis_request_sha256=synthesis_sha, claim="r3")


def test_a_synthesis_that_is_not_completed_cannot_be_verified(project):
    store = store_for(project)
    result = prepared(store)
    with pytest.raises(ValueError, match="not completed"):
        prepare_claim_verification(store, synthesis_request_sha256=result["request"]["request_sha256"], claim="s1")


# --- Completion, refusals and the record ----------------------------------------------------------------------------------------------

def test_a_judgement_is_stored_beside_its_request_and_no_record_changes(project):
    store = store_for(project)
    synthesis_sha, user = completed_synthesis(store)
    before = records_without_judgements(project)
    request, row = verify(store, synthesis_sha, "s1")
    assert row["status"] == "ready" and row["result"]["judgment"] == "supported"
    folder = arch._root(store) / "synthesis" / "verifications" / "requests" / request["request_sha256"]
    assert (folder / "result.json").exists() and (folder / "response.json").exists()
    stored = json.loads((folder / "result.json").read_text(encoding="utf-8"))
    synthesis_result = json.loads((arch._root(store) / "synthesis" / "requests" / synthesis_sha / "result.json").read_text(encoding="utf-8"))
    assert stored["synthesis_result_sha256"] == _digest(synthesis_result["answer"]), "bound to the exact synthesis answer it judged"
    assert records_without_judgements(project) == before, "a verification changes no narrative or Architecture record"


@pytest.mark.parametrize("override, expected", [
    ({"evidence": ["E999"]}, "which is not in this request"),
    ({"quote": "words the evidence does not contain at all"}, "not in the evidence it cites"),
    ({"judgment": "overreaching", "alternative_reading": None}, "must say what the evidence does support"),
    ({"judgment": "insufficient_evidence", "evidence": [], "quote": None, "would_settle": None}, "must name what would settle it"),
    ({"judgment": "supported", "evidence_register": "agent_proposed"}, "needs evidence that establishes or infers"),
    ({"evidence": [], "quote": None, "judgment": "supported"}, "cites no evidence"),
])
def test_a_judgement_the_owner_can_check_and_does_not_meet_is_refused_and_kept(project, override, expected):
    store = store_for(project)
    synthesis_sha, user = completed_synthesis(store)
    payload = verdict(user, "s1", **override)
    request = prepare_claim_verification(store, synthesis_request_sha256=synthesis_sha, claim="s1")["request"]
    with pytest.raises(ValueError, match=expected):
        complete_claim_verification(store, replay_verification(request, payload))
    refused = arch._root(store) / "synthesis" / "verifications" / "requests" / request["request_sha256"] / "refused"
    assert list(refused.glob("*.json")), "a refused judgement is kept beside its refusal"
    assert not (arch._root(store) / "synthesis" / "verifications" / "requests" / request["request_sha256"] / "result.json").exists()


def test_a_recorded_stage_is_supported_only_by_evidence_that_establishes_it(project):
    store = store_for(project)
    synthesis_sha, user = completed_synthesis(store)
    request = prepare_claim_verification(store, synthesis_request_sha256=synthesis_sha, claim="s1")["request"]
    payload = verdict(user, "s1", evidence_register="inferred_from_established")
    with pytest.raises(ValueError, match="stated as recorded"):
        complete_claim_verification(store, replay_verification(request, payload))


def test_a_judgement_about_another_claim_than_the_one_asked_is_refused(project):
    store = store_for(project)
    synthesis_sha, user = completed_synthesis(store)
    request = prepare_claim_verification(store, synthesis_request_sha256=synthesis_sha, claim="s1")["request"]
    with pytest.raises(ValueError, match="asks about s1"):
        complete_claim_verification(store, replay_verification(request, verdict(user, "s2")))


def test_the_verifier_instruction_states_every_limit_the_owner_enforces():
    """The instruction is generated from the output contract, so every bound the owner enforces is stated, and cannot drift."""
    from auteur.host_agent import contract_limit_lines
    lines = contract_limit_lines(ClaimVerification)
    for line in lines:
        assert line in _SYSTEM_VERIFY, line
    assert "creative_room: at most " + str(ROOM_CHARS) + " characters" in _SYSTEM_VERIFY


def _stage_wording(user):
    return user["claim"]["wording"]["development"]


def test_a_clause_must_be_words_the_claim_contains(project):
    store = store_for(project)
    synthesis_sha, user = completed_synthesis(store)
    request = prepare_claim_verification(store, synthesis_request_sha256=synthesis_sha, claim="s1")["request"]
    payload = verdict(user, "s1", clauses=[{"text": "words the claim never wrote", "status": "supported", "note": "x"}])
    with pytest.raises(ValueError, match="is not words the claim contains"):
        complete_claim_verification(store, replay_verification(request, payload))


def test_a_claim_with_an_unsupported_clause_cannot_be_judged_creative_speculation(project):
    """The owner cannot judge the meaning, but it can refuse the classification that would conceal an unsupported premise."""
    store = store_for(project)
    synthesis_sha, user = completed_synthesis(store)
    request = prepare_claim_verification(store, synthesis_request_sha256=synthesis_sha, claim="s1")["request"]
    clause = _stage_wording(json.loads(request["user"])).split(".")[0][:60].strip()
    payload = verdict(user, "s1", judgment="creative_speculation", evidence_register="agent_proposed",
                      defensible_possibility="A later Book could test the claim.",
                      clauses=[{"text": clause, "status": "unsupported", "note": "The cited items do not state it."}])
    with pytest.raises(ValueError, match="cannot be judged supported, a defensible inference or creative speculation"):
        complete_claim_verification(store, replay_verification(request, payload))


def test_an_unsupported_clause_must_leave_a_defensible_possibility_stated(project):
    store = store_for(project)
    synthesis_sha, user = completed_synthesis(store)
    request = prepare_claim_verification(store, synthesis_request_sha256=synthesis_sha, claim="s1")["request"]
    clause = _stage_wording(json.loads(request["user"])).split(".")[0][:60].strip()
    payload = verdict(user, "s1", judgment="overreaching", alternative_reading="The record states less than the claim.",
                      clauses=[{"text": clause, "status": "unsupported", "note": "The cited items do not state it."}])
    with pytest.raises(ValueError, match="must say which creative possibility remains defensible"):
        complete_claim_verification(store, replay_verification(request, payload))


def test_a_clause_judgement_that_names_the_unsupported_part_and_its_possibility_is_stored(project):
    store = store_for(project)
    synthesis_sha, user = completed_synthesis(store)
    request = prepare_claim_verification(store, synthesis_request_sha256=synthesis_sha, claim="s1")["request"]
    clause = _stage_wording(json.loads(request["user"])).split(".")[0][:60].strip()
    payload = verdict(user, "s1", judgment="overreaching", alternative_reading="The record states less than the claim.",
                      defensible_possibility="The labour gap can still be met by people, as a proposal.",
                      relation_survives_correction="yes",
                      clauses=[{"text": clause, "status": "unsupported", "note": "The cited items do not state it."}])
    row = complete_claim_verification(store, replay_verification(request, payload))
    assert row["result"]["clauses"][0]["status"] == "unsupported"
    assert row["result"]["relation_survives_correction"] == "yes"


def test_an_unknown_field_is_refused_by_the_schema():
    with pytest.raises(Exception):
        ClaimVerification.model_validate({"schema_version": 1, "claim": "s1", "evidence_register": "established", "judgment": "supported",
                                          "affects": "asserted_condition", "reasoning": "x", "evidence": [], "creative_room": "y",
                                          "unexpected": True})


def test_a_judgement_must_leave_creative_room_stated(project):
    store = store_for(project)
    synthesis_sha, user = completed_synthesis(store)
    with pytest.raises(Exception):
        ClaimVerification.model_validate({**verdict(user, "s1"), "creative_room": ""})


# --- Standing ---------------------------------------------------------------------------------------------------------------------------

def test_an_edited_vision_makes_a_verification_stale_and_refuses_its_judgement(project):
    store = store_for(project)
    synthesis_sha, user = completed_synthesis(store)
    request = prepare_claim_verification(store, synthesis_request_sha256=synthesis_sha, claim="s1")["request"]
    edit_vision(store)
    row = project_claim_verifications(store, synthesis_sha)["claims"]["s1"]["latest"]
    assert row["standing"] == "stale"
    with pytest.raises(BeginnerConcurrencyError, match="has changed since this verification was prepared"):
        complete_claim_verification(store, replay_verification(request, verdict(user, "s1")))


def test_the_projection_lists_each_claims_latest_verification_for_one_synthesis(project):
    store = store_for(project)
    synthesis_sha, _user = completed_synthesis(store)
    verify(store, synthesis_sha, "s1")
    projected = project_claim_verifications(store, synthesis_sha)
    assert set(projected["claims"]) == {"s1"}
    assert projected["claims"]["s1"]["latest"]["standing"] == "current"
    assert projected["claims"]["s1"]["earlier"] == 0


# --- Follow-through: a verification enters a follow-up as one criticism -----------------------------------------------------------

def test_a_verification_carried_into_a_follow_up_is_one_criticism_with_its_identity(project):
    store = store_for(project)
    synthesis_sha, user = completed_synthesis(store)
    request, row = verify(store, synthesis_sha, "s1", judgment="supported")
    follow = prepare_architecture_synthesis(
        store, question="Weigh the verifier's judgement.", developments=[question_selection()], prior_request_sha256=synthesis_sha,
        verifications=[request["request_sha256"]])
    criticism = json.loads(follow["request"]["user"])["criticism"]
    assert len(criticism) == 1
    assert criticism[0]["verification_request_sha256"] == request["request_sha256"]
    assert "judged claim s1 of the earlier synthesis as supported" in criticism[0]["text"]
    assert "The verifier's evidence identifiers belong to the earlier synthesis" in criticism[0]["text"]
    assert "The verifier cited" not in criticism[0]["text"], "earlier identifiers are not carried into a renumbered follow-up"
    assert "not evidence" in criticism[0]["text"]


def test_a_stale_verification_cannot_be_carried_into_a_follow_up(project):
    store = store_for(project)
    synthesis_sha, _user = completed_synthesis(store)
    request, _row = verify(store, synthesis_sha, "s1")
    edit_vision(store)
    with pytest.raises(ValueError, match="has changed; it cannot be carried"):
        prepare_architecture_synthesis(store, question="Follow.", developments=[question_selection()],
                                       prior_request_sha256=synthesis_sha, verifications=[request["request_sha256"]])


def test_a_quote_must_come_from_an_item_the_judgement_cites(project):
    store = store_for(project)
    synthesis_sha, user = completed_synthesis(store)
    request = prepare_claim_verification(store, synthesis_request_sha256=synthesis_sha, claim="s1")["request"]
    payload = verdict(user, "s1", judgment="insufficient_evidence", evidence=[], would_settle="A recorded element.",
                      alternative_reading=None, quote=text_of(user, user["developments"][0]["evidence"])[:40])
    with pytest.raises(ValueError, match="must come from an item the judgement cites"):
        complete_claim_verification(store, replay_verification(request, payload))


def test_a_verification_of_another_synthesis_cannot_be_carried_into_this_follow_up(project):
    store = store_for(project)
    synthesis_sha, _user = completed_synthesis(store)
    request, _row = verify(store, synthesis_sha, "s1")
    other = prepared(store, question="A different question about the same developments.", developments=[question_selection()])
    with pytest.raises(ValueError, match="must check the synthesis that follow-up continues"):
        prepare_architecture_synthesis(store, question="Follow.", developments=[question_selection()],
                                       prior_request_sha256=other["request"]["request_sha256"], verifications=[request["request_sha256"]])


def test_a_verification_carried_without_a_prior_synthesis_is_refused(project):
    store = store_for(project)
    synthesis_sha, _user = completed_synthesis(store)
    request, _row = verify(store, synthesis_sha, "s1")
    with pytest.raises(ValueError, match="name that synthesis"):
        prepare_architecture_synthesis(store, question="Follow.", developments=[question_selection()], verifications=[request["request_sha256"]])


def test_requests_without_verifications_keep_their_identities(project):
    store = store_for(project)
    first = prepared(store)["request"]["request_sha256"]
    second = prepared(store, criticism=[])["request"]["request_sha256"]
    assert first == second
    assert "verifications" not in json.loads(prepared(store)["request"]["user"])["inputs"]


# --- Owner-derived changes ----------------------------------------------------------------------------------------------------------------

def _answer(**overrides):
    base = {
        "schema_version": 2,
        "trajectory": [
            {"book": 24, "horizon": "existing_book", "development": "The duty is first met by a named household.",
             "becomes_available": "The labour is owed to the rebuild.", "changes": "It asks who carries the duty.",
             "basis": "recorded", "evidence": ["E1"], "quote": "owed"},
            {"book": None, "horizon": "proposed_book", "development": "A later Book tests the settlement under poor harvest.",
             "becomes_available": "A household has carried the duty for a season.", "changes": "It makes the settlement a practice.",
             "basis": "proposed", "evidence": ["E1"], "quote": "owed"},
        ],
        "relations": [{"kind": "enables", "between": ["s1", "s2"], "dependence": "causal", "reason": "x", "evidence": ["E1"], "quote": "owed"}],
        "culmination": None,
        "alternative_paths": [{"ordering": "If the test comes first, the duty reads as a remedy.", "effect": "e", "viability": "viable",
                               "evidence": []}],
        "opportunities": [],
        "reader_experience": "r", "open_decisions": ["Who carries it?"], "uncertainty": [], "criticism_assessments": [],
        "changes_from_prior": [],
    }
    base.update(overrides)
    return base


def test_a_reworded_stage_is_reworded_not_judged_the_same_or_changed():
    prior = _answer()
    current = _answer()
    current["trajectory"][0]["development"] = "The duty is first met by a named household in the valley."
    changes = derived_changes(prior, current)
    kinds = [change["kind"] for change in changes["changes"]]
    assert kinds == ["stage_reworded"], "only the wording differs; nothing else is claimed to have changed"


def test_a_stage_revised_in_its_own_slot_is_revised_not_withdrawn_and_replaced():
    """A correction that keeps the stage's slot and part of its wording is one stage revised. The owner matches it by slot and does not
    decide that the judgement is the same: the change is reported as revised, not as a removal and an addition."""
    prior = _answer()
    current = _answer()
    current["trajectory"][1]["development"] = ("Proposed: outside apprentices are trained under the Special Draw Right and their repair "
                                               "is shown, so the Right's training condition is tested. The record states the condition "
                                               "only in agent-proposed elements, and the review point's placement is not stated.")
    prior["trajectory"][1]["development"] = ("Outside apprentices are trained under the Special Draw Right and their repair is "
                                             "demonstrated, so the condition the Right carries is tested.")
    kinds = [change["kind"] for change in derived_changes(prior, current)["changes"]]
    assert "stage_revised" in kinds
    assert "stage_removed" not in kinds and "stage_added" not in kinds


def test_a_changed_basis_placement_and_relation_are_derived_and_a_dropped_stage_withdraws_its_relation():
    prior = _answer()
    current = _answer()
    current["trajectory"][0]["basis"] = "inferred"
    current["trajectory"][1] = {**current["trajectory"][1], "development": "Shadows fall across the harbour at dusk."}
    current["relations"] = []
    kinds = sorted(change["kind"] for change in derived_changes(prior, current)["changes"])
    assert "stage_basis_changed" in kinds
    assert "stage_removed" in kinds and "stage_added" in kinds
    assert "relation_removed" in kinds


def test_a_culmination_added_and_open_decisions_compared_as_exact_strings():
    prior = _answer()
    current = _answer(open_decisions=["Who carries it?", "Is the duty owed at all?"])
    current["culmination"] = {"statement": "The duty is met by the generation that refused to be counted.",
                              "necessary": [], "enrichment": [], "standalone_value": "The first Books stand without it."}
    kinds = {change["kind"] for change in derived_changes(prior, current)["changes"]}
    assert {"culmination_added", "open_decision_added"} <= kinds


def test_identical_answers_derive_no_changes():
    assert derived_changes(_answer(), _answer())["changes"] == []


def test_a_follow_up_row_derives_its_changes_from_the_stored_judgements(project):
    store = store_for(project)
    synthesis_sha, user = completed_synthesis(store)
    follow = prepare_architecture_synthesis(store, question="Weigh the criticism.", developments=[question_selection()],
                                            prior_request_sha256=synthesis_sha, criticism=["The first stage is too strong."])
    follow_user = json.loads(follow["request"]["user"])
    answer = valid_answer(follow_user)
    answer["trajectory"][0]["basis"] = "inferred"
    answer["changes_from_prior"] = ["The first stage is now inferred."]
    answer["criticism_assessments"] = [{"criticism": "c1", "verdict": "accepted", "reason": "The stage's basis was stronger than the record."}]
    row = complete_architecture_synthesis(store, replay(follow["request"], answer))
    assert row["changes_stated"] == ["The first stage is now inferred."]
    assert any(change["kind"] == "stage_basis_changed" for change in row["changes_derived"]["changes"])


def test_the_synthesis_projection_still_lists_its_history(project):
    store = store_for(project)
    completed_synthesis(store)
    assert project_architecture_synthesis(store)["status"] == "ready"
