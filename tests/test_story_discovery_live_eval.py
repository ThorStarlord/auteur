from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

from auteur.story_discovery_live_eval import (
    DEFAULT_CORPUS,
    LiveEvalConfig,
    ProviderSpec,
    build_story_discovery_argv,
    load_corpus,
    resolve_providers,
    run_live_evaluation,
    select_cases,
)


def _minimal_corpus(path: Path) -> Path:
    payload = {
        "schema_version": 1,
        "cases": [
            {
                "id": "case_one",
                "purpose": "controlled live-eval harness fixture",
                "focus": ["causal distinctness"],
                "brief": {
                    "premise": "A sealed-room mystery with one physically possible solution.",
                    "story_type": {"genre": "mystery", "target_audience": "adult"},
                    "target_experience": {
                        "primary_emotional_promise": "suspicion resolving into fair-play relief"
                    },
                },
            },
            {
                "id": "case_two",
                "purpose": "second controlled fixture",
                "focus": ["craft teaching"],
                "brief": {
                    "premise": "A family house becomes one room smaller every night.",
                    "story_type": {"genre": "horror", "target_audience": "adult"},
                    "target_experience": {
                        "primary_emotional_promise": "intimate dread under physical compression"
                    },
                },
            },
        ],
    }
    path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")
    return path


def _config(tmp_path: Path, corpus: Path, *providers: ProviderSpec) -> LiveEvalConfig:
    return LiveEvalConfig(
        corpus_path=corpus,
        output_dir=tmp_path / "run",
        providers=tuple(providers),
        case_ids=("case_one",),
    )


def _successful_fake_cli(calls: list[list[str]], *, secret: str | None = None):
    def fake(argv: list[str]) -> int:
        calls.append(list(argv))
        if argv[:2] == ["story-discovery", "run"]:
            output = Path(argv[argv.index("--output") + 1])
            (output / "candidate_1.yaml").write_text("title: Captured candidate\n", encoding="utf-8")
            print("live discovery completed")
            if secret:
                print(f"provider echoed {secret}")
            return 0
        if argv[:2] == ["story-discovery", "review"]:
            print("deterministic review reconstructed")
            return 0
        raise AssertionError(f"unexpected CLI call: {argv}")

    return fake


def test_versioned_phase_h_corpus_is_intent_adequate_and_has_six_cases():
    cases = load_corpus(DEFAULT_CORPUS)

    assert list(cases) == [
        "h01_dead_channel",
        "h02_between_floors",
        "h03_nothing_missing",
        "h04_missing_room",
        "h05_what_she_saves",
        "h06_fixed_point",
    ]
    assert all(case.brief_payload["premise"] for case in cases.values())


def test_load_corpus_rejects_duplicate_ids(tmp_path: Path):
    path = _minimal_corpus(tmp_path / "cases.yaml")
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    payload["cases"][1]["id"] = "case_one"
    path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")

    with pytest.raises(ValueError, match="duplicate Phase H case id"):
        load_corpus(path)


def test_provider_and_case_selection_are_explicit_and_deterministic(tmp_path: Path):
    cases = load_corpus(_minimal_corpus(tmp_path / "cases.yaml"))

    providers = resolve_providers(
        "both",
        anthropic_model="claude-test",
        openai_model="gpt-test",
    )
    assert providers == (
        ProviderSpec("anthropic", "claude-test"),
        ProviderSpec("openai", "gpt-test"),
    )
    assert select_cases(cases, requested=["case_two", "case_one", "case_two"], all_cases=False) == (
        "case_two",
        "case_one",
    )
    assert select_cases(cases, requested=[], all_cases=True) == ("case_one", "case_two")

    with pytest.raises(ValueError, match="unknown Phase H case"):
        select_cases(cases, requested=["missing"], all_cases=False)
    with pytest.raises(ValueError, match="select at least one"):
        select_cases(cases, requested=[], all_cases=False)


