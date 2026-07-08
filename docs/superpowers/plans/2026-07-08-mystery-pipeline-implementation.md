# Mystery Genre Pipeline Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement the Mystery genre pipeline (howdunit, paranoia, cozy cores) with decision trees, validation rules, and identity generation, validating that the netorare architecture generalizes to a second genre.

**Architecture:** Three mystery emotional cores (Howdunit, Paranoia, Cozy) each with a 9-phase decision tree (Layers 1-9). Templates and validation are genre-specific; Session State, HTTP Server, Browser UI, and CLI are reused from netorare without modification. Identity generation uses the existing IdentityGenerator with mystery-specific routing.

**Tech Stack:** Python 3.11+, Pydantic (StoryIdentity), YAML serialization, pytest for testing.

## Global Constraints

- Exact file paths: Create under `src/auteur/mystery/` (parallel to `src/auteur/netorare/`)
- Template API matches netorare: `phases` dict, `get_options(phase)`, `get_constraints(phase)`, `validate_choices(choices)`
- Validation API matches netorare: `ValidationRule` class, `RuleSet` dispatcher, `validate_choices(template, choices)` returning `(is_valid, errors, warnings)`
- Identity Generator routing: `from_choices(core_id="howdunit"|"paranoia"|"cozy", choices)` → `StoryIdentity` with `Genre.MYSTERY`
- All generated YAML must pass `auteur identity validate story_identity.yaml`
- All 9-phase options must be present in templates (Layer 1 gates entire cascade)
- Three cores must be independently testable and work with shared infrastructure (no modifications to Tasks 4-7)
- Test count target: 40-50 total (15 Task 1 + 20 Task 2 + 12 Task 3)

---

## Task 1: Mystery Core Templates

**Files:**
- Create: `src/auteur/mystery/__init__.py`
- Create: `src/auteur/mystery/core_templates.py`
- Create: `tests/mystery/__init__.py`
- Create: `tests/mystery/test_core_templates.py`

**Interfaces:**
- Produces:
  - `HowdunitTemplate()` class with `.phases`, `.core_id="howdunit"`, `.primary_emotion="puzzle-solving"`, `.get_options(phase)`, `.get_constraints(phase)`, `.validate_choices(choices) → (bool, List[str], List[str])`
  - `ParanoiaTemplate()` class with `.phases`, `.core_id="paranoia"`, `.primary_emotion="dread"`, same methods
  - `CozyTemplate()` class with `.phases`, `.core_id="cozy"`, `.primary_emotion="comfort"`, same methods
  - `get_template(core_id: str) → HowdunitTemplate | ParanoiaTemplate | CozyTemplate`
  - Each template class has 9 phases in `phases` dict (1-9, matching netorare pattern)
  - Each phase maps to layer name (e.g., 1→"emotional_core", 4→"structural_forces")

---

### Task 1: Step 1 — Write failing tests for HowdunitTemplate

Create `tests/mystery/test_core_templates.py`:

```python
"""Tests for Mystery genre core templates."""

import pytest
from auteur.mystery.core_templates import (
    HowdunitTemplate, ParanoiaTemplate, CozyTemplate, 
    get_template, TemplateOption
)


class TestHowdunitTemplate:
    """Test Howdunit (classic detective) template."""

    def test_howdunit_instantiation(self):
        """Test that HowdunitTemplate can be instantiated."""
        template = HowdunitTemplate()
        assert template.core_id == "howdunit"
        assert template.primary_emotion == "puzzle-solving"

    def test_howdunit_phases(self):
        """Test that HowdunitTemplate has all 9 phases."""
        template = HowdunitTemplate()
        assert len(template.phases) == 9
        assert template.phases[1] == "emotional_core"
        assert template.phases[2] == "genre_contract"
        assert template.phases[3] == "scope"
        assert template.phases[4] == "structural_forces"

    def test_howdunit_get_options_layer1(self):
        """Test get_options(1) returns howdunit as only option."""
        template = HowdunitTemplate()
        options = template.get_options(1)
        assert len(options) > 0
        assert any(opt.id == "howdunit" for opt in options)

    def test_howdunit_get_options_layer2_genre_contracts(self):
        """Test get_options(2) returns multiple genre contract options."""
        template = HowdunitTemplate()
        options = template.get_options(2)
        assert len(options) >= 4  # At least 4 genre options
        option_ids = [opt.id for opt in options]
        assert "detective" in option_ids
        assert "procedural" in option_ids
        assert "locked-room" in option_ids
        assert "puzzle-box" in option_ids

    def test_howdunit_get_options_layer4_want(self):
        """Test get_options(4, 'want') returns want options for Howdunit."""
        template = HowdunitTemplate()
        options = template.get_options(4)
        wants = [opt for opt in options if hasattr(opt, 'field') and opt.field == 'want']
        assert len(wants) >= 3
        want_ids = [opt.id for opt in wants]
        assert "want-solve-puzzle" in want_ids
        assert "want-identify-culprit" in want_ids

    def test_howdunit_validate_choices_valid(self):
        """Test validate_choices with valid howdunit choices."""
        template = HowdunitTemplate()
        choices = {
            1: {"emotional_core": "howdunit"},
            2: {"genre_contract": "detective"},
            3: {"scope": "standard"},
            4: {
                "want": "want-solve-puzzle",
                "resistance": "resistance-misleading-clues",
                "conflict": "conflict-deduction-misdirection",
                "stakes": "stakes-justice",
                "change": "change-clarity"
            },
        }
        is_valid, errors, warnings = template.validate_choices(choices)
        assert is_valid is True
        assert len(errors) == 0

    def test_howdunit_validate_choices_invalid_phase(self):
        """Test validate_choices with invalid phase number."""
        template = HowdunitTemplate()
        choices = {
            99: {"invalid": "phase"}
        }
        is_valid, errors, warnings = template.validate_choices(choices)
        assert is_valid is False
        assert any("phase" in err.lower() for err in errors)

    def test_howdunit_validate_choices_invalid_option_id(self):
        """Test validate_choices with invalid option ID."""
        template = HowdunitTemplate()
        choices = {
            2: {"genre_contract": "invalid-genre-id"}
        }
        is_valid, errors, warnings = template.validate_choices(choices)
        assert is_valid is False
        assert any("invalid-genre-id" in err for err in errors)

    def test_howdunit_get_constraints_layer4(self):
        """Test get_constraints returns validation hints for layer 4."""
        template = HowdunitTemplate()
        constraints = template.get_constraints(4)
        assert constraints is not None
        # Constraints should mention that want ≠ change
        assert isinstance(constraints, (str, dict, list))


class TestParanoiaTemplate:
    """Test Paranoia (psychological thriller) template."""

    def test_paranoia_instantiation(self):
        """Test that ParanoiaTemplate can be instantiated."""
        template = ParanoiaTemplate()
        assert template.core_id == "paranoia"
        assert template.primary_emotion == "dread"

    def test_paranoia_phases(self):
        """Test that ParanoiaTemplate has all 9 phases."""
        template = ParanoiaTemplate()
        assert len(template.phases) == 9
        assert template.phases[1] == "emotional_core"
        assert template.phases[4] == "structural_forces"

    def test_paranoia_get_options_layer1(self):
        """Test get_options(1) returns paranoia as only option."""
        template = ParanoiaTemplate()
        options = template.get_options(1)
        assert any(opt.id == "paranoia" for opt in options)

    def test_paranoia_validate_choices_valid(self):
        """Test validate_choices with valid paranoia choices."""
        template = ParanoiaTemplate()
        choices = {
            1: {"emotional_core": "paranoia"},
            2: {"genre_contract": "gaslight"},
            4: {
                "want": "want-understand-reality",
                "resistance": "resistance-unreliable-narrator",
                "conflict": "conflict-reality-perception",
                "stakes": "stakes-mental-stability",
                "change": "change-paranoia-peak"
            }
        }
        is_valid, errors, warnings = template.validate_choices(choices)
        assert is_valid is True


class TestCozyTemplate:
    """Test Cozy (low-stakes) template."""

    def test_cozy_instantiation(self):
        """Test that CozyTemplate can be instantiated."""
        template = CozyTemplate()
        assert template.core_id == "cozy"
        assert template.primary_emotion == "comfort"

    def test_cozy_phases(self):
        """Test that CozyTemplate has all 9 phases."""
        template = CozyTemplate()
        assert len(template.phases) == 9

    def test_cozy_validate_choices_valid(self):
        """Test validate_choices with valid cozy choices."""
        template = CozyTemplate()
        choices = {
            1: {"emotional_core": "cozy"},
            2: {"genre_contract": "village"},
            4: {
                "want": "want-solve-in-community",
                "resistance": "resistance-scattered-clues",
                "conflict": "conflict-investigation-daily-life",
                "stakes": "stakes-community-bonds",
                "change": "change-restored-comfort"
            }
        }
        is_valid, errors, warnings = template.validate_choices(choices)
        assert is_valid is True


class TestGetTemplate:
    """Test template factory function."""

    def test_get_template_howdunit(self):
        """Test get_template returns HowdunitTemplate for 'howdunit'."""
        template = get_template("howdunit")
        assert isinstance(template, HowdunitTemplate)
        assert template.core_id == "howdunit"

    def test_get_template_paranoia(self):
        """Test get_template returns ParanoiaTemplate for 'paranoia'."""
        template = get_template("paranoia")
        assert isinstance(template, ParanoiaTemplate)
        assert template.core_id == "paranoia"

    def test_get_template_cozy(self):
        """Test get_template returns CozyTemplate for 'cozy'."""
        template = get_template("cozy")
        assert isinstance(template, CozyTemplate)
        assert template.core_id == "cozy"

    def test_get_template_invalid_core_id(self):
        """Test get_template raises ValueError for unknown core."""
        with pytest.raises(ValueError):
            get_template("invalid-core")
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/mystery/test_core_templates.py -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'auteur.mystery'"

---

### Task 1: Step 3 — Create mystery package and core templates module

Create `src/auteur/mystery/__init__.py`:

```python
"""Mystery genre pipeline: Howdunit, Paranoia, Cozy emotional cores."""

