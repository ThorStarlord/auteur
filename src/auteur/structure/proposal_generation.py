"""Proposal generation — create StructureProposal artifacts from blueprints and diagnostics."""

from __future__ import annotations

from typing import Any
from uuid import uuid4
import re

from auteur.blueprint import StoryBlueprint, CharacterRole
from auteur.structure.diagnostics import StructureDiagnostic
from auteur.structure.proposal_models import (
    _proposal_slug,
    ProposalOption,
    ProposalSelection,
    ProposalType,
    StructureProposal,
)


def propose_story_engine(blueprint: StoryBlueprint) -> StructureProposal:
    """Generate a non-mutating proposal artifact for a blueprint that lacks a story_engine.

    Returns a :class:`StructureProposal` with 3 options grounded in the blueprint's
    identity, theme, contract, and characters.  The blueprint is never modified.

    Raises:
        ValueError: if the blueprint already has a story_engine.
    """
    if blueprint.story_engine is not None:
        raise ValueError(
            "propose_story_engine requires a blueprint with no story_engine, "
            "but blueprint.story_engine is already set."
        )

    # Harvest context from the blueprint for grounding.
    author_intent: str = blueprint.identity.author_intent
    genre: str = blueprint.identity.genre.value
    mode: str = (
        blueprint.identity.mode.value if blueprint.identity.mode else "unspecified"
    )
    central_question: str = blueprint.theme.central_question
    thesis: str = blueprint.theme.thesis
    ending_tone: str = blueprint.contract.mandatory_ending_tone.value
    title: str = blueprint.identity.title

    # Protagonist hint — use first protagonist character name if available.
    protagonist_name: str = "the protagonist"
    for char in blueprint.characters:
        if char.role == CharacterRole.PROTAGONIST:
            protagonist_name = char.name
            break

    # --- Option A: Lean protagonist drive (single main thread, no subplots) -------
    option_a_want = (
        f"{protagonist_name.capitalize()} wants to resolve the central tension "
        f"arising from: {author_intent[:80].rstrip('.')}."
    )
    option_a = ProposalOption(
        id="lean_protagonist_drive",
        summary=(
            f"A single focused main thread following {protagonist_name}'s want and "
            f"resistance in a {mode} mode — no subordinate threads."
        ),
        tradeoffs=(
            "Keeps structure tightly unified and easy to draft chapter-by-chapter. "
            "Risk: limited space for secondary character depth or thematic counterpoint."
        ),
        data={
            "story_engine": {
                "main_thread": {
                    "type": "main_plot",
                    "want": {
                        "author_text": option_a_want,
                        "checkable_claims": [],
                    },
                    "resistance": {
                        "author_text": (
                            f"The world, or {protagonist_name}'s own psychology, opposes "
                            f"resolution — grounded in the {genre} genre logic."
                        ),
                        "checkable_claims": [],
                    },
                    "conflict": {
                        "author_text": (
                            "External obstacles and internal contradiction collide at each "
                            "act turn, forcing an escalating series of choices."
                        ),
                        "checkable_claims": [],
                    },
                    "stakes": {
                        "author_text": (
                            f"Failure means a {ending_tone} outcome for {protagonist_name} "
                            f"and everyone whose fate is tied to theirs."
                        ),
                        "checkable_claims": [],
                    },
                    "change": {
                        "author_text": (
                            f"By the end, {protagonist_name} is transformed in a way that "
                            f"answers the central question: {central_question}"
                        ),
                        "checkable_claims": [],
                    },
                    "thematic_function": (
                        f"The main thread embodies the thesis: {thesis}"
                    ),
                },
                "threads": [],
            }
        },
    )

    # --- Option B: Protagonist + one character-arc subordinate thread -------------
    option_b_want = (
        f"{protagonist_name.capitalize()} pursues the core need that defines the "
        f"{mode} arc, while a key relationship thread runs parallel."
    )
    option_b = ProposalOption(
        id="protagonist_with_relationship_arc",
        summary=(
            f"Main thread for {protagonist_name} plus one subordinate relationship or "
            f"character-arc thread that mirrors or contrasts the central conflict."
        ),
        tradeoffs=(
            "Adds emotional texture and a second dramatic register. "
            "Risk: the subordinate thread must be carefully paced to avoid "
            "splitting reader attention at critical moments."
        ),
        data={
            "story_engine": {
                "main_thread": {
                    "type": "main_plot",
                    "want": {
                        "author_text": option_b_want,
                        "checkable_claims": [],
                    },
                    "resistance": {
                        "author_text": (
                            f"Systemic and interpersonal forces in the {genre} setting "
                            f"push back against {protagonist_name}'s goal."
                        ),
                        "checkable_claims": [],
                    },
                    "conflict": {
                        "author_text": (
                            "The protagonist's external goal and internal wound are "
                            "constantly in friction, sharpened at each act break."
                        ),
                        "checkable_claims": [],
                    },
                    "stakes": {
                        "author_text": (
                            f"The relationship at the heart of the subordinate thread is "
                            f"what {protagonist_name} stands to lose if the main thread fails."
                        ),
                        "checkable_claims": [],
                    },
                    "change": {
                        "author_text": (
                            f"{protagonist_name}'s resolution of both threads answers: "
                            f"{central_question}"
                        ),
                        "checkable_claims": [],
                    },
                    "thematic_function": thesis,
                },
                "threads": [
                    {
                        "name": "Relationship Arc (placeholder — rename for your story)",
                        "type": "relationship_arc",
                        "want": {
                            "author_text": (
                                "A key secondary character wants something that intersects "
                                f"with {protagonist_name}'s goal — edit to fit your cast."
                            ),
                            "checkable_claims": [],
                        },
                        "resistance": {
                            "author_text": (
                                "The same forces that oppose the protagonist also pressure "
                                "this relationship, but from a different angle."
                            ),
                            "checkable_claims": [],
                        },
                        "conflict": {
                            "author_text": (
                                "Loyalty vs self-preservation; trust vs fear of betrayal."
                            ),
                            "checkable_claims": [],
                        },
                        "stakes": {
                            "author_text": (
                                f"The bond between {protagonist_name} and this character "
                                "will define the emotional register of the ending."
                            ),
                            "checkable_claims": [],
                        },
                        "change": {
                            "author_text": (
                                "The relationship is either deepened, severed, or transformed "
                                "by the climax of the main thread."
                            ),
                            "checkable_claims": [],
                        },
                        "supports_main_by": ["mirrors"],
                        "thematic_function": (
                            f"This thread reflects the motifs of the story and "
                            f"holds the thesis ({thesis}) up to a different light."
                        ),
                    }
                ],
            }
        },
    )

    # --- Option C: Thematic ensemble (main thread + thematic-echo thread) ---------
    option_c = ProposalOption(
        id="thematic_ensemble",
        summary=(
            f"Main thread interrogates the central question directly; a thematic-echo "
            f"thread dramatises the thesis from an opposing or complementary angle."
        ),
        tradeoffs=(
            f"Produces philosophically layered storytelling aligned with the {genre} genre. "
            "Risk: requires careful structural architecture to prevent the thematic thread "
            "from becoming an essay rather than a dramatic story strand."
        ),
        data={
            "story_engine": {
                "main_thread": {
                    "type": "main_plot",
                    "want": {
                        "author_text": (
                            f"{protagonist_name.capitalize()} wants to answer, through action, "
                            f"the question the story poses: {central_question}"
                        ),
                        "checkable_claims": [],
                    },
                    "resistance": {
                        "author_text": (
                            f"Every scene in a {mode} story resists the protagonist's "
                            f"preferred answer — edit this to match your antagonist force."
                        ),
                        "checkable_claims": [],
                    },
                    "conflict": {
                        "author_text": (
                            "The conflict is between the world-as-it-is and the world-as-it-could-be "
                            "if the protagonist's desire were fulfilled."
                        ),
                        "checkable_claims": [],
                    },
                    "stakes": {
                        "author_text": (
                            f"If the protagonist cannot answer the central question in action, "
                            f"the {ending_tone} outcome becomes inevitable."
                        ),
                        "checkable_claims": [],
                    },
                    "change": {
                        "author_text": (
                            f"The story's answer to '{central_question}' is embodied in how "
                            f"{protagonist_name} changes (or refuses to change)."
                        ),
                        "checkable_claims": [],
                    },
                    "thematic_function": (
                        f"Directly dramatises the thesis: {thesis}"
                    ),
                },
                "threads": [
                    {
                        "name": "Thematic Echo (placeholder — rename for your story)",
                        "type": "thematic_echo",
                        "want": {
                            "author_text": (
                                "A secondary viewpoint or subplot wants the opposite — or a "
                                "distorted version — of what the protagonist wants, illuminating "
                                "the thesis by contrast."
                            ),
                            "checkable_claims": [],
                        },
                        "resistance": {
                            "author_text": (
                                "The same thematic forces press down on this strand, but the "
                                "character responds in a different way, showing the cost of "
                                "the alternative path."
                            ),
                            "checkable_claims": [],
                        },
                        "conflict": {
                            "author_text": (
                                "Ideological or moral conflict that externalises the thesis "
                                "as a contest between two world-views."
                            ),
                            "checkable_claims": [],
                        },
                        "stakes": {
                            "author_text": (
                                "If this thread fails, the thesis goes uncontested — the story "
                                "loses its dialectical tension."
                            ),
                            "checkable_claims": [],
                        },
                        "change": {
                            "author_text": (
                                "Resolution of this thread provides thematic counterpoint "
                                "to the main thread's ending beat."
                            ),
                            "checkable_claims": [],
                        },
                        "supports_main_by": ["contrasts"],
                        "thematic_function": (
                            f"Holds a mirror to the thesis from the opposing angle, "
                            f"enriching the answer to: {central_question}"
                        ),
                    }
                ],
            }
        },
    )

    # Normalize proposal_id to a safe slug (alphanumeric + underscore only) to prevent
    # path traversal or invalid filename issues when apply_proposal_to_blueprint() uses it.
    safe_title_slug = re.sub(r"[^a-z0-9]+", "_", title.lower()).strip("_")[:40]
    proposal_id = f"story_engine_{safe_title_slug}"

    return StructureProposal(
        proposal_id=proposal_id,
        type=ProposalType.GENERATION,
        source_rule="story_engine.missing",
        summary=(
            f"Story engine proposal for '{title}' ({genre}, {mode}). "
            f"Central question: {central_question} "
            f"Three structural options are offered below, grounded in the blueprint's "
            f"identity, theme, and contract. Choose one to edit and accept."
        ),
        options=[option_a, option_b, option_c],
    )


