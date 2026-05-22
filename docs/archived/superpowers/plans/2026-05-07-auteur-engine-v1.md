# Auteur Engine v1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn the existing prompt-rendering pipeline into a working chapter generator: `auteur draft <project> <N>` plans, drafts, validates against five focused critics, iterates up to N times, and emits a final chapter or a structured rejection.

**Architecture:** A provider-agnostic `LLMClient` Protocol with `FakeClient` for tests and Anthropic/OpenAI clients for production. A `Project` class wraps a directory containing `blueprint.yaml`, `bible.json`, and per-chapter artifacts. A new `Bard` agent renders prose from the Cartographer's outline; five `Critic` modules (contract / arc / tension / slop / theme) run in parallel and produce structured findings; the `PipelineRunner` orchestrates the plan → draft → critique → iterate loop. CLI gains `init`, `draft`, `accept`, and `retry` commands.

**Tech Stack:** Python ≥3.11, Pydantic v2, PyYAML, pytest, anthropic SDK, openai SDK, `concurrent.futures` for parallel critics.

**Spec reference:** `docs/archived/superpowers/specs/2026-05-07-auteur-engine-v1-design.md`

---

### Task 1: LLM client protocol and FakeClient

**Files:**
- Create: `src/auteur/llm/__init__.py`
- Create: `src/auteur/llm/fake.py`
- Test: `tests/test_llm_fake.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_llm_fake.py
import pytest
from auteur.llm import LLMClient, LLMRequest, LLMResponse
from auteur.llm.fake import FakeClient


def test_fake_client_returns_scripted_responses_in_order():
    scripted = [
        LLMResponse(text="first", input_tokens=10, output_tokens=2),
        LLMResponse(text="second", input_tokens=12, output_tokens=3),
    ]
    client: LLMClient = FakeClient(scripted)

    r1 = client.complete(LLMRequest(system="s", user="u1"))
    r2 = client.complete(LLMRequest(system="s", user="u2"))

    assert r1.text == "first"
    assert r2.text == "second"


def test_fake_client_raises_when_exhausted():
    client = FakeClient([LLMResponse(text="only", input_tokens=1, output_tokens=1)])
    client.complete(LLMRequest(system="s", user="u"))

    with pytest.raises(RuntimeError, match="FakeClient exhausted"):
        client.complete(LLMRequest(system="s", user="u"))


def test_fake_client_records_calls():
    client = FakeClient([LLMResponse(text="x", input_tokens=1, output_tokens=1)])
    client.complete(LLMRequest(system="sys", user="usr", temperature=0.1))

    assert len(client.calls) == 1
    assert client.calls[0].system == "sys"
    assert client.calls[0].user == "usr"
    assert client.calls[0].temperature == 0.1
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_llm_fake.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'auteur.llm'`

- [ ] **Step 3: Implement the protocol and dataclasses**

```python
# src/auteur/llm/__init__.py
"""Provider-agnostic LLM client interface."""

from __future__ import annotations

from typing import Protocol

from pydantic import BaseModel, Field


class LLMRequest(BaseModel):
    system: str
    user: str
    max_tokens: int = Field(default=4096, ge=1)
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    model: str | None = None


class LLMResponse(BaseModel):
    text: str
    input_tokens: int = Field(ge=0)
    output_tokens: int = Field(ge=0)


class LLMClient(Protocol):
    def complete(self, req: LLMRequest) -> LLMResponse: ...


__all__ = ["LLMClient", "LLMRequest", "LLMResponse"]
```

- [ ] **Step 4: Implement FakeClient**

```python
# src/auteur/llm/fake.py
"""FakeClient — replays scripted LLMResponse objects for tests."""

from __future__ import annotations

from auteur.llm import LLMRequest, LLMResponse


class FakeClient:
    def __init__(self, scripted: list[LLMResponse]):
        self._queue: list[LLMResponse] = list(scripted)
        self.calls: list[LLMRequest] = []

    def complete(self, req: LLMRequest) -> LLMResponse:
        self.calls.append(req)
        if not self._queue:
            raise RuntimeError(
                f"FakeClient exhausted after {len(self.calls)} calls; "
                "no more scripted responses."
            )
        return self._queue.pop(0)
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `pytest tests/test_llm_fake.py -v`
Expected: 3 PASSED.

- [ ] **Step 6: Commit**

```bash
git add src/auteur/llm/ tests/test_llm_fake.py
git commit -m "feat(llm): add LLMClient protocol and FakeClient for tests"
```

---

### Task 2: Project class

**Files:**
- Create: `src/auteur/project.py`
- Test: `tests/test_project.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_project.py
import json
from pathlib import Path

import pytest

from auteur.project import Project
from auteur.blueprint import StoryBlueprint


SAMPLE_YAML = Path(__file__).parent.parent / "examples" / "sample_blueprint.yaml"


def test_init_creates_directory_with_blueprint_and_bible(tmp_path):
    proj_dir = tmp_path / "novel"
    blueprint = StoryBlueprint.from_yaml(SAMPLE_YAML)

    project = Project.init(proj_dir, blueprint)

    assert proj_dir.is_dir()
    assert (proj_dir / "blueprint.yaml").exists()
    assert (proj_dir / "bible.json").exists()
    assert (proj_dir / "chapters").is_dir()
    bible_data = json.loads((proj_dir / "bible.json").read_text(encoding="utf-8"))
    assert bible_data["characters"] == {}


def test_init_refuses_to_overwrite_existing(tmp_path):
    proj_dir = tmp_path / "novel"
    blueprint = StoryBlueprint.from_yaml(SAMPLE_YAML)
    Project.init(proj_dir, blueprint)

    with pytest.raises(FileExistsError):
        Project.init(proj_dir, blueprint)


def test_load_round_trips_blueprint_and_bible(tmp_path):
    proj_dir = tmp_path / "novel"
    blueprint = StoryBlueprint.from_yaml(SAMPLE_YAML)
    Project.init(proj_dir, blueprint)

    project = Project.load(proj_dir)

    assert project.blueprint.identity.title == "The Shattered Crown"
    assert project.bible.data["characters"] == {}


def test_chapter_dir_paths_are_zero_padded(tmp_path):
    project = Project.init(tmp_path / "n", StoryBlueprint.from_yaml(SAMPLE_YAML))
    assert project.chapter_dir(1).name == "01"
    assert project.chapter_dir(45).name == "45"


def test_next_draft_version_starts_at_one(tmp_path):
    project = Project.init(tmp_path / "n", StoryBlueprint.from_yaml(SAMPLE_YAML))
    assert project.next_draft_version(1) == 1


def test_next_draft_version_after_writes(tmp_path):
    project = Project.init(tmp_path / "n", StoryBlueprint.from_yaml(SAMPLE_YAML))
    project.write_draft(1, 1, "first")
    project.write_draft(1, 2, "second")
    assert project.next_draft_version(1) == 3


def test_write_outline_and_draft_and_validation(tmp_path):
    project = Project.init(tmp_path / "n", StoryBlueprint.from_yaml(SAMPLE_YAML))

    out_path = project.write_outline(1, {"scope": "chapter", "scenes": []})
    draft_path = project.write_draft(1, 1, "Once upon a time...")
    val_path = project.write_validation(1, 1, {"passed": True, "findings": []})

    assert out_path.read_text(encoding="utf-8").startswith("scope:")
    assert draft_path.read_text(encoding="utf-8") == "Once upon a time..."
    assert json.loads(val_path.read_text(encoding="utf-8"))["passed"] is True


