"""Served Studio: what working-Architecture changes mean for the working Books, and reconciling one of them.

An applied Architecture revision → the working Books that cite what it changed → one Book's exact evidence →
a whole-Book revision through that Book's own owner → its coding agent's response → review → explicit Apply
→ the overview read again → back to the same place in the atlas. Reading writes nothing; only prepare and
apply write, and only the reconciled Book's own records change.
"""
import copy
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

import pytest
from playwright.sync_api import sync_playwright

from auteur.beginner.server import BeginnerWorkspaceServer
from auteur.beginner.studio_architecture import complete_architecture, project_architecture
from auteur.beginner.studio_store import CanvasStore
from auteur.host_agent import HostAgentRequest, build_host_agent_response

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))
import seed_book_impact_study as seed  # noqa: E402

CANVAS = seed.SPRING
SNAP = "document.getElementById('studio-atelier').atelierStudy.snapshot()"
FOLIO = "document.querySelector('#studio-atelier .atl-folio').innerText"
LIVE = "document.querySelector('#studio-atelier [aria-live]').textContent"
KEY = "document.activeElement && document.activeElement.dataset ? document.activeElement.dataset.key || null : null"
ARM = """() => { const r = document.getElementById('studio-atelier');
  window.__settled = new Promise(res => r.addEventListener('atelier:settled', e => res(e.detail), {once: true})); }"""
WAIT = "Promise.race([window.__settled, new Promise(r => setTimeout(() => r(null), 8000))])"


def q(key):
    return f'#studio-atelier [data-key="{key}"]'


@pytest.fixture(scope="module")
def browser():
    with sync_playwright() as playwright:
        options = {"headless": True, "args": ["--no-sandbox"]}
        if os.environ.get("CHROMIUM_PATH"):
            options["executable_path"] = os.environ["CHROMIUM_PATH"]
        instance = playwright.chromium.launch(**options)
        yield instance
        instance.close()


@pytest.fixture(scope="module")
def pristine(tmp_path_factory):
    root = tmp_path_factory.mktemp("impact-browser")
    seed.seed_impact(root / "impact")
    seed.seed_current(root / "current")
    return root


@pytest.fixture
def served(pristine, tmp_path):
    started = []

    def start(name="impact"):
        project = tmp_path / name
        shutil.copytree(pristine / name, project)
        server = BeginnerWorkspaceServer(project, port=0)
        started.append((server, server.start_in_thread()))
        return project, f"http://127.0.0.1:{server.port}"
    yield start
    for server, thread in started:
        server.stop()
        thread.join(timeout=5)


def open_atelier(browser, base, width=1440, height=900):
    page = browser.new_page(viewport={"width": width, "height": height})
    log = {"errors": [], "writes": []}
    page.on("pageerror", lambda error: log["errors"].append(str(error)))
    page.on("request", lambda r: log["writes"].append(r.url.split("/api/")[-1]) if r.method != "GET" else None)
    page.goto(f"{base}/studio.html?canvas={CANVAS}&atelier", wait_until="networkidle")
    page.wait_for_selector("#studio-atelier .atl-star", state="attached", timeout=20000)
    time.sleep(0.6)
    log["writes"].clear()
    return page, log


def wait_for(page, key, timeout=10000):
    page.wait_for_selector(q(key), timeout=timeout)
    time.sleep(0.3)


def books_dir(project):
    return project / ".auteur/beginner/studio/canvases" / CANVAS / "architecture/books"


def current(project, n):
    return json.loads((books_dir(project) / str(n) / "current.json").read_text(encoding="utf-8"))


def files(root, *, skip=None):
    return {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(root.rglob("*"))
            if p.is_file() and not p.name.endswith(".lock") and (skip is None or skip not in p.parents)}


def reconciled(project, n):
    """The coding agent's whole-Book answer: stop citing the removed concept, restating what it changes."""
    artifact = json.loads(json.dumps(current(project, n)["artifact"]))

    def visit(node):
        if isinstance(node, dict):
            refs = node.get("refs")
            if isinstance(refs, list) and any(r.get("id") == seed.REMOVED_NODE for r in refs):
                node["refs"] = [r for r in refs if r.get("id") != seed.REMOVED_NODE]
                if {"kind": "series_node", "id": "str_hollow_gate"} not in node["refs"]:
                    node["refs"].append({"kind": "series_node", "id": "str_hollow_gate"})
                if "provenance" in node:
                    node.pop("provenance")
                    node["attribution"], node["epistemic_status"] = "agent_proposed", "asserted"
            for value in node.values():
                visit(value)
        elif isinstance(node, list):
            for value in node:
                visit(value)
    visit(artifact)
    return artifact


