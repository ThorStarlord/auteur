"""Reproducible, local-only S2 manuscript-first host-agent exercise.

This script stages *real* Auteur Studio requests. It NEVER invents or calls a
host model. A capable coding agent must separately read each exact request and
supply its raw JSON candidate through Auteur's existing complete-file bridge.

Every mutating subcommand operates only on an explicit disposable project.
No Story Identity, Structure, Chapter or relationship acceptance is performed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from auteur.beginner.studio_architecture import (
    apply_architecture_review,
    prepare_architecture,
    project_architecture,
)
from auteur.beginner.studio_realization import prepare_realization, project_realization
from auteur.beginner.studio_store import CanvasStore
from auteur.host_agent import _atomic_json_write

FIXTURE_SOURCE = "docs/product-validation/2026-10-25-s1-s2-agent-creative-probes.md"
MANUSCRIPT: tuple[tuple[str, str, str], ...] = (
    (
        "s2-p1", "P1 - Quayside rescue",
        "At the first harbor bell, a figure in a yellow coat cut the burning ferry's "
        "mooring rope. From the rain-soaked quay, apprentice Neri thought the "
        "figure was Mara. The figure pulled a traveler from the water and slid a "
        "brass key into his coat.",
    ),
    (
        "s2-p2", "P2 - Official account",
        "Captain Ilen told the night crew the fire had been discovered after the "
        "second bell. Beneath the wet dock, a spare mooring line was coiled and "
        "dry. The captain forbade anyone to bring the rope into his office.",
    ),
    (
        "s2-p3", "P3 - Conflicting testimony",
        "In the lighthouse office, the rescued traveler swore he had seen Mara "
        "already in the ferry's hold at the first bell. Mara said, "
        "‘At the first bell I was at the outer beacon, two miles away.’ "
        "No one in the room had a working clock.",
    ),
    (
        "s2-p4", "P4 - Ambiguous motive",
        "That evening Ilen returned a brass key to Mara. "
        "‘They will say you saved him to protect yourself,’ he said. "
        "Mara answered, ‘He was not the only person in the water.’ "
        "She did not explain whose key it was.",
    ),
)
CORRECTION_ID = "s2-c1-author-correction"
CORRECTION = (
    "Mara did not start or arrange the fire. The brass key opens a temporary "
    "shelter, not any ledger room or valuables storage. The traveler's reason "
    "for making a potentially false accusation must remain unresolved. "
    "Keep the original text of all four paragraphs."
)
CORRECTION_INSTRUCTION = (
    "Revise the working interpretation using the author correction in working "
    "note s2-c1-author-correction. Preserve manuscript P1-P4 exactly; retract "
    "contradicted hypotheses and mark any remaining explanation as UNKNOWN or "
    "a tentative, noncanonical hypothesis. Keep existing stable component IDs."
)
MANIFEST_RELATIVE = Path(".auteur") / "s2_manuscript_probe" / "manifest.json"
CORRECTION_RELATIVE = MANIFEST_RELATIVE.with_name("correction.json")
CANONICAL_PATHS = (
    "story_identity.yaml", "blueprint.yaml", "relations.yaml",
    "story_structure.yaml", "story_realization.yaml",
)


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _manifest_path(root: Path) -> Path:
    return root / MANIFEST_RELATIVE


def _correction_path(root: Path) -> Path:
    return root / CORRECTION_RELATIVE


def _correction_matches_fixture(store: CanvasStore, manifest: dict[str, Any]) -> bool:
    """Confirm BOTH the working note and separate frozen correction are intact."""
    if manifest["mode"] != "manuscript" or manifest["correction_sha256"] != _sha(CORRECTION):
        return False
    try:
        frozen = json.loads(_correction_path(store.project_root).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return False
    note = next((item for item in store.load().items if item.id == CORRECTION_ID), None)
    return bool(note and note.content == CORRECTION) and frozen == {
        "item_id": CORRECTION_ID,
        "content": CORRECTION,
        "sha256": _sha(CORRECTION),
    }


def _read_manifest(root: Path, canvas: str) -> dict[str, Any]:
    payload = json.loads(_manifest_path(root).read_text(encoding="utf-8"))
    if payload["canvas_id"] != canvas or payload["version"] != 1:
        raise ValueError("S2 manifest does not match this canvas or supported format")
    return payload


def _require_fresh_project(root: Path) -> None:
    if root.exists():
        if not root.is_dir() or any(root.iterdir()):
            raise ValueError("S2 staging requires a NEW or EMPTY disposable project directory")
    checkout = Path(__file__).resolve().parents[1]
    if root == Path.cwd().resolve() or root == checkout or checkout in root.parents:
        raise ValueError("refusing to stage inside the source repository")
    root.mkdir(parents=True, exist_ok=True)


def _items(mode: str) -> tuple[tuple[str, str, str], ...]:
    if mode == "manuscript":
        return MANUSCRIPT
    # Distinct stress fixture, not more invented facts in the literary case.
    long_text = (
        "A first account stops before identifying any culprit. " + "x" * 1100
        + " This suffix is intentionally outside the visible 1000 characters."
    )
    return tuple(
        (
            f"s2-stress-{i:02d}",
            f"Stress source {i:02d}",
            long_text if i == 1 else f"Working testimony {i:02d}; not an accepted story fact.",
        )
        for i in range(1, 26)
    )


def _source_manifest(store: CanvasStore, mode: str) -> list[dict[str, Any]]:
    canvas = store.load()
    entries = []
    for order, (ident, title, text) in enumerate(_items(mode), 1):
        actual = next((item for item in canvas.items if item.id == ident), None)
        if actual is None or actual.content != text or actual.title != title:
            raise ValueError(f"source fixture changed during staging: {ident}")
        entries.append({
            "item_id": ident,
            "source_order": order,
            "title": title,
            "sha256": _sha(text),
            "characters": len(text),
            "words": len(text.split()),
        })
    return entries


def _request_location(store: CanvasStore, stage: str, request: dict[str, Any]) -> str:
    sha = request["request_sha256"]
    folder = "architecture" if stage == "architecture" else "realization"
    return str(store.directory / folder / "requests" / sha / "request.json")


def _audit_sources(store: CanvasStore, manifest: dict[str, Any]) -> dict[str, Any]:
    canvas = store.load()
    by_id = {item.id: item for item in canvas.items}
    results = []
    for entry in manifest["sources"]:
        item = by_id.get(entry["item_id"])
        results.append({
            "item_id": entry["item_id"],
            "unchanged": bool(item and _sha(item.content) == entry["sha256"]
                              and len(item.content) == entry["characters"]),
        })
    forbidden = [name for name in CANONICAL_PATHS if (store.project_root / name).exists()]
    forbidden.extend(str(path.relative_to(store.project_root)) for path in (
        store.project_root / "chapters"
    ).glob("*/final.md"))
    return {
        "source_items": results,
        "original_prose_unchanged": all(r["unchanged"] for r in results),
        "unexpected_accepted_story_artifacts": sorted(forbidden),
        "working_canvas_revision": canvas.revision,
    }


def stage(root: Path, canvas_id: str, *, mode: str) -> dict[str, Any]:
    """Create only a disposable working canvas and a real Architecture request."""
    _require_fresh_project(root)
    store = CanvasStore(root, canvas_id)
    store.create()
    for index, (ident, title, prose) in enumerate(_items(mode), 1):
        current = store.load()
        store.apply(
            "create-item", expected_revision=current.revision,
            command_id=f"stage-{index:02d}",
            payload={
                "item": {
                    "id": ident, "kind": "scene", "title": title,
                    "content": prose, "group": "S2 source excerpts",
                },
                "position": {"x": 35 + index * 8, "y": 40 + index * 9},
            },
        )
    prepared = prepare_architecture(store)
    req = prepared["request"]
    user = json.loads(req["user"])
    working = user["working_context"]
    if working.get("working_source_format") != 2:
        raise ValueError("expected S2 source-format-2 working packet")
    manifest = {
        "version": 1, "fixture": "s2-ferry-p1-p4" if mode == "manuscript" else "s2-omissions",
        "mode": mode, "canvas_id": canvas_id, "source_document": FIXTURE_SOURCE,
        "sources": _source_manifest(store, mode),
        "correction_id": CORRECTION_ID if mode == "manuscript" else None,
        "correction_sha256": _sha(CORRECTION) if mode == "manuscript" else None,
        "initial_request_sha256": req["request_sha256"],
        "accepted_story_authority": False,
    }
    _atomic_json_write(_manifest_path(root), manifest)
    return {
        "stage": "architecture_request_staged_not_executed",
        "fixture": manifest["fixture"],
        "request_path": _request_location(store, "architecture", req),
        "request_id": req["request_id"],
        "request_sha256": req["request_sha256"],
        "working_source_format": working["working_source_format"],
        "visible_item_count": len(working["working_items"]),
        "omitted_working_item_count": working["omitted_working_item_count"],
        "correction_visible_to_agent": False,
        **_audit_sources(store, manifest),
    }


def correct(root: Path, canvas_id: str) -> dict[str, Any]:
    """Introduce C1 only AFTER a real candidate has completed in this scratch."""
    store = CanvasStore(root, canvas_id)
    manifest = _read_manifest(root, canvas_id)
    if manifest["mode"] != "manuscript":
        raise ValueError("author correction applies only to the four-paragraph fixture")
    audit = _audit_sources(store, manifest)
    if not audit["original_prose_unchanged"] or audit["unexpected_accepted_story_artifacts"]:
        raise ValueError("source or accepted-story invariant failed; correction not staged")
    if project_architecture(store)["status"] != "ready":
        raise ValueError("complete the first Architecture request before revealing C1")
    if any(item.id == CORRECTION_ID for item in store.load().items) or _correction_path(root).exists():
        raise ValueError("C1 already inserted or frozen; use the existing pending revision")
    current = store.load()
    store.apply(
        "create-item", expected_revision=current.revision, command_id="reveal-c1",
        payload={
            "item": {
                "id": CORRECTION_ID, "kind": "note",
                "title": "C1 - Author correction (working only)",
                "content": CORRECTION, "group": "Author correction",
            },
            "position": {"x": 180, "y": 90},
        },
    )
    _atomic_json_write(_correction_path(root), {
        "item_id": CORRECTION_ID, "content": CORRECTION,
        "sha256": _sha(CORRECTION),
    })
    prepared = prepare_architecture(store, CORRECTION_INSTRUCTION)
    req = prepared["request"]
    return {
        "stage": "architecture_revision_staged_not_executed",
        "request_path": _request_location(store, "architecture", req),
        "request_id": req["request_id"], "request_sha256": req["request_sha256"],
        "correction_id": CORRECTION_ID,
        "correction_sha256": _sha(CORRECTION),
        "correction_file": str(_correction_path(root)),
        "correction_visible_to_agent": True,
        **_audit_sources(store, manifest),
    }


def apply_working_review(root: Path, canvas_id: str) -> dict[str, Any]:
    """Explicitly apply a completed review to the disposable WORKING architecture."""
    store = CanvasStore(root, canvas_id)
    manifest = _read_manifest(root, canvas_id)
    state = project_architecture(store)
    if state["status"] != "review_ready":
        raise ValueError("no completed working Architecture review to apply")
    if not _audit_sources(store, manifest)["original_prose_unchanged"]:
        raise ValueError("the original manuscript changed")
    if not _correction_matches_fixture(store, manifest):
        raise ValueError("the frozen author correction was changed or is missing")
    sha = state["review"]["request_sha256"]
    result = apply_architecture_review(store, sha)
    return {
        "stage": "working_architecture_review_applied_not_canon",
        "architecture_status": result["status"], "request_sha256": sha,
        **_audit_sources(store, manifest),
    }


def prepare_concrete(root: Path, canvas_id: str, focus: str) -> dict[str, Any]:
    """Stage a noncanonical Realization focus on a current working architecture."""
    store = CanvasStore(root, canvas_id)
    manifest = _read_manifest(root, canvas_id)
    if project_architecture(store)["status"] != "ready":
        raise ValueError("a current working Architecture candidate is required")
    audit = _audit_sources(store, manifest)
    if not audit["original_prose_unchanged"] or audit["unexpected_accepted_story_artifacts"]:
        raise ValueError("original manuscript or accepted-story invariant failed")
    if manifest["mode"] == "manuscript" and not _correction_matches_fixture(store, manifest):
        raise ValueError("complete the frozen author correction before Realization")
    prepared = prepare_realization(store, [focus])
    req = prepared["request"]
    return {
        "stage": "realization_request_staged_not_executed",
        "request_path": _request_location(store, "realization", req),
        "focus_id": focus, "request_sha256": req["request_sha256"],
        "request_id": req["request_id"],
        **audit,
    }


def audit(root: Path, canvas_id: str) -> dict[str, Any]:
    """Inspect immutable sources and existing owners; never claim model quality."""
    store = CanvasStore(root, canvas_id)
    manifest = _read_manifest(root, canvas_id)
    architecture = project_architecture(store)
    # Do not project Realization until Architecture exists; absent is not failure.
    realization_status = "not_started"
    if architecture["candidate"]:
        realization_status = project_realization(store)["status"]
    correction = next(
        (item for item in store.load().items if item.id == CORRECTION_ID), None
    )
    return {
        "fixture": manifest["fixture"], "canvas_id": canvas_id,
        "architecture_status": architecture["status"],
        "realization_status": realization_status,
        "initial_request_sha256": manifest["initial_request_sha256"],
        "correction_visible_to_agent": correction is not None,
        "correction_matches_fixture": _correction_matches_fixture(store, manifest),
        "correction_file_present": _correction_path(root).is_file(),
        "host_model_execution": "not_attested_by_fixture_driver",
        **_audit_sources(store, manifest),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "action",
        choices=("stage", "stress", "correct", "apply-working-review",
                 "prepare-realization", "audit"),
    )
    parser.add_argument("--project", type=Path, required=True,
                        help="A NEW disposable Auteur project root for stage/stress")
    parser.add_argument("--canvas", default="s2-manuscript",
                        help="A safe local Studio canvas identifier")
    parser.add_argument("--focus", help="Existing Architecture node ID for Realization")
    args = parser.parse_args(argv)
    root = args.project.resolve()
    if args.action in ("stage", "stress"):
        result = stage(root, args.canvas,
                       mode="manuscript" if args.action == "stage" else "stress")
    elif args.action == "correct":
        result = correct(root, args.canvas)
    elif args.action == "apply-working-review":
        result = apply_working_review(root, args.canvas)
    elif args.action == "prepare-realization":
        if not args.focus:
            parser.error("--focus must name an existing Architecture node")
        result = prepare_concrete(root, args.canvas, args.focus)
    else:
        result = audit(root, args.canvas)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
