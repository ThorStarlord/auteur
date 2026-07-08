# Gentle Femdom Semantic Coupling Fix Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix the semantic coupling weakness where template emotional cores (playful_control, safe_vulnerability, cherished_leadership) are lost during identity generation, causing all three cores to collapse into identical tragic/dread narratives.

**Architecture:** Three-layer fix ensuring semantic data flows from template → identity generator → generated identity:
1. Define emotion arc constants (progression, secondary emotions, avoided experiences) per core
2. Make IdentityGenerator template-aware: load template, extract primary_emotion, use emotion arcs
3. Add semantic validation rule ensuring generated emotion matches template emotion

**Tech Stack:** Python 3.11+, Pydantic (StoryIdentity), pytest for testing, YAML serialization

## Global Constraints

- Exact file paths: Create under `src/auteur/gentlefemdom/` and tests under `tests/gentlefemdom/`
- IdentityGenerator changes must not break existing netorare or mystery pipelines (zero regressions)
- All generated `target_experience.primary` must match selected template's `primary_emotion`
- Emotion arcs must define: primary (string), progression (text), secondary ([strings]), avoid ([strings])
- Semantic validation must allow author overrides via `author_overrides` field
- Test target: 50+ tests total across three tasks

---

## Task 1: Gentle Femdom Emotion Arc Constants

**Files:**
- Create: `src/auteur/gentlefemdom/emotion_arcs.py`
- Create: `tests/gentlefemdom/test_emotion_arcs.py`

**Interfaces:**
- Produces: `EMOTION_ARCS` dict mapping core_id → emotion definition
  - Each definition has: `primary` (str), `progression` (str), `secondary` ([str]), `avoid` ([str])
- Produces: `get_emotion_arc(core_id: str) -> dict` function
- Later tasks will import and use this

### Step 1: Write failing tests for emotion arc structure

- [ ] Create `tests/gentlefemdom/test_emotion_arcs.py`

```python
"""Tests for gentle femdom emotion arc definitions."""

import pytest
from auteur.gentlefemdom.emotion_arcs import EMOTION_ARCS, get_emotion_arc


class TestEmotionArcStructure:
    """Verify emotion arc constants have correct structure."""

    def test_emotion_arcs_dict_exists(self):
        """Test that EMOTION_ARCS dict is defined."""
        assert isinstance(EMOTION_ARCS, dict)
        assert len(EMOTION_ARCS) == 3

    def test_all_three_cores_defined(self):
        """Test that all three gentle femdom cores have emotion arcs."""
        required_cores = ["sensual_dominance", "tender_surrender", "romantic_authority"]
        assert all(core in EMOTION_ARCS for core in required_cores)

    def test_emotion_arc_schema_sensual_dominance(self):
        """Test sensual_dominance emotion arc has required fields."""
        arc = EMOTION_ARCS["sensual_dominance"]
        assert "primary" in arc
        assert "progression" in arc
        assert "secondary" in arc
        assert "avoid" in arc
        assert arc["primary"] == "playful_control"
        assert isinstance(arc["progression"], str)
        assert isinstance(arc["secondary"], list)
        assert isinstance(arc["avoid"], list)

    def test_emotion_arc_schema_tender_surrender(self):
        """Test tender_surrender emotion arc has required fields."""
        arc = EMOTION_ARCS["tender_surrender"]
        assert "primary" in arc
        assert "progression" in arc
        assert "secondary" in arc
        assert "avoid" in arc
        assert arc["primary"] == "safe_vulnerability"
        assert isinstance(arc["progression"], str)
        assert isinstance(arc["secondary"], list)
        assert isinstance(arc["avoid"], list)

    def test_emotion_arc_schema_romantic_authority(self):
        """Test romantic_authority emotion arc has required fields."""
        arc = EMOTION_ARCS["romantic_authority"]
        assert "primary" in arc
        assert "progression" in arc
        assert "secondary" in arc
        assert "avoid" in arc
        assert arc["primary"] == "cherished_leadership"
        assert isinstance(arc["progression"], str)
        assert isinstance(arc["secondary"], list)
        assert isinstance(arc["avoid"], list)

    def test_progression_strings_are_substantive(self):
        """Test that progression strings are not empty or trivial."""
        for core_id, arc in EMOTION_ARCS.items():
            progression = arc["progression"]
            assert len(progression) > 20, f"{core_id} progression too short"
            assert "->" in progression or "→" in progression, f"{core_id} progression missing arc"

    def test_secondary_emotions_are_lists_of_strings(self):
        """Test secondary emotions are non-empty lists."""
        for core_id, arc in EMOTION_ARCS.items():
            secondary = arc["secondary"]
            assert isinstance(secondary, list)
            assert len(secondary) > 0, f"{core_id} secondary is empty"
            assert all(isinstance(s, str) for s in secondary)

    def test_avoided_experiences_are_lists_of_strings(self):
        """Test avoided experiences are non-empty lists."""
        for core_id, arc in EMOTION_ARCS.items():
            avoid = arc["avoid"]
            assert isinstance(avoid, list)
            assert len(avoid) > 0, f"{core_id} avoid is empty"
            assert all(isinstance(a, str) for a in avoid)

    def test_get_emotion_arc_function_exists(self):
        """Test get_emotion_arc function can be imported and called."""
        arc = get_emotion_arc("sensual_dominance")
        assert arc is not None
        assert arc["primary"] == "playful_control"

    def test_get_emotion_arc_handles_invalid_core(self):
        """Test get_emotion_arc raises ValueError for invalid core."""
        with pytest.raises(ValueError):
            get_emotion_arc("invalid_core")
```

