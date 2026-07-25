"""Auteur CLI dispatch — handler dispatch logic."""

from __future__ import annotations

import argparse, datetime, hashlib, json, shutil, sys
from pathlib import Path
import yaml

from auteur.cli_parser import build_parser, _pilot_artifact_type, _pilot_project_root


from auteur.blueprint import StoryBlueprint
from auteur.cli_formatters import (
    format_accept, format_audit, format_cartographer_compile,
    format_cartographer_compile_success, format_cartographer_validate,
    format_cartographer_validate_success, format_draft, format_draft_not_accepted,
    format_error, format_identity_compile, format_identity_compile_success,
    format_identity_recommend, format_identity_validate, format_identity_validate_success, format_init,
    format_plan, format_publish, format_retry, format_state_canon,
    format_state_check, format_state_confirm, format_state_prepare,
    format_state_update, format_structure_apply, format_structure_diagnose,
    format_structure_generate, format_structure_propose_repairs,
)
from auteur.cli_handlers import (
    IdentityValidateData, PublishData, RecommendOpenEndedData,
    RecommendOpinionatedData, StateCanonData, StateCheckData,
    StateConfirmData, StatePrepareData, StateUpdateData,
    handle_accept, handle_audit,
    handle_audit_resolve_proposal, handle_cartographer_compile,
    handle_cartographer_validate, handle_compile_to_blueprint, handle_draft,
    handle_identity_promote, handle_identity_recommend,
    handle_identity_validate, handle_init, handle_plan, handle_publish, handle_retry,
    handle_state_canon, handle_state_check, handle_state_confirm,
    handle_state_prepare, handle_state_update,
    handle_structure_apply, handle_structure_diagnose,
    handle_structure_generate, handle_structure_propose_repairs,
)
from auteur.cli_serializers import (
    serialize_audit, serialize_compile_blueprint, serialize_identity_openended,
    serialize_identity_opinionated, serialize_identity_promote,
    serialize_identity_validate, serialize_publish, serialize_state_check,
    serialize_state_confirm, serialize_state_prepare, serialize_state_update,
    serialize_story_discovery, serialize_structure_diagnose,
    serialize_structure_generate_text, serialize_structure_propose_repairs,
)
from auteur.narrative_blueprint.cli_blueprint import handle_blueprint_init, handle_blueprint_list
from auteur.narrative_orchestration.cli_orchestration import (
    handle_orchestration_seed,
    handle_orchestration_validate,
    handle_orchestration_graph,
    handle_orchestration_status,
)
from auteur.narrative_realization.cli_realization import (
    handle_realization_seed,
    handle_realization_validate,
    handle_realization_inspect,
    handle_realization_graph,
)
from auteur.project import Project
from auteur.structure.proposals import StructureProposal

_err = lambda m: print(format_error(m), file=sys.stderr)


def _handle_reasoning_book(project: Path, json_output: bool = False) -> int:
    """Run Book Manuscript reasoning and display findings."""
    from auteur.reasoning.runtime import CriticRegistry, ReasoningRuntime, RuntimeRequest
    from auteur.reasoning.registrar import register_all_builtins

    report_dir = project / ".auteur" / "reasoning"
    registry = CriticRegistry()
    register_all_builtins(registry)
    runtime = ReasoningRuntime(registry, report_dir)

    request = RuntimeRequest(
        request_id="book_reasoning",
        critic_ids=["book.manuscript"],
        inputs={"project": project},
    )
    result = runtime.run(request)
    outcomes = result.outcomes

    if json_output:
        out: list[dict[str, object]] = []
        for o in outcomes:
            entry: dict[str, object] = {
                "critic_id": o.critic_id,
                "version": o.version,
                "status": o.status.value,
            }
            if o.reason:
                entry["reason"] = o.reason
            if o.error:
                entry["error"] = o.error
            if o.report_id:
                report_path = report_dir / f"{o.report_id}.json"
                if report_path.exists():
                    import json as _json
                    entry["report"] = _json.loads(report_path.read_text(encoding="utf-8"))
            out.append(entry)
        import json as _json
        print(_json.dumps(out, indent=2, default=str))
        return 0

    # Human-readable output
    for o in outcomes:
        print(f"Critic: {o.critic_id} ({o.version})")
        print(f"  Status: {o.status.value}")
        if o.status.value == "failed":
            print(f"  Error: {o.error or o.reason or 'unknown'}")
            continue
        if o.report_id:
            report_path = report_dir / f"{o.report_id}.json"
            if report_path.exists():
                import json as _json
                report = _json.loads(report_path.read_text(encoding="utf-8"))
                findings = report.get("findings", [])
                if not findings:
                    print("  No findings.")
                for fi, f in enumerate(findings, 1):
                    severity = f.get("severity", "info")
                    print(f"  {fi}. [{severity}] {f.get('message', '(no message)')}")
                    evidence = f.get("evidence", {})
                    if evidence:
                        for k, v in evidence.items():
                            if v:
                                print(f"     {k}: {v}")
                    recs = f.get("recommendations", [])
                    if recs:
                        print("     Recommendations:")
                        for r in recs:
                            print(f"       - {r}")

    return 0

