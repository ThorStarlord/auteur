"""Local Guided Author Workspace over existing Auteur projections and services."""

from __future__ import annotations

import argparse
import json
import secrets
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from auteur.application import AuthorActionService
from auteur.structure.proposal_service import ProposalReviewService
from auteur.ui.dashboard import build_dashboard


_AUTHORITY = "GUIDED WORKSPACE / EXPLICIT ACTIONS"
_WORKFLOW_STAGES = [
    "Tutor guidance",
    "Proposal review",
    "Revision plan",
    "Change preview",
    "Explicit authority action",
    "Reassessment",
]
_MAX_BODY_BYTES = 64 * 1024


_WORKSPACE_HTML = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Auteur — Guided Author Workspace</title>
<style>
:root{font-family:Inter,system-ui,sans-serif;line-height:1.5;background:#f4f2ed;color:#1f2420}*{box-sizing:border-box}body{margin:0}.shell{max-width:960px;margin:0 auto;padding:48px 24px 80px}.eyebrow{font-size:.78rem;font-weight:700;letter-spacing:.12em;text-transform:uppercase;color:#5c665f}h1{font-size:clamp(2rem,5vw,3.6rem);line-height:1.02;margin:.35rem 0 1rem}.lead{max-width:720px;color:#4c554e}.card{background:#fff;border:1px solid #d7d8d2;border-radius:18px;padding:24px;margin:24px 0;box-shadow:0 8px 26px rgba(20,28,22,.05)}.badge{display:inline-block;border:1px solid #b5b9b2;border-radius:999px;padding:5px 10px;font-size:.75rem;font-weight:700}.row{display:grid;grid-template-columns:1fr auto;gap:16px;align-items:start}.muted{color:#687169}.reason{font-size:1.08rem;margin:.65rem 0}.command{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;background:#171b18;color:#f7f6f2;border-radius:12px;padding:14px;overflow-wrap:anywhere;margin-top:12px}button{border:0;border-radius:10px;padding:9px 12px;font:inherit;font-weight:650;cursor:pointer;margin:5px 5px 5px 0}.primary{background:#1f2420;color:#fff}.danger{background:#7c2923;color:#fff}.rail{display:grid;grid-template-columns:repeat(6,1fr);gap:8px;list-style:none;padding:0;margin:18px 0 0}.rail li{font-size:.78rem;padding:10px;border-top:3px solid #a9aea8;color:#4e5750}.list{display:grid;gap:10px}.item{border-top:1px solid #e2e2dd;padding-top:12px}.error{color:#8a3029}.success{color:#26643a}select,input{padding:8px;border:1px solid #bbb;border-radius:8px;max-width:100%}@media(max-width:700px){.rail{grid-template-columns:repeat(2,1fr)}.row{grid-template-columns:1fr}}
</style></head><body><main class="shell"><div class="eyebrow">Auteur · local workspace</div><h1>Your story, one decision at a time.</h1><p class="lead">This workspace can carry the qualified Structure decision loop through the same application services as the CLI. Derived guidance never changes canon; authority-bearing application still requires an explicit confirmation.</p><section class="card"><div class="row"><div><span id="authority" class="badge">Loading…</span><p id="project" class="muted"></p></div><button class="primary" onclick="loadWorkspace()">Refresh</button></div></section><section class="card"><div class="eyebrow">What needs your attention</div><div id="primary"><p class="muted">Loading project state…</p></div><div id="actions"></div><p id="actionStatus"></p></section><section class="card"><div class="eyebrow">Decision loop</div><p class="muted">Selection and planning are not acceptance. The authority step is separately confirmed.</p><ol id="rail" class="rail"></ol></section><section class="card"><div class="eyebrow">Other pending items</div><div id="items" class="list"></div></section></main><script>
let csrf='';let workspace=null;const esc=(el,v)=>{el.textContent=v??''};
function attentionNode(item){const box=document.createElement('div');box.className='item';const t=document.createElement('strong');esc(t,`${item.kind} · ${item.state}`);box.appendChild(t);const r=document.createElement('p');r.className='reason';esc(r,item.reason);box.appendChild(r);const a=document.createElement('div');a.className='badge';esc(a,item.authority_status);box.appendChild(a);return box}
async function act(name,payload){const status=document.getElementById('actionStatus');status.className='muted';status.textContent='Applying bounded action…';const response=await fetch(`/api/actions/${name}`,{method:'POST',headers:{'Content-Type':'application/json','X-Auteur-CSRF':csrf},body:JSON.stringify(payload)});const data=await response.json();if(!response.ok||data.result.status!=='ok'){status.className='error';status.textContent=data.result.message||`Action blocked (${response.status})`}else{status.className='success';status.textContent=`Completed: ${data.result.action}. Authority: ${data.result.authority_status}`;}workspace=data.workspace||workspace;render(workspace);return data.result}
function button(label,fn,cls='primary'){const b=document.createElement('button');b.className=cls;b.textContent=label;b.onclick=fn;return b}
function renderActions(data){const host=document.getElementById('actions');host.replaceChildren();const item=data.primary_attention;if(!item)return;const detail=data.primary_detail||{};if(item.kind==='tutor_session'&&item.state==='active'){const input=document.createElement('input');input.placeholder='Your choice';host.appendChild(input);host.appendChild(button('Record choice',()=>act('tutor-choose',{session_id:item.artifact_id,response_action:'choose',value:input.value})));}else if(item.kind==='structure_proposal'&&item.state==='unselected'){const select=document.createElement('select');for(const opt of (detail.options||[])){const o=document.createElement('option');o.value=opt.id;o.textContent=`${opt.summary} — ${opt.tradeoffs}`;select.appendChild(o)}host.appendChild(select);host.appendChild(button('Select proposal option',()=>act('proposal-select',{proposal:detail.proposal_path,option:select.value,author:'Workspace author'})));}else if(item.kind==='structure_proposal'&&item.state==='selected'){host.appendChild(button('Create revision plan',()=>act('revision-plan',{proposal:detail.proposal_path})));}else if(item.kind==='structure_revision_plan'&&item.state==='draft'){host.appendChild(button('Validate revision plan',()=>act('revision-validate',{plan_id:item.artifact_id})));}else if(item.kind==='structure_revision_plan'&&item.state==='ready'){host.appendChild(button('Preview consequences',()=>act('revision-preview',{plan_id:item.artifact_id})));host.appendChild(button('Confirm and apply Structure revision',()=>{if(confirm('This changes accepted Structure. Apply this validated revision?'))act('revision-apply',{plan_id:item.artifact_id,confirmed:true})},'danger'));}}
function render(data){if(!data)return;esc(document.getElementById('authority'),data.authority_status);esc(document.getElementById('project'),data.dashboard.project);const primary=document.getElementById('primary');primary.replaceChildren();if(data.primary_attention)primary.appendChild(attentionNode(data.primary_attention));else{const p=document.createElement('p');p.className='muted';p.textContent='No pending Tutor/proposal/revision item requires attention.';primary.appendChild(p)}const rail=document.getElementById('rail');rail.replaceChildren(...data.workflow_stages.map(stage=>{const li=document.createElement('li');li.textContent=stage;return li}));const items=document.getElementById('items');items.replaceChildren();const rest=data.dashboard.author_attention.slice(data.primary_attention?1:0);if(rest.length)rest.forEach(item=>items.appendChild(attentionNode(item)));else{const p=document.createElement('p');p.className='muted';p.textContent='Nothing else is queued.';items.appendChild(p)}renderActions(data)}
async function loadWorkspace(){try{const response=await fetch('/api/workspace',{cache:'no-store'});if(!response.ok)throw new Error(`HTTP ${response.status}`);workspace=await response.json();csrf=workspace.csrf_token;render(workspace)}catch(error){const p=document.getElementById('actionStatus');p.className='error';p.textContent=`Workspace unavailable: ${error}`}}loadWorkspace();
</script></body></html>"""


def _primary_detail(project_root: Path, attention: dict[str, Any] | None) -> dict[str, Any] | None:
    if not attention:
        return None
    if attention.get("kind") == "structure_proposal":
        proposal_id = attention.get("artifact_id")
        path = project_root / ".auteur" / "structure" / "proposals" / f"{proposal_id}.yaml"
        try:
            return ProposalReviewService(project_root).inspect(path)
        except Exception:
            return None
    if attention.get("kind") == "tutor_session":
        from auteur.story_design_packs.session import TutorSessionStore

        try:
            session = TutorSessionStore(project_root).load(str(attention.get("artifact_id", "")))
            return session.model_dump(mode="json")
        except Exception:
            return None
    return {"plan_id": attention.get("artifact_id")}


def build_workspace_payload(
    project_root: Path,
    *,
    csrf_token: str | None = None,
) -> dict[str, Any]:
    """Compose Workspace state without changing narrative artifacts."""
    root = Path(project_root).resolve()
    dashboard = build_dashboard(root)
    attention = dashboard.get("author_attention", [])
    primary = attention[0] if attention else None
    return {
        "authority_status": _AUTHORITY,
        "mutates_story_without_explicit_action": False,
        "supports_explicit_actions": True,
        "csrf_token": csrf_token,
        "dashboard": dashboard,
        "primary_attention": primary,
        "primary_detail": _primary_detail(root, primary),
        "workflow_stages": list(_WORKFLOW_STAGES),
    }


class _WorkspaceHandler(BaseHTTPRequestHandler):
    project_root: Path
    csrf_token: str
    workspace_port: int

    def log_message(self, format: str, *args: Any) -> None:
        return

    def _send(self, status: int, body: bytes, content_type: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Security-Policy", "default-src 'self'; style-src 'unsafe-inline' 'self'; script-src 'unsafe-inline' 'self'")
        self.end_headers()
        self.wfile.write(body)

    def _json(self, status: int, payload: dict[str, Any]) -> None:
        self._send(
            status,
            json.dumps(payload, ensure_ascii=True, default=str).encode("utf-8"),
            "application/json; charset=utf-8",
        )

    def _valid_host(self) -> bool:
        raw = self.headers.get("Host", "")
        host = raw.rsplit(":", 1)[0].lower()
        return host in {"127.0.0.1", "localhost"}

    def _valid_origin(self) -> bool:
        origin = self.headers.get("Origin", "")
        return origin in {
            f"http://127.0.0.1:{self.workspace_port}",
            f"http://localhost:{self.workspace_port}",
        }

    def _payload(self) -> dict[str, Any]:
        raw_length = self.headers.get("Content-Length")
        if raw_length is None:
            raise ValueError("Content-Length is required")
        length = int(raw_length)
        if length < 0 or length > _MAX_BODY_BYTES:
            raise ValueError("Workspace action payload is too large")
        raw = self.rfile.read(length)
        data = json.loads(raw.decode("utf-8"))
        if not isinstance(data, dict):
            raise ValueError("Workspace action payload must be a JSON object")
        return data

    def do_GET(self) -> None:
        if not self._valid_host():
            self._json(403, {"error": "Invalid Workspace host"})
            return
        path = urlparse(self.path).path
        try:
            if path == "/":
                self._send(200, _WORKSPACE_HTML.encode("utf-8"), "text/html; charset=utf-8")
            elif path == "/health":
                self._json(200, {"status": "ok", "authority_status": _AUTHORITY, "supports_explicit_actions": True})
            elif path == "/api/workspace":
                self._json(200, build_workspace_payload(self.project_root, csrf_token=self.csrf_token))
            else:
                self._json(404, {"error": "Not found"})
        except Exception as exc:
            self._json(500, {"error": f"Workspace projection failed: {exc}"})

    def do_POST(self) -> None:
        if not self._valid_host() or not self._valid_origin():
            self._json(403, {"error": "Workspace request origin/host rejected"})
            return
        if not secrets.compare_digest(self.headers.get("X-Auteur-CSRF", ""), self.csrf_token):
            self._json(403, {"error": "Workspace CSRF token rejected"})
            return
        path = urlparse(self.path).path
        prefix = "/api/actions/"
        if not path.startswith(prefix) or len(path) <= len(prefix):
            self._json(404, {"error": "Not found"})
            return
        action = path[len(prefix):]
        try:
            payload = self._payload()
            result = AuthorActionService(self.project_root).execute(action, payload)
            status = 200 if result.status == "ok" else 409 if result.status == "blocked" else 400
            self._json(
                status,
                {
                    "result": result.model_dump(mode="json"),
                    "workspace": build_workspace_payload(
                        self.project_root, csrf_token=self.csrf_token
                    ),
                },
            )
        except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
            self._json(400, {"error": f"Invalid Workspace action: {exc}"})
        except Exception as exc:
            self._json(500, {"error": f"Workspace action failed safely: {exc}"})


class GuidedAuthorWorkspaceServer:
    """Loopback-only server exposing bounded explicit actions over application services."""

    def __init__(self, project_root: Path, *, port: int = 8765) -> None:
        root = Path(project_root).resolve()
        token = secrets.token_urlsafe(32)
        handler = type(
            "BoundWorkspaceHandler",
            (_WorkspaceHandler,),
            {"project_root": root, "csrf_token": token, "workspace_port": port},
        )
        self._httpd = ThreadingHTTPServer(("127.0.0.1", port), handler)
        self.port = int(self._httpd.server_address[1])
        # Port 0 resolves after binding; handlers must validate the actual port.
        handler.workspace_port = self.port
        self.host = "127.0.0.1"
        self.csrf_token = token
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
    parser = argparse.ArgumentParser(
        prog="auteur workspace",
        description="Serve the loopback-only Guided Author Workspace.",
    )
    parser.add_argument("--project", type=Path, default=Path("."))
    parser.add_argument("--port", type=int, default=8765)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_workspace_args(list(argv or []))
    server = GuidedAuthorWorkspaceServer(args.project, port=args.port)
    print(f"Guided Author Workspace: http://{server.host}:{server.port}")
    print("Status: GUIDED WORKSPACE / EXPLICIT ACTIONS")
    try:
        server.start()
    except KeyboardInterrupt:
        pass
    return 0
