from __future__ import annotations

import subprocess
import sys

import pytest
from pydantic import ValidationError

from auteur.beginner.contracts import (
    AcceptedMilestoneReference,
    DecisionStage,
    LifecycleStatus,
    RevisionRef,
    SessionEnvelope,
    StageAvailability,
    StageStatus,
    WorkingDecision,
)
from auteur.beginner.mystery_adapter import (
    EvidenceReference,
    QualificationCard,
    QualificationInventory,
    QualificationStage,
    mystery_qualification_inventory,
    validate_mystery_card_evidence,
)
from auteur.beginner.guidance import (
    BeginnerGuidance,
    NarrativeConsequence,
    OptionImpact,
    SemanticArea,
    register_evidence_source,
    unregister_evidence_source,
    guidance_for,
    register_guidance_adapter,
    unregister_guidance_adapter,
)
from auteur.beginner.projections import evidence_label
from auteur.mystery.core_templates import HowdunitTemplate
from auteur.mystery.validation import RuleSet
from auteur.story_design_packs.models import PackProvenance


def _all_stages_available_session() -> SessionEnvelope:
    session = SessionEnvelope.new(
        project_id="semantic-impact-test",
        guidance_genre="mystery",
        premise="A sealed elevator murder mystery.",
    )
    return session.model_copy(update={
        "stages": {
            stage: status.model_copy(update={"availability": StageAvailability.AVAILABLE})
            for stage, status in session.stages.items()
        }
    })


def test_narrative_consequence_supports_relevance_driven_semantic_fields() -> None:
    consequence = NarrativeConsequence(
        semantic_area=SemanticArea.STRUCTURE,
        summary="Even clues keep the reader reasoning throughout the inquiry.",
        implications=("The reversal must reinterpret evidence.",),
        what_becomes_easier=("Maintaining a fair inference path",),
        risks=("The middle may feel less urgent without setbacks",),
    )
    assert consequence.semantic_area is SemanticArea.STRUCTURE
    assert consequence.what_becomes_harder == ()
    assert consequence.compensating_requirements == ()


def test_narrative_consequence_rejects_blank_populated_fields() -> None:
    with pytest.raises(ValueError, match="nonblank"):
        NarrativeConsequence(
            semantic_area=SemanticArea.IDENTITY,
            summary=" ",
        )


def test_option_impact_remains_compatible_and_projects_derived_guidance() -> None:
    guidance = guidance_for("discover.story-experience", _all_stages_available_session())
    impact = guidance.option_impacts[guidance.recommendation]
    assert isinstance(impact, OptionImpact)
    assert impact.authority_status == "DERIVED / NOT CANON"
    assert impact.narrative_consequences


def test_every_mystery_option_has_relevant_non_generic_consequences() -> None:
    session = _all_stages_available_session()
    inventory = mystery_qualification_inventory()
    for card in inventory.cards:
        guidance = guidance_for(card.card_id, session)
        assert set(guidance.option_impacts) == set(card.options)
        for option in card.options:
            impact = guidance.option_impacts[option]
            assert impact.narrative_consequences
            assert all(item.summary.strip() for item in impact.narrative_consequences)
            rendered = " ".join(
                [impact.audience_experience, impact.aesthetic_framing,
                 impact.narrative_structure]
                + list(impact.tradeoffs)
                + [item.summary for item in impact.narrative_consequences]
            ).casefold()
            assert "a different approach" not in rendered
            assert "emphasizes a different" not in rendered


def test_irrelevant_semantic_areas_are_omitted() -> None:
    guidance = guidance_for("discover.story-experience", _all_stages_available_session())
    impact = guidance.option_impacts["Detective procedural"]
    areas = {item.semantic_area for item in impact.narrative_consequences}
    assert SemanticArea.IDENTITY in areas
    assert SemanticArea.STRUCTURE in areas
    assert SemanticArea.REALIZATION not in areas
    assert SemanticArea.EXPRESSION not in areas


def test_mystery_inventory_is_small_sealed_and_stable() -> None:
    inventory = mystery_qualification_inventory()

    assert inventory.stage_counts == {
        QualificationStage.DISCOVER: 3,
        QualificationStage.STORY_IDENTITY: 4,
        QualificationStage.STRUCTURE: 3,
    }
    assert [card.card_id for card in inventory.cards] == [
        "discover.story-experience",
        "discover.personal-stakes",
        "discover.investigation-approach",
        "story_identity.protagonist-want",
        "story_identity.relationship-pressure",
        "story_identity.information-contract",
        "story_identity.truth-opposition",
        "structure.investigation-disruption",
        "structure.clue-distribution",
        "structure.final-revelation",
    ]
    assert isinstance(inventory.cards, tuple)


