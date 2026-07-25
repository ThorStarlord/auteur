"""Fixture: scene_revision_publish — scene realization with publishable state.

Creates an Auteur project where:
- Complete blueprint with full story_engine.
- Chapter structure exists with outlines.
- Scene realization exists (``chapters/ch_001/realization/``) — a SceneOutline
  in YAML format, saved via the SceneLoader convention.
- Scene has expression candidates (``chapters/ch_001/scenes/<scene_id>/``)
  with prose candidates (``prose_v001.yaml`` + ``prose_v001.md``) in the
  ExpressionStore format.
- Chapter has an accepted expression (``chapters/ch_001/expression/accepted.yaml``)
  with ``lifecycle: accepted`` so it's publishable.
- Book expression exists (``book/expression/``) with manifest and accepted
  pointer, so ``auteur publish`` will find publishable content.
- Freshness tracking via content hashes.

The scene is "not yet current and publishable" meaning it has an accepted
expression but a scene revision exists that could be accepted as the new
version — simulating a revision workflow.

ExpressionStore layout (from src/auteur/expression/pilot.py)::

    chapters/<n>/scenes/<scene_id>/
        prose_v<N>.yaml   (ProseCandidate metadata)
        prose_v<N>.md     (prose content)
        accepted.yaml     (pointer to accepted candidate)

ChapterExpressionStore layout (from src/auteur/expression/composition.py)::

    chapters/<n>/
        chapter_v<N>.yaml
        chapter_v<N>.md
        accepted.yaml     (pointer to accepted expression)
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml


def _hash_text(text: str) -> str:
    """Deterministic SHA-256 hash with ``sha256:`` prefix."""
    import hashlib
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()


def build_scene_revision_publish(root: Path) -> Path:
    """Build a deterministic project with scene realizations and publication state."""
    # ------------------------------------------------------------------
    # .auteur marker
    # ------------------------------------------------------------------
    (root / ".auteur").mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # story_identity.yaml
    # ------------------------------------------------------------------
    identity = {
        "story_type": {
            "genre": "epic_fantasy",
            "mode": "epic",
            "medium": "novel",
        },
        "title": "The Revision Spark",
    }
    (root / "story_identity.yaml").write_text(yaml.safe_dump(identity))

    # ------------------------------------------------------------------
    # blueprint.yaml — complete
    # ------------------------------------------------------------------
    blueprint = {
        "identity": {
            "title": "The Revision Spark",
            "author_intent": "A heroic fantasy about power, sacrifice, and revision.",
            "genre": "epic_fantasy",
            "mode": "epic",
            "medium": "novel",
            "target_audience": "adult",
            "length_class": "short_story",
            "pov_type": "third_person_limited_single",
            "content_rating": "PG-13",
            "genre_overrides": {},
        },
        "structure": {
            "estimated_chapters": 5,
            "estimated_word_count": 12000,
            "max_pov_characters": 2,
            "act_structure": "three_act",
        },
        "contract": {
            "content_rating": "PG-13",
            "mandatory_ending_tone": "hopeful",
            "pacing_tolerances": "moderate",
            "genre_expectations": {
                "expected_tropes": ["chosen_one", "mentor", "ancient_evil"],
                "subverted_tropes": ["prophecy_is_literal"],
            },
            "medium_failure_modes": [
                "pacing_drag",
                "info_dump_worldbuilding",
            ],
        },
        "emotional_design": {
            "overall_emotional_arc": "From humble beginning through doubt to triumphant self-discovery.",
            "per_act_tones": [
                {"act_index": 1, "label": "Act One", "tone": "wonder and unease"},
                {"act_index": 2, "label": "Act Two", "tone": "despair and determination"},
                {"act_index": 3, "label": "Act Three", "tone": "hope and resolution"},
            ],
        },
        "theme": {
            "central_question": "What makes a person worthy of power?",
            "thesis": "Power is earned not through destiny but through the courage to revise one's mistakes.",
            "motifs": ["sparks", "mirrors", "ruins"],
        },
        "story_engine": {
            "main_thread": {
                "type": "main_plot",
                "want": {
                    "author_text": "Kael must master the Spark magic before the Eclipse consumes the realm.",
                    "checkable_claims": ["Kael discovers latent Spark magic", "The Eclipse approaches in 30 days"],
                },
                "resistance": {
                    "author_text": "The Shadow Court sends assassins to stop Kael before the Eclipse.",
                    "checkable_claims": ["Assassins attack the sanctuary", "Ancient wards are breached"],
                },
                "conflict": {
                    "author_text": "Kael's mentor reveals the true cost of the Spark — it drains life essence.",
                    "checkable_claims": ["Mentor dies from overuse", "Kael must choose between power and life"],
                },
                "stakes": {
                    "author_text": "If Kael fails, the Eclipse allows the Shadow Court to rule forever.",
                    "checkable_claims": ["Previous Spark bearers all died", "The realm falls into eternal night"],
                },
                "change": {
                    "author_text": "Kael learns that sacrifice is not the same as loss, and giving is the truest form of power.",
                    "checkable_claims": ["Kael shares the Spark with allies", "Kael survives the Eclipse"],
                },
                "thematic_function": "The Spark's power requires revision of self-understanding, mirroring the story's central question.",
            },
            "threads": [
                {
                    "name": "The Mentor's Secret",
                    "type": "mystery",
                    "want": {
                        "author_text": "Mentor Elara wants to protect Kael from the full truth of the Spark.",
                        "checkable_claims": ["Elara was the previous Spark bearer", "Elara hides her condition"],
                    },
                    "resistance": {
                        "author_text": "The Shadow Court captures Elara to extract the Spark's secrets.",
                        "checkable_claims": ["Elara is taken during a raid", "Torture fails to break her will"],
                    },
                    "conflict": {
                        "author_text": "Kael must decide whether to rescue Elara or prepare for the Eclipse.",
                        "checkable_claims": ["Rescue mission costs precious time", "Elara begs Kael to continue training"],
                    },
                    "stakes": {
                        "author_text": "Losing Elara means losing the only person who understands the Spark.",
                        "checkable_claims": ["Only Elara knows the final ritual", "Kael is not ready to face the Eclipse alone"],
                    },
                    "change": {
                        "author_text": "Kael learns to trust own judgment and finds a third path.",
                        "checkable_claims": ["Kael rescues Elara AND completes training", "Elara survives to see the Eclipse end"],
                    },
                    "supports_main_by": ["complicates", "pays_off"],
                    "thematic_function": "Elara's hidden past deepens the question of who deserves power.",
                },
            ],
        },
        "characters": [
            {
                "name": "Kael",
                "role": "protagonist",
                "arc_type": "growth",
                "arc_start_percentage": 0,
                "arc_end_percentage": 100,
                "current_arc_percentage": 0,
                "key_milestones": [
                    {"at_percentage": 10, "description": "Discovers Spark magic"},
                    {"at_percentage": 30, "description": "Learns the cost of the Spark"},
                    {"at_percentage": 60, "description": "Rescues Elara against the odds"},
                    {"at_percentage": 95, "description": "Shares the Spark to defeat the Eclipse"},
                ],
                "current_state": {
                    "current_goal": "Master the Spark",
                    "current_obstacle": "Mentor's hidden truth",
                    "secrets_known": [],
                },
            },
            {
                "name": "Elara",
                "role": "mentor",
                "arc_type": "disillusionment",
                "arc_start_percentage": 5,
                "arc_end_percentage": 95,
                "current_arc_percentage": 5,
                "key_milestones": [
                    {"at_percentage": 15, "description": "Begins training Kael"},
                    {"at_percentage": 35, "description": "Reveals the Spark's cost"},
                    {"at_percentage": 55, "description": "Captured by Shadow Court"},
                    {"at_percentage": 90, "description": "Released and reconciled"},
                ],
                "current_state": {
                    "current_goal": "Protect Kael",
                    "current_obstacle": "Her own failing health",
                    "secrets_known": [],
                },
            },
            {
                "name": "Vorlag",
                "role": "antagonist",
                "arc_type": "fall",
                "arc_start_percentage": 10,
                "arc_end_percentage": 100,
                "current_arc_percentage": 10,
                "key_milestones": [
                    {"at_percentage": 20, "description": "Sends assassins"},
                    {"at_percentage": 50, "description": "Commands the Eclipse ritual"},
                    {"at_percentage": 100, "description": "Consumed by the Eclipse"},
                ],
                "current_state": {
                    "current_goal": "Unleash the Eclipse",
                    "current_obstacle": "Kael's growing power",
                    "secrets_known": [],
                },
            },
        ],
        "tension_waveform": {
            "target_curve": [
                {"chapter_index": 1, "score": 3, "label": "spark_discovery"},
                {"chapter_index": 3, "score": 7, "label": "mentor_capture"},
                {"chapter_index": 5, "score": 10, "label": "eclipse_climax"},
            ],
        },
    }
    (root / "blueprint.yaml").write_text(yaml.safe_dump(blueprint))

    # ------------------------------------------------------------------
    # chapters/ch_001/outline.yaml
    # ------------------------------------------------------------------
    ch1 = root / "chapters" / "ch_001"
    ch1.mkdir(parents=True, exist_ok=True)
    ch1_outline = {
        "chapter_id": "ch_001",
        "title": "The Spark Awakens",
        "summary": "Kael discovers the Spark during a Shadow Court raid on the village.",
        "scenes": [
            {"id": "scene_01_01", "purpose": "Village raid and accidental Spark release"},
            {"id": "scene_01_02", "purpose": "Elara arrives and takes Kael to safety"},
        ],
    }
    (ch1 / "outline.yaml").write_text(yaml.safe_dump(ch1_outline))

    # ------------------------------------------------------------------
    # chapters/ch_002/outline.yaml
    # ------------------------------------------------------------------
    ch2 = root / "chapters" / "ch_002"
    ch2.mkdir(parents=True, exist_ok=True)
    (ch2 / "outline.yaml").write_text(yaml.safe_dump({
        "chapter_id": "ch_002",
        "title": "The Cost of Power",
        "summary": "Elara reveals the truth about the Spark's cost.",
        "scenes": [
            {"id": "scene_02_01", "purpose": "Training begins at the sanctuary"},
            {"id": "scene_02_02", "purpose": "Elara's confession"},
        ],
    }))

    # ------------------------------------------------------------------
    # Scene Realization  (chapters/ch_001/realization/)
    # SceneOutline YAML saved via SceneLoader convention
    # ------------------------------------------------------------------
    realization_dir = ch1 / "realization"
    realization_dir.mkdir(parents=True, exist_ok=True)
    scene_outline = {
        "id": "scene_01_01",
        "chapter_id": "ch_001",
        "status": "ready",
        "narrative_position": 1,
        "story_time": "day_1_evening",
        "pov_character_id": "Kael",
        "participants": ["Kael", "Villager_A", "Shadow_Assassin"],
        "temporal_relation": {
            "type": "starts_chapter",
            "relative_to": None,
        },
        "goal": {
            "actor_id": "Kael",
            "objective": "Protect the villagers from the Shadow Court raid",
            "rationale": "Kael has never fought before but cannot stand by",
        },
        "opposition": {
            "source": "Shadow_Assassin",
            "pressure": "Overwhelming force and dark magic",
            "rationale": "The Shadow Court seeks to eliminate anyone with Spark potential",
        },
        "turn": {
            "type": "revelation",
            "event": "Kael accidentally releases the Spark, blinding the assassin",
            "impact": "The assassin flees; Kael is shaken but alive",
        },
        "decision": {
            "actor_id": "Kael",
            "choice": "Leave the burning village with Elara",
            "rationale": "There is nothing left to protect; Elara offers answers",
        },
        "outcome": {
            "result": "partial_success",
            "knowledge": "Kael learns the Spark is real and dangerous",
            "emotions": [
                {"emotion": "fear", "intensity": 0.8, "target": "self"},
                {"emotion": "curiosity", "intensity": 0.6, "target": "Elara"},
            ],
            "consequences": ["Village is destroyed", "Kael's identity as Spark bearer is revealed"],
        },
        "entry_state": {
            "knowledge": [
                {"what": "Shadow Court has been raiding border villages", "how_known": "perceived", "degree": "certain", "source": "chapter_position"},
            ],
            "emotions": [
                {"emotion": "contentment", "intensity": 0.5, "target": "home"},
            ],
        },
        "exit_state": {
            "knowledge": [
                {"what": "Kael possesses the Spark", "how_known": "learned", "degree": "certain", "source": "character_id"},
                {"what": "The Shadow Court fears the Spark", "how_known": "inferred", "degree": "probable", "source": "inference"},
            ],
            "emotions": [
                {"emotion": "fear", "intensity": 0.9, "target": "unknown future"},
                {"emotion": "determination", "intensity": 0.4, "target": "survival"},
            ],
        },
        "realizes_arc_beats": [
            {"beat_id": "spark_discovery", "degree": "full", "evidence": "Kael manifests the Spark in crisis"},
        ],
        "setups_created": ["spark_potential", "mentor_intent"],
        "payoffs_triggered": [],
        "notes": "First scene, establishes the inciting incident.",
        "tags": ["action", "revelation", "inciting_incident"],
    }
    (realization_dir / "scene_01_01.yaml").write_text(yaml.safe_dump(scene_outline))

    # ------------------------------------------------------------------
    # Scene Expression Candidates  (chapters/ch_001/scenes/scene_01_01/)
    # ExpressionStore format: prose_v<N>.yaml + prose_v<N>.md + accepted.yaml
    # ------------------------------------------------------------------
    scene_dir = ch1 / "scenes" / "scene_01_01"
    scene_dir.mkdir(parents=True, exist_ok=True)

    # --- Candidate v1 (currently accepted, stable content) ---
    prose_v1_text = (
        "The smoke reached Kael before the screams did.\n\n"
        "He had been mending a fence at the edge of the village when the first "
        "shadow fell across the western field. Not a cloud shadow — something "
        "darker, moving against the sunset. The screams followed a heartbeat later.\n\n"
        "Kael dropped the hammer and ran.\n\n"
        "The village square was chaos. Villagers scattered as a figure in black "
        "armor stalked between the burning huts, tendrils of midnight magic "
        "twisting from its gauntlets. Kael's neighbors fell back, their pitchforks "
        "and hooves useless against the darkness.\n\n"
        "And then something inside Kael \u2014 something he had never felt before "
        "\u2014 answered the threat with fire.\n\n"
        "White-gold light erupted from his chest, a shockwave that threw the "
        "assassin against the well. The dark tendrils evaporated. For one "
        "breathless moment, Kael was the sun.\n\n"
        "Then the light faded, and Kael collapsed to his knees, gasping.\n\n"
        "When he looked up, a woman in a traveler's cloak stood before him. "
        "Her eyes held ancient recognition.\n\n"
        '"You have the Spark," she said. "Come with me if you want to live."'
    )

    prose_v1_hash = _hash_text(prose_v1_text)

    prose_v1_meta = {
        "candidate_id": "scene_01_01:prose_v001",
        "revision": 1,
        "source_scene": {
            "artifact_id": "scene_01_01",
            "revision": 1,
            "content_hash": _hash_text(yaml.safe_dump(scene_outline, sort_keys=False)),
            "path": "chapters/ch_001/realization/scene_01_01.yaml",
        },
        "executor": {
            "kind": "human-authored",
            "model": None,
            "version": 1,
            "configuration_hash": "sha256:placeholder",
        },
        "expression_constraints": {
            "max_words": 500,
            "tone": "consistent with heroic fantasy",
            "content_boundaries": [],
        },
        "content_hash": prose_v1_hash,
        "generated_at": "2026-07-24T10:00:00+00:00",
        "validation_findings": [],
    }
    (scene_dir / "prose_v001.yaml").write_text(yaml.safe_dump(prose_v1_meta))
    (scene_dir / "prose_v001.md").write_text(prose_v1_text)

    # --- Candidate v2 (new revision, newer content — the "revision") ---
    prose_v2_text = (
        "The smoke had teeth.\n\n"
        "It bit at Kael's throat as he sprinted toward the village square, each "
        "breath a shard of glass. The fence he had been mending lay abandoned, "
        "the hammer still where it had fallen. There was no time for tools.\n\n"
        "The square was a nightmare of shadow and flame. A figure in black "
        "armor moved through the chaos with terrible purpose, conjuring threads "
        "of darkness that strangled the light from every torch. The villagers "
        "fled or fell.\n\n"
        "And then the Spark answered.\n\n"
        "It came not as a choice but as a detonation. White-gold fire erupted "
        "from Kael's core, tearing through him with equal parts agony and "
        "ecstasy. The shockwave hurled the assassin into the well with a crack "
        "of stone and metal. The dark magic evaporated like morning frost.\n\n"
        'For three heartbeats, Kael hung in the air, blazing.\n\n'
        "Then gravity remembered him, and he crashed to his knees, the fire "
        "dying to embers in his chest. The world swam back into focus.\n\n"
        "A woman stood before him, her face unreadable but her eyes holding "
        "something ancient. Something that recognized what he had just become.\n\n"
        '"You have the Spark," Elara said. "And now every shadow in the realm '
        'knows it. We have to move."'
    )

    prose_v2_hash = _hash_text(prose_v2_text)

    prose_v2_meta = {
        "candidate_id": "scene_01_01:prose_v002",
        "revision": 2,
        "source_scene": {
            "artifact_id": "scene_01_01",
            "revision": 1,
            "content_hash": _hash_text(yaml.safe_dump(scene_outline, sort_keys=False)),
            "path": "chapters/ch_001/realization/scene_01_01.yaml",
        },
        "executor": {
            "kind": "human-authored",
            "model": None,
            "version": 2,
            "configuration_hash": "sha256:placeholder_v2",
        },
        "expression_constraints": {
            "max_words": 500,
            "tone": "consistent with heroic fantasy",
            "content_boundaries": [],
        },
        "content_hash": prose_v2_hash,
        "generated_at": "2026-07-25T08:00:00+00:00",
        "validation_findings": [],
    }
    (scene_dir / "prose_v002.yaml").write_text(yaml.safe_dump(prose_v2_meta))
    (scene_dir / "prose_v002.md").write_text(prose_v2_text)

    # --- accepted.yaml for scene (points to v1 — the "old" accepted revision) ---
    accepted_scene = dict(prose_v1_meta)
    accepted_scene["lifecycle"] = "accepted"
    accepted_scene["accepted_by"] = "author"
    accepted_scene["accepted_at"] = "2026-07-24T12:00:00+00:00"
    (scene_dir / "accepted.yaml").write_text(yaml.safe_dump(accepted_scene))

    # ------------------------------------------------------------------
    # Chapter Expression  (chapters/ch_001/)
    # Composed from accepted scene and saved as chapter_v<N>.yaml + .md + accepted.yaml
    # ------------------------------------------------------------------
    chapter_expression_v1 = {
        "artifact_id": "ch_001:expression_v001",
        "artifact_type": "expression_chapter",
        "revision": 1,
        "lifecycle": "accepted",
        "authority": "derived",
        "review_state": "NONE",
        "source_chapter": {
            "artifact_id": "ch_001",
            "revision": 1,
            "content_hash": _hash_text(yaml.safe_dump(ch1_outline, sort_keys=False)),
        },
        "source_scenes": [
            {
                "scene_id": "scene_01_01",
                "artifact_id": "scene_01_01:prose_v001",
                "content_hash": prose_v1_hash,
                "revision": 1,
                "label": "Village Raid",
            },
            {
                "scene_id": "scene_01_02",
                "artifact_id": "scene_01_01:prose_v001",
                "content_hash": prose_v1_hash,
                "revision": 1,
                "label": "Escape",
            },
        ],
        "transitions": [],
        "source_order": ["scene_01_01", "scene_01_02"],
        "section_map": [
            {"scene_id": "scene_01_01", "start_marker": "<!-- auteur:scene id=scene_01_01 expression_revision=1 -->", "end_marker": "<!-- auteur:end-scene id=scene_01_01 -->"},
            {"scene_id": "scene_01_02", "start_marker": "<!-- auteur:scene id=scene_01_02 expression_revision=1 -->", "end_marker": "<!-- auteur:end-scene id=scene_01_02 -->"},
        ],
        "content_hash": _hash_text(prose_v1_text),
        "transformation": {
            "id": "expression.compose_chapter",
            "version": 1,
            "executor": "deterministic",
        },
        "validation_findings": [],
        "accepted_at": "2026-07-24T14:00:00+00:00",
        "accepted_by": "author",
    }

    chapter_md_v1 = (
        "<!-- auteur:scene id=scene_01_01 expression_revision=1 -->\n"
        f"{prose_v1_text}\n"
        "<!-- auteur:end-scene id=scene_01_01 -->\n"
        "\n"
        "<!-- auteur:scene id=scene_01_02 expression_revision=1 -->\n"
        "_Elara led Kael through the forest path, the glow of the burning village "
        "fading behind them._\n"
        "\n"
        '"You saved lives tonight," she said. "But you also announced yourself '
        "to every shadow in the realm.\"\n"
        "\n"
        "Kael walked in silence, the echo of the white fire still singing in his "
        "veins.\n"
        "<!-- auteur:end-scene id=scene_01_02 -->\n"
    )

    (ch1 / "chapter_v001.yaml").write_text(yaml.safe_dump(chapter_expression_v1))
    (ch1 / "chapter_v001.md").write_text(chapter_md_v1)

    # --- accepted.yaml for chapter ---
    accepted_chapter = dict(chapter_expression_v1)
    (ch1 / "accepted.yaml").write_text(yaml.safe_dump(accepted_chapter))

    # ------------------------------------------------------------------
    # Book Expression  (book/expression/)
    # ------------------------------------------------------------------
    book_dir = root / "book" / "expression"
    book_dir.mkdir(parents=True, exist_ok=True)

    book_manifest = {
        "book_expression_id": "book_01:expression_v001",
        "revision": 1,
        "book_id": "book_01",
        "title": "The Revision Spark",
        "chapters": [
            {
                "chapter_id": "ch_001",
                "artifact_id": "ch_001:expression_v001",
                "content_hash": _hash_text(prose_v1_text),
                "accepted_at": "2026-07-24T14:00:00+00:00",
            },
            {
                "chapter_id": "ch_002",
                "artifact_id": "ch_002:expression_v001",
                "content_hash": "sha256:0000000000000000000000000000000000000000000000000000000000000000",
                "accepted_at": None,
            },
        ],
        "freshness": "stale",
        "book_owned_content": "",
        "accepted_by": "author",
        "accepted_at": "2026-07-24T16:00:00+00:00",
        "lifecycle": "accepted",
    }
    (book_dir / "book_v001.yaml").write_text(yaml.safe_dump(book_manifest))

    book_md = (
        "# The Revision Spark\n\n"
        "<!-- auteur:chapter id=ch_001 -->\n"
        f"{prose_v1_text}\n"
        "<!-- auteur:end-chapter id=ch_001 -->\n"
        "\n"
        "<!-- auteur:book-separator -->\n"
        "---\n"
        "<!-- auteur:end-book-separator -->\n"
        "\n"
        "<!-- auteur:chapter id=ch_002 -->\n"
        "_Chapter Two is being composed._\n"
        "<!-- auteur:end-chapter id=ch_002 -->\n"
    )
    (book_dir / "book_v001.md").write_text(book_md)

    # --- accepted.yaml for book ---
    (book_dir / "accepted.yaml").write_text(yaml.safe_dump(book_manifest))

    return root


@pytest.fixture
def scene_revision_publish(tmp_path: Path) -> Path:
    """Build a deterministic project with scene realizations and publication state."""
    return build_scene_revision_publish(tmp_path)
