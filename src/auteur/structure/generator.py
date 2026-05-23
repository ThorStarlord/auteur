"""
Structure Engine v1 Generative Path: Top-Down Synthesis

Generates story structure from global constraints (target experience, genre,
scope, mode) downward through structural forces → threads → scene proposals.
"""

from __future__ import annotations

from pydantic import BaseModel, Field
from typing import Optional

from auteur.blueprint import StoryBlueprint, StoryEngine, MainThread, StoryThread, ThreadType
from auteur.structure.diagnostics import DiagnosticLayer, DiagnosticSeverity, StructureDiagnostic


class StructuralForcesSynthesis(BaseModel):
    """Synthesized structural forces from target experience and genre constraints."""
    want: str = Field(description="What the protagonist fundamentally wants")
    resistance: str = Field(description="What resists or blocks the want")
    conflict: str = Field(description="The collision between want and resistance")
    stakes: str = Field(description="What can be lost or gained")
    change: str = Field(description="How the protagonist transforms")

    rationale: str = Field(description="Why this force structure fits the genre and target experience")


class GeneratedThread(BaseModel):
    """A thread synthesized by the generative engine."""
    name: str
    thread_type: ThreadType
    want: str
    function: Optional[str] = None
    carriers: list[str] = Field(default_factory=list)
    confidence: float = Field(default=0.8, ge=0.0, le=1.0)
    rationale: str = Field(default="")


class GenerationProposal(BaseModel):
    """A complete story engine proposal generated top-down."""
    structural_forces: StructuralForcesSynthesis
    main_thread: GeneratedThread
    subordinate_threads: list[GeneratedThread] = Field(default_factory=list)
    generation_method: str = "target-experience-driven"
    constraints_honored: list[str] = Field(default_factory=list)
    potential_issues: list[str] = Field(default_factory=list)


