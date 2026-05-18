from __future__ import annotations

from auteur.blueprint import (
    InteractionModel,
    MediumContract,
    MediumFormat,
    ReleaseModel,
    StoryMedium,
    UnitOfDelivery,
)

_REGISTRY_CACHE: dict[StoryMedium, MediumContract] = {}


def load_medium_contract(medium: StoryMedium | str) -> MediumContract:
    if isinstance(medium, str):
        try:
            medium_enum = StoryMedium(medium)
        except ValueError:
            medium_enum = StoryMedium.OTHER
    else:
        medium_enum = medium

    if medium_enum in _REGISTRY_CACHE:
        return _REGISTRY_CACHE[medium_enum]

    contract = _MEDIUM_CONTRACTS.get(medium_enum, _create_fallback_contract(medium_enum))
    _REGISTRY_CACHE[medium_enum] = contract
    return contract


def _contract(
    *,
    medium: StoryMedium,
    format: MediumFormat,
    release_model: ReleaseModel,
    interaction_model: InteractionModel,
    unit_of_delivery: UnitOfDelivery,
    representation_units: list[str],
    modulation_biases: list[str],
    medium_failure_modes: list[str],
) -> MediumContract:
    return MediumContract(
        medium=medium,
        format=format,
        release_model=release_model,
        interaction_model=interaction_model,
        unit_of_delivery=unit_of_delivery,
        representation_units=representation_units,
        modulation_biases=modulation_biases,
        medium_failure_modes=medium_failure_modes,
    )


def _create_fallback_contract(medium: StoryMedium) -> MediumContract:
    return _contract(
        medium=medium,
        format=MediumFormat.OTHER,
        release_model=ReleaseModel.OTHER,
        interaction_model=InteractionModel.OTHER,
        unit_of_delivery=UnitOfDelivery.OTHER,
        representation_units=["declared delivery units"],
        modulation_biases=["match pacing to the declared delivery form"],
        medium_failure_modes=["medium delivery grammar is underspecified"],
    )


