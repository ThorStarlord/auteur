"""Specialized Level 3 validator for skill-improvement-plan artifacts."""

import os
import re
import sys
import yaml
import argparse

from _validator_utils import format_error

# Stable error codes
IMPROVEMENT_FILE_NOT_FOUND = "IMPROVEMENT_FILE_NOT_FOUND"
MISSING_SECTION = "MISSING_SECTION"
INVALID_FAILURE_MODE_CLASS = "INVALID_FAILURE_MODE_CLASS"
INVALID_DEFECT_SOURCE = "INVALID_DEFECT_SOURCE"
MISSING_SOURCE_REPORT = "MISSING_SOURCE_REPORT"
SOURCE_REPORT_NOT_FOUND = "SOURCE_REPORT_NOT_FOUND"
ABSOLUTE_SOURCE_REPORT_PATH = "ABSOLUTE_SOURCE_REPORT_PATH"
MISSING_EVIDENCE_SNIPPET = "MISSING_EVIDENCE_SNIPPET"
INVALID_RECOMMENDED_ACTION = "INVALID_RECOMMENDED_ACTION"
MISSING_EDIT_TYPE = "MISSING_EDIT_TYPE"
MISSING_RISK_LEVEL = "MISSING_RISK_LEVEL"
MISSING_ANTI_OVERFITTING = "MISSING_ANTI_OVERFITTING"
MISSING_RERUN_SCENARIO = "MISSING_RERUN_SCENARIO"
MISSING_SUCCESS_CRITERIA = "MISSING_SUCCESS_CRITERIA"
ABSOLUTE_PATH_DETECTED = "ABSOLUTE_PATH_DETECTED"