Run: `pytest tests/gentlefemdom/test_emotion_arcs.py::TestEmotionArcStructure -v`
Expected: FAIL - "ModuleNotFoundError: No module named 'auteur.gentlefemdom.emotion_arcs'"

### Step 2: Create emotion_arcs.py with emotion arc definitions

- [ ] Create `src/auteur/gentlefemdom/emotion_arcs.py`

```python
"""Emotion arc definitions for gentle femdom genre cores.

Each core has a distinct emotional progression that guides the narrative engine.
This data must propagate through identity generation to ensure generated stories
match the selected emotional core, not default to generic tragic/dread.
"""


EMOTION_ARCS = {
    "sensual_dominance": {
        "primary": "playful_control",
        "progression": "intrigue -> playful_teasing -> deepening_connection -> intimate_confidence -> sustained_delight",
        "secondary": ["trust", "enjoyment", "agency", "anticipation"],
        "avoid": ["shame", "humiliation_without_consent", "coercion", "fear"],
    },
    "tender_surrender": {
        "primary": "safe_vulnerability",
        "progression": "defensiveness -> curiosity -> gradual_opening -> blissful_release -> cherished_security",
        "secondary": ["trust", "freedom", "emotional_growth", "acceptance"],
        "avoid": ["coercion", "manipulation", "abandonment", "exposure"],
    },
    "romantic_authority": {
        "primary": "cherished_leadership",
        "progression": "admiration -> willing_deference -> secure_interdependence -> mutual_respect -> sustained_love",
        "secondary": ["respect", "care", "partnership", "confidence"],
        "avoid": ["inequality", "control_without_care", "diminishment", "resentment"],
    },
}


def get_emotion_arc(core_id: str) -> dict:
    """Get emotion arc definition for a given gentle femdom core.

    Args:
        core_id: One of "sensual_dominance", "tender_surrender", "romantic_authority"

    Returns:
        Dict with keys: primary, progression, secondary, avoid

    Raises:
        ValueError: If core_id not found
    """
    if core_id not in EMOTION_ARCS:
        raise ValueError(
            f"Unknown gentle femdom core: {core_id}. "
            f"Valid cores: {list(EMOTION_ARCS.keys())}"
        )
    return EMOTION_ARCS[core_id]
```

Run: `pytest tests/gentlefemdom/test_emotion_arcs.py::TestEmotionArcStructure -v`
Expected: PASS (all 10 tests)

### Step 3: Add more comprehensive tests for arc contents

- [ ] Add to `tests/gentlefemdom/test_emotion_arcs.py`

