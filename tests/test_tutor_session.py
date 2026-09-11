import os

import pytest

from auteur.story_design_packs import (
    AuthorAction,
    ResolvedTutorSessionError,
    StaleTutorSessionError,
    TutorSessionCurrentnessError,
    TutorSessionStore,
    create_session,
    source_fingerprint,
    stable_session_id,
)
from auteur.story_design_packs.models import DecisionCard, DecisionSourceBinding
import auteur.story_design_packs.session as session_module


def _card(*, actions=None, source_text="source-v1") -> DecisionCard:
    binding = DecisionSourceBinding(
        source_artifact="story_design_context",
        source_subject="story_identity",
        source_fingerprint=source_fingerprint(source_text),
    )
    values = {
        "decision": "Choose the protagonist's boundary",
        "orientation": "A moral choice shapes the story's pressure.",
        "why_it_matters": "It determines what the audience expects next.",
        "craft_concept": "Moral boundary",
        "recommendation": "Make the boundary costly to cross.",
        "alternatives": ["Keep it implicit"],
        "tradeoffs": ["Less immediate clarity"],
        "beginner_trap": "Treating the boundary as decoration.",
        "downstream_consequences": ["Later choices inherit the cost."],
        "evidence": ["setup:boundary"],
        "source_binding": binding,
        "source_rule": "boundary.rule",
    }
    if actions is not None:
        values["author_actions"] = actions
    return DecisionCard(**values)


def _fingerprints(card: DecisionCard) -> dict[str, str]:
    return {
        card.source_binding.source_artifact: card.source_binding.source_fingerprint,
    }


def test_create_save_load_round_trip_is_local_and_noncanonical(tmp_path):
    card = _card()
    session = create_session(card)
    store = TutorSessionStore(tmp_path)

    path = store.save(session)
    loaded = store.load(session.session_id)

    assert loaded == session
    assert loaded.card_id == card.card_id
    assert loaded.authority_status == "LOCAL / NONCANONICAL"
    assert loaded.status == "active"
    assert path == tmp_path / ".auteur" / "tutor" / "sessions" / f"{session.session_id}.json"
    assert path.is_file()


def test_session_identity_is_stable_for_sorted_fingerprints_and_changes_with_source():
    card = _card()
    first = {
        "b": source_fingerprint("b"),
        "a": source_fingerprint("a"),
    }
    second = {
        "a": source_fingerprint("a"),
        "b": source_fingerprint("b"),
    }

    assert stable_session_id(card.card_id, first) == stable_session_id(card.card_id, second)
    assert stable_session_id(card.card_id, first) != stable_session_id(
        card.card_id,
        {**first, "a": source_fingerprint("changed")},
    )


def test_create_session_derives_source_fingerprint_from_card_binding():
    card = _card()
    session = create_session(card)

    assert session.source_fingerprints == _fingerprints(card)
    assert session.session_id == stable_session_id(card.card_id, _fingerprints(card))


def test_refresh_marks_changed_source_stale_and_never_revives_it(tmp_path):
    card = _card()
    session = create_session(card)
    store = TutorSessionStore(tmp_path)
    store.save(session)

    stale = store.refresh_status(
        session.session_id,
        {"story_design_context": source_fingerprint("source-v2")},
    )

    assert stale.status == "stale"
    assert stale.stale_reason == "source_fingerprint_changed:story_design_context"
    assert store.load(session.session_id).status == "stale"

    still_stale = store.refresh_status(session.session_id, None)
    assert still_stale.status == "stale"
    assert still_stale.stale_reason == stale.stale_reason


def test_refresh_fails_closed_when_currentness_evidence_is_missing_or_malformed(tmp_path):
    card = _card()
    session = create_session(card)
    store = TutorSessionStore(tmp_path)
    store.save(session)

    with pytest.raises(TutorSessionCurrentnessError, match="required"):
        store.refresh_status(session.session_id, None)
    with pytest.raises(TutorSessionCurrentnessError, match="incomplete"):
        store.refresh_status(session.session_id, {})
    with pytest.raises(TutorSessionCurrentnessError, match="Malformed"):
        store.refresh_status(session.session_id, {"story_design_context": "not-a-hash"})

    assert store.load(session.session_id).status == "active"


@pytest.mark.parametrize(
    ("action", "expected_status"),
    [
        (AuthorAction.CHOOSE, "resolved"),
        (AuthorAction.KEEP_UNRESOLVED, "resolved"),
        (AuthorAction.REJECT_FINDING, "resolved"),
        (AuthorAction.REQUEST_ALTERNATIVES, "active"),
    ],
)
def test_allowed_responses_record_only_advisory_session_state(
    tmp_path,
    action,
    expected_status,
):
    card = _card()
    session = create_session(card)
    store = TutorSessionStore(tmp_path)
    store.save(session)

    updated = store.record_response(
        session.session_id,
        action,
        "author-note",
        current_source_fingerprints=_fingerprints(card),
    )

    assert updated.response_action == action
    assert updated.response_value == "author-note"
    assert updated.status == expected_status
    assert updated.authority_status == "LOCAL / NONCANONICAL"


