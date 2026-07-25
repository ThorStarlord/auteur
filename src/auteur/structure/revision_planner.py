"""Revision planner — convert diagnostics and proposals into actionable revision plans.

All functions in this module are deterministic and side-effect-free (no file writes,
no project mutation). Planning only reads proposal and blueprint files to produce an
in-memory StructuralRevisionPlan.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from auteur.blueprint import StoryBlueprint
from auteur.structure.diagnostics import StructureDiagnostic
from auteur.structure.proposal_models import StructureProposal
from auteur.structure.revision_models import (
    RevisionOperation,
    RevisionOperationType,
    RevisionPlanState,
    RevisionScope,
    StructuralRevisionPlan,
    _stable_event_id,
    _stable_plan_id,
)

# Re-export for convenience
__all__ = [
    "create_revision_plan",
    "plan_from_diagnostic",
]

# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _compute_file_hash(path: Path) -> str:
    """SHA-256 hex digest of a file's raw bytes."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _hash_python_value(value: Any) -> str:
    """Deterministic SHA-256 hash of an arbitrary Python value (model, list, scalar).

    Uses model_dump for Pydantic models, JSON-serialization for everything else.
    """
    if hasattr(value, "model_dump"):
        serialized = json.dumps(value.model_dump(mode="json"), sort_keys=True)
    elif isinstance(value, list):
        items = [
            i.model_dump(mode="json") if hasattr(i, "model_dump") else i for i in value
        ]
        serialized = json.dumps(items, sort_keys=True)
    elif isinstance(value, dict):
        serialized = json.dumps(value, sort_keys=True)
    else:
        serialized = json.dumps(str(value), sort_keys=True)
    return hashlib.sha256(serialized.encode()).hexdigest()


def _build_target_artifact_id(field_path: str) -> str:
    """Build a stable artifact identifier from a blueprint field path."""
    return f"blueprint:{field_path}"


def _collect_target_hashes(
    blueprint: StoryBlueprint,
    operations: list[RevisionOperation],
) -> dict[str, str]:
    """Collect deterministic before-state hashes for each target artifact.

    Every artifact referenced by *operations* gets a content hash computed from
    the *blueprint*'s current state. Includes a top-level ``blueprint`` key.
    """
    hashes: dict[str, str] = {}

    # Top-level blueprint hash
    bp_raw = json.dumps(blueprint.model_dump(mode="json"), sort_keys=True)
    hashes["blueprint"] = hashlib.sha256(bp_raw.encode()).hexdigest()

    for op in operations:
        field = op.target_type
        if field in hashes:
            continue
        field_value = getattr(blueprint, field, None)
        if field_value is not None:
            hashes[field] = _hash_python_value(field_value)
        else:
            hashes[field] = ""

    return hashes


# ---------------------------------------------------------------------------
# Operation builders
# ---------------------------------------------------------------------------


def _build_operations_from_proposal(
    proposal: StructureProposal,
    blueprint: StoryBlueprint,
) -> list[RevisionOperation]:
    """Translate a proposal's accepted option data into ordered revision operations.

    Each top-level key in the selected option's *data* dict becomes one operation.
    Keys matching top-level StoryBlueprint fields produce a ``REPLACE`` operation;
    all others produce ``UPDATE_OUTLINE_FIELD``.

    Returns an empty list when no option is selected.
    """
    if not proposal.selection.selected_option_id:
        return []

    selected = next(
        (o for o in proposal.options if o.id == proposal.selection.selected_option_id),
        None,
    )
    if selected is None:
        return []

    patch_data = selected.data or {}
    operations: list[RevisionOperation] = []

    # Top-level StoryBlueprint fields that warrant a whole-field REPLACE
    _whole_field_ops = {
        "identity",
        "structure",
        "story_engine",
        "contract",
        "emotional_design",
        "characters",
        "tension_waveform",
        "theme",
    }

    # Sort field keys for deterministic ordering
    field_keys = sorted(patch_data.keys())
    for order, field_key in enumerate(field_keys):
        value = patch_data[field_key]

        if field_key in _whole_field_ops:
            op_type = RevisionOperationType.REPLACE
        else:
            op_type = RevisionOperationType.UPDATE_OUTLINE_FIELD

        target_id = _build_target_artifact_id(field_key)
        before_value = getattr(blueprint, field_key, None)

        # Serialize before-state as a dict for the operation
        before_dict: dict[str, Any] = {}
        if before_value is not None:
            if hasattr(before_value, "model_dump"):
                before_dict = before_value.model_dump(mode="json")
            elif isinstance(before_value, list):
                before_dict = {
                    "items": [
                        i.model_dump(mode="json") if hasattr(i, "model_dump") else i
                        for i in before_value
                    ]
                }
            else:
                before_dict = {"value": str(before_value)}

        operations.append(
            RevisionOperation(
                operation_id=f"op_{target_id}_{op_type.value}",
                target_id=target_id,
                target_type=field_key,
                operation_type=op_type,
                before_expectation=before_dict,
                requested_change=value if isinstance(value, dict) else {"value": value},
                preconditions=[],
                authority_level="authority_bearing",
                predicted_consequences=[],
                order=order,
            )
        )

    # Fallback: diagnostic-reference operation when no concrete patch exists
    if not operations and proposal.source_rule:
        target_id = _build_target_artifact_id(proposal.source_rule)
        operations.append(
            RevisionOperation(
                operation_id=f"op_{target_id}_diagnostic_reference",
                target_id=target_id,
                target_type=proposal.source_rule,
                operation_type=RevisionOperationType.REPLACE,
                before_expectation={},
                requested_change={"source_rule": proposal.source_rule},
                preconditions=[],
                authority_level="authority_bearing",
                predicted_consequences=[],
                order=0,
            )
        )

    return operations