```python
class TestEmotionArcContents:
    """Verify emotional arcs have semantically correct content."""

    def test_sensual_dominance_primary_emotion(self):
        """Verify sensual_dominance has correct primary emotion."""
        arc = EMOTION_ARCS["sensual_dominance"]
        assert arc["primary"] == "playful_control"
        assert "playful" in arc["progression"].lower()
        assert "control" in arc["progression"].lower()

    def test_sensual_dominance_avoids_non_consent(self):
        """Verify sensual_dominance explicitly avoids non-consent."""
        arc = EMOTION_ARCS["sensual_dominance"]
        avoid_lower = [a.lower() for a in arc["avoid"]]
        assert any("humiliation" in a or "coercion" in a for a in avoid_lower)

    def test_tender_surrender_primary_emotion(self):
        """Verify tender_surrender has correct primary emotion."""
        arc = EMOTION_ARCS["tender_surrender"]
        assert arc["primary"] == "safe_vulnerability"
        assert "vulnerability" in arc["progression"].lower()
        assert "trust" in arc["progression"].lower()

    def test_tender_surrender_progression_describes_journey(self):
        """Verify tender_surrender progression shows transformation."""
        arc = EMOTION_ARCS["tender_surrender"]
        progression = arc["progression"].lower()
        assert "defensive" in progression or "guard" in progression
        assert "open" in progression or "release" in progression

    def test_romantic_authority_primary_emotion(self):
        """Verify romantic_authority has correct primary emotion."""
        arc = EMOTION_ARCS["romantic_authority"]
        assert arc["primary"] == "cherished_leadership"
        assert "leadership" in arc["progression"].lower()
        assert "respect" in arc["progression"].lower()

    def test_romantic_authority_progression_shows_partnership(self):
        """Verify romantic_authority progression emphasizes partnership."""
        arc = EMOTION_ARCS["romantic_authority"]
        progression = arc["progression"].lower()
        assert "interdepend" in progression or "mutual" in progression

    def test_all_secondary_emotions_are_lowercase(self):
        """Verify secondary emotions follow naming convention."""
        for core_id, arc in EMOTION_ARCS.items():
            for emotion in arc["secondary"]:
                assert emotion == emotion.lower(), f"{core_id}: {emotion} not lowercase"

    def test_no_duplicates_in_secondary_or_avoid(self):
        """Verify no duplicate entries in secondary or avoid lists."""
        for core_id, arc in EMOTION_ARCS.items():
            secondary = arc["secondary"]
            avoid = arc["avoid"]
            assert len(secondary) == len(set(secondary)), f"{core_id}: duplicate in secondary"
            assert len(avoid) == len(set(avoid)), f"{core_id}: duplicate in avoid"
```

Run: `pytest tests/gentlefemdom/test_emotion_arcs.py -v`
Expected: PASS (all 18 tests)

### Step 4: Commit Task 1

- [ ] Run full test suite to verify no regressions:

```bash
pytest tests/gentlefemdom/test_emotion_arcs.py -v
pytest tests/ -k "gentlefemdom or mystery or netorare" --tb=short
```

Expected: All tests pass, no regressions

- [ ] Commit:

```bash
git add src/auteur/gentlefemdom/emotion_arcs.py tests/gentlefemdom/test_emotion_arcs.py
git commit -m "feat(gentlefemdom): add emotion arc definitions for semantic coupling fix

Define explicit emotional progressions for sensual_dominance, tender_surrender,
and romantic_authority cores. Each arc specifies:
- primary: core emotional tone (playful_control, safe_vulnerability, cherished_leadership)
- progression: narrative arc showing emotional transformation
- secondary: supporting emotions
- avoid: experiences that break genre contract

These constants ensure template emotion propagates through identity generation."
```

---

## Task 2: Make IdentityGenerator Template-Aware

**Files:**
- Modify: `src/auteur/netorare/identity_generator.py`
- Modify: `src/auteur/identity.py` (if needed for StoryIdentity fields)
- Create: `tests/gentlefemdom/test_identity_propagation.py`

**Interfaces:**
- Consumes: `EMOTION_ARCS` from Task 1, template classes from `core_templates.py`
- Modifies: `IdentityGenerator.from_choices(core_id, choices) → StoryIdentity`
  - Must now extract template.primary_emotion
  - Must populate target_experience with: primary, progression, secondary, avoid
- Produces: StoryIdentity with semantic emotion fields populated
- Later tasks will validate this works

### Step 1: Write failing tests for template-aware identity generation

- [ ] Create `tests/gentlefemdom/test_identity_propagation.py`