def synthesize_structural_forces(blueprint: StoryBlueprint) -> StructuralForcesSynthesis | None:
    """
    Synthesize core structural forces from target experience, genre, and mode.

    Returns None if the blueprint lacks sufficient constraints to generate forces.
    """
    # Extract constraints from blueprint
    target_exp = blueprint.identity.target_experience
    if not target_exp:
        return None

    primary_feeling = target_exp.primary
    genre = blueprint.identity.genre
    mode = blueprint.identity.mode

    # Get narrative runway if scope_contract is defined
    scope = "unknown"
    if blueprint.structure.scope_contract:
        scope = blueprint.structure.scope_contract.narrative_runway.value if blueprint.structure.scope_contract.narrative_runway else "unknown"

    # Base forces from target experience + genre + mode
    # These are archetypal patterns that fit the emotional promise and genre contract

    force_map = {
        ("dread", "mystery"): {
            "want": "To uncover a hidden truth",
            "resistance": "Deception and institutional corruption hide the truth",
            "conflict": "Each revelation deepens danger",
            "stakes": "The seeker's life and sanity vs. the truth",
            "change": "The protagonist moves from naive belief to hard knowledge"
        },
        ("awe", "epic_fantasy"): {
            "want": "To witness or achieve the impossible",
            "resistance": "The world's physics and mortality constrain all beings",
            "conflict": "Transcendence requires sacrifice of the human self",
            "stakes": "The soul vs. apotheosis",
            "change": "The protagonist becomes something other than human"
        },
        ("catharsis", "tragedy"): {
            "want": "To escape or overcome a flaw",
            "resistance": "The flaw is intrinsic to the protagonist's nature",
            "conflict": "Escape attempts trigger the very catastrophe they tried to prevent",
            "stakes": "The protagonist and everyone they love",
            "change": "Acceptance of fate rather than escape from it"
        },
        ("hope", "romance"): {
            "want": "Connection with another specific person",
            "resistance": "Circumstance, misunderstanding, or incompatibility",
            "conflict": "Getting closer reveals incompleteness",
            "stakes": "Loneliness and the possibility of forever being alone",
            "change": "The protagonist learns to be vulnerable and accept another"
        },
        ("tension", "thriller"): {
            "want": "Survive or prevent a cascading disaster",
            "resistance": "The threat multiplies faster than solutions can contain it",
            "conflict": "Each solution creates new problems and accelerates the threat",
            "stakes": "The innocent and the protagonist's moral core",
            "change": "The protagonist becomes harder, colder, or corrupted by necessary actions"
        },
    }

    key = (primary_feeling, genre.value) if genre else (primary_feeling, "neutral")
    base_forces = force_map.get(key)

    if not base_forces:
        # Fallback: generic forces from just primary feeling
        generic_map = {
            "dread": {
                "want": "To survive or escape",
                "resistance": "The threat is relentless and ubiquitous",
                "conflict": "Escape routes lead back to danger",
                "stakes": "Life and freedom",
                "change": "The protagonist accepts the inescapable nature of the threat"
            },
            "hope": {
                "want": "To achieve a positive outcome",
                "resistance": "Circumstance and doubt block the way",
                "conflict": "Success requires sacrificing something equally important",
                "stakes": "The dream and the self",
                "change": "The protagonist redefines what success means"
            },
            "catharsis": {
                "want": "Closure and acceptance",
                "resistance": "The past will not release its grip",
                "conflict": "Facing the past shatters the present illusion",
                "stakes": "Identity and peace",
                "change": "The protagonist integrates the past into a coherent self"
            },
        }
        base_forces = generic_map.get(primary_feeling, {
            "want": "To change their circumstance",
            "resistance": "Internal and external forces oppose change",
            "conflict": "Change requires destroying the old self",
            "stakes": "Everything the protagonist knows",
            "change": "Transformation or death"
        })

    rationale = (
        f"Forces synthesized to honor target experience '{primary_feeling}', "
        f"genre '{genre.value if genre else 'unspecified'}', "
        f"and scope '{scope}'. Archetype fitted to mode constraints."
    )

    return StructuralForcesSynthesis(
        want=base_forces["want"],
        resistance=base_forces["resistance"],
        conflict=base_forces["conflict"],
        stakes=base_forces["stakes"],
        change=base_forces["change"],
        rationale=rationale
    )


def generate_main_thread(
    blueprint: StoryBlueprint,
    forces: StructuralForcesSynthesis
) -> GeneratedThread:
    """
    Generate the main_thread from synthesized structural forces.
    """
    protagonist = blueprint.characters[0] if blueprint.characters else None
    protagonist_name = protagonist.name if protagonist else "the protagonist"

    main_thread_want = forces.want.replace("the protagonist", protagonist_name)

    return GeneratedThread(
        name="main_plot",
        thread_type=ThreadType.MAIN_PLOT,
        want=main_thread_want,
        function="Drives causality, escalation, and the primary emotional arc",
        carriers=[protagonist_name] if protagonist else [],
        confidence=0.95,
        rationale="Main thread carriers the protagonist's central want and embodies the story's primary conflict."
    )


