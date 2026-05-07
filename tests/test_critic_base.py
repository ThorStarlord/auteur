import pytest

from auteur.critic.base import (
    parse_findings_yaml,
    format_bible_context,
    format_outline_block,
)
from auteur.critic import CriticFinding
from auteur.bible import StoryBible


def test_parse_findings_yaml_happy_path():
    text = """
findings:
  - severity: error
    rule: forbidden_trope:chosen_one_prophecy
    evidence: "scene 2: prophecy named him"
    requested_change: remove the prophecy reveal
  - severity: warning
    rule: cliche
    evidence: "a testament to"
    requested_change: rephrase
"""
    findings = parse_findings_yaml(text, critic_name="contract")

    assert len(findings) == 2
    assert findings[0].critic == "contract"
    assert findings[0].severity == "error"
    assert findings[1].severity == "warning"


def test_parse_findings_yaml_handles_no_findings():
    text = "findings: []"
    assert parse_findings_yaml(text, critic_name="theme") == []


def test_parse_findings_yaml_strips_code_fence():
    text = """```yaml
findings:
  - severity: warning
    rule: x
    evidence: y
    requested_change: z
```"""
    findings = parse_findings_yaml(text, critic_name="slop")
    assert len(findings) == 1


def test_parse_findings_yaml_invalid_returns_parse_failure_finding():
    text = "this is not yaml at all: {[}"
    findings = parse_findings_yaml(text, critic_name="contract")

    assert len(findings) == 1
    assert findings[0].rule == "critic_parse_failure"
    assert findings[0].severity == "error"


def test_parse_findings_yaml_missing_findings_key_returns_parse_failure():
    text = "something_else:\n  - 1"
    findings = parse_findings_yaml(text, critic_name="arc")
    assert findings[0].rule == "critic_parse_failure"


def test_format_bible_context_compact(tmp_path):
    bible = StoryBible(tmp_path / "b.json")
    bible.upsert_character("Kael", location="taverntown", physical="broken_arm")
    bible.upsert_character("Lira", location="taverntown", physical="ok")

    block = format_bible_context(bible, mentioned=["Kael"])

    assert "Kael" in block
    assert "broken_arm" in block
    assert "Lira" not in block  # only mentioned characters


def test_format_outline_block_renders_yaml():
    outline = {"scope": "chapter", "scenes": [{"id": "s1", "summary": "a"}]}
    block = format_outline_block(outline)
    assert "scope: chapter" in block
    assert "scenes:" in block
