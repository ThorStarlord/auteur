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

from auteur.author_decisions.models import AuthorDecision, DecisionValidationError, RequiredCharacter, StructuralAnchor

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
    """choose_k_of_n membership semantics: an authored combination_direction
    is reported verbatim; otherwise membership-only is stated and the
    keep/cut interpretation is never inferred."""
    if decision.combination.rule != "choose_k_of_n":
        return []
    if decision.combination_direction is not None:
        message = (
            f"authored combination direction: choose_k_of_n k={decision.combination.k} "
            f"means {decision.combination_direction}"
        )
    else:
        message = "combination membership is explicit; keep/cut interpretation is unspecified"
    return [DecisionConsequence(
        probe_id="combination_direction",
        severity="info",
        message=message,
        refs=ConsequenceRefs(decision="combination"),
    )]


def _probe_roster_slot(decision: AuthorDecision, identity, blueprint,
                       required: list[RequiredCharacter] | None = None,
                       decision_ref: str = "required_characters") -> list[DecisionConsequence]:
    """Roster probe over explicit character names (decision-level
    required_characters by default; M1 bindings pass a per-alternative scope).
    Lookup is exact name equality of an explicit reference — never
    label/id matching."""
    required_list = list(decision.required_characters) if required is None else list(required)
    out: list[DecisionConsequence] = []
    for i, rc in enumerate(required_list):
        ident_matches = [j for j, c in enumerate(identity.characters) if c.name == rc.name]
        if not ident_matches:
            out.append(DecisionConsequence(
                probe_id="roster_slot",
                severity="info",
                message=f"probe not run: no identity character named {rc.name}",
                refs=ConsequenceRefs(decision=f"{decision_ref}[{i}]"),
            ))
            continue
        if len(ident_matches) > 1:
            out.append(DecisionConsequence(
                probe_id="roster_slot",
                severity="info",
                message=f"probe not run: ambiguous identity name {rc.name}",
                refs=ConsequenceRefs(decision=f"{decision_ref}[{i}]"),
            ))
            continue
        ident_idx = ident_matches[0]
        bp_matches = [k for k, c in enumerate(blueprint.characters) if c.name == rc.name]
        if not bp_matches:
            out.append(DecisionConsequence(
                probe_id="roster_slot",
                severity="warning",
                message=(
                    f"required character {rc.name} (standing={rc.standing or 'unset'}) has no "
                    "roster slot in the current Blueprint"
                ),
                refs=ConsequenceRefs(
                    decision=f"{decision_ref}[{i}]",
                    identity=f"characters[{ident_idx}]",
                ),
            ))
            continue
        if len(bp_matches) > 1:
            out.append(DecisionConsequence(
                probe_id="roster_slot",
                severity="info",
                message=f"probe not run: ambiguous roster name {rc.name}",
                refs=ConsequenceRefs(
                    decision=f"{decision_ref}[{i}]",
                    identity=f"characters[{ident_idx}]",
                ),
            ))
            continue
        bp_idx = bp_matches[0]
        ch = blueprint.characters[bp_idx]
        standing = rc.standing or "unset"
        refs = ConsequenceRefs(
            decision=f"{decision_ref}[{i}]",
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


def _probe_blocked_provenance_relevance(decision: AuthorDecision, identity,
                                          required_names: list[str] | None = None) -> list[DecisionConsequence]:
    """Probe: blocked outcome refs whose explicit identity field path resolves
    (by exact name equality) to a character in scope (decision-level
    required_characters by default; M1 bindings pass a per-alternative scope)."""
    if required_names is None:
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


def _entity_summary(entity) -> str:
    """Deterministic verbatim summary of a resolved binding entity."""
    anchor_id = getattr(entity, "anchor_id", None)
    if anchor_id is not None:
        return f"anchor {anchor_id}"
    name = getattr(entity, "name", None)
    if name is None:
        return _fmt_value(entity)
    role = getattr(entity, "structural_role", None) or getattr(entity, "role", None)
    if role is None:
        return name
    role = getattr(role, "value", role)
    arc = getattr(entity, "arc_type", None)
    arc = getattr(arc, "value", arc)
    if arc is not None:
        return f"{name} (role={role}, arc={arc})"
    return f"{name} (role={role})"


def _bound_standing(entity) -> str | None:
    """M1 bound scope standing: the identity character's structural_role when
    present (authoritative identity data), else None -> 'unset' in messages."""
    role = getattr(entity, "structural_role", None)
    if role is None:
        return None
    return str(getattr(role, "value", role))


def _probe_entity_link(alt_id: str, bindings) -> list[DecisionConsequence]:
    """M1 link echo (design Q7): quotes the authored binding with its resolved
    value; follows the shipped declared_relationship conventions (never asserts
    the relationship holds). Refs are root-routed: identity refs point at the
    identity slot, blueprint refs at the blueprint slot."""
    out: list[DecisionConsequence] = []
    for rb in bindings:
        summary = _entity_summary(rb.entity)
        severity = "warning" if rb.relationship.value == "conflicts_with" else "info"
        refs = ConsequenceRefs(decision=f"alternative_bindings[{alt_id}]")
        # the decision slot is ARTIFACT provenance (the binding block);
        # identity/blueprint slots hold the resolved entity path; decision-root
        # entity paths stay verbatim in the message (no slot collision)
        if rb.entity_ref.startswith("identity."):
            refs.identity = rb.entity_ref
        elif rb.entity_ref.startswith("blueprint."):
            refs.blueprint = rb.entity_ref
        out.append(DecisionConsequence(
            probe_id="entity_link",
            severity=severity,
            message=(
                f"declared entity link: alternative {alt_id} [{rb.relationship.value}] "
                f"relates to {rb.entity_ref} = {summary}"
            ),
            refs=refs,
            scope="alternative",
            target=alt_id,
            discriminates=True,
        ))
    return out


def _probe_binding_absence(alt_id: str) -> list[DecisionConsequence]:
    """M1 absence semantics (design Q3): no binding supplied for this
    alternative. Reported as an info finding — never as 'concerns nothing',
    never inferred."""
    return [DecisionConsequence(
        probe_id="binding_absence",
        severity="info",
        message="probe not run: no explicit binding for this alternative",
        refs=ConsequenceRefs(decision="alternative_bindings"),
        scope="alternative",
        target=alt_id,
        discriminates=True,
    )]


def _probe_anchor(alt_id: str, anchor, ctx, identity, blueprint) -> list[DecisionConsequence]:
    """B4 anchor consumption (design Q10): per-alternative consequences derived
    ONLY from the explicit anchor rows — participant roster status, carrier
    presence/absence, bears_on echoes. Never decides the creative answer."""
    ra = next((r for r in getattr(ctx, "resolved_anchors", []) or []
               if r.anchor_id == anchor.anchor_id), None)
    if ra is None:
        return [DecisionConsequence(
            probe_id="resolution_error", severity="warning",
            message=f"anchor {anchor.anchor_id!r} was not resolved",
            refs=ConsequenceRefs(decision="structural_anchors"),
            scope="alternative", target=alt_id, discriminates=True,
        )]
    out: list[DecisionConsequence] = []
    refs = ConsequenceRefs(decision=f"structural_anchors[{anchor.anchor_id}]")
    if ra.participants:
        required = [RequiredCharacter(
            name=getattr(e, "name", None) or ref,
            standing=_bound_standing(e),
        ) for e, ref in ra.participants]
        for f in _probe_roster_slot(None, identity, blueprint, required=required,
                                    decision_ref=f"structural_anchors[{anchor.anchor_id}]"):
            d = f.model_dump()
            d["scope"] = "alternative"
            d["target"] = alt_id
            d["discriminates"] = True
            out.append(DecisionConsequence(**d))
    else:
        out.append(DecisionConsequence(
            probe_id="anchor_participants", severity="info",
            message=f"no participants declared for anchor {anchor.anchor_id}",
            refs=refs, scope="alternative", target=alt_id, discriminates=True,
        ))
    if ra.carrier_refs:
        for entity, ref in ra.carrier_refs:
            out.append(DecisionConsequence(
                probe_id="anchor_carrier", severity="info",
                message=f"anchor {anchor.anchor_id} is carried by {ref} = {_entity_summary(entity)}",
                refs=refs, scope="alternative", target=alt_id, discriminates=True,
            ))
    else:
        out.append(DecisionConsequence(
            probe_id="anchor_carrier", severity="info",
            message=f"no carrier declared for anchor {anchor.anchor_id}",
            refs=refs, scope="alternative", target=alt_id, discriminates=True,
        ))
    if ra.bears_on:
        for ref, value, nature in ra.bears_on:
            if nature is None:
                message = f"anchor {anchor.anchor_id} bears on {ref} = {value}"
            else:
                message = (f"anchor {anchor.anchor_id} bears on {ref} = {value} "
                           f"(nature: {nature.value})")
            out.append(DecisionConsequence(
                probe_id="anchor_bears_on", severity="info",
                message=message,
                refs=refs, scope="alternative", target=alt_id, discriminates=True,
            ))
    else:
        out.append(DecisionConsequence(
            probe_id="anchor_bears_on", severity="info",
            message=f"anchor {anchor.anchor_id} bears on nothing declared",
            refs=refs, scope="alternative", target=alt_id, discriminates=True,
        ))
    return out


_NATURE_WORD = {"sustains": "sustaining", "pressures": "pressuring"}


def _compose_nature_consequence(ctx, alternative_id: str, verb: str, op: str,
                                combo: tuple) -> list[DecisionConsequence]:
    """N1 deterministic composition (design 1.1/1.2/5): for each authored
    bears_on entry with nature on the resolved anchor of ``alternative_id``,
    emit ``<op> alternative <X> <verb>s its declared <nature-word> relationship
    to <ref> = <value>``. ``verb`` is 'remove' for cut members and 'preserve'
    for kept members. ``preserve`` refers ONLY to preserving the declared
    relationship by retaining the anchor — never a judgment that the target
    itself will be preserved. Findings are scoped to the combination exactly
    like the member-copied findings (target=repr(tuple(combo)))."""
    out: list[DecisionConsequence] = []
    target = repr(tuple(combo))
    for ra in getattr(ctx, "resolved_anchors", []) or []:
        # match anchors bound to this alternative
        bound = [rb for rb in getattr(ctx, "resolved_bindings", []) or []
                 if rb.alternative_id == alternative_id
                 and getattr(rb.entity, "anchor_id", None) == ra.anchor_id]
        if not bound:
            continue
        for ref, value, nature in ra.bears_on:
            if nature is None:
                continue
            # explicit closed-vocabulary mapping: an unknown value fails loudly
            nature_word = _NATURE_WORD[nature.value]
            message = (f"{op} alternative {alternative_id} {verb} its declared "
                       f"{nature_word} relationship to {ref} = {value}")
            out.append(DecisionConsequence(
                probe_id="nature_consequence", severity="info",
                message=message,
                refs=ConsequenceRefs(decision=f"structural_anchors[{ra.anchor_id}]"),
                scope="combination", target=target, members=[target], discriminates=True,
            ))
    return out


# ---------------------------------------------------------------------------
# Builder: grouping, provenance-preserving common extraction, distinguishability
# ---------------------------------------------------------------------------

def build_consequences(ctx) -> dict[str, Any]:
    """Deterministic consequence inventory for an accepted decision context.

    ``ctx`` must come from ``build_decision_context`` (which carries the
    resolved Identity and Blueprint objects); missing objects fail closed.
    """
    if getattr(ctx, "identity", None) is None or getattr(ctx, "blueprint", None) is None:
        raise DecisionValidationError(
            "consequence consumer requires the resolved identity and blueprint "
            "(build the context via build_decision_context)"
        )
    decision = ctx.decision
    identity = ctx.identity
    blueprint = ctx.blueprint
    alt_ids = list(decision.alternative_ids)

    common: list[DecisionConsequence] = []
    alt_map: dict[str, list[DecisionConsequence]] = {a: [] for a in alt_ids}

    has_bindings = bool(decision.alternative_bindings)
    probe_set = []
    if not has_bindings:
        # byte-compatible with the shipped surface: the schema-capability
        # statement is only accurate while no alternative-entity relationship
        # mechanism is authored in the artifact.
        probe_set.append(_probe_explicit_alternative_relations(decision))
    probe_set += [
        _probe_combination_direction(decision),
        _probe_roster_slot(decision, identity, blueprint),
        _probe_thread_carrier(blueprint),
        _probe_declared_relationship(decision, ctx.resolved_defaults),
        _probe_blocked_provenance_relevance(decision, identity),
    ]
    for probe_findings in probe_set:
        for finding in probe_findings:
            if finding.scope == "alternative":
                alt_map.setdefault(finding.target, []).append(finding)
            else:
                common.append(finding)

    if has_bindings:
        bindings_by_alt: dict[str, list] = {}
        for rb in getattr(ctx, "resolved_bindings", []) or []:
            bindings_by_alt.setdefault(rb.alternative_id, []).append(rb)
        for alt in alt_ids:
            bound = bindings_by_alt.get(alt, [])
            if not bound:
                alt_map[alt].extend(_probe_binding_absence(alt))
                continue
            char_bound = [rb for rb in bound if not isinstance(rb.entity, StructuralAnchor)]
            anchor_bound = [rb for rb in bound if isinstance(rb.entity, StructuralAnchor)]
            required = [RequiredCharacter(
                name=getattr(rb.entity, "name", None) or rb.entity_ref,
                standing=_bound_standing(rb.entity),
            ) for rb in char_bound]
            if required:
                alt_map[alt].extend(_probe_roster_slot(
                    decision, identity, blueprint, required=required,
                    decision_ref=f"alternative_bindings[{alt}]"))
                alt_map[alt].extend(_probe_blocked_provenance_relevance(
                    decision, identity, required_names=[rc.name for rc in required]))
            for rb in anchor_bound:
                alt_map[alt].extend(_probe_anchor(alt, rb.entity, ctx, identity, blueprint))
            alt_map[alt].extend(_probe_entity_link(alt, bound))

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
    for sig in sorted(lift_sigs):
        rep = reps[sig]
        # DORMANT PATH (bug #59 same root cause): unreachable with the shipped
        # probes — the only per-alternative probe (declared_relationship) embeds
        # the target alternative id in its message, so identical signatures
        # across alternatives cannot occur. model_copy keeps it correct-by-
        # construction if a future probe ever makes it live.
        common.append(rep.model_copy(update={
            "scope": "common", "target": "", "discriminates": False, "members": alt_ids,
        }))
        for alt in alt_ids:
            alt_map[alt] = [f for f in alt_map[alt] if _sig(f) != sig]

    for f in common:
        # Decision-level findings were computed over the decision as a whole;
        # members records every alternative they apply to (grouping provenance).
        f.members = alt_ids
        f.discriminates = False
    for alt in alt_ids:
        for f in alt_map[alt]:
            f.scope = "alternative"
            f.target = alt
            f.members = [alt]
            f.discriminates = True

    axes = sorted({f.probe_id for alt in alt_ids for f in alt_map[alt]})
    # NOTE: distinguishability values are representational-only descriptors of
    # the finding sets (COMMON_ONLY / SINGLE_AXIS / MULTIPLE_AXES); they are
    # NOT evaluative signals about the alternatives and never imply ranking.
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
                    findings.append(f.model_copy(update={
                        "scope": "combination", "target": target, "members": [target],
                    }))
            combo_entry = {
                "combination": list(combo),
                "findings": [f.model_dump() for f in findings],
            }
            direction = getattr(ctx, "combination_direction", None)
            if direction == "kept":
                combo_entry["kept"] = list(combo)
                combo_entry["cut"] = [a for a in alt_ids if a not in combo]
            elif direction == "cut":
                combo_entry["kept"] = [a for a in alt_ids if a not in combo]
                combo_entry["cut"] = list(combo)
            if direction is not None:
                # N1 composed consequence: authored nature x authored kept/cut x
                # resolved target value. States what the operation removes or
                # preserves (the DECLARED relationship), never a judgment on
                # the target itself. Non-ranking / non-verdict.
                for member in combo_entry["cut"]:
                    findings.extend(_compose_nature_consequence(ctx, member, "removes", "cut", combo))
                for member in combo_entry["kept"]:
                    findings.extend(_compose_nature_consequence(ctx, member, "preserves", "kept", combo))
                combo_entry["findings"] = [f.model_dump() for f in findings]
            combos.append(combo_entry)
        report["combinations"] = combos

    return report
