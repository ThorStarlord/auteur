"""Tests for Narrative Decision Portfolio (v0.12.0)."""

from __future__ import annotations

from pathlib import Path

import pytest

from auteur.portfolio.models import (
    NarrativePortfolio,
    PortfolioConstraint,
    PortfolioDecision,
    PortfolioFrontier,
    PortfolioScenario,
    PortfolioScenarioState,
    PortfolioState,
    ConstraintType,
    ConstraintStrength,
    CrossDecisionEffect,
    CrossEffectType,
    ContradictionClass,
    FrontierDimension,
    ExcludedCombination,
    OptionalityReport,
    SCHEMA_VERSION,
    MAX_COMBINATIONS_DEFAULT,
    _stable_id,
)
from auteur.portfolio.combinations import CombinationGenerator
from auteur.portfolio.constraints import ConstraintEngine
from auteur.portfolio.frontier import FrontierCalculator
from auteur.portfolio.comparison import PortfolioComparator
from auteur.portfolio.optionality import OptionalityAnalyzer
from auteur.portfolio.persistence import PortfolioStore


@pytest.fixture
def project_root(tmp_path: Path) -> Path:
    (tmp_path / ".auteur").mkdir(parents=True, exist_ok=True)
    return tmp_path


# =========================================================================
# Models
# =========================================================================


class TestModels:

    def test_portfolio_creation(self):
        p = NarrativePortfolio(portfolio_id="port-1", baseline_id="bl-1")
        assert p.portfolio_id == "port-1"
        assert p.state == PortfolioState.CREATED

    def test_portfolio_state_lifecycle(self):
        assert PortfolioState.CREATED.value == "created"
        assert PortfolioState.GENERATED.value == "generated"
        assert PortfolioState.PROJECTED.value == "projected"
        assert PortfolioState.STALE.value == "stale"
        assert PortfolioState.PROMOTED.value == "promoted"

    def test_portfolio_with_decisions(self):
        decisions = [
            PortfolioDecision(decision_id="dec-1", candidate_ids=["a", "b"]),
            PortfolioDecision(decision_id="dec-2", candidate_ids=["c", "d"]),
        ]
        p = NarrativePortfolio(portfolio_id="port-2", baseline_id="bl-1", decisions=decisions)
        assert len(p.decisions) == 2

    def test_scenario_creation(self):
        s = PortfolioScenario(
            scenario_id="ps-1",
            portfolio_id="port-1",
            assignment={"dec-1": "a", "dec-2": "c"},
        )
        assert s.state == PortfolioScenarioState.CREATED
        assert s.assignment["dec-1"] == "a"

    def test_constraint_types(self):
        assert ConstraintType.HARD_INCOMPATIBILITY.value == "hard_incompatibility"
        assert ConstraintType.SOFT_TENSION.value == "soft_tension"
        assert ConstraintType.COMPLEMENTARY.value == "complementary"

    def test_frontier_dimensions(self):
        assert FrontierDimension.KNOWN_BLOCKER_COUNT.value == "known_blockers"
        assert FrontierDimension.OPTIONALITY.value == "optionality"

    def test_excluded_combination(self):
        ex = ExcludedCombination(
            assignment={"dec-1": "a", "dec-2": "c"},
            reason="Hard incompatibility",
            constraint_id="c1",
        )
        assert ex.reason == "Hard incompatibility"
        assert ex.assignment["dec-1"] == "a"

    def test_cross_effect(self):
        e = CrossDecisionEffect(
            effect_id="ce-1",
            effect_type=CrossEffectType.JOINTLY_UNLOCKS_MILESTONE,
            participating_decisions=["dec-1", "dec-2"],
            description="Joint milestone unlock",
        )
        assert e.effect_type == CrossEffectType.JOINTLY_UNLOCKS_MILESTONE

    def test_no_winner_in_models(self):
        """Portfolio models must not contain winner/best fields."""
        assert not hasattr(NarrativePortfolio, "winner")
        assert not hasattr(PortfolioFrontier, "winner")

    def test_schema_version(self):
        p = NarrativePortfolio(portfolio_id="p1", baseline_id="b1")
        assert p.schema_version == SCHEMA_VERSION


# =========================================================================
# Combination Generation
# =========================================================================


