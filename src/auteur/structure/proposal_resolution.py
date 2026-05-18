"""Proposal resolution — load, resolve, and write proposal artifacts to disk."""

from __future__ import annotations

from pathlib import Path
from typing import Any
from datetime import datetime, timezone

import yaml

from auteur.structure.proposal_models import (
    ProposalOption,
    ProposalType,
    StructureProposal,
)



def load_resolved_rules(project_path: Path) -> set[str]:
    """Scan structure/proposals/ for YAML files with a non-empty selected_option_id.
    Return the set of source_rule values that have been resolved."""
    import yaml as _yaml

    proposals_dir = project_path / "structure" / "proposals"
    if not proposals_dir.is_dir():
        return set()

    resolved: set[str] = set()
    for proposal_file in sorted(proposals_dir.glob("*.yaml")):
        try:
            data = _yaml.safe_load(proposal_file.read_text(encoding="utf-8"))
        except Exception:
            continue
        if not isinstance(data, dict):
            continue
        selection = data.get("selection", {})
        if isinstance(selection, dict) and selection.get("selected_option_id"):
            source_rule = data.get("source_rule")
            if source_rule:
                resolved.add(source_rule)
    return resolved


def resolve_proposal(project_path: Path, proposal_id: str, option_id: str) -> int:
    """Load a proposal YAML, set the selected option, record a decision, and save."""
    import yaml as _yaml
    from datetime import datetime, timezone

    proposals_dir = project_path / "structure" / "proposals"
    proposal_path = proposals_dir / f"{proposal_id}.yaml"

    if not proposal_path.exists():
        print(f"Proposal not found: {proposal_path}", file=__import__("sys").stderr)
        return 1

    try:
        data = _yaml.safe_load(proposal_path.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"Failed to parse {proposal_path}: {exc}", file=__import__("sys").stderr)
        return 1

    if not isinstance(data, dict):
        print(f"Invalid proposal format: {proposal_path}", file=__import__("sys").stderr)
        return 1

    options = data.get("options", [])
    option_ids = [o.get("id") for o in options if isinstance(o, dict)]
    if option_id not in option_ids:
        print(
            f"Option '{option_id}' not found in proposal. "
            f"Available: {option_ids}",
            file=__import__("sys").stderr,
        )
        return 1

    data["selection"] = {
        "selected_option_id": option_id,
        "custom_data": {},
    }
    data["decision"] = {
        "selected_option_id": option_id,
        "custom_data": {},
        "status": "accepted",
        "author": None,
        "references": [],
        "accepted_at": datetime.now(timezone.utc).isoformat(),
    }

    # Apply data updates programmatically if defined in the selected option
    selected_option = None
    for opt in options:
        if isinstance(opt, dict) and opt.get("id") == option_id:
            selected_option = opt
            break

    if selected_option and isinstance(selected_option, dict) and selected_option.get("data"):
        opt_data = selected_option["data"]
        delta_type = opt_data.get("delta_type")
        if delta_type == "bible_delta":
            action = opt_data.get("action")
            if action == "update_carrier_state":
                bible_path = project_path / "bible.json"
                if not bible_path.exists():
                    print(f"Bible not found: {bible_path}", file=__import__("sys").stderr)
                    return 1
                try:
                    from auteur.bible import StoryBible
                    from auteur.structure.state import StoryBibleModel, CharacterState
                    import json
                    bible = StoryBible(bible_path)
                    
                    event_idx = opt_data.get("event_index")
                    char = opt_data.get("character")
                    field = opt_data.get("field")
                    before = opt_data.get("before")
                    after = opt_data.get("after")
                    
                    # Validate character field
                    if field not in CharacterState.model_fields:
                        raise ValueError(f"Invalid character state field: {field}")
                    
                    # Update event deltas
                    events = bible.data.get("events", [])
                    if event_idx is not None and event_idx < len(events):
                        event = events[event_idx]
                        deltas = event.setdefault("deltas", {})
                        changes = deltas.setdefault("character_state_changes", [])
                        
                        found = False
                        for c in changes:
                            if c.get("character") == char and c.get("field") == field:
                                c["before"] = before
                                c["after"] = after
                                found = True
                                break
                        if not found:
                            changes.append({
                                "character": char,
                                "field": field,
                                "before": before,
                                "after": after,
                            })
                            
                    # Update character registry active state
                    if field == "location":
                        bible.upsert_character(char, location=after)
                    elif field == "physical":
                        bible.upsert_character(char, physical=after)
                    elif field == "emotional":
                        bible.upsert_character(char, emotional=after)
                    else:
                        bible.upsert_character(char, **{field: after})
                        
                    # Validate against StoryBibleModel schema
                    StoryBibleModel.model_validate(bible.data)
                    bible.save()
                    print(f"Applied bible delta for character {char} on {field} successfully.")
                except Exception as exc:
                    print(f"Failed to apply bible delta: {exc}", file=__import__("sys").stderr)
                    return 1
        elif delta_type == "cartographer_outline":
            action = opt_data.get("action")
            if action == "insert_scene":
                outline_path = project_path / "cartographer_outline.yaml"
                if not outline_path.exists():
                    ch_idx = opt_data.get("chapter_index")
                    if ch_idx is not None:
                        outline_path = project_path / "chapters" / f"{ch_idx:02d}" / "outline.yaml"
                
                if not outline_path.exists():
                    print(f"Outline not found at {outline_path}", file=__import__("sys").stderr)
                    return 1
                try:
                    import yaml as _yaml
                    outline_content = outline_path.read_text(encoding="utf-8")
                    outline = _yaml.safe_load(outline_content)
                    
                    ch_idx = opt_data.get("chapter_index", 1)
                    scene_id = opt_data.get("scene_id")
                    pov_char = opt_data.get("pov_character")
                    loc = opt_data.get("location")
                    summary = opt_data.get("summary")
                    
                    new_scene = {
                        "scene_id": scene_id,
                        "pov_character": pov_char,
                        "location": loc,
                        "summary": summary,
                        "key_events": [],
                        "character_state_changes": [],
                        "arc_advancements": [],
                    }
                    
                    if isinstance(outline, dict) and "chapters" in outline:
                        found_ch = False
                        for chapter in outline["chapters"]:
                            if chapter.get("index") == ch_idx:
                                chapter.setdefault("scenes", []).append(new_scene)
                                found_ch = True
                                break
                        if not found_ch:
                            raise ValueError(f"Chapter index {ch_idx} not found in outline.")
                    else:
                        outline.setdefault("scenes", []).append(new_scene)
                        
                    from auteur.cartographer_outline import CartographerOutline
                    if isinstance(outline, dict) and "scenes" in outline:
                        CartographerOutline.model_validate(outline)
                        
                    outline_path.write_text(
                        _yaml.safe_dump(outline, sort_keys=False),
                        encoding="utf-8"
                    )
                    print(f"Applied scene insertion to {outline_path} successfully.")
                except Exception as exc:
                    print(f"Failed to apply outline update: {exc}", file=__import__("sys").stderr)
                    return 1

    proposal_path.write_text(
        _yaml.safe_dump(data, sort_keys=False),
        encoding="utf-8",
    )
    print(f"Resolved {proposal_id} with option '{option_id}'.")
    return 0


def write_audit_repair_proposals(
    project_path: Path,
    diagnostics: list[object],
) -> None:
    """Serialize Bible audit diagnostics into StructureProposal YAML files.

    Proposal generation is delegated to
    ``auteur.structure.proposal_generation.propose_repairs_from_audit_diagnostics``.
    This function handles I/O only.
    """
    from auteur.structure.proposal_generation import propose_repairs_from_audit_diagnostics

    proposals_dir = project_path / "structure" / "proposals"
    proposals_dir.mkdir(parents=True, exist_ok=True)

    existing_proposals = {p.stem for p in proposals_dir.glob("repair_*.yaml")}

    proposals = propose_repairs_from_audit_diagnostics(diagnostics)

    written = 0
    for proposal in proposals:
        if proposal.proposal_id in existing_proposals:
            continue
        proposal_path = proposals_dir / f"{proposal.proposal_id}.yaml"
        import yaml as _yaml
        proposal_path.write_text(
            _yaml.safe_dump(proposal.model_dump(mode="json"), sort_keys=False),
            encoding="utf-8",
        )
        written += 1

    print(f"Wrote {written} repair proposal(s) to {proposals_dir}")