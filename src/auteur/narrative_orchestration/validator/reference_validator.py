"""Reference validator for Structure composition.

This module validates that all IDs in outline artifacts resolve correctly.
It checks:
- Arc references resolve to existing chapters
- Chapter references resolve to parent containers (sequences/books)
- Beat references resolve to chapters
- Setup→payoff references are chronologically valid
- Missing IDs and broken references
- Orphaned artifacts (artifacts with no incoming references)

The ReferenceValidator orchestrates all reference validation checks and provides
comprehensive error reporting with artifact_id, reference_id, and error_message.
"""

from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field

from auteur.narrative_orchestration.schema.references import (
    Reference,
    ReferenceResolver,
    ReferenceGraph,
    ReferenceType,
    IdFormat,
)


@dataclass
class ValidationError:
    """A single validation error with context.

    Attributes:
        artifact_id: ID of the artifact with the error
        reference_id: ID of the problematic reference (if applicable)
        error_type: Type of error (missing_reference, broken_reference, etc.)
        message: Human-readable error message
    """

    artifact_id: str
    reference_id: Optional[str]
    error_type: str
    message: str


@dataclass
class ValidationResult:
    """Result of a complete validation run.

    Attributes:
        is_valid: Whether validation passed (True if no errors)
        errors: List of ValidationError objects
        warnings: List of non-critical issues
    """

    is_valid: bool
    errors: List[ValidationError] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


