from __future__ import annotations

import re
from pathlib import Path

import yaml

from auteur.identity import StoryIdentity


ROOT = Path(__file__).resolve().parents[1]


def test_story_identity_architect_schema_example_matches_story_identity_model() -> None:
    skill_text = (ROOT / "skills" / "story-identity-architect" / "SKILL.md").read_text(
        encoding="utf-8"
    )
    match = re.search(
        r"### Schema Specification \(`story_identity\.yaml`\)\n\n```yaml\n(.*?)\n```",
        skill_text,
        re.DOTALL,
    )
    assert match is not None

    identity = StoryIdentity.model_validate(yaml.safe_load(match.group(1)))

    assert identity.title == "The Shattered Crown"
