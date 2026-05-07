"""Slop critic — clichés, AI-tells, and abstract emotion-naming."""

from __future__ import annotations

from typing import Any

from auteur.bible import StoryBible
from auteur.blueprint import StoryBlueprint
from auteur.critic import CriticFinding
from auteur.critic.base import parse_findings_yaml
from auteur.llm import LLMClient, LLMRequest


TEMPERATURE = 0.0
MAX_TOKENS = 1500

SLOP_PHRASES: list[str] = [
    "a testament to",
    "in the realm of",
    "a tapestry of",
    "an air of",
    "a whisper of",
    "stood as a beacon",
    "navigate the complexities",
    "delve into",
    "echoed through the chambers of",
    "the weight of",
    "tinged with",
    "an unspoken understanding",
    "the corners of his mouth",
    "a flicker of",
    "his very being",
]


SYSTEM_PROMPT = """\
You are the Slop Critic. You hunt for the textures that make AI-generated
prose feel hollow.

# What you flag
1. Clichés and stock metaphors ("a testament to", "in the realm of",
   "an air of", "a tapestry of"). Phrase list is provided.
2. Abstract emotion-naming instead of showing ("she felt a wave of
   sadness", "he was overcome with rage"). Prefer concrete physical
   correlates.
3. AI-tells: "the very fabric of", "his/her very being", overuse of
   "perhaps" or "indeed", excessive em-dashes, every-paragraph-summarises
   pacing, repetitive sentence rhythm.
4. Tautology and filler ("nodded his head", "shrugged his shoulders").

# Severity
- warning by default
- error only if THREE or more clichés appear in the same paragraph, or
  the prose is so dense with abstract emotion-naming that no scene can
  be visualised.

# Output
findings:
  - severity: warning|error
    rule: slop:<short>
    evidence: short quoted phrase
    requested_change: imperative for the rewrite
"""


def render(*, draft: str, chapter_index: int) -> tuple[str, str]:
    phrase_block = "\n".join(f"- {p}" for p in SLOP_PHRASES)
    user = f"""\
## CHAPTER INDEX
{chapter_index}

## CLICHE PHRASES TO MATCH (literal or near-paraphrase)
{phrase_block}

## DRAFT
{draft}

Return YAML findings. Many findings are fine; cap warnings at 10.
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
    system, user = render(draft=draft, chapter_index=chapter_index)
    resp = llm.complete(LLMRequest(
        system=system, user=user, temperature=TEMPERATURE, max_tokens=MAX_TOKENS,
    ))
    return parse_findings_yaml(resp.text, critic_name="slop")