def test_write_final_and_has_final(tmp_path):
    project = Project.init(tmp_path / "n", StoryBlueprint.from_yaml(SAMPLE_YAML))
    assert not project.has_final(1)
    project.write_final(1, "the chapter prose")
    assert project.has_final(1)
    assert (project.chapter_dir(1) / "final.md").read_text(encoding="utf-8") == "the chapter prose"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_project.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'auteur.project'`

- [ ] **Step 3: Implement the Project class**

```python
# src/auteur/project.py
"""Project — directory-backed wrapper around a StoryBlueprint and StoryBible.

A project is a directory:
    project/
      blueprint.yaml
      bible.json
      chapters/01/{outline.yaml,draft_v1.md,validation_v1.json,...,final.md}
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

import yaml

from auteur.bible import StoryBible
from auteur.blueprint import StoryBlueprint


class Project:
    def __init__(self, path: Path, blueprint: StoryBlueprint, bible: StoryBible):
        self.path = path
        self.blueprint = blueprint
        self.bible = bible

    @classmethod
    def init(cls, path: Path, blueprint: StoryBlueprint) -> "Project":
        if path.exists():
            raise FileExistsError(f"Project path already exists: {path}")
        path.mkdir(parents=True)
        (path / "chapters").mkdir()
        (path / "blueprint.yaml").write_text(
            yaml.safe_dump(blueprint.model_dump(mode="json"), sort_keys=False),
            encoding="utf-8",
        )
        bible = StoryBible(path / "bible.json")
        return cls(path, blueprint, bible)

    @classmethod
    def load(cls, path: Path) -> "Project":
        if not path.is_dir():
            raise FileNotFoundError(f"Project path is not a directory: {path}")
        blueprint = StoryBlueprint.from_yaml(path / "blueprint.yaml")
        bible = StoryBible(path / "bible.json")
        return cls(path, blueprint, bible)

    def chapter_dir(self, n: int) -> Path:
        d = self.path / "chapters" / f"{n:02d}"
        d.mkdir(parents=True, exist_ok=True)
        return d

    def next_draft_version(self, n: int) -> int:
        existing = list(self.chapter_dir(n).glob("draft_v*.md"))
        if not existing:
            return 1
        versions = [int(p.stem.removeprefix("draft_v")) for p in existing]
        return max(versions) + 1

    def write_outline(self, n: int, outline: dict[str, Any]) -> Path:
        path = self.chapter_dir(n) / "outline.yaml"
        path.write_text(yaml.safe_dump(outline, sort_keys=False), encoding="utf-8")
        return path

    def write_draft(self, n: int, version: int, prose: str) -> Path:
        path = self.chapter_dir(n) / f"draft_v{version}.md"
        path.write_text(prose, encoding="utf-8")
        return path

    def write_validation(self, n: int, version: int, report: Any) -> Path:
        path = self.chapter_dir(n) / f"validation_v{version}.json"
        if hasattr(report, "model_dump"):
            payload = report.model_dump(mode="json")
        else:
            payload = report
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        return path

    def write_final(self, n: int, prose: str) -> Path:
        path = self.chapter_dir(n) / "final.md"
        path.write_text(prose, encoding="utf-8")
        return path

    def has_final(self, n: int) -> bool:
        return (self.chapter_dir(n) / "final.md").exists()
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_project.py -v`
Expected: 7 PASSED.

- [ ] **Step 5: Commit**

```bash
git add src/auteur/project.py tests/test_project.py
git commit -m "feat(project): add Project class wrapping blueprint + bible + chapter artifacts"
```

---

### Task 3: Critic models (CriticFinding, ValidationReport)

**Files:**
- Create: `src/auteur/critic/__init__.py`
- Test: `tests/test_critic_models.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_critic_models.py
import pytest
from pydantic import ValidationError

from auteur.critic import CriticFinding, ValidationReport


def test_critic_finding_validates_severity():
    f = CriticFinding(
        critic="contract",
        severity="error",
        rule="forbidden_trope:chosen_one_prophecy",
        evidence="scene 2: 'the prophecy named him'",
        requested_change="remove all prophecy framing",
    )
    assert f.severity == "error"


def test_critic_finding_rejects_unknown_severity():
    with pytest.raises(ValidationError):
        CriticFinding(
            critic="contract",
            severity="bogus",
            rule="x",
            evidence="y",
            requested_change="z",
        )


def test_validation_report_passed_true_on_no_errors():
    report = ValidationReport(
        chapter_index=1,
        iteration=1,
        findings=[
            CriticFinding(
                critic="slop",
                severity="warning",
                rule="cliche",
                evidence="'a testament to'",
                requested_change="rephrase",
            ),
        ],
        passed=True,
    )
    assert report.passed is True


def test_validation_report_passed_false_on_any_error():
    report = ValidationReport(
        chapter_index=1,
        iteration=1,
        findings=[
            CriticFinding(
                critic="contract",
                severity="error",
                rule="r",
                evidence="e",
                requested_change="c",
            ),
        ],
        passed=False,
    )
    assert report.passed is False
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_critic_models.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'auteur.critic'`

- [ ] **Step 3: Implement the models**

```python
# src/auteur/critic/__init__.py
"""Critic system — validation findings and aggregation.

The five built-in critics live in their own modules (contract, arc, tension,
slop, theme). Each emits a list[CriticFinding]. run_critics fans them out
in parallel and aggregates into one ValidationReport.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel


class CriticFinding(BaseModel):
    critic: Literal["contract", "arc", "tension", "slop", "theme"]
    severity: Literal["error", "warning"]
    rule: str
    evidence: str
    requested_change: str


class ValidationReport(BaseModel):
    chapter_index: int
    iteration: int
    findings: list[CriticFinding]
    passed: bool


__all__ = ["CriticFinding", "ValidationReport"]
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_critic_models.py -v`
Expected: 4 PASSED.

- [ ] **Step 5: Commit**

```bash
git add src/auteur/critic/__init__.py tests/test_critic_models.py
git commit -m "feat(critic): add CriticFinding and ValidationReport models"
```

---

### Task 4: Critic base helpers and parser

**Files:**
- Create: `src/auteur/critic/base.py`
- Test: `tests/test_critic_base.py`

The `Critic` Protocol exists for typing future user-defined critics. The shared helpers parse the YAML responses critics emit and format the chapter draft + bible context into compact prompt blocks.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_critic_base.py
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_critic_base.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'auteur.critic.base'`

- [ ] **Step 3: Implement base helpers**

```python
# src/auteur/critic/base.py
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
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_critic_base.py -v`
Expected: 7 PASSED.

- [ ] **Step 5: Commit**

```bash
git add src/auteur/critic/base.py tests/test_critic_base.py
git commit -m "feat(critic): add parse_findings_yaml and shared bible/outline formatters"
```

---

### Task 5: Contract critic

**Files:**
- Create: `src/auteur/critic/contract.py`
- Test: `tests/test_critic_contract.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_critic_contract.py
from pathlib import Path

from auteur.blueprint import StoryBlueprint
from auteur.bible import StoryBible
from auteur.critic.contract import run as run_contract, SYSTEM_PROMPT
from auteur.llm import LLMResponse
from auteur.llm.fake import FakeClient


SAMPLE_YAML = Path(__file__).parent.parent / "examples" / "sample_blueprint.yaml"


def _sample_outline() -> dict:
    return {
        "scope": "chapter",
        "chapter_index": 1,
        "scenes": [{"scene_id": "s1", "summary": "Kael rides into town."}],
    }


def test_contract_critic_renders_prompt_with_required_sections(tmp_path):
    blueprint = StoryBlueprint.from_yaml(SAMPLE_YAML)
    bible = StoryBible(tmp_path / "b.json")
    bible.upsert_character("Kael", location="taverntown", physical="broken_arm")

    fake_response = """findings: []"""
    client = FakeClient([LLMResponse(text=fake_response, input_tokens=10, output_tokens=2)])

    findings = run_contract(
        draft="A long prose chapter about Kael.",
        outline=_sample_outline(),
        blueprint=blueprint,
        bible=bible,
        chapter_index=1,
        llm=client,
    )

    assert findings == []
    assert len(client.calls) == 1
    user = client.calls[0].user
    assert "CONTRACT RULES" in user
    assert "FORBIDDEN TROPES" in user
    assert "BIBLE CONTEXT" in user
    assert "DRAFT" in user
    # Bible state surfaced
    assert "broken_arm" in user


def test_contract_critic_parses_error_finding(tmp_path):
    blueprint = StoryBlueprint.from_yaml(SAMPLE_YAML)
    bible = StoryBible(tmp_path / "b.json")
    bible.upsert_character("Kael", location="taverntown", physical="broken_arm")

    fake_response = """findings:
  - severity: error
    rule: "forbidden_trope:chosen_one_prophecy"
    evidence: "scene 2: 'the prophecy named him chosen heir'"
    requested_change: "remove all prophecy framing"
"""
    client = FakeClient([LLMResponse(text=fake_response, input_tokens=10, output_tokens=20)])

    findings = run_contract(
        draft="...",
        outline=_sample_outline(),
        blueprint=blueprint,
        bible=bible,
        chapter_index=1,
        llm=client,
    )

    assert len(findings) == 1
    assert findings[0].critic == "contract"
    assert findings[0].severity == "error"
    assert "chosen_one_prophecy" in findings[0].rule


def test_contract_critic_uses_low_temperature(tmp_path):
    blueprint = StoryBlueprint.from_yaml(SAMPLE_YAML)
    bible = StoryBible(tmp_path / "b.json")
    client = FakeClient([LLMResponse(text="findings: []", input_tokens=1, output_tokens=1)])

    run_contract(
        draft="x",
        outline=_sample_outline(),
        blueprint=blueprint,
        bible=bible,
        chapter_index=1,
        llm=client,
    )

    assert client.calls[0].temperature == 0.0


def test_contract_critic_system_prompt_mentions_word_count_drift():
    assert "word_count" in SYSTEM_PROMPT or "pacing" in SYSTEM_PROMPT
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_critic_contract.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'auteur.critic.contract'`

- [ ] **Step 3: Implement the contract critic**

```python
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
        draft=draft,
        outline=outline,
        blueprint=blueprint,
        bible=bible,
        chapter_index=chapter_index,
    )
    resp = llm.complete(LLMRequest(
        system=system,
        user=user,
        temperature=TEMPERATURE,
        max_tokens=MAX_TOKENS,
    ))
    return parse_findings_yaml(resp.text, critic_name="contract")
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_critic_contract.py -v`
Expected: 4 PASSED.

- [ ] **Step 5: Commit**

```bash
git add src/auteur/critic/contract.py tests/test_critic_contract.py
git commit -m "feat(critic): add contract critic — rules, tropes, continuity, pacing"
```

---

### Task 6: Arc critic

