from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from auteur.expression.book import BookExpressionStore
from auteur.publish import PublishError, PublishingSnapshot, publish


def _accepted_book(tmp_path: Path) -> Path:
    project = tmp_path / "project"
    project.mkdir(parents=True)
    from conftest import copy_bootstrap_template

    copy_bootstrap_template(project)
    store = BookExpressionStore(project)
    book = store.compose(["chapter_01", "chapter_02"], title="Recovery Fixture")
    store.accept(book["book_expression_id"])
    return project


def test_authoritative_book_corruption_blocks_publication(tmp_path: Path) -> None:
    project = _accepted_book(tmp_path)
    accepted = project / "book" / "expression" / "accepted.yaml"
    accepted_before = accepted.read_bytes()
    manuscript = project / "book" / "expression" / "book_v001.md"
    manuscript.write_text(
        manuscript.read_text(encoding="utf-8") + "\nUNACCEPTED CORRUPTION\n",
        encoding="utf-8",
    )

    with pytest.raises(PublishError, match="modified after acceptance"):
        PublishingSnapshot(project)

    # Detection must not rewrite the accepted authority pointer/manifest.
    assert accepted.read_bytes() == accepted_before


def test_derived_publishing_records_can_be_rebuilt_without_authority_change(tmp_path: Path) -> None:
    project = _accepted_book(tmp_path)
    accepted = project / "book" / "expression" / "accepted.yaml"
    accepted_before = accepted.read_bytes()

    first = tmp_path / "first.html"
    publish(project, formats=["html"], html_output=first)
    publishing_state = project / ".auteur" / "publishing"
    assert publishing_state.is_dir()

    # Publishing snapshots/run records are derived. Losing them must not require
    # rewriting accepted Book authority; a later publish can recreate them.
    shutil.rmtree(publishing_state)
    second = tmp_path / "second.html"
    publish(project, formats=["html"], html_output=second)

    assert publishing_state.is_dir()
    assert accepted.read_bytes() == accepted_before
    assert first.read_bytes() == second.read_bytes()
