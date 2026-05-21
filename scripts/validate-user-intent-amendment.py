#!/usr/bin/env python3
"""Specialized Level 3 validator for user_intent_amendment artifacts."""

import os
import sys
import re
import yaml
import argparse

from _validator_utils import format_error

# Error codes
MISSING_FIELD = "MISSING_FIELD"
INVALID_FIELD_VALUE = "INVALID_FIELD_VALUE"
YAML_MALFORMED = "YAML_MALFORMED"
REF_MISMATCH = "REF_MISMATCH"


def validate_user_intent_amendment(artifact_path, repo_root="."):
    """Validate user_intent_amendment artifact structure and field types."""

    errors = []

    # 1. Load artifact
    if not os.path.exists(artifact_path):
        errors.append(format_error(MISSING_FIELD, f"Artifact file not found: {artifact_path}"))
        return errors

    with open(artifact_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 2. Extract YAML block
    match = re.search(
        r"---\s+(.*?)\s+---",
        content,
        re.DOTALL
    )
    if not match:
        errors.append(format_error(YAML_MALFORMED, "No YAML block found between --- markers"))
        return errors

    yaml_text = match.group(1).strip()
    try:
        artifact = yaml.safe_load(yaml_text)
    except Exception as e:
        errors.append(format_error(YAML_MALFORMED, f"Failed to parse YAML block: {e}"))
        return errors

    if not isinstance(artifact, dict):
        errors.append(format_error(YAML_MALFORMED, "YAML block must be a dictionary, not a list"))
        return errors

    # 3. Check required fields
    required_fields = [
        'artifact_id',
        'amends_intent_ref',
        'clarification_type',
        'requires_reroute',
        'created_at',
        'created_by'
    ]

    for field in required_fields:
        if field not in artifact:
            errors.append(format_error(MISSING_FIELD, f"Missing required field: {field}"))

    # 4. Validate field values

    # artifact_id must be 'user_intent_amendment'
    if artifact.get('artifact_id') != 'user_intent_amendment':
        errors.append(
            format_error(
                INVALID_FIELD_VALUE,
                f"artifact_id must be 'user_intent_amendment', got '{artifact.get('artifact_id')}'"
            )
        )

    # amends_intent_ref should point to 00-user-intent.md
    amends_ref = artifact.get('amends_intent_ref')
    if amends_ref and amends_ref != '00-user-intent.md':
        errors.append(
            format_error(
                REF_MISMATCH,
                f"amends_intent_ref should be '00-user-intent.md', got '{amends_ref}'"
            )
        )

    # clarification_type must be one of allowed values
    allowed_types = ['scope_refinement', 'scope_expansion', 'out_of_scope_addition']
    if artifact.get('clarification_type') not in allowed_types:
        errors.append(
            format_error(
                INVALID_FIELD_VALUE,
                f"clarification_type must be one of {allowed_types}, got '{artifact.get('clarification_type')}'"
            )
        )

    # requires_reroute must be boolean
    if not isinstance(artifact.get('requires_reroute'), bool):
        errors.append(
            format_error(
                INVALID_FIELD_VALUE,
                f"requires_reroute must be boolean, got {type(artifact.get('requires_reroute')).__name__}"
            )
        )

    # created_at should be ISO 8601 format
    created_at = artifact.get('created_at')
    if created_at:
        iso_pattern = r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}'
        if not re.match(iso_pattern, str(created_at)):
            errors.append(
                format_error(
                    INVALID_FIELD_VALUE,
                    f"created_at should be ISO 8601 format, got '{created_at}'"
                )
            )

    # created_by should be non-empty
    if not artifact.get('created_by'):
        errors.append(
            format_error(MISSING_FIELD, "created_by must be non-empty")
        )

    # Return errors or success
    if errors:
        for error in errors:
            print(error)
        return False

    print(f"[PASS] user_intent_amendment validation passed for {artifact_path}")
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Validate user_intent_amendment artifact structure and field types"
    )
    parser.add_argument("artifact_path", help="Path to user_intent_amendment artifact")
    parser.add_argument("--repo-root", default=".", help="Repository root")

    args = parser.parse_args()

    success = validate_user_intent_amendment(args.artifact_path, args.repo_root)
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
