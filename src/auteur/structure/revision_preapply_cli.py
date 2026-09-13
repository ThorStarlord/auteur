"""Specialized CLI for Structure revision planning, preview, and reassessment."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from auteur.structure.revision_service import RevisionService


def parse_revision_preapply_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="auteur structure revision")
    sub = parser.add_subparsers(dest="revision_command", required=True)

    plan = sub.add_parser("plan", help="Create a non-applying revision plan from a selected proposal.")
    plan.add_argument("--proposal", type=Path, required=True)
    plan.add_argument("--project", type=Path, default=Path("."))
    plan.add_argument("--json", action="store_true")

    validate = sub.add_parser("validate", help="Validate revision-plan preconditions without applying it.")
    validate.add_argument("plan_id")
    validate.add_argument("--project", type=Path, default=Path("."))
    validate.add_argument("--json", action="store_true")

    preview = sub.add_parser("preview", help="Preview intended and downstream revision consequences without applying.")
    preview.add_argument("plan_id")
    preview.add_argument("--project", type=Path, default=Path("."))
    preview.add_argument("--json", action="store_true")

    reassess = sub.add_parser("reassess", help="Re-run exact diagnostic evidence after a fully applied revision.")
    reassess.add_argument("application_id")
    reassess.add_argument("--project", type=Path, default=Path("."))
    reassess.add_argument("--json", action="store_true")
    return parser.parse_args(argv)


def _plan_payload(plan) -> dict[str, object]:
    return {
        "plan_id": plan.plan_id,
        "state": plan.state.value,
        "targets": list(plan.scope.target_artifact_ids),
        "operation_count": len(plan.operations),
        "operations": [op.model_dump(mode="json") for op in plan.operations],
        "authority_status": "REVISION PLAN / NOT APPLIED",
        "mutates_story": False,
        "validate_command": f"auteur structure revision validate {plan.plan_id} --project .",
    }


def dispatch_revision_preapply_argv(argv: list[str]) -> int:
    args = parse_revision_preapply_args(argv)
    try:
        if args.revision_command == "preview":
            from auteur.structure.revision_preview import build_revision_preview

            payload = build_revision_preview(args.project, args.plan_id)
        elif args.revision_command == "reassess":
            from auteur.structure.revision_reassessment import build_revision_reassessment

            payload = build_revision_reassessment(args.project, args.application_id)
        else:
            service = RevisionService(args.project)
            if args.revision_command == "plan":
                proposal = args.proposal.resolve() if args.proposal.is_absolute() else (args.project.resolve() / args.proposal).resolve()
                if not proposal.is_relative_to(args.project.resolve()):
                    raise ValueError("Revision proposal path must stay inside the selected project")
                plan = service.plan(proposal_path=proposal)
                payload = _plan_payload(plan)
            else:
                state, preconditions = service.validate(args.plan_id)
                payload = {
                    "plan_id": args.plan_id,
                    "state": state,
                    "preconditions": preconditions,
                    "authority_status": "REVISION PLAN / NOT APPLIED",
                    "mutates_story": False,
                    "ready_for_application": state == "ready",
                    "apply_command": (
                        f"auteur structure revision apply {args.plan_id} --project . --confirm"
                        if state == "ready"
                        else None
                    ),
                }
    except (ValueError, KeyError, FileNotFoundError, OSError) as exc:
        print(f"Error: {exc}", file=__import__("sys").stderr)
        return 1

    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False, default=str))
    elif args.revision_command == "plan":
        print(f"Revision plan: {payload['plan_id']}")
        print(f"State: {payload['state']}")
        print(f"Operations: {payload['operation_count']}")
        print("Status: REVISION PLAN / NOT APPLIED")
        print(f"Validate: {payload['validate_command']}")
    elif args.revision_command == "validate":
        print(f"Validation state: {payload['state']}")
        for precondition in payload["preconditions"]:  # type: ignore[union-attr]
            mark = "✓" if precondition.get("met") else "✗"
            print(f"  {mark} {precondition.get('target_id')}: {precondition.get('message', '')}")
        print("No story artifact was changed by validation.")
        if payload["apply_command"]:
            print(f"Authority-bearing next step: {payload['apply_command']}")
    elif args.revision_command == "preview":
        print(f"Narrative Change Preview: {payload['plan_id']}")
        print(f"Status: {payload['authority_status']}")
        print(f"Currentness: {payload['currentness']}")
        print(f"Direct targets: {', '.join(payload['direct_targets'])}")  # type: ignore[arg-type]
        print(f"Changed fields: {', '.join(payload['changed_fields']) or '(not field-addressable)'}")  # type: ignore[arg-type]
        print("Downstream workflow artifacts:")
        for impact in payload["definite_downstream_impacts"]:  # type: ignore[union-attr]
            print(f"  - {impact['artifact_id']}: {impact['impact_reason']}")
        print("Preview is derived; no story or revision state was changed.")
        if payload["next_command"]:
            print(f"Next step: {payload['next_command']}")
    else:
        print(f"Decision Reassessment: {payload['application_id']}")
        print(f"Status: {payload['assessment_status']}")
        if payload["source_rule"]:
            print(f"Diagnostic rule: {payload['source_rule']}")
        print(str(payload["reason"]))
        print(str(payload["claim_scope"]))
        print("Reassessment is derived/read-only; no story or revision history was changed.")
    if args.revision_command == "validate":
        return 0 if payload.get("state") == "ready" else 1
    return 0