def test_mystery_impacts_are_curated_for_each_qualification_card() -> None:
    session = SessionEnvelope.new(
        project_id="impact-test",
        guidance_genre="mystery",
        premise="A sealed elevator murder mystery.",
    )
    session = session.model_copy(update={
        "stages": {
            stage: status.model_copy(update={"availability": StageAvailability.AVAILABLE})
            for stage, status in session.stages.items()
        }
    })
    for card in mystery_qualification_inventory().cards:
        guidance = guidance_for(card.card_id, session)
        assert set(guidance.option_impacts) == set(card.options)
        assert all(
            "Experience the story through" not in impact.audience_experience
            for impact in guidance.option_impacts.values()
        )


def test_fairness_confidence_evidence_has_beginner_label() -> None:
    card = mystery_qualification_inventory().card("story_identity.information-contract")
    assert "fairness_confidence" not in evidence_label(card)
    assert "reader fairness confidence" in " ".join(evidence_label(card)).lower()


def test_inventory_cards_reference_existing_mystery_subjects() -> None:
    inventory = mystery_qualification_inventory()
    template = HowdunitTemplate()
    rule_ids = {rule.rule_id for rule in RuleSet("howdunit").rules}

    assert all(card.source_subject for card in inventory.cards)
    assert any("clue" in card.source_subject.casefold() for card in inventory.cards)
    assert any("solution" in card.source_subject.casefold() for card in inventory.cards)
    assert all(card.options for card in inventory.cards)
    expected_phase_names = {
        "discover.story-experience": {"genre_contract"},
        "discover.personal-stakes": {"structural_forces"},
        "discover.investigation-approach": {"investigation_style"},
        "story_identity.protagonist-want": {"structural_forces"},
        "story_identity.relationship-pressure": {"structural_forces"},
        "story_identity.information-contract": {"fairness_confidence"},
        "story_identity.truth-opposition": {"structural_forces"},
        "structure.investigation-disruption": {"pacing_rhythm"},
        "structure.clue-distribution": {"clue_distribution"},
        "structure.final-revelation": {"solution_density"},
    }
    for card in inventory.cards:
        phase_names: set[str] = set()
        supported_labels: set[str] = set()
        claims = {reference.claim for reference in card.evidence_references}
        assert claims >= {"decision", "recommendation", "option", "consequence"}
        for reference in card.evidence_references:
            assert isinstance(reference, EvidenceReference)
            if reference.source == "HowdunitTemplate":
                assert reference.phase in template.phases
                assert reference.phase is not None
                phase_names.add(template.phases[reference.phase])
                assert reference.field == template.phases[reference.phase]
                supported_labels.update(option.label for option in template.options[reference.phase])
                assert set(reference.option_labels) <= supported_labels
            else:
                assert reference.rule_id in rule_ids
        assert phase_names == expected_phase_names[card.card_id]
        assert set(card.options) <= supported_labels
        assert card.recommendation in supported_labels


def test_story_experience_options_have_distinct_structured_impacts() -> None:
    session = SessionEnvelope.new("project-1", "mystery", "A sealed elevator mystery.")
    guidance = guidance_for("discover.story-experience", session)

    assert set(guidance.option_impacts) == set(guidance.alternatives) | {guidance.recommendation}
    impacts = guidance.option_impacts
    assert impacts["Detective procedural"].audience_experience != impacts["Locked-room puzzle"].audience_experience
    assert impacts["Detective procedural"].narrative_structure != impacts["Intricate puzzle structure"].narrative_structure
    assert impacts["Locked-room puzzle"].expected_tropes
    assert impacts["Intricate puzzle structure"].tradeoffs


