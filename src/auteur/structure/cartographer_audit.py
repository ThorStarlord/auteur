"""Cross-layer validation: Narrative Engine (story engine) → Cartographer (outline).

Validates that a CartographerOutline (Layer 7) enacts the structural forces,
threads, and character psychology defined by the Narrative Engine (Layers 1-6).
This is the bridge between what the story promises and what the outline delivers.

Diagnostic rules produced:
  - cartographer.thread.main_thread_unseen
  - cartographer.thread.subordinate_threads_absent
  - cartographer.character.contradiction_unsurfaced
  - cartographer.theme.thesis_unreinforced
  - cartographer.character.scene_energy_mismatch
  - cartographer.outline_missing
"""
from __future__ import annotations

from auteur.blueprint import StoryBlueprint
from auteur.cartographer_outline import CartographerOutline
from auteur.structure.diagnostics import (
    DiagnosticLayer,
    DiagnosticSeverity,
    RepairOptions,
    StructureDiagnostic,
)

# Scene-level tension ranges that map to scene energy expectations
_LOW_TENSION_MAX = 4
_HIGH_TENSION_MIN = 7


def audit_outline_vs_story_engine(
    blueprint: StoryBlueprint,
    outline: CartographerOutline | None,
) -> list[StructureDiagnostic]:
    """Validate a CartographerOutline against the blueprint's story engine.

    When ``outline`` is None, emits a single INFO that cross-layer validation
    was skipped (no outline provided).

    When ``outline`` is provided, checks every diagnostic category:
      - Main thread enactment in scenes
      - Subordinate thread carrier presence
      - Character contradiction surfacing
      - Thesis reinforcement in thematic_reinforcement
      - Scene energy consistency (tension vs emotional_tone)

    Args:
        blueprint: The StoryBlueprint (source of story engine and character data).
        outline: Parsed CartographerOutline, or None.

    Returns:
        List of StructureDiagnostic findings (may be empty).
    """
    diagnostics: list[StructureDiagnostic] = []

    if outline is None:
        return diagnostics

    story_engine = blueprint.story_engine
    if story_engine is None:
        diagnostics.append(StructureDiagnostic(
            severity=DiagnosticSeverity.WARNING,
            layer=DiagnosticLayer.THREADS,
            rule="cartographer.story_engine_missing",
            message=(
                "Cross-layer validation skipped because the blueprint has no story_engine. "
                "Run 'auteur structure generate' to create one."
            ),
            evidence=["blueprint.story_engine is None"],
        ))
        return diagnostics

    # ------------------------------------------------------------------
    # Main thread enactment — do scenes reference the main thread's want?
    # ------------------------------------------------------------------
    main_thread = story_engine.main_thread
    if main_thread and outline.scenes:
        char_names = {c.name.casefold() for c in blueprint.characters}
        want_keywords = [
            kw for kw in _extract_keywords(main_thread.want.author_text)
            if kw not in char_names
        ]
        scene_summaries = " ".join(
            s.summary for s in outline.scenes if s.summary
        ).lower()
        scene_events = " ".join(
            " ".join(s.key_events) for s in outline.scenes if s.key_events
        ).lower()
        combined_text = f"{scene_summaries} {scene_events}"

        matched_any = any(kw in combined_text for kw in want_keywords)
        if not matched_any and want_keywords:
            diagnostics.append(StructureDiagnostic(
                severity=DiagnosticSeverity.WARNING,
                layer=DiagnosticLayer.REPRESENTATION,
                rule="cartographer.thread.main_thread_unseen",
                message=(
                    "None of the scenes in the outline reference the main thread's want. "
                    "The story engine defines the protagonist's goal, but the outline "
                    "does not show scenes that pursue it."
                ),
                evidence=[
                    f"main_thread.want = {main_thread.want.author_text}",
                    f"scenes = {[s.scene_id for s in outline.scenes]}",
                ],
                repair_options=RepairOptions(
                    preserve_intent=[
                        "Rewrite scene summaries and key_events to show the protagonist "
                        "actively pursuing their want.",
                    ],
                    challenge_intent=[
                        "Keep scenes as-is if the chapter is setting up conditions that "
                        "enable the want to be pursued later.",
                    ],
                ),
            ))

    # ------------------------------------------------------------------
    # Subordinate thread presence via inferred characters
    # ------------------------------------------------------------------
    if story_engine.threads and outline.scenes:
        scene_characters = set()
        for s in outline.scenes:
            if s.pov_character:
                scene_characters.add(s.pov_character)
            if s.character_state_changes:
                for change in s.character_state_changes:
                    if change.character:
                        scene_characters.add(change.character)
            if s.arc_advancements:
                for adv in s.arc_advancements:
                    if adv.character:
                        scene_characters.add(adv.character)

        for thread in story_engine.threads:
            inferred = _infer_carriers_from_thread_name(thread.name)
            missing = [c for c in inferred if c not in scene_characters]
            if missing:
                diagnostics.append(StructureDiagnostic(
                    severity=DiagnosticSeverity.WARNING,
                    layer=DiagnosticLayer.REPRESENTATION,
                    rule="cartographer.thread.subordinate_threads_absent",
                    message=(
                        f"Thread '{thread.name}' involves characters {missing} that "
                        f"do not appear in any scene. Subordinate threads need "
                        f"scene presence to enact their structural function."
                    ),
                    evidence=[
                        f"thread.name = {thread.name}",
                        f"inferred_characters = {inferred}",
                        f"missing_from_scenes = {missing}",
                        f"scene_characters = {sorted(scene_characters)}",
                    ],
                    repair_options=RepairOptions(
                        preserve_intent=[
                            f"Add scenes or character appearances for '{missing}' "
                            f"to enact thread '{thread.name}'.",
                        ],
                        challenge_intent=[
                            f"Drop character coverage if the thread is designed to "
                            f"affect them off-screen this chapter.",
                        ],
                    ),
                ))

    # ------------------------------------------------------------------
    # Character contradiction surfacing
    # ------------------------------------------------------------------
    for char in blueprint.characters:
        if char.identity is None:
            continue
        identity = char.identity
        if not isinstance(identity, dict):
            continue
        psychology = identity.get("psychology", {})
        contradictions = psychology.get("contradictions", []) if isinstance(psychology, dict) else []
        if len(contradictions) < 2:
            continue

        has_conflict_in_scenes = False
        for s in outline.scenes:
            if char.name in (s.pov_character or ""):
                if s.key_events:
                    conflict_keywords = ["fight", "argue", "conflict", "confront", "struggle",
                                         "resist", "oppose", "tension", "clash", "debate"]
                    events_text = " ".join(s.key_events).lower()
                    if any(kw in events_text for kw in conflict_keywords):
                        has_conflict_in_scenes = True
                        break
            if s.character_state_changes:
                for change in s.character_state_changes:
                    if change.character == char.name and change.before != change.after:
                        has_conflict_in_scenes = True
                        break

        if not has_conflict_in_scenes:
            diagnostics.append(StructureDiagnostic(
                severity=DiagnosticSeverity.WARNING,
                layer=DiagnosticLayer.REPRESENTATION,
                rule="cartographer.character.contradiction_unsurfaced",
                message=(
                    f"Character '{char.name}' has {len(contradictions)} contradictions "
                    f"({', '.join(contradictions)}) but the outline shows no scene conflict "
                    f"involving them. Contradictions should surface as scene-level tension."
                ),
                evidence=[
                    f"character.name = {char.name}",
                    f"contradictions = {contradictions}",
                    f"pov_scenes = {[s.scene_id for s in outline.scenes if s.pov_character == char.name]}",
                ],
                repair_options=RepairOptions(
                    preserve_intent=[
                        f"Add a scene where '{char.name}'s contradiction "
                        f"('{contradictions[0]}') surfaces as dramatic tension.",
                    ],
                    challenge_intent=[
                        "Keep scenes as-is if the contradictions are internal and "
                        "surfaced through subtext rather than explicit conflict.",
                    ],
                ),
            ))

    # ------------------------------------------------------------------
    # Thesis reinforcement in thematic_reinforcement
    # ------------------------------------------------------------------
    thesis = blueprint.theme.thesis
    if thesis and outline.thematic_reinforcement:
        thesis_keywords = _extract_keywords(thesis)
        reinforcement_lower = outline.thematic_reinforcement.lower()
        thesis_matched = any(kw in reinforcement_lower for kw in thesis_keywords)
        if not thesis_matched and thesis_keywords:
            diagnostics.append(StructureDiagnostic(
                severity=DiagnosticSeverity.WARNING,
                layer=DiagnosticLayer.THEME,
                rule="cartographer.theme.thesis_unreinforced",
                message=(
                    "The outline's thematic_reinforcement does not reference "
                    "the story's thesis. Thematic reinforcement should connect "
                    "the chapter's events to the central thematic argument."
                ),
                evidence=[
                    f"thesis = {thesis}",
                    f"thematic_reinforcement = {outline.thematic_reinforcement}",
                ],
                repair_options=RepairOptions(
                    preserve_intent=[
                        "Rewrite thematic_reinforcement to connect the chapter's "
                        "events to the thesis.",
                    ],
                    challenge_intent=[
                        "Keep as-is if the chapter is a setup beat where the "
                        "thematic connection is indirect.",
                    ],
                ),
            ))

    # ------------------------------------------------------------------
    # Scene energy consistency (tension vs emotional_tone)
    # ------------------------------------------------------------------
    if outline.scenes:
        for scene in outline.scenes:
            if scene.estimated_tension is None or not scene.emotional_tone:
                continue
            tension = scene.estimated_tension
            tone_lower = scene.emotional_tone.lower()

            if tension <= _LOW_TENSION_MAX:
                low_energy_keywords = ["calm", "quiet", "reflective", "peaceful", "tender",
                                       "bonding", "domestic", "melancholy", "hopeful"]
                has_low_keyword = any(kw in tone_lower for kw in low_energy_keywords)
                high_energy_keywords = ["battle", "chase", "fight", "explosion", "confrontation",
                                        "pursuit", "violence", "intense"]
                has_high_keyword = any(kw in tone_lower for kw in high_energy_keywords)

                if has_high_keyword and not has_low_keyword:
                    diagnostics.append(StructureDiagnostic(
                        severity=DiagnosticSeverity.WARNING,
                        layer=DiagnosticLayer.REPRESENTATION,
                        rule="cartographer.character.scene_energy_mismatch",
                        message=(
                            f"Scene '{scene.scene_id}' has tension {tension}/10 "
                            f"(low) but emotional_tone '{scene.emotional_tone}' "
                            f"suggests high energy. Low-tension scenes should have "
                            f"calm, reflective, or bonding tones."
                        ),
                        evidence=[
                            f"scene.scene_id = {scene.scene_id}",
                            f"scene.estimated_tension = {tension}",
                            f"scene.emotional_tone = {scene.emotional_tone}",
                        ],
                        repair_options=RepairOptions(
                            preserve_intent=[
                                f"Reduce the tension score to match the high-energy tone, "
                                f"or rewrite the tone to reflect a low-energy register.",
                            ],
                            challenge_intent=[
                                "Keep if the low tension with high-energy tone is "
                                "intentional (e.g., quiet before the storm).",
                            ],
                        ),
                    ))

            elif tension >= _HIGH_TENSION_MIN:
                high_energy_keywords = ["battle", "chase", "fight", "explosion", "confrontation",
                                        "pursuit", "violence", "intense", "urgent", "desperate",
                                        "crisis", "climax"]
                low_energy_keywords = ["calm", "reflective", "peaceful", "domestic", "bonding"]
                has_high = any(kw in tone_lower for kw in high_energy_keywords)
                has_low = any(kw in tone_lower for kw in low_energy_keywords)

                if has_low and not has_high:
                    diagnostics.append(StructureDiagnostic(
                        severity=DiagnosticSeverity.WARNING,
                        layer=DiagnosticLayer.REPRESENTATION,
                        rule="cartographer.character.scene_energy_mismatch",
                        message=(
                            f"Scene '{scene.scene_id}' has tension {tension}/10 "
                            f"(high) but emotional_tone '{scene.emotional_tone}' "
                            f"suggests low energy. High-tension scenes should have "
                            f"active conflict, danger, or urgent stakes."
                        ),
                        evidence=[
                            f"scene.scene_id = {scene.scene_id}",
                            f"scene.estimated_tension = {tension}",
                            f"scene.emotional_tone = {scene.emotional_tone}",
                        ],
                        repair_options=RepairOptions(
                            preserve_intent=[
                                f"Increase the tension score to match the low-energy tone, "
                                f"or rewrite the tone to reflect high stakes.",
                            ],
                            challenge_intent=[
                                "Keep if the high tension with a low-energy description "
                                "is intentional (e.g., aftermath of a crisis).",
                            ],
                        ),
                    ))

    return diagnostics


