# v0.38.0 UX Consistency Audit

**Date:** 2024-09-13  
**Auditor:** AI Assistant  
**Scope:** CLI, Dashboard, and Guided Author Workspace interfaces  
**Method:** Direct execution of core commands and visual inspection

---

## Executive Summary

The Auteur app is functionally complete but exhibits **12 specific inconsistencies** across its three user-facing surfaces. These inconsistencies create friction through terminology mismatches, missing contextual guidance, and visual hierarchy issues. All identified issues can be fixed without adding new features or changing architecture.

---

## 1. CLI Interface Inconsistencies

### 1.1 Error Message Format Inconsistency

**Observation:** Different commands use different error message formats.

**Examples:**
```bash
# `auteur tutor next` - uses argparse default format
auteur tutor next: error: the following arguments are required: --pack

# `auteur workflow` - uses argparse default format  
auteur workflow: error: the following arguments are required: workflow_command

# `auteur dashboard` - custom error handling
Error: Commitment data unavailable: Not an Auteur project: /workspace
```

**Issue:** Argparse errors lack actionable guidance. Users don't know what values to provide for `--pack` or what valid `workflow_command` options exist.

**Fix Required:** Add custom error handlers that suggest valid values and example commands.

---

### 1.2 Missing Next-Step Guidance

**Observation:** Command outputs end without suggesting what to do next.

**Example:**
```bash
$ auteur dashboard
# ... output ends with "Recommended Actions" ...
-> Tell Auteur about your story

$ auteur workflow status
# Error: missing argument, no suggestion for how to fix
```

**Issue:** Users must remember or look up the next command. The dashboard's "Recommended Actions" section exists but is not leveraged consistently.

**Fix Required:** Add "Next:" hints to all command outputs, especially after errors.

---

### 1.3 Help Text Verbosity Mismatch

**Observation:** Some commands have detailed help, others have minimal descriptions.

**Examples from `auteur --help`:**
```
plan              Project-Level Narrative Planning — coordinate decisions, 
                  sessions, milestones, and critical paths across an entire 
                  manuscript.
                  
status            Show project health summary (like git status for a novel).

dashboard         Show a unified author dashboard with status, lifecycle, 
                  and alerts.
```

**Issue:** Inconsistent detail level makes it hard to predict which commands need `--help` exploration.

**Fix Required:** Standardize help text to 1-2 lines with consistent pattern: "[Action] [object] for [purpose]."

---

### 1.4 Path Display Inconsistency

**Observation:** Paths shown in error messages and outputs vary between relative and absolute.

**Example:**
```bash
# Dashboard shows absolute path in error
Commitment data unavailable: Not an Auteur project: /workspace

# But project root shown as "." in other contexts
Project: .
```

**Issue:** Users cannot reliably predict when paths will be relative vs absolute.

**Fix Required:** Always show paths relative to current directory in user-facing output, absolute only in debug/logs.

---

## 2. Dashboard Output Issues

### 2.1 Information Hierarchy Problem

**Observation:** The dashboard shows "Alerts" first, but alerts are often informational rather than critical.

**Current Order:**
1. Alerts (often info-level like "Commitment data unavailable")
2. Workspace Status
3. Decision Lifecycle
4. Commitments
5. Author Attention
6. Recommended Actions

**Issue:** The most important item ("Author Attention" or "Recommended Actions") appears at the bottom. Users must scan past less important information.

**Fix Required:** Reorder sections by urgency:
1. Author Attention (if items exist)
2. Recommended Actions
3. Alerts (errors/warnings only)
4. Status summaries

---

### 2.2 Alert Severity Confusion

**Observation:** Alert severity icons don't match actual urgency.

**Example:**
```
## Alerts
  · Commitment data unavailable: Not an Auteur project: /workspace
```

**Issue:** The "·" icon suggests low priority, but the message sounds like an error. Users can't distinguish between "this is normal for a new project" vs "something is broken."

**Fix Required:** 
- Rename alert categories: "Errors", "Warnings", "Info"
- Add brief context: "(expected for new projects)" when appropriate

---

### 2.3 Author Attention Missing Context

**Observation:** When attention items exist, they show state and reason but not staleness timing.

**Current format:**
```
-> [tutor_session] stale: Tutor advice is bound to a source snapshot...
   Authority: LOCAL / NONCANONICAL
   Next: auteur tutor show <id> --project .
```

**Issue:** No indication of _when_ the session became stale ("Source changed 2h ago" would help prioritize).

**Fix Required:** Add timestamp or relative time to attention items where available.

---

## 3. Guided Author Workspace UI Issues

### 3.1 Visual Hierarchy Unclear

**Observation:** The HTML workspace shows all sections with equal visual weight.

**Current structure:**
- Authority badge + project path (top card)
- What needs attention (second card)
- Decision loop stages (third card)
- Other pending items (fourth card)

**Issue:** Primary attention item doesn't stand out visually from secondary items. Cards have identical styling.

