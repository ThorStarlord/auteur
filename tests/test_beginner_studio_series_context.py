"""The Studio's read-only Series and Book context: each owner read as itself, nothing joined or written.

A concept is linked to a Book plan only by a typed reference that working Book records to the concept's
node id. The project's Series plan and Directions are reported beside the Architecture and are never
linked to it or to each other. Accepted records are shown only when their acceptance verifies.
"""
import hashlib
import json
import shutil
import sys
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import urlopen

import pytest

from auteur.beginner.server import BeginnerWorkspaceServer
from auteur.beginner.studio_series_context import project_series_context

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))
import seed_series_context_study as seed  # noqa: E402
from seed_atelier_study import SPECIMENS, seed as seed_atelier  # noqa: E402


def tree_digest(root: Path) -> dict[str, str]:
    return {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(root.rglob("*")) if p.is_file()}


@pytest.fixture(scope="module")
def linked(tmp_path_factory):
    project = tmp_path_factory.mktemp("linked")
    seed.seed_spring(project)
    return project


@pytest.fixture(scope="module")
def context(tmp_path_factory):
    project = tmp_path_factory.mktemp("context")
    seed_atelier(project, "atelier-small", SPECIMENS["atelier-small"])
    shutil.copyfile(seed.FULL_PLAN, project / "series_identity.yaml")
    seed.seed_sparse(project)
    return project


def test_book_references_are_exactly_what_the_book_records(linked):
    before = tree_digest(linked)
    result = project_series_context(linked, seed.SPRING)
    assert tree_digest(linked) == before  # reading writes nothing
    books = result["sources"]["working_books"]
    assert books["state"] == "available" and books["authority"] == "working_noncanonical"
    (book,) = books["books"]
    assert (book["book_number"], book["freshness"], book["semantic_impact"]) == (24, "ready", "clear")
    recorded = json.loads((seed.EVIDENCE / "as-qualified/book-24-candidate.json").read_text(encoding="utf-8"))
    expected = {ref["id"] for ref in _refs(recorded) if ref["kind"] == "series_node"}
    assert {ref["node_id"] for ref in book["references"]} == expected
    ledger = next(ref for ref in book["references"] if ref["node_id"] == "eng_ledger")
    assert ledger["present"] and ledger["changed_since_book"] is False
    assert {e["id"] for e in ledger["elements"]} == {
        e["id"] for e in _elements(recorded) if any(r == {"kind": "series_node", "id": "eng_ledger"} for r in e.get("refs", []))}
    # No Book operation can accept anything; nothing reads as a commitment.
    assert {e["commitment_authority"] for ref in book["references"] for e in ref["elements"]} <= {
        "agent_working", "undecided", "author_reserved", "not_adopted", "not_established", "withdrawn"}
    # The project keeps no Series plan or Directions: nothing is invented for them.
    assert result["sources"]["series_plan"]["state"] == "absent"
    assert result["sources"]["series_direction"]["state"] == "absent"


def test_a_removed_concept_makes_the_book_stale_and_contradictory(tmp_path):
    seed.remove_node(seed.seed_spring(tmp_path), seed.REMOVED_NODE)
    (book,) = project_series_context(tmp_path, seed.SPRING)["sources"]["working_books"]["books"]
    assert (book["freshness"], book["series_changed"], book["semantic_impact"]) == ("stale", True, "contradictory")
    gone = next(ref for ref in book["references"] if ref["node_id"] == seed.REMOVED_NODE)
    assert gone["present"] is False and gone["title"] is None


