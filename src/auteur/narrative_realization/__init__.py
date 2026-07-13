"""Layer 3: Narrative Realization module.

Converts chapter intentions into concrete dramatic units (scenes) with full
structural and semantic detail.

Architecture:
- schema/: Scene models preserving 5 semantic boundaries
- loader/: YAML serialization for persistence
- validator/: Reference, knowledge, temporal, and orchestration validators
- orchestrator/: Scene builders and workflow orchestration
- cli_realization.py: CLI integration
"""