def _infer_carriers_from_thread_name(name: str) -> list[str]:
    """Infer character names from a thread name.

    Thread names follow patterns like "Kael_arc", "Kael_Malachai_rivalry",
    "thematic_echo", "Malachai_pressure". Extracts plausible character names
    by splitting on underscores and filtering to capitalized words.
    """
    parts = name.split("_")
    known_nonchars = {"arc", "rivalry", "relationship", "pressure", "thematic", "echo", "main", "plot", "and"}
    candidates = []
    for p in parts:
        if p and p[0].isupper() and p.casefold() not in known_nonchars:
            candidates.append(p)
    return candidates


def _extract_keywords(text: str) -> list[str]:
    """Extract meaningful keywords from a text string for matching.

    Strips common stop words and returns lowercase words of length >= 4.
    """
    stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at",
                  "to", "for", "of", "with", "by", "from", "is", "are",
                  "was", "were", "be", "been", "being", "have", "has",
                  "had", "do", "does", "did", "will", "would", "could",
                  "should", "may", "might", "shall", "can", "not", "no",
                  "its", "it's", "their", "them", "they", "this", "that",
                  "what", "which", "who", "whom", "when", "where", "why",
                  "how", "all", "each", "every", "both", "few", "more",
                  "most", "some", "any", "none", "one", "two", "three",
                  "very", "just", "than", "then", "also", "well", "only",
                  "own", "same", "so", "too", "quite", "about", "into",
                  "over", "after", "before", "between", "under", "above",
                  "below", "out", "off", "up", "down", "back", "there",
                  "here", "other", "another", "such", "much", "still"}
    words = text.lower().split()
    return [w for w in words if w not in stop_words and len(w) >= 4]
