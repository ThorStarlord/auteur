from __future__ import annotations

import runpy
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_f2_context_relevance_probe_passes_bounded_glass_archive_contract():
    namespace = runpy.run_path(str(ROOT / "scripts" / "f2_context_relevance_probe.py"))
    result = namespace["run_probe"]()
    assert result["five_prior_chapters_addressable"] is True
    assert result["all_accepted_events_addressable"] is True
    assert result["old_trivia_omitted_from_generation_context"] is True
    assert result["required_long_range_dependencies_present"] is True
    assert result["unresolved_accepted_state_preserved"] is True
    assert result["pending_update_explicit"] is True
    assert result["raw_bible_not_flattened_into_realized_state"] is True
    assert result["omitted_event_count"] >= 1
    assert result["selection_mode"] == "bounded_recency_plus_current_plan_overlap"
