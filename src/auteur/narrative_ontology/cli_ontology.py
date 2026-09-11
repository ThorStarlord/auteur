"""CLI commands for inspecting and validating Narrative Ontology V2."""

from __future__ import annotations

import json
import sys

from auteur.narrative_ontology.registry import OntologyRegistry


def register_ontology_subcommands(sub) -> None:
    """Register ontology subcommands with the root CLI parser."""

    parser = sub.add_parser("ontology", help="Inspect and validate narrative ontology.")
    commands = parser.add_subparsers(dest="ontology_command", required=True)

    inspect_cmd = commands.add_parser(
        "inspect", help="Show concept definition, relationships, and validation rules."
    )
    inspect_cmd.add_argument("concept", type=str, help="Concept name to inspect")
    inspect_cmd.add_argument(
        "--genre",
        type=str,
        default=None,
        help="Optional product-genre context; genres without extensions inherit core ontology",
    )
    inspect_cmd.add_argument("--json", action="store_true", help="Output as JSON")

    list_cmd = commands.add_parser("list", help="List all ontology concepts")
    list_cmd.add_argument(
        "--genre",
        type=str,
        default=None,
        help="Optional product-genre context",
    )
    list_cmd.add_argument("--json", action="store_true", help="Output as JSON")

    validate_cmd = commands.add_parser(
        "validate", help="Validate canonical ontology specification integrity"
    )
    validate_cmd.add_argument(
        "genre",
        nargs="?",
        default=None,
        help="Optional product genre / packaged extension to validate",
    )

    themes_cmd = commands.add_parser(
        "themes", help="Show ontology theme metadata for a product genre"
    )
    themes_cmd.add_argument("genre", type=str, help="Genre to show themes for")
    themes_cmd.add_argument("--json", action="store_true", help="Output as JSON")


def _valid_genre_or_error(registry: OntologyRegistry, genre: str | None) -> bool:
    if genre is None:
        return True
    if registry.is_supported_genre(genre):
        return True
    known = sorted(
        set(registry.available_genre_extensions)
        | _known_product_genres()
    )
    suffix = f" Known genres: {', '.join(known)}" if known else ""
    print(f"Error: Invalid genre '{genre}'.{suffix}", file=sys.stderr)
    return False


def _known_product_genres() -> set[str]:
    try:
        from auteur.blueprint import Genre

        return {genre.value for genre in Genre}
    except (ImportError, AttributeError):
        return set()


def handle_ontology_inspect(args) -> int:
    """Handle ``auteur ontology inspect``."""

    try:
        registry = OntologyRegistry()
        if not _valid_genre_or_error(registry, args.genre):
            return 1
        concept = registry.get_concept(args.concept, args.genre)
        if concept is None:
            print(f"Error: Unknown concept '{args.concept}'", file=sys.stderr)
            return 1
        concept_data = concept.model_dump(mode="json")
        if args.json:
            print(json.dumps(concept_data, indent=2))
        else:
            _print_concept_formatted(concept_data)
        return 0
    except Exception as exc:
        print(f"Error: Failed to inspect concept: {exc}", file=sys.stderr)
        return 1


def handle_ontology_list(args) -> int:
    """Handle ``auteur ontology list``."""

    try:
        registry = OntologyRegistry()
        if not _valid_genre_or_error(registry, args.genre):
            return 1
        concept_names = sorted(registry.get_all_concepts(args.genre))
        if args.json:
            print(json.dumps(concept_names, indent=2))
        else:
            for name in concept_names:
                print(name)
        return 0
    except Exception as exc:
        print(f"Error: Failed to list concepts: {exc}", file=sys.stderr)
        return 1


