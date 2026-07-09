from __future__ import annotations

from pathlib import Path

from auteur.critic.slop import SLOP_PHRASES
from auteur.editing.models import EditFinding, EditLocation, PatchProposal


AIISM_REPLACEMENTS: dict[str, str] = {
    "stood as a testament to": "still carried",
}


def _scan_phrases() -> list[str]:
    phrases = set(SLOP_PHRASES)
    phrases.update(AIISM_REPLACEMENTS)
    return sorted(phrases, key=len, reverse=True)


def run_aiism_pass(text: str, *, source_file: Path | str) -> tuple[list[EditFinding], list[PatchProposal]]:
    findings: list[EditFinding] = []
    patches: list[PatchProposal] = []
    source = str(source_file).replace("\\", "/")

    finding_index = 1
    patch_index = 1
    for line_number, line in enumerate(text.splitlines(), start=1):
        lowered = line.lower()
        matched_spans: list[tuple[int, int]] = []
        for phrase in _scan_phrases():
            start = lowered.find(phrase.lower())
            if start < 0:
                continue
            end = start + len(phrase)
            if any(start < existing_end and end > existing_start for existing_start, existing_end in matched_spans):
                continue
            matched_spans.append((start, end))
            original_text = line[start:end]
            finding_id = f"finding_{finding_index:03d}"
            finding_index += 1
            location = EditLocation(file=source, start_line=line_number, end_line=line_number)
            findings.append(
                EditFinding(
                    id=finding_id,
                    pass_name="aiisms",
                    issue_type="ai_ism",
                    severity="warning",
                    location=location,
                    evidence=phrase,
                    rationale="Stock phrasing was detected; deterministic replacements are suggestions, not final prose quality.",
                )
            )
            replacement = AIISM_REPLACEMENTS.get(phrase)
            if replacement is not None:
                patches.append(
                    PatchProposal(
                        id=f"patch_{patch_index:03d}",
                        finding_id=finding_id,
                        patch_type="replace_text",
                        location=location,
                        original=original_text,
                        replacement=replacement,
                        confidence=0.72,
                        status="proposed",
                    )
                )
                patch_index += 1
    return findings, patches
