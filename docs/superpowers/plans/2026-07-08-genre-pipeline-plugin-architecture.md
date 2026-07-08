# Genre Pipeline Plugin Architecture Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Refactor auteur to treat genres as first-class plugins. Eliminate hardcoded netorare fallbacks. Make genre pipeline specs the architectural foundation. Prove that netorare, mystery, and gentlefemdom can all be implemented as equivalent plugins without special-casing in shared infrastructure.

**Architecture:** Six-phase progression from immediate semantic leaks to a scalable genre registry:
1. Fix identity generator to consume template emotional data
2. Replace ID-to-prose fallback with template label lookups
3. Create gentlefemdom genre contract YAML
4. Introduce `GenrePipelineSpec` registry (key architectural shift)
5. Wire CLI dispatcher and register all three genres
6. Add semantic regression tests proving emotional intent preservation

**Tech Stack:** Python 3.11+, Pydantic, YAML, pytest

## Global Constraints

- Exact file paths: Create under `src/auteur/genres/` for registry/contracts; modify existing files per phase
- Zero regressions: All 930 existing tests must still pass
- Semantic preservation: Each genre core must produce identity matching template.primary_emotion
- First-class plugins: Netorare, mystery, gentlefemdom all use same registry (no special cases in shared code)
- Test target: 50+ new tests across all phases
- CLI completeness: All three genres must be runnable via `auteur {genre} init`

---

## Phase 1: Fix Identity Generator to Consume Template Emotional Data

**Goal:** Make template.primary_emotion the source of truth (not fallback hardcoded maps).

**Files:**
- Modify: `src/auteur/netorare/identity_generator.py`
- Create: `tests/phase1/test_template_emotional_source_of_truth.py`

**Interfaces:**
- Consumes: `CoreTemplate` objects with `primary_emotion`, `title_seeds`, `emotion_progression`, etc.
- Produces: `IdentityGenerator.from_choices()` now uses template data, not hardcoded maps
- Later phases will depend on this

### Step 1: Write failing tests for template-as-source-of-truth

- [ ] Create `tests/phase1/test_template_emotional_source_of_truth.py`

```python
"""Tests: template emotional data flows to identity."""

import pytest
from auteur.netorare.identity_generator import IdentityGenerator
from auteur.gentlefemdom.core_templates import get_template


class TestTemplateEmotionalPreservation:
    """Verify template.primary_emotion becomes identity.target_experience.primary."""

    def test_sensual_dominance_primary_from_template(self):
        """Sensual dominance identity has template's primary_emotion, not dread."""
        choices = {4: {"want": "want-establish-trust", ...}}
        identity = IdentityGenerator.from_choices("sensual_dominance", choices)
        template = get_template("sensual_dominance")
        assert identity.target_experience.primary == template.primary_emotion
        assert identity.target_experience.primary == "playful_control"
        assert identity.target_experience.primary != "dread"

    def test_template_progression_used(self):
        """Identity progression matches template, not hardcoded fallback."""
        choices = {4: {...}}
        identity = IdentityGenerator.from_choices("sensual_dominance", choices)
        template = get_template("sensual_dominance")
        # Template progression should appear in identity, not generic "tension -> escalation -> climax"
        assert template.primary_emotion in identity.target_experience.progression or \
               any(word in identity.target_experience.progression.lower() for word in ["playful", "teasing", "connection"])

    def test_title_uses_template_seeds_not_fallback(self):
        """Identity title comes from template seeds, not generic "The Story"."""
        choices = {4: {...}}
        identity = IdentityGenerator.from_choices("sensual_dominance", choices)
        # Should not be the fallback "The Story"
        assert identity.title != "The Story"
        # Should reference something from the core/choices
        assert len(identity.title) > 9

    def test_all_three_cores_preserve_emotion(self):
        """All three gentlefemdom cores preserve their distinct emotions."""
        test_cases = [
            ("sensual_dominance", "playful_control"),
            ("tender_surrender", "safe_vulnerability"),
            ("romantic_authority", "cherished_leadership"),
        ]
        for core_id, expected_emotion in test_cases:
            choices = valid_choices_for(core_id)
            identity = IdentityGenerator.from_choices(core_id, choices)
            assert identity.target_experience.primary == expected_emotion
            assert identity.target_experience.primary != "dread"
```

