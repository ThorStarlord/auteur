"""Drive the served "Reconsider this claim" control on an accepted analysis, and capture what the author sees.

Usage (system Python 3.14, which has Playwright and its browsers):
    capture_reconsideration.py --study <discovery dir of an accepted analysis> --out <dir> \
        --key reach:null --instruction-file <file> [--criticism-file <file>] \
        --answer-file <authentic unedited answer> --expect-sha <recorded request sha256> --label <name>

The study is copied to a temporary directory first; the source is never driven. The page prepares the reconsideration request
itself, from the author's text and the claim the control sits under. The request fingerprint the page produces is compared with
the recorded one: when they are equal, the authentic accepted answer is the answer to exactly that request, and it is pasted
as the coding agent's response. Nothing is applied.
"""
import argparse
import contextlib
import json
import shutil
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO / "src"))
sys.path.insert(0, str(REPO / "scripts"))

from playwright.sync_api import sync_playwright  # noqa: E402

from auteur.beginner.server import BeginnerWorkspaceServer  # noqa: E402
import consequence_exercise as ce  # noqa: E402

CANVAS = "spring-ledger"
RUNTIME = "fresh-subagent-reconsideration-exercise"


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
    parser = argparse.ArgumentParser()
    parser.add_argument("--study", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--key", required=True, help="claim key the control sits under, e.g. reach:null or connection:2")
    parser.add_argument("--instruction-file", required=True, type=Path)
    parser.add_argument("--criticism-file", type=Path, default=None)
    parser.add_argument("--answer-file", required=True, type=Path)
    parser.add_argument("--expect-sha", required=True)
    parser.add_argument("--label", required=True)
    args = parser.parse_args()

    args.out.mkdir(parents=True, exist_ok=True)
    work = Path(tempfile.mkdtemp(prefix="served-reconsider-")) / "discovery"
    shutil.copytree(args.study, work)
    instruction = args.instruction_file.read_text(encoding="utf-8").strip()
    criticism = args.criticism_file.read_text(encoding="utf-8") if args.criticism_file else ""
    answer_text = args.answer_file.read_text(encoding="utf-8")
    key = args.key
    record = {"label": args.label, "claim_key": key, "expected_request_sha256": args.expect_sha}

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True, args=["--no-sandbox"])
        for name, width, height in (("desktop-1440", 1440, 900), ("phone-390", 390, 844)):
            with served(browser, work, width, height) as (page, errors):
                page.wait_for_selector("#architecture-consequence .consequence-concern", timeout=30000)
                slot = page.locator(f'details[data-key="reconsider:{key}"]')
                slot.locator("> summary").click()
                if name == "desktop-1440":
                    # The author asks, the page prepares the request, and the recorded answer is pasted for that exact request.
                    page.locator(f'textarea[data-key="reconsider-question:{key}"]').fill(instruction)
                    if criticism.strip():
                        page.locator(f'textarea[data-key="reconsider-criticism:{key}"]').fill(criticism.strip())
                    page.locator(f'button[data-key="reconsider-prepare:{key}"]').click()
                    page.wait_for_selector("textarea.consequence-reconsider-request", timeout=20000)
                    request = json.loads(page.locator("textarea.consequence-reconsider-request").input_value())
                    record["page_request_sha256"] = request["request_sha256"]
                    record["page_request_equals_recorded"] = request["request_sha256"] == args.expect_sha
                    if request["request_sha256"] != args.expect_sha:
                        raise SystemExit("the page's request is not the recorded request; the answer is not pasted")
                    response = ce.envelope(request, answer_text, RUNTIME)
                    page.locator("textarea.consequence-reconsider-response").fill(json.dumps(response))
                    page.locator(f'button[data-key="reconsider-submit:{key}"]').click()
                page.wait_for_selector("article.consequence-reconsideration[data-disposition]:not([data-disposition='awaiting'])",
                                       timeout=30000)
                card = page.locator("article.consequence-reconsideration:not([data-disposition='awaiting'])").first
                card.scroll_into_view_if_needed()
                slot.scroll_into_view_if_needed()
                page.screenshot(path=str(args.out / f"{args.label}-{name}.png"), full_page=False)
                text = card.inner_text()
                record[name] = {
                    "disposition": card.get_attribute("data-disposition"),
                    "card_text_has_judgment": "Judgment:" in text,
                    "card_text_has_advisory": "Advisory." in text,
                    "recovered_evidence_listed": "Evidence this reconsideration examined" in page.locator(
                        "article.consequence-reconsideration").first.inner_text(),
                    "page_overflow_px": page.evaluate(
                        "() => document.documentElement.scrollWidth - document.documentElement.clientWidth"),
                    "console_page_errors": errors,
                }
        browser.close()
    (args.out / f"{args.label}-record.json").write_text(json.dumps(record, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(record, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
