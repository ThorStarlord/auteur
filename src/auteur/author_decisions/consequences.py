"""Bounded deterministic decision consumer (mechanism B): representational
consequence inventory.

Consumes an accepted ``AuthorDecision`` + its resolved context and reports
observable structural consequences, grouped per alternative / per combination.

Authority rules (design revision 1, 2026-08 — binding):
- NO alternative->character/thread/provenance relationship may be inferred from
  ids, labels, prose, token matching, fuzzy matching, or semantic similarity.
- Per-alternative consequences require an explicitly accepted relationship;
  ``default_references[].relates_to`` is currently the ONLY shipped explicit
  cross-reference mechanism and is consumed as such.
- ``roster_slot`` / ``thread_carrier`` / ``blocked_provenance_relevance`` are
  decision-level (common) probes.
- ``COMMON_ONLY`` is a valid successful result.
- No ranking, score, recommendation, verdict, mutation, or as-if propagation.
"""
from __future__ import annotations

import itertools
import json
import re
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from auteur.author_decisions.models import AuthorDecision

# Explicit identity field path, e.g. "characters[3].undergoes_central_change".
_IDENTITY_CHAR_REF_RE = re.compile(r"^characters\[(\d+)\]\.(.+)$")


class ConsequenceRefs(BaseModel):
    """Exact field-path provenance for one consequence finding.

    Every ref points at the artifact / Identity / Blueprint field the finding
    was computed from. Never dropped by grouping (see ``members``).
    """

    model_config = ConfigDict(extra="forbid")

    decision: str | None = None
    identity: str | None = None
    blueprint: str | None = None
    outcome: str | None = None


class DecisionConsequence(BaseModel):
    """One observable structural consequence.

    Deliberately contains no score/rank/verdict/recommended field; messages are
    fixed probe-registry templates quoting verbatim resolved values.
    """

    model_config = ConfigDict(extra="forbid")

    probe_id: str
    severity: Literal["info", "warning"]
    message: str
    refs: ConsequenceRefs = Field(default_factory=ConsequenceRefs)
    scope: Literal["alternative", "combination", "common"] = "common"
    target: str = ""
    discriminates: bool = False
    members: list[str] = Field(default_factory=list)


def _fmt_value(value: Any) -> str:
    """Deterministic verbatim formatting of a resolved product value."""
    if isinstance(value, list):
        return "[" + ", ".join(str(v) for v in value) + "]"
    return str(value)


# ---------------------------------------------------------------------------
# Probes (registry order defines canonical report ordering)
# ---------------------------------------------------------------------------

def _probe_explicit_alternative_relations(decision: AuthorDecision) -> list[DecisionConsequence]:
    """Schema-capability statement: per-alternative roster/thread/provenance
    probes require an explicit alternative-entity relation, which the shipped
    AuthorDecision schema does not expose."""
    return [DecisionConsequence(
        probe_id="explicit_alternative_relations",
        severity="info",
        message=(
            "per-alternative roster/thread/provenance probes were not run: "
            "the AuthorDecision schema exposes no explicit alternative-entity relationship"
        ),
        refs=ConsequenceRefs(decision="default_references"),
    )]


def _probe_combination_direction(decision: AuthorDecision) -> list[DecisionConsequence]:
    """Neutral statement for choose_k_of_n: membership is explicit, the
    keep/cut direction is not machine-decidable and is never interpreted."""
    if decision.combination.rule != "choose_k_of_n":
        return []
    return [DecisionConsequence(
        probe_id="combination_direction",
        severity="info",
        message="combination membership is explicit; keep/cut interpretation is unspecified",
        refs=ConsequenceRefs(decision="combination"),
    )]


