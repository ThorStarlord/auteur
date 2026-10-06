"""Projection adapter tests; publication/status owners are explicit test doubles.

These tests do not claim a full publishing or HTTP integration run.
"""
import importlib.util
from pathlib import Path
import sys
from types import ModuleType

import pytest


@pytest.fixture
def adapter(monkeypatch):
    publish = ModuleType("auteur.publish")
    status = ModuleType("auteur.status")

    class PublishError(Exception):
        pass

    def unavailable(root):
        raise PublishError("Book not yet accepted")

    publish.PublishError = PublishError
    publish.PublishingSnapshot = unavailable
    status.gather_status = lambda root: {
        "chapters": [{"expression": "working"}],
        "blueprint": {}, "book": {}, "reconciliation": {},
    }
    monkeypatch.setitem(sys.modules, "auteur.publish", publish)
    monkeypatch.setitem(sys.modules, "auteur.status", status)
    path = Path(__file__).resolve().parents[1] / "src/auteur/beginner/book_progress.py"
    spec = importlib.util.spec_from_file_location("book_progress_contract", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_existing_projection_exposes_orientation_without_new_authority(adapter, tmp_path):
    path = tmp_path / "chapters/01"
    path.mkdir(parents=True)
    (path / "final.md").write_text("Kept history")
    result = adapter.project_book_progress(tmp_path)
    assert result.current_chapter == 2
    assert result.next_story_action == "Write Chapter 2"
    assert result.accepted_chapters == 1
    assert result.authority_status == "DERIVED / NOT CANON"
    assert result.publication_ready is False
    assert result.publication_blocker == "Book not yet accepted"
    assert result.next_command is None


def test_legacy_model_constructors_keep_working(adapter):
    result = adapter.BookProgressProjection(
        planned_chapters=0, discovered_chapters=0, accepted_chapters=0,
        book_expression="missing", reconciliation_status="not_started", publication_ready=False,
    )
    assert result.current_chapter == 1
    assert result.pending_updates == ()


def test_explicit_plan_completion_is_different_from_discovered_count(adapter, tmp_path):
    path = tmp_path / "chapters/01"
    path.mkdir(parents=True)
    (path / "final.md").write_text("Kept history")
    adapter.gather_status = lambda root: {"chapters": [], "blueprint": {"chapters": 1}}
    assert adapter.project_book_progress(tmp_path).next_story_action == "Review your Book"


def test_preflight_cannot_mistake_backend_fields_for_browser_integration(adapter, tmp_path):
    import ast

    source = Path(__file__).resolve().parents[1] / "scripts/f2_x3_agent_simulation_probe.py"
    function = next(node for node in ast.parse(source.read_text()).body
                    if isinstance(node, ast.FunctionDef) and node.name == "_x3_book_orientation_probe")
    browser = tmp_path / "src/auteur/beginner/browser"
    browser.mkdir(parents=True)
    (browser / "index.html").write_text("Advanced: whole-book details")
    (browser / "app.js").write_text("function currentChapterFromQuery() {}")
    namespace = {"ROOT": tmp_path, "BookProgressProjection": adapter.BookProgressProjection, "Any": object}
    exec(compile(ast.Module(body=[function], type_ignores=[]), str(source), "exec"), namespace)
    result = namespace["_x3_book_orientation_probe"]()
    assert result["missing_persistent_orientation_fields"] == []
    assert result["author_orientation_surface_present"] is False
    assert result["mechanical_x3_gap"] is True
