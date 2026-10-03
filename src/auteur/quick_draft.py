"""Experimental two-input Quick Draft facade.

This spike gives a writer prose before requiring Story Identity / Structure
acceptance. All inferred scaffolding remains isolated and explicitly provisional
under .auteur/quick_draft/. It never writes accepted story files.
"""

from __future__ import annotations

import argparse
import hashlib
import os
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from auteur.bard import postprocess_draft, render_bard_prompt
from auteur.bible import StoryBible
from auteur.blueprint import (
    Genre,
    LengthClass,
    StoryMedium,
    StoryMode,
    TargetAudience,
    TargetExperience,
)
from auteur.identity import HighLevelCentralEngine, StoryIdentity, StoryType, compile_to_blueprint
from auteur.llm import LLMClient, LLMRequest
from auteur.llm.factory import build_client


STATUS = "inferred_provisional"
DEFAULT_LENSES = (
    "Main Story Engine",
    "Emotional & Aesthetic Framing",
    "Common Tropes",
    "Structural Shape",
    "Reader Experience",
)


@dataclass(frozen=True)
class QuickDraftResult:
    session_id: str
    session_dir: Path
    scaffold_path: Path
    draft_path: Path
    elapsed_seconds: float
    provider: str


def parse_quick_draft_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="auteur quick-draft",
        description=(
            "Experimental low-friction path: give Auteur a premise and what should "
            "happen in the first scene; get a working scene draft before accepting "
            "story setup or structure."
        ),
    )
    parser.add_argument("premise", help="A 1-2 sentence story premise or prompt.")
    parser.add_argument(
        "first_scene",
        help="What you want to happen in the very first scene.",
    )
    return parser.parse_args(argv)


def _provider_from_environment() -> tuple[str, str | None]:
    requested = os.environ.get("AUTEUR_QUICK_DRAFT_PROVIDER", "").strip().lower()
    model = os.environ.get("AUTEUR_QUICK_DRAFT_MODEL") or None
    if requested:
        if requested not in {"openai", "anthropic"}:
            raise ValueError(
                "AUTEUR_QUICK_DRAFT_PROVIDER must be 'openai' or 'anthropic'."
            )
        return requested, model
    if os.environ.get("OPENAI_API_KEY"):
        return "openai", model
    if os.environ.get("ANTHROPIC_API_KEY"):
        return "anthropic", model
    raise RuntimeError(
        "Quick Draft needs an existing OPENAI_API_KEY or ANTHROPIC_API_KEY. "
        "No additional story decisions are required."
    )


def _build_quick_draft_client() -> tuple[LLMClient, str]:
    provider, model = _provider_from_environment()
    return build_client(provider, model, agent_type="bard"), provider


def _session_id(premise: str, first_scene: str) -> str:
    digest = hashlib.sha256(
        (premise.strip() + "\n" + first_scene.strip()).encode("utf-8")
    ).hexdigest()[:8]
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return f"quick-{stamp}-{digest}"


def _provisional_identity(premise: str, first_scene: str) -> StoryIdentity:
    short_title = " ".join(premise.strip().split())[:72].rstrip(" .,:;-")
    return StoryIdentity(
        title=short_title or "Quick Draft",
        core_answer=premise.strip(),
        target_experience=TargetExperience(
            primary="curiosity and forward momentum",
            progression="curiosity -> tension -> change",
            avoid=[],
        ),
        story_type=StoryType(
            medium=StoryMedium.SHORT_STORY,
            mode=StoryMode.OTHER,
            genre=Genre.OTHER,
            target_audience=TargetAudience.ADULT,
            length_class=LengthClass.SHORT_STORY,
        ),
        central_engine=HighLevelCentralEngine(
            want=first_scene.strip(),
            resistance=(
                "An immediate obstacle, uncertainty, or opposing desire prevents "
                "the opening intention from resolving cleanly."
            ),
            conflict=(
                "The first-scene intention meets resistance and forces a concrete "
                "choice or discovery."
            ),
            stakes=(
                "The opening must create a meaningful reason for the reader and "
                "the viewpoint character to continue."
            ),
            change=(
                "By the end of the first scene, the situation is meaningfully "
                "different from how it began."
            ),
        ),
        open_questions=[
            "What larger story does this first scene imply?",
            "Which provisional details should the author keep after seeing the draft?",
        ],
        confidence=0.25,
        why_this_is_best=(
            "Quick Draft uses intentionally generic defaults so prose can provide "
            "evidence before the author is asked to commit to story architecture."
        ),
    )


