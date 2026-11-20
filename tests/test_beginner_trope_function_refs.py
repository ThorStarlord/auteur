"""Optional trope-function references tie one contextual function to a real trope node (#622 follow-up).

The reference is additive: historical v2 proposals without it stay valid and unchanged, and a
reference never creates identity, acceptance, or an inferred link.
"""
import pytest
from pydantic import ValidationError

from auteur.beginner.studio_architecture import ArchitectureCandidate


def base(**overrides):
    candidate = {
        "schema_version": 2,
        "summary": "A records mystery.",
        "nodes": [
            {"id": "mystery", "title": "Records mystery", "category": "genre", "summary": "Inquiry."},
            {"id": "thriller", "title": "Succession thriller", "category": "genre", "summary": "Race."},
            {"id": "pyrrhic", "title": "Pyrrhic victory", "category": "trope", "summary": "Winning is the cost."},
        ],
        "links": [],
        "genre_contracts": [{
            "genre_node_id": "thriller", "role": "supporting",
            "trope_functions": ["The ticking tide forces decisions.", "Winning costs the heir."],
            "narrative_engine": "Factions race.", "structural_pattern": "Deadlines.",
            "payoff_expectations": ["The heir survives."],
        }],
    }
    candidate.update(overrides)
    return candidate


def with_refs(refs, function_count=2):
    candidate = base()
    candidate["genre_contracts"][0]["trope_function_refs"] = refs
    return candidate


def test_historical_v2_proposals_without_references_remain_valid_and_unchanged():
    parsed = ArchitectureCandidate.model_validate(base())
    assert parsed.genre_contracts[0].trope_function_refs == []
    assert "trope_function_refs" not in parsed.genre_contracts[0].model_dump(exclude_unset=True)


def test_a_reference_names_a_real_trope_node_for_one_function():
    parsed = ArchitectureCandidate.model_validate(with_refs([{"function_index": 1, "trope_node_id": "pyrrhic"}]))
    ref = parsed.genre_contracts[0].trope_function_refs[0]
    assert (ref.function_index, ref.trope_node_id) == (1, "pyrrhic")


@pytest.mark.parametrize("refs,message", [
    ([{"function_index": 0, "trope_node_id": "missing"}], "names no trope node"),
    ([{"function_index": 0, "trope_node_id": "mystery"}], "names no trope node"),  # a genre, not a trope
    ([{"function_index": 5, "trope_node_id": "pyrrhic"}], "points past its function list"),  # past the list
    ([{"function_index": 0, "trope_node_id": "pyrrhic"}, {"function_index": 0, "trope_node_id": "pyrrhic"}],
     "more than once"),
])
def test_contradictory_or_unsourced_references_are_rejected(refs, message):
    with pytest.raises(ValidationError, match=message):
        ArchitectureCandidate.model_validate(with_refs(refs))


def test_references_extend_phase_activations_too_and_are_checked_the_same_way():
    candidate = base(phases=[{"id": "p1", "title": "Opening", "order": 1, "narrative_function": "Start.",
                              "genre_activations": [{"genre_node_id": "thriller", "basic_emotions": ["fear"],
                                                     "trope_functions": ["The ticking tide forces decisions."],
                                                     "trope_function_refs": [{"function_index": 0,
                                                                              "trope_node_id": "pyrrhic"}],
                                                     "structural_function": "The race."}]}])
    parsed = ArchitectureCandidate.model_validate(candidate)
    assert parsed.phases[0].genre_activations[0].trope_function_refs[0].trope_node_id == "pyrrhic"
    candidate["phases"][0]["genre_activations"][0]["trope_function_refs"][0]["trope_node_id"] = "nowhere"
    with pytest.raises(ValidationError, match="names no trope node"):
        ArchitectureCandidate.model_validate(candidate)


def test_unknown_fields_on_a_reference_are_rejected():
    with pytest.raises(ValidationError):
        ArchitectureCandidate.model_validate(with_refs([{"function_index": 0, "trope_node_id": "pyrrhic",
                                                         "confidence": 0.9}]))

def test_references_are_checked_on_every_schema_version_not_only_v2():
    candidate = with_refs([{"function_index": 0, "trope_node_id": "missing"}])
    candidate["schema_version"] = 1
    with pytest.raises(ValidationError, match="names no trope node"):
        ArchitectureCandidate.model_validate(candidate)


def test_stored_output_of_a_proposal_without_references_is_identical_to_before():
    dumped = ArchitectureCandidate.model_validate(base()).model_dump(mode="json")
    contract = dumped["genre_contracts"][0]
    assert "trope_function_refs" not in contract
    referenced = ArchitectureCandidate.model_validate(with_refs([{"function_index": 0, "trope_node_id": "pyrrhic"}]))
    assert referenced.model_dump(mode="json")["genre_contracts"][0]["trope_function_refs"] == [
        {"function_index": 0, "trope_node_id": "pyrrhic"}]
