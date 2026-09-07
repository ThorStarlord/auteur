from auteur.narrative_realization.epistemic import KnowledgeFact, knowledge_at
from auteur.narrative_realization.trajectory import (
    CharacterStateSnapshot,
    RelationshipStateSnapshot,
    current_character_states,
    relationship_transition_findings,
)
from auteur.reasoning.promise import PromiseRecord, review_promises
from auteur.series.causal_graph import CausalEdge, CausalStoryGraph


def test_character_and_relationship_projections_are_explicit():
    current = current_character_states([
        CharacterStateSnapshot(character_id="mara", event_index=0, wants=["escape"]),
        CharacterStateSnapshot(character_id="mara", event_index=2, wants=["protect"]),
    ])
    assert current["mara"].wants == ["protect"]
    findings = relationship_transition_findings([
        RelationshipStateSnapshot(relationship_id="r1", subject_a="a", subject_b="b", event_index=0, state="rivals"),
        RelationshipStateSnapshot(relationship_id="r1", subject_a="a", subject_b="b", event_index=1, state="allies"),
    ])
    assert findings[0]["rule"] == "relationship.transition_without_cause"


def test_knowledge_and_promises_keep_unknown_and_overdue_distinct():
    knowledge = knowledge_at([
        KnowledgeFact(observer_id="mara", proposition_id="secret", value="known", event_index=2, source_event_id="reveal"),
    ], observer_id="mara", event_index=1)
    assert knowledge == {}
    findings = review_promises([
        PromiseRecord(promise_id="p1", kind="emotional", introduced_at=1, expected_by=3),
    ], current_index=3)
    assert findings[0]["rule"] == "promise_payoff.overdue"


def test_causal_graph_distinguishes_order_from_cause_and_finds_dependents():
    graph = CausalStoryGraph()
    graph.add(CausalEdge("event-1", "choice-1", "causes"))
    graph.add(CausalEdge("choice-1", "pressure-2", "creates_pressure"))
    assert graph.descendants("event-1") == ("choice-1", "pressure-2")
    assert graph.cycles() == []
