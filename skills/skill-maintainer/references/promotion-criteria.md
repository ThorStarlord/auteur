# Skill Promotion Criteria

A skill improvement or repository edit is allowed to be promoted to "Stable" and merged only when it satisfies the following six gates.

## 1. Plan Validation
The `skill_improvement_plan.md` MUST pass the specialized validator:
- [x] Every edit is linked to evidence in a `usage_research_report.md`.
- [x] Anti-overfitting guards are provided.
- [x] `edit_type` and `risk_level` are classified.
- [x] No absolute paths.

## 2. User Approval
- [x] The user or an authorized human-in-the-loop has explicitly approved the `skill_improvement_plan.md`.
- [x] Approval is recorded in the `maintenance_run_log.md`.

## 3. Structural Integrity
- [x] The global `validate-repo.py` script passes for the entire repository after the patch is applied.

## 4. Scenario Rerun (Verification)
- [x] The triggering research scenario (the one that exposed the failure) is rerun.
- [x] The new `usage_research_report.md` (post-fix) confirms that the "Actual Behavior" now matches the "Expected Behavior".

## 5. Regression Check
- [x] At least one neighboring regression scenario (related ecosystem or boundary) is rerun.
- [x] Verification confirms that the new logic did not break previously stable behaviors.

## 6. Audit Trail
- [x] A `maintenance_run_log.md` is completed, documenting the source plan, files changed, and all verification results.
