from __future__ import annotations

from pathlib import Path

from auteur.identity import BestBasis, RecommendationMode, StoryIdentity
from auteur.series.models import SeriesIdentity


def compile_book_identities(series: SeriesIdentity) -> list[StoryIdentity]:
    identities: list[StoryIdentity] = []
    for book in series.book_plans:
        identity = StoryIdentity(
            title=book.title,
            core_answer=book.core_answer,
            target_experience=book.target_experience,
            story_type=book.story_type,
            central_engine=book.central_engine,
            not_this=[f"Do not resolve the full series question outside Book {book.book_number}."],
            open_questions=[
                f"Series question: {series.core_question}",
                f"Book function: {book.series_function}",
            ],
            recommendation_mode=RecommendationMode.OPINIONATED,
            best_basis=BestBasis.STRUCTURALLY_COHERENT,
            why_this_is_best=f"Compiled from {series.title} Book {book.book_number}.",
            rejected_directions=[],
            author_overrides=[],
        )
        diagnostics = identity.validate_identity()
        errors = [d for d in diagnostics if getattr(d.severity, "value", d.severity) == "error"]
        if errors:
            messages = "; ".join(str(d.message) for d in errors)
            raise ValueError(f"Compiled Book {book.book_number} StoryIdentity is invalid: {messages}")
        identities.append(identity)
    return identities


def write_book_identities(series: SeriesIdentity, output_dir: Path) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for book, identity in zip(series.book_plans, compile_book_identities(series)):
        book_dir = output_dir / f"book_{book.book_number:02d}"
        book_dir.mkdir(parents=True, exist_ok=True)
        path = book_dir / "story_identity.yaml"
        identity.to_yaml(path)
        written.append(path)
    return written