def _probe_roster_slot(decision: AuthorDecision, identity, blueprint) -> list[DecisionConsequence]:
    """Decision-level roster probe over required_characters (explicit authored
    names). Lookup is exact name equality of an explicit reference — never
    label/id matching."""
    out: list[DecisionConsequence] = []
    for i, rc in enumerate(decision.required_characters):
        ident_idx = next((j for j, c in enumerate(identity.characters) if c.name == rc.name), None)
        if ident_idx is None:
            out.append(DecisionConsequence(
                probe_id="roster_slot",
                severity="info",
                message=f"probe not run: no identity character named {rc.name}",
                refs=ConsequenceRefs(decision=f"required_characters[{i}]"),
            ))
            continue
        bp_idx = next((k for k, c in enumerate(blueprint.characters) if c.name == rc.name), None)
        standing = rc.standing or "unset"
        if bp_idx is None:
            out.append(DecisionConsequence(
                probe_id="roster_slot",
                severity="warning",
                message=(
                    f"required character {rc.name} (standing={standing}) has no "
                    "roster slot in the current Blueprint"
                ),
                refs=ConsequenceRefs(
                    decision=f"required_characters[{i}]",
                    identity=f"characters[{ident_idx}]",
                ),
            ))
            continue
        ch = blueprint.characters[bp_idx]
        refs = ConsequenceRefs(
            decision=f"required_characters[{i}]",
            identity=f"characters[{ident_idx}]",
            blueprint=f"characters[{bp_idx}]",
        )
        out.append(DecisionConsequence(
            probe_id="roster_slot",
            severity="info",
            message=(
                f"required character {rc.name} (standing={standing}) is represented "
                f"in the roster as {ch.role.value}, arc {ch.arc_type.value}"
            ),
            refs=refs,
        ))
        if ch.identity is None:
            out.append(DecisionConsequence(
                probe_id="roster_slot",
                severity="warning",
                message=f"roster slot for {rc.name} is not linked to an identity character",
                refs=refs,
            ))
    return out


def _probe_thread_carrier(blueprint) -> list[DecisionConsequence]:
    """Schema-capability statement: the Blueprint exposes no thread-to-character
    linkage, so carriers cannot be verified. Never matches thread text/names."""
    engine = blueprint.story_engine
    threads = engine.threads if engine is not None else None
    if not threads:
        return [DecisionConsequence(
            probe_id="thread_carrier",
            severity="info",
            message="probe not run: blueprint has no thread structure",
            refs=ConsequenceRefs(blueprint="story_engine.threads"),
        )]
    names = ", ".join(t.name for t in threads)
    return [DecisionConsequence(
        probe_id="thread_carrier",
        severity="info",
        message=(
            f"thread structure has {len(threads)} thread(s): {names}; the Blueprint "
            "exposes no explicit thread-to-character linkage, so thread carriers for "
            "decision characters cannot be verified"
        ),
        refs=ConsequenceRefs(blueprint="story_engine.threads"),
    )]


def _probe_declared_relationship(decision: AuthorDecision, resolved_defaults: dict) -> list[DecisionConsequence]:
    """Explicitly authored default_references[].relates_to — the ONLY shipped
    explicit cross-reference mechanism. Target = alternative_id -> per-alternative
    finding; any other target -> common observation. Quotes the author's
    declaration; never asserts the relationship holds."""
    out: list[DecisionConsequence] = []
    alt_ids = set(decision.alternative_ids)
    for i, dref in enumerate(decision.default_references):
        value = resolved_defaults.get(dref.default_id, "<unresolved>")
        severity = "warning" if dref.relationship == "conflicts_with" else "info"
        message = (
            f"declared relationship: {dref.default_id} = {_fmt_value(value)} "
            f"[{dref.relationship}] relates_to {dref.relates_to}"
        )
        if dref.relates_to in alt_ids:
            out.append(DecisionConsequence(
                probe_id="declared_relationship",
                severity=severity,
                message=message,
                refs=ConsequenceRefs(decision=f"default_references[{i}]", blueprint=dref.default_id),
                scope="alternative",
                target=dref.relates_to,
            ))
        else:
            out.append(DecisionConsequence(
                probe_id="declared_relationship",
                severity=severity,
                message=message,
                refs=ConsequenceRefs(decision=f"default_references[{i}]", blueprint=dref.default_id),
            ))
    return out


