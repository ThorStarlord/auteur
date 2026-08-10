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


def author_decision_handlers() -> dict:
    return {
        "create": handle_create,
        "accept": handle_accept,
        "evaluate": handle_evaluate,
        "view": handle_view,
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


def handle_view(args) -> int:
    try:
        decision = _load_decision(args.project, args.decision_id)
        if decision.decision_id != args.decision_id:
            print(
                f"Error: artifact decision_id {decision.decision_id!r} does not match filename stem {args.decision_id!r}",
                file=sys.stderr,
            )
            return 1
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
                     "references": [r.model_dump() for r in b.references]}
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
            },
            "resolved": None,
            "acceptance": None,
        }
        if args.identity and args.blueprint:
            try:
                identity = _load_identity(args.identity)
                blueprint = _load_blueprint(args.blueprint)
                ctx = build_decision_context(decision, identity, blueprint)
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
