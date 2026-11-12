# Fresh-context answers (subagent a42023708e0d06c51, verbatim final message)

Inputs read: `demo/qual/contract.md` and `demo/out/book24-resume.json` only (two Read calls, no other tools).

Both files were read. Book 24 is a working, noncanonical proposal (`artifact.authority` and `packet.authority` are both `working_noncanonical`), and nothing in it is accepted canon. The `story_vision_excerpt` in the packet is cut off mid-word, so I cannot quote the full brief.

**1. What Book 24 is about**

The title is "The Uncounted Crew." Its question is: "Can a generation that refuses to be counted learn to give back the water before the water is owed, and what does the valley record when it does?" (`fn-question`, `packet.identity.question`)

The Long Return's labour gap is first met by people rather than by a schedule. The Book exercises the Old Hand, the Ledger and the Source, and exports one new record: a public capability record, separate from debt, tally and aggregate balance (`fn-question`).

The people named in the text are:
- the Brightwater cohort (`fn-question` pressure, `inh-cohort-belief`);
- Hesper, who led Brightwater and took a Council apprenticeship (`inh-hesper`, `agent-hesper`);
- Idrun, the Council steward, whom the agent texts describe as Hesper's grandmother (`agent-steward`, `agent-hesper`);
- Ysa Trant of the maintenance lineages (`agent-lineages`).

Their name fields are null, and their sourcing is an open product question (`unk-character-sourcing`).

The creative intentions are listed by title only: "Experience brief," "Victories change the world," "No escalation; local closure," and "Independent agency across generations" (`packet.author_fixed_context.creative_intentions`). Their text is not in the file. The reader-experience targets are `rx_belonging`, `rx_consequence` and `rx_wonder`.

The file does not contain scene structure, length, point of view, or tone beyond those ids.

**2. Inherited pressures that generate the conflict**

The file has no field that names Book 24's conflict. I read it from the pressure field (`fn-question.pressure`) and these inherited items:
- **Date:** the Long Return's date is public. The Balance Stones publish it and limit Brightwater's draw. Training takes years, so the labour question cannot wait for Books 27 to 29 (`inh-date`). The date itself is not given.
- **Lineage Right:** the Special Draw Right is conditional on training apprentices from outside the lineage, and its review point falls in Book 24 (`inh-right-condition`, `assume-p1`).
- **Cohort belief:** a generation that came of age after Book 20 has never seen the labour (`inh-cohort-belief`). `assume-p2` reads "nothing counted" as "nothing owed."
- **Conversion:** hand-light houses have drawn less since the Book 20 conversion (`inh-uneven-draw`). The agent-proposed mechanism is that the conversion credits counted hands only (`eng-ledger-source`).
- **Gift reading:** "water given; hands given back; nothing counted" belongs to the Old Hand. The Balance Stones, cut in Book 23 and published by the Reading Hall, do not depend on the Gate (`inh-gift-reading`).
- **Lowfen channel:** it broke in Book 19 and was rebuilt by lineage crews in Book 20 (`str_lowfen_channel`, `th_maintenance`).

`inh-gate-independence` says Book 24 holds whether or not the Hollow Gate and Gate Table are kept. That item is unresolved and carries no source provenance.

"Conflict A" (`alt-stones-restraint`) and "the Book 21 conflict" (`str_hollow_gate`) are referenced but not defined in these files, so I cannot say how they feed Book 24.

**3. Choices and costs**

The setting (`choice-craft-mark`, agent-proposed): after the thaw the Balance Stones show the crew's return, and a silted section has cost one hand-light household a season on its terrace. The Council, through Idrun, offers to enter the crew in the stewardship tally retroactively. That would meet the Right's condition and, through the conversion, restore hand-light draw.

The options are:
- `opt-accept-count`: family draw is restored, but the cohort enters the tally it refused.
- `opt-refuse`: the gift stays pure, the families stay cut, and the condition stays unmet.
- `opt-craft-mark` (chosen): teacher and learner each cut a mark on the channel stone where a named repair was done. It records capability and place, not hours or debt, and it does not touch draw.

The visible costs are:
- `cost-draw-stays-cut`: the craft-mark does not restore draw, and the crew knows its hand-light households stay cut this cycle.
- `cost-counted-crewmates`: several crewmates, including the one whose terrace silted, choose to be counted for their families. Hesper respects that, and the cohort splits.

Engine-level costs:
- `eng-old-hand-ledger` (unresolved): the Right's training condition cannot be shown in the form the Council expected.
- `eng-ledger-source` (agent-proposed): hand-light youth's uncounted labour improves the balance but cannot restore their own households' draw, while the best-handed houses keep their counted advantage (`agent-best-handed`).
- `eng-source-witness` (agent-proposed): a badly laid section silts and must be relaid by lineage hands.

Personal costs (`trans-hesper-idrun`, agent-proposed): Hesper moves from "abundance needs no work" to "the work is real and the water sees it, but people need not count it." Idrun moves from keeping a tally that should be complete to accepting a record she does not hold.

The file does not say whether the Sallow house is hand-light (`unk-sallow-house`), which the file says changes Hesper's personal cost. It also does not say what her apprenticeship involves (`unk-apprenticeship-return`).

**4. What the local resolution changes**