def agent_cli(project, n, artifact):
    """The coding agent's side: the Working Book owner's own commands, in a fresh process."""
    env = dict(os.environ, PYTHONPATH=str(REPO / "src"), PYTHONUTF8="1")
    base = [sys.executable, "-m", "auteur.series.working_book_architecture", "--project", str(project), "--canvas", CANVAS]
    shown = subprocess.run([*base, "book-show", "--book", str(n)], capture_output=True, text=True, encoding="utf-8",
                           env=env, check=True)
    assert json.loads(shown.stdout)["status"] == "awaiting_host_agent"
    path = project.parent / f"reconciled-{n}.json"
    path.write_text(json.dumps(artifact), encoding="utf-8")
    done = subprocess.run([*base, "book-complete-file", "--book", str(n), "--candidate", str(path)],
                          capture_output=True, text=True, encoding="utf-8", env=env, check=False)
    return json.loads(done.stdout)


def place(snapshot):
    return {key: snapshot[key] for key in ("focus", "trail", "mode", "depth", "camera", "positions")}


def open_overview(page):
    page.wait_for_selector(q("impact-open"), timeout=10000)
    page.locator(q("impact-open")).click()
    page.wait_for_function(f"({SNAP}).series.status === 'ready'", timeout=10000)
    time.sleep(0.3)


def test_an_architecture_revision_applied_in_the_studio_leads_to_the_books_it_affects(browser, served):
    project, base = served("current")
    store = CanvasStore(project, CANVAS)
    page, log = open_atelier(browser, base)
    assert page.locator(q("impact-open")).count() == 0  # both Books are current: nothing to point at
    before = files(books_dir(project))
    # The author asks for the Architecture revision in the Studio; the coding agent answers it.
    page.evaluate("""() => { document.getElementById('architecture-instruction').value =
      'Let the ledger record hours, and drop the Gate table.'; document.getElementById('architecture-revise').click(); }""")
    page.wait_for_function("document.getElementById('architecture-status').textContent.length > 0", timeout=10000)
    deadline = time.time() + 10
    while project_architecture(store)["status"] != "awaiting_host_agent" and time.time() < deadline:
        time.sleep(0.2)
    prepared = project_architecture(store)
    revised = copy.deepcopy(json.loads((store.directory / "architecture/current.json").read_text(encoding="utf-8"))["candidate"])
    next(n for n in revised["nodes"] if n["id"] == seed.CHANGED_NODE)["summary"] += seed.LEDGER_REWORDING
    revised["nodes"] = [n for n in revised["nodes"] if n["id"] != seed.REMOVED_NODE]
    revised["links"] = [x for x in revised.get("links", []) if seed.REMOVED_NODE not in (x.get("source"), x.get("target"))]
    complete_architecture(store, build_host_agent_response(HostAgentRequest(**prepared["request"]), json.dumps(revised),
                                                           runtime="impact-test").model_dump())
    # The author reviews and applies the Architecture revision in the Studio, as #632 does.
    page.locator("#architecture-refresh").click()
    page.wait_for_selector("#architecture-review:not([hidden])", timeout=10000)
    page.evaluate(ARM)
    page.locator("#architecture-apply").click()
    page.evaluate(WAIT)
    page.wait_for_selector(q("impact-open"), timeout=10000)
    time.sleep(0.4)
    folio = page.evaluate(FOLIO).upper()
    assert "Your applied revision".upper() in folio
    assert "Book 24 and Book 25 cite Architecture concepts that changed or are gone".upper() in folio
    assert files(books_dir(project)) == before  # an Architecture revision rewrites no Book
    open_overview(page)
    folio = page.evaluate(FOLIO).upper()
    assert "What the Architecture changes mean for its working Books".upper() in folio
    assert "Gate Table · no longer in the Architecture · cited by Book 24 and Book 25".upper() in folio
    assert "Written against the working Architecture as it was 1 applied revision ago.".upper() in folio
    assert not log["errors"]


