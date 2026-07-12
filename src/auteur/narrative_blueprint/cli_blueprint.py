"""Blueprint CLI handlers for outline management.

Provides handlers for:
- blueprint init: Create empty book outline
- blueprint list: List existing outlines

These handlers work with argparse and can be integrated into any genre CLI.
"""

from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from auteur.genre_pipeline.session import GenreSessionStore
from auteur.genre_pipeline.registry import get_genre_pipeline
from auteur.narrative_blueprint.loader.outline_loader import OutlineLoader
from auteur.narrative_blueprint.schema.book_outline import BookOutline


class BlueprintError(Exception):
    """Errors from blueprint operations."""
    pass


def handle_blueprint_init(
    project_path: Path,
    genre: str,
    *,
    working_title: str = "Untitled Story",
) -> int:
    """Create an empty book outline for a story.

    Args:
        project_path: Path to the project directory
        genre: Genre slug (netorare, mystery, gentlefemdom)
        working_title: Optional working title for the book

    Returns:
        Exit code (0 on success, non-zero on failure)
    """
    try:
        project = Path(project_path)
        spec = get_genre_pipeline(genre)

        # Load the genre session to get story_id
        store = GenreSessionStore.for_project(project, spec)
        try:
            session = store.load()
        except Exception as exc:
            print(f"Error: Could not load genre session for {genre}: {exc}", file=sys.stderr)
            return 1

        # Create outline directory
        outlines_dir = project / ".auteur" / "outlines" / genre
        try:
            outlines_dir.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            print(f"Error: Could not create outlines directory: {exc}", file=sys.stderr)
            return 1

        # Create empty BookOutline with default phase names
        now = datetime.now(timezone.utc)
        phases = {
            1: "Setup & Exposition",
            2: "Inciting Incident",
            3: "Rising Action - Act 1",
            4: "Rising Action - Act 2",
            5: "Midpoint",
            6: "Rising Action - Act 3",
            7: "Climax Setup",
            8: "Climax & Resolution",
            9: "Denouement & Epilogue",
        }

        outline = BookOutline(
            genre=genre,
            story_id=session.id,
            name="Book Outline",
            description=f"Outline for {working_title}",
            created_at=now,
            modified_at=now,
            parent_id=None,
            title=working_title,
            chapter_estimate=20,
            structure="3-act",
            phases_summary=phases,
        )

        # Save outline
        outline_path = outlines_dir / "book_outline.yaml"
        loader = OutlineLoader()
        try:
            loader.save_outline(outline, str(outline_path))
        except Exception as exc:
            print(f"Error: Could not save outline: {exc}", file=sys.stderr)
            return 1

        print(f"Created book outline at {outline_path}")
        print(f"Story ID: {session.id}")
        print(f"Genre: {genre}")
        return 0

    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


def handle_blueprint_list(
    project_path: Path,
    genre: str,
) -> int:
    """List outline artifacts in the project.

    Args:
        project_path: Path to the project directory
        genre: Genre slug (netorare, mystery, gentlefemdom)

    Returns:
        Exit code (0 on success, non-zero on failure)
    """
    try:
        project = Path(project_path)
        outlines_dir = project / ".auteur" / "outlines" / genre

        if not outlines_dir.exists():
            print(f"No outlines directory found at {outlines_dir}")
            return 0

        yaml_files = sorted(outlines_dir.glob("*.yaml"))
        if not yaml_files:
            print(f"No outline files found in {outlines_dir}")
            return 0

        print(f"Outlines in {genre}:")
        print()
        loader = OutlineLoader()

        for yaml_file in yaml_files:
            try:
                # Try to load the file to get metadata
                # We'll just read the YAML to extract basic info
                import yaml
                with open(yaml_file, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f)

                if data:
                    outline_type = data.get("artifact_type", "unknown")
                    name = data.get("name", yaml_file.stem)
                    description = data.get("description", "")
                    print(f"  - {yaml_file.name}")
                    print(f"    Type: {outline_type}")
                    print(f"    Name: {name}")
                    if description:
                        print(f"    Description: {description}")
                    print()
            except Exception as exc:
                print(f"  - {yaml_file.name} (error reading: {exc})")
                print()

        return 0

    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
