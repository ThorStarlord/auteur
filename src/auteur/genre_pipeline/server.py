from __future__ import annotations

import argparse
import json
import logging
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from importlib.resources import files
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from auteur.blueprint import Genre
from auteur.genre_pipeline.registry import get_all_genres, get_genre_pipeline
from auteur.genre_pipeline.models import GenreSessionStatus
from auteur.genre_pipeline.session import GenreSessionError, GenreSessionStore
from auteur.genre_pipeline.templates import build_pipeline_descriptor
from auteur.genre_pipeline.validation import validate_pipeline_choices


logger = logging.getLogger(__name__)


class PipelineRequestError(ValueError):
    def __init__(self, status: int, message: str, *, errors: list[str] | None = None):
        super().__init__(message)
        self.status = status
        self.message = message
        self.errors = errors


class GenrePipelineApplication:
    def __init__(self, store: GenreSessionStore):
        self.store = store
        session = store.load()
        if session.genre != store.spec.genre or session.core_id not in store.spec.core_ids:
            raise GenreSessionError("Session genre/core does not match the selected pipeline")

    def session_payload(self) -> dict[str, Any]:
        return self.store.load().model_dump(mode="json")

    def pipeline_payload(self) -> dict[str, Any]:
        session = self.store.load()
        return build_pipeline_descriptor(self.store.spec, session.core_id).model_dump(mode="json")

    def validate(self, *, require_complete: bool = False):
        session = self.store.load()
        return validate_pipeline_choices(
            self.store.spec,
            session.core_id,
            session.choices,
            require_complete=require_complete,
        )

    def health(self) -> dict[str, Any]:
        session = self.store.load()
        return {"status": "ok", "ready": True, "session_id": session.id}

    def history(self) -> dict[str, Any]:
        return {"sessions": [session.model_dump(mode="json") for session in self.store.history()]}

    def acknowledge_warning(self, payload: dict[str, Any]) -> dict[str, Any]:
        warning = payload.get("warning")
        if not isinstance(warning, str) or not warning.strip():
            raise PipelineRequestError(400, "warning must be a non-empty string")
        session = self.store.acknowledge_warning(warning)
        return {"session": session.model_dump(mode="json")}

    def archive(self) -> dict[str, Any]:
        session = self.store.archive()
        return {"archived_session_id": session.id, "session": session.model_dump(mode="json")}

    def update(self, payload: dict[str, Any]) -> dict[str, Any]:
        phase = payload.get("phase")
        choices = payload.get("choices")
        if not isinstance(phase, int) or not isinstance(choices, dict):
            raise PipelineRequestError(400, "phase must be an integer and choices must be an object")
        if not all(isinstance(key, str) and isinstance(value, str) for key, value in choices.items()):
            raise PipelineRequestError(400, "choice keys and values must be strings")

        session = self.store.load()
        if session.status != GenreSessionStatus.INCOMPLETE:
            raise GenreSessionError("A completed genre session cannot be modified")
        candidate = {number: dict(values) for number, values in session.choices.items()}
        candidate.setdefault(phase, {}).update(choices)
        result = validate_pipeline_choices(self.store.spec, session.core_id, candidate)
        if not result.is_valid:
            raise PipelineRequestError(422, "Choice validation failed", errors=result.errors)
        updated = self.store.update_choices(phase, choices, warnings=result.warnings)
        return {
            "is_valid": True,
            "errors": [],
            "warnings": result.warnings,
            "session": updated.model_dump(mode="json"),
        }

    def update_settings(self, payload: dict[str, Any]) -> dict[str, Any]:
        allowed = {"mode", "working_title"}
        unknown = set(payload) - allowed
        if unknown:
            raise PipelineRequestError(400, f"Unknown settings: {', '.join(sorted(unknown))}")
        session = self.store.update_settings(
            mode=payload.get("mode"),
            working_title=payload.get("working_title"),
        )
        return {"session": session.model_dump(mode="json")}

    def complete(self) -> dict[str, Any]:
        if self.store.load().status != GenreSessionStatus.INCOMPLETE:
            raise GenreSessionError("A terminal genre session cannot be completed again")
        result = self.validate(require_complete=True)
        if not result.is_valid:
            raise PipelineRequestError(422, "Session is incomplete or invalid", errors=result.errors)
        session = self.store.mark_complete(warnings=result.warnings)
        return {
            "warnings": result.warnings,
            "session": session.model_dump(mode="json"),
        }


