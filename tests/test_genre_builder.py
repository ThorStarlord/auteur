from __future__ import annotations

import yaml

from auteur.genre_builder.builder import build_custom_genre_contract
from auteur.genre_builder.explainer import explain_custom_genre_contract
from auteur.genre_builder.models import CustomGenreContract
from auteur.genre_builder.parser import parse_genre_brief
from auteur.genre_builder.validation import validate_custom_genre_contract
from auteur.genres.registry import load_project_genre_contract


BRIEF = """# Genre
Cozy Political Fantasy

# Emotional Promise
The reader should feel that broken civic trust can be repaired through courage and cleverness.

# Core Truth
Communities can heal when power is made accountable.

# Required Tropes
- intimate political stakes
- community web
- restorative ending

# Optional Tropes
- magical bureaucracy
- festival council meeting

# Forbidden Mismatches
- nihilistic ending
- cruelty rewarded as wisdom

# Common Failures
- politics becomes exposition instead of pressure
- cozy tone removes real stakes

# Scope
minimum_viable_length: novella
default_length: novel
narrative_runway: medium
recommended_complexity: focused
mechanical_load: medium
worldbuilding_load: medium
cast_load: medium

# Setup Requirements
- show the community wound
- establish the trust network
"""


def test_structured_markdown_brief_compiles_into_stable_custom_contract() -> None:
    brief = parse_genre_brief(BRIEF)

    custom = build_custom_genre_contract(brief)

    assert custom.custom_genre_id == "cozy_political_fantasy"
    assert custom.base_genre == "other"
    assert custom.contract.genre_id.value == "other"
    assert custom.contract.display_name == "Cozy Political Fantasy"
    assert custom.contract.audience_product.startswith("The reader should feel")
    assert custom.contract.required_tropes == [
        "intimate political stakes",
        "community web",
        "restorative ending",
    ]
    assert custom.contract.scope_profile.default_length.value == "novel"
    assert custom.contract.setup_contract.minimum_setup_beats == [
        "show the community wound",
        "establish the trust network",
    ]


def test_missing_required_sections_produce_clear_diagnostics() -> None:
    brief = parse_genre_brief("# Genre\nThin Genre\n")

    diagnostics = brief.diagnostics

    assert "Missing required section: Emotional Promise" in diagnostics
    assert "Missing required section: Setup Requirements" in diagnostics


def test_custom_contract_validation_rejects_empty_trope_and_mismatch_contract() -> None:
    custom = build_custom_genre_contract(parse_genre_brief(BRIEF))
    broken_payload = custom.model_dump(mode="json")
    broken_payload["contract"]["required_tropes"] = []
    broken_payload["contract"]["forbidden_mismatches"] = []
    broken = CustomGenreContract.model_validate(broken_payload)

    diagnostics = validate_custom_genre_contract(broken)

    assert [diag.rule for diag in diagnostics] == ["genre_builder.empty_contract_constraints"]


def test_custom_contract_validation_rejects_unsafe_id() -> None:
    custom = build_custom_genre_contract(parse_genre_brief(BRIEF))
    broken = custom.model_copy(update={"custom_genre_id": "../bad"})

    diagnostics = validate_custom_genre_contract(broken)

    assert [diag.rule for diag in diagnostics] == ["genre_builder.unsafe_custom_genre_id"]


def test_explainer_uses_contract_language_not_prompt_template_language() -> None:
    custom = build_custom_genre_contract(parse_genre_brief(BRIEF))

    markdown = explain_custom_genre_contract(custom)

    assert "# Cozy Political Fantasy Genre Contract" in markdown
    assert "## Emotional Promise" in markdown
    assert "## Validation Checklist" in markdown
    assert "prompt template" not in markdown.lower()


def test_custom_contract_yaml_round_trip_and_project_lookup(tmp_path) -> None:
    project = tmp_path / "project"
    custom_dir = project / "genres" / "custom"
    custom_dir.mkdir(parents=True)
    custom = build_custom_genre_contract(parse_genre_brief(BRIEF))
    path = custom_dir / "cozy_political_fantasy.yaml"
    path.write_text(yaml.safe_dump(custom.model_dump(mode="json"), sort_keys=False), encoding="utf-8")

    loaded = load_project_genre_contract(project, "cozy_political_fantasy")

    assert loaded.display_name == "Cozy Political Fantasy"
    assert loaded.required_tropes[0] == "intimate political stakes"

