"""Intent-aware Story Discovery orchestration.

This adapter preserves the F2 prior-author-intent boundary while applying F3
causal qualification and F4 grounded craft teaching before comparative output.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import yaml

from auteur.llm import LLMRequest
from auteur.story_discovery_brief import DiscoveryBrief, IntentAdequacy, assess_intent_adequacy
from auteur.story_discovery_judgment import RecommendationJudgment, single_survivor_judgment
from auteur.story_discovery_recommend import (
    _JUDGE_SYSTEM,
    _augment_artifacts,
    _build_judge_request,
    _candidate_evidence,
    _err,
    _judgment_non_adjudicable_surface_lines,
    _parse_judgment,
    _recommendation_surface_lines,
    _refresh_project_contract,
    _require_distinct_engines,
    _resolve_premise,
)


_INTENT_JUDGE_SYSTEM = _JUDGE_SYSTEM + """

INTENT-AWARE DECISION RULES
When a DECLARED AUTHOR INTENT block is supplied, it is prior author intent and is
more authoritative than candidate-generated proposals about genre, audience,
target experience, architecture preference, or constraints.
- Treat every explicit hard constraint as a hard boundary.
- Optimize first for the declared genre/reader promise, target audience, and target
  experience, then for any declared architecture preferences.
- Candidate-generated fields may demonstrate how a direction realizes the brief;
  they must not be treated as evidence that the author wanted an omitted value.
- Omitted brief fields remain UNKNOWN. Do not invent preferences to fill them.
- Architecture preferences may influence the winner but must not turn profile
  length or complexity into an automatic quality signal.
- Use explicit_intent_fit only when a declared value actually distinguishes the
  recommendation. If the deciding value is Auteur's own craft preference, use
  advisory_artistic_preference and name the tradeoff honestly.
- If neither declared intent nor a defensible advisory craft preference settles the
  comparison, return not_adjudicable rather than manufacturing certainty.
