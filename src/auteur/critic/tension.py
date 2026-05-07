"""Tension critic — confirms the prose's actual tension matches outline."""

from __future__ import annotations

from typing import Any

from auteur.bible import StoryBible
from auteur.blueprint import StoryBlueprint
from auteur.critic import CriticFinding
from auteur.critic.base import parse_findings_yaml
from auteur.llm import LLMClient, LLMRequest


TEMPERATURE = 0.0
MAX_TOKENS = 1200

SYSTEM_PROMPT = """\
You are the Tension Critic. Your sole job is to read the draft and judge
whether its felt tension matches the planned target.

# Tension scale
1-2  domestic / reflective; barely any conflict; reader is at rest
3-4  quiet stakes; foreshadowing; relational warmth
5-6  rising tension; clear obstacles; some danger or conflict
7-8  active conflict; chase, fight, or major emotional rupture
9-10 climactic stakes; life, identity, or world on the line

# Decision rule
Compute your felt-tension estimate for the draft.
- If |felt − target| <= 1: emit no finding (output: findings: []).
- If |felt − target| == 2: emit a WARNING finding.
- If |felt − target| >= 3: emit an ERROR finding.

The error message should explain WHAT kind of scene the prose actually
delivers and WHAT the target requires. Then give a concrete imperative
to fix it (e.g. "add a violent confrontation in scene 3").

# Output
findings:
  - severity: warning|error
    rule: tension:drift
    evidence: brief quote or paraphrase showing the mismatch
    requested_change: imperative

Or `findings: []` if within tolerance.
"""


def render(
    *,
    draft: str,
    outline: dict[str, Any],
    blueprint: StoryBlueprint,
    chapter_index: int,
) -> tuple[str, str]:
    target_obj = blueprint.tension_waveform.target_for(chapter_index)
    waveform_label = target_obj.label if target_obj else "(no waveform target)"
    waveform_score = target_obj.score if target_obj else None
    outline_target = outline.get("estimated_chapter_tension")

    user = f"""\
## CHAPTER INDEX
{chapter_index}

## TARGETS
outline_estimated_chapter_tension: {outline_target}
waveform_target_score: {waveform_score}
waveform_label: {waveform_label}

(If both are present and disagree, weight the outline's estimate.)

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
    return parse_findings_yaml(resp.text, critic_name="tension")
