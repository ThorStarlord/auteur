"""Adapters for real subsystem integration in the Decision Workspace.

Each adapter wraps one Auteur subsystem and exposes a stable query API
that the DecisionWorkspaceService consumes. Adapters are the only
integration points that import from their target subsystem directly.
"""
