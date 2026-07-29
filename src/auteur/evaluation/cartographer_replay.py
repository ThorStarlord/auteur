"""Capture, validation, replay, and pairing for Cartographer evaluations.

This module is deliberately outside the production Cartographer invocation
path. Replay returns stored raw output through the existing ``LLMClient``
boundary; it never contacts a provider or retries.
"""

from __future__ import annotations

import hashlib
import json
import re
from copy import deepcopy
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from auteur.cartographer import render_cartographer_prompt
from auteur.llm import LLMClient, LLMRequest, LLMResponse


class CaptureError(ValueError):
    """Base error for malformed or incompatible evaluation artifacts."""


class CaptureIntegrityError(CaptureError):
    """A stored hash does not match the artifact content."""


class ReplayMismatchError(CaptureError):
    """A replay request does not match the captured request identity."""


class SecretPolicyError(CaptureError):
    """A structurally forbidden secret-bearing field was supplied."""


class CaptureProvider(BaseModel):
    model_config = ConfigDict(extra="allow")

    name: str
    requested_model: str | None = None
    resolved_model: str | None = None
    response_id: str | None = None
    invocation_at: str | None = None
    retry_count: int = Field(default=0, ge=0)
    input_tokens: int | None = Field(default=None, ge=0)
    output_tokens: int | None = Field(default=None, ge=0)
    cost: float | None = Field(default=None, ge=0)


class CaptureRequest(BaseModel):
    model_config = ConfigDict(extra="allow")

    model: str | None = None
    temperature: float = Field(ge=0, le=2)
    max_tokens: int = Field(ge=1)


class CaptureResponse(BaseModel):
    model_config = ConfigDict(extra="allow")

    raw_text: str
    parsed_outline: dict[str, Any] | None = None
    parse_status: Literal["not_attempted", "parsed", "parse_failed", "validation_failed"]
    error: str | None = None


class CaptureIntegrity(BaseModel):
    model_config = ConfigDict(extra="allow")

    prompt_hash: str
    planning_call_hash: str
    raw_response_hash: str
    parsed_output_hash: str | None = None
    artifact_hash: str
    redaction_status: Literal["allowlisted"] = "allowlisted"


class CartographerCaptureV1(BaseModel):
    """Immutable evidence for one Cartographer request/response interaction."""

    model_config = ConfigDict(extra="allow")

    artifact_type: Literal["cartographer_evaluation_capture"] = (
        "cartographer_evaluation_capture"
    )
    schema_version: Literal[1] = 1
    case_id: str
    pair_id: str
    condition: Literal["control", "treatment"]
    repetition: int = Field(ge=0)
    created_at: str
    source_blueprint_hash: str
    source_commit: str
    planning_call: dict[str, Any]
    system_prompt: str
    user_prompt: str
    profile_emotional_targets: dict[str, float] = Field(default_factory=dict)
    authored_emotional_target: str
    request: CaptureRequest
    provider: CaptureProvider
    response: CaptureResponse
    integrity: CaptureIntegrity

    @model_validator(mode="after")
    def _reject_secrets(self) -> "CartographerCaptureV1":
        _reject_secret_keys(self.model_dump(mode="python"))
        return self


class CartographerEvaluationPairV1(BaseModel):
    """Manifest linking a control and treatment capture."""

    model_config = ConfigDict(extra="allow")

    artifact_type: Literal["cartographer_evaluation_pair"] = "cartographer_evaluation_pair"
    schema_version: Literal[1] = 1
    evaluation_id: str
    pair_id: str
    control_artifact: str
    treatment_artifact: str
    only_expected_input_difference: list[str]
    rubric_version: int = Field(ge=1)
    review_status: Literal["pending", "in_review", "complete"] = "pending"


