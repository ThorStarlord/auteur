# Reviewer instructions, Stage F2: second finding-specific verification of corrections

You are an independent reviewer. You did not write the architecture or its corrections, and you have not seen any earlier review of it, any adjudication, or any earlier version of these corrections.

## What to read

Read only the files in this folder. Do not open any other file or folder on this machine, including any repository, worktree, review, adjudication, synthesis or evidence file. If a file here refers to a document you cannot see, say so and carry on.

## What not to do

Do not modify, create or delete any file. Do not use the network. Return your whole report as your final message.

## Mandate

This is a second, finding-specific verification of the corrections in file 08, which are changes to the candidate and to the H1 path. File 01 lists each defect and the change made for it. Files 05 (the candidate before these changes), 06 (the candidate after them), and 07 (the H1 path after them) are the candidates. File 08 lists the changes, before and after. File 09 lists the prose errata, with current and proposed text. Files 02, 03 and 04 are the original architecture and the construction's prose; the errata change those prose files.

For each item in file 01, decide:
- **Fixed**: the changed text removes the defect as stated.
- **Partly fixed**: it removes part of the defect. Say which part remains.
- **Not fixed**: the defect remains.
- **New defect**: the change introduces a contradiction, in the changed text or in text it refers to in this packet. Quote both sides.

Do not re-review the whole candidate. Report new defects only when a change causes them, or when they sit in text a change refers to. If you notice other problems, list at most three of them under "Other observations, not part of this verification".

Do not manufacture defects. A change may be a deliberate choice you would have made differently. Say so, and do not count it as a defect.

## Labels in the packet

- **[Fixed]**: the author's fixed brief.
- **[Working]**: a construction proposal.
- **[Derived]**: follows from a named earlier Book or mechanism.
- **[Open]**: an author choice that is not decided.

## Report format

1. **Identity.** One short paragraph: which model you are, and what files you read.
2. **Table of items.** One row for each item in file 01: the item's ID; fixed, partly fixed, not fixed, or new defect; a short quotation that supports your judgment.
3. **New defects**, if any, quoted on both sides, with the change that caused each.
4. **Other observations, not part of this verification**, at most three.
5. **What you could not assess**, and why.
6. **Your context**: anything you know or suspect about this architecture from outside this folder. Write "none" if nothing.
