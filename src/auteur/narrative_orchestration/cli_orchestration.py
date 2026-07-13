"""Orchestration Workflow CLI for Structure composition.

Provides CLI commands for complete narrative orchestration workflow:
- seed: Create template outlines from StoryIdentity
- validate: Run all 3 validators and report results
- graph: Visualize outline structure and relationships
- status: Show comprehensive outline status

All commands work identically across all 3 genres (netorara, mystery, gentlefemdom).
"""

from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from auteur.identity import StoryIdentity
from auteur.blueprint import Genre
from auteur.narrative_blueprint.loader.outline_loader import OutlineLoader
from auteur.narrative_orchestration.orchestrator.outline_builder import OutlineBuilder
from auteur.narrative_orchestration.orchestrator.outline_inspector import OutlineInspector
from auteur.narrative_orchestration.orchestrator.outline_grapher import OutlineGrapher
from auteur.narrative_orchestration.validator.reference_validator import ReferenceValidator
from auteur.narrative_orchestration.validator.chronological_validator import ChronologicalValidator
from auteur.narrative_orchestration.validator.contradiction_validator import ContradictionValidator


class OrchestrationError(Exception):
    """Errors from orchestration operations."""
    pass


class CliOrchestrationCommands:
    """CLI commands for orchestration workflow.

    Provides seed, validate, graph, and status commands for managing narrative
    outline structures. Works with any genre without special-casing.
    """

    def __init__(self, project_path: Path, genre: str):
        """Initialize orchestration commands.

        Args:
            project_path: Path to the project directory
            genre: Genre slug (netorare, mystery, gentlefemdom)
        """
        self.project_path = Path(project_path)
        self.genre = genre
        self.outlines_dir = self.project_path / ".auteur" / "outlines" / genre
        self.loader = OutlineLoader()

    def seed_command(
        self,
        story_identity_path: Path,
        *,
        force: bool = False,
    ) -> int:
        """Seed template outlines from StoryIdentity.

        Creates:
        - Book Outline
        - Sequence Outlines (3-4 depending on genre)
        - Chapter Outlines (12-16 with genre-specific goals)
        - Character Arc for protagonist
        - Story Arc for central plot

        Args:
            story_identity_path: Path to story_identity.yaml
            force: Overwrite existing outlines if True

        Returns:
            Exit code (0 on success, non-zero on failure)
        """
        try:
            # Load StoryIdentity
            if not story_identity_path.exists():
                print(f"Error: Story identity file not found: {story_identity_path}", file=sys.stderr)
                return 1

            try:
                identity = StoryIdentity.from_yaml(story_identity_path)
            except Exception as exc:
                print(f"Error: Failed to parse story identity: {exc}", file=sys.stderr)
                return 1

            # Validate genre matches
            if identity.story_type.genre.value != self.genre:
                print(
                    f"Error: Story identity genre '{identity.story_type.genre.value}' "
                    f"does not match command genre '{self.genre}'",
                    file=sys.stderr
                )
                return 1

            # Check if outlines already exist
            if self.outlines_dir.exists() and self.outlines_dir.glob("*.yaml"):
                if not force:
                    print(
                        f"Error: Outlines already exist at {self.outlines_dir}. "
                        f"Use --force to overwrite.",
                        file=sys.stderr
                    )
                    return 1

            # Create outlines directory
            try:
                self.outlines_dir.mkdir(parents=True, exist_ok=True)
            except OSError as exc:
                print(f"Error: Could not create outlines directory: {exc}", file=sys.stderr)
                return 1

            # Build outlines from identity
            print(f"Seeding outlines for '{identity.title}' ({self.genre})...")
            try:
                builder = OutlineBuilder(identity)
                (
                    book_outline,
                    sequence_outlines,
                    chapter_outlines,
                    character_arc,
                    story_arc,
                ) = builder.seed_from_story_identity()
            except Exception as exc:
                print(f"Error: Failed to build outlines: {exc}", file=sys.stderr)
                return 1

            # Save outlines
            try:
                self._save_outlines(
                    book_outline,
                    sequence_outlines,
                    chapter_outlines,
                    character_arc,
                    story_arc,
                )
            except Exception as exc:
                print(f"Error: Failed to save outlines: {exc}", file=sys.stderr)
                return 1

            # Report success
            print(f"[OK] Created Book Outline at {self.outlines_dir / 'book_outline.yaml'}")
            print(f"[OK] Created {len(sequence_outlines)} Sequence Outlines")
            print(f"[OK] Created {len(chapter_outlines)} Chapter Outlines")
            print(f"[OK] Created Character Arc at {self.outlines_dir / 'character_arc.yaml'}")
            print(f"[OK] Created Story Arc at {self.outlines_dir / 'story_arc.yaml'}")
            print(f"\nOutlines saved to {self.outlines_dir}")
            print("Next: Run 'auteur blueprint status' to review the structure")
            return 0

        except Exception as exc:
            print(f"Error: {exc}", file=sys.stderr)
            return 1

    def validate_command(self) -> int:
        """Validate all outlines against reference, chronological, and contradiction validators.

        Returns:
            Exit code (0 if all validations pass, 1 if any fail, 2 if no outlines found)
        """
        try:
            # Load all outlines
            artifacts = self._load_outlines()
            if not artifacts:
                print(f"Error: No outline files found in {self.outlines_dir}", file=sys.stderr)
                return 2

            print(f"Validating {len(artifacts)} outline artifacts...")
            print()

            has_errors = False

            # Run Reference Validator
            print("1. Reference Validator")
            print("   Checking all IDs resolve correctly...")
            try:
                ref_validator = ReferenceValidator(artifacts)
                ref_result = ref_validator.validate_all_references()

                if ref_result.is_valid:
                    print(f"   [OK] All references valid ({len(artifacts)} artifacts)")
                else:
                    print(f"   [FAIL] {len(ref_result.errors)} reference errors found:")
                    for error in ref_result.errors[:5]:
                        print(f"     - {error.artifact_id}: {error.message}")
                    if len(ref_result.errors) > 5:
                        print(f"     ... and {len(ref_result.errors) - 5} more")
                    has_errors = True
            except Exception as exc:
                print(f"   [FAIL] Reference validator failed: {exc}", file=sys.stderr)
                has_errors = True

            print()

            # Run Chronological Validator
            print("2. Chronological Validator")
            print("   Checking narrative ordering and progression...")
            try:
                chrono_validator = ChronologicalValidator()

                # Add artifacts to validator
                for artifact_id, artifact in artifacts.items():
                    artifact_type = artifact.artifact_type()
                    if artifact_type == "book_outline":
                        chrono_validator.add_book(artifact_id, artifact)
                    elif artifact_type == "sequence_outline":
                        chrono_validator.add_sequence(artifact_id, artifact)
                    elif artifact_type == "chapter_outline":
                        chrono_validator.add_chapter(artifact_id, artifact)
                    elif artifact_type == "character_arc":
                        chrono_validator.add_character_arc(artifact_id, artifact)
                    elif artifact_type == "story_arc":
                        chrono_validator.add_story_arc(artifact_id, artifact)

                is_valid = chrono_validator.validate_all_chronology()

                if is_valid:
                    print("   [OK] Narrative ordering is valid")
                else:
                    print(f"   [FAIL] {len(chrono_validator.violations)} chronological violations found:")
                    for violation in chrono_validator.violations[:5]:
                        print(f"     - {violation.source_artifact_id}: {violation.message}")
                    if len(chrono_validator.violations) > 5:
                        print(f"     ... and {len(chrono_validator.violations) - 5} more")
                    has_errors = True
            except Exception as exc:
                print(f"   [FAIL] Chronological validator failed: {exc}", file=sys.stderr)
                has_errors = True

            print()

            # Run Contradiction Validator
            print("3. Contradiction Validator")
            print("   Checking for conflicts between artifacts...")
            try:
                # Find book outline and chapter outlines for contradiction validator
                book_outline = None
                chapter_outlines = {}
                sequence_outlines = {}
                character_arcs = {}
                story_arcs = {}

                for artifact_id, artifact in artifacts.items():
                    artifact_type = artifact.artifact_type()
                    if artifact_type == "book_outline":
                        book_outline = artifact
                    elif artifact_type == "chapter_outline":
                        chapter_outlines[artifact_id] = artifact
                    elif artifact_type == "sequence_outline":
                        sequence_outlines[artifact_id] = artifact
                    elif artifact_type == "character_arc":
                        character_arcs[artifact_id] = artifact
                    elif artifact_type == "story_arc":
                        story_arcs[artifact_id] = artifact

                if book_outline and chapter_outlines:
                    contradiction_validator = ContradictionValidator(
                        book_outline=book_outline,
                        chapter_outlines=chapter_outlines,
                        genre=self.genre,
                    )

                    if sequence_outlines:
                        contradiction_validator.sequence_outlines = sequence_outlines
                    if character_arcs:
                        contradiction_validator.character_arcs = character_arcs
                    if story_arcs:
                        contradiction_validator.story_arcs = story_arcs

                    contradiction_result = contradiction_validator.validate_all_contradictions()

                    if contradiction_result.is_valid:
                        print("   [OK] No contradictions detected")
                    else:
                        print(f"   [FAIL] {len(contradiction_result.contradictions)} contradictions found:")
                        for contradiction in contradiction_result.contradictions[:5]:
                            print(f"     - {contradiction.artifact_a} vs {contradiction.artifact_b}: {contradiction.description}")
                        if len(contradiction_result.contradictions) > 5:
                            print(f"     ... and {len(contradiction_result.contradictions) - 5} more")
                        has_errors = True
                else:
                    print("   [SKIP] Skipped (requires Book Outline and Chapter Outlines)")
            except Exception as exc:
                print(f"   [SKIP] Contradiction validator skipped: {exc}")

            print()

            # Summary
            if has_errors:
                print("[FAIL] Validation failed with errors")
                return 1
            else:
                print("[OK] All validations passed")
                return 0

        except Exception as exc:
            print(f"Error: {exc}", file=sys.stderr)
            return 1

    def graph_command(self, output_format: str = "text") -> int:
        """Display outline structure visualization.

        Args:
            output_format: Output format ("text" for ASCII art, "dot" for Graphviz)

        Returns:
            Exit code (0 on success, non-zero on failure)
        """
        try:
            # Load all outlines
            artifacts = self._load_outlines()
            if not artifacts:
                print(f"Error: No outline files found in {self.outlines_dir}", file=sys.stderr)
                return 1

            print(f"Outline Structure ({output_format.upper()} format)\n")
            print("=" * 70)
            print()

            # Use OutlineGrapher to generate visualization
            try:
                grapher = OutlineGrapher()

                # Add nodes for each artifact
                for artifact_id, artifact in artifacts.items():
                    artifact_type = artifact.artifact_type()
                    if artifact_type == "book_outline":
                        grapher.add_node(artifact_id, "book", artifact.title)
                    elif artifact_type == "sequence_outline":
                        grapher.add_node(artifact_id, "sequence", artifact.name, parent_id="book_001")
                    elif artifact_type == "chapter_outline":
                        grapher.add_node(artifact_id, "chapter", f"Chapter {artifact.chapter_number}", parent_id=artifact.parent_id)
                    elif artifact_type == "character_arc":
                        grapher.add_node(artifact_id, "arc", f"Character: {artifact.character_name}")
                    elif artifact_type == "story_arc":
                        grapher.add_node(artifact_id, "arc", f"Story: {artifact.arc_name}")

                # Add arc references for character and story arcs
                for artifact_id, artifact in artifacts.items():
                    artifact_type = artifact.artifact_type()
                    if artifact_type == "character_arc" and hasattr(artifact, 'span_chapters'):
                        chapter_ids = [f"chapter_{ch:02d}" for ch in artifact.span_chapters]
                        grapher.add_arc_reference(artifact_id, artifact.character_name, "character_arc", chapter_ids)
                    elif artifact_type == "story_arc" and hasattr(artifact, 'span_chapters'):
                        chapter_ids = [f"chapter_{ch:02d}" for ch in artifact.span_chapters]
                        grapher.add_arc_reference(artifact_id, artifact.arc_name, "story_arc", chapter_ids)

                # Generate and display output
                if output_format == "dot":
                    graph_output = grapher.render_as_dot()
                else:  # default to text
                    graph_output = grapher.render_as_ascii()

                print(graph_output)
                print()
                print("=" * 70)
                return 0

            except Exception as exc:
                print(f"Error: Failed to generate graph: {exc}", file=sys.stderr)
                return 1

        except Exception as exc:
            print(f"Error: {exc}", file=sys.stderr)
            return 1

    def status_command(self) -> int:
        """Display comprehensive outline status report.

        Shows structure, character arcs, story arcs, coverage, and completeness.

        Returns:
            Exit code (0 on success, non-zero on failure)
        """
        try:
            # Load all outlines
            artifacts = self._load_outlines()
            if not artifacts:
                print(f"Error: No outline files found in {self.outlines_dir}", file=sys.stderr)
                return 1

            print(f"Outline Status Report ({self.genre})")
            print("=" * 70)
            print()

            try:
                # Create inspector and add artifacts
                inspector = OutlineInspector()
                for artifact_id, artifact in artifacts.items():
                    inspector.add_artifact(artifact)

                # Display structure
                print("STRUCTURE")
                print("-" * 70)
                structure_output = inspector.show_structure()
                if structure_output:
                    print(structure_output)
                print()

                # Display character arcs
                if inspector.character_arcs:
                    print("CHARACTER ARCS")
                    print("-" * 70)
                    char_output = inspector.show_character_arcs()
                    if char_output:
                        print(char_output)
                    print()

                # Display story arcs
                if inspector.story_arcs:
                    print("STORY ARCS")
                    print("-" * 70)
                    story_output = inspector.show_story_arcs()
                    if story_output:
                        print(story_output)
                    print()

                # Display coverage
                print("COVERAGE")
                print("-" * 70)
                coverage_output = inspector.show_coverage()
                if coverage_output:
                    print(coverage_output)
                print()

                # Display completeness
                print("COMPLETENESS")
                print("-" * 70)
                completeness_output = inspector.show_completeness()
                if completeness_output:
                    print(completeness_output)
                print()

                # Display missing elements
                missing_output = inspector.show_missing_elements()
                if missing_output:
                    print("MISSING ELEMENTS")
                    print("-" * 70)
                    print(missing_output)
                    print()

                print("=" * 70)
                return 0

            except Exception as exc:
                print(f"Error: Failed to generate status report: {exc}", file=sys.stderr)
                return 1

        except Exception as exc:
            print(f"Error: {exc}", file=sys.stderr)
            return 1

    def _save_outlines(
        self,
        book_outline,
        sequence_outlines,
        chapter_outlines,
        character_arc,
        story_arc,
    ) -> None:
        """Save all generated outlines to disk.

        Args:
            book_outline: BookOutline artifact
            sequence_outlines: List of SequenceOutline artifacts
            chapter_outlines: List of ChapterOutline artifacts
            character_arc: CharacterArc artifact
            story_arc: StoryArc artifact

        Raises:
            OSError: If file operations fail
        """
        # Save book outline
        book_path = self.outlines_dir / "book_outline.yaml"
        self.loader.save_outline(book_outline, str(book_path))

        # Save sequence outlines
        for i, seq in enumerate(sequence_outlines):
            seq_path = self.outlines_dir / f"sequence_{i+1:02d}.yaml"
            self.loader.save_outline(seq, str(seq_path))

        # Save chapter outlines
        for ch in chapter_outlines:
            ch_path = self.outlines_dir / f"chapter_{ch.chapter_number:02d}.yaml"
            self.loader.save_outline(ch, str(ch_path))

        # Save character arc
        if character_arc:
            char_path = self.outlines_dir / "character_arc.yaml"
            self.loader.save_outline(character_arc, str(char_path))

        # Save story arc
        if story_arc:
            story_path = self.outlines_dir / "story_arc.yaml"
            self.loader.save_outline(story_arc, str(story_path))

    def _load_outlines(self) -> dict:
        """Load all outline artifacts from disk.

        Returns:
            Dictionary mapping artifact IDs to artifact objects

        Raises:
            FileNotFoundError: If outline directory doesn't exist
        """
        artifacts = {}

        if not self.outlines_dir.exists():
            return artifacts

        # Load all YAML files in outlines directory
        for yaml_file in sorted(self.outlines_dir.glob("*.yaml")):
            try:
                # Infer artifact type from filename
                if "book" in yaml_file.stem:
                    from auteur.narrative_blueprint.schema.book_outline import BookOutline
                    artifact = self.loader.load_outline(str(yaml_file), BookOutline)
                    artifacts[f"book_001"] = artifact

                elif "sequence" in yaml_file.stem:
                    from auteur.narrative_blueprint.schema.sequence_outline import SequenceOutline
                    artifact = self.loader.load_outline(str(yaml_file), SequenceOutline)
                    seq_id = f"sequence_{artifact.sequence_number:02d}"
                    artifacts[seq_id] = artifact

                elif "chapter" in yaml_file.stem:
                    from auteur.narrative_blueprint.schema.chapter_outline import ChapterOutline
                    artifact = self.loader.load_outline(str(yaml_file), ChapterOutline)
                    ch_id = f"chapter_{artifact.chapter_number:02d}"
                    artifacts[ch_id] = artifact

                elif "character" in yaml_file.stem:
                    from auteur.narrative_blueprint.schema.character_arc import CharacterArc
                    artifact = self.loader.load_outline(str(yaml_file), CharacterArc)
                    artifacts["character_arc_protagonist"] = artifact

                elif "story" in yaml_file.stem:
                    from auteur.narrative_blueprint.schema.story_arc import StoryArc
                    artifact = self.loader.load_outline(str(yaml_file), StoryArc)
                    artifacts["story_arc_central"] = artifact

            except Exception as exc:
                # Skip files that can't be loaded
                print(f"Warning: Could not load {yaml_file.name}: {exc}", file=sys.stderr)
                continue

        return artifacts


# CLI handler functions for integration with argparse

def handle_orchestration_seed(
    project_path: Path,
    genre: str,
    story_identity_path: Path,
    *,
    force: bool = False,
) -> int:
    """Handle 'blueprint seed' command."""
    commands = CliOrchestrationCommands(project_path, genre)
    return commands.seed_command(story_identity_path, force=force)


def handle_orchestration_validate(
    project_path: Path,
    genre: str,
) -> int:
    """Handle 'blueprint validate' command."""
    commands = CliOrchestrationCommands(project_path, genre)
    return commands.validate_command()


def handle_orchestration_graph(
    project_path: Path,
    genre: str,
    output_format: str = "text",
) -> int:
    """Handle 'blueprint graph' command."""
    commands = CliOrchestrationCommands(project_path, genre)
    return commands.graph_command(output_format)


def handle_orchestration_status(
    project_path: Path,
    genre: str,
) -> int:
    """Handle 'blueprint status' command."""
    commands = CliOrchestrationCommands(project_path, genre)
    return commands.status_command()
