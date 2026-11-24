# Atelier: a working Book discovery, considered for the Architecture

Status: implemented on `feat/atelier-book-discovery` (builds on #631–#636). Opt-in Atelier only.

## The author's question

"Developing Book 24 surfaced a question that might matter for the whole Series. What does the Book actually
record? Is it worth asking about at the Architecture level? And if so, how do I take it there without losing
my place, and still be free to keep it in the Book?"

On `main` the author could read a Book element in the Series and Book context (#633), develop it (#634), and
ask the coding agent about an Architecture concept (#632). Nothing let an inquiry know which Book element
prompted it. The author could only paste the Book's words into the question, where they would read as the
author's own statement.

## What counts as a discovery, and what does not

**Recorded evidence.** A discovery is one working Book element the author chooses, read through the Book
owner (`book_element_evidence`):
- the element's own words;
- its attribution and epistemic status;
- its standing (`working_noncanonical`, and for example `undecided`);
- the Book's number, working revision and content identity;
- each Architecture concept the element records a typed reference to, with its status against the current
  Architecture (unchanged, changed, removed or unrecorded).

**Agent interpretation.** The inquiry answer: analysis, observations checked against the Architecture,
alternatives and uncertainties. It is noncanonical and stays so.

**Author decision.** Whether to ask, which alternative to develop (if any), and whether to apply the resulting
revision. Keeping the element in the Book is a complete outcome.

**What a discovery is not:**
- an Architecture fact;
- an author intention;
- an accepted commitment;
- a verified relationship;
- a new concept;
- a revision instruction.

A concept the element only names in its wording is not a recorded reference.

The study material is real. In the #635 run, the coding agent's reconciliation of Book 24 recorded
`unk-tally-hours`, an agent-proposed open question citing the Ledger engine: "Whether the stewardship tally
the Council keeps is the ledger's hours column or a separate count that feeds it."
(`scripts/seed_book_discovery_study.py` rebuilds that state through the owners.)

## Decisions

1. **Book evidence is a field of the inquiry request, owned by the inquiry owner.**
   `prepare_architecture_inquiry` accepts an optional `book_evidence` reference: the Book, the element, and
   the Book request and element content identity the author read. Under the canvas lock it:
   - re-reads the element through the Book owner;
   - refuses it if the Book or the element changed;
   - refuses any anchor that is not a current Architecture node the element records.

   The packet gets its own `book_evidence` section with an authority label. The author's question stays the
   author's words. The request settings record the evidence identity.
2. **Freshness follows the evidence.**
   - **Waiting request:** goes stale when the Book evidence changes, and an answer is refused and kept as
     `stale_response.json`.
   - **Completed answer:** keeps its Architecture validity, and reports its Book evidence as `current`,
     `changed` or `unreadable`. The panel labels changed evidence historical.
3. **The existing selected-alternative contract carries the evidence forward.** When the author develops an
   inquiry alternative into a revision, the revision request's `selected_creative_alternative` carries the
   Book evidence and `status_at_revision`. The revision's request and review keep it, and the Architecture's
   adoption lineage (`project_architecture_resume`) reads it back from the request, so an applied revision
   still says which Book element it came from. The revision is the Architecture owner's: reviewed, then
   applied explicitly by the author.
4. **The Atelier coordinates; it decides nothing.** "Consider for the Architecture" on a Book element opens a
   card inside that Book's record:
   - what the Book records, with its standing and identity;
   - the concepts it records, with their status;
   - "Established" and "Not established" statements;
   - two choices, "Keep it in Book 24" or "Ask your coding agent", where the author picks the operation and
     writes the question.

   Asking hands the element to the existing coding-agent panel. The panel shows the evidence apart from the
   question and sends it as its own field. The way back from the panel returns to the card.
5. **Advisory, not proactive pressure.** A collapsed list, "Questions and consequences Book 24 records about
   the Architecture", shows the Book's own unresolved questions, consequences, alternatives, later
   possibilities and assumptions that cite a current concept. Nothing is generated, and nothing interrupts the
   Book task.
6. **The cross-Book loop is #635's.** After the Architecture revision is applied, the Books citing the changed
   concept, including the Book that supplied the discovery, are reported out of date by the impact view. The
   Book is never modified or reconciled automatically.

## Alternatives not taken

- **Putting the Book's words in the author's question.** It would turn a working Book proposal into an
  author-declared statement.
- **Anchoring on Book element ids.** Graph intents anchor only on Architecture records.
- **A new opportunity store or decision taxonomy.** Keeping, asking, developing and applying are already
  expressed by existing records: an inquiry request and result, a revision request and review, and the
  applied Architecture.
- **An Architecture open-question anchor.** Open questions are not anchorable records. The removed Gate Table
  case shows why textual mentions cannot stand in for typed references.

## Removed concepts and textual mentions

- **Removed concept:** an element may record a reference to a concept the Architecture removed (Book 25 still
  cites the Gate Table). The card and the packet report it as removed, and as historical evidence, and the
  owner refuses it as an anchor with that reason.
- **Unsupported element:** an element whose only recorded concept is gone has nothing to anchor on, and the
  owner says so. The UI then offers only "Keep it in the Book".
- **Textual mentions:** the Architecture's open questions that still name the Gate Table in text are not
  typed relations. They are not used.

## Limits

- **No real author:** the walkthroughs were run by agents. This is not human usability evidence.
- **Agent alternatives are not judged:** the agent's alternatives are interpretations. The study does not
  judge their literary quality.
- **The author chooses:** advisory surfacing lists what the Book records. It does not rank or recommend.
- **Inherited Studio writes:** "Check agent result" saves the Studio's viewport (an existing fit-to-view),
  and the Studio saves the canvas before an Architecture apply. Neither changes any narrative record.
