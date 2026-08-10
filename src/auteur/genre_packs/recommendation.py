"""Opinionated Genre Pack Recommendation Engine.

Analyzes premise or story inputs and generates a candidate GenreRecommendation.
Zero mutation occurs prior to explicit author acceptance.
"""

import json
import uuid
from pathlib import Path
from datetime import datetime, timezone
from typing import Any
from auteur.genre_packs.models import (
    GenreRecommendation,
    RejectedProfileAnalysis,
    FramingCommitment,
    ResolutionContractCommitment,
    GenreErrorCode,
    GenrePackError,
    PackApplicabilityStatus,
    PackApplicabilityEvaluation,
    GenreRecommendationAdvisory,
)
from auteur.genre_packs.registry import get_pack_registry

import os

_PENDING_RECOMMENDATIONS: dict[str, GenreRecommendation] = {}


def _atomic_write_json(file_path: Path, data: dict[str, Any]) -> None:
    """Write dictionary to file atomically using a temporary file and os.replace."""
    file_path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = file_path.with_name(f".tmp_{file_path.name}_{uuid.uuid4().hex}")
    try:
        temp_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
        os.replace(temp_path, file_path)
    finally:
        if temp_path.exists():
            try:
                temp_path.unlink()
            except OSError:
                pass


def save_recommendation(rec: GenreRecommendation, project_dir: Path | str | None = None) -> Path:
    """Persist recommendation to disk atomically for process-restart durability.

    When project_dir is provided, recommendation content is stored strictly project-local
    (.auteur/genre_recommendations/) to preserve privacy and single-authority boundaries.
    """
    _PENDING_RECOMMENDATIONS[rec.recommendation_id] = rec

    if project_dir:
        p_resolved = str(Path(project_dir).resolve())
        rec.context = rec.context or {}
        rec.context["_project_dir"] = p_resolved

    data = rec.model_dump(mode="json")

    if project_dir:
        target = Path(project_dir) / ".auteur" / "genre_recommendations" / f"{rec.recommendation_id}.json"
        _atomic_write_json(target, data)
        return target

    home_target = Path.home() / ".auteur" / "genre_recommendations" / f"{rec.recommendation_id}.json"
    _atomic_write_json(home_target, data)
    return home_target


def load_recommendation(rec_id: str, project_dir: Path | str | None = None) -> GenreRecommendation:
    """Retrieve recommendation by ID from memory cache or project-local disk persistence.

    When project_dir is provided, project-local storage (.auteur/genre_recommendations/)
    is strictly authoritative. No silent global fallback is performed.
    """
    if project_dir:
        p_res = str(Path(project_dir).resolve())
        if rec_id in _PENDING_RECOMMENDATIONS:
            cached_rec = _PENDING_RECOMMENDATIONS[rec_id]
            cached_p = cached_rec.context.get("_project_dir") if cached_rec.context else None
            if cached_p == p_res:
                return cached_rec
            else:
                _PENDING_RECOMMENDATIONS.pop(rec_id, None)

        proj_file = Path(project_dir) / ".auteur" / "genre_recommendations" / f"{rec_id}.json"
        if not proj_file.exists():
            raise GenrePackError(GenreErrorCode.RECOMMENDATION_NOT_FOUND, f"Recommendation ID '{rec_id}' not found in project '{project_dir}'.")

        try:
            data = json.loads(proj_file.read_text(encoding="utf-8"))
            rec = GenreRecommendation.model_validate(data)
        except Exception as err:
            raise GenrePackError(GenreErrorCode.RECOMMENDATION_NOT_FOUND, f"Corrupt recommendation artifact at '{proj_file}': {err}")

        rec.context = rec.context or {}
        rec.context["_project_dir"] = p_res
        _PENDING_RECOMMENDATIONS[rec_id] = rec
        return rec

    # Global lookup (when project_dir is None)
    if rec_id in _PENDING_RECOMMENDATIONS:
        cached_rec = _PENDING_RECOMMENDATIONS[rec_id]
        if not cached_rec.context or not cached_rec.context.get("_project_dir"):
            return cached_rec

    home_file = Path.home() / ".auteur" / "genre_recommendations" / f"{rec_id}.json"
    if home_file.exists():
        try:
            data = json.loads(home_file.read_text(encoding="utf-8"))
            rec = GenreRecommendation.model_validate(data)
        except Exception as err:
            raise GenrePackError(GenreErrorCode.RECOMMENDATION_NOT_FOUND, f"Corrupt global recommendation artifact at '{home_file}': {err}")

        if rec.context and rec.context.get("_project_dir"):
            raise GenrePackError(GenreErrorCode.RECOMMENDATION_NOT_FOUND, f"Recommendation ID '{rec_id}' belongs to project '{rec.context['_project_dir']}'. Pass --project to access.")

        _PENDING_RECOMMENDATIONS[rec_id] = rec
        return rec

    raise GenrePackError(GenreErrorCode.RECOMMENDATION_NOT_FOUND, f"Recommendation ID '{rec_id}' not found.")


