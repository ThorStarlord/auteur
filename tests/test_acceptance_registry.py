from pathlib import Path

import pytest

from auteur.acceptance import AcceptanceRegistry


def test_registry_routes_acceptance_to_the_single_matching_owner(tmp_path: Path) -> None:
    calls: list[tuple[str, str, bool]] = []

    class Owner:
        def can_accept(self, target_artifact_id: str) -> bool:
            return target_artifact_id.startswith("scene_")

        def accept(self, target_artifact_id: str, candidate_id: str, *, confirm: bool) -> object:
            calls.append((target_artifact_id, candidate_id, confirm))
            return {"accepted": True}

    registry = AcceptanceRegistry()
    registry.register(Owner())

    assert registry.accept("scene_01", "candidate_1", confirm=True) == {"accepted": True}
    assert calls == [("scene_01", "candidate_1", True)]


def test_registry_fails_closed_for_unowned_or_ambiguous_targets() -> None:
    registry = AcceptanceRegistry()

    with pytest.raises(ValueError, match="No acceptance owner"):
        registry.accept("unknown", "candidate", confirm=True)


def test_registry_journals_started_and_completed_acceptance(tmp_path: Path) -> None:
    class Owner:
        def can_accept(self, target_artifact_id: str) -> bool:
            return True

        def accept(self, target_artifact_id: str, candidate_id: str, *, confirm: bool) -> object:
            return {"accepted": True}

    registry = AcceptanceRegistry(tmp_path)
    registry.register(Owner())

    registry.accept("scene_01", "candidate_1", confirm=True)

    records = registry.journal.recoverable()
    assert len(records) == 0
    assert registry.journal.history()[-1]["status"] == "completed"


def test_registry_journals_failed_acceptance_for_recovery(tmp_path: Path) -> None:
    class Owner:
        def can_accept(self, target_artifact_id: str) -> bool:
            return True

        def accept(self, target_artifact_id: str, candidate_id: str, *, confirm: bool) -> object:
            raise RuntimeError("write interrupted")

    registry = AcceptanceRegistry(tmp_path)
    registry.register(Owner())

    with pytest.raises(RuntimeError, match="write interrupted"):
        registry.accept("scene_01", "candidate_1", confirm=True)

    assert registry.journal.recoverable()[0]["status"] == "failed"


def test_recovery_report_is_explicit_and_does_not_replay_mutation(tmp_path: Path) -> None:
    journal = AcceptanceRegistry(tmp_path).journal
    journal.record(
        operation_id="op-1",
        target_artifact_id="scene_01",
        candidate_id="candidate-1",
        status="started",
    )

    report = journal.recovery_report()

    assert report["status"] == "recovery_required"
    assert report["replay_allowed"] is False
    assert report["operations"][0]["operation_id"] == "op-1"


def test_registry_recovers_owner_success_when_completion_journal_write_fails(tmp_path: Path) -> None:
    calls = {"accept": 0, "recover": 0}

    class Owner:
        def can_accept(self, target_artifact_id: str) -> bool:
            return True

        def accept(self, target_artifact_id: str, candidate_id: str, *, confirm: bool) -> object:
            calls["accept"] += 1
            return {"accepted": True, "revision": 1}

        def recover(self, target_artifact_id: str, candidate_id: str) -> object:
            calls["recover"] += 1
            return {"accepted": True, "revision": 1}

    registry = AcceptanceRegistry(tmp_path)
    registry.register(Owner())
    original_record = registry.journal.record
    failed_once = {"value": False}

    def fail_completion_once(**kwargs):
        if kwargs["status"] == "completed" and not failed_once["value"]:
            failed_once["value"] = True
            raise OSError("completion journal interrupted")
        return original_record(**kwargs)

    registry.journal.record = fail_completion_once  # type: ignore[method-assign]
    with pytest.raises(OSError, match="completion journal interrupted"):
        registry.accept("story_identity", "candidate-1", confirm=True, command_id="recover-1")

    result = registry.accept("story_identity", "candidate-1", confirm=True, command_id="recover-1")
    assert result == {"accepted": True, "revision": 1}
    assert calls == {"accept": 1, "recover": 1}
    assert registry.journal.find_completed("recover-1") is not None
