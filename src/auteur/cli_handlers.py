"""CLI command handler types and interface.

The handler layer separates domain orchestration from argument parsing and I/O.
Each handler is a pure function: accepts typed domain objects, returns a
HandlerResult. Formatters and serializers consume the result — handlers never
print or write files.

Usage:
    result = handle_structure_diagnose(blueprint)
    if result.is_success:
        output = format_diagnose(result)
    else:
        output = format_error(result)
"""

from __future__ import annotations

import datetime
import hashlib
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from auteur.blueprint import StoryBlueprint, Genre, StoryMedium, StoryMode
from auteur.cartographer_compiler import validate_outline
from auteur.identity import (
    StoryIdentity,
    StoryIdentityCandidate,
    StoryIdentityRecommendationSet,
    BestBasis,
    RecommendationMode,
    compile_to_blueprint,
)
from auteur.llm import LLMClient, LLMRequest
from auteur.pipeline import PipelineRunner
from auteur.project import Project
from auteur.structure import DiagnosticSeverity, analyze_structure
from auteur.structure.generator import GenerationProposal
from auteur.structure.proposals import (
    StructureProposal,
    apply_proposal_to_blueprint,
    propose_repairs_from_diagnostics,
)
import json

from auteur.bible import StoryBible
from auteur.critic import ValidationReport
from auteur.structure.analyzer import run_all_diagnostics
from auteur.structure.diagnostics import DiagnosticLayer, StructureDiagnostic
from auteur.structure.proposal_resolution import load_resolved_rules, resolve_proposal
from auteur.structure.proposals import write_audit_repair_proposals
from auteur.structure.state import (
    state_canon,
    state_check,
    state_confirm,
    state_prepare,
    state_update,
)


@dataclass
class HandlerResult:
    """Structured result from a CLI command handler.

    Attributes:
        exit_code: Process exit code (0 = success, non-zero = error/abnormal).
        data: Structured data for formatters and serializers. Shape depends on
            the specific command. None when command failed or returned no data.
        error: Human-readable error message when exit_code != 0. None on success.
        is_success: True when exit_code == 0.
    """

    exit_code: int = 0
    data: Any = None
    error: str | None = None

    def __post_init__(self) -> None:
        if self.error is None and self.exit_code != 0:
            self.error = f"Command failed with exit code {self.exit_code}"

    @property
    def is_success(self) -> bool:
        return self.exit_code == 0

    @classmethod
    def success(cls, data: Any = None) -> HandlerResult:
        """Create a success result with optional structured data."""
        return cls(exit_code=0, data=data)

    @classmethod
    def failure(cls, message: str, exit_code: int = 1) -> HandlerResult:
        """Create a failure result with a message and non-zero exit code."""
        return cls(exit_code=exit_code, error=message)


# ---------------------------------------------------------------------------
# Typed data containers for handler return values
# ---------------------------------------------------------------------------


@dataclass
class IdentityValidateData:
    """Structured data returned by handle_identity_validate."""
    diagnostics: list  # list of StructureDiagnostic
    has_error: bool
    report: dict  # JSON-serializable report


@dataclass
class CompileBlueprintData:
    """Structured data returned by handle_compile_to_blueprint."""
    blueprint: StoryBlueprint


@dataclass
class PlanData:
    """Structured data returned by handle_plan."""
    system_prompt: str
    user_message: str


@dataclass
class RecommendOpinionatedData:
    """Structured data for opinionated recommend mode."""
    identity: StoryIdentity
    warnings: list[str] = field(default_factory=list)
    debug_logs: list[dict] = field(default_factory=list)

@dataclass
class CandidateOutput:
    """A generated candidate identity and its serialized YAML content."""
    candidate_id: str
    yaml_content: str
    identity: StoryIdentity
    candidate: StoryIdentityCandidate


@dataclass
class RecommendOpenEndedData:
    """Structured data for open-ended recommend mode."""
    candidates: list[CandidateOutput]
    rec_set: StoryIdentityRecommendationSet
    comparison_lines: list[str]


DEFAULT_DISCOVERY_LENSES = ["emotional_payoff", "commercial_clarity", "thematic_coherence"]


_LENS_TO_BASIS = {
    "emotional_payoff": BestBasis.EMOTIONALLY_POWERFUL,
    "commercial_clarity": BestBasis.GENRE_ALIGNED,
    "thematic_coherence": BestBasis.STRUCTURALLY_COHERENT,
    "genre_aligned": BestBasis.GENRE_ALIGNED,
    "structurally_coherent": BestBasis.STRUCTURALLY_COHERENT,
    "faithful_to_input": BestBasis.FAITHFUL_TO_INPUT,
    "emotionally_powerful": BestBasis.EMOTIONALLY_POWERFUL,
    "character": BestBasis.EMOTIONALLY_POWERFUL,
    "thriller": BestBasis.GENRE_ALIGNED,
    "experimental": BestBasis.FAITHFUL_TO_INPUT,
    "literary": BestBasis.STRUCTURALLY_COHERENT,
    "commercial": BestBasis.GENRE_ALIGNED,
    "theme": BestBasis.STRUCTURALLY_COHERENT,
}


_LENS_RATIONALES = {
    "emotional_payoff": "Explore the interpretation that maximizes the strongest reader feeling.",
    "commercial_clarity": "Explore the interpretation with the clearest market and genre promise.",
    "thematic_coherence": "Explore the interpretation with the cleanest central argument.",
    "character": "Explore the interpretation where character agency and change carry the story.",
    "thriller": "Explore the interpretation with the strongest pressure, escalation, and urgency.",
    "experimental": "Explore the least conventional structurally valid interpretation.",
    "literary": "Explore the interpretation with the strongest interiority and thematic texture.",
    "commercial": "Explore the interpretation with the broadest audience promise.",
    "theme": "Explore the interpretation where theme drives the architecture.",
    "genre_aligned": "Explore the interpretation that best satisfies the declared genre contract.",
    "structurally_coherent": "Explore the interpretation with the cleanest causal story engine.",
    "faithful_to_input": "Explore the interpretation that preserves the premise's most specific details.",
    "emotionally_powerful": "Explore the interpretation with the highest emotional pressure.",
}


def _severity_value(diagnostic: Any) -> str:
    severity = getattr(diagnostic, "severity", "")
    return severity.value if hasattr(severity, "value") else str(severity)


