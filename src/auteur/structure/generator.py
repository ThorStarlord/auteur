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
        ("dread", "grimdark_fantasy"): {
            "want": "To survive the cost of power",
            "resistance": "Every choice that grants power demands a piece of the self",
            "conflict": "Survival requires compromise, and compromise destroys what it meant to protect",
            "stakes": "The protagonist's humanity and the lives of those they cannot save",
            "change": "Acceptance that survival and morality cannot coexist"
        },
        ("grief", "mystery"): {
            "want": "To find meaning in loss through uncovering the truth",
            "resistance": "The truth is entangled with the grief itself",
            "conflict": "Uncovering the truth forces reliving the loss",
            "stakes": "The memory of the lost and the sanity of the seeker",
            "change": "Integration of grief into a new understanding rather than resolution"
        },
        ("wonder", "sci_fi"): {
            "want": "To understand a transformative discovery",
            "resistance": "The discovery challenges the foundation of human knowledge",
            "conflict": "Understanding requires abandoning comfortable assumptions",
            "stakes": "Humanity's place in the universe vs. the comfort of certainty",
            "change": "The protagonist expands their framework of what is possible"
        },
        ("longing", "romance"): {
            "want": "To be seen and accepted as they truly are",
            "resistance": "Fear that being truly seen will lead to rejection",
            "conflict": "Vulnerability invites connection but also the possibility of wounding",
            "stakes": "Lifelong loneliness vs. the risk of devastating heartbreak",
            "change": "The protagonist chooses vulnerability over self-protection"
        },
        ("dread", "horror"): {
            "want": "To survive and escape the incomprehensible threat",
            "resistance": "The threat does not follow known rules or logic",
            "conflict": "Fighting the threat makes it stronger; fleeing draws it closer",
            "stakes": "The protagonist's body, mind, and soul",
            "change": "The protagonist is marked permanently by the encounter"
        },
        ("awe", "space_opera"): {
            "want": "To protect what they love against cosmic-scale forces",
            "resistance": "The scale of the conflict dwarfs personal attachments",
            "conflict": "Saving the galaxy requires sacrificing what makes life worth living",
            "stakes": "Love, home, and the future of civilization",
            "change": "The protagonist learns that love is not weakness but the only thing worth fighting for"
        },
        ("hope", "ya_fantasy"): {
            "want": "To discover who they are and where they belong",
            "resistance": "Adult authorities and systems that do not see or value them",
            "conflict": "Fitting in requires hiding power; expressing power invites danger",
            "stakes": "Identity, belonging, and the safety of those they love",
            "change": "The protagonist claims their identity on their own terms"
        },
        ("curiosity", "mystery"): {
            "want": "To solve the puzzle before it is too late",
            "resistance": "Every answer reveals two more questions",
            "conflict": "The satisfaction of solving versus the danger of knowing",
            "stakes": "Justice, reputation, and the final piece that changes everything",
            "change": "The protagonist learns that some truths are harder to live with than ignorance"
        },
        ("tension", "epic_fantasy"): {
            "want": "To unite disparate forces against an overwhelming threat",
            "resistance": "Ancient grudges and competing agendas prevent alliance",
            "conflict": "Unity requires compromise that may cost the war before it begins",
            "stakes": "The survival of civilization and the souls of all who fight",
            "change": "The protagonist becomes the leader they never wanted to be"
        },
        ("relief", "romance"): {
            "want": "To find peace and safety in another's love",
            "resistance": "Past wounds and present obligations stand in the way",
            "conflict": "Letting go of control feels like danger but is the only path to connection",
            "stakes": "A future of lonely safety vs. a present of loving risk",
            "change": "The protagonist learns to trust again despite the risk of loss"
        },
        ("dread", "thriller"): {
            "want": "To stop the threat before it is too late",
            "resistance": "The threat is always one step ahead",
            "conflict": "Every countermeasure accelerates the antagonist's timeline",
            "stakes": "Innocent lives and the protagonist's moral line that must not be crossed",
            "change": "The protagonist sacrifices their innocence for a victory that feels hollow"
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
            "tension": {
                "want": "To prevent a cascading failure",
                "resistance": "The situation deteriorates faster than solutions arrive",
                "conflict": "Solving one problem creates a worse one",
                "stakes": "Everything the protagonist has built or loves",
                "change": "The protagonist accepts necessary losses"
            },
            "awe": {
                "want": "To reach something greater than themselves",
                "resistance": "Mortal limits and the cost of transcendence",
                "conflict": "Growth requires destruction of the former self",
                "stakes": "The self vs. something beyond the self",
                "change": "The protagonist is transformed by the encounter with the sublime"
            },
            "longing": {
                "want": "To close the distance to what they desire",
                "resistance": "The desired thing is protected by fear or circumstance",
                "conflict": "Approaching the desire risks losing it forever",
                "stakes": "Connection vs. safe isolation",
                "change": "The protagonist risks vulnerability to bridge the distance"
            },
            "grief": {
                "want": "To find meaning in what was lost",
                "resistance": "The loss resists integration into a coherent story",
                "conflict": "Holding on prevents healing; letting go feels like betrayal",
                "stakes": "Memory, identity, and the ability to love again",
                "change": "The protagonist carries the loss differently rather than moving past it"
            },
            "curiosity": {
                "want": "To discover the hidden truth",
                "resistance": "Protective systems and those who benefit from secrecy",
                "conflict": "The desire to know vs. the danger of what will be found",
                "stakes": "Ignorance and safety vs. knowledge and danger",
                "change": "The protagonist accepts that knowledge changes who they are"
            },
            "relief": {
                "want": "To release a burden they have carried too long",
                "resistance": "The burden is woven into their identity and relationships",
                "conflict": "Release requires trust; trust risks new burden",
                "stakes": "Freedom vs. the familiar safety of the known weight",
                "change": "The protagonist lets go of what defined them"
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


def _extract_carrier_names(blueprint: StoryBlueprint) -> list[str]:
    """Extract meaningful carrier names from blueprint characters and their identities."""
    carriers: list[str] = []
    for char in blueprint.characters:
        carriers.append(char.name)
        if char.role.value == "antagonist":
            carriers.append(f"{char.name}_faction")
        if char.role.value in ("deuteragonist", "support"):
            carriers.append(f"{char.name}_circle")
    return carriers


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
    all_carrier_names = _extract_carrier_names(blueprint)

    # Character arc for protagonist
    if characters:
        protagonist = characters[0]
        threads.append(GeneratedThread(
            name=f"{protagonist.name}_arc",
            thread_type=ThreadType.CHARACTER_ARC,
            want=f"{protagonist.name} wants to {forces.change.lower()}",
            function="pressures_change",
            carriers=[protagonist.name],
            confidence=0.85,
            rationale=f"Character arc thread tracks {protagonist.name}'s internal transformation."
        ))

    # Relationship arc for every pair of primary characters with different roles
    primary_chars = [c for c in characters if c.role.value in ("protagonist", "antagonist", "deuteragonist")]
    for i in range(len(primary_chars)):
        for j in range(i + 1, len(primary_chars)):
            a, b = primary_chars[i], primary_chars[j]
            dyn_type = "rivalry" if "antagonist" in (a.role.value, b.role.value) else "relationship"
            threads.append(GeneratedThread(
                name=f"{a.name}_{b.name}_{dyn_type}",
                thread_type=ThreadType.RELATIONSHIP_ARC,
                want=f"Negotiate the dynamic between {a.name} and {b.name}",
                function="mirrors" if "antagonist" not in (a.role.value, b.role.value) else "contrasts",
                carriers=[a.name, b.name],
                confidence=0.7,
                rationale=f"Relationship {dyn_type} between {a.name} and {b.name} explores themes of connection."
            ))

    # Thematic echo thread using character carriers
    theme_carriers = [c.name for c in characters if c.role.value in ("protagonist", "deuteragonist")]
    if theme_carriers:
        threads.append(GeneratedThread(
            name="thematic_echo",
            thread_type=ThreadType.THEMATIC_ECHO,
            want="To embody the central thematic question through repeated pattern and reflection",
            function="reveals",
            carriers=theme_carriers,
            confidence=0.6,
            rationale="Thematic echo thread uses motifs and patterns across carriers to deepen exploration of the central question."
        ))

    # Faction/world thread if antagonist exists
    antagonists = [c for c in characters if c.role.value == "antagonist"]
    if antagonists:
        ant = antagonists[0]
        threads.append(GeneratedThread(
            name=f"{ant.name}_pressure",
            thread_type=ThreadType.MYSTERY,
            want=f"Counter the threat posed by {ant.name}",
            function="escalates",
            carriers=[ant.name, f"{ant.name}_faction"],
            confidence=0.75,
            rationale=f"Antagonist {ant.name} thread escalates pressure on the main thread."
        ))

    return threads


def generate_story_engine(
    blueprint: StoryBlueprint,
    llm: object | None = None,
) -> GenerationProposal | list[StructureDiagnostic]:
    """
    Generate a complete story engine from target experience downward.

    When ``llm`` is provided (an LLMClient protocol-compatible object), the
    template-based forces and threads are refined against the author's premise
    via LLM call, producing story-specific rather than archetypal output.

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
        ))
        return diagnostics

    if not blueprint.characters:
        diagnostics.append(StructureDiagnostic(
            severity=DiagnosticSeverity.ERROR,
            layer=DiagnosticLayer.CARRIERS,
            rule="characters_required_for_generation",
            message="Cannot generate story engine: at least one character (protagonist) is required.",
            evidence=["Blueprint.characters list is empty"],
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

    # When an LLM client is provided, refine the template proposal
    if llm is not None:
        from auteur.structure.generation_refiner import llm_refine_story_engine
        try:
            proposal = llm_refine_story_engine(blueprint, llm, forces)
        except Exception:
            pass

    return proposal


# ---------------------------------------------------------------------------
# Symptom-based generation (bottom-up diagnostic from author symptom)
# ---------------------------------------------------------------------------

class SymptomDiagnosis(BaseModel):
    """A diagnosis produced from an author-described symptom."""
    symptom: str = Field(description="The original symptom text from the author")
    likely_layer: DiagnosticLayer = Field(description="Most likely structural layer causing the symptom")
    root_cause_hypothesis: str = Field(description="Hypothesis about the underlying structural issue")
    recommendation: str = Field(description="Actionable recommendation to address the root cause")
    alternative_hypotheses: list[str] = Field(default_factory=list, description="Other possible causes to consider")


_SYMPTOM_REGISTRY: list[dict] = [
    # Layer 4/5: Structural Forces / Threads — escalation and stakes
    {
        "keywords": ["midpoint", "middle", "second act", "sags", "flat", "no momentum"],
        "layer": DiagnosticLayer.THREADS,
        "root_cause": (
            "The subordinate threads may lack escalation pressure on the main thread. "
            "If threads only complicate without escalating stakes or pressing change, the middle loses momentum."
        ),
        "recommendation": (
            "Review each subordinate thread's supports_main_by functions. At least one thread "
            "should use 'escalates' or 'pressures_change'. Consider adding a thread whose "
            "escalation peak falls near the midpoint. Verify the main thread's stakes increase "
            "at the midpoint rather than remaining static."
        ),
        "alternatives": [
            "The target experience may be a single-note emotion without progression — check identity.target_experience.progression.",
            "The scope container may be too long for the available thread machinery — consider compressing the length class.",
        ],
    },
    # Layer 4: Structural Forces — stakes
    {
        "keywords": ["stakes", "consequence", "don't care", "unimportant", "no tension", "low stakes"],
        "layer": DiagnosticLayer.STRUCTURAL_FORCES,
        "root_cause": (
            "The stakes may be abstract, generic, or disconnected from the protagonist's want. "
            "Stakes must name a specific, concrete loss that the protagonist personally fears."
        ),
        "recommendation": (
            "Rewrite main_thread.stakes.author_text to name a specific, personal loss. "
            "Generic stakes like 'the world will end' are less effective than 'she will lose the only family she has'. "
            "Ensure each subordinate thread also declares stakes that escalate alongside the main thread."
        ),
        "alternatives": [
            "The target experience.avoid list may include the very emotion the stakes should evoke — check for contradiction.",
            "The mode may not match the stakes register (e.g., intimate mode with civilizational stakes).",
        ],
    },
    # Layer 4: Change — ending
    {
        "keywords": ["ending", "finale", "climax", "doesn't land", "anticlimax", "fizzles", "resolution"],
        "layer": DiagnosticLayer.STRUCTURAL_FORCES,
        "root_cause": (
            "The main thread's change may duplicate its want, or the change may describe an external outcome "
            "rather than an internal transformation. An ending lands when the protagonist's change is "
            "emotionally earned and thematically coherent."
        ),
        "recommendation": (
            "Verify main_thread.change is a genuine transformation of the protagonist, not just goal achievement. "
            "Cross-reference with the ThematicCore: the ending should confirm or complicate the thesis. "
            "If the ending tone contradicts the genre contract, consider aligning them."
        ),
        "alternatives": [
            "The forbidden_mismatch rules may be blocking the natural ending tone — check genre override diagnostics.",
            "The target experience may promise an emotion that the ending does not deliver — trace from avoided feelings.",
        ],
    },
    # Layer 6: Carriers — characters
    {
        "keywords": ["character", "thin", "flat", "cardboard", "generic", "uninteresting", "motivation"],
        "layer": DiagnosticLayer.CARRIERS,
        "root_cause": (
            "Characters may lack sufficient structural force carriers: each character should instantiate "
            "a specific want, resistance point, or thematic function. Characters without structural roles "
            "feel generic."
        ),
        "recommendation": (
            "Review the characters list: does every character have a declared want, a key milestone that "
            "tests it, and a demonstrable role in at least one thread? Remove characters whose structural "
            "function can be absorbed. For remaining characters, sharpen their want into something specific "
            "and personal."
        ),
        "alternatives": [
            "The psychology_budget for this genre may be too shallow for the depth you intend — consider a genre override.",
            "The POV experience contracts may not match the character roster — prune unknown-character contracts.",
        ],
    },
    # Layer 3: Scope — pacing
    {
        "keywords": ["pacing", "slow", "rushed", "too fast", "uneven", "drag", "breathless"],
        "layer": DiagnosticLayer.SCOPE,
        "root_cause": (
            "The scope container may mismatch the genre's narrative runway requirements. A length class "
            "that is too short forces rushed pacing; one that is too long can cause pacing drag."
        ),
        "recommendation": (
            "Check the genre contract's scope_profile: does the current length class match the genre's "
            "natural_lengths or minimum_viable_length? If not, either adjust the length class or add a "
            "genre override with compression/subversion strategy. For pacing drag, increase subplot budget "
            "or add threads. For rushed pacing, decrease subplot budget or remove threads."
        ),
        "alternatives": [
            "The medium contract's unit_of_delivery may create pacing expectations that the current scope cannot satisfy.",
            "The act structure may need redistributing — check estimated_chapters vs. act proportions.",
        ],
    },
    # Layer 5: Threads — subplots
    {
        "keywords": ["subplot", "goes nowhere", "pointless", "tangent", "distraction", "unresolved"],
        "layer": DiagnosticLayer.THREADS,
        "root_cause": (
            "Subordinate threads may lack a declared support function for the main thread, or their "
            "thematic_function may be unconnected to the main thesis. Threads without structural purpose "
            "become dead ends."
        ),
        "recommendation": (
            "Audit every subordinate thread: does it have at least one supports_main_by function "
            "(escalates, pressures_change, reveals, mirrors, contrasts, complicates, pays_off)? "
            "Does its thematic_function reference the core thesis? Remove threads that lack both. "
            "Merge threads that serve identical functions."
        ),
        "alternatives": [
            "The subplot_budget may be too high for the length class — reduce threads or increase container size.",
            "A thread may be misclassified (e.g., a mystery thread without reveals function).",
        ],
    },
    # Layer 2: Genre Contract — world/milieu
    {
        "keywords": ["world", "generic", "familiar", "unoriginal", "setting", "milieu", "cliche"],
        "layer": DiagnosticLayer.CONSTRAINTS,
        "root_cause": (
            "The genre contract may be applied without subgenre modifiers or genre overrides. "
            "A bare genre without subgenre specificity tends toward generic execution. "
            "Subgenre modifiers inject specific trope biases and setup requirements that differentiate the world."
        ),
        "recommendation": (
            "Add one or more subgenre modifiers that sharpen the contract. For example, 'locked_room' "
            "for mystery adds clue-fair puzzle logic and spatial constraints. 'hardboiled' adds "
            "institutional rot and moral ambiguity. If no subgenre fits, add a GenreOverride of type "
            "'safe_variation' that documents how this world differs from the genre standard."
        ),
        "alternatives": [
            "The genre itself may be a mismatch for the premise — consider re-running identity recommend with a different genre constraint.",
            "The target audience may expect deeper worldbuilding than the current scope can deliver — adjust scope or audience.",
        ],
    },
    # Layer 9: Theme / Resonance
    {
        "keywords": ["theme", "message", "point", "meaningless", "say nothing", "shallow", "preachy"],
        "layer": DiagnosticLayer.THEME,
        "root_cause": (
            "The theme thesis may be unrepresented in thread thematic_functions, or the thesis may be "
            "so broad that no thread can test it meaningfully. A story feels shallow when its thematic "
            "question is stated but never examined through conflicting thread outcomes."
        ),
        "recommendation": (
            "Check that at least one thread's thematic_function echoes the thesis. Ensure threads "
            "take opposing positions on the thesis (one thread affirms, another complicates). "
            "If the thesis is too broad (e.g., 'love is important'), sharpen it into a debatable "
            "claim (e.g., 'love justifies betrayal' vs. 'love requires honesty')."
        ),
        "alternatives": [
            "The target experience may be disconnected from the thesis — the emotional promise should reinforce the thematic argument.",
            "The central_engine conflict may not engage the thesis at all — rewrite conflict to put the thesis under pressure.",
        ],
    },
    # Layer 1: Target Experience — emotional confusion
    {
        "keywords": ["tone", "confused", "mixed", "emotional whiplash", "jarring", "wrong emotion"],
        "layer": DiagnosticLayer.TARGET_EXPERIENCE,
        "root_cause": (
            "The target experience's primary emotion may conflict with genre contract constraints, "
            "or the progression may jump between incompatible feeling states without transitional beats. "
            "Readers experience emotional whiplash when the promised experience contradicts the genre delivery."
        ),
        "recommendation": (
            "Verify that primary does not appear in avoid. Check that progression is a sequence of "
            "adjacent emotions, not opposite poles (e.g., 'dread -> tension -> relief' works; "
            "'dread -> joy -> horror' likely does not). Ensure the genre contract's psychology_budget "
            "can support the target emotional depth."
        ),
        "alternatives": [
            "The mode may be forcing a tonal register that fights the target experience (e.g., 'noir' mode with 'hope' target).",
            "The medium contract's modulation_biases may filter out needed tonal range.",
        ],
    },
]


def diagnose_symptom(symptom: str, blueprint: StoryBlueprint | None = None) -> list[SymptomDiagnosis]:
    """Map an author-described symptom to likely structural root causes.

    Uses keyword matching against the symptom registry. Returns one or more
    SymptomDiagnosis results sorted by relevance. When a blueprint is provided,
    additional context-specific analysis may refine the diagnosis.

    Args:
        symptom: Free-text description of the felt problem (e.g. 'midpoint feels flat').
        blueprint: Optional StoryBlueprint for context-aware refinement.

    Returns:
        List of SymptomDiagnosis results, most relevant first.
    """
    symptom_lower = symptom.casefold()
    matches: list[tuple[int, dict]] = []

    for entry in _SYMPTOM_REGISTRY:
        score = 0
        for kw in entry["keywords"]:
            if kw in symptom_lower:
                score += 1
        if score > 0:
            matches.append((score, entry))

    # Sort by match count descending
    matches.sort(key=lambda x: x[0], reverse=True)

    if not matches:
        return [
            SymptomDiagnosis(
                symptom=symptom,
                likely_layer=DiagnosticLayer.STRUCTURAL_FORCES,
                root_cause_hypothesis=(
                    "The symptom does not match a known structural pattern. "
                    "Consider whether it is a modulation (prose-level) issue rather than "
                    "a structural (narrative-engine) issue."
                ),
                recommendation=(
                    "Run auteur structure diagnose on the blueprint to surface any "
                    "detectable structural issues, then check the most recent chapter "
                    "draft for prose-level problems."
                ),
                alternative_hypotheses=[
                    "The issue may be in Layer 8 (Modulation) — prose style, pacing, voice.",
                    "The issue may be in Layer 7 (Representation) — scene ordering, reveal timing.",
                ],
            )
        ]

    results: list[SymptomDiagnosis] = []
    for score, entry in matches:
        root_cause = entry["root_cause"]
        recommendation = entry["recommendation"]

        # Refine with blueprint context if available
        if blueprint is not None and entry["layer"] == DiagnosticLayer.THREADS:
            engine = blueprint.story_engine
            if engine and engine.threads:
                missing_escalation = [
                    t.name for t in engine.threads
                    if not any(f in ("escalates", "pressures_change") for f in (getattr(t, "supports_main_by", []) or []))
                ]
                if missing_escalation:
                    escalation_hint = (
                        f" Specific threads lacking escalation: {', '.join(missing_escalation)}."
                    )
                    recommendation += escalation_hint

        results.append(SymptomDiagnosis(
            symptom=symptom,
            likely_layer=entry["layer"],
            root_cause_hypothesis=root_cause,
            recommendation=recommendation,
            alternative_hypotheses=entry.get("alternatives", []),
        ))

    return results