```python
"""Tests verifying emotion propagates from template to generated identity."""

import pytest
from auteur.netorare.identity_generator import IdentityGenerator
from auteur.gentlefemdom.core_templates import get_template
from auteur.gentlefemdom.emotion_arcs import get_emotion_arc


class TestIdentityEmotionPropagation:
    """Verify template emotion flows through to generated StoryIdentity."""

    def test_sensual_dominance_emotion_propagates(self):
        """Test that sensual_dominance identity has correct primary emotion."""
        choices = {
            4: {
                "want": "want-establish-trust",
                "resistance": "resistance-partner-doubt",
                "conflict": "conflict-control-vs-consent",
                "stakes": "stakes-emotional-intimacy",
                "change": "change-tentative-to-confident",
            }
        }
        identity = IdentityGenerator.from_choices("sensual_dominance", choices)
        
        # MUST have primary emotion from arc, not default dread
        assert identity.target_experience.primary == "playful_control"

    def test_tender_surrender_emotion_propagates(self):
        """Test that tender_surrender identity has correct primary emotion."""
        choices = {
            4: {
                "want": "want-release-control",
                "resistance": "resistance-fear-vulnerability",
                "conflict": "conflict-self-protection-vs-desire",
                "stakes": "stakes-emotional-walls",
                "change": "change-defended-to-open",
            }
        }
        identity = IdentityGenerator.from_choices("tender_surrender", choices)
        
        # MUST have primary emotion from arc, not default dread
        assert identity.target_experience.primary == "safe_vulnerability"

    def test_romantic_authority_emotion_propagates(self):
        """Test that romantic_authority identity has correct primary emotion."""
        choices = {
            4: {
                "want": "want-provide-protect",
                "resistance": "resistance-partner-independence",
                "conflict": "conflict-leadership-vs-partnership",
                "stakes": "stakes-relationship-balance",
                "change": "change-uncertain-to-confident",
            }
        }
        identity = IdentityGenerator.from_choices("romantic_authority", choices)
        
        # MUST have primary emotion from arc, not default dread
        assert identity.target_experience.primary == "cherished_leadership"

    def test_emotion_progression_populated(self):
        """Test that target_experience.progression is populated from emotion arc."""
        choices = {
            4: {
                "want": "want-establish-trust",
                "resistance": "resistance-partner-doubt",
                "conflict": "conflict-control-vs-consent",
                "stakes": "stakes-emotional-intimacy",
                "change": "change-tentative-to-confident",
            }
        }
        identity = IdentityGenerator.from_choices("sensual_dominance", choices)
        
        # Progression must be a string describing emotional arc, not default
        assert identity.target_experience.progression is not None
        assert isinstance(identity.target_experience.progression, str)
        assert len(identity.target_experience.progression) > 0
        # Should contain elements from the arc
        arc = get_emotion_arc("sensual_dominance")
        assert identity.target_experience.progression == arc["progression"]

    def test_secondary_emotions_populated(self):
        """Test that target_experience.secondary is populated from emotion arc."""
        choices = {
            4: {
                "want": "want-establish-trust",
                "resistance": "resistance-partner-doubt",
                "conflict": "conflict-control-vs-consent",
                "stakes": "stakes-emotional-intimacy",
                "change": "change-tentative-to-confident",
            }
        }
        identity = IdentityGenerator.from_choices("sensual_dominance", choices)
        
        # Secondary emotions must come from arc
        arc = get_emotion_arc("sensual_dominance")
        assert identity.target_experience.secondary == arc["secondary"]
        assert len(identity.target_experience.secondary) > 0

    def test_avoided_experiences_populated(self):
        """Test that target_experience.avoid is populated from emotion arc."""
        choices = {
            4: {
                "want": "want-establish-trust",
                "resistance": "resistance-partner-doubt",
                "conflict": "conflict-control-vs-consent",
                "stakes": "stakes-emotional-intimacy",
                "change": "change-tentative-to-confident",
            }
        }
        identity = IdentityGenerator.from_choices("sensual_dominance", choices)
        
        # Avoided experiences must come from arc
        arc = get_emotion_arc("sensual_dominance")
        assert identity.target_experience.avoid == arc["avoid"]
        assert len(identity.target_experience.avoid) > 0

    def test_different_cores_produce_different_identities(self):
        """Test that three different cores produce different identities."""
        base_choices = {
            4: {
                "want": "want-establish-trust",
                "resistance": "resistance-partner-doubt",
                "conflict": "conflict-control-vs-consent",
                "stakes": "stakes-emotional-intimacy",
                "change": "change-tentative-to-confident",
            }
        }
        
        identity_sd = IdentityGenerator.from_choices("sensual_dominance", base_choices)
        
        # Use valid choices for tender_surrender
        ts_choices = {
            4: {
                "want": "want-release-control",
                "resistance": "resistance-fear-vulnerability",
                "conflict": "conflict-self-protection-vs-desire",
                "stakes": "stakes-emotional-walls",
                "change": "change-defended-to-open",
            }
        }
        identity_ts = IdentityGenerator.from_choices("tender_surrender", ts_choices)
        
        # Emotional cores must differ
        assert identity_sd.target_experience.primary != identity_ts.target_experience.primary
        assert identity_sd.target_experience.progression != identity_ts.target_experience.progression
```

