# Auteur Studio — Creative Collaboration and Honest Proposal UX

**Date:** 2026-10-15
**Status:** Owner-endorsed direction for a bounded implementation program; this specification does not claim implementation, merge, human qualification, or release.
**Scope:** Local-first Living Story Studio, Narrative Architecture first; Story Realization and Book work remain under their existing owners.
**Sources:** `MISSION.md`, `docs/design/2026-10-09-living-story-studio.md`, `docs/design/2026-10-13-contextual-narrative-mentorship.md`, `docs/superpowers/specs/2026-10-12-narrative-architecture-visual-explanation.md`, and `docs/reviews/2026-10-12-studio-explanatory-views-comparison.md`.

## 1. Problem and intended outcome

An author entered an epic paladin progression-fantasy vision centered on exceptional, generous heroism and "joy through generous heroism." A coding agent proposed a plausible solitary-protector-to-steward flaw/lesson as if it were the governing arc, although the author had not selected that interpretation. The agent also delivered prose about Auteur's request/response mechanics instead of a structured candidate ready for the graph.

The current Studio prepares a source-bound `HostAgentRequest`, but the browser alone cannot call an arbitrary parent coding agent. Exposing raw packets, completion JSON, model boundaries, and many simultaneous toolbars makes an ordinary creative task feel like an engineering task.

**Desired user-visible result:** The author can describe a story in their own words, intentionally request an architecture proposal, see what is genuinely authored versus what AI added, explore meaningfully different interpretations, and inspect emotional, genre, trope, and structural mechanisms in a graph-first workspace. If a callable host-agent capability is attached, the requested response arrives and is validated through the existing contract without manual JSON transfer. Otherwise the UI is forthright and provides a useful manual handoff.

## 2. Product decisions

1. **Graph-first stays primary.** The author's story and meaningful nodes/relations occupy the visual focal point. The Story Vision is compact and editable. The inspector opens for a chosen item; inactive tools do not consume the graph's space.
2. **Author intent is not the agent's interpretation.** Display the exact current Story Vision as author working material. All new narrative arcs, obstacles, morals, conclusions, and relationship claims produced by the agent are proposals until the author deliberately acts.
3. **Exceptional heroism is not automatically a flaw.** "The paladin must stop solving problems alone" is a legitimate optional hypothesis, not an author-established premise. A plausible alternative is expanding generous capacity without undermining the protagonist's already generous disposition. The UI must expose this difference.
4. **Narrative Architecture is abstract.** It discusses reader experience, genre roles, trope functions, aesthetic strategies, renewable engines, and structural relationships. New named characters, places, magic rules, and specific plot events belong in Story Realization unless the author supplied them.
5. **Use the existing mentor.** `studio_mentor.py` already supports explore/challenge/directions with causal differentiators and tradeoffs. Do not invent a second options engine or separate chat database.
6. **Explain the existing graph, not a competing ontology.** Reuse `studio_explanations.js`, `studio_explanation_views.js`, and the prior prototype comparison: Overview graph; Genres = Anatomy; Tropes = Convention vs. Invention; Structure = Mechanism Map; Timeline = phase composition.
7. **No unconditional generation.** An explicit author request is required. Passive rendering, selection, and viewport manipulation do not invoke any external provider.
8. **Capability-aware handoff.** The Browser can request work from a separately attached, trusted host execution capability; absent that capability, it cannot promise immediate generation. Manual request/response remains a reachable advanced fallback. A failed provider is not silently replaced by another.
9. **No automatic acceptance.** Applying a proposed architecture revision modifies only the working candidate. A mentor direction becomes a working idea only through a deliberate CanvasStore action; accepted Identity, Structure, Relationships, Expression, and Book owners remain unchanged.

## 3. Evidence vocabulary, not new canonical states

| Presented item | Source / permitted claim | Never claim |
| --- | --- | --- |
| Author Story Vision | Exact `canvas/items/story-vision` content and current canvas revision | The author endorsed an interpretation not in the text |
| Author working item | Exact CanvasStore item and revision | It is accepted Story Identity |
| Agent architecture node, link, phase or mentor direction | Candidate request SHA, candidate-local ID, and recorded proposal relation | Accepted fact, proven causal effect, author commitment |
| Genre evidence | Versioned pack/legacy contract plus exact locator when actually bound | Universal genre law, absent-pack exclusion, or global originality |
| Existing accepted story | Exact source from the established owner if present and bound | An accepted source merely because the candidate mentions it |
| Unknown or unsupported comparison | Explicitly unknown/not classified | Unconventional, invalid, forbidden, or unprecedented |

The MVP need not introduce a new canonical schema or classify every candidate node heuristically. A truthful whole-proposal label plus exact author-vision comparison is preferable to falsely precise attribution. If item-level author quotation is introduced later, require an exact source locator and verify the quotation against the same request snapshot; a model's unsupported `author_declared` claim does not become evidence by self-labeling.

