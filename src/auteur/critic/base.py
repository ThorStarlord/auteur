"""Shared helpers for critic implementations."""

from __future__ import annotations

import re
from typing import Any, Protocol

import yaml
from pydantic import ValidationError

from auteur.bible import StoryBible
from auteur.blueprint import StoryBlueprint
from auteur.critic import CriticFinding
from auteur.llm import LLMClient


class Critic(Protocol):
    def __call__(
        self,
        *,
        draft: str,
        outline: dict[str, Any],
        blueprint: StoryBlueprint,
        bible: StoryBible,
        chapter_index: int,
        llm: LLMClient,
    ) -> list[CriticFinding]: ...


_CODE_FENCE = re.compile(r"^\s*```(?:yaml)?\s*\n(.*?)\n\s*```\s*$", re.DOTALL)


def parse_findings_yaml(text: str, *, critic_name: str) -> list[CriticFinding]:
    """Parse a critic's YAML response into CriticFinding objects.

    On any parse error, returns a single CriticFinding with rule
    'critic_parse_failure' so the caller can surface the problem rather than
    silently dropping it.
    """
    stripped = text.strip()
    fence_match = _CODE_FENCE.match(stripped)
    if fence_match:
        stripped = fence_match.group(1)

    try:
        data = yaml.safe_load(stripped)
    except yaml.YAMLError as exc:
        return [_parse_failure(critic_name, f"yaml load error: {exc}")]

    if not isinstance(data, dict) or "findings" not in data:
        return [_parse_failure(critic_name, "response missing top-level 'findings' key")]

    raw = data["findings"]
    if raw is None:
        return []
    if not isinstance(raw, list):
        return [_parse_failure(critic_name, "'findings' is not a list")]

    findings: list[CriticFinding] = []
    for i, item in enumerate(raw):
        if not isinstance(item, dict):
            findings.append(_parse_failure(critic_name, f"finding {i} is not an object"))
            continue
        try:
            findings.append(CriticFinding(critic=critic_name, **item))
        except ValidationError as exc:
            findings.append(_parse_failure(critic_name, f"finding {i} invalid: {exc}"))
    return findings


def _parse_failure(critic_name: str, detail: str) -> CriticFinding:
    return CriticFinding(
        critic=critic_name,  # type: ignore[arg-type]
        severity="error",
        rule="critic_parse_failure",
        evidence=detail[:300],
        requested_change="critic emitted unparseable output; investigate critic prompt",
    )


def format_bible_context(bible: StoryBible, *, mentioned: list[str]) -> str:
    """Render only the bible state for characters named in `mentioned`."""
    chars = bible.data.get("characters", {})
    lines: list[str] = []
    for name in mentioned:
        c = chars.get(name)
        if c is None:
            lines.append(f"- {name}: (no bible record yet)")
            continue
        bits = [f"{k}={v!r}" for k, v in c.items() if v not in (None, [], {})]
        lines.append(f"- {name}: {', '.join(bits) if bits else '(empty state)'}")
    return "\n".join(lines) if lines else "(no characters tracked)"


def format_outline_block(outline: dict[str, Any]) -> str:
    return yaml.safe_dump(outline, sort_keys=False).rstrip()