def _write_blueprint_markdown(bp: Any, path: Path) -> None:
    """Render a StoryBlueprint to a readable Markdown document."""
    lines: list[str] = []
    data = bp.model_dump(mode="json") if hasattr(bp, "model_dump") else bp
    if isinstance(data, dict):
        # Identity section
        ident = data.get("identity", {}) or data.get("project_identity", {})
        if ident:
            lines.append("# Story Identity")
            for key, val in ident.items():
                if isinstance(val, dict):
                    lines.append(f"\n## {key.replace('_', ' ').title()}")
                    for sk, sv in val.items():
                        if isinstance(sv, (list, dict)):
                            continue
                        lines.append(f"- **{sk.replace('_', ' ').title()}**: {sv}")
                elif not isinstance(val, (list, dict)):
                    lines.append(f"- **{key.replace('_', ' ').title()}**: {val}")

        # Structure section
        struct = data.get("structure", {}) or data.get("structural_constants", {})
        if struct:
            lines.append("\n# Structural Constants")
            for key, val in struct.items():
                if isinstance(val, dict):
                    lines.append(f"\n## {key.replace('_', ' ').title()}")
                    for sk, sv in val.items():
                        if not isinstance(sv, (list, dict)):
                            lines.append(f"- **{sk.replace('_', ' ').title()}**: {sv}")
                elif not isinstance(val, (list, dict)):
                    lines.append(f"- **{key.replace('_', ' ').title()}**: {val}")

        # Characters section
        chars = data.get("characters", [])
        if chars:
            lines.append("\n# Characters")
            for ch in chars:
                name = ch.get("name", ch.get("role", "Unknown"))
                lines.append(f"\n## {name}")
                for key, val in ch.items():
                    if key == "name":
                        continue
                    if isinstance(val, (list, dict)):
                        continue
                    lines.append(f"- **{key.replace('_', ' ').title()}**: {val}")

        # Contract section
        contract = data.get("contract", {}) or data.get("author_audience_contract", {})
        if contract:
            lines.append("\n# Author-Audience Contract")
            for key, val in contract.items():
                if isinstance(val, dict):
                    lines.append(f"\n## {key.replace('_', ' ').title()}")
                    for sk, sv in val.items():
                        if not isinstance(sv, (list, dict)):
                            lines.append(f"- **{sk.replace('_', ' ').title()}**: {sv}")
                elif not isinstance(val, (list, dict)):
                    lines.append(f"- **{key.replace('_', ' ').title()}**: {val}")

        # Theme section
        theme = data.get("theme", {}) or data.get("thematic_core", {})
        if theme:
            lines.append("\n# Theme")
            for key, val in theme.items():
                if isinstance(val, dict):
                    lines.append(f"\n## {key.replace('_', ' ').title()}")
                    for sk, sv in val.items():
                        if not isinstance(sv, (list, dict)):
                            lines.append(f"- **{sk.replace('_', ' ').title()}**: {sv}")
                elif not isinstance(val, (list, dict)):
                    lines.append(f"- **{key.replace('_', ' ').title()}**: {val}")

        # Remaining top-level fields
        top_level_keys = ["identity", "project_identity", "structure", "structural_constants",
                          "characters", "contract", "author_audience_contract", "theme", "thematic_core",
                          "story_engine", "tension_waveform", "emotional_design"]
        for key, val in data.items():
            if key in top_level_keys:
                continue
            if isinstance(val, dict) and val:
                lines.append(f"\n# {key.replace('_', ' ').title()}")
                for sk, sv in val.items():
                    if isinstance(sv, (list, dict)):
                        continue
                    lines.append(f"- **{sk.replace('_', ' ').title()}**: {sv}")

    lines.append("\n---")
    lines.append(f"*Generated by Auteur v0.26.0 — Blueprint Publish*")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")