def test_guidance_includes_all_working_decisions_and_accepted_snapshot_details() -> None:
    session = SessionEnvelope.new("project-1", "mystery", "A missing heir returns home.")
    discover = StageStatus(
        stage=DecisionStage.DISCOVER,
        lifecycle=LifecycleStatus.WORKING,
        availability=StageAvailability.AVAILABLE,
        working_decision=WorkingDecision(
            stage=DecisionStage.DISCOVER,
            question="Which truth is being hidden?",
            options=["the inheritance", "the disappearance"],
        ),
    )
    identity = StageStatus(
        stage=DecisionStage.STORY_IDENTITY,
        lifecycle=LifecycleStatus.WORKING,
        availability=StageAvailability.AVAILABLE,
        working_decision=WorkingDecision(
            stage=DecisionStage.STORY_IDENTITY,
            question="What does the investigator risk?",
            options=["reputation", "belonging"],
        ),
    )
    full_state = session.model_copy(
        update={
            "stages": {
                **session.stages,
                DecisionStage.DISCOVER: discover,
                DecisionStage.STORY_IDENTITY: identity,
            },
            "accepted_milestones": [
                AcceptedMilestoneReference(
                    milestone_id="identity-accepted",
                    revision=RevisionRef(artifact_id="identity-42", revision=7),
                    accepted_content="accepted narrative identity",
                    fingerprint="fingerprint-v7",
                )
            ],
        }
    )
    assert discover.working_decision is not None
    changed_upstream = full_state.model_copy(
        update={
            "stages": {
                **full_state.stages,
                DecisionStage.DISCOVER: discover.model_copy(
                    update={
                        "working_decision": discover.working_decision.model_copy(
                            update={"question": "Which promise must be kept?"}
                        )
                    }
                ),
            }
        }
    )
    changed_accepted = full_state.model_copy(
        update={
            "accepted_milestones": [
                full_state.accepted_milestones[0].model_copy(
                    update={"revision": RevisionRef(artifact_id="identity-43", revision=8)}
                )
            ]
        }
    )

    projected = guidance_for("discover.story-experience", full_state)

    assert "Which truth is being hidden?" in projected.context_summary
    assert "What does the investigator risk?" in projected.context_summary
    assert "identity-42" in projected.context_summary
    assert '"revision":7' in projected.context_summary
    assert "accepted narrative identity" in projected.context_summary
    assert "fingerprint-v7" in projected.context_summary
    assert guidance_for("discover.story-experience", changed_upstream) != projected
    assert guidance_for("discover.story-experience", changed_accepted) != projected


def test_relevant_working_choice_selects_supported_recommendation() -> None:
    session = SessionEnvelope.new("project-1", "mystery", "A missing heir returns home.")
    session = session.model_copy(
        update={
            "stages": {
                **session.stages,
                DecisionStage.STORY_IDENTITY: session.stages[DecisionStage.STORY_IDENTITY].model_copy(
                    update={"lifecycle": LifecycleStatus.WORKING, "availability": StageAvailability.AVAILABLE}
                ),
            }
        }
    )
    baseline = guidance_for("story_identity.protagonist-want", session)
    identity = session.stages[DecisionStage.STORY_IDENTITY].model_copy(
        update={
            "lifecycle": LifecycleStatus.WORKING,
            "availability": StageAvailability.AVAILABLE,
            "working_decision": WorkingDecision(
                stage=DecisionStage.STORY_IDENTITY,
                question="Which want is active?",
                options=["Want: Identify the culprit"],
                selected_option="Want: Identify the culprit",
            )
        }
    )
    committed = session.model_copy(
        update={"stages": {**session.stages, DecisionStage.STORY_IDENTITY: identity}}
    )
    changed = guidance_for("story_identity.protagonist-want", committed)

    assert baseline.recommendation == "Want: Solve the puzzle"
    assert changed.recommendation == "Want: Identify the culprit"
    assert "current story identity choice" in changed.rationale
    assert changed.rationale != baseline.rationale


