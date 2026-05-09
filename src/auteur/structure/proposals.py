from __future__ import annotations

from enum import Enum
from typing import Any
from datetime import datetime, timezone
import os
import re
from copy import deepcopy
import yaml

from pydantic import BaseModel, Field, model_validator
from auteur.blueprint import StoryBlueprint, CharacterRole


class ProposalType(str, Enum):
    GENERATION = "generation"
    REPAIR = "repair"


class ProposalOption(BaseModel):
    id: str = Field(min_length=1)
    summary: str = Field(min_length=1)
    tradeoffs: str = Field(min_length=1)
    data: dict[str, Any] = Field(
        description="A partial dictionary matching the StoryBlueprint structure."
    )


class ProposalSelection(BaseModel):
    selected_option_id: str = ""
    custom_data: dict[str, Any] = Field(default_factory=dict)


class ProposalDecision(BaseModel):
    selected_option_id: str = Field(min_length=1)
    custom_data: dict[str, Any] = Field(default_factory=dict)
    status: str = Field(default="accepted")
    author: str | None = None
    references: list[str] = Field(default_factory=list)
    accepted_at: datetime | None = None


class StructureProposal(BaseModel):
    proposal_id: str = Field(min_length=1)
    type: ProposalType
    source_rule: str | None = None
    summary: str = Field(min_length=1)
    options: list[ProposalOption] = Field(min_length=1)
    selection: ProposalSelection = Field(default_factory=ProposalSelection)
    decision: ProposalDecision | None = None

    @model_validator(mode="after")
    def validate_selection(self) -> "StructureProposal":
        option_ids = [option.id for option in self.options]

        if len(option_ids) != len(set(option_ids)):
            raise ValueError("StructureProposal options must have unique IDs")

        selected_option_id = self.selection.selected_option_id
        if selected_option_id and selected_option_id not in option_ids:
            raise ValueError(
                f"selected_option_id {selected_option_id!r} does not match any option ID"
            )

        return self

    def accept(
        self,
        selected_option_id: str,
        custom_data: dict[str, Any] | None = None,
        *,
        status: str = "accepted",
        author: str | None = None,
        references: list[str] | None = None,
    ) -> None:
        """Record an author's decision on this proposal.

        This updates the in-memory proposal artifact: selection and a decision
        metadata record. This should not itself mutate any blueprints.
        """
        option_ids = [o.id for o in self.options]
        if selected_option_id and selected_option_id not in option_ids:
            raise ValueError(f"selected_option_id {selected_option_id!r} does not match any option ID")

        self.selection.selected_option_id = selected_option_id
        self.selection.custom_data = custom_data or {}
        self.decision = ProposalDecision(
            selected_option_id=selected_option_id,
            custom_data=self.selection.custom_data,
            status=status,
            author=author,
            references=references or [],
            accepted_at=datetime.now(timezone.utc),
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


def _deep_merge(base: dict[str, Any], patch: dict[str, Any]) -> dict[str, Any]:
    for k, v in patch.items():
        if isinstance(v, dict) and isinstance(base.get(k), dict):
            base[k] = _deep_merge(base.get(k, {}), v)
        else:
            base[k] = v
    return base


def apply_proposal_to_blueprint(
    proposal: StructureProposal,
    blueprint: StoryBlueprint,
    *,
    output_dir: str | None = None,
    original_path: str | None = None,
    in_place: bool = False,
) -> tuple[StoryBlueprint, str]:
    """Materialize a proposal's selected option into a StoryBlueprint.

    Default behavior writes a new blueprint YAML file (and a small sidecar
    metadata file) into `output_dir` and returns (new_blueprint, path).
    In-place mutation requires `in_place=True` and an `original_path` to
    overwrite.
    """
    if not proposal.selection.selected_option_id:
        raise ValueError("No selected option to apply")

    # locate the selected option
    selected = None
    for opt in proposal.options:
        if opt.id == proposal.selection.selected_option_id:
            selected = opt
            break
    if selected is None:
        raise ValueError("Selected option not found in proposal options")

    # Prepare merged blueprint data
    base = deepcopy(blueprint.model_dump())
    patch = deepcopy(selected.data)
    merged = _deep_merge(base, patch)

    # validate the merged blueprint
    new_bp = StoryBlueprint.model_validate(merged)

    # determine output path
    out_dir = output_dir or os.getcwd()
    os.makedirs(out_dir, exist_ok=True)
    if in_place:
        if not original_path:
            raise ValueError("in_place=True requires original_path to overwrite")
        target_path = original_path
    else:
        safe_title = (
            blueprint.identity.title.replace(" ", "_").replace("/", "-")
            if getattr(blueprint.identity, "title", None)
            else "blueprint"
        )
        fname = f"{safe_title}_applied_{proposal.proposal_id}.yaml"
        target_path = os.path.join(out_dir, fname)

    # write blueprint YAML
    with open(target_path, "w", encoding="utf-8") as f:
        yaml.safe_dump(new_bp.model_dump(mode="json"), f, sort_keys=False)

    # write a sidecar provenance file rather than mutating the blueprint schema
    meta = {
        "applied_from_proposal": proposal.proposal_id,
        "applied_at": datetime.now(timezone.utc).isoformat(),
        "selected_option_id": proposal.selection.selected_option_id,
        "decision": proposal.decision.model_dump(mode="json") if proposal.decision else None,
    }
    meta_path = target_path + ".meta.yaml"
    with open(meta_path, "w", encoding="utf-8") as mf:
        yaml.safe_dump(meta, mf, sort_keys=False)

    return new_bp, target_path
