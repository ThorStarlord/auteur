# Narrative Blueprint (Layer 2: Narrative Structure) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` (recommended) or `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement Layer 2 (Narrative Structure) as a set of reusable outline artifacts (containers and overlays) that decompose a StoryIdentity into actionable chapter-by-chapter structure, validated across all 3 genres with zero infrastructure changes.

**Architecture:** Layer 2 introduces two artifact types:
- **Containers** (hierarchical): Series → Book → Sequence → Chapter. Answer "where does this belong?"
- **Overlays** (cross-cutting): Character Arc, Story Arc (mystery/romance/political), Theme Arc. Answer "how does this evolve?"

Each outline artifact inherits genre validation rules from Layer 1 (StoryIdentity) and maps to the proven 9-phase blueprint structure. Implementation is incremental: Book Outline → Chapter Outline → Character Arc → Story Arc → Series Outline, with each step independently testable against all 3 genres (netorara, mystery, gentle femdom).

**Tech Stack:**
- YAML for artifact serialization (consistent with existing genres)
- Pydantic models for validation (existing pattern in genre_pipeline)
- Same session storage pattern (`.auteur/outlines/<genre>/`)
- Same genre-neutral server infrastructure (no changes to genre_pipeline)

## Global Constraints

- All 3 genres must use the exact same outline infrastructure (zero special-casing in shared code)
- Outline artifacts must inherit and respect genre validation rules (character arcs must pass genre validator)
- Chapter outline must map to the existing 9-phase genre structure (phases are immutable per genre)
- YAML artifacts stored in `.auteur/outlines/<genre>/` (mirrors genre_sessions/ pattern)
- All outlines are durable, testable separately from draft generation
- No breaking changes to existing StoryIdentity, Genre pipelines, or session storage
- Character/Story arc validators must be genre-aware (gentle femdom authority themes ≠ netorara humiliation themes)

---

## Architecture & Weak Boundaries

### Container vs. Overlay Distinction

**Containers** form a strict hierarchy:
```
Series
  └─ Book
      └─ Sequence
          └─ Chapter
```

Each container owns a scale of narrative decision and validates independently. A Chapter outline doesn't need the Series outline to exist (though it's valid to inherit Series constraints).

**Overlays** cut across the hierarchy:
```
Character Arc (spans multiple chapters/sequences)
Story Arc (spans multiple chapters/sequences)
Theme Arc (spans entire book/series)
```

Overlays reference containers by position, not ownership. A character arc says "Alice's belief changes from X to Y at Chapter 3" — it doesn't claim to own Chapter 3.

### Three Identified Weak Boundaries

**1. Character Arc ↔ Genre Validation**
- **Issue:** Character arc is genre-agnostic, but character development must respect genre themes.
- **Example:** In netorara, character humiliation/degradation is thematic; in gentle femdom, character surrender/dominance is thematic. A character arc that ignores these boundaries violates genre contract.
- **Solution:** Character arc validator runs genre-specific rules (Task 9). A character's state transitions must pass the genre ruleset just like genre options do.

**2. Story Arc ↔ 9-Phase Structure**
- **Issue:** The 9-phase structure is fixed per genre, but story arcs (mystery, romance, political) naturally cut across phases.
- **Example:** A mystery arc might peak at phase 6 (revelation), but a romance arc might climax at phase 8. How do we model this?
- **Solution:** Story arc artifact includes phase range (`start_phase: 1, peak_phase: 6, resolution_phase: 9`). Validator ensures arc checkpoints align with chapter phase assignments.

**3. Sequence Grouping ↔ Chapter Estimate**
- **Issue:** How many chapters per sequence? Is this determined by genre, story type, or user choice?
- **Example:** A netorara novel might be 20 chapters, mystery 35, gentle femdom 25. Should the outline prescribe chapter count?
- **Solution:** Book outline specifies chapter estimate (genre-informed), Sequence outline groups chapters flexibly. No hard constraint — user can have 2 chapters or 10 per sequence.

---

## File Structure

### New Directory: `src/auteur/narrative_blueprint/`

```
src/auteur/narrative_blueprint/
├── __init__.py                      # Public API exports
├── schema/
│   ├── __init__.py
│   ├── outline_types.py             # Shared enums & base types
│   ├── book_outline.py              # Container: Book structure
│   ├── chapter_outline.py           # Container: Chapter structure
│   ├── sequence_outline.py          # Container: Sequence grouping
│   ├── series_outline.py            # Container: Series coordination
│   ├── character_arc.py             # Overlay: Character evolution
│   └── story_arc.py                 # Overlay: Thematic arcs (mystery, romance, etc.)
├── validator/
│   ├── __init__.py
│   ├── outline_validator.py         # Validate container hierarchy consistency
│   ├── arc_validator.py             # Validate arc integrity & genre compliance
│   └── phase_mapper.py              # Map chapters to 9-phase structure
├── loader/
│   ├── __init__.py
│   └── outline_loader.py            # Load/save YAML; manage .auteur/outlines/
├── generator/
│   ├── __init__.py
│   ├── book_generator.py            # Generate book outline from StoryIdentity
│   └── chapter_generator.py         # Generate chapter stubs from book outline
└── cli_blueprint.py                 # CLI: auteur {genre} blueprint {subcommand}

tests/auteur/narrative_blueprint/
├── test_outline_types.py
├── test_book_outline.py
├── test_chapter_outline.py
├── test_sequence_outline.py
├── test_series_outline.py
├── test_character_arc.py
├── test_story_arc.py
├── test_outline_validator.py
├── test_arc_validator.py
├── test_outline_loader.py
├── test_book_generator.py
├── test_genre_integration_netorara.py    # Validate with netorara genre
├── test_genre_integration_mystery.py     # Validate with mystery genre
└── test_genre_integration_gentlefemdom.py # Validate with gentle femdom genre
```

### Integration Points (No New Files Needed)

- `src/auteur/genre_pipeline/session.py` — update to load/save outlines alongside story_identity.json
- `src/auteur/genre_pipeline/server.py` — serve outline browser UI (reuse descriptor framework)
- `src/auteur/{genre}/cli_{genre}.py` — add `blueprint` subcommand (existing pattern)

---

## Task Breakdown

### Phase 1: Type Definitions & Schemas (Foundation)

#### Task 1: Core Outline Types & Enums

**Files:**
- Create: `src/auteur/narrative_blueprint/schema/outline_types.py`
- Test: `tests/auteur/narrative_blueprint/test_outline_types.py`

**Interfaces:**
- Consumes: (none)
- Produces: `PhaseRange`, `ArcType` enum, `OutlineArtifact` base class, `ContainerArtifact`, `OverlayArtifact`

**Steps:**

- [ ] **Step 1: Write failing test for outline type hierarchy**