class CartographerReviewRecordV1(BaseModel):
    """Subjective review kept separate from immutable capture evidence."""

    model_config = ConfigDict(extra="allow")

    artifact_type: Literal["cartographer_evaluation_review"] = "cartographer_evaluation_review"
    schema_version: Literal[1] = 1
    evaluation_id: str
    pair_id: str
    reviewer_id: str
    reviewer_type: Literal["human", "model"]
    blinded_condition_order: list[Literal["control", "treatment"]]
    rubric_version: int = Field(ge=1)
    ratings: dict[str, int]
    confidence: Literal["LOW", "MEDIUM", "HIGH"]
    rationale: str
    reviewed_at: str
    reveal_result: Literal["pending", "revealed"] = "pending"

    @model_validator(mode="after")
    def _ratings_in_range(self) -> "CartographerReviewRecordV1":
        if any(value < -2 or value > 2 for value in self.ratings.values()):
            raise ValueError("review ratings must be between -2 and 2")
        return self


_SECRET_KEY = re.compile(
    r"(?:api[_-]?key|authorization|access[_-]?token|refresh[_-]?token|"
    r"secret|password|cookie|credential)",
    re.IGNORECASE,
)


def canonical_json(value: Any) -> bytes:
    """Return V1 canonical JSON bytes: UTF-8, sorted keys, compact separators."""
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def sha256_hash(value: Any) -> str:
    """Hash canonical JSON bytes with the repository's ``sha256:`` prefix."""
    return "sha256:" + hashlib.sha256(canonical_json(value)).hexdigest()


def prompt_hash(system_prompt: str, user_prompt: str) -> str:
    return sha256_hash({"system_prompt": system_prompt, "user_prompt": user_prompt})


def planning_call_hash(planning_call: dict[str, Any]) -> str:
    return sha256_hash(planning_call)


def raw_response_hash(raw_text: str) -> str:
    return sha256_hash({"raw_text": raw_text})


def parsed_output_hash(parsed_outline: dict[str, Any]) -> str:
    return sha256_hash(parsed_outline)


def _artifact_hash_payload(data: dict[str, Any]) -> dict[str, Any]:
    payload = deepcopy(data)
    integrity = dict(payload["integrity"])
    integrity.pop("artifact_hash", None)
    payload["integrity"] = integrity
    return payload


def artifact_hash(data: dict[str, Any]) -> str:
    return sha256_hash(_artifact_hash_payload(data))


def _reject_secret_keys(value: Any) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            if _SECRET_KEY.search(str(key)):
                raise SecretPolicyError(f"forbidden metadata field: {key}")
            _reject_secret_keys(child)
    elif isinstance(value, list):
        for child in value:
            _reject_secret_keys(child)


def validate_capture(capture: CartographerCaptureV1) -> CartographerCaptureV1:
    """Verify all V1 integrity hashes without rewriting the artifact."""
    data = capture.model_dump(mode="json")
    expected = capture.integrity
    if expected.prompt_hash != prompt_hash(capture.system_prompt, capture.user_prompt):
        raise CaptureIntegrityError("prompt hash mismatch")
    if expected.planning_call_hash != planning_call_hash(capture.planning_call):
        raise CaptureIntegrityError("PlanningCall hash mismatch")
    if expected.raw_response_hash != raw_response_hash(capture.response.raw_text):
        raise CaptureIntegrityError("raw response hash mismatch")
    if capture.response.parsed_outline is not None:
        actual = parsed_output_hash(capture.response.parsed_outline)
        if expected.parsed_output_hash != actual:
            raise CaptureIntegrityError("parsed output hash mismatch")
    elif expected.parsed_output_hash is not None:
        raise CaptureIntegrityError("parsed output hash present without parsed output")
    if expected.artifact_hash != artifact_hash(data):
        raise CaptureIntegrityError("artifact hash mismatch")
    return capture


def load_capture(path: str | Path) -> CartographerCaptureV1:
    """Load, validate, and integrity-check one UTF-8 JSON capture."""
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise CaptureError("malformed capture JSON") from exc
    capture = CartographerCaptureV1.model_validate(data)
    return validate_capture(capture)


def write_capture(capture: CartographerCaptureV1, path: str | Path) -> None:
    """Write an already validated capture without changing its content."""
    validate_capture(capture)
    Path(path).write_bytes(canonical_json(capture.model_dump(mode="json")) + b"\n")


def _request_identity(request: LLMRequest) -> dict[str, Any]:
    # Prompt identity is checked separately; these are the current request
    # fields exposed to the provider boundary.
    return {
        "model": request.model,
        "temperature": request.temperature,
        "max_tokens": request.max_tokens,
    }


