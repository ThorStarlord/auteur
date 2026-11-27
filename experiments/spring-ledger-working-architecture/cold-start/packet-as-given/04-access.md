# Access to the working architecture

## The working architecture

It is in a disposable Studio project. You may read it. Your own proposals, if you make any, go into the same project.

- Repository source (add it to `PYTHONPATH`): `H:/GithubRepositories/auteur-consolidated/src`
- Project root: `C:/Users/Admin/AppData/Local/Temp/claude/e91f3203f308aeba/7ded406a-3eb4-467b-8607-1f94688c650e/scratchpad/consolidated/proj`
- Canvas id: `spring-ledger-consolidated`

To read the working state, run:

    PYTHONPATH=H:/GithubRepositories/auteur-consolidated/src PYTHONUTF8=1 python -m auteur.beginner.studio_architecture --project "C:/Users/Admin/AppData/Local/Temp/claude/e91f3203f308aeba/7ded406a-3eb4-467b-8607-1f94688c650e/scratchpad/consolidated/proj" --canvas spring-ledger-consolidated resume

The JSON it prints contains everything in the working state: the story vision, the current candidate under `architecture`, the open questions, the provisional concepts, and the author's intentions. Read it before you write anything.

## Output

Write your deliverables to:

    C:/Users/Admin/AppData/Local/Temp/claude/e91f3203f308aeba/7ded406a-3eb4-467b-8607-1f94688c650e/scratchpad/consolidated/agent-output/

Create the folder if it does not exist. Write only there. Do not write into the repository.

## Boundary

Read only the files in this packet and the working state above. Do not open any other file or folder on this machine, including the repository's experiment folders, pull request history, review reports or evidence. The project's initial state is preserved at `consolidated/snapshot-before/`. Do not open it.
