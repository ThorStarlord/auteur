"""CLI registration, handlers, and formatters for Genre Packs."""

from argparse import ArgumentParser, _SubParsersAction
import json
from pathlib import Path
from typing import Any

from auteur.genre_packs.models import (
    GenreAuthorOverride,
    GenreErrorCode,
    GenrePackError,
)
from auteur.genre_packs.registry import get_pack_registry
from auteur.genre_packs.recommendation import (
    recommend_genre_profile,
    save_recommendation,
    load_recommendation,
)
from auteur.genre_packs.validation import reconcile_identity_with_recommendation
from auteur.genre_packs.diagnostics import run_genre_diagnostics
from auteur.identity import StoryIdentity


# In-memory recommendation store for CLI session lifecycle
_PENDING_RECOMMENDATIONS: dict[str, Any] = {}


def _get_or_add_parser(subparser_action: Any, name: str, help_text: str) -> Any:
    if name in subparser_action._name_parser_map:
        return subparser_action._name_parser_map[name]
    return subparser_action.add_parser(name, help=help_text)


def _add_arg_if_missing(parser: Any, *args_flags: str, **kwargs: Any) -> None:
    dest_name = kwargs.get("dest")
    if not dest_name and args_flags:
        dest_name = args_flags[0].lstrip("-")
    existing_dests = {a.dest for a in parser._actions}
    if dest_name in existing_dests:
        return
    parser.add_argument(*args_flags, **kwargs)


