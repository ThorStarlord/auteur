"""Deterministic packet construction and summary helpers for Tutor experiments."""
from __future__ import annotations

import hashlib
import json
from collections import defaultdict
from enum import Enum
from statistics import mean

from pydantic import BaseModel, Field

from .composition import compose_packs
from .tutor import tutor_recommend


class ExperimentCondition(str, Enum):
    CONTROL = "control"
    SINGLE_PACK = "single_pack"
    COMPOSED_PACK = "composed_pack"


class ExperimentCase(BaseModel):
    case_id: str = Field(min_length=1)
    premise: str = Field(min_length=1)
    decision: str = Field(min_length=1)


class ExperimentPacket(BaseModel):
    packet_id: str
    case_id: str
    condition: ExperimentCondition
    premise: str
    decision: str
    pack_ids: list[str] = Field(default_factory=list)
    guidance: dict[str, object]
    authority_status: str = "DERIVED / NOT CANON"


def _packet_id(case: ExperimentCase, condition: ExperimentCondition, pack_ids: list[str]) -> str:
    payload = {"case": case.model_dump(), "condition": condition.value, "pack_ids": pack_ids}
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode("utf-8")).hexdigest()[:16]


def build_experiment_packets(cases: list[ExperimentCase], *, pack_ids: list[str]) -> list[ExperimentPacket]:
    """Build matched control, single-pack, and composed-pack packets."""
    if not pack_ids:
        raise ValueError("At least one pack is required for matched pack experiments")
    unique_packs = list(dict.fromkeys(pack_ids))
    conditions = [
        (ExperimentCondition.CONTROL, []),
        (ExperimentCondition.SINGLE_PACK, [unique_packs[0]]),
        (ExperimentCondition.COMPOSED_PACK, unique_packs),
    ]
    packets: list[ExperimentPacket] = []
    for case in cases:
        for condition, selected in conditions:
            if condition is ExperimentCondition.CONTROL:
                guidance = {
                    "decision": case.decision,
                    "orientation": f"We are deciding {case.decision} in {case.premise}.",
                    "recommendation": "No pack recommendation; elicit the author's direction.",
                    "alternatives": [],
                    "tradeoffs": [],
                }
            else:
                guidance = tutor_recommend(selected, decision=case.decision, premise=case.premise).model_dump(mode="json")
            packets.append(ExperimentPacket(
                packet_id=_packet_id(case, condition, selected),
                case_id=case.case_id,
                condition=condition,
                premise=case.premise,
                decision=case.decision,
                pack_ids=selected,
                guidance=guidance,
            ))
    return packets


def summarize_evaluations(evaluations: list[dict[str, object]]) -> dict[str, object]:
    """Summarize artifact and learning value independently."""
    grouped: dict[str, list[dict[str, object]]] = defaultdict(list)
    for evaluation in evaluations:
        grouped[str(evaluation["condition"])].append(evaluation)
    conditions: dict[str, dict[str, object]] = {}
    for condition, rows in sorted(grouped.items()):
        completed = [row for row in rows if bool(row.get("completed"))]
        conditions[condition] = {
            "total": len(rows),
            "completed": len(completed),
            "incomplete": len(rows) - len(completed),
            "artifact_value_mean": mean(float(row["artifact_value"]) for row in completed) if completed else None,
            "learning_value_mean": mean(float(row["learning_value"]) for row in completed) if completed else None,
        }
    return {"conditions": conditions}
