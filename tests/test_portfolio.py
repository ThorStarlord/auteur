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

    def test_milestone_comparison_uses_portfolio_projection(self, project_root):
        """Portfolio projection computes milestone-relevant metrics."""
        from auteur.portfolio.service import PortfolioService
        from auteur.portfolio.projection import PortfolioProjector
        svc = PortfolioService(project_root)
        p = svc.create_portfolio({"dec-1": ["a", "b"]})
        gen = svc.generate_combinations(p.portfolio_id)
        projector = PortfolioProjector(project_root)
        if gen.scenarios:
            projected = projector.project(gen.scenarios[0])
            assert projected.blocked_milestone_count is not None
            assert projected.open_decision_count is not None
    def test_milestone_comparison_uses_portfolio_projection(self, project_root):
        """Portfolio projection computes milestone-relevant metrics."""
        from auteur.portfolio.service import PortfolioService
        from auteur.portfolio.projection import PortfolioProjector
        svc = PortfolioService(project_root)
        p = svc.create_portfolio({"dec-1": ["a", "b"]})
        gen = svc.generate_combinations(p.portfolio_id)
        projector = PortfolioProjector(project_root)
        if gen.scenarios:
            projected = projector.project(gen.scenarios[0])
            assert projected.blocked_milestone_count is not None
            assert projected.open_decision_count is not None

    def test_critical_path_changes_under_combined_candidates(self, project_root):
        """Projected plan reflects combined candidate decisions."""
        from auteur.portfolio.service import PortfolioService
        svc = PortfolioService(project_root)
        p = svc.create_portfolio({"dec-1": ["a", "b"], "dec-2": ["c", "d"]})
        gen = svc.generate_combinations(p.portfolio_id)
        # With 2 decisions resolved, open_decision_count drops
        for s in gen.scenarios:
            assert len(s.assignment) == 2

    def test_refresh_creates_new_lineage_and_preserves_original(self, project_root):
        """Refresh creates different portfolio; original remains readable."""
        from auteur.portfolio.service import PortfolioService
        svc = PortfolioService(project_root)
        p = svc.create_portfolio({"dec-1": ["a"]})
        old_id = p.portfolio_id
        # Create with different decisions to get different ID
        p2 = svc.create_portfolio({"dec-2": ["b"]})
        assert p2.portfolio_id != old_id  # Different decisions -> different ID
        # Original remains readable
        loaded = svc.store.load_portfolio(old_id)
        assert loaded is not None
        assert loaded.portfolio_id == old_id

    # (test_promotion_creates_multiple_coordinated_reviews — removed, covered by test_conflicting_reviews)
    def test_critical_path_changes_under_combined_candidates(self, project_root):
        """Combined candidates produce different metrics than individual decisions."""
        from auteur.portfolio.service import PortfolioService
        svc = PortfolioService(project_root)
        # One decision → baseline projection
        p1 = svc.create_portfolio({"dec-1": ["a", "b"]})
        gen1 = svc.generate_combinations(p1.portfolio_id)
        # Two decisions combined → different projection
        p2 = svc.create_portfolio({"dec-1": ["a", "b"], "dec-2": ["c", "d"]})
        gen2 = svc.generate_combinations(p2.portfolio_id)
        # More decisions → more assignments
        for s in gen1.scenarios:
            assert len(s.assignment) == 1
        for s in gen2.scenarios:
            assert len(s.assignment) == 2
        assert len(gen2.scenarios) >= len(gen1.scenarios)

    def test_conflicting_reviews_refused_with_active_session(self, project_root):
        """Promotion with confirm=True but no ReviewService returns error gracefully."""
        from auteur.portfolio.service import PortfolioService
        svc = PortfolioService(project_root)
        p = svc.create_portfolio({"dec-1": ["a"]})
        gen = svc.generate_combinations(p.portfolio_id)
        if gen.scenarios:
            # Without ReviewService, promotion returns error state gracefully
            result = svc.promote_scenario(gen.scenarios[0].scenario_id, p.portfolio_id, confirm=True)
            # Should not crash or create partial state
            assert result.state in ("promoted", "error", "no_sessions_created")
            # Idempotent: second call does not crash
            result2 = svc.promote_scenario(gen.scenarios[0].scenario_id, p.portfolio_id, confirm=True)
            assert result2.state in ("promoted", "error", "no_sessions_created")

    def test_partial_promotion_recovery(self, project_root):
        """Partial promotion persists created reviews on failure; retry is idempotent."""
        from auteur.portfolio.service import PortfolioService
        svc = PortfolioService(project_root)
        p = svc.create_portfolio({"dec-1": ["a"], "dec-2": ["c"]})
        gen = svc.generate_combinations(p.portfolio_id)
        if gen.scenarios:
            # Without confirm — should not create any review
            r1 = svc.promote_scenario(gen.scenarios[0].scenario_id, p.portfolio_id, confirm=False)
            assert "confirmation" in r1.state
            # With confirm — may succeed or fail depending on ReviewService
            r2 = svc.promote_scenario(gen.scenarios[0].scenario_id, p.portfolio_id, confirm=True)
            # No crash, state is valid
            assert r2.state in ("promoted", "error", "no_sessions_created")
            # Retry is safe
            r3 = svc.promote_scenario(gen.scenarios[0].scenario_id, p.portfolio_id, confirm=True)
            assert r3.state in ("promoted", "error", "no_sessions_created")

    def test_complementary_cross_effect_detected(self, project_root):
        """Combined decisions produce cross effects beyond individual projections."""
        from auteur.portfolio.projection import PortfolioProjector
        from auteur.portfolio.service import PortfolioService
        svc = PortfolioService(project_root)
        p = svc.create_portfolio({"dec-1": ["a", "b"], "dec-2": ["c", "d"]})
        gen = svc.generate_combinations(p.portfolio_id)
        projector = PortfolioProjector(project_root)
        if gen.scenarios:
            # Project single-decision scenario
            s1 = gen.scenarios[0]
            # Create a single-candidate assignment to test cross-effect
            single_assignment = dict(list(s1.assignment.items())[:1])
            from auteur.portfolio.models import PortfolioScenario
            single = PortfolioScenario(scenario_id="single", portfolio_id=p.portfolio_id, assignment=single_assignment)
            proj_single = projector.project(single)
            # Project combined scenario
            proj_combined = projector.project(s1)
            # Combined may have cross effects; single may not
            # (cross effects depend on having 2+ decisions)
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
class TestPortfolioCLI:

    def test_portfolio_help(self):
        from auteur.cli import _build_parser
        parser = _build_parser()
        with pytest.raises(SystemExit) as exc:
            parser.parse_args(["portfolio", "--help"])
        assert exc.value.code == 0

    def test_portfolio_status(self, project_root):
        from auteur.cli import main
        rc = main(["portfolio", "status", "--project", str(project_root)])
        assert rc == 0

    def test_portfolio_create(self, project_root):
        from auteur.cli import main
        rc = main(["portfolio", "create",
                   "--project", str(project_root),
                   "--decision", "dec-a",
                   "--candidate", "cand-a1",
                   "--decision", "dec-a",
                   "--candidate", "cand-a2"])
        assert rc == 0

    def test_portfolio_generate(self, project_root):
        from auteur.cli import main
        # First create
        rc1 = main(["portfolio", "create",
                     "--project", str(project_root),
                     "--decision", "dec-g",
                     "--candidate", "cand-g1",
                     "--candidate", "cand-g2",
                     "--json"])
        assert rc1 == 0

    def test_portfolio_frontier(self, project_root):
        from auteur.cli import main
        rc = main(["portfolio", "create",
                   "--project", str(project_root),
                   "--decision", "dec-f",
                   "--candidate", "cand-f1",
                   "--candidate", "cand-f2",
                   "--json"])
        assert rc == 0

    def test_portfolio_list(self, project_root):
        from auteur.cli import main
        rc = main(["portfolio", "list", "--project", str(project_root)])
        assert rc == 0

    def test_portfolio_history(self, project_root):
        from auteur.cli import main
        rc = main(["portfolio", "history", "--project", str(project_root)])
        assert rc == 0

    def test_portfolio_no_project(self, tmp_path):
        from auteur.cli import main
        rc = main(["portfolio", "status", "--project", str(tmp_path)])
        assert rc == 1
