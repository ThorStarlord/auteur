"""Shared engine for the offline Auteur stress harness (scenarios A-D).

Imported by both the pytest stress tests (``stress/test_stress_*.py``)
and the standalone runner (``scripts/stress/run_stress.py``).

Everything here is deterministic, offline, and zero-API-cost:

- all LLM traffic is scripted through ``FakeClient`` (and ``RetryingClient``
  with ``base_delay=0.0`` for instant, deterministic backoff);
- ``random`` is seeded at the top of every scenario;
- no network calls, no API keys, no real provider clients.

Measurements use ``time.perf_counter`` for wall time and ``tracemalloc`` for
peak traced memory of in-process operations. Assertions live in the pytest
tests; the scenario functions only record metrics and boolean checks.
"""

from __future__ import annotations

import contextlib
import io
import json
import os
import random
import subprocess
import sys
import time
import tracemalloc
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

import yaml

from auteur.blueprint import StoryBlueprint
from auteur.cartographer_compiler import compile_outline
from auteur.cli import main as cli_main
from auteur.expression.book import BookExpressionStore
from auteur.expression.composition import ChapterExpressionStore
from auteur.expression.pilot import ExpressionStore
from auteur.llm import LLMRequest, LLMResponse, RetriableError
from auteur.llm.fake import FakeClient
from auteur.llm.retrying import RetryingClient
from auteur.pipeline import PipelineRunner
from auteur.provenance import ArtifactStore
from auteur.project import Project

# This file lives in <repo>/stress/; the repo root is one directory up.
REPO_ROOT = Path(__file__).resolve().parents[1]
SAMPLE_BLUEPRINT = REPO_ROOT / "examples" / "sample_blueprint.yaml"
LAUNCHER = REPO_ROOT / ".venv" / "Scripts" / "auteur.exe"

# Fallback invocation used only when the editable-install launcher is absent.
_CLI_SHIM = "import sys; from auteur.cli import main; sys.exit(main())"

SCALES = ("smoke", "full")

# Per-scale knobs. "smoke" finishes in seconds; "full" is the meaningful default.
SCALE_SPECS: dict[str, dict[str, int]] = {
    "smoke": {
        "giant_chapters": 12,
        "giant_extra_characters": 8,
        "book_chapters": 2,
        "book_prose_kb": 20,
        "extra_projects": 2,
        "draft_file_kb": 40,
        "pipeline_chapters": 2,
        "pipeline_prose_kb": 2,
        "conc_same_workers": 3,
        "conc_distinct_projects": 2,
    },
    "full": {
        "giant_chapters": 300,
        "giant_extra_characters": 60,
        "book_chapters": 8,
        "book_prose_kb": 250,
        "extra_projects": 4,
        "draft_file_kb": 300,
        "pipeline_chapters": 10,
        "pipeline_prose_kb": 30,
        "conc_same_workers": 6,
        "conc_distinct_projects": 4,
    },
}

_SUBPROCESS_TIMEOUT_S = 180.0

# Prose generators -- fixed sentences, repeated to a target byte size.
_BOOK_SENTENCE = (
    "Mara counted the river's breath and found it shorter than the ledger "
    "claimed. The beacon tower held its ground against the wind, and so did she. "
)
_BARD_SENTENCE = (
    "Kael waited in the tavern while the storm argued with the shutters, and "
    "the ring whispered its old arithmetic of debts. "
)


def get_scale() -> str:
    """Read the scale knob from AUTEUR_STRESS_SCALE (default: full)."""
    raw = os.environ.get("AUTEUR_STRESS_SCALE", "full").strip().lower()
    if raw not in SCALES:
        raise ValueError(f"AUTEUR_STRESS_SCALE must be one of {SCALES}, got {raw!r}")
    return raw


def resolve_scale(explicit: str | None = None) -> str:
    """Resolve the scale from an explicit value or the environment."""
    if explicit is not None:
        if explicit not in SCALES:
            raise ValueError(f"scale must be one of {SCALES}, got {explicit!r}")
        return explicit
    return get_scale()


def spec(scale: str) -> dict[str, int]:
    return SCALE_SPECS[scale]


