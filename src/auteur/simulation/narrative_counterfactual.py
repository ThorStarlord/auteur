"""Small narrative overlay projections layered on existing simulation artifacts."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal


ConsequenceClass = Literal["KNOWN", "DERIVED", "INFERRED", "UNKNOWN"]


@dataclass(frozen=True)
class NarrativeConsequence:
    target: str
    description: str
    classification: ConsequenceClass
    evidence: tuple[str, ...] = ()


@dataclass(frozen=True)
class NarrativeCounterfactual:
    baseline_hash: str
    changed_fact: str
    consequences: tuple[NarrativeConsequence, ...] = ()
    preserved: tuple[str, ...] = ()
    unknowns: tuple[str, ...] = ()
    promoted: bool = False


def project_counterfactual(
    *, baseline_hash: str, changed_fact: str, direct_dependents: dict[str, list[str]], preserved: list[str]
) -> NarrativeCounterfactual:
    consequences: list[NarrativeConsequence] = []
    for target, evidence in sorted(direct_dependents.items()):
        consequences.append(NarrativeConsequence(
            target=target,
            description=f"{target} depends on the changed fact {changed_fact}.",
            classification="DERIVED",
            evidence=tuple(sorted(evidence)),
        ))
    return NarrativeCounterfactual(
        baseline_hash=baseline_hash,
        changed_fact=changed_fact,
        consequences=tuple(consequences),
        preserved=tuple(sorted(preserved)),
        unknowns=("Thematic interpretation requires author judgment.",),
    )