def test_recommendation_ignores_locked_or_unselected_prose() -> None:
    session = SessionEnvelope.new("project-1", "mystery", "A premise.")
    baseline = guidance_for("discover.story-experience", session)
    selected = StageStatus(
        stage=DecisionStage.DISCOVER,
        lifecycle=LifecycleStatus.WORKING,
        availability=StageAvailability.AVAILABLE,
        working_decision=WorkingDecision(
            stage=DecisionStage.DISCOVER,
            question="A rejected prose suggestion",
            options=["Police/investigation procedural"],
            selected_option="Police/investigation procedural",
        ),
    )
    locked_working = selected.model_copy(update={"availability": StageAvailability.LOCKED})
    locked_complete = selected.model_copy(
        update={"lifecycle": LifecycleStatus.COMPLETE, "availability": StageAvailability.LOCKED}
    )
    rejected = selected.model_copy(
        update={
            "working_decision": WorkingDecision(
                stage=DecisionStage.DISCOVER,
                question="Rejected prose should not select a mode",
                options=["Police/investigation procedural"],
            )
        }
    )
    locked_working_session = session.model_copy(
        update={"stages": {**session.stages, DecisionStage.DISCOVER: locked_working}}
    )
    locked_complete_session = session.model_copy(
        update={"stages": {**session.stages, DecisionStage.DISCOVER: locked_complete}}
    )
    rejected_session = session.model_copy(update={"stages": {**session.stages, DecisionStage.DISCOVER: rejected}})

    with pytest.raises(ValueError, match="guidance card stage is locked"):
        guidance_for("discover.story-experience", locked_working_session)
    with pytest.raises(ValueError, match="guidance card stage is locked"):
        guidance_for("discover.story-experience", locked_complete_session)
    assert guidance_for("discover.story-experience", rejected_session).recommendation == baseline.recommendation


def test_fresh_session_denies_future_locked_card() -> None:
    session = SessionEnvelope.new("project-1", "mystery", "A premise.")

    with pytest.raises(ValueError, match="guidance card stage is locked"):
        guidance_for("structure.investigation-disruption", session)


def test_evidence_rejects_impossible_phase() -> None:
    with pytest.raises(ValidationError):
        EvidenceReference(
            claim="decision",
            source="HowdunitTemplate",
            phase=999,
            field="invented",
            option_labels=("invented",),
        )


def test_card_evidence_rejects_unrelated_phase_mapping() -> None:
    card = mystery_qualification_inventory().card("story_identity.relationship-pressure")
    altered = card.model_copy(
        update={
            "evidence_references": tuple(
                reference.model_copy(update={"field": "solution_density"})
                if reference.claim == "decision" else reference
                for reference in card.evidence_references
            )
        }
    )

    with pytest.raises(ValueError, match="canonical card definition"):
        validate_mystery_card_evidence(altered)


@pytest.mark.parametrize(
    "field, value",
    [("title", "Altered title"), ("question", "Altered question"), ("source_subject", "Altered source")],
)
def test_canonical_card_definition_rejects_same_id_mutation(field: str, value: str) -> None:
    card = mystery_qualification_inventory().card("discover.story-experience")
    altered = card.model_copy(update={field: value})

    with pytest.raises(ValueError, match="canonical card definition"):
        validate_mystery_card_evidence(altered)


def test_latest_accepted_revision_controls_recommendation() -> None:
    session = SessionEnvelope.new("project-1", "mystery", "A premise.")
    latest = AcceptedMilestoneReference(
        milestone_id="stakes",
        revision=RevisionRef(artifact_id="artifact-a", revision=2),
        accepted_content="newer content",
        selected_option="Stakes: Order restored",
    )
    older = AcceptedMilestoneReference(
        milestone_id="stakes",
        revision=RevisionRef(artifact_id="artifact-z", revision=1),
        accepted_content="older content",
        selected_option="Stakes: Justice served",
    )
    state = session.model_copy(update={"accepted_milestones": [latest, older]})

    guidance = guidance_for("discover.personal-stakes", state)

    assert guidance.recommendation == "Stakes: Order restored"


def test_latest_accepted_commitment_uses_persisted_order_not_alphabetic_sort() -> None:
    session = SessionEnvelope.new("project-1", "mystery", "A premise.")
    state = session.model_copy(
        update={
            "accepted_milestones": [
                AcceptedMilestoneReference(
                    milestone_id="alpha",
                    revision=RevisionRef(artifact_id="artifact-z", revision=2),
                    selected_option="Stakes: Justice served",
                ),
                AcceptedMilestoneReference(
                    milestone_id="zeta",
                    revision=RevisionRef(artifact_id="artifact-a", revision=2),
                    selected_option="Stakes: Order restored",
                ),
            ]
        }
    )

    assert guidance_for("discover.personal-stakes", state).recommendation == "Stakes: Order restored"


