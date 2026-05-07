"""Cartographer agent — turns a PlanningCall into a fully-rendered prompt.

The Cartographer plans, it does not draft prose. Its sole responsibility is
producing a strict, validatable outline that the Bard then renders. Because
the Critic later compiles every constraint, the prompt must be a contract:
unambiguous inputs, unambiguous output schema.
"""

from __future__ import annotations

from auteur.blueprint import PlanningCall, PlanningScope


SYSTEM_PROMPT = """\
You are the Cartographer — a master plot architect inside the Auteur narrative
engineering pipeline. You do not write prose. You produce strict, machine-readable
outlines that downstream agents (Bard, Critic) will compile.

# Operating principles
1. Treat every input parameter as a hard constraint, not a suggestion.
2. Every scene you propose must be justified by either an arc directive, a
   contract element, the tension target, or the thematic beat.
3. Forbidden tropes are auto-fail. Do not let them appear, even subverted,
   unless explicitly listed as expected elements.
4. The tension target is numeric and bidirectional. Scores 1-4 require quiet,
   reflective, or bonding scenes; battles, chases, and major confrontations
   are forbidden — plan recovery, foreshadowing, or mundane domesticity
   instead. Scores 7-10 demand active conflict, danger, or high stakes — a
   contemplative bonding scene at a tension target of 8 is also a fail.
5. Honor character continuity. If a character's state says broken_arm, they
   cannot wield a two-handed sword. If they are in Tavern, they cannot speak
   to someone in the Capital without a transition scene.
6. If the inputs contradict each other (e.g. an arc milestone demands action
   but tension target = 2), STOP and emit a `conflict_report` instead of an
   outline.

# Output format
Return one YAML document with these top-level keys exactly:

  scope:                  # echo the input scope
  chapter_index:          # int or null
  chapter_summary:        # one paragraph, prose-free, neutral voice
  scenes:                 # ordered list, 2-6 entries for a chapter
    - scene_id:           # short kebab-case id
      pov_character:      # name from arc_directives
      location:
      summary:            # 1-3 sentences, what happens
      key_events:         # list of concrete beats (no prose)
      character_state_changes:  # list of {character, field, before, after}
      arc_advancements:   # list of {character, milestone_touched, delta_pct}
      estimated_tension:  # 1-10
      emotional_tone:     # phrase matching the emotional_target vocabulary
  arc_pushes:             # which milestones this chapter advances overall
  contract_compliance:    # list of {rule, how_honored}
  expected_elements_touched:  # subset of input expected_elements seen this chapter
  forbidden_tropes_avoided:   # explicit confirmation, list of strings
  estimated_chapter_tension:  # 1-10, must equal tension_target ± 1
  thematic_reinforcement:     # one sentence on how the chapter echoes the theme
  conflict_report:        # null unless inputs contradicted; then describe.

Do not emit any other keys. Do not wrap the YAML in prose. Do not apologize.
"""


def render_cartographer_prompt(call: PlanningCall) -> tuple[str, str]:
    """Return (system_prompt, user_message) ready for an LLM call."""
    return SYSTEM_PROMPT, _user_message(call)


def _user_message(call: PlanningCall) -> str:
    parts = [
        _section("PROJECT", _project_block(call)),
        _section("SCOPE", _scope_block(call)),
        _section("CONTRACT", _contract_block(call)),
        _section("EMOTIONAL TARGET", call.emotional_target),
        _section("TENSION TARGET", _tension_block(call)),
        _section("ARC DIRECTIVES", _arc_block(call)),
        _section("THEMATIC BEAT", call.thematic_beat),
        "Produce the YAML outline now. No prose, no commentary.",
    ]
    return "\n\n".join(parts)


def _section(title: str, body: str) -> str:
    return f"## {title}\n{body}"


def _project_block(call: PlanningCall) -> str:
    sub = f" / {call.subgenre}" if call.subgenre else ""
    return (
        f"Title: {call.title}\n"
        f"Length class: {call.length_class.value} ({call.estimated_chapters} chapters, "
        f"{call.act_structure.value})\n"
        f"Genre: {call.genre.value}{sub}\n"
        f"Audience: {call.target_audience.value}\n"
        f"POV mode: {call.pov_type.value}"
    )


def _scope_block(call: PlanningCall) -> str:
    if call.scope == PlanningScope.CHAPTER:
        return (
            f"Plan ONE chapter at index {call.chapter_index} "
            f"(act {call.act_index} of {call.act_structure.value})."
        )
    if call.scope == PlanningScope.ACT:
        return f"Plan an entire act (act {call.act_index})."
    if call.scope == PlanningScope.FULL_STORY:
        return "Plan the full story at the act/major-beat level."
    if call.scope == PlanningScope.CHARACTER_ARC_BEAT:
        return f"Plan a single arc beat for character {call.focus_character!r}."
    return f"Scope: {call.scope.value}"


def _contract_block(call: PlanningCall) -> str:
    rules = "\n".join(f"  - {r}" for r in call.contract_rules)
    expected = (
        "\n".join(f"  - {e}" for e in call.expected_elements) if call.expected_elements else "  (none)"
    )
    forbidden = (
        "\n".join(f"  - {t}" for t in call.forbidden_tropes) if call.forbidden_tropes else "  (none)"
    )
    return (
        f"Hard rules:\n{rules}\n"
        f"Expected elements (must appear somewhere across the work):\n{expected}\n"
        f"Forbidden tropes (auto-fail if used):\n{forbidden}"
    )


def _tension_block(call: PlanningCall) -> str:
    if call.tension_target is None:
        target_line = "Target: (none specified — choose a score consistent with the act tone)"
    else:
        target_line = (
            f"Target score: {call.tension_target}/10  "
            f"(label: {call.tension_target_label or 'unlabeled'})"
        )
    history = (
        ", ".join(str(s) for s in call.recent_tension_scores)
        if call.recent_tension_scores
        else "(no prior chapters)"
    )
    return f"{target_line}\nRecent realized scores: {history}"


def _arc_block(call: PlanningCall) -> str:
    if not call.arc_directives:
        return "(no arc directives — characters not yet defined)"
    lines = []
    for d in call.arc_directives:
        milestone = d.next_milestone or "(no upcoming milestone)"
        block = (
            f"- {d.character} ({d.arc_type.value}, currently {d.current_pct}%):\n"
            f"    next milestone: {milestone}\n"
            f"    state: {d.state_summary}"
        )
        lines.append(block)
    return "\n".join(lines)
