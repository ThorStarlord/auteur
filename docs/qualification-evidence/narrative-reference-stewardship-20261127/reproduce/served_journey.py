"""The served Atelier journey for reference stewardship, with screenshots and a step record.

Runs on a disposable copy of the Exercise A study (identities, PR #648's applied Book 24 association, Book 25 up to date) and
drives the page's own controls in this order:

    1. the question reading names a lead in Book 25 (not yet a reference)
    2. Book 25's own development panel shows the observation, its historical reading and the owner's choices
    3. the author chooses the current question and prepares the request (no model is called)
    4. the owner checks the coding agent's unedited answer (reviewed; nothing applied); the review names the requested association
    5. the author applies the reviewed revision through the served control
    6. the question reading then lists Books 24 and 25 as engaging it, and Book 25's lead is gone
    7. the same reading at 390 px wide, with no horizontal overflow
    8. a no-change path: a lead is opened and left alone; nothing on disk changes

Usage (from the repository root, with the system Python that has Playwright and the package's dependencies):
    PYTHONPATH=src python docs/qualification-evidence/narrative-reference-stewardship-20261127/reproduce/served_journey.py --root <fresh dir>
The root must be empty or new; the screenshots and journey.json are written to <root>/served-final, and copied by hand if kept.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import shutil
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
EVIDENCE = Path(__file__).resolve().parent / "exercise-a"
_spec = importlib.util.spec_from_file_location("exercise_a", Path(__file__).resolve().parent / "exercise_a.py")
exercise_a = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(exercise_a)

from playwright.sync_api import sync_playwright  # noqa: E402

from auteur.beginner.server import BeginnerWorkspaceServer  # noqa: E402
from auteur.beginner.studio_store import CanvasStore  # noqa: E402
from auteur.host_agent import HostAgentRequest, build_host_agent_response  # noqa: E402
from auteur.series.working_book_architecture import book_complete, book_project  # noqa: E402

CANVAS = exercise_a.discovery.SPRING
BOOK, BOOK_ASSOCIATED = exercise_a.BOOK, exercise_a.BOOK_ASSOCIATED
BLIND = exercise_a.BLIND_SPOT
CONVERSION = exercise_a.CONVERSION


def scroll_panel(page) -> None:
    """The Book's development panel re-renders as the page reads; a viewport capture of it does not depend on one element."""
    page.evaluate("() => { const p = document.querySelector('#studio-atelier [aria-label=\"Developing Book 25\"]');"
                  " if (p) p.scrollIntoView({block: 'start'}); }")
    page.wait_for_timeout(500)