"""


class _BriefAwareClient:
    """Inject prior author intent only into candidate-generation requests."""

    def __init__(self, delegate: Any, brief: DiscoveryBrief):
        self._delegate = delegate
        self._brief = brief

    def complete(self, request: LLMRequest):
        if "expert, opinionated narrative compiler" in request.system:
            declared = json.dumps(
                self._brief.declared_intent(),
                indent=2,
                ensure_ascii=False,
            )
            prefix = (
                "DECLARED AUTHOR INTENT (PRIOR TO CANDIDATE GENERATION)\n"
                f"{declared}\n\n"
                "Treat every explicit value above as author intent. Hard constraints are "
                "hard boundaries. Omitted values remain unspecified and must not be "
                "invented as author preferences. Generate a distinct candidate that serves "
                "this declared intent.\n\n"
            )
            request = request.model_copy(update={"user": prefix + request.user})
        return self._delegate.complete(request)


def _effective_constraints(brief: DiscoveryBrief) -> tuple[str | None, str | None, str | None]:
    story_type = brief.story_type
    if story_type is None:
        return None, None, None
    genre = story_type.genre.value if story_type.genre is not None else None
    medium = story_type.medium.value if story_type.medium is not None else None
    mode = story_type.mode.value if story_type.mode is not None else None
    return genre, medium, mode


def _refresh_content_hashes(candidate_outputs: list[Any]) -> None:
    for co in candidate_outputs:
        co.candidate.content_hash = (
            "sha256:" + hashlib.sha256(co.yaml_content.encode("utf-8")).hexdigest()
        )


def _declared_target_experience_fields(brief: DiscoveryBrief) -> dict[str, Any]:
    if brief.target_experience is None:
        return {}
    return brief.target_experience.model_dump(
        mode="json",
        include=brief.target_experience.model_fields_set,
        exclude_none=True,
    )


def _apply_brief_commitments(candidate_outputs: list[Any], brief: DiscoveryBrief) -> list[Any]:
    """Validate generated candidates against prior intent, then attach explicit commitments."""

    from auteur.cli_handlers import analyze_contract_fit

    target_fields = _declared_target_experience_fields(brief)
    for co in candidate_outputs:
        identity = co.identity
        mismatches: list[str] = []
        story_type = brief.story_type
        if story_type is not None:
            for field_name in ("genre", "medium", "mode", "target_audience"):
                expected = getattr(story_type, field_name)
                if expected is None:
                    continue
                actual = getattr(identity.story_type, field_name)
                if actual != expected:
                    mismatches.append(
                        f"story_type.{field_name}: expected {expected.value!r}, got {actual.value!r}"
                    )

        if brief.target_experience is not None:
            expected_primary = brief.target_experience.primary
            if identity.target_experience.primary != expected_primary:
                mismatches.append(
                    "target_experience.primary: expected "
                    f"{expected_primary!r}, got {identity.target_experience.primary!r}"
                )

        if mismatches:
            raise ValueError(
                f"{co.candidate_id} contradicts declared author intent: "
                + "; ".join(mismatches)
            )

        if target_fields:
            target_payload = identity.target_experience.model_dump(mode="json")
            target_payload.update(target_fields)
            identity.target_experience = identity.target_experience.__class__.model_validate(
                target_payload
            )

        identity.architecture_preferences = (
            brief.architecture_preferences.model_copy(deep=True)
            if brief.architecture_preferences is not None
            else None
        )
        identity.hard_constraints = list(brief.hard_constraints)

        diagnostics = identity.validate_identity()
        errors = [
            d
            for d in diagnostics
            if (
                d.severity.value.lower() == "error"
                if hasattr(d.severity, "value")
                else str(d.severity).lower() == "error"
            )
        ]
        if errors:
            details = "; ".join(f"{d.rule}: {d.message}" for d in errors)
            raise ValueError(
                f"{co.candidate_id} is invalid after applying declared author intent: {details}"
            )

        warnings = [
            d
            for d in diagnostics
            if (
                d.severity.value.lower() == "warning"
                if hasattr(d.severity, "value")
                else str(d.severity).lower() == "warning"
            )
        ]
        fit, status, problems, notes = analyze_contract_fit(identity)
        co.candidate.validation_status = "valid_with_warnings" if warnings else "valid"
        co.candidate.warning_count = len(warnings)
        co.candidate.contract_fit = fit
        co.candidate.contract_fit_status = status
        co.candidate.contract_fit_problems = problems
        co.candidate.contract_fit_notes = notes
        co.yaml_content = yaml.safe_dump(
            identity.model_dump(mode="json"),
            sort_keys=False,
            allow_unicode=True,
        )

    _refresh_content_hashes(candidate_outputs)
    return candidate_outputs


def _intent_candidate_evidence(co: Any, *, causal_profile: Any | None = None) -> dict[str, Any]:
    evidence = _candidate_evidence(co, causal_profile=causal_profile)
    story_identity = evidence["story_identity"]
    preferences = getattr(co.identity, "architecture_preferences", None)
    story_identity["architecture_preferences"] = (
        preferences.model_dump(mode="json") if preferences is not None else None
    )
    story_identity["hard_constraints"] = list(getattr(co.identity, "hard_constraints", []))
    return evidence


def _build_intent_judge_request(
    brief: DiscoveryBrief,
    candidate_outputs: list[Any],
    *,
    causal_profiles: dict[str, Any] | None = None,
) -> LLMRequest:
    evidence = [
        _intent_candidate_evidence(
            co,
            causal_profile=(causal_profiles or {}).get(co.candidate_id),
        )
        for co in candidate_outputs
    ]
    user = (
        "DISCOVERY MODE\nintent_aware\n\n"
        "DECLARED AUTHOR INTENT (PRIOR TO CANDIDATE GENERATION)\n"
        f"{json.dumps(brief.declared_intent(), indent=2, ensure_ascii=False)}\n\n"
        "SURVIVING CANDIDATE EVIDENCE\n"
        f"{json.dumps(evidence, indent=2, ensure_ascii=False)}"
    )
    return LLMRequest(
        system=_INTENT_JUDGE_SYSTEM,
        user=user,
        max_tokens=1800,
        temperature=0.2,
        model=None,
    )


def _build_intent_comparison_lines(data: Any, brief: DiscoveryBrief) -> list[str]:
    candidate_outputs = data.candidates
    lines = [
        "# Story Discovery Comparison",
        "\nSource Premise File/Text: ``",
        f"Generated At: {data.rec_set.generated_at}\n",
        "Intent-aware comparison against a structured Discovery Brief. Omitted brief fields remain UNKNOWN.\n",
        "Contract fit measures compliance with declared genre and structural contracts. It is not a story-quality ranking.\n",
        "## Declared Author Intent",
        "```json",
        json.dumps(brief.declared_intent(), indent=2, ensure_ascii=False),
        "```",
        "\n## Candidate Interpretations\n",
        "| Candidate | Genre | Audience | Primary experience | Central conflict | Contract fit |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for co in candidate_outputs:
        candidate = co.candidate
        identity = co.identity
        lines.append(
            "| "
            f"`{co.candidate_id}` | {identity.story_type.genre.value} | "
            f"{identity.story_type.target_audience.value} | "
            f"{identity.target_experience.primary} | "
            f"{identity.central_engine.conflict} | "
            f"{candidate.contract_fit} ({candidate.contract_fit_status}) |"
        )
    return lines


def _qualify_surface(lines: list[str], *, intent_aware: bool) -> list[str]:
    qualified = list(lines)
    if not qualified:
        return qualified
    recommendation_prefixes = (
        "RECOMMENDED —",
        "BEST FIT TO YOUR DECLARED INTENT —",
        "AUTEUR'S ADVISORY PREFERENCE —",
        "ONLY VIABLE INTERPRETATION —",
    )
    has_recommendation = any(
        line.startswith(recommendation_prefixes)
        for line in qualified
    )
    if intent_aware:
        qualified.insert(
            1,
            (
                "Intent-aware recommendation against your declared Discovery Brief."
                if has_recommendation
                else "Intent-aware comparative assessment against your declared Discovery Brief."
            ),
        )
        return qualified

    qualified.insert(
        1,
        (
            "Exploratory recommendation using Auteur's default criteria; no structured "
            "Discovery Brief was supplied, so this is not a claim about undeclared author intent."
            if has_recommendation
            else "Exploratory comparative assessment; no structured Discovery Brief was supplied, "
            "so this is not a claim about undeclared author intent."
        ),
    )
    for index, line in enumerate(qualified):
        if line.startswith("RECOMMENDED —"):
            qualified[index] = line.replace(
                "RECOMMENDED —",
                "EXPLORATORY RECOMMENDATION —",
                1,
            )
            break
    return qualified


def _augment_intent_artifacts(
    output_dir: Path,
    *,
    brief: DiscoveryBrief | None,
    adequacy: IntentAdequacy | None,
    brief_path: Path | None = None,
) -> None:
    mode = "intent_aware" if brief is not None else "exploratory"
    declared = brief.declared_intent() if brief is not None else None
    adequacy_data: dict[str, object] = (
        adequacy.model_dump(mode="json")
        if adequacy is not None
        else {"adequate": False, "missing": [], "status": "not_assessed_without_brief"}
    )

    for name in ("discovery_set.yaml", "discovery_report.yaml"):
        path = output_dir / name
        payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        payload["intent_mode"] = mode
        payload["declared_author_intent"] = declared
        payload["intent_adequacy"] = adequacy_data
        if brief_path is not None:
            payload["source_brief_path"] = str(brief_path)
        if brief is not None and name == "discovery_report.yaml":
            payload["premise_summary"] = brief.premise
        path.write_text(
            yaml.safe_dump(payload, sort_keys=False, allow_unicode=True),
            encoding="utf-8",
        )

    comparison_path = output_dir / "comparison.md"
    comparison = comparison_path.read_text(encoding="utf-8")
    heading = (
        "## Discovery Intent\n\n"
        + (
            "This comparison is judged against the structured author brief supplied before candidate generation.\n"
            if brief is not None
            else "This is exploratory analysis because no structured author brief was supplied.\n"
        )
    )
    comparison_path.write_text(comparison + "\n" + heading, encoding="utf-8")


def dispatch_story_discovery_recommend(args: Any) -> int:
    """Run intent-aware Story Discovery through F2 intent, F3 causality, and F4 craft gates."""

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

    brief: DiscoveryBrief | None = None
    adequacy: IntentAdequacy | None = None
    brief_path = getattr(args, "brief", None)
    if brief_path is not None:
        try:
            brief = DiscoveryBrief.from_yaml(brief_path)
        except Exception as exc:
            _err(f"Failed to parse Discovery Brief: {exc}")
            return 1
        adequacy = assess_intent_adequacy(brief)
        if not adequacy.adequate:
            _err(
                "Insufficient author intent for intent-aware Story Discovery; missing: "
                + ", ".join(adequacy.missing)
            )
            print(
                "Add primary genre, target audience, and target experience to the Discovery Brief, "
                "or run raw-premise Story Discovery for exploratory search.",
                file=sys.stderr,
            )
            return 1

    if brief is not None:
        premise_text = brief.premise
        genre, medium, mode = _effective_constraints(brief)
        source_input = str(brief_path)
    else:
        premise_text = _resolve_premise(args.brain_dump)
        genre, medium, mode = args.genre, args.medium, args.mode
        source_input = args.brain_dump

    base_client = build_client(args.provider, args.model, agent_type="identity")
    guided_client = CausalGuidanceClient(base_client)
    client = _BriefAwareClient(guided_client, brief) if brief is not None else guided_client
    result = handle_identity_recommend(
        client=client,
        premise_text=premise_text,
        genre=genre,
        medium=medium,
        mode=mode,
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
        else:
            _err(result.error or "Story Discovery failed")
        return result.exit_code

    data = result.data
    if not isinstance(data, RecommendOpenEndedData):
        _err("story discovery did not return candidate data")
        return 1

    candidate_outputs = data.candidates
    if brief is not None:
        try:
            candidate_outputs = _apply_brief_commitments(candidate_outputs, brief)
        except Exception as exc:
            _err(f"Story Discovery candidate failed declared-intent validation: {exc}")
            return 1
        data.candidates = candidate_outputs
        data.rec_set.candidates = [co.candidate for co in candidate_outputs]
        data.rec_set.valid_candidates = len(candidate_outputs)
        data.comparison_lines = _build_intent_comparison_lines(data, brief)

    if not candidate_outputs:
        _err("no Story Discovery candidate survived validation after applying declared author intent.")
        return 1

    judgment: RecommendationJudgment | None = None
    craft_analysis = None
    profiles: dict[str, Any] = {}
    try:
        contract_args = SimpleNamespace(project=args.project, genre=genre)
        _refresh_project_contract(candidate_outputs, contract_args)
        _refresh_content_hashes(candidate_outputs)
        _require_distinct_engines(candidate_outputs)
        if len(candidate_outputs) == 1:
            causal_analysis = CausalAnalysis(status="not_applicable_single_survivor", profiles={})
            judgment = single_survivor_judgment(
                candidate_outputs[0].candidate_id,
                args.candidates,
            )
        else:
            declared = brief.declared_intent() if brief is not None else None
            profiles = derive_causal_profiles(
                base_client,
                candidate_outputs,
                premise_text,
                declared_author_intent=declared,
            )
            causal_analysis = assess_causal_diversity(base_client, profiles)
            if causal_analysis.status == "qualified":
                if brief is not None:
                    response = base_client.complete(
                        _build_intent_judge_request(
                            brief,
                            candidate_outputs,
                            causal_profiles=profiles,
                        )
                    )
                else:
                    response = base_client.complete(
                        _build_judge_request(
                            premise_text,
                            candidate_outputs,
                            genre=genre,
                            medium=medium,
                            mode=mode,
                            causal_profiles=profiles,
                        )
                    )
                judgment = _parse_judgment(
                    response.text,
                    [co.candidate_id for co in candidate_outputs],
                    allow_explicit_intent_fit=brief is not None,
                )
                if judgment.status == "recommended":
                    assert judgment.recommended_candidate_id is not None
                    craft_analysis = derive_craft_impacts(
                        base_client,
                        judgment.recommended_candidate_id,
                        candidate_outputs,
                        profiles,
                        premise_text,
                        declared_author_intent=declared,
                    )
    except Exception as exc:
        _err(f"Failed to produce comparative Story Discovery recommendation: {exc}")
        return 1

    winner = judgment.recommended_candidate_id if judgment is not None else None
    if winner is not None:
        data.rec_set.recommended_candidate_id = winner
    written = serialize_story_discovery(data, args.output, source_input)
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
        surface_lines = _qualify_surface(surface_lines, intent_aware=brief is not None)
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
        surface_lines = _qualify_surface(surface_lines, intent_aware=brief is not None)
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
        surface_lines = _qualify_surface(surface_lines, intent_aware=brief is not None)

    _augment_intent_artifacts(
        args.output,
        brief=brief,
        adequacy=adequacy,
        brief_path=brief_path,
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
