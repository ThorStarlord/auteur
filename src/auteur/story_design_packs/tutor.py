"""Side-effect-free, deterministic tutor guidance derived from pack context."""
from __future__ import annotations

from .composition import compose_packs
from .models import DecisionCard, TutorDiagnosticGuidance, TutorGuidance


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


def decision_card_from_guidance(
    guidance: TutorGuidance,
    *,
    source_subject: str = "story_design_context",
) -> DecisionCard:
    """Convert existing Tutor guidance into a derived author-facing card."""
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
        evidence=list(guidance.architecture_evidence),
        pack_sources=guidance.pack_sources,
    )


def decision_card_from_diagnostic(
    diagnostic: object,
    *,
    story_context: str = "this story",
    evidence: list[str] | None = None,
) -> DecisionCard:
    """Convert one deterministic diagnostic into a non-canonical card."""
    if isinstance(diagnostic, dict):
        rule = diagnostic.get("rule", "unknown")
        message = diagnostic.get("message", "A structural issue was detected.")
        repair = diagnostic.get("recommendations", [])
        challenge = diagnostic.get("hypotheses", [])
        diagnostic_evidence = diagnostic.get("evidence", {})
        structured_evidence = [
            f"{key}={value}" for key, value in sorted(diagnostic_evidence.items())
        ] if isinstance(diagnostic_evidence, dict) else [str(diagnostic_evidence)]
    else:
        rule = getattr(diagnostic, "rule", "unknown")
        message = getattr(diagnostic, "message", "A structural issue was detected.")
        repair = getattr(getattr(diagnostic, "repair_options", None), "preserve_intent", [])
        challenge = getattr(getattr(diagnostic, "repair_options", None), "challenge_intent", [])
        structured_evidence = []
    return DecisionCard.from_diagnostic(
        rule=str(rule),
        message=str(message),
        story_context=story_context,
        repair_options=[*repair, *challenge],
        evidence=evidence or structured_evidence,
    )


def decision_card_from_reasoning_report(report: object) -> DecisionCard:
    """Render a reasoning report as a card without crossing authority boundaries."""
    if isinstance(report, dict):
        subject = str(report.get("subject", "this story"))
        claim = str(report.get("claim", "A narrative finding requires review."))
        recommendations = [str(item) for item in report.get("recommendations", [])]
        evidence = [str(item.get("source_artifact", item)) if isinstance(item, dict) else str(item) for item in report.get("evidence", [])]
        rule = str(report.get("reasoning_id", "reasoning"))
    else:
        subject = str(getattr(report, "subject", "this story"))
        claim = str(getattr(report, "claim", "A narrative finding requires review."))
        recommendations = [str(item) for item in getattr(report, "recommendations", [])]
        evidence = [str(item.source_artifact) for item in getattr(report, "evidence", [])]
        rule = str(getattr(report, "reasoning_id", "reasoning"))
    return DecisionCard.from_diagnostic(
        rule=rule,
        message=claim,
        story_context=subject,
        repair_options=recommendations or ["Inspect the evidence and decide whether to intervene."],
        evidence=evidence,
    )
