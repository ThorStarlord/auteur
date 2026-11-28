"""The architecture instruction states the node-only rule for an interpretation's ``affects`` that the owner enforces.

In a fresh Wandering Islands architecture answer, two interpretations named phase identifiers in ``affects``, and the owner refused
the whole answer (``interpretation 'int-discoverable-cause' affects unknown nodes: ph-reframing``). The rule was enforced but not
stated. The instruction now states it, so the rule is taught in the same place the owner checks it.
"""
from auteur.beginner.studio_architecture import _SYSTEM


def test_the_instruction_states_that_affects_takes_node_identifiers_only():
    flat = " ".join(_SYSTEM.split())
    assert "Its affects field takes node identifiers only: each one must be the id of a node you list in nodes" in flat
    assert "so a phase, link or question identifier is refused" in flat