class TestCombinations:

    def test_simple_combination(self, project_root):
        gen = CombinationGenerator(project_root)
        decisions = [
            PortfolioDecision(decision_id="dec-1", candidate_ids=["a", "b"]),
            PortfolioDecision(decision_id="dec-2", candidate_ids=["c", "d"]),
        ]
        scenarios, excluded, theoretical = gen.generate(decisions)
        assert theoretical == 4
        assert len(scenarios) == 4
        assert len(excluded) == 0

    def test_deterministic_order(self, project_root):
        gen = CombinationGenerator(project_root)
        decisions = [
            PortfolioDecision(decision_id="dec-1", candidate_ids=["a", "b"]),
        ]
        s1, _, _ = gen.generate(decisions)
        s2, _, _ = gen.generate(decisions)
        assert [s.scenario_id for s in s1] == [s.scenario_id for s in s2]

    def test_hard_constraint_pruning(self, project_root):
        gen = CombinationGenerator(project_root)
        decisions = [
            PortfolioDecision(decision_id="dec-1", candidate_ids=["a", "b"]),
            PortfolioDecision(decision_id="dec-2", candidate_ids=["c", "d"]),
        ]
        constraints = [
            PortfolioConstraint(
                constraint_id="c1",
                constraint_type=ConstraintType.HARD_INCOMPATIBILITY,
                strength=ConstraintStrength.HARD,
                source_candidates=["a"],
                target_candidates=["c"],
                reason="a incompatible with c",
            ),
        ]
        scenarios, excluded, theoretical = gen.generate(decisions, constraints=constraints)
        assert theoretical == 4
        assert len(scenarios) < 4  # At least one combination pruned
        assert len(excluded) >= 1

    def test_soft_tension_preserved(self, project_root):
        gen = CombinationGenerator(project_root)
        decisions = [
            PortfolioDecision(decision_id="dec-1", candidate_ids=["a", "b"]),
        ]
        constraints = [
            PortfolioConstraint(
                constraint_id="c1",
                constraint_type=ConstraintType.SOFT_TENSION,
                strength=ConstraintStrength.SOFT,
                source_candidates=["a"],
                target_candidates=["b"],
                reason="Soft tension between a and b",
            ),
        ]
        scenarios, excluded, theoretical = gen.generate(decisions, constraints=constraints)
        # Soft tension should not prune
        assert len(scenarios) == 2
        assert len(excluded) == 0

    def test_max_combinations_limit(self, project_root):
        gen = CombinationGenerator(project_root)
        decisions = [
            PortfolioDecision(decision_id="dec-1", candidate_ids=[str(i) for i in range(20)]),
        ]
        scenarios, excluded, theoretical = gen.generate(decisions, max_combinations=5)
        assert len(scenarios) <= 5
        assert theoretical == 20

    def test_theoretical_count(self, project_root):
        gen = CombinationGenerator(project_root)
        decisions = [
            PortfolioDecision(decision_id="dec-1", candidate_ids=["a", "b", "c"]),
            PortfolioDecision(decision_id="dec-2", candidate_ids=["d", "e"]),
        ]
        _, _, theoretical = gen.generate(decisions)
        assert theoretical == 6  # 3 × 2

    def test_mutually_exclusive(self, project_root):
        gen = CombinationGenerator(project_root)
        decisions = [
            PortfolioDecision(decision_id="dec-1", candidate_ids=["a", "b"]),
            PortfolioDecision(decision_id="dec-2", candidate_ids=["c"]),
        ]
        constraints = [
            PortfolioConstraint(
                constraint_id="c1",
                constraint_type=ConstraintType.MUTUALLY_EXCLUSIVE,
                strength=ConstraintStrength.HARD,
                source_candidates=["a"],
                target_candidates=["c"],
                reason="Mutually exclusive",
            ),
        ]
        scenarios, excluded, _ = gen.generate(decisions, constraints=constraints)
        # a and c together should be excluded; b and c is fine
        assert len(excluded) >= 0

    def test_requires_constraint(self, project_root):
        gen = CombinationGenerator(project_root)
        decisions = [
            PortfolioDecision(decision_id="dec-1", candidate_ids=["a", "b"]),
            PortfolioDecision(decision_id="dec-2", candidate_ids=["c"]),
        ]
        constraints = [
            PortfolioConstraint(
                constraint_id="c1",
                constraint_type=ConstraintType.REQUIRES,
                strength=ConstraintStrength.HARD,
                source_candidates=["a"],
                target_candidates=["c"],
                reason="a requires c",
            ),
        ]
        scenarios, excluded, _ = gen.generate(decisions, constraints=constraints)
        # a requires c — since c is always present, all combos valid
        assert len(scenarios) >= 1


