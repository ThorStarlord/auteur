from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from auteur.blueprint import StoryMode
from auteur.genre_pipeline.models import (
    GenrePipelineDescriptor,
    GenrePipelineSpec,
    PipelineField,
    PipelineOption,
    PipelinePhase,
)


_FORCE_FIELDS = ("want", "resistance", "conflict", "stakes", "change")


def _humanize(value: str) -> str:
    return value.replace("_", " ").replace("-", " ").title()


def _as_option(raw: Any) -> PipelineOption:
    if isinstance(raw, Mapping):
        data = raw
    elif hasattr(raw, "to_dict"):
        data = raw.to_dict()
    else:
        data = {
            "id": getattr(raw, "id"),
            "label": getattr(raw, "label"),
            "description": getattr(raw, "description", ""),
        }
    return PipelineOption(
        id=str(data["id"]),
        label=str(data["label"]),
        description=str(data.get("description", "")),
    )


def normalize_template_options(template: Any, phase_number: int) -> list[PipelineField]:
    """Normalize legacy mapping and flat option layouts without genre dispatch."""

    raw_options = template.get_options(phase_number)
    phase_id = str(template.phases[phase_number])

    if isinstance(raw_options, Mapping):
        groups = dict(raw_options)
        if set(groups) == {"options"}:
            groups = {phase_id: groups["options"]}
    elif isinstance(raw_options, Sequence) and not isinstance(raw_options, (str, bytes)):
        if phase_number == 4:
            groups = {field: [] for field in _FORCE_FIELDS}
            for raw in raw_options:
                option_id = str(raw["id"] if isinstance(raw, Mapping) else raw.id)
                prefix = option_id.split("-", 1)[0]
                groups.setdefault(prefix if prefix in _FORCE_FIELDS else phase_id, []).append(raw)
            groups = {key: values for key, values in groups.items() if values}
        else:
            groups = {phase_id: list(raw_options)}
    else:
        raise TypeError(f"Unsupported options shape for phase {phase_number}: {type(raw_options).__name__}")

    return [
        PipelineField(
            id=str(field_id),
            label=_humanize(str(field_id)),
            options=[_as_option(option) for option in options],
        )
        for field_id, options in groups.items()
        if options
    ]


def _normalize_constraints(template: Any, phase_number: int) -> list[str]:
    constraints = template.get_constraints(phase_number)
    if not constraints:
        return []
    if isinstance(constraints, str):
        return [constraints]
    return [str(constraint) for constraint in constraints]


def _derived_summary(spec: GenrePipelineSpec, core_id: str, phase_number: int) -> str:
    profile = spec.identity_profile_factory(core_id)
    contract = spec.contract_loader()
    if phase_number == 1:
        return f"{profile.display_name}: {spec.template_factory(core_id).primary_emotion}"
    if phase_number == 2:
        return f"{contract.display_name}: {contract.audience_product}"
    if phase_number == 3:
        default_length = contract.scope_profile.default_length.value
        return f"Default story length: {default_length.replace('_', ' ')}"
    return "No author selection is required for this phase."


def build_pipeline_descriptor(spec: GenrePipelineSpec, core_id: str) -> GenrePipelineDescriptor:
    if core_id not in spec.core_ids:
        raise ValueError(f"Unknown core_id '{core_id}' for {spec.slug}")

    template = spec.template_factory(core_id)
    profile = spec.identity_profile_factory(core_id)
    phases: list[PipelinePhase] = []
    for number in range(1, 10):
        phase_id = str(template.phases[number])
        fields = normalize_template_options(template, number)
        derived = not fields
        phases.append(
            PipelinePhase(
                number=number,
                id=phase_id,
                label=_humanize(phase_id),
                derived=derived,
                derived_summary=_derived_summary(spec, core_id, number) if derived else "",
                fields=fields,
                constraints=_normalize_constraints(template, number),
            )
        )

    return GenrePipelineDescriptor(
        genre=spec.genre,
        slug=spec.slug,
        core_id=core_id,
        browser_title=spec.browser_title,
        default_title=profile.default_title,
        default_mode=profile.default_mode,
        available_modes=list(StoryMode),
        phases=phases,
    )
