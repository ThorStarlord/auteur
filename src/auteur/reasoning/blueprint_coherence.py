"""Deterministic blueprint-level coherence reasoning critic.

Analyzes the StoryBlueprint for:
- Structural coherence: do story_engine claims align with identity?
- Pacing targets: are act-level tension targets set?
- Thematic depth: is the theme expressed in the story_engine?
- Character arc completeness: do all characters have arcs?
- Chapter estimate vs scene density: does the structural budget match threads?

This critic is read-only and produces explainable, deterministic findings.
"""

from __future__ import annotations

from typing import Any

from .runtime import CriticRegistry, CriticSpec


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------


def register_blueprint_coherence_critic(registry: CriticRegistry) -> None:
    """Register the deterministic Blueprint Coherence reasoning critic."""
    registry.register(CriticSpec(
        critic_id="blueprint.coherence",
        version="1.0.0",
        input_keys=("blueprint",),
        run=run_blueprint_analysis,
    ))


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def run_blueprint_analysis(*, blueprint: Any, **_: Any) -> list[dict[str, Any]]:
    """Analyze the StoryBlueprint for coherence, pacing, and structural integrity.

    Parameters
    ----------
    blueprint : StoryBlueprint or dict
        The blueprint model instance or a dict with matching keys.

    Returns
    -------
    list[dict]
        A list of findings, each with rule, message, severity, evidence, hypotheses,
        and recommendations.
    """
    findings: list[dict[str, Any]] = []

    _check_structural_coherence(blueprint, findings)
    _check_pacing_targets(blueprint, findings)
    _check_thematic_depth(blueprint, findings)
    _check_character_arc_completeness(blueprint, findings)
    _check_chapter_density(blueprint, findings)

    return findings


# ---------------------------------------------------------------------------
# Polymorphic access helpers
# ---------------------------------------------------------------------------


def _get(obj: Any, key: str, default: Any = None) -> Any:
    """Access an attribute or dict key, returning *default* when missing/None."""
    if obj is None:
        return default
    if hasattr(obj, "__getitem__") and not hasattr(obj, "model_fields"):
        try:
            return obj[key]
        except (KeyError, TypeError, IndexError):
            return default
    return getattr(obj, key, default)


def _value_of(val: Any) -> Any:
    """Resolve enum-ish values to a plain string/int for serialization."""
    if val is None:
        return None
    if hasattr(val, "value"):
        return val.value
    if isinstance(val, dict) and "value" in val:
        return val["value"]
    return val


def _resolve(blueprint: Any, *keys: str) -> Any:
    """Follow a dotted path of keys through the blueprint."""
    current = blueprint
    for key in keys:
        current = _get(current, key)
        if current is None:
            return None
    return current


def _resolve_enum(blueprint: Any, *keys: str) -> Any:
    """Like _resolve but returns the .value of an enum member."""
    return _value_of(_resolve(blueprint, *keys))


# ---------------------------------------------------------------------------
# Check 1 — Structural coherence
# ---------------------------------------------------------------------------


def _check_structural_coherence(
    blueprint: Any,
    findings: list[dict[str, Any]],
) -> None:
    """Do story_engine claims align with identity? Does the engine exist?"""
    engine = _get(blueprint, "story_engine")
    if engine is None:
        findings.append({
            "rule": "blueprint.coherence.missing_engine",
            "message": "No story_engine is defined on the blueprint.",
            "severity": "error",
            "evidence": {"has_story_engine": False},
            "hypotheses": [
                "The blueprint was created before engine generation",
                "Engine generation was skipped or failed",
            ],
            "recommendations": [
                "Generate a story_engine via the Cartographer pipeline step",
            ],
            "requested_change": "A StoryEngine with at least a main_thread is required for blueprint coherence analysis.",
        })
        return

    main_thread = _get(engine, "main_thread")
    if main_thread is None:
        findings.append({
            "rule": "blueprint.coherence.no_main_thread",
            "message": "The story_engine has no main_thread.",
            "severity": "error",
            "evidence": {"has_main_thread": False},
            "hypotheses": [
                "The engine is only partially constructed",
            ],
            "recommendations": [
                "Define a main_thread with want, resistance, conflict, stakes, and change claims",
            ],
            "requested_change": "Add a complete MainThread to the StoryEngine.",
        })
        return

    # Check that all five structural claims are present
    required_claims = ["want", "resistance", "conflict", "stakes", "change"]
    missing = [c for c in required_claims if _get(main_thread, c) is None]
    if missing:
        findings.append({
            "rule": "blueprint.coherence.incomplete_main_thread",
            "message": f"Main thread is missing structural claims: {', '.join(missing)}.",
            "severity": "warning",
            "evidence": {
                "missing_claims": missing,
                "present_claims": [c for c in required_claims if c not in missing],
            },
            "hypotheses": [
                "The engine was populated incrementally",
                "Some claims are expected from a later pipeline step",
            ],
            "recommendations": [
                f"Fill in the following claims: {', '.join(missing)}",
            ],
            "requested_change": "Complete all five structural claims on the main_thread.",
        })

    # Check thread diversity — do sub-threads have distinct types?
    threads = _get(engine, "threads", [])
    if threads:
        thread_types = set()
        for t in (threads or []):
            tt = _get(t, "type")
            if tt is not None:
                thread_types.add(str(_value_of(tt)))

        if len(thread_types) < len(threads):
            findings.append({
                "rule": "blueprint.coherence.duplicate_thread_types",
                "message": (
                    f"Sub-threads use only {len(thread_types)} distinct type(s) "
                    f"across {len(threads)} thread(s)."
                ),
                "severity": "info",
                "evidence": {
                    "thread_count": len(threads),
                    "distinct_types": list(thread_types),
                },
                "hypotheses": [
                    "Multiple threads serve the same narrative function",
                    "Thread types have not been diversified",
                ],
                "recommendations": [
                    "Assign varied ThreadType values to increase structural diversity",
                ],
                "requested_change": "Diversify thread types to avoid redundant structural roles.",
            })


