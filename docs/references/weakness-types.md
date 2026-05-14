# Weakness Types

When identifying the Weakest Boundary, check these common types:

1. Vocabulary Drift: Terms in docs do not match code or directory shape.
2. Contract Mismatch: A file or command claims one contract while enforcing another.
3. Ghost Features: Documentation references functionality with no implementation.
4. Safety Gaps: Autonomous workflows lack explicit human-approval gates where needed.
5. Implicit Dependencies: Skills or scripts rely on paths/contracts not explicitly defined.
6. Zero Validation: Critical boundaries are not enforced by deterministic checks.
7. Orphaned Examples: Examples are outdated or violate current templates/contracts.
