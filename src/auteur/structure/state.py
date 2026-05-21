"""Story State Commands — CLI business logic and unified dual validation."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field

from auteur.bible import StoryBible
from auteur.blueprint import StoryBlueprint
from auteur.structure.analyzer import run_all_diagnostics
from auteur.structure.diagnostics import DiagnosticLayer, DiagnosticSeverity


# ---------------------------------------------------------------------------
# Strict StoryBible Pydantic Validation Schema
# ---------------------------------------------------------------------------

class CharacterState(BaseModel):
    location: str | None = None
    physical: str | None = None
    emotional: str | None = None
    inventory: list[str] = Field(default_factory=list)
    relationships: dict[str, str] = Field(default_factory=dict)
    secrets_known: list[str] = Field(default_factory=list)
    current_arc_pct: float | int = 0


class LocationState(BaseModel):
    description: str | None = None
    occupants: list[str] = Field(default_factory=list)
    mood: str | None = None


class ItemState(BaseModel):
    holder: str | None = None
    properties: dict[str, Any] = Field(default_factory=dict)


class FactionState(BaseModel):
    members: list[str] = Field(default_factory=list)
    relationships: dict[str, str] = Field(default_factory=dict)
    plans: list[str] = Field(default_factory=list)


class EventState(BaseModel):
    chapter_index: int
    summary: str
    deltas: dict[str, Any] = Field(default_factory=dict)


class StoryBibleModel(BaseModel):
    characters: dict[str, CharacterState] = Field(default_factory=dict)
    locations: dict[str, LocationState] = Field(default_factory=dict)
    items: dict[str, ItemState] = Field(default_factory=dict)
    factions: dict[str, FactionState] = Field(default_factory=dict)
    events: list[EventState] = Field(default_factory=list)
    realized_tension: list[int | None] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Deep Reflection Mutator Helpers
# ---------------------------------------------------------------------------

def get_deep_attribute(obj: Any, path: str) -> tuple[Any, Any, str | int]:
    """Traverse a dotted path and return (parent, value, key/index)."""
    parts: list[str | int] = []
    for part in path.split("."):
        if "[" in part and part.endswith("]"):
            name, idx_str = part[:-1].split("[", 1)
            parts.append(name)
            parts.append(int(idx_str))
        else:
            parts.append(part)

    curr = obj
    parent = None
    last_key = None

    for part in parts:
        parent = curr
        last_key = part
        if isinstance(curr, dict):
            curr = curr[part]
        elif isinstance(curr, list):
            curr = curr[int(part)]
        elif hasattr(curr, str(part)):
            curr = getattr(curr, str(part))
        else:
            raise AttributeError(f"Path part '{part}' not found on {type(curr)}")

    return parent, curr, last_key


def set_deep_attribute(obj: Any, path: str, value: Any) -> None:
    """Set a nested value inside a Pydantic model or dictionary in place."""
    parent, _, last_key = get_deep_attribute(obj, path)
    if isinstance(parent, dict):
        parent[last_key] = value
    elif isinstance(parent, list):
        parent[int(last_key)] = value
    else:
        setattr(parent, str(last_key), value)


def parse_value(val_str: str) -> Any:
    """Parse string input dynamically into JSON types (booleans, numbers, arrays, strings)."""
    try:
        return json.loads(val_str)
    except json.JSONDecodeError:
        return val_str


# ---------------------------------------------------------------------------
# Programmatic state Commands Logic
# ---------------------------------------------------------------------------

def state_check(project_path: Path, *, outline: dict | None = None) -> int:
    """Run Structure Diagnostic and Bible Audit in one pass.

    Runs:
    - Layers 1-5 (Structure Diagnostic): within-blueprint coherence
    - Layer 6 (Bible Audit): carrier-state lore drift across chapter events
    - Layer 7 (Scene Representation): outline.yaml vs Bible carrier consistency
      (only when ``outline`` is provided; emits a WARNING when None)

    Args:
        project_path: Root path of the Auteur project.
        outline: Optional parsed outline dict (from load_outline). When None,
            a Layer 7 WARNING is emitted noting Scene Representation was skipped.

    Returns:
        Exit code: 0 (clean), 4 (errors found).
    """
    blueprint_path = project_path / "blueprint.yaml"
    bible_path = project_path / "bible.json"

    if not blueprint_path.exists():
        print(f"Error: blueprint.yaml not found at {blueprint_path}", file=sys.stderr)
        return 1
    if not bible_path.exists():
        print(f"Error: bible.json not found at {bible_path}", file=sys.stderr)
        return 1

    try:
        blueprint = StoryBlueprint.from_yaml(blueprint_path)
        bible = StoryBible(bible_path)
    except Exception as exc:
        print(f"Error loading project: {exc}", file=sys.stderr)
        return 1

    from auteur.structure.proposal_resolution import load_resolved_rules
    resolved_rules = load_resolved_rules(project_path)

    raw_diagnostics = run_all_diagnostics(blueprint, bible, outline=outline)
    diagnostics = [d for d in raw_diagnostics if d.rule not in resolved_rules]

    if not raw_diagnostics:
        print("No structural or lore issues detected.")
        return 0

    if not diagnostics:
        print("All previously detected issues have been resolved.")
        return 0

    from collections import defaultdict
    _LAYER_ORDER = [
        (1, DiagnosticLayer.TARGET_EXPERIENCE, "Target Experience"),
        (2, DiagnosticLayer.CONSTRAINTS, "Promise / Constraints"),
        (3, DiagnosticLayer.SCOPE, "Scope / Container"),
        (4, DiagnosticLayer.STRUCTURAL_FORCES, "Structural Forces"),
        (5, DiagnosticLayer.THREADS, "Threads / Modules"),
        (6, DiagnosticLayer.CARRIERS, "Carriers"),
        (7, DiagnosticLayer.REPRESENTATION, "Representation (Scene Outline)"),
        (8, DiagnosticLayer.MODULATION, "Modulation"),
        (9, DiagnosticLayer.THEME, "Theme / Resonance"),
    ]
    groups = defaultdict(list)
    for d in diagnostics:
        groups[d.layer].append(d)

    print("╔═══ Story State Report ═══════════════════════════════════╗")
    print(f"║ Project: {project_path.name:<48} ║")
    print("╚══════════════════════════════════════════════════════════╝\n")

    for num, layer, name in _LAYER_ORDER:
        items = groups[layer]
        if not items:
            continue
        label = "finding" if len(items) == 1 else "findings"
        print(f"Layer {num} — {name} ({len(items)} {label})")
        for d in items:
            severity_label = d.severity.value.upper()
            print(f"  {severity_label}: {d.message}")
            if d.evidence:
                print("    Evidence:")
                for line in d.evidence:
                    print(f"      - {line}")
        print()

    errors = sum(1 for d in diagnostics if d.severity == DiagnosticSeverity.ERROR)
    warnings = sum(1 for d in diagnostics if d.severity == DiagnosticSeverity.WARNING)
    print(f"{len(diagnostics)} findings total ({errors} error(s), {warnings} warning(s)).")

    return 4 if errors > 0 else 0


def state_update(project_path: Path, file_path: Path, key: str, val_str: str) -> int:
    """Safe, transactional updates of project files backed by schema validation."""
    if not file_path.exists():
        resolved_path = project_path / file_path
        if not resolved_path.exists():
            print(f"Error: Target file not found: {file_path}", file=sys.stderr)
            return 1
        file_path = resolved_path

    val = parse_value(val_str)

    if file_path.suffix in {".yaml", ".yml"}:
        try:
            blueprint = StoryBlueprint.from_yaml(file_path)
        except Exception as exc:
            print(f"Error loading blueprint: {exc}", file=sys.stderr)
            return 1

        try:
            set_deep_attribute(blueprint, key, val)
            validated = StoryBlueprint.model_validate(blueprint.model_dump())
        except Exception as exc:
            print(f"Error: Schema validation failed. Transaction rolled back.\nDetails: {exc}", file=sys.stderr)
            return 1

        try:
            file_path.write_text(
                yaml.safe_dump(validated.model_dump(mode="json"), sort_keys=False),
                encoding="utf-8",
            )
            print(f"Success: Updated '{key}' in blueprint.")
            return 0
        except Exception as exc:
            print(f"Error writing to file: {exc}", file=sys.stderr)
            return 1

    elif file_path.suffix == ".json":
        try:
            bible = StoryBible(file_path)
        except Exception as exc:
            print(f"Error loading bible: {exc}", file=sys.stderr)
            return 1

        original_data = json.loads(json.dumps(bible.data))
        try:
            set_deep_attribute(bible.data, key, val)
            StoryBibleModel.model_validate(bible.data)
        except Exception as exc:
            print(f"Error: Schema validation failed. Transaction rolled back.\nDetails: {exc}", file=sys.stderr)
            bible.data = original_data
            return 1

        try:
            bible.save()
            print(f"Success: Updated '{key}' in bible.")
            return 0
        except Exception as exc:
            print(f"Error writing to file: {exc}", file=sys.stderr)
            return 1

    else:
        print(f"Error: Unsupported file format {file_path.suffix}", file=sys.stderr)
        return 1


def state_prepare(project_path: Path, phase: str, scope: str, out_path: Path | None, chapter_idx: int | None) -> int:
    """Compile context packets formatted according to strict handoff skeletons."""
    blueprint_path = project_path / "blueprint.yaml"
    bible_path = project_path / "bible.json"

    if not blueprint_path.exists() or not bible_path.exists():
        print("Error: Missing blueprint.yaml or bible.json in project.", file=sys.stderr)
        return 1

    try:
        blueprint = StoryBlueprint.from_yaml(blueprint_path)
        bible = StoryBible(bible_path)
    except Exception as exc:
        print(f"Error loading project: {exc}", file=sys.stderr)
        return 1

    chapter_str = f"Chapter {chapter_idx}" if chapter_idx else "Chapter [Index]"
    pov_char = "[Name]"
    active_characters = []
    want = ""
    resistance = ""
    conflict = ""
    stakes = ""

    # Load chapter outline if available
    outline = None
    if chapter_idx is not None:
        outline_path = project_path / "chapters" / f"{chapter_idx:02d}" / "outline.yaml"
        if outline_path.exists():
            try:
                outline = yaml.safe_load(outline_path.read_text(encoding="utf-8"))
            except Exception:
                pass

    if chapter_idx is not None:
        if blueprint.story_engine is not None:
            want = blueprint.story_engine.main_thread.want.author_text
            resistance = blueprint.story_engine.main_thread.resistance.author_text
            conflict = blueprint.story_engine.main_thread.conflict.author_text
            stakes = blueprint.story_engine.main_thread.stakes.author_text

        chars = bible.data.get("characters", {})
        for name, info in chars.items():
            if info.get("location") == f"chapter_{chapter_idx}":
                active_characters.append(f"{name} ({info.get('physical', 'stable')}, {info.get('emotional', 'stable')})")
        if not active_characters:
            active_characters = ["[None recorded at this location]"]

    if phase == "drafting":
        target_scene_function = "[Generate chapter outline using Cartographer]"
        target_intensity_curve = "[Peak intensity: 7/10 at mid-scene]"
        scene_details = ""

        if outline:
            if outline.get("chapter_summary"):
                target_scene_function = outline["chapter_summary"]
            if outline.get("estimated_chapter_tension"):
                target_intensity_curve = f"Peak intensity: {outline['estimated_chapter_tension']}/10 at mid-scene"
            if outline.get("scenes") and isinstance(outline["scenes"], list):
                pov_char = outline["scenes"][0].get("pov_character") or pov_char
                scene_list_str = []
                for s in outline["scenes"]:
                    sid = s.get("scene_id", "?")
                    spov = s.get("pov_character", "?")
                    sloc = s.get("location", "?")
                    ssum = s.get("summary", "")
                    scene_list_str.append(f"  * Scene {sid} ({spov} @ {sloc}): {ssum}")
                scene_details = "\n" + "\n".join(scene_list_str)

        template = f"""# Phase Handoff: DRAFTING