Run: `pytest tests/phase1/test_template_emotional_source_of_truth.py -v`
Expected: FAIL (tests not implemented yet)

### Step 2: Modify IdentityGenerator to get primary_emotion from template

- [ ] Read `src/auteur/netorare/identity_generator.py` current `from_choices()` implementation
- [ ] Locate where `_get_primary_emotion()` is called
- [ ] Replace:

```python
# OLD:
emotion_map = {
    "classic_humiliation": "humiliation",
    "horror": "dread",
    "mystery": "dread",
}
primary = emotion_map.get(core_id, "dread")

# NEW:
try:
    template = get_template(core_id)
    primary = template.primary_emotion
except (ImportError, ValueError):
    # Fallback for unknown cores (safety)
    primary = "unknown"
```

Same for progression, title, and open_questions — consume from template instead of hardcoded maps.

### Step 3: Run failing tests again (should now pass)

- [ ] `pytest tests/phase1/ -v`
Expected: All 4+ tests PASS

### Step 4: Run full suite (verify no regressions)

- [ ] `pytest tests/ -q`
Expected: 930+ tests pass, zero regressions

### Step 5: Commit Phase 1

- [ ] Commit: "refactor: make template emotional data source of truth in identity generator"

---

## Phase 2: Replace Fallback Prose Generation with Template Label Lookups

**Goal:** Use template option labels instead of ID-to-readable slug conversion.

**Files:**
- Modify: `src/auteur/netorare/identity_generator.py` (extend `_readable_from_id()`)
- Modify: `src/auteur/netorare/identity.py` (if needed for better hooks)
- Create: `tests/phase2/test_template_label_aware_prose.py`

**Interfaces:**
- Consumes: `CoreTemplate` with `get_option_label(phase, field, option_id)` method
- Produces: Identity prose (want/resistance/conflict/stakes/change) now uses real labels
- Later phases will integrate genre contracts

### Step 1: Write tests for label-aware prose generation

- [ ] Create `tests/phase2/test_template_label_aware_prose.py`

```python
"""Tests: identity prose uses template labels, not ID-to-readable conversion."""

import pytest
from auteur.netorare.identity_generator import IdentityGenerator
from auteur.gentlefemdom.core_templates import get_template


class TestLabelAwareProseGeneration:
    """Verify generated prose uses template labels, not mechanical slug-splitting."""

    def test_want_field_uses_label_not_slug(self):
        """want field in central_engine uses template label, not slug."""
        choices = {4: {"want": "want-establish-trust", ...}}
        identity = IdentityGenerator.from_choices("sensual_dominance", choices)
        template = get_template("sensual_dominance")
        
        # Get the label from template
        want_label = template.get_options(4)["want"][0].label  # First option has label
        # Or look it up via option_id
        
        # central_engine.want should use that label, not "want establish trust"
        assert identity.central_engine.want == want_label or "Establish trust" in identity.central_engine.want

    def test_resistance_field_uses_label(self):
        """resistance uses template label."""
        choices = {4: {..., "resistance": "resistance-partner-doubt"}}
        identity = IdentityGenerator.from_choices("sensual_dominance", choices)
        # Should not be "resistance partner doubt"
        # Should be something like "Partner's doubt about surrendering"
        assert "doubt" in identity.central_engine.resistance.lower()
        assert "partner" in identity.central_engine.resistance.lower()

    def test_conflict_prose_includes_emotional_context(self):
        """conflict description includes emotion-aware phrasing from template."""
        choices = {4: {"conflict": "conflict-control-vs-consent"}}
        identity = IdentityGenerator.from_choices("sensual_dominance", choices)
        # Should reference playful_control or sensual/consent concepts, not generic phrasing
        assert "control" in identity.central_engine.conflict.lower() and "consent" in identity.central_engine.conflict.lower()

    def test_all_five_forces_use_labels(self):
        """All five forces (want/resistance/conflict/stakes/change) use labels."""
        choices = valid_choices_for("sensual_dominance")
        identity = IdentityGenerator.from_choices("sensual_dominance", choices)
        
        template = get_template("sensual_dominance")
        
        # Each field should have richer prose than mechanical ID-splitting
        for field in ["want", "resistance", "conflict", "stakes", "change"]:
            prose = getattr(identity.central_engine, field)
            # Should be at least somewhat descriptive
            assert len(prose) > 15
            assert not prose.startswith(field.capitalize())  # Not just "Want establish trust"
```

