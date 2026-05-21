"""Validator runner that reads artifact-contracts.yaml and executes the validation stack.

Usage:
    python scripts/validate-output.py <artifact_id> <artifact_path> [--repo-root PATH]

Reads the contract for the given artifact from artifact-contracts.yaml and runs:
  1. The generic validator (validate-artifact.py)
  2. Any specialized validators registered for that artifact

Exits 1 if any validator fails.
"""

import os
import sys
import subprocess
import argparse

from _validator_utils import format_error, load_artifact_contracts

CONTRACTS_FILE_NOT_FOUND = "CONTRACTS_FILE_NOT_FOUND"
CONTRACT_NOT_FOUND = "CONTRACT_NOT_FOUND"
VALIDATOR_NOT_FOUND = "VALIDATOR_NOT_FOUND"
VALIDATOR_FAILED = "VALIDATOR_FAILED"


def _resolve_validator_path(command: str) -> str | None:
    """Resolve a validator command like 'python scripts/validate-brief.py {artifact_path}'
    to the script path. Returns None if the script doesn't exist."""
    parts = command.split()
    # Find the first token that looks like a path to a .py file
    for token in parts:
        if token.endswith(".py") and os.path.exists(token):
            return token
    return None


def _run_validator(cmd: list[str], artifact_path: str, repo_root: str) -> tuple[int, str]:
    """Run a validator command and return (exit_code, output)."""
    # Replace {artifact_path} placeholder if present in any args
    resolved = [arg.replace("{artifact_path}", artifact_path) for arg in cmd]
    # Add --repo-root if not already present
    if "--repo-root" not in resolved:
        resolved.extend(["--repo-root", repo_root])

    result = subprocess.run(resolved, capture_output=True, text=True)
    output = (result.stdout + result.stderr).strip()
    return result.returncode, output


def validate_output(artifact_id: str, artifact_path: str, repo_root: str = ".") -> list[str]:
    """Run the full validation stack for an artifact. Returns list of error messages."""
    errors: list[str] = []

    if not os.path.exists(artifact_path):
        errors.append(format_error("FILE_NOT_FOUND", f"Artifact not found: {artifact_path}"))
        return errors

    contracts = load_artifact_contracts(repo_root)
    if contracts is None:
        errors.append(format_error(CONTRACTS_FILE_NOT_FOUND,
                                    "artifact-contracts.yaml not found."))
        return errors

    contract = next((a for a in contracts.get("artifacts", []) if a["id"] == artifact_id), None)
    if contract is None:
        errors.append(format_error(CONTRACT_NOT_FOUND,
                                    f"No contract found for artifact_id '{artifact_id}'"))
        return errors

    verification = contract.get("verification", {})

    # 1. Run generic validator
    generic_cmd = verification.get("generic_validator")
    if generic_cmd:
        parts = generic_cmd.split()
        script_path = _resolve_validator_path(generic_cmd)
        if script_path is None:
            errors.append(format_error(VALIDATOR_NOT_FOUND,
                                        f"Generic validator script not found: {generic_cmd}"))
        else:
            code, output = _run_validator(parts, artifact_path, repo_root)
            if code != 0:
                errors.append(format_error(VALIDATOR_FAILED,
                                            f"Generic validator failed:\n{output}"))

    # 2. Run specialized validators (only if generic passed)
    if not any(VALIDATOR_FAILED in e for e in errors):
        specialized = verification.get("specialized_validators", [])
        for spec_cmd in specialized:
            parts = spec_cmd.split()
            script_path = _resolve_validator_path(spec_cmd)
            if script_path is None:
                errors.append(format_error(VALIDATOR_NOT_FOUND,
                                            f"Specialized validator script not found: {spec_cmd}"))
                continue

            code, output = _run_validator(parts, artifact_path, repo_root)
            if code != 0:
                errors.append(format_error(VALIDATOR_FAILED,
                                            f"Specialized validator failed ({os.path.basename(script_path)}):\n{output}"))

    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run the full validation stack for an artifact."
    )
    parser.add_argument("artifact_id", help="Artifact ID from artifact-contracts.yaml")
    parser.add_argument("artifact_path", help="Path to the artifact markdown file")
    parser.add_argument("--repo-root", default=".", help="Root directory of the repository")
    args = parser.parse_args(argv)

    errs = validate_output(args.artifact_id, args.artifact_path, args.repo_root)
    if errs:
        for e in errs:
            print(f"ERROR {e}")
        return 1
    else:
        print(f"All validators passed for '{args.artifact_id}'.")
        return 0


if __name__ == "__main__":
    sys.exit(main())
