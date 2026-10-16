"""Live, operator-initiated Studio Narrative Architecture qualification.

Example (a real adapter executable that reads HostAgentRequest JSON on stdin and
prints ONLY the raw requested candidate/advice JSON on stdout):

  python scripts/studio_architecture_e2e.py --report /tmp/auteur-e2e.json \
      --agent python /absolute/path/to/actual_coding_agent_adapter.py

The agent program is an explicitly selected LOCAL test dependency, not a Studio
provider bridge. A synthetic adapter cannot establish authentic-agent E2E proof.
The command never runs in response to Browser HTTP input. No accepted-story
write is performed by this script.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import socket
import subprocess
import sys
import tempfile
import time
from urllib.error import HTTPError
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parent.parent
VISION = ("An epic progression fantasy celebrating joy through generous heroism. "
          "The paladin is already extraordinarily kind and protects beautiful, "
          "flourishing communities; a starting moral flaw is not required.")
NONCANONICAL_PREFIXES = (".auteur/beginner/studio/", ".auteur/quick_draft/")


def fingerprint_json(value: dict) -> str:
    body = json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(',', ':')).encode('utf-8')
    return hashlib.sha256(body).hexdigest()


def snapshot(root: Path) -> dict[str, str]:
    """Hash all files except existing approved noncanonical working stores."""
    result = {}
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(root).as_posix()
        if any(rel.startswith(prefix) for prefix in NONCANONICAL_PREFIXES):
            continue
        result[rel] = hashlib.sha256(path.read_bytes()).hexdigest()
    return result


def source_identity(root: Path) -> str:
    """Only a clean, pinned checkout may produce an exact-head receipt."""
    try:
        sha = subprocess.check_output(['git', '-C', str(root), 'rev-parse', 'HEAD'],
                                      text=True, stderr=subprocess.PIPE).strip()
        dirty = subprocess.check_output(['git', '-C', str(root), 'status', '--porcelain'],
                                        text=True, stderr=subprocess.PIPE)
    except (subprocess.CalledProcessError, FileNotFoundError) as error:
        raise RuntimeError('BLOCKED: exact Git source identity unavailable') from error
    if not re.fullmatch(r'[a-f0-9]{40}', sha):
        raise RuntimeError('BLOCKED: invalid Git commit identity')
    if dirty.strip():
        raise RuntimeError('BLOCKED: dirty checkout cannot prove an exact-head E2E')
    return sha


def reentry_invariants(architecture: dict, canvas: dict, sha: str, kept_id: str) -> bool:
    """A stale-but-retained proposal is valid after an intentional working edit."""
    items = canvas.get('items') or []
    return (architecture.get('status') in {'ready', 'stale'}
            and architecture.get('candidate_request_sha256') == sha
            and isinstance(architecture.get('candidate'), dict)
            and any(item.get('id') == kept_id and
                    (item.get('proposal_origin') or {}).get('source_kind') == 'host_agent_suggestion'
                    for item in items))


def wait_for_working_choice(read, *, timeout: float = 10, interval: float = 0.2):
    """Await observed CanvasStore persistence, not an arbitrary Browser sleep."""
    deadline = time.monotonic() + max(timeout, 0)
    while True:
        saved = read()
        choices = [item for item in saved.get('items', [])
                   if (item.get('proposal_origin') or {}).get('source_kind') == 'host_agent_suggestion']
        if choices:
            return saved, choices[-1]
        if time.monotonic() >= deadline:
            raise TimeoutError('The mentor working choice was not persisted')
        time.sleep(interval)


def free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def api(base: str, route: str, payload: dict | None = None) -> dict:
    body = json.dumps(payload).encode("utf-8") if payload is not None else None
    req = Request(base + route, data=body, method="POST" if payload is not None else "GET",
                  headers={"Content-Type": "application/json"})
    with urlopen(req, timeout=12) as response:
        return json.loads(response.read())


def run_agent(argv: list[str], request: dict, timeout: int) -> dict:
    """Run only operator-supplied argv; never interpolate untrusted prose in a shell."""
    if not argv:
        raise RuntimeError("BLOCKED: no authentic coding-agent command supplied")
    if not request.get("request_sha256") or request.get("role") not in {
        "studio_architecture", "studio_mentor"
    }:
        raise ValueError("missing or unexpected host-agent request identity")
    try:
        completed = subprocess.run(argv, input=json.dumps(request, ensure_ascii=False),
                                   text=True, capture_output=True, timeout=timeout,
                                   cwd=ROOT, shell=False, check=False)
    except FileNotFoundError as error:
        raise RuntimeError("BLOCKED: coding-agent executable not available") from error
    except subprocess.TimeoutExpired as error:
        raise RuntimeError("BLOCKED: coding-agent command timed out") from error
    if completed.returncode:
        # Stderr may contain tokens or prompts. Keep it out of shareable receipts.
        raise RuntimeError("Agent exited with code " + str(completed.returncode) +
                           "; inspect private agent logs locally")
    try:
        result = json.loads(completed.stdout)
    except json.JSONDecodeError as error:
        raise ValueError("Agent output was not a single raw JSON object") from error
    if not isinstance(result, dict):
        raise ValueError("Agent response must be one raw JSON object")
    return result


def record(report: dict, label: str, result: bool, detail: str = "") -> None:
    report["steps"].append({"step": label, "result": "PASS" if result else "FAIL",
                            "detail": detail[:500]})
    if not result:
        raise AssertionError(label + (": " + detail if detail else ""))


def wait_server(base: str, process: subprocess.Popen) -> None:
    for _ in range(90):
        if process.poll() is not None:
            raise RuntimeError("Auteur local server exited early: " + str(process.returncode))
        try:
            api(base, "/api/beginner/health")
            return
        except OSError:
            time.sleep(0.2)
    raise RuntimeError("Auteur server did not become healthy")


def qualify(args: argparse.Namespace, report: dict) -> None:
    report['code_sha'] = source_identity(ROOT)
    # A new project per run: never delete an existing author's story.
    project = Path(args.project).resolve() if args.project else Path(tempfile.mkdtemp(prefix="auteur-architecture-e2e-"))
    if project.exists() and (not project.is_dir() or any(project.iterdir())):
        raise ValueError("project directory must be absent or empty")
    project.mkdir(parents=True, exist_ok=True)
    report["project"] = str(project)
    before = snapshot(project)
    port = free_port()
    base = "http://127.0.0.1:" + str(port)
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT / "src") + os.pathsep + env.get("PYTHONPATH", "")
    server = subprocess.Popen([sys.executable, "-m", "auteur.beginner.server", "--project",
                               str(project), "--port", str(port), "--studio-development-default"],
                              cwd=ROOT, env=env, stdout=subprocess.DEVNULL,
                              stderr=subprocess.DEVNULL)
    try:
        wait_server(base, server)
        from playwright.sync_api import sync_playwright
        from auteur.host_agent import HostAgentRequest, build_host_agent_response

        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(**({"executable_path": args.chromium} if args.chromium else {}))
            page = browser.new_page(viewport={"width": 1300, "height": 900})
            errors = []
            page.on("pageerror", lambda error: errors.append(str(error)))
            page.goto(base + "/studio.html", wait_until="networkidle")
            page.locator("#vision-text").wait_for(state="visible")
            page.fill("#vision-text", VISION)
            page.click("#vision-save")
            page.click("#architecture-develop")
            page.wait_for_function("document.querySelector('#architecture-request').value.includes('request_sha256')", timeout=12000)
            packet = json.loads(page.input_value("#architecture-request"))
            canvas = re.search(r"[?&]canvas=([a-z0-9_-]+)", page.url)
            record(report, "Browser prepares exact Story Vision request",
                   bool(canvas and packet.get("role") == "studio_architecture"
                        and json.loads(packet["user"])["working_context"]["vision"] == VISION))
            canvas_id = canvas.group(1)
            report["canvas"] = canvas_id
            report["architecture_request_sha256"] = packet["request_sha256"]
            report["source_sha256"] = packet["settings"].get("source_sha256")
            response = run_agent(args.agent, packet, args.agent_timeout)
            report['candidate_payload_sha256'] = fingerprint_json(response)
            record(report, "real coding agent returned candidate JSON", isinstance(response, dict))
            prefix = "/api/beginner/studio/canvases/" + canvas_id
            envelope = build_host_agent_response(HostAgentRequest(**packet), json.dumps(response))
            ready = api(base, prefix + "/architecture/host-agent-response", envelope.model_dump())
            record(report, "existing backend validates exact host response",
                   ready.get("status") == "ready" and
                   ready.get("candidate_request_sha256") == packet["request_sha256"])
            wrong = envelope.model_dump()
            wrong["request_sha256"] = "0" * 64
            try:
                api(base, prefix + "/architecture/host-agent-response", wrong)
                wrong_sha_rejected = False
            except HTTPError as error:
                wrong_sha_rejected = 400 <= error.code < 500
            present = api(base, prefix + "/architecture")
            record(report, "wrong-source response rejected without changing candidate",
                   wrong_sha_rejected and present.get("status") == "ready" and
                   present.get("candidate_request_sha256") == packet["request_sha256"])
            record(report, "candidate has explanatory content and declared graph links",
                   len(response.get("nodes", [])) >= 4 and len(response.get("links", [])) >= 1
                   and {"genre", "trope"}.issubset({n.get("category") for n in response.get("nodes", [])})
                   and any(n.get("category") in {"engine", "structure"} for n in response.get("nodes", [])))
            page.click("#architecture-refresh")
            page.locator("#nodes button.node").first.wait_for(state="visible", timeout=10000)
            record(report, "Browser presents proposed spatial graph",
                   page.locator("#nodes button.node").count() >= 4)
            record(report, "author words and AI summary are visibly separate",
                   page.locator('#contrast-author').inner_text() == VISION and
                   page.locator('#contrast-proposal').inner_text() == response['summary'])
            first_edge = response["links"][0]
            linked_node = next(n for n in response["nodes"] if n["id"] == first_edge["source"])
            page.locator("#nodes button.node", has_text=linked_node["title"]).first.click()
            record(report, "author can inspect source-declared link verb",
                   page.locator("#source-links button.facet-link").count() > 0)
            for facet in ("genres", "tropes", "structure"):
                page.locator('[data-architecture-facet="' + facet + '"]').click()
                record(report, "narrative facet " + facet + " explains proposal",
                       bool(page.locator("#studio-explanatory-hero").inner_text().strip()))
            page.locator('[data-architecture-facet="overview"]').click()
            record(report, "author can return to graph",
                   page.locator("#nodes button.node:visible").count() >= 4)
            page.set_viewport_size({"width": 390, "height": 844})
            record(report, "narrow Browser has no horizontal overflow",
                   page.evaluate("document.documentElement.scrollWidth <= innerWidth + 1"))
            page.set_viewport_size({"width": 1300, "height": 900})
            # Existing mentor owns the alternatives; the command must create real advice.
            page.locator("#nodes button.node:visible").first.click()
            page.locator("#contrast-explore").click()
            page.wait_for_function("document.querySelector('#mentor-request').textContent.includes('request_sha256')", timeout=12000)
            mentor_packet = json.loads(page.locator("#mentor-request").inner_text())
            report["mentor_request_sha256"] = mentor_packet["request_sha256"]
            advice = run_agent(args.agent, mentor_packet, args.agent_timeout)
            report['mentor_payload_sha256'] = fingerprint_json(advice)
            directions = advice.get("directions", [])
            record(report, "agent returns at least two non-identical mechanisms",
                   len(directions) >= 2 and len({d.get("mechanism") for d in directions}) >= 2)
            mentor_envelope = build_host_agent_response(HostAgentRequest(**mentor_packet), json.dumps(advice))
            mentor = api(base, prefix + "/mentor/host-agent-response", mentor_envelope.model_dump())
            record(report, "mentor alternative validates", mentor.get("status") == "ready")
            page.locator("#mentor-refresh").click()
            page.locator(".mentor-direction button").first.wait_for(state="visible", timeout=8000)
            page.locator(".mentor-direction button").first.click()
            page.locator("#mentor-keep").click()
            stored, kept = wait_for_working_choice(lambda: api(base, prefix))
            record(report, "explicit keep creates only working story item", bool(kept))
            kept_id = kept["id"]
            page.reload(wait_until="networkidle")
            page.locator("#vision-text").wait_for(state="visible")
            record(report, "re-entry preserves verbatim Story Vision", page.input_value("#vision-text") == VISION)
            record(report, "re-entry restores proposal and deliberately kept working idea",
                   reentry_invariants(api(base, prefix + "/architecture"),
                                      api(base, prefix), packet["request_sha256"], kept_id))
            record(report, "Browser produces no page errors", not errors, "; ".join(errors[:2]))
            browser.close()
    finally:
        server.terminate()
        try:
            server.wait(timeout=10)
        except subprocess.TimeoutExpired:
            server.kill()
            server.wait(timeout=5)
        report["canonical_file_hashes"] = snapshot(project)
        report["canonical_unchanged"] = before == report["canonical_file_hashes"]
    record(report, "all canonical/story hashes preserved", report["canonical_unchanged"],
           "new=" + ",".join(sorted(set(report["canonical_file_hashes"]) - set(before))[:5]))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", help="NEW or EMPTY disposable project root")
    parser.add_argument("--report", required=True, help="JSON evidence receipt destination")
    parser.add_argument("--chromium", help="Optional installed Chromium executable")
    parser.add_argument("--agent-timeout", type=int, default=180)
    parser.add_argument("--agent", nargs=argparse.REMAINDER,
                        help="Actual executable + arguments; receives exact request JSON on stdin")
    args = parser.parse_args(argv)
    report = {"claim": "manual coding-agent Narrative Architecture E2E only",
              "connected_host_e2e": "BLOCKED: no attached executor proven",
              "human_usability": "NOT_TESTED", "steps": [],
              "agent_runtime": "operator-supplied executable; model unverified"}
    exit_code = 0
    try:
        if not args.agent:
            raise RuntimeError("BLOCKED: real coding-agent command required; no fixture substitution")
        qualify(args, report)
        report["result"] = "PASS - bounded manual E2E"
    except Exception as error:
        blocked = str(error).startswith("BLOCKED:")
        report["result"] = "BLOCKED" if blocked else "FAIL"
        report["error"] = str(error)
        exit_code = 2 if blocked else 1
    finally:
        Path(args.report).parent.mkdir(parents=True, exist_ok=True)
        Path(args.report).write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(report["result"] + " :: " + str(args.report))
        for item in report["steps"]:
            print(item["result"] + " " + item["step"])
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