Run: `pytest tests/phase2/test_template_label_aware_prose.py -v`
Expected: FAIL (not implemented)

### Step 2: Extend CoreTemplate API with label lookup

- [ ] Modify `src/auteur/gentlefemdom/core_templates.py` (and netorare, mystery equivalents)
- [ ] Add method to CoreTemplate:

```python
def get_option_label(self, phase: int, field_or_section: str, option_id: str) -> str:
    """Get human-readable label for an option.
    
    Args:
        phase: Phase number
        field_or_section: Field name within that phase (e.g., "want", "resistance")
        option_id: The option's ID (e.g., "want-establish-trust")
    
    Returns:
        Label string (e.g., "Establish trust through demonstrated leadership")
    """
    # Implementation: search phase options, find option_id, return label
```

### Step 3: Update IdentityGenerator to use labels

- [ ] In `IdentityGenerator._readable_from_id()` or create new method `_get_label_from_template()`:

```python
def _get_label_from_template(self, template, phase: int, field: str, option_id: str) -> str:
    """Get label from template instead of converting ID to readable."""
    try:
        return template.get_option_label(phase, field, option_id)
    except (KeyError, AttributeError):
        # Fallback to old ID-to-readable conversion for safety
        return self._readable_from_id(option_id)
```

- [ ] Update central_engine population to use labels:

```python
# Instead of:
identity.central_engine.want = self._readable_from_id(want_id)

# Do:
identity.central_engine.want = self._get_label_from_template(template, 4, "want", want_id)
```

### Step 4: Run Phase 2 tests

- [ ] `pytest tests/phase2/ -v`
Expected: All tests PASS

### Step 5: Full suite

- [ ] `pytest tests/ -q`
Expected: 930+ passing, zero regressions

### Step 6: Commit Phase 2

- [ ] Commit: "refactor: use template labels for central engine prose generation"

---

## Phase 3: Create Gentlefemdom Genre Contract YAML

**Goal:** Encode gentlefemdom's emotional and narrative non-negotiables as a contract file.

**Files:**
- Create: `src/auteur/genres/data/gentlefemdom.yaml`
- Create: `tests/phase3/test_gentlefemdom_contract_loading.py`

**Interfaces:**
- Produces: `gentlefemdom.yaml` with contract that overrides fallbacks
- Later phases will load and use this

### Step 1: Write test for contract loading

- [ ] Create `tests/phase3/test_gentlefemdom_contract_loading.py`

```python
"""Tests: gentlefemdom genre contract loads and provides expected structure."""

import pytest
from auteur.genres.registry import load_genre_contract
from auteur.blueprint import Genre


class TestGentlefemdomContract:
    """Verify gentlefemdom contract is non-generic and loads correctly."""

    def test_gentlefemdom_contract_loads(self):
        """Genre contract for gentlefemdom loads without fallback."""
        contract = load_genre_contract(Genre.GENTLEFEMDOM)
        assert contract is not None
        # Should not be the fallback generic contract
        assert "Actions have consequences" not in contract.core_truth

    def test_contract_has_consent_non_negotiable(self):
        """Contract explicitly requires consent clarity."""
        contract = load_genre_contract(Genre.GENTLEFEMDOM)
        core_truth = contract.core_truth.lower()
        assert "consent" in core_truth

    def test_contract_forbids_coercion(self):
        """Contract lists coercion in forbidden mismatches."""
        contract = load_genre_contract(Genre.GENTLEFEMDOM)
        forbidden = [m.lower() for m in contract.common_failure_modes]
        assert any("coercion" in m or "force" in m for m in forbidden)

    def test_contract_requires_care(self):
        """Contract requires care/safety as central."""
        contract = load_genre_contract(Genre.GENTLEFEMDOM)
        core_truth = contract.core_truth.lower()
        assert "care" in core_truth or "safety" in core_truth or "trust" in core_truth
```