class ReplayLLMClient:
    """No-network LLM client returning one captured raw response exactly."""

    def __init__(self, capture: CartographerCaptureV1):
        self._capture = validate_capture(capture)

    def complete(self, req: LLMRequest) -> LLMResponse:
        captured_request = self._capture.request.model_dump(mode="json")
        actual_request = _request_identity(req)
        differences = _different_paths(captured_request, actual_request)
        if differences:
            raise ReplayMismatchError("request mismatch: " + ", ".join(differences))
        if self._capture.integrity.prompt_hash != prompt_hash(
            req.system, req.user
        ):
            raise ReplayMismatchError("prompt hash mismatch")
        return LLMResponse(
            text=self._capture.response.raw_text,
            input_tokens=self._capture.provider.input_tokens or 0,
            output_tokens=self._capture.provider.output_tokens or 0,
        )


def _different_paths(left: Any, right: Any, path: str = "") -> list[str]:
    if isinstance(left, dict) and isinstance(right, dict):
        paths: list[str] = []
        for key in sorted(set(left) | set(right)):
            child = f"{path}.{key}" if path else str(key)
            if key not in left or key not in right:
                paths.append(child)
            else:
                paths.extend(_different_paths(left[key], right[key], child))
        return paths
    return [] if left == right else [path or "<root>"]


def validate_pair(
    pair: CartographerEvaluationPairV1,
    control: CartographerCaptureV1,
    treatment: CartographerCaptureV1,
) -> None:
    """Validate the narrow approved control/treatment difference."""
    validate_capture(control)
    validate_capture(treatment)
    if control.pair_id != pair.pair_id or treatment.pair_id != pair.pair_id:
        raise CaptureError("pair ID mismatch")
    if control.condition != "control" or treatment.condition != "treatment":
        raise CaptureError("capture conditions must be control and treatment")

    left = dict(control.planning_call)
    right = dict(treatment.planning_call)
    left.pop("profile_emotional_targets", None)
    right.pop("profile_emotional_targets", None)
    differences = _different_paths(left, right)
    if differences:
        raise CaptureError("unexpected pair input drift: " + ", ".join(differences))
    for field in (
        "source_blueprint_hash",
        "authored_emotional_target",
        "system_prompt",
        "source_commit",
    ):
        if getattr(control, field) != getattr(treatment, field):
            raise CaptureError(f"unexpected pair drift: {field}")
    if control.request != treatment.request or control.provider != treatment.provider:
        raise CaptureError("provider or request settings differ")
    control_system, control_user = _render_from_planning_call(control.planning_call)
    treatment_system, treatment_user = _render_from_planning_call(treatment.planning_call)
    if control.system_prompt != control_system or treatment.system_prompt != treatment_system:
        raise CaptureError("stored system prompt does not match current renderer")
    if _remove_profile_section(control.user_prompt) != _remove_profile_section(treatment.user_prompt):
        raise CaptureError("unexpected prompt drift outside profile section")
    if control_user != control.user_prompt or treatment_user != treatment.user_prompt:
        raise CaptureError("stored user prompt does not match current renderer")
    expected = {"planning_call.profile_emotional_targets", "rendered_profile_prompt_section"}
    if set(pair.only_expected_input_difference) != expected:
        raise CaptureError("pair difference declaration is not the approved set")


def _render_from_planning_call(data: dict[str, Any]) -> tuple[str, str]:
    """Render a serialized PlanningCall through the canonical renderer."""
    from auteur.cartographer_models import PlanningCall

    return render_cartographer_prompt(PlanningCall.model_validate(data))


def _remove_profile_section(user_prompt: str) -> str:
    marker = "## ACCEPTED PROFILE EMOTIONAL TARGETS\n"
    if marker not in user_prompt:
        return re.sub(r"\n{2,}", "\n\n", user_prompt).strip()
    before, remainder = user_prompt.split(marker, 1)
    next_heading = remainder.find("\n## ")
    if next_heading == -1:
        return before.rstrip()
    return (before.rstrip() + "\n\n" + remainder[next_heading:].lstrip()).strip()
