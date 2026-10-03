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
from auteur.beginner.creative_divergence import infer_creative_discoveries


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
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
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
                "pov_character": "",
                "location": "",
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
                    "If viewpoint or location is ambiguous, keep it flexible rather than treating an inference as established fact.",
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
                "target_experience": {
                    "status": STATUS,
                    "value": identity.target_experience.model_dump(mode="json"),
                },
                "story_type": {
                    "status": STATUS,
                    "value": identity.story_type.model_dump(mode="json"),
                },
                "central_engine": {
                    "status": STATUS,
                    "value": identity.central_engine.model_dump(mode="json"),
                },
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
            "current_file": "scene_draft.md",
            "edit_count": 0,
        },
        "next_author_decision": (
            "Read or edit the draft first. Story setup decisions and story updates "
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

    started = time.monotonic()
    if llm is None:
        llm, provider = _build_quick_draft_client()
    else:
        provider = provider_label or "test/facade"

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


def _quick_draft_session_dir(project_root: Path, session_id: str) -> Path:
    if not session_id or any(char in session_id for char in "/\\") or not session_id.startswith("quick-"):
        raise ValueError("invalid Quick Draft session ID")
    path = Path(project_root).resolve() / ".auteur" / "quick_draft" / session_id
    if not path.is_dir():
        raise FileNotFoundError(f"Quick Draft session not found: {session_id}")
    return path


def project_quick_draft_session(project_root: Path, session_id: str) -> dict[str, Any]:
    session_dir = _quick_draft_session_dir(project_root, session_id)
    scaffold_path = session_dir / "scaffold.yaml"
    if not scaffold_path.is_file():
        raise FileNotFoundError("Quick Draft scaffold is missing")
    scaffold = yaml.safe_load(scaffold_path.read_text(encoding="utf-8")) or {}
    draft_info = scaffold.get("draft") if isinstance(scaffold, dict) else {}
    current_file = (
        draft_info.get("current_file", "scene_draft.md")
        if isinstance(draft_info, dict)
        else "scene_draft.md"
    )
    draft_path = session_dir / str(current_file)
    if not draft_path.is_file():
        raise FileNotFoundError("Quick Draft scene is missing")
    draft_text = draft_path.read_text(encoding="utf-8")
    inputs = scaffold.get("inputs", {}) if isinstance(scaffold, dict) else {}
    baseline = " ".join(
        str(inputs.get(key, "")) for key in ("premise", "first_scene_intent")
    )
    discoveries = infer_creative_discoveries(draft_text, baseline_text=baseline)
    return {
        "session_id": session_id,
        "status": scaffold.get("status", STATUS),
        "draft_text": draft_text,
        "draft": draft_info,
        "discoveries": discoveries,
        "scaffold": scaffold,
    }


def save_quick_draft_revision(
    project_root: Path,
    session_id: str,
    prose: str,
) -> dict[str, Any]:
    if not isinstance(prose, str) or not prose.strip():
        raise ValueError("scene draft must not be empty")
    session_dir = _quick_draft_session_dir(project_root, session_id)
    scaffold_path = session_dir / "scaffold.yaml"
    scaffold = yaml.safe_load(scaffold_path.read_text(encoding="utf-8")) or {}
    draft_info = scaffold.setdefault("draft", {})
    current_file = str(draft_info.get("current_file", "scene_draft.md"))
    draft_path = session_dir / current_file
    revisions_dir = session_dir / "revisions"
    revisions_dir.mkdir(parents=True, exist_ok=True)
    revision_number = len(list(revisions_dir.glob("scene_draft_v*.md"))) + 1
    if draft_path.is_file():
        history_path = revisions_dir / f"scene_draft_v{revision_number:03d}.md"
        history_path.write_text(draft_path.read_text(encoding="utf-8"), encoding="utf-8")
    draft_path.write_text(prose.rstrip() + "\n", encoding="utf-8")
    draft_info["status"] = "draft_ready"
    draft_info["review_status"] = "not_reviewed"
    draft_info["accepted"] = False
    draft_info["edit_count"] = int(draft_info.get("edit_count", 0)) + 1
    draft_info["candidate_sha256"] = hashlib.sha256(draft_path.read_bytes()).hexdigest()
    scaffold_path.write_text(
        yaml.safe_dump(scaffold, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )
    return project_quick_draft_session(project_root, session_id)


def project_quick_draft_discoveries(project_root: Path, session_id: str) -> dict[str, Any]:
    projection = project_quick_draft_session(project_root, session_id)
    return {
        "session_id": session_id,
        "status": STATUS,
        "discoveries": projection["discoveries"],
        "message": (
            "These are working observations from the draft, not accepted story facts."
        ),
    }


def prepare_quick_draft_shape_handoff(
    project_root: Path,
    session_id: str,
    workspace_id: str,
    selected_discoveries: list[dict[str, str]] | None = None,
) -> Path:
    """Link a provisional Quick Draft to a workspace without promoting its content."""
    if not workspace_id or any(char in workspace_id for char in "/\\"):
        raise ValueError("invalid workspace ID")
    projection = project_quick_draft_session(project_root, session_id)
    available = {
        (str(item.get("kind", "")), str(item.get("value", ""))): item
        for item in projection["discoveries"]
    }
    selected: list[dict[str, str]] = []
    for requested in selected_discoveries or []:
        if not isinstance(requested, dict):
            raise ValueError("selected Quick Draft discoveries must be objects")
        key = (str(requested.get("kind", "")), str(requested.get("value", "")))
        if key not in available:
            raise ValueError("selected Quick Draft discovery is not current")
        selected.append(available[key])

    session_dir = _quick_draft_session_dir(project_root, session_id)
    draft_path = session_dir / str((projection.get("draft") or {}).get("current_file", "scene_draft.md"))
    scaffold = projection["scaffold"]
    inputs = scaffold.get("inputs", {}) if isinstance(scaffold, dict) else {}
    payload = {
        "canonical": False,
        "status": "working_context",
        "quick_draft_session_id": session_id,
        "workspace_id": workspace_id,
        "source_draft": draft_path.name,
        "source_draft_sha256": hashlib.sha256(draft_path.read_bytes()).hexdigest(),
        "premise": str(inputs.get("premise", "")),
        "first_scene_intent": str(inputs.get("first_scene_intent", "")),
        "selected_discoveries": selected,
        "note": (
            "This handoff preserves author-selected Quick Draft context. "
            "It does not accept Story setup, Story shape, or discovered facts."
        ),
    }
    handoff_path = (
        Path(project_root).resolve()
        / ".auteur"
        / "beginner"
        / "quick_draft_handoffs"
        / f"{workspace_id}.yaml"
    )
    handoff_path.parent.mkdir(parents=True, exist_ok=True)
    handoff_path.write_text(
        yaml.safe_dump(payload, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )
    (session_dir / "shape_handoff.yaml").write_text(
        yaml.safe_dump(payload, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )
    return handoff_path


def dispatch_quick_draft_argv(argv: list[str]) -> int:
    args = parse_quick_draft_args(argv)
    try:
        result = run_quick_draft(args.premise, args.first_scene)
    except Exception as exc:
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
        "Next: edit or react to the scene first. Story setup decisions and "
        "story updates are deferred until after the draft."
    )
    return 0
