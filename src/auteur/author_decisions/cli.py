"""CLI surface for author decision objects, registered under the existing
'decision' namespace: `auteur decision create|accept|evaluate|view`.

NOTE: the read-only artifact view is named `view` because the existing
decision workspace already owns `decision inspect`; reusing that verb would
silently change existing behavior. (Flagged for human awareness.)

Lifecycle invariant:
  authored/scaffolded  --explicit author action (accept)-->  accepted
  --deterministic evaluation (evaluate)-->  report
Evaluation never implies acceptance; acceptance never implies a creative verdict.
"""
from __future__ import annotations

import enum
import sys
from pathlib import Path

import yaml as _yaml

from auteur.author_decisions.models import (
    AuthorDecision,
    DecisionValidationError,
)
from auteur.author_decisions.context import build_decision_context
from auteur.author_decisions import persistence as store


def _record_value(value):
    """Serialize a resolved value for the acceptance record (YAML-safe):
    pydantic models -> dict, enums -> their value, else verbatim."""
    if hasattr(value, "model_dump"):
        return value.model_dump()
    if isinstance(value, enum.Enum):
        return value.value
    return value


def register_author_decision_subcommands(ds) -> None:
    p_create = ds.add_parser("create", help="Scaffold an author decision artifact (author_decisions/<id>.yaml).")
    p_create.add_argument("decision_id", type=str)
    p_create.add_argument("--question", required=True, help="The unresolved author question.")
    p_create.add_argument("--alternative", action="append", default=[], dest="alternatives",
                          help="An authored alternative label (repeatable; at least 2).")
    p_create.add_argument("--alternative-id", action="append", default=[], dest="alternative_ids",
                          help="Stable id for the corresponding --alternative (paired by order).")
    p_create.add_argument("--combination", choices=["one_of", "choose_k_of_n"], default="one_of")
    p_create.add_argument("--k", type=int, default=None)
    p_create.add_argument("--criterion", required=True, help="Comparison criterion text.")
    p_create.add_argument("--evaluator", default="author_or_consumer")
    p_create.add_argument("--project", type=Path, default=Path("."))
    p_create.add_argument("--force", action="store_true")

    p_accept = ds.add_parser("accept", help="Explicitly accept an author decision against current Identity/Blueprint.")
    p_accept.add_argument("decision_id", type=str)
    p_accept.add_argument("--identity", type=Path, required=True, help="Accepted story_identity.yaml path.")
    p_accept.add_argument("--blueprint", type=Path, required=True, help="Current blueprint.yaml path.")
    p_accept.add_argument("--project", type=Path, default=Path("."))
    p_accept.add_argument("--json", action="store_true")

    p_eval = ds.add_parser("evaluate", help="Run the bounded deterministic evaluation (M3) on an author decision.")
    p_eval.add_argument("decision_id", type=str)
    p_eval.add_argument("--identity", type=Path, required=True)
    p_eval.add_argument("--blueprint", type=Path, required=True)
    p_eval.add_argument("--project", type=Path, default=Path("."))
    p_eval.add_argument("--json", action="store_true")

    p_view = ds.add_parser("view", help="Read-only view of an author decision (authored vs resolved vs acceptance).")
    p_view.add_argument("decision_id", type=str)
    p_view.add_argument("--identity", type=Path, default=None)
    p_view.add_argument("--blueprint", type=Path, default=None)
    p_view.add_argument("--project", type=Path, default=Path("."))
    p_view.add_argument("--json", action="store_true")

    p_elicit = ds.add_parser(
        "elicit",
        help="Consequence-focused elicitation for a genuinely unsettled author "
             "(F3, design 2026-08-f3-elicitation.md @ 37bc784). Read-only by default; "
             "--record writes the author's explicit outcome into the existing F1 "
             "goal_significance field, or records undecided (no write).",
    )
    p_elicit.add_argument("decision_id", type=str)
    p_elicit.add_argument("--identity", type=Path, required=True,
                          help="Accepted story_identity.yaml path.")
    p_elicit.add_argument("--blueprint", type=Path, required=True,
                          help="Current blueprint.yaml path.")
    p_elicit.add_argument("--project", type=Path, default=Path("."))
    p_elicit.add_argument(
        "--record", choices=["ordered", "unranked", "undecided"], default=None,
        help="Explicit author outcome: ordered (two participating goal refs), "
             "unranked (intentional non-precedence), or undecided (no write). "
             "Without --record the command is read-only.",
    )
    p_elicit.add_argument(
        "--refs", nargs="+", default=None,
        help="Exactly two participating goal refs for --record ordered (most "
             "significant first).",
    )


