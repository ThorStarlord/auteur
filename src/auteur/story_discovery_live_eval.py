"""Manual Phase H live-provider Story Discovery evidence capture.

This module is deliberately a research harness, not a creative-quality judge.
It drives the existing public Story Discovery CLI with real providers, records
provenance and raw artifacts, and never performs canonical acceptance.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import platform
import subprocess
import sys
from contextlib import redirect_stderr, redirect_stdout
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Callable, Mapping, Sequence

import yaml

from auteur.story_discovery_brief import DiscoveryBrief, assess_intent_adequacy


SCHEMA_VERSION = 1
DEFAULT_CORPUS = Path("docs/research/story-discovery-phase-h-cases.yaml")
PROVIDER_KEYS = {
    "anthropic": "ANTHROPIC_API_KEY",
    "openai": "OPENAI_API_KEY",
}
_PROVIDER_DEFAULT = "<provider-default-at-recorded-revision>"


@dataclass(frozen=True)
class LiveEvalCase:
    case_id: str
    purpose: str
    focus: tuple[str, ...]
    brief_payload: dict[str, object]


@dataclass(frozen=True)
class ProviderSpec:
    name: str
    model: str | None

    @property
    def recorded_model(self) -> str:
        return self.model or _PROVIDER_DEFAULT


@dataclass(frozen=True)
class LiveEvalConfig:
    corpus_path: Path
    output_dir: Path
    providers: tuple[ProviderSpec, ...]
    case_ids: tuple[str, ...]
    dry_run: bool = False


def _sha256_bytes(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def _sha256_file(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def _utc_now() -> str:
    return datetime.now(UTC).isoformat()


def _repository_revision(cwd: Path) -> str | None:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=cwd,
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return None
    value = result.stdout.strip()
    return value or None


def _write_json(path: Path, payload: Mapping[str, object]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _redact(text: str, secrets: Sequence[str]) -> str:
    result = text
    for secret in secrets:
        if secret:
            result = result.replace(secret, "[REDACTED]")
    return result


def load_corpus(path: Path) -> dict[str, LiveEvalCase]:
    """Load and validate the versioned Phase H benchmark corpus offline."""

    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except (OSError, yaml.YAMLError) as exc:
        raise ValueError(f"could not read Phase H corpus {path}: {exc}") from exc
    if not isinstance(raw, dict):
        raise ValueError("Phase H corpus must be a mapping")
    if raw.get("schema_version") != SCHEMA_VERSION:
        raise ValueError(f"unsupported Phase H corpus schema_version: {raw.get('schema_version')!r}")
    items = raw.get("cases")
    if not isinstance(items, list) or not items:
        raise ValueError("Phase H corpus must contain a non-empty cases list")

    cases: dict[str, LiveEvalCase] = {}
    for index, item in enumerate(items, start=1):
        if not isinstance(item, dict):
            raise ValueError(f"Phase H case {index} must be a mapping")
        case_id = item.get("id")
        purpose = item.get("purpose", "")
        focus = item.get("focus", [])
        brief_payload = item.get("brief")
        if not isinstance(case_id, str) or not case_id.strip():
            raise ValueError(f"Phase H case {index} has no valid id")
        if case_id in cases:
            raise ValueError(f"duplicate Phase H case id: {case_id}")
        if not isinstance(purpose, str):
            raise ValueError(f"Phase H case {case_id} purpose must be text")
        if not isinstance(focus, list) or not all(isinstance(value, str) for value in focus):
            raise ValueError(f"Phase H case {case_id} focus must be a list of strings")
        if not isinstance(brief_payload, dict):
            raise ValueError(f"Phase H case {case_id} brief must be a mapping")

        try:
            brief = DiscoveryBrief.model_validate(brief_payload)
        except Exception as exc:
            raise ValueError(f"Phase H case {case_id} has invalid DiscoveryBrief: {exc}") from exc
        adequacy = assess_intent_adequacy(brief)
        if not adequacy.adequate:
            raise ValueError(
                f"Phase H case {case_id} is not intent-adequate: {', '.join(adequacy.missing)}"
            )
        declared = brief.declared_intent()
        cases[case_id] = LiveEvalCase(
            case_id=case_id,
            purpose=purpose,
            focus=tuple(focus),
            brief_payload=declared,
        )
    return cases


def resolve_providers(
    provider: str,
    *,
    anthropic_model: str | None = None,
    openai_model: str | None = None,
) -> tuple[ProviderSpec, ...]:
    if provider not in {"anthropic", "openai", "both"}:
        raise ValueError(f"unsupported provider selection: {provider}")
    if provider == "anthropic" and openai_model is not None:
        raise ValueError("--openai-model requires --provider openai or --provider both")
    if provider == "openai" and anthropic_model is not None:
        raise ValueError("--anthropic-model requires --provider anthropic or --provider both")
    if provider == "anthropic":
        return (ProviderSpec("anthropic", anthropic_model),)
    if provider == "openai":
        return (ProviderSpec("openai", openai_model),)
    return (
        ProviderSpec("anthropic", anthropic_model),
        ProviderSpec("openai", openai_model),
    )


def select_cases(
    corpus: Mapping[str, LiveEvalCase],
    *,
    requested: Sequence[str],
    all_cases: bool,
) -> tuple[str, ...]:
    if all_cases and requested:
        raise ValueError("use either --all-cases or one/more --case values, not both")
    if not all_cases and not requested:
        raise ValueError("select at least one --case or use --all-cases")
    if all_cases:
        return tuple(corpus.keys())
    unknown = [case_id for case_id in requested if case_id not in corpus]
    if unknown:
        raise ValueError("unknown Phase H case id(s): " + ", ".join(unknown))
    # Preserve user order, but avoid accidentally paying twice for the same case.
    return tuple(dict.fromkeys(requested))


def preflight_api_keys(
    providers: Sequence[ProviderSpec],
    environ: Mapping[str, str],
) -> tuple[str, ...]:
    missing = [PROVIDER_KEYS[item.name] for item in providers if not environ.get(PROVIDER_KEYS[item.name])]
    if missing:
        raise ValueError("missing required API key environment variable(s): " + ", ".join(missing))
    return tuple(environ[PROVIDER_KEYS[item.name]] for item in providers)


def build_story_discovery_argv(
    *,
    provider: ProviderSpec,
    project_dir: Path,
    brief_path: Path,
    output_dir: Path,
) -> list[str]:
    argv = [
        "story-discovery",
        "run",
        "--brief",
        str(brief_path),
        "--recommend",
        "--output",
        str(output_dir),
        "--project",
        str(project_dir),
        "--provider",
        provider.name,
    ]
    if provider.model is not None:
        argv.extend(["--model", provider.model])
    return argv


def _artifact_inventory(discovery_dir: Path) -> list[str]:
    if not discovery_dir.is_dir():
        return []
    return sorted(
        str(path.relative_to(discovery_dir))
        for path in discovery_dir.rglob("*")
        if path.is_file()
    )


def _safe_cli_call(
    argv: list[str],
    *,
    cli_main: Callable[[list[str]], int],
    secrets: Sequence[str],
) -> tuple[int, str, str]:
    stdout = io.StringIO()
    stderr = io.StringIO()
    exit_code = 70
    with redirect_stdout(stdout), redirect_stderr(stderr):
        try:
            exit_code = int(cli_main(argv))
        except SystemExit as exc:
            exit_code = int(exc.code) if isinstance(exc.code, int) else 70
        except Exception as exc:  # capture unexpected live-provider/runtime failure as evidence
            print(f"Unhandled {type(exc).__name__}: {exc}", file=sys.stderr)
            exit_code = 70
    return exit_code, _redact(stdout.getvalue(), secrets), _redact(stderr.getvalue(), secrets)


def _run_review(
    project_dir: Path,
    *,
    cli_main: Callable[[list[str]], int],
    secrets: Sequence[str],
) -> tuple[int, str, str]:
    return _safe_cli_call(
        ["story-discovery", "review", "--project", str(project_dir)],
        cli_main=cli_main,
        secrets=secrets,
    )


def _manifest(
    config: LiveEvalConfig,
    *,
    corpus_sha256: str,
    revision: str | None,
    started_at: str,
) -> dict[str, object]:
    return {
        "schema_version": SCHEMA_VERSION,
        "phase": "H1_capture",
        "started_at_utc": started_at,
        "repository_revision": revision,
        "python_version": platform.python_version(),
        "platform": platform.platform(),
        "corpus": {
            "path": str(config.corpus_path),
            "sha256": corpus_sha256,
        },
        "providers": [
            {"provider": item.name, "model": item.recorded_model}
            for item in config.providers
        ],
        "case_ids": list(config.case_ids),
        "canonical_acceptance_allowed": False,
        "automatic_quality_scoring": False,
    }


def _planned_matrix(config: LiveEvalConfig) -> list[dict[str, str]]:
    return [
        {
            "provider": provider.name,
            "model": provider.recorded_model,
            "case_id": case_id,
        }
        for provider in config.providers
        for case_id in config.case_ids
    ]


def run_live_evaluation(
    config: LiveEvalConfig,
    *,
    cli_main: Callable[[list[str]], int] | None = None,
    environ: Mapping[str, str] | None = None,
    revision_fn: Callable[[Path], str | None] = _repository_revision,
    now_fn: Callable[[], str] = _utc_now,
) -> int:
    """Execute and capture one explicit Phase H provider/case matrix.

    Return codes:
      0: all live runs and deterministic reviews returned success
      1: local preflight/configuration failure
      2: one or more captured live/review runs returned non-zero
      3: canonical-acceptance invariant violation
    """

    env = os.environ if environ is None else environ
    try:
        corpus = load_corpus(config.corpus_path)
        if config.output_dir.exists():
            raise ValueError(f"output directory already exists: {config.output_dir}")
        for case_id in config.case_ids:
            if case_id not in corpus:
                raise ValueError(f"unknown Phase H case id: {case_id}")
        if not config.providers:
            raise ValueError("at least one provider is required")
        unknown_providers = [item.name for item in config.providers if item.name not in PROVIDER_KEYS]
        if unknown_providers:
            raise ValueError("unsupported provider(s): " + ", ".join(unknown_providers))
        if not config.case_ids:
            raise ValueError("at least one case is required")
        secrets: tuple[str, ...] = () if config.dry_run else preflight_api_keys(config.providers, env)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    if config.dry_run:
        print(json.dumps({"dry_run": True, "matrix": _planned_matrix(config)}, indent=2))
        return 0

    if cli_main is None:
        from auteur.cli import main as auteur_main

        cli_main = auteur_main

    started_at = now_fn()
    config.output_dir.mkdir(parents=True, exist_ok=False)
    revision = revision_fn(Path.cwd())
    _write_json(
        config.output_dir / "run_manifest.json",
        _manifest(
            config,
            corpus_sha256=_sha256_file(config.corpus_path),
            revision=revision,
            started_at=started_at,
        ),
    )

    results: list[dict[str, object]] = []
    any_failure = False
    invariant_violation = False

    for provider in config.providers:
        for case_id in config.case_ids:
            case = corpus[case_id]
            case_root = config.output_dir / provider.name / case_id
            project_dir = case_root / "project"
            discovery_dir = project_dir / "story_discovery"
            discovery_dir.mkdir(parents=True, exist_ok=False)
            brief_path = discovery_dir / "brief.yaml"
            brief_text = yaml.safe_dump(case.brief_payload, sort_keys=False, allow_unicode=True)
            brief_path.write_text(brief_text, encoding="utf-8")

            argv = build_story_discovery_argv(
                provider=provider,
                project_dir=project_dir,
                brief_path=brief_path,
                output_dir=discovery_dir,
            )
            if "accept" in argv:
                # Defensive assertion for future edits to this research harness.
                raise RuntimeError("Phase H capture harness may never construct an acceptance command")

            _write_json(
                case_root / "case_manifest.json",
                {
                    "schema_version": SCHEMA_VERSION,
                    "case_id": case.case_id,
                    "purpose": case.purpose,
                    "focus": list(case.focus),
                    "provider": provider.name,
                    "model": provider.recorded_model,
                    "declared_brief_sha256": _sha256_bytes(brief_text.encode("utf-8")),
                    "command": argv,
                },
            )

            exit_code, stdout_text, stderr_text = _safe_cli_call(
                argv,
                cli_main=cli_main,
                secrets=secrets,
            )
            (case_root / "stdout.txt").write_text(stdout_text, encoding="utf-8")
            (case_root / "stderr.txt").write_text(stderr_text, encoding="utf-8")

            review_exit: int | None = None
            review_stdout = ""
            review_stderr = ""
            if exit_code == 0:
                review_exit, review_stdout, review_stderr = _run_review(
                    project_dir,
                    cli_main=cli_main,
                    secrets=secrets,
                )
                (case_root / "review_stdout.txt").write_text(review_stdout, encoding="utf-8")
                (case_root / "review_stderr.txt").write_text(review_stderr, encoding="utf-8")

            canonical_path = project_dir / "story_identity.yaml"
            canonical_exists = canonical_path.exists()
            if canonical_exists:
                invariant_violation = True
            if exit_code != 0 or (review_exit is not None and review_exit != 0):
                any_failure = True

            result = {
                "case_id": case_id,
                "provider": provider.name,
                "model": provider.recorded_model,
                "completed_at_utc": now_fn(),
                "exit_code": exit_code,
                "review_exit_code": review_exit,
                "canonical_story_identity_exists": canonical_exists,
                "artifact_files": _artifact_inventory(discovery_dir),
            }
            _write_json(case_root / "result.json", result)
            results.append(result)

    summary = {
        "schema_version": SCHEMA_VERSION,
        "phase": "H1_capture",
        "completed_at_utc": now_fn(),
        "result_count": len(results),
        "all_runs_successful": not any_failure,
        "canonical_acceptance_invariant_preserved": not invariant_violation,
        "results": results,
    }
    _write_json(config.output_dir / "run_summary.json", summary)

    if invariant_violation:
        print("Error: benchmark harness observed canonical story_identity.yaml creation", file=sys.stderr)
        return 3
    if any_failure:
        return 2
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="story_discovery_live_eval",
        description="Capture Phase H live-provider Story Discovery evidence without accepting canon.",
    )
    parser.add_argument("--corpus", type=Path, default=DEFAULT_CORPUS)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--provider", choices=["anthropic", "openai", "both"], required=True)
    parser.add_argument("--anthropic-model", default=None)
    parser.add_argument("--openai-model", default=None)
    selection = parser.add_mutually_exclusive_group(required=True)
    selection.add_argument("--case", action="append", default=[])
    selection.add_argument("--all-cases", action="store_true")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate corpus/selection and print the matrix without requiring API keys or creating output.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        corpus = load_corpus(args.corpus)
        providers = resolve_providers(
            args.provider,
            anthropic_model=args.anthropic_model,
            openai_model=args.openai_model,
        )
        case_ids = select_cases(corpus, requested=args.case, all_cases=args.all_cases)
    except ValueError as exc:
        parser.error(str(exc))
    config = LiveEvalConfig(
        corpus_path=args.corpus,
        output_dir=args.output,
        providers=providers,
        case_ids=case_ids,
        dry_run=args.dry_run,
    )
    return run_live_evaluation(config)


if __name__ == "__main__":
    raise SystemExit(main())