def _scene_outline(premise: str, first_scene: str) -> dict[str, Any]:
    return {
        "scope": "chapter",
        "chapter_index": 1,
        "chapter_summary": first_scene.strip(),
        "scenes": [
            {
                "scene_id": "quick_scene_01",
                "pov_character": "Protagonist",
                "location": "Infer naturally from the premise and first-scene intent.",
                "summary": first_scene.strip(),
                "key_events": [first_scene.strip()],
                "character_state_changes": [],
                "arc_advancements": [],
                "estimated_tension": 5,
                "emotional_tone": "immediate, concrete, forward-moving",
                "entry_state": premise.strip(),
                "immediate_goal": first_scene.strip(),
                "conflict": (
                    "Introduce a plausible immediate obstacle or uncertainty that "
                    "arises naturally from the premise."
                ),
                "continuity_constraints": [
                    f"Premise: {premise.strip()}",
                    "Do not invent a whole-story ending or lock future structure.",
                ],
            }
        ],
        "arc_pushes": [],
        "contract_compliance": [],
        "expected_elements_touched": [],
        "forbidden_tropes_avoided": [],
        "estimated_chapter_tension": 5,
        "thematic_reinforcement": "Discover what the story wants to become through scene work.",
        "conflict_report": None,
    }


def _scaffold_payload(
    *,
    session_id: str,
    premise: str,
    first_scene: str,
    identity: StoryIdentity,
    outline: dict[str, Any],
    provider: str,
    draft_status: str,
    elapsed_seconds: float | None = None,
    error: str | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "schema": "quick_draft_spike_v1",
        "session_id": session_id,
        "status": STATUS,
        "authority": {
            "story_setup": "not_accepted",
            "structure": "not_accepted",
            "scene_draft": "working_only",
            "canon_acceptance": "deferred_until_after_draft",
            "structural_reconciliation": "deferred_until_after_draft",
        },
        "inputs": {
            "premise": premise.strip(),
            "first_scene_intent": first_scene.strip(),
        },
        "inferred_scaffolding": {
            "status": STATUS,
            "lenses": [
                {"name": lens, "status": STATUS}
                for lens in DEFAULT_LENSES
            ],
            "identity_container": {
                "status": STATUS,
                "title": identity.title,
                "core_answer": identity.core_answer,
                "target_experience": identity.target_experience.model_dump(mode="json"),
                "story_type": identity.story_type.model_dump(mode="json"),
                "central_engine": identity.central_engine.model_dump(mode="json"),
                "confidence": identity.confidence,
            },
            "scene_plan": {
                "status": STATUS,
                **outline["scenes"][0],
            },
        },
        "draft": {
            "status": draft_status,
            "review_status": "not_reviewed",
            "accepted": False,
            "provider": provider,
        },
        "next_author_decision": (
            "Read or edit the draft first. Story setup acceptance and reconciliation "
            "remain intentionally deferred."
        ),
    }
    if elapsed_seconds is not None:
        payload["draft"]["elapsed_seconds"] = round(elapsed_seconds, 3)
        payload["draft"]["thirty_second_target_met"] = elapsed_seconds <= 30.0
    if error:
        payload["draft"]["error"] = error
    return payload


