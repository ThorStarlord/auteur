from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from auteur.cli import parse_args
from auteur.story_discovery_brief import DiscoveryBrief
from auteur.story_discovery_causality import CausalAnalysis, CausalProfileRecord
from auteur.story_discovery_compose_cli import parse_compose_args
from auteur.story_discovery_craft import (
    CraftAnalysis,
    CraftImpactRecord,
    ExternalActionShift,
    ReaderExperienceShift,
)
from auteur.story_discovery_guided_compose import dispatch_story_discovery_guided_compose


def _write_yaml(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")


def _profile(key: str, strategy: str) -> CausalProfileRecord:
    return CausalProfileRecord(
        evidence_key=key,
        primary_strategy=strategy,
        causal_owner="protagonist-led",
        external_action_pattern=["act", "adapt", "choose"],
        pressure_system=f"pressure from {strategy}",
        reversal_mechanics=[f"{strategy} changes the plan"],
        climax_mechanic=f"climax through {strategy}",
        scene_families=[f"{strategy} scene"],
        evidence_gaps=[],
    )


def _impact(candidate_id: str, composability: str) -> CraftImpactRecord:
    key = {
        "candidate_2": "bbbbbbbb222222222222",
        "candidate_3": "cccccccc333333333333",
        "candidate_4": "dddddddd444444444444",
    }[candidate_id]
    return CraftImpactRecord(
        primary_candidate_id="candidate_1",
        compared_candidate_id=candidate_id,
        primary_evidence_key="aaaaaaaa111111111111",
        compared_evidence_key=key,
        craft_layers_changed=["causal_ownership", "external_action"],
        causal_ownership_shift="Some pressure moves toward the alternative mechanism.",
        external_action_shift=ExternalActionShift(
            add_or_emphasize=["intervene"],
            de_emphasize=["direct resolution"],
        ),
        scene_family_shift=["intervention scenes"],
        pressure_texture_shift="The pressure becomes more layered.",
        reader_experience_shift=ReaderExperienceShift(
            primary_promise_effect="preserved_but_reweighted",
            secondary_palette_effect=["more tension"],
            trajectory_effect="The middle becomes more pressured.",
        ),
        thematic_effect="Responsibility becomes less singular.",
        gain="More layered pressure.",
        give_up="Some simplicity.",
        composability=composability,
        composition_note=(
            "Keep the borrowed mechanism subordinate."
            if composability == "compatible_as_secondary"
            else None
        ),
        primary_risk="The borrowed layer could displace the primary engine.",
        evidence_gaps=[],
    )


def _write_run(
    root: Path,
    *,
    candidate_2_fit: str = "compatible_as_secondary",
    candidate_3_fit: str = "requires_reframing",
    candidate_4_fit: str = "uncertain",
) -> None:
    discovery = root / "story_discovery"
    brief_path = discovery / "brief.yaml"
    _write_yaml(
        brief_path,
        {
            "premise": "A woman rebuilds after a disaster without learning who caused it.",
            "story_type": {"genre": "mystery", "target_audience": "adult"},
            "target_experience": {"primary_emotional_promise": "painful dramatic irony"},
        },
    )
    brief = DiscoveryBrief.from_yaml(brief_path)

    for candidate_id, title in {
        "candidate_1": "What She Saves",
        "candidate_2": "His Quiet Repair",
        "candidate_3": "The Official Cause",
        "candidate_4": "Everyone Knew",
    }.items():
        _write_yaml(discovery / f"{candidate_id}.yaml", {"title": title})

    causal = CausalAnalysis(
        status="qualified",
        profiles={
            "candidate_1": _profile("aaaaaaaa111111111111", "visible recovery"),
            "candidate_2": _profile("bbbbbbbb222222222222", "secret atonement"),
            "candidate_3": _profile("cccccccc333333333333", "institutional correction"),
            "candidate_4": _profile("dddddddd444444444444", "collective concealment"),
        },
        pairwise_assessments=[],
    )
    craft = CraftAnalysis(
        status="complete",
        primary_candidate_id="candidate_1",
        impacts={
            "candidate_2": _impact("candidate_2", candidate_2_fit),
            "candidate_3": _impact("candidate_3", candidate_3_fit),
            "candidate_4": _impact("candidate_4", candidate_4_fit),
        },
    )
    payload = {
        "recommended_candidate_id": "candidate_1",
        "intent_mode": "intent_aware",
        "declared_author_intent": brief.declared_intent(),
        "causal_analysis": causal.model_dump(mode="json"),
        "craft_analysis": craft.model_dump(mode="json"),
    }
    _write_yaml(discovery / "discovery_set.yaml", payload)
    _write_yaml(discovery / "discovery_report.yaml", payload)


def _guided_args(root: Path):
    return type(
        "Args",
        (),
        {
            "project": root,
            "provider": "anthropic",
            "model": None,
        },
    )()


def _input(values: list[str]):
    iterator = iter(values)
    return lambda _prompt: next(iterator)


def test_compose_cli_supports_guided_project_mode_and_preserves_advanced_mode():
    guided = parse_args(["story-discovery", "compose", "--project", "."])
    assert guided.guided is True
    assert guided.project == Path(".")
    assert guided.discovery_dir is None

    advanced = parse_args(
        [
            "story-discovery",
            "compose",
            "story_discovery",
            "--primary",
            "candidate_1",
            "--borrow",
            "candidate_2:secret intervention",
        ]
    )
    assert advanced.guided is False
    assert advanced.discovery_dir == Path("story_discovery")
    assert advanced.primary == "candidate_1"
    assert advanced.borrow == ["candidate_2:secret intervention"]


def test_guided_mode_rejects_advanced_output_or_borrow_arguments():
    with pytest.raises(SystemExit):
        parse_compose_args(["--project", ".", "--output", "custom.yaml"])
    with pytest.raises(SystemExit):
        parse_compose_args(["--project", ".", "--borrow", "candidate_2:x"])


def test_guided_handoff_lists_only_f4_compatible_alternatives_and_preserves_author_text(
    tmp_path, monkeypatch
):
    _write_run(tmp_path)
    calls = []

    def fake_f5(args):
        calls.append(args)
        return 0

    monkeypatch.setattr("auteur.story_discovery_compose.dispatch_story_discovery_compose", fake_f5)
    output: list[str] = []
    result = dispatch_story_discovery_guided_compose(
        _guided_args(tmp_path),
        input_fn=_input(["yes", "1", "secret atonement through hidden repairs"]),
        output_fn=output.append,
    )

    assert result == 0
    assert len(calls) == 1
    assert calls[0].primary == "candidate_1"
    assert calls[0].borrow == ["candidate_2:secret atonement through hidden repairs"]
    rendered = "\n".join(output)
    assert "candidate_2 — His Quiet Repair" in rendered
    assert "candidate_3 — The Official Cause" not in rendered
    assert "candidate_4 — Everyone Knew" not in rendered


def test_guided_mode_can_collect_multiple_distinct_compatible_layers(tmp_path, monkeypatch):
    _write_run(tmp_path, candidate_3_fit="compatible_as_secondary")
    calls = []
    monkeypatch.setattr(
        "auteur.story_discovery_compose.dispatch_story_discovery_compose",
        lambda args: calls.append(args) or 0,
    )

    result = dispatch_story_discovery_guided_compose(
        _guided_args(tmp_path),
        input_fn=_input(
            [
                "y",
                "candidate_2",
                "hidden repair interventions",
                "yes",
                "1",
                "institutional false model pressure",
            ]
        ),
        output_fn=lambda _line: None,
    )

    assert result == 0
    assert calls[0].borrow == [
        "candidate_2:hidden repair interventions",
        "candidate_3:institutional false model pressure",
    ]


def test_declining_primary_or_cancelling_mechanism_never_hands_off(tmp_path, monkeypatch):
    _write_run(tmp_path)
    monkeypatch.setattr(
        "auteur.story_discovery_compose.dispatch_story_discovery_compose",
        lambda _args: (_ for _ in ()).throw(AssertionError("F5 must not run")),
    )

    assert dispatch_story_discovery_guided_compose(
        _guided_args(tmp_path),
        input_fn=_input(["no"]),
        output_fn=lambda _line: None,
    ) == 0
    assert dispatch_story_discovery_guided_compose(
        _guided_args(tmp_path),
        input_fn=_input(["yes", "1", "/cancel"]),
        output_fn=lambda _line: None,
    ) == 0


def test_interruption_returns_130_without_handoff(tmp_path, monkeypatch):
    _write_run(tmp_path)
    monkeypatch.setattr(
        "auteur.story_discovery_compose.dispatch_story_discovery_compose",
        lambda _args: (_ for _ in ()).throw(AssertionError("F5 must not run")),
    )

    def interrupted(_prompt):
        raise EOFError

    assert dispatch_story_discovery_guided_compose(
        _guided_args(tmp_path),
        input_fn=interrupted,
        output_fn=lambda _line: None,
    ) == 130


def test_no_compatible_alternative_fails_before_prompt_or_provider(tmp_path, monkeypatch):
    _write_run(
        tmp_path,
        candidate_2_fit="requires_reframing",
        candidate_3_fit="mutually_exclusive_with_primary",
        candidate_4_fit="uncertain",
    )
    monkeypatch.setattr(
        "builtins.input",
        lambda _prompt: (_ for _ in ()).throw(AssertionError("must not prompt")),
    )
    monkeypatch.setattr(
        "auteur.llm.factory.build_client",
        lambda *a, **k: (_ for _ in ()).throw(AssertionError("provider must not run")),
    )

    assert dispatch_story_discovery_guided_compose(_guided_args(tmp_path)) == 1


def test_guided_mode_never_overwrites_current_or_stale_composition_artifacts(tmp_path, monkeypatch):
    _write_run(tmp_path)
    stale = tmp_path / "story_discovery" / "composed_candidate.yaml"
    stale.write_text("title: stale\n", encoding="utf-8")
    monkeypatch.setattr(
        "auteur.story_discovery_compose.dispatch_story_discovery_compose",
        lambda _args: (_ for _ in ()).throw(AssertionError("F5 must not run")),
    )

    assert dispatch_story_discovery_guided_compose(
        _guided_args(tmp_path),
        input_fn=lambda _prompt: (_ for _ in ()).throw(AssertionError("must not prompt")),
    ) == 1
    assert stale.read_text(encoding="utf-8") == "title: stale\n"


def test_guided_handoff_does_not_bypass_f5_report_revalidation(tmp_path, monkeypatch):
    _write_run(tmp_path)
    report_path = tmp_path / "story_discovery" / "discovery_report.yaml"
    report = yaml.safe_load(report_path.read_text(encoding="utf-8"))
    report.pop("craft_analysis")
    _write_yaml(report_path, report)
    monkeypatch.setattr(
        "auteur.llm.factory.build_client",
        lambda *a, **k: (_ for _ in ()).throw(AssertionError("provider must not run")),
    )

    result = dispatch_story_discovery_guided_compose(
        _guided_args(tmp_path),
        input_fn=_input(["yes", "1", "hidden repairs"]),
        output_fn=lambda _line: None,
    )

    assert result == 1
    assert not (tmp_path / "story_discovery" / "composed_candidate.yaml").exists()
    assert not (tmp_path / "story_discovery" / "composition_report.yaml").exists()
