#!/usr/bin/env python
"""Opt-in live-provider release smoke for the Auteur V1 contract.

This script never prints or records credentials. It is intentionally separate
from normal CI because it performs a real provider call and may incur cost.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from auteur import __version__
from auteur.llm import LLMProviderError, LLMRequest
from auteur.llm.factory import build_client


def _candidate_sha() -> str:
    value = os.environ.get("AUTEUR_CANDIDATE_SHA") or os.environ.get("GITHUB_SHA")
    if value:
        return value
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], text=True, stderr=subprocess.DEVNULL
        ).strip()
    except (OSError, subprocess.SubprocessError):
        return "unknown"


def _write(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--provider", choices=["anthropic", "openai"], required=True)
    parser.add_argument("--model", default=None)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    evidence: dict[str, Any] = {
        "schema_version": "auteur-v1-live-provider-smoke-v1",
        "provider": args.provider,
        "model": args.model,
        "package_version": __version__,
        "candidate_sha": _candidate_sha(),
        "started_at": datetime.now(timezone.utc).isoformat(),
        "claim_scope": "operational adapter smoke only; no literary-quality claim",
        "credential_recorded": False,
    }
    try:
        client = build_client(args.provider, args.model)
        response = client.complete(
            LLMRequest(
                system="You are performing a bounded software integration smoke test.",
                user="Reply with the single token OK.",
                max_tokens=8,
                temperature=0.0,
            )
        )
        if not response.text.strip():
            raise ValueError("provider returned an empty response")
        evidence.update(
            {
                "status": "PASS",
                "response_sha256": hashlib.sha256(
                    response.text.encode("utf-8")
                ).hexdigest(),
                "input_tokens": response.input_tokens,
                "output_tokens": response.output_tokens,
            }
        )
        exit_code = 0
    except LLMProviderError as exc:
        evidence.update(
            {
                "status": "BLOCKED_OR_FAILED",
                "error_code": exc.code.value,
                "error_message": str(exc),
                "retriable": exc.retriable,
            }
        )
        exit_code = 2
    except Exception as exc:
        evidence.update(
            {
                "status": "FAILED",
                "error_code": "qualification_runner_error",
                "error_message": f"{exc.__class__.__name__}: {exc}",
            }
        )
        exit_code = 1
    evidence["finished_at"] = datetime.now(timezone.utc).isoformat()
    _write(args.output, evidence)
    print(json.dumps(evidence, indent=2, sort_keys=True))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
