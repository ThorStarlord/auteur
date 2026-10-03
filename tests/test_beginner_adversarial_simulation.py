from pathlib import Path
import runpy


def _run_probe() -> dict:
    script = (
        Path(__file__).resolve().parents[1]
        / "scripts"
        / "beginner_adversarial_simulation_probe.py"
    )
    namespace = runpy.run_path(str(script))
    return namespace["run_probe"]()


def test_adversarial_simulation_probe_preserves_claim_ceiling() -> None:
    payload = _run_probe()

    assert payload["evidence_type"] == "SYNTHETIC_AGENT_AND_REPOSITORY_EVIDENCE"
    assert payload["human_participants"] == 0
    assert "human preference" in payload["not_established"]
    assert "felt ownership" in payload["not_established"]
    assert "real-provider quality" in payload["not_established"]
    assert "six-chapter longitudinal coherence" in payload["not_established"]


def test_adversarial_simulation_probe_establishes_agent_answerable_mechanics() -> None:
    probes = _run_probe()["probes"]

    entry = probes["entry_flow"]
    assert entry["old_visible_interactions_to_prose"] == 22
    assert entry["compressed_visible_interactions_to_prose"] == 8
    assert entry["quick_draft_visible_interactions_to_prose"] == 2
    assert entry["quick_draft_explicit_pre_prose_acceptance"] == 0

    discovery = probes["discovery_writer"]
    assert discovery["draft_generated_before_acceptance"] is True
    assert discovery["one_generation_request"] is True
    assert discovery["scaffold_explicitly_provisional"] is True
    assert discovery["no_accepted_root_artifacts"] is True
    assert discovery["unplanned_character_detected"] is True
    assert discovery["unplanned_place_detected"] is True
    assert discovery["only_explicitly_selected_discovery_carried"] is True
    assert discovery["handoff_is_noncanonical"] is True

    ambiguity = probes["ambiguity"]
    assert ambiguity["pov_left_open"] is True
    assert ambiguity["location_left_open"] is True
    assert ambiguity["story_setup_not_accepted"] is True
    assert ambiguity["structure_not_accepted"] is True

    chaotic = probes["chaotic_writer_review"]
    assert chaotic["review_stale_after_edit"] is True
    assert chaotic["stale_findings_not_presented_as_current"] is True
    assert chaotic["reconciliation_available"] is True
    assert chaotic["recommended_action_is_story_language"] is True

    continuity = probes["longitudinal_context"]
    assert continuity["prior_accepted_chapters_visible"] is True
    assert continuity["prior_chapter_refs_visible"] is True
    assert continuity["realized_state_visible"] is True
