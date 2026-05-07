"""Arc critic — checks that the draft's prose actually supports the arc
advancements the outline claimed for this chapter."""

from __future__ import annotations

from typing import Any

from auteur.bible import StoryBible
from auteur.blueprint import StoryBlueprint
from auteur.critic import CriticFinding
from auteur.critic.base import format_outline_block, parse_findings_yaml
from auteur.llm import LLMClient, LLMRequest


TEMPERATURE = 0.0
MAX_TOKENS = 1500

SYSTEM_PROMPT = """\
You are the Arc Critic. You verify that the prose draft actually supports
the character arc advancements the outline promised for this chapter.

# What you check
For each entry in the outline's `arc_pushes`:
  - Is the milestone visibly happening in the prose? Naming it in dialogue
    is not enough. The reader should be able to *infer* the milestone
    from a scene's events and the character's behavior.
  - Is the claimed delta_pct plausible for what's on the page? A 15%
    jump for a single hesitant lie is implausible; a 1% jump for a
    full-blown betrayal is implausible.
  - Is the advancement consistent with the character's arc_type? A
    "corruption" arc cannot advance via a moment of moral courage.

# What you do not check
- Whether the chapter is well written (slop critic owns that).
- Whether tension matches target (tension critic owns that).
- Contract rules (contract critic owns that).

# Output
Return one YAML document with one top-level key:

  findings:
    - severity: error|warning
      rule: arc:<short>
      evidence: short quote or paraphrase
      requested_change: imperative

If everything checks out, emit `findings: []`.
"""


def render(
    *,
    draft: str,
    outline: dict[str, Any],
    blueprint: StoryBlueprint,
    chapter_index: int,
) -> tuple[str, str]:
    directives = []
    for c in blueprint.characters:
        nxt = c.next_milestone()
        directives.append(
            f"- {c.name} (arc_type={c.arc_type.value}, current_pct={c.current_arc_percentage}%): "
            f"next milestone = {nxt.description if nxt else '(none)'}"
        )

    user = f"""\
## CHAPTER INDEX
{chapter_index}

## ARC DIRECTIVES (from blueprint)
{chr(10).join(directives)}

## OUTLINE (especially arc_pushes)
{format_outline_block(outline)}

## DRAFT
{draft}

Return YAML findings.
"""
    return SYSTEM_PROMPT, user


def run(
    *,
    draft: str,
    outline: dict[str, Any],
    blueprint: StoryBlueprint,
    bible: StoryBible,
    chapter_index: int,
    llm: LLMClient,
) -> list[CriticFinding]:
    system, user = render(
        draft=draft, outline=outline, blueprint=blueprint, chapter_index=chapter_index
    )
    resp = llm.complete(LLMRequest(
        system=system, user=user, temperature=TEMPERATURE, max_tokens=MAX_TOKENS,
    ))
    return parse_findings_yaml(resp.text, critic_name="arc")