def _candidate_contract_text(identity: StoryIdentity) -> str:
    pieces = [
        identity.title,
        identity.core_answer,
        identity.target_experience.primary,
        identity.target_experience.progression,
        identity.central_engine.want,
        identity.central_engine.resistance,
        identity.central_engine.conflict,
        identity.central_engine.stakes,
        identity.central_engine.change,
        *identity.not_this,
        *identity.open_questions,
        *identity.alternatives,
    ]
    return " ".join(p for p in pieces if p).casefold()


def _contract_phrase_present(phrase: str, haystack: str) -> bool:
    words = [w for w in re.findall(r"[a-z0-9]+", phrase.casefold()) if len(w) > 3]
    if not words:
        return True
    return any(word in haystack for word in words[:4])


def analyze_contract_fit(identity: StoryIdentity) -> tuple[int, str, list[str], list[str]]:
    """Return deterministic contract-fit metadata for a candidate identity.

    Contract fit is compliance analysis, not a quality score.
    """
    diagnostics = identity.validate_identity()
    problems: list[str] = []
    notes: list[str] = []
    fit = 100

    for diagnostic in diagnostics:
        severity = _severity_value(diagnostic).lower()
        message = str(getattr(diagnostic, "message", ""))
        if severity == "error":
            fit -= 35
            problems.append(message)
        elif severity == "warning":
            fit -= 10
            notes.append(message)

    contract = identity.genre_contract_snapshot
    text = _candidate_contract_text(identity)
    if contract:
        for trope in contract.required_tropes:
            if not _contract_phrase_present(trope, text):
                fit -= 8
                problems.append(f"Required genre trope may be under-specified: {trope}")
        for mismatch in contract.forbidden_mismatches:
            if _contract_phrase_present(mismatch, text):
                fit -= 12
                problems.append(f"Potential forbidden mismatch appears in candidate: {mismatch}")
        for failure_mode in contract.common_failure_modes[:3]:
            if _contract_phrase_present(failure_mode, text):
                fit -= 6
                notes.append(f"Watch for common {contract.display_name} failure mode: {failure_mode}")
        if not problems:
            notes.append(f"Fits the declared {contract.display_name} contract without deterministic errors.")

    fit = max(0, min(100, fit))
    if fit >= 80:
        status = "strong"
    elif fit >= 55:
        status = "mixed"
    else:
        status = "weak"
    return fit, status, problems, notes


# ---------------------------------------------------------------------------
# Handler: identity validate
# ---------------------------------------------------------------------------


def handle_identity_validate(identity: StoryIdentity) -> HandlerResult:
    """Validate a StoryIdentity and return diagnostics.

    Returns IdentityValidateData with diagnostics, has_error flag, and
    a JSON-serializable report dict.
    """
    try:
        diagnostics = identity.validate_identity()
    except Exception as exc:
        return HandlerResult.failure(f"Validation failed: {exc}")

    has_error = any(
        (d.severity.value.lower() == "error" if hasattr(d.severity, "value") else str(d.severity).lower() == "error")
        for d in diagnostics
    )

    report = {"diagnostics": [d.model_dump(mode="json") for d in diagnostics]}

    return HandlerResult.success(
        data=IdentityValidateData(
            diagnostics=list(diagnostics),
            has_error=has_error,
            report=report,
        )
    )


# ---------------------------------------------------------------------------
# Handler: compile identity to blueprint
# ---------------------------------------------------------------------------


def handle_compile_to_blueprint(identity: StoryIdentity) -> HandlerResult:
    """Compile a StoryIdentity into a StoryBlueprint.

    Returns CompileBlueprintData with the compiled blueprint.
    Also validates before compiling — returns failure if validation errors exist.
    """
    try:
        diagnostics = identity.validate_identity()
    except Exception as exc:
        return HandlerResult.failure(f"Validation failed: {exc}")

    has_error = any(
        (d.severity.value.lower() == "error" if hasattr(d.severity, "value") else str(d.severity).lower() == "error")
        for d in diagnostics
    )
    if has_error:
        error_details = []
        for d in diagnostics:
            sev = d.severity.value.upper() if hasattr(d.severity, "value") else str(d.severity).upper()
            if sev == "ERROR":
                error_details.append(f"[{sev}] Rule: {d.rule} | Message: {d.message}")
        return HandlerResult.failure(
            "StoryIdentity contains structural validation errors:\n" + "\n".join(error_details)
        )

    try:
        blueprint = compile_to_blueprint(identity)
    except Exception as exc:
        return HandlerResult.failure(f"Failed to compile identity to blueprint: {exc}")

    return HandlerResult.success(data=CompileBlueprintData(blueprint=blueprint))


# ---------------------------------------------------------------------------
# Handler: identity promote (accept-candidate)
# ---------------------------------------------------------------------------


@dataclass
class PromoteData:
    """Structured data returned by handle_identity_promote."""
    diagnostics: list  # list of StructureDiagnostic
    has_errors: bool
    warnings: list  # warning diagnostics


def handle_identity_promote(identity: StoryIdentity) -> HandlerResult:
    """Validate a candidate identity for promotion.

    Returns PromoteData with validation results and warnings.
    Does NOT write or copy files — CLI layer handles I/O.
    """
    try:
        diagnostics = identity.validate_identity()
    except Exception as exc:
        return HandlerResult.failure(f"Failed to parse candidate: {exc}")

    errors = [
        d for d in diagnostics
        if (d.severity.value.lower() == "error" if hasattr(d.severity, "value") else str(d.severity).lower() == "error")
    ]
    warnings = [
        d for d in diagnostics
        if (d.severity.value.lower() == "warning" if hasattr(d.severity, "value") else str(d.severity).lower() == "warning")
    ]

    if errors:
        return HandlerResult.failure(
            "Candidate failed structural validation.",
            data=PromoteData(diagnostics=list(diagnostics), has_errors=True, warnings=list(warnings)),
        )

    return HandlerResult.success(
        data=PromoteData(diagnostics=list(diagnostics), has_errors=False, warnings=list(warnings)),
    )


# ---------------------------------------------------------------------------
# Handler: init
# ---------------------------------------------------------------------------


def handle_init(blueprint: StoryBlueprint, project_path: Path, force: bool = False) -> HandlerResult:
    """Initialize a project from a blueprint.

    Validates the blueprint and creates the project directory structure.
    Does NOT handle --force safety checks (filesystem I/O) — CLI layer does that.
    """
    try:
        Project.init(project_path, blueprint)
    except Exception as exc:
        return HandlerResult.failure(f"Failed to initialize project: {exc}")

    return HandlerResult.success()


# ---------------------------------------------------------------------------
# Handler: plan
# ---------------------------------------------------------------------------


