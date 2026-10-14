"""Issue #360 Stage-B essential safety subset, exercised in a real browser against a live server.

Usage (Playwright is not an Auteur dependency; install it in any environment):
    pip install playwright
    AUTEUR_PYTHON=.venv/bin/python python scripts/studio_stage_b_check.py /tmp/stage-b-project

Optional: CHROMIUM_PATH=/path/to/chrome to use an existing Chromium build.
With no argument, a fresh temporary project is created and kept for inspection.
An argument must name a path that does not exist yet (or an empty directory); the
script never deletes a directory it did not create. Exit code is non-zero if any check fails.
"""

import hashlib
import json
import socket
import os
import pathlib
import tempfile
import subprocess
import sys
import time
import urllib.request
from playwright.sync_api import sync_playwright

PY = os.environ.get("AUTEUR_PYTHON", sys.executable)
PORT = int(os.environ["STAGE_B_PORT"]) if os.environ.get("STAGE_B_PORT") else None
REPO = pathlib.Path(__file__).resolve().parent.parent
CHROME = os.environ.get("CHROMIUM_PATH")
if len(sys.argv) > 1:
    proj = pathlib.Path(sys.argv[1]).resolve()
    if proj.exists() and (not proj.is_dir() or any(proj.iterdir())):
        sys.exit(f"Refusing to use non-empty existing path: {proj}. Pass a new path or omit the argument.")
    proj.mkdir(parents=True, exist_ok=True)
else:
    proj = pathlib.Path(tempfile.mkdtemp(prefix="auteur-stage-b-"))
    print(f"Project: {proj}")
results = []


def check(name, ok, detail=""):
    results.append((name, bool(ok)))
    print(("PASS " if ok else "FAIL ") + name + (" :: " + str(detail) if detail else ""))


def free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        return sock.connect_ex(("127.0.0.1", port)) == 0


PORT = PORT or free_port()
BASE = f"http://127.0.0.1:{PORT}"