_MEDIUM_CONTRACTS: dict[StoryMedium, MediumContract] = {
    StoryMedium.NOVEL: _contract(
        medium=StoryMedium.NOVEL,
        format=MediumFormat.STANDALONE_BOOK,
        release_model=ReleaseModel.COMPLETE_RELEASE,
        interaction_model=InteractionModel.PASSIVE_READER,
        unit_of_delivery=UnitOfDelivery.CHAPTER,
        representation_units=["prose narration", "scenes", "chapters"],
        modulation_biases=[
            "sustained immersion",
            "controlled interiority",
            "chapter-level tension curves",
        ],
        medium_failure_modes=[
            "delivery relies on spectacle the prose cannot directly show",
            "chapter pacing ignores reader re-entry and exit points",
        ],
    ),
    StoryMedium.SHORT_STORY: _contract(
        medium=StoryMedium.SHORT_STORY,
        format=MediumFormat.SHORT_FORM,
        release_model=ReleaseModel.COMPLETE_RELEASE,
        interaction_model=InteractionModel.PASSIVE_READER,
        unit_of_delivery=UnitOfDelivery.STORY,
        representation_units=["compressed prose", "scenes", "turns"],
        modulation_biases=["compression", "single dominant movement"],
        medium_failure_modes=["too many threads for the available runway"],
    ),
    StoryMedium.NOVELLA: _contract(
        medium=StoryMedium.NOVELLA,
        format=MediumFormat.NOVELLA,
        release_model=ReleaseModel.COMPLETE_RELEASE,
        interaction_model=InteractionModel.PASSIVE_READER,
        unit_of_delivery=UnitOfDelivery.CHAPTER,
        representation_units=["prose narration", "scenes", "chapters"],
        modulation_biases=["focused escalation", "limited subplot spread"],
        medium_failure_modes=["novel-scale machinery crowds the shorter form"],
    ),
    StoryMedium.SERIES: _contract(
        medium=StoryMedium.SERIES,
        format=MediumFormat.BOOK_SERIES,
        release_model=ReleaseModel.EPISODIC_SERIAL,
        interaction_model=InteractionModel.SERIAL_READER,
        unit_of_delivery=UnitOfDelivery.BOOK,
        representation_units=["books", "series arcs", "installment payoffs"],
        modulation_biases=["long-term escalation", "installment closure"],
        medium_failure_modes=["book-level promises do not pay off while the series arc waits"],
    ),
    StoryMedium.FILM: _contract(
        medium=StoryMedium.FILM,
        format=MediumFormat.FEATURE_FILM,
        release_model=ReleaseModel.COMPLETE_RELEASE,
        interaction_model=InteractionModel.PASSIVE_VIEWER,
        unit_of_delivery=UnitOfDelivery.SCENE,
        representation_units=["scenes", "sequences", "visual reveals"],
        modulation_biases=["visual causality", "compressed scene economy"],
        medium_failure_modes=["internal change has no visible expression"],
    ),
    StoryMedium.TV: _contract(
        medium=StoryMedium.TV,
        format=MediumFormat.EPISODIC_TV,
        release_model=ReleaseModel.SEASONAL_DROPS,
        interaction_model=InteractionModel.PASSIVE_VIEWER,
        unit_of_delivery=UnitOfDelivery.EPISODE,
        representation_units=["episodes", "season arcs", "act breaks"],
        modulation_biases=["episode propulsion", "season-level payoff"],
        medium_failure_modes=["episodes lack local engines"],
    ),
    StoryMedium.VISUAL_NOVEL: _contract(
        medium=StoryMedium.VISUAL_NOVEL,
        format=MediumFormat.ROUTE_BASED,
        release_model=ReleaseModel.COMPLETE_RELEASE,
        interaction_model=InteractionModel.CHOICE_BASED_READER,
        unit_of_delivery=UnitOfDelivery.SCENE_NODE,
        representation_units=[
            "dialogue",
            "narration boxes",
            "choices",
            "routes",
            "CG events",
            "endings",
        ],
        modulation_biases=[
            "character intimacy",
            "branching emotional payoff",
            "route-specific escalation",
        ],
        medium_failure_modes=[
            "choices do not express meaningful pressure",
            "route payoffs repeat without changing the structural question",
        ],
    ),
    StoryMedium.GAME: _contract(
        medium=StoryMedium.GAME,
        format=MediumFormat.ACTION_GAME,
        release_model=ReleaseModel.COMPLETE_OR_LIVE_SERVICE,
        interaction_model=InteractionModel.PLAYER_AGENCY,
        unit_of_delivery=UnitOfDelivery.MISSION,
        representation_units=[
            "gameplay encounters",
            "level design",
            "cutscenes",
            "mechanics",
            "boss fights",
            "environmental storytelling",
        ],
        modulation_biases=[
            "playable tension",
            "mechanical escalation",
            "short narrative inserts between action loops",
        ],
        medium_failure_modes=[
            "story stakes are not expressed through play pressure",
            "cutscenes carry promises that mechanics contradict",
        ],
    ),
    StoryMedium.INTERACTIVE_FICTION: _contract(
        medium=StoryMedium.INTERACTIVE_FICTION,
        format=MediumFormat.BRANCHING_TEXT,
        release_model=ReleaseModel.COMPLETE_RELEASE,
        interaction_model=InteractionModel.CHOICE_BASED_READER,
        unit_of_delivery=UnitOfDelivery.CHOICE_NODE,
        representation_units=["passages", "choices", "branches", "end states"],
        modulation_biases=["choice consequence", "state-aware prose"],
        medium_failure_modes=["branches multiply without structural payoff"],
    ),
    StoryMedium.OTHER: _create_fallback_contract(StoryMedium.OTHER),
}
