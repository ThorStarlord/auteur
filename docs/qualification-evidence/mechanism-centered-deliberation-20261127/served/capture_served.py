"""Capture the served consequence panel for a completed mechanism-centred analysis, at desktop and phone widths.

Usage: served_shots.py <study discovery dir> <out dir>
The study is copied first, so the captured canvas is never the one the exercise wrote to.
"""
import contextlib
import json
import shutil
import sys
from pathlib import Path

REPO = Path("H:/GithubRepositories/auteur/.worktrees/mechanism-centered")
sys.path.insert(0, str(REPO / "src"))
sys.path.insert(0, str(REPO / "tests"))

from playwright.sync_api import sync_playwright  # noqa: E402

from auteur.beginner.server import BeginnerWorkspaceServer  # noqa: E402

CANVAS = "spring-ledger"


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
    source, out = Path(sys.argv[1]), Path(sys.argv[2])
    out.mkdir(parents=True, exist_ok=True)
    import tempfile
    work = Path(tempfile.mkdtemp()) / "served-copy"
    if work.exists():
        shutil.rmtree(work)
    shutil.copytree(source, work)
    record = {}
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True, args=["--no-sandbox"])
        for name, width, height in (("desktop-1440", 1440, 900), ("phone-390", 390, 844)):
            with served(browser, work, width, height) as (page, errors):
                page.wait_for_selector("#architecture-consequence:not([hidden])", timeout=30000)
                page.wait_for_selector("#architecture-consequence .consequence-concern", timeout=30000)
                section = page.locator("#architecture-consequence")
                section.evaluate("node => node.scrollIntoView({block: 'start'})")
                page.screenshot(path=str(out / f"consequence-{name}.png"))
                overflow = page.evaluate("() => document.documentElement.scrollWidth - document.documentElement.clientWidth")
                text = section.inner_text()
                record[name] = {
                    "page_overflow_px": overflow,
                    "has_connections_section": "How the mechanisms relate" in text,
                    "has_mechanism_only_alternative": "no question needed" in text,
                    "console_page_errors": errors,
                }
        browser.close()
    (out / "served-record.json").write_text(json.dumps(record, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(record, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