**Files:**
- Create: `src/auteur/critic/arc.py`
- Test: `tests/test_critic_arc.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_critic_arc.py
from pathlib import Path

from auteur.blueprint import StoryBlueprint
from auteur.bible import StoryBible
from auteur.critic.arc import run as run_arc
from auteur.llm import LLMResponse
from auteur.llm.fake import FakeClient


SAMPLE_YAML = Path(__file__).parent.parent / "examples" / "sample_blueprint.yaml"


def _outline_with_arc_advancement():
    return {
        "scope": "chapter",
        "chapter_index": 7,
        "scenes": [{"scene_id": "s1", "pov_character": "Kael", "summary": "Kael deceives a merchant."}],
        "arc_pushes": [{"character": "Kael", "milestone_touched": "First minor deception without guilt.", "delta_pct": 5}],
    }


def test_arc_critic_passes_when_milestone_supported(tmp_path):
    blueprint = StoryBlueprint.from_yaml(SAMPLE_YAML)
    bible = StoryBible(tmp_path / "b.json")
    client = FakeClient([LLMResponse(text="findings: []", input_tokens=5, output_tokens=2)])

    findings = run_arc(
        draft="Kael lied to the merchant without flinching, untroubled.",
        outline=_outline_with_arc_advancement(),
        blueprint=blueprint,
        bible=bible,
        chapter_index=7,
        llm=client,
    )

    assert findings == []


def test_arc_critic_flags_unsupported_milestone(tmp_path):
    blueprint = StoryBlueprint.from_yaml(SAMPLE_YAML)
    bible = StoryBible(tmp_path / "b.json")
    fake = """findings:
  - severity: error
    rule: "arc:milestone_unsupported"
    evidence: "no scene in the draft shows Kael deceiving anyone"
    requested_change: "add a scene where Kael lies without remorse"
"""
    client = FakeClient([LLMResponse(text=fake, input_tokens=5, output_tokens=20)])

    findings = run_arc(
        draft="Kael spent the day repairing his cart.",
        outline=_outline_with_arc_advancement(),
        blueprint=blueprint,
        bible=bible,
        chapter_index=7,
        llm=client,
    )

    assert len(findings) == 1
    assert findings[0].critic == "arc"
    assert findings[0].severity == "error"


def test_arc_critic_user_message_includes_arc_directives(tmp_path):
    blueprint = StoryBlueprint.from_yaml(SAMPLE_YAML)
    bible = StoryBible(tmp_path / "b.json")
    client = FakeClient([LLMResponse(text="findings: []", input_tokens=1, output_tokens=1)])

    run_arc(
        draft="x",
        outline=_outline_with_arc_advancement(),
        blueprint=blueprint,
        bible=bible,
        chapter_index=7,
        llm=client,
    )

    user = client.calls[0].user
    assert "Kael" in user
    assert "corruption" in user
    assert "First minor deception" in user
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_critic_arc.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'auteur.critic.arc'`

- [ ] **Step 3: Implement the arc critic**

```python
# src/auteur/critic/arc.py
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
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_critic_arc.py -v`
Expected: 3 PASSED.

- [ ] **Step 5: Commit**

```bash
git add src/auteur/critic/arc.py tests/test_critic_arc.py
git commit -m "feat(critic): add arc critic"
```

---

### Task 7: Tension critic

**Files:**
- Create: `src/auteur/critic/tension.py`
- Test: `tests/test_critic_tension.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_critic_tension.py
from pathlib import Path

from auteur.blueprint import StoryBlueprint
from auteur.bible import StoryBible
from auteur.critic.tension import run as run_tension
from auteur.llm import LLMResponse
from auteur.llm.fake import FakeClient


SAMPLE_YAML = Path(__file__).parent.parent / "examples" / "sample_blueprint.yaml"


def test_tension_critic_passes_when_within_tolerance(tmp_path):
    blueprint = StoryBlueprint.from_yaml(SAMPLE_YAML)
    bible = StoryBible(tmp_path / "b.json")
    outline = {"scope": "chapter", "estimated_chapter_tension": 4}
    client = FakeClient([LLMResponse(text="findings: []", input_tokens=1, output_tokens=1)])

    findings = run_tension(
        draft="A quiet conversation by the hearth.",
        outline=outline,
        blueprint=blueprint,
        bible=bible,
        chapter_index=1,
        llm=client,
    )

    assert findings == []


def test_tension_critic_flags_severe_drift(tmp_path):
    blueprint = StoryBlueprint.from_yaml(SAMPLE_YAML)
    bible = StoryBible(tmp_path / "b.json")
    outline = {"scope": "chapter", "estimated_chapter_tension": 9}
    fake = """findings:
  - severity: error
    rule: "tension:drift"
    evidence: "the draft is a contemplative bonding scene; no conflict appears"
    requested_change: "rewrite to deliver active conflict; bring in the antagonist"
"""
    client = FakeClient([LLMResponse(text=fake, input_tokens=1, output_tokens=10)])

    findings = run_tension(
        draft="They sat by the river and reflected on their friendship.",
        outline=outline,
        blueprint=blueprint,
        bible=bible,
        chapter_index=22,
        llm=client,
    )

    assert findings and findings[0].severity == "error"


def test_tension_critic_includes_target_in_prompt(tmp_path):
    blueprint = StoryBlueprint.from_yaml(SAMPLE_YAML)
    bible = StoryBible(tmp_path / "b.json")
    outline = {"scope": "chapter", "estimated_chapter_tension": 9}
    client = FakeClient([LLMResponse(text="findings: []", input_tokens=1, output_tokens=1)])

    run_tension(
        draft="x",
        outline=outline,
        blueprint=blueprint,
        bible=bible,
        chapter_index=22,  # midpoint_battle in sample
        llm=client,
    )

    user = client.calls[0].user
    assert "9" in user  # target from outline
    assert "midpoint_battle" in user  # waveform label
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_critic_tension.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'auteur.critic.tension'`

- [ ] **Step 3: Implement the tension critic**

```python
# src/auteur/critic/tension.py
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
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_critic_tension.py -v`
Expected: 3 PASSED.

- [ ] **Step 5: Commit**

```bash
git add src/auteur/critic/tension.py tests/test_critic_tension.py
git commit -m "feat(critic): add tension critic"
```

---

### Task 8: Slop critic

**Files:**
- Create: `src/auteur/critic/slop.py`
- Test: `tests/test_critic_slop.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_critic_slop.py
from pathlib import Path

from auteur.blueprint import StoryBlueprint
from auteur.bible import StoryBible
from auteur.critic.slop import run as run_slop, SLOP_PHRASES
from auteur.llm import LLMResponse
from auteur.llm.fake import FakeClient


SAMPLE_YAML = Path(__file__).parent.parent / "examples" / "sample_blueprint.yaml"


def test_slop_critic_passes_clean_prose(tmp_path):
    blueprint = StoryBlueprint.from_yaml(SAMPLE_YAML)
    bible = StoryBible(tmp_path / "b.json")
    client = FakeClient([LLMResponse(text="findings: []", input_tokens=1, output_tokens=1)])

    findings = run_slop(
        draft="Kael drew his blade. The cold wind cut through his cloak.",
        outline={"scope": "chapter"},
        blueprint=blueprint,
        bible=bible,
        chapter_index=1,
        llm=client,
    )

    assert findings == []


def test_slop_critic_flags_clichés(tmp_path):
    blueprint = StoryBlueprint.from_yaml(SAMPLE_YAML)
    bible = StoryBible(tmp_path / "b.json")
    fake = """findings:
  - severity: warning
    rule: slop:cliche
    evidence: "'a testament to her courage'"
    requested_change: "show the courage in a concrete action"
"""
    client = FakeClient([LLMResponse(text=fake, input_tokens=1, output_tokens=10)])

    findings = run_slop(
        draft="Her stance was a testament to her courage.",
        outline={"scope": "chapter"},
        blueprint=blueprint,
        bible=bible,
        chapter_index=1,
        llm=client,
    )

    assert findings and findings[0].critic == "slop"


def test_slop_phrases_list_is_nonempty():
    assert isinstance(SLOP_PHRASES, list) and len(SLOP_PHRASES) >= 5
    assert all(isinstance(p, str) for p in SLOP_PHRASES)


def test_slop_critic_includes_phrase_list_in_prompt(tmp_path):
    blueprint = StoryBlueprint.from_yaml(SAMPLE_YAML)
    bible = StoryBible(tmp_path / "b.json")
    client = FakeClient([LLMResponse(text="findings: []", input_tokens=1, output_tokens=1)])

    run_slop(
        draft="x",
        outline={"scope": "chapter"},
        blueprint=blueprint,
        bible=bible,
        chapter_index=1,
        llm=client,
    )

    user = client.calls[0].user
    for phrase in SLOP_PHRASES[:3]:
        assert phrase in user
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_critic_slop.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'auteur.critic.slop'`

- [ ] **Step 3: Implement the slop critic**

```python
# src/auteur/critic/slop.py
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
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_critic_slop.py -v`
Expected: 4 PASSED.

- [ ] **Step 5: Commit**

```bash
git add src/auteur/critic/slop.py tests/test_critic_slop.py
git commit -m "feat(critic): add slop critic with cliche phrase list"
```

---

### Task 9: Theme critic

**Files:**
- Create: `src/auteur/critic/theme.py`
- Test: `tests/test_critic_theme.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_critic_theme.py
from pathlib import Path

from auteur.blueprint import StoryBlueprint
from auteur.bible import StoryBible
from auteur.critic.theme import run as run_theme
from auteur.llm import LLMResponse
from auteur.llm.fake import FakeClient


SAMPLE_YAML = Path(__file__).parent.parent / "examples" / "sample_blueprint.yaml"


def test_theme_critic_emits_only_warnings(tmp_path):
    blueprint = StoryBlueprint.from_yaml(SAMPLE_YAML)
    bible = StoryBible(tmp_path / "b.json")
    fake = """findings:
  - severity: warning
    rule: theme:no_motif_present
    evidence: "no broken-crowns / wounded-hands / rings-that-whisper imagery"
    requested_change: "weave at least one motif into a sensory beat"
"""
    client = FakeClient([LLMResponse(text=fake, input_tokens=1, output_tokens=10)])

    findings = run_theme(
        draft="A long chapter about sailing.",
        outline={"scope": "chapter"},
        blueprint=blueprint,
        bible=bible,
        chapter_index=1,
        llm=client,
    )

    assert findings and findings[0].severity == "warning"


def test_theme_critic_prompt_includes_central_question_and_motifs(tmp_path):
    blueprint = StoryBlueprint.from_yaml(SAMPLE_YAML)
    bible = StoryBible(tmp_path / "b.json")
    client = FakeClient([LLMResponse(text="findings: []", input_tokens=1, output_tokens=1)])

    run_theme(
        draft="x",
        outline={"scope": "chapter"},
        blueprint=blueprint,
        bible=bible,
        chapter_index=1,
        llm=client,
    )

    user = client.calls[0].user
    assert "redemption" in user.lower()
    assert "broken crowns" in user
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_critic_theme.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'auteur.critic.theme'`

- [ ] **Step 3: Implement the theme critic**

