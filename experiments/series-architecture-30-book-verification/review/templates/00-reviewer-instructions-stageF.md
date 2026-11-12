# Reviewer instructions, Stage F: finding-specific verification of corrections

You are an independent reviewer. You did not write the architecture or its corrections, and you have not seen any earlier review of it or any adjudication of one.

## What to read

Read only the files in this folder. Do not open any other file or folder on this machine, including any repository, worktree, review, adjudication, synthesis or evidence file. If a file here refers to a document you cannot see, say so and carry on.

## What not to do

Do not modify, create or delete any file. Do not use the network. Return your whole report as your final message.

## Mandate

This is a finding-specific verification, not a review of the whole architecture. File 01 lists the defects that earlier reviewers stated, and the corrections that were made for each one. Files 05 to 07 are the candidates: the working candidate W2 before correction, the corrected candidate W3, and the corrected H1 path H1v2. File 08 lists the candidate corrections, before and after. File 09 lists the prose corrections (errata), with the current and proposed text.

For each finding in file 01, decide:
- **Fixed**: the corrected text removes the defect as stated.
- **Partly fixed**: it removes part of the defect. Say which part remains.
- **Not fixed**: the defect remains, in the corrected text or in the text it depends on.
- **New defect**: the correction introduces a contradiction, either in the changed text or in text the change refers to in this packet. Quote both sides.

Check each proposed erratum (file 09) against its current text in files 03 and 04, which are the prose it changes. Check that the proposed text says what the finding needs and nothing more.

Do not re-review the whole candidate. Report new defects only if a correction causes them, or if they sit in text a correction refers to. If you notice other problems, list at most five of them, separately, under "Other observations, not part of this verification".

Do not manufacture defects. A correction may be a deliberate choice that you would have made differently. Say so, and do not count it as a defect. The author decides, not you.

## Labels in the packet

- **[Fixed]**: the author's fixed brief.
- **[Working]**: a construction proposal.
- **[Derived]**: follows from a named earlier Book or mechanism.
- **[Open]**: an author choice that is not decided.

## Report format

1. **Identity.** One short paragraph: which model you are, and what files you read.
2. **Table of findings.** One row for each finding in file 01: the finding's ID; fixed, partly fixed, not fixed, or new defect; and a short quotation that supports your judgment.
3. **New defects**, if any, quoted on both sides, with the correction that caused each.
4. **Other observations, not part of this verification**, at most five.
5. **What you could not assess**, and why.
6. **Your context**: anything you know or suspect about this architecture from outside this folder. Write "none" if nothing.
