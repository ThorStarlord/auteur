"""Side-effect-free, deterministic tutor guidance derived from pack context."""
from __future__ import annotations

from .composition import compose_packs
from .models import TutorGuidance


def tutor_recommend(
    pack_ids: list[str],
    *,
    decision: str = "next creative decision",
    premise: str = "your story",
) -> TutorGuidance:
    composition = compose_packs(pack_ids)
    hooks = [h for h in composition.decision_suggestions if decision.lower() in h.decision.lower()]
    hook = (hooks or composition.decision_suggestions)[0] if composition.decision_suggestions else None
    option = next(
        (o for o in composition.applicable_design_priors if hook and o.option_id == hook.recommended_option_id),
        composition.applicable_design_priors[0],
    )
    alternatives = [o.name for o in composition.applicable_design_priors if o.option_id != option.option_id][:3]
    tradeoffs = list(option.tradeoffs)
    when_stronger = [f"{name} would be stronger if it better serves a different pressure in {premise}." for name in alternatives]
    concept = composition.selected_packs[0].pack_id.replace("_", " ").title()
    return TutorGuidance(
        decision=decision,
        orientation=f"We're deciding {decision} in {premise}.",
        craft_concept=concept,
        plain_language_explanation=option.what_it_is,
        story_application=f"In {premise}, this choice would create the following pressure: {option.craft_function}",
        recommendation=option.name,
        why_recommended=f"Auteur recommends it because {option.works_well_when}",
        alternatives=alternatives,
        tradeoffs=tradeoffs,
        when_alternative_is_stronger=when_stronger,
        common_beginner_mistake=option.common_beginner_failure or "Treating a design choice as decoration instead of pressure.",
        pack_sources=composition.pack_provenance,
        architecture_evidence=option.architecture_targets,
        consequence=f"Choosing this should make {option.craft_function.lower()}",
        question_for_author=hook.question if hook else (option.questions[0] if option.questions else "What consequence should this choice create?"),
        comprehension_check=f"In your own words, what pressure does {option.name} create?",
    )