def handle_ontology_validate(args) -> int:
    """Handle ``auteur ontology validate`` using canonical V2 integrity rules."""

    try:
        registry = OntologyRegistry()
        if not _valid_genre_or_error(registry, args.genre):
            return 1

        errors = registry.validate_integrity(args.genre)
        label = "Core ontology" if args.genre is None else f"{args.genre} ontology"
        if errors:
            print(f"{label} validation FAILED:", file=sys.stderr)
            for error in errors:
                print(f"  - {error}", file=sys.stderr)
            return 1

        print(f"{label} is valid")
        return 0
    except Exception as exc:
        print(f"Error: Failed to validate ontology: {exc}", file=sys.stderr)
        return 1


def handle_ontology_themes(args) -> int:
    """Handle ``auteur ontology themes``.

    Theme metadata is descriptive/advisory. It is not a hard validity contract.
    """

    try:
        registry = OntologyRegistry()
        if not _valid_genre_or_error(registry, args.genre):
            return 1

        normalized = args.genre.strip().lower()
        concepts = registry.get_genre_extension(normalized)
        concept_themes: dict[str, object] = {}
        for concept_name, concept in concepts.items():
            themes = concept.metadata.get("themes")
            if themes:
                concept_themes[concept_name] = themes

        themes_data = {
            "genre": normalized,
            "themes": sorted(registry.get_genre_themes(normalized)),
            "concept_themes": concept_themes,
            "has_ontology_extension": normalized in registry.available_genre_extensions,
        }

        if args.json:
            print(json.dumps(themes_data, indent=2))
            return 0

        print(f"Theme set for {normalized.upper()}")
        print("=" * 50)
        if themes_data["themes"]:
            for theme in themes_data["themes"]:
                print(f"  - {theme}")
        elif themes_data["has_ontology_extension"]:
            print("No explicit shared theme metadata is registered for this extension.")
        else:
            print("No ontology extension is required; this genre inherits core ontology.")

        if concept_themes:
            print("\nThemes by concept:")
            for concept_name, themes in sorted(concept_themes.items()):
                print(f"  {concept_name}: {themes}")
        return 0
    except Exception as exc:
        print(f"Error: Failed to get themes: {exc}", file=sys.stderr)
        return 1


def _print_concept_formatted(concept_data: dict) -> None:
    """Pretty-print a typed concept dump."""

    print(f"\nConcept: {concept_data['name']}")
    print("=" * 60)
    print("\nDefinition:")
    print(f"  {concept_data['definition']}")

    if concept_data.get("category"):
        print(f"\nCategory: {concept_data['category']}")

    if concept_data.get("parent_concepts"):
        print("\nParent Concepts:")
        for parent in concept_data["parent_concepts"]:
            print(f"  - {parent}")

    if concept_data.get("aliases"):
        print("\nAliases:")
        for alias in concept_data["aliases"]:
            print(f"  - {alias}")

    if concept_data.get("relationships"):
        print("\nRelationships:")
        for relation in concept_data["relationships"]:
            source = relation.get("source_concept", "")
            target = relation.get("target_concept", "")
            relation_type = relation.get("relation_type")
            cardinality = relation.get("cardinality", "")
            description = relation.get("description", "")
            print(f"  - {source} -> {target}")
            if relation_type:
                print(f"    Relation type: {relation_type}")
            if cardinality:
                print(f"    Cardinality: {cardinality}")
            if description:
                print(f"    Description: {description}")

    if concept_data.get("validation_rules"):
        print("\nValidation Rules:")
        for rule in concept_data["validation_rules"]:
            print(f"  - {rule.get('rule_id', '')}")
            if rule.get("kind"):
                print(f"    Kind: {rule['kind']}")
            if rule.get("executor"):
                print(f"    Executor: {rule['executor']}")
            if rule.get("condition"):
                print(f"    Condition (documentation): {rule['condition']}")
            if rule.get("error_message"):
                print(f"    Diagnostic: {rule['error_message']}")

    if concept_data.get("metadata"):
        print("\nMetadata:")
        for key, value in concept_data["metadata"].items():
            if isinstance(value, (list, dict)):
                print(f"  {key}: {json.dumps(value, indent=4)}")
            else:
                print(f"  {key}: {value}")

    print()
