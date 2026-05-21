import os
import sys
import re
import argparse
import yaml

from _validator_utils import format_error, load_weakness_types, load_workflow_registry

# Stable error codes
BRIEF_FILE_NOT_FOUND = "BRIEF_FILE_NOT_FOUND"
MISSING_EVIDENCE_EXCERPTS = "MISSING_EVIDENCE_EXCERPTS"
EVIDENCE_EXCERPT_FIELD = "EVIDENCE_EXCERPT_FIELD"
HALLUCINATED_FILE = "HALLUCINATED_FILE"
INVALID_LINE_FORMAT = "INVALID_LINE_FORMAT"
PARSING_ERROR = "PARSING_ERROR"
MISSING_WORKFLOW_ID = "MISSING_WORKFLOW_ID"
HALLUCINATED_WORKFLOW_ID = "HALLUCINATED_WORKFLOW_ID"
MISSING_HANDOFF_BLOCK = "MISSING_HANDOFF_BLOCK"
REGISTRY_NOT_FOUND = "REGISTRY_NOT_FOUND"
NO_LOGIC_TRACE = "NO_LOGIC_TRACE"
NO_EVIDENCE_FILE_CITATIONS = "NO_EVIDENCE_FILE_CITATIONS"
UNKNOWN_WEAKNESS_TYPE = "UNKNOWN_WEAKNESS_TYPE"

FILE_CITATION_RE = re.compile(
    r"`?[\w./\\-]+\.(?:md|py|yaml|yml|toml|txt)(?::\d+)?`?",
    re.IGNORECASE,
)

HEADING_RE = re.compile(r"^##\s+(?:\d+\.\s*)?(?P<name>.+?)\s*$", re.MULTILINE)


def _extract_sections(text: str) -> dict[str, str]:
    sections = {}
    matches = list(HEADING_RE.finditer(text))
    for idx, match in enumerate(matches):
        start = match.end()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(text)
        sections[match.group("name").strip().lower()] = text[start:end].strip()
    return sections


