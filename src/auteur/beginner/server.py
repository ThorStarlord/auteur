"""Local JSON surface for the post-draft Beginner Workspace projection."""

from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from .continuation import build_chapter_plan, build_scene_plans
from .post_draft import accept_latest_chapter, project_draft_review, project_next_chapter_context


def _json_value(value: Any) -> Any:
    if is_dataclass(value):
        return _json_value(asdict(value))
    if isinstance(value, dict):
        return {key: _json_value(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_json_value(item) for item in value]
    if hasattr(value, "value"):
        return value.value
    return value


def create_server(project_root: Path, host: str = "127.0.0.1", port: int = 0) -> HTTPServer:
    root = Path(project_root)

    class Handler(BaseHTTPRequestHandler):
        def _send(self, status: int, payload: Any) -> None:
            body = json.dumps(_json_value(payload)).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self) -> None:  # noqa: N802
            parts = [part for part in urlparse(self.path).path.split("/") if part]
            try:
                if parts[:3] == ["api", "beginner", "chapters"] and len(parts) == 5:
                    chapter = int(parts[3])
                    if parts[4] == "review":
                        self._send(200, project_draft_review(root, chapter))
                        return
                    if parts[4] == "next":
                        self._send(200, project_next_chapter_context(root, chapter))
                        return
                    if parts[4] == "plan":
                        self._send(200, {"plan": build_chapter_plan(root, chapter), "scenes": build_scene_plans(root, chapter)})
                        return
            except (ValueError, OSError, json.JSONDecodeError) as exc:
                self._send(422, {"error": str(exc)})
                return
            self._send(404, {"error": "unknown beginner endpoint"})

        def do_POST(self) -> None:  # noqa: N802
            parts = [part for part in urlparse(self.path).path.split("/") if part]
            if parts[:3] != ["api", "beginner", "chapters"] or len(parts) != 5 or parts[4] != "accept-latest-draft":
                self._send(404, {"error": "unknown beginner endpoint"})
                return
            try:
                chapter = int(parts[3])
                length = int(self.headers.get("Content-Length", "0"))
                payload = json.loads(self.rfile.read(length) or b"{}")
                command_id = payload.get("command_id")
                result = accept_latest_chapter(root, chapter, command_id=command_id)
                self._send(200, result)
            except (FileNotFoundError, ValueError, OSError, json.JSONDecodeError, RuntimeError) as exc:
                self._send(422, {"error": str(exc)})

        def log_message(self, *_args: Any) -> None:
            return

    return HTTPServer((host, port), Handler, bind_and_activate=False)
