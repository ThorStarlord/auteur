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