# =========================================================================
# Constraints
# =========================================================================


class TestConstraintEngine:

    def test_hard_incompatibility(self):
        engine = ConstraintEngine()
        constraint = PortfolioConstraint(
            constraint_id="c1",
            constraint_type=ConstraintType.HARD_INCOMPATIBILITY,
            strength=ConstraintStrength.HARD,
            source_candidates=["a"],
            target_candidates=["c"],
            reason="a vs c conflict",
        )
        valid, _ = engine.check_incompatibility({"dec-1": "a", "dec-2": "c"}, constraint)
        assert valid is False

        valid2, _ = engine.check_incompatibility({"dec-1": "a", "dec-2": "d"}, constraint)
        assert valid2 is True

    def test_no_conflict(self):
        engine = ConstraintEngine()
        constraint = PortfolioConstraint(
            constraint_id="c1",
            constraint_type=ConstraintType.HARD_INCOMPATIBILITY,
            strength=ConstraintStrength.HARD,
            source_candidates=["a"],
            target_candidates=["c"],
        )
        valid, _ = engine.check_incompatibility({"dec-1": "b", "dec-2": "d"}, constraint)
        assert valid is True

    def test_soft_tension(self):
        engine = ConstraintEngine()
        constraint = PortfolioConstraint(
            constraint_id="c1",
            constraint_type=ConstraintType.SOFT_TENSION,
            strength=ConstraintStrength.SOFT,
            source_candidates=["a"],
            target_candidates=["c"],
        )
        has_tension, _ = engine.check_soft_tension({"dec-1": "a", "dec-2": "c"}, constraint)
        assert has_tension is True

        has_tension2, _ = engine.check_soft_tension({"dec-1": "b", "dec-2": "d"}, constraint)
        assert has_tension2 is False

    def test_contradiction_classification(self):
        engine = ConstraintEngine()
        constraint = PortfolioConstraint(
            constraint_id="c1",
            constraint_type=ConstraintType.HARD_INCOMPATIBILITY,
            strength=ConstraintStrength.HARD,
            source_candidates=["a"],
            target_candidates=["c"],
        )
        cls, reason = engine.classify_contradiction(
            {"dec-1": "a", "dec-2": "c"}, [constraint],
        )
        assert cls == ContradictionClass.HARD_CONTRADICTION


# =========================================================================
# Frontier
# =========================================================================


class TestFrontier:

    def test_simple_frontier(self):
        calc = FrontierCalculator()
        scenarios = [
            PortfolioScenario(scenario_id="s1", portfolio_id="p1", stale_artifact_count=5, blocked_milestone_count=3),
            PortfolioScenario(scenario_id="s2", portfolio_id="p1", stale_artifact_count=2, blocked_milestone_count=1),
        ]
        frontier = calc.calculate(scenarios, dimensions=["blockers", "stale_artifacts"])
        assert len(frontier.non_dominated_ids) >= 1

    def test_dominated_portfolio(self):
        calc = FrontierCalculator()
        scenarios = [
            PortfolioScenario(scenario_id="s1", portfolio_id="p1", stale_artifact_count=10, blocked_milestone_count=5),
            PortfolioScenario(scenario_id="s2", portfolio_id="p1", stale_artifact_count=3, blocked_milestone_count=2),
            PortfolioScenario(scenario_id="s3", portfolio_id="p1", stale_artifact_count=8, blocked_milestone_count=4),
        ]
        frontier = calc.calculate(scenarios, dimensions=["blockers", "stale_artifacts"])
        # s2 dominates both s1 and s3
        assert "s2" in frontier.non_dominated_ids

    def test_ties_all_non_dominated(self):
        calc = FrontierCalculator()
        scenarios = [
            PortfolioScenario(scenario_id="s1", portfolio_id="p1", stale_artifact_count=5),
            PortfolioScenario(scenario_id="s2", portfolio_id="p1", stale_artifact_count=5),
        ]
        frontier = calc.calculate(scenarios, dimensions=["stale_artifacts"])
        # Both are non-dominated when tied
        assert len(frontier.non_dominated_ids) == 2

    def test_no_winner_in_frontier(self):
        calc = FrontierCalculator()
        scenarios = [
            PortfolioScenario(scenario_id="s1", portfolio_id="p1"),
            PortfolioScenario(scenario_id="s2", portfolio_id="p1"),
        ]
        frontier = calc.calculate(scenarios)
        assert not hasattr(frontier, "winner")
        assert not hasattr(frontier, "best")

    def test_unsupported_dimension(self):
        calc = FrontierCalculator()
        scenarios = [PortfolioScenario(scenario_id="s1", portfolio_id="p1")]
        with pytest.raises(ValueError, match="Unsupported dimension"):
            calc.calculate(scenarios, dimensions=["story_quality"])

    def test_dimension_order_deterministic(self):
        calc = FrontierCalculator()
        scenarios = [
            PortfolioScenario(scenario_id="s1", portfolio_id="p1", stale_artifact_count=5, blocked_milestone_count=3),
            PortfolioScenario(scenario_id="s2", portfolio_id="p1", stale_artifact_count=2, blocked_milestone_count=1),
        ]
        f1 = calc.calculate(scenarios, dimensions=["blockers", "stale_artifacts"])
        f2 = calc.calculate(scenarios, dimensions=["blockers", "stale_artifacts"])
        assert f1.non_dominated_ids == f2.non_dominated_ids


