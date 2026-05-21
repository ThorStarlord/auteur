"""Specialized Level 3 validator for usage-research-report artifacts."""

import os
import re
import sys
import argparse

from _validator_utils import format_error

# Stable error codes
REPORT_FILE_NOT_FOUND = "REPORT_FILE_NOT_FOUND"
MISSING_SECTION = "MISSING_SECTION"
INVALID_SEMANTIC_SCORE = "INVALID_SEMANTIC_SCORE"
INVALID_FAILURE_CLASSIFICATION = "INVALID_FAILURE_CLASSIFICATION"
PLACEHOLDER_DETECTED = "PLACEHOLDER_DETECTED"
ABSOLUTE_PATH_DETECTED = "ABSOLUTE_PATH_DETECTED"
ROLE_BOUNDARY_VIOLATION = "ROLE_BOUNDARY_VIOLATION"


def validate_report(report_path, repo_root="."):
    errors = []

    if not os.path.exists(report_path):
        return [format_error(REPORT_FILE_NOT_FOUND, f"Report file not found: {report_path}")]

    with open(report_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Required sections check
    required_sections = [
        "Scenario Tested",
        "Expected Behavior",
        "Actual Behavior",
        "What Worked",
        "Friction Points",
        "Routing Quality",
        "Handoff Quality",
        "Next Test",
    ]

    # Sections that have aliases or are only required in the new format
    optional_or_aliased = {
        "Evidence Excerpts": [],
        "Failure Classification": [],
        "Semantic Quality Score": [],
        "Recommended Maintainer Input": ["Recommended Skill Edits"],
    }

    for section in required_sections:
        pattern = rf"## ([\d]+\. )?{re.escape(section)}"
        if not re.search(pattern, content, re.IGNORECASE):
            errors.append(format_error(MISSING_SECTION, f"Missing required section: '{section}'"))

    for section, aliases in optional_or_aliased.items():
        patterns = [rf"## ([\d]+\. )?{re.escape(section)}"]
        patterns.extend([rf"## ([\d]+\. )?{re.escape(alias)}" for alias in aliases])

        found = False
        for p in patterns:
            if re.search(p, content, re.IGNORECASE):
                found = True
                break

        # If it's a new required section but not found, we only error if it's not a legacy report
        if not found:
            # Check if this is a new standard report (indicated by Score or Classification)
            is_new_standard = "Semantic Quality Score" in content or "Failure Classification" in content
            if is_new_standard:
                errors.append(
                    format_error(MISSING_SECTION, f"Missing required section in new standard report: '{section}'")
                )

    # Check for placeholder text or generic AI tics if possible
    placeholders = ["TODO", "FIXME", "REPLACE_ME", "[INSERT"]
    for p in placeholders:
        if p in content:
            errors.append(format_error(PLACEHOLDER_DETECTED, f"Placeholder detected: '{p}'"))

    # Check for absolute paths
    abs_path_patterns = [r"[a-zA-Z]:\\", r"/[Uu]sers/", r"/[Hh]ome/"]
    for pattern in abs_path_patterns:
        if re.search(pattern, content):
            errors.append(
                format_error(
                    ABSOLUTE_PATH_DETECTED,
                    f"Absolute path detected in report (pattern: {pattern}). All paths must be relative.",
                )
            )

    # Check for Semantic Quality Score format (only for new standard)
    score_match = re.search(r"- \*\*Score\*\*: \[?(\d+)\]?", content)
    if score_match:
        score = int(score_match.group(1))
        if not (0 <= score <= 21):
            errors.append(
                format_error(
                    INVALID_SEMANTIC_SCORE,
                    f"Invalid Semantic Quality Score: {score}. Must be between 0 and 21.",
                )
            )

    # Check for failure classification (only for new standard)
    if "Failure Classification" in content:
        if not re.search(
            r"- \*\*Classification\*\*: \[?(Structural|Semantic|Boundary|None)\]?", content, re.IGNORECASE
        ):
            errors.append(
                format_error(
                    INVALID_FAILURE_CLASSIFICATION,
                    "Missing or invalid 'Failure Classification'. Must be one of: Structural, Semantic, Boundary, None.",
                )
            )

    # Evidence Check (New Standard must have actual evidence)
    if "Evidence Excerpts" in content:
        if not re.search(r">|```", content):
            errors.append(
                format_error(MISSING_SECTION, "Missing Evidence Excerpts content. You must provide specific snippets (blockquote or code block).")
            )

    # Role Boundary Guard: Researcher must not act as Maintainer
    patching_terms = [r"edit\s+skill", r"patch\s+instruction", r"modify\s+instruction", r"change\s+logic\s+in", r"```diff"]
    for term in patching_terms:
        if re.search(term, content, re.IGNORECASE):
            # Allow mention of improvement plans but not direct instruction edits
            if not re.search(r"recommended\s+maintainer\s+input", content, re.IGNORECASE):
                errors.append(
                    format_error(
                        ROLE_BOUNDARY_VIOLATION,
                        f"Role Boundary Violation: Usage researcher should not propose direct patches (found: '{term}'). Recommend investigation areas for the Skill Maintainer instead.",
                    )
                )

    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate a usage research report artifact.")
    parser.add_argument("artifact_path", nargs="?", help="Path to the .md report file")
    parser.add_argument("--repo-root", default=".", help="Root of the repository for file checks")
    parser.add_argument("--list-codes", action="store_true", help="List all error codes and exit")
    args = parser.parse_args(argv)

    if args.list_codes:
        codes = [
            REPORT_FILE_NOT_FOUND,
            MISSING_SECTION,
            INVALID_SEMANTIC_SCORE,
            INVALID_FAILURE_CLASSIFICATION,
            PLACEHOLDER_DETECTED,
            ABSOLUTE_PATH_DETECTED,
            ROLE_BOUNDARY_VIOLATION,
        ]
        print("Stable error codes for usage research report validation:")
        for code in codes:
            print(f"  {code}")
        return 0

    if not args.artifact_path:
        parser.print_usage()
        return 1

    errs = validate_report(args.artifact_path, args.repo_root)
    if errs:
        for e in errs:
            print(f"ERROR {e}")
        return 1
    else:
        print("Report validation passed!")
        return 0


if __name__ == "__main__":
    sys.exit(main())
