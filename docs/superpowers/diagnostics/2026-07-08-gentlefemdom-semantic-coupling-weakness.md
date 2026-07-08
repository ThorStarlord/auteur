# Gentle Femdom Pipeline - Diagnostic Report
**Date:** 2026-07-08  
**Status:** CRITICAL ARCHITECTURAL BOUNDARY ISSUE IDENTIFIED  
**Severity:** High - Silent semantic failure (structure passes, meaning fails)

## Problem Statement

The gentle femdom genre pipeline produces valid YAML that passes all validation checks, but the generated narrative identities are semantically identical regardless of which emotional core is selected. This indicates a **broken coupling between the template layer and identity generation layer**.

## Evidence

Three different cores were tested:

| Core | Template Emotion | Generated `target_experience.primary` | Generated `mode` |
|------|-----------------|---------------------------------------|------------------|
| Sensual Dominance | `playful_control` | `dread` | `tragic` |
| Tender Surrender | `safe_vulnerability` | `dread` | `tragic` |
| Romantic Authority | `cherished_leadership` | `dread` | `tragic` |

**All three produce identical tragic/dread scaffolds.** This is the wrong output.

### Secondary Evidence: Generic Boilerplate

All three generated identities contain:
- Empty `required_tropes: []`
- Empty `optional_tropes: []`
- Empty `common_failure_modes: []`
- Identical generic `genre_contract_snapshot`
- Identical `open_questions` (not core-specific)
- Generic alternatives ("shift emotional focus", "change resolution type", "expand scope")

### Mechanical Generation Issues

Some phrasing suggests direct slug concatenation without semantic cleanup:
- "fear vulnerability" (should be: "fear of vulnerability")
- "provide protect" (should be: "provide protection" or "protect and provide")
- "blocked by partner independence" (correct but abstract; should reference trust or autonomy dynamics)

## Root Cause Analysis

**Weakest boundary:** `IdentityGenerator.from_choices()` → `StoryIdentity` generation

### The Broken Coupling

```
Template Layer (CORRECT)
├─ SensualDominanceTemplate.primary_emotion = "playful_control"
├─ TenderSurrenderTemplate.primary_emotion = "safe_vulnerability"
└─ RomanticAuthorityTemplate.primary_emotion = "cherished_leadership"
    ↓
    [Choice data passes through]
    ↓
Identity Layer (WRONG)
├─ Ignores template.primary_emotion
├─ Uses hardcoded or default: target_experience.primary = "dread"
├─ Uses hardcoded: mode = "tragic"
└─ Generates boilerplate genre_contract_snapshot
```

**The identity generator does not receive or use the template's emotional architecture.**

### Why This Happened