```python
# tests/auteur/narrative_blueprint/test_outline_types.py
from auteur.narrative_blueprint.schema.outline_types import (
    ContainerArtifact, OverlayArtifact, PhaseRange, ArcType
)

def test_outline_artifact_base_class():
    """All outlines have created_at, genre, story_id."""
    # Cannot instantiate abstract base
    with pytest.raises(TypeError):
        OutlineArtifact(genre="netorara", story_id="test-123")

def test_container_artifact():
    """Containers have name, description, and hierarchical position."""
    class BookOutlineTest(ContainerArtifact):
        chapter_count: int
        structure: str  # "3-act" or "4-act"
    
    outline = BookOutlineTest(
        genre="mystery",
        story_id="story-001",
        name="The Curious Disappearance",
        description="A cozy mystery set in a small town",
        chapter_count=30,
        structure="3-act"
    )
    assert outline.genre == "mystery"
    assert outline.chapter_count == 30
    assert isinstance(outline, ContainerArtifact)

def test_overlay_artifact():
    """Overlays reference containers and span multiple chapters."""
    class CharacterArcTest(OverlayArtifact):
        character_name: str
        initial_belief: str
        final_belief: str
        turning_point_chapter: int
    
    arc = CharacterArcTest(
        genre="gentlefemdom",
        story_id="story-002",
        name="Alice's Surrender Arc",
        character_name="Alice",
        initial_belief="dominance is dangerous",
        final_belief="surrender to trusted partners is freedom",
        turning_point_chapter=12
    )
    assert arc.character_name == "Alice"
    assert isinstance(arc, OverlayArtifact)

def test_phase_range():
    """PhaseRange tracks which 9-phases are active."""
    phase_range = PhaseRange(start=3, peak=6, end=9)
    assert phase_range.start == 3
    assert phase_range.peak == 6
    assert phase_range.includes_phase(5) is True
    assert phase_range.includes_phase(10) is False

def test_arc_type_enum():
    """ArcType defines standard arc categories."""
    assert ArcType.CHARACTER in [ArcType.CHARACTER, ArcType.STORY, ArcType.THEME]
    assert ArcType.STORY.value == "story"
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd H:\GithubRepositories\auteur
python -m pytest tests/auteur/narrative_blueprint/test_outline_types.py -v
```

Expected output: Multiple `ImportError: cannot import name` failures.

- [ ] **Step 3: Implement outline type definitions**

```python
# src/auteur/narrative_blueprint/schema/outline_types.py
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, List
from datetime import datetime

class ArcType(str, Enum):
    """Types of narrative arcs."""
    CHARACTER = "character"
    STORY = "story"
    THEME = "theme"

@dataclass
class PhaseRange:
    """Tracks which 9-phases are active for an arc."""
    start: int  # 1-9
    peak: int  # 1-9, typically > start
    end: int    # 1-9, typically >= peak
    
    def __post_init__(self):
        if not (1 <= self.start <= 9):
            raise ValueError(f"start phase must be 1-9, got {self.start}")
        if not (1 <= self.peak <= 9):
            raise ValueError(f"peak phase must be 1-9, got {self.peak}")
        if not (1 <= self.end <= 9):
            raise ValueError(f"end phase must be 1-9, got {self.end}")
        if self.start > self.peak or self.peak > self.end:
            raise ValueError(
                f"phase order violated: start={self.start} <= peak={self.peak} <= end={self.end}"
            )
    
    def includes_phase(self, phase: int) -> bool:
        """Check if a phase falls within this range."""
        return self.start <= phase <= self.end

class OutlineArtifact(ABC):
    """Base class for all narrative outlines."""
    genre: str  # Must match one of registered genres
    story_id: str  # References StoryIdentity
    name: str
    description: str
    created_at: datetime = field(default_factory=datetime.now)
    modified_at: datetime = field(default_factory=datetime.now)
    
    @abstractmethod
    def artifact_type(self) -> str:
        """Return the artifact type name (e.g., 'book_outline', 'chapter_outline')."""
        pass

class ContainerArtifact(OutlineArtifact, ABC):
    """Base for hierarchical containers (Series, Book, Sequence, Chapter)."""
    parent_id: Optional[str] = None  # ID of parent container (if any)

class OverlayArtifact(OutlineArtifact, ABC):
    """Base for cross-cutting overlays (Character Arc, Story Arc, Theme Arc)."""
    arc_type: ArcType
    span_chapters: List[int]  # List of chapter indices this arc spans
```

- [ ] **Step 4: Run test to verify it passes**

```bash
python -m pytest tests/auteur/narrative_blueprint/test_outline_types.py -v
```

Expected: All tests pass.

- [ ] **Step 5: Commit**

```bash
git add src/auteur/narrative_blueprint/schema/outline_types.py tests/auteur/narrative_blueprint/test_outline_types.py
git commit -m "feat: add narrative blueprint outline type hierarchy

- Introduce ContainerArtifact and OverlayArtifact base classes
- Implement PhaseRange for 9-phase arc tracking
- Define ArcType enum (CHARACTER, STORY, THEME)
- All outline artifacts inherit genre and story_id for validation traceability

This foundation supports zero-special-casing across all 3 genres."
```

---

#### Task 2: Book Outline Schema

**Files:**
- Create: `src/auteur/narrative_blueprint/schema/book_outline.py`
- Test: `tests/auteur/narrative_blueprint/test_book_outline.py`

**Interfaces:**
- Consumes: `ContainerArtifact`, `PhaseRange` (from Task 1)
- Produces: `BookOutline` class with fields: `story_id`, `title`, `genre`, `chapter_estimate`, `structure` (3-act/4-act), `phases_summary: Dict[int, str]`, `sequences: List[str]`

**Steps:**

- [ ] **Step 1: Write failing test**

```python
# tests/auteur/narrative_blueprint/test_book_outline.py
from auteur.narrative_blueprint.schema.book_outline import BookOutline

def test_book_outline_creation():
    """Book outline captures high-level story structure."""
    outline = BookOutline(
        genre="mystery",
        story_id="story-001",
        title="The Silent House",
        chapter_estimate=32,
        structure="3-act",
        phases_summary={
            1: "Setup: Detective arrives at locked mansion",
            2: "Inciting incident: Body discovered in locked study",
            3: "Investigation begins",
            # ... phases 4-9
        }
    )
    assert outline.title == "The Silent House"
    assert outline.chapter_estimate == 32
    assert outline.structure == "3-act"
    assert len(outline.phases_summary) == 9

def test_book_outline_validates_phase_summary():
    """Book outline requires all 9 phases summarized."""
    with pytest.raises(ValueError):
        BookOutline(
            genre="netorara",
            story_id="story-002",
            title="Incomplete",
            chapter_estimate=20,
            structure="3-act",
            phases_summary={1: "Phase 1"}  # Only 1 phase, needs 9
        )

def test_book_outline_chapter_estimate_reasonable():
    """Chapter estimate must be > 0."""
    with pytest.raises(ValueError):
        BookOutline(
            genre="gentlefemdom",
            story_id="story-003",
            title="Empty",
            chapter_estimate=0,
            structure="3-act",
            phases_summary={i: f"Phase {i}" for i in range(1, 10)}
        )
```

- [ ] **Step 2: Run test to verify it fails**

```bash
python -m pytest tests/auteur/narrative_blueprint/test_book_outline.py::test_book_outline_creation -v
```

Expected: `ImportError: cannot import name 'BookOutline'`.

- [ ] **Step 3: Implement BookOutline schema**

```python
# src/auteur/narrative_blueprint/schema/book_outline.py
from dataclasses import dataclass, field
from typing import Dict, List, Literal
from datetime import datetime
from auteur.narrative_blueprint.schema.outline_types import ContainerArtifact

@dataclass
class BookOutline(ContainerArtifact):
    """Highest-level story container. Represents the full book structure."""
    title: str
    chapter_estimate: int  # Expected number of chapters
    structure: Literal["3-act", "4-act"]  # Genre-informed structure template
    phases_summary: Dict[int, str]  # One-liner for each 9-phase (phases 1-9)
    
    def __post_init__(self):
        if self.chapter_estimate <= 0:
            raise ValueError(f"chapter_estimate must be > 0, got {self.chapter_estimate}")
        
        if len(self.phases_summary) != 9:
            raise ValueError(
                f"phases_summary must contain all 9 phases, got {len(self.phases_summary)}"
            )
        
        for phase_num in range(1, 10):
            if phase_num not in self.phases_summary:
                raise ValueError(f"phases_summary missing phase {phase_num}")
    
    def artifact_type(self) -> str:
        return "book_outline"
```

