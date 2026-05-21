#!/usr/bin/env python3
"""Specialized Level 3 validator for user_intent artifacts."""

import os
import sys
import re
import yaml
import argparse

from _validator_utils import format_error

# Error codes
MISSING_FIELD = "MISSING_FIELD"
INVALID_FIELD_VALUE = "INVALID_FIELD_VALUE"
IMMUTABILITY_VIOLATION = "IMMUTABILITY_VIOLATION"
CONSISTENCY_ERROR = "CONSISTENCY_ERROR"
YAML_MALFORMED = "YAML_MALFORMED"


def validate_user_intent(artifact_path, repo_root="."):
    """Validate user_intent artifact structure and field types."""

    errors = []

    # 1. Load artifact
    if not os.path.exists(artifact_path):
        errors.append(format_error(MISSING_FIELD, f"Artifact file not found: {artifact_path}"))
        return errors

    with open(artifact_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 2. Extract YAML block (expect Section: machine_readable_intent)
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
        'intent_source',
        'scope_mode',
        'raw_problem_statement',
        'created_at',
        'immutable'
    ]

    for field in required_fields:
        if field not in artifact:
            errors.append(format_error(MISSING_FIELD, f"Missing required field: {field}"))

    # 4. Validate field values

    # artifact_id must be 'user_intent'
    if artifact.get('artifact_id') != 'user_intent':
        errors.append(
            format_error(
                INVALID_FIELD_VALUE,
                f"artifact_id must be 'user_intent', got '{artifact.get('artifact_id')}'"
            )
        )

    # intent_source must be one of allowed values
    allowed_sources = ['user_problem_statement', 'repo_inferred', 'imported_ticket']
    if artifact.get('intent_source') not in allowed_sources:
        errors.append(
            format_error(
                INVALID_FIELD_VALUE,
                f"intent_source must be one of {allowed_sources}, got '{artifact.get('intent_source')}'"
            )
        )

    # scope_mode must be one of allowed values
    allowed_scopes = ['soft', 'hard', 'advisory']
    if artifact.get('scope_mode') not in allowed_scopes:
        errors.append(
            format_error(
                INVALID_FIELD_VALUE,
                f"scope_mode must be one of {allowed_scopes}, got '{artifact.get('scope_mode')}'"
            )
        )

    # 5. Validate consistency: repo_inferred should have null raw_problem_statement
    intent_source = artifact.get('intent_source')
    raw_problem = artifact.get('raw_problem_statement')

    if intent_source == 'repo_inferred' and raw_problem is not None:
        errors.append(
            format_error(
                CONSISTENCY_ERROR,
                f"intent_source is 'repo_inferred' but raw_problem_statement is not null"
            )
        )

    if intent_source == 'user_problem_statement' and raw_problem is None:
        errors.append(
            format_error(
                CONSISTENCY_ERROR,
                f"intent_source is 'user_problem_statement' but raw_problem_statement is null"
            )
        )

    # 6. immutable must be true
    if artifact.get('immutable') is not True:
        errors.append(
            format_error(
                IMMUTABILITY_VIOLATION,
                f"immutable field must be true, got {artifact.get('immutable')}"
            )
        )

    # 7. created_at should be ISO 8601 format (basic check)
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

    # 8. List fields should be lists (optional but check if present)
    for list_field in ['constraints', 'non_goals', 'clarifications']:
        if list_field in artifact and not isinstance(artifact.get(list_field), list):
            errors.append(
                format_error(
                    INVALID_FIELD_VALUE,
                    f"{list_field} must be a list, got {type(artifact.get(list_field)).__name__}"
                )
            )

    # Return errors or success
    if errors:
        for error in errors:
            print(error)
        return False

    print(f"[PASS] user_intent validation passed for {artifact_path}")
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Validate user_intent artifact structure and field types"
    )
    parser.add_argument("artifact_path", help="Path to user_intent.md artifact")
    parser.add_argument("--repo-root", default=".", help="Repository root")

    args = parser.parse_args()

    success = validate_user_intent(args.artifact_path, args.repo_root)
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