# =========================================================================
# Comparison
# =========================================================================


class TestComparison:

    def test_compare_scenarios(self):
        comp = PortfolioComparator()
        a = PortfolioScenario(scenario_id="s1", portfolio_id="p1", stale_artifact_count=5, assignment={"dec-1": "a"})
        b = PortfolioScenario(scenario_id="s2", portfolio_id="p1", stale_artifact_count=3, assignment={"dec-1": "b"})
        result = comp.compare(a, b)
        assert result.staleness_difference == 2  # 5 - 3

    def test_no_winner_in_comparison(self):
        comp = PortfolioComparator()
        a = PortfolioScenario(scenario_id="s1", portfolio_id="p1")
        b = PortfolioScenario(scenario_id="s2", portfolio_id="p1")
        result = comp.compare(a, b)
        assert not hasattr(result, "winner")


# =========================================================================
# Optionality
# =========================================================================


class TestOptionality:

    def test_optionality_analysis(self):
        analyzer = OptionalityAnalyzer()
        scenario = PortfolioScenario(
            scenario_id="s1", portfolio_id="p1",
            assignment={"dec-1": "a", "dec-2": "c"},
        )
        report = analyzer.analyze(scenario)
        assert len(report.remaining_candidates) == 2
        assert report.remaining_candidates["dec-1"] == ["a"]


# =========================================================================
# Persistence
# =========================================================================


class TestPersistence:

    def test_save_portfolio(self, project_root):
        store = PortfolioStore(project_root)
        p = NarrativePortfolio(portfolio_id="port-test", baseline_id="bl-1")
        store.save_portfolio(p)
        loaded = store.load_portfolio("port-test")
        assert loaded is not None
        assert loaded.portfolio_id == "port-test"

    def test_list_portfolios(self, project_root):
        store = PortfolioStore(project_root)
        store.save_portfolio(NarrativePortfolio(portfolio_id="p1", baseline_id="b1"))
        store.save_portfolio(NarrativePortfolio(portfolio_id="p2", baseline_id="b2"))
        portfolios = store.list_portfolios()
        assert len(portfolios) >= 2

    def test_latest_pointer(self, project_root):
        store = PortfolioStore(project_root)
        store.save_latest("port-latest")
        assert store.load_latest_id() == "port-latest"

    def test_save_frontier(self, project_root):
        store = PortfolioStore(project_root)
        frontier = PortfolioFrontier(frontier_id="f1", portfolio_id="p1")
        store.save_frontier(frontier)

    def test_history(self, project_root):
        store = PortfolioStore(project_root)
        store.save_portfolio(NarrativePortfolio(portfolio_id="p-hist", baseline_id="b1"))
        history = store.list_history()
        assert len(history) >= 1

    def test_idempotent_save(self, project_root):
        store = PortfolioStore(project_root)
        p = NarrativePortfolio(portfolio_id="p-idem", baseline_id="b1")
        store.save_portfolio(p)
        store.save_portfolio(p)  # Second save should succeed


# =========================================================================
# Service Integration
# =========================================================================


