# 03. Shared Book 30 crisis: the Lowfen surge (frozen)

Status: **working / noncanonical.** One bounded situation, built from the established late-Series architecture, to run Alternatives A, B and C against the same starting conditions. Nothing here is accepted canon. The author has not chosen any alternative, and this scenario does not choose one.

**Freeze.** This file is frozen before any trace is written. Its SHA-256 is in [00](00-freeze-and-provenance.md). If any value below changes, every trace must be rerun. The coordinator had read the Stage A and Stage B reports when this scenario was built. The scenario is written to avoid depending on the two findings it might otherwise have leaned on: the Book 15 surfeit mechanism (Stage A R8, not used here), and the ratification body (Stage A R16, handled as a stated assumption in the C trace).

Labels: **[Est]** established in the packet, with its source. **[INV]** an invented numerical or operational assumption, stated so that it can be tested. **[Scen]** a scenario fact that is not a number.

---

## 1. The situation in one paragraph

The Long Return's pulse reaches the Hollow Gate on a date the Balance Stones fixed in Book 23. The pulse must be split between the high cistern and the lower channels. The Lowfen, the channel that carries Lower Ammen's wells down to the orchard terrace, is silted from the Book 21 release, and the window to clear it is ten weeks. The valley has 120 hands in that window, but 66 are owed to routine work that must go on. The labour that is free cannot both clear the Lowfen and reset its sluice. The Gate can send water to the high cistern, which means fever in the high terraces, or to the lower channels, which means a flood on the orchard terrace unless the lowland gate at Harrow Lowe passes it on, and that gate is the Mill Compact's.

## 2. Established inputs

| Input | Source in the packet |
|---|---|
| The Long Return is a deep-store pulse, predicted by the Balance Stones cut in Book 23, and it arrives in Book 30. | 01 §6; W2 `str_long_return`; original §5 Book 23 and Book 30 |
| The pulse needs channel labour before its date and a Gate routing that decides which channel takes the surge. | 01 §6; W2 `str_long_return` |
| The Hollow Gate divides the high cistern's release between the upper and lower channels. The Gate Table sets its schedule from the gauge and holds no record. | 01 §1, §3; W2 `str_hollow_gate`, `inst_gate_table` |
| Thinning dries the high channels and floods wild water below. Surfeit is "too much return, or stored water with no draw", and it brings stagnant pools and fever. | original §2 (the Source) |
| Release at need in a dry spring draws the high cistern down, and the lower channels silt when the release stops. | 01 §3 (Book 21 consequence) |
| Lineage crews repaired the Lowfen in Book 20 under a Special Draw Right, which is conditional on training apprentices from outside the lineage. | 01 §2; W2 `inst_lineage_crews` |
| The Book 21 declined household's share runs wild down the lowest Lowfen terrace into a neighbour's orchard. | 01 §2; W2 `str_declined_share` |
| Repair in Book 19 needed roughly one rota's worth of labour for a season. | 01 §2 |
| The Mill Compact buys shares, its draw carries no return labour, and its Book 27–29 bid for lowland water rights is pending. Under B and C its grain can be owed as labour. | 01 §1, §6; W2 `inst_mill_compact`, `l_compact_hands_in_kind` |
| The Mill Compact is "lowland grain-buyers at the lower gate of Harrow Lowe". | original §2 (**not in W2**; see §11) |
| Hesper Sallow was born about Book 13, so she is an adult in Book 30. Idrun Sallow is about 65. | original §2 |
| The Terrace Council runs the counted Turn in the high terraces and holds the gift reading as legitimate. The Reading Hall publishes the gauge and the Balance Stones. The Gate Table has been in place since Book 22. | W2 `inst_terrace_council`, `inst_reading_hall`, `inst_gate_table` |

## 3. Invented assumptions

Every number below is **[INV]**. Each is an illustrative scale, chosen to test feasibility. None is taken from the architecture.

