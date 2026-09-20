"""Thin local JSON API over BeginnerWorkspaceApplication (Task 6).

Routes (all JSON):
- POST /api/beginner/workspaces -> create workspace; 201 + full projection.
- GET /api/beginner/workspaces/<workspace_id> -> full projection read.
- POST /api/beginner/workspaces/<workspace_id>/commands/<command> -> journey
  command with a full MutationCommand envelope; 200 + full projection.

The handler holds no narrative rules: the sealed fixture premise enters only
via workspace creation passthrough and every mutation delegates to
BeginnerWorkspaceApplication. Error mapping: 400 malformed envelope, 409
concurrency/idempotency conflicts, 422 domain/readiness rejection.
"""

from __future__ import annotations

import argparse
import json
import logging
import mimetypes
import secrets
import threading
from dataclasses import asdict, dataclass, is_dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Callable
from urllib.parse import urlparse

from pydantic import ValidationError

from auteur.llm.factory import build_client

from .application import BeginnerWorkspaceApplication, BeginnerWorkspaceError
from .architecture_analysis import (
    ArchitectureAnalyzer,
    DeterministicArchitectureAnalyzer,
    ProviderArchitectureAnalyzer,
    ResilientArchitectureAnalyzer,
)
from .architecture_models import ArchitectureFacet, ArchitectureRole
from .discovery import (
    DiscoveryRecommender,
    StoryDiscoveryRecommender,
    UnavailableDiscoveryRecommender,
)
from .contracts import MutationCommand
from .persistence import BeginnerConcurrencyError, BeginnerPersistenceError
from .projections import WorkspaceProjection
from .continuation import build_contextual_chapter_plan, build_contextual_scene_plans
from .book_progress import project_book_progress
from .post_draft import (
    accept_latest_chapter,
    prepare_revision_handoff,
    project_chapter_outcome,
    project_draft_review,
    project_next_chapter_context,
)

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class BeginnerRuntimeDependencies:
    architecture_analyzer: ArchitectureAnalyzer
    discovery_recommender: DiscoveryRecommender


def default_runtime_dependencies() -> BeginnerRuntimeDependencies:
    return BeginnerRuntimeDependencies(
        architecture_analyzer=DeterministicArchitectureAnalyzer(),
        discovery_recommender=UnavailableDiscoveryRecommender(),
    )


class BeginnerRequestError(ValueError):
    def __init__(self, status: int, message: str):
        super().__init__(message)
        self.status = status
        self.message = message


def _enum_value(value: Any) -> Any:
    return value.value if hasattr(value, "value") else value


def _json_value(value: Any) -> Any:
    if is_dataclass(value):
        return _json_value(asdict(value))
    if hasattr(value, "model_dump"):
        return _json_value(value.model_dump(mode="json"))
    if isinstance(value, dict):
        return {str(key): _json_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_value(item) for item in value]
    if isinstance(value, Path):
        return str(value)
    if hasattr(value, "value"):
        return value.value
    return value