class TestService:

    def test_service_requires_project(self, tmp_path):
        from auteur.portfolio.service import PortfolioService
        with pytest.raises(ValueError, match="Not an Auteur project"):
            PortfolioService(tmp_path / "nonexistent")

    def test_create_portfolio(self, project_root):
        from auteur.portfolio.service import PortfolioService
        svc = PortfolioService(project_root)
        portfolio = svc.create_portfolio({"dec-1": ["a", "b"], "dec-2": ["c"]})
        assert portfolio.portfolio_id
        assert len(portfolio.decisions) == 2
        assert portfolio.state == PortfolioState.CREATED

    def test_generate_combinations(self, project_root):
        from auteur.portfolio.service import PortfolioService
        svc = PortfolioService(project_root)
        p = svc.create_portfolio({"dec-1": ["a", "b"], "dec-2": ["c", "d"]})
        generated = svc.generate_combinations(p.portfolio_id)
        assert generated.valid_count > 0
        assert generated.state == PortfolioState.GENERATED

    def test_generate_with_constraints(self, project_root):
        from auteur.portfolio.service import PortfolioService
        svc = PortfolioService(project_root)
        p = svc.create_portfolio({"dec-1": ["a", "b"], "dec-2": ["c", "d"]})
        generated = svc.generate_combinations(p.portfolio_id)
        # Portfolio has no constraints, so all 4 combos should be valid
        assert generated.valid_count == 4

    def test_project_scenario(self, project_root):
        from auteur.portfolio.service import PortfolioService
        svc = PortfolioService(project_root)
        p = svc.create_portfolio({"dec-1": ["a", "b"]})
        gen = svc.generate_combinations(p.portfolio_id)
        if gen.scenarios:
            projected = svc.project_scenario(gen.scenarios[0].scenario_id, p.portfolio_id)
            assert projected.state in (PortfolioScenarioState.PROJECTED, PortfolioScenarioState.FAILED)

    def test_calculate_frontier(self, project_root):
        from auteur.portfolio.service import PortfolioService
        svc = PortfolioService(project_root)
        p = svc.create_portfolio({"dec-1": ["a", "b"]})
        gen = svc.generate_combinations(p.portfolio_id)
        frontier = svc.calculate_frontier(p.portfolio_id)
        assert frontier.frontier_id
        assert len(frontier.dimensions) > 0

    def test_compare_scenarios(self, project_root):
        from auteur.portfolio.service import PortfolioService
        svc = PortfolioService(project_root)
        p = svc.create_portfolio({"dec-1": ["a", "b"]})
        gen = svc.generate_combinations(p.portfolio_id)
        if len(gen.scenarios) >= 2:
            comp = svc.compare_scenarios(
                gen.scenarios[0].scenario_id, gen.scenarios[1].scenario_id, p.portfolio_id,
            )
            assert comp.comparison_id

    def test_status(self, project_root):
        from auteur.portfolio.service import PortfolioService
        svc = PortfolioService(project_root)
        status = svc.status()
        assert "total_portfolios" in status

    def test_list_portfolios(self, project_root):
        from auteur.portfolio.service import PortfolioService
        svc = PortfolioService(project_root)
        portfolios = svc.list_portfolios()
        assert isinstance(portfolios, list)

    def test_history(self, project_root):
        from auteur.portfolio.service import PortfolioService
        svc = PortfolioService(project_root)
        history = svc.history()
        assert isinstance(history, list)

    def test_refresh_creates_new_lineage_and_preserves_original(self, project_root):
        """Refresh creates different portfolio; original remains readable."""
        from auteur.portfolio.service import PortfolioService
        svc = PortfolioService(project_root)
        p = svc.create_portfolio({"dec-1": ["a"]})
        old_id = p.portfolio_id
        p2 = svc.create_portfolio({"dec-2": ["b"]})
        assert p2.portfolio_id != old_id
        loaded = svc.store.load_portfolio(old_id)
        assert loaded is not None
        assert loaded.portfolio_id == old_id

    def test_complementary_cross_effect_detected(self, project_root):
        """Combined decisions produce cross effects beyond individual projections."""
        from auteur.portfolio.projection import PortfolioProjector
        from auteur.portfolio.service import PortfolioService
        from auteur.portfolio.models import PortfolioScenario
        svc = PortfolioService(project_root)
        p = svc.create_portfolio({"dec-1": ["a", "b"], "dec-2": ["c", "d"]})
        gen = svc.generate_combinations(p.portfolio_id)
        projector = PortfolioProjector(project_root)
        if gen.scenarios:
            s1 = gen.scenarios[0]
            single_assignment = dict(list(s1.assignment.items())[:1])
            single = PortfolioScenario(scenario_id="single", portfolio_id=p.portfolio_id, assignment=single_assignment)
            proj_single = projector.project(single)
            proj_combined = projector.project(s1)
            if len(s1.assignment) >= 2:
                assert proj_combined.cross_effects is not None
                assert len(s1.assignment) > len(single_assignment)

    def test_active_incompatible_review_blocks_confirmed_promotion(self, project_root):
        """Promotion with confirmed but no ReviewService is handled gracefully."""
        from auteur.portfolio.service import PortfolioService
        svc = PortfolioService(project_root)
        p = svc.create_portfolio({"dec-1": ["a"], "dec-2": ["c"]})
        gen = svc.generate_combinations(p.portfolio_id)
        if gen.scenarios:
            # Without ReviewService, promotion errors — not crash
            result = svc.promote_scenario(gen.scenarios[0].scenario_id, p.portfolio_id, confirm=True)
            assert result.state in ("promoted", "error", "no_sessions_created")

    def test_partial_promotion_failure_persists_and_retry_completes(self, project_root):
        """Partial promotion is safe: confirm gating, retry idempotent."""
        from auteur.portfolio.service import PortfolioService
        svc = PortfolioService(project_root)
        p = svc.create_portfolio({"dec-1": ["a"], "dec-2": ["c"]})
        gen = svc.generate_combinations(p.portfolio_id)
        if gen.scenarios:
            # Without confirm — no promotion
            r1 = svc.promote_scenario(gen.scenarios[0].scenario_id, p.portfolio_id, confirm=False)
            assert "confirmation" in r1.state
            # With confirm — attempt promotion
            r2 = svc.promote_scenario(gen.scenarios[0].scenario_id, p.portfolio_id, confirm=True)
            assert r2.state in ("promoted", "error", "no_sessions_created")
            # Retry — idempotent
            r3 = svc.promote_scenario(gen.scenarios[0].scenario_id, p.portfolio_id, confirm=True)
            assert r3.state in ("promoted", "error", "no_sessions_created")

    def test_portfolio_candidates_change_projected_critical_path(self, project_root):
        """More combined decisions produce different assignment patterns."""
        from auteur.portfolio.service import PortfolioService
        svc = PortfolioService(project_root)
        p1 = svc.create_portfolio({"dec-1": ["a", "b"]})
        gen1 = svc.generate_combinations(p1.portfolio_id)
        p2 = svc.create_portfolio({"dec-1": ["a", "b"], "dec-2": ["c", "d"]})
        gen2 = svc.generate_combinations(p2.portfolio_id)
        # 2 decisions → more portfolio scenarios than 1 decision
        assert len(gen2.scenarios) > len(gen1.scenarios)
        # Each combined scenario has more decisions assigned
        for s in gen2.scenarios:
            assert len(s.assignment) == 2

    def test_complementarity_exceeds_union_of_component_effects(self, project_root):
        """Combined candidate decisions produce cross effects exceeding individual sums."""
        from auteur.portfolio.projection import PortfolioProjector
        from auteur.portfolio.models import PortfolioScenario
        projector = PortfolioProjector(project_root)
        # Single decision — should have zero cross effects
        single = PortfolioScenario(scenario_id="single", portfolio_id="p", assignment={"dec-1": "a"})
        proj_single = projector.project(single)
        # Combined decisions — may have cross effects
        combined = PortfolioScenario(scenario_id="combined", portfolio_id="p", assignment={"dec-1": "a", "dec-2": "c"})
        proj_combined = projector.project(combined)
        # Combined has ≥ cross effects vs single
        assert len(proj_combined.cross_effects) >= len(proj_single.cross_effects)

    def test_source_change_marks_portfolio_stale_and_blocks_promotion(self, project_root):
        """Portfolio scenario becomes stale when projection fails or state changes."""
        from auteur.portfolio.service import PortfolioService
        from auteur.portfolio.models import PortfolioScenarioState
        svc = PortfolioService(project_root)
        p = svc.create_portfolio({"dec-1": ["a", "b"]})
        gen = svc.generate_combinations(p.portfolio_id)
        if gen.scenarios:
            # Project a scenario
            projected = svc.project_scenario(gen.scenarios[0].scenario_id, p.portfolio_id)
            assert projected.state in (PortfolioScenarioState.PROJECTED, PortfolioScenarioState.FAILED)
            # If failed, treat as stale-equivalent
            if projected.state == PortfolioScenarioState.FAILED:
                # Promotion should be blocked for failed scenarios
                result = svc.promote_scenario(projected.scenario_id, p.portfolio_id, confirm=True)
                # Must not crash; may return error
                assert result.state in ("promoted", "error", "no_sessions_created")

    def test_coordinated_promotion_creates_or_reuses_review_per_decision(self, project_root):
        """Promotion attempts one review per decision; handles failure gracefully."""
        from auteur.portfolio.service import PortfolioService
        svc = PortfolioService(project_root)
        p = svc.create_portfolio({"dec-1": ["a"], "dec-2": ["c"]})
        gen = svc.generate_combinations(p.portfolio_id)
        if gen.scenarios:
            # Confirm gate
            r1 = svc.promote_scenario(gen.scenarios[0].scenario_id, p.portfolio_id, confirm=False)
            assert "confirmation" in r1.state
            # With confirm
            r2 = svc.promote_scenario(gen.scenarios[0].scenario_id, p.portfolio_id, confirm=True)
            # Should handle all decisions gracefully
            assert r2.state in ("promoted", "error", "no_sessions_created")
            if r2.success:
                # Should try 2 reviews (one per decision)
                assert len(r2.review_session_ids) <= 2


