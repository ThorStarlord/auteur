"""Consequence analysis of one pending working revision: what it keeps, transforms and may displace.

An author about to apply a reviewed working revision can ask an explicitly invoked coding agent what the proposal does to
the creative concerns the Architecture already holds. The request is built from the exact pending review: the baseline
it would replace, the proposed candidate, the question changes the owner recorded, the question history and Working Book
decisions of each examined question, the author's instruction and any chosen alternative or discovery origin. Every
fact the agent may cite has an identifier, and the owner refuses an answer that cites anything else.

The answer is advisory. It is stored as a noncanonical record beside the Architecture and changes no Architecture,
review, Working Book or accepted record. Apply is never gated by it: a deliberately transformative revision is not
blocked. A deterministic comparison says what changed; only the agent says what that may mean, and the owner never judges
that two wordings mean the same thing or that a concern was intentionally abandoned.

An analysis is about the exact proposal it examined. Its standing is read at each projection, never stored: ``current``
while that proposal is still the pending review on the same baseline, ``applied`` once it has been applied, ``superseded``
when another revision has replaced it, and ``stale_context`` when the source or design guidance changed. Only ``current``
is presented as about the proposal on screen.
"""
from __future__ import annotations

import hashlib
import json
import re
import uuid
from typing import Annotated, Any, Literal

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator

from auteur.host_agent import (
    HostAgentRequest, _atomic_json_write, build_host_agent_request, load_host_agent_request, model_output_contract,
    validate_host_agent_response, write_host_agent_request, write_host_agent_response,
)
from auteur.series.working_book_architecture import book_elements, book_numbers, book_series_references

from . import studio_architecture as arch
from .studio_architecture_deliberation import _book_item, _history_for, deliberation_standing
from .studio_architecture_mechanisms import (
    MAX_BOOK_ELEMENTS, MAX_HISTORICAL_VERSIONS, MAX_MECHANISMS, PROVENANCE, PROVENANCE_MEANING, RELATION_MEANINGS, ROUTE_MEANING,
    book_element_candidates, mechanism_inventory, provenance_summary, relation_status, seed_node_identifiers,
)
from .studio_architecture_question_projection import project_architecture_questions
from .studio_architecture_questions import text_digest
from .studio_store import CanvasStore

SCHEMA = "studio-revision-consequence/1"
SCHEMA_V2 = "studio-revision-consequence/2"
SCHEMA_V3 = "studio-revision-consequence/3"
CONTRACT_VERSION = 3  # the answer contract a new analysis asks for; versions 1 and 2 are read unchanged
PACKET_VERSION = 3  # 3: question-linked Book elements (a class of examined questions) take reserved shares; 2 is unchanged
ROLE = "studio_architecture_consequence"
AUTHORITY = "noncanonical_consequence_analysis_not_working_architecture"

# Bounds. Every limit the answer must respect is a named constant here, and the instruction is generated from them.
MAX_CONCERNS = 6
MAX_PROSPECTIVE = 4
MAX_ALTERNATIVES = 4
MAX_EVIDENCE_PER_CONCERN = 6
MAX_EXAMINED_QUESTIONS = 4
MAX_BOOK_DECISIONS = 4
MAX_COMPONENTS = 10
MAX_PHASES = 10
MAX_BOOK_TITLES = 12
MAX_CONSTRAINTS = 6
MAX_COUNTEREVIDENCE = 3
MAX_NOT_ESTABLISHED = 6
MAX_HISTORY = 8
INSTRUCTION_LIMIT = 1200
VISION_LIMIT = 800
TEXT_LIMIT = 600
REASON_LIMIT = 400
DISCOVERY_LIMIT = 600
READING_LIMIT = 900
CONCERN_TITLE_LIMIT = 120
CONCERN_READING_LIMIT = 600
CONCERN_SIDE_LIMIT = 400
COUNTER_LIMIT = 240
PROSPECT_LIMIT = 500
APPROACH_TITLE_LIMIT = 120
APPROACH_SUMMARY_LIMIT = 500
APPROACH_GAINS_LIMIT = 300
APPROACH_COSTS_LIMIT = 300
NEXT_LIMIT = 300
NOT_ESTABLISHED_LIMIT = 240
NO_CONCERN_LIMIT = 400
ITEM_LIMIT = 240
# Version 2: recorded mechanisms, inheritance and trajectories.
MAX_MECHANISM_READINGS = 6
MAX_INHERITANCE = 6
MAX_TRAJECTORIES = 3
MAX_TRAJECTORY_STEPS = 5
MAX_TRAJECTORY_ASSUMPTIONS = 3
MAX_MECHANISM_COUNTEREVIDENCE = 3
MAX_MECHANISM_UNRESOLVED = 3
MAX_ALTERNATIVE_MECHANISMS = 4
MAX_KEEPS = 3
READING_ITEM_LIMIT = 400
TRANSFORMATION_LIMIT = 400
CONSEQUENCE_LIMIT = 400
INHERITANCE_TEXT_LIMIT = 400
STEP_TEXT_LIMIT = 300
TRAJECTORY_TITLE_LIMIT = 120
COMPARISON_LIMIT = 200
ASSUMPTION_LIMIT = 240
KEEPS_LIMIT = 3

ConcernStatus = Literal["preserved", "transformed", "possibly_displaced", "introduced"]
IntentBasis = Literal["instruction_names_it", "selected_alternative_names_it", "not_established"]
Approach = Literal["replace", "integrate", "separate", "retain", "defer", "reframe"]
ApproachV2 = Literal["keep_baseline", "accept_proposal", "replace", "integrate", "separate", "defer", "reframe"]
ProspectKind = Literal["recorded_relationship", "proposed_possibility"]
ReachKind = Literal["local", "conditional_inheritance", "long_horizon", "not_established"]
InheritanceKind = Literal["recorded_inheritance", "plausible_inheritance", "proposed_inheritance", "unknown_inheritance"]
TrajectoryStage = Literal["local_decision", "mechanism_transformation", "tension", "opportunity", "inheritance", "long_horizon"]
StepBasis = Literal["recorded", "interpreted", "speculative"]

# Shared vocabulary: the instruction, the owner's checks and the served page read these same tables.
APPROACH_MEANINGS: dict[str, str] = {
    "keep_baseline": "Keep the earlier concern as recorded: its baseline wording and role stay in play, and the proposal's change "
                     "to it is not adopted. keeps cites the baseline wording of the named questions.",
    "accept_proposal": "Accept the proposal as written for the named questions, including any displacement it causes. The "
                       "displacement is recorded as accepted, not resolved. keeps cites proposal-side items (proposed wording or "
                       "a removal).",
    "replace": "Put a different formulation in place of the earlier concern. A new question is described in the summary; it is "
               "not given an identity. keeps cites the wording of the question replaced.",
    "integrate": "Hold two or three named concerns in one development, answered together. The summary says what the combined "
                 "development gives up. keeps cites the wording of each named question.",
    "separate": "Split a concern into parts developed independently. The parts keep the named questions; a distinct new question is "
                "described, not given an identity. keeps cites the wording of the question split.",
    "defer": "Postpone reconsideration and name the evidence or Book that would settle it. The named questions keep their current "
             "wording. keeps cites their wording.",
    "reframe": "Restate the creative problem at another level, keeping the named questions' identities. The restatement is in the "
               "summary. keeps cites the wording of the named questions.",
}
RETAIN_LEGACY_MEANING = ("Version 1 analyses used this name for both keeping the earlier concern and accepting a retirement. "
                         "Its meaning is not fixed by that analysis and is not reinterpreted here.")
REACH_MEANINGS: dict[str, str] = {
    "local": "The change stays within the Architecture and the examined questions; no later development is recorded or proposed.",
    "conditional_inheritance": "A later Book may receive the change, but only through the cited inheritance; the inheritance is "
                               "conditional on the author's decision.",
    "long_horizon": "A later development may depend on the change. At least one trajectory step is a long-horizon or inheritance "
                    "step. Every such step is hypothetical unless it cites a recorded item.",
    "not_established": "The records do not show whether the change reaches later development.",
}
INHERITANCE_MEANINGS: dict[str, str] = {
    "recorded_inheritance": "A later Book's own inherited element cites the earlier development.",
    "plausible_inheritance": "A later Book's element or decision cites the earlier development; whether the Book carries it is an "
                             "interpretation.",
    "proposed_inheritance": "A relationship the agent suggests the author construct. It is not recorded.",
    "unknown_inheritance": "The records do not establish whether the later Book carries the earlier concern.",
}
# Version 3: alternatives anchored on a question, a mechanism or both; relations between two mechanisms, checked against the graph.
MAX_V3_ANCHORS = 3
MAX_CONNECTIONS = 4
MAX_CONNECTION_ASSUMPTIONS = 3
MAX_CONNECTION_COUNTEREVIDENCE = 2
CONNECTION_TEXT_LIMIT = 400
CONNECTION_REASON_LIMIT = 400
CONNECTION_ITEM_LIMIT = 240
ApproachV3 = Literal["keep_baseline", "accept_proposal", "replace", "integrate", "separate", "defer", "reframe", "retire"]
ConnectionStanding = Literal["recorded", "inferred", "hypothetical", "unestablished"]
ConnectionBasis = Literal["graph_miss", "competing_readings", "incomplete_evidence", "productive_independence"]

APPROACH_MEANINGS_V3: dict[str, str] = {
    "keep_baseline": "Keep the earlier concern as recorded: its baseline wording or record stays in play, and the proposal's change to it "
                     "is not adopted. keeps cites the baseline wording of each named question and the baseline record of each named "
                     "mechanism.",
    "accept_proposal": "Accept the proposal as written for the named questions and mechanisms, including any displacement it causes. The "
                       "displacement is recorded as accepted, not resolved. keeps cites the proposed side of each anchor: the proposed "
                       "wording or removal of a question, and the proposed record of a mechanism.",
    "replace": "Put a different formulation or mechanism in place of the earlier one. A new question or mechanism is described in the "
               "summary; it is not given an identity. keeps cites the baseline wording or record of each anchor.",
    "integrate": "Hold two or three named concerns or mechanisms in one development, answered together. The summary says what the "
                 "combined development gives up. keeps cites the baseline wording or record of each anchor.",
    "separate": "Split a concern or mechanism into parts developed independently. The parts keep the named anchors; a distinct new "
                "question or mechanism is described, not given an identity. keeps cites the baseline wording or record of each anchor.",
    "defer": "Postpone reconsideration and name the evidence or Book that would settle it. The named anchors keep their current form. "
             "keeps cites their baseline wording or record.",
    "reframe": "Restate the creative problem at another level, keeping the named anchors' identities. The restatement is in the summary. "
               "keeps cites the baseline wording or record of each anchor.",
    "retire": "Deliberately give up a named mechanism or question as part of the story: its recorded role is not carried forward. The "
              "summary says what is lost and what, if anything, takes its place. keeps cites the baseline wording or record of each "
              "anchor.",
}
CONNECTION_MEANINGS: dict[str, str] = {
    "recorded": "The Architecture records a joining link or interaction, or a shared node, between the two mechanisms. The owner checks "
                "this against the candidates and stores what it found beside the standing.",
    "inferred": "Not recorded. The agent infers the connection from the packet's evidence; the reasoning and the assumptions are the "
                "agent's interpretation.",
    "hypothetical": "Not recorded and not established. A creative possibility worth developing, with what it would need to hold.",
    "unestablished": "The evidence does not warrant a conclusion. The basis says why. graph_miss means only that this Architecture records "
                     "no connection between them, never that the story has none.",
}
CONNECTION_BASIS_MEANINGS: dict[str, str] = {
    "graph_miss": "The Architecture records no joining link or shared node between the two mechanisms, checked by the owner. This is "
                  "not a claim about the story.",
    "competing_readings": "The evidence supports more than one reading of how the two relate, and none is preferred.",
    "incomplete_evidence": "The evidence the packet gives does not settle whether they relate.",
    "productive_independence": "They may be better understood as independent: keeping them apart may be the stronger development.",
}
_V3_EARLIER_PROVENANCE = {"preserved", "transformed", "removed"}
_V3_PROPOSED_PROVENANCE = {"preserved", "transformed", "introduced", "removed"}

TRAJECTORY_STATUS = "hypothetical"
_EARLIER_KINDS = {"baseline_wording", "recorded_history", "book_decision"}
_EARLIER_PROVENANCE = {"preserved", "transformed", "removed", "historical"}
_PROPOSED_KINDS = {"proposed_wording", "proposed_component", "removed"}
_PROPOSED_PROVENANCE = {"transformed", "introduced", "removed"}
_QUESTION_KINDS = {"baseline_wording", "recorded_history", "book_decision", "proposed_wording", "removed"}

EvidenceId = Annotated[str, StringConstraints(pattern=r"^E[1-9][0-9]{0,2}$")]
QuestionId = Annotated[str, StringConstraints(min_length=1, max_length=80)]
ItemText = Annotated[str, StringConstraints(min_length=1, max_length=COUNTER_LIMIT)]

