"""Advisory convergence for Story Discovery.

The existing Story Discovery search remains the source of candidates. This layer
adds bounded causal qualification, advisory comparative judgment, and grounded
craft explanation without promoting canonical state.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import yaml

from auteur.llm import LLMRequest
from auteur.story_discovery_judgment import (
    RecommendationJudgment,
    parse_recommendation_judgment,
    single_survivor_judgment,
)


_JUDGE_SYSTEM = """You are Auteur's comparative narrative architect.

Compare the supplied surviving StoryIdentity candidates. The candidates already
survived hard StoryIdentity validation and causal-distinctness qualification.
Your job is to make a bounded advisory judgment without inventing author intent,
without numeric creative scoring, and without mutating or claiming to mutate
canonical state.

EVIDENCE RULES
- Deterministic contract fit is compliance evidence, not a story-quality ranking.
- A higher contract-fit number does not automatically win.
- Scope and emotional runway are capacity evidence, not artistic-quality scores.
- Explicit author constraints are hard boundaries unless the author explicitly overrides them.
- Generation provenance and self-evaluation (lens, basis, confidence, alternatives, rejected directions, summaries, tradeoffs, risks, best-for) are not evidence for this judgment.
- A derived causal profile describes implied actions, pressure, reversals, and climax mechanics. It is evidence, not a quality score.
- Causal distinctness is a prerequisite for comparison, not a reason to reward the longest, most complex, or most ornate profile.

DECISION CALIBRATION
1. Use recommendation_basis = explicit_intent_fit only when a declared author
   preference or hard constraint actually distinguishes the winner from the
   alternatives. Name that declared preference in the rationale.
2. Use recommendation_basis = advisory_artistic_preference when multiple
   candidates legitimately satisfy the available author evidence but Auteur has
   a defensible craft preference among their different pleasures/tradeoffs.
   Present that criterion as Auteur's advisory taste, not as an undeclared author
   requirement.
3. Use recommendation_status = not_adjudicable only when even a bounded advisory
   preference would require inventing a criterion unsupported by the evidence.
   Multiple good options by itself is not enough reason to decline judgment.
4. When a winner exists, describe losing candidates as tradeoffs rather than
   deficiencies when they remain legitimate stories.

DEFAULT ADVISORY PRIORITY
When no declared preference settles the question, Auteur may prefer stronger
premise fidelity, causal architecture, genre/reader-promise delivery, or a more
coherent target-experience realization. Those are advisory craft criteria. They
must not be rewritten as author intent unless the author actually declared them.

Return JSON only with exactly these keys:
- recommendation_status: "recommended" or "not_adjudicable"
- recommendation_basis: "explicit_intent_fit", "advisory_artistic_preference", or null
- recommended_candidate_id: a surviving candidate ID, or null
- recommendation_rationale: non-empty explanation
- candidate_tradeoffs: mapping of candidate IDs to non-empty tradeoff explanations

For recommendation_status = recommended:
- recommendation_basis must be non-null;
- recommended_candidate_id must name one survivor;
- candidate_tradeoffs must cover exactly every non-selected survivor.

