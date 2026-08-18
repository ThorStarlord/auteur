from __future__ import annotations

from types import SimpleNamespace

import pytest

from auteur.cli import _prepare_argv, main
from auteur.story_discovery_recommend import (
    _parse_judgment,
    _require_distinct_engines,
    _single_survivor,
)


def _candidate(candidate_id: str, suffix: str = "") -> SimpleNamespace:
    engine = SimpleNamespace(
        want=f"want {suffix}",
        resistance=f"resistance {suffix}",
        conflict=f"conflict {suffix}",
        stakes=f"stakes {suffix}",
        change=f"change {suffix}",
    )
    return SimpleNamespace(
        candidate_id=candidate_id,
        identity=SimpleNamespace(central_engine=engine),
    )


def test_prepare_argv_only_consumes_recommend_for_story_discovery_run():
    raw, recommend = _prepare_argv([
        "story-discovery",
        "run",
        "A royal murder.",
        "--recommend",
    ])
    assert recommend is True
    assert raw == ["story-discovery", "run", "A royal murder."]

    raw, recommend = _prepare_argv(["identity", "recommend", "A royal murder.", "--recommend"])
    assert recommend is False
    assert "--recommend" in raw


def test_main_routes_recommend_to_adapter_without_touching_normal_dispatch(monkeypatch, tmp_path):
    observed = {}

    def fake_recommend(args):
        observed["command"] = args.command
        observed["subcommand"] = args.story_discovery_command
        observed["candidates"] = args.candidates
        return 17

    monkeypatch.setattr(
        "auteur.story_discovery_recommend.dispatch_story_discovery_recommend",
        fake_recommend,
    )
    monkeypatch.setattr("auteur.cli.dispatch", lambda args: pytest.fail("normal dispatch should not run"))

    result = main([
        "story-discovery",
        "run",
        "A royal murder.",
        "--output",
        str(tmp_path),
        "--recommend",
    ])

    assert result == 17
    assert observed == {
        "command": "story-discovery",
        "subcommand": "run",
        "candidates": 3,
    }


def test_main_without_recommend_preserves_existing_dispatch(monkeypatch, tmp_path):
    monkeypatch.setattr("auteur.cli.dispatch", lambda args: 23)
    result = main([
        "story-discovery",
        "run",
        "A royal murder.",
        "--output",
        str(tmp_path),
    ])
    assert result == 23


def test_parse_judgment_requires_exact_survivor_coverage():
    text = (
        '{"recommended_candidate_id":"candidate_2",'
        '"recommendation_rationale":"Best causal use of the premise.",'
        '"rejected_candidate_reasons":{'
        '"candidate_1":"Too much machinery.",'
        '"candidate_3":"Genericizes the premise."}}'
    )
    winner, rationale, rejected = _parse_judgment(
        text,
        ["candidate_1", "candidate_2", "candidate_3"],
    )
    assert winner == "candidate_2"
    assert "causal" in rationale
    assert set(rejected) == {"candidate_1", "candidate_3"}


def test_parse_judgment_rejects_unknown_winner_and_extra_keys():
    with pytest.raises(ValueError, match="surviving candidates"):
        _parse_judgment(
            '{"recommended_candidate_id":"candidate_99",'
            '"recommendation_rationale":"No.",'
            '"rejected_candidate_reasons":{"candidate_1":"A"}}',
            ["candidate_1", "candidate_2"],
        )

    with pytest.raises(ValueError, match="exactly the required keys"):
        _parse_judgment(
            '{"recommended_candidate_id":"candidate_1",'
            '"recommendation_rationale":"A.",'
            '"rejected_candidate_reasons":{"candidate_2":"B"},'
            '"confidence":0.9}',
            ["candidate_1", "candidate_2"],
        )


def test_exact_duplicate_engine_force_tuples_are_rejected():
    with pytest.raises(ValueError, match="exact duplicates"):
        _require_distinct_engines([
            _candidate("candidate_1"),
            _candidate("candidate_2"),
        ])

    _require_distinct_engines([
        _candidate("candidate_1", "one"),
        _candidate("candidate_2", "two"),
    ])


def test_single_survivor_is_labeled_as_viability_not_artistic_judgment():
    winner, rationale, rejected = _single_survivor("candidate_1", 3)
    assert winner == "candidate_1"
    assert "only candidate" in rationale
    assert "viability result" in rationale
    assert "not a comparative artistic-quality judgment" in rationale
    assert rejected == {}
