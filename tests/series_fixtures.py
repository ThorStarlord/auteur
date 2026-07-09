from __future__ import annotations


def valid_trilogy_data() -> dict:
    return {
        "title": "The Ash Empire Trilogy",
        "series_type": "trilogy",
        "core_question": "Can civilization survive without sacrificing humanity?",
        "target_experience": {
            "primary": "inevitability",
            "progression": "fragile order -> collapse -> costly renewal",
            "avoid": ["randomness"],
        },
        "global_arc": {
            "beginning": "Order exists but depends on suppression.",
            "midpoint": "Order collapses into civil war.",
            "ending": "A new order emerges at personal cost.",
        },
        "book_plans": [
            {
                "book_number": 1,
                "title": "Ashes of Order",
                "series_function": "question",
                "core_answer": "Elena exposes the empire's cruelty and chooses rebellion.",
                "target_experience": {
                    "primary": "dread",
                    "progression": "security -> suspicion -> rupture",
                    "avoid": [],
                },
                "story_type": {
                    "medium": "novel",
                    "mode": "tragic",
                    "genre": "grimdark_fantasy",
                    "subgenres": [],
                    "target_audience": "adult",
                    "length_class": None,
                },
                "central_engine": {
                    "want": "Elena wants to preserve peace in the imperial capital.",
                    "resistance": "The empire's peace depends on hidden executions and coerced loyalty.",
                    "conflict": "Protecting order requires Elena to defend atrocities she can no longer excuse.",
                    "stakes": "The capital falls into revolt and Elena loses her moral identity.",
                    "change": "Elena changes from obedient idealist into a public dissident.",
                },
                "series_threads_carried": ["elena_arc", "empire_arc", "emperor_identity"],
                "required_setups": ["emperor_identity"],
                "required_payoffs": [],
                "scope": "city",
                "climax_intensity": 6,
            },
            {
                "book_number": 2,
                "title": "The Civil Crown",
                "series_function": "complication",
                "core_answer": "Elena leads a revolution and learns victory can repeat imperial cruelty.",
                "target_experience": {
                    "primary": "pressure",
                    "progression": "momentum -> exhaustion -> fracture",
                    "avoid": [],
                },
                "story_type": {
                    "medium": "novel",
                    "mode": "tragic",
                    "genre": "grimdark_fantasy",
                    "subgenres": [],
                    "target_audience": "adult",
                    "length_class": None,
                },
                "central_engine": {
                    "want": "Elena wants to win the civil war without becoming a tyrant.",
                    "resistance": "Every faction demands compromises that harm civilians.",
                    "conflict": "Mercy weakens the revolution while ruthlessness corrupts it.",
                    "stakes": "The rebellion fails or becomes indistinguishable from the empire.",
                    "change": "Elena changes from revolutionary symbol into exhausted commander.",
                },
                "series_threads_carried": ["elena_arc", "empire_arc", "emperor_identity"],
                "required_setups": [],
                "required_payoffs": [],
                "scope": "national",
                "climax_intensity": 8,
            },
            {
                "book_number": 3,
                "title": "The Human Throne",
                "series_function": "resolution",
                "core_answer": "Elena defeats the emperor and accepts rule as a burden, not a prize.",
                "target_experience": {
                    "primary": "catharsis",
                    "progression": "desperation -> sacrifice -> renewal",
                    "avoid": [],
                },
                "story_type": {
                    "medium": "novel",
                    "mode": "tragic",
                    "genre": "grimdark_fantasy",
                    "subgenres": [],
                    "target_audience": "adult",
                    "length_class": None,
                },
                "central_engine": {
                    "want": "Elena wants to end the imperial cycle permanently.",
                    "resistance": "The revealed emperor has made every faction dependent on imperial machinery.",
                    "conflict": "Destroying the throne may destroy the only structure keeping millions alive.",
                    "stakes": "Civilization collapses or survives by repeating its founding sin.",
                    "change": "Elena changes from exhausted commander into reluctant ruler.",
                },
                "series_threads_carried": ["elena_arc", "empire_arc", "emperor_identity"],
                "required_setups": [],
                "required_payoffs": ["emperor_identity"],
                "scope": "civilizational",
                "climax_intensity": 10,
            },
        ],
        "character_arcs": [
            {
                "id": "elena_arc",
                "character": "Elena",
                "start_state": "naive idealist",
                "end_state": "reluctant ruler",
                "planned_completion_book": 3,
                "book_states": {
                    "1": "public dissident",
                    "2": "exhausted commander",
                    "3": "reluctant ruler",
                },
                "transitions": {
                    "1->2": "war pressure turns dissent into command.",
                    "2->3": "the final sacrifice makes rule unavoidable.",
                },
            }
        ],
        "relationship_arcs": [
            {
                "id": "elena_marcus",
                "participants": ["Elena", "Marcus"],
                "start_state": "trust",
                "end_state": "tempered loyalty",
                "book_states": {"1": "trust", "2": "fracture", "3": "tempered loyalty"},
            }
        ],
        "faction_arcs": [
            {
                "id": "empire_arc",
                "faction": "Empire",
                "start_state": "stable",
                "end_state": "reconstituted",
                "book_states": {"1": "exposed", "2": "civil_war", "3": "reconstituted"},
            }
        ],
        "mysteries": [
            {
                "id": "emperor_identity",
                "question": "Who truly controls the emperor?",
                "introduced_book": 1,
                "expected_payoff_book": 3,
                "actual_payoff_book": 3,
            }
        ],
        "dependency_edges": [
            {
                "source": "book_1",
                "target": "emperor_identity",
                "type": "sets_up",
                "description": "Book 1 introduces the hidden emperor question.",
            },
            {
                "source": "emperor_identity",
                "target": "book_3",
                "type": "pays_off",
                "description": "The reveal drives the final book climax.",
            },
            {
                "source": "emperor_identity",
                "target": "elena_arc",
                "type": "pressures",
                "description": "The reveal forces Elena to accept rule.",
            },
        ],
        "recurring_symbols": ["ash crown", "broken gates"],
    }
