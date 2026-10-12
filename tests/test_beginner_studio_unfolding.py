"""Focused unfolding uses the existing graph, CanvasStore, and explicit source-linked host-agent boundary."""
from pathlib import Path
import json
import re
from urllib.request import Request, urlopen
from urllib.error import HTTPError

from auteur.beginner.server import BeginnerWorkspaceServer

BROWSER=Path(__file__).resolve().parents[1]/"src/auteur/beginner/browser"

def source(name):
    return (BROWSER/name).read_text(encoding="utf-8")

def api(base,method,route,payload=None):
    body=None if payload is None else json.dumps(payload).encode("utf-8")
    req=Request(base+route,method=method,data=body,headers={"Content-Type":"application/json"})
    with urlopen(req) as result:
        return result.status,json.loads(result.read().decode("utf-8"))

def test_focus_overlay_is_source_scoped_and_does_not_become_canonical():
    html=source("studio.html")
    js=source("studio.js")
    assert 'id="unfolding-ghosts"' in html
    assert 'id="unfolding-start"' in html
    assert 'id="unfolding-explanation"' in html
    assert 'id="unfolding-role"' in html
    assert 'src="/studio_unfolding.js"' in html
    assert html.index('/studio_unfolding.js')<html.index('/studio.js')
    assert "function renderUnfolding()" in js
    controller=source("studio_unfolding_controller.js")
    assert "window.AuteurStudioUnfoldingController.create" in js
    assert "global.AuteurStudioUnfoldingController={create:create}" in controller
    renderer=controller.split("function render(){",1)[1].split("function more(){",1)[0]
    assert "projectLocalSuggestions(" in controller
    assert "queueSave(" not in renderer and "applyReviewedArchitecture(" not in renderer
    assert "requestArchitecture(" not in renderer
    assert "accepted story" not in renderer.lower() or "not accepted" in renderer.lower()

def test_single_explicit_adopt_uses_canvas_command_not_story_acceptance():
    js=source("studio.js")
    assert "function adoptUnfolding(" in js
    controller=source("studio_unfolding_controller.js")
    assert "updateWorkingCommand('adopt-suggestion'" in controller
    assert "/commands/" in js
    assert "expected_revision" in js
    assert "remote.canvasId" in js
    assert "architectureRequestSha" in controller
    assert "applyReviewedArchitecture(" not in controller

def test_server_exposes_helper_without_exposing_arbitrary_assets():
    js=source("studio.js")
    server=(BROWSER.parent/"server.py").read_text(encoding="utf-8")
    assert '"/studio_unfolding.js": "studio_unfolding.js"' in server
    assert '"/studio_unfolding_controller.js": "studio_unfolding_controller.js"' in server
    assert 'src="/studio_unfolding.js"' in source("studio.html")
    assert 'src="/studio_unfolding_controller.js"' in source("studio.html")
    ids=re.findall(r'\bid="([^"]+)"',source("studio.html"))
    assert len(ids)==len(set(ids))

def test_real_canvas_http_adoption_and_idempotent_replay(tmp_path):
    server=BeginnerWorkspaceServer(tmp_path,port=0)
    thread=server.start_in_thread()
    try:
        base=f"http://127.0.0.1:{server.port}"
        status,first=api(base,"POST","/api/beginner/studio/canvases",{"canvas_id":"unfold-test"})
        assert status==201 and first["revision"]==0
        payload={"command_id":"adopt-1","expected_revision":0,"payload":{
            "item":{"id":"adopted","title":"Earned breakthrough","kind":"note","content":"An author-editable hypothesis",
                "architecture_role":"trope","group":"Narrative Architecture","proposal_origin":{
                    "request_sha":"a"*64,"source_ref":"links/0","source_kind":"proposal_edge","focus_id":"g"}},
            "position":{"x":250,"y":350}}}
        route="/api/beginner/studio/canvases/unfold-test/commands/adopt-suggestion"
        status,one=api(base,"POST",route,payload)
        assert status==200 and one["revision"]==1
        _,again=api(base,"POST",route,payload)
        assert len(again["items"])==1 and again["revision"]==1
        _,reloaded=api(base,"GET","/api/beginner/studio/canvases/unfold-test")
        assert reloaded["items"][0]["architecture_role"]=="trope"
        assert reloaded["items"][0]["proposal_origin"]["source_ref"]=="links/0"
        payload["command_id"]="adopt-second"
        payload["expected_revision"]=1
        payload["payload"]["item"]["id"]="duplicate"
        try:
            api(base,"POST",route,payload)
            assert False,"Duplicate source unexpectedly accepted"
        except HTTPError as e:
            assert e.code==400
        assert not (tmp_path/"story_identity.yaml").exists()
    finally:
        server.stop();thread.join(timeout=2)
        assert not thread.is_alive()

def test_frontend_can_create_manual_emotion_anchor_without_an_agent():
    js=source("studio.js")
    assert "function createUnfoldingAnchor(" in js
    controller=source("studio_unfolding_controller.js")
    assert "buildManualAnchorCommand" in controller
    assert "updateWorkingCommand('create-item'" in controller
    assert "expected_revision" in js
    assert "requestArchitecture(" not in controller

def test_unfolding_controller_is_initialized_with_canvasstore_bridge():
    js=source("studio.js")
    assert "window.AuteurStudioUnfoldingController.create({" in js
    assert "function createUnfoldingAnchor()" in js
    assert "function adoptUnfolding(ghost)" in js
    assert '"/commands/" + action' in js
    assert "unfoldingController.render()" in js
    assert "unfoldingController.more()" in js
