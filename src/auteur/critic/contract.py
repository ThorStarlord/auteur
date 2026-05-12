# src/auteur/critic/contract.py
"""Contract critic — checks every flattened contract rule plus pacing.

Errors:  forbidden tropes used; content rating breached; on_page_torture/
         child_harm violated; character state continuity broken (e.g. the
         draft has Kael wielding a two-handed weapon while bible says
         broken_arm); chapter word count more than 50% off target.
Warnings: expected element not touched; word count 20-50% off target;
          custom_rules infractions that are stylistic rather than hard.
"""

from __future__ import annotations

from typing import Any

from auteur.bible import StoryBible
from auteur.blueprint import StoryBlueprint
from auteur.critic import CriticFinding
from auteur.critic.base import (
    format_bible_context,
    format_outline_block,
    parse_findings_yaml,
)
from auteur.llm import LLMClient, LLMRequest


TEMPERATURE = 0.0
MAX_TOKENS = 2000

SYSTEM_PROMPT = """\
You are the Contract Critic for the Auteur narrative pipeline. You receive
a draft chapter, the outline that produced it, the project's contract
rules, and the live Bible state for characters mentioned in the chapter.

You must detect violations and emit them as structured YAML.

# What you check
1. Forbidden tropes: any forbidden trope present, including paraphrased
   or implicit uses (e.g. "chosen_one_prophecy" applies even if the word
   "prophecy" never appears, when the structure of the scene IS a prophecy
   reveal). These are always errors.
2. Content controls: explicit_violence, explicit_sex, profanity,
   on_page_torture, child_harm — flag if the draft exceeds the declared
   level. Errors.
3. Character state continuity vs the Bible. If the Bible says Kael has
   broken_arm and the draft has him wielding a two-handed sword, that's
   an error. If the Bible says Kael is in taverntown and the draft has
   him conversing in the Capital without any transition scene, that's an
   error.
4. Word-count / pacing: the outline implies a target chapter length
   (estimated_word_count / estimated_chapters). The actual draft length
   will be supplied. Drift over 50% is an error
   (rule="pacing:word_count_drift_severe"); 20-50% drift is a warning
   (rule="pacing:word_count_drift").
5. Expected elements: emit a WARNING for each expected_element that the
   outline claimed would be touched but the draft fails to honor.
6. Custom rules: line-by-line scan for the project's custom_rules.

# Output
Return one YAML document with exactly one top-level key:

  findings:
    - severity: error|warning
      rule: <short identifier, e.g. "forbidden_trope:chosen_one_prophecy">
      evidence: <short quote or paraphrase from the draft>
      requested_change: <imperative sentence telling the Bard what to fix>

If nothing is wrong, emit `findings: []`.
Do not emit any other top-level keys. Do not wrap in prose.
"""


def render(
    *,
    draft: str,
    outline: dict[str, Any],
    blueprint: StoryBlueprint,
    bible: StoryBible,
    chapter_index: int,
) -> tuple[str, str]:
    contract = blueprint.contract
    rules = [
        f"content_rating = {contract.content_rating.value}",
        f"explicit_violence = {contract.explicit_violence}",
        f"explicit_sex = {contract.explicit_sex}",
        f"profanity = {contract.profanity}",
        f"on_page_torture = {contract.on_page_torture}",
        f"child_harm = {contract.child_harm}",
        f"mandatory_ending_tone = {contract.mandatory_ending_tone.value}",
    ] + list(contract.custom_rules)

    forbidden = contract.forbidden_tropes or ["(none)"]
    expected = contract.expected_elements or ["(none)"]

    chars_in_outline = sorted({
        c["pov_character"]
        for s in outline.get("scenes", [])
        for c in [{"pov_character": s.get("pov_character")}]
        if c["pov_character"]
    })
    bible_block = format_bible_context(bible, mentioned=chars_in_outline)

    target_words = (blueprint.structure.estimated_word_count or 0) // max(
        1, blueprint.structure.estimated_chapters or 1
    )
    actual_words = len(draft.split())

    user = f"""\
## CHAPTER INDEX
{chapter_index}

## CONTRACT RULES
{chr(10).join(f"- {r}" for r in rules)}

## FORBIDDEN TROPES
{chr(10).join(f"- {t}" for t in forbidden)}

## EXPECTED ELEMENTS
{chr(10).join(f"- {e}" for e in expected)}

## OUTLINE (for context only — do not re-validate the outline itself)
{format_outline_block(outline)}

## BIBLE CONTEXT (for characters in this chapter)
{bible_block}

## WORD COUNT
target_per_chapter: {target_words}
actual: {actual_words}

## DRAFT
{draft}

Return your YAML findings now.
"""
    return SYSTEM_PROMPT, user