def test_story_discovery_command_is_real_intent_aware_path_and_never_accepts(tmp_path: Path):
    argv = build_story_discovery_argv(
        provider=ProviderSpec("anthropic", "claude-test"),
        project_dir=tmp_path / "project",
        brief_path=tmp_path / "project" / "story_discovery" / "brief.yaml",
        output_dir=tmp_path / "project" / "story_discovery",
    )

    assert argv[:2] == ["story-discovery", "run"]
    assert "--brief" in argv
    assert "--recommend" in argv
    assert argv[argv.index("--provider") + 1] == "anthropic"
    assert argv[argv.index("--model") + 1] == "claude-test"
    assert "accept" not in argv


def test_missing_api_key_fails_before_output_or_cli_use(tmp_path: Path):
    corpus = _minimal_corpus(tmp_path / "cases.yaml")
    calls: list[list[str]] = []

    result = run_live_evaluation(
        _config(tmp_path, corpus, ProviderSpec("anthropic", None)),
        cli_main=_successful_fake_cli(calls),
        environ={},
    )

    assert result == 1
    assert calls == []
    assert not (tmp_path / "run").exists()


def test_output_collision_fails_closed_before_cli_use(tmp_path: Path):
    corpus = _minimal_corpus(tmp_path / "cases.yaml")
    output = tmp_path / "run"
    output.mkdir()
    calls: list[list[str]] = []

    result = run_live_evaluation(
        LiveEvalConfig(
            corpus_path=corpus,
            output_dir=output,
            providers=(ProviderSpec("anthropic", None),),
            case_ids=("case_one",),
        ),
        cli_main=_successful_fake_cli(calls),
        environ={"ANTHROPIC_API_KEY": "secret"},
    )

    assert result == 1
    assert calls == []


def test_dry_run_needs_no_key_and_creates_no_evidence_directory(tmp_path: Path, capsys):
    corpus = _minimal_corpus(tmp_path / "cases.yaml")
    calls: list[list[str]] = []

    result = run_live_evaluation(
        LiveEvalConfig(
            corpus_path=corpus,
            output_dir=tmp_path / "run",
            providers=(ProviderSpec("openai", "gpt-test"),),
            case_ids=("case_one",),
            dry_run=True,
        ),
        cli_main=_successful_fake_cli(calls),
        environ={},
    )

    assert result == 0
    assert calls == []
    assert not (tmp_path / "run").exists()
    assert '"dry_run": true' in capsys.readouterr().out


def test_capture_writes_manifest_before_cli_and_persists_raw_evidence_with_secret_redaction(
    tmp_path: Path,
):
    corpus = _minimal_corpus(tmp_path / "cases.yaml")
    output = tmp_path / "run"
    calls: list[list[str]] = []
    secret = "sk-test-super-secret"

    def checking_cli(argv: list[str]) -> int:
        assert (output / "run_manifest.json").is_file()
        return _successful_fake_cli(calls, secret=secret)(argv)

    result = run_live_evaluation(
        LiveEvalConfig(
            corpus_path=corpus,
            output_dir=output,
            providers=(ProviderSpec("anthropic", "claude-test"),),
            case_ids=("case_one",),
        ),
        cli_main=checking_cli,
        environ={"ANTHROPIC_API_KEY": secret},
        revision_fn=lambda _cwd: "abc123",
        now_fn=lambda: "2026-08-21T16:00:00+00:00",
    )

    assert result == 0
    manifest = json.loads((output / "run_manifest.json").read_text(encoding="utf-8"))
    assert manifest["repository_revision"] == "abc123"
    assert manifest["providers"] == [{"provider": "anthropic", "model": "claude-test"}]
    assert manifest["canonical_acceptance_allowed"] is False
    assert manifest["automatic_quality_scoring"] is False
    assert "ANTHROPIC_API_KEY" not in json.dumps(manifest)
    case_root = output / "anthropic" / "case_one"
    assert secret not in (case_root / "stdout.txt").read_text(encoding="utf-8")
    assert "[REDACTED]" in (case_root / "stdout.txt").read_text(encoding="utf-8")
    assert "deterministic review reconstructed" in (case_root / "review_stdout.txt").read_text(
        encoding="utf-8"
    )
    result_payload = json.loads((case_root / "result.json").read_text(encoding="utf-8"))
    assert result_payload["exit_code"] == 0
    assert result_payload["review_exit_code"] == 0
    assert "candidate_1.yaml" in result_payload["artifact_files"]
    assert not (case_root / "project" / "story_identity.yaml").exists()
    assert all("accept" not in argv for argv in calls)


