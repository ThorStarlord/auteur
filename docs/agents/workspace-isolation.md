# Workspace and repository isolation

This page is the detailed, reusable reference behind the workspace-repository
rule in `AGENTS.md`. It explains the vocabulary, the invariant, the preflight
checks, and the failure rule, so agents and operators do not have to infer
infrastructure intent from ambiguous terms.

## Vocabulary

These are distinct identities. Treating them as interchangeable is the root
cause of the workspace-confusion class of incident.

- **Session workspace**: the directory an agent/session is launched against.
- **Git repository**: a collection of Git data (refs, objects, config) rooted
  at a `.git` directory (or a `.git` file pointing to one).
- **Branch**: a movable ref inside a repository.
- **Linked Git worktree**: an additional checkout owned by an existing
  repository; it shares that repository's object/ref universe.
- **Standalone clone**: a repository with its own independent `.git`; it does
  not share another repository's Git universe.

## How isolation is determined

Path location does **not** determine isolation; `.git` topology does.

```
Standalone repo A            Standalone repo B
└── .git/                    └── .git/
    independent universe         independent universe


Repo A
├── .git/
└── linked worktree C
              ↑
      shares Repo A's Git universe
```

A checkout nested under `.worktrees/` could technically be independent, and a
sibling directory could be linked. Verify ownership with
`git rev-parse --git-common-dir`, never by folder name alone.

## The invariant

> If isolation or repository identity matters, the agent's initial workspace
> must already be the intended repository. Verify and bind the workspace
> before the session begins.

Do not start an agent in one repository and ask it to repair its own
workspace mid-session. That leaks context and is not a reliable launch flow.

## Preflight

When repository identity matters, verify at least:

```text
git rev-parse --show-toplevel     # workspace/repo root
git rev-parse --git-common-dir    # which Git universe owns this checkout
git rev-parse HEAD                # exact current commit
git remote -v                     # remotes policy (none / expected set)
git worktree list                 # standalone vs linked; siblings
```

Where strong historical isolation matters, additionally inspect refs and
object reachability to confirm the executor cannot inspect post-BASE history.

`scripts/verify-agent-workspace.ps1` automates the root/topology/HEAD checks
against expected values and fails loudly when they do not match.

## Failure rule

If a session starts in the wrong workspace:

> **Do not repair the experimental session in place.** Stop, fix the launch
> configuration, and create a fresh session bound to the intended workspace.

This rule is scoped to tasks where initial context or isolation matters. For
ordinary non-experimental work, changing directories during a session is
fine.

## Ambiguity rule

If a request says something like "change the worktree to X" and X is a
filesystem path, first determine what X actually is before mutating anything:

- a branch?
- a linked worktree?
- a standalone repository?
- a plain directory?

Inspect with the preflight commands and, if still ambiguous, ask.

## Blameless postmortem principle

When workspace confusion occurs, improve the preflight and the terminology
rather than attributing failure to the operator or the agent. This aligns with
the "blame process, not people" rule in `AGENTS.md` and `CLAUDE.md`.

## Storage conventions

- **Normal development**: linked Git worktrees under
  `auteur/.worktrees/<task>`, e.g.
  `git worktree add .worktrees/feature-x -b agent/feature-x`. These share the
  repository, which is intended for fast parallel feature work. Add
  `.worktrees/` to `.gitignore`.
- **Isolated / blind execution**: a standalone repository with its own `.git`
  (e.g. a sibling directory), so the executor cannot inspect the development
  repository's history.

Use the words precisely: **linked worktree** for `.worktrees/` checkouts,
**standalone repository** for isolated checkouts, and **session workspace**
for the directory an agent is launched against.
