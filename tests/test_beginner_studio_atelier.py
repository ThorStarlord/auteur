"""The Atelier visual study is opt-in, explicitly served, and presentation only."""
from pathlib import Path
import re
from urllib.request import urlopen

from auteur.beginner.server import BeginnerWorkspaceServer, _RequestHandler

BROWSER = Path(__file__).resolve().parents[1] / "src/auteur/beginner/browser"
ATELIER = ("studio_atelier_model.js", "studio_atelier.js", "studio_atelier.css")


def source(name):
    return (BROWSER / name).read_text(encoding="utf-8")


def test_every_studio_script_and_stylesheet_is_allowlisted():
    html = source("studio.html")
    referenced = re.findall(r'<script src="(/[^"]+)"', html) + re.findall(r'<link rel="stylesheet" href="(/[^"]+)"', html)
    assert referenced, "Studio references its assets"
    missing = [path for path in referenced if path not in _RequestHandler._BROWSER_ASSETS]
    assert missing == []
    for name in ATELIER:
        assert f"/{name}" in referenced


def test_atelier_assets_are_served(tmp_path):
    server = BeginnerWorkspaceServer(tmp_path, port=0)
    thread = server.start_in_thread()
    try:
        for name, kind in (("studio_atelier_model.js", "javascript"), ("studio_atelier.js", "javascript"),
                           ("studio_atelier.css", "css")):
            with urlopen(f"http://127.0.0.1:{server.port}/{name}") as response:
                assert response.status == 200
                assert kind in response.headers["Content-Type"]
    finally:
        server.stop()
        thread.join(timeout=5)


def test_atelier_loads_after_its_contract_and_before_the_studio():
    html = source("studio.html")
    assert html.index("/studio_explanations.js") < html.index("/studio_atelier_model.js") \
        < html.index("/studio_atelier.js") < html.index("/studio.js")


def test_atelier_is_opt_in_and_never_the_default():
    js = source("studio.js")
    html = source("studio.html")
    assert 'id="studio-mode-atelier" type="button" aria-pressed="false" hidden' in html
    assert 'id="studio-atelier"' in html and 'aria-label="Atelier visual study' in html
    assert 'var atelierEnabled = atelierParam !== null' in js
    assert 'if (atelierEnabled && window.AuteurStudioAtelier)' in js
    # A remembered study mode is honoured only while the study is enabled by URL.
    assert '["focus","full","review"].concat(atelierController ? ["atelier"] : [])' in js
    assert 'if (!atelierController && state.fullArchitectureDisplay === "atelier") state.fullArchitectureDisplay = "focus";' in js
    assert '$("studio-mode-atelier").hidden = !atelierController;' in js


def test_atelier_is_presentation_only():
    for name in ("studio_atelier_model.js", "studio_atelier.js"):
        text = source(name)
        for forbidden in ("fetch(", "XMLHttpRequest", "localStorage", "sessionStorage", "scheduleSave", "queueSave",
                          "requestArchitecture", "applyReviewedArchitecture", "/api/"):
            assert forbidden not in text, f"{name} must not use {forbidden}"
    route = source("studio.js").split("function renderAtelierStudy()", 1)[1].split("function captureInspectorFields()", 1)[0]
    assert "scheduleSave(" not in route and "queueSave(" not in route and "fetch(" not in route


def test_full_architecture_mode_ignores_the_study_mode():
    controller = source("studio_full_architecture_controller.js")
    assert "if(!eligible||mode==='focus'||mode==='atelier')return false;" in controller
    assert "String(mode==='full'||mode==='review')" in controller
