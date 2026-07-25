"""Tests for Scene realization reasoning critic (v0.31.0)."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml


# =========================================================================
# Fixtures
# =========================================================================


@pytest.fixture
def project_root(tmp_path: Path) -> Path:
    root = tmp_path / "project"
    root.mkdir(parents=True, exist_ok=True)
    (root / ".auteur").mkdir(parents=True, exist_ok=True)
    return root


def _write_scene(scenes_dir: Path, scene_id: str, chapter_id: str, data: dict) -> None:
    """Helper to write a scene YAML file to the scenes directory."""
    scenes_dir.mkdir(parents=True, exist_ok=True)
    (scenes_dir / f"{scene_id}.yaml").write_text(yaml.safe_dump(data), encoding="utf-8")


@pytest.fixture
def with_complete_scenes(project_root: Path) -> Path:
    """Project with fully valid scenes."""
    genre_dir = project_root / ".auteur" / "scenes" / "netorare"
    _write_scene(genre_dir, "scene_01_01", "chapter_01", {
        "id": "scene_01_01",
        "chapter_id": "chapter_01",
        "status": "ready",
        "narrative_position": 1,
        "story_time": "day_1_morning",
        "pov_character_id": "hero",
        "participants": ["hero", "villain"],
        "goal": {"actor_id": "hero", "objective": "Retrieve the map"},
        "opposition": {"source_id": "villain", "pressure": "Demands tribute"},
        "turn": {"type": "revelation", "event": "Map is a forgery", "impact": "Hero realises betrayal"},
        "decision": {"actor_id": "hero", "choice": "Pretend to cooperate"},
        "outcome": {"result": "partial", "knowledge_added": ["villain's motive"], "consequences": ["must find real map"]},
        "entry_state": {"knowledge": [], "emotional": {"hope": "moderate"}},
        "exit_state": {"knowledge": [{"what": "villain betrayal", "how_known": "learned", "degree": "certain", "source": "inference"}], "emotional": {"determination": "high"}},
        "realizes_arc_beats": [{"beat_id": "beat_intro", "degree": "full"}],
        "setups_created": ["forgery_plot"],
        "tags": ["revelation", "tension"],
    })
    _write_scene(genre_dir, "scene_01_02", "chapter_01", {
        "id": "scene_01_02",
        "chapter_id": "chapter_01",
        "status": "incomplete",
        "narrative_position": 2,
        "pov_character_id": "hero",
        "participants": ["hero"],
        "goal": {"actor_id": "hero", "objective": "Find the real map"},
        "opposition": {"source_id": "external", "pressure": "Guard patrols"},
        "outcome": {"result": "failure"},
        "tags": ["conflict"],
    })
    return project_root


@pytest.fixture
def with_problematic_scenes(project_root: Path) -> Path:
    """Project with scenes that have known issues."""
    genre_dir = project_root / ".auteur" / "scenes" / "mystery"
    # Scene with POV not in participants
    _write_scene(genre_dir, "scene_02_01", "chapter_02", {
        "id": "scene_02_01",
        "chapter_id": "chapter_02",
        "status": "incomplete",
        "narrative_position": 1,
        "pov_character_id": "detective",
        "participants": ["suspect", "witness"],
        "goal": {"actor_id": "detective", "objective": "Question the witness"},
        "opposition": {"source_id": "suspect", "pressure": "Interrupts interrogation"},
        "outcome": {"result": "partial"},
    })
    # Scene missing narrative_position
    _write_scene(genre_dir, "scene_02_02", "chapter_02", {
        "id": "scene_02_02",
        "chapter_id": "chapter_02",
        "status": "ready",
        "pov_character_id": "detective",
        "participants": ["detective"],
        "goal": {"actor_id": "detective", "objective": "Analyse clues"},
        "opposition": {"source_id": "external", "pressure": "Time pressure"},
        "outcome": {"result": "success"},
    })
    return project_root


# =========================================================================
# Scene analysis unit tests
# =========================================================================


class TestAnalyzerNoScenes:

    def test_empty_project_path(self, project_root):
        from auteur.reasoning.scene import run_scene_analysis
        findings = run_scene_analysis(project=project_root)
        assert len(findings) == 1
        assert findings[0]["rule"] == "scene.completeness.no_scenes"

    def test_nonexistent_project(self, tmp_path):
        from auteur.reasoning.scene import run_scene_analysis
        missing = tmp_path / "nonexistent"
        findings = run_scene_analysis(project=missing)
        assert len(findings) == 1
        assert "no_scenes" in findings[0]["rule"]


class TestAnalyzerWithScenes:

    def test_complete_scenes_no_findings(self, with_complete_scenes):
        from auteur.reasoning.scene import run_scene_analysis
        findings = run_scene_analysis(project=with_complete_scenes)
        # Both scenes are valid: no missing fields, POV in participants, enough tension
        assert len(findings) == 0

    def test_problematic_scenes_findings(self, with_problematic_scenes):
        from auteur.reasoning.scene import run_scene_analysis
        findings = run_scene_analysis(project=with_problematic_scenes)
        rules = {f["rule"] for f in findings}
        # scene_02_01: POV not in participants
        assert "scene.character.pov_not_in_participants" in rules
        # scene_02_02: ready status but missing narrative_position and entry_state/exit_state/turn/decision
        assert "scene.completeness.missing_fields" in rules

    def test_completeness_draft_skips_checks(self, project_root):
        """Draft scenes only need id and chapter_id."""
        from auteur.reasoning.scene import run_scene_analysis
        genre_dir = project_root / ".auteur" / "scenes" / "test_genre"
        _write_scene(genre_dir, "scene_99_01", "chapter_99", {
            "id": "scene_99_01",
            "chapter_id": "chapter_99",
            "status": "draft",
        })
        findings = run_scene_analysis(project=project_root)
        # Only a tension marker finding (draft scenes skip completeness and character checks)
        assert len(findings) == 0

    def test_incomplete_scene_needs_core_fields(self, project_root):
        """incomplete status requires specific fields."""
        from auteur.reasoning.scene import run_scene_analysis
        genre_dir = project_root / ".auteur" / "scenes" / "test_genre"
        _write_scene(genre_dir, "scene_03_01", "chapter_03", {
            "id": "scene_03_01",
            "chapter_id": "chapter_03",
            "status": "incomplete",
        })
        findings = run_scene_analysis(project=project_root)
        missing_rules = [f for f in findings if f["rule"] == "scene.completeness.missing_fields"]
        assert len(missing_rules) == 1
        missing = missing_rules[0]["evidence"]["missing_fields"]
        assert "narrative_position" in missing
        assert "pov_character_id" in missing
        assert "participants" in missing

    def test_ready_scene_needs_all_fields(self, project_root):
        """ready status requires entry_state, exit_state, turn, decision."""
        from auteur.reasoning.scene import run_scene_analysis
        genre_dir = project_root / ".auteur" / "scenes" / "test_genre"
        _write_scene(genre_dir, "scene_04_01", "chapter_04", {
            "id": "scene_04_01",
            "chapter_id": "chapter_04",
            "status": "ready",
            "narrative_position": 1,
            "pov_character_id": "hero",
            "participants": ["hero"],
            "goal": {"actor_id": "hero", "objective": "Win"},
            "opposition": {"source_id": "villain", "pressure": "Fights back"},
            "outcome": {"result": "success"},
        })
        findings = run_scene_analysis(project=project_root)
        missing_rules = [f for f in findings if f["rule"] == "scene.completeness.missing_fields"]
        assert len(missing_rules) >= 1
        missing = missing_rules[0]["evidence"]["missing_fields"]
        assert "entry_state" in missing
        assert "exit_state" in missing
        assert "turn" in missing
        assert "decision" in missing

    def test_tension_low_signals(self, project_root):
        """Scene with fewer than 2 tension signals gets a warning."""
        from auteur.reasoning.scene import run_scene_analysis
        genre_dir = project_root / ".auteur" / "scenes" / "test_genre"
        _write_scene(genre_dir, "scene_05_01", "chapter_05", {
            "id": "scene_05_01",
            "chapter_id": "chapter_05",
            "status": "incomplete",
            "narrative_position": 1,
            "pov_character_id": "hero",
            "participants": ["hero"],
            "goal": {"actor_id": "hero", "objective": "Stand still"},
            "opposition": {"source_id": "external", "pressure": "None"},
            "outcome": {"result": "success"},
        })
        findings = run_scene_analysis(project=project_root)
        tension_rules = [f for f in findings if f["rule"] == "scene.tension.low_tension_signals"]
        assert len(tension_rules) == 1


# =========================================================================
# Critic registration tests
# =========================================================================


class TestCriticRegistration:

    def test_register(self):
        from auteur.reasoning import CriticRegistry, register_scene_critic
        registry = CriticRegistry()
        register_scene_critic(registry)

    def test_registered_spec(self):
        from auteur.reasoning import CriticRegistry, CriticSpec, register_scene_critic
        registry = CriticRegistry()
        register_scene_critic(registry)
        spec = registry.discover(critic_id="scene.analysis")
        assert isinstance(spec, CriticSpec)
        assert spec.critic_id == "scene.analysis"
        assert spec.version == "1.0.0"
        assert "project" in spec.input_keys

    def test_register_via_builtins(self):
        from auteur.reasoning import CriticRegistry
        from auteur.reasoning.registrar import register_all_builtins
        registry = CriticRegistry()
        register_all_builtins(registry)
        spec = registry.discover(critic_id="scene.analysis")
        assert spec.critic_id == "scene.analysis"

    def test_no_duplicate_registration(self):
        from auteur.reasoning import CriticRegistry, register_scene_critic
        registry = CriticRegistry()
        register_scene_critic(registry)
        import pytest
        with pytest.raises(ValueError, match="already registered"):
            register_scene_critic(registry)


# =========================================================================
# Runtime integration tests
# =========================================================================


class TestRuntimeIntegration:

    def test_runtime_execution(self, with_complete_scenes):
        from auteur.reasoning import (
            CriticRegistry,
            ReasoningRuntime,
            RuntimeRequest,
            RuntimeStatus,
            register_scene_critic,
        )
        registry = CriticRegistry()
        register_scene_critic(registry)
        runtime = ReasoningRuntime(registry, with_complete_scenes / "reports")
        result = runtime.run(RuntimeRequest(
            critic_ids=("scene.analysis",),
            inputs={"project": str(with_complete_scenes)},
        ))
        assert result.outcomes[0].status is RuntimeStatus.SUCCESS

    def test_runtime_with_problems(self, with_problematic_scenes):
        from auteur.reasoning import (
            CriticRegistry,
            ReasoningRuntime,
            RuntimeRequest,
            register_scene_critic,
        )
        registry = CriticRegistry()
        register_scene_critic(registry)
        runtime = ReasoningRuntime(registry, with_problematic_scenes / "reports")
        result = runtime.run(RuntimeRequest(
            critic_ids=("scene.analysis",),
            inputs={"project": str(with_problematic_scenes)},
        ))
        assert len(result.outcomes) == 1
        outcome = result.outcomes[0]
        assert outcome.status.name == "SUCCESS"
        import json
        report = json.loads((with_problematic_scenes / "reports" / f"{outcome.report_id}.json").read_text())
        rules = {f["rule"] for f in report.get("observations", [])}
        assert "scene.character.pov_not_in_participants" in rules
