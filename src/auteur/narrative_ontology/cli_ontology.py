"""CLI commands for inspecting and validating narrative ontology.

Layer 0 Task 7: Implements CLI commands to expose ontology inspection and validation:
- auteur ontology inspect <concept> [--genre GENRE] [--json]
- auteur ontology list [--genre GENRE] [--json]
- auteur ontology validate [GENRE]
- auteur ontology themes <genre> [--json]
"""

import json
import sys
from typing import Optional
from pathlib import Path

from auteur.narrative_ontology.loader.ontology_loader import OntologyLoader


def register_ontology_subcommands(sub) -> None:
    """Register ontology subcommands with the CLI parser.

    Args:
        sub: The subparsers object from argparse
    """
    parser = sub.add_parser("ontology", help="Inspect and validate narrative ontology.")
    commands = parser.add_subparsers(dest="ontology_command", required=True)

    # inspect command
    inspect_cmd = commands.add_parser(
        "inspect",
        help="Show concept definition, relationships, and validation rules."
    )
    inspect_cmd.add_argument("concept", type=str, help="Concept name to inspect")
    inspect_cmd.add_argument(
        "--genre",
        type=str,
        default=None,
        help="Optional genre filter (netorare, mystery, gentlefemdom)"
    )
    inspect_cmd.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON"
    )

    # list command
    list_cmd = commands.add_parser(
        "list",
        help="List all concepts in ontology"
    )
    list_cmd.add_argument(
        "--genre",
        type=str,
        default=None,
        help="Optional genre filter (netorare, mystery, gentlefemdom)"
    )
    list_cmd.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON"
    )

    # validate command
    validate_cmd = commands.add_parser(
        "validate",
        help="Validate ontology structure and relationships"
    )
    validate_cmd.add_argument(
        "genre",
        nargs="?",
        default=None,
        help="Optional genre to validate (netorare, mystery, gentlefemdom)"
    )

    # themes command
    themes_cmd = commands.add_parser(
        "themes",
        help="Show theme set for a genre"
    )
    themes_cmd.add_argument(
        "genre",
        type=str,
        help="Genre to show themes for"
    )
    themes_cmd.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON"
    )


def handle_ontology_inspect(args) -> int:
    """Handle 'ontology inspect' command.

    Args:
        args: Parsed command arguments

    Returns:
        Exit code (0 for success, 1 for error)
    """
    try:
        loader = OntologyLoader()
        concept_data = loader.get_concept(args.concept, genre=args.genre)

        if args.json:
            print(json.dumps(concept_data, indent=2))
        else:
            _print_concept_formatted(concept_data)

        return 0
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"Error: Failed to inspect concept: {exc}", file=sys.stderr)
        return 1


def handle_ontology_list(args) -> int:
    """Handle 'ontology list' command.

    Args:
        args: Parsed command arguments

    Returns:
        Exit code (0 for success, 1 for error)
    """
    try:
        loader = OntologyLoader()
        concept_names = loader.get_concept_names(genre=args.genre)

        if args.json:
            print(json.dumps(concept_names, indent=2))
        else:
            for name in concept_names:
                print(name)

        return 0
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"Error: Failed to list concepts: {exc}", file=sys.stderr)
        return 1


def handle_ontology_validate(args) -> int:
    """Handle 'ontology validate' command.

    Args:
        args: Parsed command arguments

    Returns:
        Exit code (0 for success, 1 for error)
    """
    try:
        loader = OntologyLoader()

        if args.genre is None:
            # Validate base ontology
            base = loader.load_base_ontology()
            errors = loader.validate_ontology_structure(base)

            if errors:
                print("Base ontology validation FAILED:", file=sys.stderr)
                for error in errors:
                    print(f"  - {error}", file=sys.stderr)
                return 1
            else:
                print("Base ontology is valid")
                return 0
        else:
            # Validate specific genre
            valid_genres = {"netorare", "mystery", "gentlefemdom"}
            if args.genre not in valid_genres:
                print(
                    f"Error: Invalid genre '{args.genre}'. "
                    f"Must be one of: {', '.join(sorted(valid_genres))}",
                    file=sys.stderr
                )
                return 1

            base = loader.load_base_ontology()
            genre_ont = loader.load_genre_ontology(args.genre)
            merged = loader.merge_ontologies(base, genre_ont)
            errors = loader.validate_ontology_structure(merged)

            if errors:
                print(
                    f"{args.genre.capitalize()} ontology validation FAILED:",
                    file=sys.stderr
                )
                for error in errors:
                    print(f"  - {error}", file=sys.stderr)
                return 1
            else:
                print(f"{args.genre.capitalize()} ontology is valid")
                return 0

    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    except FileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"Error: Failed to validate ontology: {exc}", file=sys.stderr)
        return 1


