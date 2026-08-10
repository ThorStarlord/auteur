"""Regression tests for BUG #59: choose_k_of_n + per-alternative findings crash.

The consequence consumer's combination renderer previously crashed with
`TypeError: DecisionConsequence() got multiple values for keyword argument
'scope'` (the choose_k_of_n combination renderer inside build_consequences)
whenever a choose_k_of_n decision carried ANY per-alternative finding, because
`f.model_dump()` already contains the mutated `scope` key while
`scope="combination"` was passed as an explicit keyword.

Reproducer shape: frozen Case E (salt-of-the-earth-subplot-cut, choose_k_of_n
k=2) plus one authored default_reference targeting an alternative id.
"""
from __future__ import annotations

from pathlib import Path

import yaml as _yaml

from auteur.author_decisions import AuthorDecision, build_decision_context
from auteur.blueprint import StoryBlueprint
from auteur.identity import StoryIdentity

FIXTURES = Path(__file__).parent / "fixtures" / "author_decisions"
CASE_E = FIXTURES / "case-e"


def _decision_with_per_alternative_finding():
    """Frozen Case E artifact + one authored declared relationship targeting
    alternative `signe_marriage` (yields exactly one per-alternative finding)."""
    data = _yaml.safe_load((CASE_E / "salt-of-the-earth-subplot-cut.yaml").read_text(encoding="utf-8"))
    data.setdefault("default_references", []).append({
        "default_id": "contract.mandatory_ending_tone",
        "relates_to": "signe_marriage",
        "relationship": "conflicts_with",
    })
    return AuthorDecision.from_dict(data)


def _context(decision):
    identity = StoryIdentity.from_yaml(CASE_E / "story_identity.yaml")
    blueprint = StoryBlueprint.from_yaml(CASE_E / "blueprint.yaml")
    return build_decision_context(decision, identity, blueprint)


def test_choose_k_of_n_with_per_alternative_finding_renders_combinations():
    """Regression: evaluate must not crash; each combination carries the union
    of its member alternatives' findings."""
    ctx = _context(_decision_with_per_alternative_finding())
    report = ctx.build_report()
    consequences = report["consequences"]
    assert consequences["distinguishability"] == "SINGLE_AXIS"
    combos = consequences["combinations"]
    assert len(combos) == 3  # C(3,2)
    by_members = {tuple(c["combination"]): c["findings"] for c in combos}
    # signe_marriage is a member of two combinations -> each carries its finding
    assert len(by_members[("anders_debt", "signe_marriage")]) == 1
    assert len(by_members[("marta_pregnancy", "signe_marriage")]) == 1
    # shipped combination semantics: findings are re-scoped to the combination
    # (target = the combination tuple) and keep the member alternative's finding
    f = by_members[("anders_debt", "signe_marriage")][0]
    assert f["target"] == repr(("anders_debt", "signe_marriage"))
    assert f["scope"] == "combination"
    assert f["members"] == [f["target"]]
    # the combination without signe_marriage carries no per-alternative findings
    assert by_members[("anders_debt", "marta_pregnancy")] == []


def test_choose_k_of_n_without_per_alternative_finding_unchanged():
    """Frozen Case E (no per-alternative findings) keeps its shipped shape:
    3 combinations with empty findings, COMMON_ONLY."""
    ctx = _context(AuthorDecision.from_yaml(CASE_E / "salt-of-the-earth-subplot-cut.yaml"))
    report = ctx.build_report()
    consequences = report["consequences"]
    assert consequences["distinguishability"] == "COMMON_ONLY"
    assert all(c["findings"] == [] for c in consequences["combinations"])


def test_choose_k_of_n_one_finding_on_each_alternative():
    """Every alternative carrying a finding: each of the 3 combinations gets the
    union (2 findings); still renders without crashing."""
    data = _yaml.safe_load((CASE_E / "salt-of-the-earth-subplot-cut.yaml").read_text(encoding="utf-8"))
    for alt in ("anders_debt", "marta_pregnancy", "signe_marriage"):
        data.setdefault("default_references", []).append({
            "default_id": "contract.mandatory_ending_tone",
            "relates_to": alt,
            "relationship": "conflicts_with",
        })
    ctx = _context(AuthorDecision.from_dict(data))
    report = ctx.build_report()
    combos = report["consequences"]["combinations"]
    assert len(combos) == 3
    assert all(len(c["findings"]) == 2 for c in combos)