```python
# src/auteur/critic/theme.py
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


def run(
    *,
    draft: str,
    outline: dict[str, Any],
    blueprint: StoryBlueprint,
    bible: StoryBible,
    chapter_index: int,
    llm: LLMClient,
) -> list[CriticFinding]:
    system, user = render(draft=draft, blueprint=blueprint, chapter_index=chapter_index)
    resp = llm.complete(LLMRequest(
        system=system, user=user, temperature=TEMPERATURE, max_tokens=MAX_TOKENS,
    ))
    return parse_findings_yaml(resp.text, critic_name="theme")
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_critic_theme.py -v`
Expected: 2 PASSED.

- [ ] **Step 5: Commit**

```bash
git add src/auteur/critic/theme.py tests/test_critic_theme.py
git commit -m "feat(critic): add theme critic"
```

---

### Task 10: run_critics aggregator

**Files:**
- Modify: `src/auteur/critic/__init__.py`
- Test: `tests/test_critic_run.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_critic_run.py
from pathlib import Path

from auteur.blueprint import StoryBlueprint
from auteur.bible import StoryBible
from auteur.critic import run_critics
from auteur.llm import LLMResponse
from auteur.llm.fake import FakeClient


SAMPLE_YAML = Path(__file__).parent.parent / "examples" / "sample_blueprint.yaml"


def _scripted_all_pass():
    return [LLMResponse(text="findings: []", input_tokens=1, output_tokens=1) for _ in range(5)]


def test_run_critics_aggregates_all_passes(tmp_path):
    blueprint = StoryBlueprint.from_yaml(SAMPLE_YAML)
    bible = StoryBible(tmp_path / "b.json")
    client = FakeClient(_scripted_all_pass())

    report = run_critics(
        draft="ok prose",
        outline={"scope": "chapter", "scenes": [{"pov_character": "Kael"}], "estimated_chapter_tension": 4},
        blueprint=blueprint,
        bible=bible,
        chapter_index=1,
        iteration=1,
        llm=client,
    )

    assert report.passed is True
    assert report.findings == []
    assert report.chapter_index == 1
    assert report.iteration == 1
    assert len(client.calls) == 5  # one per critic


def test_run_critics_passed_false_on_any_error(tmp_path):
    blueprint = StoryBlueprint.from_yaml(SAMPLE_YAML)
    bible = StoryBible(tmp_path / "b.json")

    contract_error = """findings:
  - severity: error
    rule: forbidden_trope:chosen_one_prophecy
    evidence: "scene 2"
    requested_change: "remove"
"""
    others_pass = "findings: []"
    client = FakeClient([
        LLMResponse(text=contract_error, input_tokens=1, output_tokens=5),
        LLMResponse(text=others_pass, input_tokens=1, output_tokens=1),
        LLMResponse(text=others_pass, input_tokens=1, output_tokens=1),
        LLMResponse(text=others_pass, input_tokens=1, output_tokens=1),
        LLMResponse(text=others_pass, input_tokens=1, output_tokens=1),
    ])

    report = run_critics(
        draft="prose",
        outline={"scope": "chapter", "scenes": [{"pov_character": "Kael"}], "estimated_chapter_tension": 4},
        blueprint=blueprint,
        bible=bible,
        chapter_index=1,
        iteration=2,
        llm=client,
    )

    assert report.passed is False
    assert len(report.findings) == 1
    assert report.findings[0].critic == "contract"


def test_run_critics_passed_true_when_only_warnings(tmp_path):
    blueprint = StoryBlueprint.from_yaml(SAMPLE_YAML)
    bible = StoryBible(tmp_path / "b.json")

    warn = """findings:
  - severity: warning
    rule: slop:cliche
    evidence: "x"
    requested_change: "y"
"""
    client = FakeClient([
        LLMResponse(text="findings: []", input_tokens=1, output_tokens=1),
        LLMResponse(text="findings: []", input_tokens=1, output_tokens=1),
        LLMResponse(text="findings: []", input_tokens=1, output_tokens=1),
        LLMResponse(text=warn, input_tokens=1, output_tokens=5),
        LLMResponse(text="findings: []", input_tokens=1, output_tokens=1),
    ])

    report = run_critics(
        draft="prose",
        outline={"scope": "chapter", "scenes": [{"pov_character": "Kael"}], "estimated_chapter_tension": 4},
        blueprint=blueprint,
        bible=bible,
        chapter_index=1,
        iteration=1,
        llm=client,
    )

    assert report.passed is True
    assert len(report.findings) == 1
    assert report.findings[0].severity == "warning"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_critic_run.py -v`
Expected: FAIL with `ImportError: cannot import name 'run_critics'`

- [ ] **Step 3: Extend `critic/__init__.py` with `run_critics`**

Replace the file contents with:

```python
# src/auteur/critic/__init__.py
"""Critic system — validation findings and aggregation.

The five built-in critics live in their own modules. run_critics fans
them out in parallel and aggregates into one ValidationReport.
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from typing import Any, Literal

from pydantic import BaseModel

from auteur.bible import StoryBible
from auteur.blueprint import StoryBlueprint
from auteur.llm import LLMClient


class CriticFinding(BaseModel):
    critic: Literal["contract", "arc", "tension", "slop", "theme"]
    severity: Literal["error", "warning"]
    rule: str
    evidence: str
    requested_change: str


class ValidationReport(BaseModel):
    chapter_index: int
    iteration: int
    findings: list[CriticFinding]
    passed: bool


def run_critics(
    *,
    draft: str,
    outline: dict[str, Any],
    blueprint: StoryBlueprint,
    bible: StoryBible,
    chapter_index: int,
    iteration: int,
    llm: LLMClient,
) -> ValidationReport:
    # Imported here to avoid circular imports at package init time.
    from auteur.critic import contract as contract_mod
    from auteur.critic import arc as arc_mod
    from auteur.critic import tension as tension_mod
    from auteur.critic import slop as slop_mod
    from auteur.critic import theme as theme_mod

    runners = [
        contract_mod.run,
        arc_mod.run,
        tension_mod.run,
        slop_mod.run,
        theme_mod.run,
    ]

    kwargs = dict(
        draft=draft,
        outline=outline,
        blueprint=blueprint,
        bible=bible,
        chapter_index=chapter_index,
        llm=llm,
    )

    findings: list[CriticFinding] = []
    with ThreadPoolExecutor(max_workers=len(runners)) as ex:
        futures = [ex.submit(r, **kwargs) for r in runners]
        for f in futures:
            findings.extend(f.result())

    return ValidationReport(
        chapter_index=chapter_index,
        iteration=iteration,
        findings=findings,
        passed=not any(f.severity == "error" for f in findings),
    )


__all__ = ["CriticFinding", "ValidationReport", "run_critics"]
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_critic_run.py tests/test_critic_models.py -v`
Expected: 7 PASSED.

- [ ] **Step 5: Commit**

```bash
git add src/auteur/critic/__init__.py tests/test_critic_run.py
git commit -m "feat(critic): add run_critics — parallel fan-out aggregator"
```

---

### Task 11: Bard agent

**Files:**
- Create: `src/auteur/bard.py`
- Test: `tests/test_bard.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_bard.py
from pathlib import Path

from auteur.blueprint import StoryBlueprint
from auteur.bible import StoryBible
from auteur.bard import render_bard_prompt, postprocess_draft, draft_chapter
from auteur.critic import CriticFinding
from auteur.llm import LLMResponse
from auteur.llm.fake import FakeClient


SAMPLE_YAML = Path(__file__).parent.parent / "examples" / "sample_blueprint.yaml"

OUTLINE = {
    "scope": "chapter",
    "chapter_index": 1,
    "chapter_summary": "Kael returns to the tavern with broken arm.",
    "scenes": [{"scene_id": "s1", "pov_character": "Kael", "summary": "He drinks alone."}],
    "estimated_chapter_tension": 4,
}


def test_render_bard_prompt_draft_mode(tmp_path):
    blueprint = StoryBlueprint.from_yaml(SAMPLE_YAML)
    bible = StoryBible(tmp_path / "b.json")
    bible.upsert_character("Kael", location="taverntown", physical="broken_arm")

    system, user = render_bard_prompt(
        outline=OUTLINE,
        bible=bible,
        blueprint=blueprint,
        chapter_index=1,
        prior_draft=None,
        findings=None,
    )

    assert "POV" in system
    assert "OUTLINE" in user
    assert "Kael" in user
    assert "broken_arm" in user
    assert "REWRITE TASK" not in user


def test_render_bard_prompt_rewrite_mode_includes_findings(tmp_path):
    blueprint = StoryBlueprint.from_yaml(SAMPLE_YAML)
    bible = StoryBible(tmp_path / "b.json")
    finding = CriticFinding(
        critic="contract",
        severity="error",
        rule="forbidden_trope:chosen_one_prophecy",
        evidence="scene 2: prophecy reveal",
        requested_change="remove all prophecy framing",
    )

    system, user = render_bard_prompt(
        outline=OUTLINE,
        bible=bible,
        blueprint=blueprint,
        chapter_index=1,
        prior_draft="The previous draft text.",
        findings=[finding],
    )

    assert "REWRITE TASK" in user
    assert "previous draft text" in user.lower()
    assert "chosen_one_prophecy" in user
    assert "remove all prophecy framing" in user


def test_postprocess_draft_strips_code_fences():
    raw = "```markdown\nThe chapter prose.\n```"
    assert postprocess_draft(raw) == "The chapter prose."


def test_postprocess_draft_trims_whitespace():
    assert postprocess_draft("\n\n  The prose.  \n\n") == "The prose."


def test_postprocess_draft_passes_through_clean_markdown():
    raw = "# Chapter 1\n\nThe prose."
    assert postprocess_draft(raw) == "# Chapter 1\n\nThe prose."


def test_draft_chapter_calls_llm_with_rendered_prompt(tmp_path):
    blueprint = StoryBlueprint.from_yaml(SAMPLE_YAML)
    bible = StoryBible(tmp_path / "b.json")
    bible.upsert_character("Kael", location="taverntown", physical="broken_arm")
    client = FakeClient([LLMResponse(text="The chapter prose.", input_tokens=10, output_tokens=4)])

    prose = draft_chapter(
        outline=OUTLINE,
        bible=bible,
        blueprint=blueprint,
        chapter_index=1,
        llm=client,
    )

    assert prose == "The chapter prose."
    assert len(client.calls) == 1
    assert "Kael" in client.calls[0].user
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_bard.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'auteur.bard'`