def handle_plan(blueprint: StoryBlueprint, chapter_index: int) -> HandlerResult:
    """Render the cartographer prompt for a chapter (no LLM call).

    Returns PlanData with system_prompt and user_message.
    """
    try:
        result = PipelineRunner(blueprint).plan_chapter(chapter_index)
    except Exception as exc:
        return HandlerResult.failure(f"Failed to plan chapter: {exc}")

    return HandlerResult.success(
        data=PlanData(system_prompt=result.system_prompt, user_message=result.user_message)
    )


# ---------------------------------------------------------------------------
# Handler: cartographer compile
# ---------------------------------------------------------------------------


def handle_cartographer_compile(
    blueprint_path: Path,
    llm: LLMClient,
    output_path: Path,
    split: bool = True,
) -> HandlerResult:
    """Compile a cartographer outline using the given LLM client.

    NOTE: This calls compile_outline which performs its own file I/O.
    The handler wraps it with error handling for CLI consumption.
    """
    from auteur.cartographer_compiler import compile_outline

    project_path = output_path.parent
    try:
        compile_outline(
            project_path=project_path,
            blueprint_path=blueprint_path,
            output_path=output_path,
            split_output=split,
            llm=llm,
        )
    except Exception as exc:
        return HandlerResult.failure(f"Failed to compile outline: {exc}")

    return HandlerResult.success()


# ---------------------------------------------------------------------------
# Handler: cartographer validate
# ---------------------------------------------------------------------------


def handle_cartographer_validate(
    outline_path: Path,
    blueprint_path: Path | None = None,
) -> HandlerResult:
    """Validate a cartographer outline.

    Wraps validate_outline with error handling for CLI consumption.
    """
    try:
        validate_outline(outline_path, blueprint_path)
    except FileNotFoundError:
        return HandlerResult.failure(f"Outline file not found: {outline_path}")
    except Exception as exc:
        return HandlerResult.failure(f"Outline validation failed: {exc}")

    return HandlerResult.success()


# ---------------------------------------------------------------------------
# Handler: identity recommend
# ---------------------------------------------------------------------------


