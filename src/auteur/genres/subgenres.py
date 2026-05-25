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
    ),
    "chosen_one": SubgenreModifier(
        id="chosen_one",
        allowed_primary_genres=[Genre.EPIC_FANTASY, Genre.YA_FANTASY],
        prompt_guidance=[
            "The protagonist is uniquely destined to resolve the central conflict, but their agency in accepting or rejecting this destiny is the dramatic engine.",
            "Avoid making destiny a shortcut around character choice and growth."
        ],
        trope_biases=[
            "prophecy or ancient selection",
            "unique power or birthright",
            "mentor who reveals the truth",
            "journey to accept or reject fate"
        ],
        setup_biases=[
            "Establish the protagonist's ordinary life before the destiny reveal."
        ],
        scope_biases=[
            "Expect a journey structure: preparation, testing, confrontation."
        ],
        common_misuses=[
            "The prophecy removes all agency and surprise.",
            "The chosen one status excuses the protagonist from earning their growth."
        ]
    ),
    "fish_out_of_water": SubgenreModifier(
        id="fish_out_of_water",
        allowed_primary_genres=[Genre.EPIC_FANTASY, Genre.URBAN_FANTASY, Genre.YA_FANTASY, Genre.SCI_FI],
        prompt_guidance=[
            "The protagonist is displaced from their natural environment and must adapt to a world with different rules, culture, or physics.",
            "The dramatic tension comes from the gap between the protagonist's original skills and the new world's demands."
        ],
        trope_biases=[
            "protagonist from a different world or culture",
            "learning the rules of the new environment",
            "mistakes born of cultural ignorance",
            "bridge between two worlds"
        ],
        setup_biases=[
            "Establish the protagonist's original world thoroughly so the contrast lands."
        ],
        scope_biases=[
            "Expect discovery and adaptation arcs before the main conflict escalates."
        ],
        common_misuses=[
            "The protagonist adapts too quickly, losing the fish-out-of-water tension.",
            "The original world is forgotten once the new world is revealed."
        ]
    ),
    "second_chance": SubgenreModifier(
        id="second_chance",
        allowed_primary_genres=[Genre.ROMANCE],
        prompt_guidance=[
            "The protagonists have a prior history — often a relationship that ended badly or an unresolved connection — and the story is about whether they can rebuild something different.",
            "The narrative weight is on the history, the wound, and whether trust can be restored."
        ],
        trope_biases=[
            "prior relationship history",
            "unresolved feelings or resentment",
            "forced proximity rekindling connection",
            "the question of whether people can really change"
        ],
        setup_biases=[
            "Establish the history and the original wound or separation cause."
        ],
        scope_biases=[
            "Need enough runway for the history to matter and the rebuilding to feel earned."
        ],
        common_misuses=[
            "The original wound is too trivial to justify the separation.",
            "The reunion is resolved without earning the reconciliation."
        ]
    ),
    "hard_sci_fi": SubgenreModifier(
        id="hard_sci_fi",
        allowed_primary_genres=[Genre.SCI_FI],
        prompt_guidance=[
            "The speculative premise is grounded in real or extrapolated science. The story respects known physics and technology constraints.",
            "The intellectual rigor of the premise is part of the reader's product, not just window dressing."
        ],
        trope_biases=[
            "rigorous scientific extrapolation",
            "technology with realistic limitations",
            "problem-solving through genuine scientific reasoning",
            "human adaptation to real physical constraints"
        ],
        setup_biases=[
            "Establish the scientific premise and its rules early and clearly."
        ],
        scope_biases=[
            "Expect slower pacing to allow for exposition and problem-solving scenes."
        ],
        common_misuses=[
            "The science is handwaved when it becomes inconvenient.",
            "Characters solve problems through technology rather than human choice."
        ]
    ),
}

def load_subgenre_modifier(subgenre_id: str) -> SubgenreModifier | None:
    """Retrieve the SubgenreModifier for the given subgenre identifier.
    
    Returns None if the subgenre is not pre-registered.
    """
    return _SUBGENRE_REGISTRY.get(subgenre_id.lower().strip())
