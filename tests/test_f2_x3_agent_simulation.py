from __future__ import annotations

import runpy
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_f2_x3_agent_preflight_establishes_current_mechanical_ceiling() -> None:
    namespace = runpy.run_path(str(ROOT / "scripts" / "f2_x3_agent_simulation_probe.py"))
    payload = namespace["run_probe"]()

    history = payload["probes"]["accepted_history_and_precedence"]
    assert history["prior_accepted_chapters_visible"] is True
    assert history["accepted_change_visible"] is True
    assert history["obsolete_plan_reported_as_divergence"] is True
    assert history["historical_plan_not_silently_rewritten"] is True
    assert history["next_chapter_role_preserved"] is True

    relevance = payload["probes"]["six_chapter_context_relevance"]
    assert relevance["five_prior_accepted_chapters_visible"] is True
    assert relevance["all_prior_events_exposed"] is True
    assert relevance["clearly_low_value_detail_still_exposed"] is True
    assert relevance["relevance_filter_demonstrated"] is False

    x3 = payload["probes"]["x3_book_orientation"]
    assert x3["mechanical_x3_gap"] is True
    assert x3["authority_remains_derived"] is True
    assert x3["missing_persistent_orientation_fields"] == []
    assert x3["author_orientation_surface_present"] is False

    assert payload["disposition"]["f2_accepted_history_precedence"] == "PASS"
    assert payload["disposition"]["f2_full_frontier"] == "NOT_QUALIFIED"
    assert payload["disposition"]["f2_context_relevance"] == "GAP_OR_NOT_ESTABLISHED"
    assert payload["disposition"]["x3_mechanical_projection"] == "GAP_ESTABLISHED"
    assert payload["human_participants"] == 0
    assert payload["provider_calls"] == 0