def projection_to_dict(projection: WorkspaceProjection, *, workspace_id: str) -> dict[str, Any]:
    card = projection.decision_card
    decision_workspace = projection.decision_workspace
    guidance_inspector = projection.guidance_inspector
    return {
        "workspace": {
            "workspace_id": workspace_id,
            "session_version": projection.session_version,
        },
        "session_version": projection.session_version,
        "navigator": [
            {
                "stage": _enum_value(entry.stage),
                "lifecycle": _enum_value(entry.lifecycle),
                "availability": _enum_value(entry.availability),
                "total_cards": entry.total_cards,
                "answered_cards": entry.answered_cards,
                "current_card_id": entry.current_card_id,
                "review_available": entry.review_available,
                "ready_to_accept": entry.ready_to_accept,
                "at_risk_if_accepted": entry.at_risk_if_accepted,
                "stale": entry.stale,
                "canonical_ref": entry.canonical_ref,
            }
            for entry in projection.navigator
        ],
        "decision_card": (
            None
            if card is None
            else {
                "card_id": card.card_id,
                "stage": _enum_value(card.stage),
                "question": card.question,
                "options": list(card.options),
                "selected_option": card.selected_option,
                "recommendation": card.recommendation,
                "why_this_matters": card.why_this_matters,
                "narrative_principle": card.narrative_principle,
                "warnings_or_tensions": list(card.warnings_or_tensions),
                "downstream_consequences": list(card.downstream_consequences),
                "evidence": list(card.evidence),
                "option_impacts": {
                    option: impact.model_dump(mode="json") if hasattr(impact, "model_dump") else impact
                    for option, impact in card.option_impacts.items()
                },
                "is_exploratory": card.is_exploratory,
            }
        ),
        "decision_workspace": (
            None
            if decision_workspace is None
            else {
                "current_focus": {
                    "stage": _enum_value(decision_workspace.current_focus.stage),
                    "position": decision_workspace.current_focus.position,
                    "question": decision_workspace.current_focus.question,
                    "why_this_matters_now": decision_workspace.current_focus.why_this_matters_now,
                },
                "options": [
                    {
                        "label": option.label,
                        "selected": option.selected,
                        "recommended": option.recommended,
                    }
                    for option in decision_workspace.options
                ],
                "immediate_consequence": decision_workspace.immediate_consequence,
                "working_state": decision_workspace.working_state,
                "active_issue_summary": decision_workspace.active_issue_summary,
                "next_action": decision_workspace.next_action,
                "authority_status": decision_workspace.authority_status,
            }
        ),
        "guidance_inspector": (
            None
            if guidance_inspector is None
            else {
                "recommendation": guidance_inspector.recommendation,
                "recommendation_rationale": guidance_inspector.recommendation_rationale,
                "selected_choice_relationship": guidance_inspector.selected_choice_relationship,
                "context_guidance": {
                    "reader_experience": guidance_inspector.context_guidance.reader_experience,
                    "emotional_promise": guidance_inspector.context_guidance.emotional_promise,
                    "narrative_promise": guidance_inspector.context_guidance.narrative_promise,
                    "genre_conventions": list(guidance_inspector.context_guidance.genre_conventions),
                    "patterns": list(guidance_inspector.context_guidance.patterns),
                    "craft_principle": guidance_inspector.context_guidance.craft_principle,
                    "common_failure_mode": guidance_inspector.context_guidance.common_failure_mode,
                },
                "narrative_consequences": [
                    {
                        "semantic_area": _enum_value(consequence.semantic_area),
                        "summary": consequence.summary,
                        "implications": list(consequence.implications),
                        "what_becomes_easier": list(consequence.what_becomes_easier),
                        "what_becomes_harder": list(consequence.what_becomes_harder),
                        "risks": list(consequence.risks),
                        "compensating_requirements": list(consequence.compensating_requirements),
                    }
                    for consequence in guidance_inspector.narrative_consequences
                ],
                "option_comparisons": [
                    {
                        "label": comparison.label,
                        "reader_experience": comparison.reader_experience,
                        "narrative_promise": comparison.narrative_promise,
                        "genre_conventions": list(comparison.genre_conventions),
                        "tradeoffs": list(comparison.tradeoffs),
                    }
                    for comparison in guidance_inspector.option_comparisons
                ],
                "alternatives": list(guidance_inspector.alternatives),
                "tradeoffs": list(guidance_inspector.tradeoffs),
                "craft_principles": list(guidance_inspector.craft_principles),
                "evidence": list(guidance_inspector.evidence),
                "freshness": guidance_inspector.freshness,
                "authority_status": guidance_inspector.authority_status,
            }
        ),
        "stage_status": {
            _enum_value(stage): {
                "stage": _enum_value(status.stage),
                "lifecycle": _enum_value(status.lifecycle),
                "availability": _enum_value(status.availability),
            }
            for stage, status in projection.stage_status.items()
        },
        "warnings": list(projection.warnings),
        "tensions": [
            {
                "tension_id": tension.tension_id,
                "card_id": tension.card_id,
                "detail": tension.detail,
                "blocking": tension.blocking,
                "acknowledged": tension.acknowledged,
            }
            for tension in projection.tensions
        ],
        "reviews": {
            _enum_value(stage): {
                "stage": _enum_value(review.stage),
                "opened": review.opened,
                "review_available": review.review_available,
                "ready_to_accept": review.ready_to_accept,
                "blockers": list(review.blockers),
                "synthesis": review.synthesis,
                "card_summaries": [
                    {
                        "card_id": summary.card_id,
                        "label": summary.label,
                        "question": summary.question,
                        "selected_option": summary.selected_option,
                        "recommendation": summary.recommendation,
                        "guidance_alignment": summary.guidance_alignment,
                        "evidence": list(summary.evidence),
                    }
                    for summary in review.card_summaries
                ],
            }
            for stage, review in projection.reviews.items()
        },
        "canonical_refs": [ref.model_dump(mode="json") for ref in projection.canonical_refs],
        "revision": {
            "active_revision_id": projection.revision.active_revision_id,
            "is_exploration": projection.revision.is_exploration,
            "at_risk_stages": [_enum_value(stage) for stage in projection.revision.at_risk_stages],
            "base_session_version": projection.revision.base_session_version,
            "target_stage": _enum_value(projection.revision.target_stage),
        },
        "available_actions": list(projection.available_actions),
        "working_composition": (
            None
            if projection.working_composition is None
            else projection.working_composition.model_dump(mode="json")
        ),
        "mapping_preview": (
            None
            if projection.mapping_preview is None
            else projection.mapping_preview.model_dump(mode="json")
            if hasattr(projection.mapping_preview, "model_dump")
            else projection.mapping_preview
        ),
        "story_orientation": (
            None
            if projection.story_orientation is None
            else projection.story_orientation.model_dump(mode="json")
        ),
        "primary_surface": projection.primary_surface,
        "discovery": (
            None if projection.discovery is None else projection.discovery.model_dump(mode="json")
        ),
        "identity_candidate": (
            None
            if projection.identity_candidate is None
            else projection.identity_candidate.model_dump(mode="json")
        ),
        "continuation": (
            None
            if projection.continuation is None
            else projection.continuation.model_dump(mode="json")
        ),
    }


