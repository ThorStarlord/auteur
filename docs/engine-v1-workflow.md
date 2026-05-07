# Engine v1 Workflow

Engine v1 generates one chapter at a time from a project directory.

## 1. Initialize A Project

```powershell
auteur init .\tmp\shattered_crown --from .\examples\sample_blueprint.yaml
```

This creates:

```text
tmp/shattered_crown/
  blueprint.yaml
  bible.json
  chapters/
```

`blueprint.yaml` is the story specification. `bible.json` is the live story state.

## 2. Inspect The Plan Prompt

```powershell
auteur plan .\examples\sample_blueprint.yaml 1
```

This renders the Cartographer prompt and exits. It does not call an LLM and does not create project artifacts.

## 3. Draft A Chapter

```powershell
auteur draft .\tmp\shattered_crown 1 --provider anthropic --max-iterations 3
```

The pipeline does the following:

1. Build a `PlanningCall` from the blueprint.
2. Render the Cartographer prompt.
3. Call the selected LLM provider for an outline.
4. Parse the outline YAML and write `outline.yaml`.
5. If `conflict_report` is present, stop with exit code `3`.
6. Ask Bard to write `draft_v1.md`.
7. Run all five critics in parallel.
8. Write `validation_v1.json`.
9. If the validation has no error findings, write `final.md` and update `bible.json`.
10. If validation has errors, feed the prior draft and findings back to Bard for the next version.
11. Stop when a version passes or `--max-iterations` is exhausted.

Warnings do not block acceptance. Error findings do.

## Exit Codes

`0`: accepted and `final.md` was written.

`1`: local setup/input failure, such as missing project files or malformed retry artifacts.

`2`: iteration cap exhausted; drafts and validation reports remain on disk.

`3`: Cartographer emitted a `conflict_report`; outline is written, but no draft is produced.

Unhandled provider/API exceptions currently propagate to the caller.

## Accept Flow

```powershell
auteur accept .\tmp\shattered_crown 1
```

This promotes the latest `draft_v*.md` to `final.md`, then records a manual accept event in `bible.json`. If `outline.yaml` contains an integer `estimated_chapter_tension`, that tension is also recorded.

Use this when a human edits a rejected draft and wants to accept it.

## Retry Flow

```powershell
auteur retry .\tmp\shattered_crown 1 --max-iterations 2
```

Retry requires:

- `outline.yaml`
- at least one `draft_v*.md`
- matching `validation_vN.json` for the latest draft version

It loads the latest draft and validation findings, then continues with the next version number. For example, if `draft_v3.md` is latest, retry writes `draft_v4.md` and `validation_v4.json`.

Retry does not re-run Cartographer. It uses the existing outline.

## Manual Real-LLM Smoke

```powershell
python .\scripts\smoke_real_llm.py
```

This runs chapter 1 of the sample blueprint against Anthropic and prints token usage. It requires `ANTHROPIC_API_KEY` and spends real tokens, so it is intentionally not part of the pytest suite.