def test_full_plan_and_directions_are_separate_unlinked_owners(context):
    before = tree_digest(context)
    result = project_series_context(context, "atelier-small")
    assert tree_digest(context) == before
    assert result["architecture_link"]["recorded"] is False
    assert result["separate_owners_note"]
    plan = result["sources"]["series_plan"]
    assert plan["state"] == "available" and plan["authority"] == "author_declared_plan"
    assert [s["id"] for s in plan["setups"]] == ["setup_execution_ledger", "setup_mercy_oath"]
    assert plan["setups"][0]["source"]["ref"] == "narrative_setups[0]"
    assert plan["payoffs"][0]["setup_id"] == "setup_execution_ledger"
    origins = {(e["source_id"], e["type"], e["target_id"]): e["origin"] for e in plan["derived"]["edges"]}
    assert origins[("book_1", "sets_up", "emperor_identity")] == "declared"
    assert origins[("book_1", "transforms", "elena_arc")] == "derived_from_plan"
    assert plan["derived"]["authority"] == "derived_not_canonical"
    assert {c["id"] for c in plan["derived"]["setup_payoff_checks"]} == set()

    direction = result["sources"]["series_direction"]
    assert direction["series"]["state"] == "accepted" and direction["series"]["revision"] == 2
    (book,) = direction["books"]
    assert (book["accepted_against_series_revision"], book["current_series_revision"], book["freshness"]) == (
        1, 2, "series_direction_revised")
    assert book["series_commitment_ids"] == ["contested-history"]
    # Two Series proposals are kept; one is behind the current accepted record. The Book's is current.
    assert direction["other_proposals"] == {"series_direction": 1, "book_direction": 0}


def test_damaged_owner_records_are_reported_not_shown(context, tmp_path):
    project = tmp_path / "damaged"
    shutil.copytree(context, project)
    (project / "series_identity.yaml").write_text("title: Unfinished\nbook_plans: [\n", encoding="utf-8")
    accepted = project / ".auteur/series/vertical-slice/accepted/series-direction.yaml"
    accepted.write_text(accepted.read_text(encoding="utf-8").replace("Archive of Lies", "Archive of Truths"),
                        encoding="utf-8")
    result = project_series_context(project, "atelier-small")
    plan = result["sources"]["series_plan"]
    assert plan["state"] == "invalid" and "books" not in plan
    direction = result["sources"]["series_direction"]
    assert direction["series"]["state"] == "unverified"
    assert "Truths" not in json.dumps(result) and "promise" not in direction["series"]
    (book,) = direction["books"]
    assert book["state"] == "accepted" and book["freshness"] == "unknown"
    assert result["version"] != project_series_context(context, "atelier-small")["version"]


def test_a_project_without_plans_says_so(tmp_path):
    seed_atelier(tmp_path, "atelier-small", SPECIMENS["atelier-small"])
    result = project_series_context(tmp_path, "atelier-small")
    assert result["available"] is False
    assert {k: v["state"] for k, v in result["sources"].items()} == {
        "working_books": "absent", "series_plan": "absent", "series_direction": "absent"}


def test_route_is_read_only_and_canvas_scoped(context):
    server = BeginnerWorkspaceServer(context, port=0)
    thread = server.start_in_thread()
    try:
        base = f"http://127.0.0.1:{server.port}/api/beginner/studio/canvases"
        before = tree_digest(context)
        body = json.loads(urlopen(f"{base}/atelier-small/series-context").read())
        assert body["schema"] == "studio-series-context/1" and body["canvas_id"] == "atelier-small"
        assert tree_digest(context) == before
        for bad, code in (("missing-canvas", 404), ("..%2F..", 400)):
            with pytest.raises(HTTPError) as raised:
                urlopen(f"{base}/{bad}/series-context")
            assert raised.value.code == code
    finally:
        server.stop()
        thread.join(timeout=5)


def _elements(node):
    if isinstance(node, dict):
        if "id" in node and "text" in node:
            yield node
        for value in node.values():
            yield from _elements(value)
    elif isinstance(node, list):
        for value in node:
            yield from _elements(value)


def _refs(node):
    if isinstance(node, dict):
        if set(node) == {"kind", "id"}:
            yield node
        for value in node.values():
            yield from _refs(value)
    elif isinstance(node, list):
        for value in node:
            yield from _refs(value)
