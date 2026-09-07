from pathlib import Path

from auteur.story_design_packs.models import DecisionCard
from auteur.story_design_packs.session import TutorSessionStore, create_session


def _card() -> DecisionCard:
    return DecisionCard(
        decision="Choose the protagonist's boundary",
        orientation="We are deciding the protagonist's boundary.",
        why_it_matters="The boundary changes the cost of later choices.",
        craft_concept="Moral pressure",
        recommendation="Refuse the easy harm",
        alternatives=["Accept the harm", "Delay the choice"],
        tradeoffs=["Preserves integrity but increases external pressure."],
        beginner_trap="Treating the boundary as a label instead of a costly choice.",
        downstream_consequences=["The antagonist can escalate through consequences."],
        evidence=["story_identity:abc"],
    )


def test_session_round_trip_is_atomic_and_noncanonical(tmp_path: Path):
    store = TutorSessionStore(tmp_path)
    session = create_session(_card(), {"story_identity": "abc"})
    store.save(session)

    loaded = store.load(session.session_id)
    assert loaded.session_id == session.session_id
    assert loaded.status == "active"
    assert not (tmp_path / "story_identity.yaml").exists()


def test_session_marks_stale_when_source_fingerprint_changes(tmp_path: Path):
    store = TutorSessionStore(tmp_path)
    session = create_session(_card(), {"story_identity": "abc"})
    store.save(session)

    stale = store.refresh_status(session.session_id, {"story_identity": "changed"})
    assert stale.status == "stale"
    assert stale.stale_reason == "source_fingerprint_changed"
