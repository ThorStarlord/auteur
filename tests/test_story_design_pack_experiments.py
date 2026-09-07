from __future__ import annotations

from auteur.story_design_packs.experiments import (
    ExperimentCondition,
    ExperimentCase,
    build_experiment_packets,
    summarize_evaluations,
)


def test_experiment_packets_are_matched_and_deterministic():
    case = ExperimentCase(case_id="case-1", premise="A hero predicts a disaster.", decision="whether to resist")

    first = build_experiment_packets([case], pack_ids=["superhero", "hard_determinism"])
    second = build_experiment_packets([case], pack_ids=["superhero", "hard_determinism"])

    assert [packet.packet_id for packet in first] == [packet.packet_id for packet in second]
    assert {packet.condition for packet in first} == {
        ExperimentCondition.CONTROL,
        ExperimentCondition.SINGLE_PACK,
        ExperimentCondition.COMPOSED_PACK,
    }
    assert all(packet.authority_status == "DERIVED / NOT CANON" for packet in first)


def test_experiment_summary_keeps_artifact_and_learning_metrics_separate():
    summary = summarize_evaluations([
        {"condition": "control", "artifact_value": 2, "learning_value": 1, "completed": True},
        {"condition": "composed_pack", "artifact_value": 4, "learning_value": 3, "completed": True},
        {"condition": "composed_pack", "artifact_value": 0, "learning_value": 0, "completed": False},
    ])

    assert summary["conditions"]["composed_pack"]["completed"] == 1
    assert summary["conditions"]["composed_pack"]["artifact_value_mean"] == 4.0
    assert summary["conditions"]["composed_pack"]["learning_value_mean"] == 3.0
    assert summary["conditions"]["composed_pack"]["incomplete"] == 1
