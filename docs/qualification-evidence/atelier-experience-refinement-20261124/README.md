# Atelier experience refinement — evidence

**What was tested:** branch `feat/atelier-experience-refinement`, built on `main@2db01cc5`.

**How it was captured:** with the same capture script on both, which walks journeys A–G on fresh copies of
three seeded projects:
- **small:** `seed_atelier_study` `atelier-small`;
- **dense:** `atelier-dense`;
- **discovery:** `seed_book_discovery_study`.

**Widths:** 1440 × 900 and 390 × 844.

**Agent answers:** the inquiry answer and the Architecture revision are the recorded answers of the real
coding agents from the #637 run, replayed through the owners' command lines.

**Limit:** agent-operated only. This is not human usability evidence.

- **`journeys-before.json`:** `main@2db01cc5`, the step log per journey: focus target, scrollY, page height,
  writes, page errors, load and constellation timings.
- **`journeys-after.json`:** the branch, with the same journeys and fields.

**Headline facts:**
- **After Apply:** focus moves from the page body at scrollY 1,877 (desktop) or 9,634 (phone) to the
  discovery the author came from, at scrollY 168 or 3,344.
- **Page height:** at the inquiry answer, 5,739 → 4,935 px on desktop.
- **Errors:** 0 page errors in every journey, before and after.
- **Writes:** the same requests in the same order: the inquiry prepare, the revision prepare, Apply, and the
  Studio's existing canvas saves.

The screenshots are kept with the PR's visual report rather than in the repository.
