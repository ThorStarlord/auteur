"""Tests for the ReasoningRuntime draft critic adapters."""

from __future__ import annotations

import pytest

from auteur.reasoning.runtime import CriticRegistry, CriticSpec
from auteur.reasoning.draft_critics import register_draft_critics


EXPECTED_IDS = {"draft.contract", "draft.arc", "draft.tension", "draft.slop", "draft.theme"}


def _registered_ids(registry: CriticRegistry) -> set[str]:
    return {spec.critic_id for spec in registry._entries.values()}


def _registered_specs(registry: CriticRegistry) -> list[CriticSpec]:
    return list(registry._entries.values())


class TestDraftCriticRegistration:
    def test_all_five_registered(self) -> None:
        registry = CriticRegistry()
        register_draft_critics(registry)
        ids = _registered_ids(registry)
        assert ids == EXPECTED_IDS, f"Missing: {EXPECTED_IDS - ids}"

    def test_stable_versions(self) -> None:
        registry = CriticRegistry()
        register_draft_critics(registry)
        for spec in _registered_specs(registry):
            assert spec.version == "0.1.0", f"{spec.critic_id} version mismatch"

    def test_no_dependencies(self) -> None:
        registry = CriticRegistry()
        register_draft_critics(registry)
        for spec in _registered_specs(registry):
            assert spec.requires == (), f"{spec.critic_id} declares dependencies: {spec.requires}"

    def test_input_keys_defined(self) -> None:
        registry = CriticRegistry()
        register_draft_critics(registry)
        for spec in _registered_specs(registry):
            assert len(spec.input_keys) > 0, f"{spec.critic_id} missing input_keys"
            assert "draft" in spec.input_keys
            assert "llm" in spec.input_keys

    def test_discover_returns_spec(self) -> None:
        registry = CriticRegistry()
        register_draft_critics(registry)
        for cid in EXPECTED_IDS:
            spec = registry.discover(critic_id=cid)
            assert spec is not None
            assert spec.critic_id == cid

    def test_idempotent_double_registration(self) -> None:
        registry = CriticRegistry()
        register_draft_critics(registry)
        register_draft_critics(registry)  # second call must not raise
        ids = _registered_ids(registry)
        assert ids == EXPECTED_IDS

    def test_adapter_signature_is_callable(self) -> None:
        registry = CriticRegistry()
        register_draft_critics(registry)
        for spec in _registered_specs(registry):
            assert callable(spec.run)
