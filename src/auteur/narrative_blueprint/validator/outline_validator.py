"""ContainerValidator for validating hierarchical consistency of outline artifacts.

Ensures consistency across container outlines (BookOutline, ChapterOutline, SequenceOutline).
Validates:
- No chapter exceeds book's chapter_estimate
- All chapter phases are 1-9
- Sequence chapter_range is sensible (start <= end, both > 0)

The validator is lenient: partial specs are valid, missing outlines are OK.
"""

from typing import List, Tuple

from auteur.narrative_blueprint.schema.outline_types import ContainerArtifact
from auteur.narrative_blueprint.schema.book_outline import BookOutline
from auteur.narrative_blueprint.schema.chapter_outline import ChapterOutline
from auteur.narrative_blueprint.schema.sequence_outline import SequenceOutline


class ContainerValidator:
    """Validator for hierarchical consistency of container outlines.

    Validates that nested outlines maintain consistency with their parent containers.
    Supports all genres without special-casing.
    """

    def validate_consistency(
        self, outlines: List[ContainerArtifact]
    ) -> Tuple[bool, List[str]]:
        """Validate consistency across container outlines.

        Args:
            outlines: List of container artifacts to validate

        Returns:
            Tuple of (is_valid: bool, error_messages: List[str])
            - If valid: (True, [])
            - If invalid: (False, ["error1", "error2", ...])
        """
        errors = []

        # Empty list is valid (partial specs OK)
        if not outlines:
            return True, []

        # Filter out None values
        valid_outlines = [o for o in outlines if o is not None]

        if not valid_outlines:
            return True, []

        # Extract book and chapter outlines
        books = [o for o in valid_outlines if isinstance(o, BookOutline)]
        chapters = [o for o in valid_outlines if isinstance(o, ChapterOutline)]
        sequences = [o for o in valid_outlines if isinstance(o, SequenceOutline)]

        # Validate books
        for book in books:
            book_errors = self._validate_book(book)
            errors.extend(book_errors)

        # Validate chapters
        for chapter in chapters:
            chapter_errors = self._validate_chapter(chapter)
            errors.extend(chapter_errors)

        # Validate book-chapter consistency if both exist
        if books and chapters:
            consistency_errors = self._validate_book_chapter_consistency(books, chapters)
            errors.extend(consistency_errors)

        # Validate sequences if present
        if sequences:
            for sequence in sequences:
                sequence_errors = self._validate_sequence(sequence)
                errors.extend(sequence_errors)

        return (True, []) if not errors else (False, errors)

    def _validate_book(self, book: BookOutline) -> List[str]:
        """Validate a single BookOutline.

        Args:
            book: BookOutline to validate

        Returns:
            List of error messages (empty if valid)
        """
        errors = []

        # BookOutline validation - these are already handled in __init__
        # so we mainly check for logical consistency here
        if book.chapter_estimate <= 0:
            errors.append(
                f"Book '{book.title}' has invalid chapter_estimate: {book.chapter_estimate} "
                f"(must be > 0)"
            )

        return errors

    def _validate_chapter(self, chapter: ChapterOutline) -> List[str]:
        """Validate a single ChapterOutline.

        Args:
            chapter: ChapterOutline to validate

        Returns:
            List of error messages (empty if valid)
        """
        errors = []

        # Phase must be 1-9 (already validated in ChapterOutline.__init__)
        if not 1 <= chapter.phase <= 9:
            errors.append(
                f"Chapter {chapter.chapter_number} ('{chapter.title}') has invalid phase: "
                f"{chapter.phase} (must be 1-9)"
            )

        # Chapter number must be positive (already validated in ChapterOutline.__init__)
        if chapter.chapter_number <= 0:
            errors.append(
                f"Chapter has invalid chapter_number: {chapter.chapter_number} (must be > 0)"
            )

        return errors

    def _validate_book_chapter_consistency(
        self, books: List[BookOutline], chapters: List[ChapterOutline]
    ) -> List[str]:
        """Validate consistency between books and chapters.

        Checks that no chapter exceeds its book's chapter_estimate.

        Args:
            books: List of BookOutlines
            chapters: List of ChapterOutlines

        Returns:
            List of error messages (empty if valid)
        """
        errors = []

        # For each book, check that no chapter exceeds its estimate
        for book in books:
            for chapter in chapters:
                if chapter.chapter_number > book.chapter_estimate:
                    errors.append(
                        f"Chapter {chapter.chapter_number} ('{chapter.title}') exceeds "
                        f"book estimate of {book.chapter_estimate} for book '{book.title}'"
                    )

        return errors

    def _validate_sequence(self, sequence: SequenceOutline) -> List[str]:
        """Validate a single SequenceOutline.

        Checks that chapter_range is valid: start > 0, end > 0, start <= end.

        Args:
            sequence: SequenceOutline to validate

        Returns:
            List of error messages (empty if valid)
        """
        errors = []

        start, end = sequence.chapter_range

        # Verify range is sensible
        if start <= 0 or end <= 0:
            errors.append(
                f"Sequence {sequence.sequence_number} has invalid chapter_range ({start}, {end}): "
                f"start and end must be > 0"
            )
        elif start > end:
            errors.append(
                f"Sequence {sequence.sequence_number} has invalid chapter_range ({start}, {end}): "
                f"start must be <= end"
            )

        return errors
