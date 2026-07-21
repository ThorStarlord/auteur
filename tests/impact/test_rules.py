"""Tests for propagation rules and severity combination."""

from __future__ import annotations

from auteur.impact.models import ImpactSeverity
from auteur.impact.rules import highest_severity, match_rule


class TestRuleMatching:
    def test_identity_to_structure(self) -> None:
        results = match_rule("story_identity", "blueprint", "content_changed")
        assert any(r[0] == "R001" for r in results)
        r = [x for x in results if x[0] == "R001"][0]
        assert r[1] == ImpactSeverity.RECONCILE

    def test_outline_to_realization(self) -> None:
        results = match_rule("chapter_outline", "scene_realization", "content_changed")
        assert any(r[0] == "R003" for r in results)
        r = [x for x in results if x[0] == "R003"][0]
        assert r[1] == ImpactSeverity.RECONCILE

    def test_realization_to_expression(self) -> None:
        results = match_rule("scene_realization", "scene_expression", "content_changed")
        assert any(r[0] == "R004" for r in results)
        r = [x for x in results if x[0] == "R004"][0]
        assert r[1] == ImpactSeverity.REGENERATE_CANDIDATE

    def test_expression_to_chapter_expression(self) -> None:
        results = match_rule("scene_expression", "chapter_expression", "content_changed")
        assert any(r[0] == "R005" for r in results)
        r = [x for x in results if x[0] == "R005"][0]
        assert r[1] == ImpactSeverity.REGENERATE_CANDIDATE

    def test_chapter_to_book_expression(self) -> None:
        results = match_rule("chapter_expression", "book_expression", "content_changed")
        assert any(r[0] == "R006" for r in results)
        r = [x for x in results if x[0] == "R006"][0]
        assert r[1] == ImpactSeverity.REGENERATE_CANDIDATE

    def test_book_to_published(self) -> None:
        results = match_rule("book_expression", "published_output", "content_changed")
        assert any(r[0] == "R007" for r in results)
        r = [x for x in results if x[0] == "R007"][0]
        assert r[1] == ImpactSeverity.BLOCKED

    def test_upstream_stales_reasoning(self) -> None:
        results = match_rule("chapter_outline", "reasoning_review", "content_changed")
        assert any(r[0] == "R008" for r in results)
        r = [x for x in results if x[0] == "R008"][0]
        assert r[1] == ImpactSeverity.BLOCKED

    def test_accepted_chapter_to_book_assembly(self) -> None:
        results = match_rule("accepted_chapter", "book_assembly", "content_changed")
        assert any(r[0] == "R009" for r in results)
        r = [x for x in results if x[0] == "R009"][0]
        assert r[1] == ImpactSeverity.REGENERATE_CANDIDATE

    def test_no_match_returns_empty(self) -> None:
        results = match_rule("unknown_type", "other_unknown", "content_changed")
        assert results == []

    def test_adjacent_chapter_continuity(self) -> None:
        results = match_rule("chapter_outline", "chapter_outline", "content_changed")
        assert any(r[0] == "R012" for r in results)
        r = [x for x in results if x[0] == "R012"][0]
        assert r[1] == ImpactSeverity.REVIEW


class TestSeverityCombination:
    def test_highest_severity(self) -> None:
        assert highest_severity([ImpactSeverity.NONE, ImpactSeverity.REVIEW]) == ImpactSeverity.REVIEW
        assert highest_severity([ImpactSeverity.REVIEW, ImpactSeverity.RECONCILE]) == ImpactSeverity.RECONCILE
        assert highest_severity([ImpactSeverity.RECONCILE, ImpactSeverity.REGENERATE_CANDIDATE]) == ImpactSeverity.REGENERATE_CANDIDATE
        assert highest_severity([ImpactSeverity.REGENERATE_CANDIDATE, ImpactSeverity.BLOCKED]) == ImpactSeverity.BLOCKED

    def test_all_none(self) -> None:
        assert highest_severity([ImpactSeverity.NONE, ImpactSeverity.NONE]) == ImpactSeverity.NONE

    def test_single(self) -> None:
        assert highest_severity([ImpactSeverity.BLOCKED]) == ImpactSeverity.BLOCKED