# ---------------------------------------------------------------------------
# Check 2 — Pacing targets
# ---------------------------------------------------------------------------


def _check_pacing_targets(
    blueprint: Any,
    findings: list[dict[str, Any]],
) -> None:
    """Are tension targets and act tones set to guide pacing?"""
    estimated_chapters = _resolve(blueprint, "structure", "estimated_chapters")

    # --- Tension target curve ---
    target_curve = _resolve(blueprint, "tension_waveform", "target_curve") or []
    n_targets = len(target_curve)

    if n_targets == 0:
        findings.append({
            "rule": "blueprint.coherence.no_tension_curve",
            "message": "No tension targets are defined on the tension_waveform.",
            "severity": "warning",
            "evidence": {
                "target_curve_length": 0,
                "estimated_chapters": estimated_chapters,
            },
            "hypotheses": [
                "Tension design was deferred to the drafting phase",
                "Tension targets are populated after chapter outline generation",
            ],
            "recommendations": [
                "Define tension targets for key structural beats "
                "(e.g. inciting incident, midpoint, climax)",
                "Use TensionWaveform.target_curve to set pacing guardrails",
            ],
            "requested_change": "Add at least one tension target (e.g. for chapter 1 and the climax).",
        })
    elif estimated_chapters and n_targets < max(1, estimated_chapters // 4):
        findings.append({
            "rule": "blueprint.coherence.sparse_tension_curve",
            "message": (
                f"Only {n_targets} tension target(s) for "
                f"{estimated_chapters} estimated chapters."
            ),
            "severity": "info",
            "evidence": {
                "target_curve_length": n_targets,
                "estimated_chapters": estimated_chapters,
            },
            "hypotheses": [
                "Only major beats are tracked; micro-pacing will be determined during drafting",
                "The tension curve is deliberately minimal",
            ],
            "recommendations": [
                "Consider adding targets at act boundaries and major structural beats",
            ],
            "requested_change": "Optionally flesh out the tension curve to cover more structural transitions.",
        })

    # --- Act tones ---
    per_act_tones = _resolve(blueprint, "emotional_design", "per_act_tones") or []
    if len(per_act_tones) == 0:
        findings.append({
            "rule": "blueprint.coherence.no_act_tones",
            "message": "No act-level emotional tones are defined.",
            "severity": "warning",
            "evidence": {"per_act_tones_length": 0},
            "hypotheses": [
                "Emotional design is captured only at the overall-arc level",
                "Per-act tones are populated after act outlines are finalized",
            ],
            "recommendations": [
                "Define per_act_tones with distinct emotional descriptors for each act",
            ],
            "requested_change": (
                "Add ActTone entries to emotional_design.per_act_tones "
                "for each act in the structure."
            ),
        })


# ---------------------------------------------------------------------------
# Check 3 — Thematic depth
# ---------------------------------------------------------------------------


def _check_thematic_depth(
    blueprint: Any,
    findings: list[dict[str, Any]],
) -> None:
    """Is the theme expressed through the story_engine?"""
    theme = _get(blueprint, "theme")
    if theme is None:
        findings.append({
            "rule": "blueprint.coherence.no_theme",
            "message": "No thematic core is defined on the blueprint.",
            "severity": "error",
            "evidence": {"has_theme": False},
            "hypotheses": [
                "The theme was not set during blueprint initialization",
            ],
            "recommendations": [
                "Define a ThematicCore with a central_question and thesis",
            ],
            "requested_change": "Add a theme to the blueprint.",
        })
        return

    central_question = _get(theme, "central_question", "")
    thesis = _get(theme, "thesis", "")

    if not central_question:
        findings.append({
            "rule": "blueprint.coherence.empty_central_question",
            "message": "The thematic core has no central_question.",
            "severity": "warning",
            "evidence": {"central_question": ""},
            "hypotheses": [
                "The theme was populated as a placeholder",
                "Central question generation was deferred",
            ],
            "recommendations": [
                "Write a philosophical question the story interrogates",
            ],
            "requested_change": "Add a non-empty central_question to the ThematicCore.",
        })

    if not thesis:
        findings.append({
            "rule": "blueprint.coherence.empty_thesis",
            "message": "The thematic core has no thesis.",
            "severity": "info",
            "evidence": {"thesis": ""},
            "hypotheses": [
                "The story's answer to the central question hasn't been settled yet",
                "The thesis will be derived during drafting",
            ],
            "recommendations": [
                "Define a tentative thesis to anchor thematic expression",
            ],
            "requested_change": "Add a thesis to the ThematicCore.",
        })

    # Check whether the story_engine references the theme
    engine = _get(blueprint, "story_engine")
    if engine is None:
        return  # already reported in structural coherence

    main_tf = _resolve(blueprint, "story_engine", "main_thread", "thematic_function")
    if not main_tf:
        findings.append({
            "rule": "blueprint.coherence.main_thread_no_thematic_function",
            "message": "The main_thread has no thematic_function.",
            "severity": "warning",
            "evidence": {"has_thematic_function": False},
            "hypotheses": [
                "The engine was generated without thematic annotation",
                "Thematic function is implicit in the claims",
            ],
            "recommendations": [
                "Add a thematic_function string linking the main thread to the central question",
            ],
            "requested_change": (
                f"Set main_thread.thematic_function to a phrase connecting it to "
                f"'{central_question or 'the central question'}'."
            ),
        })

    # Check sub-threads for thematic_function
    threads = _get(engine, "threads", [])
    threadless = sum(1 for t in (threads or []) if not _get(t, "thematic_function"))
    if threads and threadless > 0:
        findings.append({
            "rule": "blueprint.coherence.threads_missing_thematic_function",
            "message": (
                f"{threadless} of {len(threads)} sub-thread(s) "
                f"have no thematic_function."
            ),
            "severity": "info",
            "evidence": {
                "threads_without_thematic_function": threadless,
                "total_threads": len(threads),
            },
            "hypotheses": [
                "Thematic function is less critical for minor threads",
                "Sub-threads were populated from a template",
            ],
            "recommendations": [
                "Annotate each sub-thread with a thematic_function "
                "linking to the central question or thesis",
            ],
            "requested_change": "Add thematic_function to all sub-threads.",
        })


# ---------------------------------------------------------------------------
# Check 4 — Character arc completeness
# ---------------------------------------------------------------------------


def _check_character_arc_completeness(
    blueprint: Any,
    findings: list[dict[str, Any]],
) -> None:
    """Do all characters have defined arcs and milestones?"""
    characters = _get(blueprint, "characters", [])
    if not characters:
        findings.append({
            "rule": "blueprint.coherence.no_characters",
            "message": "No characters are defined on the blueprint.",
            "severity": "error",
            "evidence": {"character_count": 0},
            "hypotheses": [
                "Character creation was skipped",
                "Characters are populated later in the pipeline",
            ],
            "recommendations": [
                "Add at least one protagonist character",
            ],
            "requested_change": "Define characters with roles, arc types, and milestones.",
        })
        return

    # Check each non-flat character has milestones
    milestone_less = 0
    flat_count = 0
    total_char = len(characters)

    for char in characters:
        arc_type = _get(char, "arc_type")
        arc_type_str = str(_value_of(arc_type) or "").lower()

        if arc_type_str == "flat":
            flat_count += 1
            continue

        milestones = _get(char, "key_milestones", [])
        if not milestones:
            milestone_less += 1

    if milestone_less > 0:
        findings.append({
            "rule": "blueprint.coherence.characters_without_milestones",
            "message": (
                f"{milestone_less} non-flat character(s) "
                f"have no key milestones."
            ),
            "severity": "warning",
            "evidence": {
                "characters_without_milestones": milestone_less,
                "total_characters": total_char,
                "flat_characters": flat_count,
            },
            "hypotheses": [
                "Milestones will be populated when chapter outlines are generated",
                "These characters have implicit arcs driven by plot events",
            ],
            "recommendations": [
                "Define key_milestones for each non-flat character to guide arc progression",
            ],
            "requested_change": "Add at least one ArcMilestone to each non-flat character that lacks milestones.",
        })

    # Check character count against structural budget
    max_total = _resolve(blueprint, "structure", "max_characters_total")
    if max_total is not None and total_char > max_total:
        findings.append({
            "rule": "blueprint.coherence.exceeds_character_budget",
            "message": (
                f"{total_char} characters exceed the structural budget "
                f"of {max_total}."
            ),
            "severity": "warning",
            "evidence": {
                "character_count": total_char,
                "max_characters_total": max_total,
            },
            "hypotheses": [
                "The character budget was estimated conservatively",
                "Some characters may be merged or cut",
            ],
            "recommendations": [
                f"Reduce the cast to {max_total} or update max_characters_total",
            ],
            "requested_change": "Trim the character list or adjust the structural budget.",
        })

    # Check for POV role characters
    pov_roles = {"protagonist", "deuteragonist"}
    role_strs = set()
    for char in characters:
        role = _get(char, "role")
        rv = str(_value_of(role) or "").lower()
        if rv:
            role_strs.add(rv)

    has_pov = bool(pov_roles & role_strs)
    if not has_pov and total_char > 0:
        findings.append({
            "rule": "blueprint.coherence.no_pov_character",
            "message": "No protagonist or deuteragonist (POV-eligible) characters are defined.",
            "severity": "error",
            "evidence": {"roles_found": sorted(role_strs) if role_strs else None},
            "hypotheses": [
                "Roles are set from a different enum representation",
                "The character roles are populated later",
            ],
            "recommendations": [
                "Set at least one character's role to protagonist",
            ],
            "requested_change": "Assign a protagonist role to at least one character.",
        })


# ---------------------------------------------------------------------------
# Check 5 — Chapter estimate vs scene density
# ---------------------------------------------------------------------------


def _check_chapter_density(
    blueprint: Any,
    findings: list[dict[str, Any]],
) -> None:
    """Does the chapter estimate match the thread and subplot density?"""
    estimated_chapters = _resolve(blueprint, "structure", "estimated_chapters")
    subplot_budget = _resolve(blueprint, "structure", "subplot_budget")

    threads = _resolve(blueprint, "story_engine", "threads") or []
    n_threads = len(threads)

    if estimated_chapters is None:
        findings.append({
            "rule": "blueprint.coherence.no_chapter_estimate",
            "message": "No estimated chapter count is set on the blueprint structure.",
            "severity": "info",
            "evidence": {"estimated_chapters": None},
            "hypotheses": [
                "The estimate is derived from length_class defaults",
                "Chapter count was not explicitly configured",
            ],
            "recommendations": [
                "Set estimated_chapters explicitly or rely on length_class defaults",
            ],
            "requested_change": "Ensure estimated_chapters is resolved (check fill_defaults_from).",
        })
        return

    # Warn if subplot_budget is unused
    if subplot_budget is not None and n_threads > subplot_budget:
        findings.append({
            "rule": "blueprint.coherence.threads_exceed_subplot_budget",
            "message": (
                f"{n_threads} story thread(s) exceed the subplot budget "
                f"of {subplot_budget}."
            ),
            "severity": "warning",
            "evidence": {
                "thread_count": n_threads,
                "subplot_budget": subplot_budget,
                "estimated_chapters": estimated_chapters,
            },
            "hypotheses": [
                "The subplot budget was set conservatively",
                "Some threads serve as B/C plots that fit within the budget",
            ],
            "recommendations": [
                f"Reduce threads to {subplot_budget} or increase the "
                f"subplot_budget to {n_threads}",
            ],
            "requested_change": "Align thread count with the subplot_budget.",
        })

    # Density: ratio of threads to chapters
    if estimated_chapters and n_threads > 0:
        ratio = n_threads / estimated_chapters
        if ratio > 0.33:
            findings.append({
                "rule": "blueprint.coherence.high_thread_density",
                "message": (
                    f"Thread density is {ratio:.2f} threads per chapter "
                    f"({n_threads} threads, {estimated_chapters} chapters)."
                ),
                "severity": "info",
                "evidence": {
                    "thread_count": n_threads,
                    "estimated_chapters": estimated_chapters,
                    "threads_per_chapter": round(ratio, 2),
                },
                "hypotheses": [
                    "Threads may compete for page time",
                    "Shorter threads could be consolidated",
                ],
                "recommendations": [
                    "Consider consolidating or pruning threads to stay under "
                    "1 thread per 3 chapters",
                    "Ensure each thread has distinct supporting functions",
                ],
                "requested_change": "Review thread count relative to chapter budget.",
            })