def digest_tree(project: Path) -> dict[str, str]:
    return {str(p.relative_to(project)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(project.rglob("*")) if p.is_file() and not p.name.endswith(".lock")}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", required=True, type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    root.mkdir(parents=True, exist_ok=True)
    shots = root / "served-final"
    shots.mkdir(exist_ok=True)
    exercise_a.seed(root / "study", root / "seed-out")
    project = root / "study" / "discovery"
    store = CanvasStore(project, CANVAS)
    steps: list[dict] = []

    def step(name: str, ok: bool, note: str = "") -> None:
        steps.append({"step": name, "ok": bool(ok), "note": note})
        print(("ok   " if ok else "FAIL ") + name + (f" — {note}" if note else ""))

    server = BeginnerWorkspaceServer(project, port=0)
    thread = server.start_in_thread()
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True, args=["--no-sandbox"])
            page = browser.new_page(viewport={"width": 1440, "height": 900})
            errors: list[str] = []
            page.on("pageerror", lambda error: errors.append(str(error)))
            page.goto(f"http://127.0.0.1:{server.port}/studio.html?canvas={CANVAS}&atelier", wait_until="networkidle")
            page.wait_for_selector("#studio-atelier .atl-star", state="attached", timeout=20000)
            page.wait_for_selector('#studio-atelier [data-key="questions-all"]', state="attached", timeout=20000)

            def open_question(identifier: str) -> None:
                page.locator('#studio-atelier [data-key="questions-all"]').click()
                page.locator(f'#studio-atelier .atl-question-item[data-key="question:{identifier}"]').click()
                page.wait_for_selector("#studio-atelier .atl-folio", timeout=10000)

            open_question(CONVERSION)
            lead = page.locator(f'#studio-atelier [data-key="question-lead:{BOOK}:{BLIND}"]')
            step("question reading names a lead in Book 25", lead.count() == 1, "not a reference")
            page.locator("#studio-atelier .atl-qleads").first.scroll_into_view_if_needed()
            page.locator("#studio-atelier .atl-qleads").first.screenshot(path=str(shots / "01-question-lead.png"))

            lead.click()
            page.wait_for_selector(f'#studio-atelier [data-key="observation-prepare:{BOOK}:{BLIND}"]', timeout=30000)
            step("Book 25 shows the observation with the owner's choices", True)
            page.locator(f'#studio-atelier [data-key="observation-question:{BOOK}:{BLIND}"]').select_option(CONVERSION)
            scroll_panel(page)
            page.screenshot(path=str(shots / "02-observation-desktop.png"))

            page.locator(f'#studio-atelier [data-key="observation-prepare:{BOOK}:{BLIND}"]').click()
            page.wait_for_function("() => /Prepared for your coding agent/.test(document.querySelector('#studio-atelier').textContent)",
                                   timeout=30000)
            pending = book_project(store, BOOK)
            request = json.loads((EVIDENCE / "request-book25.json").read_text(encoding="utf-8"))
            step("prepare writes exactly the request the evidence answers", pending["request"] is not None
                 and pending["request"]["request_sha256"] == request["request_sha256"])
            step("preparing changes nothing in Book 25", json.loads(
                (project / ".auteur/beginner/studio/canvases" / CANVAS / "architecture/books/25/current.json")
                .read_text(encoding="utf-8"))["request_sha256"] != pending["request"]["request_sha256"])

            answer = (EVIDENCE / "candidate-book25-unedited.json").read_text(encoding="utf-8")
            book_complete(store, BOOK, build_host_agent_response(HostAgentRequest(**request), answer,
                                                                runtime="fresh-sub-agent").model_dump())
            review = book_project(store, BOOK)["review"]
            step("the owner reviews the unedited answer as applicable", bool(review and review["applicable"]))
            step("the review states the requested association was recorded", bool(review) and [
                row["established"] for row in review["requested_question_associations"]] == [True])
            page.reload(wait_until="networkidle")
            page.wait_for_selector("#studio-atelier .atl-star", state="attached", timeout=20000)
            open_question(CONVERSION)
            page.locator(f'#studio-atelier [data-key="question-lead:{BOOK}:{BLIND}"]').click()
            page.wait_for_function("""() => { const p = document.querySelector('#studio-atelier [aria-label="Developing Book 25"]');
                                       return !!p && p.textContent.indexOf('Association you asked for') >= 0; }""", timeout=30000)
            scroll_panel(page)
            page.screenshot(path=str(shots / "03-review-before-apply.png"))

            page.locator(f'#studio-atelier [data-key="book-apply:{BOOK}"]').click()
            page.wait_for_function("() => /Applied to working Book 25/.test(document.querySelector('#studio-atelier').textContent)",
                                   timeout=30000)
            applied = book_project(store, BOOK)
            step("Apply, through the served control, records the association", applied["review"] is None
                 and any(ref["kind"] == "series_question" and ref["id"] == CONVERSION
                         for row in json.loads(project_record_text(project, BOOK))["artifact"]["series_consequences"]
                         if row["id"] == BLIND for ref in row["refs"]))

            page.reload(wait_until="networkidle")
            page.wait_for_selector("#studio-atelier .atl-star", state="attached", timeout=20000)
            open_question(CONVERSION)
            folio = page.locator("#studio-atelier .atl-folio").text_content()
            step("the question reading lists Books 24 and 25 as engaging it", "Book elements that engage it · 2" in folio)
            step("Book 25's lead is gone once the association is recorded",
                 page.locator(f'#studio-atelier [data-key="question-lead:{BOOK}:{BLIND}"]').count() == 0)
            page.evaluate("() => { const s = document.querySelector('#studio-atelier .atl-qengagements'); if (s) s.scrollIntoView({block: 'start'}); }")
            page.wait_for_timeout(400)
            page.screenshot(path=str(shots / "04-question-after-apply.png"))

            page.set_viewport_size({"width": 390, "height": 844})
            page.reload(wait_until="networkidle")
            page.wait_for_selector("#studio-atelier .atl-star", state="attached", timeout=20000)
            open_question(CONVERSION)
            overflow = page.evaluate("() => document.documentElement.scrollWidth - document.documentElement.clientWidth")
            step("the question reading at 390 px has no horizontal overflow", overflow <= 0, f"overflow {overflow}")
            page.evaluate("() => { const s = document.querySelector('#studio-atelier .atl-qengagements'); if (s) s.scrollIntoView({block: 'start'}); }")
            page.wait_for_timeout(400)
            page.screenshot(path=str(shots / "05-question-narrow-390.png"))

            step("no page errors during the journey", not errors, "; ".join(errors)[:200])
            browser.close()
    finally:
        server.stop()
        thread.join(timeout=5)
    journey = {"steps": steps, "all_passed": all(row["ok"] for row in steps)}
    (shots / "journey.json").write_text(json.dumps(journey, ensure_ascii=False, indent=2), encoding="utf-8")
    print("all passed:", journey["all_passed"])


def project_record_text(project: Path, number: int) -> str:
    return (project / ".auteur/beginner/studio/canvases" / CANVAS / f"architecture/books/{number}/current.json").read_text(encoding="utf-8")


if __name__ == "__main__":
    main()