_SYSTEM = f"""You are the active Auteur consequence-analysis agent. The author is considering a proposed working revision of
the narrative Architecture. The revision has been reviewed but NOT applied. Your task is to help the author understand what
the proposal accomplishes; which earlier creative concerns it keeps, transforms or may displace; what it may make possible or
require reconsidering in later Books; and which developable alternatives exist. You are not judging whether the proposal is
right. Deliberate transformation is legitimate: a concern may be replaced, separated, combined or abandoned on purpose. Do not
presume that preserving every earlier concern is better, and do not presume that integration is better than separation.

Read the baseline candidate (the applied working Architecture), the proposed candidate (the un-applied revision) and the
consequence packet. The packet's evidence list gives items E1, E2 and so on. Each is a fact the owners recorded, or a
deterministic comparison of the two candidates. Cite evidence only by these identifiers. Keep apart what the record shows
(cite it), what you interpret (say so) and what the record cannot establish (say so in not_established). A changed wording does
not prove a changed meaning, and an unchanged identity does not prove an unchanged concern. A book_decision whose
proposal_status is not unchanged refers to a question the proposal changes: that is a recorded relationship by identity, not a
demonstrated contradiction. A Working Book the coverage note lists only by title was not read for its decisions, and that is not
evidence that it is unaffected. A named_gap is missing history: never fill it in.

Return ONLY a JSON object with these keys:
- schema_version: 1
- reading: what the proposal accomplishes and what it changes, in plain words. Required, at most {READING_LIMIT} characters.
- concerns: 0 to {MAX_CONCERNS} objects. Each has title (at most {CONCERN_TITLE_LIMIT} characters); status, one of preserved,
  transformed, possibly_displaced or introduced; earlier and proposed (optional, at most {CONCERN_SIDE_LIMIT} characters each: how
  the concern was formulated before and how the proposal formulates or displaces it); reading (required, at most
  {CONCERN_READING_LIMIT} characters); evidence (1 to {MAX_EVIDENCE_PER_CONCERN} identifiers); intent (required for transformed and
  possibly_displaced: instruction_names_it, selected_alternative_names_it or not_established; instruction_names_it must cite the
  instruction item, and selected_alternative_names_it must cite the selected_alternative item; never assert an intent the evidence
  does not show; omit intent for preserved and introduced); counterevidence (0 to {MAX_COUNTEREVIDENCE} strings, each at most
  {COUNTER_LIMIT} characters); competing_reading (optional, at most {CONCERN_SIDE_LIMIT} characters).
  Status meanings: preserved, the concern is still represented; transformed, it is still in play but its formulation or function has
  changed; possibly_displaced, it may no longer be represented or may need separate consideration, and the record may not establish
  whether that was intended; introduced, a new uncertainty, tension or opportunity the proposal brings. A concern is never given a new
  identity by you.
- no_concern_reason: required when concerns is empty (at most {NO_CONCERN_LIMIT} characters): say why no concern is consequential. Do
  not produce repetitive assessments for trivial wording changes.
Evidence rules, enforced exactly as written. Cite only the items that bear on the concern, and cite each kind of item it needs:
preserved needs at least one cited item; introduced needs at least one proposed_wording or proposed_component item;
possibly_displaced needs at least one baseline_wording, recorded_history or book_decision item; transformed needs at least one
earlier-side item (baseline_wording, recorded_history or book_decision) AND at least one proposed-side item (proposed_wording,
proposed_component or removed). Concern titles are distinct from one another. An alternative names two or three distinct question
ids, each one of baseline_question_ids, and its title is distinct from the other alternatives' titles.
- prospective: 0 to {MAX_PROSPECTIVE} objects. Each has kind, recorded_relationship (must cite a book_decision or recorded_history
  item) or proposed_possibility; text (at most {PROSPECT_LIMIT} characters); evidence (0 to 4 identifiers).
- alternatives: 0 to {MAX_ALTERNATIVES} objects. Each has approach, one of replace, integrate, separate, retain, defer or reframe;
  title (at most {APPROACH_TITLE_LIMIT} characters); summary (at most {APPROACH_SUMMARY_LIMIT} characters); questions (two or three
  question ids, each one of the baseline_question_ids the packet lists); gains (at most {APPROACH_GAINS_LIMIT} characters); costs
  (at most {APPROACH_COSTS_LIMIT} characters); next_investigation (at most {NEXT_LIMIT} characters). Every approach states its costs as
  well as its gains. Name what each approach keeps, and for separate, name the questions it keeps: a distinct question it would
  introduce is described in the summary and is not given an identity. If you recommend one approach, say why it is stronger than the
  others here.
- not_established: 0 to {MAX_NOT_ESTABLISHED} strings, each at most {NOT_ESTABLISHED_LIMIT} characters.

Use only the evidence identifiers and question ids the packet gives. Do not invent narrative facts, Book content or future events.
A proposed_possibility and an alternative are the only places for speculation, and each must be labelled as such. Never state or imply
that the proposal is accepted, applied or canonical, and never say that a Working Book has been changed by this analysis."""


