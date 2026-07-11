from __future__ import annotations

from auteur.identity import BestBasis, RecommendationMode, StoryIdentity
from auteur.series.models import BookPlan


def build_book_identity(plan: BookPlan) -> StoryIdentity:
    """Compile one validated BookPlan into the canonical StoryIdentity artifact."""
    identity = StoryIdentity(
        title=plan.title,
        core_answer=plan.core_answer,
        target_experience=plan.target_experience,
        story_type=plan.story_type,
        central_engine=plan.central_engine,
        not_this=[f"Do not resolve the series question outside Book {plan.book_number}."],
        open_questions=[f"Book function: {plan.series_function.value}"],
        recommendation_mode=RecommendationMode.OPINIONATED,
        best_basis=BestBasis.STRUCTURALLY_COHERENT,
        why_this_is_best=f"Built from BookPlan {plan.book_number}.",
        rejected_directions=[],
        author_overrides=[],
    )
    errors = [d for d in identity.validate_identity() if getattr(d.severity, "value", d.severity) == "error"]
    if errors:
        raise ValueError("BookPlan produced an invalid StoryIdentity: " + "; ".join(d.message for d in errors))
    return identity
