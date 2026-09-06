"""Deterministic composition of independent Story Design Packs."""
from __future__ import annotations

from .models import PackComposition, PackProvenance
from .registry import get_design_pack_registry


def compose_packs(pack_ids: list[str], *, version: str = "0.1.0") -> PackComposition:
    if not pack_ids:
        raise ValueError("At least one Story Design Pack is required")
    registry = get_design_pack_registry()
    selected = []
    packs = []
    for pack_id in dict.fromkeys(pack_ids):
        pack, digest = registry.get(pack_id, version)
        packs.append(pack)
        selected.append(PackProvenance(pack_id=pack.pack_id, version=pack.version, content_hash=digest))

    reinforcing: list[str] = []
    tensions: list[str] = []
    conflicts: list[str] = []
    questions: list[str] = []
    for pack in packs:
        for rule in pack.compatibility_rules:
            if rule.other_pack_id not in pack_ids:
                continue
            line = f"{pack.display_name} × {registry.get(rule.other_pack_id, version)[0].display_name}: {rule.statement}"
            target = {"reinforces": reinforcing, "tension": tensions, "incompatible": conflicts}[rule.relation]
            if line not in target:
                target.append(line)
            if rule.suggested_question and rule.suggested_question not in questions:
                questions.append(rule.suggested_question)

    hooks = []
    for pack in packs:
        for hook in pack.decision_hooks:
            if hook not in hooks:
                hooks.append(hook)
    return PackComposition(
        selected_packs=selected,
        applicable_design_priors=[option for pack in packs for option in pack.design_options],
        reinforcing_patterns=reinforcing,
        productive_tensions=tensions,
        actual_conflicts=conflicts,
        unresolved_questions=questions,
        decision_suggestions=hooks,
        pack_provenance=selected,
    )