def test_commitment_summary_only_uses_available_selected_working_decisions() -> None:
    session = SessionEnvelope.new("project-1", "mystery", "A premise.")
    selected = StageStatus(
        stage=DecisionStage.DISCOVER,
        lifecycle=LifecycleStatus.WORKING,
        availability=StageAvailability.AVAILABLE,
        working_decision=WorkingDecision(
            stage=DecisionStage.DISCOVER,
            question="Untrusted prose question",
            options=["Detective procedural"],
            selected_option="Detective procedural",
        ),
    )
    blocked = selected.model_copy(update={"lifecycle": LifecycleStatus.BLOCKED})
    state = session.model_copy(
        update={
            "stages": {
                **session.stages,
                DecisionStage.DISCOVER: selected,
                DecisionStage.STORY_IDENTITY: StageStatus(
                    stage=DecisionStage.STORY_IDENTITY,
                    lifecycle=LifecycleStatus.WORKING,
                    availability=StageAvailability.AVAILABLE,
                ),
            }
        }
    )
    blocked_state = state.model_copy(update={"stages": {**state.stages, DecisionStage.DISCOVER: blocked}})

    committed = guidance_for("story_identity.protagonist-want", state)
    ignored = guidance_for("story_identity.protagonist-want", blocked_state)

    assert "Discovery: Detective procedural" in committed.rationale
    assert "Discovery: Detective procedural" not in ignored.rationale


def test_rationale_uses_sanitized_commitments_not_persisted_session_details() -> None:
    session = SessionEnvelope.new("project-1", "mystery", "A missing heir returns home.")
    blocked = StageStatus(
        stage=DecisionStage.DISCOVER,
        lifecycle=LifecycleStatus.BLOCKED,
        availability=StageAvailability.AVAILABLE,
        working_decision=WorkingDecision(
            stage=DecisionStage.DISCOVER,
            question="Do not expose this blocked question",
            options=["Detective procedural", "Locked-room puzzle"],
            selected_option=None,
        ),
    )
    state = session.model_copy(
        update={
            "stages": {
                **session.stages,
                DecisionStage.DISCOVER: blocked,
                DecisionStage.STORY_IDENTITY: StageStatus(
                    stage=DecisionStage.STORY_IDENTITY,
                    lifecycle=LifecycleStatus.WORKING,
                    availability=StageAvailability.AVAILABLE,
                ),
            }
        }
    )
    accepted = AcceptedMilestoneReference(
        milestone_id="internal-milestone",
        revision=RevisionRef(artifact_id="artifact-secret", revision=17),
        selected_option="Detective procedural",
    )
    state = state.model_copy(update={"accepted_milestones": [accepted]})

    rationale = guidance_for("story_identity.protagonist-want", state).rationale

    assert "Do not expose this blocked question" not in rationale
    assert "artifact-secret" not in rationale
    assert "17" not in rationale
    assert "BLOCKED" not in rationale
    assert "session_version" not in rationale


def test_equal_revision_accepted_commitment_uses_latest_list_occurrence() -> None:
    session = SessionEnvelope.new("project-1", "mystery", "A premise.")
    state = session.model_copy(
        update={
            "accepted_milestones": [
                AcceptedMilestoneReference(
                    milestone_id="same",
                    revision=RevisionRef(artifact_id="artifact-z", revision=2),
                    selected_option="Stakes: Justice served",
                ),
                AcceptedMilestoneReference(
                    milestone_id="same",
                    revision=RevisionRef(artifact_id="artifact-a", revision=2),
                    selected_option="Stakes: Order restored",
                ),
            ]
        }
    )

    assert guidance_for("discover.personal-stakes", state).recommendation == "Stakes: Order restored"


def test_tradeoffs_match_each_card_source_field() -> None:
    inventory = mystery_qualification_inventory()
    expected_terms = {
        "discover.investigation-approach": ("deduction", "intuitive", "procedure"),
        "story_identity.information-contract": ("confidence", "solv", "reread"),
        "structure.investigation-disruption": ("tempo", "rhythm", "pace"),
        "structure.clue-distribution": ("timing", "inference", "distribution"),
    }
    for card_id, terms in expected_terms.items():
        text = " ".join(inventory.card(card_id).warnings_or_tensions).casefold()
        assert all(term in text for term in terms)

    with pytest.raises(ValidationError):
        EvidenceReference(
            claim="option",
            source="HowdunitTemplate",
            phase=2,
            field="genre_contract",
            option_labels=("invented option",),
        )
    with pytest.raises(ValidationError):
        EvidenceReference(
            claim="consequence",
            source="HowdunitTemplate",
            phase=2,
            field="genre_contract",
            option_labels=("Detective procedural",),
            rule_id="howdunit.unknown.rule",
        )


