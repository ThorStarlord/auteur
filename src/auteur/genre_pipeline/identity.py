from __future__ import annotations

from dataclasses import dataclass
from types import SimpleNamespace

from auteur.blueprint import StoryMedium, StoryMode, TargetAudience, TargetExperience
from auteur.genre_pipeline.models import GenrePipelineSpec
from auteur.genre_pipeline.templates import build_pipeline_descriptor
from auteur.genre_pipeline.validation import validate_pipeline_choices
from auteur.identity import HighLevelCentralEngine, StoryIdentity, StoryType
from auteur.structure.diagnostics import DiagnosticSeverity, StructureDiagnostic


class IdentityCompilationError(ValueError):
    pass


def build_semantic_identity_preview(template, choices: dict[int, dict[str, str]]):
    """Build the minimal neutral view required by semantic validators."""
    del choices
    return SimpleNamespace(
        target_experience=SimpleNamespace(primary=str(template.primary_emotion)),
        author_overrides=[],
    )


@dataclass(frozen=True)
class IdentityCompilationResult:
    identity: StoryIdentity
    diagnostics: tuple[StructureDiagnostic, ...]
    choice_warnings: tuple[str, ...] = ()

    @property
    def error_diagnostics(self) -> tuple[StructureDiagnostic, ...]:
        return tuple(
            diagnostic
            for diagnostic in self.diagnostics
            if diagnostic.severity == DiagnosticSeverity.ERROR
        )

    @property
    def warning_diagnostics(self) -> tuple[StructureDiagnostic, ...]:
        return tuple(
            diagnostic
            for diagnostic in self.diagnostics
            if diagnostic.severity == DiagnosticSeverity.WARNING
        )


def _strip_force_prefix(field: str, label: str) -> str:
    prefix = f"{field}:"
    return label[len(prefix) :].strip() if label.casefold().startswith(prefix) else label


def _option_label(template, phase: int, field: str, option_id: str) -> str:
    try:
        return str(template.get_option_label(phase, field, option_id))
    except (AttributeError, KeyError):
        return option_id.replace("_", " ").replace("-", " ")


def _central_engine(template, choices: dict[int, dict[str, str]]) -> HighLevelCentralEngine:
    selected = choices.get(4, {})
    labels = {
        field: _strip_force_prefix(field, _option_label(template, 4, field, option_id))
        for field, option_id in selected.items()
        if field in {"want", "resistance", "conflict", "stakes", "change"}
    }
    want = labels.get("want", "Pursue the central desire")
    resistance = labels.get("resistance", "An inescapable opposing force")
    change = labels.get("change", "Become permanently changed")
    conflict = labels.get(
        "conflict",
        f"The want to {want.lower()} faces {resistance}, forcing a choice to {change.lower()}.",
    )
    stakes = labels.get("stakes", f"The cost of failing to {want.lower()}")
    return HighLevelCentralEngine(
        want=want,
        resistance=resistance,
        conflict=conflict,
        stakes=stakes,
        change=change,
    )


def _open_questions(spec: GenrePipelineSpec, core_id: str, choices: dict[int, dict[str, str]]) -> list[str]:
    descriptor = build_pipeline_descriptor(spec, core_id)
    template = spec.template_factory(core_id)
    questions: list[str] = []
    for phase in descriptor.phases:
        if phase.number < 5:
            continue
        for field, option_id in choices.get(phase.number, {}).items():
            label = _option_label(template, phase.number, field, option_id)
            questions.append(
                f"How will {phase.label.lower()} make '{label}' visible in the story?"
            )
    return questions


def _alternatives(spec: GenrePipelineSpec, core_id: str, choices: dict[int, dict[str, str]]) -> list[str]:
    descriptor = build_pipeline_descriptor(spec, core_id)
    alternatives: list[str] = []
    for phase in descriptor.phases:
        if phase.number < 5:
            continue
        selected = set(choices.get(phase.number, {}).values())
        for field in phase.fields:
            alternative = next((option for option in field.options if option.id not in selected), None)
            if alternative:
                alternatives.append(
                    f"For {phase.label}, consider '{alternative.label}' instead."
                )
                break
        if len(alternatives) == 3:
            break
    return alternatives


def compile_story_identity(
    spec: GenrePipelineSpec,
    core_id: str,
    choices: dict[int, dict[str, str]],
    *,
    working_title: str | None = None,
    mode: StoryMode | str | None = None,
    require_complete: bool = True,
    strict_options: bool = True,
) -> IdentityCompilationResult:
    validation = validate_pipeline_choices(
        spec,
        core_id,
        choices,
        require_complete=require_complete,
        strict_options=strict_options,
    )
    if not validation.is_valid:
        raise IdentityCompilationError(
            f"Choice validation failed: {'; '.join(validation.errors)}"
        )

    profile = spec.identity_profile_factory(core_id)
    template = spec.template_factory(core_id)
    contract = spec.contract_loader()
    engine = _central_engine(template, choices)
    resolved_mode = profile.default_mode if mode is None else StoryMode(mode)
    title = (working_title or profile.default_title).strip()
    if not title:
        raise IdentityCompilationError("Working title must not be empty")

    identity = StoryIdentity(
        title=title,
        core_answer=(
            f"{engine.want} faces {engine.resistance}. The defining conflict is "
            f"{engine.conflict}; the stakes are {engine.stakes}, and the intended "
            f"transformation is {engine.change}."
        ),
        target_experience=TargetExperience(
            primary=str(template.primary_emotion),
            progression=profile.progression,
            secondary=list(profile.secondary_emotions),
            avoid=list(profile.avoided_experiences),
        ),
        story_type=StoryType(
            medium=StoryMedium.NOVEL,
            mode=resolved_mode,
            genre=spec.genre,
            target_audience=TargetAudience.ADULT,
            length_class=contract.scope_profile.default_length,
        ),
        central_engine=engine,
        open_questions=_open_questions(spec, core_id, choices),
        alternatives=_alternatives(spec, core_id, choices),
        confidence=0.75,
        genre_contract_snapshot=contract,
    )
    diagnostics = tuple(identity.validate_identity())
    errors = [diagnostic for diagnostic in diagnostics if diagnostic.severity == DiagnosticSeverity.ERROR]
    if errors:
        raise IdentityCompilationError("; ".join(diagnostic.message for diagnostic in errors))
    return IdentityCompilationResult(
        identity=identity,
        diagnostics=diagnostics,
        choice_warnings=tuple(validation.warnings),
    )