* **Current Phase**: Drafting Handoff
* **Active Story Object**: {chapter_str}
* **Drafting Scope**: {scope.upper()}

## 1. Scene Specifications
* **Target Scene Function**: {target_scene_function}
* **Target Intensity Curve**: {target_intensity_curve}
* **Target POV Character**: {pov_char}
* **Word Count Target**: 3,000 words{scene_details}

## 2. Ingested 9-Layer Context
* **Emotional Tone (Layer 1)**: {blueprint.emotional_design.overall_emotional_arc if blueprint.emotional_design else 'Bittersweet'}
* **Structural Forces (Layer 4)**:
  * **Want**: {want or '[Protagonist Goal]'}
  * **Resistance**: {resistance or '[Obstacles/Forces]'}
  * **Conflict**: {conflict or '[The Climax]'}
  * **Stakes**: {stakes or '[What is at risk]'}
* **Thread Focus (Layer 5)**: Main Thread - 100%
* **Carrier Reference (Layer 6)**:
  * **Characters Present**: {", ".join(active_characters) if active_characters else '[Protagonist]'}
  * **Setting Details**: [Location settings and rules]

## 3. Downstream Constraints & Foreshadowing
* **Downstream Constraints**: [Keep consistency with previous events]
* **Foreshadowing Requirements**: [Plant elements for future acts]
"""
    elif phase == "revision":
        intended_scene_function = "[Intended drafting goal]"
        intensity_val = "7/10"
        facts_established = []
        canon_deltas = []

        if outline:
            if outline.get("chapter_summary"):
                intended_scene_function = outline["chapter_summary"]
            if outline.get("estimated_chapter_tension"):
                intensity_val = f"{outline['estimated_chapter_tension']}/10"
            if outline.get("scenes") and isinstance(outline["scenes"], list):
                pov_char = outline["scenes"][0].get("pov_character") or pov_char
                for s in outline["scenes"]:
                    for event in s.get("key_events", []) or []:
                        facts_established.append(f"  * {event}")

            from auteur.pipeline.extraction import extract_character_state_changes
            state_changes = extract_character_state_changes(outline)
            for change in state_changes:
                char = change.get("character", "?")
                field = change.get("field", "?")
                before = change.get("before")
                after = change.get("after")
                canon_deltas.append(f"  * {char}: {field} = {before or 'None'} -> {after or 'None'}")

        if not facts_established:
            facts_established = ["  * [Fact 1]"]
        if not canon_deltas:
            canon_deltas = [f"  * {pov_char}: stable -> [Realized state change]"]

        facts_str = "\n".join(facts_established)
        deltas_str = "\n".join(canon_deltas)

        template = f"""# Phase Handoff: REVISION