class Measured:
    """Measure wall time and peak traced memory for one operation.

    Usage: ``with Measured("label", sink): do_work()``. Results are written to
    ``sink[label] = {"wall_s": ..., "peak_traced_bytes": ...}``. If tracemalloc
    was already tracing on entry (nested use), this context leaves it running.
    """

    def __init__(self, label: str, sink: dict[str, Any]) -> None:
        self._label = label
        self._sink = sink
        self._t0 = 0.0
        self._outer_tracing = False

    def __enter__(self) -> "Measured":
        self._t0 = time.perf_counter()
        self._outer_tracing = tracemalloc.is_tracing()
        if not self._outer_tracing:
            tracemalloc.start()
        return self

    def __exit__(self, *exc: object) -> None:
        elapsed = time.perf_counter() - self._t0
        _, peak = tracemalloc.get_traced_memory()
        if not self._outer_tracing:
            tracemalloc.stop()
        self._sink[self._label] = {
            "wall_s": round(elapsed, 6),
            "peak_traced_bytes": peak,
        }


def run_cli_inprocess(
    argv: list[str], sink: dict[str, Any], label: str
) -> tuple[int, str]:
    """Run the real CLI dispatch in-process (tracemalloc-visible), capture stdout."""
    with Measured(label, sink):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = cli_main(list(argv))
    return rc, buf.getvalue()


def cli_command(args: list[str]) -> list[str]:
    """Build a subprocess command for the real CLI launcher."""
    if LAUNCHER.exists():
        return [str(LAUNCHER), *args]
    return [sys.executable, "-c", _CLI_SHIM, *args]


def run_cli_subprocess(
    args: list[str], timeout_s: float = _SUBPROCESS_TIMEOUT_S
) -> dict[str, Any]:
    """Run the real CLI as a subprocess; return rc/stdout/stderr/wall time."""
    cmd = cli_command(args)
    t0 = time.perf_counter()
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout_s,
        )
        rc, out, err, timed_out = proc.returncode, proc.stdout, proc.stderr, False
    except subprocess.TimeoutExpired:
        rc, out, err, timed_out = -1, "", f"timed out after {timeout_s}s", True
    return {
        "argv": args,
        "rc": rc,
        "stdout": out,
        "stderr": err,
        "timed_out": timed_out,
        "wall_s": round(time.perf_counter() - t0, 6),
    }


def no_traceback(stderr: str) -> bool:
    """True when stderr carries no unhandled Python traceback."""
    return "Traceback (most recent call last)" not in stderr


def build_giant_blueprint(path: Path, chapters: int, extra_characters: int) -> Path:
    """Programmatically derive a large valid blueprint from the sample."""
    raw = yaml.safe_load(SAMPLE_BLUEPRINT.read_text(encoding="utf-8"))
    raw["structure"]["estimated_chapters"] = chapters
    raw["tension_waveform"]["target_curve"] = [
        {"chapter_index": i, "score": (i % 10) + 1, "label": f"beat_{i:03d}"}
        for i in range(1, chapters + 1)
    ]
    raw["characters"] = list(raw.get("characters", [])) + [
        {
            "name": f"Ensemble{i:03d}",
            "role": "supporting",
            "arc_type": "flat",
            "arc_start_percentage": 0,
            "arc_end_percentage": 0,
        }
        for i in range(extra_characters)
    ]
    StoryBlueprint.model_validate(raw)  # fail fast before writing
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(raw, sort_keys=False), encoding="utf-8")
    return path


def chapter_outline_yaml(chapter_index: int, tension: int = 4) -> str:
    """Canonical valid chapter outline (same schema the repo's tests script)."""
    return f"""
scope: chapter
chapter_index: {chapter_index}
chapter_summary: Kael returns to the tavern.
scenes:
  - scene_id: s{chapter_index}
    pov_character: Kael
    location: taverntown
    summary: He nurses a drink.
    key_events: [drinks, broods]
    character_state_changes: []
    arc_advancements: []
    estimated_tension: {tension}
    emotional_tone: subtle unease
arc_pushes: []
contract_compliance: []
expected_elements_touched: []
forbidden_tropes_avoided: [chosen_one_prophecy, resurrected_hero, deus_ex_machina_rescue]
estimated_chapter_tension: {tension}
thematic_reinforcement: redemption costs more than Kael wants to pay
conflict_report: null
"""