Run: `pytest tests/gentlefemdom/test_identity_propagation.py -v`
Expected: FAIL - Identities don't populate emotion arcs yet

### Step 2: Modify IdentityGenerator to be template-aware

- [ ] Examine `src/auteur/netorare/identity_generator.py` to understand current structure

Look for:
- `from_choices()` method signature
- How `StoryIdentity` is constructed
- Where defaults are set for `target_experience.primary`, `target_experience.progression`

- [ ] Modify `src/auteur/netorare/identity_generator.py`:

Find the `from_choices()` method and update it:

```python
from auteur.gentlefemdom.core_templates import get_template as get_gf_template
from auteur.gentlefemdom.emotion_arcs import get_emotion_arc

@staticmethod
def from_choices(core_id: str, choices: dict) -> StoryIdentity:
    """Generate story identity from core_id and user choices.
    
    Now template-aware: extracts emotional data from template to ensure
    generated identity matches the selected core's emotional intent.
    """
    # Load template to access primary emotion
    try:
        # Try gentle femdom first
        template = get_gf_template(core_id)
        emotion_arc = get_emotion_arc(core_id)
    except (ValueError, ImportError):
        # Fall back to existing logic for netorare/mystery
        # (existing code path unchanged)
        pass
    
    # Validate choices
    if not TEMPLATE_MAP[core_id].validate_choices(choices)[0]:
        raise ValueError(f"Invalid choices for {core_id}")
    
    # Create identity (existing logic)
    identity = StoryIdentity(...)
    
    # NEW: Set emotional fields from template + arc
    identity.target_experience.primary = template.primary_emotion
    identity.target_experience.progression = emotion_arc["progression"]
    identity.target_experience.secondary = emotion_arc["secondary"]
    identity.target_experience.avoid = emotion_arc["avoid"]
    
    # Rest of existing identity generation...
    return identity
```

**Important:** Do NOT modify the core structure or break existing netorare/mystery paths. This should be additive.

Run: `pytest tests/gentlefemdom/test_identity_propagation.py::TestIdentityEmotionPropagation::test_sensual_dominance_emotion_propagates -v`
Expected: PASS (emotion now propagates)

### Step 3: Run all propagation tests

- [ ] Run full test suite:

```bash
pytest tests/gentlefemdom/test_identity_propagation.py -v
pytest tests/ -k "identity" --tb=short
```

Expected: All propagation tests pass, no regressions in existing identity tests

### Step 4: Commit Task 2

- [ ] Commit:

```bash
git add src/auteur/netorare/identity_generator.py tests/gentlefemdom/test_identity_propagation.py
git commit -m "feat(gentlefemdom): make IdentityGenerator template-aware

IdentityGenerator.from_choices() now:
1. Loads template for the selected core_id
2. Extracts primary_emotion, progression, secondary, avoid from template + emotion_arcs
3. Populates StoryIdentity.target_experience with semantic emotional data

This ensures three different gentle femdom cores produce three different
emotional identities, not a generic tragic/dread scaffold for all.

Verified: All three cores (sensual_dominance, tender_surrender, romantic_authority)
now propagate correct primary emotions to generated identities."
```

---

## Task 3: Add Semantic Validation Rule

**Files:**
- Create: `src/auteur/gentlefemdom/semantic_validation.py`
- Modify: `src/auteur/gentlefemdom/validation.py` (integrate semantic rule)
- Create: `tests/gentlefemdom/test_semantic_validation.py`

**Interfaces:**
- Consumes: Template classes, emotion arc data from Tasks 1-2
- Produces: `SemanticCoherenceRule` class with `validate(identity, template)` method
- Integrates into existing `validate_choices()` function
- Later tasks will use this in validation pipeline