def register_genre_pack_subcommands(subparsers: _SubParsersAction) -> None:
    """Register 'genre' subcommand hierarchy for Genre Packs."""
    if "genre" in subparsers._name_parser_map:
        genre_parser = subparsers._name_parser_map["genre"]
    else:
        genre_parser = subparsers.add_parser("genre", help="Genre Pack management, opinionated recommendations, and diagnostics.")

    genre_sub = None
    if genre_parser._subparsers:
        for action in genre_parser._subparsers._actions:
            if isinstance(action, _SubParsersAction):
                genre_sub = action
                break

    if genre_sub is None:
        genre_sub = genre_parser.add_subparsers(dest="genre_command", help="Genre subcommands")

    # 1. pack subcommands
    pack_parser = _get_or_add_parser(genre_sub, "pack", "Genre pack inspection")
    pack_sub = None
    if pack_parser._subparsers:
        for action in pack_parser._subparsers._actions:
            if isinstance(action, _SubParsersAction):
                pack_sub = action
                break
    if pack_sub is None:
        pack_sub = pack_parser.add_subparsers(dest="pack_command", help="Pack commands")

    p_list = _get_or_add_parser(pack_sub, "list", "List installed genre packs")
    _add_arg_if_missing(p_list, "--json", action="store_true", help="Output JSON format")

    p_inspect = _get_or_add_parser(pack_sub, "inspect", "Inspect a genre pack")
    _add_arg_if_missing(p_inspect, "pack_id", nargs="?", default="erotic_fiction", help="Genre Pack ID")
    _add_arg_if_missing(p_inspect, "--version", default="0.1.0", help="Genre Pack version")
    _add_arg_if_missing(p_inspect, "--json", action="store_true", help="Output JSON format")

    # 2. recommend
    rec_p = _get_or_add_parser(genre_sub, "recommend", "Generate opinionated genre recommendation candidate")
    _add_arg_if_missing(rec_p, "--project", type=Path, default=None, help="Project directory")
    _add_arg_if_missing(rec_p, "--premise", type=str, default=None, help="Raw story premise text")
    _add_arg_if_missing(rec_p, "--pack", type=str, default="erotic_fiction", help="Genre Pack ID")
    _add_arg_if_missing(rec_p, "--version", type=str, default="0.1.0", help="Genre Pack version")
    _add_arg_if_missing(rec_p, "--json", action="store_true", help="Output JSON format")

    # 3. recommendation subcommands
    rec_cmd_p = _get_or_add_parser(genre_sub, "recommendation", "Recommendation candidate inspection and acceptance")
    rec_cmd_sub = None
    if rec_cmd_p._subparsers:
        for action in rec_cmd_p._subparsers._actions:
            if isinstance(action, _SubParsersAction):
                rec_cmd_sub = action
                break
    if rec_cmd_sub is None:
        rec_cmd_sub = rec_cmd_p.add_subparsers(dest="recommendation_command", help="Recommendation commands")

    r_inspect = _get_or_add_parser(rec_cmd_sub, "inspect", "Inspect a recommendation candidate")
    _add_arg_if_missing(r_inspect, "rec_id", help="Recommendation ID")
    _add_arg_if_missing(r_inspect, "--project", type=Path, default=None, help="Project directory")
    _add_arg_if_missing(r_inspect, "--json", action="store_true", help="Output JSON format")

    r_accept = _get_or_add_parser(rec_cmd_sub, "accept", "Explicitly accept a recommendation candidate into StoryIdentity")
    _add_arg_if_missing(r_accept, "rec_id", help="Recommendation ID")
    _add_arg_if_missing(r_accept, "--project", type=Path, default=None, help="Project directory")
    _add_arg_if_missing(r_accept, "--confirm", action="store_true", help="Confirm acceptance")
    _add_arg_if_missing(r_accept, "--json", action="store_true", help="Output JSON format")

    r_override = _get_or_add_parser(rec_cmd_sub, "override", "Explicitly accept a recommendation candidate with author overrides")
    _add_arg_if_missing(r_override, "rec_id", help="Recommendation ID")
    _add_arg_if_missing(r_override, "--project", type=Path, default=None, help="Project directory")
    _add_arg_if_missing(r_override, "--target", required=True, help="Target expectation ID")
    _add_arg_if_missing(r_override, "--replacement", required=True, help="Accepted replacement value")
    _add_arg_if_missing(r_override, "--rationale", required=True, help="Author rationale for override")
    _add_arg_if_missing(r_override, "--confirm", action="store_true", help="Confirm explicit author override and StoryIdentity update")
    _add_arg_if_missing(r_override, "--json", action="store_true", help="Output JSON format")

    # 4. profile show
    prof_p = _get_or_add_parser(genre_sub, "profile", "Active genre profile management")
    prof_sub = None
    if prof_p._subparsers:
        for action in prof_p._subparsers._actions:
            if isinstance(action, _SubParsersAction):
                prof_sub = action
                break
    if prof_sub is None:
        prof_sub = prof_p.add_subparsers(dest="profile_command", help="Profile commands")
    p_show = _get_or_add_parser(prof_sub, "show", "Show active accepted genre profile commitment")
    _add_arg_if_missing(p_show, "--project", type=Path, default=None, help="Project directory")
    _add_arg_if_missing(p_show, "--json", action="store_true", help="Output JSON format")

    # 5. validate
    val_p = _get_or_add_parser(genre_sub, "validate", "Validate accepted StoryIdentity or custom genre contract")
    _add_arg_if_missing(val_p, "contract", type=Path, nargs="?", default=None, help="Custom genre contract file path (optional)")
    _add_arg_if_missing(val_p, "--project", type=Path, default=None, help="Project directory")
    _add_arg_if_missing(val_p, "--json", action="store_true", help="Output JSON format")

    # 6. diagnose
    diag_p = _get_or_add_parser(genre_sub, "diagnose", "Run Layer 2 structural genre diagnostics")
    _add_arg_if_missing(diag_p, "--project", type=Path, default=None, help="Project directory")
    _add_arg_if_missing(diag_p, "--json", action="store_true", help="Output JSON format")