_COMMAND_HANDLERS: dict[str, str] = {
    "select": "select_working_option",
    "continue": "continue_decision",
    "open-review": "open_milestone_review",
    "reassess": "reassess_guidance",
    "acknowledge": "acknowledge_tension",
    "acknowledge-remainder": "acknowledge_unmapped_remainder",
    "confirm-dimension": "confirm_dimension",
    "reject-dimension": "reject_dimension",
    "add-dimension": "add_author_dimension",
    "override-mapping": "override_mapping",
    "open-revision": "open_revision",
    "cancel-revision": "cancel_revision",
    "request-acceptance": "request_acceptance",
    "accept-direction": "accept_story_direction",
    "accept-identity": "accept_story_identity",
    "accept-structure": "accept_whole_story_structure",
    "accept-revised-direction": "accept_revised_story_direction",
    "accept-revised-identity": "accept_revised_story_identity",
    "accept-revised-structure": "accept_revised_whole_story_structure",
    "continue-architecture": "continue_from_architecture",
    "select-direction": "select_story_direction",
    "confirm-architecture-component": "confirm_architecture_component",
    "suppress-architecture-component": "suppress_architecture_component",
    "restore-architecture-component": "restore_architecture_component",
    "rename-architecture-component": "rename_architecture_component",
    "choose-architecture-alternative": "choose_architecture_alternative",
    "set-architecture-component-role": "set_architecture_component_role",
    "add-architecture-component": "add_architecture_component",
    "reanalyze-premise": "reanalyze_premise",
    "propose-outline": "propose_outline",
    "accept-outline": "accept_outline",
    "propose-chapter-plan": "propose_chapter_plan",
    "accept-chapter-plan": "accept_chapter_plan",
    "propose-scene-plans": "propose_scene_plans",
    "accept-scene-plans": "accept_scene_plans",
    "prepare-draft-handoff": "prepare_draft_handoff",
}

_IDEMPOTENCY_MARKERS = ("already in progress", "receipt mismatch", "intent conflict", "already exists")


def _is_idempotency_conflict(message: str) -> bool:
    lowered = message.lower()
    return any(marker in lowered for marker in _IDEMPOTENCY_MARKERS)