def run_quick_draft(
    premise: str,
    first_scene: str,
    *,
    project_root: Path = Path("."),
    llm: LLMClient | None = None,
    provider_label: str | None = None,
) -> QuickDraftResult:
    premise = " ".join(premise.split()).strip()
    first_scene = " ".join(first_scene.split()).strip()
    if not premise:
        raise ValueError("premise must not be empty")
    if not first_scene:
        raise ValueError("first-scene intent must not be empty")

    if llm is None:
        llm, provider = _build_quick_draft_client()
    else:
        provider = provider_label or "test/facade"

    started = time.monotonic()
    session_id = _session_id(premise, first_scene)
    root = Path(project_root).resolve()
    session_dir = root / ".auteur" / "quick_draft" / session_id
    session_dir.mkdir(parents=True, exist_ok=False)

    identity = _provisional_identity(premise, first_scene)
    blueprint = compile_to_blueprint(identity)
    # Keep the prose call scene-sized rather than chapter-sized.
    blueprint.structure.estimated_chapters = 1
    blueprint.structure.estimated_word_count = 1400

    outline = _scene_outline(premise, first_scene)
    bible = StoryBible(session_dir / "provisional_bible.json")
    scaffold_path = session_dir / "scaffold.yaml"
    draft_path = session_dir / "scene_draft.md"

    scaffold_path.write_text(
        yaml.safe_dump(
            _scaffold_payload(
                session_id=session_id,
                premise=premise,
                first_scene=first_scene,
                identity=identity,
                outline=outline,
                provider=provider,
                draft_status="generating",
            ),
            sort_keys=False,
            allow_unicode=True,
        ),
        encoding="utf-8",
    )

    try:
        system, user = render_bard_prompt(
            outline=outline,
            bible=bible,
            blueprint=blueprint,
            chapter_index=1,
            prior_draft=None,
            findings=None,
        )
        response = llm.complete(
            LLMRequest(
                system=system,
                user=user,
                temperature=0.85,
                max_tokens=1800,
            )
        )
        prose = postprocess_draft(response.text)
        if not prose:
            raise RuntimeError("the drafting model returned an empty scene")
        draft_path.write_text(prose.rstrip() + "\n", encoding="utf-8")
    except Exception as exc:
        elapsed = time.monotonic() - started
        scaffold_path.write_text(
            yaml.safe_dump(
                _scaffold_payload(
                    session_id=session_id,
                    premise=premise,
                    first_scene=first_scene,
                    identity=identity,
                    outline=outline,
                    provider=provider,
                    draft_status="generation_failed",
                    elapsed_seconds=elapsed,
                    error=str(exc),
                ),
                sort_keys=False,
                allow_unicode=True,
            ),
            encoding="utf-8",
        )
        raise

    elapsed = time.monotonic() - started
    scaffold_path.write_text(
        yaml.safe_dump(
            _scaffold_payload(
                session_id=session_id,
                premise=premise,
                first_scene=first_scene,
                identity=identity,
                outline=outline,
                provider=provider,
                draft_status="draft_ready",
                elapsed_seconds=elapsed,
            ),
            sort_keys=False,
            allow_unicode=True,
        ),
        encoding="utf-8",
    )
    return QuickDraftResult(
        session_id=session_id,
        session_dir=session_dir,
        scaffold_path=scaffold_path,
        draft_path=draft_path,
        elapsed_seconds=elapsed,
        provider=provider,
    )


def dispatch_quick_draft_argv(argv: list[str]) -> int:
    args = parse_quick_draft_args(argv)
    try:
        result = run_quick_draft(args.premise, args.first_scene)
    except (RuntimeError, ValueError, ImportError) as exc:
        print(f"Quick Draft could not start: {exc}")
        return 1

    prose = result.draft_path.read_text(encoding="utf-8").rstrip()
    print("Quick Draft — working scene")
    print("Nothing below is accepted story material yet.\n")
    print(prose)
    print("\n---")
    print(f"Draft: {result.draft_path}")
    print(f"Provisional setup: {result.scaffold_path}")
    print(f"Time to draft: {result.elapsed_seconds:.1f}s")
    print(
        "Next: edit or react to the scene first. Story setup acceptance and "
        "structural reconciliation are deferred until after the draft."
    )
    return 0
