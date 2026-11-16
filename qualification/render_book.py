"""Render a Working Book artifact readably for blind comparison."""
from __future__ import annotations

import json
import sys
from pathlib import Path


def main() -> int:
    source = Path(sys.argv[1]).resolve()
    out = Path(sys.argv[2]).resolve()
    d = json.loads(source.read_text(encoding="utf-8"))
    lines = [f"# Book {d.get('book_number')}: {d.get('title')}", ""]

    fn = d.get("function", {})
    lines += ["## What this Book is for", "", f"{fn.get('text')}", ""]
    lines += [f"- Question: {fn.get('question')}", f"- Pressure: {fn.get('pressure')}", ""]

    if d.get("inherited"):
        lines += ["## Inherited from the Series", ""]
        for item in d["inherited"]:
            lines.append(f"- {item.get('text')}")
        lines.append("")

    lines += ["## Engines", ""]
    for engine in d.get("engines", []):
        lines.append(f"- **{engine.get('id')}**: {engine.get('text')}")
        for key in ("condition", "consequence", "changed_state"):
            if engine.get(key):
                lines.append(f"  - {key.replace('_', ' ')}: {engine[key]}")
    lines.append("")

    if d.get("agents"):
        lines += ["## Agents and institutions", ""]
        for item in d["agents"]:
            lines.append(f"- {item.get('text')}")
        lines.append("")

    choice = d.get("choice", {})
    lines += ["## The choice", "", f"{choice.get('text')}", ""]
    for option in choice.get("options", []):
        marker = " (chosen)" if option.get("id") == choice.get("chosen_option_id") else ""
        lines.append(f"- {option.get('text')}{marker}")
    lines.append("")
    for cost in choice.get("costs_kept_visible", []):
        lines.append(f"- Cost kept visible: {cost.get('text')}")
    transformation = choice.get("transformation")
    if transformation:
        lines.append(f"- Transformation: {transformation.get('text')}")
    lines.append("")

    lines += ["## What this Book resolves", ""]
    for item in d.get("local_resolution", []):
        lines.append(f"- {item.get('text')}")
    lines.append("")

    lines += ["## Consequences for the Series", ""]
    for item in d.get("series_consequences", []):
        lines.append(f"- ({item.get('kind')}) {item.get('text')}")
    lines.append("")

    lines += ["## What later Books may do", ""]
    for item in d.get("later_possibilities", []):
        lines.append(f"- ({item.get('kind')}) {item.get('text')}")
    lines.append("")

    if d.get("assumptions"):
        lines += ["## Working assumptions", ""]
        for item in d["assumptions"]:
            line = f"- {item.get('text')}"
            if item.get("reversal"):
                line += f" (reverse if: {item['reversal']})"
            lines.append(line)
        lines.append("")

    if d.get("alternatives"):
        lines += ["## Alternatives considered", ""]
        for item in d["alternatives"]:
            responsibility = item.get("responsibility", "in_service")
            lines.append(f"- {item.get('title')} [{responsibility}]: {item.get('rationale')}")
        lines.append("")

    if d.get("unresolved"):
        lines += ["## What the source cannot establish", ""]
        for item in d["unresolved"]:
            lines.append(f"- {item.get('text')}")
        lines.append("")

    if d.get("open_author_decisions"):
        lines += ["## What only the author can decide", ""]
        for item in d["open_author_decisions"]:
            lines.append(f"- {item.get('text')}")
        lines.append("")

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"out": str(out), "chars": len("\n".join(lines))}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