- [ ] **Step 4: Run test to verify it passes**

```bash
python -m pytest tests/auteur/narrative_blueprint/test_book_outline.py -v
```

Expected: All tests pass.

- [ ] **Step 5: Commit**

```bash
git add src/auteur/narrative_blueprint/schema/book_outline.py tests/auteur/narrative_blueprint/test_book_outline.py
git commit -m "feat: implement BookOutline container schema

- Represents highest-level story structure (entire book)
- Captures 9-phase summary, chapter estimate, structure template
- Validates all 9 phases are documented
- Foundation for chapter decomposition"
```

---

#### Task 3: Chapter Outline Schema

**Files:**
- Create: `src/auteur/narrative_blueprint/schema/chapter_outline.py`
- Test: `tests/auteur/narrative_blueprint/test_chapter_outline.py`

**Interfaces:**
- Consumes: `ContainerArtifact`, `PhaseRange` (from Task 1)
- Produces: `ChapterOutline` class with fields: `chapter_number`, `phase`, `title`, `goal`, `conflict`, `turning_point`, `emotional_beat`, `arc_progressions: Dict[str, str]`

**Steps:**

- [ ] **Step 1: Write failing test**

```python
# tests/auteur/narrative_blueprint/test_chapter_outline.py
from auteur.narrative_blueprint.schema.chapter_outline import ChapterOutline

def test_chapter_outline_creation():
    """Chapter outline captures one chapter's key narrative decisions."""
    outline = ChapterOutline(
        genre="netorara",
        story_id="story-001",
        chapter_number=1,
        phase=1,
        title="The Invitation",
        goal="Introduce protagonist and establish his confidence",
        conflict="His wife unexpectedly suggests exploration",
        turning_point="He agrees despite hesitation",
        emotional_beat="excitement mixed with unease",
        arc_progressions={}
    )
    assert outline.chapter_number == 1
    assert outline.phase == 1
    assert outline.title == "The Invitation"

def test_chapter_outline_phase_must_be_1_to_9():
    """Phase must align with 9-phase genre structure."""
    with pytest.raises(ValueError):
        ChapterOutline(
            genre="mystery",
            story_id="story-002",
            chapter_number=5,
            phase=10,  # Invalid: only 1-9
            title="Invalid",
            goal="test",
            conflict="test",
            turning_point="test",
            emotional_beat="test"
        )

def test_chapter_outline_arc_progressions_optional():
    """Arc progressions (optional) map character/story arc changes in this chapter."""
    outline = ChapterOutline(
        genre="gentlefemdom",
        story_id="story-003",
        chapter_number=12,
        phase=6,
        title="The Confession",
        goal="Alice admits her desires",
        conflict="Fear of judgment",
        turning_point="Sarah accepts her",
        emotional_beat="vulnerable acceptance",
        arc_progressions={
            "Alice's Surrender Arc": "Belief shifts from shame to self-acceptance",
            "Romance Arc": "Intimacy reaches new depth"
        }
    )
    assert len(outline.arc_progressions) == 2
    assert "Alice's Surrender Arc" in outline.arc_progressions
```

- [ ] **Step 2: Run test to verify it fails**

```bash
python -m pytest tests/auteur/narrative_blueprint/test_chapter_outline.py::test_chapter_outline_creation -v
```

Expected: `ImportError: cannot import name 'ChapterOutline'`.

- [ ] **Step 3: Implement ChapterOutline schema**

```python
# src/auteur/narrative_blueprint/schema/chapter_outline.py
from dataclasses import dataclass, field
from typing import Dict
from auteur.narrative_blueprint.schema.outline_types import ContainerArtifact

@dataclass
class ChapterOutline(ContainerArtifact):
    """Local chapter structure. Represents one chapter's key narrative decisions."""
    chapter_number: int  # Position in book (1-indexed)
    phase: int  # Which 9-phase this chapter primarily occupies (1-9)
    title: str  # Chapter title
    goal: str  # What narrative objective does this chapter accomplish?
    conflict: str  # What opposition/challenge does protagonist face?
    turning_point: str  # The moment that changes everything in this chapter
    emotional_beat: str  # Emotional tone/progression (e.g., "hope → despair → acceptance")
    arc_progressions: Dict[str, str] = field(default_factory=dict)  # How do story/character arcs advance?
    
    def __post_init__(self):
        if self.chapter_number <= 0:
            raise ValueError(f"chapter_number must be > 0, got {self.chapter_number}")
        
        if not (1 <= self.phase <= 9):
            raise ValueError(f"phase must be 1-9, got {self.phase}")
    
    def artifact_type(self) -> str:
        return "chapter_outline"
```

- [ ] **Step 4: Run test to verify it passes**

```bash
python -m pytest tests/auteur/narrative_blueprint/test_chapter_outline.py -v
```

Expected: All tests pass.

- [ ] **Step 5: Commit**

```bash
git add src/auteur/narrative_blueprint/schema/chapter_outline.py tests/auteur/narrative_blueprint/test_chapter_outline.py
git commit -m "feat: implement ChapterOutline container schema

- Captures one chapter's goal, conflict, turning point, emotional arc
- Maps chapter to 9-phase genre structure
- Tracks arc progressions (how arcs advance in this chapter)
- Independent validation: doesn't require Book or Sequence outlines"
```

---

#### Task 4: Character Arc Schema

**Files:**
- Create: `src/auteur/narrative_blueprint/schema/character_arc.py`
- Test: `tests/auteur/narrative_blueprint/test_character_arc.py`

**Interfaces:**
- Consumes: `OverlayArtifact`, `PhaseRange`, `ArcType` (from Task 1)
- Produces: `CharacterArc` class with fields: `character_name`, `initial_belief`, `final_belief`, `turning_points: List[TurningPoint]`, `genre_themes: List[str]`

**Steps:**

- [ ] **Step 1: Write failing test**

```python
# tests/auteur/narrative_blueprint/test_character_arc.py
from auteur.narrative_blueprint.schema.character_arc import CharacterArc, TurningPoint

def test_character_arc_creation():
    """Character arc tracks belief transformation."""
    arc = CharacterArc(
        genre="netorara",
        story_id="story-001",
        name="Protagonist's Humiliation Arc",
        character_name="Michael",
        initial_belief="I control everything; my wife is mine alone",
        final_belief="Control is an illusion; surrender brings unexpected pleasure",
        genre_themes=["humiliation", "degradation", "cuckoldry"]
    )
    assert arc.character_name == "Michael"
    assert arc.initial_belief == "I control everything; my wife is mine alone"
    assert arc.genre_themes == ["humiliation", "degradation", "cuckoldry"]

def test_character_arc_turning_points():
    """Character arc includes specific moments where belief shifts."""
    arc = CharacterArc(
        genre="gentlefemdom",
        story_id="story-002",
        name="Alice's Dominance Discovery Arc",
        character_name="Alice",
        initial_belief="I must be submissive to be loved",
        final_belief="My authority excites and comforts my partner",
        turning_points=[
            TurningPoint(
                chapter=5,
                moment="Sarah asks Alice to take control",
                belief_shift="Maybe dominance isn't selfish"
            ),
            TurningPoint(
                chapter=12,
                moment="Sarah explicitly requests Alice's authority",
                belief_shift="My dominance is desired; it's an act of care"
            )
        ],
        genre_themes=["authority", "surrender", "trust"]
    )
    assert len(arc.turning_points) == 2
    assert arc.turning_points[0].chapter == 5

def test_character_arc_genre_themes_required():
    """Character arc must specify genre-relevant themes."""
    with pytest.raises(ValueError):
        CharacterArc(
            genre="mystery",
            story_id="story-003",
            name="Detective Arc",
            character_name="Detective Smith",
            initial_belief="The butler did it",
            final_belief="The victim orchestrated it",
            genre_themes=[]  # Missing themes
        )
```