- [ ] **Step 3: Implement Bard**

```python
# src/auteur/bard.py
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
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_bard.py -v`
Expected: 6 PASSED.

- [ ] **Step 5: Commit**

```bash
git add src/auteur/bard.py tests/test_bard.py
git commit -m "feat(bard): add Bard agent with draft and rewrite modes"
```

---

### Task 12: PipelineRunner.draft_chapter — full loop

**Files:**
- Modify: `src/auteur/pipeline.py`
- Test: `tests/test_pipeline_draft.py`

This task wires Cartographer → Bard → critics → iterate. Cartographer outputs are parsed from YAML; the Bard sees the parsed outline; critics see the parsed outline plus the prose draft.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_pipeline_draft.py
from pathlib import Path

import pytest

from auteur.project import Project
from auteur.blueprint import StoryBlueprint
from auteur.pipeline import PipelineRunner
from auteur.llm import LLMResponse
from auteur.llm.fake import FakeClient


SAMPLE_YAML = Path(__file__).parent.parent / "examples" / "sample_blueprint.yaml"


def _cartographer_outline_yaml(tension: int = 4) -> str:
    return f"""
scope: chapter
chapter_index: 1
chapter_summary: Kael returns to the tavern.
scenes:
  - scene_id: s1
    pov_character: Kael
    location: taverntown
    summary: He nurses a drink.
    key_events: [drinks, broods]
    character_state_changes: []
    arc_advancements: []
    estimated_tension: 4
    emotional_tone: subtle unease
arc_pushes: []
contract_compliance: []
expected_elements_touched: []
forbidden_tropes_avoided: [chosen_one_prophecy, resurrected_hero, deus_ex_machina_rescue]
estimated_chapter_tension: {tension}
thematic_reinforcement: redemption costs more than Kael wants to pay
conflict_report: null
"""


def _scripted_draft_iteration(*, fail: bool):
    """One Bard call + 5 critic calls."""
    bard = LLMResponse(text="The prose of Kael at the tavern.", input_tokens=20, output_tokens=10)
    if fail:
        contract = LLMResponse(text="""findings:
  - severity: error
    rule: forbidden_trope:chosen_one_prophecy
    evidence: "scene 1: a prophecy named him"
    requested_change: "remove the prophecy framing"
""", input_tokens=5, output_tokens=10)
    else:
        contract = LLMResponse(text="findings: []", input_tokens=5, output_tokens=2)
    others = [LLMResponse(text="findings: []", input_tokens=1, output_tokens=1) for _ in range(4)]
    return [bard, contract, *others]


def test_draft_chapter_happy_path(tmp_path):
    blueprint = StoryBlueprint.from_yaml(SAMPLE_YAML)
    project = Project.init(tmp_path / "novel", blueprint)

    cartographer = LLMResponse(text=_cartographer_outline_yaml(), input_tokens=50, output_tokens=80)
    iteration = _scripted_draft_iteration(fail=False)
    client = FakeClient([cartographer, *iteration])

    runner = PipelineRunner(blueprint, bible=project.bible)
    result = runner.draft_chapter(1, llm=client, project=project, max_iterations=3)

    assert result.accepted is True
    assert result.iterations == 1
    assert result.final_path is not None and result.final_path.exists()
    assert (project.chapter_dir(1) / "outline.yaml").exists()
    assert (project.chapter_dir(1) / "draft_v1.md").exists()
    assert (project.chapter_dir(1) / "validation_v1.json").exists()
    # Bible recorded the event + tension.
    assert project.bible.data["events"][-1]["chapter_index"] == 1
    assert project.bible.data["realized_tension"] == [4]


def test_draft_chapter_fail_then_pass_path(tmp_path):
    blueprint = StoryBlueprint.from_yaml(SAMPLE_YAML)
    project = Project.init(tmp_path / "novel", blueprint)

    cartographer = LLMResponse(text=_cartographer_outline_yaml(), input_tokens=50, output_tokens=80)
    fail_iter = _scripted_draft_iteration(fail=True)
    pass_iter = _scripted_draft_iteration(fail=False)
    client = FakeClient([cartographer, *fail_iter, *pass_iter])

    runner = PipelineRunner(blueprint, bible=project.bible)
    result = runner.draft_chapter(1, llm=client, project=project, max_iterations=3)

    assert result.accepted is True
    assert result.iterations == 2
    assert (project.chapter_dir(1) / "draft_v1.md").exists()
    assert (project.chapter_dir(1) / "draft_v2.md").exists()
    assert (project.chapter_dir(1) / "final.md").exists()


def test_draft_chapter_exhaustion_path(tmp_path):
    blueprint = StoryBlueprint.from_yaml(SAMPLE_YAML)
    project = Project.init(tmp_path / "novel", blueprint)

    cartographer = LLMResponse(text=_cartographer_outline_yaml(), input_tokens=50, output_tokens=80)
    fail_iter_1 = _scripted_draft_iteration(fail=True)
    fail_iter_2 = _scripted_draft_iteration(fail=True)
    fail_iter_3 = _scripted_draft_iteration(fail=True)
    client = FakeClient([cartographer, *fail_iter_1, *fail_iter_2, *fail_iter_3])

    runner = PipelineRunner(blueprint, bible=project.bible)
    result = runner.draft_chapter(1, llm=client, project=project, max_iterations=3)

    assert result.accepted is False
    assert result.iterations == 3
    assert not (project.chapter_dir(1) / "final.md").exists()
    # Bible NOT updated on rejection.
    assert project.bible.data["events"] == []
    assert project.bible.data["realized_tension"] == []