| ID | Assumption | Value |
|---|---|---|
| INV-1 | Unit of water: the Lowfen's capacity when fully clear | 1 CU (channel unit) |
| INV-2 | Surge at the peak, as the Stones' range | 1.4 to 1.9 CU |
| INV-3 | Surge revealed at the leading edge, three days before the peak | frozen run: **1.7 CU** |
| INV-4 | High cistern's tolerable added store before surfeit | 0.4 CU |
| INV-5 | Silted Lowfen capacity now (Council survey, Book 30 week -12) | 0.6 CU, taken as exact in the frozen run |
| INV-6 | Declined household's forfeited share, running wild on the orchard reach while it stays outside the rota | 0.1 CU |
| INV-7 | Partial clearance: capacity rises linearly with hand-seasons delivered to task T1, up to 60 | c = 0.6 + 0.2 × min(1, H_T1 / 60) |
| INV-8 | Full clearance T2 (sluice reset and sealing), all-or-nothing, not started until T1 is complete | 18 hand-seasons, of which 12 skilled |
| INV-9 | Lowland plots below the orchard can take overflow if the Harrow Lowe gate is open | up to 0.8 CU, at the cost of the Compact's purchased harvest there |
| INV-10 | Lowland hired hands the Compact can pay for in grain, per window, unskilled | up to 12 hand-seasons |
| INV-11 | Routine work, which must go on in the window and is not suspended in any trace | 66 hand-seasons (table §5) |
| INV-12 | Window length: week -10 to the peak. Lead time before labour can start: A (pair-hands) and C (pre-drawn panel) one week; B (lot-drawn panel and published rota, decided in Book 30) three weeks | see §8 |
| INV-13 | Harrow Lowe gate is operated by the Compact's factor, under the Book 6 settlement | operational assumption, labelled |
| INV-14 | Labour delivered = (free hand-seasons, plus any Compact hands) × (1 − lead weeks ÷ 10). Factor 0.9 for A and C; 0.7 for B | used in §8 |

## 4. Physical state at the start of the window (week -10)

- **Pulse date:** fixed. The peak arrives at the Hollow Gate on day D.
- **Surge range:** 1.4 to 1.9 CU (INV-2). Central estimate 1.65 CU, published by the Reading Hall.
- **Lowfen:** silted, capacity 0.6 CU (INV-5).
- **Orchard terrace:** the lowest community, below the Lowfen. Its own channel reach below the declined household is unrepaired.
- **Declined household:** outside the rota since Book 21. Its share is forfeit and its water runs wild (INV-6).
- **High cistern:** store as at the end of the settled Book 22–29 period, with no surfeit now.
- **Harrow Lowe lower gate:** operated by the Compact's factor (INV-13). It can pass overflow onward to the lowland plots (INV-9).

## 5. Labour in the window

