"""Local, read-only Guided Author Workspace over existing Auteur projections."""
from __future__ import annotations

import argparse
import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from auteur.ui.dashboard import build_dashboard


_AUTHORITY = "DERIVED WORKSPACE / READ ONLY"
_WORKFLOW_STAGES = [
    "Tutor guidance",
    "Proposal review",
    "Revision plan",
    "Change preview",
    "Explicit authority action",
    "Reassessment",
]

_WORKSPACE_HTML = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Auteur — Guided Author Workspace</title>
<style>
:root{font-family:Inter,system-ui,sans-serif;line-height:1.5;background:#f4f2ed;color:#1f2420}
*{box-sizing:border-box}body{margin:0}.shell{max-width:960px;margin:0 auto;padding:48px 24px 80px}
.eyebrow{font-size:.78rem;font-weight:700;letter-spacing:.12em;text-transform:uppercase;color:#5c665f}
h1{font-size:clamp(2rem,5vw,3.6rem);line-height:1.02;margin:.35rem 0 1rem}.lead{max-width:690px;color:#4c554e}
.card{background:#fff;border:1px solid #d7d8d2;border-radius:18px;padding:24px;margin:24px 0;box-shadow:0 8px 26px rgba(20,28,22,.05)}
.badge{display:inline-block;border:1px solid #b5b9b2;border-radius:999px;padding:5px 10px;font-size:.75rem;font-weight:700;letter-spacing:.04em}
.row{display:grid;grid-template-columns:1fr auto;gap:16px;align-items:start}.muted{color:#687169}.reason{font-size:1.08rem;margin:.65rem 0}
.command{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;background:#171b18;color:#f7f6f2;border-radius:12px;padding:14px;overflow-wrap:anywhere;margin-top:12px}
button{border:0;border-radius:10px;padding:9px 12px;font:inherit;font-weight:650;cursor:pointer}.refresh{background:#1f2420;color:#fff}.copy{margin-top:10px}
.rail{display:grid;grid-template-columns:repeat(6,1fr);gap:8px;list-style:none;padding:0;margin:18px 0 0}.rail li{font-size:.78rem;padding:10px;border-top:3px solid #a9aea8;color:#4e5750}
.list{display:grid;gap:10px}.item{border-top:1px solid #e2e2dd;padding-top:12px}.error{color:#8a3029}@media(max-width:700px){.rail{grid-template-columns:repeat(2,1fr)}.row{grid-template-columns:1fr}}
</style>
</head>
<body><main class="shell">
<div class="eyebrow">Auteur · local workspace</div>
<h1>Your story, one decision at a time.</h1>
<p class="lead">This workspace explains what needs attention and where authority lives. It never changes the story by itself.</p>
<section class="card"><div class="row"><div><span id="authority" class="badge">Loading…</span><p id="project" class="muted"></p></div><button class="refresh" onclick="loadWorkspace()">Refresh</button></div></section>
<section class="card"><div class="eyebrow">What needs your attention</div><div id="primary"><p class="muted">Loading project state…</p></div></section>
<section class="card"><div class="eyebrow">Decision loop</div><p class="muted">These are workflow stages, not inferred story-quality scores.</p><ol id="rail" class="rail"></ol></section>
<section class="card"><div class="eyebrow">Other pending items</div><div id="items" class="list"></div></section>
</main>
<script>
const escText=(el,value)=>{el.textContent=value??''};
function attentionHTML(item){
  const box=document.createElement('div'); box.className='item';
  const title=document.createElement('strong'); escText(title,`${item.kind} · ${item.state}`); box.appendChild(title);
  const reason=document.createElement('p'); reason.className='reason'; escText(reason,item.reason); box.appendChild(reason);
  const authority=document.createElement('div'); authority.className='badge'; escText(authority,item.authority_status); box.appendChild(authority);
  if(item.next_command){const cmd=document.createElement('div');cmd.className='command';escText(cmd,item.next_command);box.appendChild(cmd);const copy=document.createElement('button');copy.className='copy';copy.textContent='Copy next command';copy.onclick=()=>navigator.clipboard?.writeText(item.next_command);box.appendChild(copy)}
  return box;
}
async function loadWorkspace(){
 try{const response=await fetch('/api/workspace',{cache:'no-store'}); if(!response.ok)throw new Error(`HTTP ${response.status}`); const data=await response.json();
  escText(document.getElementById('authority'),data.authority_status);escText(document.getElementById('project'),data.dashboard.project);
  const primary=document.getElementById('primary');primary.replaceChildren(); if(data.primary_attention)primary.appendChild(attentionHTML(data.primary_attention));else{const p=document.createElement('p');p.className='muted';p.textContent='No pending Tutor/proposal/revision item requires attention.';primary.appendChild(p)}
  const rail=document.getElementById('rail');rail.replaceChildren(...data.workflow_stages.map(stage=>{const li=document.createElement('li');li.textContent=stage;return li}));
  const items=document.getElementById('items');items.replaceChildren();const rest=data.dashboard.author_attention.slice(data.primary_attention?1:0);if(rest.length)rest.forEach(item=>items.appendChild(attentionHTML(item)));else{const p=document.createElement('p');p.className='muted';p.textContent='Nothing else is queued.';items.appendChild(p)}
 }catch(error){const primary=document.getElementById('primary');primary.replaceChildren();const p=document.createElement('p');p.className='error';p.textContent=`Workspace unavailable: ${error}`;primary.appendChild(p)}
}
loadWorkspace();
</script></body></html>"""


def build_workspace_payload(project_root: Path) -> dict[str, Any]:
    """Compose beginner-facing workspace state without changing project artifacts."""
    dashboard = build_dashboard(project_root)
    attention = dashboard.get("author_attention", [])
    return {
        "authority_status": _AUTHORITY,
        "mutates_story": False,
        "dashboard": dashboard,
        "primary_attention": attention[0] if attention else None,
        "workflow_stages": list(_WORKFLOW_STAGES),
    }


class _WorkspaceHandler(BaseHTTPRequestHandler):
    project_root: Path

    def log_message(self, format: str, *args: Any) -> None:
        return

    def _send(self, status: int, body: bytes, content_type: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _json(self, status: int, payload: dict[str, Any]) -> None:
        self._send(
            status,
            json.dumps(payload, ensure_ascii=True, default=str).encode("utf-8"),
            "application/json; charset=utf-8",
        )

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        try:
            if path == "/":
                self._send(200, _WORKSPACE_HTML.encode("utf-8"), "text/html; charset=utf-8")
            elif path == "/health":
                self._json(200, {"status": "ok", "authority_status": _AUTHORITY, "mutates_story": False})
            elif path == "/api/workspace":
                self._json(200, build_workspace_payload(self.project_root))
            else:
                self._json(404, {"error": "Not found"})
        except Exception as exc:
            self._json(500, {"error": f"Workspace projection failed: {exc}"})

    def do_POST(self) -> None:
        self._json(405, {"error": "Guided Author Workspace V1 is read-only"})


class GuidedAuthorWorkspaceServer:
    """Loopback-only HTTP server for the read-only Guided Author Workspace."""

    def __init__(self, project_root: Path, *, port: int = 8765) -> None:
        root = Path(project_root).resolve()
        handler = type("BoundWorkspaceHandler", (_WorkspaceHandler,), {"project_root": root})
        self._httpd = ThreadingHTTPServer(("127.0.0.1", port), handler)
        self.port = int(self._httpd.server_address[1])
        self.host = "127.0.0.1"
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        try:
            self._httpd.serve_forever(poll_interval=0.05)
        finally:
            self._httpd.server_close()

    def start_in_thread(self) -> threading.Thread:
        if self._thread and self._thread.is_alive():
            raise RuntimeError("Guided Author Workspace server is already running")
        self._thread = threading.Thread(target=self.start, daemon=True)
        self._thread.start()
        return self._thread

    def stop(self) -> None:
        self._httpd.shutdown()
        self._httpd.server_close()


def parse_workspace_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="auteur workspace", description="Serve the read-only Guided Author Workspace.")
    parser.add_argument("--project", type=Path, default=Path("."))
    parser.add_argument("--port", type=int, default=8765)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_workspace_args(list(argv or []))
    server = GuidedAuthorWorkspaceServer(args.project, port=args.port)
    print(f"Guided Author Workspace: http://{server.host}:{server.port}")
    print("Status: DERIVED WORKSPACE / READ ONLY")
    try:
        server.start()
    except KeyboardInterrupt:
        pass
    return 0