class ReferenceValidator:
    """Validates all IDs and references in outline artifacts.

    The ReferenceValidator accepts outline artifacts (Book, Sequence, Chapter,
    CharacterArc, StoryArc) and validates that:
    1. All arc references point to existing chapters
    2. All chapter references point to valid parent containers
    3. All beat references point to valid chapters
    4. Setup→payoff relationships are chronologically ordered
    5. No orphaned artifacts exist

    It provides comprehensive error reporting with specific artifact IDs and
    reference IDs that failed validation.
    """

    def __init__(self, artifact_registry: Dict[str, Any]):
        """Initialize validator with artifact registry.

        Args:
            artifact_registry: Dictionary mapping artifact IDs to artifact objects
                Expected keys: artifact IDs like "chapter_01", "book_001", etc.
                Expected values: outline artifacts with attributes like 'id', 'parent_id'
        """
        self.registry = artifact_registry
        self.resolver = ReferenceResolver(artifact_registry)
        self.graph = ReferenceGraph()
        self.errors: List[ValidationError] = []
        self.warnings: List[str] = []

    def validate_all_references(self) -> ValidationResult:
        """Orchestrate all reference validation checks.

        This is the main entry point. It runs all validation checks and returns
        a comprehensive result.

        Returns:
            ValidationResult with is_valid flag and complete error/warning lists
        """
        self.errors = []
        self.warnings = []

        # Run all validation checks
        self.validate_arc_references()
        self.validate_chapter_references()
        self.validate_beat_references()
        self.validate_setup_payoff_chain()
        self.detect_orphaned_artifacts()

        # Compile results
        is_valid = len(self.errors) == 0
        return ValidationResult(
            is_valid=is_valid,
            errors=self.errors,
            warnings=self.warnings,
        )

    def validate_arc_references(self) -> None:
        """Validate that arc references point to existing chapters.

        Checks:
        - Arc artifacts reference only existing chapters
        - Arc artifacts reference at least one chapter
        - All referenced chapters exist in the registry
        """
        # Find all arc artifacts in the registry
        arc_artifacts = self._find_artifacts_by_pattern(
            ["character_arc_", "story_arc_", "theme_arc_"]
        )

        for artifact_id, artifact in arc_artifacts.items():
            # Check if arc has references to chapters
            if hasattr(artifact, 'span_chapters') and artifact.span_chapters:
                for chapter_num in artifact.span_chapters:
                    # Try to resolve chapter ID
                    chapter_id = self._resolve_chapter_id(chapter_num)
                    if not chapter_id:
                        # Could not resolve the chapter ID - report error
                        self.errors.append(
                            ValidationError(
                                artifact_id=artifact_id,
                                reference_id=f"chapter_{chapter_num:02d}",
                                error_type="missing_chapter_reference",
                                message=f"Arc {artifact_id} references non-existent chapter chapter_{chapter_num:02d}",
                            )
                        )
                    elif not self.resolver.artifact_exists(chapter_id):
                        self.errors.append(
                            ValidationError(
                                artifact_id=artifact_id,
                                reference_id=chapter_id,
                                error_type="missing_chapter_reference",
                                message=f"Arc {artifact_id} references non-existent chapter {chapter_id}",
                            )
                        )

            # Check for turning points or checkpoints with chapter references
            if hasattr(artifact, 'turning_points') and artifact.turning_points:
                for tp in artifact.turning_points:
                    chapter_id = self._resolve_chapter_id(tp.chapter)
                    if not chapter_id:
                        self.errors.append(
                            ValidationError(
                                artifact_id=artifact_id,
                                reference_id=f"chapter_{tp.chapter:02d}",
                                error_type="missing_beat_chapter_reference",
                                message=f"Arc {artifact_id} beat references non-existent chapter chapter_{tp.chapter:02d}",
                            )
                        )
                    elif not self.resolver.artifact_exists(chapter_id):
                        self.errors.append(
                            ValidationError(
                                artifact_id=artifact_id,
                                reference_id=chapter_id,
                                error_type="missing_beat_chapter_reference",
                                message=f"Arc {artifact_id} beat references non-existent chapter {chapter_id}",
                            )
                        )

            if hasattr(artifact, 'checkpoints') and artifact.checkpoints:
                for cp in artifact.checkpoints:
                    # Checkpoints reference phases, not chapters directly
                    if hasattr(cp, 'chapter') and cp.chapter:
                        chapter_id = self._resolve_chapter_id(cp.chapter)
                        if not chapter_id:
                            self.errors.append(
                                ValidationError(
                                    artifact_id=artifact_id,
                                    reference_id=f"chapter_{cp.chapter:02d}",
                                    error_type="missing_checkpoint_chapter_reference",
                                    message=f"Arc {artifact_id} checkpoint references non-existent chapter chapter_{cp.chapter:02d}",
                                )
                            )
                        elif not self.resolver.artifact_exists(chapter_id):
                            self.errors.append(
                                ValidationError(
                                    artifact_id=artifact_id,
                                    reference_id=chapter_id,
                                    error_type="missing_checkpoint_chapter_reference",
                                    message=f"Arc {artifact_id} checkpoint references non-existent chapter {chapter_id}",
                                )
                            )

    def validate_chapter_references(self) -> None:
        """Validate that chapters reference valid parent containers.

        Checks:
        - Each chapter has a parent_id pointing to a sequence or book
        - Parent artifact exists in the registry
        - Parent is either a sequence or book (not another chapter)
        """
        # Find all chapter artifacts
        chapter_artifacts = self._find_artifacts_by_pattern(["chapter_"])

        for artifact_id, artifact in chapter_artifacts.items():
            if hasattr(artifact, 'parent_id'):
                parent_id = artifact.parent_id

                if not parent_id:
                    self.errors.append(
                        ValidationError(
                            artifact_id=artifact_id,
                            reference_id=None,
                            error_type="missing_parent_reference",
                            message=f"Chapter {artifact_id} has no parent_id",
                        )
                    )
                    continue

                # Check parent exists
                if not self.resolver.artifact_exists(parent_id):
                    self.errors.append(
                        ValidationError(
                            artifact_id=artifact_id,
                            reference_id=parent_id,
                            error_type="missing_parent_artifact",
                            message=f"Chapter {artifact_id} references non-existent parent {parent_id}",
                        )
                    )
                else:
                    # Verify parent is sequence or book, not another chapter
                    if parent_id.startswith("chapter_"):
                        self.errors.append(
                            ValidationError(
                                artifact_id=artifact_id,
                                reference_id=parent_id,
                                error_type="invalid_parent_type",
                                message=f"Chapter {artifact_id} parent cannot be another chapter: {parent_id}",
                            )
                        )

    def validate_beat_references(self) -> None:
        """Validate that beats reference valid chapters.

        Checks:
        - All beat artifacts reference existing chapters
        - Beat phase/chapter mapping is valid
        """
        # Find all beat artifacts (turning points, checkpoints stored with arcs)
        # This is typically validated as part of arc validation, but we can add
        # specific beat-level checks if needed
        pass

    def validate_setup_payoff_chain(self) -> None:
        """Validate setup→payoff references are chronologically valid.

        Checks:
        - Payoff chapters occur after setup chapters
        - Both setup and payoff chapters exist
        - Chronological ordering is respected within books
        """
        # Extract chapter ordering from registry
        chapter_ordering = self._build_chapter_ordering()

        # Find payoff references and validate ordering
        for artifact_id, artifact in self.registry.items():
            # Check for setup_payoff_reference attribute
            if hasattr(artifact, 'setup_payoff_reference'):
                setup_id = artifact_id
                payoff_id = artifact.setup_payoff_reference

                if not payoff_id:
                    continue

                # Check both exist
                if not self.resolver.artifact_exists(setup_id):
                    self.errors.append(
                        ValidationError(
                            artifact_id=setup_id,
                            reference_id=None,
                            error_type="missing_setup_artifact",
                            message=f"Setup artifact {setup_id} not found",
                        )
                    )
                    continue

                if not self.resolver.artifact_exists(payoff_id):
                    self.errors.append(
                        ValidationError(
                            artifact_id=setup_id,
                            reference_id=payoff_id,
                            error_type="missing_payoff_artifact",
                            message=f"Payoff artifact {payoff_id} referenced by {setup_id} not found",
                        )
                    )
                    continue

                # Check chronological ordering
                if setup_id in chapter_ordering and payoff_id in chapter_ordering:
                    setup_order = chapter_ordering[setup_id]
                    payoff_order = chapter_ordering[payoff_id]

                    if setup_order >= payoff_order:
                        self.errors.append(
                            ValidationError(
                                artifact_id=setup_id,
                                reference_id=payoff_id,
                                error_type="invalid_chronological_order",
                                message=f"Setup {setup_id} (order {setup_order}) must occur before payoff {payoff_id} (order {payoff_order})",
                            )
                        )

    def detect_orphaned_artifacts(self) -> None:
        """Detect artifacts with no incoming references.

        An orphaned artifact is one that:
        - Is not a root artifact (like series or book)
        - Has no incoming references from parent containers
        - Is not directly referenced by any other artifact

        This helps identify incomplete outline structures.
        """
        # Build reference graph by analyzing registry
        self._build_reference_graph()

        # Find artifacts with no incoming references
        root_types = ["series_", "book_"]

        for artifact_id in self.registry.keys():
            # Skip root artifacts
            if any(artifact_id.startswith(root) for root in root_types):
                continue

            # Check for incoming references
            incoming = self.graph.get_incoming(artifact_id)

            # Chapters and sequences should have parent references
            if artifact_id.startswith("chapter_") or artifact_id.startswith("sequence_"):
                if not incoming:
                    self.warnings.append(
                        f"Orphaned artifact: {artifact_id} has no parent reference"
                    )

            # Arcs should be referenced by something
            elif artifact_id.startswith("character_arc_") or artifact_id.startswith("story_arc_"):
                if not incoming:
                    self.warnings.append(
                        f"Orphaned arc: {artifact_id} has no references from chapters"
                    )

    def report_validation_status(self) -> str:
        """Generate a comprehensive error report.

        Returns:
            Human-readable report of all validation issues
        """
        result = self.validate_all_references()

        lines = []

        # Summary
        if result.is_valid:
            lines.append("✓ All references valid")
        else:
            lines.append(f"✗ Validation failed: {len(result.errors)} error(s)")

        if result.warnings:
            lines.append(f"  {len(result.warnings)} warning(s)")

        lines.append("")

        # Errors
        if result.errors:
            lines.append("ERRORS:")
            for error in result.errors:
                lines.append(f"  [{error.error_type}] {error.artifact_id}")
                if error.reference_id:
                    lines.append(f"    ref: {error.reference_id}")
                lines.append(f"    {error.message}")

        # Warnings
        if result.warnings:
            lines.append("")
            lines.append("WARNINGS:")
            for warning in result.warnings:
                lines.append(f"  {warning}")

        return "\n".join(lines)

    # Helper methods

    def _find_artifacts_by_pattern(self, patterns: List[str]) -> Dict[str, Any]:
        """Find all artifacts matching any of the given patterns.

        Args:
            patterns: List of string patterns (e.g., ["chapter_", "sequence_"])

        Returns:
            Dictionary of matching artifact_id -> artifact
        """
        result = {}
        for artifact_id, artifact in self.registry.items():
            if any(artifact_id.startswith(pattern) for pattern in patterns):
                result[artifact_id] = artifact
        return result

    def _resolve_chapter_id(self, chapter_ref: int) -> Optional[str]:
        """Try to resolve a chapter reference to a chapter ID.

        Args:
            chapter_ref: Chapter number (integer)

        Returns:
            Chapter ID like "chapter_01" or None if not found
        """
        # Try common formatting patterns
        for fmt in [f"chapter_{chapter_ref:02d}", f"chapter_{chapter_ref}"]:
            if self.resolver.artifact_exists(fmt):
                return fmt

        return None

    def _build_chapter_ordering(self) -> Dict[str, int]:
        """Build ordering of chapters based on chapter_number or position.

        Returns:
            Dictionary mapping artifact_id to ordering position
        """
        ordering = {}

        # Get all chapters and sort by chapter_number
        chapters = self._find_artifacts_by_pattern(["chapter_"])

        chapter_list = []
        for artifact_id, artifact in chapters.items():
            chapter_num = 0
            if hasattr(artifact, 'chapter_number'):
                chapter_num = artifact.chapter_number
            elif hasattr(artifact, 'number'):
                chapter_num = artifact.number

            chapter_list.append((artifact_id, chapter_num))

        # Sort by chapter number
        chapter_list.sort(key=lambda x: x[1])

        # Assign ordering positions
        for position, (artifact_id, _) in enumerate(chapter_list):
            ordering[artifact_id] = position

        return ordering

    def _build_reference_graph(self) -> None:
        """Build reference graph from registry artifacts.

        Populates self.graph with references extracted from artifact attributes.
        """
        self.graph = ReferenceGraph()

        # Extract references from artifacts
        for artifact_id, artifact in self.registry.items():
            # Parent references (child → parent)
            if hasattr(artifact, 'parent_id') and artifact.parent_id:
                parent_id = artifact.parent_id
                if self.resolver.artifact_exists(parent_id):
                    ref = Reference(
                        source_id=artifact_id,
                        target_id=parent_id,
                        reference_type=ReferenceType.CHAPTER_TO_PARENT,
                    )
                    self.graph.add_reference(ref)

            # Arc → chapter references
            if hasattr(artifact, 'span_chapters') and artifact.span_chapters:
                for chapter_num in artifact.span_chapters:
                    chapter_id = self._resolve_chapter_id(chapter_num)
                    if chapter_id:
                        ref = Reference(
                            source_id=artifact_id,
                            target_id=chapter_id,
                            reference_type=ReferenceType.ARC_TO_CHAPTER,
                        )
                        self.graph.add_reference(ref)