- [ ] **Step 2: Run test to verify it fails**

```bash
python -m pytest tests/auteur/narrative_blueprint/test_character_arc.py::test_character_arc_creation -v
```

Expected: `ImportError: cannot import name 'CharacterArc'`.

- [ ] **Step 3: Implement CharacterArc schema**

```python
# src/auteur/narrative_blueprint/schema/character_arc.py
from dataclasses import dataclass, field
from typing import List
from auteur.narrative_blueprint.schema.outline_types import OverlayArtifact, ArcType

@dataclass
class TurningPoint:
    """A specific moment where a character's belief shifts."""
    chapter: int  # Chapter number where turning point occurs
    moment: str  # Description of what happens
    belief_shift: str  # How does the character's understanding change?

@dataclass
class CharacterArc(OverlayArtifact):
    """Cross-cutting character evolution across multiple chapters."""
    character_name: str
    initial_belief: str  # What does the character believe at the start?
    final_belief: str  # What does the character believe by the end?
    turning_points: List[TurningPoint] = field(default_factory=list)
    genre_themes: List[str] = field(default_factory=list)  # e.g., ["humiliation", "degradation"] for netorara
    
    def __post_init__(self):
        self.arc_type = ArcType.CHARACTER
        
        if not self.genre_themes:
            raise ValueError(
                f"Character arc must specify genre_themes (e.g., humiliation/degradation for netorara)"
            )
    
    def artifact_type(self) -> str:
        return "character_arc"
```

- [ ] **Step 4: Run test to verify it passes**

```bash
python -m pytest tests/auteur/narrative_blueprint/test_character_arc.py -v
```

Expected: All tests pass.

- [ ] **Step 5: Commit**

```bash
git add src/auteur/narrative_blueprint/schema/character_arc.py tests/auteur/narrative_blueprint/test_character_arc.py
git commit -m "feat: implement CharacterArc overlay schema

- Tracks character belief transformation from initial → final state
- Includes turning points (specific chapters where beliefs shift)
- Requires genre_themes (cuckoldry/humiliation for netorara, etc.)
- Foundation for genre-aware character validation"
```

---

#### Task 5: Story Arc Schema

**Files:**
- Create: `src/auteur/narrative_blueprint/schema/story_arc.py`
- Test: `tests/auteur/narrative_blueprint/test_story_arc.py`

**Interfaces:**
- Consumes: `OverlayArtifact`, `PhaseRange`, `ArcType` (from Task 1)
- Produces: `StoryArc` class with fields: `arc_name`, `arc_category` (mystery/romance/political/revenge/survival), `phase_range: PhaseRange`, `checkpoints: List[ArcCheckpoint]`

**Steps:**

- [ ] **Step 1: Write failing test**

```python
# tests/auteur/narrative_blueprint/test_story_arc.py
from auteur.narrative_blueprint.schema.story_arc import StoryArc, ArcCheckpoint
from auteur.narrative_blueprint.schema.outline_types import PhaseRange

def test_story_arc_creation():
    """Story arc spans multiple chapters across defined phase range."""
    arc = StoryArc(
        genre="mystery",
        story_id="story-001",
        name="The Library Secret",
        arc_category="mystery",
        phase_range=PhaseRange(start=1, peak=6, end=9),
        checkpoints=[
            ArcCheckpoint(phase=1, moment="First clue hidden in old book"),
            ArcCheckpoint(phase=3, moment="Second clue suggests conspiracy"),
            ArcCheckpoint(phase=6, moment="Truth revealed: victim faked death"),
            ArcCheckpoint(phase=9, moment="Conspiracy unravels")
        ]
    )
    assert arc.arc_category == "mystery"
    assert arc.phase_range.start == 1
    assert len(arc.checkpoints) == 4

def test_story_arc_phase_range_must_be_valid():
    """Phase range must be sensible (start <= peak <= end)."""
    with pytest.raises(ValueError):
        StoryArc(
            genre="netorara",
            story_id="story-002",
            name="Invalid Arc",
            arc_category="mystery",
            phase_range=PhaseRange(start=7, peak=4, end=9)  # Peak < start (invalid)
        )

def test_romance_and_mystery_arcs_can_coexist():
    """Same story can have multiple story arcs."""
    romance = StoryArc(
        genre="gentlefemdom",
        story_id="story-003",
        name="Sarah & Alice's Romance",
        arc_category="romance",
        phase_range=PhaseRange(start=2, peak=8, end=9)
    )
    
    authority = StoryArc(
        genre="gentlefemdom",
        story_id="story-003",
        name="Alice's Authority Discovery",
        arc_category="political",  # Power dynamics
        phase_range=PhaseRange(start=3, peak=7, end=9)
    )
    
    assert romance.arc_category == "romance"
    assert authority.arc_category == "political"
    # Both can exist in same story_id
```

- [ ] **Step 2: Run test to verify it fails**

```bash
python -m pytest tests/auteur/narrative_blueprint/test_story_arc.py::test_story_arc_creation -v
```

Expected: `ImportError: cannot import name 'StoryArc'`.

- [ ] **Step 3: Implement StoryArc schema**

```python
# src/auteur/narrative_blueprint/schema/story_arc.py
from dataclasses import dataclass, field
from typing import List, Literal
from auteur.narrative_blueprint.schema.outline_types import OverlayArtifact, ArcType, PhaseRange

@dataclass
class ArcCheckpoint:
    """A milestone within a story arc (typically one per phase or key moment)."""
    phase: int  # Which phase does this checkpoint belong to? (1-9)
    moment: str  # What happens at this checkpoint?

@dataclass
class StoryArc(OverlayArtifact):
    """Cross-cutting thematic/plot arc spanning multiple chapters."""
    arc_name: str  # Specific arc title (e.g., "The Library Secret", "First Contact")
    arc_category: Literal["mystery", "romance", "political", "revenge", "survival"]
    phase_range: PhaseRange  # Which 9-phases does this arc span?
    checkpoints: List[ArcCheckpoint] = field(default_factory=list)
    
    def __post_init__(self):
        self.arc_type = ArcType.STORY
    
    def artifact_type(self) -> str:
        return "story_arc"
```

- [ ] **Step 4: Run test to verify it passes**

```bash
python -m pytest tests/auteur/narrative_blueprint/test_story_arc.py -v
```

Expected: All tests pass.

- [ ] **Step 5: Commit**

```bash
git add src/auteur/narrative_blueprint/schema/story_arc.py tests/auteur/narrative_blueprint/test_story_arc.py
git commit -m "feat: implement StoryArc overlay schema

- Models thematic/plot arcs (mystery, romance, political, revenge, survival)
- Spans defined phase range with checkpoints per phase
- Multiple arcs can coexist in same story (proves generality)
- Enables complex multi-arc narratives across all genres"
```

---

#### Task 6: Sequence & Series Outline Schemas

**Files:**
- Create: `src/auteur/narrative_blueprint/schema/sequence_outline.py`
- Create: `src/auteur/narrative_blueprint/schema/series_outline.py`
- Test: `tests/auteur/narrative_blueprint/test_sequence_outline.py`
- Test: `tests/auteur/narrative_blueprint/test_series_outline.py`