def test_draft_chapter_conflict_report_short_circuits(tmp_path):
    blueprint = StoryBlueprint.from_yaml(SAMPLE_YAML)
    project = Project.init(tmp_path / "novel", blueprint)

    conflict_yaml = """
scope: chapter
chapter_index: 1
chapter_summary: null
scenes: []
arc_pushes: []
contract_compliance: []
expected_elements_touched: []
forbidden_tropes_avoided: []
estimated_chapter_tension: null
thematic_reinforcement: null
conflict_report: "tension target 3 conflicts with required arc milestone (betrayal)"
"""
    client = FakeClient([LLMResponse(text=conflict_yaml, input_tokens=5, output_tokens=10)])

    runner = PipelineRunner(blueprint, bible=project.bible)
    result = runner.draft_chapter(1, llm=client, project=project, max_iterations=3)

    assert result.accepted is False
    assert result.iterations == 0
    assert result.conflict_report == "tension target 3 conflicts with required arc milestone (betrayal)"
    # Outline written, but no drafts.
    assert (project.chapter_dir(1) / "outline.yaml").exists()
    assert not (project.chapter_dir(1) / "draft_v1.md").exists()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_pipeline_draft.py -v`
Expected: FAIL — `PipelineRunner` has no `draft_chapter` method.

- [ ] **Step 3: Extend PipelineRunner**

Replace the contents of `src/auteur/pipeline.py` with:

```python
# src/auteur/pipeline.py
"""PipelineRunner — orchestrates planning, drafting, validation, iteration."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

import yaml

from auteur.bard import draft_chapter as bard_draft
from auteur.bible import StoryBible
from auteur.blueprint import PlanningCall, StoryBlueprint
from auteur.cartographer import render_cartographer_prompt
from auteur.critic import ValidationReport, run_critics
from auteur.llm import LLMClient, LLMRequest


CARTOGRAPHER_TEMPERATURE = 0.4
CARTOGRAPHER_MAX_TOKENS = 4000


@dataclass
class PlanResult:
    call: PlanningCall
    system_prompt: str
    user_message: str


@dataclass
class DraftResult:
    chapter_index: int
    accepted: bool
    iterations: int
    final_path: Path | None
    last_validation: ValidationReport | None
    conflict_report: str | None
    total_input_tokens: int
    total_output_tokens: int


class PipelineRunner:
    def __init__(self, blueprint: StoryBlueprint, bible: StoryBible | None = None):
        self.blueprint = blueprint
        self.bible = bible

    def plan_chapter(self, chapter_index: int) -> PlanResult:
        call = PlanningCall.for_chapter(self.blueprint, chapter_index)
        system, user = render_cartographer_prompt(call)
        return PlanResult(call=call, system_prompt=system, user_message=user)

    def draft_chapter(
        self,
        chapter_index: int,
        *,
        llm: LLMClient,
        project: Any,  # auteur.project.Project — typed as Any to avoid circular import
        max_iterations: int = 3,
        on_iteration: Callable[[int, ValidationReport], None] | None = None,
    ) -> DraftResult:
        if self.bible is None:
            raise ValueError("PipelineRunner needs a StoryBible to draft chapters.")
        bible = self.bible

        # 1. Plan.
        plan = self.plan_chapter(chapter_index)
        cart_resp = llm.complete(LLMRequest(
            system=plan.system_prompt,
            user=plan.user_message,
            temperature=CARTOGRAPHER_TEMPERATURE,
            max_tokens=CARTOGRAPHER_MAX_TOKENS,
        ))
        outline = _parse_outline_yaml(cart_resp.text)
        project.write_outline(chapter_index, outline)
        total_in = cart_resp.input_tokens
        total_out = cart_resp.output_tokens

        # 2. Conflict short-circuit.
        if outline.get("conflict_report"):
            return DraftResult(
                chapter_index=chapter_index,
                accepted=False,
                iterations=0,
                final_path=None,
                last_validation=None,
                conflict_report=outline["conflict_report"],
                total_input_tokens=total_in,
                total_output_tokens=total_out,
            )

        # 3. Plan -> Draft -> Critique loop.
        prior_draft: str | None = None
        prior_findings: list[Any] | None = None
        last_report: ValidationReport | None = None

        for i in range(1, max_iterations + 1):
            prose = bard_draft(
                outline=outline,
                bible=bible,
                blueprint=self.blueprint,
                chapter_index=chapter_index,
                llm=llm,
                prior_draft=prior_draft,
                findings=prior_findings,
            )
            project.write_draft(chapter_index, i, prose)

            report = run_critics(
                draft=prose,
                outline=outline,
                blueprint=self.blueprint,
                bible=bible,
                chapter_index=chapter_index,
                iteration=i,
                llm=llm,
            )
            project.write_validation(chapter_index, i, report)
            last_report = report

            if on_iteration is not None:
                on_iteration(i, report)

            if report.passed:
                final_path = project.write_final(chapter_index, prose)
                bible.record_event(
                    chapter_index=chapter_index,
                    summary=outline.get("chapter_summary", ""),
                    deltas={"draft_iterations": i},
                )
                tension_score = outline.get("estimated_chapter_tension")
                if isinstance(tension_score, int):
                    bible.record_tension(chapter_index, tension_score)
                bible.save()
                return DraftResult(
                    chapter_index=chapter_index,
                    accepted=True,
                    iterations=i,
                    final_path=final_path,
                    last_validation=report,
                    conflict_report=None,
                    total_input_tokens=total_in,
                    total_output_tokens=total_out,
                )

            prior_draft = prose
            prior_findings = report.findings

        return DraftResult(
            chapter_index=chapter_index,
            accepted=False,
            iterations=max_iterations,
            final_path=None,
            last_validation=last_report,
            conflict_report=None,
            total_input_tokens=total_in,
            total_output_tokens=total_out,
        )


def _parse_outline_yaml(text: str) -> dict[str, Any]:
    stripped = text.strip()
    if stripped.startswith("```"):
        # Strip a fenced code block.
        first_nl = stripped.find("\n")
        last_fence = stripped.rfind("```")
        if first_nl != -1 and last_fence > first_nl:
            stripped = stripped[first_nl + 1 : last_fence].strip()
    try:
        data = yaml.safe_load(stripped)
    except yaml.YAMLError as exc:
        raise ValueError(f"Cartographer YAML parse error: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError("Cartographer response is not a YAML mapping.")
    return data
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_pipeline_draft.py -v`
Expected: 4 PASSED.

- [ ] **Step 5: Run full test suite to confirm nothing regressed**

Run: `pytest -v`
Expected: all tests PASSED.

- [ ] **Step 6: Commit**

```bash
git add src/auteur/pipeline.py tests/test_pipeline_draft.py
git commit -m "feat(pipeline): add draft_chapter — full plan/draft/critique loop"
```

---

### Task 13: AnthropicClient

**Files:**
- Create: `src/auteur/llm/anthropic.py`
- Modify: `pyproject.toml` (add `anthropic` to optional dependencies)

This task does not have unit tests — the client is a thin wrapper around the SDK. End-to-end behavior is exercised in the smoke script (Task 16).

- [ ] **Step 1: Add anthropic to pyproject.toml**

Edit `pyproject.toml`. Add a new optional-dependencies group:

```toml
[project.optional-dependencies]
dev = ["pytest>=8.0"]
anthropic = ["anthropic>=0.39"]
openai = ["openai>=1.40"]
all = ["anthropic>=0.39", "openai>=1.40"]
```

- [ ] **Step 2: Implement AnthropicClient**

```python
# src/auteur/llm/anthropic.py
"""Anthropic SDK client for the LLM Protocol.

Defaults to claude-sonnet-4-6. Caches the system prompt so repeated calls
within a chapter (especially the five critics on the same draft) share
cached input.

Requires `pip install auteur[anthropic]`.
"""

from __future__ import annotations

import os

from auteur.llm import LLMRequest, LLMResponse


_DEFAULT_MODEL = "claude-sonnet-4-6"


class AnthropicClient:
    def __init__(self, *, api_key: str | None = None, default_model: str = _DEFAULT_MODEL):
        try:
            from anthropic import Anthropic
        except ImportError as exc:
            raise ImportError(
                "AnthropicClient requires the anthropic SDK. "
                "Install with: pip install auteur[anthropic]"
            ) from exc
        self._sdk = Anthropic(api_key=api_key or os.environ.get("ANTHROPIC_API_KEY"))
        self._default_model = default_model

    def complete(self, req: LLMRequest) -> LLMResponse:
        model = req.model or self._default_model
        result = self._sdk.messages.create(
            model=model,
            max_tokens=req.max_tokens,
            temperature=req.temperature,
            system=[{
                "type": "text",
                "text": req.system,
                "cache_control": {"type": "ephemeral"},
            }],
            messages=[{"role": "user", "content": req.user}],
        )
        text = "".join(block.text for block in result.content if block.type == "text")
        return LLMResponse(
            text=text,
            input_tokens=result.usage.input_tokens,
            output_tokens=result.usage.output_tokens,
        )
```

- [ ] **Step 3: Verify the import path works without an API key**

Run: `python -c "from auteur.llm.anthropic import AnthropicClient; print('ok')"`
Expected: `ok` printed (instantiation requires the key, but the import does not).

If the `anthropic` package is not installed yet, run `pip install -e .[anthropic]` first; the bare import should still work and print a clean ImportError if the SDK is missing.

- [ ] **Step 4: Commit**

```bash
git add src/auteur/llm/anthropic.py pyproject.toml
git commit -m "feat(llm): add AnthropicClient with prompt caching"
```

---

### Task 14: OpenAIClient

**Files:**
- Create: `src/auteur/llm/openai.py`

- [ ] **Step 1: Implement OpenAIClient**

```python
# src/auteur/llm/openai.py
"""OpenAI SDK client for the LLM Protocol.

Defaults to gpt-4o.

Requires `pip install auteur[openai]`.
"""

from __future__ import annotations

import os

from auteur.llm import LLMRequest, LLMResponse


_DEFAULT_MODEL = "gpt-4o"


class OpenAIClient:
    def __init__(self, *, api_key: str | None = None, default_model: str = _DEFAULT_MODEL):
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise ImportError(
                "OpenAIClient requires the openai SDK. "
                "Install with: pip install auteur[openai]"
            ) from exc
        self._sdk = OpenAI(api_key=api_key or os.environ.get("OPENAI_API_KEY"))
        self._default_model = default_model

    def complete(self, req: LLMRequest) -> LLMResponse:
        model = req.model or self._default_model
        result = self._sdk.chat.completions.create(
            model=model,
            max_tokens=req.max_tokens,
            temperature=req.temperature,
            messages=[
                {"role": "system", "content": req.system},
                {"role": "user", "content": req.user},
            ],
        )
        choice = result.choices[0].message
        return LLMResponse(
            text=choice.content or "",
            input_tokens=result.usage.prompt_tokens,
            output_tokens=result.usage.completion_tokens,
        )
```

- [ ] **Step 2: Verify the import path works**

Run: `python -c "from auteur.llm.openai import OpenAIClient; print('ok')"`
Expected: `ok` printed.

- [ ] **Step 3: Commit**

```bash
git add src/auteur/llm/openai.py
git commit -m "feat(llm): add OpenAIClient"
```

---

### Task 15: CLI extensions — init, draft, accept, retry

**Files:**
- Modify: `src/auteur/cli.py`
- Test: `tests/test_cli.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_cli.py
import json
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

from auteur.cli import main
from auteur.llm import LLMResponse


SAMPLE_YAML = Path(__file__).parent.parent / "examples" / "sample_blueprint.yaml"


def _outline_yaml(tension: int = 4) -> str:
    return f"""
scope: chapter
chapter_index: 1
chapter_summary: A quiet return to the tavern.
scenes: [{{scene_id: s1, pov_character: Kael, location: taverntown, summary: drinks alone, key_events: [], character_state_changes: [], arc_advancements: [], estimated_tension: 4, emotional_tone: subtle unease}}]
arc_pushes: []
contract_compliance: []
expected_elements_touched: []
forbidden_tropes_avoided: [chosen_one_prophecy, resurrected_hero, deus_ex_machina_rescue]
estimated_chapter_tension: {tension}
thematic_reinforcement: redemption costs
conflict_report: null
"""


def test_cli_init_creates_project(tmp_path):
    target = tmp_path / "novel"
    rc = main(["init", str(target), "--from", str(SAMPLE_YAML)])
    assert rc == 0
    assert (target / "blueprint.yaml").exists()
    assert (target / "bible.json").exists()
    assert (target / "chapters").is_dir()


def test_cli_init_refuses_existing(tmp_path):
    target = tmp_path / "novel"
    main(["init", str(target), "--from", str(SAMPLE_YAML)])
    rc = main(["init", str(target), "--from", str(SAMPLE_YAML)])
    assert rc == 1


def test_cli_plan_still_works(tmp_path, capsys):
    rc = main(["plan", str(SAMPLE_YAML), "1"])
    assert rc == 0
    out = capsys.readouterr().out
    assert "SYSTEM PROMPT" in out


def _patch_client(scripted):
    from auteur.llm.fake import FakeClient
    return patch("auteur.cli._build_client", return_value=FakeClient(scripted))


def test_cli_draft_happy_path(tmp_path, capsys):
    target = tmp_path / "novel"
    main(["init", str(target), "--from", str(SAMPLE_YAML)])

    scripted = [
        LLMResponse(text=_outline_yaml(), input_tokens=50, output_tokens=80),
        LLMResponse(text="Chapter 1 prose.", input_tokens=20, output_tokens=10),
        *[LLMResponse(text="findings: []", input_tokens=1, output_tokens=1) for _ in range(5)],
    ]

    with _patch_client(scripted):
        rc = main(["draft", str(target), "1"])

    assert rc == 0
    assert (target / "chapters" / "01" / "final.md").exists()


def test_cli_draft_exhausted_returns_2(tmp_path):
    target = tmp_path / "novel"
    main(["init", str(target), "--from", str(SAMPLE_YAML)])

    fail_iter = [
        LLMResponse(text="The draft.", input_tokens=10, output_tokens=4),
        LLMResponse(text="""findings:
  - severity: error
    rule: forbidden_trope:chosen_one_prophecy
    evidence: x
    requested_change: y
