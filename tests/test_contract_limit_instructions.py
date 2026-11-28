"""Owner-enforced bounds are stated to the agent from the same contract that the owner validates against.

An instruction that omits a bound refuses a whole answer (the first authentic verification run, creative_room at 401 characters).
The bounds are generated from the contract, so they cannot drift from the validator.
"""

from auteur.beginner.studio_architecture_synthesis import SynthesisAnswer, _SYSTEM_SYNTHESIS
from auteur.beginner.studio_architecture_verification import ClaimVerification, _SYSTEM_VERIFY
from auteur.host_agent import contract_limit_lines, limits_instruction


def test_the_synthesis_instruction_states_every_bound_the_owner_enforces():
    lines = contract_limit_lines(SynthesisAnswer)
    assert lines, "the contract carries bounds"
    for line in lines:
        assert line in _SYSTEM_SYNTHESIS, line


def test_the_verification_instruction_states_every_bound_the_owner_enforces():
    for line in contract_limit_lines(ClaimVerification):
        assert line in _SYSTEM_VERIFY, line


def test_optional_fields_and_integer_ranges_are_read_from_the_contract():
    lines = contract_limit_lines(SynthesisAnswer)
    assert "trajectory[].book: at least 1; at most 60" in lines
    assert any(line.startswith("trajectory[].quote: at most 240 characters") for line in lines), "an optional field keeps its bound"
    assert limits_instruction(SynthesisAnswer).startswith("Limits, enforced by the owner")


def test_every_bounded_field_is_listed_and_the_listing_is_deterministic():
    first = contract_limit_lines(SynthesisAnswer)
    assert first == contract_limit_lines(SynthesisAnswer)
    assert any("reader_experience: at most 600 characters" in line for line in first)
    assert any("open_decisions[]: at most 240 characters" in line for line in first)