- A capability record now exists alongside the debt reading's ledger (remnant), the stewardship tally (care) and the Balance Stones (aggregate balance) (`eng-record-form` changed_state, `cons-capability-record`).
- Ysa Trant accepts craft-marks as proof of training, and the Council accepts them as meeting the Right's condition for one review cycle only (`res-craft-mark-provisional`, closure false). The Right's revocability and final condition remain unsettled.
- A first group of outside-lineage hands is trained. Its size is unstated, and it narrows the gap without closing it (`res-first-group`).
- The Lowfen upkeep holds through the thaw, and the silted section is relaid (`res-lowfen-upkeep`, unresolved).
- The remnant's custody offer is declined. Oona's offer stands, neither accepted nor refused (`res-custody-declined`).
- The cohort's belief is now two practices (`cons-belief-plural`). The Idrun–Hesper relationship is now a disagreement rather than an inheritance (`cons-relationship`).
- Labour readiness has begun, and a visible shortfall remains (`cons-labour-readiness`).
- Closed threads: `closed-ignored-right` (provisionally met), `closed-remnant-keeper`, `closed-invisible-gift` (narrowed), `closed-idle-generation`, and `closed-book30-surprise` (named and partly worked).

Not changed: draw (`cons-capability-record`, `cost-draw-stays-cut`), the three finale alternatives (`cons-finale-open`), the Gate questions (`dec-gate-table`), and the Stones' attribution of local return (`cons-reading-hall`, `assume-p3`). The closure flags are local to each thread. None of them closes the labour gap itself.

**5. What it exports to the Whole-Series Architecture**

`packet.series_changed` is false, so these are consequences handed to the Series, not edits the file applies. The file does not say which Series nodes would be edited.

Series consequences (`packet.exports.series_consequences`, which the artifact copies with provenance tags):
- `cons-capability-record` (changes): the Ledger engine gains a capability record. It bears on `th_hands_and_draw` by showing who can give return labour, without changing who is counted for draw.
- `cons-conversion-blind-spot` (changes): the Book 20 conversion credits counted hands only.
- `cons-reading-hall` (complicates): it bears on `alt_c_ratified_trigger` and `alt_b_allotted` and decides neither.
- `cons-belief-plural` (changes): plurality of practice now crosses generations.
- `cons-labour-readiness` (changes), `cons-relationship` (changes, no refs).
- `cons-finale-open` (preserves): `alt_a_reciprocal`, `alt_b_allotted` and `alt_c_ratified_trigger` all remain unselected, and each must reckon with the capability record.

Later possibilities (enabled): `later-channel-skill`, `later-finale-capability` (usable by pair-hands under A, rota assignment under B and the pre-drawn panel under C; it lowers some costs and chooses none), `later-books-25-26`, `later-cohort-seat` and `later-oona-offer`. The five `closed-*` entries are also exported.

Typed edges: `edge-capability-hands`, `edge-capability-lineage`, `edge-function-long-return`, `edge-conversion-draw`, `edge-crew-setup`, `edge-reading-hall-threshold`, `edge-finale-open` and `edge-remnant-register`. `edge-finale-open` points only at `alt_a_reciprocal`, although `cons-finale-open` references all three alternatives.

**6. Assumptions and creative decisions still open**

Assumptions (`artifact.assumptions`):
- `assume-p1` (agent-proposed): the Right has a review point in Book 24. Reversal: the pressure comes from the lineage's own count of the shortfall.
- `assume-p2` (agent-proposed): the cohort reads "nothing counted" as "nothing owed." Reversal: the belief comes from invisible lineage labour alone, and the function survives.
- `assume-p3` (P3, unresolved): return labour shows on the Stones in aggregate. Whether the Stones can resolve local return is not established. No reversal.
- `assume-p4` (P4, unresolved): unskilled gift-hands can damage a channel. No reversal.
- `assume-p5`: the craft-mark is a capability record held by no institution. No reversal.
- `assume-p6`: the Council accepts craft-marks for one cycle. This does not decide "author-reserved choice 7."
- `assume-p7`: the Reading Hall refuses attribution.
- `assume-p8`: the remnant's custody offer and Oona's offer stand as described.
- `assume-p9`: Hesper remains a Council apprentice after the Book. The author may have her leave, but that is an alternative, not a stated reversal.
- `assume-p10`: the Lowfen upkeep is the crew's work site. The surge route remains author-reserved, and Book 24 neither designates nor excludes the Lowfen.

The artifact tags `assume-p3` through `assume-p10` as unresolved, even where their text says "Agent-proposed in the source." I treat them as unverified either way.

Open author decisions (`artifact.open_author_decisions`, with Series question index):
- `dec-finale-mechanism` (2): which finale mechanism, A, B, C or a third.
- `dec-right-revocable` (4): whether the Right is revocable, its training condition, and who carries the Turn when the lineages end.
- `dec-conversion-settlement` (5): whether the conversion is a lasting settlement or a stage to revisit.
- `dec-compact-settlement` (6): whether the Compact accepts grain-labour, and whether the Gate Table's schedule reaches lowland draw.
- `dec-surge-route` (7): which channel takes the surge, and whether any household floods.
- `dec-hesper-motive` (9): whether her motive is independent of the author's preference.
- `dec-reform-stance` (12), `dec-plurality` (13) and `dec-gate-table` (14).

Unresolved (`artifact.unresolved`): `unk-years`, `unk-lineage-count`, `unk-stones-local-return`, `unk-corrow` (whether Corrow is alive), `unk-sallow-house`, `unk-apprenticeship-return` and `unk-character-sourcing`.

Hypothetical alternatives not taken: `alt-cistern`, `alt-stones-restraint`, `alt-threshold`, `alt-early-compact` and `alt-right-revocation`.

One numbering point: the prose "open question 5, 6 and 10" matches the structured indexes 4, 5 and 9, so prose numbering is one-based. But "author-reserved choice 7" (`assume-p6`, `alt-right-revocation`) does not match any listed decision in these two files.
