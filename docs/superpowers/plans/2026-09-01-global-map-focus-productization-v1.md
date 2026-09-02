# Plan: Global Map / Focus Productization Pilot V1

## Goal

Turn the bounded whole-story vertical slice into one normal-project author workflow: rebuildable Global Map composition, a small read-only Focus projection, and a revision-impact handoff that preserves accepted authority.

## Architecture

Keep `SeriesVerticalSliceService` as the authority boundary for accepted artifacts, provenance, derivation, and impact. Add only a thin productization façade and presentation model. Global Map and Focus remain derived artifacts; Focus never accepts or rewrites story material. Existing impact/reconciliation artifacts remain the source of revision status.

## Tech Stack

Python 3.11, Pydantic 2, YAML-backed `ArtifactStore`, argparse CLI, pytest.

## Implementation Steps

1. Add failing contract tests for a normal-project productization service: build/rebuild a Global Map, project a Focus without a caller seed, expose provenance and why-now explanations, and return revision-impact/reconciliation handoff data without mutation.
2. Implement the thin productization service and read-only Focus report models by composing existing Global Map, Focus selection, `realization_impact`, and `series_impact` behavior.
3. Add deterministic Markdown/text formatting and the `auteur series focus` author-facing command, retaining `--detail` for provenance inspection.
4. Add failing and passing tests for stale-map handling, deleted-map rebuild, accepted-authority preservation, and CLI output.
5. Add the bounded dogfood protocol and friction-log artifact with the three pilot tasks, behavioral measures, stopping rule, and explicit pending author-run status.
6. Run focused tests, lint, and the repository qualification checks from the exact candidate SHA; report evidence categories separately.

## Non-goals

No graph UI, open-world inference, automatic extraction, generalized commitment lifecycle, automatic downstream rewrites, multi-user editing, or new reconciliation manager.