def author_decision_handlers() -> dict:
    return {
        "create": handle_create,
        "accept": handle_accept,
        "evaluate": handle_evaluate,
        "view": handle_view,
        "elicit": handle_elicit,
    }


def _load_decision(project: Path, decision_id: str) -> AuthorDecision:
    path = store.artifact_path(project, decision_id)
    if not path.exists():
        raise FileNotFoundError(f"no author decision artifact at {path}")
    return AuthorDecision.from_yaml(path)


def handle_create(args) -> int:
    try:
        labels = list(args.alternatives)
        ids = list(args.alternative_ids)
        if len(labels) < 2:
            print("Error: at least 2 --alternative values are required; alternatives are never derived from prose.",
                  file=sys.stderr)
            return 1
        if ids and len(ids) != len(labels):
            print("Error: --alternative-id count must match --alternative count.", file=sys.stderr)
            return 1
        alternative_ids = ids if ids else [f"alt_{i}" for i in range(len(labels))]
        out = store.artifact_path(args.project, args.decision_id)
        if out.exists() and not args.force:
            print(f"Error: artifact already exists: {out} (use --force to overwrite)", file=sys.stderr)
            return 1
        if out.exists() and args.force and store.load_acceptance_record(args.project, args.decision_id) is not None:
            print(
                f"Error: {args.decision_id} is accepted; --force refuses to overwrite accepted creative authority",
                file=sys.stderr,
            )
            return 1
        data = {
            "decision_id": args.decision_id,
            "unresolved_choice": {
                "choice_id": args.decision_id,
                "question": args.question,
                "options": labels,
            },
            "alternative_ids": alternative_ids,
            "combination": {"rule": args.combination, "k": args.k},
            "criterion": {"text": args.criterion, "evaluator": args.evaluator},
            "hard_constraints": [],
            "required_characters": [],
            "blocked_provenance": {"outcome_refs": []},
            "default_references": [],
            "alternative_bindings": [],
            "structural_anchors": [],
            "combination_direction": None,
        }
        AuthorDecision.from_dict(data)  # schema sanity: round-trips or fails
        store.atomic_write_yaml(out, data)
        print(f"Created author decision artifact (NOT accepted): {out}")
        return 0
    except DecisionValidationError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:  # pragma: no cover - defensive CLI boundary
        print(f"Error: {exc}", file=sys.stderr)
        return 1


