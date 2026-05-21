"""Specialized Level 3 validator for prompt_handoff artifacts."""

import os
import sys
import re
import argparse

from _validator_utils import format_error, load_skill_registry, load_artifact_contracts

# Stable error codes
MISSING_SECTION = "MISSING_SECTION"
UNKNOWN_TARGET_SKILL = "UNKNOWN_TARGET_SKILL"
EMPTY_STOP_CONDITION = "EMPTY_STOP_CONDITION"
EMPTY_EXPECTED_OUTPUT = "EMPTY_EXPECTED_OUTPUT"
HALLUCINATED_ARTIFACT_REF = "HALLUCINATED_ARTIFACT_REF"
ABSOLUTE_PATH_DETECTED = "ABSOLUTE_PATH_DETECTED"
MISSING_READY_PROMPT = "MISSING_READY_PROMPT"

REQUIRED_SECTIONS = [
    "target_skill",
    "context_to_preserve",
    "task",
    "constraints",
    "inputs",
    "expected_output",
    "stop_condition",
    "ready_to_copy_prompt",
]

HEADING_RE = re.compile(r"^##\s+(?:\d+\.\s*)?(?P<name>.+?)\s*$", re.MULTILINE)


def _extract_sections(content: str) -> dict[str, str]:
    """Split content by ## headings, returning {lowercase_name: body_text}."""
    sections = {}
    matches = list(HEADING_RE.finditer(content))
    for idx, match in enumerate(matches):
        start = match.end()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(content)
        # Normalize hyphens to spaces for consistent lookup
        name = match.group("name").strip().lower().replace("-", " ")
        sections[name] = content[start:end].strip()
    return sections


def _all_skill_ids(skill_reg: dict) -> set[str]:
    """Extract all skill IDs from the skill-registry.yaml structure."""
    ids = set()
    for ecosystem in skill_reg.get("ecosystems", {}).values():
        for skill in ecosystem.get("skills", []):
            if "id" in skill:
                ids.add(skill["id"])
    return ids


def _all_artifact_ids(contracts: dict) -> set[str]:
    """Extract all artifact IDs from artifact-contracts.yaml."""
    return {a["id"] for a in contracts.get("artifacts", []) if "id" in a}