@pytest.mark.parametrize("consequences", [(), ("",), ("   ",)])
def test_qualification_card_rejects_empty_or_blank_consequences(
    consequences: tuple[str, ...],
) -> None:
    card = mystery_qualification_inventory().card("discover.story-experience")
    payload = card.model_dump()
    payload["downstream_consequences"] = consequences

    with pytest.raises(ValidationError, match="downstream_consequences"):
        QualificationCard.model_validate(payload)


def test_guidance_routing_uses_an_extensible_adapter_registry() -> None:
    class StubAdapter:
        genre = "stub"

        @staticmethod
        def inventory() -> QualificationInventory:
            return mystery_qualification_inventory()

        @staticmethod
        def validate_inventory(inventory: QualificationInventory) -> None:
            assert inventory.cards

        @staticmethod
        def pack_sources() -> tuple[PackProvenance, ...]:
            return (PackProvenance(pack_id="stub", version="1", content_hash="stable"),)

        @staticmethod
        def tutor_session_fingerprints() -> dict[str, str]:
            return {"stub": "stable"}

    adapter = StubAdapter()
    register_guidance_adapter(adapter)
    try:
        with pytest.raises(ValueError, match="already registered"):
            register_guidance_adapter(adapter)
        session = SessionEnvelope.new("project-1", "stub", "A test premise.")
        guidance = guidance_for("discover.story-experience", session)
        assert guidance.card_id == "discover.story-experience"
    finally:
        unregister_guidance_adapter("stub")


def test_evidence_provider_registration_rejects_collisions() -> None:
    class Source:
        @staticmethod
        def validate(reference: EvidenceReference) -> None:
            return None

    source = Source()
    register_evidence_source("test-source", source)
    try:
        with pytest.raises(ValueError, match="already registered"):
            register_evidence_source("test-source", source)
    finally:
        unregister_evidence_source("test-source")


def test_beginner_guidance_projects_to_existing_tutor_decision_card() -> None:
    from auteur.story_design_packs.models import DecisionCard, TutorDepth

    guidance = guidance_for(
        "discover.story-experience",
        SessionEnvelope.new("project-1", "mystery", "A missing heir returns home."),
    )
    card = guidance.to_decision_card()
    tutor_session = guidance.to_tutor_session()

    assert isinstance(card, DecisionCard)
    assert card.decision == guidance.question
    assert card.recommendation == guidance.recommendation
    assert card.authority_status == "DERIVED / NOT CANON"
    assert card.depth is TutorDepth.RECOMMEND
    assert tutor_session.card == card
    assert tutor_session.source_fingerprints.items() >= guidance.tutor_session_fingerprints.items()
    assert "beginner.guidance.context" in tutor_session.source_fingerprints
    assert {source.pack_id for source in guidance.pack_sources} == {"howdunit", "howdunit-rules"}


def test_tutor_session_identity_includes_full_beginner_context(tmp_path) -> None:
    from auteur.story_design_packs.session import TutorSessionStore

    base = SessionEnvelope.new("project-1", "mystery", "A missing heir returns home.")
    selected = base.model_copy(
        update={
            "stages": {
                **base.stages,
                DecisionStage.DISCOVER: StageStatus(
                    stage=DecisionStage.DISCOVER,
                    lifecycle=LifecycleStatus.WORKING,
                    availability=StageAvailability.AVAILABLE,
                    working_decision=WorkingDecision(
                        stage=DecisionStage.DISCOVER,
                        question="Which lens?",
                        options=["Detective procedural", "Locked-room puzzle"],
                        selected_option="Locked-room puzzle",
                    ),
                ),
            }
        }
    )
    other_project = selected.model_copy(update={"project_id": "project-2"})

    first = guidance_for("discover.story-experience", base).to_tutor_session()
    same = guidance_for("discover.story-experience", base).to_tutor_session()
    changed = guidance_for("discover.story-experience", selected).to_tutor_session()
    other = guidance_for("discover.story-experience", other_project).to_tutor_session()

    assert first.session_id == same.session_id
    assert first.source_fingerprints == same.source_fingerprints
    assert changed.session_id != first.session_id
    assert changed.source_fingerprints != first.source_fingerprints
    assert other.session_id != changed.session_id
    assert other.source_fingerprints != changed.source_fingerprints

    store = TutorSessionStore(tmp_path)
    store.save(first)
    store.save(changed)
    store.save(other)
    assert store.load(first.session_id).card_id == first.card_id
    assert store.load(changed.session_id).card_id == changed.card_id
    assert store.load(other.session_id).card_id == other.card_id