def validate_brief(artifact_path: str, repo_root: str = ".") -> list[str]:
    errors: list[str] = []

    if not os.path.exists(artifact_path):
        errors.append(format_error(BRIEF_FILE_NOT_FOUND, f"Brief file not found: {artifact_path}"))
        return errors

    with open(artifact_path, encoding="utf-8") as f:
        content = f.read()

    sections = _extract_sections(content)
    weakness_types = load_weakness_types(repo_root)

    # --- Novel checks from auteur validator ---

    # 1. Logic trace reasoning marker
    if "logic trace" not in content.lower():
        errors.append(
            format_error(NO_LOGIC_TRACE, "Brief does not include a logic trace showing diagnostic reasoning.")
        )

    # 2. File-level citations in the Evidence section
    evidence_section = sections.get("evidence", "")
    if evidence_section and not FILE_CITATION_RE.search(evidence_section):
        errors.append(
            format_error(
                NO_EVIDENCE_FILE_CITATIONS,
                "Evidence section has no file-level citations (e.g., path/to/file.py:42).",
            )
        )

    # 3. Recognized weakness type in the Weakest boundary section
    weakest_boundary = sections.get("weakest boundary", "")
    if weakest_boundary and weakness_types:
        if not any(kind.lower() in weakest_boundary.lower() for kind in weakness_types):
            types_list = ", ".join(weakness_types)
            errors.append(
                format_error(
                    UNKNOWN_WEAKNESS_TYPE,
                    f"Weakest boundary does not include a recognized weakness type. "
                    f"Known types: {types_list}",
                )
            )

    # --- Existing evidence_excerpts validation (now with error codes) ---
    evidence_match = re.search(
        r"```yaml\s+(evidence_excerpts:.*?)\s+```", content, re.DOTALL | re.IGNORECASE
    )
    if not evidence_match:
        evidence_match = re.search(r"```yaml\s+(- file:.*?)\s+```", content, re.DOTALL)

    if not evidence_match:
        errors.append(
            format_error(MISSING_EVIDENCE_EXCERPTS, "Missing or malformed YAML block for evidence_excerpts.")
        )
    else:
        try:
            data = yaml.safe_load(evidence_match.group(1))
            if isinstance(data, dict):
                excerpts = data.get("evidence_excerpts", [])
            elif isinstance(data, list):
                excerpts = data
            else:
                errors.append(
                    format_error(
                        PARSING_ERROR,
                        "evidence_excerpts block must be a list or dict containing 'evidence_excerpts'.",
                    )
                )
                excerpts = []

            if not excerpts:
                errors.append(format_error(EVIDENCE_EXCERPT_FIELD, "Evidence excerpts list is empty."))

            for i, exc in enumerate(excerpts):
                for field in ["file", "lines", "quote", "supports_claim"]:
                    if field not in exc:
                        errors.append(
                            format_error(EVIDENCE_EXCERPT_FIELD, f"Excerpt[{i}] missing required field: {field}")
                        )

                file_path = exc.get("file")
                if file_path:
                    if file_path.startswith("file:///"):
                        errors.append(
                            format_error(HALLUCINATED_FILE, f"Excerpt[{i}] uses absolute file:/// path: {file_path}")
                        )
                    else:
                        full_path = os.path.join(repo_root, file_path)
                        if not os.path.exists(full_path):
                            errors.append(
                                format_error(
                                    HALLUCINATED_FILE,
                                    f"Excerpt[{i}] references non-existent file: {file_path}",
                                )
                            )

                lines = exc.get("lines")
                if lines and not re.match(r"^L\d+(?:-L\d+)?$", str(lines)):
                    errors.append(
                        format_error(
                            INVALID_LINE_FORMAT,
                            f"Excerpt[{i}] has invalid lines format: {lines} (Expected Lx or Lx-Ly)",
                        )
                    )
        except Exception as e:
            errors.append(format_error(PARSING_ERROR, f"Failed to parse evidence YAML: {e}"))

    # --- Existing handoff / workflow ID validation (now with error codes) ---
    handoff_match = re.search(
        r"## 13\. Machine-readable handoff\s+```yaml\s+(.*?)\s+```",
        content,
        re.DOTALL | re.IGNORECASE,
    )
    if handoff_match:
        try:
            handoff_data = yaml.safe_load(handoff_match.group(1))
            workflow_id = handoff_data.get("recommended_workflow_id")

            if workflow_id:
                registry = load_workflow_registry(repo_root)
                if registry is None:
                    errors.append(
                        format_error(REGISTRY_NOT_FOUND, "Workflow registry not found.")
                    )
                else:
                    valid_ids = {w["id"] for w in registry.get("workflows", [])}
                    if workflow_id not in valid_ids:
                        errors.append(
                            format_error(
                                HALLUCINATED_WORKFLOW_ID,
                                f"Recommended workflow ID '{workflow_id}' not found in registry.",
                            )
                        )
            else:
                errors.append(
                    format_error(MISSING_WORKFLOW_ID, "Handoff missing 'recommended_workflow_id'.")
                )
        except Exception as e:
            errors.append(format_error(PARSING_ERROR, f"Failed to parse handoff YAML: {e}"))
    else:
        errors.append(
            format_error(MISSING_HANDOFF_BLOCK, "Missing 'Machine-readable handoff' YAML block.")
        )

    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Specialized validator for repository sensemaking brief.")
    parser.add_argument("artifact_path", nargs="?", help="Path to the brief .md file")
    parser.add_argument("--repo-root", default=".", help="Root of the repository for file checks")
    parser.add_argument("--list-codes", action="store_true", help="List all error codes and exit")
    args = parser.parse_args(argv)

    if args.list_codes:
        codes = [
            BRIEF_FILE_NOT_FOUND,
            PARSING_ERROR,
            MISSING_EVIDENCE_EXCERPTS,
            EVIDENCE_EXCERPT_FIELD,
            HALLUCINATED_FILE,
            INVALID_LINE_FORMAT,
            MISSING_WORKFLOW_ID,
            HALLUCINATED_WORKFLOW_ID,
            MISSING_HANDOFF_BLOCK,
            REGISTRY_NOT_FOUND,
            NO_LOGIC_TRACE,
            NO_EVIDENCE_FILE_CITATIONS,
            UNKNOWN_WEAKNESS_TYPE,
        ]
        print("Stable error codes for brief validation:")
        for code in codes:
            print(f"  {code}")
        return 0

    if not args.artifact_path:
        parser.print_usage()
        return 1

    errs = validate_brief(args.artifact_path, args.repo_root)
    if errs:
        for e in errs:
            print(f"ERROR {e}")
        return 1
    else:
        print("Brief verification passed! Evidence and workflow ID are valid.")
        return 0


if __name__ == "__main__":
    sys.exit(main())