def evaluate_pack_applicability(
    premise_text: str,
    pack_id: str = "erotic_fiction",
    version: str = "0.1.0",
) -> PackApplicabilityEvaluation:
    """Evaluate whether a Genre Pack is applicable to the raw premise text."""
    premise_lower = premise_text.casefold()

    if pack_id == "erotic_fiction":
        domain_signals = [
            "desire", "intimacy", "erotic", "passion", "sexual", "romantic attraction",
            "sensual", "affair", "lover", "relationship boundary", "longing", "attraction",
            "temptation", "surrender", "lust", "seduction", "physical attraction",
            "obsession", "romance", "romantic", "intimate", "identity facades",
        ]

        global_negations = [
            "not an erotic", "not erotic", "no erotic", "non-erotic", "not a romance",
            "no romance", "not romance", "not romantic", "attraction is not part",
            "attraction is not a part", "contains no erotic", "has no erotic",
            "without any erotic", "platonic only", "strictly professional", "never erotic",
            "is not part of the story", "not part of the plot",
            "studies erotic", "analyzes erotic", "analyzing erotic", "catalogs romance",
            "critic analyzes erotic", "scholar studies erotic",
        ]

        local_negated_cues = [
            "rejects desire", "avoids all intimacy", "no intimacy", "avoids desire",
            "never attracted", "feels no attraction", "no sexual", "rejects all desire",
            "avoids intimacy", "rejects intimacy",
        ]

        matched = [sig for sig in domain_signals if sig in premise_lower]
        matched_global_negations = [g for g in global_negations if g in premise_lower]
        matched_local_negations = [c for c in local_negated_cues if c in premise_lower]
        negated = list(dict.fromkeys(matched_global_negations + matched_local_negations))

        # Filter out domain signals that appear inside any negation phrase (global or local)
        effective_matched = []
        for sig in matched:
            inside_negation = any(sig in phrase for phrase in negated)
            if not inside_negation:
                effective_matched.append(sig)

        if matched_global_negations and len(effective_matched) < 2:
            score = 0.05
            status = PackApplicabilityStatus.NOT_APPLICABLE
            explanation = f"Premise explicitly negates or frames out domain '{pack_id}'."
        elif negated and len(effective_matched) == 0:
            score = 0.05
            status = PackApplicabilityStatus.NOT_APPLICABLE
            explanation = f"Premise lacks un-negated core domain signals for pack '{pack_id}'."
        elif len(effective_matched) == 0:
            score = 0.05
            status = PackApplicabilityStatus.NOT_APPLICABLE
            explanation = f"Premise lacks core domain signals for pack '{pack_id}'."
        elif len(effective_matched) == 1:
            score = 0.40
            status = PackApplicabilityStatus.APPLICABLE
            explanation = f"Premise contains initial domain signal '{effective_matched[0]}'."
        else:
            score = min(0.95, 0.50 + len(effective_matched) * 0.15)
            status = PackApplicabilityStatus.APPLICABLE
            explanation = f"Premise strongly aligns with domain signals ({', '.join(effective_matched[:3])})."

        return PackApplicabilityEvaluation(
            pack_id=pack_id,
            version=version,
            status=status,
            applicability_score=round(score, 2),
            matched_signals=effective_matched,
            missing_signals=[s for s in domain_signals if s not in effective_matched][:5],
            negated_signals=negated,
            explanation=explanation,
        )

    return PackApplicabilityEvaluation(
        pack_id=pack_id,
        version=version,
        status=PackApplicabilityStatus.INSUFFICIENT_EVIDENCE,
        applicability_score=0.0,
        explanation=f"Pack '{pack_id}' evaluation rule set is unconfigured.",
    )


