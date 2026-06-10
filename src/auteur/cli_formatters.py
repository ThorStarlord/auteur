"""Formatter layer for CLI output — separates I/O from domain logic.

Each ``format_*`` function takes a ``HandlerResult`` (or raw data) and returns
a ready-to-print string or ``None`` (nothing to print).  No function in this
module calls ``print`` or writes to ``sys.stderr`` — that is the caller's job.
"""

from __future__ import annotations

from auteur.cli_handlers import (
    AcceptResultData,
    AuditResultData,
    CompileBlueprintData,
    DraftResultData,
    HandlerResult,
    IdentityValidateData,
    PlanData,
)


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------


def format_error(message: str, exit_code: int = 1) -> str:
    """Format an error message for stderr output."""
    return f"Error: {message}"


def format_diagnostics(diagnostics: list[dict], artifact_path: str = "") -> str:
    """Format a list of diagnostic dicts into a human-readable summary.

    Each dict should have the keys ``severity``, ``rule``, ``message``, and
    optionally ``evidence`` (list of strings).
    """
    lines: list[str] = []
    for d in diagnostics:
        label = d.get("severity", "unknown").upper()
        lines.append(f"[{label}] {d['rule']}: {d['message']}")
        evidence = d.get("evidence", [])
        for e in evidence:
            lines.append(f"       {e}")
    if artifact_path:
        lines.append(f"Diagnostics written to {artifact_path}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Per-command formatters
# ---------------------------------------------------------------------------


def format_init(result: HandlerResult) -> str | None:
    """Format the output of ``_cmd_init``."""
    if not result.is_success:
        return format_error(result.error or "init failed")
    return None  # silent success — caller prints path


def format_plan(result: HandlerResult) -> str | None:
    """Format the output of ``_cmd_plan``."""
    if not result.is_success:
        return format_error(result.error or "plan failed")
    data: PlanData = result.data
    return (
        "--- SYSTEM PROMPT ---\n"
        f"{data.system_prompt}\n"
        "\n--- USER MESSAGE ---\n"
        f"{data.user_message}"
    )


def format_structure_diagnose(result: HandlerResult) -> str | None:
    """Format the output of ``_cmd_structure_diagnose``."""
    if not result.is_success:
        return format_error(result.error or "diagnose failed")
    data = result.data
    diagnostics: list[dict] = data["diagnostics"]
    errors: list[dict] = data["errors"]
    warnings: list[dict] = data["warnings"]
    infos: list[dict] = data["infos"]

    lines: list[str] = []
    for d in diagnostics:
        label = d.get("severity", "unknown").upper()
        lines.append(f"[{label}] {d['rule']}: {d['message']}")
        evidence = d.get("evidence", [])
        for e in evidence:
            lines.append(f"       {e}")
    lines.append("---")
    lines.append(
        f"{len(diagnostics)} total: {len(errors)} error(s), "
        f"{len(warnings)} warning(s), {len(infos)} info"
    )
    return "\n".join(lines)


def format_structure_propose_repairs(result: HandlerResult) -> str | None:
    """Format the output of ``_cmd_structure_propose_repairs``.

    Returns JSON with diagnostic count, proposal count, report path,
    and proposal paths (if present in data).
    """
    if not result.is_success:
        return format_error(result.error or "propose repairs failed")
    import json
    data = result.data
    payload = {
        "diagnostic_count": data["diagnostic_count"],
        "proposal_count": data["proposal_count"],
    }
    # Optional fields that the CLI may inject after the handler
    if "report_path" in data:
        payload["report_path"] = str(data["report_path"])
    if "proposal_paths" in data:
        payload["proposal_paths"] = [str(p) for p in data["proposal_paths"]]
    return json.dumps(payload, indent=2)


def format_structure_apply(result: HandlerResult) -> str | None:
    """Format the output of ``_cmd_structure_apply``.

    Returns JSON with target path, in_place flag, and selected option id
    (plus optional fields the CLI may inject).
    """
    if not result.is_success:
        return format_error(result.error or "apply failed")
    import json
    data = result.data
    payload: dict = {
        "target_path": str(data["target_path"]),
        "in_place": data["in_place"],
        "selected_option_id": data["selected_option_id"],
    }
    if "proposal_path" in data:
        payload["proposal_path"] = str(data["proposal_path"])
    if "source_blueprint_path" in data:
        payload["source_blueprint_path"] = str(data["source_blueprint_path"])
    return json.dumps(payload, indent=2)


def format_structure_generate(result: HandlerResult) -> str | None:
    """Format the output of ``_cmd_structure_generate``.

    Three modes:
    - Symptom-based (bottom-up): returns JSON with symptom and diagnoses.
    - Diagnostics-only: returns formatted diagnostic lines.
    - Top-down generation: returns JSON proposal dict.
    """
    if not result.is_success:
        return format_error(result.error or "generate failed")
    import json
    data = result.data

    if data.get("is_diagnostics") and "diagnoses" in data:
        return json.dumps(
            {
                "symptom": data["symptom"],
                "blueprint": str(data.get("blueprint", "")),
                "diagnoses": data["diagnoses"],
            },
            indent=2,
        )

    if data.get("is_diagnostics") and "diagnostics" in data:
        lines: list[str] = []
        for d in data["diagnostics"]:
            sev = d.get("severity", "").upper()
            msg = d.get("message", "")
            lines.append(f"{sev}: {msg}")
            for ev in d.get("evidence", []):
                lines.append(f"  - {ev}")
        return "\n".join(lines)

    return json.dumps(data["proposal_dict"], indent=2)


def format_draft(result: HandlerResult) -> str | None:
    """Format the output of ``_cmd_draft`` / ``_cmd_retry``.

    Returns:
    - Accepted summary on success.
    - Conflict message on conflict.
    - ``None`` for not-accepted (caller may append guidance with
      ``format_draft_not_accepted``).
    - Error string on handler failure.
    """
    if not result.is_success and result.data is None:
        return format_error(result.error or "draft/retry failed")

    data: DraftResultData | None = result.data
    if data is None:
        return None

    if data.conflict_report is not None:
        return f"CONFLICT: {data.conflict_report}"

    if data.accepted:
        lines = [f"ACCEPTED on iteration {data.iterations}."]
        if data.final_path:
            lines.append(f"  final.md: {data.final_path}")
        lines.append(
            f"  tokens: {data.total_input_tokens} in / {data.total_output_tokens} out"
        )
        return "\n".join(lines)

    return None  # not accepted — caller adds guidance


def format_draft_not_accepted(
    result: HandlerResult,
    project_path: str,
    chapter_index: int,
) -> str | None:
    """Format the 'not accepted after N iterations' output block.

    Requires ``project_path`` and ``chapter_index`` because those are
    CLI-level concerns not stored in ``DraftResultData``.
    """
    data: DraftResultData | None = result.data
    if data is None or data.accepted or data.conflict_report:
        return None

    lines = [
        f"NOT ACCEPTED after {data.iterations} iterations.",
        "  Latest draft and validation kept on disk.",
    ]
    if data.critic_proposal_paths:
        lines.append("  Critic repair proposals written to structure/proposals/.")
        lines.append("  Review with: auteur audit --show")
    lines.append(f"  Edit manually then: auteur accept {project_path} {chapter_index}")
    lines.append(f"  Or:                  auteur retry {project_path} {chapter_index}")
    return "\n".join(lines)


def format_accept(result: HandlerResult) -> str | None:
    """Format the output of ``_cmd_accept``."""
    if not result.is_success:
        return format_error(result.error or "accept failed")
    data: AcceptResultData = result.data
    return f"Accepted {data.latest_draft_name} as final.md for chapter {data.chapter_index}."


def format_retry(result: HandlerResult) -> str | None:
    """Format the output of ``_cmd_retry`` (same shape as ``format_draft``)."""
    return format_draft(result)


def format_audit(result: HandlerResult) -> str | None:
    """Format the stdout portion of ``_cmd_audit``."""
    if not result.is_success and result.data is None:
        return format_error(result.error or "audit failed")

    data: AuditResultData | None = result.data
    if data is None:
        return None

    if not data.diagnostics and result.exit_code == 0:
        if data.error_count == 0 and data.warning_count == 0:
            return "No structural or lore issues detected."
        return "All previously detected issues have been resolved."

    from collections import defaultdict
    from auteur.structure.diagnostics import DiagnosticLayer

    _LAYER_ORDER: list[tuple[int, DiagnosticLayer, str]] = [
        (5, DiagnosticLayer.STRUCTURAL_FORCES, "Structural Forces"),
        (6, DiagnosticLayer.CARRIERS, "Carriers"),
    ]
    groups: dict[DiagnosticLayer, list] = defaultdict(list)
    for d in data.diagnostics:
        groups[d.layer].append(d)

    lines: list[str] = []
    for num, layer, name in _LAYER_ORDER:
        items = groups.get(layer)
        if not items:
            continue
        label = "finding" if len(items) == 1 else "findings"
        lines.append(f"Layer {num} \u2014 {name} ({len(items)} {label})")
        for diag in items:
            severity_label = diag.severity.value.upper()
            lines.append(f"[{severity_label}] {diag.rule}: {diag.message}")
            if diag.evidence:
                lines.append("  Evidence:")
                for ev in diag.evidence:
                    lines.append(f"    - {ev}")
            if diag.repair_options.preserve_intent:
                lines.append("  Preserve intent:")
                for opt in diag.repair_options.preserve_intent:
                    lines.append(f"    - {opt}")
            if diag.repair_options.challenge_intent:
                lines.append("  Challenge intent:")
                for opt in diag.repair_options.challenge_intent:
                    lines.append(f"    - {opt}")
            lines.append("")
        lines.append("")

    if not data.diagnostics:
        lines.append("No unresolved issues found in selected layers.")

    lines.append(
        f"Found {data.error_count} unresolved error(s), "
        f"{data.warning_count} unresolved warning(s)."
    )
    if data.artifact_path:
        lines.append(f"Audit report written to {data.artifact_path}")
    if data.resolved_proposal_count:
        label = "proposal" if data.resolved_proposal_count == 1 else "proposals"
        lines.append(
            f"{data.resolved_proposal_count} previously resolved {label} were skipped."
        )
    return "\n".join(lines)


def format_identity_validate(result: HandlerResult) -> str | None:
    """Format the output of ``_cmd_identity_validate``.

    Returns diagnostic details or a success message.
    Error output is always stderr-targeted (caller should print to stderr).
    """
    if not result.is_success:
        return format_error(result.error or "identity validation failed")

    data: IdentityValidateData = result.data
    diagnostics = data.diagnostics

    lines: list[str] = []
    if diagnostics:
        has_error = data.has_error
        for diag in diagnostics:
            severity_str = (
                diag.severity.value.upper()
                if hasattr(diag.severity, "value")
                else str(diag.severity).upper()
            )
            if severity_str == "ERROR":
                has_error = True
            lines.append(
                f"[{severity_str}] Layer: "
                f"{diag.layer.value if hasattr(diag.layer, 'value') else diag.layer}"
                f" | Rule: {diag.rule}"
            )
            lines.append(f"  Message: {diag.message}")
            if diag.evidence:
                lines.append(f"  Evidence: {diag.evidence}")
            if diag.repair_options:
                if diag.repair_options.preserve_intent:
                    lines.append(
                        f"  Preserve Intent options: {diag.repair_options.preserve_intent}"
                    )
                if diag.repair_options.challenge_intent:
                    lines.append(
                        f"  Challenge Intent options: {diag.repair_options.challenge_intent}"
                    )
            lines.append("")
        return "\n".join(lines)

    return None  # no diagnostics — caller prints success


def format_identity_validate_success(result: HandlerResult, identity_path: str) -> str | None:
    """Format the success/error verdict for identity validate.

    Separate from the diagnostic output because the CLI may need to print
    the diagnostic details (to stderr) first, then the verdict (to stdout).
    """
    if not result.is_success:
        return format_error(result.error or "identity validation failed")

    data: IdentityValidateData = result.data
    diagnostics = data.diagnostics

    if diagnostics and data.has_error:
        return f"Error: StoryIdentity {identity_path} failed structural validation."

    if diagnostics:
        return f"Success: StoryIdentity {identity_path} is valid (with warnings)."

    return f"Success: StoryIdentity {identity_path} is valid."


def format_identity_compile(result: HandlerResult) -> str | None:
    """Format the output of ``_cmd_identity_compile`` / ``_cmd_blueprint_seed``."""
    if not result.is_success:
        return format_error(result.error or "identity compile failed")
    return None  # caller prints success with paths


def format_identity_compile_success(identity_path: str, output_path: str) -> str:
    """Format the success message for identity compile."""
    return f"Success: compiled identity {identity_path} to blueprint {output_path}"


def format_cartographer_compile(result: HandlerResult) -> str | None:
    """Format the output of ``_cmd_cartographer_compile``."""
    if not result.is_success:
        return format_error(result.error or "cartographer compile failed")
    return None  # caller prints success with path


def format_cartographer_compile_success(output_path: str) -> str:
    """Format the success message for cartographer compile."""
    return f"Success: compiled outline into {output_path}"


def format_cartographer_validate(result: HandlerResult) -> str | None:
    """Format the output of ``_cmd_cartographer_validate``."""
    if not result.is_success:
        return format_error(result.error or "cartographer validate failed")
    return None  # caller prints success with path


def format_cartographer_validate_success(outline_path: str) -> str:
    """Format the success message for cartographer validate."""
    return f"Success: outline {outline_path} is valid."
