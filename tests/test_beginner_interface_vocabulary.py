from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_beginner_front_door_uses_plain_story_language() -> None:
    app = _read("src/auteur/beginner/browser/app.js")
    html = _read("src/auteur/beginner/browser/index.html")
    workspace = _read("src/auteur/ui/workspace.py")
    attention = _read("src/auteur/ui/author_attention.py")
    quick_draft = _read("src/auteur/quick_draft.py")
    combined = app + html + workspace + attention + quick_draft

    for jargon in (
        "Will become canonical",
        "May contribute to canon",
        "Will remain context / provenance",
        "<strong>Reconciliation:</strong>",
        "Next owning command:",
        "DERIVED WORKSPACE / READ ONLY",
        "where authority lives",
        "Workspace projection failed:",
        "LOCAL / NONCANONICAL",
        "NONCANONICAL PROPOSAL / NOT APPLIED",
        "explicit authority action",
        "Keep draft & reconcile",
        "structural reconciliation are deferred",
    ):
        assert jargon not in combined

    for plain in (
        "Will become part of the accepted story",
        "May shape the accepted story",
        "Will remain supporting context",
        "<strong>Story updates:</strong>",
        "Next technical action:",
        "READ-ONLY STORY VIEW",
        "which decisions need you",
        "Workspace view failed:",
        "ADVICE ONLY / NOT PART OF STORY YET",
        "SUGGESTED CHANGE / NOT APPLIED",
        "Confirm the change",
        "Keep draft &amp; update story",
        "Story setup decisions and story updates are deferred",
    ):
        assert plain in combined


def test_cli_help_translates_architecture_without_renaming_commands() -> None:
    parser = _read("src/auteur/cli_parser.py")
    expression = _read("src/auteur/expression/cli.py")
    ontology = _read("src/auteur/narrative_ontology/cli_ontology.py")
    universe = _read("src/auteur/universe/cli.py")

    assert "Generate StoryIdentity candidates and an architectural comparison." not in parser
    assert "Generate story-setup options and compare their creative tradeoffs." in parser
    assert "Scene Realization prose candidates." not in expression
    assert "Generate and review scene drafts." in expression
    assert "Inspect and validate narrative ontology." not in ontology
    assert "Inspect and check the story concept library." in ontology
    assert "canonical universe_identity.yaml" not in universe
    assert "accepted universe setup file" in universe

    # Stable command identifiers remain intact.
    assert 'add_parser("ontology"' in ontology
    assert 'add_parser("reconcile"' in expression
    assert 'add_parser("accept-candidate"' in parser


def test_cli_rendered_output_uses_accepted_story_and_change_review_language() -> None:
    handlers = _read("src/auteur/cli_handlers.py")
    formatters = _read("src/auteur/cli_formatters.py")
    expression_formatters = _read("src/auteur/expression/formatters.py")
    convergence = _read("src/auteur/convergence/cli.py")
    roundtrip = _read("src/auteur/roundtrip/cli.py")

    assert "# Canonical Reference Manual" not in handlers
    assert "# Accepted Story Reference" in handlers
    assert "Recovery candidate layers validated and merged into blueprint and bible." not in formatters
    assert "recovered story choices were checked and merged" in formatters
    assert '"Reconciliation application plan"' not in expression_formatters
    assert '"Change application plan"' in expression_formatters
    assert 'print("Reconciliation Proposal:")' not in convergence
    assert 'print("Story Update Proposal:")' in convergence
    assert "No canon update proposals were generated." not in roundtrip
    assert "No accepted-story update suggestions were generated." in roundtrip