### Step 1: Write failing tests for semantic validation

- [ ] Create `tests/gentlefemdom/test_semantic_validation.py`

```python
"""Tests for semantic validation ensuring emotion coherence."""

import pytest
from auteur.gentlefemdom.semantic_validation import SemanticCoherenceRule
from auteur.netorare.identity_generator import IdentityGenerator
from auteur.gentlefemdom.core_templates import get_template


class TestSemanticCoherenceValidation:
    """Verify semantic coherence rule catches emotion mismatches."""

    def test_semantic_rule_accepts_matching_emotion(self):
        """Test that rule passes when identity emotion matches template."""
        # Generate identity for sensual_dominance
        choices = {
            4: {
                "want": "want-establish-trust",
                "resistance": "resistance-partner-doubt",
                "conflict": "conflict-control-vs-consent",
                "stakes": "stakes-emotional-intimacy",
                "change": "change-tentative-to-confident",
            }
        }
        identity = IdentityGenerator.from_choices("sensual_dominance", choices)
        template = get_template("sensual_dominance")
        
        rule = SemanticCoherenceRule()
        result = rule.validate(identity, template)
        
        assert result["passed"] is True

    def test_semantic_rule_rejects_mismatched_emotion(self):
        """Test that rule fails when identity emotion doesn't match template."""
        # Manually create identity with wrong emotion
        identity = IdentityGenerator.from_choices("sensual_dominance", {...})
        
        # Manually corrupt the emotion (simulate the old bug)
        identity.target_experience.primary = "dread"
        
        template = get_template("sensual_dominance")
        
        rule = SemanticCoherenceRule()
        result = rule.validate(identity, template)
        
        assert result["passed"] is False
        assert "emotion" in result.get("error", "").lower()

    def test_semantic_rule_explains_mismatch(self):
        """Test that validation error explains what's wrong."""
        identity = IdentityGenerator.from_choices("tender_surrender", {...})
        identity.target_experience.primary = "dread"  # Wrong
        
        template = get_template("tender_surrender")
        rule = SemanticCoherenceRule()
        result = rule.validate(identity, template)
        
        assert result["passed"] is False
        error = result.get("error", "")
        assert "safe_vulnerability" in error  # Expected
        assert "dread" in error  # Actual

    def test_semantic_rule_allows_author_override(self):
        """Test that explicit author override bypasses validation."""
        identity = IdentityGenerator.from_choices("sensual_dominance", {...})
        identity.target_experience.primary = "dread"  # Mismatch
        
        # Author explicitly overrides
        identity.author_overrides = {"emotional_arc": True}
        
        template = get_template("sensual_dominance")
        rule = SemanticCoherenceRule()
        result = rule.validate(identity, template)
        
        # Should pass because author explicitly approved
        assert result["passed"] is True

    def test_all_three_cores_pass_semantic_validation(self):
        """Test that all three gentle femdom cores pass validation."""
        test_cases = [
            ("sensual_dominance", {
                4: {
                    "want": "want-establish-trust",
                    "resistance": "resistance-partner-doubt",
                    "conflict": "conflict-control-vs-consent",
                    "stakes": "stakes-emotional-intimacy",
                    "change": "change-tentative-to-confident",
                }
            }),
            ("tender_surrender", {
                4: {
                    "want": "want-release-control",
                    "resistance": "resistance-fear-vulnerability",
                    "conflict": "conflict-self-protection-vs-desire",
                    "stakes": "stakes-emotional-walls",
                    "change": "change-defended-to-open",
                }
            }),
            ("romantic_authority", {
                4: {
                    "want": "want-provide-protect",
                    "resistance": "resistance-partner-independence",
                    "conflict": "conflict-leadership-vs-partnership",
                    "stakes": "stakes-relationship-balance",
                    "change": "change-uncertain-to-confident",
                }
            }),
        ]
        
        rule = SemanticCoherenceRule()
        for core_id, choices in test_cases:
            identity = IdentityGenerator.from_choices(core_id, choices)
            template = get_template(core_id)
            result = rule.validate(identity, template)
            assert result["passed"] is True, f"{core_id} failed validation"
```

Run: `pytest tests/gentlefemdom/test_semantic_validation.py -v`
Expected: FAIL - SemanticCoherenceRule not implemented yet

