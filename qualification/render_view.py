"""Render an ArchitectureCandidate readably, without implementation vocabulary.

Used so an independent evaluator sees the creative proposal rather than JSON.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path


def main() -> int:
    source = Path(sys.argv[1]).resolve()
    out = Path(sys.argv[2]).resolve()
    data = json.loads(source.read_text(encoding="utf-8"))
    lines = ["# Working narrative architecture (an AI proposal, not accepted story)", ""]
    lines += ["## Summary", "", data.get("summary", ""), ""]

    lines += ["## Mechanisms and components", ""]
    for node in data.get("nodes", []):
        lines.append(f"- **{node.get('title')}** ({node.get('category')}): {node.get('summary')}")
    lines.append("")

    lines += ["## How the components connect", ""]
    titles = {node["id"]: node.get("title", node["id"]) for node in data.get("nodes", [])}
    for link in data.get("links", []):
        lines.append(
            f"- {titles.get(link.get('source'), link.get('source'))} -> "
            f"{titles.get(link.get('target'), link.get('target'))}: {link.get('function')}"
        )
    lines.append("")

    lines += ["## Phases across the horizon", ""]
    for phase in sorted(data.get("phases", []), key=lambda p: p.get("order", 0)):
        lines.append(
            f"{phase.get('order')}. **{phase.get('title')}** — {phase.get('narrative_function')}"
        )
    lines.append("")

    targets = data.get("emotion_targets", [])
    if targets:
        lines += ["## Intended emotional progression", ""]
        for target in targets:
            lines.append(
                f"- {target.get('emotion')} ({target.get('role')}): "
                f"{target.get('intended_effect')} — elicited by {target.get('eliciting_condition')}"
            )
        lines.append("")

    opportunities = data.get("opportunities", [])
    if opportunities:
        lines += ["## Possibilities the agent noticed but did not adopt", ""]
        for item in opportunities:
            lines.append(
                f"- {item.get('title')} ({item.get('relationship', 'unclear')}): "
                f"{item.get('why_it_matters')}"
            )
        lines.append("")

    questions = data.get("open_questions", [])
    if questions:
        lines += ["## Open questions left to the author", ""]
        for question in questions:
            lines.append(f"- {question}")
        lines.append("")

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({
        "out": str(out),
        "nodes": len(data.get("nodes", [])),
        "phases": len(data.get("phases", [])),
        "open_questions": len(questions),
        "chars": len("\n".join(lines)),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
