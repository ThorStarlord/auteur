"""Deterministic propagation rules for impact analysis.

Each rule is a function that takes (source_artifact_type, target_artifact_type,
change_type) and returns an ImpactSeverity and reason string.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from auteur.impact.models import ChangeType, ImpactSeverity


@dataclass(frozen=True)
class PropagationRule:
    rule_id: str
    description: str
    match_fn: Callable[[str, str, str], tuple[ImpactSeverity, str] | None]


def _rule(rule_id: str, description: str, source_types: tuple[str, ...],
          target_types: tuple[str, ...],
          change_types: tuple[str, ...] | None = None,
          severity: ImpactSeverity = ImpactSeverity.REVIEW,
          reason_template: str = "") -> PropagationRule:

    def _match(src_type: str, tgt_type: str, chg_type: str) -> tuple[ImpactSeverity, str] | None:
        if src_type not in source_types and source_types:
            return None
        if tgt_type not in target_types and target_types:
            return None
        if change_types and chg_type not in change_types:
            return None
        reason = reason_template.format(src=src_type, tgt=tgt_type, chg=chg_type)
        return severity, reason

    return PropagationRule(rule_id=rule_id, description=description, match_fn=_match)


RULES: list[PropagationRule] = [
    # R001: Identity changed → Structure
    _rule("R001", "Identity change affects structure",
          ("story_identity",), ("blueprint", "structure"),
          severity=ImpactSeverity.RECONCILE,
          reason_template="Identity changed; structure must be reconciled"),

    # R002: Structure changed → Chapter outline
    _rule("R002", "Structure change affects chapter outlines",
          ("blueprint", "structure"), ("chapter_outline",),
          severity=ImpactSeverity.RECONCILE,
          reason_template="Structure changed; chapter outlines need reconciliation"),

    # R003: Chapter outline changed → Scene realization
    _rule("R003", "Chapter outline change affects scene realizations",
          ("chapter_outline",), ("scene_realization",),
          severity=ImpactSeverity.RECONCILE,
          reason_template="Outline changed; scene realizations need reconciliation"),

    # R004: Scene realization changed → Scene expression
    _rule("R004", "Realization change affects scene expressions",
          ("scene_realization",), ("scene_expression",),
          severity=ImpactSeverity.REGENERATE_CANDIDATE,
          reason_template="Realization changed; scene expression should be regenerated"),

    # R005: Scene expression changed → Chapter expression
    _rule("R005", "Scene expression change affects chapter expression",
          ("scene_expression",), ("chapter_expression",),
          severity=ImpactSeverity.REGENERATE_CANDIDATE,
          reason_template="Scene expression changed; chapter expression needs regeneration"),

    # R006: Chapter expression changed → Book expression
    _rule("R006", "Chapter expression change affects book expression",
          ("chapter_expression",), ("book_expression",),
          severity=ImpactSeverity.REGENERATE_CANDIDATE,
          reason_template="Chapter expression changed; book expression needs regeneration"),

    # R007: Book expression changed → Published outputs
    _rule("R007", "Book expression change affects published outputs",
          ("book_expression",), ("published_output",),
          severity=ImpactSeverity.BLOCKED,
          reason_template="Book expression changed; publishing is blocked until resolved"),

    # R008: Any upstream change → Reasoning review (stale)
    _rule("R008", "Upstream change stales reasoning review",
          ("chapter_outline", "scene_realization", "scene_expression", "chapter_expression"),
          ("reasoning_review",),
          severity=ImpactSeverity.BLOCKED,
          reason_template="{src} changed; reasoning review is stale and BLOCKED"),

    # R009: Changed accepted chapter → Book assembly
    _rule("R009", "Accepted chapter change affects book assembly",
          ("accepted_chapter",), ("book_assembly",),
          severity=ImpactSeverity.REGENERATE_CANDIDATE,
          reason_template="Accepted chapter changed; book assembly needs regeneration"),

    # R010: Changed chapter expression → Reconciliation result
    _rule("R010", "Chapter expression change affects reconciliation",
          ("chapter_expression",), ("reconciliation_result",),
          severity=ImpactSeverity.REVIEW,
          reason_template="Chapter expression changed; reconciliation result needs review"),

    # R011: Changed book assembly → Published outputs
    _rule("R011", "Book assembly change affects published outputs",
          ("book_assembly",), ("published_output",),
          severity=ImpactSeverity.REGENERATE_CANDIDATE,
          reason_template="Book assembly changed; published outputs need regeneration"),

    # R012: Adjacent chapter → Continuity review
    _rule("R012", "Adjacent chapter change affects next chapter opening",
          ("chapter_outline",), ("chapter_outline",),
          severity=ImpactSeverity.REVIEW,
          reason_template="Adjacent outline changed; next chapter opening should be reviewed"),

    # R016: Accepted artifact with same content → Preserve
    _rule("R016", "Accepted artifact unchanged content preserves",
          (), (),
          change_types=("none",),
          severity=ImpactSeverity.NONE,
          reason_template="Artifact unchanged; no impact"),

    # R017: Accepted artifact with upstream changed → Reconcile
    _rule("R017", "Accepted artifact needs reconciliation when upstream changed",
          (), ("accepted_chapter", "chapter_expression", "book_expression"),
          severity=ImpactSeverity.RECONCILE,
          reason_template="Accepted artifact's upstream changed; needs reconciliation"),
]


def match_rule(src_type: str, tgt_type: str, change_type: str) -> list[tuple[str, ImpactSeverity, str]]:
    """Find all matching rules and return (rule_id, severity, reason) tuples."""
    results: list[tuple[str, ImpactSeverity, str]] = []
    for rule in RULES:
        match = rule.match_fn(src_type, tgt_type, change_type)
        if match is not None:
            severity, reason = match
            results.append((rule.rule_id, severity, reason))
    return results


# Non-rule severity combination: pick the highest severity
SEVERITY_ORDER = [
    ImpactSeverity.NONE,
    ImpactSeverity.REVIEW,
    ImpactSeverity.RECONCILE,
    ImpactSeverity.REGENERATE_CANDIDATE,
    ImpactSeverity.BLOCKED,
]


def highest_severity(severities: list[ImpactSeverity]) -> ImpactSeverity:
    """Return the highest severity from a list."""
    best = ImpactSeverity.NONE
    for s in severities:
        if SEVERITY_ORDER.index(s) > SEVERITY_ORDER.index(best):
            best = s
    return best