## 4. Author-facing interaction

**Initial/empty:** Keep the existing no-premise graph entry. "What should readers experience?" and other starting anchors are valid. One prominent primary action helps develop the current Story Vision when it contains meaningful input; no mandatory novel synopsis.

**Request:** The author deliberately invokes "Explore narrative architecture." The application saves working edits and produces the existing `studio_architecture.prepare_architecture` request. It must distinguish (a) an attached callable host from (b) no attached host. In (a), bounded asynchronous fulfillment proceeds without copying JSON, while request identity and ability to cancel/stop waiting stay visible. In (b), say "Request ready — connect or ask your coding agent" and provide one direct copy/CLI completion path, with advanced packet details collapsed.

**While waiting:** Explain that no new proposal has arrived; preserve previous proposals, working edits, and focus. A failed, stale, timed-out, or superseded request never replaces the active candidate and can be retried explicitly.

**On result:** Show a working-proposal summary beside the exact authored Story Vision. The primary visual surface is a focused graph or a focused concept; explain one meaningful link at a time. The current evidence/source and proposed status remain legible. The author may inspect, request alternatives, revise working architecture, or keep an editable working idea. None accepts canon.

**Alternatives:** Use the current scoped mentor contract to compare a small number of genuinely different causal mechanisms with consequences and tradeoffs, instead of automatically selecting a morality lesson. For the paladin fixture, compare at least (a) expansion of generous power without a required character flaw and (b) stewardship/intervention tension as an optional arc. A third option is warranted only when it is materially different.

**Explanation:** Genre Anatomy displays promise/engine/pressures/payoffs and source coverage. Tropes compare independently evidenced genre expectations with the proposal's story-specific treatment; multiple genre roles may coexist. Structure displays only declared edges, explicit relation verbs, sources and uncertainty. A missing link must not create a decorative causal arrow. All views allow returning to the same graph/selection.

## 5. Execution boundary

- Keep `HostAgentRequest`, `HostAgentResponse`, `ArchitectureCandidate`, request SHA/source fingerprints, idempotent completion, stale refusal, and revision-review/apply unchanged unless a narrowly evidenced extension is needed.
- A host adapter is an explicitly attached capability, **not a Browser shell runner**. Never run arbitrary commands submitted through HTTP or interpolate author prose into command-line execution.
- The default local server reports no attached executor unless one is actually registered. A configured adapter must preserve vendor neutrality at the author-facing interface and record the actual runtime/model when known, otherwise "unavailable."
- A single user-initiated request has bounded waiting, stop/cancel behavior where supported, correct tab/canvas identity checks, and recovery on re-entry. Canceling display does not silently erase existing evidence; cancellation of remote computation is claimed only if the adapter supports it.
- Author text is never sent to a new external provider without an intentional generation action and a visible indication of the configured execution destination. Secrets and provider credentials never appear in Browser request packets.
- If a real callable host cannot be attached in the chosen environment, implement an honest manual UX, preserve the integration seam, and **do not** report one-click generation as working.

## 6. Acceptance scenarios

1. A paladin vision explicitly values extraordinary generosity. Auteur quotes it as author intent but labels "must learn not to solve everything alone" as an unaccepted optional hypothesis.
2. The author can compare two substantively different paladin trajectories with rationale/tradeoffs, keep one as a working idea, revise or reject the other, and observe no accepted story mutation.
3. An attached host completes the actual typed ArchitectureCandidate request end-to-end without manually pasting JSON; a disconnected host yields an actionable truthful fallback and no phantom "working" state.
4. Changed vision or canvas invalidates stale host/mentor responses; a late response cannot rewrite current working architecture. Repeated identical response is idempotent; conflicting response is refused.
5. Genres/Tropes/Structure explanations use current candidate IDs and known source coverage. Missing Progression/Heroic Fantasy versioned packs are labeled as a coverage gap, not evidence of a violated convention.
6. Keyboard-only and narrow-screen authors can reach Story Vision, primary request action, a selected graph idea, the proposed/author distinction, alternatives, and return/back navigation without horizontal overflow.
7. A synthetic/automated Browser journey establishes mechanical UX only. A short actual-author walkthrough independently probes whether these meanings are understood.

## 7. Out of scope

No direct chat-plugin integration claim, mandatory new genre packs, universal trope originality classifier, semantic graph database, second mentorship engine, permanent provider daemon, background autonomous generation, hosted collaboration, native desktop GUI, rewriting prior author intent, auto-accept, auto-publish, or broad release.

**Integration:** The program should consist of reversible, narrowly verified PRs. Pre-existing PR #344's manual Quick Draft handoff remains a separate code scope. The #437 historic Glass Archive evidence and already merged #439 Book navigation are baselines; do not rewrite them as proof of this new UX.