Looking at `src/auteur/netorare/identity_generator.py` and `IdentityGenerator.from_choices()`:
1. It receives only `core_id` (string) and `choices` (dict)
2. It does not load the template to access `primary_emotion`, phase names, or genre constraints
3. It uses default scaffolds (likely borrowed from netorare's tragic structure)
4. Genre-specific configuration (tropes, psychology budget, scope) is hardcoded or absent

## Impact

This is a **silent failure**: 
- All tests pass (structure is valid)
- No validation errors (YAML shape is correct)
- Author receives wrong emotional identity (meaning is broken)

An author selecting "Sensual Dominance" with playful_control intent gets a tragic dread story instead.

## Required Fixes

### Fix 1: Template Awareness (MUST HAVE)

`IdentityGenerator.from_choices()` must:
1. Load the template via `core_id` (it can do this already)
2. Extract `template.primary_emotion`
3. Pass it to identity scaffold generation
4. Use template emotion as source of truth for `target_experience.primary`

```python
def from_choices(core_id: str, choices: dict) -> StoryIdentity:
    template = get_template(core_id)  # Already possible
    
    # Extract emotional data from template
    primary_emotion = template.primary_emotion  # BUG: Currently ignored
    
    # Use template emotion in scaffold
    identity = StoryIdentity(...)
    identity.target_experience.primary = primary_emotion  # FIX: Must do this
    
    return identity
```

### Fix 2: Genre-Specific Emotion Arc (SHOULD HAVE)

Each gentle femdom core needs a mapping of its emotional progression:

```python
EMOTION_ARCS = {
    "sensual_dominance": {
        "primary": "playful_control",
        "progression": "intrigue -> playful_teasing -> deepening_connection -> intimate_confidence",
        "secondary": ["trust", "enjoyment", "agency"],
        "avoid": ["shame", "humiliation", "coercion"],
    },
    "tender_surrender": {
        "primary": "safe_vulnerability",
        "progression": "defensiveness -> curiosity -> gradual_opening -> blissful_release -> cherished_security",
        "secondary": ["trust", "freedom", "emotional_growth"],
        "avoid": ["coercion", "manipulation", "abandonment"],
    },
    "romantic_authority": {
        "primary": "cherished_leadership",
        "progression": "admiration -> willing_deference -> secure_interdependence -> sustained_love",
        "secondary": ["respect", "care", "partnership"],
        "avoid": ["inequality", "control", "diminishment"],
    },
}
```

### Fix 3: Genre Contract Specificity (SHOULD HAVE)

Replace generic "Actions have consequences…" with gentle femdom specifics:

```yaml
genre_contract_snapshot:
  genre_id: gentlefemdom
  core_truth: Power is a language for intimacy. Consent is explicit. Care is central.
  audience_product: Emotional safety through power exchange.
  primary_excitement_beats:
  - negotiation / trust-building scene
  - first power dynamic exchange
  - vulnerability deepening moment
  - transformation through trust
  - interdependent love established
  required_tropes:
  - enthusiastic_consent
  - communication_about_boundaries
  - aftercare_or_emotional_check_in
  optional_tropes:
  - power_roles_explicitly_named
  - safe_word_or_boundary_system
  forbidden_mismatches:
  - coercion
  - non_consent
  - humiliation_without_consent
  - control_without_care
  common_failure_modes:
  - consent_assumed_rather_than_negotiated
  - care_missing_in_power_exchange
  - vulnerability_treated_as_weakness
  - power_dynamic_mistaken_for_relationship_inequality
```

### Fix 4: Shallow Validation (OPTIONAL BUT IMPORTANT)

Add a validation rule: **Semantic Coherence Check**

```python
class SemanticCoherenceRule(ValidationRule):
    """Verify that generated identity's emotion matches selected core."""
    
    def validate(self, identity: StoryIdentity, template: Template) -> bool:
        # MUST match or explicitly justify divergence
        if identity.target_experience.primary != template.primary_emotion:
            if not identity.author_overrides.get("emotional_arc"):
                return False  # Fail: emotion mismatch with no override
        return True
```

## Recommendations

### Priority 1 (Do First)
- Fix 1: Make `IdentityGenerator.from_choices()` template-aware
- Add emotional arc mapping to all three gentle femdom cores
- Update identity generation to use template emotion as source of truth

### Priority 2 (Do Next)
- Fix 3: Replace generic genre contract with gentle femdom specifics
- Add semantic coherence validation
- Write tests that verify: "If I select Sensual Dominance, I get playful_control, not dread"

### Priority 3 (Follow-up)
- Review netorare and mystery pipelines for the same coupling issue
- If present, apply same fix pattern to all genres

## Test Case (Validation)

After fixes, this test must pass:

```python
def test_emotional_core_propagates_to_identity():
    """Verify selected template emotion propagates to generated identity."""
    choices = {4: {...}}  # Any valid phase 4 choices
    
    identity = IdentityGenerator.from_choices("tender_surrender", choices)
    
    # The semantic invariant
    assert identity.target_experience.primary == "safe_vulnerability"
    assert "safe_vulnerability" in identity.target_experience.progression
    assert identity.genre_contract_snapshot.core_truth.contains("vulnerability")
    assert "coercion" in identity.genre_contract_snapshot.forbidden_mismatches
```

---

**Conclusion:** The gentle femdom pipeline is structurally sound but semantically broken. The fix is straightforward (template → identity coupling) and high-value (makes the system actually genre-aware rather than just genre-decorated).
