"""Quick test to verify validate_choices() method works correctly."""
from auteur.netorare.core_templates import HumiliationTemplate, HorrorTemplate, MysteryTemplate

# Test HumiliationTemplate
print("Testing HumiliationTemplate.validate_choices()...")
hum = HumiliationTemplate()

# Valid choices
valid_choices = {
    4: {"want": "want-dignity", "resistance": "resistance-inadequacy", "change": "change-accept"},
    5: {"subplot": "subplot-rival-perspective"},
    6: {"pov_structure": "pov-limited-mc"},
}
is_valid, errors, warnings = hum.validate_choices(valid_choices)
print(f"  Valid choices: is_valid={is_valid}, errors={errors}, warnings={warnings}")
assert is_valid, "Valid choices should pass validation"
assert len(errors) == 0, "Valid choices should have no errors"

# Invalid phase
invalid_phase = {10: {"field": "value"}}
is_valid, errors, warnings = hum.validate_choices(invalid_phase)
print(f"  Invalid phase: is_valid={is_valid}, errors={errors}")
assert not is_valid, "Invalid phase should fail validation"
assert any("Unknown phase" in e for e in errors), "Should report unknown phase"

# Invalid field
invalid_field = {4: {"unknown_field": "want-dignity"}}
is_valid, errors, warnings = hum.validate_choices(invalid_field)
print(f"  Invalid field: is_valid={is_valid}, errors={errors}")
assert not is_valid, "Invalid field should fail validation"
assert any("Unknown field" in e for e in errors), "Should report unknown field"

# Invalid value
invalid_value = {4: {"want": "invalid-id"}}
is_valid, errors, warnings = hum.validate_choices(invalid_value)
print(f"  Invalid value: is_valid={is_valid}, errors={errors}")
assert not is_valid, "Invalid value should fail validation"
assert any("Invalid value" in e for e in errors), "Should report invalid value"

print("\nTesting HorrorTemplate.validate_choices()...")
horror = HorrorTemplate()
valid_choices = {
    4: {"want": "want-escape", "change": "change-transform"},
}
is_valid, errors, warnings = horror.validate_choices(valid_choices)
print(f"  Valid choices: is_valid={is_valid}")
assert is_valid, "Valid choices should pass validation"

print("\nTesting MysteryTemplate.validate_choices()...")
mystery = MysteryTemplate()
valid_choices = {
    4: {"want": "want-truth", "change": "change-witness"},
}
is_valid, errors, warnings = mystery.validate_choices(valid_choices)
print(f"  Valid choices: is_valid={is_valid}")
assert is_valid, "Valid choices should pass validation"

print("\nAll validate_choices() tests passed!")
