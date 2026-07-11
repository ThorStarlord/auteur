from __future__ import annotations

from collections.abc import Callable

from auteur.blueprint import Genre, StoryMode
from auteur.genre_pipeline.models import CoreIdentityProfile, GenrePipelineSpec


_PROFILES: dict[str, CoreIdentityProfile] = {
    "classic_humiliation": CoreIdentityProfile(
        display_name="Classic Humiliation",
        default_title="The Cost of Love",
        default_mode=StoryMode.TRAGIC,
        progression="unease -> suspicion -> humiliation -> acceptance",
        avoided_experiences=("triumphant vindication", "cozy comfort", "clean redemption"),
    ),
    "horror": CoreIdentityProfile(
        display_name="Netorare Horror",
        default_title="The Inescapable",
        default_mode=StoryMode.TRAGIC,
        progression="unease -> dread -> cosmic horror -> transformation",
        avoided_experiences=("cozy safety", "triumphant power fantasy", "return to normalcy"),
    ),
    "mystery": CoreIdentityProfile(
        display_name="Netorare Mystery",
        default_title="The Hidden Truth",
        default_mode=StoryMode.NOIR,
        progression="curiosity -> suspicion -> revelation -> complicity",
        avoided_experiences=("ignorant innocence", "pure heroic victory", "easy answers"),
    ),
    "howdunit": CoreIdentityProfile(
        display_name="Classic Detective Mystery",
        default_title="Untitled: Classic Detective Mystery",
        default_mode=StoryMode.PROCEDURAL,
        progression="curiosity -> investigation -> deduction -> revelation",
        avoided_experiences=("unsolvable puzzle", "random culprit", "explanation by coincidence"),
    ),
    "paranoia": CoreIdentityProfile(
        display_name="Paranoia",
        default_title="Untitled: Paranoia",
        default_mode=StoryMode.NOIR,
        progression="unease -> suspicion -> paranoia -> transformation",
        avoided_experiences=("cozy safety", "absolute trust", "simple solutions"),
    ),
    "cozy": CoreIdentityProfile(
        display_name="Cozy Mystery",
        default_title="Untitled: Cozy Mystery",
        default_mode=StoryMode.COMIC,
        progression="curiosity -> discovery -> comfort -> satisfaction",
        avoided_experiences=("graphic brutality", "nihilistic resolution", "community destroyed"),
    ),
    "sensual_dominance": CoreIdentityProfile(
        display_name="Sensual Dominance",
        default_title="Untitled: Sensual Dominance",
        default_mode=StoryMode.INTIMATE,
        progression="intrigue -> playful_teasing -> deepening_connection -> intimate_confidence -> sustained_delight",
        secondary_emotions=("trust", "enjoyment", "agency", "anticipation"),
        avoided_experiences=("shame", "humiliation_without_consent", "coercion", "fear"),
    ),
    "tender_surrender": CoreIdentityProfile(
        display_name="Tender Surrender",
        default_title="Untitled: Tender Surrender",
        default_mode=StoryMode.INTIMATE,
        progression="defensiveness -> curiosity -> gradual_opening -> blissful_release -> cherished_security",
        secondary_emotions=("trust", "freedom", "emotional_growth", "acceptance"),
        avoided_experiences=("coercion", "manipulation", "abandonment", "exposure"),
    ),
    "romantic_authority": CoreIdentityProfile(
        display_name="Romantic Authority",
        default_title="Untitled: Romantic Authority",
        default_mode=StoryMode.INTIMATE,
        progression="admiration -> willing_deference -> secure_interdependence -> mutual_respect -> sustained_love",
        secondary_emotions=("respect", "care", "partnership", "confidence"),
        avoided_experiences=("inequality", "control_without_care", "diminishment", "resentment"),
    ),
}


def _profile_factory(core_ids: tuple[str, ...]) -> Callable[[str], CoreIdentityProfile]:
    def load(core_id: str) -> CoreIdentityProfile:
        if core_id not in core_ids:
            raise ValueError(f"Unknown core_id: {core_id}")
        return _PROFILES[core_id]

    return load