def test_record_response_establishes_currentness_without_prior_refresh(tmp_path):
    card = _card()
    session = create_session(card)
    store = TutorSessionStore(tmp_path)
    store.save(session)

    with pytest.raises(TutorSessionCurrentnessError, match="required"):
        store.record_response(session.session_id, AuthorAction.CHOOSE)
    with pytest.raises(TutorSessionCurrentnessError, match="incomplete"):
        store.record_response(
            session.session_id,
            AuthorAction.CHOOSE,
            current_source_fingerprints={},
        )

    with pytest.raises(StaleTutorSessionError, match="regenerate"):
        store.record_response(
            session.session_id,
            AuthorAction.CHOOSE,
            current_source_fingerprints={
                "story_design_context": source_fingerprint("changed-source")
            },
        )

    persisted = store.load(session.session_id)
    assert persisted.status == "stale"
    assert persisted.response_action is None


@pytest.mark.parametrize("action", list(AuthorAction))
def test_stale_session_rejects_every_substantive_response(tmp_path, action):
    card = _card()
    session = create_session(card)
    store = TutorSessionStore(tmp_path)
    store.save(session)
    store.refresh_status(
        session.session_id,
        {"story_design_context": source_fingerprint("changed-source")},
    )

    with pytest.raises(StaleTutorSessionError):
        store.record_response(
            session.session_id,
            action,
            current_source_fingerprints=_fingerprints(card),
        )

    assert store.load(session.session_id).response_action is None


def test_resolved_session_rejects_a_second_response(tmp_path):
    card = _card()
    session = create_session(card)
    store = TutorSessionStore(tmp_path)
    store.save(session)
    store.record_response(
        session.session_id,
        AuthorAction.CHOOSE,
        current_source_fingerprints=_fingerprints(card),
    )

    with pytest.raises(ResolvedTutorSessionError):
        store.record_response(
            session.session_id,
            AuthorAction.REQUEST_ALTERNATIVES,
            current_source_fingerprints=_fingerprints(card),
        )


def test_unknown_and_card_disallowed_actions_are_rejected(tmp_path):
    card = _card(actions=[AuthorAction.CHOOSE])
    session = create_session(card)
    store = TutorSessionStore(tmp_path)
    store.save(session)

    with pytest.raises(ValueError, match="Unknown"):
        store.record_response(
            session.session_id,
            "apply_to_story",
            current_source_fingerprints=_fingerprints(card),
        )
    with pytest.raises(ValueError, match="not allowed"):
        store.record_response(
            session.session_id,
            AuthorAction.REJECT_FINDING,
            current_source_fingerprints=_fingerprints(card),
        )

    assert store.load(session.session_id).response_action is None


def test_atomic_write_failure_preserves_existing_session_and_cleans_temp(tmp_path, monkeypatch):
    card = _card()
    session = create_session(card)
    store = TutorSessionStore(tmp_path)
    target = store.save(session)
    before = target.read_bytes()

    changed = session.model_copy()
    changed.response_action = AuthorAction.REQUEST_ALTERNATIVES
    changed.response_value = "new request"

    def fail_replace(_source, _target):
        raise OSError("controlled replace failure")

    monkeypatch.setattr(session_module.os, "replace", fail_replace)

    with pytest.raises(OSError, match="controlled replace failure"):
        store.save(changed)

    assert target.read_bytes() == before
    assert list(target.parent.glob(f".{session.session_id}.*.tmp")) == []


def test_session_operations_do_not_modify_story_identity_or_blueprint(tmp_path):
    story_identity = tmp_path / "story_identity.yaml"
    blueprint = tmp_path / "blueprint.yaml"
    story_identity.write_bytes(b"story: canonical\n")
    blueprint.write_bytes(b"blueprint: canonical\n")
    before_identity = story_identity.read_bytes()
    before_blueprint = blueprint.read_bytes()

    card = _card()
    session = create_session(card)
    store = TutorSessionStore(tmp_path)
    store.save(session)
    store.refresh_status(session.session_id, _fingerprints(card))
    store.record_response(
        session.session_id,
        AuthorAction.CHOOSE,
        "option-a",
        current_source_fingerprints=_fingerprints(card),
    )

    assert story_identity.read_bytes() == before_identity
    assert blueprint.read_bytes() == before_blueprint
    assert not (tmp_path / "structure-proposal.yaml").exists()


def test_invalid_session_id_cannot_escape_local_session_directory(tmp_path):
    store = TutorSessionStore(tmp_path)

    with pytest.raises(ValueError, match="session_id"):
        store.load("../story_identity")

    assert not (tmp_path.parent / "story_identity.json").exists()