### Step 2: Create SemanticCoherenceRule

- [ ] Create `src/auteur/gentlefemdom/semantic_validation.py`

```python
"""Semantic validation ensuring emotion coherence between template and identity."""

from typing import Dict, Any


class SemanticCoherenceRule:
    """Validates that generated identity's emotion matches selected template's emotion.
    
    This rule catches the silent semantic failure where structure is valid but
    meaning is broken (e.g., selecting sensual_dominance but getting dread output).
    """

    def __init__(self):
        self.name = "semantic_coherence"
        self.description = "Verifies generated identity emotion matches template emotional core"

    def validate(self, identity: Any, template: Any) -> Dict[str, Any]:
        """Validate that identity emotion matches template primary emotion.

        Args:
            identity: StoryIdentity object with target_experience
            template: Template object with primary_emotion

        Returns:
            Dict with keys:
            - passed: bool (True if valid or author overrode)
            - error: str (if not passed, explains mismatch)
        """
        # Check if author explicitly approved override
        if hasattr(identity, "author_overrides") and identity.author_overrides:
            if identity.author_overrides.get("emotional_arc"):
                return {"passed": True, "reason": "author_override"}

        # Check emotion match
        identity_emotion = identity.target_experience.primary
        template_emotion = template.primary_emotion

        if identity_emotion == template_emotion:
            return {"passed": True}

        # Mismatch: explain what's wrong
        error = (
            f"Semantic coherence violation: Selected template has primary emotion "
            f"'{template_emotion}' but generated identity has '{identity_emotion}'. "
            f"This indicates the template's emotional intent was not propagated during "
            f"identity generation. Override with author_overrides['emotional_arc'] = True "
            f"if intentional."
        )
        return {"passed": False, "error": error}
```

Run: `pytest tests/gentlefemdom/test_semantic_validation.py -v`
Expected: PASS (all 5 tests pass)

### Step 3: Integrate semantic rule into validation pipeline

- [ ] Modify `src/auteur/gentlefemdom/validation.py` to use semantic rule

Find the `validate_choices()` function and add:

```python
from auteur.gentlefemdom.semantic_validation import SemanticCoherenceRule

# Inside validate_choices or create a new function
def validate_with_semantics(identity, template, choices):
    """Run all validations including semantic coherence."""
    # Run existing validation
    template_is_valid, errors, warnings = template.validate_choices(choices)
    
    if not template_is_valid:
        return False, errors, warnings
    
    # NEW: Run semantic coherence check
    semantic_rule = SemanticCoherenceRule()
    semantic_result = semantic_rule.validate(identity, template)
    
    if not semantic_result["passed"]:
        errors.append(semantic_result["error"])
        return False, errors, warnings
    
    return True, errors, warnings
```

### Step 4: Run comprehensive tests

- [ ] Run all validation tests:

```bash
pytest tests/gentlefemdom/test_semantic_validation.py -v
pytest tests/gentlefemdom/test_validation.py -v
pytest tests/gentlefemdom/ -v
```

Expected: All tests pass, including existing validation tests (no regressions)

### Step 5: Commit Task 3

- [ ] Commit:

```bash
git add src/auteur/gentlefemdom/semantic_validation.py tests/gentlefemdom/test_semantic_validation.py
git commit -m "feat(gentlefemdom): add semantic coherence validation rule

Add SemanticCoherenceRule to catch silent semantic failures where structure
is valid but meaning is broken (e.g., template emotion not propagated to identity).

Rule validates: identity.target_experience.primary == template.primary_emotion

Allows author override via author_overrides['emotional_arc'] = True for
intentional deviations.

This completes the semantic coupling fix: all three gentle femdom cores now
produce semantically distinct identities matching their emotional intent."
```

---

## Summary Checklist

- [ ] All 3 tasks completed
- [ ] 50+ tests passing across all three tasks:
  - Task 1 (emotion arcs): 18 tests
  - Task 2 (template-aware identity): 7 tests
  - Task 3 (semantic validation): 5 tests
- [ ] Zero regressions on existing netorare/mystery tests
- [ ] Three clean commits (one per task)
- [ ] Generated identities now reflect selected emotional core:
  - Sensual Dominance → playful_control (not dread)
  - Tender Surrender → safe_vulnerability (not dread)
  - Romantic Authority → cherished_leadership (not dread)