* **Current Phase**: Revision Handoff
* **Active Story Object**: {chapter_str}
* **Scope**: {scope.upper()}
  * *Rationale*: Compiling realized facts and character updates from the drafted chapter.

## 1. Intended vs Realized Analysis
* **Intended Scene Function**: {intended_scene_function}
* **Realized Scene Function**: [Review draft text against outline]
* **Intensity Deviation**: [No deviation reported, Target: {intensity_val}]

## 2. Canon Delta Log (Layer 6 Changes)
* **New Facts Established**:
{facts_str}
* **Character State Transitions**:
{deltas_str}

## 3. Legacy Drift & Issues Detected
* **Contradictions Found**: [Identify any conflicts with blueprint or previous chapters]
* **Stray Threads**: [Details]
"""
    elif phase == "recovery":
        template = f"""# Phase Handoff: RECOVERY
* **Current Phase**: Bridge Recovery
* **Active Story Object**: Raw draft fragments
* **Scope**: {scope.upper()}
  * *Rationale*: Reverse-engineering full narrative skeleton from unfinished prose fragments.

## 1. Recovery Metadata & Confidence Matrix
| Layer | Name | Confidence | Candidate Locked State | Speculative / Sandbox |
| :--- | :--- | :--- | :--- | :--- |
| **Layer 1** | Target Experience | Med | {blueprint.identity.target_experience.primary if blueprint.identity.target_experience else 'Bittersweet'} | [Speculative ideas] |
| **Layer 2** | Promise/Constraints| High | {blueprint.identity.genre.value} | [Speculative ideas] |
| **Layer 3** | Scope / Container | Med | {blueprint.identity.length_class.value} | [Speculative ideas] |
| **Layer 4** | Structural Forces | Med | {want or 'Want/Resistance map'} | [Speculative ideas] |
| **Layer 5** | Threads / Modules | Med | [Main Plot Thread] | [Speculative ideas] |
| **Layer 6** | Carriers | Med | [Bible database characters] | [Speculative ideas] |
| **Layer 7** | Representation | Med | [Scene sequence outline] | [Speculative ideas] |
| **Layer 8** | Modulation | Med | [Tension waveform peaks] | [Speculative ideas] |
| **Layer 9** | Resonance/Coherence| Med | {blueprint.theme.thesis if blueprint.theme else 'Thematic question'} | [Speculative ideas] |

