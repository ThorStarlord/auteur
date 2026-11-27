"""The served journey for question-linked narrative inheritance, with final-version screenshots.

Runs on a fresh disposable copy of the Exercise A study in which the Mill Compact association is pending for review. The
journey uses the page's own controls, as an author would: the question reading (pending, not yet an engagement), the Book
review (the association named before Apply), the explicit Apply, the question reading after Apply, and the narrow-screen
presentation. Nothing calls a provider and nothing is written to the repository.

Usage (from the worktree root, with PYTHONPATH=src):
    python docs/qualification-evidence/question-linked-narrative-inheritance-20261127/reproduce/served_journey.py \
        --study <copy of Exercise A discovery study> --out docs/qualification-evidence/question-linked-narrative-inheritance-20261127/served-final
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

from auteur.beginner.server import BeginnerWorkspaceServer
from auteur.beginner.studio_store import CanvasStore
from auteur.host_agent import HostAgentRequest, build_host_agent_response
from auteur.series.working_book_architecture import _book_root, _read, book_complete, book_prepare, book_project

REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO / "scripts"))
sys.path.insert(0, str(REPO / "tests"))
import seed_book_discovery_study as discovery  # noqa: E402
from test_persistent_narrative_questions import identity_for  # noqa: E402

CANVAS = discovery.SPRING
COMPACT = identity_for(6)
CONVERSION = identity_for(5)


def prepare_pending(project: Path) -> None:
    """Book 24 has the Mill Compact association waiting for review. Written through the owner, as Exercise A does."""
    store = CanvasStore(project, CANVAS)
    prepared = book_prepare(store, 24, instruction="Check which open questions the Mill Compact agent engages.",
                            targets=("agent-mill-compact",))
    artifact = json.loads(json.dumps(_read(_book_root(store, 24) / "current.json")["artifact"]))
    agent = next(item for item in artifact["agents"] if item["id"] == "agent-mill-compact")
    if agent.get("provenance") is not None:
        agent.pop("provenance")
        agent["attribution"], agent["epistemic_status"] = "agent_proposed", "asserted"
    agent.setdefault("refs", []).append({"kind": "series_question", "id": COMPACT})
    book_complete(store, 24, build_host_agent_response(HostAgentRequest(**prepared["request"]), json.dumps(artifact),
                                                       runtime="served-journey").model_dump())
    assert book_project(store, 24)["status"] == "review_ready"


def back_to_all_questions(page, atelier: str) -> None:
    """From an open question, the folio's own control returns to the list of all open questions."""
    page.locator(f'{atelier} button', has_text="Back to all open questions").first.click()
    page.locator(f'{atelier} .atl-question-item').first.wait_for(state="visible", timeout=10000)


