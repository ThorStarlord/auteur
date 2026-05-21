"""Generic Level 2 validator for all artifact types.

This validator checks artifacts against their contracts in artifact-contracts.yaml.
It preserves the two-positional signature (artifact_id + artifact_path) as a documented
exception to the standard single-positional CLI.
"""

import os
import sys
import re
import yaml
import argparse

from _validator_utils import format_error, load_artifact_contracts

# Stable error codes
ARTIFACT_FILE_NOT_FOUND = "ARTIFACT_FILE_NOT_FOUND"
CONTRACTS_FILE_NOT_FOUND = "CONTRACTS_FILE_NOT_FOUND"
CONTRACT_NOT_FOUND = "CONTRACT_NOT_FOUND"
ABSOLUTE_FILE_LINK = "ABSOLUTE_FILE_LINK"
MISSING_REQUIRED_SECTION = "MISSING_REQUIRED_SECTION"
MISSING_YAML_BLOCK = "MISSING_YAML_BLOCK"
MISSING_MACHINE_FIELDS = "MISSING_MACHINE_FIELDS"
MISSING_EVIDENCE_EXCERPTS = "MISSING_EVIDENCE_EXCERPTS"
MISSING_EXCERPT_FIELD = "MISSING_EXCERPT_FIELD"
ABSOLUTE_EXCERPT_PATH = "ABSOLUTE_EXCERPT_PATH"
MISSING_RECOMMENDED_FIELD = "MISSING_RECOMMENDED_FIELD"

warnings = []  # Collect warnings separately from errors


