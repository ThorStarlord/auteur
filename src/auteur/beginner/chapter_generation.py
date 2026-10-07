"""Backend-neutral Chapter-N generation orchestration with fail-closed freshness."""

from __future__ import annotations

import hashlib
import json
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from auteur.bard import MAX_TOKENS, TEMPERATURE, postprocess_draft, render_bard_prompt
from auteur.host_agent import (
    HostAgentResponse,
    build_host_agent_request,
    load_host_agent_request,
    validate_host_agent_response,
    write_host_agent_request,
    write_host_agent_response,
)
from auteur.project import Project

from .continuation import build_contextual_chapter_plan


@dataclass(frozen=True)
class PreparedChapterGeneration:
    chapter_index: int
    request_id: str
    request_sha256: str
    source_fingerprint: str
    request_path: Path
    receipt_path: Path


@dataclass(frozen=True)
class CompletedChapterGeneration:
    chapter_index: int
    draft_version: int
    draft_path: Path
    metadata_path: Path
    response_path: Path
    candidate_sha256: str
    provider: str
    elapsed_seconds: float | None


def _safe_command_id(command_id: str) -> str:
    value = command_id.strip()
    if not value or not re.fullmatch(r"[A-Za-z0-9._-]+", value):
        raise ValueError("command_id must be a non-empty path-safe identifier")
    return value


def _chapter_dir(root: Path, chapter_index: int) -> Path:
    padded = root / "chapters" / f"{chapter_index:02d}"
    unpadded = root / "chapters" / str(chapter_index)
    return unpadded if unpadded.is_dir() and not padded.is_dir() else padded


def _generation_dir(root: Path, chapter_index: int) -> Path:
    return root / ".auteur" / "beginner" / "chapter_generation" / f"chapter-{chapter_index:02d}"


def _read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"invalid Chapter generation artifact: {path.name}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"invalid Chapter generation artifact: {path.name}")
    return value


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    os.replace(temporary, path)


def _load_outline(root: Path, chapter_index: int) -> dict[str, Any]:
    path = _chapter_dir(root, chapter_index) / "outline.yaml"
    if not path.is_file():
        raise FileNotFoundError(f"Chapter {chapter_index} outline is required before drafting")
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"Chapter {chapter_index} outline must be a mapping")
    existing = value.get("chapter_index")
    if existing is not None and existing != chapter_index:
        raise ValueError("Chapter outline belongs to a different Chapter")
    return {**value, "scope": value.get("scope", "chapter"), "chapter_index": chapter_index}