class _RequestHandler(BaseHTTPRequestHandler):
    project_root: Path
    dependencies: BeginnerRuntimeDependencies

    _BROWSER_ASSETS = {
        "/": "index.html",
        "/index.html": "index.html",
        "/app.js": "app.js",
        "/styles.css": "styles.css",
    }

    def log_message(self, format: str, *args: Any) -> None:
        logger.info(format, *args)

    def _send_json(self, status: int, payload: Any) -> None:
        body = json.dumps(_json_value(payload), ensure_ascii=True).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_json(self) -> dict[str, Any]:
        try:
            length = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(length).decode("utf-8") or "{}")
        except (ValueError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise BeginnerRequestError(400, "Request body must be valid JSON") from exc
        if not isinstance(payload, dict):
            raise BeginnerRequestError(400, "Request body must be a JSON object")
        return payload

    def _handle_error(self, error: Exception) -> None:
        if isinstance(error, BeginnerRequestError):
            self._send_json(error.status, {"error": error.message})
        elif isinstance(error, ValidationError):
            self._send_json(400, {"error": f"malformed command envelope: {error}"})
        elif isinstance(error, BeginnerConcurrencyError):
            self._send_json(409, {"error": str(error)})
        elif isinstance(error, BeginnerWorkspaceError):
            if _is_idempotency_conflict(str(error)):
                self._send_json(409, {"error": str(error)})
            else:
                self._send_json(422, {"error": str(error)})
        elif isinstance(error, BeginnerPersistenceError):
            self._send_json(409, {"error": str(error)})
        elif isinstance(error, ValueError):
            self._send_json(400, {"error": str(error)})
        else:
            logger.exception("Unhandled beginner workspace request error")
            self._send_json(500, {"error": "Internal server error"})

    def _app_for(self, workspace_id: str) -> BeginnerWorkspaceApplication:
        return BeginnerWorkspaceApplication(
            self.project_root,
            workspace_id,
            architecture_analyzer=self.dependencies.architecture_analyzer,
            discovery_recommender=self.dependencies.discovery_recommender,
        )

    def _serve_browser_asset(self, path: str) -> bool:
        filename = self._BROWSER_ASSETS.get(path)
        if filename is None:
            return False
        asset = Path(__file__).parent / "browser" / filename
        if not asset.is_file():
            self._send_json(404, {"error": "Browser asset not found"})
            return True
        body = asset.read_bytes()
        content_type = mimetypes.guess_type(filename)[0] or "application/octet-stream"
        self.send_response(200)
        self.send_header("Content-Type", f"{content_type}; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)
        return True

    def do_GET(self) -> None:
        path = urlparse(self.path).path.rstrip("/") or "/"
        try:
            if self._serve_browser_asset(path):
                return
            parts = [part for part in path.split("/") if part]
            if parts == ["api", "beginner", "book", "progress"]:
                self._send_json(200, project_book_progress(self.project_root))
                return
            if len(parts) == 5 and parts[:3] == ["api", "beginner", "chapters"]:
                try:
                    chapter_index = int(parts[3])
                except ValueError as exc:
                    raise BeginnerRequestError(400, "chapter index must be an integer") from exc
                action = parts[4]
                try:
                    if action == "review":
                        self._send_json(200, project_draft_review(self.project_root, chapter_index))
                        return
                    if action == "outcome":
                        self._send_json(200, project_chapter_outcome(self.project_root, chapter_index))
                        return
                    if action == "next":
                        self._send_json(200, project_next_chapter_context(self.project_root, chapter_index))
                        return
                    if action == "plan":
                        self._send_json(
                            200,
                            {
                                "plan": build_contextual_chapter_plan(self.project_root, chapter_index),
                                "scenes": build_contextual_scene_plans(self.project_root, chapter_index),
                            },
                        )
                        return
                except (FileNotFoundError, OSError, RuntimeError) as exc:
                    raise BeginnerRequestError(422, str(exc)) from exc
            # GET /api/beginner/workspaces/<workspace_id>
            if len(parts) == 3 and parts[:2] == ["api", "beginner"] and parts[2] == "workspaces":
                raise BeginnerRequestError(400, "workspace_id is required")
            if len(parts) == 4 and parts[:3] == ["api", "beginner", "workspaces"]:
                workspace_id = parts[3]
                try:
                    projection = self._app_for(workspace_id).projection()
                except BeginnerPersistenceError as exc:
                    raise BeginnerRequestError(404, str(exc)) from exc
                self._send_json(200, projection_to_dict(projection, workspace_id=workspace_id))
                return
            self._send_json(404, {"error": "Not found"})
        except Exception as exc:
            self._handle_error(exc)

    def do_POST(self) -> None:
        path = urlparse(self.path).path.rstrip("/") or "/"
        try:
            parts = [part for part in path.split("/") if part]
            if len(parts) == 5 and parts[:3] == ["api", "beginner", "chapters"]:
                try:
                    chapter_index = int(parts[3])
                except ValueError as exc:
                    raise BeginnerRequestError(400, "chapter index must be an integer") from exc
                action = parts[4]
                payload = self._read_json()
                try:
                    if action == "accept-latest-draft":
                        command_id = payload.get("command_id")
                        if not isinstance(command_id, str) or not command_id:
                            raise BeginnerRequestError(400, "command_id must be a non-empty string")
                        self._send_json(
                            200,
                            accept_latest_chapter(
                                self.project_root,
                                chapter_index,
                                command_id=command_id,
                            ),
                        )
                        return
                    if action == "revision-handoff":
                        command_id = payload.get("command_id")
                        decision = payload.get("decision")
                        route = payload.get("route")
                        if not isinstance(command_id, str) or not command_id:
                            raise BeginnerRequestError(400, "command_id must be a non-empty string")
                        if not isinstance(decision, str) or not decision:
                            raise BeginnerRequestError(400, "decision must be a non-empty string")
                        if not isinstance(route, str) or not route:
                            raise BeginnerRequestError(400, "route must be a non-empty string")
                        self._send_json(
                            200,
                            prepare_revision_handoff(
                                self.project_root,
                                chapter_index,
                                command_id=command_id,
                                decision=decision,
                                route=route,
                            ),
                        )
                        return
                except BeginnerRequestError:
                    raise
                except (FileNotFoundError, OSError, RuntimeError, ValueError) as exc:
                    raise BeginnerRequestError(422, str(exc)) from exc
            if parts == ["api", "beginner", "workspaces"]:
                self._handle_create(self._read_json())
                return
            if (
                len(parts) == 6
                and parts[:3] == ["api", "beginner", "workspaces"]
                and parts[4] == "commands"
            ):
                workspace_id, slug = parts[3], parts[5]
                self._handle_command(workspace_id, slug, self._read_json())
                return
            self._send_json(404, {"error": "Not found"})
        except Exception as exc:
            self._handle_error(exc)

    def _handle_create(self, payload: dict[str, Any]) -> None:
        command_id = payload.get("command_id")
        project_id = payload.get("project_id")
        guidance_genre = payload.get("guidance_genre", "mystery")
        premise = payload.get("premise")
        workspace_id = payload.get("workspace_id") or f"workspace-{secrets.token_hex(4)}"
        if not isinstance(command_id, str) or not command_id:
            raise BeginnerRequestError(400, "command_id must be a non-empty string")
        if not isinstance(project_id, str) or not project_id:
            raise BeginnerRequestError(400, "project_id must be a non-empty string")
        if not isinstance(premise, str) or not premise:
            raise BeginnerRequestError(400, "premise must be a non-empty string")
        if not isinstance(workspace_id, str) or not workspace_id:
            raise BeginnerRequestError(400, "workspace_id must be a non-empty string")
        if guidance_genre != "mystery":
            raise BeginnerRequestError(422, f"unsupported guidance_genre: {guidance_genre!r}")
        try:
            app = self._app_for(workspace_id)
        except ValueError as exc:
            raise BeginnerRequestError(400, str(exc)) from exc
        try:
            app.create_workspace(
                command_id=command_id,
                project_id=project_id,
                premise=premise,
                guidance_genre=guidance_genre,
            )
        except BeginnerConcurrencyError:
            raise
        except BeginnerPersistenceError:
            raise
        except ValueError as exc:
            raise BeginnerRequestError(400, str(exc)) from exc
        projection = app.projection()
        self._send_json(201, projection_to_dict(projection, workspace_id=workspace_id))

    def _handle_command(self, workspace_id: str, slug: str, payload: dict[str, Any]) -> None:
        method_name = _COMMAND_HANDLERS.get(slug)
        if method_name is None:
            self._send_json(404, {"error": f"Unknown command: {slug}"})
            return
        try:
            envelope = MutationCommand.model_validate(payload)
        except ValidationError as exc:
            raise BeginnerRequestError(400, f"malformed command envelope: {exc}") from exc
        if envelope.workspace_id != workspace_id:
            raise BeginnerRequestError(400, "envelope workspace_id does not match path workspace_id")
        try:
            app = self._app_for(workspace_id)
        except ValueError as exc:
            raise BeginnerRequestError(400, str(exc)) from exc
        handler: Callable[..., Any] = getattr(app, method_name)
        rich_commands = {
            "continue-architecture",
            "select-direction",
            "confirm-architecture-component",
            "suppress-architecture-component",
            "restore-architecture-component",
            "rename-architecture-component",
            "choose-architecture-alternative",
            "set-architecture-component-role",
            "add-architecture-component",
            "reanalyze-premise",
            "propose-outline",
            "accept-outline",
            "propose-chapter-plan",
            "accept-chapter-plan",
            "propose-scene-plans",
            "accept-scene-plans",
            "prepare-draft-handoff",
        }
        if slug in rich_commands:
            kwargs: dict[str, Any] = {
                "expected_session_version": envelope.expected_session_version,
                "command_id": envelope.command_id,
                **dict(envelope.payload),
            }
            if "role" in kwargs and isinstance(kwargs["role"], str):
                kwargs["role"] = ArchitectureRole(kwargs["role"])
            if "facet" in kwargs and isinstance(kwargs["facet"], str):
                kwargs["facet"] = ArchitectureFacet(kwargs["facet"])
            handler(**kwargs)
        else:
            handler(command=envelope)
        projection = app.projection()
        self._send_json(200, projection_to_dict(projection, workspace_id=workspace_id))


class BeginnerWorkspaceServer:
    def __init__(
        self,
        project_root: Path | str,
        *,
        port: int,
        dependencies: BeginnerRuntimeDependencies | None = None,
    ):
        self.project_root = Path(project_root)
        self.dependencies = dependencies or default_runtime_dependencies()
        handler = type(
            "BoundBeginnerWorkspaceRequestHandler",
            (_RequestHandler,),
            {
                "project_root": self.project_root,
                "dependencies": self.dependencies,
            },
        )
        self._httpd = ThreadingHTTPServer(("127.0.0.1", port), handler)
        self.port = int(self._httpd.server_address[1])
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        try:
            self._httpd.serve_forever(poll_interval=0.05)
        finally:
            self._httpd.server_close()

    def start_in_thread(self) -> threading.Thread:
        if self._thread and self._thread.is_alive():
            raise RuntimeError("Beginner workspace server is already running")
        self._thread = threading.Thread(target=self.start, daemon=True)
        self._thread.start()
        return self._thread

    def stop(self) -> None:
        self._httpd.shutdown()
        self._httpd.server_close()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Serve an Auteur beginner workspace.")
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--port", type=int, default=0)
    parser.add_argument("--provider", choices=("openai", "anthropic"))
    parser.add_argument("--model")
    args = parser.parse_args(argv)
    if args.provider:
        client = build_client(args.provider, args.model)
        resolved_model = args.model or (
            "gpt-4o" if args.provider == "openai" else "claude-sonnet-4-6"
        )
        dependencies = BeginnerRuntimeDependencies(
            architecture_analyzer=ResilientArchitectureAnalyzer(
                primary=ProviderArchitectureAnalyzer(
                    client=client,
                    analyzer_id="beginner-architecture",
                    analyzer_version="1",
                    model_id=resolved_model,
                    provider_id=args.provider,
                ),
                fallback=DeterministicArchitectureAnalyzer(),
            ),
            discovery_recommender=StoryDiscoveryRecommender(client=client),
        )
    else:
        dependencies = default_runtime_dependencies()
    server = BeginnerWorkspaceServer(
        args.project,
        port=args.port,
        dependencies=dependencies,
    )
    print(f"Beginner workspace server on http://127.0.0.1:{server.port}")
    try:
        server.start()
    except KeyboardInterrupt:
        return 130
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