def validate_prompt_handoff(artifact_path: str, repo_root: str = ".") -> list[str]:
    errors = []

    if not os.path.exists(artifact_path):
        errors.append(format_error(MISSING_SECTION, f"Handoff file not found: {artifact_path}"))
        return errors

    with open(artifact_path, encoding="utf-8") as f:
        content = f.read()

    sections = _extract_sections(content)

    # 1. Check all required sections exist
    for section in REQUIRED_SECTIONS:
        section_key = section.replace("_", " ")
        if section_key not in sections:
            errors.append(format_error(MISSING_SECTION, f"Missing required section: '{section_key}'"))

    # 2. Validate target_skill against skill registry
    target_skill_section = sections.get("target skill", "")
    if target_skill_section:
        skill_reg = load_skill_registry(repo_root)
        if skill_reg:
            known_skills = _all_skill_ids(skill_reg)
            # Extract the skill ID from the section (typically wrapped in backticks)
            skill_match = re.search(r"`(\S+?)`", target_skill_section)
            if skill_match:
                skill_id = skill_match.group(1)
                if skill_id not in known_skills:
                    errors.append(
                        format_error(UNKNOWN_TARGET_SKILL, f"Target skill '{skill_id}' not found in skill-registry.yaml")
                    )
            elif not target_skill_section.strip().startswith("The name or ID"):
                # Non-template content without a backtick-wrapped ID
                first_line = target_skill_section.split("\n")[0].strip().strip("`")
                if first_line and first_line not in known_skills:
                    errors.append(
                        format_error(UNKNOWN_TARGET_SKILL, f"Target skill '{first_line}' not found in skill-registry.yaml")
                    )

    # 3. Check stop_condition is not empty
    stop_section = sections.get("stop condition", "")
    if stop_section:
        words = stop_section.split()
        if len(words) < 3:
            errors.append(format_error(EMPTY_STOP_CONDITION, "Stop Condition section is too short or empty."))
    elif "stop condition" not in sections:
        pass  # MISSING_SECTION already reported above

    # 4. Check expected_output is not empty
    output_section = sections.get("expected output", "")
    if output_section:
        words = output_section.split()
        if len(words) < 3:
            errors.append(format_error(EMPTY_EXPECTED_OUTPUT, "Expected Output section is too short or empty."))

    # 5. Check inputs against artifact-contracts.yaml and existing files
    inputs_section = sections.get("inputs", "")
    if inputs_section:
        artifact_contracts = load_artifact_contracts(repo_root)
        known_artifacts = _all_artifact_ids(artifact_contracts) if artifact_contracts else set()

        # Find file references in the inputs section
        file_refs = re.findall(r"`?([\w./\\-]+\.\w+)`?", inputs_section)
        for ref in file_refs:
            # Check if it's an absolute path
            if ref.startswith("/") or re.match(r"^[a-zA-Z]:\\", ref):
                errors.append(
                    format_error(ABSOLUTE_PATH_DETECTED, f"Input '{ref}' is an absolute path. Use repository-relative paths.")
                )
            else:
                # Check if it looks like an artifact ID reference (no file extension / known artifact)
                ref_stem = ref.replace(".md", "").replace(".yaml", "").replace(".yml", "")
                if ref_stem in known_artifacts:
                    continue  # Known artifact reference, skip file check
                # Check actual file existence relative to repo root
                full_path = os.path.normpath(os.path.join(repo_root, ref))
                if not os.path.exists(full_path):
                    errors.append(
                        format_error(
                            HALLUCINATED_ARTIFACT_REF,
                            f"Input '{ref}' does not exist in the repository and is not a known artifact ID.",
                        )
                    )

    # 6. Check for absolute paths anywhere in the document
    abs_path_patterns = [r"[a-zA-Z]:\\", r"/[Uu]sers/", r"/[Hh]ome/"]
    for pattern in abs_path_patterns:
        if re.search(pattern, content):
            errors.append(
                format_error(
                    ABSOLUTE_PATH_DETECTED,
                    f"Absolute path detected (pattern: {pattern}). All paths must be repository-relative.",
                )
            )

    # 7. Check ready-to-copy prompt has content
    prompt_section = sections.get("ready to copy prompt", "")
    if prompt_section:
        if not re.search(r"```", prompt_section):
            errors.append(format_error(MISSING_READY_PROMPT, "Ready-to-copy Prompt section must contain a markdown code block."))
        elif len(prompt_section.strip().split()) < 5:
            errors.append(format_error(MISSING_READY_PROMPT, "Ready-to-copy Prompt section is too short."))

    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate a prompt_handoff artifact.")
    parser.add_argument("artifact_path", nargs="?", help="Path to the prompt handoff .md file")
    parser.add_argument("--repo-root", default=".", help="Root of the repository for file checks")
    parser.add_argument("--list-codes", action="store_true", help="List all error codes and exit")
    args = parser.parse_args(argv)

    if args.list_codes:
        codes = [
            MISSING_SECTION,
            UNKNOWN_TARGET_SKILL,
            EMPTY_STOP_CONDITION,
            EMPTY_EXPECTED_OUTPUT,
            HALLUCINATED_ARTIFACT_REF,
            ABSOLUTE_PATH_DETECTED,
            MISSING_READY_PROMPT,
        ]
        print("Stable error codes for prompt handoff validation:")
        for code in codes:
            print(f"  {code}")
        return 0

    if not args.artifact_path:
        parser.print_usage()
        return 1

    errs = validate_prompt_handoff(args.artifact_path, args.repo_root)
    if errs:
        for e in errs:
            print(f"ERROR {e}")
        return 1
    else:
        print("Prompt handoff validation passed!")
        return 0


if __name__ == "__main__":
    sys.exit(main())