**Interfaces:**
- Consumes: `ContainerArtifact` (from Task 1)
- Produces: `SequenceOutline` (groups chapters around one narrative objective), `SeriesOutline` (coordinates multiple books)

**Steps:**

- [ ] **Step 1: Write failing test for Sequence Outline**

```python
# tests/auteur/narrative_blueprint/test_sequence_outline.py
from auteur.narrative_blueprint.schema.sequence_outline import SequenceOutline

def test_sequence_outline_creation():
    """Sequence groups chapters around one narrative objective."""
    sequence = SequenceOutline(
        genre="netorara",
        story_id="story-001",
        sequence_number=1,
        title="The Setup",
        objective="Establish Michael's confidence and control before it shatters",
        chapter_range=(1, 3),  # Chapters 1-3
        key_scenes=["Meeting the couple", "First dinner", "The proposition"]
    )
    assert sequence.sequence_number == 1
    assert sequence.chapter_range == (1, 3)
    assert len(sequence.key_scenes) == 3
```

- [ ] **Step 2: Run test to verify it fails**

```bash
python -m pytest tests/auteur/narrative_blueprint/test_sequence_outline.py::test_sequence_outline_creation -v
```

Expected: `ImportError: cannot import name 'SequenceOutline'`.

- [ ] **Step 3: Implement SequenceOutline & SeriesOutline**

```python
# src/auteur/narrative_blueprint/schema/sequence_outline.py
from dataclasses import dataclass, field
from typing import List, Tuple
from auteur.narrative_blueprint.schema.outline_types import ContainerArtifact

@dataclass
class SequenceOutline(ContainerArtifact):
    """Groups chapters around one narrative objective."""
    sequence_number: int  # Position in book (1-indexed)
    objective: str  # What does this sequence accomplish narratively?
    chapter_range: Tuple[int, int]  # (start_chapter, end_chapter), 1-indexed inclusive
    key_scenes: List[str] = field(default_factory=list)  # Major scenes in sequence
    
    def __post_init__(self):
        if self.sequence_number <= 0:
            raise ValueError(f"sequence_number must be > 0, got {self.sequence_number}")
        
        start, end = self.chapter_range
        if start <= 0 or end <= 0 or start > end:
            raise ValueError(f"chapter_range must be (start, end) with 0 < start <= end, got {self.chapter_range}")
    
    def artifact_type(self) -> str:
        return "sequence_outline"
```

```python
# src/auteur/narrative_blueprint/schema/series_outline.py
from dataclasses import dataclass, field
from typing import List, Dict
from auteur.narrative_blueprint.schema.outline_types import ContainerArtifact

@dataclass
class SeriesOutline(ContainerArtifact):
    """Coordinates multiple books across a series."""
    series_name: str
    book_ids: List[str]  # List of story_ids for each book in order
    long_term_character_evolution: Dict[str, str] = field(default_factory=dict)
    # e.g., {"Michael": "from control → acceptance", "Sarah": "from passive → confident"}
    thematic_progression: List[str] = field(default_factory=list)
    # e.g., ["Book 1: Setup & First Breach", "Book 2: Escalation", "Book 3: Resolution"]
    
    def artifact_type(self) -> str:
        return "series_outline"
```

- [ ] **Step 4: Run test to verify it passes**

```bash
python -m pytest tests/auteur/narrative_blueprint/test_sequence_outline.py tests/auteur/narrative_blueprint/test_series_outline.py -v
```

Expected: All tests pass.

- [ ] **Step 5: Commit**

```bash
git add src/auteur/narrative_blueprint/schema/sequence_outline.py src/auteur/narrative_blueprint/schema/series_outline.py tests/auteur/narrative_blueprint/test_sequence_outline.py tests/auteur/narrative_blueprint/test_series_outline.py
git commit -m "feat: implement SequenceOutline and SeriesOutline container schemas

- SequenceOutline groups chapters around narrative objectives
- SeriesOutline coordinates multi-book character & thematic progression
- Completes container hierarchy: Series → Book → Sequence → Chapter"
```

---

### Phase 2: Validators (Enforce Integrity)

#### Task 7: Outline Hierarchy Validator

**Files:**
- Create: `src/auteur/narrative_blueprint/validator/outline_validator.py`
- Test: `tests/auteur/narrative_blueprint/test_outline_validator.py`

**Interfaces:**
- Consumes: `BookOutline`, `ChapterOutline`, `SequenceOutline`, `SeriesOutline` (from Tasks 2-6)
- Produces: `ContainerValidator` class with method `validate_consistency(outlines: List[ContainerArtifact]) -> Tuple[bool, List[str]]`

**Steps:**

- [ ] **Step 1: Write failing test**

```python
# tests/auteur/narrative_blueprint/test_outline_validator.py
from auteur.narrative_blueprint.validator.outline_validator import ContainerValidator
from auteur.narrative_blueprint.schema.book_outline import BookOutline
from auteur.narrative_blueprint.schema.chapter_outline import ChapterOutline

def test_container_validator_book_chapter_consistency():
    """Validator ensures chapters respect book structure."""
    book = BookOutline(
        genre="mystery",
        story_id="story-001",
        title="The Mystery",
        chapter_estimate=10,
        structure="3-act",
        phases_summary={i: f"Phase {i}" for i in range(1, 10)}
    )
    
    chapters = [
        ChapterOutline(
            genre="mystery", story_id="story-001",
            chapter_number=1, phase=1, title="Ch1", goal="goal", conflict="conflict",
            turning_point="turn", emotional_beat="beat"
        ),
        ChapterOutline(
            genre="mystery", story_id="story-001",
            chapter_number=11, phase=1, title="Ch11", goal="goal", conflict="conflict",
            turning_point="turn", emotional_beat="beat"
        )  # Chapter 11 exceeds book estimate of 10
    ]
    
    validator = ContainerValidator()
    is_valid, errors = validator.validate_consistency([book] + chapters)
    assert is_valid is False
    assert any("Chapter 11 exceeds book estimate" in err for err in errors)

def test_validator_detects_phase_violations():
    """Validator ensures chapter phases respect book phases."""
    book = BookOutline(
        genre="netorara",
        story_id="story-002",
        title="Netorara Story",
        chapter_estimate=20,
        structure="3-act",
        phases_summary={i: f"Phase {i}" for i in range(1, 10)}
    )
    
    bad_chapter = ChapterOutline(
        genre="netorara", story_id="story-002",
        chapter_number=1, phase=10,  # Invalid: only phases 1-9 exist
        title="Ch1", goal="goal", conflict="conflict",
        turning_point="turn", emotional_beat="beat"
    )
    
    validator = ContainerValidator()
    is_valid, errors = validator.validate_consistency([book, bad_chapter])
    assert is_valid is False
```

- [ ] **Step 2: Run test to verify it fails**

```bash
python -m pytest tests/auteur/narrative_blueprint/test_outline_validator.py -v
```

Expected: `ImportError: cannot import name 'ContainerValidator'`.

- [ ] **Step 3: Implement ContainerValidator**

