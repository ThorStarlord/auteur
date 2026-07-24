"""Semantic comparison of counterfactual scenarios."""

from __future__ import annotations

from auteur.simulation.models import (
    ConfidenceLevel,
    ConsequenceCategory,
    CounterfactualScenario,
    ProjectedConsequence,
    ScenarioComparison,
    _stable_id,
)


class ScenarioComparator:
    """Compare two counterfactual scenarios.

    Identifies shared, unique, and opposing consequences.
    Never emits a winner or artistic recommendation.
    """

    def compare(
        self,
        scenario_a: CounterfactualScenario,
        scenario_b: CounterfactualScenario,
    ) -> ScenarioComparison:
        """Compare two scenarios semantically.

        Both scenarios should be in PROJECTED or COMPARABLE state.
        Baseline mismatch is detected and reported.
        """
        cid = _stable_id("compare", scenario_a.scenario_id, scenario_b.scenario_id)

        # Check baseline mismatch
        if scenario_a.baseline_id != scenario_b.baseline_id:
            return ScenarioComparison(
                comparison_id=cid,
                scenario_a_id=scenario_a.scenario_id,
                scenario_b_id=scenario_b.scenario_id,
                evidence_asymmetry=f"Baseline mismatch: {scenario_a.baseline_id[:12]}... vs {scenario_b.baseline_id[:12]}...",
                unknowns=["Baselines differ — direct comparison may be unreliable"],
            )

        # Group consequences by target
        a_by_target: dict[str, ProjectedConsequence] = {}
        for c in scenario_a.projected_consequences:
            a_by_target[c.target] = c

        b_by_target: dict[str, ProjectedConsequence] = {}
        for c in scenario_b.projected_consequences:
            b_by_target[c.target] = c

        all_targets = set(a_by_target.keys()) | set(b_by_target.keys())

        shared: list[ProjectedConsequence] = []
        a_only: list[ProjectedConsequence] = []
        b_only: list[ProjectedConsequence] = []
        opposing: list[tuple[ProjectedConsequence, ProjectedConsequence]] = []
        milestone_diffs: list[dict] = []
        unknowns: list[str] = []

        for target in sorted(all_targets):
            ca = a_by_target.get(target)
            cb = b_by_target.get(target)

            if ca and cb:
                if ca.description == cb.description:
                    shared.append(ca)
                else:
                    opposing.append((ca, cb))
            elif ca and not cb:
                a_only.append(ca)
            elif cb and not ca:
                b_only.append(cb)

        # Uncertainty asymmetry
        a_undetermined = sum(1 for c in scenario_a.projected_consequences
                             if c.confidence == ConfidenceLevel.UNDETERMINED)
        b_undetermined = sum(1 for c in scenario_b.projected_consequences
                             if c.confidence == ConfidenceLevel.UNDETERMINED)

        uncertainty_text = ""
        if a_undetermined > b_undetermined:
            uncertainty_text = f"Scenario A has {a_undetermined - b_undetermined} more undetermined consequences"
        elif b_undetermined > a_undetermined:
            uncertainty_text = f"Scenario B has {b_undetermined - a_undetermined} more undetermined consequences"

        # Evidence asymmetry
        evidence_text = ""
        a_known = sum(1 for c in scenario_a.projected_consequences
                      if c.classification == ConsequenceCategory.KNOWN)
        b_known = sum(1 for c in scenario_b.projected_consequences
                      if c.classification == ConsequenceCategory.KNOWN)
        if a_known > b_known:
            evidence_text = f"Scenario A has {a_known - b_known} more known consequences"
        elif b_known > a_known:
            evidence_text = f"Scenario B has {b_known - a_known} more known consequences"

        # Milestone differences from projected plans
        if scenario_a.projected_plan and scenario_b.projected_plan:
            pa = scenario_a.projected_plan
            pb = scenario_b.projected_plan
            if pa.open_decision_count != pb.open_decision_count:
                milestone_diffs.append({
                    "dimension": "open_decision_count",
                    "scenario_a": pa.open_decision_count,
                    "scenario_b": pb.open_decision_count,
                })
            if pa.blocked_milestone_count != pb.blocked_milestone_count:
                milestone_diffs.append({
                    "dimension": "blocked_milestone_count",
                    "scenario_a": pa.blocked_milestone_count,
                    "scenario_b": pb.blocked_milestone_count,
                })

        # Unknowns
        unknown_in_a = [c for c in scenario_a.projected_consequences
                        if c.classification == ConsequenceCategory.UNKNOWN]
        unknown_in_b = [c for c in scenario_b.projected_consequences
                        if c.classification == ConsequenceCategory.UNKNOWN]
        for c in unknown_in_a + unknown_in_b:
            if c.description not in unknowns:
                unknowns.append(c.description)

        return ScenarioComparison(
            comparison_id=cid,
            scenario_a_id=scenario_a.scenario_id,
            scenario_b_id=scenario_b.scenario_id,
            shared_consequences=shared,
            a_only_consequences=a_only,
            b_only_consequences=b_only,
            opposing_consequences=opposing,
            milestone_differences=milestone_diffs,
            evidence_asymmetry=evidence_text,
            uncertainty_asymmetry=uncertainty_text,
            unknowns=unknowns,
        )
