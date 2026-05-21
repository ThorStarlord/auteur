# Unknowns Map

## 1. Knowns
Facts that are verified by code, documentation, or explicit user confirmation.

## 2. Unknowns
Explicitly missing information that is required to move forward safely.

## 3. Assumptions
Things we are treating as true but have not yet verified.

## 4. Risks
Potential failures, blockers, or high-impact negative outcomes.

## 5. Research Paths
Specific, time-boxed questions or actions to resolve the most critical unknowns/assumptions.

## 6. Stopping Rule
The condition that, when met, indicates research is complete enough to resume routing or orchestration.

Examples:
- **Weak**: "Stop when the unknowns are resolved."
- **Strong**: "Stop when the 3 missing files are found and the artifact handoff contract for Step 4 is confirmed as technically feasible."

## 7. Machine-readable routing

```yaml
# Routing metadata for dynamic orchestration and artifact handling
clarity_assessment: "high"  # valid values: "critical", "high", "medium", "low" — indicates overall clarity of the unknowns map
unknowns_count: 3           # number of distinct unknowns identified — drives triage priority and research effort
assumptions_count: 2        # number of distinct assumptions — indicates stability of current understanding
research_needed: false      # boolean: true if research paths are recommended, false if enough is known to proceed
```

These machine-readable fields enable orchestration systems to:
- **Triage dynamically**: Route artifacts based on clarity_assessment level (critical clarifications block handoff; high allows conditional proceeds)
- **Track scope**: Monitor unknowns_count and assumptions_count across iterations to show convergence
- **Signal readiness**: Use research_needed to determine if stopping rule is met and safe to resume downstream routing
- **Enable metrics**: Build dashboards of clarity trends and assumption validation rates across projects

Include this block in every unknowns-map artifact so routing systems can ingest metadata directly from the rendered markdown.
