"""Drive the served Investigate control on an accepted fresh-agent analysis, then capture the owner's inquiry result.

Usage (system Python 3.14, which has Playwright and its browsers):
    capture_investigation.py prepare <study discovery dir> <out dir> <new working dir>
        Copies the study to the new working directory, opens the served page on that copy, presses Investigate on the first
        alternative of the accepted analysis, and captures the creative panel. The press prepares an inquiry request for a
        fresh agent; nothing is applied.
    capture_investigation.py result <unused> <out dir> <working dir>
        Opens the served page on the working directory after its inquiry has been answered and completed through the owner,
        and captures the creative panel with the owner's result.

The exercise record is never the canvas that is driven: only the copy is.
"""
import contextlib
import json
import shutil
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO / "src"))

from playwright.sync_api import sync_playwright  # noqa: E402

from auteur.beginner.server import BeginnerWorkspaceServer  # noqa: E402

CANVAS = "spring-ledger"
# The owner's hypothesis titles for the served inquiry answer (completed through the owner), checked on the page.
RESULT_TITLES = ["Duty as a late settlement clause", "Every-season reading reaches back to Book 6"]


@contextlib.contextmanager
def served(browser, project: Path, width: int, height: int):
    server = BeginnerWorkspaceServer(project, port=0)
    thread = server.start_in_thread()
    page = browser.new_page(viewport={"width": width, "height": height})
    errors = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    try:
        page.goto(f"http://127.0.0.1:{server.port}/studio.html?canvas={CANVAS}", wait_until="networkidle")
        page.wait_for_selector("#architecture-status", state="attached", timeout=30000)
        yield page, errors
    finally:
        page.close()
        server.stop()
        thread.join(timeout=5)


def main() -> None:
    # mode prepare: copy the source study to a new working directory, then drive it.
    # mode result: drive the working directory that prepare left behind, after its inquiry was completed through the owner.
    mode, source_or_work, out, work = sys.argv[1], Path(sys.argv[2]), Path(sys.argv[3]), Path(sys.argv[4])
    out.mkdir(parents=True, exist_ok=True)
    if mode == "prepare":
        if work.exists():
            raise SystemExit("the working copy must not exist yet")
        shutil.copytree(source_or_work, work)
    elif not work.exists():
        raise SystemExit("the working copy from the prepare run is missing")
    record = {"mode": mode, "working_copy": str(work)}
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True, args=["--no-sandbox"])
        for name, width, height in (("desktop-1440", 1440, 900), ("phone-390", 390, 844)):
            with served(browser, work, width, height) as (page, errors):
                page.wait_for_selector("#architecture-consequence .consequence-concern", timeout=30000)
                if mode == "prepare":
                    page.locator("#architecture-consequence .consequence-investigate").first.click()
                    page.wait_for_function(
                        "document.querySelector('#architecture-consequence .consequence-notice') && "
                        "document.querySelector('#architecture-consequence .consequence-notice')"
                        ".textContent.includes('Investigation prepared')", timeout=20000)
                panel = page.locator("#architecture-creative-agent-panel")
                origin = panel.locator(".creative-origin")
                record_origin = origin.first.text_content() if origin.count() else ""
                notice = page.locator("#architecture-consequence .consequence-notice")
                if mode == "result":
                    # The owner's result is in the creative panel, inside the page's own disclosure for the coding agent.
                    page.locator("summary", has_text="Explore graph with coding agent").first.click()
                    page.wait_for_selector("#architecture-creative-agent-panel", timeout=15000)
                target = "#architecture-creative-agent-panel" if mode == "result" else "#architecture-consequence"
                page.locator(target).evaluate("node => node.scrollIntoView({block: 'start'})")
                page.screenshot(path=str(out / f"{mode}-{name}.png"))
                page_text = page.locator("body").inner_text()
                record[name] = {
                    "result_titles_visible": [title for title in RESULT_TITLES if title in page_text],
                    "notice": notice.first.text_content() if notice.count() else "",
                    "creative_origin": record_origin,
                    "page_overflow_px": page.evaluate(
                        "() => document.documentElement.scrollWidth - document.documentElement.clientWidth"),
                    "console_page_errors": errors,
                }
        browser.close()
    (out / f"{mode}-record.json").write_text(json.dumps(record, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(record, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