def _render(root: Path, chapter_index: int) -> tuple[str, str, dict[str, Any], str]:
    plan = build_contextual_chapter_plan(root, chapter_index)
    if not plan.draft_handoff_ready:
        raise ValueError(f"Chapter {chapter_index} is not ready for drafting")
    author_context = plan.context.get("author_context")
    if not isinstance(author_context, dict):
        raise ValueError("Chapter-N contextual plan is missing author_context")
    if not (root / "blueprint.yaml").is_file():
        raise FileNotFoundError("accepted blueprint is required before Chapter drafting")
    if not (root / "bible.json").is_file():
        raise FileNotFoundError("accepted story state is required before Chapter-N drafting")

    project = Project.load(root)
    system, user = render_bard_prompt(
        outline=_load_outline(root, chapter_index),
        bible=project.bible,
        blueprint=project.blueprint,
        chapter_index=chapter_index,
        prior_draft=None,
        findings=None,
        author_context=author_context,
    )
    settings = {"temperature": TEMPERATURE, "max_tokens": MAX_TOKENS}
    source_fingerprint = hashlib.sha256(
        json.dumps(
            {
                "chapter_index": chapter_index,
                "system": system,
                "user": user,
                "settings": settings,
            },
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()
    return system, user, settings, source_fingerprint


def _assert_receipt_request(receipt: dict[str, Any], request: Any) -> None:
    if (
        receipt.get("candidate_id") != request.candidate_id
        or receipt.get("request_id") != request.request_id
        or receipt.get("request_sha256") != request.request_sha256
    ):
        raise ValueError("Chapter generation receipt does not match request")


def prepare_chapter_generation(
    project_root: Path,
    chapter_index: int,
    *,
    command_id: str,
) -> PreparedChapterGeneration:
    """Prepare the exact Bard request for the active host coding agent."""
    if chapter_index < 1:
        raise ValueError("chapter_index must be positive")
    command_id = _safe_command_id(command_id)
    root = Path(project_root).resolve()
    artifacts = _generation_dir(root, chapter_index)
    receipt_path = artifacts / f"{command_id}.receipt.json"
    request_path = artifacts / f"{command_id}.request.json"
    system, user, settings, source_fingerprint = _render(root, chapter_index)

    if receipt_path.is_file():
        receipt = _read_json(receipt_path)
        if receipt.get("chapter_index") != chapter_index:
            raise ValueError("Chapter generation receipt belongs to another Chapter")
        if receipt.get("source_fingerprint") != source_fingerprint:
            raise ValueError("Chapter generation request is stale; prepare a new command")
        if receipt.get("status") not in {"awaiting_host_agent", "committing", "complete"}:
            raise ValueError("Chapter generation receipt has an invalid status")
        request = load_host_agent_request(request_path)
        _assert_receipt_request(receipt, request)
    else:
        candidate_id = f"chapter-{chapter_index:02d}-{command_id}"
        request = build_host_agent_request(
            candidate_id=candidate_id,
            role="chapter_generation",
            system=system,
            user=user,
            settings=settings,
        )
        write_host_agent_request(request_path, request)
        _write_json(
            receipt_path,
            {
                "status": "awaiting_host_agent",
                "command_id": command_id,
                "chapter_index": chapter_index,
                "candidate_id": candidate_id,
                "source_fingerprint": source_fingerprint,
                "request_id": request.request_id,
                "request_sha256": request.request_sha256,
            },
        )

    return PreparedChapterGeneration(
        chapter_index=chapter_index,
        request_id=request.request_id,
        request_sha256=request.request_sha256,
        source_fingerprint=source_fingerprint,
        request_path=request_path,
        receipt_path=receipt_path,
    )


def _completed(root: Path, receipt: dict[str, Any]) -> CompletedChapterGeneration:
    chapter_index = int(receipt["chapter_index"])
    version = int(receipt["draft_version"])
    draft_path = _chapter_dir(root, chapter_index) / f"draft_v{version}.md"
    candidate_sha = str(receipt["candidate_sha256"])
    if (
        not draft_path.is_file()
        or hashlib.sha256(draft_path.read_bytes()).hexdigest() != candidate_sha
    ):
        raise RuntimeError("completed Chapter generation receipt does not match the Working draft")
    artifacts = _generation_dir(root, chapter_index)
    metadata_path = draft_path.with_suffix(".meta.json")
    response_path = artifacts / str(receipt["response_file"])
    if not metadata_path.is_file() or not response_path.is_file():
        raise RuntimeError("completed Chapter generation evidence is incomplete")
    return CompletedChapterGeneration(
        chapter_index=chapter_index,
        draft_version=version,
        draft_path=draft_path,
        metadata_path=metadata_path,
        response_path=response_path,
        candidate_sha256=candidate_sha,
        provider=str(receipt["provider"]),
        elapsed_seconds=receipt.get("elapsed_seconds"),
    )


def complete_chapter_generation(
    project_root: Path,
    chapter_index: int,
    *,
    command_id: str,
    response_payload: HostAgentResponse | dict[str, Any],
) -> CompletedChapterGeneration:
    """Validate an exact, current response and write one Working draft."""
    if chapter_index < 1:
        raise ValueError("chapter_index must be positive")
    command_id = _safe_command_id(command_id)
    root = Path(project_root).resolve()
    artifacts = _generation_dir(root, chapter_index)
    receipt_path = artifacts / f"{command_id}.receipt.json"
    request_path = artifacts / f"{command_id}.request.json"
    if not receipt_path.is_file() or not request_path.is_file():
        raise FileNotFoundError("prepare the Chapter generation request before completing it")

    receipt = _read_json(receipt_path)
    if receipt.get("chapter_index") != chapter_index:
        raise ValueError("Chapter generation receipt belongs to another Chapter")
    request = load_host_agent_request(request_path)
    _assert_receipt_request(receipt, request)
    response = validate_host_agent_response(request, response_payload)
    prose = postprocess_draft(response.text)
    if not prose:
        raise ValueError("host-agent response produced an empty Chapter")
    draft_bytes = (prose.rstrip() + "\n").encode("utf-8")
    candidate_sha = hashlib.sha256(draft_bytes).hexdigest()

    if receipt.get("status") == "complete":
        if receipt.get("candidate_sha256") != candidate_sha:
            raise ValueError("Chapter generation request already completed with a different response")
        return _completed(root, receipt)
    if receipt.get("status") not in {"awaiting_host_agent", "committing"}:
        raise ValueError("Chapter generation receipt has an invalid status")

    _, _, _, current_fingerprint = _render(root, chapter_index)
    if receipt.get("source_fingerprint") != current_fingerprint:
        raise ValueError("Chapter generation response is stale because story context changed")

    project = Project.load(root)
    response_path = artifacts / f"{command_id}.response.json"
    provider = f"{response.backend}/{response.runtime}/{response.model}"
    if receipt.get("status") == "awaiting_host_agent":
        version = project.next_draft_version(chapter_index)
        receipt = {
            **receipt,
            "status": "committing",
            "draft_version": version,
            "candidate_sha256": candidate_sha,
            "response_file": response_path.name,
            "provider": provider,
            "elapsed_seconds": response.elapsed_seconds,
        }
        _write_json(receipt_path, receipt)
    else:
        if receipt.get("candidate_sha256") != candidate_sha:
            raise ValueError("Chapter generation commit already reserved for a different response")
        version = int(receipt["draft_version"])

    draft_path = _chapter_dir(root, chapter_index) / f"draft_v{version}.md"
    if draft_path.is_file():
        if hashlib.sha256(draft_path.read_bytes()).hexdigest() != candidate_sha:
            raise RuntimeError("reserved Chapter draft version contains different Working prose")
    else:
        draft_path = project.write_draft(
            chapter_index,
            version,
            draft_bytes.decode("utf-8"),
        )
    metadata_path = draft_path.with_suffix(".meta.json")
    write_host_agent_response(response_path, response)
    metadata: dict[str, Any] = {
        "chapter_index": chapter_index,
        "draft_version": version,
        "status": "working",
        "candidate_sha256": candidate_sha,
        "generation_request_id": request.request_id,
        "generation_request_sha256": request.request_sha256,
        "generation_source_fingerprint": current_fingerprint,
        "generation_backend": response.backend,
        "generation_runtime": response.runtime,
        "generation_model": response.model,
    }
    if response.elapsed_seconds is not None:
        metadata["generation_elapsed_seconds"] = response.elapsed_seconds
    _write_json(metadata_path, metadata)
    _write_json(receipt_path, {**receipt, "status": "complete"})
    return _completed(root, _read_json(receipt_path))


__all__ = ["CompletedChapterGeneration", "PreparedChapterGeneration", "complete_chapter_generation", "prepare_chapter_generation"]
