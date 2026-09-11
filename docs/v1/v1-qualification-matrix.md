# Auteur V1 Qualification Matrix

A V1 claim is release evidence only when it is tied to the exact frozen candidate required by `docs/engineering/release-qualification.md`.

## Qualification lanes

| Lane | Required for 1.0 | Evidence |
| --- | --- | --- |
| repository validation | yes | repository validators/check script succeed |
| deterministic test suite | yes | full accounting: collected/passed/skipped/xfailed/xpassed/failed/errors |
| Linux Python 3.11 | yes | exact-head CI |
| Linux Python 3.12 | yes | exact-head CI |
| Linux Python 3.13 | yes | exact-head CI |
| Windows Python 3.13 | yes | exact-head CI |
| wheel build + fresh install | yes | artifact hash + installed-wheel public smoke |
| authority death tests | yes | pre-accept bytes/hashes unchanged; failed writes leave authority intact |
| restart/resume | yes | project reload preserves canonical revisions, dependencies, and pending attention |
| corruption handling | yes | authoritative corruption blocks; rebuildable derived corruption is recoverable where supported |
| browser control-plane safety | yes when Workspace mutation ships | loopback, Host/Origin, CSRF/session, POST-only mutation, confinement, confirmation tests |
| Anthropic live adapter smoke | yes for final release claim, subject to credentials/publication authorization | bounded request + recorded provider/model/outcome; no literary-quality claim |
| OpenAI live adapter smoke | yes for final release claim, subject to credentials/publication authorization | bounded request + recorded provider/model/outcome; no literary-quality claim |
| Golden Author Journey | yes | fresh install traverses documented V1 path and HTML/EPUB output |
| beginner owner dogfood | yes as bounded usability evidence | no implementation docs/raw YAML required for the core browser decision loop |
| macOS | no unless product contract is expanded | optional evidence only |
| 50/100+ Book scale | no | explicitly outside V1 claim ceiling |

## Provider failure contract

Production adapters must normalize or otherwise expose stable categories for:

- missing credentials;
- invalid credentials;
- rate limiting;
- timeout;
- connection failure;
- provider 5xx/service failure;
- malformed provider response;
- structured-output/schema failure in the consuming workflow;
- retry exhaustion;
- user interruption.

For each category, tests/evidence must identify whether retry is allowed, what is persisted, whether canonical state can change, and the safe next action.

## Golden Author Journey minimum evidence

The qualification project should exercise a Book-scale topology (target 15–30 Chapters and 50–100 Scenes; synthetic/bounded prose is allowed) with multiple characters/relationships/setup-payoffs, one accepted structural revision, one stale downstream artifact, one complete process restart, and HTML/EPUB output.

The automated path must record or assert:

```text
premise
→ multiple Story Discovery candidates
→ explicit StoryIdentity acceptance
→ Structure
→ Tutor decision
→ proposal selection
→ revision plan/validation/preview
→ explicit Structure application
→ correct downstream freshness
→ Realization and Expression acceptance
→ restart/reload
→ accepted Book publication
```

At every authority boundary capture before/after hashes. Before explicit acceptance/application, authoritative bytes must remain unchanged.

## Release gate

A required matrix row may end only in `PASS` or in an explicit pre-freeze change to `v1-product-contract.md` that removes/narrows the associated claim. `UNKNOWN`, `PARTIAL`, and unaccounted skips/xfails do not satisfy release readiness.