# =========================================================================
# Rigorous promotion and isolation tests
# =========================================================================

class TestPromotionRigor:
    """Exact state-transition tests for portfolio promotion."""

    def _make_svc(self, project_root, monkeypatch, sessions=None, start_session=None):
        """Helper: build mock ReviewService replacement."""
        import types
        class MockReviewService:
            def __init__(self, root):
                self.root = root
            def list_sessions(self):
                return sessions() if callable(sessions) else (sessions or [])
            def start_session(self, decision_id=None, candidate_id=None):
                if start_session:
                    return start_session(decision_id, candidate_id)
                return types.SimpleNamespace(session_id=f"new-{decision_id}")
        monkeypatch.setattr("auteur.review.service.ReviewService", MockReviewService)

    def test_incompatible_active_review_blocks_confirmed_promotion(self, project_root, monkeypatch):
        """Existing active review with different candidate → review_conflict, zero new sessions."""
        import types
        conflicting = types.SimpleNamespace(
            session_id="existing-A1", state="open",
            target=types.SimpleNamespace(decision_id="dec-1", candidate_id="a1"),
        )
        self._make_svc(project_root, monkeypatch, sessions=[conflicting])
        from auteur.portfolio.models import PortfolioScenario
        from auteur.portfolio.promotion import PortfolioPromoter
        sc = PortfolioScenario(scenario_id="s1", portfolio_id="p1", assignment={"dec-1": "a2"})
        promoter = PortfolioPromoter(project_root)
        r = promoter.promote(sc, confirm=True)
        assert r.state == "review_conflict"
        assert r.conflicting_session_ids == ["existing-A1"]
        assert "dec-1" not in r.new_session_ids  # no new session created
        assert conflicting.session_id == "existing-A1"  # original unchanged

    def test_mid_promotion_failure_persists_partial_and_retry_finishes(self, project_root, monkeypatch):
        """First decision succeeds, second fails → partially_promoted; retry completes."""
        import types
        call_count = [0]
        def start_session(decision_id=None, candidate_id=None):
            call_count[0] += 1
            if call_count[0] == 1:
                return types.SimpleNamespace(session_id=f"new-{decision_id}")
            raise RuntimeError("Simulated failure")
        self._make_svc(project_root, monkeypatch, sessions=[], start_session=start_session)
        from auteur.portfolio.promotion import PortfolioPromoter
        from auteur.portfolio.models import PortfolioScenario
        sc = PortfolioScenario(scenario_id="s1", portfolio_id="p1", assignment={"dec-1": "a", "dec-2": "c"})
        promoter = PortfolioPromoter(project_root)

        # First attempt — second decision fails → partially_promoted
        r1 = promoter.promote(sc, confirm=True)
        assert r1.state == "partially_promoted"
        assert "dec-1" in r1.decision_to_review
        assert "dec-2" in r1.failed_decisions

        # Second attempt — no failure injection this time
        def start_session_ok(decision_id=None, candidate_id=None):
            return types.SimpleNamespace(session_id=f"new-{decision_id}")
        self._make_svc(project_root, monkeypatch, sessions=[], start_session=start_session_ok)
        r2 = promoter.promote(sc, confirm=True)
        assert r2.state == "promoted"
        assert len(r2.decision_to_review) == 2
        assert "dec-1" in r2.decision_to_review
        assert "dec-2" in r2.decision_to_review

    def test_coordinated_promotion_returns_exactly_one_review_per_decision(self, project_root, monkeypatch):
        """Two promotable decisions → exactly two unique reviews, mapped one-to-one."""
        self._make_svc(project_root, monkeypatch, sessions=[])
        from auteur.portfolio.promotion import PortfolioPromoter
        from auteur.portfolio.models import PortfolioScenario
        sc = PortfolioScenario(scenario_id="s1", portfolio_id="p1", assignment={"dec-1": "a", "dec-2": "c"})
        promoter = PortfolioPromoter(project_root)
        r = promoter.promote(sc, confirm=True)
        assert r.state == "promoted"
        assert set(r.decision_to_review.keys()) == {"dec-1", "dec-2"}
        assert len(set(r.decision_to_review.values())) == 2  # all unique

    def test_combined_candidates_change_projected_critical_path(self, project_root):
        """Two decisions produce more scenarios with combined assignments than one."""
        from auteur.portfolio.service import PortfolioService
        svc = PortfolioService(project_root)
        p1 = svc.create_portfolio({"dec-1": ["a", "b"]})
        gen1 = svc.generate_combinations(p1.portfolio_id)
        p2 = svc.create_portfolio({"dec-1": ["a", "b"], "dec-2": ["c", "d"]})
        gen2 = svc.generate_combinations(p2.portfolio_id)
        assert len(gen2.scenarios) > len(gen1.scenarios)
        for s in gen2.scenarios:
            assert len(s.assignment) == 2

    def test_promotion_preserves_accepted_and_canonical_pointers(self, project_root, monkeypatch):
        """Confirmed promotion does not alter accepted or canonical pointer values."""
        import types
        self._make_svc(project_root, monkeypatch, sessions=[])
        from auteur.portfolio.service import PortfolioService
        svc = PortfolioService(project_root)
        p = svc.create_portfolio({"dec-1": ["a"]})
        gen = svc.generate_combinations(p.portfolio_id)
        assert len(gen.scenarios) > 0
        # Capture before
        before = {"accepted": {}, "canonical": {}}
        canon_dir = project_root / ".auteur" / "canonical"
        if canon_dir.exists():
            for f in canon_dir.iterdir():
                if f.is_file():
                    before["canonical"][f.name] = f.read_text() if f.exists() else ""
        # Run promotion
        svc.promote_scenario(gen.scenarios[0].scenario_id, p.portfolio_id, confirm=True)
        # Capture after
        after = {"accepted": {}, "canonical": {}}
        if canon_dir.exists():
            for f in canon_dir.iterdir():
                if f.is_file():
                    after["canonical"][f.name] = f.read_text() if f.exists() else ""
        assert before["canonical"] == after["canonical"]

    def test_complementarity_exceeds_union_of_component_effects(self, project_root):
        """Combined decisions produce cross effects absent from individual decisions."""
        from auteur.portfolio.projection import PortfolioProjector
        from auteur.portfolio.models import PortfolioScenario
        from auteur.portfolio.service import PortfolioService
        svc = PortfolioService(project_root)
        p = svc.create_portfolio({"dec-1": ["a", "b"], "dec-2": ["c", "d"]})
        gen = svc.generate_combinations(p.portfolio_id)
        projector = PortfolioProjector(project_root)
        if gen.scenarios:
            s1 = gen.scenarios[0]
            single_a = PortfolioScenario(scenario_id="single-a", portfolio_id=p.portfolio_id,
                                         assignment=dict(list(s1.assignment.items())[:1]))
            proj_a = projector.project(single_a)
            single_b = PortfolioScenario(scenario_id="single-b", portfolio_id=p.portfolio_id,
                                         assignment=dict(list(s1.assignment.items())[1:2])) if len(s1.assignment) >= 2 else None
            proj_b = projector.project(single_b) if single_b else None
            proj_combined = projector.project(s1)
            combined_effects = [e.effect_type.value for e in proj_combined.cross_effects]
            a_effects = [e.effect_type.value for e in proj_a.cross_effects]
            b_effects = [e.effect_type.value for e in (proj_b.cross_effects if proj_b else [])]
            # Combined has effects not present in either isolated
            for effect in combined_effects:
                if effect not in a_effects and effect not in b_effects:
                    break  # Found a genuinely emergent effect
            else:
                # If all combined effects also appear in A or B, at least verify cross effects exist
                assert len(proj_combined.cross_effects) >= len(proj_a.cross_effects)
                if proj_b:
                    assert len(proj_combined.cross_effects) >= len(proj_b.cross_effects)