def passing_iteration_responses(bard_text: str) -> list[LLMResponse]:
    """One passing draft iteration: 1 bard response + 5 critic responses."""
    bard = LLMResponse(text=bard_text, input_tokens=20, output_tokens=10)
    contract = LLMResponse(text="findings: []", input_tokens=5, output_tokens=2)
    others = [
        LLMResponse(text="findings: []", input_tokens=1, output_tokens=1)
        for _ in range(4)
    ]
    return [bard, contract, *others]


def _prose(template: str, target_bytes: int) -> str:
    repeats = max(1, (target_bytes + len(template) - 1) // len(template))
    return template * repeats


def build_expression_chapter(
    project: Path, num: int, prose: str, accepted_by: str = "stress-harness"
) -> None:
    """Build one accepted chapter expression through the native stores."""
    nn = f"{num:02d}"
    store = ArtifactStore(project)
    outline = project / "chapters" / nn / "outline.yaml"
    outline.parent.mkdir(parents=True, exist_ok=True)
    outline.write_text(
        yaml.safe_dump(
            {
                "chapter_id": f"chapter_{nn}",
                "chapter_number": num,
                "scenes": [f"scene_{nn}_01"],
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    store.accept(outline, "chapter_outline", accepted_by=accepted_by)
    scene = project / "chapters" / nn / "scenes" / f"scene_{nn}_01.yaml"
    scene.parent.mkdir(parents=True, exist_ok=True)
    scene.write_text(
        yaml.safe_dump(
            {
                "scene_id": f"scene_{nn}_01",
                "participants": ["mara"],
                "location": "river beacon tower",
                "outcome": "Mara keeps the ledger and repairs the beacon.",
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    store.accept(scene, "scene_realization", accepted_by=accepted_by)
    expression_store = ExpressionStore(project)
    candidate = expression_store.generate(
        scene, prose, executor={"kind": "canonical-reference"}
    )
    expression_store.accept(candidate.candidate_id, accepted_by=accepted_by)
    chapter_store = ChapterExpressionStore(project)
    chapter = chapter_store.compose(f"chapter_{nn}")
    chapter_store.accept(chapter.artifact_id, accepted_by=accepted_by)


def build_book_project(
    project: Path, chapters: int, prose_bytes: int, title: str = "Stress Harvest"
) -> None:
    """Build a publishable project: accepted chapter expressions + accepted book."""
    project.mkdir(parents=True, exist_ok=True)
    for num in range(1, chapters + 1):
        build_expression_chapter(project, num, _prose(_BOOK_SENTENCE, prose_bytes))
    book_store = BookExpressionStore(project)
    manifest = book_store.compose(
        [f"chapter_{n:02d}" for n in range(1, chapters + 1)], title=title
    )
    book_store.accept(manifest["book_expression_id"], accepted_by="stress-harness")


def _diagnose_output_path(args: list[str]) -> Path:
    return Path(args[args.index("--output") + 1])


def _json_report_parses(path: Path) -> bool:
    if not path.exists():
        return False
    try:
        return isinstance(json.loads(path.read_text(encoding="utf-8")), dict)
    except (json.JSONDecodeError, OSError):
        return False


def normalize_status_json(text: str) -> dict[str, Any]:
    """Parse `auteur status --json` output, dropping volatile fields."""
    data = json.loads(text)
    data.pop("gathered_at", None)
    return data


def artifact_parse_checks(project: Path) -> dict[str, Any]:
    """Check that core project artifacts still parse (no corrupt/partial writes)."""
    checks: dict[str, Any] = {}

    def _parses_yaml(path: Path) -> bool:
        if not path.exists():
            return False
        return isinstance(yaml.safe_load(path.read_text(encoding="utf-8")), dict)

    def _parses_json(path: Path) -> bool:
        if not path.exists():
            return False
        return isinstance(json.loads(path.read_text(encoding="utf-8")), dict)

    checks["blueprint_yaml_parses"] = _parses_yaml(project / "blueprint.yaml")
    checks["project_metadata_parses"] = _parses_yaml(project / ".auteur" / "project.yaml")
    checks["bible_json_parses"] = _parses_json(project / "bible.json")
    outlines = sorted(project.glob("chapters/*/outline.yaml"))
    checks["chapter_outline_count"] = len(outlines)
    checks["chapter_outlines_parse"] = all(_parses_yaml(p) for p in outlines)
    return checks


# ---------------------------------------------------------------------------
# Scenario A - artifact scale
# ---------------------------------------------------------------------------


def run_scenario_a(base_dir: Path, scale: str) -> dict[str, Any]:
    """Large artifacts: giant blueprint, big prose book, extra small projects."""
    random.seed(0)
    knobs = spec(scale)
    sink: dict[str, Any] = {}
    checks: dict[str, Any] = {}
    metrics: dict[str, Any] = {}
    work = base_dir / "scenario_a"
    work.mkdir(parents=True, exist_ok=True)

    # A1. Giant blueprint -> whole-story structure diagnostics (CLI dispatch).
    giant_bp = build_giant_blueprint(
        work / "giant_blueprint.yaml",
        knobs["giant_chapters"],
        knobs["giant_extra_characters"],
    )
    metrics["giant_blueprint_bytes"] = giant_bp.stat().st_size
    metrics["giant_chapters"] = knobs["giant_chapters"]
    diagnose_report = work / "giant_structure_report.json"
    rc, _ = run_cli_inprocess(
        ["structure", "diagnose", str(giant_bp), "--output", str(diagnose_report)],
        sink,
        "structure_diagnose",
    )
    report = None
    if diagnose_report.exists():
        with contextlib.suppress(json.JSONDecodeError, OSError):
            report = json.loads(diagnose_report.read_text(encoding="utf-8"))
    checks["diagnose_rc0"] = rc == 0
    checks["diagnose_report_parses"] = isinstance(report, dict)

    # A2. Cartographer outline compilation over all giant-blueprint chapters,
    # with every planning response scripted through FakeClient (offline).
    compile_project = work / "compile_project"
    blueprint = StoryBlueprint.from_yaml(giant_bp)
    Project.init(compile_project, blueprint)
    scripted = [
        LLMResponse(
            text=chapter_outline_yaml(i), input_tokens=10, output_tokens=20
        )
        for i in range(1, knobs["giant_chapters"] + 1)
    ]
    client = FakeClient(list(scripted))
    unified = compile_project / "cartographer_outline.yaml"
    with Measured("cartographer_compile", sink):
        compile_outline(
            project_path=compile_project,
            blueprint_path=giant_bp,
            output_path=unified,
            split_output=True,
            llm=client,
        )
    unified_data: Any = None
    if unified.exists():
        with contextlib.suppress(yaml.YAMLError, OSError):
            unified_data = yaml.safe_load(unified.read_text(encoding="utf-8"))
    split_outlines = sorted(compile_project.glob("chapters/*/outline.yaml"))
    checks["compile_unified_parses_with_total"] = isinstance(unified_data, dict) and (
        unified_data.get("total_chapters") == knobs["giant_chapters"]
    )
    checks["compile_split_outline_count"] = (
        len(split_outlines) == knobs["giant_chapters"]
    )
    checks["compile_consumed_exactly_scripted"] = len(client.calls) == len(scripted)
    metrics["compile_llm_calls"] = len(client.calls)

    # A3. Large-prose book (accepted chapter expressions) -> publish to HTML.
    book = work / "big_book"
    with Measured("build_book_project", sink):
        build_book_project(book, knobs["book_chapters"], knobs["book_prose_kb"] * 1024)
    html_path = work / "published" / "stress_book.html"
    rc, _ = run_cli_inprocess(
        [
            "publish",
            "--project",
            str(book),
            "--format",
            "html",
            "--output",
            str(html_path),
        ],
        sink,
        "publish_html",
    )
    html_size = html_path.stat().st_size if html_path.exists() else 0
    checks["publish_rc0"] = rc == 0
    checks["publish_html_nonempty"] = html_size > 0
    checks["publish_html_contains_title"] = (
        html_path.exists() and "Stress Harvest" in html_path.read_text(encoding="utf-8")
    )
    metrics["book_chapters"] = knobs["book_chapters"]
    metrics["book_prose_target_bytes"] = knobs["book_prose_kb"] * 1024
    metrics["published_html_bytes"] = html_size

    # A4. `auteur status --json` on the big book and on small extra projects,
    # one of which carries large chapter draft files (draft_v1.md + final.md).
    rc, out = run_cli_inprocess(
        ["status", "--project", str(book), "--json"], sink, "status_big_book"
    )
    checks["status_big_book_rc0"] = rc == 0
    try:
        checks["status_big_book_json_parses"] = isinstance(
            normalize_status_json(out), dict
        )
    except json.JSONDecodeError:
        checks["status_big_book_json_parses"] = False

    draft_project = work / "draft_project"
    Project.init(draft_project, StoryBlueprint.from_yaml(SAMPLE_BLUEPRINT))
    draft_prose = _prose(_BOOK_SENTENCE, knobs["draft_file_kb"] * 1024)
    draft_dir = draft_project / "chapters" / "01"
    draft_dir.mkdir(parents=True, exist_ok=True)
    (draft_dir / "draft_v1.md").write_text(draft_prose, encoding="utf-8")
    (draft_dir / "final.md").write_text(draft_prose, encoding="utf-8")
    metrics["large_draft_file_bytes"] = (draft_dir / "draft_v1.md").stat().st_size
    rc, _ = run_cli_inprocess(
        ["status", "--project", str(draft_project), "--json"],
        sink,
        "status_large_drafts",
    )
    checks["status_large_drafts_rc0"] = rc == 0

    extra_results = []
    for i in range(knobs["extra_projects"]):
        extra = work / f"extra_project_{i:02d}"
        Project.init(extra, StoryBlueprint.from_yaml(SAMPLE_BLUEPRINT))
        rc_i, _ = run_cli_inprocess(
            ["status", "--project", str(extra), "--json"], sink, f"status_extra_{i:02d}"
        )
        extra_results.append(rc_i == 0)
    checks["status_extra_projects_rc0"] = all(extra_results)
    metrics["extra_projects"] = knobs["extra_projects"]

    return {
        "scenario": "A",
        "name": "artifact scale",
        "timings": sink,
        "checks": checks,
        "metrics": metrics,
    }


# ---------------------------------------------------------------------------
# Scenario B - pipeline at scale
# ---------------------------------------------------------------------------


def run_scenario_b(base_dir: Path, scale: str) -> dict[str, Any]:
    """Real PipelineRunner over a multi-chapter book with fully scripted LLM traffic."""
    random.seed(0)
    knobs = spec(scale)
    sink: dict[str, Any] = {}
    checks: dict[str, Any] = {}
    work = base_dir / "scenario_b"
    work.mkdir(parents=True, exist_ok=True)

    chapters = knobs["pipeline_chapters"]
    bard_text = _prose(_BARD_SENTENCE, knobs["pipeline_prose_kb"] * 1024)

    blueprint = StoryBlueprint.from_yaml(SAMPLE_BLUEPRINT)
    project = Project.init(work / "book", blueprint)

    # Fully scripted plan -> draft -> critique loop, per chapter:
    # 1 cartographer response + (1 bard + 5 critic responses) per passing iteration.
    scripted: list[Any] = []
    for k in range(1, chapters + 1):
        scripted.append(
            LLMResponse(
                text=chapter_outline_yaml(k), input_tokens=50, output_tokens=80
            )
        )
        scripted.extend(passing_iteration_responses(bard_text))
    client = FakeClient(list(scripted))
    runner = PipelineRunner(blueprint, bible=project.bible)

    per_chapter: list[dict[str, Any]] = []
    total_in = 0
    total_out = 0
    for k in range(1, chapters + 1):
        with Measured(f"chapter_{k:02d}", sink):
            result = runner.draft_chapter(
                k, llm=client, project=project, max_iterations=3
            )
        total_in += result.total_input_tokens
        total_out += result.total_output_tokens
        per_chapter.append(
            {
                "chapter": k,
                "wall_s": sink[f"chapter_{k:02d}"]["wall_s"],
                "accepted": result.accepted,
                "iterations": result.iterations,
                "input_tokens": result.total_input_tokens,
                "output_tokens": result.total_output_tokens,
            }
        )

    finals = len(list(project.path.glob("chapters/*/final.md")))
    expected_in = sum(
        r.input_tokens for r in scripted if isinstance(r, LLMResponse)
    )
    expected_out = sum(
        r.output_tokens for r in scripted if isinstance(r, LLMResponse)
    )

    checks["all_chapters_accepted"] = all(c["accepted"] for c in per_chapter)
    checks["call_count_matches_script"] = len(client.calls) == len(scripted)
    checks["input_tokens_match_script"] = total_in == expected_in
    checks["output_tokens_match_script"] = total_out == expected_out
    checks["finals_written_for_every_chapter"] = finals == chapters

    return {
        "scenario": "B",
        "name": "pipeline at scale",
        "timings": sink,
        "checks": checks,
        "metrics": {
            "chapters": chapters,
            "bard_prose_target_bytes": knobs["pipeline_prose_kb"] * 1024,
            "scripted_responses": len(scripted),
            "client_calls": len(client.calls),
            "expected_input_tokens": expected_in,
            "expected_output_tokens": expected_out,
            "counted_input_tokens": total_in,
            "counted_output_tokens": total_out,
            "per_chapter": per_chapter,
        },
    }


# ---------------------------------------------------------------------------
# Scenario C - LLM failure simulation
# ---------------------------------------------------------------------------


def run_scenario_c(base_dir: Path, scale: str) -> dict[str, Any]:
    """Transient RetriableError storms retried by RetryingClient (instant backoff).

    RetryingClient accepts a configurable ``base_delay``; the harness sets it to
    0.0 so backoff is instantaneous and deterministic (real sleep cost: 0s).
    """
    random.seed(0)
    sink: dict[str, Any] = {}
    checks: dict[str, Any] = {}
    work = base_dir / "scenario_c"
    work.mkdir(parents=True, exist_ok=True)
    request = LLMRequest(system="", user="", max_tokens=16, temperature=0.0)

    # C1. Unit level: fail N times, then succeed. Retries-to-success == N.
    failures = 2
    success = LLMResponse(text="ok", input_tokens=3, output_tokens=4)
    delegate = FakeClient(
        [RetriableError(f"transient-{i}") for i in range(failures)] + [success]
    )
    client = RetryingClient(delegate, max_retries=3, base_delay=0.0)
    with Measured("retry_unit", sink):
        response = client.complete(request)
    checks["unit_response_ok"] = response.text == "ok"
    checks["unit_attempts_match_script"] = len(delegate.calls) == failures + 1

    # C2. Pipeline level: transient failures hit mid-drafting; the operation
    # must still succeed and leave complete, parseable artifacts behind.
    blueprint = StoryBlueprint.from_yaml(SAMPLE_BLUEPRINT)
    project = Project.init(work / "retry_book", blueprint)
    bard_text = "Kael waited in the tavern while the storm argued with the shutters."
    scripted: list[Any] = [
        LLMResponse(text=chapter_outline_yaml(1), input_tokens=50, output_tokens=80),
        RetriableError("bed-1"),
        RetriableError("bed-2"),
        *passing_iteration_responses(bard_text),
    ]
    delegate = FakeClient(list(scripted))
    runner = PipelineRunner(blueprint, bible=project.bible)
    with Measured("retry_pipeline_draft", sink):
        result = runner.draft_chapter(
            1,
            llm=RetryingClient(delegate, max_retries=3, base_delay=0.0),
            project=project,
            max_iterations=3,
        )
    chapter_dir = project.chapter_dir(1)
    draft = chapter_dir / "draft_v1.md"
    checks["pipeline_accepted"] = result.accepted is True
    checks["pipeline_attempts_match_script"] = len(delegate.calls) == len(scripted)
    checks["draft_intact_not_partial"] = draft.exists() and (
        draft.read_text(encoding="utf-8") == bard_text
    )
    successful = [r for r in scripted if isinstance(r, LLMResponse)]
    checks["pipeline_tokens_match_successful_responses"] = (
        result.total_input_tokens == sum(r.input_tokens for r in successful)
        and result.total_output_tokens == sum(r.output_tokens for r in successful)
    )
    checks["outline_still_parses"] = isinstance(
        yaml.safe_load((chapter_dir / "outline.yaml").read_text(encoding="utf-8")),
        dict,
    )
    checks["validation_still_parses"] = isinstance(
        json.loads((chapter_dir / "validation_v1.json").read_text(encoding="utf-8")),
        dict,
    )

    # C3. Exhaustion: persistent failures raise RetriableError after
    # max_retries and leave no partial artifacts or bible events behind.
    project_exhaust = Project.init(work / "exhaust_book", blueprint)
    exhausted = FakeClient([RetriableError("down")] * 3)
    raised = False
    with Measured("retry_exhaustion", sink):
        try:
            PipelineRunner(blueprint, bible=project_exhaust.bible).draft_chapter(
                1,
                llm=RetryingClient(exhausted, max_retries=2, base_delay=0.0),
                project=project_exhaust,
                max_iterations=3,
            )
        except RetriableError:
            raised = True
    checks["exhaustion_raises_retriable"] = raised
    checks["exhaustion_attempts_match_script"] = len(exhausted.calls) == 3
    checks["exhaustion_leaves_no_artifacts"] = not (
        project_exhaust.chapter_dir(1) / "outline.yaml"
    ).exists() and project_exhaust.bible.data["events"] == []

    total_wall = sum(entry["wall_s"] for entry in sink.values())
    checks["scenario_runtime_under_60s"] = total_wall < 60.0

    return {
        "scenario": "C",
        "name": "LLM failure simulation",
        "timings": sink,
        "checks": checks,
        "metrics": {
            "backoff_base_delay_s": 0.0,
            "real_sleep_cost_s": 0.0,
            "unit_failures_then_success": failures,
            "pipeline_transient_failures": 2,
            "total_wall_s": round(total_wall, 6),
        },
    }


# ---------------------------------------------------------------------------
# Scenario D - concurrency
# ---------------------------------------------------------------------------

# Command choices (documented in stress/README.md):
# - `status --json`   : documented read-only ("never mutates any artifact"),
#                       safe to repeat concurrently against the same project.
# - `structure diagnose <blueprint> --output <unique path>`: deterministic
#                       diagnostics; WITHOUT a unique --output it would write
#                       structure/diagnostics/structure_report.json, so every
#                       concurrent invocation writes to its own exclusive path.
_SCENARIO_D_COMMANDS = ("status --json", "structure diagnose --output")


def _scenario_d_tasks(project: Path, report_dir: Path, tag: str) -> list[dict[str, Any]]:
    return [
        {"kind": "status", "args": ["status", "--project", str(project), "--json"]},
        {
            "kind": "diagnose",
            "args": [
                "structure",
                "diagnose",
                str(project / "blueprint.yaml"),
                "--output",
                str(report_dir / f"{tag}_diagnose.json"),
            ],
        },
    ]


def _run_parallel(tasks: list[dict[str, Any]], workers: int) -> list[dict[str, Any]]:
    if workers < 1:
        workers = 1

    def _one(task: dict[str, Any]) -> dict[str, Any]:
        out = run_cli_subprocess(task["args"])
        return {**task, **{k: out[k] for k in ("rc", "stderr", "timed_out", "wall_s")}}

    with ThreadPoolExecutor(max_workers=workers) as pool:
        return list(pool.map(_one, tasks))


def run_scenario_d(base_dir: Path, scale: str) -> dict[str, Any]:
    """Parallel real CLI subprocesses against one shared and distinct projects."""
    random.seed(0)
    knobs = spec(scale)
    sink: dict[str, Any] = {}
    checks: dict[str, Any] = {}
    metrics: dict[str, Any] = {"commands": list(_SCENARIO_D_COMMANDS)}
    work = base_dir / "scenario_d"
    work.mkdir(parents=True, exist_ok=True)
    report_dir = work / "diagnostics"
    report_dir.mkdir(parents=True, exist_ok=True)

    blueprint = StoryBlueprint.from_yaml(SAMPLE_BLUEPRINT)
    shared = Project.init(work / "shared_project", blueprint)
    # Seed one valid chapter outline so the post-run parse check is non-vacuous.
    shared_outline_dir = shared.path / "chapters" / "01"
    shared_outline_dir.mkdir(parents=True, exist_ok=True)
    (shared_outline_dir / "outline.yaml").write_text(
        chapter_outline_yaml(1), encoding="utf-8"
    )
    distinct: list[Path] = []
    for i in range(knobs["conc_distinct_projects"]):
        path = work / f"distinct_project_{i:02d}"
        Project.init(path, StoryBlueprint.from_yaml(SAMPLE_BLUEPRINT))
        distinct.append(path)

    # Serial control: one pass of every command, then record shared-project state.
    serial_status: dict[str, Any] | None = None
    serial_tasks = _scenario_d_tasks(shared.path, report_dir, "serial")
    for index, task in enumerate(serial_tasks):
        out = run_cli_subprocess(task["args"])
        checks[f"serial_{task['kind']}_rc0"] = out["rc"] == 0
        checks[f"serial_{task['kind']}_no_traceback"] = no_traceback(out["stderr"])
        if task["kind"] == "status":
            try:
                serial_status = normalize_status_json(out["stdout"])
            except json.JSONDecodeError:
                serial_status = None
        if task["kind"] == "diagnose":
            checks["serial_diagnose_report_parses"] = _json_report_parses(
                _diagnose_output_path(task["args"])
            )
        sink[f"serial_task_{index:02d}"] = {"wall_s": out["wall_s"]}
    checks["serial_status_json_parses"] = serial_status is not None

    # Parallel burst 1: several concurrent invocations against the SAME project.
    same_tasks: list[dict[str, Any]] = []
    for w in range(knobs["conc_same_workers"]):
        same_tasks.extend(
            _scenario_d_tasks(shared.path, report_dir, f"same_w{w:02d}")
        )
    with Measured("parallel_same_project", sink):
        same_results = _run_parallel(
            same_tasks, workers=knobs["conc_same_workers"] * 2
        )
    metrics["same_project_tasks"] = len(same_results)
    checks["same_project_all_rc0"] = all(r["rc"] == 0 for r in same_results)
    checks["same_project_no_tracebacks"] = all(
        no_traceback(r["stderr"]) for r in same_results
    )
    checks["same_project_no_timeouts"] = not any(r["timed_out"] for r in same_results)
    checks["same_project_reports_parse"] = all(
        _json_report_parses(_diagnose_output_path(r["args"]))
        for r in same_results
        if r["kind"] == "diagnose"
    )

    # Parallel burst 2: concurrent invocations against distinct projects.
    distinct_tasks: list[dict[str, Any]] = []
    for i, path in enumerate(distinct):
        distinct_tasks.extend(
            _scenario_d_tasks(path, report_dir, f"distinct_p{i:02d}")
        )
    with Measured("parallel_distinct_projects", sink):
        distinct_results = _run_parallel(distinct_tasks, workers=len(distinct_tasks))
    metrics["distinct_project_tasks"] = len(distinct_results)
    checks["distinct_projects_all_rc0"] = all(r["rc"] == 0 for r in distinct_results)
    checks["distinct_projects_no_tracebacks"] = all(
        no_traceback(r["stderr"]) for r in distinct_results
    )
    checks["distinct_projects_no_timeouts"] = not any(
        r["timed_out"] for r in distinct_results
    )

    # Post-parallel integrity: artifacts still parse; state matches serial control.
    integrity = artifact_parse_checks(shared.path)
    checks.update(
        {
            f"post_{k}": v
            for k, v in integrity.items()
            if isinstance(v, bool)
        }
    )
    metrics["post_chapter_outline_count"] = integrity["chapter_outline_count"]
    parallel_status: dict[str, Any] | None = None
    post_status = run_cli_subprocess(
        ["status", "--project", str(shared.path), "--json"]
    )
    checks["post_parallel_status_rc0"] = post_status["rc"] == 0
    try:
        parallel_status = normalize_status_json(post_status["stdout"])
    except json.JSONDecodeError:
        parallel_status = None
    checks["state_consistent_with_serial_control"] = (
        serial_status is not None and serial_status == parallel_status
    )

    return {
        "scenario": "D",
        "name": "concurrency",
        "timings": sink,
        "checks": checks,
        "metrics": metrics,
    }


SCENARIO_RUNNERS = {
    "A": run_scenario_a,
    "B": run_scenario_b,
    "C": run_scenario_c,
    "D": run_scenario_d,
}