| Community | Hands | Skilled within the hands | Routine work (fixed) | Free |
|---|---|---|---|---|
| High terraces (Quillmark; the counted Turn) | 56 | 0 | 40 | 16 |
| Lineage crews (Ysa Trant's line; holds the Special Draw Right) | 16 | 16 | 6 | 10 |
| Lower Ammen (the gift practice; 4 trained apprentices from outside the lineage) | 30 | 4 | 14 | 16 |
| Orchard terrace (the lowest; excludes the declined household's 4 hands) | 18 | 0 | 6 | 12 |
| **Total** | **120** | **20** | **66** | **54** |

**Tasks.**
- **T1, clear the Lowfen's silt:** 60 hand-seasons, unskilled work. Skilled hands may do it.
- **T2, reset the sluice and seal the leaks:** 12 skilled and 6 unskilled, 18 in all. It gives no capacity until complete (INV-8).

**Feasibility, frozen.**
- Free labour is 54. Free labour plus the Compact's hired hands is at most 66. T1 plus T2 needs 78. So **T2 is infeasible in every alternative** in this window.
- Without the Compact's 12 hands, T1 is short by 6. Capacity reaches at most 0.78 CU (INV-7).
- With the Compact's 12 hands, T1 is complete and capacity reaches 0.8 CU. T2 cannot finish, so the Lowfen stays at 0.8 CU at best.
- Routine work is not suspended in any trace. Suspending the high terraces' 40 hand-seasons would make T2 feasible, but it would thin the high channels and dry Quillmark's season, and no alternative's authority covers it. The frozen scenario excludes it and says so (§11).

## 6. Routing rules, frozen

1. The Gate splits the surge: high allotment h to the high cistern, and the rest to the lower channels.
2. The lower channels receive S − h + w, where w is the declined household's wild water (INV-6) unless it rejoins the rota.
3. Overflow o = max(0, S − h + w − c), where c is the Lowfen's capacity at the peak.
4. Overflow floods the orchard terrace unless the Harrow Lowe gate is open. If it is open, the overflow passes to the lowland plots, up to 0.8 CU (INV-9).
5. Surfeit: any h above 0.4 CU adds stagnant pools and fever in the high terraces, in proportion to the excess above 0.4 (INV-4). Surfeit is a human cost, not a choice the Gate can make alone. Who may authorise h above 0.4 is part of each alternative's trace.
6. The Lowfen's overflow breaks first where the declined household's reach is unrepaired.

## 7. Institutions and characters, starting positions

- **Idrun Sallow** (Council steward, about 65). Wants the orchard protected, and wants the Turn kept humane. Reluctant to ask Quillmark for fever.
- **Hesper Sallow** (Council surveyor, about 25). Measured the Lowfen at 0.6 CU. She has to defend that figure against the Stones' central estimate, and she is aware that the lineage carries the skill. Wants the Turn measured fairly and does not want the lineage to bear the cost alone.
- **Ysa Trant's line** (the maintenance lineages). Holds the Special Draw Right, which is revocable by the Council and whose revocability is an open author question. Will not carry the Right's cost alone and threatens craft withdrawal if the Right is used to fund a floor it did not agree to.
- **Oona Brisk** (Compact factor). Keeps the Harrow Lowe gate. Her bid for lowland water rights is pending. Wants the Compact's plots spared, and sees the gate as leverage, not as a duty.
- **Corrow's remnant.** Holds the debt reading. Presses that the Compact's purchased draw owes hands, and that the gauge is not a record.
- **Orchard-terrace households.** Want their channel cleared. The declined household wants its standing back without losing face. Its neighbours bear the breach first.
- **Quillmark's high-terrace households.** Want their Turn respected. The low-lying houses fear fever in the pools.
- **The Gate Table** (rotating; one seat for each practice, and one by lot from non-craft households). Sets the schedule from the gauge. No record, no shares.
- **The Reading Hall.** Publishes the central estimate and the surge range. Keeps the public record. No schedule authority.

## 8. Information and timeline, common to all alternatives

| When | Event | Who knows |
|---|---|---|
| Week -12 | The Council's surveyor measures the Lowfen at 0.6 CU (INV-5). | Council, then all |
| Week -10 | Window opens. The Stones' range (1.4 to 1.9 CU) and central estimate (1.65 CU) are published. Routine work continues for every community. | All |
| Week -10 to -3 | Labour is organised. Lead time: one week for pair-hands (A) or a pre-drawn panel (C); three weeks for a lot-drawn panel and a published rota (B, decided in Book 30). Delivered labour = (free hand-seasons, plus any Compact hands) × (1 − lead weeks ÷ 10) (INV-14). | Each alternative's bodies |
| Day D − 3 | Leading edge. The true surge is revealed (frozen: 1.7 CU). The Gate must set h within 24 hours. The Harrow Lowe gate must be decided at the same time. | Gate, Compact, Council |
| Day D | Peak. | All |

**Uncertainties that persist.** The surge is unknown until the leading edge. The Lowfen's measured capacity is an estimate. Whether the Compact's gate opens is unknown until it does.

## 9. The decision each alternative must answer

Every alternative must answer these questions from its own mechanisms, not from the narrative:
1. Who volunteers, is assigned or is bound, and who can refuse?
2. How is the labour shortfall redistributed?
3. Does the Lowfen reach 0.8 CU? Can anything reach 1.0 CU?
4. What sets h, and who may authorise h above 0.4 CU?
5. Is the Harrow Lowe gate opened, and by whom?
6. Who bears the surfeit, the overflow and the declined household's loss?
7. Which institution's authority is exercised, and does it stay within its remit?

## 10. Frozen run and sensitivity

- **Frozen run:** S = 1.7 CU, w = 0.1 CU, c as each alternative delivers.
- **Sensitivity A-low:** S = 1.4 CU. Run for each alternative.
- **Sensitivity A-high:** S = 1.9 CU. Run for each alternative.
- The traces report the frozen run in full and the sensitivity cases in one line each.

## 11. Declared exclusions and inheritance flags

- **Lives are not decided.** Each trace reports exposure and loss of stores, homes and water. Whether the flood or the fever causes deaths is an author-reserved decision, and the traces say so and do not settle it.
- **Routine suspension is excluded** (see §5). No alternative's authority covers it, and it would thin the high channels.
- **The Harrow Lowe gate is inherited from the original (§2) and is absent from W2.** It is treated as established here, and it is flagged. If the author rejects it, the lowland overflow path disappears and every trace must be rerun.
- **The Book 15 surfeit mechanism is not used.** The scenario relies only on the Source definitions in §2, not on the Book 15 claim that Stage A flagged (R8).
- **Ratification is not assumed in this scenario.** C's trace states its ratification as an explicit assumption, because the architecture does not yet name a body that ratifies (Stage A R16).
- **The Compact's clause is not assumed in this scenario.** Each trace states whether the Compact's 12 hands are owed or voluntary.

## 12. Author-reserved decisions the traces do not settle

- Whether the flood or the fever causes deaths.
- Whether the shared accounting of care binds, and in what form.
- Whether Alternative A, B or C is the finale direction.
- Whether the Hollow Gate and the Gate Table are accepted parts of the world.
- Whether the Special Draw Right is revocable or permanent.
- Whether the Compact's grain-labour settles its claim, and whether the Compact has a seat.
- Whether a Balance Stones threshold exists and whether activation is automatic or confirmed (C only).
