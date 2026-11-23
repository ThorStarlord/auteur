"""Read-only Series and Book planning context for the Studio.

For one canvas this module reads, each through its own owner and side by side:

* the canvas's working Book architectures (``auteur.series.working_book_architecture``),
  noncanonical Book-level proposals that record typed references to the canvas's
  own working Architecture nodes. These are the only recorded links between an
  Architecture concept and a Book plan, and they are reported exactly as recorded,
  with the owner's freshness against the current Architecture.

The Studio serves one project, which may also keep two Series planning contracts:

* the full Series plan, ``series_identity.yaml`` at the project root
  (``SeriesIdentity``, ADR 012). It is the author's declared plan; Auteur keeps
  no acceptance record for it. Its dependency graph and setup/payoff checks are
  derived from it here and labelled as derived.
* the sparse Series and Book Directions kept by the Series vertical slice
  (``VerticalSliceStore``) under ``.auteur/series/vertical-slice``. Only a
  record whose acceptance metadata verifies is shown as accepted; a file that
  no longer matches its acceptance record is reported and its content withheld.

Nothing here writes, accepts, migrates or links anything. No relationship
between the project-level plans and a working Architecture is recorded anywhere,
so none is inferred: not from equal titles, trope names or mechanism phrases.
Every record carries its owner, artifact, path, field reference and revision
or content hash so a later owner-routed action can name exactly what it acts on.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import yaml
from pydantic import ValidationError

from auteur.beginner.studio_store import CanvasStore
from auteur.provenance.store import canonical_content_hash
from auteur.series.continuity_validators import SetupPayoffValidator
from auteur.series.graph import build_dependency_graph
from auteur.series.models import SeriesIdentity
from auteur.series.vertical_slice_store import VerticalSliceStore
from auteur.series.working_book_architecture import book_numbers, book_series_references

SCHEMA = "studio-series-context/1"
SERIES_PLAN_PATH = "series_identity.yaml"
NO_LINK = (
    "Nothing in the working Architecture or in these plans records that they refer to each other. "
    "Equal words are not a link."
)
MAX_BOOK_DIRECTIONS = 200
_TEXT = 600


def _clip(value: Any, limit: int = _TEXT) -> str:
    text = "" if value is None else str(value)
    return text if len(text) <= limit else text[: limit - 1] + "…"


def _first_line(error: Exception) -> str:
    text = str(error).strip().splitlines()
    detail = [line.strip() for line in text if line.strip() and "errors.pydantic.dev" not in line]
    return _clip(" ".join(detail[:3]), 300) or type(error).__name__


def _src(owner: str, path: str, ref: str | None, *, artifact: str | None = None,
         revision: int | None = None, content_hash: str | None = None) -> dict[str, Any]:
    return {"owner": owner, "artifact": artifact or Path(path).stem, "path": path,
            "ref": ref, "revision": revision, "content_hash": content_hash}


def _series_plan(root: Path) -> dict[str, Any]:
    owner = "series_identity"
    base: dict[str, Any] = {
        "owner": owner, "label": "Series plan", "path": SERIES_PLAN_PATH,
        "authority": "author_declared_plan",
        "authority_note": ("The author's declared Series plan file. Auteur keeps no acceptance record for it, "
                           "and generated reports never write back to it."),
    }
    path = root / SERIES_PLAN_PATH
    if not path.is_file():
        return {**base, "state": "absent"}
    try:
        content_hash = canonical_content_hash(path)
        series = SeriesIdentity.from_yaml(path)
    except (OSError, UnicodeError, yaml.YAMLError, ValidationError, ValueError, TypeError) as exc:
        return {**base, "state": "invalid", "reason": _first_line(exc)}

    def src(ref: str) -> dict[str, Any]:
        return _src(owner, SERIES_PLAN_PATH, ref, content_hash=content_hash)

    books = [{
        "id": f"book_{b.book_number}", "book_number": b.book_number, "title": _clip(b.title, 200),
        "series_function": b.series_function.value, "scope": b.scope.value,
        "core_answer": _clip(b.core_answer), "target_experience": _clip(b.target_experience.primary, 200),
        "series_threads_carried": list(b.series_threads_carried),
        "required_setups": list(b.required_setups), "required_payoffs": list(b.required_payoffs),
        "source": src(f"book_plans[{i}]"),
    } for i, b in enumerate(series.book_plans)]
    setups = [{
        "id": s.id, "description": _clip(s.description), "book_introduced": s.book_introduced,
        "expected_payoff_by_book": s.expected_payoff_by_book, "payoff_id": s.payoff_id,
        "status": s.status, "reason_abandoned": _clip(s.reason_abandoned) or None,
        "source": src(f"narrative_setups[{i}]"),
    } for i, s in enumerate(series.narrative_setups)]
    payoffs = [{
        "id": p.id, "setup_id": p.setup_id, "book": p.book, "description": _clip(p.description),
        "source": src(f"narrative_payoffs[{i}]"),
    } for i, p in enumerate(series.narrative_payoffs)]
    mysteries = [{
        "id": m.id, "question": _clip(m.question), "introduced_book": m.introduced_book,
        "expected_payoff_book": m.expected_payoff_book, "actual_payoff_book": m.actual_payoff_book,
        "source": src(f"mysteries[{i}]"),
    } for i, m in enumerate(series.mysteries)]
    themes = [{
        "id": t.id, "theme": _clip(t.theme, 200), "books": list(t.books),
        "progression": {str(k): _clip(v, 300) for k, v in sorted(t.progression.items())},
        "source": src(f"thematic_arcs[{i}]"),
    } for i, t in enumerate(series.thematic_arcs)]
    declared = [{
        "source_id": e.source, "target_id": e.target, "type": e.type.value,
        "description": _clip(e.description, 300) or None, "source": src(f"dependency_edges[{i}]"),
    } for i, e in enumerate(series.dependency_edges)]

    declared_keys = {(e.source, e.target, e.type.value) for e in series.dependency_edges}
    graph = build_dependency_graph(series)
    derived_edges = [{
        "source_id": e.source, "target_id": e.target, "type": e.type.value
        if hasattr(e.type, "value") else str(e.type),
        "origin": "declared" if (e.source, e.target, getattr(e.type, "value", e.type)) in declared_keys
        else "derived_from_plan",
    } for e in graph.edges]
    checks = [{
        "id": d.id, "severity": d.severity, "source": d.source, "explanation": _clip(d.explanation, 300),
    } for d in SetupPayoffValidator().validate(series)]

    return {
        **base, "state": "available", "content_hash": content_hash,
        "title": _clip(series.title, 200), "series_type": series.series_type.value,
        "core_question": _clip(series.core_question),
        "global_arc": {k: _clip(v) for k, v in series.global_arc.model_dump().items() if v},
        "source": src(None),
        "books": books, "setups": setups, "payoffs": payoffs, "mysteries": mysteries,
        "thematic_arcs": themes, "declared_edges": declared,
        "derived": {
            "authority": "derived_not_canonical",
            "note": ("Derived here from the Series plan by the Series dependency graph and the setup/payoff "
                     "continuity check. Not stored, not a plan of its own."),
            "edge_semantics": graph.edge_semantics,
            "edges": derived_edges,
            "setup_payoff_checks": checks,
        },
    }


def _metadata_view(metadata: Any) -> dict[str, Any]:
    return {"revision": metadata.revision, "accepted_at": metadata.accepted_at,
            "accepted_by": metadata.accepted_by, "content_hash": metadata.content_hash}


def _book_number(path: Path) -> int | None:
    stem = path.name.removesuffix(".yaml")
    if not (stem.startswith("book-") and stem.endswith("-direction")):
        return None
    number = stem[len("book-"):-len("-direction")]
    return int(number) if number.isdigit() and int(number) >= 1 else None


def _proposal_ids(directory: Path, pattern: str = "*.yaml") -> set[str]:
    try:
        return {p.stem for p in directory.glob(pattern) if p.is_file()}
    except OSError:
        return set()


def _series_direction(root: Path) -> dict[str, Any]:
    owner = "series_vertical_slice"
    base: dict[str, Any] = {
        "owner": owner, "label": "Series and Book Directions",
        "path": ".auteur/series/vertical-slice",
        "authority": "owner_accepted_records",
        "authority_note": ("Directions accepted through the Series journey. Each accepted record keeps its "
                           "revision and content hash; a Book Direction records the Series Direction "
                           "revision it was accepted against."),
    }
    store = VerticalSliceStore(root)
    # The Series journey keeps every proposal file, the accepted ones included. Only the proposal behind
    # each current accepted record is known; every other kept proposal is earlier or was never accepted.
    proposal_ids = {
        "series_direction": _proposal_ids(store.root / "proposals" / "series-direction"),
        "book_direction": _proposal_ids(store.root / "proposals" / "book-direction", "book-*/*.yaml"),
    }
    proposals = {key: len(value) for key, value in proposal_ids.items()}
    accepted_dir = store.root / "accepted"
    series_path = store.accepted_series_direction_path
    if not series_path.is_file() and not accepted_dir.is_dir() and not any(proposals.values()):
        return {**base, "state": "absent"}

    result: dict[str, Any] = {**base}
    rel_series = series_path.relative_to(root).as_posix()
    series_meta = None
    try:
        accepted = store.load_accepted_series_direction()
        series_meta = store.load_series_direction_metadata()
    except (OSError, UnicodeError, yaml.YAMLError, ValidationError, ValueError) as exc:
        accepted, result["series_reason"] = None, _first_line(exc)
    if accepted is not None and series_meta is not None:
        d = accepted.direction
        src = _src(owner, rel_series, None, artifact=accepted.artifact_id,
                   revision=series_meta.revision, content_hash=series_meta.content_hash)
        result["series"] = {
            "state": "accepted", **_metadata_view(series_meta), "source": src,
            "proposal_id": accepted.proposal_id, "series_id": d.series_id, "title": _clip(d.title, 200), "series_type": d.series_type,
            "promise": _clip(d.promise), "pressure": _clip(d.pressure), "open_question": _clip(d.open_question),
            "commitments": [{
                "commitment_id": c.commitment_id, "statement": _clip(c.statement), "scope": c.scope,
                "source": {**src, "ref": f"direction.commitments[{i}]"},
            } for i, c in enumerate(d.commitments)],
        }
    elif series_path.is_file():
        result["series"] = {"state": "unverified", "path": rel_series,
                            "reason": result.pop("series_reason", None) or
                            "The file does not match its acceptance record, so its content is not shown as accepted."}
    else:
        result["series"] = {"state": "absent"}

    books: list[dict[str, Any]] = []
    files = sorted((p for p in accepted_dir.glob("book-*-direction.yaml") if _book_number(p)),
                   key=lambda p: _book_number(p) or 0) if accepted_dir.is_dir() else []
    for path in files[:MAX_BOOK_DIRECTIONS]:
        number = _book_number(path)
        rel = path.relative_to(root).as_posix()
        try:
            book = store.load_accepted_book_direction(number)
            meta = store.load_book_direction_metadata(number)
        except (OSError, UnicodeError, yaml.YAMLError, ValidationError, ValueError) as exc:
            books.append({"state": "unverified", "book_number": number, "path": rel, "reason": _first_line(exc)})
            continue
        if book is None or meta is None:
            books.append({"state": "unverified", "book_number": number, "path": rel,
                          "reason": "The file does not match its acceptance record, so its content is not shown as accepted."})
            continue
        against = meta.dependencies[0].revision if meta.dependencies else None
        current = series_meta.revision if series_meta is not None and "series" in result \
            and result["series"].get("state") == "accepted" else None
        identity = book.direction.identity
        src = _src(owner, rel, None, artifact=book.artifact_id, revision=meta.revision,
                   content_hash=meta.content_hash)
        books.append({
            "state": "accepted", "book_number": number, **_metadata_view(meta), "source": src,
            "proposal_id": book.proposal_id,
            "title": _clip(identity.title, 200), "core_answer": _clip(identity.core_answer),
            "target_experience": _clip(identity.target_experience.primary, 200),
            "want": _clip(identity.central_engine.want), "stakes": _clip(identity.central_engine.stakes),
            "series_commitment_ids": list(book.direction.series_commitment_ids),
            "accepted_against_series_revision": against,
            "current_series_revision": current,
            "freshness": ("current" if against is not None and current is not None and against == current
                          else "series_direction_revised" if against is not None and current is not None
                          else "unknown"),
        })
    result["books"] = books
    current_proposals = {result["series"].get("proposal_id")} | {b.get("proposal_id") for b in books}
    result["other_proposals"] = {
        key: len(ids - current_proposals) for key, ids in proposal_ids.items()
    }
    result["state"] = ("accepted" if result["series"].get("state") == "accepted"
                       or any(b["state"] == "accepted" for b in books)
                       else "unverified" if result["series"].get("state") == "unverified"
                       or any(b["state"] == "unverified" for b in books)
                       else "proposals_only")
    return result


def _working_books(store: CanvasStore) -> dict[str, Any]:
    owner = "working_book_architecture"
    base: dict[str, Any] = {
        "owner": owner, "label": "Working Book architectures",
        "path": f".auteur/beginner/studio/canvases/{store.canvas_id}/architecture/books",
        "authority": "working_noncanonical",
        "authority_note": ("Book-level working proposals for this canvas. They reference this working "
                           "Architecture by node id; nothing in them is accepted, and no Book operation "
                           "can accept anything."),
        "owner_route": "python -m auteur.series.working_book_architecture --project <project> --canvas "
                       f"{store.canvas_id} book-resume --book <n>",
    }
    books: list[dict[str, Any]] = []
    for number in book_numbers(store):
        rel = f"{base['path']}/{number}/current.json"
        try:
            view = book_series_references(store, number)
        except (OSError, UnicodeError, ValueError, ValidationError, KeyError, TypeError) as exc:
            books.append({"state": "unreadable", "book_number": number, "path": rel, "reason": _first_line(exc)})
            continue
        refs = []
        for item in view["references"]:
            refs.append({**item,
                         "elements": [{**e, "text": _clip(e["text"])} for e in item["elements"]],
                         "edges": [{**e, "function": _clip(e["function"], 400)} for e in item["edges"]]})
        books.append({
            "state": "working", "book_number": number,
            "title": _clip(view["title"], 200), "question": _clip(view["question"]),
            "pressure": _clip(view["pressure"]),
            "freshness": view["freshness"], "series_changed": view["series_changed"],
            "source_changed": view["source_changed"], "semantic_impact": view["semantic_impact"],
            "revision_number": view["revision_number"], "open_author_decisions": view["open_author_decisions"],
            "source": _src(owner, rel, None, artifact=f"book-{number}", revision=view["revision_number"],
                           content_hash=view.get("content_sha256")),
            "written_against_request": view["series_request_sha256"],
            "references": refs,
        })
    return {**base, "state": "available" if books else "absent", "books": books}


def project_series_context(project_root: Path, canvas_id: str) -> dict[str, Any]:
    """Project the Book and Series plans this canvas and its project keep, read-only.

    Raises FileNotFoundError when the canvas does not exist.
    """
    root = Path(project_root).resolve()
    store = CanvasStore(root, canvas_id)
    store.load()
    working = _working_books(store)
    plan = _series_plan(root)
    direction = _series_direction(root)
    sources = [working, plan, direction]
    available = [s for s in sources if s["state"] not in {"absent"}]
    fingerprint = json.dumps([
        [(b.get("book_number"), b.get("state"), b.get("source", {}).get("content_hash"), b.get("freshness"),
          b.get("semantic_impact")) for b in working["books"]],
        plan.get("state"), plan.get("content_hash"), plan.get("reason"),
        direction.get("state"),
        (direction.get("series") or {}).get("revision"), (direction.get("series") or {}).get("content_hash"),
        [(b.get("book_number"), b.get("state"), b.get("revision"), b.get("content_hash"))
         for b in direction.get("books", [])],
        direction.get("other_proposals"),
    ], sort_keys=True)
    return {
        "schema": SCHEMA,
        "authority": "read_only_owner_records",
        "canvas_id": store.canvas_id,
        "scope_note": ("The Series plan and the Directions are kept for the project this Studio serves. Being in "
                       "the same project does not make them the plan of any one working Architecture."),
        "architecture_link": {"recorded": False, "statement": NO_LINK,
                              "applies_to": ["series_plan", "series_direction"]},
        "separate_owners_note": ("The Series plan and the Series and Book Directions are separate planning records "
                                 "with their own owners; nothing records that they describe the same Series.")
        if plan["state"] != "absent" and direction["state"] != "absent" else None,
        "available": bool(available),
        "version": "sha256:" + hashlib.sha256(fingerprint.encode("utf-8")).hexdigest(),
        "sources": {"working_books": working, "series_plan": plan, "series_direction": direction},
    }
