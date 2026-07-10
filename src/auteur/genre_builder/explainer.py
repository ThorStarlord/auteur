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
        "## What Auteur Will Validate",
        "- Required tropes are present in the declared story contract.",
        "- Forbidden mismatches are treated as contract risks.",
        "- Scope and setup expectations are available to diagnostics.",
        "",
        "## How This Genre Fails",
        *_bullets(contract.common_failure_modes),
        "",
        "## Suggested StoryIdentity Defaults",
        f"- Genre: {contract.genre_id.value}",
        f"- Target experience: {contract.audience_product or '-'}",
        f"- Engine bias: {', '.join(contract.default_engine_biases) if contract.default_engine_biases else 'derive from required tropes and core truth'}",
        "",
        "## Setup Contract",
        *_bullets(contract.setup_contract.minimum_setup_beats),
        "",
        "## Setup/Payoff Expectations",
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