def _extract_yaml_block(text: str) -> str:
    """Extract YAML from an LLM response containing markdown code fences."""
    match = re.search(r"```(?:yaml|json)?\n(.*?)```", text, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()
    match = re.search(r"```\n(.*?)```", text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return text.strip()


def handle_identity_recommend(
    client: LLMClient,
    premise_text: str,
    genre: str | None = None,
    medium: str | None = None,
    mode: str | None = None,
    recommend_mode: str = "opinionated",
    candidates_count: int = 3,
    discovery_lenses: list[str] | None = None,
    strict_candidate_count: bool = False,
    debug: bool = False,
    timestamp: str | None = None,
    project_path: Path | None = None,
) -> HandlerResult:
    """Generate story identity recommendations from a premise text.

    Pure logic handler — does NOT print, write files, or interact with the
    filesystem for output. Returns structured RecommendOpinionatedData or
    RecommendOpenEndedData for the CLI layer to serialize.
    """
    if timestamp is None:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    from auteur.identity import StoryIdentity
    from auteur.genres.registry import load_genre_contract, load_project_genre_contract
    from auteur.genres.subgenres import load_subgenre_modifier
    from auteur.structure.diagnostics import StructureDiagnostic, DiagnosticSeverity, DiagnosticLayer, RepairOptions

    # Resolve premise text (already done by CLI, but support Path strings)
    resolved_premise = premise_text

    # Load primary genre contract if constrained
    genre_guidance = ""
    if genre:
        try:
            genre_key = genre.lower().strip()
            try:
                Genre(genre_key)
            except ValueError:
                return HandlerResult.failure(
                    f"Custom genre '{genre_key}' is not supported as a canonical StoryIdentity genre in V1; use a built-in genre or 'other'."
                )
            contract = (
                load_project_genre_contract(project_path, genre_key)
                if project_path is not None
                else load_genre_contract(Genre(genre_key))
            )
            if contract:
                genre_guidance = f"""
Primary Genre Contract Details ({contract.display_name}):
- Audience Product: {contract.audience_product}
- Core Truth: {contract.core_truth}
- Required Tropes: {", ".join(contract.required_tropes)}
- Forbidden Mismatches: {", ".join(contract.forbidden_mismatches)}
"""
        except Exception:
            pass

    genres_list = [g.value for g in Genre]
    mediums_list = [m.value for m in StoryMedium]
    modes_list = [o.value for o in StoryMode]

    # --- Helper: generate a single candidate ---
    def _generate_candidate(
        basis: BestBasis,
        index: int,
        lens: str | None = None,
        attempt_limit: int = 4,
    ) -> tuple[StoryIdentity | None, list[str], list[dict]]:
        """Generate a single candidate identity. Returns (identity, warnings, debug_logs)."""
        basis_guideline = ""
        if basis == BestBasis.GENRE_ALIGNED:
            basis_guideline = "Optimize for the primary genre contract promise, core truth, required tropes, and audience expectations."
        elif basis == BestBasis.STRUCTURALLY_COHERENT:
            basis_guideline = "Optimize for tight conflict escalation, causal plot momentum, want/change transformational alignment, and subplot discipline."
        elif basis == BestBasis.FAITHFUL_TO_INPUT:
            basis_guideline = "Optimize for preserving the literal details, quirky eccentricities, and specific tone of the author's original premise without over-commercializing or genericizing it."
        elif basis == BestBasis.EMOTIONALLY_POWERFUL:
            basis_guideline = "Maximize emotional stakes, cathartic affect, target emotional trajectories, and character psychological depth within the genre's psychology budget."
        if lens:
            lens_guidance = _LENS_RATIONALES.get(
                lens,
                f"Explore the '{lens}' region of the premise's narrative design space.",
            )
            basis_guideline += f"\n\nStory Discovery Lens ('{lens}'):\n{lens_guidance}\nGenerate a candidate that is architecturally distinct because of this lens."

        system_prompt = f"""You are an expert, opinionated narrative compiler. Your job is to take a raw creative premise/idea and translate it into a single, cohesive, structurally sound recommended story identity.

You must recommend exactly one direction (choose the best-suited genre, medium, and mode) for this story to maximize its narrative potential. Do not be vague or generic.

Optimization Lens (best_basis: '{basis.value}'):
{basis_guideline}

The available genres, mediums, and modes are:
Genres:
{", ".join(genres_list)}

Mediums:
{", ".join(mediums_list)}

Modes:
{", ".join(modes_list)}

{genre_guidance}

Note on Genre Runway constraints:
Each genre has a minimum viable length requirement. For instance, epic fantasy, mystery, or thrillers typically require a longer medium (e.g. novel, novella) rather than a short story. If you specify a genre, ensure the medium matches or exceeds its runway requirements, unless you specify runway_compression in author_overrides.

Here are the rules for a valid StoryIdentity:
1. The 'change' field in central_engine must describe a genuine transformation (how the protagonist/world changes after the conflict) and MUST NOT duplicate or merely restate the 'want' field.
2. The chosen mode must be compatible with the genre's ending tone restrictions. For example, Romance forbids tragic endings.
3. The 'target_experience.avoid' list must NOT contain the primary emotional experience or any progression steps.

Your response must contain ONLY a single YAML code block defining the recommended story identity matching the following schema structure:

```yaml
title: "Title of the Story"
core_answer: "One sentence summarizing the premise, main thread conflict, and resolution."
target_experience:
  primary: "the primary emotion/experience to evoke"
  progression: "emotion1 -> emotion2 -> emotion3"
  avoid:
    - "avoided emotion1"
story_type:
  medium: "medium_value"
  mode: "mode_value"
  genre: "genre_value"
  subgenres:
    - "subgenre1"
  target_audience: "adult"
  length_class: null
central_engine:
  want: "What the protagonist desperately wants."
  resistance: "The chief force resisting that want."
  conflict: "The clash between want and resistance."
  stakes: "What is lost if they fail."
  change: "How they/the world are transformed after the conflict."
not_this:
  - "what this story should not be"
open_questions:
  - "open questions to resolve"
confidence: 0.95
alternatives:
  - "alternative direction 1"
recommendation_mode: "{recommend_mode}"
best_basis: "{basis.value}"
why_this_is_best: "Explanation of why this specific setup is best optimized for this lens."
rejected_directions:
  - "rejected direction 1"
author_overrides: []
```

Make sure the output is valid YAML, contains no conversational preamble/postamble, and strictly adheres to the schema.
"""

        constraints_text = []
        if genre:
            constraints_text.append(f"Constraint: You MUST set story_type.genre to '{genre}'.")
        if medium:
            constraints_text.append(f"Constraint: You MUST set story_type.medium to '{medium}'.")
        if mode:
            constraints_text.append(f"Constraint: You MUST set story_type.mode to '{mode}'.")

        constraints_str = "\n".join(constraints_text)
        user_prompt = f"Raw Premise:\n{resolved_premise}\n\n{constraints_str}\n\nPlease generate the story identity recommendation YAML block."

        last_output = ""
        validation_feedback = ""
        debug_logs: list[dict] = []

        for attempt in range(1, attempt_limit + 1):
            try:
                if attempt == 1:
                    req_user = user_prompt
                else:
                    req_user = (
                        user_prompt
                        + f"\n\n--- PREVIOUS ATTEMPT OUTPUT ---\n{last_output}\n\n"
                        + f"--- VALIDATION ERRORS ---\n{validation_feedback}\n\n"
                        + "Please correct the errors and output ONLY the corrected YAML block. "
                        + "You MUST NOT add items to 'author_overrides' to bypass these validation errors. "
                        + "Resolve them by correcting the actual content fields."
                    )

                req = LLMRequest(
                    system=system_prompt,
                    user=req_user,
                    max_tokens=4096,
                    temperature=0.7,
                    model=None,
                )

                response = client.complete(req)
                last_output = response.text

                yaml_text = _extract_yaml_block(last_output)
                data = yaml.safe_load(yaml_text)
                if not isinstance(data, dict):
                    raise ValueError("LLM output is not a dictionary.")

                if "story_type" not in data or not isinstance(data["story_type"], dict):
                    data["story_type"] = {}
                if genre:
                    data["story_type"]["genre"] = genre
                if medium:
                    data["story_type"]["medium"] = medium
                if mode:
                    data["story_type"]["mode"] = mode

                identity = StoryIdentity.model_validate(data)

                # Refuse auto-overrides: LLM cannot inject overrides
                auto_overrides_detected = False
                if identity.author_overrides:
                    auto_overrides_detected = True
                    auto_override_diag = StructureDiagnostic(
                        severity=DiagnosticSeverity.ERROR,
                        layer=DiagnosticLayer.CONSTRAINTS,
                        rule="identity.auto_overrides_forbidden",
                        message="Generating auto-overrides is forbidden. Do not add overrides to 'author_overrides'. Resolve the underlying issue by changing the story elements.",
                        evidence=[f"author_overrides = {identity.author_overrides}"],
                        repair_options=RepairOptions(
                            preserve_intent=["Clear the author_overrides list and fix the underlying validation errors instead."],
                            challenge_intent=[]
                        )
                    )
                    identity.author_overrides = []

                diagnostics = identity.validate_identity()
                if auto_overrides_detected:
                    diagnostics.append(auto_override_diag)

                errors = [
                    d for d in diagnostics
                    if (d.severity.value.lower() == "error" if hasattr(d.severity, "value") else str(d.severity).lower() == "error")
                ]

                if not errors:
                    # Apply warning confidence penalty
                    warnings = [
                        d for d in diagnostics
                        if (d.severity.value.lower() == "warning" if hasattr(d.severity, "value") else str(d.severity).lower() == "warning")
                    ]
                    if warnings:
                        original_confidence = identity.confidence or 1.0
                        identity.confidence = max(0.10, round(original_confidence - 0.05 * len(warnings), 2))
                    return identity, [str(d.message) for d in diagnostics], debug_logs
                else:
                    err_lines = []
                    for err in errors:
                        err_lines.append(f"- Rule: {err.rule} | Message: {err.message}")
                    validation_feedback = "\n".join(err_lines)
                    debug_logs.append({
                        "attempt": attempt,
                        "basis": basis.value,
                        "index": index,
                        "type": "validation_error",
                        "feedback": validation_feedback,
                        "last_output": last_output,
                    })

            except Exception as exc:
                validation_feedback = f"Error during parsing/validation: {exc}"
                debug_logs.append({
                    "attempt": attempt,
                    "basis": basis.value,
                    "index": index,
                    "type": "exception",
                    "feedback": validation_feedback,
                    "last_output": last_output,
                    "exception": str(exc),
                })

        return None, [], debug_logs

    # --- Opinionated Mode ---
    if recommend_mode == "opinionated":
        identity, warnings, debug_logs = _generate_candidate(BestBasis.GENRE_ALIGNED, 1)
        if identity:
            return HandlerResult.success(
                data=RecommendOpinionatedData(identity=identity, warnings=warnings, debug_logs=debug_logs)
            )
        else:
            return HandlerResult.failure("Failed to generate a valid StoryIdentity after maximum retries.")

    # --- Open-Ended Mode ---
    elif recommend_mode == "open_ended":
        lenses = discovery_lenses or DEFAULT_DISCOVERY_LENSES
        if candidates_count > len(lenses):
            lenses = [*lenses]
            while len(lenses) < candidates_count:
                lenses.append(DEFAULT_DISCOVERY_LENSES[len(lenses) % len(DEFAULT_DISCOVERY_LENSES)])
        else:
            lenses = lenses[:candidates_count]

        labels_mapping = {
            "emotional_payoff": "Emotional payoff",
            "commercial_clarity": "Commercial clarity",
            "thematic_coherence": "Thematic coherence",
            "character": "Character-first",
            "thriller": "Thriller pressure",
            "experimental": "Experimental interpretation",
            "literary": "Literary depth",
            "commercial": "Commercial appeal",
            "theme": "Theme-first",
            "genre_aligned": "Genre-contract benchmark",
            "structurally_coherent": "Cleanest story engine",
            "faithful_to_input": "Most faithful / most idiosyncratic",
            "emotionally_powerful": "Highest affect / character-pressure",
        }

        candidate_outputs: list[CandidateOutput] = []
        valid_count = 0

        for idx in range(1, candidates_count + 1):
            lens = lenses[idx - 1]
            basis = _LENS_TO_BASIS.get(lens, BestBasis.GENRE_ALIGNED)
            identity, diagnostics_messages, _ = _generate_candidate(basis, idx, lens=lens)

            candidate_id = f"candidate_{idx}"

            if identity:
                yaml_content = yaml.safe_dump(identity.model_dump(mode="json"), sort_keys=False)
                content_hash = "sha256:" + hashlib.sha256(yaml_content.encode("utf-8")).hexdigest()

                valid_count += 1
                status = "valid" if not diagnostics_messages else "valid_with_warnings"

                label = labels_mapping.get(lens, lens.replace("_", " ").title())
                contract_fit, contract_fit_status, fit_problems, fit_notes = analyze_contract_fit(identity)

                candidate = StoryIdentityCandidate(
                    candidate_id=candidate_id,
                    path="",  # CLI fills in the actual path
                    label=label,
                    best_basis=basis,
                    lens=lens,
                    lens_rationale=_LENS_RATIONALES.get(
                        lens,
                        f"Explore the '{lens}' region of the premise's narrative design space.",
                    ),
                    recommendation_summary=identity.why_this_is_best or "No summary available.",
                    tradeoffs=[],
                    risks=[],
                    best_for=[],
                    validation_status=status,
                    warning_count=len(diagnostics_messages),
                    contract_fit=contract_fit,
                    contract_fit_status=contract_fit_status,
                    contract_fit_problems=fit_problems,
                    contract_fit_notes=fit_notes,
                    content_hash=content_hash,
                )

                candidate_outputs.append(
                    CandidateOutput(
                        candidate_id=candidate_id,
                        yaml_content=yaml_content,
                        identity=identity,
                        candidate=candidate,
                    )
                )
            else:
                if strict_candidate_count:
                    return HandlerResult.failure(
                        f"Candidate {idx} ({basis.value}) failed to validate after maximum retries "
                        "and strict_candidate_count is active."
                    )

        if valid_count == 0:
            return HandlerResult.failure("0 valid candidates survived validation checks.")

        # Generate LLM summaries for candidates
        for co in candidate_outputs:
            try:
                sum_req = LLMRequest(
                    system="You are an assistant summarizing a story identity. Provide a concise 1-sentence recommendation summary, a list of 2 key tradeoffs, 2 risks, and 2 ideal scenarios this candidate is best for. Output ONLY valid JSON structure: {\"summary\": \"...\", \"tradeoffs\": [\"...\", \"...\"], \"risks\": [\"...\", \"...\"], \"best_for\": [\"...\", \"...\"]}",
                    user=f"Story Identity:\n{co.yaml_content}",
                    max_tokens=500,
                    temperature=0.3,
                    model=None,
                )
                summary_resp = client.complete(sum_req).text
                json_match = re.search(r"(\{.*\})", summary_resp, re.DOTALL)
                s_data = json.loads(json_match.group(1)) if json_match else {}
            except Exception:
                s_data = {}

            co.candidate.recommendation_summary = s_data.get("summary", co.identity.why_this_is_best or "No summary available.")
            co.candidate.tradeoffs = s_data.get("tradeoffs", [])
            co.candidate.risks = s_data.get("risks", [])
            co.candidate.best_for = s_data.get("best_for", [])

        # Build recommendation set
        rec_set = StoryIdentityRecommendationSet(
            mode=RecommendationMode.OPEN_ENDED,
            source_input_path="",  # CLI fills from premise
            generated_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
            requested_candidates=candidates_count,
            valid_candidates=valid_count,
            search_strategy="Narrative Search",
            design_lenses=lenses,
            recommended_candidate_id=None,
            candidates=[co.candidate for co in candidate_outputs],
        )

        # Build comparison lines
        comparison_lines = [
            "# Story Discovery Comparison",
            f"\nSource Premise File/Text: ``",
            f"Generated At: {rec_set.generated_at}\n",
            "Contract fit measures compliance with the declared genre and structural contract. It is not a story-quality ranking.\n",
            "## Search Strategy",
            f"Narrative Search across design lenses: {', '.join(lenses)}.\n",
            "## Architectural Matrix",
            "| Dimension | " + " | ".join(co.candidate.candidate_id for co in candidate_outputs) + " |",
            "| --- | " + " | ".join("---" for _ in candidate_outputs) + " |",
            "| Lens | " + " | ".join(co.candidate.lens for co in candidate_outputs) + " |",
            "| Emotional promise | " + " | ".join(co.identity.target_experience.primary for co in candidate_outputs) + " |",
            "| Primary engine | " + " | ".join(co.identity.central_engine.conflict for co in candidate_outputs) + " |",
            "| Character agency | " + " | ".join("High" if len(co.identity.central_engine.want) > 20 else "Medium" for co in candidate_outputs) + " |",
            "| Structural complexity | " + " | ".join(co.identity.story_type.medium.value for co in candidate_outputs) + " |",
            "| Series potential | " + " | ".join("High" if co.identity.story_type.medium.value in {"series", "novel"} else "Moderate" for co in candidate_outputs) + " |",
            "| Reader expectation | " + " | ".join(co.identity.story_type.genre.value for co in candidate_outputs) + " |",
            "| Contract fit | " + " | ".join(f"{co.candidate.contract_fit} ({co.candidate.contract_fit_status})" for co in candidate_outputs) + " |",
            "| Risk profile | " + " | ".join((co.candidate.risks[0] if co.candidate.risks else "Not yet summarized") for co in candidate_outputs) + " |",
            "\n## Architectural Interpretations\n",
            "| Candidate | Lens | Genre | Contract Fit | Summary |",
            "| --- | --- | --- | --- | --- |"
        ]
        for co in candidate_outputs:
            c = co.candidate
            comparison_lines.append(f"| `{c.candidate_id}` | **{c.lens}** ({c.label}) | {co.identity.story_type.genre.value} | {c.contract_fit} ({c.contract_fit_status}) | {c.recommendation_summary} |")

        comparison_lines.append("\n## Tradeoffs & Risks\n")
        for co in candidate_outputs:
            c = co.candidate
            comparison_lines.append(f"### {c.candidate_id}: {c.label}")
            comparison_lines.append(f"**Lens**: `{c.lens}`")
            comparison_lines.append(f"**Why this interpretation exists**: {c.lens_rationale}")
            comparison_lines.append(f"**Summary**: {c.recommendation_summary}")
            comparison_lines.append(f"**Contract fit**: {c.contract_fit} ({c.contract_fit_status})")
            if c.contract_fit_problems:
                comparison_lines.append("\n*Contract Fit Problems*:")
                for p in c.contract_fit_problems:
                    comparison_lines.append(f"- {p}")
            if c.contract_fit_notes:
                comparison_lines.append("\n*Contract Fit Notes*:")
                for n in c.contract_fit_notes:
                    comparison_lines.append(f"- {n}")
            if c.tradeoffs:
                comparison_lines.append("\n*Tradeoffs*:")
                for t in c.tradeoffs:
                    comparison_lines.append(f"- {t}")
            if c.risks:
                comparison_lines.append("\n*Risks*:")
                for r in c.risks:
                    comparison_lines.append(f"- {r}")
            if c.best_for:
                comparison_lines.append("\n*Best For*:")
                for bf in c.best_for:
                    comparison_lines.append(f"- {bf}")
            comparison_lines.append(f"\nPromotion command: `auteur story-discovery accept {c.path or (c.candidate_id + '.yaml')} --output story_identity.yaml`")
            comparison_lines.append("")

        return HandlerResult.success(
            data=RecommendOpenEndedData(
                candidates=candidate_outputs,
                rec_set=rec_set,
                comparison_lines=comparison_lines,
            )
        )

    return HandlerResult.failure(f"Unknown recommend_mode: {recommend_mode}")


# ---------------------------------------------------------------------------
# Structure command handlers
# ---------------------------------------------------------------------------


def handle_structure_diagnose(blueprint: StoryBlueprint) -> HandlerResult:
    """Run structural analysis on a blueprint and return diagnostics.

    Returns structured data with diagnostics grouped by severity for the
    formatter to render as a human-readable summary or JSON artifact.
    """
    diagnostics = analyze_structure(blueprint)
    errors = [d for d in diagnostics if d.severity == DiagnosticSeverity.ERROR]
    warnings = [d for d in diagnostics if d.severity == DiagnosticSeverity.WARNING]
    infos = [d for d in diagnostics if d.severity == DiagnosticSeverity.INFO]
    return HandlerResult.success(
        data={
            "diagnostics": [d.model_dump(mode="json") for d in diagnostics],
            "errors": [d.model_dump(mode="json") for d in errors],
            "warnings": [d.model_dump(mode="json") for d in warnings],
            "infos": [d.model_dump(mode="json") for d in infos],
        }
    )


def handle_structure_propose_repairs(blueprint: StoryBlueprint) -> HandlerResult:
    """Analyze blueprint and generate repair proposals from diagnostics.

    Returns structured data containing both diagnostics and the derived
    repair proposals for the formatter to render or serialize.
    """
    diagnostics = analyze_structure(blueprint)
    proposals = propose_repairs_from_diagnostics(diagnostics)
    return HandlerResult.success(
        data={
            "diagnostics": [d.model_dump(mode="json") for d in diagnostics],
            "proposals": proposals,
            "diagnostic_count": len(diagnostics),
            "proposal_count": len(proposals),
        }
    )


def handle_structure_apply(
    proposal: StructureProposal,
    blueprint: StoryBlueprint,
    *,
    in_place: bool = False,
    output_dir: str | None = None,
    original_path: str | None = None,
) -> HandlerResult:
    """Apply a selected proposal to a blueprint.

    Validates the proposal state (must have a selected option), then delegates
    to apply_proposal_to_blueprint which performs the merge and writes the
    resulting blueprint file.

    Returns the target path and selection metadata for the caller to report.
    """
    if not proposal.selection.selected_option_id:
        return HandlerResult.failure(
            "proposal must include an accepted or selected option before apply"
        )

    option_ids = {option.id for option in proposal.options}
    if proposal.selection.selected_option_id not in option_ids:
        return HandlerResult.failure(
            f"selected_option_id {proposal.selection.selected_option_id!r} not found in proposal options"
        )

    try:
        _, target_path = apply_proposal_to_blueprint(
            proposal,
            blueprint,
            output_dir=output_dir,
            original_path=original_path,
            in_place=in_place,
        )
    except (ValueError, OSError, yaml.YAMLError) as exc:
        return HandlerResult.failure(f"failed to apply proposal: {exc}")

    return HandlerResult.success(
        data={
            "target_path": target_path,
            "selected_option_id": proposal.selection.selected_option_id,
            "in_place": in_place,
        }
    )


def handle_structure_generate(
    blueprint: StoryBlueprint,
    *,
    symptom: str | None = None,
) -> HandlerResult:
    """Generate a story engine from a blueprint, or diagnose from a symptom.

    Two modes:
    - Symptom-based (bottom-up): maps an author-described symptom to likely
      structural root causes using keyword matching.
    - Top-down generation: synthesizes structural forces and generates a
      story engine proposal (main thread + subordinate threads).
    """
    if symptom:
        from auteur.structure.generator import diagnose_symptom

        diagnoses = diagnose_symptom(symptom, blueprint=blueprint)
        if not diagnoses:
            return HandlerResult.failure(
                f"No structural diagnosis could be made for symptom: {symptom}"
            )
        return HandlerResult.success(
            data={
                "symptom": symptom,
                "diagnoses": [d.model_dump(mode="json") for d in diagnoses],
                "is_diagnostics": True,
            }
        )

    from auteur.structure.generator import generate_story_engine

    result = generate_story_engine(blueprint)
    if isinstance(result, list):
        return HandlerResult.success(
            data={
                "diagnostics": [d.model_dump(mode="json") for d in result],
                "is_diagnostics": True,
            }
        )

    proposal = result
    return HandlerResult.success(
        data={
            "proposal": proposal,
            "proposal_dict": proposal.model_dump(mode="json"),
            "is_diagnostics": False,
        }
    )


# ---------------------------------------------------------------------------
# Draft/accept/retry/audit handler result data types
# ---------------------------------------------------------------------------


@dataclass
class DraftResultData:
    """Structured data returned by handle_draft / handle_retry."""

    chapter_index: int
    accepted: bool
    iterations: int
    final_path: Path | None = None
    total_input_tokens: int = 0
    total_output_tokens: int = 0
    conflict_report: str | None = None
    critic_proposal_paths: list[Path] = field(default_factory=list)


@dataclass
class AcceptResultData:
    """Structured data returned by handle_accept."""

    chapter_index: int
    latest_draft_name: str
    summary: str = ""
    tension: int | None = None


@dataclass
class AuditResultData:
    """Structured data returned by handle_audit."""

    diagnostics: list[StructureDiagnostic]
    error_count: int
    warning_count: int
    resolved_proposal_count: int = 0
    artifact_path: Path | None = None
    repairs_written: bool = False


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _draft_version(path: Path) -> int:
    return int(path.stem.removeprefix("draft_v"))


def _sorted_drafts(chapter_dir: Path) -> list[Path]:
    return sorted(chapter_dir.glob("draft_v*.md"), key=_draft_version)


# ---------------------------------------------------------------------------
# Draft handler
# ---------------------------------------------------------------------------


def handle_draft(
    project: Project,
    chapter_index: int,
    max_iterations: int,
    llm: LLMClient,
) -> HandlerResult:
    """Draft a chapter through plan -> draft -> critique -> iterate pipeline.

    Returns structured result data with the outcome (accepted, rejected,
    or conflict). The caller handles all I/O.
    """
    runner = PipelineRunner(project.blueprint, bible=project.bible)

    result = runner.draft_chapter(
        chapter_index,
        llm=llm,
        project=project,
        max_iterations=max_iterations,
        on_iteration=None,
    )

    data = DraftResultData(
        chapter_index=chapter_index,
        accepted=result.accepted,
        iterations=result.iterations,
        final_path=result.final_path,
        total_input_tokens=result.total_input_tokens,
        total_output_tokens=result.total_output_tokens,
        conflict_report=result.conflict_report,
        critic_proposal_paths=list(result.critic_proposal_paths),
    )

    if result.conflict_report is not None:
        return HandlerResult(exit_code=3, data=data)

    if result.accepted:
        return HandlerResult.success(data=data)

    return HandlerResult(exit_code=2, data=data)


# ---------------------------------------------------------------------------
# Accept handler
# ---------------------------------------------------------------------------


def handle_accept(
    project: Project,
    chapter_index: int,
) -> HandlerResult:
    """Promote the latest draft to final.md and record the event in the bible.

    Returns structured data about what was accepted.
    """
    chapter_dir = project.chapter_dir(chapter_index)
    drafts = _sorted_drafts(chapter_dir)
    if not drafts:
        return HandlerResult.failure(f"No drafts found in {chapter_dir}")

    latest = drafts[-1]
    project.write_final(chapter_index, latest.read_text(encoding="utf-8"))

    outline_path = chapter_dir / "outline.yaml"
    summary = ""
    tension: int | None = None
    if outline_path.exists():
        outline = yaml.safe_load(outline_path.read_text(encoding="utf-8"))
        summary = outline.get("chapter_summary", "")
        t = outline.get("estimated_chapter_tension")
        if isinstance(t, int):
            tension = t

    project.bible.record_event(
        chapter_index=chapter_index,
        summary=summary,
        deltas={"manually_accepted": True},
    )
    if tension is not None:
        project.bible.record_tension(chapter_index, tension)
    project.bible.save()

    data = AcceptResultData(
        chapter_index=chapter_index,
        latest_draft_name=latest.name,
        summary=summary,
        tension=tension,
    )
    return HandlerResult.success(data=data)


# ---------------------------------------------------------------------------
# Retry handler
# ---------------------------------------------------------------------------


def handle_retry(
    project: Project,
    chapter_index: int,
    max_iterations: int,
    llm: LLMClient,
) -> HandlerResult:
    """Continue iterating on a chapter from the last draft + validation state.

    Loads the prior outline, latest draft, and previous validation report,
    then resumes drafting from where the last run left off.
    """
    chapter_dir = project.chapter_dir(chapter_index)
    outline_path = chapter_dir / "outline.yaml"

    if not outline_path.exists():
        return HandlerResult.failure(
            f"No outline found in {chapter_dir}; run auteur draft first."
        )

    outline = yaml.safe_load(outline_path.read_text(encoding="utf-8"))
    if not isinstance(outline, dict):
        return HandlerResult.failure(f"Invalid outline file: {outline_path}")

    drafts = _sorted_drafts(chapter_dir)
    if not drafts:
        return HandlerResult.failure(
            f"No drafts found in {chapter_dir}; run auteur draft first."
        )

    latest = drafts[-1]
    latest_version = _draft_version(latest)
    validation_path = chapter_dir / f"validation_v{latest_version}.json"

    if not validation_path.exists():
        return HandlerResult.failure(
            f"No validation found for {latest.name}: {validation_path}"
        )

    try:
        previous_report = ValidationReport.model_validate(
            json.loads(validation_path.read_text(encoding="utf-8"))
        )
    except (json.JSONDecodeError, ValueError) as exc:
        return HandlerResult.failure(
            f"Invalid validation file {validation_path}: {exc}"
        )

    runner = PipelineRunner(project.blueprint, bible=project.bible)
    result = runner.draft_chapter(
        chapter_index,
        llm=llm,
        project=project,
        max_iterations=max_iterations,
        on_iteration=None,
        initial_outline=outline,
        start_iteration=latest_version + 1,
        prior_draft=latest.read_text(encoding="utf-8"),
        prior_findings=previous_report.findings,
    )

    data = DraftResultData(
        chapter_index=chapter_index,
        accepted=result.accepted,
        iterations=result.iterations,
        final_path=result.final_path,
        total_input_tokens=result.total_input_tokens,
        total_output_tokens=result.total_output_tokens,
        conflict_report=result.conflict_report,
        critic_proposal_paths=list(result.critic_proposal_paths),
    )

    if result.conflict_report is not None:
        return HandlerResult(exit_code=3, data=data)
    if result.accepted:
        return HandlerResult.success(data=data)
    return HandlerResult(exit_code=2, data=data)


# ---------------------------------------------------------------------------
# Audit handler
# ---------------------------------------------------------------------------


def _parse_audit_layers(spec: str) -> set[DiagnosticLayer]:
    """Parse a --layers flag value into a set of DiagnosticLayer enums."""
    spec = spec.strip()
    if spec == "all":
        return set(DiagnosticLayer)

    parts = spec.split("-")
    if len(parts) == 2:
        try:
            start, end = int(parts[0]), int(parts[1])
        except ValueError:
            return set(DiagnosticLayer)
        layer_map = {
            1: DiagnosticLayer.TARGET_EXPERIENCE,
            2: DiagnosticLayer.CONSTRAINTS,
            3: DiagnosticLayer.SCOPE,
            4: DiagnosticLayer.STRUCTURAL_FORCES,
            5: DiagnosticLayer.THREADS,
            6: DiagnosticLayer.CARRIERS,
            7: DiagnosticLayer.REPRESENTATION,
            8: DiagnosticLayer.MODULATION,
            9: DiagnosticLayer.THEME,
        }
        return {v for k, v in layer_map.items() if start <= k <= end}

    if spec == "other":
        return {DiagnosticLayer.CARRIERS}

    try:
        layer_map = {
            "1": DiagnosticLayer.TARGET_EXPERIENCE,
            "2": DiagnosticLayer.CONSTRAINTS,
            "3": DiagnosticLayer.SCOPE,
            "4": DiagnosticLayer.STRUCTURAL_FORCES,
            "5": DiagnosticLayer.THREADS,
            "6": DiagnosticLayer.CARRIERS,
            "7": DiagnosticLayer.REPRESENTATION,
            "8": DiagnosticLayer.MODULATION,
            "9": DiagnosticLayer.THEME,
        }
        parts = spec.split(",")
        result: set[DiagnosticLayer] = set()
        for p in parts:
            p = p.strip()
            if p in layer_map:
                result.add(layer_map[p])
        return result
    except Exception:
        return set(DiagnosticLayer)


def handle_audit_resolve_proposal(
    project_path: Path,
    accept: str,
    option: str,
) -> HandlerResult:
    """Resolve an audit proposal by selecting an option."""
    exit_code = resolve_proposal(project_path, accept, option)
    if exit_code != 0:
        return HandlerResult.failure(
            f"Failed to resolve proposal '{accept}' with option '{option}'",
            exit_code=exit_code,
        )
    return HandlerResult.success(
        data={"proposal_id": accept, "option_id": option}
    )


def handle_audit(
    blueprint: StoryBlueprint,
    bible: StoryBible,
    project: Project,
    *,
    repair: bool = False,
    layers: str = "all",
) -> HandlerResult:
    """Run Bible Audit diagnostics and return structured results.

    The caller handles all I/O (writing reports, printing output).
    """
    resolved_rules: set[str] = load_resolved_rules(project.path)

    raw_diagnostics = run_all_diagnostics(blueprint, bible)
    diagnostics = [d for d in raw_diagnostics if d.rule not in resolved_rules]

    if not raw_diagnostics:
        return HandlerResult.success(
            data=AuditResultData(
                diagnostics=[],
                error_count=0,
                warning_count=0,
            )
        )

    if not diagnostics:
        return HandlerResult.success(
            data=AuditResultData(
                diagnostics=[],
                error_count=0,
                warning_count=0,
                resolved_proposal_count=0,
            )
        )

    # Layer filter for human-readable view
    if layers != "all":
        selected = _parse_audit_layers(layers)
        view_diagnostics = [d for d in diagnostics if d.layer in selected]
    else:
        view_diagnostics = diagnostics

    errors = sum(1 for d in view_diagnostics if d.severity.value == "error")
    warnings = sum(
        1 for d in view_diagnostics if d.severity.value == "warning"
    )

    # Count resolved proposals for footer
    proposals_dir = project.path / "structure" / "proposals"
    resolved_count = 0
    if proposals_dir.is_dir():
        for pf in sorted(proposals_dir.glob("*.yaml")):
            try:
                pd = yaml.safe_load(pf.read_text(encoding="utf-8"))
            except Exception:
                continue
            if isinstance(pd, dict):
                sel = pd.get("selection", {})
                if isinstance(sel, dict) and sel.get("selected_option_id"):
                    resolved_count += 1

    data = AuditResultData(
        diagnostics=view_diagnostics,
        error_count=errors,
        warning_count=warnings,
        resolved_proposal_count=resolved_count,
    )

    result_code = 1 if errors > 0 else 0
    return HandlerResult(exit_code=result_code, data=data)


# ---------------------------------------------------------------------------
# State command handler wrappers
# ---------------------------------------------------------------------------
# These wrap the existing state.py functions that still do inline printing
# and file writes. The wrappers convert their int exit codes to HandlerResult.
# Full handler extraction (separating domain from I/O) is deferred to a
# future task.


def handle_state_check(
    project_path: Path, *, outline: dict | None = None
) -> HandlerResult:
    """Run Structure Diagnostic and Bible Audit in one pass."""
    code = state_check(project_path, outline=outline)
    return HandlerResult(exit_code=code)


def handle_state_update(
    project_path: Path, file_path: Path, key: str, val_str: str
) -> HandlerResult:
    """Safe, transactional update of project file backed by schema validation."""
    code = state_update(project_path, file_path, key, val_str)
    return HandlerResult(exit_code=code)


def handle_state_prepare(
    project_path: Path,
    phase: str,
    scope: str,
    out_path: Path | None,
    chapter_idx: int | None,
) -> HandlerResult:
    """Compile context packets formatted according to strict handoff skeletons."""
    code = state_prepare(project_path, phase, scope, out_path, chapter_idx)
    return HandlerResult(exit_code=code)


def handle_state_canon(project_path: Path, format: str) -> HandlerResult:
    """Generate canonical reference manual output."""
    code = state_canon(project_path, format)
    return HandlerResult(exit_code=code)


def handle_state_confirm(
    project_path: Path, recovery_run_path: Path
) -> HandlerResult:
    """Validate and safely merge recovery run locked layers into blueprint/bible."""
    code = state_confirm(project_path, recovery_run_path)
    return HandlerResult(exit_code=code)
