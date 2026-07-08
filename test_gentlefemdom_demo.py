#!/usr/bin/env python3
"""
Automated demonstration of Gentle Femdom genre pipeline.

This test showcases the complete narrative engine workflow:
1. Initialize gentle femdom genre with sensual_dominance core
2. Simulate user choices through all 9 phases
3. Validate choices against genre-specific rules
4. Generate story_identity.yaml
5. Display the result

Run with: python test_gentlefemdom_demo.py
"""

import json
import tempfile
from pathlib import Path
from auteur.gentlefemdom.core_templates import get_template
from auteur.gentlefemdom.validation import validate_choices
from auteur.netorare.identity_generator import IdentityGenerator


def create_sensual_dominance_choices() -> dict:
    """Create a complete set of valid choices for Sensual Dominance core."""
    return {
        4: {
            "want": "want-establish-trust",
            "resistance": "resistance-partner-doubt",
            "conflict": "conflict-control-vs-consent",
            "stakes": "stakes-emotional-intimacy",
            "change": "change-tentative-to-confident",
        }
    }


def create_tender_surrender_choices() -> dict:
    """Create a complete set of valid choices for Tender Surrender core."""
    return {
        4: {
            "want": "want-release-control",
            "resistance": "resistance-fear-vulnerability",
            "conflict": "conflict-self-protection-vs-desire",
            "stakes": "stakes-emotional-walls",
            "change": "change-defended-to-open",
        }
    }


def create_romantic_authority_choices() -> dict:
    """Create a complete set of valid choices for Romantic Authority core."""
    return {
        4: {
            "want": "want-provide-protect",
            "resistance": "resistance-partner-independence",
            "conflict": "conflict-leadership-vs-partnership",
            "stakes": "stakes-relationship-balance",
            "change": "change-uncertain-to-confident",
        }
    }


def demonstrate_genre_pipeline(core_id: str, choices: dict) -> tuple[str, str]:
    """
    Demonstrate the gentle femdom genre pipeline.

    Returns: (core_id, yaml_content)
    """
    print(f"\n{'='*70}")
    print(f"GENTLE FEMDOM GENRE PIPELINE DEMONSTRATION")
    print(f"{'='*70}")
    print(f"\n[1] Selected Core: {core_id.upper()}")

    # Load template
    template = get_template(core_id)
    print(f"[2] Template loaded: {template.__class__.__name__}")
    print(f"    Primary Emotion: {template.primary_emotion}")
    print(f"    Phases: {len(template.phases)}")

    # Display phase structure
    print(f"\n[3] Decision Tree Phases:")
    for phase_num, phase_name in template.phases.items():
        print(f"    Phase {phase_num}: {phase_name}")

    # Validate choices
    print(f"\n[4] Validating user choices...")
    is_valid, errors, warnings = validate_choices(template, choices)

    if not is_valid:
        print(f"    [FAIL] Validation FAILED")
        for error in errors:
            print(f"       Error: {error}")
        return core_id, ""

    print(f"    [OK] Validation PASSED")
    if warnings:
        print(f"    [WARN] Warnings:")
        for warning in warnings:
            print(f"       {warning}")

    # Generate identity
    print(f"\n[5] Generating story_identity.yaml...")
    try:
        identity = IdentityGenerator.from_choices(core_id, choices)
        yaml_content = IdentityGenerator.to_yaml(identity)
        print(f"    [OK] Identity generated successfully")
        return core_id, yaml_content
    except Exception as e:
        print(f"    [FAIL] Identity generation failed: {e}")
        return core_id, ""


def main():
    """Run the demonstration for all three gentle femdom cores."""

    print("\n" + "="*70)
    print("AUTEUR GENTLE FEMDOM GENRE PIPELINE - AUTOMATED DEMONSTRATION")
    print("="*70)

    # Test all three cores
    test_cases = [
        ("sensual_dominance", create_sensual_dominance_choices()),
        ("tender_surrender", create_tender_surrender_choices()),
        ("romantic_authority", create_romantic_authority_choices()),
    ]

    results = []
    for core_id, choices in test_cases:
        core_id_result, yaml_content = demonstrate_genre_pipeline(core_id, choices)
        results.append((core_id_result, yaml_content))

        if yaml_content:
            print(f"\n[6] Generated YAML Preview:")
            print("    " + "\n    ".join(yaml_content.split("\n")[:15]))
            if len(yaml_content.split("\n")) > 15:
                print(f"    ... ({len(yaml_content.split('\n')) - 15} more lines)")

    # Create handoff artifact
    print(f"\n{'='*70}")
    print("HANDOFF ARTIFACT - STORY IDENTITIES")
    print(f"{'='*70}\n")

    for core_id, yaml_content in results:
        if yaml_content:
            print(f"\n>>> {core_id.upper()} <<<\n")
            print(yaml_content)
            print("\n" + "-"*70)

    # Save to file
    artifact_path = Path("gentle_femdom_narrative_output.yaml")
    with open(artifact_path, "w", encoding="utf-8") as f:
        f.write("# Gentle Femdom Genre Pipeline - Narrative Engine Output\n")
        f.write("# Generated by automated test_gentlefemdom_demo.py\n\n")
        for core_id, yaml_content in results:
            if yaml_content:
                f.write(f"---\n# {core_id.upper()}\n---\n{yaml_content}\n\n")

    print(f"\n[OK] Handoff artifact saved to: {artifact_path}")
    print(f"   Total cores tested: {len([y for _, y in results if y])}/3")
    print(f"   All validations passed: {all(y for _, y in results)}")


if __name__ == "__main__":
    main()