def validate_improvement_plan(plan_path, repo_root="."):
    errors = []

    if not os.path.exists(plan_path):
        return [format_error(IMPROVEMENT_FILE_NOT_FOUND, f"Plan file not found: {plan_path}")]

    with open(plan_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Structural Header Check
    required_sections = [
        "Diagnosis",
        "Evidence",
        "Proposed Edits",
        "Impact Assessment",
        "Verification Plan",
    ]

    for section in required_sections:
        pattern = rf"## ([\d]+\. )?{re.escape(section)}"
        if not re.search(pattern, content, re.IGNORECASE):
            errors.append(format_error(MISSING_SECTION, f"Missing required section: '{section}'"))

    # 1.1 Failure Mode Class Verification (Flexible)
    fm_match = re.search(
        r'-\s*\*?\*?Failure Mode Class\*?\*?:\s*`?(.*?)`?\s*$', content, re.IGNORECASE | re.MULTILINE
    )
    if not fm_match:
        # Fallback to "Failure Mode" if Class is missing
        fm_match = re.search(
            r'-\s*\*?\*?Failure Mode\*?\*?:\s*`?(.*?)`?\s*$', content, re.IGNORECASE | re.MULTILINE
        )

    if not fm_match:
        errors.append(
            format_error(
                INVALID_FAILURE_MODE_CLASS,
                "Missing mandatory field '- **Failure Mode Class**: Class X: Name'.",
            )
        )
    else:
        fm_class = fm_match.group(1)
        valid_classes = [
            "Class 1: Input Ambiguity",
            "Class 2: Wrong Routing",
            "Class 3: Artifact Weakness",
            "Class 4: Handoff Failure",
            "Class 5: Boundary Violation",
            "Class 6: Hallucinated Evidence",
            "Class 7: Path Hygiene Error",
            "Class 8: Over-Maintenance",
            "Class 9: Validator Mismatch",
            "Class 10: Status Overclaiming",
        ]
        is_valid = False
        fm_class_clean = fm_class.strip().lower()
        for vc in valid_classes:
            if fm_class_clean == vc.lower():
                is_valid = True
                break
        if not is_valid:
            errors.append(
                format_error(
                    INVALID_FAILURE_MODE_CLASS,
                    f"Invalid Failure Mode Class '{fm_class}'. Must be an EXACT match for one of the 10 formal classes defined in docs/philosophy/AGENTIC_FAILURE_MODES.md.",
                )
            )

    # 1.2 Defect Source Verification
    ds_match = re.search(r'-\s*\*?\*?Defect Source\*?\*?:\s*`?(\w+)`?', content, re.IGNORECASE)
    if not ds_match:
        errors.append(
            format_error(
                INVALID_DEFECT_SOURCE,
                "Missing mandatory field '- **Defect Source**: fixture_defect | validator_defect | registry_defect | consumer_skill_defect | producer_artifact_defect'.",
            )
        )
    else:
        ds = ds_match.group(1).lower()
        valid_sources = [
            "fixture_defect",
            "validator_defect",
            "registry_defect",
            "consumer_skill_defect",
            "producer_artifact_defect",
        ]
        if ds not in valid_sources:
            errors.append(
                format_error(
                    INVALID_DEFECT_SOURCE,
                    f"Invalid Defect Source '{ds}'. Must be one of: {', '.join(valid_sources)}",
                )
            )

    # 2. Source Report Verification
    match = re.search(r'-\s*\*?\*?Source Report\*?\*?:\s*\[(.*?)\]\((.*?)\)', content, re.IGNORECASE)
    if not match:
        # Also try to match non-linked Report ID for legacy support if needed
        match = re.search(
            r'-\s*\*?\*?(Source Report|Report ID)\*?\*?:\s*(.*)', content, re.IGNORECASE
        )
        if not match:
            errors.append(
                format_error(
                    MISSING_SOURCE_REPORT,
                    "Missing mandatory Source Report link: '- **Source Report**: [name](path)'.",
                )
            )

    if match and match.lastindex >= 2:
        report_rel_path = match.group(2).strip()
        if report_rel_path.startswith("file://") or os.path.isabs(report_rel_path):
            errors.append(
                format_error(
                    ABSOLUTE_SOURCE_REPORT_PATH,
                    f"Source Report path must be relative, got: {report_rel_path}",
                )
            )
        else:
            plan_dir = os.path.dirname(plan_path)
            full_report_path = os.path.normpath(os.path.join(plan_dir, report_rel_path))
            if not os.path.exists(full_report_path):
                errors.append(
                    format_error(
                        SOURCE_REPORT_NOT_FOUND,
                        f"Source Report file not found at: {full_report_path}",
                    )
                )

    # 3. Evidence Mapping Check
    if "Evidence Snippet" not in content and ">" not in content:
        errors.append(
            format_error(
                MISSING_EVIDENCE_SNIPPET,
                "Missing Evidence Snippet (must include a blockquote with a quote from research).",
            )
        )

    # 4. Recommended Action Check
    action_match = re.search(r'-\s*\*?\*?Recommended Action\*?\*?:\s*`?(\w+)`?', content, re.IGNORECASE)
    if not action_match:
        # Fallback to recommended action without list bullet
        action_match = re.search(r'recommended\s*action\s*:\s*`?(\w+)`?', content, re.IGNORECASE)

    if not action_match:
        errors.append(
            format_error(
                INVALID_RECOMMENDED_ACTION,
                "Missing 'Recommended Action' (e.g., skill_edit, fixture_edit, no_skill_change).",
            )
        )
    else:
        action = action_match.group(1).lower()
        valid_actions = ["skill_edit", "fixture_edit", "validator_edit", "registry_edit", "no_skill_change"]
        if action not in valid_actions:
            errors.append(
                format_error(
                    INVALID_RECOMMENDED_ACTION,
                    f"Invalid Recommended Action '{action}'. Must be one of: {', '.join(valid_actions)}",
                )
            )

    # 5. Proposed Edits Check
    if action_match and action == "skill_edit":
        if not re.search(r'edit\s*\*?\*?type\*?\*?\s*:', content, re.IGNORECASE):
            errors.append(
                format_error(MISSING_EDIT_TYPE, "Proposed edits must specify 'Edit Type' (instruction_edit, template_edit).")
            )
        if not re.search(r'risk\s*\*?\*?level\*?\*?\s*:', content, re.IGNORECASE):
            errors.append(
                format_error(MISSING_RISK_LEVEL, "Proposed edits must specify 'Risk Level'.")
            )

    # 5.1 Do Not Edit Check (Conditional if not skill_edit)
    if action_match and action != "skill_edit":
        if not re.search(r'Do Not Edit', content, re.IGNORECASE) and action != "no_skill_change":
            errors.append(
                format_error(
                    MISSING_SECTION,
                    f"Plans with Recommended Action '{action}' should specify a 'Do Not Edit' protection list.",
                )
            )

    # 6. Anti-Overfitting Check (Mandatory for all)
    if not re.search(r'anti[\s\-_]*overfitting', content, re.IGNORECASE):
        errors.append(
            format_error(
                MISSING_ANTI_OVERFITTING,
                "Missing 'Anti-Overfitting Guard' rationale. Every change must justify why it isn't overfitting to the fixture.",
            )
        )

    # 6. Verification Plan Check
    if not re.search(r'(Rerun Scenario|Scenario)\*?\*?\s*:', content, re.IGNORECASE):
        errors.append(
            format_error(MISSING_RERUN_SCENARIO, "Verification Plan must specify a 'Rerun Scenario'.")
        )
    if not re.search(r'(Success Criteria|Success)\*?\*?\s*:', content, re.IGNORECASE):
        errors.append(
            format_error(MISSING_SUCCESS_CRITERIA, "Verification Plan must specify 'Success Criteria'.")
        )

    # 7. Path Hygiene
    abs_path_patterns = [r"[a-zA-Z]:\\", r"/[Uu]sers/", r"/[Hh]ome/"]
    for pattern in abs_path_patterns:
        if re.search(pattern, content):
            errors.append(
                format_error(
                    ABSOLUTE_PATH_DETECTED,
                    f"Absolute path detected in plan: {pattern}. All paths must be repository-relative.",
                )
            )

    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate a skill improvement plan artifact.")
    parser.add_argument("artifact_path", nargs="?", help="Path to the .md improvement plan file")
    parser.add_argument("--repo-root", default=".", help="Root directory of the repository")
    parser.add_argument("--list-codes", action="store_true", help="List all error codes and exit")
    args = parser.parse_args(argv)

    if args.list_codes:
        codes = [
            IMPROVEMENT_FILE_NOT_FOUND,
            MISSING_SECTION,
            INVALID_FAILURE_MODE_CLASS,
            INVALID_DEFECT_SOURCE,
            MISSING_SOURCE_REPORT,
            SOURCE_REPORT_NOT_FOUND,
            ABSOLUTE_SOURCE_REPORT_PATH,
            MISSING_EVIDENCE_SNIPPET,
            INVALID_RECOMMENDED_ACTION,
            MISSING_EDIT_TYPE,
            MISSING_RISK_LEVEL,
            MISSING_ANTI_OVERFITTING,
            MISSING_RERUN_SCENARIO,
            MISSING_SUCCESS_CRITERIA,
            ABSOLUTE_PATH_DETECTED,
        ]
        print("Stable error codes for skill improvement plan validation:")
        for code in codes:
            print(f"  {code}")
        return 0

    if not args.artifact_path:
        parser.print_usage()
        return 1

    errs = validate_improvement_plan(args.artifact_path, args.repo_root)
    if errs:
        for e in errs:
            print(f"ERROR {e}")
        return 1
    else:
        print("Improvement plan validation passed!")
        return 0


if __name__ == "__main__":
    sys.exit(main())