class _RequestHandler(BaseHTTPRequestHandler):
    application: GenrePipelineApplication
    html_content: str

    def log_message(self, format: str, *args: Any) -> None:
        logger.info(format, *args)

    def _send_json(self, status: int, payload: dict[str, Any]) -> None:
        body = json.dumps(payload, ensure_ascii=True).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_html(self) -> None:
        body = self.html_content.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_json(self) -> dict[str, Any]:
        try:
            length = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(length).decode("utf-8") or "{}")
        except (ValueError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise PipelineRequestError(400, "Request body must be valid JSON") from exc
        if not isinstance(payload, dict):
            raise PipelineRequestError(400, "Request body must be a JSON object")
        return payload

    def _handle_error(self, error: Exception) -> None:
        if isinstance(error, PipelineRequestError):
            payload: dict[str, Any] = {"error": error.message}
            if error.errors is not None:
                payload["errors"] = error.errors
            self._send_json(error.status, payload)
        elif isinstance(error, GenreSessionError):
            self._send_json(409, {"error": str(error)})
        else:
            logger.exception("Unhandled genre pipeline request error")
            self._send_json(500, {"error": "Internal server error"})

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        try:
            if path == "/":
                self._send_html()
            elif path == "/health":
                self._send_json(200, self.application.health())
            elif path == "/session":
                self._send_json(200, self.application.session_payload())
            elif path == "/session/history":
                self._send_json(200, self.application.history())
            elif path == "/pipeline":
                self._send_json(200, self.application.pipeline_payload())
            elif path == "/session/validate":
                result = self.application.validate()
                self._send_json(
                    200,
                    {
                        "is_valid": result.is_valid,
                        "errors": result.errors,
                        "warnings": result.warnings,
                    },
                )
            else:
                self._send_json(404, {"error": "Not found"})
        except Exception as exc:
            self._handle_error(exc)

    def do_POST(self) -> None:
        path = urlparse(self.path).path
        try:
            payload = self._read_json()
            if path == "/session/update":
                result = self.application.update(payload)
            elif path == "/session/settings":
                result = self.application.update_settings(payload)
            elif path == "/session/warnings/acknowledge":
                result = self.application.acknowledge_warning(payload)
            elif path == "/session/archive":
                result = self.application.archive()
            elif path == "/session/complete":
                result = self.application.complete()
            else:
                self._send_json(404, {"error": "Not found"})
                return
            self._send_json(200, result)
        except Exception as exc:
            self._handle_error(exc)


class GenrePipelineServer:
    def __init__(self, store: GenreSessionStore, *, port: int):
        self.application = GenrePipelineApplication(store)
        self.html_content = files("auteur.genre_pipeline.browser").joinpath("index.html").read_text(
            encoding="utf-8"
        )
        handler = type(
            "BoundGenrePipelineRequestHandler",
            (_RequestHandler,),
            {"application": self.application, "html_content": self.html_content},
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
            raise RuntimeError("Genre pipeline server is already running")
        self._thread = threading.Thread(target=self.start, daemon=True)
        self._thread.start()
        return self._thread

    def stop(self) -> None:
        self._httpd.shutdown()
        self._httpd.server_close()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Serve an Auteur interactive genre pipeline.")
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument(
        "--genre",
        choices=[spec.slug for spec in get_all_genres()],
        required=True,
    )
    parser.add_argument("--port", type=int)
    args = parser.parse_args(argv)

    spec = get_genre_pipeline(Genre(args.genre))
    store = GenreSessionStore.for_project(args.project, spec)
    server = GenrePipelineServer(store, port=args.port or spec.default_port)
    try:
        server.start()
    except KeyboardInterrupt:
        return 130
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
