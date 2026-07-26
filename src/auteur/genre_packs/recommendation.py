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
)
from auteur.genre_packs.registry import get_pack_registry

_PENDING_RECOMMENDATIONS: dict[str, GenreRecommendation] = {}


def save_recommendation(rec: GenreRecommendation, project_dir: Path | str | None = None) -> Path:
    """Persist recommendation to disk for process-restart durability."""
    _PENDING_RECOMMENDATIONS[rec.recommendation_id] = rec
    
    saved_path = None
    paths_to_write = []
    
    if project_dir:
        p_dir = Path(project_dir) / ".auteur" / "genre_recommendations"
        p_dir.mkdir(parents=True, exist_ok=True)
        paths_to_write.append(p_dir / f"{rec.recommendation_id}.json")

    home_dir = Path.home() / ".auteur" / "genre_recommendations"
    home_dir.mkdir(parents=True, exist_ok=True)
    paths_to_write.append(home_dir / f"{rec.recommendation_id}.json")

    for target_file in paths_to_write:
        target_file.write_text(json.dumps(rec.model_dump(mode="json"), indent=2), encoding="utf-8")
        if not saved_path:
            saved_path = target_file
            
    return saved_path or (home_dir / f"{rec.recommendation_id}.json")


def load_recommendation(rec_id: str, project_dir: Path | str | None = None) -> GenreRecommendation:
    """Retrieve recommendation by ID from memory cache or disk persistence."""
    if rec_id in _PENDING_RECOMMENDATIONS:
        return _PENDING_RECOMMENDATIONS[rec_id]

    paths_to_check = []
    if project_dir:
        paths_to_check.append(Path(project_dir) / ".auteur" / "genre_recommendations" / f"{rec_id}.json")

    paths_to_check.append(Path.home() / ".auteur" / "genre_recommendations" / f"{rec_id}.json")

    for target_file in paths_to_check:
        if target_file.exists():
            data = json.loads(target_file.read_text(encoding="utf-8"))
            rec = GenreRecommendation.model_validate(data)
            _PENDING_RECOMMENDATIONS[rec_id] = rec
            return rec

    raise GenrePackError(GenreErrorCode.RECOMMENDATION_NOT_FOUND, f"Recommendation ID '{rec_id}' not found.")


def recommend_genre_profile(
    premise_text: str,
    pack_id: str = "erotic_fiction",
    version: str = "0.1.0",
    context: dict[str, Any] | None = None,
) -> GenreRecommendation:
    """Analyze premise and return exactly one opinionated GenreRecommendation candidate.
    
    This function is strictly read-only and causes zero pre-acceptance state mutation.
    """
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
