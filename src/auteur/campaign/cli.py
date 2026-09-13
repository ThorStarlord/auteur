from __future__ import annotations

import json
from pathlib import Path

from auteur.campaign.bundle import export_bundle, inspect_bundle
from auteur.campaign.handoff import HandoffStore, resume_handoff
from auteur.campaign.inspection import inspect_campaign
from auteur.campaign.models import Campaign
from auteur.campaign.persistence import CampaignStore


def register_campaign_subcommands(sub) -> None:
    campaign = sub.add_parser("campaign", help="Persist and inspect local Campaign state.")
    commands = campaign.add_subparsers(dest="campaign_command", required=True)

    init = commands.add_parser("init", help="Create a local Campaign record.")
    init.add_argument("--project", type=Path, default=Path("."))
    init.add_argument("--campaign-id", required=True)
    init.add_argument("--project-id", required=True)
    init.add_argument("--phase", choices=["identity", "structure", "realization", "expression", "complete"], default="identity")

    for name, help_text in (("validate", "Validate persisted Campaign shape."), ("inspect", "Inspect Campaign dependencies read-only.")):
        command = commands.add_parser(name, help=help_text)
        command.add_argument("--project", type=Path, default=Path("."))
        command.add_argument("--json", action="store_true")

    handoff = commands.add_parser("handoff", help="Create an explicit resumable handoff record.")
    handoff.add_argument("--project", type=Path, default=Path("."))
    handoff.add_argument("--operation", required=True)

    resume = commands.add_parser("resume", help="Revalidate a handoff and return a plan-only result.")
    resume.add_argument("handoff_id")
    resume.add_argument("--project", type=Path, default=Path("."))
    resume.add_argument("--json", action="store_true")

    bundle = commands.add_parser("bundle", help="Export or inspect a Campaign bundle.")
    bundle_commands = bundle.add_subparsers(dest="bundle_command", required=True)
    export = bundle_commands.add_parser("export")
    export.add_argument("--project", type=Path, default=Path("."))
    export.add_argument("--output", type=Path, required=True)
    inspect = bundle_commands.add_parser("inspect")
    inspect.add_argument("bundle", type=Path)
    inspect.add_argument("--staging", type=Path, required=True)
    inspect.add_argument("--json", action="store_true")


def dispatch_campaign(args) -> int:
    project = Path(args.project)
    if args.campaign_command == "init":
        path = CampaignStore(project).save(
            Campaign(campaign_id=args.campaign_id, project_id=args.project_id, phase=args.phase)
        )
        print(path)
        return 0
    if args.campaign_command == "validate":
        campaign = CampaignStore(project).load()
        result = {"valid": True, "campaign_id": campaign.campaign_id, "findings": []}
        return _emit(result, args.json)
    if args.campaign_command == "inspect":
        campaign = CampaignStore(project).load()
        return _emit(inspect_campaign(project, campaign).model_dump(mode="json"), args.json)
    if args.campaign_command == "handoff":
        campaign = CampaignStore(project).load()
        handoff = HandoffStore(project).create(campaign, operation=args.operation)
        return _emit(handoff.model_dump(mode="json"), True)
    if args.campaign_command == "resume":
        return _emit(resume_handoff(project, args.handoff_id).model_dump(mode="json"), args.json)
    if args.campaign_command == "bundle" and args.bundle_command == "export":
        print(export_bundle(project, args.output))
        return 0
    if args.campaign_command == "bundle" and args.bundle_command == "inspect":
        return _emit(inspect_bundle(args.bundle, args.staging).model_dump(mode="json"), args.json)
    raise ValueError(f"unsupported campaign command: {args.campaign_command}")


def _emit(payload: dict, as_json: bool) -> int:
    if as_json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(payload)
    return 0
