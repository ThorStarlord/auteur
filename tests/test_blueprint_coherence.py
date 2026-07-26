"""Tests for Blueprint Coherence reasoning (v0.31.0).

Tests cover:
- Registration and runtime discovery
- Structural coherence (missing engine, incomplete main thread, duplicate types)
- Pacing targets (missing tension curve, missing act tones)
- Thematic depth (missing theme, unlinked engine)
- Character arc completeness (missing arcs, milestone gaps, budget, POV roles)
- Chapter density (estimate, subplot budget, thread density)
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from auteur.reasoning import (
    CriticRegistry,
    ReasoningRuntime,
    RuntimeRequest,
    RuntimeStatus,
)
from auteur.reasoning.blueprint_coherence import (
    register_blueprint_coherence_critic,
    run_blueprint_analysis,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def registry() -> CriticRegistry:
    r = CriticRegistry()
    register_blueprint_coherence_critic(r)
    return r


@pytest.fixture
def empty_blueprint() -> dict:
    return {"identity": {"title": "Test"}, "structure": {}, "characters": [], "theme": None}


@pytest.fixture
def minimal_blueprint() -> dict:
    """A blueprint with the bare minimum to pass most checks."""
    return {
        "identity": {"title": "Test Story", "author_intent": "A thriller"},
        "structure": {"estimated_chapters": 15, "max_characters_total": 10, "subplot_budget": 3},
        "story_engine": {
            "main_thread": {
                "want": {"author_text": "Find the truth"},
                "resistance": {"author_text": "The system"},
                "conflict": {"author_text": "Truth vs safety"},
                "stakes": {"author_text": "Everything"},
                "change": {"author_text": "Grows courage"},
                "thematic_function": "Hero confronts the cost of truth",
            },
            "threads": [
                {"name": "Romance", "type": "romance_subplot",
                 "thematic_function": "Love as a catalyst for change"},
                {"name": "Mystery", "type": "mystery_subplot",
                 "thematic_function": "Past secrets unraveling"},
            ],
        },
        "emotional_design": {
            "overall_emotional_arc": "Rising hope",
            "per_act_tones": [
                {"act_index": 1, "label": "Act 1", "tone": "Curiosity"},
                {"act_index": 2, "label": "Act 2", "tone": "Dread"},
                {"act_index": 3, "label": "Act 3", "tone": "Triumph"},
            ],
        },
        "characters": [
            {"name": "Hero", "role": "protagonist", "arc_type": "growth",
             "arc_start_percentage": 0, "arc_end_percentage": 100,
             "key_milestones": [{"at_percentage": 50, "label": "Midpoint revelation"}]},
            {"name": "Sidekick", "role": "deuteragonist", "arc_type": "healing",
             "arc_start_percentage": 30, "arc_end_percentage": 90,
             "key_milestones": [{"at_percentage": 60, "label": "Opens up"}]},
            {"name": "Mentor", "role": "supporting", "arc_type": "flat",
             "key_milestones": [{"at_percentage": 80, "label": "Final lesson"}]},
        ],
        "tension_waveform": {
            "target_curve": [
                {"chapter_index": 1, "score": 3, "label": "hook"},
                {"chapter_index": 5, "score": 6, "label": "inciting"},
                {"chapter_index": 8, "score": 4, "label": "recovery"},
                {"chapter_index": 12, "score": 8, "label": "climax_build"},
                {"chapter_index": 15, "score": 9, "label": "climax"},
            ],
        },
        "theme": {
            "central_question": "What does truth cost?",
            "thesis": "Truth demands sacrifice but is worth it.",
            "motifs": ["Illusion", "Sacrifice"],
        },
    }


# ---------------------------------------------------------------------------
# Registration tests
# ---------------------------------------------------------------------------


class TestCriticRegistration:
    def test_register_via_registry(self, registry: CriticRegistry) -> None:
        spec = registry.discover(critic_id="blueprint.coherence")
        assert spec.critic_id == "blueprint.coherence"
        assert spec.version == "1.0.0"
        assert spec.input_keys == ("blueprint",)

    def test_register_duplicate_raises(self, registry: CriticRegistry) -> None:
        with pytest.raises(ValueError, match="already registered"):
            register_blueprint_coherence_critic(registry)


# ---------------------------------------------------------------------------
# Runtime integration tests
# ---------------------------------------------------------------------------


class TestRuntimeIntegration:
    def test_runtime_execution(self, registry: CriticRegistry, empty_blueprint: dict, tmp_path: Path) -> None:
        runtime = ReasoningRuntime(registry, tmp_path / "reports")
        result = runtime.run(RuntimeRequest(
            critic_ids=("blueprint.coherence",),
            inputs={"blueprint": empty_blueprint},
        ))
        assert result.outcomes[0].status is RuntimeStatus.SUCCESS
        assert result.outcomes[0].report_id

    def test_runtime_persists_report(self, registry: CriticRegistry, empty_blueprint: dict, tmp_path: Path) -> None:
        runtime = ReasoningRuntime(registry, tmp_path / "reports")
        result = runtime.run(RuntimeRequest(
            critic_ids=("blueprint.coherence",),
            inputs={"blueprint": empty_blueprint},
        ))
        report_path = tmp_path / "reports" / f"{result.outcomes[0].report_id}.json"
        report = json.loads(report_path.read_text())
        assert report["critic_id"] == "blueprint.coherence"
        assert report["status"] == "derived"
        assert "findings" in report
        assert "observations" in report
        assert len(report["findings"]) > 0


# ---------------------------------------------------------------------------
# Structural coherence checks
# ---------------------------------------------------------------------------


class TestStructuralCoherence:
    def test_missing_engine_reports_error(self) -> None:
        bp = {"identity": {"title": "T"}, "structure": {}, "characters": [], "theme": None}
        findings = run_blueprint_analysis(blueprint=bp)
        rules = [f["rule"] for f in findings]
        assert "blueprint.coherence.missing_engine" in rules

    def test_missing_main_thread_reports_error(self) -> None:
        bp = {
            "identity": {"title": "T"},
            "story_engine": {},
            "structure": {},
            "characters": [],
            "theme": None,
        }
        findings = run_blueprint_analysis(blueprint=bp)
        rules = [f["rule"] for f in findings]
        assert "blueprint.coherence.no_main_thread" in rules

    def test_incomplete_main_thread_reports_warning(self) -> None:
        bp = {
            "identity": {"title": "T"},
            "story_engine": {"main_thread": {"want": {"author_text": "X"}}},
            "structure": {},
            "characters": [],
            "theme": None,
        }
        findings = run_blueprint_analysis(blueprint=bp)
        rules = [f["rule"] for f in findings]
        assert "blueprint.coherence.incomplete_main_thread" in rules

    def test_duplicate_thread_types_reports_info(self) -> None:
        bp = {
            "identity": {"title": "T"},
            "story_engine": {
                "main_thread": {
                    "want": {"author_text": "A"},
                    "resistance": {"author_text": "B"},
                    "conflict": {"author_text": "C"},
                    "stakes": {"author_text": "D"},
                    "change": {"author_text": "E"},
                },
                "threads": [
                    {"name": "T1", "type": "romance"},
                    {"name": "T2", "type": "romance"},
                ],
            },
            "structure": {},
            "characters": [],
            "theme": None,
        }
        findings = run_blueprint_analysis(blueprint=bp)
        rules = [f["rule"] for f in findings]
        assert "blueprint.coherence.duplicate_thread_types" in rules

    def test_complete_engine_passes_coherence(self, minimal_blueprint: dict) -> None:
        findings = run_blueprint_analysis(blueprint=minimal_blueprint)
        rules = [f["rule"] for f in findings]
        assert "blueprint.coherence.missing_engine" not in rules
        assert "blueprint.coherence.no_main_thread" not in rules
        assert "blueprint.coherence.incomplete_main_thread" not in rules
        assert "blueprint.coherence.duplicate_thread_types" not in rules


# ---------------------------------------------------------------------------
# Pacing targets checks
# ---------------------------------------------------------------------------


class TestPacingTargets:
    def test_empty_tension_curve_reports_warning(self) -> None:
        bp = {"structure": {}, "characters": [], "theme": None}
        findings = run_blueprint_analysis(blueprint=bp)
        rules = [f["rule"] for f in findings]
        assert "blueprint.coherence.no_tension_curve" in rules

    def test_sparse_tension_curve_reports_info(self) -> None:
        bp = {
            "structure": {"estimated_chapters": 20},
            "tension_waveform": {"target_curve": [{"chapter_index": 1, "score": 3, "label": "hook"}]},
            "characters": [],
            "theme": None,
        }
        findings = run_blueprint_analysis(blueprint=bp)
        rules = [f["rule"] for f in findings]
        assert "blueprint.coherence.sparse_tension_curve" in rules

    def test_no_act_tones_reports_warning(self) -> None:
        bp = {"structure": {}, "characters": [], "theme": None}
        findings = run_blueprint_analysis(blueprint=bp)
        rules = [f["rule"] for f in findings]
        assert "blueprint.coherence.no_act_tones" in rules


# ---------------------------------------------------------------------------
# Thematic depth checks
# ---------------------------------------------------------------------------


class TestThematicDepth:
    def test_missing_theme_reports_error(self) -> None:
        bp = {"structure": {}, "characters": [], "theme": None}
        findings = run_blueprint_analysis(blueprint=bp)
        rules = [f["rule"] for f in findings]
        assert "blueprint.coherence.no_theme" in rules

    def test_empty_central_question_reports_warning(self) -> None:
        bp = {"structure": {}, "characters": [], "theme": {"central_question": "", "thesis": "Something"}}
        findings = run_blueprint_analysis(blueprint=bp)
        rules = [f["rule"] for f in findings]
        assert "blueprint.coherence.empty_central_question" in rules

    def test_main_thread_missing_thematic_function_reports_warning(self) -> None:
        bp = {
            "story_engine": {"main_thread": {"want": {"author_text": "A"},
                                              "resistance": {"author_text": "B"},
                                              "conflict": {"author_text": "C"},
                                              "stakes": {"author_text": "D"},
                                              "change": {"author_text": "E"}}},
            "structure": {},
            "characters": [],
            "theme": {"central_question": "Q?", "thesis": "A."},
        }
        findings = run_blueprint_analysis(blueprint=bp)
        rules = [f["rule"] for f in findings]
        assert "blueprint.coherence.main_thread_no_thematic_function" in rules

    def test_threads_missing_thematic_function_reports_info(self) -> None:
        bp = {
            "story_engine": {
                "main_thread": {
                    "want": {"author_text": "A"}, "resistance": {"author_text": "B"},
                    "conflict": {"author_text": "C"}, "stakes": {"author_text": "D"},
                    "change": {"author_text": "E"}, "thematic_function": "Main arc",
                },
                "threads": [
                    {"name": "T1", "thematic_function": "Has one"},
                    {"name": "T2", "thematic_function": ""},
                    {"name": "T3"},
                ],
            },
            "structure": {},
            "characters": [],
            "theme": {"central_question": "Q?", "thesis": "A."},
        }
        findings = run_blueprint_analysis(blueprint=bp)
        rules = [f["rule"] for f in findings]
        assert "blueprint.coherence.threads_missing_thematic_function" in rules


# ---------------------------------------------------------------------------
# Character arc completeness checks
# ---------------------------------------------------------------------------


class TestCharacterArcCompleteness:
    def test_no_characters_reports_error(self) -> None:
        bp = {"structure": {}, "characters": [], "theme": None}
        findings = run_blueprint_analysis(blueprint=bp)
        rules = [f["rule"] for f in findings]
        assert "blueprint.coherence.no_characters" in rules

    def test_missing_milestones_reports_warning(self) -> None:
        bp = {
            "structure": {},
            "characters": [
                {"name": "Hero", "role": "protagonist", "arc_type": "growth",
                 "arc_start_percentage": 0, "arc_end_percentage": 100},
                {"name": "FlatGuy", "role": "supporting", "arc_type": "flat"},
            ],
            "theme": None,
        }
        findings = run_blueprint_analysis(blueprint=bp)
        rules = [f["rule"] for f in findings]
        assert "blueprint.coherence.characters_without_milestones" in rules

    def test_exceeds_character_budget_reports_warning(self) -> None:
        bp = {
            "structure": {"max_characters_total": 2},
            "characters": [
                {"name": "A", "role": "protagonist", "arc_type": "growth",
                 "arc_start_percentage": 0, "arc_end_percentage": 100},
                {"name": "B", "role": "supporting", "arc_type": "growth",
                 "arc_start_percentage": 0, "arc_end_percentage": 100},
                {"name": "C", "role": "supporting", "arc_type": "growth",
                 "arc_start_percentage": 0, "arc_end_percentage": 100},
            ],
            "theme": None,
        }
        findings = run_blueprint_analysis(blueprint=bp)
        rules = [f["rule"] for f in findings]
        assert "blueprint.coherence.exceeds_character_budget" in rules

    def test_no_pov_character_reports_error(self) -> None:
        bp = {
            "structure": {},
            "characters": [
                {"name": "Minion", "role": "supporting", "arc_type": "flat"},
                {"name": "Villain", "role": "antagonist", "arc_type": "fall",
                 "arc_start_percentage": 0, "arc_end_percentage": 100},
            ],
            "theme": None,
        }
        findings = run_blueprint_analysis(blueprint=bp)
        rules = [f["rule"] for f in findings]
        assert "blueprint.coherence.no_pov_character" in rules


# ---------------------------------------------------------------------------
# Chapter density checks
# ---------------------------------------------------------------------------


class TestChapterDensity:
    def test_no_chapter_estimate_reports_info(self) -> None:
        bp = {"structure": {}, "characters": [], "theme": None}
        findings = run_blueprint_analysis(blueprint=bp)
        rules = [f["rule"] for f in findings]
        assert "blueprint.coherence.no_chapter_estimate" in rules

    def test_threads_exceed_subplot_budget_reports_warning(self) -> None:
        bp = {
            "structure": {"estimated_chapters": 10, "subplot_budget": 1},
            "story_engine": {
                "main_thread": {
                    "want": {"author_text": "A"}, "resistance": {"author_text": "B"},
                    "conflict": {"author_text": "C"}, "stakes": {"author_text": "D"},
                    "change": {"author_text": "E"},
                },
                "threads": [
                    {"name": "T1", "thematic_function": "F1", "type": "romance"},
                    {"name": "T2", "thematic_function": "F2", "type": "mystery"},
                ],
            },
            "characters": [],
            "theme": None,
        }
        findings = run_blueprint_analysis(blueprint=bp)
        rules = [f["rule"] for f in findings]
        assert "blueprint.coherence.threads_exceed_subplot_budget" in rules

    def test_high_thread_density_reports_info(self) -> None:
        bp = {
            "structure": {"estimated_chapters": 5},
            "story_engine": {
                "main_thread": {
                    "want": {"author_text": "A"}, "resistance": {"author_text": "B"},
                    "conflict": {"author_text": "C"}, "stakes": {"author_text": "D"},
                    "change": {"author_text": "E"},
                },
                "threads": [
                    {"name": "T1", "thematic_function": "F1"},
                    {"name": "T2", "thematic_function": "F2"},
                    {"name": "T3", "thematic_function": "F3"},
                ],
            },
            "characters": [],
            "theme": None,
        }
        findings = run_blueprint_analysis(blueprint=bp)
        rules = [f["rule"] for f in findings]
        assert "blueprint.coherence.high_thread_density" in rules


# ---------------------------------------------------------------------------
# Minimal blueprint passes all checks
# ---------------------------------------------------------------------------


class TestMinimalBlueprint:
    def test_minimal_blueprint_has_no_findings(self, minimal_blueprint: dict) -> None:
        findings = run_blueprint_analysis(blueprint=minimal_blueprint)
        assert len(findings) == 0, f"Expected no findings, got: {[f['rule'] for f in findings]}"