def handle_ontology_themes(args) -> int:
    """Handle 'ontology themes' command.

    Args:
        args: Parsed command arguments

    Returns:
        Exit code (0 for success, 1 for error)
    """
    try:
        valid_genres = {"netorare", "mystery", "gentlefemdom"}
        if args.genre not in valid_genres:
            print(
                f"Error: Invalid genre '{args.genre}'. "
                f"Must be one of: {', '.join(sorted(valid_genres))}",
                file=sys.stderr
            )
            return 1

        loader = OntologyLoader()

        # Load genre ontology to extract themes from metadata
        genre_ont = loader.load_genre_ontology(args.genre)

        # Collect themes from all concepts' metadata
        themes_data = {
            "genre": args.genre,
            "themes": {},
            "concept_themes": {}
        }

        for concept_name, concept in genre_ont.items():
            metadata = concept.get("metadata", {})
            if "themes" in metadata:
                themes_data["concept_themes"][concept_name] = metadata["themes"]

        # Also check base ontology for genre-agnostic themes
        base = loader.load_base_ontology()
        for concept_name, concept in base.items():
            metadata = concept.get("metadata", {})
            if "themes" in metadata:
                if concept_name not in themes_data["concept_themes"]:
                    themes_data["concept_themes"][concept_name] = metadata["themes"]

        if args.json:
            print(json.dumps(themes_data, indent=2))
        else:
            print(f"Theme set for {args.genre.upper()}")
            print("=" * 50)

            if themes_data["concept_themes"]:
                print("\nThemes by concept:")
                for concept_name, themes_list in sorted(
                    themes_data["concept_themes"].items()
                ):
                    print(f"  {concept_name}:")
                    for theme in themes_list:
                        print(f"    - {theme}")
            else:
                print(
                    f"\nNo explicit themes defined in {args.genre} ontology metadata."
                )
                print("However, the following concepts are available:")
                concept_names = sorted(genre_ont.keys())
                for name in concept_names:
                    print(f"  - {name}")

        return 0

    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    except FileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"Error: Failed to get themes: {exc}", file=sys.stderr)
        return 1


def _print_concept_formatted(concept_data: dict) -> None:
    """Pretty-print a concept definition.

    Args:
        concept_data: Dictionary representation of the concept
    """
    print(f"\nConcept: {concept_data['name']}")
    print("=" * 60)

    print(f"\nDefinition:")
    print(f"  {concept_data['definition']}")

    if concept_data.get("category"):
        print(f"\nCategory: {concept_data['category']}")

    if concept_data.get("parent_concepts"):
        print(f"\nParent Concepts:")
        for parent in concept_data["parent_concepts"]:
            print(f"  - {parent}")

    if concept_data.get("relationships"):
        print(f"\nRelationships:")
        for rel in concept_data["relationships"]:
            source = rel.get("source_concept", rel.get("source", ""))
            target = rel.get("target_concept", rel.get("target", ""))
            cardinality = rel.get("cardinality", "")
            description = rel.get("description", "")

            print(f"  - {source} -> {target}")
            if cardinality:
                print(f"    Cardinality: {cardinality}")
            if description:
                print(f"    Description: {description}")

    if concept_data.get("validation_rules"):
        print(f"\nValidation Rules:")
        for rule in concept_data["validation_rules"]:
            rule_id = rule.get("rule_id", "")
            condition = rule.get("condition", "")
            error_msg = rule.get("error_message", "")

            print(f"  - {rule_id}")
            if condition:
                print(f"    Condition: {condition}")
            if error_msg:
                print(f"    Error: {error_msg}")

    if concept_data.get("metadata"):
        print(f"\nMetadata:")
        for key, value in concept_data["metadata"].items():
            if isinstance(value, (list, dict)):
                print(f"  {key}: {json.dumps(value, indent=4)}")
            else:
                print(f"  {key}: {value}")

    print()
