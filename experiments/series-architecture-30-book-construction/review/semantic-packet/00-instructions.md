# Semantic consistency review (fresh context)

You are an independent reviewer. Test whether elements of a working narrative architecture remain meaningful and consistent under revised premises. Check meaning and consequences, not only identifiers or string equality.

## Scope limits
- Read only the files in this packet folder. Do not read the repository, other folders, or the web.
- 01-working-candidate.json is the working architecture on the original path.
- 02-h1-candidate.json is the same architecture after a hypothetical revision, H1, described in 03-h1-revision-instruction.txt. H1 is hypothetical and not accepted.
- 04-preserved-ids.json lists the element identifiers an automated review marked as preserved. That marking compares identifiers only and does not check meaning. Do not assume it is right or wrong.

## Tasks
1. **Preserved elements.** For every ID in 04-preserved-ids.json (all categories), decide whether the element, as written in 02-h1-candidate.json, remains semantically valid under H1. Consider its summary, eliciting condition, context, trope functions, payoff expectations, narrative engine, and any phase text that depends on it. Give one verdict per element: **consistent**; **conditional** (valid only if a stated condition holds); **stale** (contradicted by H1 or by the text it depends on); or **unsupported** (no text supports it). Quote the text you rely on.
2. **Changed elements.** Inspect the elements that differ between 01 and 02. For each, say whether the change is consistent with H1. Do not assume a changed element is correct because it changed.
3. **Missed propagation.** Find any element that H1 materially affects but that neither the instruction nor the preserved list names. Also find any element the instruction names that appears in neither file. Quote the text.
4. **Internal consistency.** Check that H1's facts (who opens the records, who holds custody and when, when the remnant forms, what the Gate Table does) are stated the same way everywhere they appear in 02. List every place they appear, and flag any disagreement.
5. **Your own check.** Is there any element a careful reader would expect to change under H1 that the text does not change? Quote it.

## Rules
- Do not give a preferred verdict on H1 or on the story.
- Quote the text for every claim.
- Keep assessment separate from repair. Put suggestions in a final section titled "Optional repair notes", labelled as suggestions.
- Do not rewrite the record.

## Report format
Start with "# Semantic consistency report (verbatim)". Give a table for task 1: id | category | verdict | quoted text | reason. Then sections for tasks 2–5. Keep the report under 2500 words.
