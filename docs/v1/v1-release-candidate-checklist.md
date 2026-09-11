# Auteur V1.0 Exact Release-Candidate Checklist

This checklist is the operational bridge from implemented V1 closure code to a defensible `1.0.0` release. It does not authorize publication and must not be pre-filled with synthetic PASS claims.

## Candidate identity

```yaml
candidate_sha: null
version: null
wheel_sha256: null
sdist_sha256: null
candidate_frozen_at: null
```

A source/test/version/package-resource/build change after freeze invalidates downstream evidence and requires a new candidate.

## Source qualification

- [ ] working tree/release branch is clean and exact candidate SHA recorded;
- [ ] repository verification succeeds;
- [ ] full deterministic suite accounting reconciles collected/passed/skipped/xfailed/xpassed/failed/errors;
- [ ] Linux Python 3.11 exact candidate PASS;
- [ ] Linux Python 3.12 exact candidate PASS;
- [ ] Linux Python 3.13 exact candidate PASS;
- [ ] Windows Python 3.13 exact candidate PASS;
- [ ] dedicated V1 closure evidence artifact records the same candidate SHA and PASS;
- [ ] no unexpected XPASS or unaccounted release-blocking skip/xfail.

## Artifact qualification

- [ ] wheel and sdist are built from the frozen candidate;
- [ ] hashes are recorded;
- [ ] fresh environment installs the wheel from the artifact, not the source checkout;
- [ ] public CLI/help/ontology smoke passes from site-packages;
- [ ] core V1 author journey passes against the installed artifact or an explicitly equivalent artifact-qualified runner;
- [ ] HTML and EPUB generation succeed from accepted, fresh Book sources;
- [ ] stale/transitively stale accepted Book state is rejected at publication.

## Provider qualification

These are operational adapter smokes, not literary-quality tests.

- [ ] Anthropic optional dependency installed in fresh environment;
- [ ] authorized Anthropic credential supplied without entering evidence artifacts;
- [ ] `scripts/qualify_v1_provider.py --provider anthropic ...` records PASS for the frozen candidate;
- [ ] OpenAI optional dependency installed in fresh environment;
- [ ] authorized OpenAI credential supplied without entering evidence artifacts;
- [ ] `scripts/qualify_v1_provider.py --provider openai ...` records PASS for the frozen candidate;
- [ ] provider evidence candidate SHA equals frozen candidate SHA.

## Beginner product evidence

- [ ] perform `workspace-v2-owner-dogfood.md` on the frozen candidate;
- [ ] owner record says PASS or an explicitly accepted PASS_WITH_FRICTION that does not contradict the V1 Product Contract;
- [ ] core browser loop completed without implementation docs/raw YAML;
- [ ] authority boundary and blocked-state explanations were understandable;
- [ ] restart/resume orientation succeeded.

## Final release invariant

Before tagging/publishing, mechanically verify:

```text
source-qualified commit
= artifact-built-from commit
= installed-qualified commit
= final release HEAD
= tag peeled commit
```

- [ ] version metadata finalized to `1.0.0` only after all pre-version candidate requirements are known;
- [ ] final version-bearing commit is requalified where the version/build change invalidates prior evidence;
- [ ] release notes finalized against the exact candidate;
- [ ] tag target verified;
- [ ] GitHub Release publication authorization present;
- [ ] package-registry publication status separately recorded/authorized if applicable.

## Stop conditions

Do **not** publish/tag `1.0.0` when any required row is `UNKNOWN`, `PARTIAL`, `NOT_RUN`, or failed. Either close the concrete release gate or explicitly narrow the V1 Product Contract and produce a new frozen candidate.