@pytest.mark.parametrize("consequences", [(), [], ("   ",)])
def test_projection_rejects_empty_or_blank_downstream_consequence(
    consequences: tuple[str, ...] | list[str],
) -> None:
    guidance = guidance_for(
        "discover.story-experience",
        SessionEnvelope.new("project-1", "mystery", "A missing heir returns home."),
    )
    invalid = guidance.model_copy(update={"downstream_consequences": consequences})

    with pytest.raises(ValueError, match="downstream_consequences"):
        invalid.to_decision_card()


@pytest.mark.parametrize("consequences", [(), ("",), ("   ",)])
def test_beginner_guidance_rejects_empty_or_blank_consequences(
    consequences: tuple[str, ...],
) -> None:
    guidance = guidance_for(
        "discover.story-experience",
        SessionEnvelope.new("project-1", "mystery", "A missing heir returns home."),
    )
    payload = guidance.model_dump()
    payload["downstream_consequences"] = consequences

    with pytest.raises(ValidationError, match="downstream_consequences"):
        BeginnerGuidance.model_validate(payload)


def test_guidance_for_mystery_registers_in_a_fresh_process() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            "from auteur.beginner.contracts import SessionEnvelope; "
            "from auteur.beginner.guidance import guidance_for; "
            "print(guidance_for('discover.story-experience', "
            "SessionEnvelope.new('p', 'mystery', 'premise')).card_id)",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    assert result.stdout.strip() == "discover.story-experience"


def test_guidance_contains_teaching_decision_and_evidence_contract() -> None:
    session = SessionEnvelope.new("project-1", "mystery", "A missing heir returns home.")

    guidance = guidance_for("discover.story-experience", session)

    assert guidance.card_id == "discover.story-experience"
    assert guidance.stage is QualificationStage.DISCOVER
    assert guidance.why_this_matters
    assert guidance.narrative_principle
    assert guidance.recommendation
    assert guidance.rationale
    assert guidance.alternatives
    assert guidance.tradeoffs
    assert guidance.downstream_consequences
    assert guidance.warnings_or_tensions
    assert guidance.evidence_references
    assert guidance.authority_status == "DERIVED / NOT CANON"


def test_guidance_is_deterministic_contextual_and_non_mutating() -> None:
    session = SessionEnvelope.new("project-1", "mystery", "A missing heir returns home.")
    before = session.model_dump(mode="json")

    first = guidance_for("discover.story-experience", session)
    second = guidance_for("discover.story-experience", session)

    assert first == second
    assert "A missing heir returns home." in first.rationale
    assert session.model_dump(mode="json") == before

    progressed = session.model_copy(deep=True)
    progressed.stages[next(iter(progressed.stages))].lifecycle = LifecycleStatus.COMPLETE
    progressed_guidance = guidance_for("discover.story-experience", progressed)
    assert progressed_guidance.rationale != first.rationale


def test_guidance_is_independent_of_stage_mapping_insertion_order() -> None:
    session = SessionEnvelope.new("project-1", "mystery", "A missing heir returns home.")
    reversed_stages = dict(reversed(tuple(session.stages.items())))
    reordered = session.model_copy(update={"stages": reversed_stages})

    assert guidance_for("discover.story-experience", reordered) == guidance_for(
        "discover.story-experience", session
    )


def test_context_contains_complete_canonical_session_projection() -> None:
    session = SessionEnvelope.new("project-1", "mystery", "A missing heir returns home.")
    guidance = guidance_for("discover.story-experience", session)
    changed = session.model_copy(
        update={
            "session_version": 4,
            "project_id": "project-2",
            "stages": {
                **session.stages,
                DecisionStage.STORY_IDENTITY: session.stages[DecisionStage.STORY_IDENTITY].model_copy(
                    update={
                        "lifecycle": LifecycleStatus.COMPLETE,
                        "availability": StageAvailability.AVAILABLE,
                    }
                ),
            },
        }
    )
    changed_guidance = guidance_for("discover.story-experience", changed)

    assert '"schema_version":1' in guidance.context_summary
    assert '"session_version":0' in guidance.context_summary
    assert '"project_id":"project-1"' in guidance.context_summary
    for stage in DecisionStage:
        assert f'"stage":"{stage.value}"' in guidance.context_summary
    assert guidance != changed_guidance
    assert '"session_version":4' in changed_guidance.context_summary
    assert '"project_id":"project-2"' in changed_guidance.context_summary
    assert '"lifecycle":"complete"' in changed_guidance.context_summary
    assert '"availability":"available"' in changed_guidance.context_summary