## 2. Legacy Drift & Contradiction Notes
* **Legacy Drift**: [Check for old character names or aborted subplot concepts]
* **Contradictions Found**: [Check if draft text conflicts with engine layers]

## 3. Candidate Locked Layers
* [List of layers proposed for immediate lock with rationales]

## 4. Recommended Next Workflow
* **Next Target Phase**: State Update
* **Author Confirmation Required**:
  * Question 1: Resolve Speculative Layer 7
  * Question 2: Approve Candidate Locked Layer 4
"""
    else:
        template = f"""# Phase Handoff: IDEATION
* **Current Phase**: Ideation Handoff
* **Active Story Object**: {chapter_str}
* **Scope**: {scope.upper()}

## Conceptual Design Map
* **Target Genre**: {blueprint.identity.genre.value}
* **Mandatory Ending Tone**: {blueprint.contract.mandatory_ending_tone.value}
* **Thematic Thesis**: {blueprint.theme.thesis if blueprint.theme else '[Thesis Statement]'}
"""

    if out_path:
        try:
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(template, encoding="utf-8")
            print(f"Success: Prepared handoff context saved to {out_path}.")
        except Exception as exc:
            print(f"Error saving handoff context: {exc}", file=sys.stderr)
            return 1
    else:
        print(template)

    return 0


def state_canon(project_path: Path, format: str) -> int:
    """Generate high-fidelity summary facts report of characters and setting lore."""
    bible_path = project_path / "bible.json"
    if not bible_path.exists():
        print(f"Error: bible.json not found at {bible_path}", file=sys.stderr)
        return 1

    try:
        bible = StoryBible(bible_path)
    except Exception as exc:
        print(f"Error loading bible: {exc}", file=sys.stderr)
        return 1

    if format == "json":
        print(json.dumps(bible.data, indent=2, ensure_ascii=False))
        return 0

    output = []
    output.append("# Canonical Reference Manual\n")

    output.append("## 👥 Character Registry")
    chars = bible.data.get("characters", {})
    if not chars:
        output.append("*No characters recorded in bible.*")
    else:
        for name, info in sorted(chars.items()):
            output.append(f"\n### {name}")
            output.append(f"* **Current Location**: {info.get('location', 'Unknown')}")
            output.append(f"* **Physical State**: {info.get('physical', 'Stable')}")
            output.append(f"* **Emotional State**: {info.get('emotional', 'Stable')}")
            if info.get("inventory"):
                output.append(f"* **Inventory**: {', '.join(info['inventory'])}")
            if info.get("relationships"):
                rels = [f"{k}: {v}" for k, v in info["relationships"].items()]
                output.append(f"* **Relationships**: {', '.join(rels)}")
            if info.get("secrets_known"):
                output.append(f"* **Secrets Known**: {', '.join(info['secrets_known'])}")
            output.append(f"* **Current Arc Progress**: {info.get('current_arc_pct', 0)}%")
    output.append("")

    output.append("## 📍 Settings & Factions")
    locs = bible.data.get("locations", {})
    if not locs:
        output.append("*No locations recorded in bible.*")
    else:
        for name, info in sorted(locs.items()):
            output.append(f"\n### Location: {name}")
            output.append(f"* **Description**: {info.get('description', 'No description.')}")
            output.append(f"* **Mood**: {info.get('mood', 'Neutral')}")
            if info.get("occupants"):
                output.append(f"* **Occupants**: {', '.join(info['occupants'])}")

    factions = bible.data.get("factions", {})
    if factions:
        for name, info in sorted(factions.items()):
            output.append(f"\n### Faction: {name}")
            if info.get("members"):
                output.append(f"* **Members**: {', '.join(info['members'])}")
            if info.get("relationships"):
                rels = [f"{k}: {v}" for k, v in info["relationships"].items()]
                output.append(f"* **Relationships**: {', '.join(rels)}")
            if info.get("plans"):
                output.append(f"* **Plans**: {', '.join(info['plans'])}")
    output.append("")

    output.append("## 📜 Historical Timeline")
    events = bible.data.get("events", [])
    if not events:
        output.append("*No events recorded in bible timeline.*")
    else:
        for ev in events:
            output.append(f"* **Chapter {ev.get('chapter_index', 0)}**: {ev.get('summary', 'No summary.')}")

    print("\n".join(output))
    return 0


def state_confirm(project_path: Path, recovery_run_path: Path) -> int:
    """Validate and safely merge recovery run locked layers into blue print/bible."""
    if not recovery_run_path.exists():
        print(f"Error: Recovery run file not found: {recovery_run_path}", file=sys.stderr)
        return 1

    try:
        recovery_payload = yaml.safe_load(recovery_run_path.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"Error loading recovery run file: {exc}", file=sys.stderr)
        return 1

    blueprint_path = project_path / "blueprint.yaml"
    bible_path = project_path / "bible.json"

    if not blueprint_path.exists() or not bible_path.exists():
        print("Error: Missing blueprint.yaml or bible.json in project.", file=sys.stderr)
        return 1

    try:
        blueprint = StoryBlueprint.from_yaml(blueprint_path)
        bible = StoryBible(bible_path)
    except Exception as exc:
        print(f"Error loading project: {exc}", file=sys.stderr)
        return 1

    locked = recovery_payload.get("candidate_locked_layers") or recovery_payload.get("candidate_locked_state")
    if not locked:
        print("Error: Recovery run file has no 'candidate_locked_layers' or 'candidate_locked_state'.", file=sys.stderr)
        return 1

    try:
        if "target_experience" in locked:
            te = locked["target_experience"]
            from auteur.blueprint import TargetExperience
            if isinstance(te, str):
                blueprint.identity.target_experience = TargetExperience(primary=te, progression="quiet pressure", avoid=[])
            elif isinstance(te, dict):
                blueprint.identity.target_experience = TargetExperience(
                    primary=te.get("primary", "bittersweet"),
                    progression=te.get("progression", "quiet pressure"),
                    avoid=te.get("avoid", []),
                )
        if "promise_constraints" in locked:
            pc = locked["promise_constraints"]
            if isinstance(pc, dict):
                if "genre" in pc:
                    blueprint.identity.genre = pc["genre"]
                if "mode" in pc:
                    blueprint.identity.mode = pc["mode"]
        if "scope_container" in locked:
            ss = locked["scope_container"]
            if isinstance(ss, dict):
                if "length_class" in ss:
                    blueprint.identity.length_class = ss["length_class"]
                if "estimated_chapters" in ss:
                    blueprint.structure.estimated_chapters = ss["estimated_chapters"]

        if "structural_forces" in locked:
            sf = locked["structural_forces"]
            if isinstance(sf, dict) and blueprint.story_engine:
                if "want" in sf:
                    blueprint.story_engine.main_thread.want.author_text = sf["want"]
                if "resistance" in sf:
                    blueprint.story_engine.main_thread.resistance.author_text = sf["resistance"]
                if "conflict" in sf:
                    blueprint.story_engine.main_thread.conflict.author_text = sf["conflict"]
                if "stakes" in sf:
                    blueprint.story_engine.main_thread.stakes.author_text = sf["stakes"]

        validated_bp = StoryBlueprint.model_validate(blueprint.model_dump())

        original_bible_data = json.loads(json.dumps(bible.data))
        if "carriers" in locked:
            carriers = locked["carriers"]
            if isinstance(carriers, dict):
                for section in {"characters", "locations", "items", "factions"}:
                    if section in carriers:
                        for name, info in carriers[section].items():
                            if section == "characters":
                                bible.upsert_character(name, **info)
                            else:
                                if name not in bible.data[section]:
                                    bible.data[section][name] = {}
                                bible.data[section][name].update(info)
            StoryBibleModel.model_validate(bible.data)

    except Exception as exc:
        print(f"Error: Recovery merge validation failed. Transaction rolled back.\nDetails: {exc}", file=sys.stderr)
        return 1

    try:
        blueprint_path.write_text(
            yaml.safe_dump(validated_bp.model_dump(mode="json"), sort_keys=False),
            encoding="utf-8",
        )
        bible.save()
        print("Success: Recovery candidate layers validated and merged into blueprint and bible.")
        return 0
    except Exception as exc:
        print(f"Error writing updates to disk: {exc}", file=sys.stderr)
        return 1
