from __future__ import annotations
from pydantic import BaseModel, Field
from auteur.blueprint import Genre

class SubgenreModifier(BaseModel):
    id: str
    allowed_primary_genres: list[Genre]
    prompt_guidance: list[str] = Field(default_factory=list)
    trope_biases: list[str] = Field(default_factory=list)
    setup_biases: list[str] = Field(default_factory=list)
    scope_biases: list[str] = Field(default_factory=list)
    common_misuses: list[str] = Field(default_factory=list)

# Standard registered subgenre modifiers
_SUBGENRE_REGISTRY: dict[str, SubgenreModifier] = {
    "locked_room": SubgenreModifier(
        id="locked_room",
        allowed_primary_genres=[Genre.MYSTERY],
        prompt_guidance=[
            "Constrain the suspect pool, the physical location, and the crime timeline.",
            "Prioritize clue fairness and the puzzle mechanics of an apparently impossible crime."
        ],
        trope_biases=[
            "sealed location",
            "limited suspects",
            "impossible method",
            "clue-fair puzzle logic"
        ],
        setup_biases=[
            "Establish the layout of the crime scene and the accessibility constraints early."
        ],
        scope_biases=[
            "Focus structural weight on investigation and questioning rather than active chases."
        ],
        common_misuses=[
            "Introducing supernatural solutions or external actors at the last minute.",
            "Violating fair-play detective rules by withholding key physical evidence from the reader."
        ]
    ),
    "hardboiled": SubgenreModifier(
        id="hardboiled",
        allowed_primary_genres=[Genre.MYSTERY],
        prompt_guidance=[
            "Emphasize a cynical tone, moral ambiguity, and institutional rot.",
            "The detective should be professional but weary, operating in a corrupt city environment."
        ],
        trope_biases=[
            "weary private eye",
            "corrupt city administration",
            "femme fatale / homme fatale",
            "street-level violence"
        ],
        setup_biases=[
            "Introduce the protagonist's low financial/social baseline status and their cynical worldview."
        ],
        scope_biases=[
            "Introduce multiple overlapping societal threads showing systemic rot."
        ],
        common_misuses=[
            "Solving the crime cleanly with the justice system triumphing completely.",
            "Making the detective protagonist too clean or ethically uncompromised."
        ]
    ),
    "cozy": SubgenreModifier(
        id="cozy",
        allowed_primary_genres=[Genre.MYSTERY],
        prompt_guidance=[
            "Set the story in a small, tight-knit community with an amateur detective protagonist.",
            "Keep active physical violence off-screen and focus on social/interpersonal dynamics."
        ],
        trope_biases=[
            "small-town secrets",
            "eccentric suspects",
            "hobbyist sleuth",
            "tidy/moral resolution"
        ],
        setup_biases=[
            "Establish the warmth and eccentric charm of the community and the detective's day-to-day hobby/job."
        ],
        scope_biases=[
            "Minimize external action/thriller pacing; keep stakes focused on community restoration."
        ],
        common_misuses=[
            "Introducing explicit torture, gore, or graphic sexual violence.",
            "Leaving the community fractured and unsafe at the end of the story."
        ]
    )
}

def load_subgenre_modifier(subgenre_id: str) -> SubgenreModifier | None:
    """Retrieve the SubgenreModifier for the given subgenre identifier.
    
    Returns None if the subgenre is not pre-registered.
    """
    return _SUBGENRE_REGISTRY.get(subgenre_id.lower().strip())
