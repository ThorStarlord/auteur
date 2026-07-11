from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from auteur.genre_pipeline.models import GenrePipelineSpec
from auteur.genre_pipeline.templates import build_pipeline_descriptor


@dataclass(frozen=True)
class PipelineValidationResult:
    is_valid: bool
    errors: list[str]
    warnings: list[str]


def _legacy_choices(template, choices: dict[int, dict[str, str]]) -> dict[int, dict[str, str]]:
    translated = {phase: dict(values) for phase, values in choices.items()}
    for phase, values in translated.items():
        raw_options = template.get_options(phase)
        if isinstance(raw_options, Mapping) and set(raw_options) == {"options"}:
            phase_id = str(template.phases[phase])
            if phase_id in values:
                values["options"] = values.pop(phase_id)
    return translated


def validate_pipeline_choices(
    spec: GenrePipelineSpec,
    core_id: str,
    choices: dict[int, dict[str, str]],
    *,
    require_complete: bool = False,
    strict_options: bool = True,
) -> PipelineValidationResult:
    descriptor = build_pipeline_descriptor(spec, core_id)
    phases = {phase.number: phase for phase in descriptor.phases}
    errors: list[str] = []

    if strict_options:
        for phase_number, selected_fields in choices.items():
            phase = phases.get(phase_number)
            if phase is None:
                errors.append(f"Unknown phase {phase_number}.")
                continue
            allowed_fields = {field.id: field for field in phase.fields}
            if phase.derived and selected_fields:
                errors.append(f"Phase {phase_number} is derived and does not accept selections.")
                continue
            for field_id, option_id in selected_fields.items():
                field = allowed_fields.get(field_id)
                if field is None:
                    errors.append(f"Phase {phase_number} has no field '{field_id}'.")
                    continue
                valid_ids = {option.id for option in field.options}
                if option_id not in valid_ids:
                    errors.append(
                        f"Phase {phase_number} field '{field_id}' has invalid option '{option_id}'."
                    )
    else:
        # Historical direct generator calls used synthetic structural choices,
        # but still relied on phases 1-3 to reject an invalid pipeline setup.
        for phase_number, selected_fields in choices.items():
            phase = phases.get(phase_number)
            if phase is None or phase.derived or phase_number >= 4:
                continue
            allowed_fields = {field.id: field for field in phase.fields}
            for field_id, option_id in selected_fields.items():
                field = allowed_fields.get(field_id)
                if field is None or option_id not in {option.id for option in field.options}:
                    errors.append(
                        f"Phase {phase_number} field '{field_id}' has invalid option '{option_id}'."
                    )

    if require_complete and strict_options:
        for phase in descriptor.phases:
            selected_fields = choices.get(phase.number, {})
            for field in phase.fields:
                if field.id not in selected_fields:
                    errors.append(f"Phase {phase.number} requires a '{field.id}' selection.")

    if errors:
        return PipelineValidationResult(False, errors, [])

    structural_phase = next(phase for phase in descriptor.phases if phase.number == 4)
    selected_forces = choices.get(4, {})
    if (
        strict_options
        and not require_complete
        and any(field.id not in selected_forces for field in structural_phase.fields)
    ):
        return PipelineValidationResult(True, [], [])

    template = spec.template_factory(core_id)
    is_valid, genre_errors, warnings = spec.validate_choices(
        template,
        _legacy_choices(template, choices),
    )
    return PipelineValidationResult(bool(is_valid), list(genre_errors), list(warnings))