def dispatch(args: argparse.Namespace) -> int:
    if args.command == "reasoning":
        if args.reasoning_command == "book":
            return _handle_reasoning_book(args.project, args.json)
        from auteur.reasoning.cli import format_review, load_review
        try:
            review = load_review(args.review)
        except FileNotFoundError:
            _err(f"reasoning review not found: {args.review}")
            return 1
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            _err(f"invalid reasoning review {args.review}: {exc}")
            return 1
        if args.reasoning_command == "review":
            print(json.dumps(review, indent=2, sort_keys=True) if args.json else format_review(review))
            return 0
        # inspect: search groups first, then critic_summaries (with bare-name fallback)
        group = next((item for item in review.get("groups", []) if item.get("group_id") == args.group), None)
        if group is None:
            group = next((cs for cs in review.get("critic_summaries", [])
                          if cs.get("critic_id") == args.group
                          or cs.get("critic_id") == f"draft.{args.group}"
                          or cs.get("critic_id", "").replace("draft.", "") == args.group), None)
        if group is None:
            _err(f"reasoning group not found: {args.group}")
            return 1
        print(json.dumps(group, indent=2, sort_keys=True) if args.json else
              f"{group.get('group_id', group.get('critic_id'))}: {group.get('summary', group.get('status', '?'))}\n"
              f"Basis: {group.get('overlap_basis', '')}\n"
              f"Claims: {group.get('claim_refs', group.get('finding_count', 0))}")
        return 0
    # === status ===
    if args.command == "status":
        from auteur.status import gather_status, format_status
        status = gather_status(args.project)
        if args.json:
            print(json.dumps(status, indent=2, default=str))
        else:
            print(format_status(status, verbose=args.verbose))
        return 0
    # === publish ===
    if args.command == "publish":
        formats = [f.strip() for f in args.format.split(",")]
        css = args.css.read_text(encoding="utf-8") if args.css else None
        result = handle_publish(
            args.project,
            formats=formats,
            html_output=args.output if "html" in formats else None,
            epub_output=args.output if "epub" in formats else None,
            output_dir=args.output_dir,
            css=css,
            title_page=not args.no_title_page,
            toc=not args.no_toc,
        )
        if not result.is_success:
            _err(result.error)
            return result.exit_code
        serialize_publish(result, args.output)
        out = format_publish(result)
        if out:
            print(out)
        return 0
    # === init ===
    if args.command == "init":
        path = args.path
        if path.exists() and not args.force:
            _err(f"project path already exists: {path}")
            return 1
        if args.force and path.exists():
            if not (path / "blueprint.yaml").is_file() or not (path / "bible.json").is_file():
                _err("--force requires an existing auteur project directory (blueprint.yaml + bible.json).")
                return 1
            shutil.rmtree(path)
        try: bp = StoryBlueprint.from_yaml(args.blueprint_path)
        except FileNotFoundError: _err(f"blueprint not found: {args.blueprint_path}"); return 1
        except Exception as exc: _err(f"invalid blueprint \u2014 {exc}"); return 1
        result = handle_init(bp, path)
        if not result.is_success: _err(result.error); return result.exit_code
        out = format_init(result)
        if out: print(out)
        else: print(f"Initialized project at {path}")
        return 0
    # === dashboard ===
    if args.command == "dashboard":
        from auteur.ui.dashboard import build_dashboard, format_dashboard
        try:
            data = build_dashboard(args.project)
        except Exception as exc:
            _err(f"failed to build dashboard: {exc}"); return 1
        if args.json:
            import json as _json
            print(_json.dumps(data, indent=2, default=str))
        else:
            print(format_dashboard(data))
        return 0
    # === plan ===
    if args.command == "plan":
        from auteur.planning.cli import dispatch_plan
        return dispatch_plan(args)
    # === draft ===
    if args.command == "draft":
        return _draft_retry(args, is_retry=False)
    # === accept ===
    if args.command == "accept":
        proj = Project.load(args.project)
        result = handle_accept(proj, args.chapter)
        if not result.is_success: _err(result.error); return result.exit_code
        out = format_accept(result)
        if out: print(out)
        return 0
    # === retry ===
    if args.command == "retry":
        return _draft_retry(args, is_retry=True)
    # === audit ===
    if args.command == "audit":
        bp_path = args.project / "blueprint.yaml"
        if not bp_path.exists(): _err(f"No blueprint.yaml found in {args.project}"); return 1
        if not (args.project / "bible.json").exists():
            _err(f"No bible.json found in {args.project}"); return 1
        if args.accept is not None:
            if args.option is None: print("--accept requires --option.", file=sys.stderr); return 1
            return handle_audit_resolve_proposal(args.project, args.accept, args.option).exit_code
        from auteur.bible import StoryBible
        result = handle_audit(StoryBlueprint.from_yaml(bp_path),
            StoryBible(args.project / "bible.json"), Project.load(args.project),
            repair=args.repair, layers=args.layers)
        if result.data is None: return result.exit_code
        d = result.data
        if not d.diagnostics and result.exit_code == 0:
            out = format_audit(result)
            if out: print(out)
            return 0
        dd = args.project / "structure" / "diagnostics"
        try:
            ap = serialize_audit(result, dd)
            if ap is None: _err("no data to serialize"); return 1
        except OSError as exc:
            _err(f"failed to write audit report to {dd / 'audit_report.json'}: {exc}"); return 1
        d.artifact_path = ap; result.data = d
        out = format_audit(result)
        if out: print(out)
        if args.repair and d.diagnostics:
            from auteur.structure.proposal_resolution import write_audit_repair_proposals
            write_audit_repair_proposals(args.project, d.diagnostics)
        return result.exit_code
    # === structure diagnose ===
    if args.command == "structure" and args.structure_command == "diagnose":
        try: bp = StoryBlueprint.from_yaml(args.blueprint)
        except FileNotFoundError: _err(f"blueprint not found: {args.blueprint}"); return 1
        except (ValueError, yaml.YAMLError) as exc:
            _err(f"invalid blueprint {args.blueprint}: {exc}"); return 1
        result = handle_structure_diagnose(bp)
        if not result.is_success: _err(result.error); return result.exit_code
        if args.output: ap = args.output
        else:
            bpp = args.blueprint
            if bpp.is_dir(): dd = Project.load(bpp).structure_diagnostics_dir()
            elif bpp.name == "blueprint.yaml" and (bpp.parent / "bible.json").exists():
                dd = Project.load(bpp.parent).structure_diagnostics_dir()
            else: dd = bpp.parent / "structure" / "diagnostics"; dd.mkdir(parents=True, exist_ok=True)
            ap = dd / "structure_report.json"
        try:
            if serialize_structure_diagnose(result, ap) is None: _err("no data to serialize"); return 1
        except OSError as exc: _err(f"failed to write report to {ap}: {exc}"); return 1
        out = format_structure_diagnose(result)
        if out: print(out)
        print(f"Diagnostics written to {ap}")
        return 4 if result.data["errors"] else 0
    # === structure propose-repairs ===
    if args.command == "structure" and args.structure_command == "propose-repairs":
        try: bp, dd, pd = _bp_dirs(args.blueprint)
        except FileNotFoundError: _err(f"blueprint not found: {args.blueprint}"); return 1
        except Exception as exc: _err(f"invalid blueprint {args.blueprint}: {exc}"); return 1
        result = handle_structure_propose_repairs(bp)
        if not result.is_success: _err(result.error); return result.exit_code
        try:
            if serialize_structure_propose_repairs(result, dd, pd) is None:
                _err("no data to serialize"); return 1
        except OSError as exc: _err(f"failed to write structure artifacts: {exc}"); return 1
        out = format_structure_propose_repairs(result)
        if out: print(out)
        return 0
    # === structure apply ===
    if args.command == "structure" and args.structure_command == "apply":
        if not args.proposal.exists(): _err(f"proposal not found: {args.proposal}"); return 1
        if not args.blueprint.exists(): _err(f"blueprint not found: {args.blueprint}"); return 1
        if args.in_place and args.output is not None:
            print("Error: --output cannot be used with --in-place", file=sys.stderr); return 1
        try: prop = StructureProposal.model_validate(
            yaml.safe_load(args.proposal.read_text(encoding="utf-8")))
        except (ValueError, yaml.YAMLError, OSError) as exc:
            _err(f"invalid proposal {args.proposal}: {exc}"); return 1
        if prop.source_domain == "bible_audit":
            _err("bible_audit proposals cannot be applied to blueprints. "
                "Resolve them with `auteur audit --accept ... --option ...`."); return 1
        try: bp, _, _ = _bp_dirs(args.blueprint)
        except Exception as exc: _err(f"invalid blueprint {args.blueprint}: {exc}"); return 1
        if (not prop.selection.selected_option_id and prop.decision is not None
                and prop.decision.status == "accepted"):
            prop.selection.selected_option_id = prop.decision.selected_option_id
            if not prop.selection.custom_data and prop.decision.custom_data:
                prop.selection.custom_data = prop.decision.custom_data
        src = args.blueprint / "blueprint.yaml" if args.blueprint.is_dir() else args.blueprint
        result = handle_structure_apply(prop, bp, in_place=args.in_place,
            output_dir=str(args.output or src.parent) if not args.in_place else None,
            original_path=str(src) if args.in_place else None)
        if not result.is_success: _err(result.error); return result.exit_code
        result.data["proposal_path"] = str(args.proposal)
        result.data["source_blueprint_path"] = str(src)
        out = format_structure_apply(result)
        if out: print(out)
        return 0

    # === structure propose ===
    if args.command == "structure" and args.structure_command == "propose":
        project = args.project
        diag_dir = project / ".auteur" / "structure" / "diagnostics"
        proposals_dir = project / ".auteur" / "structure" / "proposals"

        if args.list or (not args.apply):
            # List proposals
            proposals_dir.mkdir(parents=True, exist_ok=True)
            proposals = sorted(proposals_dir.glob("*.yaml"))
            if args.json:
                data = []
                for p in proposals:
                    try:
                        prop = StructureProposal.from_yaml(p)
                        data.append(prop.model_dump(mode="json"))
                    except Exception:
                        data.append({"proposal_id": p.stem, "error": "parse failed"})
                print(json.dumps(data, indent=2, default=str))
            else:
                if not proposals:
                    print("No proposals found.")
                else:
                    print(f"Proposals ({len(proposals)}):")
                    for p in proposals:
                        try:
                            prop = StructureProposal.from_yaml(p)
                            sel = prop.selection.selected_option_id if prop.selection else ""
                            marker = "✓" if sel else "·"
                            print(f"  {marker} {prop.proposal_id[:24]}... {prop.summary[:60]}")
                        except Exception:
                            print(f"  ? {p.stem}")
            return 0

        if args.apply:
            apply_path = proposals_dir / f"{args.apply}.yaml"
            if not apply_path.exists():
                # Try matching by ID prefix
                matches = list(proposals_dir.glob(f"{args.apply}*.yaml"))
                if not matches:
                    _err(f"Proposal not found: {args.apply}")
                    return 1
                apply_path = matches[0]
            try:
                prop = StructureProposal.from_yaml(apply_path)
                bp_path = project / "blueprint.yaml"
                if not bp_path.exists():
                    # Try .auteur version
                    bp_path = project / ".auteur" / "state" / "artifacts" / "blueprint.yaml"
                if not bp_path.exists():
                    _err("No blueprint found in project")
                    return 1
                bp = StoryBlueprint.from_yaml(bp_path)
                result = handle_structure_apply(prop, bp, in_place=True)
                if not result.is_success:
                    _err(result.error)
                    return result.exit_code
                print(f"Applied proposal: {prop.proposal_id[:24]}...")
            except Exception as e:
                _err(f"Failed to apply proposal: {e}")
                return 1
            return 0
    # === structure generate ===
    if args.command == "structure" and args.structure_command == "generate":
        try: bp = StoryBlueprint.from_yaml(args.blueprint)
        except FileNotFoundError: _err(f"blueprint file not found: {args.blueprint}"); return 1
        except Exception as e: _err(f"failed to parse blueprint {args.blueprint}: {e}"); return 1
        result = handle_structure_generate(bp, symptom=args.symptom)
        if not result.is_success: _err(result.error); return result.exit_code
        d = result.data
        if d.get("is_diagnostics") and "diagnoses" in d:
            d["blueprint"] = str(args.blueprint); result.data = d
            out = format_structure_generate(result)
            if out: print(out)
            if args.output: serialize_structure_generate_text(out, args.output)
            if args.output: print(f"\nDiagnosis written to {args.output}", file=sys.stderr)
            return 0
        if d.get("is_diagnostics") and "diagnostics" in d:
            out = format_structure_generate(result)
            if out: print(out, file=sys.stderr)
            return 1 if [x for x in d["diagnostics"] if x.get("severity") == "error"] else 0
        out = format_structure_generate(result)
        if out: print(out)
        if args.output: serialize_structure_generate_text(out, args.output); print(
            f"\nProposal written to {args.output}", file=sys.stderr)
        return 0
    # === story-discovery run ===
    if args.command == "story-discovery" and args.story_discovery_command == "run":
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        premise_text = args.brain_dump
        try:
            premise_path = Path(args.brain_dump)
            if premise_path.exists() and premise_path.is_file():
                premise_text = premise_path.read_text(encoding="utf-8")
        except Exception:
            pass
        from auteur.llm.factory import build_client
        client = build_client(args.provider, args.model, agent_type="identity")
        result = handle_identity_recommend(
            client=client,
            premise_text=premise_text,
            genre=args.genre,
            medium=args.medium,
            mode=args.mode,
            recommend_mode="open_ended",
            candidates_count=args.candidates,
            discovery_lenses=args.lens,
            strict_candidate_count=args.strict_candidate_count,
            debug=args.debug,
            timestamp=ts,
            project_path=args.project,
        )
        if not result.is_success:
            _err(result.error)
            return result.exit_code
        data = result.data
        if not isinstance(data, RecommendOpenEndedData):
            _err("story discovery did not return candidate data")
            return 1
        written = serialize_story_discovery(data, args.output, args.brain_dump)
        candidate_count = len(data.candidates)
        for path in written[:candidate_count]:
            print(f"  Wrote {path.name}")
        print(f"\nSuccess: generated {candidate_count} Story Discovery candidates under {args.output}/")
        print(f"Discovery report written to {args.output / 'discovery_report.yaml'}")
        print(f"Comparison document written to {args.output / 'comparison.md'}")
        return 0
    # === story-discovery accept ===
    if args.command == "story-discovery" and args.story_discovery_command == "accept":
        from auteur.identity import StoryIdentity
        if not args.candidate.exists():
            print(f"Error: Candidate file not found: {args.candidate}", file=sys.stderr)
            return 1
        try:
            ident = StoryIdentity.from_yaml(args.candidate)
        except Exception as exc:
            print(f"Error: failed to parse candidate YAML: {exc}", file=sys.stderr)
            return 1
        result = handle_identity_promote(ident)
        if not result.is_success:
            print(f"Error: {result.error}", file=sys.stderr)
            if result.data:
                for err in result.data.diagnostics:
                    sv = err.severity.value.upper() if hasattr(err.severity, "value") else str(err.severity).upper()
                    if sv == "ERROR":
                        print(f" - {err.message}", file=sys.stderr)
            return result.exit_code
        if result.data.warnings:
            print("Warnings present in promoted candidate:")
            for w in result.data.warnings:
                print(f" - {w.message}")
        try:
            serialize_identity_promote(ident, args.output)
        except Exception as exc:
            print(f"Error: failed to promote candidate to {args.output}: {exc}", file=sys.stderr)
            return 1
        report_path = args.candidate.parent / "discovery_report.yaml"
        if report_path.exists():
            try:
                report = yaml.safe_load(report_path.read_text(encoding="utf-8")) or {}
                report["chosen_candidate"] = args.candidate.stem
                report_path.write_text(yaml.safe_dump(report, sort_keys=False), encoding="utf-8")
            except (OSError, yaml.YAMLError) as exc:
                print(f"[WARNING] Failed to update discovery report: {exc}", file=sys.stderr)
        print(f"Success: promoted candidate {args.candidate} to {args.output}")
        if not args.keep_candidates:
            candidate_dir = args.candidate.parent
            if candidate_dir.name == "story_discovery" and candidate_dir.exists():
                try:
                    # Keep the discovery report/comparison as durable provenance;
                    # only remove unselected candidate YAML files.
                    for candidate_file in candidate_dir.glob("candidate_*.yaml"):
                        if candidate_file != args.candidate:
                            candidate_file.unlink()
                    print(f"Retained discovery provenance at {candidate_dir}")
                except Exception as exc:
                    print(f"[WARNING] Failed to delete candidate directory {candidate_dir}: {exc}", file=sys.stderr)
        return 0
    # === identity validate ===
    if args.command == "identity" and args.identity_command == "validate":
        if not args.identity.exists(): _err(f"identity file not found: {args.identity}"); return 1
        try:
            from auteur.identity import StoryIdentity
            ident = StoryIdentity.from_yaml(args.identity)
            if args.project is not None:
                from auteur.genres.registry import load_project_genre_contract
                ident.genre_contract_snapshot = load_project_genre_contract(args.project, ident.story_type.genre)
        except Exception as exc: _err(f"invalid story identity {args.identity}: {exc}"); return 1
        result = handle_identity_validate(ident)
        if not result.is_success: _err(result.error); return result.exit_code
        data: IdentityValidateData = result.data
        dd = args.identity.parent / "identity"; dd.mkdir(parents=True, exist_ok=True)
        ap = dd / "validation_report.json"
        try:
            if serialize_identity_validate(result, dd) is None: _err("no data to serialize"); return 1
        except OSError as exc: _err(f"failed to write validation report to {ap}: {exc}"); return 1
        out = format_identity_validate(result)
        if out: print(out, file=sys.stderr)
        verdict = format_identity_validate_success(result, str(args.identity))
        if data.has_error:
            print(verdict, file=sys.stderr); print(f"Validation report written to {ap}", file=sys.stderr)
            return 1
        print(verdict); print(f"Validation report written to {ap}")
        return 0
    # === identity compile / blueprint seed ===
    if (args.command == "identity" and args.identity_command == "compile") or \
       (args.command == "blueprint" and args.blueprint_command == "seed"):
        if not args.identity.exists(): _err(f"identity file not found: {args.identity}"); return 1
        try:
            from auteur.identity import StoryIdentity
            ident = StoryIdentity.from_yaml(args.identity)
        except Exception as exc:
            _err(f"failed to parse story identity {args.identity}: {exc}"); return 1
        result = handle_compile_to_blueprint(ident)
        if not result.is_success: _err(result.error); return result.exit_code
        try:
            if serialize_compile_blueprint(result, args.output) is None:
                _err("no data to serialize"); return 1
        except Exception as exc:
            _err(f"failed to write blueprint to {args.output}: {exc}"); return 1
        print(format_identity_compile_success(str(args.identity), str(args.output)))
    # === blueprint publish ===
    if args.command == "blueprint" and args.blueprint_command == "publish":
        bp_path = args.blueprint
        if not bp_path.exists():
            _err(f"blueprint not found: {bp_path}"); return 1
        try:
            bp = StoryBlueprint.from_yaml(bp_path)
        except Exception as exc:
            _err(f"failed to load blueprint: {exc}"); return 1
        output = args.output
        if output is None:
            output = bp_path.parent / "published"
            output.mkdir(parents=True, exist_ok=True)
            name = bp_path.stem
            output = output / f"{name}.{args.format}"
        elif output.is_dir():
            output = output / f"blueprint.{args.format}"
        output.parent.mkdir(parents=True, exist_ok=True)
        try:
            if args.format == "yaml":
                import yaml as _yaml
                _yaml.safe_dump(bp.model_dump(mode="json"), output.open("w", encoding="utf-8"),
                                sort_keys=False, allow_unicode=True)
            else:
                _write_blueprint_markdown(bp, output)
        except Exception as exc:
            _err(f"failed to publish blueprint: {exc}"); return 1
        print(f"Blueprint published to {output}")
        return 0
    if args.command == "identity" and args.identity_command == "recommend":
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        pt = args.premise
        try:
            pp = Path(args.premise)
            if pp.exists() and pp.is_file(): pt = pp.read_text(encoding="utf-8")
        except Exception: pass
        rec_mode = args.recommend_mode; story_mode = args.mode
        if args.mode in ("open-ended", "open_ended"):
            print("Warning: --mode open-ended is deprecated. "
                "Use --recommend-mode open-ended instead.", file=sys.stderr)
            rec_mode = "open_ended"; story_mode = None
        if rec_mode == "open-ended": rec_mode = "open_ended"
        from auteur.llm.factory import build_client
        client = build_client(args.provider, args.model, agent_type="identity")
        result = handle_identity_recommend(client=client, premise_text=pt,
            genre=args.genre, medium=args.medium, mode=story_mode,
            recommend_mode=rec_mode, candidates_count=args.candidates,
            discovery_lenses=(
                ["genre_aligned", "structurally_coherent", "faithful_to_input", "emotionally_powerful"]
                if rec_mode == "open_ended" else None
            ),
            strict_candidate_count=args.strict_candidate_count,
            debug=args.debug, timestamp=ts)
        if not result.is_success: _err(result.error); return result.exit_code
        data = result.data
        if isinstance(data, RecommendOpinionatedData):
            serialize_identity_opinionated(data, args.output, debug=args.debug, timestamp=ts)
            out = format_identity_recommend(result, output_path=args.output)
            if out: print(out)
            return 0
        elif isinstance(data, RecommendOpenEndedData):
            written = serialize_identity_openended(data, args.output, args.premise)
            out = format_identity_recommend(result, written_paths=written)
            if out: print(out)
            return 0
        return 1
    # === identity accept-candidate ===
    if args.command == "identity" and args.identity_command == "accept-candidate":
        from auteur.identity import StoryIdentity, StoryIdentityRecommendationSet
        if not args.candidate.exists():
            print(f"Error: Candidate file not found: {args.candidate}", file=sys.stderr); return 1
        try: ident = StoryIdentity.from_yaml(args.candidate)
        except Exception as exc:
            print(f"Error: failed to parse candidate YAML: {exc}", file=sys.stderr); return 1
        result = handle_identity_promote(ident)
        if not result.is_success:
            print(f"Error: {result.error}", file=sys.stderr)
            if result.data:
                for err in result.data.diagnostics:
                    sv = err.severity.value.upper() if hasattr(err.severity, "value") else str(err.severity).upper()
                    if sv == "ERROR": print(f" - {err.message}", file=sys.stderr)
            return result.exit_code
        if result.data.warnings:
            print("Warnings present in promoted candidate:")
            for w in result.data.warnings:
                sv = w.severity.value.upper() if hasattr(w.severity, "value") else str(w.severity).upper()
                print(f" - {w.message}")
        pdir = args.candidate.parent; rsp = pdir / "recommendation_set.yaml"
        if rsp.exists():
            try:
                rs = StoryIdentityRecommendationSet.model_validate(
                    yaml.safe_load(open(rsp, encoding="utf-8")))
                cur = "sha256:" + hashlib.sha256(
                    args.candidate.read_text(encoding="utf-8").encode()).hexdigest()
                for c in rs.candidates:
                    if Path(c.path).resolve() == args.candidate.resolve() and c.content_hash != cur:
                        print("[WARNING] Candidate file has been manually modified "
                            "since recommendation generation index was created.")
                        break
            except Exception as exc:
                print(f"[WARNING] Failed to verify candidate hash against "
                    f"recommendation_set.yaml index: {exc}", file=sys.stderr)
        try: serialize_identity_promote(ident, args.output)
        except Exception as exc:
            print(f"Error: failed to promote candidate to {args.output}: {exc}", file=sys.stderr)
            return 1
        print(f"Success: promoted candidate {args.candidate} to {args.output}")
        if not args.keep_candidates:
            cd = pdir
            if cd.name == "story_identity_candidates" and cd.exists():
                try: shutil.rmtree(cd); print(f"Cleaned up candidate directory: {cd}")
                except Exception as exc:
                    print(f"[WARNING] Failed to delete candidate directory {cd}: {exc}", file=sys.stderr)
        return 0
    if args.command == "expression":
        from auteur.expression.cli import dispatch_expression
        return dispatch_expression(args)

    # === state ===
    if args.command == "state":
        if args.state_command == "check":
            ol: Path | None = getattr(args, "outline", None)
            if ol is not None:
                if not ol.exists(): _err(f"Outline file not found: {ol}"); return 1
                from auteur.structure.outline_audit import load_outline
                try: outline = load_outline(str(ol))
                except ValueError as exc: _err(str(exc)); return 1
                result = handle_state_check(args.project, outline=outline)
            else:
                result = handle_state_check(args.project)
            # state_check returns exit_code 4 for diagnostics found, not a crash
            if result.exit_code != 0 and result.exit_code != 4:
                _err(result.error or "state check failed")
                return result.exit_code
            out = format_state_check(result)
            if out: print(out)
            serialize_state_check(result)
            return result.exit_code
        if args.state_command == "update":
            result = handle_state_update(args.project, args.file, args.key, args.val)
            if not result.is_success: _err(result.error or "state update failed"); return result.exit_code
            out = format_state_update(result)
            if out: print(out)
            serialize_state_update(result)
            return 0
        if args.state_command == "prepare":
            result = handle_state_prepare(args.project, args.phase, args.scope, args.out, args.chapter)
            if not result.is_success: _err(result.error or "state prepare failed"); return result.exit_code
            out = format_state_prepare(result)
            if out: print(out)
            if args.out:
                serialize_state_prepare(result)
            return 0
        if args.state_command == "canon":
            result = handle_state_canon(args.project, args.format)
            if not result.is_success: _err(result.error or "state canon failed"); return result.exit_code
            out = format_state_canon(result)
            if out: print(out)
            return 0
        if args.state_command == "confirm":
            result = handle_state_confirm(args.project, args.recovery_run)
            if not result.is_success: _err(result.error or "state confirm failed"); return result.exit_code
            out = format_state_confirm(result)
            if out: print(out)
            serialize_state_confirm(result)
            return 0
        if args.state_command in {"status", "explain", "adopt", "accept", "archive", "affected-by"}:
            from auteur.provenance import ArtifactStore
            artifact = args.artifact
            project = _pilot_project_root(artifact)
            artifact_type = getattr(args, "artifact_type", None) or _pilot_artifact_type(artifact)
            store = ArtifactStore(project)
            if args.state_command == "affected-by":
                affected = store.impact(store._artifact_id(artifact))
                if args.json_output:
                    print(json.dumps({"artifact_id": store._artifact_id(artifact), "affected": affected}, indent=2))
                else:
                    print(f"Affected by {store._artifact_id(artifact)}:")
                    for item in affected:
                        relation = "direct" if item["direct"] else "transitive"
                        print(f"- {item['artifact_id']} ({relation}; {item['health']}/{item['freshness']}; {item['reason']})")
                return 0
            if args.state_command == "status":
                print(json.dumps(store.status(artifact, artifact_type).model_dump(mode="json"), indent=2))
                return 0
            if args.state_command == "explain":
                print(json.dumps(store.explain(artifact, artifact_type), indent=2))
                return 0
            if args.state_command == "adopt":
                store.adopt(artifact, artifact_type)
                return 0
            if args.state_command == "accept":
                if store.accept(artifact, artifact_type) is None:
                    _err("archived artifact cannot be accepted")
                    return 1
                return 0
            store.archive(artifact, artifact_type, reason=args.reason, by="author")
            return 0
    # === cartographer ===
    if args.command == "cartographer":
        if args.cartographer_command == "compile":
            try: bp = StoryBlueprint.from_yaml(args.blueprint)
            except FileNotFoundError: _err(f"blueprint file not found: {args.blueprint}"); return 1
            except Exception: bp = None
            try:
                from auteur.llm.factory import build_client
                llm = build_client(args.provider, args.model, agent_type="cartographer", blueprint=bp)
            except Exception as exc: _err(f"failed to build LLM client: {exc}"); return 1
            result = handle_cartographer_compile(args.blueprint, llm, args.output, split=args.split)
            if not result.is_success: _err(result.error); return result.exit_code
            out = format_cartographer_compile(result)
            if out: print(out)
            else: print(format_cartographer_compile_success(str(args.output)))
            return 0
        if args.cartographer_command == "validate":
            result = handle_cartographer_validate(args.outline, args.blueprint)
            if not result.is_success: _err(result.error); return result.exit_code
            out = format_cartographer_validate(result)
            if out: print(out)
            else: print(format_cartographer_validate_success(str(args.outline)))
            return 0
    # === character ===
    if args.command == "character":
        from auteur.character.cli import handle_character_command
        return handle_character_command(args)
    # === series ===
    if args.command == "series":
        from auteur.series.cli import handle_series_command
        return handle_series_command(args)
    # === edit ===
    if args.command == "edit":
        from auteur.editing.cli import handle_edit_command
        return handle_edit_command(args)
    # === relations ===
    if args.command == "relations":
        from auteur.relations.cli import handle_relations_command
        return handle_relations_command(args)
    # === export/import round-trip ===
    if args.command == "export":
        from auteur.roundtrip.cli import handle_export_command
        return handle_export_command(args)
    if args.command == "import":
        from auteur.roundtrip.cli import handle_import_command
        return handle_import_command(args)
    # === genre builder ===
    if args.command == "genre":
        from auteur.genre_builder.cli import handle_genre_builder_command
        return handle_genre_builder_command(args)

    # === universe ===
    if args.command == "universe":
        from auteur.universe.cli import handle_universe_command
        return handle_universe_command(args)
    if args.command == "book":
        from auteur.book.cli import handle_book_command
        return handle_book_command(args)

    # === netorare ===
    # Registered genre pipelines all share one command implementation.  Keep
    # the legacy branches below as compatibility handlers for existing callers.
    from auteur.genre_pipeline.registry import get_genre_pipeline
    from auteur.genre_pipeline.cli import GenrePipelineCommand
    try:
        registered_spec = get_genre_pipeline(args.command)
    except ValueError:
        registered_spec = None
    if registered_spec is not None and getattr(args, f"{registered_spec.slug}_command", None) in {"init", "resume"}:
        command_name = getattr(args, f"{registered_spec.slug}_command")
        try:
            return GenrePipelineCommand(
                project_path=args.project,
                spec=registered_spec,
                core_id=getattr(args, "core", registered_spec.default_core_id),
                mode=getattr(args, "mode", None),
                provider=getattr(args, "provider", None),
                port=args.port,
                timeout=args.timeout,
                debug=args.debug,
                resume=command_name == "resume",
                no_browser=getattr(args, "no_browser", False),
            ).run()
        except ValueError as exc:
            _err(str(exc))
            return 2


    # === ontology ===
    if args.command == "ontology":
        from auteur.narrative_ontology.cli_ontology import (
            handle_ontology_inspect,
            handle_ontology_list,
            handle_ontology_validate,
            handle_ontology_themes,
        )
        if args.ontology_command == "inspect":
            return handle_ontology_inspect(args)
        if args.ontology_command == "list":
            return handle_ontology_list(args)
        if args.ontology_command == "validate":
            return handle_ontology_validate(args)
        if args.ontology_command == "themes":
            return handle_ontology_themes(args)

    # === realization (convergence) ===
    if args.command == "realization":
        from auteur.convergence.cli import dispatch_realization
        return dispatch_realization(args)

    # === decision ===
    if args.command == "decision":
        from auteur.decision.cli import dispatch_decision
        return dispatch_decision(args)

    # === review ===
    if args.command == "review":
        from auteur.review.cli import dispatch_review
        return dispatch_review(args)

    # === portfolio ===
    if args.command == "portfolio":
        from auteur.portfolio.cli import dispatch_portfolio
        return dispatch_portfolio(args)

    # === commit ===
    if args.command == "commit":
        from auteur.commitment.cli import dispatch_commit
        return dispatch_commit(args)

    # === lifecycle ===
    if args.command == "lifecycle":
        from auteur.lifecycle.cli import dispatch_lifecycle
        return dispatch_lifecycle(args)

    # === notify ===
    if args.command == "notify":
        from auteur.notify.cli import dispatch_notify
        return dispatch_notify(args)
    # === simulate ===
    if args.command == "simulate":
        from auteur.simulation.cli import dispatch_simulate
        return dispatch_simulate(args)

    # === workflow ===
    if args.command == "workflow":
        from auteur.workflow.cli import (
            format_workflow_status,
            handle_workflow_explain,
            handle_workflow_next,
            handle_workflow_status,
        )
        if args.workflow_command == "status":
            result = handle_workflow_status(args.project)
            if not result.is_success:
                _err(result.error or "workflow status failed")
                return result.exit_code
            if args.json:
                print(json.dumps(result.data.state.to_dict(), indent=2))
            else:
                output = format_workflow_status(result)
                if output:
                    print(output)
            return 0
        if args.workflow_command == "next":
            result = handle_workflow_next(args.project, execute=args.execute)
            if not result.is_success:
                _err(result.error or "workflow next failed")
                return result.exit_code
            if args.json:
                print(json.dumps(result.data, indent=2, default=str))
            else:
                data = result.data
                action = data.get("action")
                alerts = data.get("alerts", [])

                # Show alerts first
                if alerts:
                    for alert in alerts:
                        print(f"  ⚠ {alert}")
                    print("")

                if action:
                    label = action.label if hasattr(action, "label") else action.get("label", "")
                    command = action.command if hasattr(action, "command") else action.get("command", "")
                    authority = action.authority.value if hasattr(action, "authority") else action.get("authority", "")
                    description = action.description if hasattr(action, "description") else action.get("description", "")
                    print(f"Next: {label}")
                    print(f"  Command: {command}")
                    print(f"  Authority: {authority}")
                    if description:
                        print(f"  {description}")
                else:
                    print("No next action — all stages complete.")
            return 0
        if args.workflow_command == "explain":
            result = handle_workflow_explain(args.project, args.stage)
            if not result.is_success:
                _err(result.error or "workflow explain failed")
                return result.exit_code
            if args.json:
                print(json.dumps(result.data, indent=2))
            else:
                data = result.data
                if data.get("explanation"):
                    # Lifecycle or custom explanation
                    print(data["explanation"])
                elif "stage" in data:
                    stage = data["stage"]
                    complete = data["is_complete"]
                    print(f"Stage: {stage} ({'complete' if complete else 'incomplete'})")
                    if data.get("current_artifact"):
                        print(f"  Current artifact: {data['current_artifact']}")
                    for b in data.get("blockers", []):
                        print(f"  [{b['severity']}] {b['category']}: {b['message']}")
                        if b.get("artifact"):
                            print(f"    artifact: {b['artifact']}")
                else:
                    cs = data.get("current_stage")
                    if cs:
                        print(f"Current stage: {cs}")
                    else:
                        print("All stages complete.")
                    print(f"Summary: {data.get('summary', '')}")

                # Show lifecycle and commitment data for non-stage explanations
                if not data.get("stage"):
                    lc = data.get("lifecycle", {})
                    cm = data.get("commitment", {})
                    total = lc.get("total_decisions", 0)
                    if total > 0:
                        print("")
                        print("Lifecycle:")
                        print(f"  Decisions:       {total} total")
                        by_stage = lc.get("by_stage", {})
                        for sk in ["open", "evidence_gathered", "simulated", "portfolio",
                                   "under_review", "acceptance_ready", "accepted", "committed"]:
                            c = by_stage.get(sk, 0)
                            if c > 0:
                                print(f"    {sk.replace('_', ' ').title():<18} {c}")
                        if lc.get("diverged", 0) > 0:
                            print(f"  Diverged:        {lc['diverged']}")
                        if lc.get("with_gaps", 0) > 0:
                            print(f"  With gaps:       {lc['with_gaps']}")
                    cm_total = cm.get("total_commitments", 0)
                    if cm_total > 0 or cm.get("has_commitments"):
                        print("")
                        print("Commitments:")
                        print(f"  Total:           {cm_total}")
                        cm_state = cm.get("state", "")
                        if cm_state:
                            print(f"  State:           {cm_state}")
            return 0

    return 0

