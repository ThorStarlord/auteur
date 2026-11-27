"""Drive the served long-horizon synthesis on an accepted study and capture what the author sees (Exercise E).

Usage (system Python 3.14, which has Playwright and its browsers):
    capture_synthesis.py --study <fresh seeded discovery dir> --out <dir> \
        --question-file <file> --developments '<JSON list>' \
        --answer-file <authentic unedited answer> --expect-sha <recorded request sha256> \
        [--follow-question-file <file> --criticism-file <file> --follow-answer-file <authentic answer> --expect-follow-sha <sha>]

The study is copied first; the source is never driven. The page prepares each request itself, from the author's text and the
developments it selected. Each page-prepared request fingerprint is compared with the recorded one; only when they are equal is the
authentic answer pasted as the coding agent's response for that exact request. Nothing is applied; no record changes.
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
RUNTIME = "fresh-subagent-synthesis-exercise"


@contextlib.contextmanager
def served(browser, project: Path, width: int, height: int):
    server = BeginnerWorkspaceServer(project, port=0)
    thread = server.start_in_thread()
    page = browser.new_page(viewport={"width": width, "height": height})
    errors = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    try:
        page.goto(f"http://127.0.0.1:{server.port}/studio.html?canvas={CANVAS}", wait_until="networkidle")
        page.wait_for_selector("#architecture-synthesis:not([hidden])", timeout=30000)
        page.wait_for_selector('input[data-development^="question:"]', timeout=30000)
        yield page, errors
    finally:
        page.close()
        server.stop()
        thread.join(timeout=5)


def prepared_request(page) -> dict:
    page.wait_for_selector("textarea.synthesis-request", timeout=30000)
    return json.loads(page.locator("textarea.synthesis-request").input_value())


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--study", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--question-file", required=True, type=Path)
    parser.add_argument("--developments", required=True, help='JSON list of {"kind": ..., "ref": ...} the page selects')
    parser.add_argument("--answer-file", required=True, type=Path)
    parser.add_argument("--expect-sha", required=True)
    parser.add_argument("--follow-question-file", type=Path)
    parser.add_argument("--criticism-file", type=Path)
    parser.add_argument("--follow-answer-file", type=Path)
    parser.add_argument("--expect-follow-sha")
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)

    work = Path(tempfile.mkdtemp(prefix="served-synthesis-")) / "discovery"
    shutil.copytree(args.study, work)
    question = args.question_file.read_text(encoding="utf-8").strip()
    developments = json.loads(args.developments)
    answer_text = args.answer_file.read_text(encoding="utf-8")
    record = {"expected_request_sha256": args.expect_sha, "passes": {}}

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True, args=["--no-sandbox"])
        with served(browser, work, 1440, 900) as (page, errors):
            for item in developments:
                page.locator(f'input[data-development="{item["kind"]}:{item["ref"]}"]').check()
            page.locator('textarea[data-synthesis="question"]').fill(question)
            page.locator('button[data-synthesis="prepare"]').click()
            request = prepared_request(page)
            record["page_request_sha256"] = request["request_sha256"]
            record["page_request_equals_recorded"] = request["request_sha256"] == args.expect_sha
            if request["request_sha256"] != args.expect_sha:
                raise SystemExit("the page's request is not the recorded request; the answer is not pasted")
            page.locator("textarea.synthesis-response").fill(json.dumps(ce.envelope(request, answer_text, RUNTIME)))
            page.locator('button[data-synthesis="submit"]').click()
            page.wait_for_selector(".synthesis-stage", timeout=30000)
            page.locator("#architecture-synthesis").scroll_into_view_if_needed()
            page.screenshot(path=str(args.out / "01-trajectory-desktop-1440.png"), full_page=False)
            record["passes"]["first"] = {
                "stages": page.locator(".synthesis-stage").count(),
                "standing_text": page.locator(".synthesis-standing").inner_text(),
                "evidence_disclosed": page.locator(".synthesis-evidence-item").count(),
                "page_overflow_px": page.evaluate("() => document.documentElement.scrollWidth - document.documentElement.clientWidth"),
            }
            if args.follow_question_file and args.follow_answer_file:
                page.locator('button[data-synthesis="continue"]').click()
                follow_question = args.follow_question_file.read_text(encoding="utf-8").strip()
                page.locator('textarea[data-synthesis="question"]').fill(follow_question)
                criticism = [line.strip() for line in args.criticism_file.read_text(encoding="utf-8").splitlines() if line.strip()]
                page.locator('textarea[data-synthesis="criticism"]').fill("\n".join(criticism))
                page.locator('button[data-synthesis="prepare"]').click()
                follow = prepared_request(page)
                record["follow_page_request_sha256"] = follow["request_sha256"]
                record["follow_page_request_equals_recorded"] = follow["request_sha256"] == args.expect_follow_sha
                if follow["request_sha256"] != args.expect_follow_sha:
                    raise SystemExit("the page's follow-up request is not the recorded one; the answer is not pasted")
                follow_answer = args.follow_answer_file.read_text(encoding="utf-8")
                page.locator("textarea.synthesis-response").fill(json.dumps(ce.envelope(follow, follow_answer, RUNTIME)))
                page.locator('button[data-synthesis="submit"]').click()
                page.wait_for_selector(".synthesis-stage", timeout=30000)
                page.locator("#architecture-synthesis").scroll_into_view_if_needed()
                page.screenshot(path=str(args.out / "02-follow-up-desktop-1440.png"), full_page=False)
                record["passes"]["follow_up"] = {
                    "verdicts_shown": page.locator(".synthesis-verdict").count(),
                    "changes_shown": page.locator(".synthesis-change").count(),
                    "page_overflow_px": page.evaluate("() => document.documentElement.scrollWidth - document.documentElement.clientWidth"),
                }
            record["console_page_errors"] = errors
        with served(browser, work, 390, 844) as (page, errors):
            page.wait_for_selector(".synthesis-stage", timeout=30000)
            page.locator(".synthesis-stage").first.scroll_into_view_if_needed()
            page.screenshot(path=str(args.out / "03-latest-phone-390.png"), full_page=False)
            record["passes"]["phone"] = {
                "stages": page.locator(".synthesis-stage").count(),
                "page_overflow_px": page.evaluate("() => document.documentElement.scrollWidth - document.documentElement.clientWidth"),
                "console_page_errors": errors,
            }
        browser.close()
    (args.out / "record.json").write_text(json.dumps(record, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(record, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
