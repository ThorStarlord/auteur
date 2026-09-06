"""Side-effect-free, deterministic tutor guidance derived from pack context."""
from __future__ import annotations

from .composition import compose_packs
from .models import TutorDiagnosticGuidance, TutorGuidance


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
    tradeoffs.extend(composition.productive_tensions[:2])
    tradeoffs.extend(composition.actual_conflicts[:2])
    when_stronger = [f"{name} would be stronger if it better serves a different pressure in {premise}." for name in alternatives]
    concept = composition.selected_packs[0].pack_id.replace("_", " ").title()
    return TutorGuidance(
        decision=decision,
        orientation=f"We're deciding {decision} in {premise}.",
        craft_concept=concept,
        plain_language_explanation=option.what_it_is,
        story_application=f"In {premise}, this choice would create the following pressure: {option.craft_function}"
        + (f" The selected packs also create this interaction: {composition.reinforcing_patterns[0]}" if composition.reinforcing_patterns else ""),
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


def tutorize_diagnostic(diagnostic: object, *, story_context: str = "this story") -> TutorDiagnosticGuidance:
    """Translate one deterministic diagnostic without changing or applying it."""
    rule = getattr(diagnostic, "rule", "unknown")
    message = getattr(diagnostic, "message", "A structural issue was detected.")
    repair = getattr(getattr(diagnostic, "repair_options", None), "preserve_intent", [])
    challenge = getattr(getattr(diagnostic, "repair_options", None), "challenge_intent", [])
    options = [*repair, *challenge]
    return TutorDiagnosticGuidance(
        diagnostic_rule=rule,
        what_seems_wrong=message,
        craft_principle="A prominent setup creates an audience expectation that should be resolved, transformed, or deliberately carried forward.",
        why_it_matters_in_this_story=f"The finding affects the promises and consequences the author has established in {story_context}.",
        repair_options=options,
        tradeoffs=["Resolving the issue may require changing a later commitment.", "Keeping it unresolved preserves ambiguity but should be intentional."],
        next_author_decision="Choose a repair, preserve the tension deliberately, or explicitly challenge the finding.",
    )
