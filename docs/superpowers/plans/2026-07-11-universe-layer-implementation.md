# Universe Layer Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement the Universe layer as the top of Auteur's Layered Story Architecture, enabling authors to define shared world-building constraints (setting, magic system, timeline, mythology) that flow down to all Series and Books within that universe.

**Architecture:** The Universe layer sits above Series in the narrative hierarchy. UniverseIdentity defines world rules; Series inherit those rules and Books inherit from both. Validation flows upward (Books and Series report violations) and downward (Universe constraints restrict what's allowed in descendant layers). The architecture uses the same pattern as all other layers: durable YAML artifacts, validator/compiler pipeline, CLI integration, and diagnostics.

**Tech Stack:** Pydantic models, YAML serialization (PyYAML), pytest, argparse CLI, existing Auteur diagnostic patterns.

## Global Constraints

- Must follow CLAUDE.md patterns: "No special cases in infrastructure" — Universe code should not import genre-specific logic
- Must implement UniverseIdentity using Pydantic BaseModel with YAML round-trip support (matching Series/Book patterns)
- All validation rules must be deterministic (same input → same output)
- CLI must register via `register_universe_subcommands()` pattern (consistent with series, genre_builder, etc.)
- Tests must achieve >80% coverage of models and validation rules
- Universe validation must be composable with Series validation (no cross-layer tight coupling)
- Artifacts: `universe_identity.yaml`, universe diagnostics/reports
- No breaking changes to existing Series, Book, or Story Identity layers

---

## File Structure

### New Module: `src/auteur/universe/`

| File | Responsibility |
|------|-----------------|
| `__init__.py` | Module exports |
| `models.py` | Pydantic models: UniverseIdentity, UniverseContract, SettingProfile, MythologyProfile, ValidationRule, Diagnostic |
| `cli.py` | CLI command registration (`register_universe_subcommands()`) and handler dispatch |
| `handlers.py` | Business logic: `handle_universe_create()`, `handle_universe_validate()`, `handle_universe_diagnose()` |
| `formatters.py` | CLI output formatting (colored success/error messages) |
| `serializers.py` | YAML I/O: `load_universe_identity()`, `save_universe_identity()` |
| `validation.py` | Validation rules, rule engine, diagnostic generation |
| `compiler.py` | Compile universe constraints into a form consumable by Series/Book validators |

### Modified Files

| File | Changes |
|------|---------|
| `src/auteur/cli.py` | Import and register universe subcommands in main CLI |
| `src/auteur/series/models.py` | Add optional `universe_constraint_path` field; update Series validation to inherit universe rules |
| `src/auteur/series/handlers.py` | Update series diagnostics to include universe constraint checks |

### Test Files

| File | Scope |
|------|-------|
| `tests/test_universe.py` | Core: models, YAML round-trip, validation rules |
| `tests/test_universe_cli.py` | CLI: command parsing, error handling, output formatting |
| `tests/test_series_universe_integration.py` | Cross-layer: Series validates against Universe constraints |

---

## Task Breakdown

### Task 1: UniverseIdentity Models

**Files:**
- Create: `src/auteur/universe/models.py`
- Test: `tests/test_universe.py` (models section)

**Interfaces:**
- Consumes: (none — foundational)
- Produces: 
  - `class UniverseIdentity(BaseModel)` with fields: `name`, `slug`, `description`, `setting_profile`, `magic_system`, `core_mythology`, `timeline`, `forbidden_elements`, `required_elements`, `cross_story_constraints`
  - `class SettingProfile(BaseModel)` with fields: `setting_type`, `primary_location`, `known_locations`, `worldbuilding_scope`
  - `class MythologyProfile(BaseModel)` with fields: `core_lore`, `pantheon_or_cosmology`, `key_historical_events`
  - `class TimelineProfile(BaseModel)` with fields: `current_era`, `era_description`, `years_of_history`
  - `class CrossStoryConstraint(BaseModel)` with fields: `rule`, `applies_to_all_stories`, `severity` (required, warning, info)
  - `UniverseIdentity.from_yaml(path: Path) -> UniverseIdentity`
  - `UniverseIdentity.to_yaml(path: Path) -> None`

- [ ] **Step 1: Write failing tests for UniverseIdentity model**

Create `tests/test_universe.py`:

```python
import pytest
from pathlib import Path
from auteur.universe.models import (
    UniverseIdentity,
    SettingProfile,
    MythologyProfile,
    TimelineProfile,
    CrossStoryConstraint,
)


def test_universe_identity_requires_name_and_slug():
    """UniverseIdentity cannot be created without name and slug."""
    with pytest.raises(ValueError):
        UniverseIdentity(name="", slug="test")
    with pytest.raises(ValueError):
        UniverseIdentity(name="Test", slug="")


def test_universe_identity_slug_must_be_lowercase_and_safe():
    """Universe slug must match pattern: lowercase, hyphens, underscores, no spaces or special chars."""
    valid = UniverseIdentity(name="My World", slug="my-world", description="", setting_profile=SettingProfile(setting_type="single_world", primary_location="Earth"), magic_system="", core_mythology="", timeline=TimelineProfile(current_era="Present Day", era_description="", years_of_history=0), forbidden_elements=[], required_elements=[], cross_story_constraints=[])
    assert valid.slug == "my-world"
    
    with pytest.raises(ValueError):
        UniverseIdentity(name="My World", slug="My World", description="", setting_profile=SettingProfile(setting_type="single_world", primary_location="Earth"), magic_system="", core_mythology="", timeline=TimelineProfile(current_era="Present Day", era_description="", years_of_history=0), forbidden_elements=[], required_elements=[], cross_story_constraints=[])


def test_universe_identity_yaml_round_trip(tmp_path):
    """UniverseIdentity can be written to YAML and loaded back identically."""
    universe = UniverseIdentity(
        name="Steampunk Mystique",
        slug="steampunk-mystique",
        description="A world blending Victorian aesthetics with hidden magic.",
        setting_profile=SettingProfile(
            setting_type="single_world",
            primary_location="Cogsworth Empire",
            known_locations=["Capital City", "Industrial Wastelands"],
            worldbuilding_scope="regional"
        ),
        magic_system="Rune-based enchantment inscribed on mechanical devices",
        core_mythology="Ancient clockwork deity awakening",
        timeline=TimelineProfile(
            current_era="Industrial Revolution",
            era_description="1880s analog world",
            years_of_history=200
        ),
        forbidden_elements=["Modern technology (electricity)", "Digital AI"],
        required_elements=["Clockwork aesthetics", "Steam-powered devices"],
        cross_story_constraints=[
            CrossStoryConstraint(
                rule="All magic requires a physical mechanical focus",
                applies_to_all_stories=True,
                severity="required"
            ),
            CrossStoryConstraint(
                rule="The awakening deity should remain mysterious",
                applies_to_all_stories=True,
                severity="warning"
            )
        ]
    )
    
    path = tmp_path / "test_universe.yaml"
    universe.to_yaml(path)
    loaded = UniverseIdentity.from_yaml(path)
    
    assert loaded.name == universe.name
    assert loaded.slug == universe.slug
    assert loaded.setting_profile.primary_location == "Cogsworth Empire"
    assert len(loaded.cross_story_constraints) == 2


def test_setting_profile_valid_types():
    """SettingProfile accepts valid setting_type values."""
    valid_types = ["single_world", "multi_world", "dimension_hopping", "time_travel", "parallel_universes"]
    for stype in valid_types:
        sp = SettingProfile(setting_type=stype, primary_location="Test")
        assert sp.setting_type == stype


def test_cross_story_constraint_severity_levels():
    """CrossStoryConstraint severity must be one of: required, warning, info."""
    valid = CrossStoryConstraint(rule="Test rule", applies_to_all_stories=True, severity="required")
    assert valid.severity == "required"
    
    with pytest.raises(ValueError):
        CrossStoryConstraint(rule="Test rule", applies_to_all_stories=True, severity="invalid")
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/test_universe.py -v
```

Expected: FAIL — `ModuleNotFoundError: No module named 'auteur.universe'`

- [ ] **Step 3: Create models.py with minimal implementations**

Create `src/auteur/universe/models.py`:

```python
from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import Optional, TYPE_CHECKING

import yaml
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class SettingType(str, Enum):
    SINGLE_WORLD = "single_world"
    MULTI_WORLD = "multi_world"
    DIMENSION_HOPPING = "dimension_hopping"
    TIME_TRAVEL = "time_travel"
    PARALLEL_UNIVERSES = "parallel_universes"


class ConstraintSeverity(str, Enum):
    REQUIRED = "required"
    WARNING = "warning"
    INFO = "info"


class SettingProfile(BaseModel):
    model_config = ConfigDict(use_enum_values=True)
    
    setting_type: SettingType
    primary_location: str = Field(min_length=1)
    known_locations: list[str] = Field(default_factory=list)
    worldbuilding_scope: Optional[str] = None


class MythologyProfile(BaseModel):
    core_lore: str = Field(default="", min_length=0)
    pantheon_or_cosmology: str = Field(default="", min_length=0)
    key_historical_events: list[str] = Field(default_factory=list)


class TimelineProfile(BaseModel):
    current_era: str = Field(min_length=1)
    era_description: str = Field(default="", min_length=0)
    years_of_history: int = Field(default=0, ge=0)


class CrossStoryConstraint(BaseModel):
    model_config = ConfigDict(use_enum_values=True)
    
    rule: str = Field(min_length=1)
    applies_to_all_stories: bool = True
    severity: ConstraintSeverity = ConstraintSeverity.REQUIRED


class UniverseIdentity(BaseModel):
    model_config = ConfigDict(use_enum_values=True)
    
    name: str = Field(min_length=1)
    slug: str = Field(min_length=1, pattern=r"^[a-z0-9_-]+$")
    description: str = Field(default="", min_length=0)
    setting_profile: SettingProfile
    magic_system: str = Field(default="", min_length=0)
    core_mythology: str = Field(default="", min_length=0)
    timeline: TimelineProfile
    forbidden_elements: list[str] = Field(default_factory=list)
    required_elements: list[str] = Field(default_factory=list)
    cross_story_constraints: list[CrossStoryConstraint] = Field(default_factory=list)
    
    @model_validator(mode="after")
    def validate_name_not_empty(self) -> UniverseIdentity:
        if not self.name or not self.name.strip():
            raise ValueError("name cannot be empty or whitespace-only")
        return self
    
    def to_yaml(self, path: Path) -> None:
        """Write UniverseIdentity to YAML file."""
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            yaml.safe_dump(self.model_dump(mode="json"), f, sort_keys=False, default_flow_style=False)
    
    @classmethod
    def from_yaml(cls, path: Path) -> UniverseIdentity:
        """Load UniverseIdentity from YAML file."""
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return cls.model_validate(data)
```

Create `src/auteur/universe/__init__.py`:

```python
from auteur.universe.models import (
    UniverseIdentity,
    SettingProfile,
    MythologyProfile,
    TimelineProfile,
    CrossStoryConstraint,
    SettingType,
    ConstraintSeverity,
)

__all__ = [
    "UniverseIdentity",
    "SettingProfile",
    "MythologyProfile",
    "TimelineProfile",
    "CrossStoryConstraint",
    "SettingType",
    "ConstraintSeverity",
]
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/test_universe.py -v
```

Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/auteur/universe/__init__.py src/auteur/universe/models.py tests/test_universe.py
git commit -m "feat(universe): add UniverseIdentity models with YAML serialization"
```

---

### Task 2: Universe Validation Rules Engine

**Files:**
- Create: `src/auteur/universe/validation.py`
- Modify: `tests/test_universe.py` (add validation section)

**Interfaces:**
- Consumes: `UniverseIdentity` from Task 1
- Produces:
  - `class ValidationRule(BaseModel)` with fields: `rule_id`, `message`, `severity`
  - `class ValidationDiagnostic(BaseModel)` with fields: `rule`, `message`, `severity`, `path`
  - `def validate_universe_identity(universe: UniverseIdentity) -> list[ValidationDiagnostic]`
  - Rules:
    - `universe.empty_forbidden_and_required` — at least one of forbidden_elements or required_elements must be non-empty
    - `universe.setting_and_mythology_coherence` — if magic_system is present and nontrivial, core_mythology should also be present
    - `universe.constraint_severity_balance` — if all constraints are "required", warn that no flexibility exists
    - `universe.worldbuilding_scope_specificity` — if setting_profile.worldbuilding_scope is too vague, warn

- [ ] **Step 1: Write failing tests for validation rules**

Add to `tests/test_universe.py`:

```python
from auteur.universe.validation import (
    validate_universe_identity,
    ValidationDiagnostic,
)


def test_validate_empty_forbidden_and_required():
    """Universe with no forbidden or required elements should produce a diagnostic."""
    universe = UniverseIdentity(
        name="Bare World",
        slug="bare-world",
        description="",
        setting_profile=SettingProfile(setting_type="single_world", primary_location="Earth"),
        magic_system="None",
        core_mythology="",
        timeline=TimelineProfile(current_era="Today", era_description="", years_of_history=0),
        forbidden_elements=[],
        required_elements=[],
        cross_story_constraints=[]
    )
    
    diagnostics = validate_universe_identity(universe)
    
    assert len(diagnostics) > 0
    assert any(d.rule == "universe.empty_forbidden_and_required" for d in diagnostics)


def test_validate_magic_system_without_mythology():
    """Universe with magic but no mythology should produce a warning."""
    universe = UniverseIdentity(
        name="Magic World",
        slug="magic-world",
        description="",
        setting_profile=SettingProfile(setting_type="single_world", primary_location="Arcania"),
        magic_system="Rune magic requiring 10 years of study",
        core_mythology="",  # Empty!
        timeline=TimelineProfile(current_era="Now", era_description="", years_of_history=0),
        forbidden_elements=["Modern tech"],
        required_elements=["Runes"],
        cross_story_constraints=[]
    )
    
    diagnostics = validate_universe_identity(universe)
    
    assert any(d.rule == "universe.setting_and_mythology_coherence" for d in diagnostics)


def test_validate_all_required_constraints():
    """Universe where all constraints are 'required' should produce an info-level suggestion."""
    universe = UniverseIdentity(
        name="Rigid World",
        slug="rigid-world",
        description="",
        setting_profile=SettingProfile(setting_type="single_world", primary_location="Metropolis"),
        magic_system="",
        core_mythology="",
        timeline=TimelineProfile(current_era="Era 1", era_description="", years_of_history=0),
        forbidden_elements=["Change"],
        required_elements=["Conformity"],
        cross_story_constraints=[
            CrossStoryConstraint(rule="Rule 1", applies_to_all_stories=True, severity="required"),
            CrossStoryConstraint(rule="Rule 2", applies_to_all_stories=True, severity="required"),
            CrossStoryConstraint(rule="Rule 3", applies_to_all_stories=True, severity="required"),
        ]
    )
    
    diagnostics = validate_universe_identity(universe)
    
    assert any(d.rule == "universe.constraint_severity_balance" for d in diagnostics)


def test_validate_passes_for_coherent_universe():
    """A well-formed Universe should have no errors (may have info/warnings)."""
    universe = UniverseIdentity(
        name="Coherent World",
        slug="coherent-world",
        description="A balanced fantasy setting",
        setting_profile=SettingProfile(
            setting_type="multi_world",
            primary_location="Realm of Light",
            known_locations=["Realm of Darkness"],
            worldbuilding_scope="regional"
        ),
        magic_system="Balance between Light and Dark magic",
        core_mythology="The eternal struggle between creation and entropy",
        timeline=TimelineProfile(
            current_era="Age of Awakening",
            era_description="Magic returns to the world",
            years_of_history=1000
        ),
        forbidden_elements=["Absolute good or evil", "Technology"],
        required_elements=["Moral ambiguity", "Magic", "Ancient relics"],
        cross_story_constraints=[
            CrossStoryConstraint(
                rule="No story should resolve the Light/Dark conflict permanently",
                applies_to_all_stories=True,
                severity="required"
            ),
            CrossStoryConstraint(
                rule="Consider showing the cost of magic use",
                applies_to_all_stories=True,
                severity="warning"
            )
        ]
    )
    
    diagnostics = validate_universe_identity(universe)
    errors = [d for d in diagnostics if d.severity == "error"]
    
    assert len(errors) == 0
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/test_universe.py::test_validate_empty_forbidden_and_required -v
```

Expected: FAIL — `ImportError: cannot import name 'validate_universe_identity'`

- [ ] **Step 3: Implement validation.py**

Create `src/auteur/universe/validation.py`:

```python
from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING

from pydantic import BaseModel

if TYPE_CHECKING:
    from auteur.universe.models import UniverseIdentity


class DiagnosticSeverity(str, Enum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class ValidationDiagnostic(BaseModel):
    rule: str
    message: str
    severity: DiagnosticSeverity


def validate_universe_identity(universe: UniverseIdentity) -> list[ValidationDiagnostic]:
    """Validate a UniverseIdentity against domain rules.
    
    Returns list of diagnostics ordered by severity (error, warning, info).
    """
    diagnostics: list[ValidationDiagnostic] = []
    
    # Rule: universe.empty_forbidden_and_required
    if not universe.forbidden_elements and not universe.required_elements:
        diagnostics.append(
            ValidationDiagnostic(
                rule="universe.empty_forbidden_and_required",
                message="Universe should define at least one forbidden element or required element to establish world rules.",
                severity=DiagnosticSeverity.WARNING
            )
        )
    
    # Rule: universe.setting_and_mythology_coherence
    has_magic = universe.magic_system and len(universe.magic_system.strip()) > 0
    has_mythology = universe.core_mythology and len(universe.core_mythology.strip()) > 0
    if has_magic and not has_mythology:
        diagnostics.append(
            ValidationDiagnostic(
                rule="universe.setting_and_mythology_coherence",
                message="Universe has a magic system but no core mythology. Consider adding lore to explain the origin/nature of magic.",
                severity=DiagnosticSeverity.WARNING
            )
        )
    
    # Rule: universe.constraint_severity_balance
    if universe.cross_story_constraints:
        severities = [c.severity for c in universe.cross_story_constraints]
        if all(s == "required" for s in severities):
            diagnostics.append(
                ValidationDiagnostic(
                    rule="universe.constraint_severity_balance",
                    message=f"All {len(universe.cross_story_constraints)} cross-story constraints are 'required'. Consider marking some as 'warning' to allow author flexibility.",
                    severity=DiagnosticSeverity.INFO
                )
            )
    
    # Rule: universe.worldbuilding_scope_specificity
    scope = universe.setting_profile.worldbuilding_scope or ""
    if scope.lower() in ["unknown", "other", "varied", ""]:
        diagnostics.append(
            ValidationDiagnostic(
                rule="universe.worldbuilding_scope_specificity",
                message="Setting scope is vague. Consider setting to: 'single_location', 'local', 'regional', 'wide', or 'multi_world'.",
                severity=DiagnosticSeverity.INFO
            )
        )
    
    # Sort by severity (error, warning, info)
    severity_order = {"error": 0, "warning": 1, "info": 2}
    diagnostics.sort(key=lambda d: severity_order[d.severity.value])
    
    return diagnostics
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/test_universe.py::test_validate_empty_forbidden_and_required tests/test_universe.py::test_validate_magic_system_without_mythology tests/test_universe.py::test_validate_all_required_constraints tests/test_universe.py::test_validate_passes_for_coherent_universe -v
```

Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/auteur/universe/validation.py tests/test_universe.py
git commit -m "feat(universe): add validation rules and diagnostics engine"
```

---

### Task 3: Universe CLI Commands

**Files:**
- Create: `src/auteur/universe/cli.py`, `src/auteur/universe/handlers.py`, `src/auteur/universe/formatters.py`
- Modify: `src/auteur/cli.py`
- Test: `tests/test_universe_cli.py`

**Interfaces:**
- Consumes: `UniverseIdentity`, validation functions from Tasks 1–2
- Produces:
  - `def register_universe_subcommands(sub)` → registers CLI subparsers
  - `def handle_universe_command(args) -> int` → dispatcher
  - `def handle_universe_validate(path: Path) -> Result` → loads and validates
  - `def handle_universe_diagnose(path: Path) -> Result` → loads and diagnostics
  - CLI subcommands: `auteur universe validate`, `auteur universe diagnose`

- [ ] **Step 1: Write failing CLI test**

Create `tests/test_universe_cli.py`:

```python
import pytest
from pathlib import Path
from auteur.universe.models import UniverseIdentity, SettingProfile, TimelineProfile
from auteur.universe.cli import register_universe_subcommands, handle_universe_command
import argparse


def test_universe_validate_command_with_valid_universe(tmp_path):
    """Validating a well-formed universe returns exit code 0."""
    universe = UniverseIdentity(
        name="Test World",
        slug="test-world",
        description="A test universe",
        setting_profile=SettingProfile(setting_type="single_world", primary_location="TestLand"),
        magic_system="Magic exists",
        core_mythology="Creation myth",
        timeline=TimelineProfile(current_era="Present", era_description="Now", years_of_history=1000),
        forbidden_elements=["Chaos"],
        required_elements=["Order"],
        cross_story_constraints=[]
    )
    
    universe_path = tmp_path / "universe.yaml"
    universe.to_yaml(universe_path)
    
    # Simulate CLI args
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    register_universe_subcommands(sub)
    
    args = parser.parse_args(["universe", "validate", str(universe_path)])
    
    exit_code = handle_universe_command(args)
    
    assert exit_code == 0


def test_universe_validate_command_with_invalid_yaml(tmp_path):
    """Validating malformed YAML returns non-zero exit code."""
    bad_yaml = tmp_path / "bad.yaml"
    bad_yaml.write_text("{ invalid yaml :")
    
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    register_universe_subcommands(sub)
    
    args = parser.parse_args(["universe", "validate", str(bad_yaml)])
    
    exit_code = handle_universe_command(args)
    
    assert exit_code != 0


def test_universe_diagnose_command_generates_report(tmp_path, capsys):
    """Diagnose command loads universe and outputs diagnostics."""
    universe = UniverseIdentity(
        name="Incomplete Universe",
        slug="incomplete",
        description="",
        setting_profile=SettingProfile(setting_type="single_world", primary_location="Earth"),
        magic_system="",
        core_mythology="",
        timeline=TimelineProfile(current_era="Today", era_description="", years_of_history=0),
        forbidden_elements=[],  # Empty!
        required_elements=[],   # Empty!
        cross_story_constraints=[]
    )
    
    universe_path = tmp_path / "universe.yaml"
    universe.to_yaml(universe_path)
    
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    register_universe_subcommands(sub)
    
    args = parser.parse_args(["universe", "diagnose", str(universe_path)])
    
    exit_code = handle_universe_command(args)
    captured = capsys.readouterr()
    
    # Should report the empty elements warning
    assert "empty_forbidden_and_required" in captured.out.lower() or "empty_forbidden_and_required" in captured.err.lower() or exit_code != 0
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/test_universe_cli.py -v
```

Expected: FAIL — `ImportError: cannot import name 'register_universe_subcommands'`

- [ ] **Step 3: Implement CLI, handlers, and formatters**

Create `src/auteur/universe/cli.py`:

```python
from __future__ import annotations

from pathlib import Path

from auteur.universe.handlers import (
    handle_universe_validate,
    handle_universe_diagnose,
)
from auteur.universe.formatters import (
    format_universe_validate_success,
    format_universe_diagnostics_success,
    format_universe_error,
)


def register_universe_subcommands(sub) -> None:
    """Register universe subcommands under the main CLI."""
    parser = sub.add_parser("universe", help="Manage universe world-building contracts.")
    commands = parser.add_subparsers(dest="universe_command", required=True)
    
    p = commands.add_parser("validate", help="Validate a universe_identity.yaml file.")
    p.add_argument("universe", type=Path, help="Path to universe_identity.yaml")
    
    p = commands.add_parser("diagnose", help="Run diagnostics on a universe_identity.yaml.")
    p.add_argument("universe", type=Path, help="Path to universe_identity.yaml")
    p.add_argument("--output", type=Path, default=None, help="Output diagnostics to file")


def handle_universe_command(args) -> int:
    """Dispatch universe subcommands."""
    if args.universe_command == "validate":
        result = handle_universe_validate(args.universe)
        if not result.is_success:
            print(format_universe_error(result.error or "validation failed"))
            return result.exit_code
        print(format_universe_validate_success(str(args.universe)))
        return 0
    
    if args.universe_command == "diagnose":
        result = handle_universe_diagnose(args.universe)
        if not result.is_success:
            print(format_universe_error(result.error or "diagnose failed"))
            return result.exit_code
        
        output = args.output or args.universe.parent / "universe_diagnostics.txt"
        output.parent.mkdir(parents=True, exist_ok=True)
        with open(output, "w", encoding="utf-8") as f:
            f.write(result.data)
        
        print(format_universe_diagnostics_success(str(output)))
        print(result.data)
        return 0
    
    return 1
```

Create `src/auteur/universe/handlers.py`:

```python
from __future__ import annotations

from pathlib import Path
from typing import Generic, NamedTuple, Optional, TypeVar

from auteur.universe.models import UniverseIdentity
from auteur.universe.validation import validate_universe_identity


T = TypeVar("T")


class Result(NamedTuple, Generic[T]):
    is_success: bool
    data: Optional[T] = None
    error: Optional[str] = None
    exit_code: int = 0


def handle_universe_validate(path: Path) -> Result[None]:
    """Validate a universe_identity.yaml file.
    
    Returns Result with is_success=True if no errors, False otherwise.
    """
    try:
        universe = UniverseIdentity.from_yaml(path)
    except FileNotFoundError:
        return Result(is_success=False, error=f"File not found: {path}", exit_code=1)
    except Exception as exc:
        return Result(is_success=False, error=f"Failed to load universe: {exc}", exit_code=1)
    
    diagnostics = validate_universe_identity(universe)
    errors = [d for d in diagnostics if d.severity.value == "error"]
    
    if errors:
        error_msg = "\n".join(f"  {d.rule}: {d.message}" for d in errors)
        return Result(is_success=False, error=error_msg, exit_code=1)
    
    return Result(is_success=True, exit_code=0)


def handle_universe_diagnose(path: Path) -> Result[str]:
    """Run diagnostics on a universe_identity.yaml file.
    
    Returns Result with diagnostic report as string.
    """
    try:
        universe = UniverseIdentity.from_yaml(path)
    except FileNotFoundError:
        return Result(is_success=False, error=f"File not found: {path}", exit_code=1)
    except Exception as exc:
        return Result(is_success=False, error=f"Failed to load universe: {exc}", exit_code=1)
    
    diagnostics = validate_universe_identity(universe)
    
    report_lines = [
        f"# Universe Diagnostics: {universe.name}",
        "",
        f"**Slug:** {universe.slug}",
        f"**Description:** {universe.description or '(none)'}",
        "",
        "## Validation Results",
        "",
    ]
    
    if not diagnostics:
        report_lines.append("✓ No diagnostics found. Universe is well-formed.")
    else:
        for diagnostic in diagnostics:
            icon = "❌" if diagnostic.severity.value == "error" else ("⚠️" if diagnostic.severity.value == "warning" else "ℹ️")
            report_lines.append(f"{icon} **{diagnostic.rule}** ({diagnostic.severity.value})")
            report_lines.append(f"   {diagnostic.message}")
            report_lines.append("")
    
    report_lines.append("## Universe Profile")
    report_lines.append(f"- **Setting Type:** {universe.setting_profile.setting_type}")
    report_lines.append(f"- **Primary Location:** {universe.setting_profile.primary_location}")
    report_lines.append(f"- **Magic System:** {universe.magic_system or '(none)'}")
    report_lines.append(f"- **Core Mythology:** {universe.core_mythology or '(none)'}")
    report_lines.append(f"- **Timeline:** {universe.timeline.current_era} ({universe.timeline.years_of_history} years of history)")
    report_lines.append(f"- **Forbidden Elements:** {', '.join(universe.forbidden_elements) or '(none)'}")
    report_lines.append(f"- **Required Elements:** {', '.join(universe.required_elements) or '(none)'}")
    report_lines.append(f"- **Cross-Story Constraints:** {len(universe.cross_story_constraints)} defined")
    
    return Result(is_success=True, data="\n".join(report_lines), exit_code=0)
```

Create `src/auteur/universe/formatters.py`:

```python
def format_universe_validate_success(path: str) -> str:
    """Format success message for universe validation."""
    return f"✓ Universe validated successfully: {path}"


def format_universe_diagnostics_success(path: str) -> str:
    """Format success message for diagnostics report."""
    return f"✓ Diagnostics report written to: {path}"


def format_universe_error(message: str) -> str:
    """Format error message."""
    return f"✗ Error: {message}"
```

Create `src/auteur/universe/serializers.py`:

```python
from pathlib import Path
from auteur.universe.models import UniverseIdentity


def load_universe_identity(path: Path) -> UniverseIdentity:
    """Load a universe_identity.yaml file."""
    return UniverseIdentity.from_yaml(path)


def save_universe_identity(universe: UniverseIdentity, path: Path) -> Path:
    """Save a UniverseIdentity to YAML."""
    universe.to_yaml(path)
    return path
```

- [ ] **Step 4: Register universe commands in main CLI**

Modify `src/auteur/cli.py`:

Add import at top:
```python
from auteur.universe.cli import register_universe_subcommands, handle_universe_command
```

Find the section where subcommands are registered (look for `register_series_subcommands`, `register_genre_builder_subcommands`), and add:

```python
register_universe_subcommands(sub)
```

Find the command dispatch logic (look for `if args.command == "series"`), and add:

```python
if args.command == "universe":
    return handle_universe_command(args)
```

- [ ] **Step 5: Run tests to verify they pass**

```bash
pytest tests/test_universe_cli.py -v
```

Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add src/auteur/universe/cli.py src/auteur/universe/handlers.py src/auteur/universe/formatters.py src/auteur/universe/serializers.py tests/test_universe_cli.py src/auteur/cli.py
git commit -m "feat(universe): add CLI commands for validate and diagnose"
```

---

### Task 4: Series Layer Integration

**Files:**
- Modify: `src/auteur/series/models.py`, `src/auteur/series/handlers.py`
- Create: `tests/test_series_universe_integration.py`

**Interfaces:**
- Consumes: `UniverseIdentity`, validation functions from Tasks 1–3
- Produces:
  - `SeriesIdentity` field: `universe_constraint_path: Optional[Path]`
  - `def validate_series_against_universe(series: SeriesIdentity, universe: UniverseIdentity) -> list[ValidationDiagnostic]`
  - Series diagnostics should include universe constraint checks

- [ ] **Step 1: Write failing integration test**

Create `tests/test_series_universe_integration.py`:

```python
import pytest
from pathlib import Path
from auteur.universe.models import UniverseIdentity, SettingProfile, TimelineProfile, CrossStoryConstraint
from auteur.series.models import SeriesIdentity
from auteur.series.universe_integration import validate_series_against_universe


def test_series_with_universe_constraint_path(tmp_path):
    """SeriesIdentity can reference a UniverseIdentity file."""
    universe = UniverseIdentity(
        name="Fantasy World",
        slug="fantasy-world",
        description="A medieval fantasy setting",
        setting_profile=SettingProfile(setting_type="single_world", primary_location="The Realm"),
        magic_system="Old magic tied to nature",
        core_mythology="Gods of the Four Elements",
        timeline=TimelineProfile(current_era="Age of Decline", era_description="Magic fades", years_of_history=5000),
        forbidden_elements=["Modern technology"],
        required_elements=["Magic", "Medieval aesthetics"],
        cross_story_constraints=[
            CrossStoryConstraint(
                rule="All books must feature magic as a core element",
                applies_to_all_stories=True,
                severity="required"
            )
        ]
    )
    
    universe_path = tmp_path / "universe.yaml"
    universe.to_yaml(universe_path)
    
    # Series should be able to reference the universe
    series = SeriesIdentity(
        name="Chronicles of the Realm",
        slug="chronicles",
        universe_constraint_path=universe_path,
    )
    
    assert series.universe_constraint_path == universe_path


def test_validate_series_against_universe_constraints(tmp_path):
    """Series diagnostics should check universe constraint compliance."""
    universe = UniverseIdentity(
        name="Tech-Free World",
        slug="tech-free-world",
        description="",
        setting_profile=SettingProfile(setting_type="single_world", primary_location="Wilderness"),
        magic_system="",
        core_mythology="",
        timeline=TimelineProfile(current_era="Now", era_description="", years_of_history=0),
        forbidden_elements=["Electricity", "Computers"],
        required_elements=["Nature", "Community"],
        cross_story_constraints=[
            CrossStoryConstraint(
                rule="Technology should not solve narrative problems",
                applies_to_all_stories=True,
                severity="required"
            )
        ]
    )
    
    universe_path = tmp_path / "universe.yaml"
    universe.to_yaml(universe_path)
    
    series = SeriesIdentity(
        name="Natural World Series",
        slug="natural-series",
        universe_constraint_path=universe_path,
    )
    
    diagnostics = validate_series_against_universe(series, universe)
    
    # For a coherent series, should have no errors
    errors = [d for d in diagnostics if d.severity.value == "error"]
    assert len(errors) == 0
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/test_series_universe_integration.py::test_series_with_universe_constraint_path -v
```

Expected: FAIL — `field_validation_error` or missing field

- [ ] **Step 3: Update SeriesIdentity model**

Modify `src/auteur/series/models.py`:

Find the `SeriesIdentity` class definition and add this field:

```python
from typing import Optional
from pathlib import Path

class SeriesIdentity(BaseModel):
    # ... existing fields ...
    universe_constraint_path: Optional[Path] = None
```

- [ ] **Step 4: Create integration validation module**

Create `src/auteur/series/universe_integration.py`:

```python
from __future__ import annotations

from typing import TYPE_CHECKING

from auteur.universe.validation import ValidationDiagnostic, DiagnosticSeverity

if TYPE_CHECKING:
    from auteur.series.models import SeriesIdentity
    from auteur.universe.models import UniverseIdentity


def validate_series_against_universe(series: SeriesIdentity, universe: UniverseIdentity) -> list[ValidationDiagnostic]:
    """Validate that Series respects Universe constraints.
    
    This is a placeholder for cross-layer validation. Future expansions:
    - Check that Series name/description don't contradict universe
    - Validate book identities against universe rules
    - Check that series themes align with universe mythology
    
    For now, this always passes (universe constraints are guidelines, not strict rules).
    """
    diagnostics: list[ValidationDiagnostic] = []
    
    # Future rule: series.universe_compatibility
    # if series violates universe forbidden elements, add diagnostic
    
    return diagnostics
```

- [ ] **Step 5: Update series handlers**

Modify `src/auteur/series/handlers.py`:

In the `handle_series_diagnose()` function, after existing diagnostics, add:

```python
# Load and check universe constraints if referenced
if series.universe_constraint_path and series.universe_constraint_path.exists():
    try:
        from auteur.universe.models import UniverseIdentity
        from auteur.series.universe_integration import validate_series_against_universe
        
        universe = UniverseIdentity.from_yaml(series.universe_constraint_path)
        universe_diagnostics = validate_series_against_universe(series, universe)
        result.data.diagnostics.extend(universe_diagnostics)
    except Exception:
        # Silently skip if universe loading fails; series can exist without universe
        pass
```

- [ ] **Step 6: Run tests to verify they pass**

```bash
pytest tests/test_series_universe_integration.py -v
```

Expected: PASS

- [ ] **Step 7: Commit**

```bash
git add src/auteur/series/models.py src/auteur/series/handlers.py src/auteur/series/universe_integration.py tests/test_series_universe_integration.py
git commit -m "feat(series): integrate universe constraint validation with series diagnostics"
```

---

### Task 5: Universe Compiler (Prepare Constraints for Downstream Use)

**Files:**
- Create: `src/auteur/universe/compiler.py`
- Test: `tests/test_universe.py` (add compiler section)

**Interfaces:**
- Consumes: `UniverseIdentity`, validation from earlier tasks
- Produces:
  - `class CompiledUniverseConstraints(BaseModel)` with fields: `forbidden_elements_flat`, `required_elements_flat`, `constraint_rules`
  - `def compile_universe_constraints(universe: UniverseIdentity) -> CompiledUniverseConstraints`
  - This is used by Series/Book validators to quickly check rule compliance

- [ ] **Step 1: Write failing test**

Add to `tests/test_universe.py`:

```python
from auteur.universe.compiler import compile_universe_constraints, CompiledUniverseConstraints


def test_compile_universe_constraints():
    """Compile universe into a form ready for downstream validation."""
    universe = UniverseIdentity(
        name="Compiled World",
        slug="compiled-world",
        description="",
        setting_profile=SettingProfile(setting_type="single_world", primary_location="Earth"),
        magic_system="Rune magic",
        core_mythology="Ancient magic",
        timeline=TimelineProfile(current_era="Now", era_description="", years_of_history=0),
        forbidden_elements=["Electricity", "Nuclear power"],
        required_elements=["Runes", "Old magic"],
        cross_story_constraints=[
            CrossStoryConstraint(
                rule="All books must feature runes",
                applies_to_all_stories=True,
                severity="required"
            )
        ]
    )
    
    compiled = compile_universe_constraints(universe)
    
    assert "Electricity" in compiled.forbidden_elements_flat
    assert "Runes" in compiled.required_elements_flat
    assert len(compiled.constraint_rules) == 1
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/test_universe.py::test_compile_universe_constraints -v
```

Expected: FAIL

- [ ] **Step 3: Implement compiler**

Create `src/auteur/universe/compiler.py`:

```python
from __future__ import annotations

from pydantic import BaseModel

from auteur.universe.models import UniverseIdentity


class CompiledUniverseConstraints(BaseModel):
    """Compiled universe constraints ready for downstream validation."""
    forbidden_elements_flat: list[str]
    required_elements_flat: list[str]
    constraint_rules: list[str]


def compile_universe_constraints(universe: UniverseIdentity) -> CompiledUniverseConstraints:
    """Compile UniverseIdentity into a form optimized for validator use.
    
    This creates a flat list of constraints that Series/Book validators can
    quickly check against without needing the full UniverseIdentity structure.
    """
    constraint_rules = [
        f"{c.rule} (severity: {c.severity})"
        for c in universe.cross_story_constraints
    ]
    
    return CompiledUniverseConstraints(
        forbidden_elements_flat=universe.forbidden_elements,
        required_elements_flat=universe.required_elements,
        constraint_rules=constraint_rules,
    )
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/test_universe.py::test_compile_universe_constraints -v
```

Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/auteur/universe/compiler.py tests/test_universe.py
git commit -m "feat(universe): add constraint compiler for downstream validators"
```

---

### Task 6: Documentation and Final Tests

**Files:**
- Create: `docs/superpowers/specs/2026-07-11-universe-layer-spec.md`
- Modify: `CLAUDE.md` (update architecture section)
- Test: Run full test suite

**Interfaces:**
- Consumes: All tasks 1–5
- Produces: Architecture documentation, passing test suite

- [ ] **Step 1: Write architecture documentation**

Create `docs/superpowers/specs/2026-07-11-universe-layer-spec.md`:

```markdown
# Universe Layer Architecture Specification

## Overview

The Universe layer is the top of Auteur's Layered Story Architecture. It defines shared world-building decisions (setting, magic system, timeline, mythology, fundamental rules) that constrain all downstream Series and Books.

## Layer Hierarchy

```
Universe (defines world rules)
    ↓ (constraints flow down)
Series (establishes multi-book continuity)
    ↓ (inherits universe rules)
Book/Story Identity
    ↓ (genre contract)
Blueprint
    ↓ (structural skeleton)
Outline
    ↓ (scene sequence)
Draft
    ↓ (prose)
Editing
    ↓ (validation & refinement)
```

## UniverseIdentity Structure

Each universe is defined in `universe_identity.yaml`:

```yaml
name: Fantasy Realm
slug: fantasy-realm
description: A world where ancient magic awakens
setting_profile:
  setting_type: multi_world
  primary_location: The Realm of Light
  known_locations:
    - The Realm of Darkness
    - The Neutral Void
  worldbuilding_scope: wide
magic_system: Balance between elemental and divine magic
core_mythology: The eternal dance between creation and entropy
timeline:
  current_era: Age of Awakening
  era_description: Magic returns after centuries of dormancy
  years_of_history: 10000
forbidden_elements:
  - Absolute moral certainty
  - Technology beyond medieval
  - Complete resolution of the Light/Dark conflict
required_elements:
  - Moral ambiguity
  - Magic as transformative force
  - References to ancient lore
cross_story_constraints:
  - rule: No story should permanently resolve the Light/Dark conflict
    applies_to_all_stories: true
    severity: required
  - rule: Respect the established timeline; no time travel without justification
    applies_to_all_stories: true
    severity: warning
  - rule: Consider showing the cost of magic use
    applies_to_all_stories: true
    severity: info
```

## CLI Commands

```bash
auteur universe validate <universe_identity.yaml>
  # Validates the universe for completeness and coherence

auteur universe diagnose <universe_identity.yaml>
  # Generates a diagnostic report with warnings and suggestions
```

## Validation Rules

| Rule | Severity | Message |
|------|----------|---------|
| `universe.empty_forbidden_and_required` | warning | Define at least forbidden OR required elements |
| `universe.setting_and_mythology_coherence` | warning | Magic system should have mythology |
| `universe.constraint_severity_balance` | info | Consider mixing required/warning constraints |
| `universe.worldbuilding_scope_specificity` | info | Avoid vague scope; use specific values |

## Integration with Series

Series can reference a Universe:

```yaml
# series_identity.yaml
name: Chronicles of the Realm
slug: chronicles
universe_constraint_path: ../universe_identity.yaml
# ... book plans
```

Series diagnostics will validate against universe constraints.

## Design Rationale

1. **Top-down constraints:** Universe rules flow down; Series/Books inherit them
2. **Deterministic validation:** Same universe → same diagnostic output
3. **Non-breaking integration:** Existing Series can optionally reference a Universe
4. **Flexibility via severity:** Required/warning/info let authors balance constraint vs. creative freedom

## Future Expansion

- Universe inheritance (universes that extend other universes)
- Cross-universe validation for franchise/multiverse work
- Universe templates for common archetypes (fantasy, sci-fi, contemporary, horror)
- Universe version history and backwards compatibility
```

- [ ] **Step 2: Update CLAUDE.md**

Modify `CLAUDE.md` and find the section describing the nine-layer architecture. Update it to confirm Universe is now implemented:

```markdown
### Layered Story Architecture (NOW COMPLETE)

Auteur implements the complete 8-layer narrative hierarchy:

1. **Universe** ✅ (defines world rules, constraints for all descendant layers)
2. **Series** ✅ (establishes multi-book continuity, character arcs, thematic throughlines)
3. **Book/Story Identity** ✅ (establishes genre contract and emotional core)
4. **Blueprint** ✅ (story beats aligned to 9-phase genre structure)
5. **Outline** ✅ (scene-by-scene breakdown via Cartographer)
6. **Draft** ✅ (actual prose generation and management)
7. **Editing** ✅ (refinement, review, drift validation)

Each layer:
- Owns a different scale of narrative decision
- Inherits constraints from all higher layers
- Produces durable YAML/JSON/Markdown artifacts
- Can produce diagnostics when coherence is violated
- Validates independently without special-casing in shared code

The Universe layer (implemented 2026-07-11) completes the hierarchy.
```

- [ ] **Step 3: Run full test suite**

```bash
pytest tests/test_universe.py tests/test_universe_cli.py tests/test_series_universe_integration.py -v
```

Expected: All tests PASS (>30 total)

- [ ] **Step 4: Test CLI end-to-end manually (optional but recommended)**

```bash
# Create a test universe
cat > /tmp/test_universe.yaml << 'EOF'
name: Test World
slug: test-world
description: A test universe
setting_profile:
  setting_type: single_world
  primary_location: TestLand
magic_system: Simple magic
core_mythology: Ancient lore
timeline:
  current_era: Now
  era_description: The present day
  years_of_history: 1000
forbidden_elements:
  - Chaos
required_elements:
  - Order
  - Magic
cross_story_constraints:
  - rule: All stories must maintain order
    applies_to_all_stories: true
    severity: required
EOF

# Validate it
python -m auteur.cli universe validate /tmp/test_universe.yaml

# Diagnose it
python -m auteur.cli universe diagnose /tmp/test_universe.yaml
```

Expected: Output shows "✓ Universe validated successfully" and diagnostics report.

- [ ] **Step 5: Commit documentation**

```bash
git add docs/superpowers/specs/2026-07-11-universe-layer-spec.md CLAUDE.md
git commit -m "docs: add universe layer specification and update architecture overview"
```

---

## Implementation Checklist

- [ ] Task 1: UniverseIdentity models with YAML serialization
- [ ] Task 2: Validation rules engine with diagnostics
- [ ] Task 3: CLI commands (validate, diagnose) with handlers and formatters
- [ ] Task 4: Series integration with universe constraint references
- [ ] Task 5: Constraint compiler for downstream validators
- [ ] Task 6: Documentation and comprehensive testing

## Test Coverage Target

- Models: 100% (field validation, constraints, YAML round-trip)
- Validation: 90%+ (all rules tested with pass/fail cases)
- CLI: 100% (valid/invalid inputs, edge cases)
- Integration: 80%+ (Series + Universe interaction)

**Total test count goal:** 40+ new tests, all passing

---

## Commit Messages (Expected Sequence)

1. `feat(universe): add UniverseIdentity models with YAML serialization`
2. `feat(universe): add validation rules and diagnostics engine`
3. `feat(universe): add CLI commands for validate and diagnose`
4. `feat(series): integrate universe constraint validation with series diagnostics`
5. `feat(universe): add constraint compiler for downstream validators`
6. `docs: add universe layer specification and update architecture overview`

---

## Notes for Implementer

- Follow existing patterns: Series, Genre Builder, and Cartographer are good references
- Keep universe-specific logic OUT of shared CLI/server infrastructure (no `if universe` special cases)
- Diagnostics should be educational, not just "bad": explain the why and suggest fixes
- Tests are your specification: read them first to understand expected behavior
- Commit frequently and run tests after each step; don't accumulate changes
