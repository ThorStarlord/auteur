"""Bard agent — turns a Cartographer outline into prose.

The Bard runs in two modes:
    draft mode   — first pass, no prior draft.
    rewrite mode — accepts the prior draft and the critic findings,
                   produces a revised draft that addresses them while
                   preserving the outline.
"""

from __future__ import annotations

import re
from typing import Any

from auteur.bible import StoryBible
from auteur.blueprint import StoryBlueprint
from auteur.critic import CriticFinding
from auteur.critic.base import format_bible_context, format_outline_block
from auteur.llm import LLMClient, LLMRequest


TEMPERATURE = 0.85
MAX_TOKENS = 8000

SYSTEM_PROMPT = """\
You are the Bard for the Auteur narrative pipeline. You write prose
chapters from a planning outline.

# Operating principles
1. Honor every scene in the outline. Do not invent scenes.
2. Honor the POV mode declared by the project — never break perspective.
3. Honor the contract rules. Never depict what is forbidden.
4. Use the Bible state for character details (e.g. if Kael has
   broken_arm, his physical actions reflect that).
5. Show, don't tell. Concrete sensory beats over abstract emotion-naming.
6. Avoid clichés ("a testament to", "in the realm of", etc.).

# Output format
Pure prose, Markdown allowed for chapter title only. NO commentary.
NO summarizing-the-outline-at-the-top. NO afterword. Just the chapter.

# When you are in REWRITE mode
A REWRITE TASK section will appear. Your job is to produce a revised
draft that addresses every error finding and as many warning findings
as possible while preserving the outline. Do not abandon scenes.
"""


_CODE_FENCE = re.compile(r"^\s*```(?:markdown|md)?\s*\n(.*?)\n\s*```\s*$", re.DOTALL)


def render_bard_prompt(
    *,
    outline: dict[str, Any],
    bible: StoryBible,
    blueprint: StoryBlueprint,
    chapter_index: int,
    prior_draft: str | None,
    findings: list[CriticFinding] | None,
) -> tuple[str, str]:
    chars_in_outline = sorted({
        s.get("pov_character")
        for s in outline.get("scenes", [])
        if s.get("pov_character")
    })
    bible_block = format_bible_context(bible, mentioned=chars_in_outline)

    pov = blueprint.identity.pov_type.value
    target_words = (blueprint.structure.estimated_word_count or 0) // max(
        1, blueprint.structure.estimated_chapters or 1
    )

    parts = [
        "## PROJECT",
        f"Title: {blueprint.identity.title}",
        f"POV: {pov}",
        f"Genre: {blueprint.identity.genre.value}",
        f"Target chapter length: ~{target_words} words (±20% acceptable).",
        "",
        "## OUTLINE",
        format_outline_block(outline),
        "",
        "## BIBLE CONTEXT",
        bible_block,
    ]

    if prior_draft is not None and findings is not None:
        finding_block = "\n".join(
            f"- [{f.severity}] {f.rule}: {f.requested_change}\n    evidence: {f.evidence}"
            for f in findings
        ) or "(no findings)"
        parts.extend([
            "",
            "## REWRITE TASK",
            "Your previous draft was rejected. Produce a revised draft.",
            "",
            "### PREVIOUS DRAFT",
            prior_draft,
            "",
            "### CRITIC FINDINGS",
            finding_block,
        ])

    parts.extend(["", "Now write the chapter."])
    return SYSTEM_PROMPT, "\n".join(parts)


def postprocess_draft(text: str) -> str:
    stripped = text.strip()
    fence_match = _CODE_FENCE.match(stripped)
    if fence_match:
        return fence_match.group(1).strip()
    return stripped


def draft_chapter(
    *,
    outline: dict[str, Any],
    bible: StoryBible,
    blueprint: StoryBlueprint,
    chapter_index: int,
    llm: LLMClient,
    prior_draft: str | None = None,
    findings: list[CriticFinding] | None = None,
) -> str:
    system, user = render_bard_prompt(
        outline=outline,
        bible=bible,
        blueprint=blueprint,
        chapter_index=chapter_index,
        prior_draft=prior_draft,
        findings=findings,
    )
    resp = llm.complete(LLMRequest(
        system=system,
        user=user,
        temperature=TEMPERATURE,
        max_tokens=MAX_TOKENS,
    ))
    return postprocess_draft(resp.text)