def wait_for_text(page, selector: str, text: str, timeout: int = 30000) -> None:
    page.wait_for_function(
        """([selector, text]) => { const n = document.querySelector(selector);
                                    return !!n && n.textContent.indexOf(text) >= 0; }""",
        arg=[selector, text], timeout=timeout)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--study", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--work", required=True, type=Path, help="a scratch directory for the disposable copy")
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    project = args.work / "discovery"
    if project.exists():
        shutil.rmtree(project)
    args.work.mkdir(parents=True, exist_ok=True)
    shutil.copytree(args.study, project)
    prepare_pending(project)
    steps: list[dict] = []
    folio = "#studio-atelier .atl-folio"
    atelier = "#studio-atelier"

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True, args=["--no-sandbox"])
        server = BeginnerWorkspaceServer(project, port=0)
        thread = server.start_in_thread()
        url = f"http://127.0.0.1:{server.port}/studio.html?canvas={CANVAS}&atelier"
        errors: list[str] = []
        try:
            def open_atelier(width: int = 1440, height: int = 900):
                page = browser.new_page(viewport={"width": width, "height": height})
                page.on("pageerror", lambda error: errors.append(str(error)))
                page.goto(url, wait_until="networkidle")
                page.wait_for_selector(f"{atelier} .atl-star", state="attached", timeout=20000)
                page.locator(f'{atelier} [data-key="questions-all"]').wait_for(state="visible", timeout=20000)
                return page

            # 1. The Mill Compact question, while its association waits for review.
            page = open_atelier()
            page.locator(f'{atelier} [data-key="questions-all"]').click()
            page.locator(f'{atelier} .atl-question-item[data-key="question:{COMPACT}"]').click()
            page.wait_for_selector(folio, timeout=10000)
            steps.append({"step": "1 Mill Compact question, association pending",
                          "engagements_shown": "Book elements that engage it" in page.locator(folio).text_content()})
            page.locator(folio).screenshot(path=str(args.out / "01-compact-question-pending-desktop-1440.png"))
            page.close()

            # 2. The conversion question, its engagement, the route to Book 24, and the review before Apply.
            page = open_atelier()
            page.locator(f'{atelier} [data-key="questions-all"]').click()
            page.locator(f'{atelier} .atl-question-item[data-key="question:{CONVERSION}"]').click()
            page.wait_for_selector(folio, timeout=10000)
            page.locator(f'{atelier} [data-key="question-engagement:24:cons-conversion-blind-spot"]').click()
            wait_for_text(page, f'{atelier} [aria-label="Developing Book 24"]', "Question associations in this revision")
            developing = page.locator(f'{atelier} [aria-label="Developing Book 24"]')
            developing.scroll_into_view_if_needed()
            steps.append({"step": "2 Book 24 review before Apply",
                          "review_names_association": "now engages" in developing.text_content()})
            kicker = page.get_by_text("Question associations in this revision", exact=False).first
            kicker.wait_for(state="visible", timeout=10000)
            kicker.scroll_into_view_if_needed()
            page.wait_for_timeout(800)
            page.screenshot(path=str(args.out / "02-book24-review-before-apply-desktop-1440.png"))

            # 3. The explicit Apply, through the review's own button.
            page.locator(f'{atelier} [data-key="book-apply:24"]').click()
            wait_for_text(page, f'{atelier} [aria-label="Developing Book 24"]', "Applied to working Book 24")
            steps.append({"step": "3 explicit Apply of the reviewed revision", "result": "applied"})
            page.close()

            # 4. The Mill Compact question after Apply: the association reads as a Book engagement.
            page = open_atelier()
            page.locator(f'{atelier} [data-key="questions-all"]').click()
            page.locator(f'{atelier} .atl-question-item[data-key="question:{COMPACT}"]').click()
            page.wait_for_selector(folio, timeout=10000)
            text = page.locator(folio).text_content()
            steps.append({"step": "4 Mill Compact question after Apply",
                          "engagements_shown": "Book elements that engage it · 1" in text,
                          "limit_line_shown": "does not say the element answers, settles, develops or inherits" in text})
            engagement = page.locator(f"{atelier} .atl-qengagements")
            engagement.wait_for(state="visible", timeout=10000)
            page.wait_for_timeout(800)  # the reading settles after its first render
            engagement.screenshot(path=str(args.out / "03-compact-question-after-apply-desktop-1440.png"))
            page.close()

            # 5. The same question on a narrow screen, with no horizontal overflow.
            page = open_atelier(390, 844)
            page.locator(f'{atelier} [data-key="questions-all"]').click()
            page.locator(f'{atelier} .atl-question-item[data-key="question:{COMPACT}"]').click()
            page.wait_for_selector(folio, timeout=10000)
            overflow = page.evaluate("() => document.documentElement.scrollWidth - document.documentElement.clientWidth")
            steps.append({"step": "5 narrow screen 390 px", "horizontal_overflow_px": overflow})
            narrow = page.locator(f"{atelier} .atl-qengagements")
            narrow.wait_for(state="visible", timeout=10000)
            page.wait_for_timeout(800)
            narrow.screenshot(path=str(args.out / "04-compact-question-after-apply-narrow-390.png"))
            page.close()
            steps.append({"step": "page errors", "errors": list(errors)})
        finally:
            server.stop()
            thread.join(timeout=5)
            browser.close()
    (args.out / "journey.json").write_text(json.dumps(steps, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(steps, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
