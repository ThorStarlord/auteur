VERDICT: APPROVE

No blocking defects found. Checks (a) to (d) pass. Three non-blocking observations follow.

Checks
(a) Legacy standing preserved. `_standing_key` (studio_architecture_synthesis.py:558-562) returns `settings.get("configuration_sha256") or settings["developments_sha256"]`. Requests prepared before this change never carry `configuration_sha256`, so both the writer (line 459) and the reader (`_standing`, line 575) still resolve them to `latest_by_developments/<developments_sha256>.json`. The pointer filename scheme is unchanged. `_developments_pointer` has only these two callers.
(b) No-culmination requests unchanged. The key is added only under `if culmination_text:` (line 446), so for a request with no culmination the settings dict is the same, and so are its candidate_id and request_sha256.
(c) Instructions match the validators.
- Consequence v3 (studio_architecture_consequence.py:1147-1150) states 0 to MAX_MECHANISM_COUNTEREVIDENCE objects, text up to COUNTER_LIMIT, and 1 to 3 evidence ids. This matches `MechanismCounterevidence` (ItemText max COUNTER_LIMIT, evidence min 1 / max 3) and the `max_length` on `MechanismReading.counterevidence`. The "other than this mechanism itself" rule matches line 1296: `all(row["id"] == reading.evidence ...)` refuses the object. "Recorded" matches `resolve()`, which refuses unknown ids.
- Architecture `_SYSTEM` (studio_architecture.py:995-997) matches `valid_graph` lines 281-286, which accepts an affects id only if it is in `{node.id for node in self.nodes}`. Phase, link and question ids are refused.
(d) The new tests would fail on the old code.
- Synthesis test 1: before the change, the culmination prepare overwrites the same developments pointer, so the plain request reads "superseded", and the `== "current"` assertion fails.
- Synthesis test 2: the same mechanism makes the first culmination "superseded".
- Both instruction tests assert sentences that did not exist before, so they fail.

Findings (non-blocking)

1. src/auteur/beginner/studio_architecture_synthesis.py:446-451. Identity drift for culmination requests prepared before the change.
Defect: `configuration_sha256` goes into `settings`, which feeds candidate_id and request_sha256. So re-preparing an identical culmination request now gives a new request instead of reusing the existing folder.
Scenario: an author re-prepares the same developments and culmination after upgrading. The old-format request stays keyed by developments and the new one by configuration, so both show "current" for what is really one configuration. A later plain request then supersedes only the old-format one. The comment "requests without one keep their identities" is accurate, but culmination requests do not keep theirs. This is acceptable if intended; consider saying so in the docstring or evidence record.

2. studio_architecture_synthesis.py:415-424 together with 559-562. A follow-up that adds, removes or changes the culmination does not supersede the synthesis it follows.
Scenario: the author completes a plain synthesis, then prepares a follow-up (`prior_request_sha256` set) that adds a culmination. Both are now reported "current". This may be the intended "parallel configuration" meaning, but it is not tested, and the `_standing` docstring (line ~566) still says "latest synthesis of these developments". Suggest updating that docstring to say "configuration".

3. studio_architecture_synthesis.py:448. Minor redundancy. `culmination_sha256` is already in settings, so `_standing_key` could derive the key without storing a new field (e.g. digest developments plus culmination when culmination_sha256 is not None). That would avoid finding 1's identity change. Not required.

Tests do not cover the legacy path directly, i.e. a stored request without `configuration_sha256` but with a culmination. The code path is trivially correct by inspection, so this is optional.