class ConsequenceConcern(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    title: str = Field(min_length=1, max_length=CONCERN_TITLE_LIMIT)
    status: ConcernStatus
    earlier: str | None = Field(default=None, max_length=CONCERN_SIDE_LIMIT)
    proposed: str | None = Field(default=None, max_length=CONCERN_SIDE_LIMIT)
    reading: str = Field(min_length=1, max_length=CONCERN_READING_LIMIT)
    evidence: list[EvidenceId] = Field(min_length=1, max_length=MAX_EVIDENCE_PER_CONCERN)
    intent: IntentBasis | None = None
    counterevidence: list[ItemText] = Field(default_factory=list, max_length=MAX_COUNTEREVIDENCE)
    competing_reading: str | None = Field(default=None, max_length=CONCERN_SIDE_LIMIT)

    @model_validator(mode="after")
    def intent_only_where_it_is_asked(self) -> "ConsequenceConcern":
        if self.status in ("transformed", "possibly_displaced") and self.intent is None:
            raise ValueError("a transformed or possibly displaced concern states its intent basis")
        if self.status in ("preserved", "introduced") and self.intent is not None:
            raise ValueError("intent applies only to a transformed or possibly displaced concern")
        return self


class ConsequenceProspect(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    kind: ProspectKind
    text: str = Field(min_length=1, max_length=PROSPECT_LIMIT)
    evidence: list[EvidenceId] = Field(default_factory=list, max_length=4)


class ConsequenceAlternative(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    approach: Approach
    title: str = Field(min_length=1, max_length=APPROACH_TITLE_LIMIT)
    summary: str = Field(min_length=1, max_length=APPROACH_SUMMARY_LIMIT)
    questions: list[QuestionId] = Field(min_length=2, max_length=3)
    gains: str = Field(min_length=1, max_length=APPROACH_GAINS_LIMIT)
    costs: str = Field(min_length=1, max_length=APPROACH_COSTS_LIMIT)
    next_investigation: str = Field(min_length=1, max_length=NEXT_LIMIT)

    @model_validator(mode="after")
    def distinct_questions(self) -> "ConsequenceAlternative":
        if len(set(self.questions)) != len(self.questions):
            raise ValueError("an alternative names each question once")
        return self


class ConsequenceAnswer(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    schema_version: Literal[1]
    reading: str = Field(min_length=1, max_length=READING_LIMIT)
    concerns: list[ConsequenceConcern] = Field(default_factory=list, max_length=MAX_CONCERNS)
    no_concern_reason: str | None = Field(default=None, max_length=NO_CONCERN_LIMIT)
    prospective: list[ConsequenceProspect] = Field(default_factory=list, max_length=MAX_PROSPECTIVE)
    alternatives: list[ConsequenceAlternative] = Field(default_factory=list, max_length=MAX_ALTERNATIVES)
    not_established: list[str] = Field(default_factory=list, max_length=MAX_NOT_ESTABLISHED)

    @model_validator(mode="after")
    def empty_concerns_say_why(self) -> "ConsequenceAnswer":
        if not self.concerns and not (self.no_concern_reason or "").strip():
            raise ValueError("an analysis with no concern must say why in no_concern_reason")
        for text in self.not_established:
            if not text.strip() or len(text) > NOT_ESTABLISHED_LIMIT:
                raise ValueError(f"each not_established item is text under {NOT_ESTABLISHED_LIMIT} characters")
        return self


class MechanismCounterevidence(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    text: ItemText
    evidence: list[EvidenceId] = Field(min_length=1, max_length=3)


class MechanismReading(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    evidence: EvidenceId
    reading: str = Field(min_length=1, max_length=READING_ITEM_LIMIT)
    transformation: str | None = Field(default=None, max_length=TRANSFORMATION_LIMIT)
    conditional_consequence: str | None = Field(default=None, max_length=CONSEQUENCE_LIMIT)
    counterevidence: list[MechanismCounterevidence] = Field(default_factory=list, max_length=MAX_MECHANISM_COUNTEREVIDENCE)
    unresolved: list[ItemText] = Field(default_factory=list, max_length=MAX_MECHANISM_UNRESOLVED)


class InheritanceItem(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, populate_by_name=True)
    kind: InheritanceKind
    from_: EvidenceId = Field(alias="from")
    to: EvidenceId
    text: str = Field(min_length=1, max_length=INHERITANCE_TEXT_LIMIT)
    evidence: list[EvidenceId] = Field(default_factory=list, max_length=4)


class TrajectoryStep(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    stage: TrajectoryStage
    text: str = Field(min_length=1, max_length=STEP_TEXT_LIMIT)
    evidence: list[EvidenceId] = Field(default_factory=list, max_length=3)
    basis: StepBasis


class TrajectoryComparison(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    creative_gain: str | None = Field(default=None, max_length=COMPARISON_LIMIT)
    narrative_cost: str | None = Field(default=None, max_length=COMPARISON_LIMIT)
    contrivance_risk: str | None = Field(default=None, max_length=COMPARISON_LIMIT)
    future_commitment: str | None = Field(default=None, max_length=COMPARISON_LIMIT)
    flexibility: str | None = Field(default=None, max_length=COMPARISON_LIMIT)


class Trajectory(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    title: str = Field(min_length=1, max_length=TRAJECTORY_TITLE_LIMIT)
    steps: list[TrajectoryStep] = Field(min_length=2, max_length=MAX_TRAJECTORY_STEPS)
    assumptions: list[ItemText] = Field(default_factory=list, max_length=MAX_TRAJECTORY_ASSUMPTIONS)
    comparison: TrajectoryComparison | None = None


class AlternativeV2(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    approach: ApproachV2
    title: str = Field(min_length=1, max_length=APPROACH_TITLE_LIMIT)
    summary: str = Field(min_length=1, max_length=APPROACH_SUMMARY_LIMIT)
    questions: list[QuestionId] = Field(min_length=1, max_length=3)
    keeps: list[EvidenceId] = Field(min_length=1, max_length=MAX_KEEPS)
    mechanisms: list[EvidenceId] = Field(default_factory=list, max_length=MAX_ALTERNATIVE_MECHANISMS)
    gains: str = Field(min_length=1, max_length=APPROACH_GAINS_LIMIT)
    costs: str = Field(min_length=1, max_length=APPROACH_COSTS_LIMIT)
    next_investigation: str = Field(min_length=1, max_length=NEXT_LIMIT)

    @model_validator(mode="after")
    def distinct_questions(self) -> "AlternativeV2":
        if len(set(self.questions)) != len(self.questions):
            raise ValueError("an alternative names each question once")
        if len(set(self.keeps)) != len(self.keeps) or len(set(self.mechanisms)) != len(self.mechanisms):
            raise ValueError("an alternative cites each item once")
        return self


class ConsequenceAnswerV2(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    schema_version: Literal[2]
    reading: str = Field(min_length=1, max_length=READING_LIMIT)
    reach: ReachKind
    concerns: list[ConsequenceConcern] = Field(default_factory=list, max_length=MAX_CONCERNS)
    no_concern_reason: str | None = Field(default=None, max_length=NO_CONCERN_LIMIT)
    mechanisms: list[MechanismReading] = Field(default_factory=list, max_length=MAX_MECHANISM_READINGS)
    inheritance: list[InheritanceItem] = Field(default_factory=list, max_length=MAX_INHERITANCE)
    trajectories: list[Trajectory] = Field(default_factory=list, max_length=MAX_TRAJECTORIES)
    alternatives: list[AlternativeV2] = Field(default_factory=list, max_length=MAX_ALTERNATIVES)
    not_established: list[str] = Field(default_factory=list, max_length=MAX_NOT_ESTABLISHED)

    @model_validator(mode="after")
    def empty_concerns_say_why(self) -> "ConsequenceAnswerV2":
        if not self.concerns and not (self.no_concern_reason or "").strip():
            raise ValueError("an analysis with no concern must say why in no_concern_reason")
        for text in self.not_established:
            if not text.strip() or len(text) > NOT_ESTABLISHED_LIMIT:
                raise ValueError(f"each not_established item is text under {NOT_ESTABLISHED_LIMIT} characters")
        return self


class AlternativeV3(BaseModel):
    """An alternative anchored on a continuing question, a current mechanism, or both. It needs no question to exist."""
    model_config = ConfigDict(extra="forbid", strict=True)
    approach: ApproachV3
    title: str = Field(min_length=1, max_length=APPROACH_TITLE_LIMIT)
    summary: str = Field(min_length=1, max_length=APPROACH_SUMMARY_LIMIT)
    questions: list[QuestionId] = Field(default_factory=list, max_length=3)
    mechanisms: list[EvidenceId] = Field(default_factory=list, max_length=3)
    keeps: list[EvidenceId] = Field(min_length=1, max_length=MAX_V3_ANCHORS)
    gains: str = Field(min_length=1, max_length=APPROACH_GAINS_LIMIT)
    costs: str = Field(min_length=1, max_length=APPROACH_COSTS_LIMIT)
    next_investigation: str = Field(min_length=1, max_length=NEXT_LIMIT)

    @model_validator(mode="after")
    def anchored_and_distinct(self) -> "AlternativeV3":
        if not self.questions and not self.mechanisms:
            raise ValueError("an alternative names at least one question or mechanism it concerns")
        if len(self.questions) + len(self.mechanisms) > MAX_V3_ANCHORS:
            raise ValueError("an alternative names at most three anchors in all, because an investigation takes no more")
        if len(set(self.questions)) != len(self.questions) or len(set(self.mechanisms)) != len(self.mechanisms):
            raise ValueError("an alternative names each question and each mechanism once")
        if len(set(self.keeps)) != len(self.keeps):
            raise ValueError("an alternative cites each item once")
        return self


class MechanismConnection(BaseModel):
    """A relation between two recorded mechanisms, with the standing the agent gives it. The owner checks the graph separately."""
    model_config = ConfigDict(extra="forbid", strict=True)
    between: list[EvidenceId] = Field(min_length=2, max_length=2)
    standing: ConnectionStanding
    text: str = Field(min_length=1, max_length=CONNECTION_TEXT_LIMIT)
    reasoning: str | None = Field(default=None, max_length=CONNECTION_REASON_LIMIT)
    worth_developing: str | None = Field(default=None, max_length=CONNECTION_REASON_LIMIT)
    basis: ConnectionBasis | None = None
    assumptions: list[ItemText] = Field(default_factory=list, max_length=MAX_CONNECTION_ASSUMPTIONS)
    counterevidence: list[ItemText] = Field(default_factory=list, max_length=MAX_CONNECTION_COUNTEREVIDENCE)
    evidence: list[EvidenceId] = Field(default_factory=list, max_length=4)

    @model_validator(mode="after")
    def standing_states_its_basis(self) -> "MechanismConnection":
        if len(set(self.between)) != 2:
            raise ValueError("a connection relates two distinct mechanisms")
        if self.standing == "inferred":
            if not (self.reasoning or "").strip():
                raise ValueError("an inferred connection states its reasoning")
            if not self.assumptions:
                raise ValueError("an inferred connection states at least one assumption")
        if self.standing == "hypothetical":
            if not (self.worth_developing or "").strip():
                raise ValueError("a hypothetical connection says what makes it worth developing (worth_developing)")
            if not self.assumptions:
                raise ValueError("a hypothetical connection states at least one assumption")
        if self.standing == "unestablished" and self.basis is None:
            raise ValueError("an unestablished connection states its basis")
        if self.standing != "unestablished" and self.basis is not None:
            raise ValueError("a basis is stated only for an unestablished connection")
        if self.standing != "inferred" and self.reasoning is not None:
            raise ValueError("reasoning is stated only for an inferred connection")
        if self.standing != "hypothetical" and self.worth_developing is not None:
            raise ValueError("worth_developing is stated only for a hypothetical connection")
        return self


class ConsequenceAnswerV3(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    schema_version: Literal[3]
    reading: str = Field(min_length=1, max_length=READING_LIMIT)
    reach: ReachKind
    concerns: list[ConsequenceConcern] = Field(default_factory=list, max_length=MAX_CONCERNS)
    no_concern_reason: str | None = Field(default=None, max_length=NO_CONCERN_LIMIT)
    mechanisms: list[MechanismReading] = Field(default_factory=list, max_length=MAX_MECHANISM_READINGS)
    inheritance: list[InheritanceItem] = Field(default_factory=list, max_length=MAX_INHERITANCE)
    trajectories: list[Trajectory] = Field(default_factory=list, max_length=MAX_TRAJECTORIES)
    alternatives: list[AlternativeV3] = Field(default_factory=list, max_length=MAX_ALTERNATIVES)
    connections: list[MechanismConnection] = Field(default_factory=list, max_length=MAX_CONNECTIONS)
    not_established: list[str] = Field(default_factory=list, max_length=MAX_NOT_ESTABLISHED)

    @model_validator(mode="after")
    def empty_concerns_say_why(self) -> "ConsequenceAnswerV3":
        if not self.concerns and not (self.no_concern_reason or "").strip():
            raise ValueError("an analysis with no concern must say why in no_concern_reason")
        for text in self.not_established:
            if not text.strip() or len(text) > NOT_ESTABLISHED_LIMIT:
                raise ValueError(f"each not_established item is text under {NOT_ESTABLISHED_LIMIT} characters")
        return self


def _clip(text: Any, limit: int = TEXT_LIMIT) -> str | None:
    if text is None:
        return None
    text = str(text)
    return text if len(text) <= limit else text[: limit - 1] + "…"


def _digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()


def _root(store: CanvasStore):
    return arch._root(store) / "consequences"


def _discovery_possibility(store: CanvasStore, origin: dict) -> dict | None:
    """The possibility a discovery origin names, read from its completed discovery result (text only; never judged)."""
    sha = origin.get("request_sha256")
    if not isinstance(sha, str):
        return None
    result = arch._read(arch._root(store) / "discoveries" / "requests" / sha / "result.json") or {}
    return next((row for row in result.get("possibilities", []) if row.get("id") == origin.get("possibility_id")), None)


def build_consequence_packet(store: CanvasStore, review: dict[str, Any], baseline: dict[str, Any]) -> dict[str, Any]:
    """The bounded, ID-cited evidence for one pending revision. Read-only; raises ValueError when no baseline is readable.

    The packet names each fact it gives the agent. A question's history and Book decisions come from the same owner reads
    the deliberation uses; ``proposal_status`` on a Book decision is the deterministic change of its question in the
    proposal (an identity fact), never a judgement of meaning.
    """
    proposed = review["candidate"]
    view = project_architecture_questions(store)
    if not view["available"]:
        raise ValueError("no current working architecture")
    continuing = {question["id"]: question for question in view["questions"] if question["standing"] == "continuing"}
    changes = review.get("question_changes") or {}
    rows = {row["id"]: row for row in changes.get("questions", []) if row.get("id")}
    removed = {row["id"]: row for row in changes.get("removed", [])}
    chosen = review.get("selected_creative_alternative") or {}
    considered = [row["id"] for row in chosen.get("considered_questions") or []]

    # What is examined first: a deliberate removal, then rewordings and introductions, then the questions the instruction
    # considered. A question that moved only in position is not a change of wording, and a removal or introduction shifts the
    # positions of later questions: those shifts must not crowd the change itself out of the examined set.
    changed = list(removed) + [identifier for identifier, row in rows.items()
                               if row["status"] in ("reworded", "moved_and_reworded", "introduced")]
    examined = list(dict.fromkeys(changed + [identifier for identifier in considered]))
    questions_omitted = max(0, len(examined) - MAX_EXAMINED_QUESTIONS)
    examined = examined[:MAX_EXAMINED_QUESTIONS]

    evidence: list[dict[str, Any]] = []

    def add(kind: str, text: Any, limit: int = TEXT_LIMIT, **fields: Any) -> str:
        identifier = f"E{len(evidence) + 1}"
        evidence.append({"id": identifier, "kind": kind, "text": _clip(text, limit), **fields})
        return identifier

    requested = str(review.get("requested_change") or "")
    if requested.strip():
        add("instruction", requested, INSTRUCTION_LIMIT, sha256=text_digest(requested))
    if chosen:
        add("selected_alternative",
            f"{chosen.get('title', '')}. {chosen.get('description', '')}", TEXT_LIMIT,
            hypothesis_id=chosen.get("hypothesis_id"), inquiry_request_sha256=chosen.get("inquiry_request_sha256"),
            considered_questions=considered)
    origin = chosen.get("from_discovery")
    if isinstance(origin, dict):
        possibility = _discovery_possibility(store, origin) or {}
        add("discovery_origin",
            f"{origin.get('title', '')}. {possibility.get('possibility', '')}", DISCOVERY_LIMIT,
            request_sha256=origin.get("request_sha256"), possibility_id=origin.get("possibility_id"),
            questions=possibility.get("questions", []))
    vision = next((item.content for item in store.load().items if item.id == "story-vision"), "")
    if vision and vision.strip():
        add("author_vision", vision, VISION_LIMIT)
    preserved = review.get("preserved") or {}
    constraints = list(preserved.get("accepted_constraints") or [])
    not_this = list(preserved.get("accepted_not_this") or [])
    for text in constraints[:MAX_CONSTRAINTS]:
        add("accepted_constraint", text, ITEM_LIMIT)
    for text in not_this[:MAX_CONSTRAINTS]:
        add("accepted_not_this", text, ITEM_LIMIT)

    examined_books: set[int] = set()
    examined_rows = []
    for identifier in examined:
        status = rows[identifier]["status"] if identifier in rows else (
            "removed" if identifier in removed else "not_in_proposal")
        baseline_question = continuing.get(identifier)
        row_view: dict[str, Any] = {"id": identifier, "proposal_status": status, "baseline_evidence": [],
                                    "proposed_evidence": [], "history_items_omitted": 0, "book_decisions_omitted": 0}
        if baseline_question is not None:
            wording = add("baseline_wording", baseline_question["text"], question_id=identifier,
                          index=baseline_question["index"])
            row_view["baseline_evidence"].append(wording)
            history, omitted_history = _history_for(baseline_question)
            row_view["history_items_omitted"] = omitted_history
            for item in history:
                if item.get("basis") == "named_gap":
                    # An unreadable version is said to be unreadable, never left as an empty item.
                    add("named_gap", item.get("note") or item.get("gap") or
                        "A recorded version of this question cannot be read, so its wording is not shown.",
                        question_id=identifier, gap=item.get("gap") or "unreadable_version")
                    continue
                reason = item.get("reason") or {}
                label = item.get("text")
                if label is None and item.get("kind") == "absent":
                    label = "The question was not recorded in this version."
                # The owner's reason item carries the author's instruction under "instruction" (or a named gap with no instruction).
                row_view["baseline_evidence"].append(add(
                    "recorded_history", label, question_id=identifier, basis=item.get("basis"),
                    change=item.get("change"), from_revision=item.get("from_revision"), to_revision=item.get("to_revision"),
                    recorded_reason=reason.get("instruction"),
                    selected_alternative=(reason.get("selected_alternative") or {}).get("title"),
                    note=reason.get("note") or item.get("note")))
            entries = sorted(baseline_question["books"], key=lambda entry: (entry["book_number"], entry["decision_id"]))
            # Every Book that records a decision on an examined question was read for it, even when its decision is beyond the
            # display limit, which is counted and not shown.
            examined_books.update(entry["book_number"] for entry in entries)
            shown = entries[:MAX_BOOK_DECISIONS]
            row_view["book_decisions_omitted"] = max(0, len(entries) - len(shown))
            book_rows = [_book_item(entry) for entry in shown]
            standing = {(row["book_number"], row["decision_id"]): row["standing"] for row in deliberation_standing(
                store, {"questions": [{"id": identifier, "books": book_rows}]})}
            for book in book_rows:
                row_view["baseline_evidence"].append(add(
                    "book_decision", book.get("decision_text") or "", question_id=identifier,
                    book_number=book["book_number"], title=book["title"], decision_id=book["decision_id"],
                    state=book["state"], identity_basis=book["identity_basis"],
                    standing=standing.get((book["book_number"], book["decision_id"])),
                    recorded_text=(book["recorded"] or {}).get("text"),
                    current_text=(book["current"] or {}).get("text") if book.get("current") else None,
                    proposal_status=status))
        if identifier in rows:
            row = rows[identifier]
            row_view["proposed_evidence"].append(add(
                "proposed_wording", row["text"], question_id=identifier, index=row["index"],
                proposal_status=status, previous_text=row.get("previous_text")))
        if identifier in removed:
            row_view["proposed_evidence"].append(add(
                "removed", removed[identifier]["previous_text"], question_id=identifier, proposal_status="removed"))
        examined_rows.append(row_view)

    components = list(review.get("changed_components") or [])
    for component in components[:MAX_COMPONENTS]:
        add("proposed_component",
            f"{component.get('kind')} · {component.get('title')} ({component.get('change')}): "
            f"{component.get('before')} -> {component.get('after')}",
            component_kind=component.get("kind"), component_id=component.get("id"))

    phases = list((baseline.get("phases") or []))
    for phase in phases[:MAX_PHASES]:
        add("recorded_phase", f"{phase.get('order')}. {phase.get('title')}: {phase.get('narrative_function')}",
            phase_id=phase.get("id"))

    unreadable_books = [row["book_number"] for row in view["books"]["unreadable"]]
    for number in unreadable_books:
        add("named_gap", f"Working Book {number} cannot be read, so its references are not shown.",
            gap="book_unreadable", book_number=number)
    readable_books = []
    book_node_refs: dict[int, list[str]] = {}
    book_rows: dict[int, list[dict]] = {}
    for number in book_numbers(store):
        if number in unreadable_books:
            continue
        try:
            read = book_series_references(store, number)
            rows = book_elements(store, number)
        except Exception:  # noqa: BLE001 - one Book's damage is reported for that Book only
            add("named_gap", f"Working Book {number} cannot be read, so its references are not shown.",
                gap="book_unreadable", book_number=number)
            continue
        readable_books.append((number, read["title"]))
        book_node_refs[number] = [row["node_id"] for row in read["references"]]
        book_rows[number] = rows
    for number, title in readable_books[:MAX_BOOK_TITLES]:
        add("working_book", f"Book {number}: {title}", book_number=number,
            records_examined_decisions=number in examined_books)
    if not view["history"]["chain_complete"]:
        add("named_gap", "The revision history cannot be read whole, so no earlier version is numbered.",
            gap="chain_incomplete")

    # Version 2: the recorded mechanisms and the Working Book elements that cite them. Appended after the v1 evidence, so every
    # earlier identifier keeps its meaning. Each record is named by its provenance against the exact candidates it came from.
    book_nodes: dict[str, list[int]] = {}
    for number, node_ids in book_node_refs.items():
        for node_id in node_ids:
            book_nodes.setdefault(node_id, []).append(number)
    earlier_versions = [(sha, candidate) for sha, candidate in
                        list(arch.architecture_versions(store, limit=MAX_HISTORICAL_VERSIONS + 2))[1:]
                        if candidate is not None]
    inventory = mechanism_inventory(baseline, proposed, book_nodes=book_nodes, historical=earlier_versions)
    for row in inventory["items"]:
        shown = row["proposed_text"] or row["baseline_text"] or row["historical_text"] or ""
        if row["provenance"] == "transformed":
            shown = f"{row['baseline_text']} ⇒ {row['proposed_text']}"
        add("mechanism", f"{row['provenance']} · {shown}", TEXT_LIMIT,
            record_kind=row["record_kind"], record_id=row["record_id"], provenance=row["provenance"],
            changed_fields=row["changed_fields"], routes=row["routes"], book_references=row["book_references"],
            endpoints=row["endpoints"], baseline_text=row["baseline_text"], proposed_text=row["proposed_text"],
            historical_text=row["historical_text"], baseline_sha256=row["baseline_sha256"],
            proposed_sha256=row["proposed_sha256"], historical_sha256=row["historical_sha256"],
            version_request_sha256=row["version_request_sha256"])
    present_nodes = {node["id"] for node in list(baseline.get("nodes", [])) + list(proposed.get("nodes", []))}
    elements = book_element_candidates(
        book_rows, seed_node_identifiers(inventory), present_nodes, question_ids=examined)
    for row in elements["items"]:
        add("book_element", row["text"], book_number=row["book_number"], element_id=row["element_id"],
            collection=row["collection"], attribution=row["attribution"], epistemic_status=row["epistemic_status"],
            cites=row["cites"], cited_seed_nodes=row["cited_seed_nodes"],
            decision_examined=row["book_number"] in examined_books,
            # The question identities this element references, and those among them the proposal examines. An association
            # records engagement only: it is not a recorded inheritance or an accepted answer.
            question_refs=row["question_refs"], examined_question_ids=row["examined_question_ids"])

    packet: dict[str, Any] = {
        "packet_version": PACKET_VERSION,
        "schema": SCHEMA,
        "authority": AUTHORITY,
        "proposal": {
            "revision_request_sha256": review["request_sha256"],
            "baseline_request_sha256": review.get("prior_request_sha256"),
            "proposal_sha256": _digest(proposed),
            "baseline_candidate_sha256": _digest(baseline),
            "requested_change_sha256": text_digest(requested) if requested.strip() else None,
            "proposed_summary": (review.get("proposed_rationale") or {}).get("text"),
        },
        "baseline_question_ids": [question["id"] for question in view["questions"]
                                  if question["standing"] == "continuing"],
        "examined_questions": examined_rows,
        "evidence": evidence,
        "coverage": {
            # Only the titles actually shown count as read; any beyond the title limit are counted in limits, never listed.
            "books_read": [number for number, _ in readable_books[:MAX_BOOK_TITLES]],
            "books_with_decisions_on_examined_questions": sorted(examined_books),
            "books_listed_by_title_only": [number for number, _ in readable_books[:MAX_BOOK_TITLES]
                                           if number not in examined_books],
            "unreadable_books": unreadable_books,
            "note": ("A Working Book listed by title only was not read for its decisions about these questions. That is "
                     "not evidence that it is unaffected."),
        },
        "limits": {
            "examined_questions_shown": MAX_EXAMINED_QUESTIONS,
            "questions_omitted": questions_omitted,
            "book_decisions_per_question": MAX_BOOK_DECISIONS,
            "components_shown": min(len(components), MAX_COMPONENTS),
            "components_omitted": max(0, len(components) - MAX_COMPONENTS),
            "phases_shown": min(len(phases), MAX_PHASES),
            "phases_omitted": max(0, len(phases) - MAX_PHASES),
            "books_shown": min(len(readable_books), MAX_BOOK_TITLES),
            "books_omitted": max(0, len(readable_books) - MAX_BOOK_TITLES),
            "instruction_characters": INSTRUCTION_LIMIT,
            "text_characters": TEXT_LIMIT,
            "mechanisms_shown": len(inventory["items"]),
            "mechanisms_considered": inventory["considered"],
            "mechanisms_omitted": inventory["omitted"],
            "book_elements_shown": len(elements["items"]),
            "book_elements_considered": elements["considered"],
            "book_elements_omitted": elements["omitted"],
            "historical_versions_read": len(earlier_versions),
            "mechanism_cap": MAX_MECHANISMS,
            "book_element_cap": MAX_BOOK_ELEMENTS,
        },
        "mechanism_vocabulary": {"provenance": PROVENANCE_MEANING, "routes": ROUTE_MEANING},
        # Which identifiers each field may take, derived from the same kinds and provenance the owner checks. It is guidance for
        # the responding agent; the owner still checks every citation against the request.
        "citation_index": _citation_index(evidence),
    }
    packet["evidence_sha256"] = _digest(packet)
    return packet


CITATION_FIELDS = (
    "instruction", "selected_alternative", "question_wording", "current_mechanisms", "inheritance_from", "inheritance_to",
    "inheritance_to_recorded", "recorded_steps",
)


def _citation_index(evidence: list[dict[str, Any]]) -> dict[str, list[str]]:
    """The identifiers each citing field may take. ``inheritance_to`` names only later-side items: a recorded phase, a recorded
    history item or a mechanism is never a target. ``recorded_steps`` are the items a step labelled recorded may cite."""
    index: dict[str, list[str]] = {field: [] for field in CITATION_FIELDS}
    for item in evidence:
        identifier, kind = item["id"], item["kind"]
        if kind == "instruction":
            index["instruction"].append(identifier)
        if kind == "selected_alternative":
            index["selected_alternative"].append(identifier)
        if kind in ("baseline_wording", "proposed_wording", "removed"):
            index["question_wording"].append(identifier)
        if kind == "mechanism" and item.get("provenance") != "historical":
            index["current_mechanisms"].append(identifier)
        if "earlier" in _sides(item):
            index["inheritance_from"].append(identifier)
        if kind in ("book_element", "book_decision", "working_book"):
            index["inheritance_to"].append(identifier)
        if kind == "book_element" and item.get("collection") == "inherited":
            index["inheritance_to_recorded"].append(identifier)
        if _is_recorded(item):
            index["recorded_steps"].append(identifier)
    return index


def _live(store: CanvasStore, current: dict | None, request, review: dict | None) -> bool:
    """The examined proposal is still the pending review, on the same baseline, source and design guidance."""
    settings = request.settings
    if not current or current["request_sha256"] != settings["baseline_candidate_request_sha256"]:
        return False
    if arch._current_candidate_freshness(store, current) != "ready":
        return False
    if current.get("source_sha256") != settings.get("source_sha256"):
        return False
    if current.get("design_guidance_sha256") != settings.get("design_guidance_sha256"):
        return False
    if not review or review.get("request_sha256") != settings["review_request_sha256"]:
        return False
    # The pending review carries its own working context (sources, guidance, creative intentions). Apply refuses it once that
    # context changes, so an analysis of it is stale from the same moment.
    review_request = load_host_agent_request(arch._root(store) / "requests" / settings["review_request_sha256"] / "request.json")
    return not arch.review_context_changed(store, review_request)


def _standing(store: CanvasStore, request, pending: dict | None, current: dict | None, latest: bool = False) -> str:
    """The standing of one analysis against the proposal as it is now. Only the latest analysis of the pending proposal, while
    it is still live, is ``current``; an earlier analysis of that same proposal is ``superseded`` by the later one."""
    revision = request.settings["review_request_sha256"]
    if current and current["request_sha256"] == revision:
        return "applied"
    if pending and pending.get("request_sha256") == revision:
        if not _live(store, current, request, pending):
            return "stale_context"
        return "current" if latest else "superseded"
    if revision in arch.architecture_revision_chain(store)["requests"]:
        return "applied"
    return "superseded"


def analysis_standing(store: CanvasStore, analysis_request_sha256: str) -> str:
    """The standing of one saved analysis now, read the same way the history rows read it.

    It is ``current`` only while it is the latest analysis on the canvas and its proposal is still live. Any other analysis of
    that proposal is ``superseded``; one whose proposal has changed is ``stale_context``. Read-only.
    """
    base = _root(store)
    pointer = arch._read(base / "latest_request.json")
    latest = pointer.get("request_sha256") if pointer else None
    request = load_host_agent_request(base / "requests" / analysis_request_sha256 / "request.json")
    pending = arch.project_architecture(store).get("review")
    return _standing(store, request, pending, arch._candidate(store), latest=(analysis_request_sha256 == latest))


def prepare_architecture_consequence(store: CanvasStore, *, contract_version: int = CONTRACT_VERSION) -> dict:
    """Prepare the analysis of the pending revision. Explicit only; nothing is executed and no record changes.

    ``contract_version`` names the answer contract the request asks for: the current one by default, or version 2 where a
    version 2 analysis is deliberately reproduced (the historical exercises). A version 2 request accepts only version 2 answers.
    """
    if contract_version not in (2, 3):
        raise ValueError("the consequence analysis contract is version 2 or 3")
    with arch._FilesystemLock(store._path(".canvas.lock")):
        current = arch._candidate(store)
        if not current:
            raise ValueError("no current working architecture")
        if arch._current_candidate_freshness(store, current) != "ready":
            raise arch.BeginnerConcurrencyError("architecture source or guidance is stale")
        projection = arch.project_architecture(store)
        review = projection.get("review")
        if projection.get("status") != "review_ready" or not review:
            raise ValueError("no pending architecture revision to analyse")
        if review.get("prior_request_sha256") != current["request_sha256"]:
            raise arch.BeginnerConcurrencyError("the pending revision was prepared against a superseded baseline")
        packet = build_consequence_packet(store, review, current["candidate"])
        context = arch._source(store, previous=current["candidate"])
        _, _, design_context = arch._design_context_parts(store, context)
        payload = {
            "operation": "consequence_analysis",
            "consequence_packet": packet,
            "baseline_candidate": current["candidate"],
            "proposed_candidate": review["candidate"],
            "narrative_design_context": design_context,
        }
        user = json.dumps(payload, ensure_ascii=False, sort_keys=True)
        settings = {
            "operation": "analyse_consequences",
            "canvas_id": store.canvas_id,
            "review_request_sha256": review["request_sha256"],
            "baseline_candidate_request_sha256": current["request_sha256"],
            "proposal_sha256": packet["proposal"]["proposal_sha256"],
            "source_sha256": current["source_sha256"],
            "design_guidance_sha256": current.get("design_guidance_sha256"),
            "consequence_schema_version": contract_version,
            "evidence_sha256": packet["evidence_sha256"],
            # Each explicit invocation is its own record, so an identical request is still a new ask.
            "invocation": uuid.uuid4().hex,
        }
        # The authoritative output contract is generated from the model the owner validates against, so the responding agent is
        # given the exact field names, literal values, bounds and identifier patterns of that model, not a prose approximation.
        answer_model = ConsequenceAnswerV2 if contract_version == 2 else ConsequenceAnswerV3
        request = build_host_agent_request(
            candidate_id="studio-consequence-" + _digest({"settings": settings, "user": user})[:24],
            role=ROLE, system=_SYSTEM_V2 if contract_version == 2 else _SYSTEM_V3, user=user, settings=settings,
            output_contract=model_output_contract(answer_model),
        )
        base = _root(store)
        write_host_agent_request(base / "requests" / request.request_sha256 / "request.json", request)
        _atomic_json_write(base / "latest_request.json", {"request_sha256": request.request_sha256})
    return project_architecture_consequence(store)


def _check_answer(answer: ConsequenceAnswer, packet: dict[str, Any]) -> None:
    """Every reference resolves inside this request, and every stated basis is the one the evidence shows."""
    evidence = {item["id"]: item for item in packet["evidence"]}
    baseline_ids = set(packet["baseline_question_ids"])

    def cited_kinds(identifiers: list[str], owner: str) -> set[str]:
        for identifier in identifiers:
            if identifier not in evidence:
                raise ValueError(f"{owner} cites {identifier}, which is not in this request")
        return {evidence[identifier]["kind"] for identifier in identifiers}

    titles: set[str] = set()
    earlier = {"baseline_wording", "recorded_history", "book_decision"}
    proposed = {"proposed_wording", "proposed_component", "removed"}
    for concern in answer.concerns:
        key = " ".join(concern.title.casefold().split())
        if key in titles:
            raise ValueError(f"two concerns share the title {concern.title!r}")
        titles.add(key)
        kinds = cited_kinds(concern.evidence, f"concern {concern.title!r}")
        if concern.intent == "instruction_names_it" and "instruction" not in kinds:
            raise ValueError(f"concern {concern.title!r} says the instruction names it but cites no instruction")
        if concern.intent == "selected_alternative_names_it" and "selected_alternative" not in kinds:
            raise ValueError(f"concern {concern.title!r} says the selected alternative names it but cites none")
        # An introduced concern is new wording or a new structure. A removal is the opposite, so it never satisfies this rule.
        if concern.status == "introduced" and not kinds & {"proposed_wording", "proposed_component"}:
            raise ValueError(f"concern {concern.title!r} is introduced but cites no proposed wording or component")
        if concern.status == "possibly_displaced" and not kinds & earlier:
            raise ValueError(f"concern {concern.title!r} may be displaced but cites no earlier formulation or decision")
        if concern.status == "transformed" and not (kinds & earlier and kinds & proposed):
            raise ValueError(f"concern {concern.title!r} is transformed and must cite both its earlier and its proposed form")
    for item in answer.prospective:
        kinds = cited_kinds(item.evidence, "a prospective item")
        if item.kind == "recorded_relationship" and not kinds & {"book_decision", "recorded_history"}:
            raise ValueError("a recorded relationship must cite a Book decision or recorded history")
    alternative_titles: set[str] = set()
    for alternative in answer.alternatives:
        key = " ".join(alternative.title.casefold().split())
        if key in alternative_titles:
            raise ValueError(f"two alternatives share the title {alternative.title!r}")
        alternative_titles.add(key)
        missing = [identifier for identifier in alternative.questions if identifier not in baseline_ids]
        if missing:
            raise ValueError(f"alternative {alternative.title!r} names {', '.join(missing)}, which is not a continuing "
                             "question of the baseline")


def _system_v2() -> str:
    """The version 2 instruction. Every bound, value and rule is generated from the constants the owner enforces."""
    approaches = "\n".join(f"  - {name}: {meaning}" for name, meaning in APPROACH_MEANINGS.items())
    reach = "\n".join(f"  - {name}: {meaning}" for name, meaning in REACH_MEANINGS.items())
    kinds = "\n".join(f"  - {name}: {meaning}" for name, meaning in INHERITANCE_MEANINGS.items())
    provenance = "\n".join(f"  - {name}: {meaning}" for name, meaning in PROVENANCE_MEANING.items())
    return f"""You are the active Auteur consequence-analysis agent. The author is considering a proposed working revision of
the narrative Architecture. The revision has been reviewed but NOT applied. Help the author understand what the proposal does
through the recorded narrative mechanisms it touches, what earlier creative concerns it keeps, transforms or may displace, what
later Books may inherit, and which developmental trajectories become possible. You are not judging whether the proposal is right.
Deliberate transformation and abandonment are legitimate. Do not presume that preservation is better, and do not presume that
a local change must have far consequences.

Read the baseline candidate (the applied working Architecture), the proposed candidate (the un-applied revision) and the
consequence packet. Evidence items E1, E2 and so on are facts the owners recorded or a deterministic comparison of the two
candidates. Cite evidence only by these identifiers. A mechanism item is one recorded record (a node, link, phase, emotion
target, complex emotion, genre contract or genre interaction) with its provenance:
{provenance}
A mechanism that keeps its identifier is not thereby unchanged in function. A book_element is a Working Book element that cites
a recorded node; it is the Book's own noncanonical working proposal. A working_book item is a Book's title only and is not
evidence of its content. A book_decision whose proposal_status is not unchanged refers to a question the proposal changes: a
recorded relationship by identity, not a demonstrated contradiction. A Working Book the packet lists only by title, or whose
decisions on an examined question were not read, is not evidence that it is unaffected. A named_gap is missing history: never
fill it in.

Keep apart what the record shows (cite it), what you interpret (say so) and what the record cannot establish (say so in
not_established or unresolved). A changed wording does not prove a changed meaning. A recorded relation is not a causal law of
the story. An inheritance you propose is not recorded. A trajectory is a hypothetical developmental sequence, never an event.

Return ONLY a JSON object with these keys:
- schema_version: 2
- reading: what the proposal accomplishes and what it changes, in plain words. Required, at most {READING_LIMIT} characters.
- reach: one of
{reach}
- concerns: 0 to {MAX_CONCERNS} objects with title (at most {CONCERN_TITLE_LIMIT} characters); status, one of preserved,
  transformed, possibly_displaced or introduced; earlier and proposed (optional, at most {CONCERN_SIDE_LIMIT} characters each);
  reading (required, at most {CONCERN_READING_LIMIT} characters); evidence (1 to {MAX_EVIDENCE_PER_CONCERN} identifiers); intent (required
  for transformed and possibly_displaced: instruction_names_it, selected_alternative_names_it or not_established; instruction_names_it
  must cite the instruction item and selected_alternative_names_it the selected_alternative item; omit intent for preserved and
  introduced); counterevidence (0 to {MAX_COUNTEREVIDENCE} strings, each at most {COUNTER_LIMIT} characters); competing_reading (optional,
  at most {CONCERN_SIDE_LIMIT} characters). Status: preserved, the concern is still represented; transformed, it is in play but its
  formulation or function changed; possibly_displaced, it may no longer be represented or needs separate consideration, and the
  record may not establish whether that was intended; introduced, a new uncertainty, tension or opportunity.
- no_concern_reason: required when concerns is empty (at most {NO_CONCERN_LIMIT} characters).
- mechanisms: 0 to {MAX_MECHANISM_READINGS} objects, each about one mechanism item:
  evidence (a mechanism identifier); reading (required, at most {READING_ITEM_LIMIT} characters: what the recorded record does,
  as an interpretation); transformation (at most {TRANSFORMATION_LIMIT} characters: how the proposal alters the record's operation or
  significance; REQUIRED for transformed, removed and introduced; optional for preserved, where it says how the proposal bears on
  the operation); conditional_consequence (optional, at most {CONSEQUENCE_LIMIT} characters, phrased as "if ..."); counterevidence (0 to
  {MAX_MECHANISM_COUNTEREVIDENCE} objects, each with text of at most {COUNTER_LIMIT} characters and 1 to 3 evidence identifiers of recorded
  material other than this mechanism itself, which limits the reading); unresolved (0 to {MAX_MECHANISM_UNRESOLVED} strings, each at most {ITEM_LIMIT} characters: the decision or
  evidence needed).
- inheritance: 0 to {MAX_INHERITANCE} objects with kind, from, to, text and evidence:
  kind, one of
{kinds}
  from: an earlier-side identifier (baseline_wording, recorded_history, book_decision, or a mechanism item).
  to: a later-side identifier (book_element, book_decision or working_book). recorded_inheritance requires to to be a book_element
  in collection inherited; plausible_inheritance requires a book_element or book_decision; a working_book title never supports a
  recorded or plausible inheritance. A recorded_inheritance must come from a mechanism whose endpoints the Book element's cites list
  names. text: at most {INHERITANCE_TEXT_LIMIT} characters. evidence: 0 to 4 identifiers.
- trajectories: 0 to {MAX_TRAJECTORIES} objects with title (at most {TRAJECTORY_TITLE_LIMIT} characters), steps (2 to {MAX_TRAJECTORY_STEPS} objects),
  assumptions (0 to {MAX_TRAJECTORY_ASSUMPTIONS} strings, at most {ASSUMPTION_LIMIT} characters: what must hold) and comparison (optional
  object with optional strings of at most {COMPARISON_LIMIT} characters: creative_gain, narrative_cost, contrivance_risk,
  future_commitment, flexibility). Each step has stage (one of local_decision, mechanism_transformation, tension, opportunity,
  inheritance, long_horizon), text (at most {STEP_TEXT_LIMIT} characters), evidence (0 to 3 identifiers) and basis (recorded,
  interpreted or speculative). A step with basis recorded must cite a recorded item: a baseline wording, a recorded history item, a Book decision or
  element, a recorded phase, or a preserved, removed or historical mechanism. A proposal item, an instruction or a Working Book
  title is never recorded. Trajectories are hypothetical and are stored as such.
- alternatives: 0 to {MAX_ALTERNATIVES} objects with approach, title (at most {APPROACH_TITLE_LIMIT} characters), summary (at most
  {APPROACH_SUMMARY_LIMIT} characters), questions (1 to 3 baseline question identifiers), keeps (1 to {MAX_KEEPS} identifiers: the object of
  retention, see the approach rules), mechanisms (0 to {MAX_ALTERNATIVE_MECHANISMS} mechanism identifiers the investigation should
  examine), gains (at most {APPROACH_GAINS_LIMIT} characters), costs (at most {APPROACH_COSTS_LIMIT} characters; state costs as well as
  gains), next_investigation (at most {NEXT_LIMIT} characters). Approaches, one of:
{approaches}
  keeps rules: keep_baseline, replace, integrate, separate, defer and reframe keep baseline wording only; accept_proposal keeps
  proposal-side wording only. Every keeps item is wording of one of the alternative's questions, every named question's wording is
  kept, and only questions whose wording the packet gives may be named. Every keeps item is a wording item of one of the alternative's questions. Name a
  distinct question a proposal introduces in the summary; never give it an identity. If you recommend one approach, say why it is
  stronger than the others here.
- not_established: 0 to {MAX_NOT_ESTABLISHED} strings, each at most {NOT_ESTABLISHED_LIMIT} characters.

Evidence rules, enforced exactly as written. Reach local allows no inheritance other than unknown_inheritance and no inheritance
trajectory step; reach conditional_inheritance needs an inheritance other than unknown_inheritance; reach not_established allows no
recorded_inheritance. Preserved needs at least one cited item. Introduced needs a proposed_wording,
proposed_component or an introduced or transformed mechanism. Possibly_displaced needs an earlier-side item (baseline_wording,
recorded_history, book_decision or a mechanism on the earlier side). Transformed needs an earlier-side item AND a proposed-side item
(proposed_wording, proposed_component, removed, or a transformed mechanism, which is on both sides). Earlier-side mechanisms are
preserved, transformed, removed and historical; proposed-side mechanisms are transformed, introduced and removed. Concern titles are
distinct. Mechanism readings cite distinct mechanisms. Alternative titles are distinct.

Use only the identifiers the packet gives. Do not invent narrative facts, Book content or future events. A proposed possibility,
inheritance, trajectory and conditional consequence are the only places for speculation, and each is labelled as such. Never state
or imply that the proposal is accepted, applied or canonical, and never say that a Working Book has been changed by this analysis."""


_SYSTEM_V2 = _system_v2()


def _contract_keys() -> str:
    """The exact key names of the version 3 answer, read from the owner's models so the instruction cannot drift from them."""
    def keys(model: type[BaseModel]) -> str:
        return ", ".join(field.alias or name for name, field in model.model_fields.items())

    return "\n".join([
        f"- answer (top level): {keys(ConsequenceAnswerV3)}",
        f"- concerns[]: {keys(ConsequenceConcern)}",
        f"- mechanisms[]: {keys(MechanismReading)}; counterevidence[] items: {keys(MechanismCounterevidence)}",
        f"- inheritance[]: {keys(InheritanceItem)}",
        f"- trajectories[]: {keys(Trajectory)}; steps[]: {keys(TrajectoryStep)}; comparison: {keys(TrajectoryComparison)}",
        f"- alternatives[]: {keys(AlternativeV3)}",
        f"- connections[]: {keys(MechanismConnection)}",
    ])


def _system_v3() -> str:
    """The version 3 instruction. Every bound, value and rule is generated from the constants the owner enforces."""
    approaches = "\n".join(f"  - {name}: {meaning}" for name, meaning in APPROACH_MEANINGS_V3.items())
    standings = "\n".join(f"  - {name}: {meaning}" for name, meaning in CONNECTION_MEANINGS.items())
    bases = "\n".join(f"  - {name}: {meaning}" for name, meaning in CONNECTION_BASIS_MEANINGS.items())
    reach = "\n".join(f"  - {name}: {meaning}" for name, meaning in REACH_MEANINGS.items())
    kinds = "\n".join(f"  - {name}: {meaning}" for name, meaning in INHERITANCE_MEANINGS.items())
    provenance = "\n".join(f"  - {name}: {meaning}" for name, meaning in PROVENANCE_MEANING.items())
    return f"""You are the active Auteur consequence-analysis agent. The author is considering a proposed working revision of
the narrative Architecture. The revision has been reviewed but NOT applied. Help the author understand what the proposal does
through the recorded narrative mechanisms it touches, what earlier creative concerns it keeps, transforms or may displace, what
later Books may inherit, which developmental trajectories become possible, and how the mechanisms relate to one another. You are
not judging whether the proposal is right. Deliberate transformation and abandonment are legitimate, and a mechanism may be
investigated without any question standing for it: a mechanism alone is a legitimate object of an alternative. Do not presume that
preservation is better, and do not presume that a local change must have far consequences.

Read the baseline candidate (the applied working Architecture), the proposed candidate (the un-applied revision) and the
consequence packet. Evidence items E1, E2 and so on are facts the owners recorded or a deterministic comparison of the two
candidates. Cite evidence only by these identifiers. A mechanism item is one recorded record (a node, link, phase, emotion target,
complex emotion, genre contract or genre interaction) with its provenance:
{provenance}
A mechanism that keeps its identifier is not thereby unchanged in function. A book_element is a Working Book element that cites a
recorded node; it is the Book's own noncanonical working proposal. A working_book item is a Book's title only and is not evidence of
its content. A named_gap is missing history: never fill it in.

Keep apart what the record shows (cite it), what you interpret (say so) and what the record cannot establish (say so in
not_established or unresolved). A changed wording does not prove a changed meaning. A recorded relation is not a causal law of the
story. An inheritance you propose is not recorded. A trajectory is a hypothetical developmental sequence, never an event. A
connection is a claim about how two mechanisms relate, and its standing is yours; the owner separately reads the recorded graph and
stores what it finds beside your standing.

Return ONLY a JSON object with these keys. Everything in version 2 keeps its bounds and rules, except where stated here.
Field names are exact, and are listed here from the owner's contract. Use these names and no others:
{_contract_keys()}
Identifiers. A mechanism is cited by its EVIDENCE identifier: the letter E followed by a number, as the packet lists it. Every field
that takes a mechanism takes that identifier: mechanisms[].evidence (ONE string, not a list), alternatives[].mechanisms and keeps,
connections[].between and connections[].evidence, and inheritance from. A record identifier such as l_compact_hands_in_kind is the
record's own name; it appears in the packet's record_id field and is never cited in an identifier field. Likewise a question is cited
by its question identifier from baseline_question_ids, never by its position.
Field shapes the schema cannot state. The output_contract gives every name, type, literal and bound. These rules are the owner's,
checked on top of it, and each one is stated for the field it governs:
- concerns[].intent is one of instruction_names_it, selected_alternative_names_it or not_established. It is never a basis word:
  recorded, interpreted and speculative belong to trajectory steps and connections only. intent is required for a transformed or
  possibly_displaced concern, and a preserved or introduced concern omits intent.
- concerns[].counterevidence is a list of plain strings. mechanisms[].counterevidence is a list of objects, each {{text, evidence}}.
- A transformed, removed or introduced mechanism states its transformation.
- consequence_packet.citation_index lists what each field may take, and the owner checks against it. inheritance[].from takes an
  inheritance_from item. inheritance[].to takes an inheritance_to item, never a recorded_phase, recorded_history or a mechanism.
  recorded_inheritance takes an inheritance_to_recorded item and comes from a mechanism; plausible_inheritance takes a book_element
  or book_decision; a working_book title supports only unknown_inheritance.
- alternatives[].mechanisms and connections[].between take current_mechanisms items. alternatives[].keeps takes question_wording
  items for its questions and mechanism items for its mechanisms. A trajectory step labelled recorded cites at least one
  recorded_steps item.
- The instruction is cited in concerns[].evidence by its identifier in citation_index.instruction, and intent
  instruction_names_it needs that identifier among the concern's evidence.
- schema_version: 3
- reading, reach, concerns, no_concern_reason, mechanisms, inheritance, trajectories: as in version 2. Reach values:
{reach}
  Concern bounds: at most {MAX_CONCERNS} concerns; each reading at most {CONCERN_READING_LIMIT} characters; each evidence list 1 to
  {MAX_EVIDENCE_PER_CONCERN} identifiers. Mechanism readings: 0 to {MAX_MECHANISM_READINGS}, one per mechanism; each reading at most
  {READING_ITEM_LIMIT} characters; a transformed, removed or introduced mechanism states its transformation. Mechanism counterevidence
  is 0 to {MAX_MECHANISM_COUNTEREVIDENCE} objects, each {{text, evidence}} with text of at most {COUNTER_LIMIT} characters, and its
  evidence (1 to 3 identifiers) must include at least one recorded item other than this mechanism itself, because counterevidence
  limits the reading; an object whose evidence names only this mechanism is refused. Inheritance kinds:
{kinds}
- alternatives: 0 to {MAX_ALTERNATIVES} objects. Each names at least one anchor and at most three anchors in all: questions (0 to 3 continuing
  baseline question identifiers) and mechanisms (0 to 3 mechanism identifiers). A mechanism-only alternative is legitimate. Do not
  invent a question to satisfy it. Each has approach, title (at most {APPROACH_TITLE_LIMIT} characters), summary (at most
  {APPROACH_SUMMARY_LIMIT} characters), keeps (1 to 3 identifiers), gains (at most {APPROACH_GAINS_LIMIT} characters), costs (at most
  {APPROACH_COSTS_LIMIT} characters; state costs as well as gains) and next_investigation (at most {NEXT_LIMIT} characters). Approaches:
{approaches}
  keeps rules: every anchor is represented exactly once in keeps and keeps names nothing else. A named question is represented by its
  wording on the side the approach keeps. A named mechanism is represented by its own identifier on the side the approach keeps: for
  accept_proposal, a preserved, transformed, introduced or removed record; for every other approach, a preserved, transformed or removed
  record. A historical mechanism is never an anchor. A distinct question or mechanism a proposal introduces is described in the summary
  and is never given an identity. If you recommend one approach, say why it is stronger than the others here.
- connections: 0 to {MAX_CONNECTIONS} objects. Each relates exactly two distinct mechanisms, between (two mechanism identifiers), with
  standing, one of:
{standings}
  text (at most {CONNECTION_TEXT_LIMIT} characters). An inferred connection states reasoning (at most {CONNECTION_REASON_LIMIT}
  characters) and 1 to {MAX_CONNECTION_ASSUMPTIONS} assumptions (each at most {CONNECTION_ITEM_LIMIT} characters). A hypothetical
  connection states worth_developing (at most {CONNECTION_REASON_LIMIT} characters: why it could be worth developing) and 1 to
  {MAX_CONNECTION_ASSUMPTIONS} assumptions. An unestablished connection states its basis, one of:
{bases}
  A basis is stated only for an unestablished connection, and reasoning only for an inferred one. A recorded connection is refused
  unless the Architecture records a joining link or interaction, or a shared node, between the two; a graph_miss is refused when it
  does record one. Each connection may give evidence (0 to 4 identifiers) and counterevidence (0 to {MAX_CONNECTION_COUNTEREVIDENCE}
  strings, each at most {CONNECTION_ITEM_LIMIT} characters).
- not_established: 0 to {MAX_NOT_ESTABLISHED} strings, each at most {NOT_ESTABLISHED_LIMIT} characters.

Evidence rules, enforced exactly as written. Reach local allows no inheritance other than unknown_inheritance and no inheritance
trajectory step; reach conditional_inheritance needs an inheritance other than unknown_inheritance; reach not_established allows no
recorded_inheritance. Preserved needs at least one cited item. Introduced needs a proposed_wording, proposed_component or an
introduced or transformed mechanism. Possibly_displaced needs an earlier-side item. Transformed needs an earlier-side item AND a
proposed-side item. Concern titles are distinct. Mechanism readings cite distinct mechanisms. Alternative titles are distinct. A
connection cites two distinct mechanisms, and no pair of mechanisms is connected twice.

Use only the identifiers the packet gives. Do not invent narrative facts, Book content or future events. A proposed possibility,
inheritance, trajectory, alternative and inferred or hypothetical connection are the only places for speculation, and each is labelled
as such. Never state or imply that the proposal is accepted, applied or canonical, and never say that a Working Book has been changed
by this analysis."""


_SYSTEM_V3 = _system_v3()


def _sides(item: dict[str, Any]) -> set[str]:
    """The side or sides of the proposal an evidence item lies on: earlier, proposed or both."""
    kind = item["kind"]
    if kind == "mechanism":
        sides = set()
        if item.get("provenance") in _EARLIER_PROVENANCE:
            sides.add("earlier")
        if item.get("provenance") in _PROPOSED_PROVENANCE:
            sides.add("proposed")
        return sides
    if kind in _EARLIER_KINDS:
        return {"earlier"}
    if kind in _PROPOSED_KINDS:
        return {"proposed"}
    return set()


def _resolver(packet: dict[str, Any]):
    """Resolve cited identifiers inside one request; an identifier the request does not give is refused by name."""
    evidence = {item["id"]: item for item in packet["evidence"]}

    def resolve(identifiers: list[str], owner: str) -> list[dict[str, Any]]:
        for identifier in identifiers:
            if identifier not in evidence:
                raise ValueError(f"{owner} cites {identifier}, which is not in this request")
        return [evidence[identifier] for identifier in identifiers]

    return resolve


def _collect(problems: list[str], check, items) -> None:
    """Run one item's rules and keep its refusal, so one answer reports every failing item and not only the first."""
    for item in items:
        try:
            check(item)
        except ValueError as refusal:
            problems.append(str(refusal))


def _refuse(problems: list[str]) -> None:
    """Refuse once, with every failing rule of the answer stated once. A single failure keeps its own wording."""
    if not problems:
        return
    if len(problems) == 1:
        raise ValueError(problems[0])
    raise ValueError(f"{len(problems)} rules are not met:\n" + "\n".join(
        f"{number}. {text}" for number, text in enumerate(problems, start=1)))


def _check_answer_v2(answer: ConsequenceAnswerV2, packet: dict[str, Any]) -> None:
    """Every reference resolves inside this request; every stated basis, side and bound is the one the evidence shows."""
    problems = _reading_problems(answer, packet)
    problems += _alternative_problems_v2(answer, packet)
    _refuse(problems)


def _reading_problems(answer: Any, packet: dict[str, Any]) -> list[str]:
    """The concern, mechanism, inheritance, trajectory and reach rules, shared by versions 2 and 3. Every failing item is reported."""
    resolve = _resolver(packet)
    problems: list[str] = []

    # Concerns: the version 1 rules, with mechanism items on the side their provenance puts them.
    titles: set[str] = set()

    def concern_rules(concern) -> None:
        key = " ".join(concern.title.casefold().split())
        if key in titles:
            raise ValueError(f"two concerns share the title {concern.title!r}")
        titles.add(key)
        items = resolve(concern.evidence, f"concern {concern.title!r}")
        kinds = {item["kind"] for item in items}
        sides: set[str] = set().union(*(_sides(item) for item in items)) if items else set()
        if concern.intent == "instruction_names_it" and "instruction" not in kinds:
            raise ValueError(f"concern {concern.title!r} says the instruction names it but cites no instruction")
        if concern.intent == "selected_alternative_names_it" and "selected_alternative" not in kinds:
            raise ValueError(f"concern {concern.title!r} says the selected alternative names it but cites none")
        if concern.status == "introduced" and not any(
                item["kind"] in ("proposed_wording", "proposed_component")
                or (item["kind"] == "mechanism" and item.get("provenance") in ("introduced", "transformed"))
                for item in items):
            raise ValueError(f"concern {concern.title!r} is introduced but cites no proposed wording, component or new mechanism")
        if concern.status == "possibly_displaced" and "earlier" not in sides:
            raise ValueError(f"concern {concern.title!r} may be displaced but cites no earlier formulation, decision or mechanism")
        if concern.status == "transformed" and not {"earlier", "proposed"} <= sides:
            raise ValueError(f"concern {concern.title!r} is transformed and must cite both its earlier and its proposed form")

    _collect(problems, concern_rules, answer.concerns)

    # Mechanisms: each is a mechanism item, once; a change to the record must be stated; counterevidence cites recorded
    # material other than the mechanism's own record, so a reading cannot be "limited" by itself.
    seen: set[str] = set()

    def mechanism_rules(reading) -> None:
        if reading.evidence in seen:
            raise ValueError(f"mechanism {reading.evidence} is read twice")
        seen.add(reading.evidence)
        item = resolve([reading.evidence], "a mechanism reading")[0]
        if item["kind"] != "mechanism":
            raise ValueError(f"{reading.evidence} is not a recorded mechanism")
        if item.get("provenance") in ("transformed", "removed", "introduced") and not (reading.transformation or "").strip():
            raise ValueError(f"mechanism {reading.evidence} is {item['provenance']} and its transformation must be stated")
        for counter in reading.counterevidence:
            cited = resolve(counter.evidence, f"counterevidence to {reading.evidence}")
            if all(row["id"] == reading.evidence for row in cited):
                raise ValueError(f"counterevidence to {reading.evidence} must cite material other than the mechanism itself")

    _collect(problems, mechanism_rules, answer.mechanisms)

    # Inheritance: the owner's basis rules. A recorded inheritance is backed by the Book's own element, which must cite a node
    # the earlier mechanism involves; without that citation it is at most a plausible inheritance.
    def inheritance_rules(link) -> None:
        source, target = resolve([link.from_, link.to], "an inheritance")
        resolve(link.evidence, "an inheritance")
        if "earlier" not in _sides(source):
            raise ValueError(f"inheritance from {link.from_} must name an earlier development, not {source['kind']}")
        if target["kind"] not in ("book_element", "book_decision", "working_book"):
            raise ValueError(f"inheritance must name a later Book, not {target['kind']}")
        if link.kind == "recorded_inheritance":
            if not (target["kind"] == "book_element" and target.get("collection") == "inherited"):
                raise ValueError("recorded inheritance must cite a Book's own inherited element")
            if source["kind"] != "mechanism":
                raise ValueError("recorded inheritance must come from a recorded mechanism the Book's element cites")
            cited_nodes = {cite["node_id"] for cite in target.get("cites", [])}
            if not set(source.get("endpoints") or []) & cited_nodes:
                raise ValueError("recorded inheritance needs a Book element that cites a node the mechanism involves")
        if link.kind == "plausible_inheritance" and target["kind"] not in ("book_element", "book_decision"):
            raise ValueError("plausible inheritance must cite a Book element or a Book decision, not a Book title")
        if link.kind in ("recorded_inheritance", "plausible_inheritance") and target["kind"] == "working_book":
            raise ValueError("a Working Book title is not evidence of inheritance")

    _collect(problems, inheritance_rules, answer.inheritance)

    # Trajectories: titles distinct; a step that claims to be recorded cites a recorded item, never the proposal itself.
    trajectory_titles: set[str] = set()

    def trajectory_rules(trajectory) -> None:
        key = " ".join(trajectory.title.casefold().split())
        if key in trajectory_titles:
            raise ValueError(f"two trajectories share the title {trajectory.title!r}")
        trajectory_titles.add(key)
        for step in trajectory.steps:
            cited = resolve(step.evidence, f"trajectory {trajectory.title!r}")
            if step.basis == "recorded":
                if not step.evidence:
                    raise ValueError(f"a recorded step of {trajectory.title!r} must cite evidence")
                if not any(_is_recorded(item) for item in cited):
                    raise ValueError(f"a recorded step of {trajectory.title!r} must cite a recorded item, not the proposal")

    _collect(problems, trajectory_rules, answer.trajectories)

    # Reach: the stated locality must be the one the content shows.
    stages = {step.stage for trajectory in answer.trajectories for step in trajectory.steps}
    inheritance_kinds = {link.kind for link in answer.inheritance}
    if answer.reach == "local":
        if "long_horizon" in stages:
            problems.append("a local change has no long-horizon trajectory step")
        if "inheritance" in stages or inheritance_kinds - {"unknown_inheritance"}:
            problems.append("a local change records no later development; use conditional_inheritance for it")
    if answer.reach == "long_horizon" and not stages & {"long_horizon", "inheritance"}:
        problems.append("a long-horizon reach needs a long-horizon or inheritance step")
    if answer.reach == "conditional_inheritance" and not inheritance_kinds - {"unknown_inheritance"}:
        problems.append("a conditional inheritance reach needs an inheritance other than unknown")
    if answer.reach == "not_established" and "recorded_inheritance" in inheritance_kinds:
        problems.append("a reach not established by the record cannot rest on a recorded inheritance")
    return problems


def _alternative_problems_v2(answer: ConsequenceAnswerV2, packet: dict[str, Any]) -> list[str]:
    """Alternatives: distinct; each names continuing baseline questions; its keeps cover every named question with the wording
    the approach keeps (proposal-side wording for accept_proposal, baseline wording otherwise), and nothing else."""
    resolve = _resolver(packet)
    baseline_ids = set(packet["baseline_question_ids"])
    problems: list[str] = []
    alternative_titles: set[str] = set()

    def alternative_rules(alternative) -> None:
        key = " ".join(alternative.title.casefold().split())
        if key in alternative_titles:
            raise ValueError(f"two alternatives share the title {alternative.title!r}")
        alternative_titles.add(key)
        missing = [identifier for identifier in alternative.questions if identifier not in baseline_ids]
        if missing:
            raise ValueError(f"alternative {alternative.title!r} names {', '.join(missing)}, which is not a continuing "
                             "question of the baseline")
        kept = resolve(alternative.keeps, f"alternative {alternative.title!r}")
        for item in kept:
            if item["kind"] not in _QUESTION_KINDS or item.get("question_id") not in alternative.questions:
                raise ValueError(f"alternative {alternative.title!r} keeps an item that is not wording of its own questions")
        if alternative.approach == "accept_proposal":
            if not any(item["kind"] in ("proposed_wording", "removed") for item in kept):
                raise ValueError(f"alternative {alternative.title!r} accepts the proposal but keeps no proposal-side item")
            for item in kept:
                if item["kind"] not in ("proposed_wording", "removed"):
                    raise ValueError(f"alternative {alternative.title!r} accepts the proposal and keeps only proposal-side wording")
        else:
            if not any(item["kind"] == "baseline_wording" for item in kept):
                raise ValueError(f"alternative {alternative.title!r} ({alternative.approach}) must keep the baseline wording")
            for item in kept:
                if item["kind"] != "baseline_wording":
                    raise ValueError(f"alternative {alternative.title!r} ({alternative.approach}) must keep the baseline wording "
                                     "only, not its proposal")
        covered = {item["question_id"] for item in kept}
        uncovered = [identifier for identifier in alternative.questions if identifier not in covered]
        if uncovered:
            raise ValueError(f"alternative {alternative.title!r} keeps no wording of {', '.join(uncovered)}; every named "
                             "question's wording is kept")
        for identifier in alternative.mechanisms:
            if resolve([identifier], f"alternative {alternative.title!r}")[0]["kind"] != "mechanism":
                raise ValueError(f"alternative {alternative.title!r} names {identifier}, which is not a recorded mechanism")

    _collect(problems, alternative_rules, answer.alternatives)
    return problems


def _alternative_problems_v3(answer: ConsequenceAnswerV3, packet: dict[str, Any]) -> list[str]:
    """Version 3 alternatives: anchored on continuing questions and current mechanisms. Every anchor is kept once on the side its
    approach keeps; a historical record is never an anchor; a keeps item that names nothing the alternative concerns is refused."""
    resolve = _resolver(packet)
    baseline_ids = set(packet["baseline_question_ids"])
    problems: list[str] = []
    titles: set[str] = set()

    def alternative_rules(alternative) -> None:
        key = " ".join(alternative.title.casefold().split())
        if key in titles:
            raise ValueError(f"two alternatives share the title {alternative.title!r}")
        titles.add(key)
        owner = f"alternative {alternative.title!r}"
        accepts = alternative.approach == "accept_proposal"
        missing = [identifier for identifier in alternative.questions if identifier not in baseline_ids]
        if missing:
            raise ValueError(f"{owner} names {', '.join(missing)}, which is not a continuing question of the baseline")
        for identifier in alternative.mechanisms:
            item = resolve([identifier], owner)[0]
            if item["kind"] != "mechanism":
                raise ValueError(f"{owner} names {identifier}, which is not a recorded mechanism")
            provenance = item.get("provenance")
            if provenance == "historical":
                raise ValueError(f"{owner} names {identifier}, a historical record, which is not a current mechanism")
            if accepts and provenance not in _V3_PROPOSED_PROVENANCE:
                raise ValueError(f"{owner} accepts the proposal but {identifier} has no proposed record ({provenance})")
            if not accepts and provenance not in _V3_EARLIER_PROVENANCE:
                raise ValueError(f"{owner} ({alternative.approach}) must keep the baseline record of {identifier}; the proposal "
                                 f"{provenance} it, so it has no baseline record to keep")
        kept = resolve(alternative.keeps, owner)
        # Coverage is checked before the side of each kept wording, so an omitted anchor is named as omitted.
        covered_questions = {item.get("question_id") for item in kept if item["kind"] in _QUESTION_KINDS}
        uncovered = [identifier for identifier in alternative.questions if identifier not in covered_questions]
        if uncovered:
            raise ValueError(f"{owner} keeps no wording of {', '.join(uncovered)}; every named question's wording is kept")
        kept_mechanisms = {item["id"] for item in kept if item["kind"] == "mechanism"}
        not_kept = [identifier for identifier in alternative.mechanisms if identifier not in kept_mechanisms]
        if not_kept:
            raise ValueError(f"{owner} keeps no record of {', '.join(not_kept)}; every named mechanism's record is kept")
        for item in kept:
            if item["kind"] == "mechanism":
                if item["id"] not in alternative.mechanisms:
                    raise ValueError(f"{owner} keeps an item that is not wording of its own questions or a named mechanism")
                continue
            if item["kind"] not in _QUESTION_KINDS or item.get("question_id") not in alternative.questions:
                raise ValueError(f"{owner} keeps an item that is not wording of its own questions or a named mechanism")
            if accepts and item["kind"] not in ("proposed_wording", "removed"):
                raise ValueError(f"{owner} accepts the proposal and must keep the proposal-side wording of {item['question_id']}")
            if not accepts and item["kind"] != "baseline_wording":
                raise ValueError(f"{owner} ({alternative.approach}) must keep the baseline wording of {item['question_id']}")

    _collect(problems, alternative_rules, answer.alternatives)
    return problems


def _connection_problems_v3(answer: ConsequenceAnswerV3, packet: dict[str, Any], baseline: dict | None,
                            proposed: dict | None) -> tuple[list[str], list[dict[str, Any]]]:
    """Each connection relates two current mechanisms. The owner reads the recorded graph of the baseline and the proposal and
    refuses a recorded standing the graph does not show, and a graph miss the graph contradicts. Returns every failing connection
    and, for the connections that pass, the graph reading to store beside the agent's standing."""
    resolve = _resolver(packet)
    pairs: set[tuple[str, str]] = set()
    readings: list[dict[str, Any]] = []
    problems: list[str] = []

    def connection_rules(connection) -> None:
        first, second = resolve(connection.between, "a connection")
        for item in (first, second):
            if item["kind"] != "mechanism" or item.get("provenance") == "historical":
                raise ValueError(f"a connection relates current mechanisms; {item.get('record_id', item['id'])} is not one")
        key = tuple(sorted(connection.between))
        if key in pairs:
            raise ValueError("two connections relate the same pair of mechanisms")
        pairs.add(key)
        resolve(connection.evidence, "a connection")
        reading = relation_status(first.get("endpoints") or [], second.get("endpoints") or [], [baseline, proposed],
                                  exclude=[str(first.get("record_id")), str(second.get("record_id"))])
        label = f"{first.get('record_id')} and {second.get('record_id')}"
        # A recorded connection is a direct link between two nodes, or a node both mechanisms name. Adjacency is one link away and
        # is not a relation between these two, so it cannot be claimed as recorded.
        if connection.standing == "recorded" and reading["status"] not in ("joined_by_link", "shared_endpoint"):
            raise ValueError(f"a recorded connection between {label} cannot stand: the Architecture records no relation between "
                             f"them ({reading['status']}) in the baseline or the proposal")
        if connection.standing == "unestablished" and connection.basis == "graph_miss" \
                and reading["status"] != "no_recorded_relation":
            raise ValueError(f"graph_miss is refused for {label}: the Architecture records a relation between them "
                             f"({reading['status']}); cite it as recorded, or give another basis")
        readings.append(reading)

    _collect(problems, connection_rules, answer.connections)
    return problems, readings


def _check_answer_v3(answer: ConsequenceAnswerV3, packet: dict[str, Any], baseline: dict | None,
                     proposed: dict | None) -> list[dict[str, Any]]:
    """Version 3: the shared reading rules, the anchored alternatives and the graph-checked connections. Every failing rule of the
    answer is refused together. Returns the graph reading of each connection."""
    problems = _reading_problems(answer, packet)
    problems += _alternative_problems_v3(answer, packet)
    connection_problems, readings = _connection_problems_v3(answer, packet, baseline, proposed)
    problems += connection_problems
    _refuse(problems)
    return readings


def _is_recorded(item: dict[str, Any]) -> bool:
    """A record the Architecture or a Working Book holds: never the proposal, an instruction or a title alone."""
    if item["kind"] in ("baseline_wording", "recorded_history", "book_decision", "book_element", "recorded_phase"):
        return True
    return item["kind"] == "mechanism" and item.get("provenance") in ("preserved", "removed", "historical")


def _with_ids(alternatives: list[dict]) -> list[dict]:
    return [{"id": f"a{index}", **row} for index, row in enumerate(alternatives, start=1)]


def _evidence_label(item: dict[str, Any]) -> str:
    """A short, source-true label for one evidence item, for the page and the history. It is not a judgement."""
    kind = item["kind"]
    if kind == "mechanism":
        return f"{item.get('record_kind')} {item.get('record_id')} ({item.get('provenance')})"
    if kind == "book_element":
        return f"Book {item.get('book_number')} · {item.get('element_id')}"
    if kind in ("book_decision",):
        return f"Book {item.get('book_number')} decision on {item.get('question_id')}"
    if kind == "working_book":
        return item.get("text") or f"Book {item.get('book_number')}"
    if kind in ("baseline_wording", "recorded_history"):
        return f"{item.get('question_id')} (earlier wording)"
    if kind in ("proposed_wording", "removed"):
        return f"{item.get('question_id')} (proposal)"
    return kind


def _enrich_v2(saved: dict[str, Any], packet: dict[str, Any], approach_meanings: dict[str, str] = APPROACH_MEANINGS) -> dict[str, Any]:
    """Attach the source-true view of each cited item, read from the evidence and never from the agent's words."""
    evidence = {item["id"]: item for item in packet["evidence"]}

    def view(identifier: str) -> dict[str, Any]:
        item = evidence[identifier]
        return {"id": identifier, "kind": item["kind"], "label": _evidence_label(item)}

    for reading in saved.get("mechanisms", []):
        reading["record"] = provenance_summary(evidence[reading["evidence"]])
        reading["view"] = view(reading["evidence"])
    for link in saved.get("inheritance", []):
        link["from_view"] = view(link["from"])
        link["to_view"] = view(link["to"])
        link["evidence_views"] = [view(identifier) for identifier in link.get("evidence", [])]
    for alternative in saved.get("alternatives", []):
        alternative["approach_meaning"] = approach_meanings[alternative["approach"]]
        alternative["keeps_views"] = [view(identifier) for identifier in alternative["keeps"]]
        alternative["mechanism_views"] = [view(identifier) for identifier in alternative.get("mechanisms", [])]
        alternative["question_views"] = [{"id": identifier, "label": _question_label(evidence, identifier)}
                                         for identifier in alternative.get("questions", [])]
    for trajectory in saved.get("trajectories", []):
        trajectory["status"] = TRAJECTORY_STATUS
        for step in trajectory["steps"]:
            step["evidence_views"] = [view(identifier) for identifier in step.get("evidence", [])]
    saved["reach_meaning"] = REACH_MEANINGS[saved["reach"]]
    return saved


def _question_label(evidence: dict[str, dict[str, Any]], question_id: str) -> str:
    """The question's wording as the packet gives it (the baseline's), for the page; never the agent's paraphrase."""
    for item in evidence.values():
        if item.get("kind") == "baseline_wording" and item.get("question_id") == question_id:
            return item.get("text") or question_id
    return question_id


def _enrich_v3(saved: dict[str, Any], packet: dict[str, Any]) -> dict[str, Any]:
    """Version 3: the version 2 views, the version 3 approach meanings, and the source-true view of each connection."""
    saved = _enrich_v2(saved, packet, APPROACH_MEANINGS_V3)
    evidence = {item["id"]: item for item in packet["evidence"]}

    def view(identifier: str) -> dict[str, Any]:
        item = evidence[identifier]
        return {"id": identifier, "kind": item["kind"], "label": _evidence_label(item)}

    # What an investigation of each alternative takes as its anchors: its continuing questions and its mechanism records, read from
    # the evidence, so the served page never reconstructs an anchor from a label.
    for alternative in saved.get("alternatives", []):
        alternative["investigation_anchors"] = (
            [{"kind": "question", "id": identifier} for identifier in alternative["questions"]]
            + [{"kind": evidence[identifier]["record_kind"], "id": evidence[identifier]["record_id"]}
               for identifier in alternative.get("mechanisms", [])])

    for connection in saved.get("connections", []):
        connection["between_views"] = [view(identifier) for identifier in connection["between"]]
        connection["evidence_views"] = [view(identifier) for identifier in connection.get("evidence", [])]
        connection["standing_meaning"] = CONNECTION_MEANINGS[connection["standing"]]
        if connection.get("basis"):
            connection["basis_meaning"] = CONNECTION_BASIS_MEANINGS[connection["basis"]]
        connection["graph"] = {**connection["graph"], "meaning": RELATION_MEANINGS[connection["graph"]["status"]]}
    return saved


def consequence_correction_brief(request: HostAgentRequest, refusal: str, attempt: int) -> str:
    """The correction sent to the same responding agent after one owner refusal of one request. It quotes the owner's message
    unedited and asks for the same analysis, corrected only where the message names a rule. It never widens the request: the same
    packet, the same identifiers and no new claims. The refused response stays on record beside the message."""
    return (
        f"Correction attempt {attempt} for request {request.request_id}. The owner refused your previous answer with this "
        f"message, quoted unedited:\n\n{refusal.strip()}\n\n"
        "Return a complete corrected JSON object for the same request, under its output_contract. Change only what the message "
        "names, and keep the rest of the analysis as it was. Do not add new claims, new evidence identifiers, new questions or new "
        "mechanisms. Use only identifiers that the consequence_packet gives, and the citation_index for the field each is cited in. "
        "Return ONLY the JSON object."
    )


def complete_architecture_consequence(store: CanvasStore, payload: dict) -> dict:
    with arch._FilesystemLock(store._path(".canvas.lock")):
        base = _root(store)
        pointer = arch._read(base / "latest_request.json")
        if not pointer:
            raise ValueError("no consequence analysis request exists")
        sha = pointer["request_sha256"]
        folder = base / "requests" / sha
        request = load_host_agent_request(folder / "request.json")
        if request.role != ROLE:
            raise ValueError("wrong consequence analysis role")
        response = validate_host_agent_response(request, payload)
        prior = arch._read(folder / "response.json")
        if prior and prior != response.model_dump():
            raise arch.BeginnerConcurrencyError("a different analysis response already completed this request")
        if prior and arch._read(folder / "result.json") is not None:
            return project_architecture_consequence(store)
        # A response stored without its result (an interrupted completion) is completed now, if the proposal is still live.
        current = arch._candidate(store)
        pending = arch.project_architecture(store).get("review")
        if not _live(store, current, request, pending):
            write_host_agent_response(folder / "stale_response.json", response)
            raise arch.BeginnerConcurrencyError(
                "the pending revision, its baseline or the design context changed since this analysis was prepared; "
                "response retained as stale evidence")
        submitted = json.loads(request.user)
        version = request.settings.get("consequence_schema_version", 1)
        graph: list[dict[str, Any]] = []
        try:
            if version == 3:
                answer = ConsequenceAnswerV3.model_validate_json(response.text)
                graph = _check_answer_v3(answer, submitted["consequence_packet"], submitted["baseline_candidate"],
                                         submitted["proposed_candidate"])
            elif version == 2:
                answer = ConsequenceAnswerV2.model_validate_json(response.text)
                _check_answer_v2(answer, submitted["consequence_packet"])
            else:
                answer = ConsequenceAnswer.model_validate_json(response.text)
                _check_answer(answer, submitted["consequence_packet"])
        except ValueError as refusal:
            # A refused answer is kept as evidence of what was returned and refused, beside the owner's exact message. It is never
            # stored as the analysis, and a corrected answer may still complete the same request. Each refusal is numbered, so two
            # identical refusals are both kept and counted.
            refused = response.model_dump()
            directory = folder / "refused"
            directory.mkdir(parents=True, exist_ok=True)
            name = f"{len(list(directory.glob('*.json'))) + 1:02d}-{_digest(refused)[:16]}"
            _atomic_json_write(directory / f"{name}.json", refused)
            (directory / f"{name}.refusal.txt").write_text(str(refusal).strip() + "\n", encoding="utf-8")
            raise
        dumped = answer.model_dump(mode="json", by_alias=True)
        # How this analysis was reached: first pass, or after how many owner refusals of this same request. Historical analyses
        # carry no such record and are read without it.
        refused_before = len(list((folder / "refused").glob("*.json"))) if (folder / "refused").exists() else 0
        saved = {
            **dumped,
            "alternatives": _with_ids(dumped["alternatives"]),
            "schema": SCHEMA_V3 if version == 3 else (SCHEMA_V2 if version == 2 else SCHEMA),
            "authority": AUTHORITY,
            "revision_request_sha256": request.settings["review_request_sha256"],
            "baseline_request_sha256": request.settings["baseline_candidate_request_sha256"],
            "proposal_sha256": request.settings["proposal_sha256"],
            "evidence": submitted["consequence_packet"],
            "evidence_sha256": submitted["consequence_packet"]["evidence_sha256"],
            "completion": {"attempt": refused_before + 1, "refused_attempts": refused_before, "first_pass": refused_before == 0},
        }
        if version == 3:
            saved["connections"] = [{**row, "graph": reading} for row, reading in zip(dumped["connections"], graph)]
            saved = _enrich_v3(saved, submitted["consequence_packet"])
        elif version == 2:
            saved = _enrich_v2(saved, submitted["consequence_packet"])
        write_host_agent_response(folder / "response.json", response)
        _atomic_json_write(folder / "result.json", saved)
    return project_architecture_consequence(store)


def _analysis_rows(store: CanvasStore, pending: dict | None, current: dict | None, limit: int, latest: str | None) -> list[dict]:
    """Completed analyses on this canvas, newest first, each with its standing read now."""
    requests_root = _root(store) / "requests"
    if not requests_root.is_dir():
        return []
    rows = []
    for folder in requests_root.iterdir():
        try:
            # One damaged folder is named by its absence, and must not hide the rest.
            result = arch._read(folder / "result.json")
            if result is None:
                continue
            request = load_host_agent_request(folder / "request.json")
        except Exception:  # noqa: BLE001
            continue
        rows.append((request.created_at, folder.name, request, result))
    rows.sort(key=lambda row: (row[0], row[1]), reverse=True)
    return [{
        "request_sha256": name,
        "revision_request_sha256": request.settings["review_request_sha256"],
        "standing": _standing(store, request, pending, current, latest=(name == latest)),
        "concern_count": len(result.get("concerns", [])),
        "alternative_titles": [row["title"] for row in result.get("alternatives", [])],
    } for _created, name, request, result in rows[:limit]]


def _vocabulary() -> dict[str, Any]:
    """The shared vocabulary the served page reads, so its labels and definitions are the owner's own."""
    return {"approaches": APPROACH_MEANINGS, "approaches_v3": APPROACH_MEANINGS_V3, "retain_legacy": RETAIN_LEGACY_MEANING,
            "reach": REACH_MEANINGS, "connection_standings": CONNECTION_MEANINGS, "connection_bases": CONNECTION_BASIS_MEANINGS,
            "graph": RELATION_MEANINGS, "contract": CONTRACT_VERSION,
            "inheritance_kinds": INHERITANCE_MEANINGS, "provenance": PROVENANCE_MEANING, "routes": ROUTE_MEANING,
            "trajectory_status": TRAJECTORY_STATUS,
            "stages": ["local_decision", "mechanism_transformation", "tension", "opportunity", "inheritance", "long_horizon"],
            "bases": {"recorded": "cites a recorded item",
                      "interpreted": "the agent's reading of recorded material",
                      "speculative": "a possibility the record does not establish"}}


def project_architecture_consequence(store: CanvasStore) -> dict[str, Any]:
    """Read-only projection of the latest analysis, its standing and the earlier analyses, with the shared vocabulary."""
    projection = _project_consequence(store)
    projection["vocabulary"] = _vocabulary()
    return projection


def _project_consequence(store: CanvasStore) -> dict[str, Any]:
    """Read-only: the latest analysis, its standing against the pending revision as it is now, and earlier analyses."""
    projection = arch.project_architecture(store)
    pending = projection.get("review")
    current = arch._candidate(store)
    base = _root(store)
    pointer = arch._read(base / "latest_request.json")
    latest = pointer.get("request_sha256") if pointer else None
    history = _analysis_rows(store, pending, current, MAX_HISTORY, latest)
    if not pointer:
        return {"schema": SCHEMA, "authority": AUTHORITY, "status": "not_started", "standing": None, "request": None,
                "request_sha256": None, "result": None, "history": history,
                "pending_revision_request_sha256": pending["request_sha256"] if pending else None}
    sha = pointer.get("request_sha256", "")
    if not isinstance(sha, str) or not re.fullmatch(r"[0-9a-f]{64}", sha):
        raise ValueError("invalid consequence analysis pointer")
    request = load_host_agent_request(base / "requests" / sha / "request.json")
    if request.role != ROLE:
        raise ValueError("unexpected consequence analysis host role")
    try:
        result = arch._read(base / "requests" / sha / "result.json")
    except (OSError, ValueError):
        # A damaged result is named as unreadable; the earlier analyses stay readable.
        return {"schema": SCHEMA, "authority": AUTHORITY, "status": "unreadable", "standing": None, "request": None,
                "request_sha256": sha, "revision_request_sha256": request.settings["review_request_sha256"],
                "result": None, "history": history,
                "pending_revision_request_sha256": pending["request_sha256"] if pending else None}
    standing = _standing(store, request, pending, current, latest=True)
    if result is None:
        status = "awaiting_host_agent" if standing == "current" else "stale"
    else:
        status = "ready"
    return {
        "schema": SCHEMA,
        "authority": AUTHORITY,
        "status": status,
        "standing": standing,
        "request_sha256": sha,
        "revision_request_sha256": request.settings["review_request_sha256"],
        "request": request.model_dump() if result is None and standing == "current" else None,
        "result": result,
        "history": history,
        "pending_revision_request_sha256": pending["request_sha256"] if pending else None,
    }


def consequence_origin(store: CanvasStore, origin: dict, anchors: list) -> dict:
    """The check an investigation makes when it is taken from an analysed alternative. Raises ValueError if it may not be.

    The alternative's questions are identities. An investigation concerns exactly those questions, and only while each is
    still a continuing question of the current working Architecture. Nothing is rebound to a replacement by wording. A version 3
    alternative also names mechanisms: the investigation takes them as ``{"kind", "id"}`` anchors, and a mechanism the proposal
    introduces is not in the current Architecture, so it is refused. ``anchors`` may name a question by its identifier alone.
    """
    if not isinstance(origin, dict):
        raise ValueError("a consequence alternative is named by its analysis and its alternative id")
    sha = origin.get("request_sha256") if isinstance(origin.get("request_sha256"), str) else ""
    alternative_id = origin.get("alternative_id") if isinstance(origin.get("alternative_id"), str) else ""
    if not re.fullmatch(r"[0-9a-f]{64}", sha) or not alternative_id:
        raise ValueError("a consequence alternative is named by its analysis and its alternative id")
    folder = _root(store) / "requests" / sha
    if not (folder / "request.json").is_file():
        raise ValueError("that consequence analysis is not recorded on this canvas")
    result = arch._read(folder / "result.json")
    if result is None:
        raise ValueError("that consequence analysis is not completed")
    alternative = next((row for row in result.get("alternatives", []) if row["id"] == alternative_id), None)
    if alternative is None:
        raise ValueError("that alternative is not in the consequence analysis")
    version_three = result.get("schema") == SCHEMA_V3
    recorded_items = {item["id"]: item for item in (result.get("evidence") or {}).get("evidence", [])}

    def anchor_key(anchor: Any) -> tuple[str, str]:
        if isinstance(anchor, str):
            return ("question", anchor)
        if isinstance(anchor, dict) and isinstance(anchor.get("kind"), str) and isinstance(anchor.get("id"), str):
            return (anchor["kind"], anchor["id"])
        raise ValueError("an investigation names each anchor by its kind and identifier")

    supplied = {anchor_key(anchor) for anchor in anchors}
    expected = {("question", identifier) for identifier in alternative["questions"]}
    if version_three:
        expected |= {(recorded_items[identifier]["record_kind"], recorded_items[identifier]["record_id"])
                     for identifier in alternative.get("mechanisms", []) if identifier in recorded_items}
    if supplied != expected:
        raise ValueError("the investigation must concern exactly the questions and mechanisms the alternative names; "
                         "it cannot substitute others" if version_three else
                         "the investigation must concern exactly the questions the alternative names; "
                         "it cannot substitute other questions")
    for identifier in alternative.get("mechanisms", []) if version_three else []:
        item = recorded_items.get(identifier) or {}
        if item.get("provenance") == "introduced":
            raise ValueError(f"{item.get('record_kind')} {item.get('record_id')} is introduced by this proposal and is not in the "
                             "current Architecture; it can be investigated once the revision is applied")
    continuing = {question["id"] for question in project_architecture_questions(store)["questions"]
                  if question["standing"] == "continuing"}
    missing = [identifier for identifier in alternative["questions"] if identifier not in continuing]
    if missing:
        raise ValueError("a question this alternative concerns is no longer open: " + ", ".join(missing) +
                         ". It is not rebound to another question.")
    keys = ("title", "approach", "summary", "questions") + (("mechanisms",) if version_three else ())
    text = json.dumps({key: alternative.get(key) for key in keys}, ensure_ascii=False, sort_keys=True)
    # An investigation starts only from the latest analysis of the proposal on screen. An earlier analysis, or one whose
    # revision has been applied or replaced, is history: its alternatives are read there, not investigated from here.
    request = load_host_agent_request(folder / "request.json")
    pointer = arch._read(_root(store) / "latest_request.json") or {}
    standing = _standing(store, request, arch.project_architecture(store).get("review"), arch._candidate(store),
                         latest=(pointer.get("request_sha256") == sha))
    if standing != "current":
        raise ValueError("only the latest analysis of the proposal on screen can be investigated; this one is "
                         + ("about an earlier or replaced proposal" if standing == "superseded" else standing.replace("_", " ")))
    # The object of retention and the mechanisms the alternative names travel with it as provenance. They add context to the
    # investigation; they never widen what the revision is authorized to change.
    packet_items = {item["id"]: item for item in (result.get("evidence") or {}).get("evidence", [])}
    return {"request_sha256": sha, "alternative_id": alternative_id, "title": alternative["title"],
            "approach": alternative["approach"], "questions": list(alternative["questions"]),
            "keeps": [provenance_summary(packet_items[i]) if packet_items.get(i, {}).get("kind") == "mechanism"
                      else {"evidence_kind": packet_items.get(i, {}).get("kind"),
                            "question_id": packet_items.get(i, {}).get("question_id"),
                            "proposal_status": packet_items.get(i, {}).get("proposal_status")}
                      for i in alternative.get("keeps", [])],
            "mechanisms": [provenance_summary(packet_items[i]) for i in alternative.get("mechanisms", [])
                           if i in packet_items],
            "alternative_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest()}