def test_overview_evidence_reconcile_review_apply_and_return(browser, served):
    project, base = served()
    outside = files(project, skip=books_dir(project) / "24")
    page, log = open_atelier(browser, base)
    home = page.evaluate(SNAP)
    open_overview(page)
    folio = page.evaluate(FOLIO).upper()
    assert "Cite concepts that changed or are gone · 2".upper() in folio
    assert "Out of date, with every cited concept unchanged · 1".upper() in folio and "not that the Book is unaffected".upper() in folio
    assert "Could not be read · 1".upper() in folio and "Book 29".upper() in folio
    assert "Book 27 (a develop request is prepared) and Book 28 have source items in this canvas but no working Book".upper() in folio
    assert "change to the Book’s source, not to the Architecture".upper() in folio  # Book 25, told apart
    assert page.locator(q("impact-show:29")).count() == 0  # an unreadable Book offers nothing
    assert "Its working record is damaged and cannot be read".upper() in folio
    assert "Unterminated string".upper() not in folio  # the parser's words wait behind "Technical detail"
    assert page.locator(q("impact-tech:29")).count() == 1
    assert "What changed is not cited by it: “Reading the First Stones” (changed)".upper() in folio  # Book 26
    # The removed concept is discoverable here, and the atlas does not show it as current.
    assert "Gate Table · no longer in the Architecture".upper() in folio
    assert page.locator('#studio-atelier .atl-star[data-id*="inst_gate_table"]').count() == 0
    page.locator(q("impact-show:24")).click()
    time.sleep(0.4)
    assert page.evaluate(KEY) == "impact-evidence:24"
    folio = page.evaluate(FOLIO).upper()
    assert "As the Book recorded it".upper() in folio and "A rotating inter-community body formed in Book 22".upper() in folio
    assert "When the Book was written".upper() in folio and "the ledger now also records the hours".upper() in folio
    assert "it does not mean the Book no longer works".upper() in folio  # said once, in the overview
    assert "unchanged in name, kind and description".upper() in folio
    assert "Also changed in the Architecture since, and not cited by Book 24: “Reading the First Stones” (changed)".upper() in folio
    # Escape steps back one level: to the Book's row in the overview, not out of it.
    page.keyboard.press("Escape")
    time.sleep(0.3)
    assert page.evaluate(KEY) == "impact-show:24" and page.evaluate(SNAP)["series"]["leaf"] is not None
    page.locator(q("impact-show:24")).click()
    time.sleep(0.3)
    page.locator(q("impact-reconcile:24")).click()
    page.wait_for_function(f"({KEY}) === 'book-instruction:24'", timeout=5000)
    seeded = page.locator(q("book-instruction:24")).input_value()
    assert seeded.startswith("Reconcile working Book 24") and "Later possibility later-cohort-seat" in seeded
    assert "Revise the whole Book".upper() in page.evaluate(FOLIO).upper()
    assert not log["writes"]  # reading, opening the evidence and the composer write nothing
    page.locator(q("book-prepare:24")).click()
    wait_for(page, "book-check:24")
    assert agent_cli(project, 24, reconciled(project, 24))["status"] == "review_ready"
    assert current(project, 24).get("revision_number", 0) == 0  # a completed response is not a reconciliation
    page.locator(q("book-check:24")).click()
    wait_for(page, "book-apply:24")
    page.locator(q("book-apply:24")).click()
    wait_for(page, "book-note:24")
    page.wait_for_function(f"({SNAP}).series.status === 'ready'", timeout=10000)
    time.sleep(0.5)
    folio = page.evaluate(FOLIO).upper()
    assert "now recorded as written against the current working Architecture".upper() in folio
    assert "Written against the current working Architecture: Book 24.".upper() in folio
    assert "Cite concepts that changed or are gone · 1".upper() in folio  # Book 25 is untouched and still flagged
    snap = page.evaluate(SNAP)
    assert snap["revision"] is None and place(snap) == place(home)
    page.keyboard.press("Escape")  # first to all the Books (Book 24 is now current), then back to the atlas
    time.sleep(0.4)
    assert page.evaluate(SNAP)["series"]["leaf"] is not None
    page.keyboard.press("Escape")
    time.sleep(0.4)
    back = page.evaluate(SNAP)
    assert back["series"]["leaf"] is None and place(back) == place(home)
    assert log["writes"] == [f"beginner/studio/canvases/{CANVAS}/books/24/prepare",
                             f"beginner/studio/canvases/{CANVAS}/books/24/apply"]
    assert current(project, 24)["revision_number"] == 1
    assert files(project, skip=books_dir(project) / "24") == outside
    assert not log["errors"]


def test_a_reconciliation_made_stale_by_another_architecture_change_is_not_applied(browser, served):
    project, base = served()
    page, log = open_atelier(browser, base)
    open_overview(page)
    page.locator(q("impact-show:26")).click()
    time.sleep(0.3)
    page.locator(q("impact-reconcile:26")).click()
    page.wait_for_function(f"({KEY}) === 'book-instruction:26'", timeout=5000)
    page.locator(q("book-prepare:26")).click()
    wait_for(page, "book-check:26")
    assert agent_cli(project, 26, current(project, 26)["artifact"])["status"] == "review_ready"
    page.locator(q("book-check:26")).click()
    wait_for(page, "book-apply:26")
    before = current(project, 26)
    seed.reword_unrelated(CanvasStore(project, CANVAS))  # the Architecture changes again behind the author
    page.locator(q("book-apply:26")).click()
    wait_for(page, "book-note:26")
    folio = page.evaluate(FOLIO).upper()
    assert "Not applied".upper() in folio and "Working Book 26 is unchanged".upper() in folio
    assert current(project, 26) == before
    assert not log["errors"]


def test_phone_width_keeps_the_overview_and_evidence_inside_the_screen(browser, served):
    project, base = served()
    page, log = open_atelier(browser, base, width=390, height=844)
    open_overview(page)
    page.locator(q("impact-show:25")).click()
    time.sleep(0.4)
    overflow = page.evaluate("""() => { const f = document.querySelector('#studio-atelier .atl-folio');
      return [document.documentElement.scrollWidth - document.documentElement.clientWidth, f.scrollWidth - f.clientWidth]; }""")
    assert overflow == [0, 0]
    assert page.locator(q("impact-reconcile:25")).is_visible()
    assert not log["errors"]