def _contract_loader(genre: Genre):
    def load():
        from auteur.genres.registry import load_genre_contract

        return load_genre_contract(genre)

    return load


def _netorare_spec() -> GenrePipelineSpec:
    from auteur.netorare.core_templates import HumiliationTemplate, HorrorTemplate, MysteryTemplate
    from auteur.netorare.validation import validate_choices

    core_ids = ("classic_humiliation", "horror", "mystery")
    templates = {
        "classic_humiliation": HumiliationTemplate,
        "horror": HorrorTemplate,
        "mystery": MysteryTemplate,
    }
    return GenrePipelineSpec(
        genre=Genre.NETORARE,
        slug="netorare",
        core_ids=core_ids,
        default_core_id="classic_humiliation",
        default_port=8765,
        browser_title="Netorare Story Identity Authoring",
        template_factory=lambda core_id: templates[core_id](),
        validate_choices=validate_choices,
        contract_loader=_contract_loader(Genre.NETORARE),
        identity_profile_factory=_profile_factory(core_ids),
    )


def _mystery_spec() -> GenrePipelineSpec:
    from auteur.mystery.core_templates import CozyTemplate, HowdunitTemplate, ParanoiaTemplate
    from auteur.mystery.validation import validate_choices

    core_ids = ("howdunit", "paranoia", "cozy")
    templates = {"howdunit": HowdunitTemplate, "paranoia": ParanoiaTemplate, "cozy": CozyTemplate}
    return GenrePipelineSpec(
        genre=Genre.MYSTERY,
        slug="mystery",
        core_ids=core_ids,
        default_core_id="howdunit",
        default_port=8766,
        browser_title="Mystery Story Identity Authoring",
        template_factory=lambda core_id: templates[core_id](),
        validate_choices=validate_choices,
        contract_loader=_contract_loader(Genre.MYSTERY),
        identity_profile_factory=_profile_factory(core_ids),
    )


def _gentlefemdom_spec() -> GenrePipelineSpec:
    from auteur.gentlefemdom.core_templates import (
        RomanticAuthorityTemplate,
        SensualDominanceTemplate,
        TenderSurrenderTemplate,
    )
    from auteur.gentlefemdom.validation import validate_choices

    core_ids = ("sensual_dominance", "tender_surrender", "romantic_authority")
    templates = {
        "sensual_dominance": SensualDominanceTemplate,
        "tender_surrender": TenderSurrenderTemplate,
        "romantic_authority": RomanticAuthorityTemplate,
    }
    return GenrePipelineSpec(
        genre=Genre.GENTLEFEMDOM,
        slug="gentlefemdom",
        core_ids=core_ids,
        default_core_id="sensual_dominance",
        default_port=8767,
        browser_title="Gentle Femdom Story Identity Authoring",
        template_factory=lambda core_id: templates[core_id](),
        validate_choices=validate_choices,
        contract_loader=_contract_loader(Genre.GENTLEFEMDOM),
        identity_profile_factory=_profile_factory(core_ids),
    )


_SPECS: dict[Genre, GenrePipelineSpec] | None = None


def _specs() -> dict[Genre, GenrePipelineSpec]:
    global _SPECS
    if _SPECS is None:
        _SPECS = {
            Genre.NETORARE: _netorare_spec(),
            Genre.MYSTERY: _mystery_spec(),
            Genre.GENTLEFEMDOM: _gentlefemdom_spec(),
        }
    return _SPECS


def get_genre_pipeline(genre: Genre | str) -> GenrePipelineSpec:
    try:
        genre_enum = genre if isinstance(genre, Genre) else Genre(genre)
        return _specs()[genre_enum]
    except (KeyError, ValueError) as exc:
        raise ValueError(f"No built-in interactive pipeline for genre: {genre}") from exc


def get_all_genres() -> list[GenrePipelineSpec]:
    return list(_specs().values())


def get_genre_pipeline_for_core(core_id: str) -> GenrePipelineSpec:
    matches = [spec for spec in get_all_genres() if core_id in spec.core_ids]
    if len(matches) != 1:
        raise ValueError(f"Unknown or ambiguous core_id: {core_id}")
    return matches[0]