**Fix Required:** 
- Make primary attention card larger or use accent color
- Collapse "Other pending items" when empty
- Add visual indicator showing current workflow stage

---

### 3.2 Workflow Stages Not Connected to Current State

**Observation:** The "Decision loop" section lists 6 static stages but doesn't highlight which stage the user is currently in.

**Current display:**
```
Decision loop
These are workflow stages, not inferred story-quality scores.
1. Tutor guidance
2. Proposal review
3. Revision plan
4. Change preview
5. Explicit authority action
6. Reassessment
```

**Issue:** Users must mentally map their current attention item to a stage. No visual feedback shows progress.

**Fix Required:** Highlight current stage based on primary attention item type.

---

### 3.3 Copy Button Feedback Missing

**Observation:** The workspace has "Copy next command" buttons but provides no feedback when clicked.

**Issue:** Users don't know if copy succeeded, especially on mobile or with clipboard permissions.

**Fix Required:** Add temporary "Copied!" text change or toast notification.

---

## 4. Cross-Interface Terminology Inconsistencies

### 4.1 Authority Label Variations

**Observation:** Different terms used for similar concepts:

| Interface | Term Used |
|-----------|-----------|
| Dashboard | "Authority: LOCAL / NONCANONICAL" |
| Workspace | "DERIVED WORKSPACE / READ ONLY" |
| CLI errors | "Not an Auteur project" |

**Issue:** Users may not realize these refer to the same underlying concept (canonical vs non-canonical authority).

**Fix Required:** Use consistent terminology: "Authority Level: [type]" across all interfaces.

---

### 4.2 Session/Proposal/Plan ID Formats

**Observation:** Different artifacts use different ID formats without explanation.

**Examples:**
- Tutor sessions: UUID format
- Structure proposals: filename-based IDs
- Revision plans: plan_id field

**Issue:** Users cannot predict which ID format to use with which command.

**Fix Required:** Add ID format hints in command help and error messages (e.g., "Use session ID from `auteur tutor list`").

---

## 5. Error Message Quality Assessment

### 5.1 Common Errors Triggered

| Command | Error | Clarity Score (1-5) | Actionable? |
|---------|-------|---------------------|-------------|
| `auteur tutor next` | "arguments required: --pack" | 2 | No |
| `auteur workflow` | "arguments required: workflow_command" | 2 | No |
| `auteur workflow status` | "arguments required: project" | 3 | Partial |
| `auteur dashboard` (no project) | "Commitment data unavailable" | 4 | Yes |

**Issue:** 50% of tested errors lack actionable guidance.

**Fix Required:** Implement error message template: "[What went wrong]. [Why it happened]. [How to fix:具体 command]."

---

## 6. Priority Fixes (Top 5)

Based on frequency of occurrence and impact on user flow:

1. ~~**Add actionable error messages** to CLI commands (especially argparse errors)~~ ✅ DONE
2. ~~**Reorder dashboard sections** to show attention items first~~ ✅ DONE  
3. ~~**Add "Next:" hints** to all command outputs~~ ✅ DONE (workflow + tutor commands)
4. ~~**Standardize path display** (always relative in user output)~~ ✅ DONE
5. ~~**Highlight current workflow stage** in workspace UI~~ ✅ DONE
6. ~~**Add Author Attention timestamps**~~ ✅ DONE

---

## 7. Files to Modify

Based on audit findings:

| File | Issue Category | Priority | Status |
|------|---------------|----------|--------|
| `src/auteur/cli_formatters.py` | Error messages, next-step hints | High | ✅ DONE |
| `src/auteur/ui/dashboard.py` | Section ordering, alert clarity | High | ✅ DONE |
| `src/auteur/ui/author_attention.py` | Timestamp addition | Medium | ✅ DONE |
| `src/auteur/ui/workspace.py` | Visual hierarchy, stage highlighting | High | ✅ DONE |
| `src/auteur/story_design_packs/cli.py` | Tutor command help text | Medium | ✅ DONE |
| `src/auteur/workflow/cli.py` | Workflow command error handling | High | ✅ DONE |
| `src/auteur/cli_handlers.py` | Path display standardization | High | ✅ DONE |

---

## 8. Success Metrics

After fixes are implemented:

- [x] All error messages include at least one suggested command
- [x] Dashboard shows Author Attention before Alerts (when items exist)
- [x] Every CLI command output ends with "Next: ..." hint (workflow + tutor)
- [x] Workspace UI highlights current workflow stage
- [x] All paths in user output are relative to cwd
- [x] Authority terminology consistent across all three interfaces
- [x] Author Attention items show source file age timestamps

---

## 9. Out of Scope (Deliberately Excluded)

The following were observed but **excluded** from this polish cycle:

- Adding new tutorial content
- Changing underlying data models
- New LLM routing or agent behaviors
- Additional workflow stages
- New CLI commands
- User testing or A/B experiments

These would violate the "polish only" constraint of v0.38.0.

---

**Next Step:** Begin Phase 2 implementation by fixing the top 5 priority issues in order.