def _build_operations_from_diagnostic(
    diagnostic: StructureDiagnostic,
    blueprint: StoryBlueprint,
) -> list[RevisionOperation]:
    """Build a single operation from a diagnostic's layer/rule metadata."""
    # Map diagnostic layer to the most specific StoryBlueprint field
    layer_to_field: dict[str, str] = {
        "target_experience": "contract",
        "constraints": "contract",
        "scope": "structure",
        "structural_forces": "structure",
        "threads": "structure",
        "theme": "theme",
        "carriers": "characters",
        "representation": "story_engine",
        "modulation": "emotional_design",
    }
    field_key = layer_to_field.get(diagnostic.layer.value, "structure")
    target_id = _build_target_artifact_id(field_key)

    return [
        RevisionOperation(
            operation_id=f"op_{target_id}_diagnostic_{diagnostic.rule}",
            target_id=target_id,
            target_type=field_key,
            operation_type=RevisionOperationType.UPDATE_OUTLINE_FIELD,
            before_expectation={},
            requested_change={
                "layer": diagnostic.layer.value,
                "rule": diagnostic.rule,
                "message": diagnostic.message,
            },
            preconditions=[],
            authority_level="authority_bearing",
            predicted_consequences=[],
            order=0,
        )
    ]


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def create_revision_plan(
    proposal_path: str | Path,
    blueprint_path: str | Path,
    project_root: str | Path,
) -> StructuralRevisionPlan:
    """Read a proposal and blueprint from disk and produce a non-mutating revision plan.

    Args:
        proposal_path: Path to the proposal YAML file.
        blueprint_path: Path to the blueprint YAML file.
        project_root: Project root directory (used for namespacing the plan ID).

    Returns:
        A StructuralRevisionPlan with a stable semantic plan ID, typed operations,
        before-state hashes, and scope constraints.

    The function does **not** write any files — it is purely analytical.
    """
    proposal_path = Path(proposal_path)
    blueprint_path = Path(blueprint_path)
    project_root = Path(project_root)

    # Load artifacts from disk (read-only)
    blueprint = StoryBlueprint.from_yaml(blueprint_path)
    raw = yaml.safe_load(proposal_path.read_text(encoding="utf-8"))
    proposal = StructureProposal.model_validate(raw)

    # Derive operations
    operations = _build_operations_from_proposal(proposal, blueprint)

    # Compute before-state hashes for every touched artifact
    target_hashes = _collect_target_hashes(blueprint, operations)
    target_ids = sorted(target_hashes.keys())

    source_ids: list[str] = [proposal.proposal_id]
    if proposal.source_rule:
        source_ids.append(proposal.source_rule)

    # Build scope constraints
    scope = RevisionScope(
        target_artifact_ids=list(target_ids),
        allowed_fields=sorted({op.target_type for op in operations}),
        allowed_operations=sorted({op.operation_type for op in operations}),
    )

    # Stable content-addressed plan ID
    plan_id = _stable_plan_id(
        project=str(project_root.resolve()),
        source_ids=source_ids,
        target_ids=list(target_ids),
        target_hashes=target_hashes,
        operations=operations,
        scope=scope,
    )

    return StructuralRevisionPlan(
        plan_id=plan_id,
        project=str(project_root.resolve()),
        state=RevisionPlanState.DRAFT,
        source_ids=source_ids,
        target_artifact_ids=list(target_ids),
        target_hashes=target_hashes,
        operations=operations,
        scope=scope,
        created_at=datetime.now(timezone.utc).isoformat(),
        metadata={
            "proposal_id": proposal.proposal_id,
            "blueprint_path": str(blueprint_path.resolve()),
            "proposal_path": str(proposal_path.resolve()),
        },
    )


def plan_from_diagnostic(
    diagnostic: StructureDiagnostic,
    blueprint: StoryBlueprint,
    project_root: str | Path,
) -> StructuralRevisionPlan:
    """Create a revision plan directly from a single diagnostic and in-memory blueprint.

    Args:
        diagnostic: A structural diagnostic to address.
        blueprint: The StoryBlueprint to plan changes for.
        project_root: Project root directory.

    Returns:
        A StructuralRevisionPlan targeting the diagnostic's findings.

    The function does **not** mutate the blueprint or write any files.
    """
    project_root = Path(project_root)

    # Derive operations from the diagnostic
    operations = _build_operations_from_diagnostic(diagnostic, blueprint)

    # Compute before-state hashes
    target_hashes = _collect_target_hashes(blueprint, operations)
    target_ids = sorted(target_hashes.keys())

    source_ids = [f"diagnostic:{diagnostic.rule}"]

    scope = RevisionScope(
        target_artifact_ids=list(target_ids),
        allowed_fields=[diagnostic.layer.value],
        allowed_operations=[RevisionOperationType.UPDATE_OUTLINE_FIELD],
    )

    plan_id = _stable_plan_id(
        project=str(project_root.resolve()),
        source_ids=source_ids,
        target_ids=list(target_ids),
        target_hashes=target_hashes,
        operations=operations,
        scope=scope,
    )

    return StructuralRevisionPlan(
        plan_id=plan_id,
        project=str(project_root.resolve()),
        state=RevisionPlanState.DRAFT,
        source_ids=source_ids,
        target_artifact_ids=list(target_ids),
        target_hashes=target_hashes,
        operations=operations,
        scope=scope,
        created_at=datetime.now(timezone.utc).isoformat(),
        metadata={
            "diagnostic_rule": diagnostic.rule,
            "diagnostic_layer": diagnostic.layer.value,
            "diagnostic_severity": diagnostic.severity.value,
        },
    )
