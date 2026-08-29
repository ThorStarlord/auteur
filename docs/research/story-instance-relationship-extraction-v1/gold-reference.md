# Story-Instance Relationship Extraction V1 — Minimal Gold Reference

**Status:** FROZEN WITH PROTOCOL — NOT EXPOSED TO EXTRACTOR

This file defines the smallest gold relationship subset needed to test the V3
causal/pressure-grouping mechanism. It is not a production ontology and is not
the full V3 golden ledger.

## Source boundary

All source facts come from the frozen Archive of Lies fixture and the V3 source
manifest at the V3 starting revision. The relevant accepted source rows are:

- `series_direction.yaml` — `contested-history` commitment;
- `book_1_realization.yaml` — `founding-record`;
- `book_2_realization.yaml` — ordered `public-admission` then
  `admission-retracted`;
- `book_3_direction.yaml` — protect archive after retraction;
- `book_3_realization.yaml` — `archive-protected`; and
- the derived Canonical State/transition lineage used only to identify current
  state and source references.

Planning intent is a non-authoritative downstream relevance trigger. It is not
evidence for persistent relation extraction.

## Relation vocabulary

The vocabulary is deliberately small:

| type | meaning | allowed shape |
|---|---|---|
| `CAUSAL_SUPPORT` | an accepted earlier event/history materially supports or motivates a later accepted constraint | one source fact to one target fact |
| `PRESSURE_GROUP` | accepted facts collectively instantiate one named accepted Series pressure | two or more source/member facts to one pressure target, with member roles |

`PRESSURE_GROUP` is not a new narrative entity. Its target is a research-local
label that must cite the accepted Series commitment which names the pressure.

## Frozen gold entries

### `GOLD-R01` — retraction supports treaty protection

| field | value |
|---|---|
| relation type | `CAUSAL_SUPPORT` |
| source/member facts | `ST-F5` / `admission-retracted` |
| target | `ST-F6` / `archive-protected` |
| role | `causal_pivot` → `current_constraint` |
| evidence basis | Book 3 Direction explicitly wants to protect the archive after the accepted retraction; Book 3 realization records treaty protection as the evidentiary chain's protection |
| authority | `INTERPRETIVE` — source-backed causal interpretation, not a new accepted event |
| exact recovery | exact endpoints and causal direction required; equivalent wording such as “retraction motivated treaty protection” accepted |
| omission severity | `SEVERE` for P03/P04/P05; non-consequential for P02 because `ST-F6` is outside its horizon |

### `GOLD-R02` — contested-history pressure group

| field | value |
|---|---|
| relation type | `PRESSURE_GROUP` |
| source/member facts | `ST-F1` / `founding-record`; `ST-F5` / `admission-retracted`; `ST-F6` / `archive-protected` |
| target | `contested-history` Series commitment/pressure |
| member roles | `ST-F1` = `originating_history`; `ST-F5` = `causal_pivot`; `ST-F6` = `current_constraint` |
| evidence basis | accepted Series commitment plus carried commitment references in Books 1–3; member transitions are accepted and ordered/current by the source history |
| authority | `DETERMINISTIC_DERIVATION` for membership and roles under the preregistered grouping rule; the plain-language “pressure cluster” label is a derived projection |
| exact recovery | semantic member-set and role-equivalent recovery accepted; exact label wording not required |
| omission severity | `SEVERE` for P05; `MODERATE` for P03/P04; non-consequential for P02 |

No thematic or interpretive annotation such as V3 REL-10 is in the gold set.
No unaccepted proposal (`burn-archive`, `ally-militia`) is a member or target.
The lantern transitions are not members.

## Gold construction rules

1. Include only relations whose endpoints and evidence are within the probe's
   accepted horizon.
2. A causal relation requires an accepted source-backed sequence or explicit
   accepted Direction/realization basis; plausible narrative causality alone
   is insufficient.
3. A pressure group requires a named accepted Series commitment and at least
   two accepted consequences whose carried commitment/history supports the
   grouping.
4. Roles are derived from accepted order/current-state evidence, not model
   intuition: originating history precedes the pivot, causal pivot supports a
   later consequence, and current constraint is the latest accepted state
   governing the Book-4 decision.
5. A relation may be omitted when an endpoint is outside the horizon. The
   extractor must abstain rather than backfill a later fact.
6. An equivalent semantic relation with different prose is correct only when
   direction, members, target, source grounding, and authority class remain
   correct.

## Probe projection

| probe | visible gold overlay |
|---|---|
| P02 | empty target overlay; `ST-F6` and the Book-4 target mechanism are outside the accepted horizon |
| P03 | `GOLD-R01` and `GOLD-R02` |
| P04 | `GOLD-R01` and `GOLD-R02` |
| P05 | `GOLD-R01` and `GOLD-R02` |

The empty P02 projection is intentional: it is the currentness control, not an
attempt to make the relationship family answer every decision.

## Leakage boundary

The extractor may receive source-faithful fact text, stable source references,
ordered transition metadata, and the extraction contract's generic vocabulary
definitions. It must not receive:

- this file or its contents;
- `GOLD-R01`, `GOLD-R02`, `ST-F1`, `ST-F5`, or `ST-F6` as expected answer IDs;
- V3 ledger relation IDs or dispositions;
- V3 evaluator rubric, must-not-miss items, forbidden criteria, or result;
- condition names or expected winners; or
- the downstream question/options as answer cues.

The evaluator receives this gold reference only after extraction outputs are
raw-captured and sealed, through the separate blinded extraction-evaluation
packet process.