def propose_repairs_from_diagnostics(
    diagnostics: list[StructureDiagnostic],
) -> list[StructureProposal]:
    """Convert structure diagnostics into human-editable repair proposals.

    Diagnostics provide repair text, not guaranteed blueprint patches, so generated
    options leave `data` empty until an author edits a concrete patch into the
    proposal artifact.
    """
    proposals: list[StructureProposal] = []
    for index, diagnostic in enumerate(diagnostics, start=1):
        options: list[ProposalOption] = []
        for option_index, repair in enumerate(
            diagnostic.repair_options.preserve_intent,
            start=1,
        ):
            options.append(
                ProposalOption(
                    id=f"preserve_intent_{option_index}",
                    summary=repair,
                    tradeoffs=(
                        "Preserve-intent repair. Keeps the declared target "
                        "experience and constraints unless the author edits "
                        "the proposal data."
                    ),
                    data={},
                )
            )
        for option_index, repair in enumerate(
            diagnostic.repair_options.challenge_intent,
            start=1,
        ):
            options.append(
                ProposalOption(
                    id=f"challenge_intent_{option_index}",
                    summary=repair,
                    tradeoffs=(
                        "Challenge-intent repair. Reconsiders a higher-level "
                        "intent or constraint before the author edits the "
                        "proposal data."
                    ),
                    data={},
                )
            )

        evidence = "; ".join(diagnostic.evidence)
        summary = (
            f"{diagnostic.severity.value} diagnostic "
            f"{diagnostic.rule} in report context {diagnostic.layer.value}: "
            f"{diagnostic.message} Evidence: {evidence}"
        )
        proposals.append(
            StructureProposal(
                proposal_id=f"repair_{index}_{_proposal_slug(diagnostic.rule)}",
                type=ProposalType.REPAIR,
                source_rule=diagnostic.rule,
                source_domain="structure",
                summary=summary,
                options=options,
            )
        )
    return proposals