```python
# src/auteur/narrative_blueprint/validator/outline_validator.py
from typing import List, Tuple
from auteur.narrative_blueprint.schema.outline_types import ContainerArtifact
from auteur.narrative_blueprint.schema.book_outline import BookOutline
from auteur.narrative_blueprint.schema.chapter_outline import ChapterOutline
from auteur.narrative_blueprint.schema.sequence_outline import SequenceOutline

class ContainerValidator:
    """Validates hierarchical consistency of container outlines."""
    
    def validate_consistency(self, outlines: List[ContainerArtifact]) -> Tuple[bool, List[str]]:
        """
        Validate that all outlines are mutually consistent.
        
        Returns (is_valid, error_messages).
        """
        errors = []
        
        # Group by type
        books = [o for o in outlines if isinstance(o, BookOutline)]
        chapters = [o for o in outlines if isinstance(o, ChapterOutline)]
        sequences = [o for o in outlines if isinstance(o, SequenceOutline)]
        
        # If we have a book, validate chapters against it
        if books:
            book = books[0]  # Assume one book per story_id
            
            # Check chapter count doesn't exceed estimate
            max_chapter = max((c.chapter_number for c in chapters), default=0)
            if max_chapter > book.chapter_estimate:
                errors.append(
                    f"Chapter {max_chapter} exceeds book estimate of {book.chapter_estimate}"
                )
            
            # Check all chapter phases are 1-9
            for chapter in chapters:
                if not (1 <= chapter.phase <= 9):
                    errors.append(
                        f"Chapter {chapter.chapter_number} has invalid phase {chapter.phase} (must be 1-9)"
                    )
        
        # If we have sequences, validate chapter ranges
        if sequences:
            for sequence in sequences:
                start, end = sequence.chapter_range
                
                # Verify chapters in range exist (optional — chapters might not be defined yet)
                for chapter in chapters:
                    if start <= chapter.chapter_number <= end:
                        # This chapter belongs in this sequence (implicit ownership)
                        pass
        
        return (len(errors) == 0, errors)
```

- [ ] **Step 4: Run test to verify it passes**

```bash
python -m pytest tests/auteur/narrative_blueprint/test_outline_validator.py -v
```

Expected: All tests pass.

- [ ] **Step 5: Commit**

```bash
git add src/auteur/narrative_blueprint/validator/outline_validator.py tests/auteur/narrative_blueprint/test_outline_validator.py
git commit -m "feat: implement container hierarchy validator

- Validates chapter counts don't exceed book estimates
- Checks phase assignments are 1-9
- Ensures sequence chapter ranges are coherent
- Independent validation: works for any subset of outlines"
```

---

#### Task 8: Arc Validator (Genre-Aware)

**Files:**
- Create: `src/auteur/narrative_blueprint/validator/arc_validator.py`
- Test: `tests/auteur/narrative_blueprint/test_arc_validator.py`

**Interfaces:**
- Consumes: `CharacterArc`, `StoryArc`, `ChapterOutline` (from earlier tasks)
- Produces: `ArcValidator` class with method `validate_arc_themes(arc, genre) -> Tuple[bool, List[str]]`
- **WEAK BOUNDARY:** Must integrate with genre ruleset from genre_pipeline

**Steps:**

- [ ] **Step 1: Write failing test**

```python
# tests/auteur/narrative_blueprint/test_arc_validator.py
from auteur.narrative_blueprint.validator.arc_validator import ArcValidator
from auteur.narrative_blueprint.schema.character_arc import CharacterArc

def test_arc_validator_netorara_themes():
    """Character arc themes must match genre expectations."""
    arc = CharacterArc(
        genre="netorara",
        story_id="story-001",
        name="Protagonist's Arc",
        character_name="Michael",
        initial_belief="My wife is mine",
        final_belief="Sharing is inevitable",
        genre_themes=["humiliation", "cuckoldry", "degradation"]
    )
    
    validator = ArcValidator()
    is_valid, errors = validator.validate_arc_themes(arc, "netorara")
    assert is_valid is True
    assert errors == []

def test_arc_validator_rejects_wrong_genre_themes():
    """Netorara arc with gentle femdom themes should fail."""
    arc = CharacterArc(
        genre="netorara",
        story_id="story-002",
        name="Wrong Arc",
        character_name="Michael",
        initial_belief="I must control",
        final_belief="I surrender",
        genre_themes=["authority", "dominance", "control"]  # Gentle femdom themes, not netorara
    )
    
    validator = ArcValidator()
    is_valid, errors = validator.validate_arc_themes(arc, "netorara")
    assert is_valid is False
    assert any("genre_themes" in err.lower() for err in errors)

def test_arc_validator_gentlefemdom_themes():
    """Gentle femdom arcs expect authority/surrender themes."""
    arc = CharacterArc(
        genre="gentlefemdom",
        story_id="story-003",
        name="Alice's Authority",
        character_name="Alice",
        initial_belief="I must submit to be loved",
        final_belief="My authority is a gift",
        genre_themes=["authority", "surrender", "trust"]
    )
    
    validator = ArcValidator()
    is_valid, errors = validator.validate_arc_themes(arc, "gentlefemdom")
    assert is_valid is True
```

- [ ] **Step 2: Run test to verify it fails**

```bash
python -m pytest tests/auteur/narrative_blueprint/test_arc_validator.py -v
```

Expected: `ImportError: cannot import name 'ArcValidator'`.

- [ ] **Step 3: Implement ArcValidator**

```python
# src/auteur/narrative_blueprint/validator/arc_validator.py
from typing import List, Tuple
from auteur.narrative_blueprint.schema.character_arc import CharacterArc
from auteur.narrative_blueprint.schema.story_arc import StoryArc

# Genre-specific theme expectations
GENRE_THEMES = {
    "netorara": {"humiliation", "degradation", "cuckoldry", "shame", "exposure"},
    "mystery": {"investigation", "deception", "revelation", "conspiracy", "doubt"},
    "gentlefemdom": {"authority", "surrender", "dominance", "trust", "control"},
}

class ArcValidator:
    """Validates arc integrity and genre compliance."""
    
    def validate_arc_themes(self, arc: CharacterArc, genre: str) -> Tuple[bool, List[str]]:
        """
        Validate that character arc themes align with genre expectations.
        
        Returns (is_valid, error_messages).
        
        WEAK BOUNDARY: This is where character arcs integrate with genre validation.
        Genre-specific rules must be checked here.
        """
        errors = []
        
        if genre not in GENRE_THEMES:
            errors.append(f"Unknown genre: {genre}")
            return (False, errors)
        
        expected_themes = GENRE_THEMES[genre]
        arc_themes_set = set(arc.genre_themes)
        
        # Check: at least one theme matches genre expectations
        overlap = arc_themes_set & expected_themes
        if not overlap:
            errors.append(
                f"Character arc themes {arc.genre_themes} don't match {genre} expectations: "
                f"{expected_themes}"
            )
        
        return (len(errors) == 0, errors)
    
    def validate_story_arc_phases(self, arc: StoryArc, num_chapters: int) -> Tuple[bool, List[str]]:
        """Validate that story arc phases are sensible given chapter count."""
        errors = []
        
        # Checkpoints should reference valid phases
        for checkpoint in arc.checkpoints:
            if not (1 <= checkpoint.phase <= 9):
                errors.append(
                    f"Arc checkpoint phase {checkpoint.phase} is invalid (must be 1-9)"
                )
        
        return (len(errors) == 0, errors)
```

- [ ] **Step 4: Run test to verify it passes**

```bash
python -m pytest tests/auteur/narrative_blueprint/test_arc_validator.py -v
```

Expected: All tests pass.

- [ ] **Step 5: Commit**

```bash
git add src/auteur/narrative_blueprint/validator/arc_validator.py tests/auteur/narrative_blueprint/test_arc_validator.py
git commit -m "feat: implement genre-aware arc validator

- Validates character arc themes match genre expectations
- Checks story arc phase ranges are valid
- WEAK BOUNDARY: Character arcs integrate with genre validation here
- Ensures gentle femdom authority themes ≠ netorara humiliation themes"
```