def _draft_retry(args, *, is_retry: bool) -> int:
    from auteur.llm.factory import build_client
    proj = Project.load(args.project)
    client = build_client(args.provider, args.model, agent_type="bard", blueprint=proj.blueprint)
    result = handle_retry(proj, args.chapter, args.max_iterations, client) if is_retry else \
             handle_draft(proj, args.chapter, args.max_iterations, client, regenerate_outline=getattr(args, "regenerate_outline", False))
    if not is_retry and result.data is None: return result.exit_code
    if is_retry and not result.is_success and result.data is None:
        _err(result.error); return result.exit_code
    d = result.data
    if d is None: return result.exit_code
    if d.conflict_report is not None:
        out = format_draft(result)
        if out: print(out, file=sys.stderr)
        print(f"  See {proj.chapter_dir(args.chapter) / 'outline.yaml'} for details.", file=sys.stderr)
        return result.exit_code
    if d.accepted:
        out = format_retry(result) if is_retry else format_draft(result)
        if out: print(out)
        return 0
    out = format_draft_not_accepted(result, str(args.project), args.chapter)
    if out: print(out, file=sys.stderr)
    return 2

def _bp_dirs(bp_path: Path) -> tuple[StoryBlueprint, Path, Path]:
    if bp_path.is_dir():
        proj = Project.load(bp_path)
        return proj.blueprint, proj.structure_diagnostics_dir(), proj.structure_proposals_dir()
    if bp_path.name == "blueprint.yaml" and (bp_path.parent / "bible.json").exists():
        proj = Project.load(bp_path.parent)
        return proj.blueprint, proj.structure_diagnostics_dir(), proj.structure_proposals_dir()
    bp = StoryBlueprint.from_yaml(bp_path)
    dd = bp_path.parent / "structure" / "diagnostics"
    pd = bp_path.parent / "structure" / "proposals"
    dd.mkdir(parents=True, exist_ok=True); pd.mkdir(parents=True, exist_ok=True)
    return bp, dd, pd

if __name__ == "__main__":
    raise SystemExit(main())



if __name__ == "__main__":
    raise SystemExit(main())