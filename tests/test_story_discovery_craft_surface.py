from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

from auteur.story_discovery_causality import CausalProfileRecord
from auteur.story_discovery_craft import (
    CraftAnalysis,
    CraftImpactRecord,
    ExternalActionShift,
    ReaderExperienceShift,
)
from auteur.story_discovery_craft_surface import (
    append_craft_comparison,
    compact_craft_lines,
    replace_generic_alternatives_with_craft,
)


class Dumpable(SimpleNamespace):
    def model_dump(self, mode="json"):
        return dict(self.__dict__)


def _candidate(candidate_id: str, title: str, *, secondary=None, trajectory=None):
    target = Dumpable(
        primary="painful dramatic irony",
        primary_emotional_promise="painful dramatic irony",
        secondary_palette=list(secondary or []),
        secondary=list(secondary or []),
        emotional_trajectory=trajectory,
        progression=(trajectory or {}).get("pattern", "static") if isinstance(trajectory, dict) else "static",
    )
    return SimpleNamespace(
        candidate_id=candidate_id,
        identity=SimpleNamespace(title=title, target_experience=target),
    )


def _analysis():
    impact = CraftImpactRecord(
        primary_candidate_id="candidate_1",
        compared_candidate_id="candidate_2",
        primary_evidence_key="aaaaaaaa111111111111",
        compared_evidence_key="bbbbbbbb222222222222",
        craft_layers_changed=[
            "causal_ownership",
            "external_action",
            "scene_families",
            "reader_experience",
            "theme",
        ],
        causal_ownership_shift="More consequential turns originate with the brother.",
        external_action_shift=ExternalActionShift(
            add_or_emphasize=["conceal", "intervene", "sacrifice"],
            de_emphasize=["direct protagonist-led repair"],
        ),
        scene_family_shift=["parallel hidden intervention", "near-discovery"],
        pressure_texture_shift="More hidden-action dramatic irony.",
        reader_experience_shift=ReaderExperienceShift(
            primary_promise_effect="preserved_but_reweighted",
            secondary_palette_effect=["more pity", "more moral discomfort"],
            trajectory_effect="Dread increases as interventions accumulate.",
        ),
        thematic_effect="Atonement without confession gains weight.",
        gain="Stronger hidden causal pressure.",
        give_up="Some protagonist causal ownership.",
        composability="compatible_as_secondary",
        composition_note="Keep the protagonist's own decisions decisive.",
        primary_risk="The brother can become the effective protagonist.",
        evidence_gaps=[],
    )
    return CraftAnalysis(
        status="complete",
        primary_candidate_id="candidate_1",
        impacts={"candidate_2": impact},
    )


def _profiles():
    return {
        "candidate_1": CausalProfileRecord(
            evidence_key="aaaaaaaa111111111111",
            primary_strategy="repair visible consequences under incomplete knowledge",
            causal_owner="protagonist-led",
            external_action_pattern=["repair", "organize", "protect", "choose"],
            pressure_system="incomplete knowledge",
            reversal_mechanics=["new consequences challenge the working explanation"],
            climax_mechanic="the protagonist's own decisions resolve the crisis",
            scene_families=["recovery operation", "family confrontation"],
            evidence_gaps=[],
        ),
        "candidate_2": CausalProfileRecord(
            evidence_key="bbbbbbbb222222222222",
            primary_strategy="secret atonement through hidden intervention",
            causal_owner="brother-led hidden pressure",
            external_action_pattern=["conceal", "intervene", "sacrifice"],
            pressure_system="near-discovery",
            reversal_mechanics=["an intervention solves one problem and creates another"],
            climax_mechanic="the brother sacrifices without confessing",
            scene_families=["parallel intervention", "near-discovery"],
            evidence_gaps=[],
        ),
    }


def test_compact_surface_exposes_primary_engine_reader_hierarchy_and_tradeoff():
    candidates = [
        _candidate(
            "candidate_1",
            "What She Saves",
            secondary=["dread", "hope"],
            trajectory={"pattern": "suspicion -> dread -> bittersweet agency"},
        ),
        _candidate("candidate_2", "His Quiet Repair"),
    ]
    text = "\n".join(compact_craft_lines(_analysis(), _profiles(), candidates))

    assert "Primary narrative engine" in text
    assert "repair visible consequences" in text
    assert "Governing reader promise: painful dramatic irony" in text
    assert "Supporting emotional palette: dread, hope" in text
    assert "Emotional trajectory: suspicion -> dread -> bittersweet agency" in text
    assert "You would write more: conceal, intervene, sacrifice" in text
    assert "Give up / reweight: Some protagonist causal ownership." in text
    assert "Composability: compatible as secondary" in text


def test_compact_surface_does_not_invent_missing_secondary_emotions_or_trajectory():
    candidates = [
        _candidate("candidate_1", "What She Saves"),
        _candidate("candidate_2", "His Quiet Repair"),
    ]
    text = "\n".join(compact_craft_lines(_analysis(), _profiles(), candidates))
    assert "Supporting emotional palette:" not in text
    assert "Emotional trajectory:" not in text


def test_generic_alternatives_are_replaced_but_authority_commands_survive():
    base = [
        "Story Discovery",
        "",
        "RECOMMENDED — What She Saves (`candidate_1`)",
        "",
        "Alternatives",
        "- His Quiet Repair (`candidate_2`) — generic rejection prose",
        "",
        "Nothing has been accepted yet.",
        "",
        "Next",
        "  Accept the recommendation:",
        "    auteur story-discovery accept candidate_1.yaml --output story_identity.yaml",
    ]
    craft = ["Primary narrative engine", "- Causal strategy: repair", "", "Craft tradeoffs"]
    text = "\n".join(replace_generic_alternatives_with_craft(base, craft))
    assert "generic rejection prose" not in text
    assert "Primary narrative engine" in text
    assert "Nothing has been accepted yet." in text
    assert "auteur story-discovery accept" in text


def test_comparison_artifact_teaches_named_craft_layers(tmp_path: Path):
    output_dir = tmp_path / "story_discovery"
    output_dir.mkdir()
    comparison = output_dir / "comparison.md"
    comparison.write_text("# Story Discovery Comparison\n", encoding="utf-8")
    candidates = [
        _candidate("candidate_1", "What She Saves", secondary=["dread"]),
        _candidate("candidate_2", "His Quiet Repair"),
    ]

    append_craft_comparison(output_dir, _analysis(), _profiles(), candidates)
    text = comparison.read_text(encoding="utf-8")

    for heading in (
        "WHAT CHANGES",
        "CAUSAL EFFECT",
        "WHAT YOU WILL WRITE MORE OF",
        "PRESSURE / STORY TEXTURE",
        "READER-EXPERIENCE SHIFT",
        "THEMATIC EFFECT",
        "WHAT YOU GAIN",
        "WHAT YOU GIVE UP / REWEIGHT",
        "COMPOSABILITY",
        "PRIMARY RISK",
    ):
        assert heading in text
    assert "narrative-weight movement" in text
