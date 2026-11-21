"""Capture machine-generated evidence for the Atelier visual study from a served Studio.

Prerequisites (disposable project only):
    PYTHONPATH=src python scripts/seed_atelier_study.py --project <dir>
    PYTHONPATH=src python -m auteur.beginner.server --project <dir> --port 8793

Then:
    python scripts/qualification/atelier_study_capture.py --base http://127.0.0.1:8793 --out <dir> [--video]

It walks the author journeys of the refinement brief on both recorded specimens:

  A  the resting world (nothing selected);
  B  progressive discovery: select, reveal, deepen, in place;
  C  deep exploration: follow documented relationships, including after zooming in;
  D  focused analysis: examine one concept as a constellation, follow inside it, return;
  E  narrow screen, keyboard only, and the operating-system reduced-motion preference;

plus one run of research treatment C for continuity with the first study. It writes screenshots,
optional recordings and metrics.json: the study's own settle and label measures and invariant
checks (positions never move in the living atlas, the camera is kept, restoration is exact).
The browser is Chromium (headless by default; `--windowed` for real-compositor frame times);
these are measurements, not a human usability evaluation.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

TASKS = {"atelier-small": "genres|genre:literary_mystery", "atelier-dense": "genres|genre:genre-procedural"}
ACT = """async ([selector]) => {
  const root = document.getElementById('studio-atelier');
  const done = new Promise(r => root.addEventListener('atelier:settled', e => r(e.detail), {once: true}));
  const target = root.querySelector(selector);
  if (!target) return {error: 'missing ' + selector};
  target.click();
  return await Promise.race([done, new Promise(r => setTimeout(() => r({error: 'no settle'}), 8000))]);
}"""
KEY = """async ([key]) => {
  const root = document.getElementById('studio-atelier');
  const done = new Promise(r => root.addEventListener('atelier:settled', e => r(e.detail), {once: true}));
  window.__pressed = done; return true;
}"""
SNAPSHOT = "document.getElementById('studio-atelier').atelierStudy.snapshot()"
METRICS = "document.getElementById('studio-atelier').atelierStudy.metrics()"


def star(concept: str) -> str:
    return '.atl-star[data-id="' + concept.replace('"', '\\"') + '"]'


def drift(a: dict, b: dict) -> int:
    return max(abs(a[k]["x"] - b[k]["x"]) + abs(a[k]["y"] - b[k]["y"]) for k in a)


def same_camera(a: dict, b: dict) -> bool:
    return all(abs(a[k] - b[k]) < 0.01 for k in ("cx", "cy", "z"))


def open_study(page, base, canvas, pause=0.0, query=""):
    page.goto(f"{base}/studio.html?canvas={canvas}&atelier{query}", wait_until="networkidle")
    page.wait_for_selector("#studio-atelier .atl-star", state="attached", timeout=20000)
    page.evaluate("document.getElementById('studio-mode-atelier').scrollIntoView({block:'start'})")
    time.sleep(0.6 + pause)


def press(page, key):
    page.evaluate(KEY, [key])
    page.keyboard.press(key)
    return page.evaluate("Promise.race([window.__pressed, new Promise(r => setTimeout(() => r({error: 'no settle'}), 8000))])")


def journeys(page, base, canvas, out: Path | None, prefix: str, pause: float = 0.0) -> dict:
    """Journeys A to D on one specimen; every shot is the served study at the step it names."""
    stage = page.locator("#studio-atelier")

    def shot(name):
        if out:
            stage.screenshot(path=str(out / f"{prefix}-{name}.png"))

    def act(selector, name=None, wait=0.2):
        m = page.evaluate(ACT, [selector])
        time.sleep(wait + pause)
        if name:
            shot(name)
        return m

    record = {"canvas": canvas, "focus": TASKS[canvas], "steps": {}}
    open_study(page, base, canvas, pause)
    rest, rest_metrics = page.evaluate(SNAPSHOT), page.evaluate(METRICS)
    shot("A1-rest")
    record["steps"]["rest"] = rest_metrics
    # Journey B: progressive discovery, in place.
    page.evaluate("""([sel]) => { const r = document.getElementById('studio-atelier');
      window.__settled = new Promise(res => r.addEventListener('atelier:settled', e => res(e.detail), {once: true}));
      r.querySelector(sel).click(); }""", [star(TASKS[canvas])])
    time.sleep(0.33)
    shot("B1-revealing")
    record["steps"]["select"] = page.evaluate("window.__settled")
    time.sleep(0.2 + pause)
    shot("B2-revealed")
    selected = page.evaluate(SNAPSHOT)
    record["revealKeepsPositions"] = drift(selected["positions"], rest["positions"]) == 0
    record["revealKeepsZoom"] = abs(selected["camera"]["z"] - rest["camera"]["z"]) < 0.001
    record["steps"]["deeper"] = act(".atl-look [data-key=depth]", "B3-deeper")
    act(".atl-look [data-key=depth]")
    # Journey C: deep exploration across the atlas, then closer in.
    record["steps"]["follow-1"] = act(".atl-folio .atl-rel[data-other^='timeline']", "C1-follow")
    record["steps"]["follow-2"] = act(".atl-folio .atl-rel:not([data-other^='genres'])", "C2-follow")
    zoom_before = page.evaluate(SNAPSHOT)["camera"]["z"]
    act(".atl-zoom-btn")
    act(".atl-zoom-btn")
    record["steps"]["follow-3-zoomed"] = act(".atl-folio .atl-rel", "C3-zoomed-follow")
    explored = page.evaluate(SNAPSHOT)
    record["explorationKeepsPositions"] = drift(explored["positions"], rest["positions"]) == 0
    record["zoomNeverReducedAutomatically"] = explored["camera"]["z"] >= zoom_before * 1.5 - 0.001
    record["trail"] = explored["trail"]
    # Journey D: focused analysis from a fresh atlas, then exact restoration.
    open_study(page, base, canvas, pause)
    rest = page.evaluate(SNAPSHOT)
    act(star(TASKS[canvas]))
    atlas_view = page.evaluate(SNAPSHOT)
    record["steps"]["examine"] = act(".atl-look [data-key=look]", "D1-constellation")
    record["steps"]["examine-follow"] = act(".atl-folio .atl-rel", "D2-constellation-follow")
    page.evaluate("const d = document.querySelector('#studio-atelier .atl-source'); d.open = true; d.scrollIntoView({block: 'center'})")
    time.sleep(0.2 + pause)
    shot("D3-source")
    record["steps"]["leave"] = act(".atl-look [data-key=look]", "D4-back-in-atlas")
    back = page.evaluate(SNAPSHOT)
    record["leaveRestoresPositions"] = drift(back["positions"], rest["positions"]) == 0
    record["leaveKeepsZoom"] = abs(back["camera"]["z"] - atlas_view["camera"]["z"]) < 0.001
    record["steps"]["return"] = act(".atl-folio .atl-return", "D5-rest-again")
    after = page.evaluate(SNAPSHOT)
    record["returnPositionDrift"] = drift(after["positions"], rest["positions"])
    record["cameraRestored"] = same_camera(after["camera"], rest["camera"])
    return record


def narrow(page, base, canvas, out, prefix) -> dict:
    stage = page.locator("#studio-atelier")
    open_study(page, base, canvas)
    rest = page.evaluate(SNAPSHOT)
    stage.screenshot(path=str(out / f"{prefix}-E1-rest.png"))
    steps = {"rest": page.evaluate(METRICS)}
    for key, sel in (("select", star(TASKS[canvas])), ("examine", ".atl-look [data-key=look]"),
                     ("leave", ".atl-look [data-key=look]"), ("return", ".atl-folio .atl-return")):
        steps[key] = page.evaluate(ACT, [sel])
        time.sleep(0.25)
        stage.screenshot(path=str(out / f"{prefix}-E-{key}.png"))
    after = page.evaluate(SNAPSHOT)
    return {"canvas": canvas, "viewport": "narrow 390x844", "steps": steps,
            "returnPositionDrift": drift(after["positions"], rest["positions"]),
            "cameraRestored": same_camera(after["camera"], rest["camera"])}


def keyboard(page, base, canvas) -> dict:
    """Keyboard only: roving focus, arrows, Enter, ] deeper, E constellation, Escape twice."""
    open_study(page, base, canvas)
    rest = page.evaluate(SNAPSHOT)
    page.evaluate("document.querySelector('#studio-atelier .atl-star[tabindex=\"0\"]').focus()")
    start = page.evaluate("document.activeElement.dataset.id")
    page.keyboard.press("ArrowRight")
    time.sleep(0.5)
    target = page.evaluate("document.activeElement.dataset.id")
    steps = {"select": press(page, "Enter"), "deeper": press(page, "BracketRight"), "examine": press(page, "e"),
             "leave": press(page, "Escape"), "return": press(page, "Escape")}
    after = page.evaluate(SNAPSHOT)
    return {"canvas": canvas, "start": start, "arrowMovedTo": target,
            "modes": {k: (v or {}).get("mode") for k, v in steps.items()},
            "focusKeptOnConcept": page.evaluate("document.activeElement.dataset.id || null") == target,
            "returnPositionDrift": drift(after["positions"], rest["positions"]),
            "cameraRestored": same_camera(after["camera"], rest["camera"])}


def main() -> None:
    parser = argparse.ArgumentParser(description="Atelier study evidence capture")
    parser.add_argument("--base", default="http://127.0.0.1:8793")
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--video", action="store_true", help="also record the dense desktop and narrow journeys")
    parser.add_argument("--windowed", action="store_true",
                        help="use a visible Chromium window for real-compositor frame times")
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    manifest = {"desktop": [], "narrow": [], "keyboard": [], "reducedMotion": [], "researchC": []}
    errors = []
    with sync_playwright() as pw:
        launch = {"headless": not args.windowed}
        if args.windowed:
            launch["args"] = ["--window-size=1440,900"]
        browser = pw.chromium.launch(**launch)
        page = browser.new_page(viewport={"width": 1440, "height": 900})
        page.on("pageerror", lambda e: errors.append(str(e)))
        for canvas in TASKS:
            manifest["desktop"].append(journeys(page, args.base, canvas, args.out, f"desktop-{canvas.split('-')[1]}"))
        manifest["keyboard"].append(keyboard(page, args.base, "atelier-dense"))
        open_study(page, args.base, "atelier-dense", query="=C")
        research = page.evaluate(ACT, [star(TASKS["atelier-dense"])])
        page.locator("#studio-atelier").screenshot(path=str(args.out / "desktop-dense-research-C.png"))
        manifest["researchC"].append({"canvas": "atelier-dense", "select": research})
        page.close()
        small = browser.new_page(viewport={"width": 390, "height": 844})
        small.on("pageerror", lambda e: errors.append(str(e)))
        manifest["narrow"].append(narrow(small, args.base, "atelier-dense", args.out, "narrow-dense"))
        small.close()
        reduced = browser.new_context(viewport={"width": 1440, "height": 900}, reduced_motion="reduce").new_page()
        reduced.on("pageerror", lambda e: errors.append(str(e)))
        record = journeys(reduced, args.base, "atelier-dense", None, "reduced")
        record["viewport"] = "desktop, prefers-reduced-motion"
        manifest["reducedMotion"].append(record)
        if args.video:
            (args.out / "video").mkdir(exist_ok=True)
            for label, size in (("desktop", {"width": 1280, "height": 860}), ("narrow", {"width": 390, "height": 844})):
                context = browser.new_context(viewport=size, record_video_dir=str(args.out / "video"), record_video_size=size)
                vpage = context.new_page()
                if label == "desktop":
                    journeys(vpage, args.base, "atelier-dense", None, "video", pause=1.0)
                else:
                    narrow(vpage, args.base, "atelier-dense", args.out / "video", "video-narrow")
                name = vpage.video.path()
                context.close()
                Path(name).replace(args.out / "video" / f"dense-{label}.webm")
        browser.close()
    repo = Path(__file__).resolve().parents[2]
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo, capture_output=True, text=True).stdout.strip()
    dirty = bool(subprocess.run(["git", "status", "--porcelain", "--", "src"], cwd=repo,
                                capture_output=True, text=True).stdout.strip())
    manifest = {"generator": "scripts/qualification/atelier_study_capture.py", "sourceHead": head,
                "sourceTreeDirty": dirty,
                "browser": "windowed Chromium (Playwright)" if args.windowed else "headless Chromium (Playwright)",
                "note": "Machine measurements of the served Studio; not a human usability evaluation.",
                "pageErrors": errors, **manifest}
    (args.out / "metrics.json").write_text(json.dumps(manifest, indent=1), encoding="utf-8")
    print(f"{len(errors)} page errors -> {args.out}")


if __name__ == "__main__":
    main()
