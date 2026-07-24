"""Constraint management for narrative decision portfolios."""

from __future__ import annotations

from auteur.portfolio.models import (
    ConstraintStrength,
    ConstraintType,
    ContradictionClass,
    PortfolioConstraint,
    _stable_id,
)


class ConstraintEngine:
    """Evaluate constraints against candidate combinations."""

    def check_incompatibility(
        self,
        assignment: dict[str, str],
        constraint: PortfolioConstraint,
    ) -> tuple[bool, str]:
        """Check if a constraint is violated by an assignment.

        Returns (is_valid, reason).
        """
        if constraint.strength != ConstraintStrength.HARD:
            return True, ""

        if constraint.constraint_type == ConstraintType.HARD_INCOMPATIBILITY:
            if self._candidates_present(assignment, constraint.source_candidates) and \
               self._candidates_present(assignment, constraint.target_candidates):
                return False, constraint.reason or "Hard incompatibility"

        elif constraint.constraint_type == ConstraintType.REQUIRES:
            if self._candidates_present(assignment, constraint.source_candidates) and not \
               self._candidates_present(assignment, constraint.target_candidates):
                return False, constraint.reason or "Requires condition not met"

        elif constraint.constraint_type == ConstraintType.MUTUALLY_EXCLUSIVE:
            present = []
            for c in constraint.source_candidates + constraint.target_candidates:
                if c in assignment.values():
                    present.append(c)
            if len(present) >= 2:
                return False, constraint.reason or "Mutually exclusive candidates"

        return True, ""

    def check_soft_tension(
        self,
        assignment: dict[str, str],
        constraint: PortfolioConstraint,
    ) -> tuple[bool, str]:
        """Check soft tension without excluding the combination."""
        if constraint.constraint_type == ConstraintType.SOFT_TENSION:
            if self._candidates_present(assignment, constraint.source_candidates) and \
               self._candidates_present(assignment, constraint.target_candidates):
                return True, constraint.reason or "Soft tension present"
        return False, ""

    def classify_contradiction(
        self, assignment: dict[str, str],
        constraints: list[PortfolioConstraint],
    ) -> tuple[ContradictionClass | None, str]:
        """Classify the contradiction level of an assignment."""
        for c in constraints:
            valid, reason = self.check_incompatibility(assignment, c)
            if not valid:
                return ContradictionClass.HARD_CONTRADICTION, reason
        for c in constraints:
            has_tension, reason = self.check_soft_tension(assignment, c)
            if has_tension:
                return ContradictionClass.SOFT_TENSION, reason
        return None, ""

    def _candidates_present(
        self, assignment: dict[str, str], candidates: list[str],
    ) -> bool:
        """Check if any of the given candidates appear in the assignment."""
        assigned = set(assignment.values())
        return bool(set(candidates) & assigned)
