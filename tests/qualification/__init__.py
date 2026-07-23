"""Canonical real-state acceptance qualification harness for Auteur v0.8.0.

Each scenario builds a deterministic fixture project, exercises a complete
decision lifecycle path via subprocess CLI calls, and verifies exact
exit codes and JSON output. No canonical or accepted-state mutation is
permitted during read-only scenarios.
"""