def generate_subordinate_threads(
    blueprint: StoryBlueprint,
    forces: StructuralForcesSynthesis,
    main_thread: GeneratedThread
) -> list[GeneratedThread]:
    """
    Generate subordinate threads (character arcs, subplots, themes) that support the main.
    """
    threads: list[GeneratedThread] = []
    characters = blueprint.characters

    # Character arc for protagonist (if they have secondary characters)
    if len(characters) > 1:
        protagonist = characters[0]
        threads.append(GeneratedThread(
            name=f"{protagonist.name}_arc",
            thread_type=ThreadType.CHARACTER_ARC,
            want=f"{protagonist.name} wants to {forces.change.lower()}",
            function="pressures_change",
            carriers=[protagonist.name],
            confidence=0.85,
            rationale="Character arc thread tracks the protagonist's internal transformation."
        ))

    # Relationship arc if there's a potential love interest or key relationship
    if len(characters) > 1:
        other = characters[1]
        threads.append(GeneratedThread(
            name=f"{characters[0].name}_relationship",
            thread_type=ThreadType.RELATIONSHIP_ARC,
            want=f"Connection between {characters[0].name} and {other.name}",
            function="mirrors",
            carriers=[characters[0].name, other.name],
            confidence=0.7,
            rationale="Relationship arc explores themes of connection through interpersonal dynamics."
        ))

    # Thematic echo thread
    themes = blueprint.theme.core_questions if hasattr(blueprint.theme, 'core_questions') else []
    if themes:
        threads.append(GeneratedThread(
            name="thematic_echo",
            thread_type=ThreadType.THEMATIC_ECHO,
            want="To embody the central thematic question through repeated pattern and reflection",
            function="reveals",
            carriers=[characters[0].name] if characters else [],
            confidence=0.6,
            rationale="Thematic echo thread uses motifs and patterns to deepen exploration of the story's central question."
        ))

    return threads


def generate_story_engine(blueprint: StoryBlueprint) -> GenerationProposal | list[StructureDiagnostic]:
    """
    Generate a complete story engine from target experience downward.

    Returns either a GenerationProposal (success) or a list of diagnostics (failure).
    """
    diagnostics: list[StructureDiagnostic] = []

    # Check for required inputs
    if not blueprint.identity.target_experience:
        diagnostics.append(StructureDiagnostic(
            severity=DiagnosticSeverity.ERROR,
            layer=DiagnosticLayer.TARGET_EXPERIENCE,
            rule="target_experience_required_for_generation",
            message="Cannot generate story engine: target_experience is required but missing.",
            evidence=["Blueprint.identity.target_experience is None"],
            repair_options=None
        ))
        return diagnostics

    if not blueprint.characters:
        diagnostics.append(StructureDiagnostic(
            severity=DiagnosticSeverity.ERROR,
            layer=DiagnosticLayer.CARRIERS,
            rule="characters_required_for_generation",
            message="Cannot generate story engine: at least one character (protagonist) is required.",
            evidence=["Blueprint.characters list is empty"],
            repair_options=None
        ))
        return diagnostics

    # Synthesize structural forces
    forces = synthesize_structural_forces(blueprint)
    if not forces:
        diagnostics.append(StructureDiagnostic(
            severity=DiagnosticSeverity.ERROR,
            layer=DiagnosticLayer.STRUCTURAL_FORCES,
            rule="structural_forces_synthesis_failed",
            message="Could not synthesize structural forces from target experience and genre.",
            evidence=[
                f"Target experience: {blueprint.identity.target_experience}",
                f"Genre: {blueprint.identity.genre}",
                f"Mode: {blueprint.identity.mode}"
            ],
            repair_options=None
        ))
        return diagnostics

    # Generate main thread
    main_thread = generate_main_thread(blueprint, forces)

    # Generate subordinate threads
    subordinate_threads = generate_subordinate_threads(blueprint, forces, main_thread)

    # Get scope for constraints honored
    scope_str = "unknown"
    if blueprint.structure.scope_contract:
        scope_str = blueprint.structure.scope_contract.narrative_runway.value if blueprint.structure.scope_contract.narrative_runway else "unknown"

    # Build proposal
    proposal = GenerationProposal(
        structural_forces=forces,
        main_thread=main_thread,
        subordinate_threads=subordinate_threads,
        constraints_honored=[
            f"Target experience: {blueprint.identity.target_experience.primary}",
            f"Genre: {blueprint.identity.genre.value}",
            f"Mode: {blueprint.identity.mode.value if blueprint.identity.mode else 'unspecified'}",
            f"Scope: {scope_str}",
        ],
        potential_issues=[
            "Generated threads are archetypal and should be refined against specific premise and characters.",
            "Thread confidence scores reflect generic patterns; custom adjustments recommended.",
            "Subordinate threads may need customization based on author intent.",
        ]
    )

    return proposal
