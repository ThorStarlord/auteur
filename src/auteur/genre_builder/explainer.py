from __future__ import annotations

from auteur.genre_builder.models import CustomGenreContract


def explain_custom_genre_contract(custom: CustomGenreContract) -> str:
    contract = custom.contract
    lines = [
        f"# {contract.display_name} Genre Contract",
        "",
        "## Emotional Promise",
        contract.audience_product or "-",
        "",
        "## Core Truth",
        contract.core_truth or "-",
        "",
        "## Required Tropes",
        *_bullets(contract.required_tropes),
        "",
        "## Forbidden Mismatches",
        *_bullets(contract.forbidden_mismatches),
        "",
        "## Scope Profile",
        f"- Minimum viable length: {contract.scope_profile.minimum_viable_length.value}",
        f"- Default length: {contract.scope_profile.default_length.value}",
        f"- Narrative runway: {contract.scope_profile.narrative_runway.value}",
        f"- Recommended complexity: {contract.scope_profile.recommended_complexity.value}",
        "",
        "## Setup Contract",
        *_bullets(contract.setup_contract.minimum_setup_beats),
        "",
        "## Common Failure Modes",
        *_bullets(contract.common_failure_modes),
        "",
        "## Validation Checklist",
        "- Required tropes or forbidden mismatches are present.",
        "- Setup requirements are present.",
        "- Scope values use Auteur contract vocabulary.",
    ]
    return "\n".join(lines) + "\n"


def _bullets(items: list[str]) -> list[str]:
    return [f"- {item}" for item in items] if items else ["-"]

