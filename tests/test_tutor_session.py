from pathlib import Path

import pytest

from auteur.story_design_packs import AuthorAction, source_fingerprint
from auteur.story_design_packs.models import DecisionCard, DecisionSourceBinding
from auteur.story_design_packs import session as session_module
from auteur.story_design_packs.session import TutorSessionStore, create_session


def _card(**overrides) -> DecisionCard:
    source_hash = source_fingerprint("identity-v1")
    values = {
        "decision": "Choose the protagonist's boundary",
        "orientation": "We are deciding the protagonist's boundary.",
        "why_it_matters": "The boundary changes the cost of later choices.",
        "craft_concept": "Moral pressure",
        "recommendation": "Refuse the easy harm",
        "alternatives": ["Accept the harm", "Delay the choice"],
        "tradeoffs": ["Preserves integrity but increases external pressure."],
        "beginner_trap": "Treating the boundary as a label instead of a costly choice.",
        "downstream_consequences": ["The antagonist can escalate through consequences."],
        "evidence": ["story_identity:boundary"],
        "source_binding": DecisionSourceBinding(
            source_artifact="story_identity",
            source_subject="story_identity.yaml",
            source_fingerprint=source_hash,
        ),
    }
    values.update(overrides)
    return DecisionCard(**values)


def _fingerprints(value: str = "identity-v1") -> dict[str, str]:
    return {"story_identity": source_fingerprint(value)}


def test_session_round_trip_is_stable_local_and_noncanonical(tmp_path: Path):
    store = TutorSessionStore(tmp_path)
    first = create_session(_card(), _fingerprints())
    second = create_session(_card(), dict(reversed(list(_fingerprints().items()))))

    path = store.save(first)
    loaded = store.load(first.session_id)

    assert first.session_id == second.session_id
    assert loaded == first
    assert loaded.status == "active"
    assert loaded.authority_status == "LOCAL / NONCANONICAL"
    assert path == tmp_path.resolve() / ".auteur" / "tutor" / "sessions" / f"{first.session_id}.json"
    assert not (tmp_path / "story_identity.yaml").exists()
    assert not (tmp_path / "blueprint.yaml").exists()


def test_create_session_derives_source_fingerprint_from_card_binding():
    card = _card()
    session = create_session(card)
    assert session.source_fingerprints == {
        "story_identity": card.source_binding.source_fingerprint
    }


def test_session_marks_stale_and_never_revives_implicitly(tmp_path: Path):
    store = TutorSessionStore(tmp_path)
    session = create_session(_card(), _fingerprints())
    store.save(session)

    stale = store.refresh_status(session.session_id, _fingerprints("identity-v2"))
    still_stale = store.refresh_status(session.session_id, _fingerprints())

    assert stale.status == "stale"
    assert stale.stale_reason == "source_fingerprint_changed"
    assert still_stale.status == "stale"


@pytest.mark.parametrize(
    ("action", "expected_status"),
    [
        (AuthorAction.CHOOSE, "resolved"),
        (AuthorAction.KEEP_UNRESOLVED, "resolved"),
        (AuthorAction.REJECT_FINDING, "resolved"),
        (AuthorAction.REQUEST_ALTERNATIVES, "active"),
    ],
)
def test_allowed_responses_only_change_local_session(
    tmp_path: Path, action: AuthorAction, expected_status: str
):
    identity = tmp_path / "story_identity.yaml"
    blueprint = tmp_path / "blueprint.yaml"
    identity.write_bytes(b"accepted identity\n")
    blueprint.write_bytes(b"accepted blueprint\n")
    before = (identity.read_bytes(), blueprint.read_bytes())

    store = TutorSessionStore(tmp_path)
    session = create_session(_card(), _fingerprints())
    store.save(session)
    result = store.record_response(
        session.session_id,
        action,
        "author response",
        current_source_fingerprints=_fingerprints(),
    )

    assert result.response_action == action
    assert result.response_value == "author response"
    assert result.status == expected_status
    assert (identity.read_bytes(), blueprint.read_bytes()) == before
    assert list((tmp_path / ".auteur" / "tutor" / "sessions").glob("*.json"))


def test_stale_session_rejects_every_substantive_action(tmp_path: Path):
    store = TutorSessionStore(tmp_path)
    session = create_session(_card(), _fingerprints())
    store.save(session)
    store.refresh_status(session.session_id, _fingerprints("identity-v2"))

    for action in AuthorAction:
        with pytest.raises(ValueError, match="stale Tutor session"):
            store.record_response(
                session.session_id,
                action,
                current_source_fingerprints=_fingerprints("identity-v2"),
            )

    assert store.load(session.session_id).status == "stale"


def test_record_response_fails_closed_without_complete_current_evidence(tmp_path: Path):
    store = TutorSessionStore(tmp_path)
    session = create_session(_card(), _fingerprints())
    store.save(session)

    with pytest.raises(ValueError, match="required"):
        store.record_response(session.session_id, AuthorAction.CHOOSE)

    with pytest.raises(ValueError, match="malformed"):
        store.record_response(
            session.session_id,
            AuthorAction.CHOOSE,
            current_source_fingerprints={"story_identity": "not-a-hash"},
        )

    with pytest.raises(ValueError, match="stale Tutor session"):
        store.record_response(
            session.session_id,
            AuthorAction.CHOOSE,
            current_source_fingerprints={},
        )
    assert store.load(session.session_id).status == "stale"


def test_unknown_disallowed_and_repeat_responses_are_rejected(tmp_path: Path):
    store = TutorSessionStore(tmp_path)
    card = _card(author_actions=[AuthorAction.CHOOSE])
    session = create_session(card, _fingerprints())
    store.save(session)

    with pytest.raises(ValueError, match="Unknown Tutor response action"):
        store.record_response(
            session.session_id,
            "rewrite_canon",
            current_source_fingerprints=_fingerprints(),
        )
    with pytest.raises(ValueError, match="not allowed"):
        store.record_response(
            session.session_id,
            AuthorAction.REJECT_FINDING,
            current_source_fingerprints=_fingerprints(),
        )

    store.record_response(
        session.session_id,
        AuthorAction.CHOOSE,
        current_source_fingerprints=_fingerprints(),
    )
    with pytest.raises(ValueError, match="already resolved"):
        store.record_response(
            session.session_id,
            AuthorAction.CHOOSE,
            current_source_fingerprints=_fingerprints(),
        )


def test_atomic_replace_failure_preserves_existing_session_and_cleans_temp(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    store = TutorSessionStore(tmp_path)
    session = create_session(_card(), _fingerprints())
    target = store.save(session)
    original = target.read_bytes()

    candidate = store.load(session.session_id)
    candidate.response_value = "must not leak into existing file"

    def fail_replace(_source, _target):
        raise OSError("controlled replace failure")

    monkeypatch.setattr(session_module.os, "replace", fail_replace)
    with pytest.raises(OSError, match="controlled replace failure"):
        store.save(candidate)

    assert target.read_bytes() == original
    assert list(store.root.glob("*.tmp")) == []