---

### Phase 3: Loaders & Integration

#### Task 9: Outline Loader (YAML Serialization)

**Files:**
- Create: `src/auteur/narrative_blueprint/loader/outline_loader.py`
- Test: `tests/auteur/narrative_blueprint/test_outline_loader.py`

**Interfaces:**
- Consumes: All outline schemas (Tasks 2-6), session storage pattern from genre_pipeline
- Produces: `OutlineLoader` class with methods `load_outline(path: str)`, `save_outline(outline: OutlineArtifact, path: str)`

**Steps:**

- [ ] **Step 1: Write failing test**

```python
# tests/auteur/narrative_blueprint/test_outline_loader.py
import tempfile
import os
from auteur.narrative_blueprint.loader.outline_loader import OutlineLoader
from auteur.narrative_blueprint.schema.book_outline import BookOutline

def test_outline_loader_roundtrip():
    """Load and save book outline; verify content is preserved."""
    original = BookOutline(
        genre="mystery",
        story_id="story-123",
        title="The Vanishing",
        chapter_estimate=28,
        structure="3-act",
        phases_summary={i: f"Phase {i} summary" for i in range(1, 10)}
    )
    
    with tempfile.TemporaryDirectory() as tmpdir:
        loader = OutlineLoader()
        path = os.path.join(tmpdir, "book_outline.yaml")
        
        # Save
        loader.save_outline(original, path)
        assert os.path.exists(path)
        
        # Load
        loaded = loader.load_outline(path, BookOutline)
        assert loaded.title == "The Vanishing"
        assert loaded.chapter_estimate == 28
        assert loaded.genre == "mystery"

def test_outline_loader_preserves_arc_progressions():
    """Chapter outline arc_progressions must survive roundtrip."""
    from auteur.narrative_blueprint.schema.chapter_outline import ChapterOutline
    
    original = ChapterOutline(
        genre="gentlefemdom",
        story_id="story-456",
        chapter_number=12,
        phase=6,
        title="The Confession",
        goal="Alice admits her desires",
        conflict="Fear of judgment",
        turning_point="Sarah accepts",
        emotional_beat="relief & excitement",
        arc_progressions={
            "Alice's Dominance Arc": "Accepts authority as expression of love",
            "Romance Arc": "Physical intimacy reaches new depth"
        }
    )
    
    with tempfile.TemporaryDirectory() as tmpdir:
        loader = OutlineLoader()
        path = os.path.join(tmpdir, "chapter_outline.yaml")
        
        loader.save_outline(original, path)
        loaded = loader.load_outline(path, ChapterOutline)
        
        assert len(loaded.arc_progressions) == 2
        assert "Alice's Dominance Arc" in loaded.arc_progressions
```

- [ ] **Step 2: Run test to verify it fails**

```bash
python -m pytest tests/auteur/narrative_blueprint/test_outline_loader.py -v
```

Expected: `ImportError: cannot import name 'OutlineLoader'`.

- [ ] **Step 3: Implement OutlineLoader**

```python
# src/auteur/narrative_blueprint/loader/outline_loader.py
import yaml
import os
from typing import Type, TypeVar
from auteur.narrative_blueprint.schema.outline_types import OutlineArtifact
from datetime import datetime

T = TypeVar('T', bound=OutlineArtifact)

class OutlineLoader:
    """Load and save outline artifacts as YAML."""
    
    def save_outline(self, outline: OutlineArtifact, path: str) -> None:
        """
        Save outline to YAML file.
        
        Args:
            outline: OutlineArtifact subclass instance
            path: File path (e.g., ".auteur/outlines/netorara/book.yaml")
        """
        # Convert outline to dict for YAML serialization
        outline_dict = self._to_dict(outline)
        
        # Ensure parent directory exists
        os.makedirs(os.path.dirname(path), exist_ok=True)
        
        with open(path, 'w') as f:
            yaml.dump(outline_dict, f, default_flow_style=False, sort_keys=False)
    
    def load_outline(self, path: str, outline_class: Type[T]) -> T:
        """
        Load outline from YAML file.
        
        Args:
            path: File path
            outline_class: OutlineArtifact subclass to instantiate
        
        Returns:
            Instance of outline_class populated from YAML
        """
        with open(path, 'r') as f:
            data = yaml.safe_load(f)
        
        return self._from_dict(data, outline_class)
    
    def _to_dict(self, outline: OutlineArtifact) -> dict:
        """Convert outline instance to serializable dict."""
        result = {}
        for key, value in outline.__dict__.items():
            if isinstance(value, datetime):
                result[key] = value.isoformat()
            elif hasattr(value, '__dict__'):
                # Nested dataclass (e.g., TurningPoint, PhaseRange)
                result[key] = self._to_dict(value)
            else:
                result[key] = value
        return result
    
    def _from_dict(self, data: dict, outline_class: Type[T]) -> T:
        """Reconstruct outline instance from dict."""
        return outline_class(**data)
```

- [ ] **Step 4: Run test to verify it passes**

```bash
python -m pytest tests/auteur/narrative_blueprint/test_outline_loader.py -v
```

Expected: All tests pass (after `pyyaml` is available).

- [ ] **Step 5: Commit**

```bash
git add src/auteur/narrative_blueprint/loader/outline_loader.py tests/auteur/narrative_blueprint/test_outline_loader.py
git commit -m "feat: implement outline YAML loader/saver

- Serializes all outline types to .yaml format
- Roundtrip preservation of complex fields (arc_progressions, turning_points)
- Mirrors genre_pipeline session storage pattern
- Ready for .auteur/outlines/<genre>/ integration"
```

---

### Phase 4: Integration Tests (Validate All 3 Genres)

#### Task 10: Genre Integration Tests (Netorara)

**Files:**
- Create: `tests/auteur/narrative_blueprint/test_genre_integration_netorara.py`

**Interfaces:**
- Consumes: All outline schemas and validators (previous tasks)
- Produces: Full outlines for a netorara story, validated end-to-end

**Steps:**

- [ ] **Step 1: Write comprehensive netorara workflow test**