For recommendation_status = not_adjudicable:
- recommendation_basis and recommended_candidate_id must both be null;
- candidate_tradeoffs must cover every surviving candidate;
- the rationale must explain why the deciding artistic value remains genuinely open.
"""


def _err(message: str) -> None:
    print(f"Error: {message}", file=sys.stderr)


def _normalize(value: Any) -> str:
    return " ".join(str(value).casefold().split())


def _engine_signature(identity: Any) -> tuple[str, ...]:
    engine = identity.central_engine
    return tuple(
        _normalize(getattr(engine, field))
        for field in ("want", "resistance", "conflict", "stakes", "change")
    )


def _require_distinct_engines(candidate_outputs: list[Any]) -> None:
    """Retain deterministic exact-force-tuple duplicate protection."""
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


def _candidate_evidence(co: Any, *, causal_profile: Any | None = None) -> dict[str, Any]:
    identity = co.identity
    candidate = co.candidate
    evidence = {
        "candidate_id": co.candidate_id,
        "story_identity": {
            "title": identity.title,
            "core_answer": identity.core_answer,
            "target_experience": identity.target_experience.model_dump(mode="json"),
            "story_type": identity.story_type.model_dump(mode="json"),
            "central_engine": identity.central_engine.model_dump(mode="json"),
            "not_this": identity.not_this,
            "open_questions": identity.open_questions,
            "author_overrides": identity.author_overrides,
            "genre_contract": _bounded_contract_evidence(identity),
        },
        "validation_status": candidate.validation_status,
        "warning_count": candidate.warning_count,
        "contract_fit": candidate.contract_fit,
        "contract_fit_status": candidate.contract_fit_status,
        "contract_fit_problems": candidate.contract_fit_problems,
        "contract_fit_notes": candidate.contract_fit_notes,
    }
    if causal_profile is not None:
        evidence["derived_causal_profile"] = causal_profile.model_dump(mode="json")
    return evidence


def _build_judge_request(
    premise_text: str,
    candidate_outputs: list[Any],
    *,
    genre: str | None,
    medium: str | None,
    mode: str | None,
    causal_profiles: dict[str, Any] | None = None,
) -> LLMRequest:
    constraints = {
        key: value
        for key, value in {"genre": genre, "medium": medium, "mode": mode}.items()
        if value is not None
    }
    evidence = [
        _candidate_evidence(co, causal_profile=(causal_profiles or {}).get(co.candidate_id))
        for co in candidate_outputs
    ]
    user = (
        "DISCOVERY MODE\nexploratory\n\n"
        "RAW PREMISE\n"
        f"{premise_text}\n\n"
        "EXPLICIT RUN CONSTRAINTS\n"
        f"{json.dumps(constraints, indent=2, ensure_ascii=False)}\n\n"
        "This is not a structured Discovery Brief. recommendation_basis MUST NOT be "
        "explicit_intent_fit; any comparative winner is an advisory artistic preference.\n\n"
        "SURVIVING CANDIDATE EVIDENCE\n"
        f"{json.dumps(evidence, indent=2, ensure_ascii=False)}"
    )
    return LLMRequest(
        system=_JUDGE_SYSTEM,
        user=user,
        max_tokens=1800,
        temperature=0.2,
        model=None,
    )


def _parse_judgment(
    text: str,
    surviving_candidate_ids: list[str],
    *,
    allow_explicit_intent_fit: bool = True,
) -> RecommendationJudgment:
    return parse_recommendation_judgment(
        text,
        surviving_candidate_ids,
        allow_explicit_intent_fit=allow_explicit_intent_fit,
    )


def _single_survivor(candidate_id: str, requested: int) -> tuple[str, str, dict[str, str]]:
    """Preserve the historic helper contract for focused tests/callers."""
    judgment = single_survivor_judgment(candidate_id, requested)
    winner, rationale, rejected = judgment
    assert winner is not None
    return winner, rationale, rejected


def _candidate_by_id(candidate_outputs: list[Any], candidate_id: str) -> Any:
    matches = [co for co in candidate_outputs if co.candidate_id == candidate_id]
    if len(matches) != 1:
        raise ValueError(
            f"candidate lookup for {candidate_id!r} expected exactly one match; found {len(matches)}"
        )
    return matches[0]


def _recommendation_surface_lines(
    *,
    winner: str,
    rationale: str,
    rejected: dict[str, str],
    candidate_outputs: list[Any],
    output_dir: Path,
    requested_candidates: int,
    basis: str | None = None,
) -> list[str]:
    winner_output = _candidate_by_id(candidate_outputs, winner)
    identity = winner_output.identity
    target_experience = identity.target_experience.model_dump(mode="json")
    central_engine = identity.central_engine.model_dump(mode="json")
    accept_command = (
        f"auteur story-discovery accept {output_dir / (winner + '.yaml')} "
        "--output story_identity.yaml"
    )

    if len(candidate_outputs) == 1:
        return [
            "Story Discovery",
            f"1 viable interpretation survived from a {requested_candidates}-candidate search.",
            "",
            f"ONLY VIABLE INTERPRETATION — {identity.title} (`{winner}`)",
            identity.core_answer,
            "",
            "Why this result is different",
            rationale,
            "",
            "Nothing has been accepted yet.",
            "",
            "Next",
            "  Accept this interpretation:",
            f"    {accept_command}",
            "",
            "  Or revise the premise/constraints and run Story Discovery again.",
        ]

    if basis == "explicit_intent_fit":
        recommendation_heading = f"BEST FIT TO YOUR DECLARED INTENT — {identity.title} (`{winner}`)"
        why_heading = "Why this direction fits what you said you want"
        basis_note = None
    elif basis == "advisory_artistic_preference":
        recommendation_heading = f"AUTEUR'S ADVISORY PREFERENCE — {identity.title} (`{winner}`)"
        why_heading = "Why Auteur prefers it"
        basis_note = (
            "This is a craft judgment among compatible directions, not an additional author requirement."
        )
    else:
        recommendation_heading = f"RECOMMENDED — {identity.title} (`{winner}`)"
        why_heading = "Why Auteur recommends it"
        basis_note = None

    lines = [
        "Story Discovery",
        f"Found {len(candidate_outputs)} viable interpretations of your premise.",
        "",
        recommendation_heading,
        identity.core_answer,
        "",
        why_heading,
        rationale,
    ]
    if basis_note is not None:
        lines.extend(["", basis_note])
    lines.extend(
        [
            "",
            "What this choice emphasizes",
            f"- Reader experience: {target_experience['primary']}",
            f"- Central conflict: {central_engine['conflict']}",
            f"- Stakes: {central_engine['stakes']}",
            "",
            "Alternatives",
        ]
    )
    for co in candidate_outputs:
        if co.candidate_id == winner:
            continue
        lines.append(f"- {co.identity.title} (`{co.candidate_id}`) — {rejected[co.candidate_id]}")

    lines.extend(
        [
            "",
            "Nothing has been accepted yet.",
            "",
            "Next",
            "  Accept the recommendation:",
            f"    {accept_command}",
            "",
            "  Or choose another interpretation:",
        ]
    )
    for co in candidate_outputs:
        if co.candidate_id != winner:
            lines.append(
                "    auteur story-discovery accept "
                f"{output_dir / (co.candidate_id + '.yaml')} --output story_identity.yaml"
            )
    lines.extend(
        [
            "",
            "  Review the full comparison:",
            f"    {output_dir / 'comparison.md'}",
        ]
    )
    return lines


def _judgment_non_adjudicable_surface_lines(
    *,
    rationale: str,
    tradeoffs: dict[str, str],
    candidate_outputs: list[Any],
    output_dir: Path,
) -> list[str]:
    lines = [
        "Story Discovery",
        "AUTEUR DOES NOT HAVE AN HONEST PREFERENCE HERE",
        "",
        (
            "The surviving directions are causally distinct, but the available author intent "
            "does not settle the deciding artistic value. Auteur will not invent that preference for you."
        ),
        "",
        rationale,
        "",
        "Meaningful alternatives",
    ]
    for co in candidate_outputs:
        lines.append(
            f"- {co.identity.title} (`{co.candidate_id}`) — {tradeoffs[co.candidate_id]}"
        )
    lines.extend(["", "Nothing has been accepted yet.", "", "You can:"])
    for co in candidate_outputs:
        lines.append(
            "- Choose this direction explicitly: "
            f"auteur story-discovery accept {output_dir / (co.candidate_id + '.yaml')} "
            "--output story_identity.yaml"
        )
    lines.extend(
        [
            "- Change your declared intent, if you want Auteur to optimize for a sharper preference.",
            "- Generate a different search space.",
        ]
    )
    return lines


def _resolve_premise(raw: str) -> str:
    try:
        path = Path(raw)
        if path.exists() and path.is_file():
            return path.read_text(encoding="utf-8")
    except Exception:
        pass
    return raw


def _refresh_project_contract(candidate_outputs: list[Any], args: Any) -> None:
    if args.project is None or args.genre is None:
        return
    from auteur.cli_handlers import analyze_contract_fit
    from auteur.genres.registry import load_project_genre_contract

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
    winner: str | None,
    rationale: str,
    rejected: dict[str, str],
    surface_lines: list[str],
    recommendation_status: str = "recommended",
    recommendation_basis: str | None = None,
    candidate_tradeoffs: dict[str, str] | None = None,
) -> None:
    discovery_set_path = output_dir / "discovery_set.yaml"
    report_path = output_dir / "discovery_report.yaml"
    comparison_path = output_dir / "comparison.md"
    tradeoffs = dict(candidate_tradeoffs if candidate_tradeoffs is not None else rejected)

    for path in (discovery_set_path, report_path):
        payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        if winner is None:
            payload.pop("recommended_candidate_id", None)
        else:
            payload["recommended_candidate_id"] = winner
        payload["recommendation_status"] = recommendation_status
        payload["recommendation_basis"] = recommendation_basis
        payload["recommendation_rationale"] = rationale
        payload["candidate_tradeoffs"] = tradeoffs
        # Backward-compatible field retained for recommendation consumers.
        payload["rejected_candidate_reasons"] = rejected
        path.write_text(
            yaml.safe_dump(payload, sort_keys=False, allow_unicode=True),
            encoding="utf-8",
        )

    lines = comparison_path.read_text(encoding="utf-8").splitlines()
    lines.extend(["", "## Auteur Recommendation Judgment", "", *surface_lines[1:]])
    comparison_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def dispatch_story_discovery_recommend(args: Any) -> int:
    """Run search, qualify causal diversity, recommend, then teach grounded craft effects."""
    if args.candidates < 2:
        _err("Story Discovery --recommend requires --candidates >= 2 so a narrative search actually occurs.")
        return 1

    from auteur.cli_handlers import RecommendOpenEndedData, handle_identity_recommend
    from auteur.cli_serializers import serialize_story_discovery
    from auteur.llm.factory import build_client
    from auteur.story_discovery_causality import (
        CausalAnalysis,
        CausalGuidanceClient,
        append_causal_comparison,
        assess_causal_diversity,
        derive_causal_profiles,
        non_adjudicable_surface_lines,
        persist_causal_analysis,
    )
    from auteur.story_discovery_craft import derive_craft_impacts, persist_craft_analysis
    from auteur.story_discovery_craft_surface import (
        append_craft_comparison,
        compact_craft_lines,
        replace_generic_alternatives_with_craft,
    )

    premise_text = _resolve_premise(args.brain_dump)
    base_client = build_client(args.provider, args.model, agent_type="identity")
    result = handle_identity_recommend(
        client=CausalGuidanceClient(base_client),
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
        if result.error and result.error.strip().startswith("0 valid candidates survived"):
            _err("no Story Discovery candidate survived validation.")
            print("Try revising the premise or constraints and run again.", file=sys.stderr)
            print(
                "Use --debug to preserve failed candidate attempts when deeper inspection is needed.",
                file=sys.stderr,
            )
        else:
            _err(result.error or "Story Discovery failed")
        return result.exit_code
    data = result.data
    if not isinstance(data, RecommendOpenEndedData):
        _err("story discovery did not return candidate data")
        return 1

    candidate_outputs = data.candidates
    if not candidate_outputs:
        _err("no Story Discovery candidate survived validation.")
        return 1

    judgment: RecommendationJudgment | None = None
    craft_analysis = None
    profiles: dict[str, Any] = {}
    try:
        _refresh_project_contract(candidate_outputs, args)
        _require_distinct_engines(candidate_outputs)
        if len(candidate_outputs) == 1:
            causal_analysis = CausalAnalysis(status="not_applicable_single_survivor", profiles={})
            judgment = single_survivor_judgment(
                candidate_outputs[0].candidate_id,
                args.candidates,
            )
        else:
            profiles = derive_causal_profiles(base_client, candidate_outputs, premise_text)
            causal_analysis = assess_causal_diversity(base_client, profiles)
            if causal_analysis.status == "qualified":
                response = base_client.complete(
                    _build_judge_request(
                        premise_text,
                        candidate_outputs,
                        genre=args.genre,
                        medium=args.medium,
                        mode=args.mode,
                        causal_profiles=profiles,
                    )
                )
                judgment = _parse_judgment(
                    response.text,
                    [co.candidate_id for co in candidate_outputs],
                    allow_explicit_intent_fit=False,
                )
                if judgment.status == "recommended":
                    assert judgment.recommended_candidate_id is not None
                    craft_analysis = derive_craft_impacts(
                        base_client,
                        judgment.recommended_candidate_id,
                        candidate_outputs,
                        profiles,
                        premise_text,
                    )
    except Exception as exc:
        _err(f"Failed to produce comparative Story Discovery recommendation: {exc}")
        return 1

    winner = judgment.recommended_candidate_id if judgment is not None else None
    if winner is not None:
        data.rec_set.recommended_candidate_id = winner
    written = serialize_story_discovery(data, args.output, args.brain_dump)
    persist_causal_analysis(
        args.output,
        analysis=causal_analysis,
        artifact_names=("discovery_set.yaml", "discovery_report.yaml"),
    )
    append_causal_comparison(args.output, causal_analysis)

    if judgment is not None and judgment.status == "recommended":
        assert winner is not None
        surface_lines = _recommendation_surface_lines(
            winner=winner,
            rationale=judgment.rationale,
            rejected=judgment.rejected_candidate_reasons,
            candidate_outputs=candidate_outputs,
            output_dir=args.output,
            requested_candidates=args.candidates,
            basis=judgment.basis,
        )
        if craft_analysis is not None:
            surface_lines = replace_generic_alternatives_with_craft(
                surface_lines,
                compact_craft_lines(craft_analysis, profiles, candidate_outputs),
            )
        _augment_artifacts(
            args.output,
            winner=winner,
            rationale=judgment.rationale,
            rejected=judgment.rejected_candidate_reasons,
            surface_lines=surface_lines,
            recommendation_status=judgment.status,
            recommendation_basis=judgment.basis,
            candidate_tradeoffs=judgment.candidate_tradeoffs,
        )
        if craft_analysis is not None:
            persist_craft_analysis(
                args.output,
                craft_analysis,
                artifact_names=("discovery_set.yaml", "discovery_report.yaml"),
            )
            append_craft_comparison(args.output, craft_analysis, profiles, candidate_outputs)
    elif judgment is not None:
        surface_lines = _judgment_non_adjudicable_surface_lines(
            rationale=judgment.rationale,
            tradeoffs=judgment.candidate_tradeoffs,
            candidate_outputs=candidate_outputs,
            output_dir=args.output,
        )
        _augment_artifacts(
            args.output,
            winner=None,
            rationale=judgment.rationale,
            rejected={},
            surface_lines=surface_lines,
            recommendation_status=judgment.status,
            recommendation_basis=None,
            candidate_tradeoffs=judgment.candidate_tradeoffs,
        )
    else:
        surface_lines = non_adjudicable_surface_lines(
            causal_analysis,
            candidate_outputs,
            args.output,
        )

    print()
    for line in surface_lines:
        print(line)

    candidate_count = len(data.candidates)
    print("\nArtifacts")
    for path in written[:candidate_count]:
        print(f"  {path.name}")
    print(f"  {args.output / 'discovery_report.yaml'}")
    print(f"  {args.output / 'comparison.md'}")
    return 0
