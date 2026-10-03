# Agent Instructions For Auteur

Auteur is becoming a whole-story structure engine first and a chapter drafting
engine second. Agent work should preserve that distinction.

For unsupervised/factory runs, `MISSION.md` (scope, out-of-scope-forever, hard
invariants) and `FACTORY_RULES.md` (unsupervised behavior rules) are the
governing documents and sit on the protected list.

## Core rules

1. **Infer within the delegation envelope; escalate material ambiguity.** Once a
   human has authorized a goal, accepted design/specification, and constraints,
   proceed autonomously on low-level implementation choices that preserve that
   envelope. Do not ask for approval on routine naming, helper placement, local
   refactoring, test organization, or behaviorally equivalent algorithms.
2. **Simplest solution first.** Always implement the simplest thing that could
   work. Do not add abstractions or flexibility that were not explicitly
   requested or required by the authorized behavior.
3. **Don't touch unrelated code.** If a file or function is not directly part
   of the current task, do not modify it, even if you think it could be
   improved.
4. **Flag material uncertainty explicitly.** Investigate routine technical
   uncertainty yourself. Stop only when the unresolved uncertainty would change
   product intent, architecture, authority, security, compatibility, external
   effects, or authorized scope.

## Process

- For conceptual design, use a grilling workflow: ask one question at a time,
  give a recommended answer, and wait for approval before locking owner-reserved
  decisions.
- After the work package/design is approved, execute continuously without
  human-in-loop pauses for low-level implementation choices unless a stop
  condition below is reached.
- Blame process, not people. If work drifts, add a clearer checkpoint,
  document the decision earlier, or improve the verification path.
- Capture approved conceptual decisions in `docs/` before implementing schema,
  analyzer, CLI, or pipeline behavior.
- Prefer updating an existing authoritative document over creating a new durable
  document. Create a new durable document only when it has a distinct long-lived
  role that cannot be represented clearly in an existing mission, PRD, status,
  roadmap, ADR, design, guide, or evidence surface. Do not create session-only
  meta-documents merely to restate information already preserved elsewhere.
- Keep user-authorial choices explicit. Do not silently fill or rewrite the
  story spine.
- Treat workspace identity as a preflight condition, not something the
  executor should discover or repair after work begins.

### Upstream story-idea selection

When the task is **what story should be made** rather than how an already
selected story should be designed, follow
`docs/story-opportunity-discovery.md`.

In particular:

- decompose influences into desired experience, portable mechanism, and tradeoff
  rather than copying source-specific expression;
- keep author preference, sourced audience evidence, critique claims, craft
  interpretation, and design prescriptions epistemically distinct;
- treat latent model knowledge about stories or criticism as a search prior /
  hypothesis, not current audience consensus or market evidence;
- interpret criticism before acting on it; a complaint is not automatically the
  correct repair;
- generate causally distinct working opportunities, not cosmetic reskins;
- when comparing a working premise against an intended genre, experience, and
  narrative horizon, use `docs/premise-fitness.md`: distinguish premise
  efficacy from realized effectiveness, inspect efficiency/runway/scope fit,
  and do not reduce fitness to a universal quality score;
- if scope is unknown, provide conditional fitness across plausible horizons
  rather than silently selecting one;
- distinguish finite, renewable, expanding, and multi-domain runway when useful,
  and keep runway, renewability, and expansion capacity conceptually separate;
- do not infer runway from world size or evocative setting alone; an appropriate
  finding is `EVOCATIVE PREMISE / GOVERNING ENGINE UNESTABLISHED`;
- treat Genre Packs as reusable genre knowledge that Premise Fitness may
  consume, not as automatic mass-appeal or premise-quality selectors; when no
  relevant pack exists, use bounded generic craft reasoning and lower the
  specificity of genre claims rather than fabricating pack knowledge;
- prefer advisory scope, engine, complexity, or hierarchy repairs over a single
  automatic "fix";
- keep opportunity and fitness outputs `WORKING / NOT ACCEPTED` and hand
  selected premises into existing Story Discovery rather than silently creating
  Story Identity;
