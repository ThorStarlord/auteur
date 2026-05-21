"""Specialized validator for unknowns_map routing fields.

Checks that the machine-readable YAML block contains required routing fields
with valid values.
"""

import os
import sys
import re
import yaml
import argparse

from _validator_utils import format_error

# Stable error codes
UNKNOWNS_MAP_FILE_NOT_FOUND = "UNKNOWNS_MAP_FILE_NOT_FOUND"
MISSING_ROUTING_BLOCK = "MISSING_ROUTING_BLOCK"
PARSING_ERROR = "PARSING_ERROR"
MISSING_ROUTING_FIELD = "MISSING_ROUTING_FIELD"
INVALID_CLARITY_VALUE = "INVALID_CLARITY_VALUE"
INVALID_UNKNOWNS_COUNT = "INVALID_UNKNOWNS_COUNT"
INVALID_ASSUMPTIONS_COUNT = "INVALID_ASSUMPTIONS_COUNT"
INVALID_RESEARCH_NEEDED = "INVALID_RESEARCH_NEEDED"


def validate_unknowns_map(artifact_path: str, repo_root: str = ".") -> list[str]:
    """Validate unknowns_map routing fields. Returns list of error messages."""
    errors: list[str] = []

    if not os.path.exists(artifact_path):
        errors.append(format_error(UNKNOWNS_MAP_FILE_NOT_FOUND, f"File not found: {artifact_path}"))
        return errors

    with open(artifact_path, encoding="utf-8") as f:
        content = f.read()

    # Extract the routing YAML block
    routing_match = re.search(
        r"## 7\. Machine-readable routing\s+```yaml\s+(.*?)\s+```",
        content,
        re.DOTALL | re.IGNORECASE,
    )

    if not routing_match:
        errors.append(
            format_error(MISSING_ROUTING_BLOCK, "Missing 'Machine-readable routing' YAML block in section 7.")
        )
        return errors

    try:
        routing_data = yaml.safe_load(routing_match.group(1))
        if not isinstance(routing_data, dict):
            errors.append(format_error(PARSING_ERROR, "Routing block must be a YAML mapping, not a list."))
            return errors

        # Check required fields
        required_fields = ["clarity_assessment", "unknowns_count", "assumptions_count", "research_needed"]
        for field in required_fields:
            if field not in routing_data:
                errors.append(format_error(MISSING_ROUTING_FIELD, f"Missing routing field: {field}"))

        # Validate clarity_assessment
        clarity = routing_data.get("clarity_assessment")
        if clarity and clarity not in ["high", "medium", "low"]:
            errors.append(
                format_error(
                    INVALID_CLARITY_VALUE,
                    f"clarity_assessment must be 'high', 'medium', or 'low', got: {clarity}",
                )
            )

        # Validate unknowns_count is an integer >= 0
        unknowns_count = routing_data.get("unknowns_count")
        if unknowns_count is not None:
            if not isinstance(unknowns_count, int) or unknowns_count < 0:
                errors.append(
                    format_error(INVALID_UNKNOWNS_COUNT, f"unknowns_count must be non-negative integer, got: {unknowns_count}")
                )

        # Validate assumptions_count is an integer >= 0
        assumptions_count = routing_data.get("assumptions_count")
        if assumptions_count is not None:
            if not isinstance(assumptions_count, int) or assumptions_count < 0:
                errors.append(
                    format_error(
                        INVALID_ASSUMPTIONS_COUNT,
                        f"assumptions_count must be non-negative integer, got: {assumptions_count}",
                    )
                )

        # Validate research_needed is boolean
        research_needed = routing_data.get("research_needed")
        if research_needed is not None:
            if not isinstance(research_needed, bool):
                errors.append(
                    format_error(INVALID_RESEARCH_NEEDED, f"research_needed must be boolean, got: {research_needed}")
                )

    except Exception as e:
        errors.append(format_error(PARSING_ERROR, f"Failed to parse routing YAML: {e}"))

    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Specialized validator for unknowns_map routing fields.")
    parser.add_argument("artifact_path", nargs="?", help="Path to the unknowns_map .md file")
    parser.add_argument("--repo-root", default=".", help="Root of the repository for file checks")
    parser.add_argument("--list-codes", action="store_true", help="List all error codes and exit")
    args = parser.parse_args(argv)

    if args.list_codes:
        codes = [
            UNKNOWNS_MAP_FILE_NOT_FOUND,
            MISSING_ROUTING_BLOCK,
            PARSING_ERROR,
            MISSING_ROUTING_FIELD,
            INVALID_CLARITY_VALUE,
            INVALID_UNKNOWNS_COUNT,
            INVALID_ASSUMPTIONS_COUNT,
            INVALID_RESEARCH_NEEDED,
        ]
        for code in codes:
            print(code)
        return 0

    if not args.artifact_path:
        parser.print_help()
        return 1

    errors = validate_unknowns_map(args.artifact_path, args.repo_root)
    if errors:
        for error in errors:
            print(error)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