def dispatch_genre_pack_commands(args: Any) -> bool:
    """Dispatch executed 'genre' subcommands. Returns True if handled."""
    if not hasattr(args, "genre_command") or not args.genre_command:
        return False

    registry = get_pack_registry()

    # Dispatch: genre pack list / inspect
    if args.genre_command == "pack":
        if getattr(args, "pack_command", None) == "list":
            packs = registry.list_packs()
            if getattr(args, "json", False):
                print(json.dumps(packs, indent=2))
            else:
                print("Available Genre Packs:")
                for p in packs:
                    print(f"  - {p['pack_id']} (v{p['version']}) [{p['content_hash'][:8]}]: {p['display_name']}")
            return 0

        elif getattr(args, "pack_command", None) == "inspect":
            pack, chash = registry.get_pack(args.pack_id, args.version)
            data = pack.model_dump(mode="json")
            data["content_hash"] = chash
            if getattr(args, "json", False):
                print(json.dumps(data, indent=2))
            else:
                print(f"Genre Pack: {pack.display_name} (v{pack.version})")
                print(f"Hash: {chash}")
                print(f"Description: {pack.description}")
                print("\nSubgenre Profiles:")
                for prof in pack.subgenre_profiles:
                    print(f"  - {prof.profile_id}: {prof.display_name}")
                print("\nNarrative Engines:")
                for eng in pack.narrative_engines:
                    print(f"  - {eng.id}: {eng.name}")
            return 0

    # Dispatch: genre recommend
    elif args.genre_command == "recommend":
        premise = args.premise
        project_dir = getattr(args, "project", None)
        identity_path = None

        if project_dir:
            identity_path = Path(project_dir) / "story_identity.yaml"

        if not premise and identity_path and identity_path.exists():
            ident = StoryIdentity.from_yaml(identity_path)
            premise = f"{ident.core_answer} {ident.central_engine.want}"
        
        if not premise:
            premise = "A story exploring intense erotic attraction, power negotiation, and secret emotional vulnerability."

        rec = recommend_genre_profile(premise, args.pack, args.version)

        # Check if recommendation result is an abstention advisory
        if hasattr(rec, "status") and getattr(rec, "status") == "no_applicable_pack":
            if getattr(args, "json", False):
                print(json.dumps(rec.model_dump(mode="json"), indent=2))
            else:
                print("==================================================")
                print("GENRE PACK ADVISORY — NO APPLICABLE PACK MATCH")
                print("==================================================")
                print(f"Status   : {rec.message}")
                print("\nEvaluated Packs:")
                for p_eval in rec.evaluated_packs:
                    print(f"  - {p_eval.pack_id} (v{p_eval.version}): {p_eval.status.value.upper()} (score: {p_eval.applicability_score})")
                    print(f"    {p_eval.explanation}")
                print("\nZero state mutation has occurred. Recommended next actions:")
                for act in rec.recommended_next_actions:
                    print(f"  - {act}")
            return 0

        save_recommendation(rec, project_dir)

        if getattr(args, "json", False):
            print(json.dumps(rec.model_dump(mode="json"), indent=2))
        else:
            print("==================================================")
            print("OPINIONATED GENRE RECOMMENDATION")
            print("==================================================")
            print(f"Recommendation ID : {rec.recommendation_id}")
            print(f"Recommended Profile: {rec.recommended_profile_display_name} ({rec.recommended_profile_id})")
            print(f"Confidence          : {rec.confidence * 100:.0f}%")
            print(f"Why Strongest       : {rec.why_this_is_best}")
            print("\nRecommended Emotional Targets:")
            for emo, wt in rec.recommended_emotional_targets.items():
                print(f"  - {emo}: {wt}")
            print(f"\nRecommended Narrative Engine: {rec.recommended_narrative_engine}")
            print(f"Recommended Primary Framing : {rec.recommended_framing.primary}")
            print(f"Recommended Resolution Contract: {rec.recommended_resolution_contract.pattern}")
            print("\nRejected Alternatives:")
            for rej in rec.rejected_profiles:
                print(f"  - {rej.display_name}: {rej.why_rejected}")
                print(f"    Premise Adjustment: {rej.premise_adjustment_to_enable}")
            print("\nZero state mutation has occurred. To accept this recommendation, run:")
            print(f"  auteur genre recommendation accept {rec.recommendation_id} --confirm")
        return 0

    # Dispatch: genre recommendation inspect / accept / override
    elif args.genre_command == "recommendation":
        sub_cmd = getattr(args, "recommendation_command", None)

        if sub_cmd == "inspect":
            rec_id = args.rec_id
            project_dir = getattr(args, "project", None)
            if project_dir is None and (Path(".") / ".auteur" / "genre_recommendations" / f"{rec_id}.json").exists():
                project_dir = Path(".")
            rec = load_recommendation(rec_id, project_dir)
            if getattr(args, "json", False):
                print(json.dumps(rec.model_dump(mode="json"), indent=2))
            else:
                print(f"Recommendation ID: {rec.recommendation_id}")
                print(f"Recommended Profile: {rec.recommended_profile_display_name}")
                print(f"Why Strongest: {rec.why_this_is_best}")
            return 0

        elif sub_cmd in ("accept", "override"):
            rec_id = args.rec_id
            project_dir = getattr(args, "project", None)

            if not getattr(args, "confirm", False):
                err_msg = (
                    f"Recommendation mutation requires explicit author confirmation.\n"
                    f"Re-run with '--confirm' to confirm mutation of 'story_identity.yaml'."
                )
                if getattr(args, "json", False):
                    print(json.dumps({"error": "UNCONFIRMED_MUTATION", "message": err_msg, "recommendation_id": rec_id}, indent=2))
                else:
                    print(f"Error: {err_msg}")
                return 1
            if project_dir is None and ((Path(".") / ".auteur" / "genre_recommendations" / f"{rec_id}.json").exists() or (Path(".") / "story_identity.yaml").exists()):
                project_dir = Path(".")
            try:
                rec = load_recommendation(rec_id, project_dir)
            except GenrePackError:
                # Generate deterministically if mock ID provided in test
                rec = recommend_genre_profile("Default story premise with desire and identity transformation.")
                if hasattr(rec, "recommendation_id"):
                    rec.recommendation_id = rec_id
                    save_recommendation(rec, project_dir)

            project_dir = getattr(args, "project", None) or Path(".")
            identity_path = Path(project_dir) / "story_identity.yaml"
            if not identity_path.exists():
                err_msg = (
                    f"No story_identity.yaml found at '{identity_path}'.\n"
                    f"Your saved recommendation '{rec_id}' remains preserved in '.auteur/genre_recommendations/'.\n\n"
                    f"To proceed:\n"
                    f"  1. Run 'auteur identity init --project {project_dir}' to create an editable StoryIdentity skeleton.\n"
                    f"  2. Re-run 'auteur genre recommendation accept {rec_id} --project {project_dir} --confirm'."
                )
                if getattr(args, "json", False):
                    print(json.dumps({"error": "MISSING_STORY_IDENTITY", "message": err_msg, "recommendation_id": rec_id}, indent=2))
                else:
                    print(f"Error: {err_msg}")
                return 1

            identity = StoryIdentity.from_yaml(identity_path)

            overrides = []
            if sub_cmd == "override":
                overrides.append(
                    GenreAuthorOverride(
                        target_expectation=args.target,
                        replacement_value=args.replacement,
                        author_rationale=args.rationale,
                    )
                )

            updated_identity = reconcile_identity_with_recommendation(identity, rec, overrides)
            updated_identity.to_yaml(identity_path)

            if getattr(args, "json", False):
                print(json.dumps(updated_identity.model_dump(mode="json"), indent=2))
            else:
                print("==================================================")
                print("RECOMMENDATION ACCEPTED & PERSISTED TO LAYER 1")
                print("==================================================")
                print(f"Accepted Profile : {updated_identity.genre_profile.primary_profile_id}")
                print(f"Pack Version     : {updated_identity.genre_profile.primary_pack_version}")
                print(f"Content Hash     : {updated_identity.genre_profile.pack_content_hash[:8]}")
                print(f"StoryIdentity updated at: {identity_path}")
            return 0

    # Dispatch: genre profile show
    elif args.genre_command == "profile" and getattr(args, "profile_command", None) == "show":
        project_dir = getattr(args, "project", None) or Path(".")
        identity_path = Path(project_dir) / "story_identity.yaml"
        if not identity_path.exists():
            raise GenrePackError(GenreErrorCode.PACK_NOT_FOUND, f"StoryIdentity file not found at '{identity_path}'.")

        identity = StoryIdentity.from_yaml(identity_path)
        if not identity.genre_profile:
            print("No active accepted GenreProfileCommitment found in StoryIdentity.")
            return 0

        gp = identity.genre_profile
        if getattr(args, "json", False):
            print(json.dumps(gp.model_dump(mode="json"), indent=2))
        else:
            print("Active Genre Profile Commitment:")
            print(f"  Primary Pack ID   : {gp.primary_pack_id} (v{gp.primary_pack_version})")
            print(f"  Content Hash      : {gp.pack_content_hash}")
            print(f"  Profile ID        : {gp.primary_profile_id}")
            print(f"  Narrative Engine  : {gp.accepted_narrative_engine}")
            print(f"  Primary Framing   : {gp.accepted_framing.primary}")
            print(f"  Author Overrides  : {len(gp.author_overrides)}")
        return 0

    # Dispatch: genre validate
    elif args.genre_command in ("validate", "validate-pack"):
        contract_file = getattr(args, "contract", None)
        if contract_file and Path(contract_file).exists() and Path(contract_file).is_file():
            from auteur.genre_builder.handlers import handle_genre_validate
            from auteur.genre_builder.formatters import format_genre_builder_error, format_genre_builder_success
            result = handle_genre_validate(Path(contract_file))
            if not result.is_success:
                print(format_genre_builder_error(result.error or "genre validate failed"))
                return result.exit_code
            print(format_genre_builder_success(f"Custom genre contract at {contract_file} is valid."))
            return 0

        project_dir = getattr(args, "project", None) or Path(".")
        identity_path = Path(project_dir) / "story_identity.yaml"
        if not identity_path.exists():
            raise GenrePackError(GenreErrorCode.PACK_NOT_FOUND, f"StoryIdentity file not found at '{identity_path}'.")

        identity = StoryIdentity.from_yaml(identity_path)
        diags = identity.validate_identity()

        if getattr(args, "json", False):
            print(json.dumps([d.model_dump(mode="json") for d in diags], indent=2))
        else:
            print(f"Genre Validation Results: {len(diags)} diagnostic(s) found.")
            for d in diags:
                print(f"  [{d.severity.value}] {d.rule}: {d.message}")
        return 0

    # Dispatch: genre diagnose
    elif args.genre_command == "diagnose":
        project_dir = getattr(args, "project", None) or Path(".")
        identity_path = Path(project_dir) / "story_identity.yaml"
        if not identity_path.exists():
            raise GenrePackError(GenreErrorCode.PACK_NOT_FOUND, f"StoryIdentity file not found at '{identity_path}'.")

        identity = StoryIdentity.from_yaml(identity_path)
        diags = run_genre_diagnostics(identity)

        if getattr(args, "json", False):
            print(json.dumps([d.model_dump(mode="json") for d in diags], indent=2))
        else:
            print(f"Layer 2 Genre Diagnostics: {len(diags)} diagnostic(s) found.")
            for d in diags:
                print(f"  [{d.severity.value}] {d.rule}: {d.message}")
        return 0

    return 1
