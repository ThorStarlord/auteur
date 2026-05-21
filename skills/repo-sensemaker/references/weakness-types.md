# Weakness Types in Repositories

When identifying the **Weakest Boundary**, look for these common types:

1. **Vocabulary Drift**: Terms used in the README don't match the code or directory structure.
2. **Contract Mismatch**: Files claim to be one format (e.g., `.yaml`) but are actually another (e.g., Markdown).
3. **Ghost Features**: Functionality mentioned in documentation that has no corresponding implementation.
4. **Safety Gaps**: Autonomous workflows that lack mandatory human-approval gates.
5. **Implicit Dependencies**: Skills or scripts that depend on files or paths not explicitly defined or validated.
6. **Zero Validation**: Core logic or structure that has no automated check (e.g., no `validate-repo.py` or equivalent).
7. **Orphaned Examples**: Examples that are outdated or don't follow current templates.
