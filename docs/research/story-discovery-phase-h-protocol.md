# Phase H — Live-provider Story Discovery semantic-quality protocol

## Status

**H1 capture infrastructure.** This document defines how raw live-provider evidence is produced. It does not contain a semantic-quality conclusion.

Phase G established the writer-facing Story Discovery workflow under controlled provider outputs. Phase H tests the deferred question: whether real Anthropic/OpenAI behavior produces useful creative reasoning through that qualified product path.

## Research question

> When production Story Discovery is driven by a real provider, are its candidate search, causal analysis, comparative recommendation, craft explanation, and bounded composition semantically good enough to be worth a writer's trust and attention?

## H1 scope

H1 creates only the reproducible evidence-capture layer:

- a versioned corpus of intent-adequate `DiscoveryBrief` cases;
- explicit provider/model/case selection;
- API-key preflight before any provider construction;
- immutable run provenance written before provider execution;
- raw stdout/stderr/exit capture;
- persisted Story Discovery artifacts under a fresh run directory;
- deterministic `story-discovery review` capture after successful discovery;
- a hard check that no canonical `story_identity.yaml` is created;
- offline tests for all harness control behavior.

H1 deliberately **does not grade** candidate quality or recommendation quality. H2 freezes real outputs; H3 performs human semantic adjudication; H4 separately tests live bounded composition.

## Benchmark corpus

The corpus is `docs/research/story-discovery-phase-h-cases.yaml`.

The six cases reuse the high-information premises that drove Phase E founder adjudication, but now encode explicit, production-valid declared intent rather than simulated recommendation prose. This preserves continuity with earlier findings while exercising the actual F2–F4 contracts.

The corpus is versioned and hashed into every run manifest. A changed corpus is a new evidence condition, not a silent continuation of an earlier run.

## Manual run contract

Run from a repository checkout with the relevant optional provider dependency installed.

Dry-run first:

```bash
python scripts/story_discovery_live_eval.py \
  --provider anthropic \
  --case h02_between_floors \
  --output /tmp/auteur-phase-h-anthropic-01 \
  --dry-run
```

Anthropic example:

```bash
ANTHROPIC_API_KEY=... python scripts/story_discovery_live_eval.py \
  --provider anthropic \
  --anthropic-model claude-sonnet-4-6 \
  --case h02_between_floors \
  --case h05_what_she_saves \
  --output artifacts/phase-h/anthropic-01
```

OpenAI example:

```bash
OPENAI_API_KEY=... python scripts/story_discovery_live_eval.py \
  --provider openai \
  --openai-model gpt-4o \
  --case h02_between_floors \
  --case h05_what_she_saves \
  --output artifacts/phase-h/openai-01
```

Both providers can be selected with `--provider both`, but H2 should still use explicit model flags so model identity is frozen rather than inferred from a mutable future default.

`--all-cases` is intentionally explicit. The harness never treats an omitted case selection as permission to spend tokens across the full corpus.

## Output layout

```text
<run>/
  run_manifest.json          # written before provider execution; never rewritten
  run_summary.json           # written after the matrix finishes
  anthropic/
    h02_between_floors/
      case_manifest.json
      stdout.txt
      stderr.txt
      review_stdout.txt
      review_stderr.txt
      result.json
      project/
        story_discovery/
          brief.yaml
          candidate_*.yaml
          discovery_set.yaml
          discovery_report.yaml
          comparison.md
          ...
```

The project root lives *inside* the run evidence directory so all generated artifacts remain self-contained. The harness does not copy a selected candidate to `story_identity.yaml` and never invokes `story-discovery accept`.

## Provenance rules

`run_manifest.json` records:

- schema/phase;
- UTC start time;
- repository revision when `git rev-parse HEAD` is available;
- Python version and platform;
- corpus path and SHA-256;
- selected providers and explicit model or a provider-default-at-recorded-revision marker;
- selected case IDs;
- explicit `canonical_acceptance_allowed: false`;
- explicit `automatic_quality_scoring: false`.

Each `case_manifest.json` records the exact safe CLI arguments, provider/model, case purpose/focus, and SHA-256 of the persisted declared brief.

The harness never stores API keys or a copy of the process environment. Captured output is redacted against the key values supplied through the required provider environment variables before being written.

## Failure handling

Harness exit codes:

- `0` — every requested live discovery and deterministic review returned success and no canonical Identity appeared;
- `1` — local configuration/preflight failure before live execution;
- `2` — at least one provider/review run returned non-zero; raw evidence is still retained;
- `3` — canonical-authority invariant violation (`story_identity.yaml` appeared).

Unexpected exceptions from a live CLI invocation are captured as evidence with exit code `70`; the remaining matrix continues so one provider/case failure does not erase evidence from other requested cells.

Provider/transport failure is not automatically a semantic failure. H3 must classify the run evidence before drawing conclusions.

## Adjudication dimensions reserved for H3

The live evidence will later be reviewed for:

- intent adequacy / whether the brief supplied a defensible optimization target;
- causal distinctness of candidate engines;
- causal-profile accuracy relative to the actual candidate commitments;
- recommendation defensibility against declared intent and alternatives;
- craft-layer propagation: causal ownership → verbs/actions → scene families → pressure/texture → reader experience → theme;
- alternative fairness;
- authority feel;
- experienced-writer insight/persuasiveness.

Use the Phase E reaction/failure vocabulary where it still applies. Do not replace qualitative adjudication with a weighted aggregate score.

## H1 qualification boundary

H1 is complete when the corpus and capture harness pass offline tests plus the repository's full CI/validator/Ruff/wheel matrix on an exact PR head.

That proves only that Auteur can **reproducibly capture** live-provider Story Discovery evidence without crossing canonical authority. It does not prove that any provider's creative output is good.