def propose_repairs_from_diagnostic_report(
    report: Mapping[str, Any],
) -> list[StructureProposal]:
    diagnostics = [
        diagnostic
        if isinstance(diagnostic, StructureDiagnostic)
        else StructureDiagnostic.model_validate(diagnostic)
        for diagnostic in report.get("diagnostics", [])
    ]
    return propose_repairs_from_diagnostics(diagnostics)


def propose_repairs_from_audit_diagnostics(
    diagnostics: list[object],
) -> list[StructureProposal]:
    """Convert Bible audit diagnostics into human-editable repair proposals.

    Each diagnostic is expected to have ``rule``, ``severity``, ``message``,
    and ``repair_options`` attributes (matching ``BibleAuditDiagnostic`` and
    ``StructureDiagnostic`` shapes).  The ``data`` field of each option is left
    empty — authors edit a concrete repair into the proposal YAML.

    Sets ``source_domain='bible_audit'`` on every produced proposal.

    Diagnostics with no ``repair_options`` (empty ``preserve_intent`` and
    ``challenge_intent``) are informational warnings and are skipped — they
    cannot produce a valid ``StructureProposal``.
    """
    proposals: list[StructureProposal] = []
    for idx, d in enumerate(diagnostics, start=1):
        options: list[ProposalOption] = []
        for pi, preserve in enumerate(d.repair_options.preserve_intent, start=1):
            options.append(
                ProposalOption(
                    id=f"preserve_{pi}",
                    summary=preserve,
                    tradeoffs=(
                        "Preserves the story's declared intent while "
                        "resolving the continuity break."
                    ),
                    data={},
                )
            )
        for ci, challenge in enumerate(d.repair_options.challenge_intent, start=1):
            options.append(
                ProposalOption(
                    id=f"challenge_{ci}",
                    summary=challenge,
                    tradeoffs=(
                        "Questions a higher-level assumption to resolve "
                        "the continuity break."
                    ),
                    data={},
                )
            )
        # Skip informational diagnostics that have no repair options — they
        # cannot produce a valid StructureProposal (options list must be non-empty).
        if not options:
            continue
        proposals.append(
            StructureProposal(
                proposal_id=f"repair_{idx}_{d.rule.replace('.', '_')}",
                type=ProposalType.REPAIR,
                source_rule=d.rule,
                source_domain="bible_audit",
                summary=f"[{d.severity.value.upper()}] {d.rule}: {d.message}",
                options=options,
            )
        )
    return proposals


