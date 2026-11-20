"""Capture machine-generated evidence for the Atelier visual study from a served Studio.

Prerequisites (disposable project only):
    PYTHONPATH=src python scripts/seed_atelier_study.py --project <dir>
    PYTHONPATH=src python -m auteur.beginner.server --project <dir> --port 8793

Then:
    python scripts/qualification/atelier_study_capture.py --base http://127.0.0.1:8793 --out <dir> [--video]

For every specimen and treatment it walks the same author task: the resting atlas, selecting a
concept (a frame mid-unfolding and the settled constellation), revealing deeper connections,
following one documented relationship, opening its source record and returning to the atlas.
It writes screenshots, optional recordings and metrics.json (the study's own settle measures,
composition measures and the position drift left after returning). The browser is a real
headless Chromium; these are measurements, not a human usability evaluation.
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

TASKS = {
    # canvas: (focus concept for the task, label)
    "atelier-small": "genres|genre:literary_mystery",
    "atelier-dense": "genres|genre:genre-procedural",
}
ACT = """async ([selector]) => {
  const root = document.getElementById('studio-atelier');
  const done = new Promise(r => root.addEventListener('atelier:settled', e => r(e.detail), {once: true}));
  const target = root.querySelector(selector);
  if (!target) return {error: 'missing ' + selector};
  target.click();
  return await Promise.race([done, new Promise(r => setTimeout(() => r({error: 'no settle'}), 8000))]);
}"""
SNAPSHOT = "document.getElementById('studio-atelier').atelierStudy.snapshot()"


def star(concept: str) -> str:
    return '.atl-star[data-id="' + concept.replace('"', '\\"') + '"]'


def walk(page, base, canvas, treatment, out: Path | None, prefix: str, pause: float = 0.0) -> dict:
    page.goto(f"{base}/studio.html?canvas={canvas}&atelier={treatment}", wait_until="networkidle")
    page.wait_for_selector("#studio-atelier .atl-star", timeout=20000)
    page.evaluate("document.getElementById('studio-mode-atelier').scrollIntoView({block:'start'})")
    time.sleep(0.6 + pause)
    stage = page.locator("#studio-atelier")

    def shot(name):
        if out:
            stage.screenshot(path=str(out / f"{prefix}-{name}.png"))

    shot("1-atlas")
    rest = page.evaluate(SNAPSHOT)
    steps = []
    page.evaluate("""([sel]) => { const r = document.getElementById('studio-atelier');
      window.__atelierSettled = new Promise(res => r.addEventListener('atelier:settled', e => res(e.detail), {once: true}));
      r.querySelector(sel).click(); }""", [star(TASKS[canvas])])
    time.sleep(0.32)
    shot("2-unfolding")
    steps.append({"step": "select", "metrics": page.evaluate("window.__atelierSettled")})
    time.sleep(0.2 + pause)
    shot("3-constellation")
    steps.append({"step": "deeper", "metrics": page.evaluate(ACT, [".atl-depth .atl-action-primary"])})
    time.sleep(0.2 + pause)
    shot("4-deeper")
    page.evaluate(ACT, [".atl-depth .atl-action-primary"])
    steps.append({"step": "follow", "metrics": page.evaluate(ACT, [".atl-folio .atl-rel"])})
    time.sleep(0.2 + pause)
    shot("5-follow")
    page.evaluate("const d = document.querySelector('#studio-atelier .atl-source'); d.open = true; d.scrollIntoView({block: 'center'})")
    time.sleep(0.2 + pause)
    shot("6-source")
    steps.append({"step": "return", "metrics": page.evaluate(ACT, [".atl-folio .atl-return"])})
    time.sleep(0.2 + pause)
    shot("7-returned")
    after = page.evaluate(SNAPSHOT)
    drift = max(abs(after["positions"][k]["x"] - rest["positions"][k]["x"]) +
                abs(after["positions"][k]["y"] - rest["positions"][k]["y"]) for k in rest["positions"])
    return {"canvas": canvas, "treatment": treatment, "focus": TASKS[canvas], "steps": steps,
            "returnPositionDrift": drift, "cameraRestored": after["camera"] == rest["camera"],
            "atlas": {"concepts": len(rest["concepts"])}}


def main() -> None:
    parser = argparse.ArgumentParser(description="Atelier study evidence capture")
    parser.add_argument("--base", default="http://127.0.0.1:8793")
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--video", action="store_true", help="also record one walk per treatment (dense)")
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    runs, errors = [], []
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        for width, height, label in ((1440, 900, "desktop"), (390, 844, "narrow")):
            page = browser.new_page(viewport={"width": width, "height": height})
            page.on("pageerror", lambda e: errors.append(str(e)))
            for canvas in TASKS:
                for treatment in "ABC":
                    if label == "narrow" and treatment == "A" and canvas == "atelier-small":
                        continue
                    prefix = f"{label}-{canvas.split('-')[1]}-{treatment}"
                    run = walk(page, args.base, canvas, treatment, args.out, prefix)
                    run["viewport"] = label
                    runs.append(run)
            page.close()
        reduced = browser.new_context(viewport={"width": 1440, "height": 900}, reduced_motion="reduce").new_page()
        run = walk(reduced, args.base, "atelier-dense", "C", None, "reduced")
        run["viewport"] = "desktop, prefers-reduced-motion"
        runs.append(run)
        if args.video:
            for treatment in "ABC":
                context = browser.new_context(viewport={"width": 1280, "height": 860},
                                              record_video_dir=str(args.out / "video"),
                                              record_video_size={"width": 1280, "height": 860})
                page = context.new_page()
                walk(page, args.base, "atelier-dense", treatment, None, "video", pause=1.1)
                name = page.video.path()
                context.close()
                Path(name).rename(args.out / "video" / f"dense-{treatment}.webm")
        browser.close()
    manifest = {"generator": "scripts/qualification/atelier_study_capture.py", "browser": "headless Chromium (Playwright)",
                "note": "Machine measurements of the served Studio; not a human usability evaluation.",
                "pageErrors": errors, "runs": runs}
    (args.out / "metrics.json").write_text(json.dumps(manifest, indent=1), encoding="utf-8")
    print(f"{len(runs)} runs, {len(errors)} page errors -> {args.out}")


if __name__ == "__main__":
    main()