- do not add numerical "idea quality", popularity, premise-fitness, or
  commercial-success scores unless a separately authorized, claim-appropriate
  contract exists.

### Delegation envelope

The initial human prompt, accepted design/specification, repository hard
invariants, and explicit constraints define the delegation envelope.

Inside that envelope, the coding agent owns decisions such as:

- internal function and variable naming;
- helper extraction and local refactoring needed to implement the goal cleanly;
- behaviorally equivalent implementation algorithms;
- test fixture and focused regression-test organization;
- L1 focused-test selection;
- whether a named changed boundary justifies targeted L2 validation;
- local error-handling mechanics consistent with existing public semantics;
- internal data flow and commit decomposition;
- minor documentation updates that describe the implemented behavior;
- removal of dead ends introduced by the current work package.

These decisions do not require repeated human approval.

### Consuming strategic-analysis artifacts

A strategic analysis describes the decision space; it does not automatically
authorize every construction path, transition, candidate responsibility, or
future capability it identifies.

When the governing analysis disposition is `INVESTIGATE`, `DEFER`, `STOP`,
`NO_CHANGE`, or another evidence/authority-limited state, a later broad
instruction such as "implement all tasks" applies only to responsibilities that
are both executable and already authorized within the delegation envelope.
Candidate paths, future transitions, evidence-gated features, and owner-reserved
choices remain unselected until the required evidence or explicit authority
selects them.

If strategic analysis separates independent lanes, preserve that separation.
For example, already-authorized behavior-preserving maintenance may continue
while a product-direction lane waits for human or external evidence. Do not
manufacture the missing evidence merely to keep implementation moving.

For incremental maintainability programs, repository size or file length alone
is not sufficient admission evidence for another refactor. Continue
decomposition only when another concrete existing responsibility can be
extracted behavior-preservingly, behind stable public/authority semantics, with
focused regression evidence. When no such responsibility is presently
warranted, stopping the decomposition is a valid outcome.

In shorthand:

```text
strategic path != implementation authority
broad execution request != selection of every candidate
maintenance authorization != product-direction authorization
large file != automatic refactor responsibility
```

### Owner-reserved decisions and stop conditions

Stop and escalate only when continuing requires a material decision about:

- product intent or user-visible semantics not implied by the authorized goal;
- canonical narrative meaning or Layer 1 author commitments;
- semantic architecture or ownership boundaries;
- public compatibility contracts;
- destructive or irreversible data migration;
- security, credentials, privacy, or new external data transmission;
- deployment, publication, or release authorization;
- permanent product-scope constraints;
- material scope expansion beyond the authorized work package;
- changing a hard invariant in `MISSION.md`;
- contradictory requirements that cannot be resolved from current sources of truth.

Also stop when repeated focused attempts indicate the approved design is wrong
rather than merely incomplete, or when cheap validation cannot establish
reasonable confidence in the changed behavior.

Routine uncertainty about naming, helper placement, fixture structure, or
other equivalent implementation mechanics is not a stop condition.

### Code Review & Verification

When reviewing code changes or investigating test failures:

1. **Distinguish issue types before acting:**
   - **Code defect:** Tests fail, tests contradict source inspection, behavior violates invariants
   - **Incomplete requirements:** Feature partially implemented, edge cases unhandled
   - **Environment issue:** Tests pass, source is correct, manual behavior differs (stale package, PATH, Python version mismatch)
   - **Design preference:** Works as intended, but stakeholder wants different tradeoff

2. **Verify claims with evidence:**
   - Don't cite line numbers without inspecting them
   - Don't claim missing components without checking current git HEAD
   - Distinguish between "tests pass" (exercises live code) and "implementation exists in git" (requires committed files)
   - Investigate ordinary uncertainty before escalating it

3. **Investigate environment issues before rewriting:**
   - Multiple Python installations can coexist; verify `which python` and `python -m module`
   - Editable installs (`pip install -e .`) can become stale; verify import paths
   - Shell executables resolve from PATH; use `which` or equivalent to check resolution order
   - When manual test fails but automated tests pass: investigate execution environment, not code

4. **Regression tests protect invariants, not environments:**