"""Typed comparative-judgment contract for Story Discovery.

The recommendation layer distinguishes evidence-backed author-intent fit from
Auteur's own advisory craft preference, and can decline to manufacture a
preference when neither is defensible. The result remains advisory and never
mutates canonical StoryIdentity state.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Literal

RecommendationStatus = Literal["recommended", "not_adjudicable"]
RecommendationBasis = Literal[
    "explicit_intent_fit",
    "advisory_artistic_preference",
]

_V2_KEYS = {
    "recommendation_status",
    "recommendation_basis",
    "recommended_candidate_id",
    "recommendation_rationale",
    "candidate_tradeoffs",
}
_LEGACY_KEYS = {
    "recommended_candidate_id",
    "recommendation_rationale",
    "rejected_candidate_reasons",
}


@dataclass(frozen=True)
class RecommendationJudgment:
    """Validated comparative recommendation result.

    ``__iter__`` intentionally preserves the historic three-value unpacking
    contract used by older tests/callers: winner, rationale, rejected reasons.
    New v2 callers should inspect ``status`` and ``basis`` directly. A ``None``
    basis on a recommended result means the response used the pre-calibration
    legacy contract and therefore supplied no defensible basis classification.
    """

    status: RecommendationStatus
    basis: RecommendationBasis | None
    recommended_candidate_id: str | None
    rationale: str
    candidate_tradeoffs: dict[str, str]

    @property
    def rejected_candidate_reasons(self) -> dict[str, str]:
        if self.recommended_candidate_id is None:
            return {}
        return {
            candidate_id: reason
            for candidate_id, reason in self.candidate_tradeoffs.items()
            if candidate_id != self.recommended_candidate_id
        }

    def __iter__(self):
        yield self.recommended_candidate_id
        yield self.rationale
        yield self.rejected_candidate_reasons


def _json_object(text: str) -> dict[str, object]:
    match = re.search(r"\{.*\}", text.strip(), re.DOTALL)
    if not match:
        raise ValueError("comparative judgment did not contain a JSON object")
    payload = json.loads(match.group(0))
    if not isinstance(payload, dict):
        raise ValueError("comparative judgment must be a JSON object")
    return payload


def _normalize_nonempty_mapping(value: object, *, label: str) -> dict[str, str]:
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be a mapping")
    normalized: dict[str, str] = {}
    for candidate_id, reason in value.items():
        if not isinstance(candidate_id, str) or not isinstance(reason, str):
            raise ValueError(f"{label} must map candidate IDs to strings")
        clean_id = candidate_id.strip()
        clean_reason = reason.strip()
        if not clean_id or not clean_reason:
            raise ValueError(f"{label} requires non-empty candidate IDs and reasons")
        normalized[clean_id] = clean_reason
    return normalized


def parse_recommendation_judgment(
    text: str,
    surviving_candidate_ids: list[str],
    *,
    allow_explicit_intent_fit: bool,
) -> RecommendationJudgment:
    """Parse a comparative judgment and fail closed on semantic contradictions."""

    if len(surviving_candidate_ids) < 2:
        raise ValueError("comparative judgment requires at least two surviving candidates")
    if len(set(surviving_candidate_ids)) != len(surviving_candidate_ids):
        raise ValueError("surviving candidate IDs must be unique")

    payload = _json_object(text)
    keys = set(payload)

    # Backward-compatible fixture/artifact response support. A legacy result can
    # prove only that the old judge preferred a candidate. It cannot establish
    # *why* that candidate won under the new calibrated basis contract, so the
    # basis deliberately remains unclassified instead of being guessed.
    if keys == _LEGACY_KEYS:
        winner = payload["recommended_candidate_id"]
        if not isinstance(winner, str) or winner.strip() not in surviving_candidate_ids:
            raise ValueError("recommended candidate must be one of the surviving candidates")
        winner = winner.strip()
        rationale = payload["recommendation_rationale"]
        if not isinstance(rationale, str) or not rationale.strip():
            raise ValueError("recommendation rationale is required")
        reasons = _normalize_nonempty_mapping(
            payload["rejected_candidate_reasons"],
            label="rejected_candidate_reasons",
        )
        expected = set(surviving_candidate_ids) - {winner}
        if set(reasons) != expected:
            raise ValueError("rejection reasons must cover exactly every non-selected survivor")
        return RecommendationJudgment(
            status="recommended",
            basis=None,
            recommended_candidate_id=winner,
            rationale=rationale.strip(),
            candidate_tradeoffs=reasons,
        )

    if keys != _V2_KEYS:
        raise ValueError("comparative judgment must contain exactly the required keys")

    status = payload["recommendation_status"]
    if status not in {"recommended", "not_adjudicable"}:
        raise ValueError("recommendation_status must be recommended or not_adjudicable")

    rationale = payload["recommendation_rationale"]
    if not isinstance(rationale, str) or not rationale.strip():
        raise ValueError("recommendation rationale is required")
    rationale = rationale.strip()

    tradeoffs = _normalize_nonempty_mapping(
        payload["candidate_tradeoffs"],
        label="candidate_tradeoffs",
    )

    raw_winner = payload["recommended_candidate_id"]
    raw_basis = payload["recommendation_basis"]

    if status == "not_adjudicable":
        if raw_winner is not None:
            raise ValueError("not_adjudicable judgment must not select a winner")
        if raw_basis is not None:
            raise ValueError("not_adjudicable judgment must not claim a recommendation basis")
        if set(tradeoffs) != set(surviving_candidate_ids):
            raise ValueError(
                "not_adjudicable tradeoffs must cover every surviving candidate"
            )
        return RecommendationJudgment(
            status="not_adjudicable",
            basis=None,
            recommended_candidate_id=None,
            rationale=rationale,
            candidate_tradeoffs=tradeoffs,
        )

    if not isinstance(raw_winner, str) or raw_winner.strip() not in surviving_candidate_ids:
        raise ValueError("recommended candidate must be one of the surviving candidates")
    winner = raw_winner.strip()

    if raw_basis not in {"explicit_intent_fit", "advisory_artistic_preference"}:
        raise ValueError("recommended judgment requires a valid recommendation_basis")
    basis: RecommendationBasis = raw_basis
    if basis == "explicit_intent_fit" and not allow_explicit_intent_fit:
        raise ValueError(
            "explicit_intent_fit requires a structured declared-author-intent context"
        )

    expected = set(surviving_candidate_ids) - {winner}
    if set(tradeoffs) != expected:
        raise ValueError(
            "recommended candidate_tradeoffs must cover exactly every non-selected survivor"
        )

    return RecommendationJudgment(
        status="recommended",
        basis=basis,
        recommended_candidate_id=winner,
        rationale=rationale,
        candidate_tradeoffs=tradeoffs,
    )


def single_survivor_judgment(
    candidate_id: str,
    requested: int,
) -> RecommendationJudgment:
    """Represent a viability-only single-survivor result without fake comparison."""

    return RecommendationJudgment(
        status="recommended",
        basis=None,
        recommended_candidate_id=candidate_id,
        rationale=(
            f"{candidate_id} is the only candidate that survived StoryIdentity validation "
            f"from a {requested}-candidate search. This is a viability result, not a "
            "comparative artistic-quality judgment."
        ),
        candidate_tradeoffs={},
    )
