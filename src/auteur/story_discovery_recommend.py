"""Advisory convergence for Story Discovery.

This module is intentionally an experiment adapter: the existing Story Discovery
search remains the source of candidates, and this layer adds one bounded
comparative recommendation without promoting canonical state.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

import yaml

from auteur.llm import LLMRequest


_JUDGE_SYSTEM = """You are Auteur's comparative narrative architect.

Choose one advisory winner from the supplied surviving StoryIdentity candidates.
The candidates already survived hard StoryIdentity validation. Compare them; do
not invent a candidate and do not mutate or claim to mutate canonical state.

EVIDENCE RULES
- Deterministic contract fit is compliance evidence, not a story-quality ranking.
- A higher contract-fit number does not automatically win.
- Scope and emotional runway are capacity evidence, not artistic-quality scores.
- Explicit author constraints are hard boundaries unless the author explicitly overrides them.
- Generated candidate summaries, tradeoffs, risks, and best-for lists are not evidence for this judgment.

DEFAULT DECISION PRIORITY
1. Genre/reader promise is the primary optimization basis.
2. Explicit author constraints and scope/runway viability constrain the choice.
3. Among genre-credible candidates, prefer stronger causal architecture and premise fidelity.
4. Use target-experience/emotional power to sharpen close calls, not as an automatic winner.
5. Explain meaningful tradeoffs against the actual alternatives.

Return JSON only with exactly these keys:
- recommended_candidate_id
- recommendation_rationale
- rejected_candidate_reasons

