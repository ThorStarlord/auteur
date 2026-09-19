from __future__ import annotations

from auteur.beginner.application import BeginnerWorkspaceApplication
from auteur.beginner.architecture_analysis import premise_fingerprint
from tests.fixtures.beginner_hybrid_mystery import (
    CountingArchitectureAnalyzer,
    HYBRID_ANALYSIS,
    HYBRID_MYSTERY_PREMISE,
)


def test_create_workspace_persists_analysis_and_get_never_regenerates(tmp_path) -> None:
    analyzer = CountingArchitectureAnalyzer(HYBRID_ANALYSIS)
    app = BeginnerWorkspaceApplication(
        tmp_path,
        "analysis-workspace",
        architecture_analyzer=analyzer,
    )
    created = app.create_workspace(
        command_id="create-analysis-workspace",
        project_id="project",
        premise=HYBRID_MYSTERY_PREMISE,
        guidance_genre="mystery",
    )
    assert created.architecture_analysis is not None
    assert created.architecture_analysis.premise_fingerprint == premise_fingerprint(HYBRID_MYSTERY_PREMISE)
    assert analyzer.calls == 1

    reopened = BeginnerWorkspaceApplication(
        tmp_path,
        "analysis-workspace",
        architecture_analyzer=analyzer,
    )
    reopened.projection()
    assert analyzer.calls == 1


def test_analysis_currentness_is_derived_without_get_mutation(tmp_path) -> None:
    analyzer = CountingArchitectureAnalyzer(HYBRID_ANALYSIS)
    app = BeginnerWorkspaceApplication(
        tmp_path,
        "analysis-currentness",
        architecture_analyzer=analyzer,
    )
    created = app.create_workspace(
        command_id="create-analysis-currentness",
        project_id="project",
        premise=HYBRID_MYSTERY_PREMISE,
        guidance_genre="mystery",
    )
    assert app._analysis_is_current(created) is True

    stale = created.model_copy(
        update={
            "architecture_analysis": created.architecture_analysis.model_copy(
                update={"premise_fingerprint": "wrong"}
            )
        }
    )
    projected = app._architecture_analysis(stale)
    assert projected is not None
    assert projected.stale is True
    assert app.session_store.load().architecture_analysis.stale is False


def test_legacy_session_without_analysis_remains_projectable(tmp_path) -> None:
    app = BeginnerWorkspaceApplication(tmp_path, "legacy-analysis")
    from auteur.beginner.contracts import SessionEnvelope

    legacy = SessionEnvelope.new(
        project_id="project",
        guidance_genre="mystery",
        premise="A detective investigates a mystery.",
    )
    legacy = legacy.model_copy(update={"working_composition": app._initial_composition(legacy)})
    app.session_store.create(legacy)

    projection = app.projection()
    assert projection.session_version == 1
    assert app.session_store.load().architecture_analysis is None
