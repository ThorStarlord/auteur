"""F2 intent-aware Story Discovery orchestration.

This adapter keeps the qualified Story Discovery search/judge mechanics intact while
adding one explicit prior-author-intent input contract. Raw premise recommendation
remains available, but is labeled exploratory rather than pretending undeclared
preferences are known.
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
from auteur.story_discovery_recommend import (
    _JUDGE_SYSTEM,
    _augment_artifacts,
    _build_judge_request,
    _candidate_evidence,
    _err,
    _parse_judgment,
    _recommendation_surface_lines,
    _refresh_project_contract,
    _require_distinct_engines,
    _resolve_premise,
    _single_survivor,
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
    """Validate candidate output against prior intent, then attach explicit commitments.

    Genre, medium, mode, audience, and the governing primary reader experience are
    never silently rewritten here. If candidate generation contradicts those declared
    values, F2 fails closed. Explicit subordinate TargetExperience fields are merged,
    while architecture preferences and hard constraints are copied as author
    commitments before comparative judgment and serialization.
    """

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

        # Structured-brief architecture commitments must represent only what the
        # author declared before generation, never an inferred candidate preference.
        identity.architecture_preferences = (
            brief.architecture_preferences.model_copy(deep=True)
            if brief.architecture_preferences is not None
            else None
        )
        identity.hard_constraints = list(brief.hard_constraints)

        diagnostics = identity.validate_identity()
        errors = [
            diagnostic
            for diagnostic in diagnostics
            if (
                diagnostic.severity.value.lower() == "error"
                if hasattr(diagnostic.severity, "value")
                else str(diagnostic.severity).lower() == "error"
            )
        ]
        if errors:
            details = "; ".join(f"{d.rule}: {d.message}" for d in errors)
            raise ValueError(
                f"{co.candidate_id} is invalid after applying declared author intent: {details}"
            )

        warnings = [
            diagnostic
            for diagnostic in diagnostics
            if (
                diagnostic.severity.value.lower() == "warning"
                if hasattr(diagnostic.severity, "value")
                else str(diagnostic.severity).lower() == "warning"
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


def _intent_candidate_evidence(co: Any) -> dict[str, Any]:
    evidence = _candidate_evidence(co)
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
) -> LLMRequest:
    evidence = [_intent_candidate_evidence(co) for co in candidate_outputs]
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
        max_tokens=1600,
        temperature=0.2,
        model=None,
    )


def _build_intent_comparison_lines(data: Any, brief: DiscoveryBrief) -> list[str]:
    """Rebuild comparison evidence after explicit brief commitments are attached."""
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
    if intent_aware:
        qualified.insert(
            1,
            "Intent-aware recommendation against your declared Discovery Brief.",
        )
        return qualified

    qualified.insert(
        1,
        "Exploratory recommendation using Auteur's default criteria; no structured "
        "Discovery Brief was supplied, so this is not a claim about undeclared author intent.",
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
            "This comparison is judged against the structured author brief supplied before "
            "candidate generation.\n"
            if brief is not None
            else "This is exploratory ranking under Auteur's default criteria because no "
            "structured author brief was supplied.\n"
        )
    )
    comparison_path.write_text(comparison + "\n" + heading, encoding="utf-8")


def dispatch_story_discovery_recommend(args: Any) -> int:
    """Run exploratory or intent-aware Story Discovery with F2 evidence boundaries."""

    if args.candidates < 2:
        _err("Story Discovery --recommend requires --candidates >= 2 so a narrative search actually occurs.")
        return 1

    from auteur.cli_handlers import RecommendOpenEndedData, handle_identity_recommend
    from auteur.cli_serializers import serialize_story_discovery
    from auteur.llm.factory import build_client

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
    client = _BriefAwareClient(base_client, brief) if brief is not None else base_client
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
        print("Revise the brief or premise and run again.", file=sys.stderr)
        return 1

    try:
        contract_args = SimpleNamespace(project=args.project, genre=genre)
        _refresh_project_contract(candidate_outputs, contract_args)
        _refresh_content_hashes(candidate_outputs)
        _require_distinct_engines(candidate_outputs)
        if len(candidate_outputs) == 1:
            winner, rationale, rejected = _single_survivor(
                candidate_outputs[0].candidate_id,
                args.candidates,
            )
        elif brief is not None:
            response = base_client.complete(_build_intent_judge_request(brief, candidate_outputs))
            winner, rationale, rejected = _parse_judgment(
                response.text,
                [co.candidate_id for co in candidate_outputs],
            )
        else:
            response = base_client.complete(
                _build_judge_request(
                    premise_text,
                    candidate_outputs,
                    genre=genre,
                    medium=medium,
                    mode=mode,
                )
            )
            winner, rationale, rejected = _parse_judgment(
                response.text,
                [co.candidate_id for co in candidate_outputs],
            )
    except Exception as exc:
        _err(f"Failed to produce comparative Story Discovery recommendation: {exc}")
        return 1

    data.rec_set.recommended_candidate_id = winner
    written = serialize_story_discovery(data, args.output, source_input)
    surface_lines = _recommendation_surface_lines(
        winner=winner,
        rationale=rationale,
        rejected=rejected,
        candidate_outputs=candidate_outputs,
        output_dir=args.output,
        requested_candidates=args.candidates,
    )
    surface_lines = _qualify_surface(surface_lines, intent_aware=brief is not None)
    _augment_artifacts(
        args.output,
        winner=winner,
        rationale=rationale,
        rejected=rejected,
        surface_lines=surface_lines,
    )
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