rejected_candidate_reasons must contain one non-empty reason for every surviving
candidate except the selected winner, and no other candidate IDs.
"""

_REQUIRED_JUDGE_KEYS = {
    "recommended_candidate_id",
    "recommendation_rationale",
    "rejected_candidate_reasons",
}


def _err(message: str) -> None:
    print(f"Error: {message}", file=sys.stderr)


def _normalize(value: Any) -> str:
    return " ".join(str(value).casefold().split())


def _engine_signature(identity: Any) -> tuple[str, ...]:
    """Return the exact normalized central-engine force tuple.

    This is deliberately not semantic near-duplicate detection. It rejects only
    exact normalized force duplication so the experiment does not pretend to
    solve similarity judgment deterministically.
    """
    engine = identity.central_engine
    return tuple(
        _normalize(getattr(engine, field))
        for field in ("want", "resistance", "conflict", "stakes", "change")
    )


def _require_distinct_engines(candidate_outputs: list[Any]) -> None:
    seen: dict[tuple[str, ...], str] = {}
    duplicates: list[str] = []
    for co in candidate_outputs:
        signature = _engine_signature(co.identity)
        previous = seen.get(signature)
        if previous is not None:
            duplicates.append(f"{previous}/{co.candidate_id}")
        else:
            seen[signature] = co.candidate_id
    if duplicates:
        raise ValueError(
            "Story Discovery recommendation requires distinct surviving central-engine "
            f"force tuples; exact duplicates: {', '.join(duplicates)}"
        )


def _bounded_contract_evidence(identity: Any) -> dict[str, Any] | None:
    contract = getattr(identity, "genre_contract_snapshot", None)
    if contract is None:
        return None
    data = contract.model_dump(mode="json")
    keep = (
        "genre_id",
        "display_name",
        "core_truth",
        "audience_product",
        "primary_excitement_beats",
        "scope_profile",
        "setup_contract",
    )
    return {key: data.get(key) for key in keep if key in data}


def _candidate_evidence(co: Any) -> dict[str, Any]:
    identity = co.identity
    candidate = co.candidate
    return {
        "candidate_id": co.candidate_id,
        "lens": getattr(candidate, "lens", ""),
        "best_basis": getattr(getattr(candidate, "best_basis", None), "value", None),
        "story_identity": {
            "title": identity.title,
            "core_answer": identity.core_answer,
            "target_experience": identity.target_experience.model_dump(mode="json"),
            "story_type": identity.story_type.model_dump(mode="json"),
            "central_engine": identity.central_engine.model_dump(mode="json"),
            "not_this": identity.not_this,
            "open_questions": identity.open_questions,
            "alternatives": identity.alternatives,
            "confidence": identity.confidence,
            "rejected_directions": identity.rejected_directions,
            "genre_contract": _bounded_contract_evidence(identity),
        },
        "validation_status": candidate.validation_status,
        "warning_count": candidate.warning_count,
        "contract_fit": candidate.contract_fit,
        "contract_fit_status": candidate.contract_fit_status,
        "contract_fit_problems": candidate.contract_fit_problems,
        "contract_fit_notes": candidate.contract_fit_notes,
    }


def _build_judge_request(
    premise_text: str,
    candidate_outputs: list[Any],
    *,
    genre: str | None,
    medium: str | None,
    mode: str | None,
) -> LLMRequest:
    constraints = {
        key: value
        for key, value in {"genre": genre, "medium": medium, "mode": mode}.items()
        if value is not None
    }
    evidence = [_candidate_evidence(co) for co in candidate_outputs]
    user = (
        "RAW PREMISE\n"
        f"{premise_text}\n\n"
        "EXPLICIT AUTHOR CONSTRAINTS\n"
        f"{json.dumps(constraints, indent=2, ensure_ascii=False)}\n\n"
        "SURVIVING CANDIDATE EVIDENCE\n"
        f"{json.dumps(evidence, indent=2, ensure_ascii=False)}"
    )
    return LLMRequest(
        system=_JUDGE_SYSTEM,
        user=user,
        max_tokens=1600,
        temperature=0.2,
        model=None,
    )


def _parse_judgment(
    text: str,
    surviving_candidate_ids: list[str],
) -> tuple[str, str, dict[str, str]]:
    if len(surviving_candidate_ids) < 2:
        raise ValueError("comparative judgment requires at least two surviving candidates")
    if len(set(surviving_candidate_ids)) != len(surviving_candidate_ids):
        raise ValueError("surviving candidate IDs must be unique")

    match = re.search(r"\{.*\}", text.strip(), re.DOTALL)
    if not match:
        raise ValueError("comparative judgment did not contain a JSON object")
    payload = json.loads(match.group(0))
    if not isinstance(payload, dict) or set(payload) != _REQUIRED_JUDGE_KEYS:
        raise ValueError("comparative judgment must contain exactly the required keys")

    winner = payload["recommended_candidate_id"]
    if not isinstance(winner, str) or winner.strip() not in surviving_candidate_ids:
        raise ValueError("recommended candidate must be one of the surviving candidates")
    winner = winner.strip()

    rationale = payload["recommendation_rationale"]
    if not isinstance(rationale, str) or not rationale.strip():
        raise ValueError("recommendation rationale is required")
    rationale = rationale.strip()

    raw_reasons = payload["rejected_candidate_reasons"]
    if not isinstance(raw_reasons, dict):
        raise ValueError("rejected_candidate_reasons must be a mapping")
    reasons: dict[str, str] = {}
    for candidate_id, reason in raw_reasons.items():
        if not isinstance(candidate_id, str) or not isinstance(reason, str):
            raise ValueError("rejection reasons must map candidate IDs to strings")
        reasons[candidate_id.strip()] = reason.strip()

    expected = set(surviving_candidate_ids) - {winner}
    if set(reasons) != expected:
        raise ValueError("rejection reasons must cover exactly every non-selected survivor")
    if any(not reasons[candidate_id] for candidate_id in expected):
        raise ValueError("every rejected survivor requires a non-empty reason")
    return winner, rationale, reasons


def _single_survivor(candidate_id: str, requested: int) -> tuple[str, str, dict[str, str]]:
    return (
        candidate_id,
        f"{candidate_id} is the only candidate that survived StoryIdentity validation "
        f"from a {requested}-candidate search. This is a viability result, not a "
        "comparative artistic-quality judgment.",
        {},
    )


def _resolve_premise(raw: str) -> str:
    try:
        path = Path(raw)
        if path.exists() and path.is_file():
            return path.read_text(encoding="utf-8")
    except Exception:
        pass
    return raw


def _refresh_project_contract(candidate_outputs: list[Any], args: Any) -> None:
    """Keep project-local GenreContract authority intact for experiment evidence."""
    if args.project is None or args.genre is None:
        return
    from auteur.genres.registry import load_project_genre_contract
    from auteur.cli_handlers import analyze_contract_fit

    contract = load_project_genre_contract(args.project, args.genre.lower().strip())
    for co in candidate_outputs:
        co.identity.genre_contract_snapshot = contract
        fit, status, problems, notes = analyze_contract_fit(co.identity)
        co.candidate.contract_fit = fit
        co.candidate.contract_fit_status = status
        co.candidate.contract_fit_problems = problems
        co.candidate.contract_fit_notes = notes
        co.yaml_content = yaml.safe_dump(
            co.identity.model_dump(mode="json"),
            sort_keys=False,
            allow_unicode=True,
        )


def _augment_artifacts(
    output_dir: Path,
    *,
    winner: str,
    rationale: str,
    rejected: dict[str, str],
    candidate_outputs: list[Any],
) -> None:
    discovery_set_path = output_dir / "discovery_set.yaml"
    report_path = output_dir / "discovery_report.yaml"
    comparison_path = output_dir / "comparison.md"

    discovery_set = yaml.safe_load(discovery_set_path.read_text(encoding="utf-8")) or {}
    discovery_set["recommended_candidate_id"] = winner
    discovery_set["recommendation_rationale"] = rationale
    discovery_set["rejected_candidate_reasons"] = rejected
    discovery_set_path.write_text(
        yaml.safe_dump(discovery_set, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )

    report = yaml.safe_load(report_path.read_text(encoding="utf-8")) or {}
    report["recommended_candidate_id"] = winner
    report["recommendation_rationale"] = rationale
    report["rejected_candidate_reasons"] = rejected
    report_path.write_text(
        yaml.safe_dump(report, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )

    lines = comparison_path.read_text(encoding="utf-8").splitlines()
    lines.extend(["", "## Auteur Advisory Recommendation", "", f"**Recommended candidate**: `{winner}`", f"**Why**: {rationale}"])
    if rejected:
        lines.extend(["", "**Why the other surviving candidates lose:**"])
        for co in candidate_outputs:
            candidate_id = co.candidate_id
            if candidate_id != winner:
                lines.append(f"- `{candidate_id}`: {rejected[candidate_id]}")
    lines.extend([
        "",
        "This recommendation is advisory. Canonical StoryIdentity changes only after an explicit `auteur story-discovery accept ...` command.",
    ])
    comparison_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def dispatch_story_discovery_recommend(args: Any) -> int:
    """Run Story Discovery search, then add one advisory comparative recommendation."""
    if args.candidates < 2:
        _err("Story Discovery --recommend requires --candidates >= 2 so a narrative search actually occurs.")
        return 1

    from auteur.cli_handlers import RecommendOpenEndedData, handle_identity_recommend
    from auteur.cli_serializers import serialize_story_discovery
    from auteur.llm.factory import build_client

    premise_text = _resolve_premise(args.brain_dump)
    client = build_client(args.provider, args.model, agent_type="identity")
    result = handle_identity_recommend(
        client=client,
        premise_text=premise_text,
        genre=args.genre,
        medium=args.medium,
        mode=args.mode,
        recommend_mode="open_ended",
        candidates_count=args.candidates,
        discovery_lenses=args.lens,
        strict_candidate_count=args.strict_candidate_count,
        debug=args.debug,
        project_path=args.project,
    )
    if not result.is_success:
        _err(result.error)
        return result.exit_code
    data = result.data
    if not isinstance(data, RecommendOpenEndedData):
        _err("story discovery did not return candidate data")
        return 1

    candidate_outputs = data.candidates
    if not candidate_outputs:
        _err("0 valid candidates survived validation checks.")
        return 1

    try:
        _refresh_project_contract(candidate_outputs, args)
        _require_distinct_engines(candidate_outputs)
        if len(candidate_outputs) == 1:
            winner, rationale, rejected = _single_survivor(
                candidate_outputs[0].candidate_id,
                args.candidates,
            )
        else:
            request = _build_judge_request(
                premise_text,
                candidate_outputs,
                genre=args.genre,
                medium=args.medium,
                mode=args.mode,
            )
            response = client.complete(request)
            winner, rationale, rejected = _parse_judgment(
                response.text,
                [co.candidate_id for co in candidate_outputs],
            )
    except Exception as exc:
        _err(f"Failed to produce comparative Story Discovery recommendation: {exc}")
        return 1

    data.rec_set.recommended_candidate_id = winner
    written = serialize_story_discovery(data, args.output, args.brain_dump)
    _augment_artifacts(
        args.output,
        winner=winner,
        rationale=rationale,
        rejected=rejected,
        candidate_outputs=candidate_outputs,
    )

    candidate_count = len(data.candidates)
    for path in written[:candidate_count]:
        print(f"  Wrote {path.name}")
    print(f"\nSuccess: generated {candidate_count} Story Discovery candidates under {args.output}/")
    print(f"Discovery report written to {args.output / 'discovery_report.yaml'}")
    print(f"Comparison document written to {args.output / 'comparison.md'}")
    print(f"Auteur advisory recommendation: {winner}")
    print("  Canonical state is unchanged; use `auteur story-discovery accept ...` to promote a candidate.")
    return 0