from auteur.mystery.core_templates import (
    HowdunitTemplate,
    ParanoiaTemplate,
    CozyTemplate,
    TemplateOption,
    get_template,
)

__all__ = [
    "HowdunitTemplate",
    "ParanoiaTemplate",
    "CozyTemplate",
    "TemplateOption",
    "get_template",
]
```

Create `src/auteur/mystery/core_templates.py` (see code block below):

```python
"""Core templates: decision trees for howdunit, paranoia, cozy emotional cores."""

from dataclasses import dataclass, asdict
from typing import Dict, List, Any, Optional, Tuple


@dataclass
class TemplateOption:
    """A single option in a decision phase."""
    id: str
    label: str
    description: str = ""
    cascades_to: Optional[Dict[int, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict for serialization."""
        result = asdict(self)
        if result.get("cascades_to") is None:
            del result["cascades_to"]
        if not result.get("description"):
            del result["description"]
        return result


class HowdunitTemplate:
    """Classic Detective Mystery (puzzle-solving) template."""

    phases = {
        1: "emotional_core",
        2: "genre_contract",
        3: "scope",
        4: "structural_forces",
        5: "investigation_style",
        6: "pacing_rhythm",
        7: "clue_distribution",
        8: "solution_density",
        9: "fairness_confidence"
    }

    def __init__(self):
        self.core_id = "howdunit"
        self.primary_emotion = "puzzle-solving"
        self._initialize_options()

    def _initialize_options(self):
        """Define all decision options for this template."""
        self.options = {
            1: [
                TemplateOption(
                    id="howdunit",
                    label="Classic Detective Mystery",
                    description="Intellectual satisfaction via puzzle-solving"
                )
            ],
            2: [  # Genre Contract
                TemplateOption(id="detective", label="Detective procedural"),
                TemplateOption(id="procedural", label="Police/investigation procedural"),
                TemplateOption(id="locked-room", label="Locked-room puzzle"),
                TemplateOption(id="puzzle-box", label="Intricate puzzle structure"),
            ],
            3: [  # Scope
                TemplateOption(id="focused", label="Single crime, contained"),
                TemplateOption(id="standard", label="Multi-faceted crime, wider cast"),
                TemplateOption(id="expanded", label="Serial crimes, city-scale investigation"),
            ],
            4: [  # Structural Forces (requires all fields)
                TemplateOption(id="want-solve-puzzle", label="Want: Solve the puzzle", description="Discover truth"),
                TemplateOption(id="want-identify-culprit", label="Want: Identify the culprit", description="Find the guilty party"),
                TemplateOption(id="want-restore-order", label="Want: Restore order", description="Resolve disruption"),
                TemplateOption(id="resistance-misleading-clues", label="Resistance: Misleading clues", description="False evidence misdirects"),
                TemplateOption(id="resistance-false-suspects", label="Resistance: False suspects", description="Red herrings point wrong way"),
                TemplateOption(id="resistance-hidden-motives", label="Resistance: Hidden motives", description="True reasons obscured"),
                TemplateOption(id="conflict-deduction-misdirection", label="Conflict: Deduction vs. misdirection", description="Reader vs. author puzzle"),
                TemplateOption(id="conflict-logic-chaos", label="Conflict: Logic vs. chaos", description="Pattern-seeking in confusion"),
                TemplateOption(id="stakes-justice", label="Stakes: Justice served", description="Culprit answer required"),
                TemplateOption(id="stakes-order-restored", label="Stakes: Order restored", description="Community resolution"),
                TemplateOption(id="change-clarity", label="Change: From confusion to clarity", description="Understanding achieved"),
                TemplateOption(id="change-certainty", label="Change: From suspicion to certainty", description="Truth confirmed"),
            ],
            5: [  # Investigation Style
                TemplateOption(id="logical", label="Logical deduction"),
                TemplateOption(id="intuitive", label="Intuitive investigation"),
                TemplateOption(id="procedural", label="By-the-book procedure"),
            ],
            6: [  # Pacing Rhythm
                TemplateOption(id="accelerating", label="Clues accelerate toward solution"),
                TemplateOption(id="rhythmic", label="Steady rhythm of discovery"),
                TemplateOption(id="zigzag", label="Forward progress with setbacks"),
            ],
            7: [  # Clue Distribution
                TemplateOption(id="early-heavy", label="Heavy clues early, light late"),
                TemplateOption(id="even", label="Even clue distribution"),
                TemplateOption(id="late-heavy", label="Light clues early, heavy late"),
            ],
            8: [  # Solution Density
                TemplateOption(id="tight", label="Solution barely derivable from clues"),
                TemplateOption(id="moderate", label="Solution is one of several reasonable readings"),
                TemplateOption(id="generous", label="Solution obvious once clues are gathered"),
            ],
            9: [  # Fairness Confidence
                TemplateOption(id="fair-high", label="High confidence reader could solve it"),
                TemplateOption(id="fair-medium", label="Medium confidence (possible on rereads)"),
                TemplateOption(id="fair-challenging", label="Challenging but fair puzzle"),
            ]
        }

    def get_options(self, phase: int) -> List[TemplateOption]:
        """Get available options for a phase."""
        return self.options.get(phase, [])

    def get_constraints(self, phase: int) -> str:
        """Get validation constraints for a phase."""
        if phase == 4:
            return "Must select one from each field: want, resistance, conflict, stakes, change"
        return ""

    def validate_choices(self, choices: Dict[int, Dict[str, str]]) -> Tuple[bool, List[str], List[str]]:
        """Validate choices for structural coherence. Returns (is_valid, errors, warnings)."""
        errors = []
        warnings = []

        for phase, phase_choices in choices.items():
            if phase not in self.phases:
                errors.append(f"Phase {phase} does not exist in Howdunit template (valid: 1-9)")
                continue

            for field, value in phase_choices.items():
                # Check that value exists in options for this phase
                valid_ids = [opt.id for opt in self.get_options(phase)]
                if value not in valid_ids:
                    errors.append(f"Phase {phase}: '{value}' is not a valid option. Valid options: {valid_ids}")

        return len(errors) == 0, errors, warnings


class ParanoiaTemplate:
    """Paranoia (psychological thriller) template."""

    phases = {
        1: "emotional_core",
        2: "genre_contract",
        3: "scope",
        4: "structural_forces",
        5: "narrator_reliability",
        6: "gaslighting_intensity",
        7: "paranoia_escalation",
        8: "truth_ambiguity",
        9: "dread_confidence"
    }

    def __init__(self):
        self.core_id = "paranoia"
        self.primary_emotion = "dread"
        self._initialize_options()

    def _initialize_options(self):
        """Define all decision options for this template."""
        self.options = {
            1: [
                TemplateOption(
                    id="paranoia",
                    label="Paranoia / Psychological Thriller",
                    description="Dread and uncertainty via unreliable reality"
                )
            ],
            2: [
                TemplateOption(id="gaslight", label="Gaslighting narrative"),
                TemplateOption(id="conspiracy", label="Hidden conspiracy"),
                TemplateOption(id="psychological-horror", label="Psychological horror premise"),
                TemplateOption(id="unreliable-narrator", label="Unreliable narrator study"),
            ],
            3: [
                TemplateOption(id="intimate", label="1-2 characters, internal focus"),
                TemplateOption(id="contained", label="Household or institution"),
                TemplateOption(id="sprawling", label="Conspiracy reaches wider"),
            ],
            4: [
                TemplateOption(id="want-understand-reality", label="Want: Understand what's real"),
                TemplateOption(id="want-escape-situation", label="Want: Escape the situation"),
                TemplateOption(id="want-prove-sanity", label="Want: Prove they're not crazy"),
                TemplateOption(id="resistance-unreliable-narrator", label="Resistance: Unreliable narrator"),
                TemplateOption(id="resistance-gaslighting", label="Resistance: Active gaslighting"),
                TemplateOption(id="resistance-hidden-truth", label="Resistance: Truth hidden from all"),
                TemplateOption(id="conflict-reality-perception", label="Conflict: Reality vs. Perception"),
                TemplateOption(id="conflict-trust-doubt", label="Conflict: Trust vs. Doubt"),
                TemplateOption(id="stakes-mental-stability", label="Stakes: Mental stability"),
                TemplateOption(id="stakes-safety", label="Stakes: Physical safety"),
                TemplateOption(id="stakes-identity", label="Stakes: Sense of identity"),
                TemplateOption(id="change-paranoia-peak", label="Change: Paranoia reaches peak"),
                TemplateOption(id="change-revelation", label="Change: Revelation of truth"),
            ],
            5: [
                TemplateOption(id="highly-unreliable", label="Narrator severely distorts reality"),
                TemplateOption(id="moderately-unreliable", label="Narrator's account has selective gaps"),
                TemplateOption(id="subtly-unreliable", label="Subtle inconsistencies suggest doubt"),
            ],
            6: [
                TemplateOption(id="psychological", label="Psychological manipulation"),
                TemplateOption(id="social", label="Social pressure and isolation"),
                TemplateOption(id="institutional", label="System-level deception"),
            ],
            7: [
                TemplateOption(id="slow-build", label="Paranoia builds slowly from doubt"),
                TemplateOption(id="rapid-spiral", label="Paranoia spirals rapidly"),
                TemplateOption(id="rhythmic-escalation", label="Rhythmic escalation of dread"),
            ],
            8: [
                TemplateOption(id="fully-revealed", label="Truth is fully revealed by end"),
                TemplateOption(id="ambiguous", label="Truth remains ambiguous"),
                TemplateOption(id="devastatingly-different", label="Reality is devastatingly different from perception"),
            ],
            9: [
                TemplateOption(id="high-dread", label="Maintains high dread throughout"),
                TemplateOption(id="managed-dread", label="Dread peaks then resolves"),
                TemplateOption(id="open-dread", label="Dread remains unresolved"),
            ]
        }

    def get_options(self, phase: int) -> List[TemplateOption]:
        """Get available options for a phase."""
        return self.options.get(phase, [])

    def get_constraints(self, phase: int) -> str:
        """Get validation constraints for a phase."""
        if phase == 4:
            return "Must select one from each field: want, resistance, conflict, stakes, change"
        return ""

    def validate_choices(self, choices: Dict[int, Dict[str, str]]) -> Tuple[bool, List[str], List[str]]:
        """Validate choices for structural coherence."""
        errors = []
        warnings = []

        for phase, phase_choices in choices.items():
            if phase not in self.phases:
                errors.append(f"Phase {phase} does not exist in Paranoia template (valid: 1-9)")
                continue

            for field, value in phase_choices.items():
                valid_ids = [opt.id for opt in self.get_options(phase)]
                if value not in valid_ids:
                    errors.append(f"Phase {phase}: '{value}' is not a valid option. Valid options: {valid_ids}")

        return len(errors) == 0, errors, warnings


class CozyTemplate:
    """Cozy Mystery (low-stakes, community-focused) template."""

    phases = {
        1: "emotional_core",
        2: "genre_contract",
        3: "scope",
        4: "structural_forces",
        5: "humor_level",
        6: "relationship_focus",
        7: "violence_budget",
        8: "community_role",
        9: "warmth_confidence"
    }

    def __init__(self):
        self.core_id = "cozy"
        self.primary_emotion = "comfort"
        self._initialize_options()

    def _initialize_options(self):
        """Define all decision options for this template."""
        self.options = {
            1: [
                TemplateOption(
                    id="cozy",
                    label="Cozy Mystery",
                    description="Comfort and closure in a warm, safe world"
                )
            ],
            2: [
                TemplateOption(id="village", label="Village/small-town cozy"),
                TemplateOption(id="bookshop", label="Bookshop or library cozy"),
                TemplateOption(id="domestic", label="Domestic/home cozy"),
                TemplateOption(id="culinary", label="Food/culinary cozy"),
            ],
            3: [
                TemplateOption(id="micro", label="Single household or shop"),
                TemplateOption(id="village", label="Village with interconnected residents"),
                TemplateOption(id="regional", label="Multiple small towns"),
            ],
            4: [
                TemplateOption(id="want-solve-community", label="Want: Solve in community context"),
                TemplateOption(id="want-find-truth", label="Want: Find the truth gently"),
                TemplateOption(id="want-restore-peace", label="Want: Restore community peace"),
                TemplateOption(id="resistance-scattered-clues", label="Resistance: Clues are scattered"),
                TemplateOption(id="resistance-community-dynamics", label="Resistance: Community politics block truth"),
                TemplateOption(id="resistance-reluctant-witnesses", label="Resistance: Witnesses reluctant to speak"),
                TemplateOption(id="conflict-investigation-daily-life", label="Conflict: Investigation vs. daily life"),
                TemplateOption(id="conflict-truth-bonds", label="Conflict: Finding truth vs. maintaining bonds"),
                TemplateOption(id="stakes-community-bonds", label="Stakes: Community relationships"),
                TemplateOption(id="stakes-personal-growth", label="Stakes: Personal transformation"),
                TemplateOption(id="stakes-closure", label="Stakes: Closure and peace"),
                TemplateOption(id="change-community-shift", label="Change: Community dynamics shift"),
                TemplateOption(id="change-mystery-resolved", label="Change: Mystery is solved"),
            ],
            5: [
                TemplateOption(id="light-humor", label="Light, warm humor throughout"),
                TemplateOption(id="occasional-humor", label="Occasional moments of levity"),
                TemplateOption(id="dark-undertone", label="Dark humor underneath warmth"),
            ],
            6: [
                TemplateOption(id="protagonist-centric", label="Focus on protagonist relationships"),
                TemplateOption(id="community-web", label="Complex web of community bonds"),
                TemplateOption(id="romance-subplot", label="Romantic subplot alongside investigation"),
            ],
            7: [
                TemplateOption(id="none", label="No violence (mystery is abstract)"),
                TemplateOption(id="off-page", label="Violence is off-page"),
                TemplateOption(id="minimal", label="Minimal, non-graphic violence"),
            ],
            8: [
                TemplateOption(id="community-central", label="Community bonds are central to resolution"),
                TemplateOption(id="community-involved", label="Community participates in solution"),
                TemplateOption(id="protagonist-solves", label="Protagonist solves mostly alone"),
            ],
            9: [
                TemplateOption(id="very-cozy", label="Very warm and safe throughout"),
                TemplateOption(id="cozy-with-tension", label="Cozy interrupted by investigation tension"),
                TemplateOption(id="restored-coziness", label="Coziness restored by resolution"),
            ]
        }

    def get_options(self, phase: int) -> List[TemplateOption]:
        """Get available options for a phase."""
        return self.options.get(phase, [])

    def get_constraints(self, phase: int) -> str:
        """Get validation constraints for a phase."""
        if phase == 4:
            return "Must select one from each field: want, resistance, conflict, stakes, change"
        return ""

    def validate_choices(self, choices: Dict[int, Dict[str, str]]) -> Tuple[bool, List[str], List[str]]:
        """Validate choices for structural coherence."""
        errors = []
        warnings = []

        for phase, phase_choices in choices.items():
            if phase not in self.phases:
                errors.append(f"Phase {phase} does not exist in Cozy template (valid: 1-9)")
                continue

            for field, value in phase_choices.items():
                valid_ids = [opt.id for opt in self.get_options(phase)]
                if value not in valid_ids:
                    errors.append(f"Phase {phase}: '{value}' is not a valid option. Valid options: {valid_ids}")

        return len(errors) == 0, errors, warnings


def get_template(core_id: str):
    """Factory function: return template instance for core_id."""
    if core_id == "howdunit":
        return HowdunitTemplate()
    elif core_id == "paranoia":
        return ParanoiaTemplate()
    elif core_id == "cozy":
        return CozyTemplate()
    else:
        raise ValueError(f"Unknown mystery core_id: {core_id}. Valid: howdunit, paranoia, cozy")
```

Create `tests/mystery/__init__.py` (empty file):

```python
"""Tests for mystery genre pipeline."""
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/mystery/test_core_templates.py -v`
Expected: PASS (15 tests passing)

- [ ] **Step 5: Commit**

```bash
git add src/auteur/mystery/ tests/mystery/
git commit -m "feat(mystery): add howdunit, paranoia, cozy core templates with full 9-phase decision trees"
```

---

## Task 2: Mystery Validation Rules

**Files:**
- Create: `src/auteur/mystery/validation.py`
- Create: `tests/mystery/test_validation.py`

**Interfaces:**
- Consumes: `HowdunitTemplate`, `ParanoiaTemplate`, `CozyTemplate` from Task 1
- Produces:
  - `ValidationRule` class (reuse netorare pattern)
  - `RuleSet` class with `.rules` list
  - `validate_choices(template: HowdunitTemplate | ParanoiaTemplate | CozyTemplate, choices: Dict[int, Dict[str, str]]) → (bool, List[str], List[str])`

---

### Task 2: Step 1 — Write failing tests for validation rules

Create `tests/mystery/test_validation.py`:

```python
"""Tests for Mystery genre validation rules."""

import pytest
from auteur.mystery.core_templates import (
    HowdunitTemplate, ParanoiaTemplate, CozyTemplate
)
from auteur.mystery.validation import validate_choices, RuleSet, ValidationRule


class TestHowdunitValidationRules:
    """Test validation rules specific to Howdunit."""

    def test_howdunit_want_not_equal_change(self):
        """Howdunit: Want and Change must differ."""
        template = HowdunitTemplate()
        # Valid: want ≠ change
        choices = {
            1: {"emotional_core": "howdunit"},
            2: {"genre_contract": "detective"},
            4: {
                "want": "want-solve-puzzle",
                "resistance": "resistance-misleading-clues",
                "conflict": "conflict-deduction-misdirection",
                "stakes": "stakes-justice",
                "change": "change-clarity"
            }
        }
        is_valid, errors, warnings = validate_choices(template, choices)
        assert is_valid is True, f"Valid howdunit choices failed: {errors}"

    def test_howdunit_red_herring_coherence(self):
        """Howdunit: Red herrings must not contradict solution."""
        template = HowdunitTemplate()
        choices = {
            1: {"emotional_core": "howdunit"},
            2: {"genre_contract": "puzzle-box"},
            7: {"clue_distribution": "early-heavy"},
        }
        # This should pass; red herring coherence is checked by rule
        is_valid, errors, warnings = validate_choices(template, choices)
        # Should not error on missing layer 4 (optional layers)
        assert is_valid is True

    def test_howdunit_solution_derivable(self):
        """Howdunit: Solution must be theoretically discoverable."""
        template = HowdunitTemplate()
        choices = {
            1: {"emotional_core": "howdunit"},
            8: {"solution_density": "tight"},  # Reader can barely derive solution
        }
        is_valid, errors, warnings = validate_choices(template, choices)
        # Tight solution density is valid
        assert "solution" not in str(errors).lower() or "valid" in str(warnings).lower()


class TestParanoiaValidationRules:
    """Test validation rules specific to Paranoia."""

    def test_paranoia_want_not_equal_change(self):
        """Paranoia: Want and Change must differ."""
        template = ParanoiaTemplate()
        choices = {
            1: {"emotional_core": "paranoia"},
            2: {"genre_contract": "gaslight"},
            4: {
                "want": "want-understand-reality",
                "resistance": "resistance-gaslighting",
                "conflict": "conflict-reality-perception",
                "stakes": "stakes-mental-stability",
                "change": "change-revelation"
            }
        }
        is_valid, errors, warnings = validate_choices(template, choices)
        assert is_valid is True

    def test_paranoia_narrator_inconsistency_deliberate(self):
        """Paranoia: Narrator inconsistencies must be intentional."""
        template = ParanoiaTemplate()
        choices = {
            1: {"emotional_core": "paranoia"},
            5: {"narrator_reliability": "highly-unreliable"},  # Intentional unreliability
        }
        is_valid, errors, warnings = validate_choices(template, choices)
        assert is_valid is True

    def test_paranoia_paranoia_escalates(self):
        """Paranoia: Dread/paranoia must escalate logically."""
        template = ParanoiaTemplate()
        choices = {
            1: {"emotional_core": "paranoia"},
            7: {"paranoia_escalation": "rapid-spiral"},  # Escalates logically
        }
        is_valid, errors, warnings = validate_choices(template, choices)
        assert is_valid is True


class TestCozyValidationRules:
    """Test validation rules specific to Cozy."""

    def test_cozy_violence_budget_respected(self):
        """Cozy: Violence must stay within declared budget."""
        template = CozyTemplate()
        choices = {
            1: {"emotional_core": "cozy"},
            2: {"genre_contract": "village"},
            7: {"violence_budget": "off-page"},  # Off-page is acceptable
        }
        is_valid, errors, warnings = validate_choices(template, choices)
        assert is_valid is True

    def test_cozy_tone_consistency(self):
        """Cozy: Warm tone must be maintained."""
        template = CozyTemplate()
        choices = {
            1: {"emotional_core": "cozy"},
            5: {"humor_level": "light-humor"},  # Maintains warmth
        }
        is_valid, errors, warnings = validate_choices(template, choices)
        assert is_valid is True

    def test_cozy_community_relationships_nuanced(self):
        """Cozy: Community relationships must be complex, not binary."""
        template = CozyTemplate()
        choices = {
            1: {"emotional_core": "cozy"},
            6: {"relationship_focus": "community-web"},  # Complex relationships
        }
        is_valid, errors, warnings = validate_choices(template, choices)
        assert is_valid is True


class TestValidationIntegration:
    """Integration tests for validation across all three cores."""

    def test_validate_choices_function_exists(self):
        """Test that validate_choices function is callable."""
        template = HowdunitTemplate()
        choices = {1: {"emotional_core": "howdunit"}}
        result = validate_choices(template, choices)
        assert isinstance(result, tuple)
        assert len(result) == 3
        is_valid, errors, warnings = result
        assert isinstance(is_valid, bool)
        assert isinstance(errors, list)
        assert isinstance(warnings, list)

    def test_ruleset_for_howdunit(self):
        """Test RuleSet instantiation for Howdunit."""
        ruleset = RuleSet("howdunit")
        assert len(ruleset.rules) > 0

    def test_ruleset_for_paranoia(self):
        """Test RuleSet instantiation for Paranoia."""
        ruleset = RuleSet("paranoia")
        assert len(ruleset.rules) > 0

    def test_ruleset_for_cozy(self):
        """Test RuleSet instantiation for Cozy."""
        ruleset = RuleSet("cozy")
        assert len(ruleset.rules) > 0

    def test_all_cores_produce_errors_list_on_validation(self):
        """Test that validation always returns (bool, list, list)."""
        for core_id, TemplateClass in [
            ("howdunit", HowdunitTemplate),
            ("paranoia", ParanoiaTemplate),
            ("cozy", CozyTemplate)
        ]:
            template = TemplateClass()
            choices = {1: {"emotional_core": core_id}}
            is_valid, errors, warnings = validate_choices(template, choices)
            assert isinstance(errors, list)
            assert isinstance(warnings, list)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/mystery/test_validation.py -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'auteur.mystery.validation'"

- [ ] **Step 3: Implement mystery validation rules**

Create `src/auteur/mystery/validation.py`:

```python
"""Deterministic validation rules for mystery story structure."""

from typing import Tuple, List, Dict, Any
from auteur.mystery.core_templates import (
    HowdunitTemplate, ParanoiaTemplate, CozyTemplate
)


class ValidationError(Exception):
    """Raised when validation fails."""
    pass


class ValidationRule:
    """A single validation rule."""

    def __init__(self, rule_id: str, name: str, check_fn, error_msg: str):
        self.rule_id = rule_id
        self.name = name
        self.check_fn = check_fn  # Function that returns (passes: bool, message: str)
        self.error_msg = error_msg

    def check(self, template, choices: Dict[int, Dict[str, str]]) -> Tuple[bool, str]:
        """Run this rule. Returns (passes, message)."""
        return self.check_fn(template, choices)


class RuleSet:
    """A collection of validation rules for a template."""

    def __init__(self, core_id: str):
        self.core_id = core_id
        self.rules: List[ValidationRule] = []
        self._build_rules()

    def _build_rules(self):
        """Build rule set based on core type."""
        if self.core_id == "howdunit":
            self._build_howdunit_rules()
        elif self.core_id == "paranoia":
            self._build_paranoia_rules()
        elif self.core_id == "cozy":
            self._build_cozy_rules()

    def _build_howdunit_rules(self):
        """Howdunit-specific validation rules."""

        # Rule 1: Want ≠ Change
        def check_want_not_equal_change(template, choices):
            layer4 = choices.get(4, {})
            want = layer4.get("want")
            change = layer4.get("change")
            if want and change and want == change:
                return False, "Want and Change cannot be the same (no dramatic arc)"
            return True, ""

        self.rules.append(ValidationRule(
            "howdunit.core.want_not_equal_change",
            "Want must differ from Change",
            check_want_not_equal_change,
            "Want and Change cannot be identical in a dramatic arc"
        ))

        # Rule 2: Solution must be derivable
        def check_solution_derivable(template, choices):
            layer7 = choices.get(7, {})
            clue_dist = layer7.get("clue_distribution")
            layer8 = choices.get(8, {})
            solution_density = layer8.get("solution_density")

            # Tight solution requires good clue distribution
            if solution_density == "tight" and clue_dist == "late-heavy":
                return False, "Tight solutions require better clue distribution (not all clues come late)"
            return True, ""

        self.rules.append(ValidationRule(
            "howdunit.structure.solution_derivable",
            "Solution must be theoretically derivable",
            check_solution_derivable,
            "Howdunit solutions must be fair (reader can theoretically solve)"
        ))

        # Rule 3: Red herring coherence check
        def check_red_herring_coherence(template, choices):
            layer2 = choices.get(2, {})
            genre = layer2.get("genre_contract")
            layer7 = choices.get(7, {})
            clues = layer7.get("clue_distribution")

            # For puzzle-box, clues must be tightly distributed
            if genre == "puzzle-box" and clues == "late-heavy":
                return False, "Puzzle-box mysteries need earlier clue introduction"
            return True, ""

        self.rules.append(ValidationRule(
            "howdunit.structure.red_herring_coherence",
            "Red herrings must not contradict solution",
            check_red_herring_coherence,
            "Red herrings must be coherent with central solution"
        ))

    def _build_paranoia_rules(self):
        """Paranoia-specific validation rules."""

        # Rule 1: Want ≠ Change
        def check_want_not_equal_change(template, choices):
            layer4 = choices.get(4, {})
            want = layer4.get("want")
            change = layer4.get("change")
            if want and change and want == change:
                return False, "Want and Change cannot be the same"
            return True, ""

        self.rules.append(ValidationRule(
            "paranoia.core.want_not_equal_change",
            "Want must differ from Change",
            check_want_not_equal_change,
            "Want and Change cannot be identical"
        ))

        # Rule 2: Narrator unreliability must be intentional
        def check_narrator_intentional(template, choices):
            layer5 = choices.get(5, {})
            reliability = layer5.get("narrator_reliability")
            layer8 = choices.get(8, {})
            truth_ambiguity = layer8.get("truth_ambiguity")

            # If narrator is unreliable, truth must be ambiguous or revealed differently
            if reliability in ["highly-unreliable", "moderately-unreliable"]:
                if not truth_ambiguity:
                    return False, "Unreliable narrator requires ambiguous truth or revelation"
            return True, ""

        self.rules.append(ValidationRule(
            "paranoia.structure.narrator_intentional",
            "Unreliable narrator must serve narrative purpose",
            check_narrator_intentional,
            "Narrator unreliability must be deliberate, not accidental"
        ))

        # Rule 3: Paranoia escalates logically
        def check_paranoia_escalates(template, choices):
            layer6 = choices.get(6, {})
            gaslight = layer6.get("gaslighting_intensity")
            layer7 = choices.get(7, {})
            escalation = layer7.get("paranoia_escalation")

            # Intense gaslighting should pair with appropriate escalation
            if gaslight == "institutional" and escalation == "slow-build":
                return False, "Institutional gaslighting typically escalates rapidly, not slowly"
            return True, ""

        self.rules.append(ValidationRule(
            "paranoia.structure.paranoia_escalates",
            "Paranoia must escalate logically",
            check_paranoia_escalates,
            "Dread escalation must match narrative tension"
        ))

    def _build_cozy_rules(self):
        """Cozy-specific validation rules."""

        # Rule 1: Violence budget respected
        def check_violence_budget(template, choices):
            layer7 = choices.get(7, {})
            violence = layer7.get("violence_budget")

            # Cozy should not have violence
            if violence and violence not in ["none", "off-page", "minimal"]:
                return False, f"Cozy mysteries should minimize violence, got: {violence}"
            return True, ""

        self.rules.append(ValidationRule(
            "cozy.tone.violence_budget",
            "Violence must stay within cozy constraints",
            check_violence_budget,
            "Cozy mysteries require off-page or minimal violence"
        ))

        # Rule 2: Tone consistency
        def check_tone_consistency(template, choices):
            layer5 = choices.get(5, {})
            humor = layer5.get("humor_level")
            layer9 = choices.get(9, {})
            warmth = layer9.get("warmth_confidence")

            # Dark humor should pair with restored coziness, not very cozy
            if humor == "dark-undertone" and warmth == "very-cozy":
                return False, "Dark humor undermines 'very cozy' tone"
            return True, ""

        self.rules.append(ValidationRule(
            "cozy.tone.consistency",
            "Tone must remain warm and safe",
            check_tone_consistency,
            "Cozy tone must be maintained throughout"
        ))

        # Rule 3: Community relationships matter
        def check_community_integrity(template, choices):
            layer6 = choices.get(6, {})
            relationships = layer6.get("relationship_focus")
            layer8 = choices.get(8, {})
            community_role = layer8.get("community_role")

            # Community-web relationships should involve community in solution
            if relationships == "community-web" and community_role == "protagonist-solves":
                return False, "Community-focused relationships should involve community in solution"
            return True, ""

        self.rules.append(ValidationRule(
            "cozy.structure.community_integrity",
            "Community must remain intact after resolution",
            check_community_integrity,
            "Cozy stories should not destroy community bonds"
        ))


def validate_choices(template, choices: Dict[int, Dict[str, str]]) -> Tuple[bool, List[str], List[str]]:
    """Validate choices using core-specific rules.

    Args:
        template: HowdunitTemplate, ParanoiaTemplate, or CozyTemplate instance
        choices: Dict mapping phase (int) to field choices dict

    Returns:
        (is_valid: bool, errors: List[str], warnings: List[str])
    """
    errors = []
    warnings = []

    # Get ruleset for this core
    ruleset = RuleSet(template.core_id)

    # Run all rules
    for rule in ruleset.rules:
        passes, message = rule.check(template, choices)
        if not passes and message:
            errors.append(message)

    return len(errors) == 0, errors, warnings
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/mystery/test_validation.py -v`
Expected: PASS (20 tests passing)

- [ ] **Step 5: Commit**

```bash
git add src/auteur/mystery/validation.py tests/mystery/test_validation.py
git commit -m "feat(mystery): add validation rules for howdunit, paranoia, cozy"
```

---

## Task 3: Identity Generator Extension & CLI Entry Point

**Files:**
- Modify: `src/auteur/netorare/identity_generator.py` (add mystery routing)
- Create: `src/auteur/cli_mystery.py` (CLI entry point)
- Create: `tests/mystery/test_identity_generator.py`

**Interfaces:**
- Consumes:
  - `IdentityGenerator.from_choices(core_id, choices)` → returns `StoryIdentity`
  - `IdentityGenerator.to_yaml(identity)` → returns YAML string
  - `HowdunitTemplate`, `ParanoiaTemplate`, `CozyTemplate` from Task 1
  - `validate_choices()` from Task 2

- Produces:
  - Extended `IdentityGenerator` accepting "howdunit", "paranoia", "cozy" core IDs
  - `handle_mystery_init()` CLI entry point function
  - Valid `story_identity.yaml` files with `Genre.MYSTERY`

---

### Task 3: Step 1 — Write integration tests for mystery identity generation

Create `tests/mystery/test_identity_generator.py`:

```python
"""Tests for mystery identity generation."""

import pytest
from auteur.netorare.identity_generator import IdentityGenerator
from auteur.mystery.core_templates import (
    HowdunitTemplate, ParanoiaTemplate, CozyTemplate
)


class TestMysteryIdentityGeneratorBasics:
    """Test basic identity generation for mystery cores."""

    def test_from_choices_howdunit(self):
        """Test generating identity from howdunit choices."""
        choices = {
            1: {"emotional_core": "howdunit"},
            2: {"genre_contract": "detective"},
            3: {"scope": "standard"},
            4: {
                "want": "want-solve-puzzle",
                "resistance": "resistance-misleading-clues",
                "conflict": "conflict-deduction-misdirection",
                "stakes": "stakes-justice",
                "change": "change-clarity"
            }
        }
        identity = IdentityGenerator.from_choices("howdunit", choices)
        assert identity is not None
        assert identity.story_type.genre.value == "mystery"

    def test_from_choices_paranoia(self):
        """Test generating identity from paranoia choices."""
        choices = {
            1: {"emotional_core": "paranoia"},
            2: {"genre_contract": "gaslight"},
            4: {
                "want": "want-understand-reality",
                "resistance": "resistance-gaslighting",
                "conflict": "conflict-reality-perception",
                "stakes": "stakes-mental-stability",
                "change": "change-revelation"
            }
        }
        identity = IdentityGenerator.from_choices("paranoia", choices)
        assert identity is not None
        assert identity.story_type.genre.value == "mystery"

    def test_from_choices_cozy(self):
        """Test generating identity from cozy choices."""
        choices = {
            1: {"emotional_core": "cozy"},
            2: {"genre_contract": "village"},
            4: {
                "want": "want-solve-community",
                "resistance": "resistance-scattered-clues",
                "conflict": "conflict-investigation-daily-life",
                "stakes": "stakes-community-bonds",
                "change": "change-community-shift"
            }
        }
        identity = IdentityGenerator.from_choices("cozy", choices)
        assert identity is not None
        assert identity.story_type.genre.value == "mystery"

    def test_from_choices_validates_before_generating(self):
        """Test that invalid choices raise ValueError."""
        invalid_choices = {
            1: {"emotional_core": "invalid-core"}
        }
        with pytest.raises(ValueError):
            IdentityGenerator.from_choices("howdunit", invalid_choices)


class TestMysteryIdentityYAML:
    """Test YAML serialization for mystery identities."""

    def test_to_yaml_produces_valid_yaml(self):
        """Test that generated YAML is parseable."""
        import yaml
        choices = {
            1: {"emotional_core": "howdunit"},
            2: {"genre_contract": "detective"},
            4: {
                "want": "want-solve-puzzle",
                "resistance": "resistance-misleading-clues",
                "conflict": "conflict-deduction-misdirection",
                "stakes": "stakes-justice",
                "change": "change-clarity"
            }
        }
        identity = IdentityGenerator.from_choices("howdunit", choices)
        yaml_content = IdentityGenerator.to_yaml(identity)
        
        # Verify it's valid YAML
        parsed = yaml.safe_load(yaml_content)
        assert parsed is not None
        assert "story_type" in parsed

    def test_yaml_output_has_mystery_genre(self):
        """Test that mystery YAML contains Genre: mystery."""
        choices = {
            1: {"emotional_core": "howdunit"},
            2: {"genre_contract": "detective"},
            4: {
                "want": "want-solve-puzzle",
                "resistance": "resistance-misleading-clues",
                "conflict": "conflict-deduction-misdirection",
                "stakes": "stakes-justice",
                "change": "change-clarity"
            }
        }
        identity = IdentityGenerator.from_choices("howdunit", choices)
        yaml_content = IdentityGenerator.to_yaml(identity)
        
        # Genre should be mystery
        assert "genre:" in yaml_content.lower()
        assert "mystery" in yaml_content.lower()


class TestMysteryIdentityIntegration:
    """Integration tests for full mystery pipeline."""

    def test_full_howdunit_workflow(self):
        """Test end-to-end: choices → identity → YAML."""
        choices = {
            1: {"emotional_core": "howdunit"},
            2: {"genre_contract": "puzzle-box"},
            3: {"scope": "focused"},
            4: {
                "want": "want-identify-culprit",
                "resistance": "resistance-false-suspects",
                "conflict": "conflict-logic-chaos",
                "stakes": "stakes-order-restored",
                "change": "change-certainty"
            },
            5: {"investigation_style": "logical"},
            6: {"pacing_rhythm": "accelerating"},
            7: {"clue_distribution": "even"},
            8: {"solution_density": "moderate"},
            9: {"fairness_confidence": "fair-high"}
        }
        
        identity = IdentityGenerator.from_choices("howdunit", choices)
        yaml_content = IdentityGenerator.to_yaml(identity)
        
        # Should produce valid YAML with all required fields
        import yaml
        parsed = yaml.safe_load(yaml_content)
        assert "target_experience" in parsed
        assert "story_type" in parsed
        assert parsed["story_type"]["genre"] == "mystery"

    def test_multiple_cores_generate_different_identities(self):
        """Test that different cores produce distinct identities."""
        howdunit_choices = {
            1: {"emotional_core": "howdunit"},
            2: {"genre_contract": "detective"},
            4: {
                "want": "want-solve-puzzle",
                "resistance": "resistance-misleading-clues",
                "conflict": "conflict-deduction-misdirection",
                "stakes": "stakes-justice",
                "change": "change-clarity"
            }
        }
        
        paranoia_choices = {
            1: {"emotional_core": "paranoia"},
            2: {"genre_contract": "gaslight"},
            4: {
                "want": "want-understand-reality",
                "resistance": "resistance-gaslighting",
                "conflict": "conflict-reality-perception",
                "stakes": "stakes-mental-stability",
                "change": "change-revelation"
            }
        }
        
        h_identity = IdentityGenerator.from_choices("howdunit", howdunit_choices)
        p_identity = IdentityGenerator.from_choices("paranoia", paranoia_choices)
        
        # Both should be mystery genre but different target experiences
        h_yaml = IdentityGenerator.to_yaml(h_identity)
        p_yaml = IdentityGenerator.to_yaml(p_identity)
        
        assert "mystery" in h_yaml.lower()
        assert "mystery" in p_yaml.lower()
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/mystery/test_identity_generator.py -v`
Expected: May pass if IdentityGenerator already handles mystery cores, or fail if routing needs updates

- [ ] **Step 3: Extend IdentityGenerator to support mystery (if needed)**

Read the existing `src/auteur/netorare/identity_generator.py` to check if mystery cores are already handled. If not, modify it:

The IdentityGenerator should already have routing logic in `from_choices()`. Verify that it accepts core_id values "howdunit", "paranoia", "cozy" and routes them to Genre.MYSTERY. If the code needs modification:

```python
# In IdentityGenerator.from_choices(), ensure:
if core_id in ["howdunit", "paranoia", "cozy"]:
    genre = Genre.MYSTERY
elif core_id == "classic_humiliation":
    genre = Genre.NETORARE
# ... etc
```

- [ ] **Step 4: Create CLI entry point for mystery**

Create `src/auteur/cli_mystery.py`:

```python
"""CLI orchestration for the mystery pipeline (howdunit, paranoia, cozy cores)."""

from __future__ import annotations

import json
import logging
import subprocess
import sys
import time
import webbrowser
from pathlib import Path
from typing import Optional

from auteur.netorare.browser.server import NetorareServer, ServerError
from auteur.netorare.identity_generator import IdentityGenerator
from auteur.netorare.session import SessionManager, SessionError
from auteur.mystery.validation import validate_choices

logger = logging.getLogger(__name__)


class MysteryError(Exception):
    """Base error for mystery CLI operations."""
    pass


class MysteryCommand:
    """Orchestrates the complete mystery pipeline.

    Identical to NetorareCommand but routes to mystery core IDs (howdunit, paranoia, cozy).
    Reuses all infrastructure from netorare (Session, Server, UI).
    """

    def __init__(
        self,
        project_path: Path,
        core_id: str = "howdunit",
        provider: str = "anthropic",
        port: int = 8766,
        timeout: float = 3600.0,
        debug: bool = False,
    ):
        """Initialize the mystery command.

        Args:
            project_path: Path to project root
            core_id: Core template ID (howdunit, paranoia, cozy)
            provider: LLM provider (anthropic, openai)
            port: Port for browser server
            timeout: Timeout in seconds for waiting for completion
            debug: Enable debug logging
        """
        self.project_path = Path(project_path)
        self.core_id = core_id
        self.provider = provider
        self.port = port
        self.timeout = timeout
        self.debug = debug

        if debug:
            logging.basicConfig(level=logging.DEBUG)

        self.mystery_dir = self.project_path / "mystery"
        self.session_file = self.mystery_dir / "session.json"
        self.identity_file = self.project_path / "story_identity.yaml"

        self.session_manager: Optional[SessionManager] = None
        self.server_process: Optional[subprocess.Popen] = None

    def run(self) -> int:
        """Execute the complete mystery pipeline. Returns exit code (0 for success)."""
        try:
            self._validate_project_path()
            self._create_project_structure()
            self._create_session()
            self._start_browser_server()
            self._open_browser()
            self._poll_for_completion()
            choices = self._read_and_validate_choices()
            identity = self._generate_identity(choices)
            self._save_identity(identity)
            self._cleanup()
            self._display_success()
            return 0
        except MysteryError as e:
            self._cleanup()
            print(f"Error: {e}", file=sys.stderr)
            logger.exception(f"Mystery pipeline failed: {e}")
            return 1
        except KeyboardInterrupt:
            self._cleanup()
            print("\nMystery pipeline interrupted", file=sys.stderr)
            return 130
        except Exception as e:
            self._cleanup()
            print(f"Unexpected error: {e}", file=sys.stderr)
            logger.exception(f"Unexpected error in mystery pipeline: {e}")
            return 1

    def _validate_project_path(self) -> None:
        """Validate project path is usable."""
        if not self.project_path.exists():
            self.project_path.mkdir(parents=True, exist_ok=True)
        if not self.project_path.is_dir():
            raise MysteryError(f"Project path must be a directory: {self.project_path}")

    def _create_project_structure(self) -> None:
        """Create project directory structure."""
        self.project_path.mkdir(parents=True, exist_ok=True)
        self.mystery_dir.mkdir(parents=True, exist_ok=True)
        (self.project_path / ".auteur").mkdir(parents=True, exist_ok=True)

    def _create_session(self) -> None:
        """Create a new mystery session."""
        if self.session_file.exists():
            raise MysteryError(f"Session already exists at {self.session_file}")
        try:
            self.session_manager = SessionManager.create_session(self.project_path, self.core_id)
        except SessionError as e:
            raise MysteryError(f"Failed to create session: {e}")

    def _start_browser_server(self) -> None:
        """Start the browser server in a subprocess (reuses netorare server)."""
        if not self.session_file.exists():
            raise MysteryError(f"Session file not found: {self.session_file}")

        server_code = self._get_server_runner_code()

        try:
            self.server_process = subprocess.Popen(
                [sys.executable, "-c", server_code],
                env={
                    **subprocess.os.environ,
                    "NETORARE_SESSION_FILE": str(self.session_file),
                    "NETORARE_PORT": str(self.port),
                    "PYTHONUNBUFFERED": "1",
                },
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            time.sleep(1.0)
            if self.server_process.poll() is not None:
                _, stderr = self.server_process.communicate()
                raise MysteryError(f"Server failed to start: {stderr}")
            logger.info(f"Browser server started (PID {self.server_process.pid}) on port {self.port}")
        except Exception as e:
            raise MysteryError(f"Failed to start browser server: {e}")

    def _get_server_runner_code(self) -> str:
        """Get Python code to run the server in a subprocess."""
        return """
import sys
import os
from pathlib import Path
from auteur.netorare.browser.server import NetorareServer

session_file = Path(os.environ["NETORARE_SESSION_FILE"])
port = int(os.environ["NETORARE_PORT"])

try:
    server = NetorareServer(session_file=session_file, port=port)
    server.start()
except KeyboardInterrupt:
    sys.exit(0)
except Exception as e:
    print(f"Server error: {e}", file=sys.stderr)
    sys.exit(1)
"""

    def _open_browser(self) -> None:
        """Open browser to the mystery server."""
        url = f"http://localhost:{self.port}/?session={self.session_manager.get_state()['id']}"
        try:
            success = webbrowser.open(url)
            if success:
                logger.info(f"Opened browser: {url}")
            else:
                print(f"Please open this URL in your browser: {url}", file=sys.stderr)
        except Exception as e:
            logger.warning(f"Failed to open browser: {e}")
            print(f"Please open this URL in your browser: {url}", file=sys.stderr)

    def _poll_for_completion(self) -> None:
        """Poll session for completion with timeout."""
        if not self.session_manager:
            raise MysteryError("Session manager not initialized")

        start_time = time.time()
        poll_interval = 2.0
        logger.info(f"Polling for completion (timeout: {self.timeout}s)...")

        while time.time() - start_time < self.timeout:
            try:
                manager = SessionManager.load_session(self.session_file)
                if manager.is_complete():
                    self.session_manager = manager
                    return
            except SessionError as e:
                logger.debug(f"Error loading session: {e}")
            time.sleep(poll_interval)

        raise MysteryError(f"Session did not complete within {self.timeout}s")

    def _read_and_validate_choices(self) -> dict:
        """Read choices from completed session and validate."""
        if not self.session_manager:
            raise MysteryError("Session manager not initialized")

        choices = self.session_manager.get_choices()
        if not choices:
            raise MysteryError("No choices found in completed session")

        try:
            from auteur.mystery.core_templates import get_template
            template = get_template(self.core_id)
            is_valid, errors, warnings = validate_choices(template, choices)

            if warnings:
                print("\nWarnings during validation:", file=sys.stderr)
                for warning in warnings:
                    print(f"  - {warning}", file=sys.stderr)

            if not is_valid:
                error_msg = "; ".join(errors)
                raise MysteryError(f"Choices validation failed: {error_msg}")

            logger.info("Choices validated successfully")
            return choices
        except MysteryError:
            raise
        except Exception as e:
            raise MysteryError(f"Validation error: {e}")

    def _generate_identity(self, choices: dict) -> str:
        """Generate story_identity.yaml content from choices."""
        try:
            identity = IdentityGenerator.from_choices(self.core_id, choices)
            yaml_content = IdentityGenerator.to_yaml(identity)
            logger.info("Identity generated successfully")
            return yaml_content
        except ValueError as e:
            raise MysteryError(f"Failed to generate identity: {e}")
        except Exception as e:
            raise MysteryError(f"Unexpected error generating identity: {e}")

    def _save_identity(self, yaml_content: str) -> None:
        """Save generated identity to story_identity.yaml."""
        try:
            self.identity_file.write_text(yaml_content, encoding="utf-8")
            logger.info(f"Identity saved to {self.identity_file}")
        except Exception as e:
            raise MysteryError(f"Failed to save identity file: {e}")

    def _cleanup(self) -> None:
        """Clean up: stop server subprocess and close resources."""
        if self.server_process:
            try:
                self.server_process.terminate()
                try:
                    self.server_process.wait(timeout=5.0)
                except (subprocess.TimeoutExpired, Exception) as e:
                    if isinstance(e, subprocess.TimeoutExpired):
                        self.server_process.kill()
                logger.info("Browser server stopped")
            except Exception as e:
                logger.warning(f"Error stopping server: {e}")

    def _display_success(self) -> None:
        """Display success message with next steps."""
        print("\n[OK] Mystery pipeline completed successfully!")
        print(f"\nGenerated files:")
        print(f"  - Session: {self.session_file}")
        print(f"  - Identity: {self.identity_file}")
        print(f"\nNext steps:")
        print(f"  1. Validate identity: auteur identity validate {self.identity_file}")
        print(f"  2. Compile blueprint: auteur identity compile {self.identity_file} --output {self.project_path / 'blueprint.yaml'}")


def handle_mystery_init(
    project_path: Path,
    core_id: str = "howdunit",
    provider: str = "anthropic",
    port: int = 8766,
    timeout: float = 3600.0,
    debug: bool = False,
) -> int:
    """Handle 'auteur mystery init' command.

    Args:
        project_path: Path to project directory
        core_id: Core template ID (howdunit, paranoia, cozy)
        provider: LLM provider
        port: Server port
        timeout: Completion timeout in seconds
        debug: Enable debug logging

    Returns:
        Exit code (0 for success)
    """
    command = MysteryCommand(
        project_path=project_path,
        core_id=core_id,
        provider=provider,
        port=port,
        timeout=timeout,
        debug=debug,
    )
    return command.run()
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `pytest tests/mystery/test_identity_generator.py -v`
Expected: PASS (12 tests passing)

- [ ] **Step 6: Run end-to-end test manually**

```bash
python -c "from auteur.cli_mystery import handle_mystery_init; import sys; sys.exit(handle_mystery_init('./test_mystery', core_id='howdunit'))"
```

Expected: Browser opens, can select options, YAML generated

- [ ] **Step 7: Verify generated YAML passes auteur validation**

```bash
auteur identity validate ./test_mystery/story_identity.yaml
```

Expected: PASS (0 errors)

- [ ] **Step 8: Commit**

```bash
git add src/auteur/cli_mystery.py tests/mystery/test_identity_generator.py
git commit -m "feat(mystery): add CLI entry point and identity generation for mystery genre"
```

---

## Summary Checklist

- [ ] All 15 Task 1 (templates) tests passing
- [ ] All 20 Task 2 (validation) tests passing
- [ ] All 12 Task 3 (identity) tests passing
- [ ] Total: 47 tests passing (within target of 40-50)
- [ ] End-to-end: `auteur mystery init ./test_project --core howdunit` succeeds
- [ ] Generated `story_identity.yaml` passes `auteur identity validate`
- [ ] All commits pushed to main
- [ ] Code follows netorare architecture patterns exactly

