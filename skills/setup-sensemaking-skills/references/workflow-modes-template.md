# Sensemaking Workflow Modes

| Mode | Allowed | Description |
| :--- | :--- | :--- |
| `plan_only` | Yes | Generate the plan only. No execution. |
| `prompt_chain` | Yes | Generate copy/paste prompts for specialized skills. |
| `guided_execution` | [Yes/No] | Step-by-step execution with mandatory approval gates. |
| `autonomous_execution` | [Yes/No] | Full pipeline execution (Requires explicit opt-in). |

## High-Risk Operations
- Commits to `main` are [PROHIBITED | PERMITTED WITH OPT-IN].
- PR creation is [PROHIBITED | PERMITTED WITH OPT-IN].
- Documentation deletion is [PROHIBITED | PERMITTED WITH OPT-IN].
