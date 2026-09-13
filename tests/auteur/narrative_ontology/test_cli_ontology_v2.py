"""CLI qualification for the Narrative Ontology V2 registry path."""

import json

from auteur.cli import main


def test_validate_core_includes_modern_semantic_vocabulary(capsys) -> None:
    rc = main(["ontology", "validate"])
    assert rc == 0
    assert "valid" in capsys.readouterr().out.lower()


def test_product_genre_without_extension_inherits_core(capsys) -> None:
    rc = main(["ontology", "inspect", "Event", "--genre", "literary", "--json"])
    assert rc == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["name"] == "Event"


def test_list_for_core_only_genre_includes_modern_vocabulary(capsys) -> None:
    rc = main(["ontology", "list", "--genre", "literary", "--json"])
    assert rc == 0
    concepts = json.loads(capsys.readouterr().out)
    assert "Character" in concepts
    assert "StateTransition" in concepts


def test_validate_core_only_product_genre_succeeds(capsys) -> None:
    rc = main(["ontology", "validate", "literary"])
    assert rc == 0
    assert "valid" in capsys.readouterr().out.lower()


def test_themes_for_core_only_product_genre_are_honest(capsys) -> None:
    rc = main(["ontology", "themes", "literary", "--json"])
    assert rc == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["genre"] == "literary"
    assert payload["themes"] == []
    assert payload["has_ontology_extension"] is False


def test_invalid_genre_remains_rejected(capsys) -> None:
    rc = main(["ontology", "validate", "definitely_not_a_genre"])
    assert rc != 0
    assert "invalid genre" in capsys.readouterr().err.lower()
