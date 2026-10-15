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
    assert relevance["all_prior_events_exposed"] is False
    assert relevance["clearly_low_value_detail_still_exposed"] is False
    assert relevance["relevance_filter_demonstrated"] is True
    assert relevance["full_evidence_index_preserved"] is True

    paraphrase = payload["probes"]["paraphrased_dependency"]
    assert paraphrase["older_accepted_event_omitted_from_generation_context"] is True
    assert paraphrase["older_accepted_prose_omitted_from_generation_context"] is True
    assert paraphrase["references_remain_indexed"] is True

    x3 = payload["probes"]["x3_book_orientation"]
    assert x3["mechanical_x3_gap"] is False
    assert x3["authority_remains_derived"] is True
    assert x3["missing_persistent_orientation_fields"] == []
    assert x3["author_orientation_surface_present"] is True
    assert x3["book_orientation_is_primary"] is True
    assert x3["technical_details_progressively_disclosed"] is True

    assert payload["schema"] == "f2_x3_agent_preflight_v2"
    assert payload["disposition"]["f2_accepted_history_precedence"] == "PASS"
    assert payload["disposition"]["f2_full_frontier"] == "NOT_QUALIFIED"
    assert payload["disposition"]["f2_context_relevance"] == "BOUNDED_SELECTION_PRESENT"
    assert payload["disposition"]["f2_paraphrased_dependency"] == "LEXICAL_MISS_POSSIBLE"
    assert payload["disposition"]["x3_mechanical_projection"] == "PRESENT_IN_SOURCE"
    assert payload["human_participants"] == 0
    assert payload["provider_calls"] == 0