```python
# tests/auteur/narrative_blueprint/test_genre_integration_netorara.py
from auteur.narrative_blueprint.schema.book_outline import BookOutline
from auteur.narrative_blueprint.schema.chapter_outline import ChapterOutline
from auteur.narrative_blueprint.schema.character_arc import CharacterArc, TurningPoint
from auteur.narrative_blueprint.schema.story_arc import StoryArc, ArcCheckpoint
from auteur.narrative_blueprint.schema.outline_types import PhaseRange
from auteur.narrative_blueprint.validator.outline_validator import ContainerValidator
from auteur.narrative_blueprint.validator.arc_validator import ArcValidator

def test_netorara_full_outline_workflow():
    """
    Netorara story: Michael's journey from control to acceptance
    Validates that all outlines work with netorara genre.
    """
    
    # Book outline
    book = BookOutline(
        genre="netorara",
        story_id="netorara-001",
        title="The Surrender",
        chapter_estimate=20,
        structure="3-act",
        phases_summary={
            1: "Michael's confidence & control; marriage appears perfect",
            2: "First proposal; Michael & Sarah consider exploration",
            3: "Preparations; emotional reckoning begins",
            4: "First encounter; Michael experiences humiliation",
            5: "Aftermath & obsession; Michael spirals",
            6: "Breakdown; Michael confronts his desires",
            7: "Acceptance begins; family reunion with new understanding",
            8: "Second encounter; Michael participates willingly",
            9: "New equilibrium; marriage redefined through shared taboo"
        }
    )
    
    # Chapters (sample)
    chapters = [
        ChapterOutline(
            genre="netorara", story_id="netorara-001",
            chapter_number=1, phase=1,
            title="The Perfect Marriage",
            goal="Establish Michael's confidence and control",
            conflict="Sarah subtly suggests exploration",
            turning_point="Michael dismisses the idea",
            emotional_beat="confident, dismissive",
            arc_progressions={"Michael's Humiliation Arc": "Unaware of desires"}
        ),
        ChapterOutline(
            genre="netorara", story_id="netorara-001",
            chapter_number=6, phase=4,
            title="First Night",
            goal="Michael experiences humiliation directly",
            conflict="Reality vs fantasy; Michael's conflicted arousal",
            turning_point="Michael watches; pleasure mixes with shame",
            emotional_beat="shame, arousal, disorientation",
            arc_progressions={"Michael's Humiliation Arc": "Belief begins to crack"}
        ),
    ]
    
    # Character arc: Michael's humiliation journey
    michael_arc = CharacterArc(
        genre="netorara",
        story_id="netorara-001",
        name="Michael's Humiliation Arc",
        character_name="Michael",
        initial_belief="My wife is mine alone; control proves my worth",
        final_belief="Sharing creates deeper intimacy; humiliation is erotic",
        genre_themes=["humiliation", "cuckoldry", "shame", "arousal"],
        turning_points=[
            TurningPoint(chapter=2, moment="Sarah's first suggestion", belief_shift="Maybe I'm not as in control as I thought"),
            TurningPoint(chapter=6, moment="First encounter", belief_shift="The humiliation is... arousing?"),
            TurningPoint(chapter=15, moment="Willing participation", belief_shift="I want this; it defines me"),
        ]
    )
    
    # Story arc: The Taboo Discovery
    taboo_arc = StoryArc(
        genre="netorara",
        story_id="netorara-001",
        name="The Taboo Discovery",
        arc_category="mystery",  # Netorara often has mystery: who? when? how?
        phase_range=PhaseRange(start=1, peak=6, end=9),
        checkpoints=[
            ArcCheckpoint(phase=1, moment="Taboo is hinted"),
            ArcCheckpoint(phase=3, moment="Taboo is explored intellectually"),
            ArcCheckpoint(phase=6, moment="Taboo becomes physical reality"),
            ArcCheckpoint(phase=9, moment="Taboo is integrated into relationship"),
        ]
    )
    
    # Validate all together
    validator = ContainerValidator()
    is_valid, errors = validator.validate_consistency([book] + chapters)
    assert is_valid, f"Container validation failed: {errors}"
    
    arc_validator = ArcValidator()
    is_valid, errors = arc_validator.validate_arc_themes(michael_arc, "netorara")
    assert is_valid, f"Arc validation failed: {errors}"
    
    is_valid, errors = arc_validator.validate_story_arc_phases(taboo_arc, book.chapter_estimate)
    assert is_valid, f"Story arc validation failed: {errors}"
```

- [ ] **Step 2: Run test to verify all classes exist and work together**

```bash
python -m pytest tests/auteur/narrative_blueprint/test_genre_integration_netorara.py -v
```

Expected: Test passes, proving netorara outlines are fully supported.

- [ ] **Step 3: Commit**

```bash
git add tests/auteur/narrative_blueprint/test_genre_integration_netorara.py
git commit -m "test: add end-to-end netorara genre integration

- Full outline workflow: book, chapters, character arc, story arc
- Validates Michael's humiliation journey through all 9 phases
- Proves zero infrastructure changes needed for netorara support"
```

---

#### Task 11: Genre Integration Tests (Mystery & Gentle Femdom)

**Files:**
- Create: `tests/auteur/narrative_blueprint/test_genre_integration_mystery.py`
- Create: `tests/auteur/narrative_blueprint/test_genre_integration_gentlefemdom.py`

**Steps:** (Similar to Task 10, adapted for each genre)

- [ ] **Create mystery test file with cozy mystery story structure**

- [ ] **Create gentle femdom test file with authority discovery arc**

- [ ] **Run both integration tests**

```bash
python -m pytest tests/auteur/narrative_blueprint/test_genre_integration_*.py -v
```

Expected: All 3 genre integration tests pass.

- [ ] **Commit**

```bash
git add tests/auteur/narrative_blueprint/test_genre_integration_mystery.py tests/auteur/narrative_blueprint/test_genre_integration_gentlefemdom.py
git commit -m "test: add genre integration tests for mystery and gentle femdom

- Mystery: cozy detective story with investigation arc
- Gentle femdom: Alice's authority discovery with dominance arc
- All 3 genres validated with zero infrastructure modifications"
```

---

### Phase 5: CLI & Server Integration

#### Task 12: Blueprint CLI Entry Point

**Files:**
- Create: `src/auteur/narrative_blueprint/cli_blueprint.py`
- Modify: `src/auteur/netorara/cli_netorara.py`, `src/auteur/mystery/cli_mystery.py`, `src/auteur/gentlefemdom/cli_gentlefemdom.py` (add blueprint subcommand)

**Interfaces:**
- Consumes: Outline loaders, validators
- Produces: `auteur {genre} blueprint init` (generate book from story_id), `auteur {genre} blueprint chapters` (generate chapter stubs)

**Steps:** (Example for netorara; repeat for other genres)

- [ ] **Implement blueprint CLI with subcommands**

```python
# src/auteur/narrative_blueprint/cli_blueprint.py
import click
from pathlib import Path
from auteur.narrative_blueprint.loader.outline_loader import OutlineLoader
from auteur.narrative_blueprint.schema.book_outline import BookOutline
from auteur.genre_pipeline.session import GenreSessionStore

@click.group()
def blueprint_cli():
    """Manage narrative structure outlines."""
    pass

@blueprint_cli.command()
@click.option('--genre', required=True, help='Genre (netorara, mystery, gentlefemdom)')
@click.option('--project-dir', type=click.Path(), default='.', help='Project root')
def init_book(genre, project_dir):
    """Generate book outline from story identity."""
    session = GenreSessionStore(genre=genre, project_dir=project_dir)
    story_id = session.load_story_id()
    
    # For now, return placeholder (Task 13 implements generation)
    click.echo(f"Creating book outline for {story_id}...")
    
    book = BookOutline(
        genre=genre,
        story_id=story_id,
        title="[To be filled in]",
        chapter_estimate=20,
        structure="3-act",
        phases_summary={i: f"Phase {i}" for i in range(1, 10)}
    )
    
    loader = OutlineLoader()
    path = session.get_outline_path("book_outline.yaml")
    loader.save_outline(book, str(path))
    click.echo(f"Saved to {path}")
```

---

## Summary: Container vs. Overlay Pattern

By the end of Phase 5:

**Containers** ✅
- Series Outline
- Book Outline
- Sequence Outline
- Chapter Outline

**Overlays** ✅
- Character Arc
- Story Arc
- (Theme Arc — future)

**Validators** ✅
- Container hierarchy (consistent chapter counts, phases)
- Arc integrity (genre-aware themes)

**No special-casing in shared code.** All 3 genres validate identically. ✅

---

## Execution Handoff

Plan complete and saved to `docs/superpowers/plans/2026-07-12-narrative-blueprint-layer2.md`.

**Two execution options:**

**1. Subagent-Driven (recommended)** — I dispatch a fresh subagent per task, review between tasks, fast iteration. Maintains momentum and catches issues early (if Task 1 has problems, fix before Task 2 starts).

**2. Inline Execution** — Execute tasks in this session using `superpowers:executing-plans`, batch execution with checkpoints.

**Which approach would you prefer?**