def test_both_providers_capture_separate_cells_and_preserve_explicit_models(tmp_path: Path):
    corpus = _minimal_corpus(tmp_path / "cases.yaml")
    calls: list[list[str]] = []
    output = tmp_path / "run"

    result = run_live_evaluation(
        LiveEvalConfig(
            corpus_path=corpus,
            output_dir=output,
            providers=(
                ProviderSpec("anthropic", "claude-test"),
                ProviderSpec("openai", "gpt-test"),
            ),
            case_ids=("case_one",),
        ),
        cli_main=_successful_fake_cli(calls),
        environ={"ANTHROPIC_API_KEY": "a-secret", "OPENAI_API_KEY": "o-secret"},
        revision_fn=lambda _cwd: None,
        now_fn=lambda: "2026-08-21T16:00:00+00:00",
    )

    assert result == 0
    assert (output / "anthropic" / "case_one" / "result.json").is_file()
    assert (output / "openai" / "case_one" / "result.json").is_file()
    summary = json.loads((output / "run_summary.json").read_text(encoding="utf-8"))
    assert summary["result_count"] == 2
    assert summary["all_runs_successful"] is True
    run_calls = [argv for argv in calls if argv[:2] == ["story-discovery", "run"]]
    assert [argv[argv.index("--model") + 1] for argv in run_calls] == ["claude-test", "gpt-test"]


def test_live_failure_is_retained_and_matrix_returns_two(tmp_path: Path):
    corpus = _minimal_corpus(tmp_path / "cases.yaml")
    output = tmp_path / "run"

    def failing_cli(argv: list[str]) -> int:
        if argv[:2] == ["story-discovery", "run"]:
            print("provider failure", file=__import__("sys").stderr)
            return 9
        raise AssertionError("review should not run after failed discovery")

    result = run_live_evaluation(
        _config(tmp_path, corpus, ProviderSpec("anthropic", None)),
        cli_main=failing_cli,
        environ={"ANTHROPIC_API_KEY": "secret"},
        now_fn=lambda: "2026-08-21T16:00:00+00:00",
    )

    assert result == 2
    case_root = output / "anthropic" / "case_one"
    assert "provider failure" in (case_root / "stderr.txt").read_text(encoding="utf-8")
    assert not (case_root / "review_stdout.txt").exists()
    assert json.loads((case_root / "result.json").read_text(encoding="utf-8"))["exit_code"] == 9


def test_canonical_identity_creation_is_hard_invariant_violation(tmp_path: Path):
    corpus = _minimal_corpus(tmp_path / "cases.yaml")

    def bad_cli(argv: list[str]) -> int:
        if argv[:2] == ["story-discovery", "run"]:
            project = Path(argv[argv.index("--project") + 1])
            (project / "story_identity.yaml").write_text("title: forbidden\n", encoding="utf-8")
            return 0
        if argv[:2] == ["story-discovery", "review"]:
            return 0
        raise AssertionError(argv)

    result = run_live_evaluation(
        _config(tmp_path, corpus, ProviderSpec("anthropic", None)),
        cli_main=bad_cli,
        environ={"ANTHROPIC_API_KEY": "secret"},
        now_fn=lambda: "2026-08-21T16:00:00+00:00",
    )

    assert result == 3
    summary = json.loads((tmp_path / "run" / "run_summary.json").read_text(encoding="utf-8"))
    assert summary["canonical_acceptance_invariant_preserved"] is False