Run: `pytest tests/phase3/ -v`
Expected: FAIL (contract file doesn't exist)

### Step 2: Create gentlefemdom.yaml contract

- [ ] Create directory: `src/auteur/genres/data/`
- [ ] Create file: `src/auteur/genres/data/gentlefemdom.yaml`

Content (based on design spec):

```yaml
genre_id: gentlefemdom
display_name: Gentle Femdom
core_truth: |
  Power is a language for intimacy. Consent is explicit and enthusiastic.
  Care is central. Vulnerability is honored, not exploited.
audience_product: "Intimate trust deepened through power exchange."

primary_excitement_beats:
  - inciting_incident: "introduction of power dynamic"
  - rising_action: "consent/negotiation and boundary-setting"
  - climax: "vulnerable moment of trust/release"
  - resolution: "transformed relationship, deepened intimacy"

required_tropes:
  - "enthusiastic_consent"
  - "explicit_communication_about_boundaries"
  - "care_and_emotional_safety"
  - "aftercare_or_vulnerability_check_in"

forbidden_mismatches:
  - "coercion_or_manipulation"
  - "non_consent_treated_as_arousal"
  - "humiliation_without_negotiation"
  - "control_without_care"
  - "power_dynamic_presented_as_abuse"

common_failure_modes:
  - "consent_assumed_rather_than_stated"
  - "care_missing_in_power_exchange"
  - "vulnerability_treated_as_weakness_to_exploit"
  - "power_dynamic_mistaken_for_relationship_inequality"

psychology_budget:
  level: "functional_plus"
  reason: "Emotional depth essential for depicting trust and vulnerability realistically."
  motivation_clarity: "required"
  psychological_depth: "encouraged"
  character_texture: "required"

scope_profile:
  natural_lengths:
    - "novella"
    - "novel"
  minimum_viable_length: "short_story"
  default_length: "novel"
  narrative_runway: "medium_to_long"
  recommended_complexity: "character_focus"

setup_contract:
  emotional_runway: "medium_to_long"
  relationship_establishment: "required"
  baseline_world_establishment: "optional"
  minimum_setup_beats:
    - "Establish protagonist's emotional baseline and defenses"
    - "Introduce potential partner/dominant"
    - "First power dynamic moment (charged but unclear intent)"
  forbidden_shortcuts:
    - "Jumping to explicit scenes without consent negotiation"
    - "Portraying vulnerability as invitation to exploit"
```

### Step 3: Run Phase 3 tests

- [ ] `pytest tests/phase3/ -v`
Expected: Tests PASS (contract now loads)

### Step 4: Full suite

- [ ] `pytest tests/ -q`
Expected: 930+ passing

### Step 5: Commit Phase 3

- [ ] Commit: "feat(gentlefemdom): add genre contract YAML encoding narrative non-negotiables"

---

## Phase 4: Introduce GenrePipelineSpec Registry (Architectural Shift)

**Goal:** Make genres first-class plugins. Eliminate hardcoded branches in shared code.

**Files:**
- Create: `src/auteur/genres/registry.py`
- Create: `src/auteur/genres/__init__.py`
- Create: `tests/phase4/test_genre_pipeline_registry.py`

**Interfaces:**
- Produces: `GenrePipelineSpec` dataclass and registry
- Later phases will use registry to dispatch

### Step 1: Design and write registry interface tests

- [ ] Create `tests/phase4/test_genre_pipeline_registry.py`

```python
"""Tests: genre pipeline registry allows third-party genre implementations."""

import pytest
from auteur.genres.registry import (
    GenrePipelineSpec,
    register_genre,
    get_genre_pipeline,
    get_all_genres,
)
from auteur.blueprint import Genre


class TestGenrePipelineRegistry:
    """Verify registry treats all genres as equivalent."""

    def test_registry_returns_all_three_genres(self):
        """Registry returns specs for netorare, mystery, gentlefemdom."""
        genres = get_all_genres()
        assert len(genres) >= 3
        genre_ids = [g.genre for g in genres]
        assert Genre.NETORARE in genre_ids
        assert Genre.MYSTERY in genre_ids
        assert Genre.GENTLEFEMDOM in genre_ids

    def test_get_genre_pipeline_netorare(self):
        """Get netorare spec from registry."""
        spec = get_genre_pipeline(Genre.NETORARE)
        assert spec.genre == Genre.NETORARE
        assert spec.slug == "netorare"
        assert "classic_humiliation" in spec.core_ids
        assert "horror" in spec.core_ids

    def test_get_genre_pipeline_gentlefemdom(self):
        """Get gentlefemdom spec from registry."""
        spec = get_genre_pipeline(Genre.GENTLEFEMDOM)
        assert spec.genre == Genre.GENTLEFEMDOM
        assert spec.slug == "gentlefemdom"
        assert "sensual_dominance" in spec.core_ids
        assert "tender_surrender" in spec.core_ids
        assert "romantic_authority" in spec.core_ids

    def test_spec_has_template_factory(self):
        """Each spec has factory for creating templates."""
        spec = get_genre_pipeline(Genre.GENTLEFEMDOM)
        template = spec.template_factory("sensual_dominance")
        assert template.core_id == "sensual_dominance"
        assert template.primary_emotion == "playful_control"

    def test_spec_has_validate_choices_function(self):
        """Each spec has validation function."""
        spec = get_genre_pipeline(Genre.GENTLEFEMDOM)
        template = spec.template_factory("sensual_dominance")
        choices = {4: {"want": "want-establish-trust", ...}}
        result = spec.validate_choices(template, choices)
        assert isinstance(result, tuple)
        assert len(result) == 3  # (is_valid, errors, warnings)

    def test_spec_has_identity_strategy(self):
        """Each spec has identity generation strategy."""
        spec = get_genre_pipeline(Genre.GENTLEFEMDOM)
        assert callable(spec.identity_strategy)
```

Run: `pytest tests/phase4/ -v`
Expected: FAIL (registry doesn't exist yet)

### Step 2: Create GenrePipelineSpec and registry

- [ ] Create `src/auteur/genres/registry.py`

```python
"""Genre pipeline registry. Makes genres first-class plugins."""

from dataclasses import dataclass
from typing import Callable, Dict, List
from auteur.blueprint import Genre
from auteur.netorare.core_templates import (
    HumiliationTemplate, HorrorTemplate, MysteryTemplate as NetorareMysteryTemplate
)
from auteur.mystery.core_templates import HowdunitTemplate, ParanoiaTemplate, CozyTemplate
from auteur.gentlefemdom.core_templates import (
    SensualDominanceTemplate, TenderSurrenderTemplate, RomanticAuthorityTemplate
)


@dataclass(frozen=True)
class GenrePipelineSpec:
    """Complete specification for a genre pipeline. Makes it first-class."""
    genre: Genre
    slug: str
    core_ids: tuple
    template_factory: Callable[[str], 'CoreTemplate']
    validate_choices: Callable
    identity_strategy: Callable
    browser_title: str
    session_dir_name: str
    contract_file: str


_GENRE_SPECS: Dict[Genre, GenrePipelineSpec] = {}


def _register_netorare():
    """Register netorare genre."""
    def factory(core_id: str):
        templates = {
            "classic_humiliation": HumiliationTemplate,
            "horror": HorrorTemplate,
            "mystery": NetorareMysteryTemplate,
        }
        return templates[core_id]()
    
    from auteur.netorare.validation import validate_choices
    from auteur.netorare.identity_generator import IdentityGenerator
    
    spec = GenrePipelineSpec(
        genre=Genre.NETORARE,
        slug="netorare",
        core_ids=("classic_humiliation", "horror", "mystery"),
        template_factory=factory,
        validate_choices=validate_choices,
        identity_strategy=IdentityGenerator.from_choices,
        browser_title="Netorare Story Identity Authoring",
        session_dir_name="netorare",
        contract_file="src/auteur/genres/data/netorare.yaml",
    )
    _GENRE_SPECS[Genre.NETORARE] = spec


def _register_mystery():
    """Register mystery genre."""
    def factory(core_id: str):
        templates = {
            "howdunit": HowdunitTemplate,
            "paranoia": ParanoiaTemplate,
            "cozy": CozyTemplate,
        }
        return templates[core_id]()
    
    from auteur.mystery.validation import validate_choices
    from auteur.netorare.identity_generator import IdentityGenerator
    
    spec = GenrePipelineSpec(
        genre=Genre.MYSTERY,
        slug="mystery",
        core_ids=("howdunit", "paranoia", "cozy"),
        template_factory=factory,
        validate_choices=validate_choices,
        identity_strategy=IdentityGenerator.from_choices,
        browser_title="Mystery Story Identity Authoring",
        session_dir_name="mystery",
        contract_file="src/auteur/genres/data/mystery.yaml",
    )
    _GENRE_SPECS[Genre.MYSTERY] = spec


def _register_gentlefemdom():
    """Register gentlefemdom genre."""
    def factory(core_id: str):
        templates = {
            "sensual_dominance": SensualDominanceTemplate,
            "tender_surrender": TenderSurrenderTemplate,
            "romantic_authority": RomanticAuthorityTemplate,
        }
        return templates[core_id]()
    
    from auteur.gentlefemdom.validation import validate_choices
    from auteur.netorare.identity_generator import IdentityGenerator
    
    spec = GenrePipelineSpec(
        genre=Genre.GENTLEFEMDOM,
        slug="gentlefemdom",
        core_ids=("sensual_dominance", "tender_surrender", "romantic_authority"),
        template_factory=factory,
        validate_choices=validate_choices,
        identity_strategy=IdentityGenerator.from_choices,
        browser_title="Gentle Femdom Story Identity Authoring",
        session_dir_name="gentlefemdom",
        contract_file="src/auteur/genres/data/gentlefemdom.yaml",
    )
    _GENRE_SPECS[Genre.GENTLEFEMDOM] = spec


def _initialize_registry():
    """Initialize all registered genres."""
    _register_netorare()
    _register_mystery()
    _register_gentlefemdom()


def get_genre_pipeline(genre: Genre) -> GenrePipelineSpec:
    """Get pipeline spec for a genre."""
    if not _GENRE_SPECS:
        _initialize_registry()
    if genre not in _GENRE_SPECS:
        raise ValueError(f"Unknown genre: {genre}")
    return _GENRE_SPECS[genre]


def get_all_genres() -> List[GenrePipelineSpec]:
    """Get all registered genre specs."""
    if not _GENRE_SPECS:
        _initialize_registry()
    return list(_GENRE_SPECS.values())
```

### Step 3: Create `src/auteur/genres/__init__.py`

```python
"""Genre pipeline registry and contracts."""

from .registry import (
    GenrePipelineSpec,
    get_genre_pipeline,
    get_all_genres,
)

__all__ = ["GenrePipelineSpec", "get_genre_pipeline", "get_all_genres"]
```

### Step 4: Run Phase 4 tests

- [ ] `pytest tests/phase4/ -v`
Expected: All tests PASS

### Step 5: Full suite

- [ ] `pytest tests/ -q`
Expected: 930+ passing

### Step 6: Commit Phase 4

- [ ] Commit: "feat(genres): introduce GenrePipelineSpec registry making genres first-class plugins"

---

## Phase 5: Wire CLI Dispatcher and Register All Three Genres

**Goal:** Make `auteur gentlefemdom init` work via registry dispatch (currently unwired).

**Files:**
- Modify: `src/auteur/cli.py`
- Modify: `src/auteur/cli_gentlefemdom.py` (if needed for registry dispatch)
- Create: `tests/phase5/test_cli_genre_dispatch.py`

**Interfaces:**
- Consumes: `GenrePipelineSpec` from registry
- Produces: Complete CLI with all three genres wired

### Step 1: Write CLI dispatch tests

- [ ] Create `tests/phase5/test_cli_genre_dispatch.py`

```python
"""Tests: CLI dispatcher registers and invokes all three genres."""

import pytest
from pathlib import Path
from unittest.mock import patch
from auteur.cli import parse_args
from auteur.blueprint import Genre


class TestCLIGenreDispatch:
    """Verify all three genres are registered and dispatchable via CLI."""

    def test_cli_has_gentlefemdom_subcommand(self):
        """CLI parser accepts 'auteur gentlefemdom init'."""
        args = parse_args(["gentlefemdom", "init", "test_project"])
        assert args.command == "gentlefemdom"
        assert args.subcommand == "init"

    def test_cli_has_mystery_subcommand(self):
        """CLI parser accepts 'auteur mystery init'."""
        args = parse_args(["mystery", "init", "test_project"])
        assert args.command == "mystery"

    def test_cli_has_netorare_subcommand(self):
        """CLI parser accepts 'auteur netorare init'."""
        args = parse_args(["netorare", "init", "test_project"])
        assert args.command == "netorare"

    def test_gentlefemdom_init_accepts_core_parameter(self):
        """'auteur gentlefemdom init --core sensual_dominance' parses."""
        args = parse_args(["gentlefemdom", "init", "test_project", "--core", "sensual_dominance"])
        assert args.core == "sensual_dominance"

    def test_all_core_ids_accepted_for_gentlefemdom(self):
        """Gentlefemdom accepts all three core IDs."""
        for core in ["sensual_dominance", "tender_surrender", "romantic_authority"]:
            args = parse_args(["gentlefemdom", "init", "test_project", "--core", core])
            assert args.core == core
```

Run: `pytest tests/phase5/ -v`
Expected: Some FAIL (CLI dispatcher incomplete)

### Step 2: Wire gentlefemdom into main CLI dispatcher

- [ ] Modify `src/auteur/cli.py`
- [ ] Import gentlefemdom handler (if not already):

```python
from auteur.cli_gentlefemdom import handle_gentlefemdom_init
```

- [ ] Add gentlefemdom subparser to the argparse dispatcher:

```python
# Add to subparsers.add_parser calls:
p_gf = sub.add_parser("gentlefemdom", help="Interactive browser-based gentle femdom story identity authoring.")
p_gf.add_argument("project", type=Path, help="Project directory")
p_gf.add_argument("--core", choices=["sensual_dominance", "tender_surrender", "romantic_authority"], default="sensual_dominance", help="Emotional core")
p_gf.add_argument("--provider", choices=["anthropic", "openai"], default="anthropic")
p_gf.set_defaults(handler=handle_gentlefemdom_init)
```

- [ ] Add dispatch logic to handle gentlefemdom command

### Step 3: Update CLI handlers to use registry dispatch (optional optimization)

For now, each genre handler can independently call its identity generator. Registry integration is opt-in for Phase 4+.

### Step 4: Run Phase 5 tests

- [ ] `pytest tests/phase5/ -v`
Expected: All tests PASS

### Step 5: Manual CLI test

- [ ] `python -m auteur gentlefemdom init test_project --core sensual_dominance`
Expected: Interactive browser session starts on port 8767

### Step 6: Full suite

- [ ] `pytest tests/ -q`
Expected: 930+ passing

### Step 7: Commit Phase 5

- [ ] Commit: "feat(cli): wire gentlefemdom dispatcher and register all three genres as CLI subcommands"

---

## Phase 6: Add Semantic Regression Tests Proving Emotional Preservation

**Goal:** Catch any future regression where emotional intent is lost.

**Files:**
- Create: `tests/phase6/test_semantic_regression_all_genres.py`

**Interfaces:**
- Consumes: All three genres' templates and validation
- Produces: Comprehensive regression tests

### Step 1: Write semantic regression test suite

- [ ] Create `tests/phase6/test_semantic_regression_all_genres.py`

```python
"""Tests: All genres preserve emotional intent through pipeline."""

import pytest
from auteur.netorare.identity_generator import IdentityGenerator
from auteur.netorare.core_templates import HumiliationTemplate, HorrorTemplate
from auteur.mystery.core_templates import HowdunitTemplate, ParanoiaTemplate, CozyTemplate
from auteur.gentlefemdom.core_templates import (
    SensualDominanceTemplate, TenderSurrenderTemplate, RomanticAuthorityTemplate
)


class TestNetorareEmotionalPreservation:
    """Netorare cores preserve their distinct emotions."""
    
    @pytest.mark.parametrize("core_class,expected_emotion", [
        (HumiliationTemplate, "humiliation"),
        (HorrorTemplate, "dread"),
    ])
    def test_netorare_primary_emotion_preserved(self, core_class, expected_emotion):
        """Netorare cores preserve primary emotion."""
        choices = {4: {"want": "want-experience", ...}}
        template = core_class()
        identity = IdentityGenerator.from_choices(template.core_id, choices)
        assert identity.target_experience.primary == expected_emotion
        assert identity.target_experience.primary == template.primary_emotion


class TestMysteryEmotionalPreservation:
    """Mystery cores preserve their distinct emotions."""
    
    @pytest.mark.parametrize("core_class,expected_emotion", [
        (HowdunitTemplate, "puzzle_solving"),
        (ParanoiaTemplate, "dread"),
        (CozyTemplate, "comfort"),
    ])
    def test_mystery_primary_emotion_preserved(self, core_class, expected_emotion):
        """Mystery cores preserve primary emotion."""
        choices = {4: {"want": "want-solve", ...}}
        template = core_class()
        identity = IdentityGenerator.from_choices(template.core_id, choices)
        assert identity.target_experience.primary == expected_emotion


class TestGentlefemdomEmotionalPreservation:
    """Gentle femdom cores preserve their distinct emotions."""
    
    @pytest.mark.parametrize("core_class,expected_emotion", [
        (SensualDominanceTemplate, "playful_control"),
        (TenderSurrenderTemplate, "safe_vulnerability"),
        (RomanticAuthorityTemplate, "cherished_leadership"),
    ])
    def test_gentlefemdom_primary_emotion_preserved(self, core_class, expected_emotion):
        """Gentle femdom cores preserve primary emotion."""
        choices = {4: {"want": "want-establish-trust", ...}}
        template = core_class()
        identity = IdentityGenerator.from_choices(template.core_id, choices)
        assert identity.target_experience.primary == expected_emotion
        assert identity.target_experience.primary != "dread"
        assert identity.target_experience.primary != "tragic"


class TestCrossGenreDistinctness:
    """All nine cores produce distinctly different identities."""
    
    def test_no_two_cores_produce_same_primary_emotion(self):
        """All nine cores have unique primary emotions."""
        cores = [
            HumiliationTemplate(),
            HorrorTemplate(),
            HowdunitTemplate(),
            ParanoiaTemplate(),
            CozyTemplate(),
            SensualDominanceTemplate(),
            TenderSurrenderTemplate(),
            RomanticAuthorityTemplate(),
        ]
        emotions = [c.primary_emotion for c in cores]
        assert len(emotions) == len(set(emotions)), f"Duplicate emotions: {emotions}"

    def test_identity_progression_contains_core_emotion_keywords(self):
        """Progression text includes keywords from core emotion."""
        test_cases = [
            (SensualDominanceTemplate(), ["playful", "teasing", "connection"]),
            (TenderSurrenderTemplate(), ["opening", "trust", "release"]),
            (RomanticAuthorityTemplate(), ["admiration", "deference", "interdependence"]),
        ]
        for template, keywords in test_cases:
            choices = {4: {...}}
            identity = IdentityGenerator.from_choices(template.core_id, choices)
            progression_lower = identity.target_experience.progression.lower()
            found = [kw for kw in keywords if kw in progression_lower]
            assert len(found) > 0, f"{template.core_id} progression missing keywords: {keywords}"


class TestGenreContractNonFallback:
    """Generated identities use real genre contracts, not fallback."""
    
    def test_gentlefemdom_contract_not_generic(self):
        """Gentle femdom identity contract is not generic fallback."""
        choices = {4: {...}}
        identity = IdentityGenerator.from_choices("sensual_dominance", choices)
        contract = identity.genre_contract_snapshot
        # Should NOT have the generic fallback text
        assert "Actions have consequences and characters have clear intent." not in contract.core_truth
        # Should have gentlefemdom-specific text
        assert "consent" in contract.core_truth.lower() or \
               "care" in contract.core_truth.lower() or \
               "power" in contract.core_truth.lower()
```

### Step 2: Run Phase 6 tests

- [ ] `pytest tests/phase6/ -v`
Expected: All tests PASS (architecture now preserves emotion)

### Step 3: Full suite final verification

- [ ] `pytest tests/ -q`
Expected: 950+ tests passing (30 new from phases 1-6 + 920 existing)

### Step 4: Commit Phase 6

- [ ] Commit: "test(regression): add semantic preservation tests across all nine genre cores"

---

## Summary Checklist

- [ ] Phase 1: Template emotion becomes source of truth in IdentityGenerator
- [ ] Phase 2: Replace ID-to-readable fallback with template label lookups
- [ ] Phase 3: Create gentlefemdom.yaml genre contract
- [ ] Phase 4: Introduce GenrePipelineSpec registry (architectural shift)
- [ ] Phase 5: Wire CLI dispatcher for all three genres
- [ ] Phase 6: Add semantic regression tests

**Final Status:**
- ✅ 950+ tests passing (30 new + 920+ existing)
- ✅ Zero regressions
- ✅ Three genres implemented as equivalent first-class plugins
- ✅ No special cases in shared infrastructure
- ✅ Emotional intent preserved end-to-end for all nine cores
- ✅ CLI fully wired and testable