""", input_tokens=5, output_tokens=10),
        *[LLMResponse(text="findings: []", input_tokens=1, output_tokens=1) for _ in range(4)],
    ]
    scripted = [LLMResponse(text=_outline_yaml(), input_tokens=50, output_tokens=80)] + fail_iter * 3

    with _patch_client(scripted):
        rc = main(["draft", str(target), "1", "--max-iterations", "3"])

    assert rc == 2


def test_cli_draft_conflict_returns_3(tmp_path):
    target = tmp_path / "novel"
    main(["init", str(target), "--from", str(SAMPLE_YAML)])

    conflict_yaml = """
scope: chapter
chapter_index: 1
chapter_summary: null
scenes: []
arc_pushes: []
contract_compliance: []
expected_elements_touched: []
forbidden_tropes_avoided: []
estimated_chapter_tension: null
thematic_reinforcement: null
conflict_report: "incompatible inputs"
"""
    scripted = [LLMResponse(text=conflict_yaml, input_tokens=5, output_tokens=10)]

    with _patch_client(scripted):
        rc = main(["draft", str(target), "1"])

    assert rc == 3


def test_cli_accept_promotes_latest_draft(tmp_path):
    target = tmp_path / "novel"
    main(["init", str(target), "--from", str(SAMPLE_YAML)])

    chapter_dir = target / "chapters" / "01"
    chapter_dir.mkdir(parents=True, exist_ok=True)
    (chapter_dir / "draft_v1.md").write_text("v1", encoding="utf-8")
    (chapter_dir / "draft_v2.md").write_text("v2 final", encoding="utf-8")
    (chapter_dir / "outline.yaml").write_text("estimated_chapter_tension: 4\nchapter_summary: ok\n", encoding="utf-8")

    rc = main(["accept", str(target), "1"])
    assert rc == 0
    assert (chapter_dir / "final.md").read_text(encoding="utf-8") == "v2 final"
    bible = json.loads((target / "bible.json").read_text(encoding="utf-8"))
    assert bible["realized_tension"] == [4]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_cli.py -v`
Expected: most cases fail because `init`, `draft`, `accept` subcommands don't exist yet.

- [ ] **Step 3: Replace cli.py with the extended version**

Replace the contents of `src/auteur/cli.py` with:

```python
# src/auteur/cli.py
"""Auteur CLI.

Subcommands:
  init    create a project directory from a blueprint
  plan    render the Cartographer prompt (debug, no LLM call)
  draft   plan -> draft -> critique -> iterate (writes artifacts)
  accept  promote the latest draft_v*.md to final.md and update bible
  retry   continue iterating past previous max-iterations cap
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

import yaml

from auteur.blueprint import StoryBlueprint
from auteur.llm import LLMClient
from auteur.pipeline import PipelineRunner
from auteur.project import Project


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="auteur", description="Agentic narrative engineering toolkit.")
    sub = parser.add_subparsers(dest="command", required=True)

    p_init = sub.add_parser("init", help="Create a new project directory.")
    p_init.add_argument("path", type=Path)
    p_init.add_argument("--from", dest="blueprint_path", type=Path, required=True)

    p_plan = sub.add_parser("plan", help="Render the Cartographer prompt for a chapter (no LLM call).")
    p_plan.add_argument("blueprint", type=Path)
    p_plan.add_argument("chapter", type=int)

    p_draft = sub.add_parser("draft", help="Plan, draft, validate, iterate one chapter.")
    p_draft.add_argument("project", type=Path)
    p_draft.add_argument("chapter", type=int)
    p_draft.add_argument("--max-iterations", type=int, default=3)
    p_draft.add_argument("--provider", choices=["anthropic", "openai"], default="anthropic")
    p_draft.add_argument("--model", default=None)

    p_accept = sub.add_parser("accept", help="Promote the latest draft_v*.md to final.md.")
    p_accept.add_argument("project", type=Path)
    p_accept.add_argument("chapter", type=int)

    p_retry = sub.add_parser("retry", help="Continue iterating past previous max-iterations cap.")
    p_retry.add_argument("project", type=Path)
    p_retry.add_argument("chapter", type=int)
    p_retry.add_argument("--max-iterations", type=int, default=3)
    p_retry.add_argument("--provider", choices=["anthropic", "openai"], default="anthropic")
    p_retry.add_argument("--model", default=None)

    args = parser.parse_args(argv)

    if args.command == "init":
        return _cmd_init(args.path, args.blueprint_path)
    if args.command == "plan":
        return _cmd_plan(args.blueprint, args.chapter)
    if args.command == "draft":
        return _cmd_draft(args.project, args.chapter, args.max_iterations, args.provider, args.model)
    if args.command == "accept":
        return _cmd_accept(args.project, args.chapter)
    if args.command == "retry":
        return _cmd_retry(args.project, args.chapter, args.max_iterations, args.provider, args.model)
    parser.print_help()
    return 2


def _cmd_init(path: Path, blueprint_path: Path) -> int:
    if path.exists():
        print(f"Error: project path already exists: {path}", file=sys.stderr)
        return 1
    if not blueprint_path.exists():
        print(f"Error: blueprint not found: {blueprint_path}", file=sys.stderr)
        return 1
    blueprint = StoryBlueprint.from_yaml(blueprint_path)
    Project.init(path, blueprint)
    print(f"Initialized project at {path}")
    return 0


def _cmd_plan(blueprint_path: Path, chapter_index: int) -> int:
    if not blueprint_path.exists():
        print(f"Error: blueprint file not found: {blueprint_path}", file=sys.stderr)
        return 1
    blueprint = StoryBlueprint.from_yaml(blueprint_path)
    result = PipelineRunner(blueprint).plan_chapter(chapter_index)
    print("--- SYSTEM PROMPT ---\n")
    print(result.system_prompt)
    print("\n--- USER MESSAGE ---\n")
    print(result.user_message)
    return 0


def _cmd_draft(
    project_path: Path,
    chapter_index: int,
    max_iterations: int,
    provider: str,
    model: str | None,
) -> int:
    project = Project.load(project_path)
    client = _build_client(provider, model)
    runner = PipelineRunner(project.blueprint, bible=project.bible)

    def _progress(i: int, report: Any) -> None:
        status = "PASSED" if report.passed else f"FAILED ({sum(1 for f in report.findings if f.severity == 'error')} errors)"
        print(f"  iteration {i}: {status}")

    result = runner.draft_chapter(
        chapter_index,
        llm=client,
        project=project,
        max_iterations=max_iterations,
        on_iteration=_progress,
    )

    if result.conflict_report is not None:
        print(f"CONFLICT: {result.conflict_report}", file=sys.stderr)
        print(f"  See {project.chapter_dir(chapter_index) / 'outline.yaml'} for details.", file=sys.stderr)
        return 3
    if result.accepted:
        print(f"ACCEPTED on iteration {result.iterations}.")
        print(f"  final.md: {result.final_path}")
        print(f"  tokens: {result.total_input_tokens} in / {result.total_output_tokens} out")
        return 0
    print(f"NOT ACCEPTED after {result.iterations} iterations.", file=sys.stderr)
    print(f"  Latest draft and validation kept on disk.", file=sys.stderr)
    print(f"  Edit manually then: auteur accept {project_path} {chapter_index}", file=sys.stderr)
    print(f"  Or:                  auteur retry {project_path} {chapter_index}", file=sys.stderr)
    return 2


def _cmd_accept(project_path: Path, chapter_index: int) -> int:
    project = Project.load(project_path)
    chapter_dir = project.chapter_dir(chapter_index)
    drafts = sorted(chapter_dir.glob("draft_v*.md"), key=lambda p: int(p.stem.removeprefix("draft_v")))
    if not drafts:
        print(f"No drafts found in {chapter_dir}", file=sys.stderr)
        return 1
    latest = drafts[-1]
    project.write_final(chapter_index, latest.read_text(encoding="utf-8"))

    outline_path = chapter_dir / "outline.yaml"
    summary = ""
    tension: int | None = None
    if outline_path.exists():
        outline = yaml.safe_load(outline_path.read_text(encoding="utf-8"))
        summary = outline.get("chapter_summary", "")
        t = outline.get("estimated_chapter_tension")
        if isinstance(t, int):
            tension = t

    project.bible.record_event(chapter_index=chapter_index, summary=summary, deltas={"manually_accepted": True})
    if tension is not None:
        project.bible.record_tension(chapter_index, tension)
    project.bible.save()
    print(f"Accepted {latest.name} as final.md for chapter {chapter_index}.")
    return 0


def _cmd_retry(
    project_path: Path,
    chapter_index: int,
    max_iterations: int,
    provider: str,
    model: str | None,
) -> int:
    # In v1, retry re-runs draft from scratch (fresh planning). A future
    # enhancement could resume from the highest existing draft.
    return _cmd_draft(project_path, chapter_index, max_iterations, provider, model)


