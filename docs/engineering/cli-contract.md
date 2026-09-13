# Auteur 1.0 CLI contract

The `auteur` console script is the supported command-line interface. The
following root command groups are included in the 1.0 promise:

| Command group | Contract | Mutation posture |
|---|---|---|
| `status` | human summary and documented `--json` output | read-only |
| `init` | create a project from an explicit blueprint | author-invoked mutation |
| `identity` | validate and compile story identity | validation or explicit derived output |
| `structure` | deterministic whole-story diagnosis and proposals | diagnostics/proposals; canonical mutation requires explicit action |
| `workflow` | inspect state and recommend the next bounded action | read-only/recommendation |
| `campaign` | persist, validate, inspect, hand off, resume-plan, and bundle local Campaign state | local persistence; canonical acceptance remains owner-specific |
| `decision` | inspect, compare, and prepare author decisions | read-only/preparation |
| `review` | inspect and explicitly accept through an owning artifact seam | author-authorized mutation |
| `publish` | render accepted book output | explicit publication action |

Commands outside these groups are experimental, legacy, or domain-specific and
are not covered by the 1.0 CLI compatibility promise unless their own contract
is declared and qualified.

For stable commands:

- invalid user input returns a non-zero exit code and writes the diagnostic to
  stderr;
- successful `--json` commands write one parseable JSON value to stdout;
- canonical mutation requires the command's explicit confirmation mechanism;
- stale, malformed, unavailable, or ambiguous state blocks promotion;
- `campaign resume` is plan-only and never replays canonical mutation;
- `campaign bundle inspect` stages verified files outside canonical project paths;
- error message wording is diagnostic, not a stable parsing contract; callers
  must use exit codes and documented JSON fields.

The parser-level command presence is guarded by
`tests/test_cli_contract.py`. Behavior and serialized output remain governed by
the command-specific integration and qualification suites.

The stable Campaign command forms are:

```text
auteur campaign init --project PATH --campaign-id ID --project-id ID
auteur campaign validate --project PATH [--json]
auteur campaign inspect --project PATH [--json]
auteur campaign handoff --project PATH --operation OPERATION
auteur campaign resume HANDOFF_ID --project PATH [--json]
auteur campaign bundle export --project PATH --output PATH
auteur campaign bundle inspect BUNDLE --staging PATH [--json]
```
