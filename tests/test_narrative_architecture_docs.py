from pathlib import Path


ROOT = Path(__file__).parents[1]
CANONICAL_DOCS = (
    ROOT / "CONTEXT.md",
    ROOT / "README.md",
    ROOT / "docs" / "architecture.md",
    ROOT / "docs" / "artifacts.md",
    ROOT / "AGENTS.md",
)


def test_canonical_documentation_links_to_the_source_of_truth() -> None:
    canonical = (ROOT / "docs" / "narrative-architecture.md").read_text(encoding="utf-8")
    assert "Ontology" in canonical
    assert "Identity" in canonical
    assert "Structure" in canonical
    assert "Realization" in canonical
    assert "Expression" in canonical
    assert "There is no permanent Layer 2.5." in canonical


def test_active_architecture_documents_do_not_restore_obsolete_layer_models() -> None:
    forbidden = ("7-layer", "seven-layer", "9-layer", "nine-layer", "Layer 2.5")
    for path in CANONICAL_DOCS:
        text = path.read_text(encoding="utf-8").lower()
        for phrase in forbidden:
            assert phrase.lower() not in text, f"{phrase!r} found in {path}"


def test_artifact_document_treats_scopes_as_scopes() -> None:
    text = (ROOT / "docs" / "artifacts.md").read_text(encoding="utf-8")
    assert "Universe, Series, Book,\nChapter, and Scene are scopes, not layers." in text
    assert "### Expression: Draft" in text
    assert "### Cross-cutting Editing" in text