def recommend_genre_profile(
    premise_text: str,
    pack_id: str = "erotic_fiction",
    version: str = "0.1.0",
    context: dict[str, Any] | None = None,
) -> GenreRecommendation | GenreRecommendationAdvisory:
    """Analyze premise and return an opinionated GenreRecommendation or an abstention advisory.

    This function is strictly read-only and causes zero pre-acceptance state mutation.
    """
    applicability = evaluate_pack_applicability(premise_text, pack_id=pack_id, version=version)
    if applicability.status != PackApplicabilityStatus.APPLICABLE:
        return GenreRecommendationAdvisory(
            status="no_applicable_pack",
            message=(
                f"No installed Genre Pack is a strong fit for this premise. "
                f"Evaluated pack '{pack_id}' status: {applicability.status.value} (score: {applicability.applicability_score})."
            ),
            evaluated_packs=[applicability],
            recommended_next_actions=[
                "Run 'auteur story-discovery' to explore open-ended interpretations",
                "Use 'auteur identity init' to create an author-editable StoryIdentity skeleton",
                "Manually specify your desired genre when creating story identity",
            ],
            mutated_state=False,
        )

    registry = get_pack_registry()
    pack, content_hash = registry.get_pack(pack_id, version)

    premise_lower = premise_text.casefold()

    # Keyword / tone scoring heuristics for deterministic evaluation
    horror_signals = ["dread", "horror", "monster", "terrifying", "fear", "haunted", "corrupt", "darkness", "decay", "nightmare"]
    psycho_signals = ["identity", "psychological", "ambivalence", "obsession", "secret", "power", "transgression", "control", "facade", "mind"]
    romance_signals = ["love", "romance", "trust", "affection", "together", "heart", "forever", "devotion", "bond", "partner"]

    horror_score = sum(1 for w in horror_signals if w in premise_lower)
    psycho_score = sum(1 for w in psycho_signals if w in premise_lower)
    romance_score = sum(1 for w in romance_signals if w in premise_lower)

    # Determine recommended profile
    if horror_score > psycho_score and horror_score > romance_score:
        recommended_profile_id = "erotic_horror"
    elif psycho_score >= horror_score and psycho_score >= romance_score:
        recommended_profile_id = "erotic_psychological_drama"
    else:
        recommended_profile_id = "erotic_romance"

    rec_profile = registry.get_profile(pack_id, recommended_profile_id, version)

    # Build evidence and rationale
    evidence: list[str] = []
    for word in (horror_signals if recommended_profile_id == "erotic_horror" else psycho_signals if recommended_profile_id == "erotic_psychological_drama" else romance_signals):
        if word in premise_lower:
            evidence.append(f"Premise emphasizes '{word}'")

    if not evidence:
        evidence.append("Premise focuses on psychological transformation and internal conflict.")

    why_this_is_best = (
        f"The premise aligns strongest with {rec_profile.display_name}. "
        f"Key elements highlight {', '.join(rec_profile.primary_emotions[:3])}."
    )

    # Build rejected profiles analysis
    rejected_profiles: list[RejectedProfileAnalysis] = []
    for p in pack.subgenre_profiles:
        if p.profile_id != recommended_profile_id:
            if p.profile_id == "erotic_romance":
                why = "The premise emphasizes tension, identity ambivalence, or dark stakes over comforting relational fulfillment."
                adj = "Emphasize mutual affection, emotional trust, and a commitment to relational harmony."
            elif p.profile_id == "erotic_horror":
                why = "The premise focuses on personal transformation or relational conflict rather than dread and destabilizing horror."
                adj = "Introduce elements of dread, bodily/supernatural threat, or terrifying surrender."
            else:
                why = "The premise lacks explicit focus on psychological ambivalence and identity facade breakdown."
                adj = "Heighten internal identity conflict, compulsion, and psychological secrecy."

            rejected_profiles.append(
                RejectedProfileAnalysis(
                    profile_id=p.profile_id,
                    display_name=p.display_name,
                    why_rejected=why,
                    premise_adjustment_to_enable=adj,
                )
            )

    # Determine recommended commitments
    emotional_weights = {
        emo: 1.0 if idx == 0 else 0.8 if idx == 1 else 0.7
        for idx, emo in enumerate(rec_profile.primary_emotions)
    }

    narrative_engine = (
        rec_profile.preferred_narrative_engines[0]
        if rec_profile.preferred_narrative_engines
        else "erotic_identity_transformation"
    )

    framing = FramingCommitment(
        primary=rec_profile.preferred_framing,
        secondary=["heroic"] if recommended_profile_id == "erotic_romance" else ["unsettling"]
    )

    res_pattern = (
        "relational_fulfillment"
        if recommended_profile_id == "erotic_romance"
        else "dark_transgression_resolution"
        if recommended_profile_id == "erotic_horror"
        else "transformative_resolution"
    )

    resolution_contract = ResolutionContractCommitment(
        pattern=res_pattern,
        required_outcomes=rec_profile.resolution_expectations,
        rejected_outcomes=rec_profile.boundary_warnings,
    )

    rec_id = f"rec_{uuid.uuid4().hex[:12]}"
    created_at = datetime.now(timezone.utc).isoformat()

    return GenreRecommendation(
        recommendation_id=rec_id,
        recommended_pack_id=pack_id,
        recommended_pack_version=version,
        pack_content_hash=content_hash,
        recommended_profile_id=recommended_profile_id,
        recommended_profile_display_name=rec_profile.display_name,
        confidence=0.88,
        best_basis="GENRE_ALIGNED",
        why_this_is_best=why_this_is_best,
        supporting_evidence=evidence,
        recommended_emotional_targets=emotional_weights,
        recommended_narrative_engine=narrative_engine,
        recommended_framing=framing,
        recommended_resolution_contract=resolution_contract,
        rejected_profiles=rejected_profiles,
        warnings=[],
        questions_or_uncertainties=["Confirm whether secondary subgenre elements should be preserved."],
        created_at=created_at,
    )
