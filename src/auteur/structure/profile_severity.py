"""Severity policy for accepted Genre Profile resolution diagnostics."""

from auteur.genre_packs.models import AdherencePosture
from auteur.structure.diagnostics import DiagnosticSeverity


_CONTRACT_DIAGNOSTICS = {
    "profile.resolution_contract.missing_required_outcome",
    "profile.resolution_contract.rejected_outcome_present",
}
_ENDING_CONFLICT = "profile.resolution_contract.ending_tone_conflict"


def _coerce_posture(posture: AdherencePosture | str | None) -> AdherencePosture:
    if posture is None:
        return AdherencePosture.CONVENTIONAL
    if isinstance(posture, AdherencePosture):
        return posture
    try:
        return AdherencePosture(posture)
    except ValueError:
        return AdherencePosture.CONVENTIONAL


def severity_for_profile_diagnostic(
    posture: AdherencePosture | str | None,
    diagnostic_id: str,
) -> DiagnosticSeverity:
    """Return the approved effective severity for a profile diagnostic.

    Flexible, revisionist, and subversive remain distinct author choices but
    intentionally share severity behavior in this first policy slice.
    Unknown or missing posture values use the conventional legacy default.
    """
    effective_posture = _coerce_posture(posture)
    if effective_posture is AdherencePosture.DECONSTRUCTIVE:
        return DiagnosticSeverity.INFO
    if diagnostic_id in _CONTRACT_DIAGNOSTICS:
        if effective_posture is AdherencePosture.CONVENTIONAL:
            return DiagnosticSeverity.ERROR
        return DiagnosticSeverity.WARNING
    if diagnostic_id == _ENDING_CONFLICT:
        return DiagnosticSeverity.WARNING
    return DiagnosticSeverity.WARNING