def start():
    """Start a server on PORT and insist that the answering server is this process."""
    if port_in_use(PORT):
        raise RuntimeError(f"port {PORT} is already in use; set STAGE_B_PORT to a free port")
    p = subprocess.Popen(
        [
            PY,
            "-m",
            "auteur.beginner.server",
            "--project",
            str(proj),
            "--port",
            str(PORT),
            "--studio-development-default",
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        cwd=str(REPO),
    )
    for _ in range(100):
        if p.poll() is not None:
            raise RuntimeError(f"server exited early with code {p.returncode}")
        try:
            urllib.request.urlopen(BASE + "/api/beginner/health", timeout=2)
            return p
        except Exception:
            time.sleep(0.2)
    p.terminate()
    raise RuntimeError("server did not start")


def canonical_snapshot():
    """Map each non-canonical-store file to its SHA-256 content hash."""
    # Studio working store and Quick Draft's provisional staging are non-canonical by design.
    noncanonical = (".auteur/beginner/studio", ".auteur/quick_draft")
    snapshot = {}
    for f in proj.rglob("*"):
        if not f.is_file():
            continue
        relative = f.relative_to(proj).as_posix()
        if any(relative.startswith(f"{part}/") for part in noncanonical):
            continue
        snapshot[relative] = hashlib.sha256(f.read_bytes()).hexdigest()
    return snapshot


def canvas_docs():
    return {f.parent.name: json.loads(f.read_text()) for f in proj.rglob("canvas.json")}


def item_text(doc):
    return json.dumps(doc)


srv = None
try:
    srv = start()
    before = canonical_snapshot()
    with sync_playwright() as pw:
        br = pw.chromium.launch(**{"executable_path": CHROME} if CHROME else {})
        pg = br.new_page(viewport={"width": 1300, "height": 900})
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))

        def open_(page):
            page.goto(BASE + "/", wait_until="networkidle")
            page.wait_for_timeout(600)

        open_(pg)
        check("root serves Studio with --studio-development-default", pg.locator("#viewport").count() == 1)
        pg.click("#workspace-realization")
        pg.wait_for_timeout(300)
        pg.click("#add-note")
        pg.wait_for_timeout(300)
        pg.fill("#title", "Note A")
        pg.fill("#content", "alpha text one")
        pg.click("#add-note")
        pg.wait_for_timeout(300)
        pg.fill("#title", "Note B")
        pg.fill("#content", "beta text")
        pg.locator("button.node", has_text="Note A").first.click()
        pg.wait_for_timeout(300)
        check(
            "A->B->A edit preserved in inspector",
            pg.input_value("#content") == "alpha text one",
            pg.input_value("#content"),
        )
        pg.wait_for_timeout(2000)
        srv.terminate()
        srv.wait(timeout=10)
        srv = start()
        pg2 = br.new_page(viewport={"width": 1300, "height": 900})
        open_(pg2)
        pg2.click("#workspace-realization")
        pg2.wait_for_timeout(300)
        titles = [t.split("\n")[0] for t in pg2.locator("button.node:visible").all_inner_texts()]
        check("autosave survives server restart and reopen", "Note A" in titles and "Note B" in titles, titles)
        pg2.locator("button.node", has_text="Note A").first.click()
        pg2.wait_for_timeout(300)
        check(
            "reopened note content intact", pg2.input_value("#content") == "alpha text one", pg2.input_value("#content")
        )
        first_canvas = pg2.url
        pg2.locator("summary:visible", has_text="More tools").first.click()
        pg2.wait_for_timeout(200)
        pg2.click("#new-canvas")
        pg2.wait_for_timeout(900)
        pg2.click("#workspace-realization")
        pg2.wait_for_timeout(300)
        pg2.click("#add-note")
        pg2.wait_for_timeout(300)
        pg2.fill("#title", "Second canvas note")
        pg2.wait_for_timeout(2000)
        pg3 = br.new_page()
        open_(pg3)
        pg3.click("#workspace-realization")
        pg3.wait_for_timeout(300)
        t3 = [t.split("\n")[0] for t in pg3.locator("button.node:visible").all_inner_texts()]
        check("root reopens the most recently edited canvas", "Second canvas note" in t3, t3)
        picker = pg3.locator("#canvas-picker option").count()
        check("earlier canvas still reachable from picker", picker >= 2, picker)
        pg3.close()
        pg2.click("#add-scene")
        pg2.wait_for_timeout(300)
        pg2.fill("#title", "Stair scene")
        pg2.click("#write")
        pg2.wait_for_timeout(500)
        pg2.fill("#scene-premise", "A disgraced archivist uncovers a buried city.")
        pg2.fill("#scene-intent", "The archivist finds steps below the reading room.")
        pg2.fill("#scene-text", "The steps were cold.")
        pg2.click("#generate-scene")
        pg2.wait_for_timeout(2500)
        gen = pg2.locator("#generation-status").inner_text()
        truthful = (
            "await" in gen.lower() or "coding agent" in gen.lower() or "host" in gen.lower() or ("fail" in gen.lower())
        ) and "complete" not in gen.lower()
        check("Quick Draft reports pending/failure truthfully, never success", truthful, gen[:160])
        pg2.wait_for_timeout(1500)
        check("scene text persisted", "The steps were cold." in item_text(canvas_docs()))
        url = pg2.url
        tabA = br.new_page()
        tabA.goto(url, wait_until="networkidle")
        tabA.wait_for_timeout(500)
        tabB = br.new_page()
        tabB.goto(url, wait_until="networkidle")
        tabB.wait_for_timeout(500)
        for t in (tabA, tabB):
            t.click("#workspace-realization")
            t.wait_for_timeout(200)
        tabA.locator("button.node", has_text="Second canvas note").first.click()
        tabA.fill("#content", "NEWER from tab A")
        tabA.wait_for_timeout(2500)
        tabB.locator("button.node", has_text="Second canvas note").first.click()
        tabB.fill("#content", "STALE from tab B")
        tabB.wait_for_timeout(2500)
        docs = item_text(canvas_docs())
        check(
            "stale tab does not overwrite newer content", "NEWER from tab A" in docs and "STALE from tab B" not in docs
        )
        check(
            "stale tab is told about the conflict",
            any(
                (
                    k in tabB.locator("#status").inner_text().lower()
                    for k in ("conflict", "changed", "newer", "fail", "retry", "reload")
                )
            ),
            tabB.locator("#status").inner_text()[:140],
        )
        for t in (tabA, tabB):
            t.close()
        pg2.reload(wait_until="networkidle")
        pg2.wait_for_timeout(500)
        pg2.click("#workspace-realization")
        pg2.wait_for_timeout(300)
        pg2.locator("button.node", has_text="Note A").first.click() if pg2.locator(
            "button.node", has_text="Note A"
        ).count() else None
        pg2.locator("button.node").first.click()
        pg2.fill("#content", "typed just before leaving")
        pg2.click("#legacy-home")
        pg2.wait_for_timeout(2500)
        check(
            "leaving to Previous Beginner UI saves first",
            "typed just before leaving" in item_text(canvas_docs()) and "beginner.html" in pg2.url,
            pg2.url,
        )
        pg4 = br.new_page()
        open_(pg4)
        pg4.click("#workspace-realization")
        pg4.wait_for_timeout(300)
        pg4.route(
            "**/commands/replace-working-document",
            lambda r: r.fulfill(status=500, body='{"error":"forced"}', content_type="application/json"),
        )
        pg4.locator("button.node").first.click()
        pg4.fill("#content", "unsaved during outage")
        pg4.wait_for_timeout(1500)
        pg4.click("#legacy-home")
        pg4.wait_for_timeout(1500)
        check("navigation refused while save is failing", "beginner.html" not in pg4.url, pg4.url)
        check("unsaved content still on screen", pg4.input_value("#content") == "unsaved during outage")
        pg4.close()
        pg5 = br.new_page()
        open_(pg5)
        pg5.click("#workspace-realization")
        pg5.wait_for_timeout(300)
        node = pg5.locator("button.node").first
        node.focus()
        b1 = node.bounding_box()
        pg5.keyboard.press("ArrowRight")
        pg5.keyboard.press("ArrowRight")
        pg5.wait_for_timeout(300)
        b2 = node.bounding_box()
        check("arrow keys move a focused node", b2["x"] > b1["x"], (b1["x"], b2["x"]))
        pg5.close()
        check("no page errors", not errs, errs[:3])
        br.close()
    after = canonical_snapshot()
    check(
        "no canonical project files created or changed outside the Studio working store",
        before == after,
        sorted(set(after) - set(before))[:5],
    )
    srv.terminate()
    srv.wait()
    print("SUMMARY:", sum((ok for _, ok in results)), "/", len(results), "passed")
    sys.exit(0 if all((ok for _, ok in results)) else 1)
finally:
    if srv is not None and srv.poll() is None:
        srv.terminate()
        srv.wait(timeout=10)
