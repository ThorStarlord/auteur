"""Side-effect-free, deterministic tutor guidance derived from pack context."""
from __future__ import annotations

from .composition import compose_packs
from .models import DecisionCard, DecisionSourceBinding, TutorDiagnosticGuidance, TutorGuidance, source_fingerprint


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


def decision_card_from_guidance(
    guidance: TutorGuidance,
    *,
    source_subject: str = "story_design_context",
) -> DecisionCard:
    """Convert guidance into a derived card without mutating its source."""
    binding = DecisionSourceBinding(
        source_artifact="story_design_context",
        source_subject=source_subject,
        source_fingerprint=source_fingerprint(guidance.model_dump(mode="json")),
    )
    return DecisionCard(
        decision=guidance.decision,
        orientation=guidance.orientation,
        why_it_matters=guidance.why_recommended,
        craft_concept=guidance.craft_concept,
        recommendation=guidance.recommendation,
        alternatives=guidance.alternatives,
        tradeoffs=guidance.tradeoffs,
        beginner_trap=guidance.common_beginner_mistake,
        downstream_consequences=[guidance.consequence],
        evidence=guidance.architecture_evidence,
        pack_sources=guidance.pack_sources,
        source_binding=binding,
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


def decision_card_from_diagnostic(
    diagnostic: object,
    *,
    story_context: str = "this story",
) -> DecisionCard:
    """Convert one deterministic diagnostic into a non-canonical card."""
    if isinstance(diagnostic, dict):
        rule = str(diagnostic.get("rule", "unknown"))
        message = str(diagnostic.get("message", "A structural issue was detected."))
        repair = [str(item) for item in diagnostic.get("recommendations", [])]
        repair.extend(str(item) for item in diagnostic.get("hypotheses", []))
        raw_evidence = diagnostic.get("evidence", [])
        if isinstance(raw_evidence, dict):
            evidence = [f"{key}={value}" for key, value in sorted(raw_evidence.items())]
        else:
            evidence = [str(item) for item in raw_evidence]
        source = diagnostic
    else:
        rule = str(getattr(diagnostic, "rule", "unknown"))
        message = str(getattr(diagnostic, "message", "A structural issue was detected."))
        repair_options = getattr(diagnostic, "repair_options", None)
        repair = [
            str(item) for item in getattr(repair_options, "preserve_intent", [])
        ] + [
            str(item) for item in getattr(repair_options, "challenge_intent", [])
        ]
        evidence = [str(item) for item in getattr(diagnostic, "evidence", [])]
        source = diagnostic.model_dump(mode="json") if hasattr(diagnostic, "model_dump") else vars(diagnostic)

    if not repair:
        repair = ["Inspect the finding before changing the story."]
    return DecisionCard(
        decision="Resolve or intentionally preserve the finding",
        orientation=f"A finding needs an author decision in {story_context}.",
        why_it_matters=message,
        craft_concept="Narrative consequence",
        recommendation=repair[0],
        alternatives=repair,
        tradeoffs=[
            "Repairing the finding may require changing a later commitment.",
            "Keeping it preserves ambiguity but should be intentional.",
        ],
        beginner_trap="Treating a diagnostic as an automatic rewrite instruction.",
        downstream_consequences=["Any selected repair remains a proposal until explicitly accepted."],
        evidence=evidence or [rule, message],
        source_rule=rule,
        source_binding=DecisionSourceBinding(
            source_artifact="structure_diagnostic",
            source_subject=story_context,
            source_fingerprint=source_fingerprint(source),
        ),
    )
