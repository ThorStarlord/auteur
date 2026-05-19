# Grill With Docs — Stabilizing Phase 0: The Narrative Engine

Date: 2026-05-19
Mode: self-answered grilling (no user pauses, as requested)
Inputs: CONTEXT.md, identity.py, analyzer.py, docs/opinionated-narrative-engine.md

---

## Q1. Where should structural and coherence validation of the Narrative Engine live, and how should it be executed?
**Recommended Answer**: 
We should introduce a dedicated, deterministic validation check directly in the `StoryIdentity` layer. When `auteur identity validate` runs, it must perform Pydantic schema validation *and* execute a suite of deterministic, LLM-free structural rules on the identity itself.
**Answer**: Accepted.

---

## Q2. What exact validation rules are required to declare a `StoryIdentity` structurally sound?
**Recommended Answer**: 
The validation runner must enforce the following rules:
1. **Want-Change Coherence**: The central engine's `want` and `change` must not be duplicate/identical (case-insensitive, whitespace-stripped).
2. **Genre Ending Tone Mismatch**: The chosen mode/ending tone (tragic or hopeful) must not violate the genre contract snapshot's `forbidden_mismatches` (e.g. forbidding tragic endings in Romance or hopeful endings in Grimdark), unless an explicit override is configured in `author_overrides`.
3. **Target Experience Avoidance Clash**: The avoided experiences list must not clash with the primary target experience or progression tone steps.
**Answer**: Accepted.

---

## Q3. How should validation failures be presented to the user?
**Recommended Answer**: 
The command `auteur identity validate` should output a structured list of diagnostics (with rule, severity, layer, message, evidence, and repair options) to `stderr`, and exit with code `1` if there is any error.
**Answer**: Accepted.

---

## Q4. What is the behavior of the compilation step (`auteur blueprint seed` / `auteur identity compile`) when the identity has validation errors?
**Recommended Answer**: 
The compiler must run the identity validation checks before compiling. If any validation errors exist, the compilation process must abort, print the diagnostics, and exit with code `1`, preventing the creation of an invalid blueprint.
**Answer**: Accepted.

---

## Q5. What test cases are needed to verify the stability of the Narrative Engine (Phase 0)?
**Recommended Answer**: 
We should add tests in `tests/test_identity_validation.py` asserting that:
1. An identity with duplicate want/change fails validation with a specific warning or error.
2. An identity with a forbidden ending tone fails validation.
3. An identity with clashing avoided experiences fails validation.
4. Compilation (`compile_to_blueprint`) fails and aborts if validation errors are present.
**Answer**: Accepted.

---

## Design Result
Upgrade the `StoryIdentity` schema in `src/auteur/identity.py` to include a validation method running these rules. Update the CLI commands `validate` and `compile`/`seed` in `src/auteur/cli.py` to run these rules, output structural diagnostics on failure, and fail with exit code `1`.