def handle_accept(args) -> int:
    try:
        decision = _load_decision(args.project, args.decision_id)
        if decision.decision_id != args.decision_id:
            print(
                f"Error: artifact decision_id {decision.decision_id!r} does not match filename stem {args.decision_id!r}",
                file=sys.stderr,
            )
            return 1
        if store.load_acceptance_record(args.project, args.decision_id) is not None:
            print(f"Error: decision {args.decision_id} is already accepted; re-acceptance is not in this slice.",
                  file=sys.stderr)
            return 1
        identity = _load_identity(args.identity)
        blueprint = _load_blueprint(args.blueprint)
        ctx = build_decision_context(decision, identity, blueprint)
        summary = {
            "decision_id": decision.decision_id,
            "question": decision.unresolved_choice.question,
            "alternatives": ctx.alternative_labels,
            "combination": decision.combination.rule,
            "criterion": decision.criterion.text,
            "resolved_constraints": [{"ref": c.ref, "text": c.text} for c in ctx.constraints],
            "blocked_provenance": {"expected": ctx.blocked_count, "verified": ctx.blocked_provenance_verified},
            "resolved_defaults": ctx.resolved_defaults,
            "resolved_bindings": [
                {"alternative_id": rb.alternative_id, "entity_ref": rb.entity_ref,
                 "relationship": rb.relationship.value}
                for rb in ctx.resolved_bindings
            ],
            "resolved_anchors": [
                {"anchor_id": ra.anchor_id, "kind": ra.kind.value,
                 "participants": [ref for _, ref in ra.participants],
                 "carrier_refs": [ref for _, ref in ra.carrier_refs],
                 "bears_on": [{"ref": ref, "value": _record_value(value),
                              "nature": nature.value if nature else None}
                             for ref, value, nature in ra.bears_on]}
                for ra in ctx.resolved_anchors
            ],
            "combination_direction": ctx.combination_direction,
        }
        if args.json:
            print(_yaml.safe_dump(summary, sort_keys=False))
        else:
            print(f"Decision: {decision.decision_id}")
            print(f"Question: {decision.unresolved_choice.question}")
            print(f"Alternatives: {summary['alternatives']}")
            print(f"Combination: {summary['combination']}")
            print(f"Criterion: {decision.criterion.text}")
            print(f"Hard constraints ({len(ctx.constraints)}):")
            for c in ctx.constraints:
                print(f"  - {c.ref}: {c.text}")
            print(f"Blocked provenance: expected={ctx.blocked_count} verified={ctx.blocked_provenance_verified}")
            print(f"Resolved product defaults: {ctx.resolved_defaults}")
        store.write_acceptance_record(
            args.project,
            decision.decision_id,
            identity_fingerprint=store.sha256_file(args.identity),
            blueprint_fingerprint=store.sha256_file(args.blueprint),
            resolved_constraints=summary["resolved_constraints"],
            blocked_count=ctx.blocked_count,
            blocked_provenance_verified=ctx.blocked_provenance_verified,
            resolved_defaults=ctx.resolved_defaults,
            resolved_bindings=summary["resolved_bindings"],
            resolved_anchors=summary["resolved_anchors"],
            combination_direction=summary["combination_direction"],
            chosen=decision.chosen,
        )
        print(f"Accepted (provenance recorded): {store.acceptance_path(args.project, decision.decision_id)}")
        return 0
    except (DecisionValidationError, FileNotFoundError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:  # pragma: no cover
        print(f"Error: {exc}", file=sys.stderr)
        return 1


def handle_evaluate(args) -> int:
    try:
        decision = _load_decision(args.project, args.decision_id)
        if decision.decision_id != args.decision_id:
            print(
                f"Error: artifact decision_id {decision.decision_id!r} does not match filename stem {args.decision_id!r}",
                file=sys.stderr,
            )
            return 1
        identity = _load_identity(args.identity)
        blueprint = _load_blueprint(args.blueprint)
        ctx = build_decision_context(decision, identity, blueprint)
        report = ctx.build_report()
        acceptance = store.load_acceptance_record(args.project, args.decision_id)
        report["acceptance_status"] = "accepted" if acceptance else "authored_only"
        if args.json:
            print(_yaml.safe_dump(report, sort_keys=False))
        else:
            print(f"Decision: {report['decision_id']} [{report['acceptance_status']}]")
            print(f"Enumerated combinations: {report['enumerated_combinations']}")
            print(f"Constraints: {len(report['constraints'])} (verbatim)")
            print(f"Blocked provenance: {report['blocked_provenance']}")
            print(f"Resolved defaults: {report['resolved_defaults']}")
            _render_consequences(report.get("consequences", {}))
            print("No verdict is rendered; creative evaluation is the author's responsibility.")
        return 0
    except (DecisionValidationError, FileNotFoundError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:  # pragma: no cover
        print(f"Error: {exc}", file=sys.stderr)
        return 1


def _elicitation_state(decision, report) -> dict:
    """A2 (design 2026-08-a2-surface-elicitation.md @ 94b09f8): deterministic
    elicitation-availability state for the author-decision view surface. Three
    states: unsettled (no goal_significance + composed combinations exist),
    no_composed_consequences (no significance + no composed combinations),
    declared (goal_significance present — F1 is the destination). The hint
    never ranks, recommends, or infers from prose."""
    if decision.goal_significance is not None:
        return {"state": "declared"}
    combos = report.get("consequences", {}).get("combinations") or []
    if not combos:
        return {"state": "no_composed_consequences"}
    return {"state": "unsettled"}


def _render_elicitation_hint(decision, args, state: str) -> None:
    if state == "unsettled":
        print("Elicitation (F3): available — examine the concrete tradeoff:")
        print(f"  auteur decision elicit {decision.decision_id} "
              f"--identity {args.identity} --blueprint {args.blueprint} "
              f"--project {args.project}")
    elif state == "no_composed_consequences":
        print("Elicitation (F3): not applicable — no composed consequences yet "
              "(an authored combination_direction is required to compose them).")


def handle_view(args) -> int:
    try:
        decision = _load_decision(args.project, args.decision_id)
        if decision.decision_id != args.decision_id:
            print(
                f"Error: artifact decision_id {decision.decision_id!r} does not match filename stem {args.decision_id!r}",
                file=sys.stderr,
            )
            return 1
        elicitation = None
        out = {
            "authored": {
                "decision_id": decision.decision_id,
                "question": decision.unresolved_choice.question,
                "options": decision.unresolved_choice.options,
                "alternative_ids": decision.alternative_ids,
                "combination": decision.combination.model_dump(),
                "criterion": decision.criterion.model_dump(),
                "hard_constraints": [c.model_dump() for c in decision.hard_constraints],
                "required_characters": [c.model_dump() for c in decision.required_characters],
                "blocked_provenance": [r.model_dump() for r in decision.blocked_provenance.outcome_refs],
                "default_references": [r.model_dump() for r in decision.default_references],
                "alternative_bindings": [
                    {"alternative_id": b.alternative_id,
                     "references": [{"entity_ref": r.entity_ref,
                                     "relationship": r.relationship.value}
                                    for r in b.references]}
                    for b in decision.alternative_bindings
                ],
                "structural_anchors": [
                    {"anchor_id": a.anchor_id, "kind": a.kind.value,
                     "participants": a.participants, "carrier_refs": a.carrier_refs,
                     "bears_on": [{"ref": b.ref, "relationship": b.relationship.value,
                                  "nature": b.nature.value if b.nature else None} for b in a.bears_on]}
                    for a in decision.structural_anchors
                ],
                "combination_direction": decision.combination_direction,
                "goal_significance": (
                    decision.goal_significance.model_dump()
                    if decision.goal_significance else None
                ),
                "chosen": decision.chosen,
                "elicitation": elicitation,
            },
            "resolved": None,
            "acceptance": None,
        }
        if args.identity and args.blueprint:
            try:
                identity = _load_identity(args.identity)
                blueprint = _load_blueprint(args.blueprint)
                ctx = build_decision_context(decision, identity, blueprint)
                report = ctx.build_report()
                elicitation = _elicitation_state(decision, report)
                if elicitation["state"] == "unsettled":
                    elicitation["command"] = (
                        f"auteur decision elicit {decision.decision_id} "
                        f"--identity {args.identity} --blueprint {args.blueprint} "
                        f"--project {args.project}"
                    )
                out["authored"]["elicitation"] = elicitation
                out["resolved"] = {
                    "constraints": [{"ref": c.ref, "text": c.text} for c in ctx.constraints],
                    "blocked_provenance": {"expected": ctx.blocked_count, "verified": ctx.blocked_provenance_verified},
                    "resolved_defaults": ctx.resolved_defaults,
                    "resolved_bindings": [
                        {"alternative_id": rb.alternative_id, "entity_ref": rb.entity_ref,
                         "relationship": rb.relationship.value}
                        for rb in ctx.resolved_bindings
                    ],
                    "resolved_anchors": [
                        {"anchor_id": ra.anchor_id, "kind": ra.kind.value,
                         "participants": [ref for _, ref in ra.participants],
                         "carrier_refs": [ref for _, ref in ra.carrier_refs],
                         "bears_on": [{"ref": ref, "value": _record_value(value),
                                       "nature": nature.value if nature else None}
                                      for ref, value, nature in ra.bears_on]}
                        for ra in ctx.resolved_anchors
                    ],
                    "combination_direction": ctx.combination_direction,
                }
            except (DecisionValidationError, FileNotFoundError) as exc:
                out["resolved"] = {"error": str(exc)}
        record = store.load_acceptance_record(args.project, args.decision_id)
        if record is not None:
            out["acceptance"] = {
                "accepted_at": record["accepted_at"],
                "identity_fingerprint": record["identity_fingerprint"],
                "blueprint_fingerprint": record["blueprint_fingerprint"],
            }
            if args.identity and args.blueprint:
                current = {
                    "identity_fingerprint": store.sha256_file(args.identity),
                    "blueprint_fingerprint": store.sha256_file(args.blueprint),
                }
                stale = current != {
                    "identity_fingerprint": record["identity_fingerprint"],
                    "blueprint_fingerprint": record["blueprint_fingerprint"],
                }
                out["acceptance"]["staleness"] = "STALE" if stale else "CURRENT"
        if args.json:
            print(_yaml.safe_dump(out, sort_keys=False))
        else:
            print(f"=== AUTHORED: {out['authored']['decision_id']} ===")
            print(f"Question: {out['authored']['question']}")
            print(f"Options (authored): {out['authored']['options']}")
            print(f"Combination: {out['authored']['combination']}")
            print(f"Criterion: {out['authored']['criterion']}")
            print(f"Constraint refs (authored): {[c['ref'] for c in out['authored']['hard_constraints']]}")
            print(f"Alternative bindings (authored): {[(b['alternative_id'], [(r['entity_ref'], r['relationship']) for r in b['references']]) for b in out['authored']['alternative_bindings']]}")
            print(f"Structural anchors (authored): {[(a['anchor_id'], a['kind'], a['participants'], a['carrier_refs'], a['bears_on']) for a in out['authored']['structural_anchors']]}")
            print(f"Combination direction (authored): {out['authored']['combination_direction']}")
            print(f"Goal significance (authored, decision-scoped): {out['authored']['goal_significance']}")
            print(f"Chosen (authored): {out['authored']['chosen']}")
            if out["authored"].get("elicitation") and out["authored"]["elicitation"]["state"] != "declared":
                _render_elicitation_hint(decision, args, out["authored"]["elicitation"]["state"])
            if out["resolved"] is not None:
                print("=== RESOLVED ===")
                if "error" in out["resolved"]:
                    print(f"resolution failed: {out['resolved']['error']}")
                else:
                    print(f"constraints: {len(out['resolved']['constraints'])} resolved verbatim")
                    print(f"blocked provenance: {out['resolved']['blocked_provenance']}")
                    print(f"product defaults: {out['resolved']['resolved_defaults']}")
                    print(f"resolved bindings: {[(r['alternative_id'], r['entity_ref'], r['relationship']) for r in out['resolved']['resolved_bindings']]}")
                    print(f"resolved anchors: {[(r['anchor_id'], r['participants'], r['bears_on']) for r in out['resolved']['resolved_anchors']]}")
            else:
                print("=== RESOLVED: not shown (pass --identity/--blueprint) ===")
            if out["acceptance"] is not None:
                print("=== ACCEPTANCE ===")
                print(f"accepted_at: {out['acceptance']['accepted_at']}")
                if "staleness" in out["acceptance"]:
                    print(f"staleness vs current Identity/Blueprint: {out['acceptance']['staleness']}")
            else:
                print("=== ACCEPTANCE: none (authored only) ===")
        return 0
    except (DecisionValidationError, FileNotFoundError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:  # pragma: no cover
        print(f"Error: {exc}", file=sys.stderr)
        return 1


def handle_elicit(args) -> int:
    """F3 (design 2026-08-f3-elicitation.md @ 37bc784): consequence-focused
    elicitation for a genuinely unsettled author. Render mode (default) shows the
    ALREADY-COMPOSED concrete losses (verbatim nature_consequence findings grouped
    per cut) plus the consequence-focused question and the three valid outcomes —
    nothing inferred from prose, nothing ranked, no recommendation. Record mode
    (--record) writes the author's explicit outcome into the EXISTING F1
    goal_significance field (ordered | unranked), or records undecided by writing
    nothing. Fail-closed via AuthorDecision.from_dict round-trip; authored
    significance is never silently overwritten."""
    try:
        decision = _load_decision(args.project, args.decision_id)
        if decision.decision_id != args.decision_id:
            print(
                f"Error: artifact decision_id {decision.decision_id!r} does not match filename stem {args.decision_id!r}",
                file=sys.stderr,
            )
            return 1
        identity = _load_identity(args.identity)
        blueprint = _load_blueprint(args.blueprint)
        ctx = build_decision_context(decision, identity, blueprint)
        report = ctx.build_report()
        cons = report.get("consequences", {})

        # --- render mode (always shown first) ---
        print(f"=== ELICITATION: {decision.decision_id} ===")
        print(f"Question: {decision.unresolved_choice.question}")
        combos = cons.get("combinations", [])
        if not combos:
            print()
            print("No composed consequences exist for this decision yet — an authored")
            print("combination_direction (one_of means kept or cut) is required before")
            print("the concrete losses of each cut can be composed. Nothing to elicit.")
            if args.record is not None:
                print()
                print("No outcome can be recorded against an uncomposed decision.")
            return 0 if args.record is None else 1
        print()
        print("CONCRETE CONSEQUENCES (composed, verbatim):")
        for combo in combos:
            cut_members = combo.get("cut") or []
            findings = combo.get("findings", [])
            for member in cut_members:
                print(f"  If you CUT {member}, you remove:")
                removes = [
                    f["message"] for f in findings
                    if f.get("probe_id") == "nature_consequence"
                    and f["message"].startswith(f"cut alternative {member} removes")
                ]
                if not removes:
                    print("    (no declared nature consequences for this cut)")
                for msg in removes:
                    print(f"    - {msg}")
        print()
        print("QUESTION (consequence-focused):")
        print("  Which of these concrete losses would you regret more?")
        print()
        print("VALID OUTCOMES (nothing is recorded unless you choose):")
        print("  - you discover a priority       -> --record ordered <REF1> <REF2>")
        print("       (auteur decision elicit <id> --identity ... --blueprint ...)")
        print("  - intentional non-precedence    -> --record unranked")
        print("       (auteur decision elicit <id> --identity ... --blueprint ...)")
        print("  - still genuinely undecided     -> --record undecided (nothing is written)")
        print("       (auteur decision elicit <id> --identity ... --blueprint ...)")

        # --- record mode: explicit author action ---
        if args.record is None:
            return 0
        if decision.goal_significance is not None:
            print(
                "Error: this decision already declares authored significance "
                f"({decision.goal_significance.model_dump()}); elicitation is for "
                "genuinely unsettled decisions. Edit the decision YAML directly to "
                "change an existing declaration.",
                file=sys.stderr,
            )
            return 1
        if args.refs and args.record in ("unranked", "undecided"):
            print(
                "Warning: --refs are ignored for --record "
                f"{args.record} (refs apply only to --record ordered).",
                file=sys.stderr,
            )
        if args.record == "undecided":
            print()
            print("Recorded: continue-undecided. The decision remains genuinely")
            print("undecided — a valid outcome. No significance field was written;")
            print("you may revisit this tradeoff later.")
            return 0
        if args.record == "ordered":
            if not args.refs or len(args.refs) != 2:
                print("Error: --record ordered requires exactly two --refs (most significant first).",
                      file=sys.stderr)
                return 1
            goal_significance = {"ordered": list(args.refs)}
        else:  # unranked
            goal_significance = {"unranked": True}

        # Fail-closed write: round-trip the whole artifact through the schema.
        path = store.artifact_path(args.project, args.decision_id)
        data = store.read_yaml(path)
        data["goal_significance"] = goal_significance
        AuthorDecision.from_dict(data)  # raises DecisionValidationError on any violation
        store.atomic_write_yaml(path, data)
        print()
        print(f"Recorded into the existing F1 goal_significance field: {goal_significance}")
        if args.record == "ordered":
            print(f"Authored significance (this decision): {args.refs[0]} > {args.refs[1]}")
        return 0
    except (DecisionValidationError, FileNotFoundError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:  # pragma: no cover
        print(f"Error: {exc}", file=sys.stderr)
        return 1


def _render_consequences(c: dict) -> None:
    """Deterministic text rendering of the consequence inventory (no ranking)."""
    if not c:
        return
    n_obs = len(c.get("observations", []))
    n_alt = sum(len(a.get("findings", [])) for a in c.get("alternatives", []))
    axes = c.get("distinguishability_axes", [])
    status = c.get("distinguishability", "COMMON_ONLY")
    if axes:
        print(f"Consequences: {n_obs} observation(s), {n_alt} per-alternative finding(s); "
              f"distinguishability: {status} [{', '.join(axes)}]")
    else:
        print(f"Consequences: {n_obs} observation(s), {n_alt} per-alternative finding(s); "
              f"distinguishability: {status}")
    note = c.get("distinguishability_note")
    if note:
        print(f"  {note}")
    for f in c.get("observations", []):
        print(f"  [{f['severity']}] ({f['probe_id']}) {f['message']}")
    for a in c.get("alternatives", []):
        for f in a.get("findings", []):
            print(f"  [{f['severity']}] ({f['probe_id']}) {f['message']}")
    for combo in c.get("combinations", []):
        kept = combo.get("kept")
        cut = combo.get("cut")
        line = f"  combination {combo['combination']}"
        if kept is not None and cut is not None:
            line += f" (kept: {kept}, cut: {cut})"
        print(line)
        for f in combo.get("findings", []):
            print(f"    [{f['severity']}] ({f['probe_id']}) {f['message']}")
    print("No consequence implies a recommendation; alternatives are not ranked.")


def _load_identity(path: Path):
    from auteur.identity import StoryIdentity

    return StoryIdentity.from_yaml(path)


def _load_blueprint(path: Path):
    from auteur.blueprint import StoryBlueprint

    return StoryBlueprint.from_yaml(path)