def test_card_questions_options_and_consequences_are_card_specific() -> None:
    inventory = mystery_qualification_inventory()
    question_card = inventory.card("discover.story-experience")
    want_card = inventory.card("story_identity.protagonist-want")

    assert question_card.question == "Which mystery experience or lens should the story promise?"
    assert "Solve the puzzle" not in want_card.options
    assert want_card.question == "Which practical investigation want should drive the protagonist?"
    assert question_card.downstream_consequences != want_card.downstream_consequences
    session = SessionEnvelope.new("project-1", "mystery", "A premise.")
    assert guidance_for(question_card.card_id, session).downstream_consequences == question_card.downstream_consequences


def test_guidance_projects_working_decision_and_accepted_milestone_state() -> None:
    session = SessionEnvelope.new("project-1", "mystery", "A missing heir returns home.")
    working = StageStatus(
        stage=DecisionStage.DISCOVER,
        lifecycle=LifecycleStatus.WORKING,
        availability=StageAvailability.AVAILABLE,
        working_decision=WorkingDecision(
            stage=DecisionStage.DISCOVER,
            question="Which truth is being hidden?",
            options=["the inheritance", "the disappearance"],
        ),
    )
    working_state = session.model_copy(
        update={"stages": {**session.stages, DecisionStage.DISCOVER: working}}
    )
    accepted_state = working_state.model_copy(
        update={
            "accepted_milestones": [
                AcceptedMilestoneReference(
                    milestone_id="identity-accepted",
                    revision=RevisionRef(artifact_id="identity-1", revision=1),
                )
            ]
        }
    )

    base = guidance_for("discover.story-experience", session)
    working_guidance = guidance_for("discover.story-experience", working_state)
    accepted_guidance = guidance_for("discover.story-experience", accepted_state)

    assert working_guidance != base
    assert accepted_guidance != working_guidance
    assert "Which truth is being hidden?" in working_guidance.context_summary
    assert "identity-accepted" in accepted_guidance.context_summary


def test_guidance_routes_by_genre_and_rejects_unsupported_genres() -> None:
    romance = SessionEnvelope.new("project-1", "romance", "Two rivals share a secret.")

    with pytest.raises(ValueError, match="unsupported guidance genre"):
        guidance_for("discover.story-experience", romance)


def test_guidance_contract_is_strict_and_never_canonical() -> None:
    session = SessionEnvelope.new("project-1", "mystery", "A missing heir returns home.")
    guidance = guidance_for("discover.story-experience", session)
    payload = guidance.model_dump(mode="python")

    with pytest.raises(ValidationError):
        BeginnerGuidance.model_validate({**payload, "stage": "discover"}, strict=True)
    with pytest.raises(ValidationError):
        BeginnerGuidance.model_validate({**payload, "alternatives": list(guidance.alternatives)}, strict=True)
    with pytest.raises(ValidationError):
        BeginnerGuidance.model_validate({**payload, "authority_status": "CANON"}, strict=True)


def test_inventory_contract_rejects_coercible_enum_and_list_fields() -> None:
    card = mystery_qualification_inventory().cards[0]
    payload = card.model_dump(mode="python")

    with pytest.raises(ValidationError):
        QualificationCard.model_validate({**payload, "stage": "discover"}, strict=True)
    with pytest.raises(ValidationError):
        QualificationCard.model_validate({**payload, "options": list(card.options)}, strict=True)
    with pytest.raises(ValidationError):
        QualificationInventory.model_validate(
            {"cards": list(mystery_qualification_inventory().cards)}, strict=True
        )


def test_guidance_rejects_unknown_card_id() -> None:
    session = SessionEnvelope.new("project-1", "mystery", "A missing heir returns home.")

    with pytest.raises(KeyError, match="unknown-card"):
        guidance_for("unknown-card", session)