def _probe_blocked_provenance_relevance(decision: AuthorDecision, identity) -> list[DecisionConsequence]:
    """Decision-level probe: blocked outcome refs whose explicit identity field
    path resolves (by exact name equality) to a required character."""
    required_names = [rc.name for rc in decision.required_characters]
    relevant: list[str] = []
    for ref in decision.blocked_provenance.outcome_refs:
        src = ref.source or ""
        m = _IDENTITY_CHAR_REF_RE.fullmatch(src)
        if not m:
            continue
        idx = int(m.group(1))
        if 0 <= idx < len(identity.characters) and identity.characters[idx].name in required_names:
            relevant.append(src)
    if relevant:
        message = (
            f"{len(relevant)} blocked propagation outcome(s) reference decision "
            f"characters: {', '.join(relevant)}; the decision does not resolve them"
        )
        severity = "warning"
    else:
        message = "no blocked propagation outcomes reference decision characters"
        severity = "info"
    return [DecisionConsequence(
        probe_id="blocked_provenance_relevance",
        severity=severity,
        message=message,
        refs=ConsequenceRefs(
            decision="blocked_provenance.outcome_refs",
            blueprint="identity_propagation.outcomes",
        ),
    )]


# ---------------------------------------------------------------------------
# Builder: grouping, provenance-preserving common extraction, distinguishability
# ---------------------------------------------------------------------------

def build_consequences(ctx) -> dict[str, Any]:
    """Deterministic consequence inventory for an accepted decision context."""
    decision = ctx.decision
    identity = ctx.identity
    blueprint = ctx.blueprint
    alt_ids = list(decision.alternative_ids)

    common: list[DecisionConsequence] = []
    alt_map: dict[str, list[DecisionConsequence]] = {a: [] for a in alt_ids}

    for finding in (
        _probe_explicit_alternative_relations(decision)
        + _probe_combination_direction(decision)
        + _probe_roster_slot(decision, identity, blueprint)
        + _probe_thread_carrier(blueprint)
        + _probe_declared_relationship(decision, ctx.resolved_defaults)
        + _probe_blocked_provenance_relevance(decision, identity)
    ):
        if finding.scope == "alternative":
            alt_map.setdefault(finding.target, []).append(finding)
        else:
            common.append(finding)

    # Provenance-preserving common extraction: lift findings that are identical
    # (probe_id, message, refs) across EVERY alternative; lifted entries keep
    # their exact refs and record every member they were computed over.
    def _sig(f: DecisionConsequence) -> tuple:
        return (f.probe_id, f.message, json.dumps(f.refs.model_dump(), sort_keys=True))

    reps = {_sig(f): f for f in alt_map[alt_ids[0]]}
    lift_sigs = set()
    if alt_ids and alt_map[alt_ids[0]]:
        for sig in reps:
            if all(any(_sig(f) == sig for f in alt_map[a]) for a in alt_ids[1:]):
                lift_sigs.add(sig)
    for sig in lift_sigs:
        rep = reps[sig]
        common.append(DecisionConsequence(
            **rep.model_dump(), scope="common", target="",
            discriminates=False, members=alt_ids,
        ))
        for alt in alt_ids:
            alt_map[alt] = [f for f in alt_map[alt] if _sig(f) != sig]

    for f in common:
        f.members = alt_ids
        f.discriminates = False
    for alt in alt_ids:
        for f in alt_map[alt]:
            f.scope = "alternative"
            f.target = alt
            f.members = [alt]
            f.discriminates = True

    axes = sorted({f.probe_id for alt in alt_ids for f in alt_map[alt]})
    if not axes:
        status = "COMMON_ONLY"
        note = ("all alternatives share these consequences; the current "
                "representation cannot distinguish them further")
    elif len(axes) == 1:
        status = "SINGLE_AXIS"
        note = f"only this structural axis differs: {axes[0]}"
    else:
        status = "MULTIPLE_AXES"
        note = f"alternatives differ on axes: {', '.join(axes)}"

    report: dict[str, Any] = {
        "observations": [f.model_dump() for f in common],
        "alternatives": [
            {"alternative_id": a, "findings": [f.model_dump() for f in alt_map[a]]}
            for a in alt_ids
        ],
        "distinguishability": status,
        "distinguishability_axes": axes,
        "distinguishability_note": note,
    }

    if decision.combination.rule == "choose_k_of_n":
        k = decision.combination.k or 1
        combos: list[dict] = []
        for combo in itertools.combinations(alt_ids, k):
            target = repr(tuple(combo))
            findings: list[DecisionConsequence] = []
            for cid in combo:
                for f in alt_map[cid]:
                    findings.append(DecisionConsequence(
                        **f.model_dump(), scope="combination",
                        target=target, members=[target],
                    ))
            combos.append({
                "combination": list(combo),
                "findings": [f.model_dump() for f in findings],
            })
        report["combinations"] = combos

    return report