def validate_artifact(artifact_id, artifact_path, repo_root=".", strict_recommended=False):
    errors = []

    if not os.path.exists(artifact_path):
        errors.append(format_error(ARTIFACT_FILE_NOT_FOUND, f"Artifact file not found: {artifact_path}"))
        return errors

    # Load contracts using shared utility
    contracts_data = load_artifact_contracts(repo_root)
    if contracts_data is None:
        errors.append(format_error(CONTRACTS_FILE_NOT_FOUND, "artifact-contracts.yaml not found in workflow-orchestrator references."))
        return errors

    # Find specific contract
    contract = next((a for a in contracts_data.get("artifacts", []) if a["id"] == artifact_id), None)
    if not contract:
        errors.append(format_error(CONTRACT_NOT_FOUND, f"Contract for artifact_id '{artifact_id}' not found in artifact-contracts.yaml"))
        return errors

    # Read artifact content
    with open(artifact_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Ban file:/// links
    if "file:///" in content:
        errors.append(format_error(ABSOLUTE_FILE_LINK, "Absolute 'file:///' links are banned in generated artifacts. Use relative paths."))

    # 2. Check required sections
    required_sections = contract.get("required_sections", [])
    for section in required_sections:
        section_regex_part = re.escape(section).replace("_", r"[\s_\-]").replace(r"\_", r"[\s_\-]")
        pattern = rf"^##\s+(?:\d+\.\s+)?{section_regex_part}"
        if not re.search(pattern, content, re.MULTILINE | re.IGNORECASE):
            errors.append(format_error(MISSING_REQUIRED_SECTION, f"Missing required section: {section}"))

    # 3. Check machine fields in YAML block
    required_fields = contract.get("required_machine_fields", [])
    recommended_fields = contract.get("recommended_machine_fields", [])
    yaml_data = None

    if required_fields or recommended_fields:
        yaml_blocks = re.findall(r"```yaml\s+(.*?)\s+```", content, re.DOTALL)
        if not yaml_blocks:
            errors.append(format_error(MISSING_YAML_BLOCK, "Missing machine-readable YAML block"))
        else:
            found_valid_block = False
            for yaml_text in yaml_blocks:
                try:
                    data = yaml.safe_load(yaml_text)
                    if isinstance(data, dict):
                        missing = [f for f in required_fields if f not in data]
                        if not missing:
                            found_valid_block = True
                            yaml_data = data
                            break
                except Exception:
                    pass

            if not found_valid_block:
                errors.append(
                    format_error(
                        MISSING_MACHINE_FIELDS,
                        f"Could not find a single YAML block containing all required machine fields: {required_fields}",
                    )
                )

    # 3b. Check recommended fields (warnings only, unless --strict-recommended)
    if yaml_data and recommended_fields:
        for field in recommended_fields:
            if field not in yaml_data:
                msg = format_error(MISSING_RECOMMENDED_FIELD, f"Recommended field missing: {field}")
                if strict_recommended:
                    errors.append(msg)
                else:
                    warnings.append(msg)

    # 4. Specific validation for repository_sensemaking_brief
    if artifact_id == "repository_sensemaking_brief":
        evidence_match = re.search(r"evidence_excerpts:.*?```yaml\s+(.*?)\s+```", content, re.DOTALL | re.IGNORECASE)
        if not evidence_match:
            evidence_match = re.search(r"```yaml\s+(evidence_excerpts:.*?)\s+```", content, re.DOTALL)

        if not evidence_match:
            errors.append(format_error(MISSING_EVIDENCE_EXCERPTS, "Missing or malformed YAML block for evidence_excerpts"))
        else:
            try:
                evidence_data = yaml.safe_load(evidence_match.group(1))
                excerpts = evidence_data.get("evidence_excerpts", [])
                if not isinstance(excerpts, list):
                    errors.append(format_error(MISSING_EVIDENCE_EXCERPTS, "evidence_excerpts must be a list of excerpts"))
                else:
                    for i, exc in enumerate(excerpts):
                        for f in ["file", "lines", "quote", "supports_claim"]:
                            if f not in exc:
                                errors.append(format_error(MISSING_EXCERPT_FIELD, f"evidence_excerpt[{i}] missing field: {f}"))
                        if "file" in exc and exc["file"].startswith("file:///"):
                            errors.append(
                                format_error(ABSOLUTE_EXCERPT_PATH, f"evidence_excerpt[{i}] file path must be relative, got: {exc['file']}")
                            )
            except Exception as e:
                errors.append(format_error(MISSING_EVIDENCE_EXCERPTS, f"Failed to parse evidence_excerpts YAML: {e}"))

    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate an artifact against its contract.")
    parser.add_argument("artifact_id", help="The ID of the artifact (e.g., repository_sensemaking_brief)")
    parser.add_argument("artifact_path", nargs="?", help="Path to the artifact markdown file")
    parser.add_argument("--repo-root", default=".", help="Root directory of the repository")
    parser.add_argument("--list-codes", action="store_true", help="List all error codes and exit")
    parser.add_argument("--strict-recommended", action="store_true", help="Treat missing recommended fields as errors")
    args = parser.parse_args(argv)

    if args.list_codes:
        codes = [
            ARTIFACT_FILE_NOT_FOUND,
            CONTRACTS_FILE_NOT_FOUND,
            CONTRACT_NOT_FOUND,
            ABSOLUTE_FILE_LINK,
            MISSING_REQUIRED_SECTION,
            MISSING_YAML_BLOCK,
            MISSING_MACHINE_FIELDS,
            MISSING_RECOMMENDED_FIELD,
            MISSING_EVIDENCE_EXCERPTS,
            MISSING_EXCERPT_FIELD,
            ABSOLUTE_EXCERPT_PATH,
        ]
        print("Stable error codes for artifact validation:")
        for code in codes:
            print(f"  {code}")
        return 0

    if not args.artifact_path:
        parser.print_usage()
        return 1

    global warnings
    warnings = []  # Reset warnings for this run
    errs = validate_artifact(args.artifact_id, args.artifact_path, args.repo_root, args.strict_recommended)

    # Print results with clear formatting
    if errs:
        print(f"[FAIL] Artifact validation failed:")
        for e in errs:
            print(f"  ERROR {e}")
        return 1

    # All required fields present
    print(f"[PASS] Required fields present")

    # Print warnings if any
    if warnings:
        for w in warnings:
            print(f"[WARN] {w}")
        print(f"\n  • {len(warnings)} recommended field(s) missing")
        print(f"  • Use --strict-recommended to promote warnings to errors")
        return 0
    else:
        print(f"[OK] All fields (required + recommended) present")
        return 0
        return 0


if __name__ == "__main__":
    sys.exit(main())
