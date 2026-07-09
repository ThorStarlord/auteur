"""Tests: gentlefemdom genre contract loads and provides expected structure."""

import pytest
from auteur.genres.registry import load_genre_contract
from auteur.blueprint import Genre


class TestGentlefemdomContract:
    """Verify gentlefemdom contract is non-generic and loads correctly."""

    def test_gentlefemdom_contract_loads(self):
        """Genre contract for gentlefemdom loads without fallback."""
        contract = load_genre_contract(Genre.GENTLEFEMDOM)
        assert contract is not None
        # Should not be the fallback generic contract
        assert "Actions have consequences" not in contract.core_truth

    def test_contract_has_consent_non_negotiable(self):
        """Contract explicitly requires consent clarity."""
        contract = load_genre_contract(Genre.GENTLEFEMDOM)
        core_truth = contract.core_truth.lower()
        assert "consent" in core_truth

    def test_contract_forbids_coercion(self):
        """Contract lists coercion in forbidden mismatches."""
        contract = load_genre_contract(Genre.GENTLEFEMDOM)
        forbidden = [m.lower() for m in contract.common_failure_modes]
        assert any("coercion" in m or "force" in m for m in forbidden)

    def test_contract_requires_care(self):
        """Contract requires care/safety as central."""
        contract = load_genre_contract(Genre.GENTLEFEMDOM)
        core_truth = contract.core_truth.lower()
        assert "care" in core_truth or "safety" in core_truth or "trust" in core_truth
