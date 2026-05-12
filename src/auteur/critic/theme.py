"""Theme critic — central question echoed; at least one motif visible.

Theme is a long-game concern; per-chapter findings are warnings only.
"""

from __future__ import annotations

from typing import Any

from auteur.bible import StoryBible
from auteur.blueprint import StoryBlueprint
from auteur.critic import CriticFinding
from auteur.critic.base import parse_findings_yaml
from auteur.llm import LLMClient, LLMRequest


TEMPERATURE = 0.2
MAX_TOKENS = 1200

SYSTEM_PROMPT = """\
You are the Theme Critic. You check whether the chapter draft echoes the
project's thematic core.

# What you check
1. The central thematic question is touched on, even glancingly. The
   echo can be subtle — a character's choice, a contrasting image, a
   moment of doubt.
2. At least one of the project's motifs appears as concrete imagery
   somewhere in the chapter.

# Severity
All findings are WARNINGS. Theme is cumulative across the whole work;
a single chapter without a motif is not a failure mode.

# Output
findings:
  - severity: warning
    rule: theme:<short>
    evidence: short paraphrase of what's missing
    requested_change: imperative — concrete and small (one image, one beat)

Or findings: [] if the chapter does its job thematically.
"""


def render(
    *,
    draft: str,
    blueprint: StoryBlueprint,
    chapter_index: int,
    **kwargs,
) -> tuple[str, str]:
    theme = blueprint.theme
    motifs = "\n".join(f"- {m}" for m in theme.motifs) if theme.motifs else "(none declared)"

    user = f"""\
## CHAPTER INDEX
{chapter_index}

## CENTRAL QUESTION
{theme.central_question}

## THESIS
{theme.thesis}

## MOTIFS
{motifs}

## DRAFT
{draft}

Return YAML findings (warnings only).
"""
    return SYSTEM_PROMPT, user