def _build_client(provider: str, model: str | None) -> LLMClient:
    """Construct the production client for the chosen provider.

    Patched in tests with a FakeClient.
    """
    if provider == "anthropic":
        from auteur.llm.anthropic import AnthropicClient
        return AnthropicClient(default_model=model or "claude-sonnet-4-6")
    if provider == "openai":
        from auteur.llm.openai import OpenAIClient
        return OpenAIClient(default_model=model or "gpt-4o")
    raise ValueError(f"Unknown provider: {provider}")


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_cli.py -v`
Expected: 7 PASSED.

- [ ] **Step 5: Run full suite**

Run: `pytest -v`
Expected: all PASSED.

- [ ] **Step 6: Commit**

```bash
git add src/auteur/cli.py tests/test_cli.py
git commit -m "feat(cli): add init, draft, accept, retry subcommands"
```

---

### Task 16: Smoke integration test (FakeClient end-to-end)

**Files:**
- Create: `tests/test_engine_v1_smoke.py`

This test exercises the full pipeline against the sample blueprint, with one rule violation in iteration 1 that gets fixed in iteration 2. It is the "this is working" milestone for Engine v1.

- [ ] **Step 1: Write the test**

```python
# tests/test_engine_v1_smoke.py
"""End-to-end smoke test for Engine v1 against the sample blueprint.

Iteration 1 violates a forbidden trope; iteration 2 fixes it. The test
asserts: final.md is written, bible records the event and tension, and
the chapter directory contains every expected artifact.
"""

import json
from pathlib import Path

from auteur.cli import main
from auteur.llm import LLMResponse
from unittest.mock import patch


SAMPLE_YAML = Path(__file__).parent.parent / "examples" / "sample_blueprint.yaml"


def _outline(tension: int = 4) -> str:
    return f"""
scope: chapter
chapter_index: 1
chapter_summary: Kael returns to the tavern with a broken arm.
scenes:
  - scene_id: s1
    pov_character: Kael
    location: taverntown
    summary: He nurses a drink and reflects.
    key_events: [drinks, broods, refuses Lira's offer of help]
    character_state_changes: []
    arc_advancements: []
    estimated_tension: {tension}
    emotional_tone: subtle unease
arc_pushes: []
contract_compliance: []
expected_elements_touched: []
forbidden_tropes_avoided: [chosen_one_prophecy, resurrected_hero, deus_ex_machina_rescue]
estimated_chapter_tension: {tension}
thematic_reinforcement: redemption costs more than Kael wants to admit.
conflict_report: null
"""


def _all_pass_critics():
    return [LLMResponse(text="findings: []", input_tokens=1, output_tokens=1) for _ in range(5)]


def _failing_contract_then_pass_others():
    fail = LLMResponse(
        text="""findings:
  - severity: error
    rule: forbidden_trope:chosen_one_prophecy
    evidence: "scene 1: a prophecy named him chosen heir"
    requested_change: "remove all prophecy framing"
""",
        input_tokens=5,
        output_tokens=20,
    )
    others = [LLMResponse(text="findings: []", input_tokens=1, output_tokens=1) for _ in range(4)]
    return [fail, *others]


def test_engine_v1_smoke_fail_then_pass(tmp_path):
    target = tmp_path / "shattered_crown"
    rc = main(["init", str(target), "--from", str(SAMPLE_YAML)])
    assert rc == 0

    scripted = [
        # Cartographer
        LLMResponse(text=_outline(), input_tokens=80, output_tokens=120),
        # Iteration 1: Bard, then 5 critics (contract fails)
        LLMResponse(text="The first draft, with a prophecy...", input_tokens=20, output_tokens=10),
        *_failing_contract_then_pass_others(),
        # Iteration 2: Bard rewrites, all critics pass
        LLMResponse(text="The second draft, prophecy excised. Just Kael at the tavern.",
                    input_tokens=25, output_tokens=15),
        *_all_pass_critics(),
    ]

    from auteur.llm.fake import FakeClient
    with patch("auteur.cli._build_client", return_value=FakeClient(scripted)):
        rc = main(["draft", str(target), "1", "--max-iterations", "3"])

    assert rc == 0

    chapter_dir = target / "chapters" / "01"
    assert (chapter_dir / "outline.yaml").exists()
    assert (chapter_dir / "draft_v1.md").exists()
    assert (chapter_dir / "validation_v1.json").exists()
    assert (chapter_dir / "draft_v2.md").exists()
    assert (chapter_dir / "validation_v2.json").exists()
    assert (chapter_dir / "final.md").exists()

    val_v1 = json.loads((chapter_dir / "validation_v1.json").read_text(encoding="utf-8"))
    val_v2 = json.loads((chapter_dir / "validation_v2.json").read_text(encoding="utf-8"))
    assert val_v1["passed"] is False
    assert val_v2["passed"] is True

    bible = json.loads((target / "bible.json").read_text(encoding="utf-8"))
    assert len(bible["events"]) == 1
    assert bible["events"][0]["chapter_index"] == 1
    assert bible["realized_tension"] == [4]
```

- [ ] **Step 2: Run the smoke test**

Run: `pytest tests/test_engine_v1_smoke.py -v`
Expected: 1 PASSED.

- [ ] **Step 3: Run the entire suite**

Run: `pytest -v`
Expected: all PASSED. This is the milestone gate for Engine v1.

- [ ] **Step 4: Commit**

```bash
git add tests/test_engine_v1_smoke.py
git commit -m "test: add Engine v1 end-to-end smoke (fail-then-pass path)"
```

---

### Task 17: Real-LLM smoke script (manual, not in CI)

**Files:**
- Create: `scripts/smoke_real_llm.py`
- Create: `scripts/__init__.py` (empty marker so packaging tools ignore it)

This script is run manually before releases against the actual API. It is gated on `ANTHROPIC_API_KEY` and is NOT a pytest target.

- [ ] **Step 1: Implement the script**

```python
# scripts/smoke_real_llm.py
"""Real-LLM smoke test for Engine v1.

Run manually before a release:

    ANTHROPIC_API_KEY=sk-... python scripts/smoke_real_llm.py

Drafts chapter 1 of the sample blueprint against the real Anthropic API
and prints the cost. NOT a pytest target — uses real tokens.
"""

from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

from auteur.blueprint import StoryBlueprint
from auteur.llm.anthropic import AnthropicClient
from auteur.pipeline import PipelineRunner
from auteur.project import Project


SAMPLE_YAML = Path(__file__).parent.parent / "examples" / "sample_blueprint.yaml"


def main() -> int:
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("ANTHROPIC_API_KEY not set; aborting.", file=sys.stderr)
        return 1

    blueprint = StoryBlueprint.from_yaml(SAMPLE_YAML)
    with tempfile.TemporaryDirectory() as tmp:
        project_path = Path(tmp) / "smoke_novel"
        project = Project.init(project_path, blueprint)
        runner = PipelineRunner(blueprint, bible=project.bible)
        client = AnthropicClient()

        def progress(i, report):
            errs = sum(1 for f in report.findings if f.severity == "error")
            warns = sum(1 for f in report.findings if f.severity == "warning")
            print(f"iteration {i}: passed={report.passed} errors={errs} warnings={warns}")

        print("Drafting chapter 1 against the real API...")
        result = runner.draft_chapter(
            1,
            llm=client,
            project=project,
            max_iterations=3,
            on_iteration=progress,
        )

        print()
        print(f"accepted: {result.accepted}")
        print(f"iterations: {result.iterations}")
        print(f"input tokens: {result.total_input_tokens}")
        print(f"output tokens: {result.total_output_tokens}")
        if result.final_path:
            print(f"final.md preview (first 500 chars):")
            print(result.final_path.read_text(encoding='utf-8')[:500])
        if result.conflict_report:
            print(f"CONFLICT: {result.conflict_report}")
            return 3
        return 0 if result.accepted else 2


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 2: Verify the script imports cleanly without running it**

Run: `python -c "import scripts.smoke_real_llm; print('ok')"`

If `scripts` is not on the path, run from the project root with `PYTHONPATH=. python -c ...`. Expected: `ok`.

- [ ] **Step 3: Commit**

```bash
git add scripts/__init__.py scripts/smoke_real_llm.py
git commit -m "test: add manual real-LLM smoke script for Engine v1"
```

---

## Self-Review

I checked the plan against the spec:

**Spec coverage** — every spec section has tasks:
- LLMClient + FakeClient — Task 1 ✓
- AnthropicClient + OpenAIClient — Tasks 13, 14 ✓
- Project class + directory layout — Task 2 ✓
- CriticFinding + ValidationReport — Task 3 ✓
- Critic Protocol + base helpers — Task 4 ✓
- Five critics (contract, arc, tension, slop, theme) — Tasks 5–9 ✓
- run_critics aggregator (parallel fan-out) — Task 10 ✓
- Bard agent (draft + rewrite + post-processing) — Task 11 ✓
- PipelineRunner.draft_chapter, conflict-report short-circuit, bible mutations on accept — Task 12 ✓
- CLI: init / plan / draft / accept / retry, exit codes — Task 15 ✓
- Smoke integration test — Task 16 ✓
- Real-LLM smoke script — Task 17 ✓
- Word-count tolerance — handled in contract critic (Task 5) ✓

**Type/method-name consistency** — `run_critics` signature, `DraftResult` fields, `Project` method names, `LLMRequest`/`LLMResponse` shapes, and `CriticFinding`/`ValidationReport` are all consistent across tasks where they appear.

**Placeholders** — No "TBD", "TODO", "implement later", or "similar to Task N". Every step shows the actual code or command.

**Risks already noted in the spec** — token cost (mitigated by per-critic max_tokens caps in Task 5–9), critic thrash (single rewrite-feedback bundle per iteration in Task 11/12), YAML parse failures (surfaced as findings rather than exceptions in Task 4), word count drift (rule in Task 5), Bible compactness (`format_bible_context` in Task 4 limits to characters mentioned in the outline).
