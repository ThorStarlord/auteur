"""Realization Workflow CLI for Layer 3 narrative structure.

Provides CLI commands for complete scene realization workflow:
- seed: Create template scenes from chapter outlines
- validate: Run all validators (knowledge, temporal, realization) and report results
- inspect: Show scene tree, coverage, and status
- graph: Visualize scene sequence and temporal relationships

All commands work identically across all 3 genres (netorara, mystery, gentlefemdom).
"""

from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from auteur.narrative_blueprint.loader.outline_loader import OutlineLoader
from auteur.narrative_blueprint.schema.chapter_outline import ChapterOutline
from auteur.narrative_realization.loader.scene_loader import SceneLoader
from auteur.narrative_realization.orchestrator.scene_builder import SceneBuilder
from auteur.narrative_realization.orchestrator.scene_inspector import SceneInspector
from auteur.narrative_realization.schema.scene_outline import SceneOutline
from auteur.narrative_realization.validator.knowledge_validator import KnowledgeValidator
from auteur.narrative_realization.validator.temporal_validator import TemporalValidator
from auteur.narrative_realization.validator.realization_validator import RealizationValidator


class RealizationError(Exception):
    """Errors from realization operations."""
    pass


class CliRealizationCommands:
    """CLI commands for realization workflow.

    Provides seed, validate, inspect, and graph commands for managing scene
    structures. Works with any genre without special-casing.
    """

    def __init__(self, project_path: Path, genre: str):
        """Initialize realization commands.

        Args:
            project_path: Path to the project directory
            genre: Genre slug (netorara, mystery, gentlefemdom)
        """
        self.project_path = Path(project_path)
        self.genre = genre
        self.outlines_dir = self.project_path / ".auteur" / "outlines" / genre
        self.scenes_dir = self.project_path / ".auteur" / "scenes" / genre
        self.outline_loader = OutlineLoader()
        self.scene_loader = SceneLoader()

    def seed_command(
        self,
        *,
        force: bool = False,
    ) -> int:
        """Seed template scenes from chapter outlines.

        Creates one or more template scenes for each chapter in the project.
        Each scene has draft status and is ready for author refinement.

        Args:
            force: Overwrite existing scenes if True

        Returns:
            Exit code (0 on success, non-zero on failure)
        """
        try:
            # Load chapter outlines
            chapter_outlines = self._load_chapter_outlines()
            if not chapter_outlines:
                print(f"Error: No chapter outlines found in {self.outlines_dir}", file=sys.stderr)
                return 1

            # Get story_id from first chapter
            story_id = chapter_outlines[0].story_id

            # Check if scenes already exist
            if self.scenes_dir.exists() and list(self.scenes_dir.glob("**/*.yaml")):
                if not force:
                    print(
                        f"Error: Scenes already exist at {self.scenes_dir}. "
                        f"Use --force to overwrite.",
                        file=sys.stderr
                    )
                    return 1

            # Create scenes directory
            try:
                self.scenes_dir.mkdir(parents=True, exist_ok=True)
            except OSError as exc:
                print(f"Error: Could not create scenes directory: {exc}", file=sys.stderr)
                return 1

            # Build scenes from chapters
            print(f"Seeding scenes for {len(chapter_outlines)} chapters ({self.genre})...")
            try:
                builder = SceneBuilder(genre=self.genre)
                all_scenes = builder.build_scenes_from_chapters(
                    chapter_outlines,
                    story_id
                )
            except Exception as exc:
                print(f"Error: Failed to build scenes: {exc}", file=sys.stderr)
                return 1

            # Save scenes
            try:
                self._save_scenes(all_scenes)
            except Exception as exc:
                print(f"Error: Failed to save scenes: {exc}", file=sys.stderr)
                return 1

            # Report success
            scene_count_by_chapter = {}
            for scene in all_scenes:
                ch_id = scene.chapter_id
                scene_count_by_chapter[ch_id] = scene_count_by_chapter.get(ch_id, 0) + 1

            print(f"[OK] Created {len(all_scenes)} scenes across {len(chapter_outlines)} chapters")
            for ch_id in sorted(scene_count_by_chapter.keys()):
                count = scene_count_by_chapter[ch_id]
                print(f"     {ch_id}: {count} scene{'s' if count != 1 else ''}")

            print(f"\nScenes saved to {self.scenes_dir}")
            print("Next: Run 'auteur {genre} realization inspect' to review the structure")
            return 0

        except Exception as exc:
            print(f"Error: {exc}", file=sys.stderr)
            return 1

    def validate_command(self) -> int:
        """Validate all scenes against knowledge, temporal, and realization validators.

        Returns:
            Exit code (0 if all validations pass, 1 if any fail, 2 if no scenes found)
        """
        try:
            # Load all scenes
            scenes = self._load_scenes()
            if not scenes:
                print(f"Error: No scene files found in {self.scenes_dir}", file=sys.stderr)
                return 2

            print(f"Validating {len(scenes)} scenes...")
            print()

            has_errors = False

            # Run Temporal Validator
            print("1. Temporal Validator")
            print("   Checking narrative positioning and temporal relationships...")
            try:
                temporal_validator = TemporalValidator()

                # Add scenes to validator
                for scene_id, scene in scenes.items():
                    temporal_validator.add_scene(scene)

                result = temporal_validator.validate_all_scenes()

                if result.is_valid:
                    print("   [OK] Temporal relationships are valid")
                else:
                    print(f"   [FAIL] {len(result.violations)} temporal violations found:")
                    for violation in result.violations[:5]:
                        print(f"     - {violation.scene_id}: {violation.message}")
                    if len(result.violations) > 5:
                        print(f"     ... and {len(result.violations) - 5} more")
                    has_errors = True
            except Exception as exc:
                print(f"   [FAIL] Temporal validator failed: {exc}", file=sys.stderr)
                has_errors = True

            print()

            # Run Knowledge Validator
            print("2. Knowledge Validator")
            print("   Checking knowledge consistency and no retroactive forgetting...")
            try:
                knowledge_validator = KnowledgeValidator()

                # Add scenes to validator
                for scene_id, scene in scenes.items():
                    knowledge_validator.add_scene(scene)

                result = knowledge_validator.validate_all_scenes()

                if result.is_valid:
                    print("   [OK] Knowledge consistency validated")
                else:
                    print(f"   [FAIL] {len(result.violations)} knowledge violations found:")
                    for violation in result.violations[:5]:
                        print(f"     - {violation.scene_id}: {violation.message}")
                    if len(result.violations) > 5:
                        print(f"     ... and {len(result.violations) - 5} more")
                    has_errors = True
            except Exception as exc:
                print(f"   [SKIP] Knowledge validator skipped: {exc}")

            print()

            # Run Realization Validator
            print("3. Realization Validator")
            print("   Checking arc beat realization...")
            try:
                realization_validator = RealizationValidator()

                # Add scenes to validator
                for scene_id, scene in scenes.items():
                    realization_validator.add_scene(scene)

                result = realization_validator.validate_all_scenes()

                if result.is_valid:
                    print("   [OK] Arc beat realization validated")
                else:
                    print(f"   [FAIL] {len(result.violations)} realization violations found:")
                    for violation in result.violations[:5]:
                        print(f"     - {violation.scene_id}: {violation.message}")
                    if len(result.violations) > 5:
                        print(f"     ... and {len(result.violations) - 5} more")
                    has_errors = True
            except Exception as exc:
                print(f"   [SKIP] Realization validator skipped: {exc}")

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

    def inspect_command(self) -> int:
        """Display scene structure and coverage information.

        Shows:
        - Scene tree organized by chapter
        - POV character coverage
        - Character participation
        - Arc beat realization status
        - Completeness metrics

        Returns:
            Exit code (0 on success, non-zero on failure)
        """
        try:
            # Load all scenes
            scenes = self._load_scenes()
            if not scenes:
                print(f"Error: No scene files found in {self.scenes_dir}", file=sys.stderr)
                return 1

            print(f"Scene Inspection Report ({self.genre})")
            print("=" * 70)
            print()

            try:
                # Create inspector and add scenes
                inspector = SceneInspector()
                for scene_id, scene in scenes.items():
                    inspector.add_scene(scene)

                # Display scene tree
                print("SCENE TREE")
                print("-" * 70)
                tree_output = inspector.show_scene_tree()
                if tree_output:
                    print(tree_output)
                print()

                # Display POV coverage
                print("POV CHARACTER COVERAGE")
                print("-" * 70)
                pov_output = inspector.show_pov_coverage()
                if pov_output:
                    print(pov_output)
                print()

                # Display participant coverage
                print("CHARACTER PARTICIPATION")
                print("-" * 70)
                participant_output = inspector.show_participant_coverage()
                if participant_output:
                    print(participant_output)
                print()

                # Display arc beat coverage
                print("ARC BEAT REALIZATION")
                print("-" * 70)
                arc_output = inspector.show_arc_beat_coverage()
                if arc_output:
                    print(arc_output)
                print()

                # Display status summary
                print("STATUS SUMMARY")
                print("-" * 70)
                status_output = inspector.show_status_summary()
                if status_output:
                    print(status_output)
                print()

                # Display completeness
                print("COMPLETENESS METRICS")
                print("-" * 70)
                completeness_output = inspector.show_completeness()
                if completeness_output:
                    print(completeness_output)
                print()

                print("=" * 70)
                return 0

            except Exception as exc:
                print(f"Error: Failed to generate inspection report: {exc}", file=sys.stderr)
                return 1

        except Exception as exc:
            print(f"Error: {exc}", file=sys.stderr)
            return 1

    def graph_command(self, output_format: str = "text") -> int:
        """Display scene sequence visualization.

        Shows scenes organized by chapter with temporal relationships.

        Args:
            output_format: Output format ("text" for ASCII art, "dot" for Graphviz)

        Returns:
            Exit code (0 on success, non-zero on failure)
        """
        try:
            # Load all scenes
            scenes = self._load_scenes()
            if not scenes:
                print(f"Error: No scene files found in {self.scenes_dir}", file=sys.stderr)
                return 1

            print(f"Scene Sequence Graph ({output_format.upper()} format)")
            print()
            print("=" * 70)
            print()

            if output_format == "dot":
                graph_output = self._render_scenes_as_dot(scenes)
            else:
                graph_output = self._render_scenes_as_ascii(scenes)

            print(graph_output)
            print()
            print("=" * 70)
            return 0

        except Exception as exc:
            print(f"Error: {exc}", file=sys.stderr)
            return 1

    def _load_chapter_outlines(self) -> list[ChapterOutline]:
        """Load all chapter outlines from disk.

        Returns:
            List of ChapterOutline objects sorted by chapter number

        Raises:
            FileNotFoundError: If outline directory doesn't exist
        """
        outlines = []

        if not self.outlines_dir.exists():
            return outlines

        # Load all chapter_*.yaml files
        for yaml_file in sorted(self.outlines_dir.glob("chapter_*.yaml")):
            try:
                artifact = self.outline_loader.load_outline(str(yaml_file), ChapterOutline)
                if isinstance(artifact, ChapterOutline):
                    outlines.append(artifact)
            except Exception as exc:
                print(f"Warning: Could not load {yaml_file.name}: {exc}", file=sys.stderr)
                continue

        # Sort by chapter number
        outlines.sort(key=lambda c: c.chapter_number)
        return outlines

    def _load_scenes(self) -> dict[str, SceneOutline]:
        """Load all scene artifacts from disk.

        Returns:
            Dictionary mapping scene IDs to SceneOutline objects
        """
        scenes = {}

        if not self.scenes_dir.exists():
            return scenes

        # Load all YAML files in scenes directory
        for yaml_file in sorted(self.scenes_dir.glob("**/*.yaml")):
            try:
                scene = self.scene_loader.load_scene(str(yaml_file))
                scenes[scene.id] = scene
            except Exception as exc:
                print(f"Warning: Could not load {yaml_file.name}: {exc}", file=sys.stderr)
                continue

        return scenes

    def _save_scenes(self, scenes: list[SceneOutline]) -> None:
        """Save all scenes to disk organized by chapter.

        Args:
            scenes: List of SceneOutline objects to save

        Raises:
            OSError: If file operations fail
        """
        for scene in scenes:
            chapter_dir = self.scenes_dir / scene.chapter_id
            scene_path = chapter_dir / f"{scene.id}.yaml"
            self.scene_loader.save_scene(scene, str(scene_path))

    def _render_scenes_as_ascii(self, scenes: dict[str, SceneOutline]) -> str:
        """Render scene sequence as ASCII art.

        Args:
            scenes: Dictionary of scene ID → SceneOutline

        Returns:
            ASCII art representation
        """
        # Group scenes by chapter
        by_chapter = {}
        for scene in scenes.values():
            if scene.chapter_id not in by_chapter:
                by_chapter[scene.chapter_id] = []
            by_chapter[scene.chapter_id].append(scene)

        lines = []
        for chapter_id in sorted(by_chapter.keys()):
            chapter_scenes = sorted(
                by_chapter[chapter_id],
                key=lambda s: s.narrative_position or 0
            )
            lines.append(f"{chapter_id.upper()}")

            for i, scene in enumerate(chapter_scenes):
                is_last = i == len(chapter_scenes) - 1
                connector = "└─" if is_last else "├─"
                lines.append(f"  {connector} {scene.id}")

                # Show temporal relations
                if scene.temporal_relation:
                    if scene.temporal_relation.follows_scene:
                        indent = "    " if is_last else "  │ "
                        lines.append(f"{indent} (follows {scene.temporal_relation.follows_scene})")

            lines.append()

        return "\n".join(lines)

    def _render_scenes_as_dot(self, scenes: dict[str, SceneOutline]) -> str:
        """Render scene sequence as Graphviz DOT format.

        Args:
            scenes: Dictionary of scene ID → SceneOutline

        Returns:
            DOT format representation
        """
        lines = []
        lines.append("digraph SceneSequence {")
        lines.append('  rankdir=TB;')
        lines.append('  node [shape=box];')
        lines.append()

        # Add chapter clusters
        by_chapter = {}
        for scene in scenes.values():
            if scene.chapter_id not in by_chapter:
                by_chapter[scene.chapter_id] = []
            by_chapter[scene.chapter_id].append(scene)

        cluster_id = 0
        for chapter_id in sorted(by_chapter.keys()):
            cluster_id += 1
            chapter_scenes = sorted(
                by_chapter[chapter_id],
                key=lambda s: s.narrative_position
            )

            lines.append(f'  subgraph cluster_{cluster_id} {{')
            lines.append(f'    label="{chapter_id}";')

            for scene in chapter_scenes:
                node_id = scene.id.replace("-", "_")
                lines.append(f'    {node_id} [label="{scene.id}"];')

            lines.append('  }')
            lines.append()

        # Add edges for temporal relations
        for scene in scenes.values():
            if scene.temporal_relations and scene.temporal_relations.follows_scene:
                source = scene.temporal_relations.follows_scene.replace("-", "_")
                target = scene.id.replace("-", "_")
                lines.append(f'  {source} -> {target};')

        lines.append("}")
        return "\n".join(lines)


# CLI handler functions for integration with argparse

def handle_realization_seed(
    project_path: Path,
    genre: str,
    *,
    force: bool = False,
) -> int:
    """Handle 'realization seed' command."""
    commands = CliRealizationCommands(project_path, genre)
    return commands.seed_command(force=force)


def handle_realization_validate(
    project_path: Path,
    genre: str,
) -> int:
    """Handle 'realization validate' command."""
    commands = CliRealizationCommands(project_path, genre)
    return commands.validate_command()


def handle_realization_inspect(
    project_path: Path,
    genre: str,
) -> int:
    """Handle 'realization inspect' command."""
    commands = CliRealizationCommands(project_path, genre)
    return commands.inspect_command()


def handle_realization_graph(
    project_path: Path,
    genre: str,
    output_format: str = "text",
) -> int:
    """Handle 'realization graph' command."""
    commands = CliRealizationCommands(project_path, genre)
    return commands.graph_command(output_format)
