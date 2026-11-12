"""Disposable spike for the Working Book Architecture design (2026-11-12). NOT production code.

Question: can a Book-scoped working artifact preserve the complete Book 24 function, support a
bounded revision and a consequence trace, expose a proportionate continuation packet, and accept a
counterfactual rejection without disturbing the Series architecture?

Usage: python probe_book24.py <repo_root> <output_dir>

Inputs are read read-only from the PR #555 commit with `git show`; nothing there is modified. The
probe writes probe-output.json to <output_dir>. It does not write any Studio or Series store.
"""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field

REPO = Path(sys.argv[1]).resolve()
OUT = Path(sys.argv[2]).resolve()
OUT.mkdir(parents=True, exist_ok=True)

PR555 = "fa85b7f1c2fbfdf8d5b8b35f6ce64c27bf438e04"
FN_PATH = "experiments/spring-ledger-working-architecture/cold-start/output/book-24-function.corrected-2.md"
W6_PATH = "experiments/spring-ledger-working-architecture/02-working-candidate-W6.json"
B24_PATH = "experiments/spring-ledger-working-architecture/cold-start/output/book-24-candidate.corrected-2.json"

Provenance = Literal["author_fixed", "derived", "agent_proposed", "hypothetical", "unresolved", "unlabelled"]
EdgeType = Literal["sets_up", "pays_off", "depends_on", "pressures", "contradicts", "transforms"]
CRAFT_MARK = "str_b24_capability_mark"


class Item(BaseModel):
    id: str
    section: int
    text: str
    tags: list[str] = Field(default_factory=list)
    provenance: Provenance
    refs: list[str] = Field(default_factory=list)
    external_refs: list[str] = Field(default_factory=list)
    reversal: str | None = None
    fields: dict[str, str] = Field(default_factory=dict)


class TypedEdge(BaseModel):
    source: str
    target: str
    type: EdgeType
    rationale: str


class WorkingBookArtifact(BaseModel):
    artifact_schema: str = "working-book-architecture/spike-v0"
    book_number: int
    title: str
    base_series_fingerprint: str
    items: list[Item]
    typed_edges: list[TypedEdge]


def git_text(path: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(REPO), "show", f"{PR555}:{path}"], capture_output=True, check=True
    )
    return result.stdout.decode("utf-8")


def digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()


ID_RE = re.compile(r"\b(?:th|eng|str|rx|inst|gn|alt|ph|et|l)_[a-z0-9_]+\b")
PARA_RE = re.compile(r"\bP(?:10|[1-9])\b")
EXT_RE = re.compile(r"01 §[0-9][0-9.]*")
TAG_RE = re.compile(r"\[((?:Agent|Derived|motive Agent)[^\]]*)\]")
SECTION_RE = re.compile(r"^## (\d+)\. (.+)$", re.M)
FIELD_RE = re.compile(r"^\*(Condition|Choice|Consequence|Changed state|New possibility):\*\s*(.*)$", re.M)
SECTION_DEFAULT = {10: "hypothetical", 11: "unresolved"}


def split_sections(markdown: str) -> dict[int, str]:
    matches = list(SECTION_RE.finditer(markdown))
    out: dict[int, str] = {}
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(markdown)
        out[int(match.group(1))] = markdown[match.end():end].strip()
    return out


def provenance_for(section: int, text: str) -> tuple[list[str], Provenance]:
    tags = [tag for tag in TAG_RE.findall(text)]
    has_agent = any("Agent" in tag for tag in tags)
    has_derived = any("Derived" in tag for tag in tags)
    if has_agent:
        return tags, "agent_proposed"
    if has_derived:
        return tags, "derived"
    if section in SECTION_DEFAULT:
        return tags, SECTION_DEFAULT[section]  # type: ignore[return-value]
    return tags, "unlabelled"


def make_item(section: int, ident: str, text: str, reversal: str | None = None, fields: dict[str, str] | None = None) -> Item:
    tags, provenance = provenance_for(section, text)
    return Item(
        id=ident,
        section=section,
        text=text,
        tags=tags,
        provenance=provenance,
        refs=sorted(set(ID_RE.findall(text)) | set(PARA_RE.findall(text))),
        external_refs=sorted(set(EXT_RE.findall(text))),
        reversal=reversal,
        fields=fields or {},
    )


def parse_engines(section: int, body: str) -> list[Item]:
    items: list[Item] = []
    for block_index, block in enumerate(re.split(r"\n\s*\n", body), start=1):
        lines = [line.rstrip() for line in block.splitlines() if line.strip()]
        if not lines or not lines[0].startswith("**"):
            continue
        header = lines[0].strip("*").rstrip(".")
        fields = {label.lower().replace(" ", "_"): value.strip() for label, value in FIELD_RE.findall(block)}
        items.append(make_item(section, f"s{section}_engine_{block_index:02d}", block.strip(), fields={"title": header, **fields}))
    return items


def parse_bullets_and_paragraphs(section: int, body: str, prefix: str) -> list[Item]:
    items: list[Item] = []
    counter = 0
    for block in re.split(r"\n\s*\n", body):
        lines = [line.rstrip() for line in block.splitlines() if line.strip()]
        if not lines:
            continue
        if lines[0].startswith("**") and any(line.startswith("- ") for line in lines[1:]) and not all(l.startswith("- ") for l in lines):
            head_lines = []
            bullets: list[list[str]] = []
            for line in lines:
                if line.startswith("- "):
                    bullets.append([line[2:]])
                elif bullets:
                    bullets[-1].append(line)
                else:
                    head_lines.append(line)
            if head_lines:
                counter += 1
                items.append(make_item(section, f"{prefix}{counter:02d}", " ".join(head_lines)))
            for bullet in bullets:
                counter += 1
                items.append(make_item(section, f"{prefix}{counter:02d}", " ".join(bullet)))
            continue
        if all(line.startswith("- ") for line in lines):
            bullets = []
            for line in lines:
                if line.startswith("- "):
                    bullets.append([line[2:]])
                else:
                    bullets[-1].append(line)
            for bullet in bullets:
                counter += 1
                text = " ".join(bullet)
                reversal = None
                items.append(make_item(section, f"{prefix}{counter:02d}", text, reversal=reversal))
            continue
        if all(re.match(r"^\d+\. ", line) for line in lines[:1]):
            numbered: list[list[str]] = []
            for line in lines:
                if re.match(r"^\d+\. ", line):
                    numbered.append([re.sub(r"^\d+\. ", "", line)])
                else:
                    numbered[-1].append(line)
            for entry in numbered:
                counter += 1
                items.append(make_item(section, f"{prefix}{counter:02d}", " ".join(entry)))
            continue
        counter += 1
        items.append(make_item(section, f"{prefix}{counter:02d}", " ".join(lines)))
    return items


def parse_assumptions(section: int, body: str) -> list[Item]:
    items: list[Item] = []
    for line in body.splitlines():
        match = re.match(r"^- \*\*(P\d+) \[(\w+)\]\.\*\* (.*)$", line.strip())
        if not match:
            continue
        ident, tag, rest = match.groups()
        text, _, reversal = rest.partition("Reversal:")
        item = make_item(section, ident, text.strip(), reversal=reversal.strip() or None)
        # The bracket tag sits in the bullet header, outside the text that make_item scans.
        item.tags = [f"[{tag}]"]
        item.provenance = "agent_proposed" if tag == "Agent" else "derived"
        item.refs = sorted(set(ID_RE.findall(rest)) | set(PARA_RE.findall(rest)))
        item.external_refs = sorted(set(EXT_RE.findall(rest)))
        items.append(item)
    return items


def parse_section(section: int, body: str) -> list[Item]:
    if section == 3:
        return parse_engines(section, body)
    if section == 9:
        return parse_assumptions(section, body)
    if section == 1:
        items = []
        for label, text in re.findall(r"\*\*([^*]+)\*\*\s*(.*?)(?=\n\n|\Z)", body, re.S):
            items.append(make_item(1, f"s1_{re.sub(r'[^a-z]+', '_', label.lower()).strip('_')}", f"{label} {text.strip()}"))
        return items
    prefix = {2: "s2_", 4: "s4_", 5: "s5_", 6: "s6_", 7: "s7_", 8: "s8_", 10: "s10_", 11: "s11_"}[section]
    return parse_bullets_and_paragraphs(section, body, prefix)


def build_artifact(markdown: str, base_fingerprint: str, node_titles: dict[str, str]) -> WorkingBookArtifact:
    sections = split_sections(markdown)
    items: list[Item] = []
    for number in sorted(sections):
        items.extend(parse_section(number, sections[number]))
    typed_edges = [
        TypedEdge(source=CRAFT_MARK, target="th_hands_and_draw", type="pressures",
                  rationale="Bears on who can return labour; does not change who is counted for draw (sec 7.2)."),
        TypedEdge(source=CRAFT_MARK, target="inst_lineage_crews", type="pressures",
                  rationale="Meets the Right's training condition for one review cycle (sec 6.1, P6)."),
        TypedEdge(source=CRAFT_MARK, target="str_long_return", type="sets_up",
                  rationale="A public capability record any finale mechanism may draw on (sec 8, enabled)."),
        TypedEdge(source="str_b24_uncounted_crew", target="th_hands_and_draw", type="pressures",
                  rationale="Uncounted labour cannot restore hand-light draw under the conversion (sec 3, sec 7.3)."),
        TypedEdge(source="str_b24_uncounted_crew", target="eng_source", type="pressures",
                  rationale="Return labour shows on the Balance Stones in aggregate only (P3)."),
        TypedEdge(source="str_b24_uncounted_crew", target="th_maintenance", type="transforms",
                  rationale="The cohort gives uncounted return labour under lineage instruction (sec 3)."),
        TypedEdge(source="eng_old_hand", target="str_b24_uncounted_crew", type="transforms",
                  rationale="'Nothing counted' heard as 'nothing owed' drives the refusal of the tally (P2)."),
        TypedEdge(source="inst_reading_hall", target="str_b24_uncounted_crew", type="pressures",
                  rationale="Declines to attribute Balance Stones readings to named hands (P7)."),
    ]
    return WorkingBookArtifact(
        book_number=24,
        title="The Uncounted Crew",
        base_series_fingerprint=base_fingerprint,
        items=items,
        typed_edges=typed_edges,
    )


def main() -> None:
    fn_markdown = git_text(FN_PATH)
    w6 = json.loads(git_text(W6_PATH))
    b24 = json.loads(git_text(B24_PATH))
    base_fingerprint = digest({"nodes": sorted(n["id"] for n in w6["nodes"]), "links": sorted(l["id"] for l in w6["links"])})
    node_titles = {n["id"]: n["title"] for n in b24["nodes"]}
    node_summaries = {n["id"]: n["summary"] for n in b24["nodes"]}
    resolvable = (
        {n["id"] for n in b24["nodes"]}
        | {l["id"] for l in b24["links"]}
        | {e["id"] for e in b24["emotion_targets"]}
        | {p["id"] for p in b24["phases"]}
    )

    artifact = build_artifact(fn_markdown, base_fingerprint, node_titles)
    dumped = artifact.model_dump_json()
    restored = WorkingBookArtifact.model_validate_json(dumped)
    round_trip_ok = restored == artifact

    # --- Demonstration A: preservation -------------------------------------------------------
    sections = split_sections(fn_markdown)
    section_count = len(sections)
    per_section = {}
    for number in sorted(sections):
        section_items = [item for item in artifact.items if item.section == number]
        source_body = re.sub(r"\[[^\]]*\]", "", sections[number])
        source_nonspace = re.sub(r"[\s*\-_]|\d+\.", "", source_body)
        captured_nonspace = re.sub(r"[\s*\-_]|\d+\.", "", "".join(item.text + (item.reversal or "") for item in section_items))
        per_section[number] = {
            "items": len(section_items),
            "provenance": sorted({item.provenance for item in section_items}),
            "unlabelled": [item.id for item in section_items if item.provenance == "unlabelled"],
            # Verbatim capture: every source block became an item. It measures partition completeness,
            # not structured fidelity, so it is capped at 1.0 and reported as a ceiling only.
            "verbatim_capture_ratio": round(min(1.0, len(captured_nonspace) / max(1, len(source_nonspace))), 3),
        }
    all_refs = [ref for item in artifact.items for ref in item.refs]
    unresolved = sorted({ref for ref in all_refs if ref not in resolvable and not re.fullmatch(r"P\d+", ref)})
    provenance_counts: dict[str, int] = {}
    for item in artifact.items:
        provenance_counts[item.provenance] = provenance_counts.get(item.provenance, 0) + 1
    external = sorted({ref for item in artifact.items for ref in item.external_refs})
    preservation = {
        "sections_present": section_count,
        "items_total": len(artifact.items),
        "structured_engine_blocks": sum(1 for item in artifact.items if item.section == 3),
        "assumptions_with_reversal": sum(1 for item in artifact.items if item.id.startswith("P") and item.reversal),
        "assumptions": sum(1 for item in artifact.items if re.fullmatch(r"P\d+", item.id)),
        "typed_edges": len(artifact.typed_edges),
        "typed_edge_targets_resolve": all(edge.target in resolvable and edge.source in resolvable | {CRAFT_MARK} for edge in artifact.typed_edges),
        "provenance_counts": provenance_counts,
        "unlabelled_items": [item.id for item in artifact.items if item.provenance == "unlabelled"],
        "unresolved_refs": unresolved,
        "external_doc_refs": external,
        "per_section": per_section,
        "round_trip_equal": round_trip_ok,
        "source_chars": len(fn_markdown),
        "artifact_json_chars": len(dumped),
    }

    # --- Demonstration B: local revision consequence trace -----------------------------------
    # Lexical match on the mark's own terms. A bare "capability" would also match unrelated phrases.
    mark_pattern = re.compile(r"craft-mark|craft mark|capability record|capability mark", re.I)
    book_affected = [
        item.id for item in artifact.items
        if CRAFT_MARK in item.refs or "P5" in item.refs or "P6" in item.refs or mark_pattern.search(item.text)
    ]
    link_edges = [(l["source"], l["target"], l["id"]) for l in b24["links"]] + [(l["source"], l["target"], l["id"]) for l in w6["links"]]
    adjacency: dict[str, list[str]] = {}
    for source, target, _ in link_edges:
        adjacency.setdefault(source, []).append(target)
    typed_adjacency: dict[str, list[str]] = {}
    for edge in artifact.typed_edges:
        typed_adjacency.setdefault(edge.source, []).append(edge.target)

    def reach(start: str, graph: dict[str, list[str]]) -> set[str]:
        seen: set[str] = set()
        frontier = [start]
        while frontier:
            current = frontier.pop()
            for nxt in graph.get(current, []):
                if nxt not in seen:
                    seen.add(nxt)
                    frontier.append(nxt)
        return seen

    typed_reach = reach(CRAFT_MARK, typed_adjacency)
    series_reach = reach(CRAFT_MARK, adjacency)
    finale_alternatives = {"alt_a_reciprocal", "alt_b_allotted", "alt_c_ratified_trigger"}
    author_decisions = sorted({ext for item in artifact.items if item.id in book_affected for ext in item.external_refs})
    unaffected_items = [item.id for item in artifact.items if item.id not in book_affected]
    revision_trace = {
        "changed_element": CRAFT_MARK,
        "book_items_to_inspect": book_affected,
        "book_items_to_inspect_count": len(book_affected),
        "typed_direct_targets": sorted(typed_adjacency.get(CRAFT_MARK, [])),
        "typed_reach_targets": sorted(typed_reach),
        "series_link_reach_count": len(series_reach),
        "series_link_reach_includes_finale_alternatives": sorted(series_reach & finale_alternatives),
        "series_nodes_reachable_by_links": sorted(series_reach & set(node_titles)),
        "author_reserved_references_in_affected_items": author_decisions,
        "unaffected_book_items_count": len(unaffected_items),
    }

    # --- Demonstration C: continuation packet for a Book 25 agent ----------------------------
    exports = [item for item in artifact.items if item.section in (7, 8) and "Enabled" not in item.text]
    provisional = [item for item in artifact.items if re.fullmatch(r"P\d+", item.id)]
    open_items = [item for item in artifact.items if item.section == 11]
    constraint_ids = sorted({edge.target for edge in artifact.typed_edges} | finale_alternatives | {"th_hands_and_draw"})
    constraints = [{"id": ident, "summary": node_summaries.get(ident) or next((n["summary"] for n in w6["nodes"] if n["id"] == ident), "")} for ident in constraint_ids]
    packet = {
        "identity": {"book": 24, "title": artifact.title, "question": next(i.text for i in artifact.items if i.id == "s1_question")},
        "exported_pressures_and_consequences": [{"id": i.id, "text": i.text} for i in exports],
        "provisional_assumptions": [{"id": i.id, "text": i.text, "reversal": i.reversal} for i in provisional],
        "open_questions_and_author_decisions": [{"id": i.id, "text": i.text} for i in open_items],
        "series_constraints": constraints,
        "source_identity": {"base_series_fingerprint": artifact.base_series_fingerprint,
                            "artifact_content_sha256": digest(artifact.model_dump(mode="json"))},
    }
    packet_json = json.dumps(packet, ensure_ascii=False)
    continuation = {
        "packet_chars": len(packet_json),
        "full_book_artifact_chars": len(dumped),
        "full_series_candidate_chars": len(json.dumps(b24, ensure_ascii=False)),
        "packet_fraction_of_book_artifact": round(len(packet_json) / len(dumped), 3),
        "packet_fraction_of_series_candidate": round(len(packet_json) / len(json.dumps(b24, ensure_ascii=False)), 3),
        "constraint_ids": constraint_ids,
        "exported_item_ids": [i.id for i in exports],
    }

    # --- Demonstration D: counterfactual rejection of the craft-mark --------------------------
    surviving = [item for item in artifact.items if CRAFT_MARK not in item.refs and item.id not in book_affected]
    dangling = [item.id for item in artifact.items if item.id in book_affected]
    kept_edges = [edge for edge in artifact.typed_edges if CRAFT_MARK not in (edge.source, edge.target)]
    # By construction, not measured: Book artifacts reference Series nodes and never write them.
    # Comparing a value with itself would be a tautology, so the report labels the property instead.
    counterfactual = {
        "rejected_element": CRAFT_MARK,
        "series_unchanged_by_construction": True,
        "items_needing_revision_after_rejection": dangling,
        "items_still_valid_without_revision": len(surviving),
        "typed_edges_surviving": len(kept_edges),
        "typed_edges_removed": len(artifact.typed_edges) - len(kept_edges),
        "crew_items_intact": sorted(i.id for i in surviving if "crew" in i.text.lower())[:12],
    }

    # --- Authority probe: can an agent response carry author_declared provenance? -------------
    authority_probe: dict[str, object] = {}
    try:
        sys.path.insert(0, str(REPO / "src"))
        from auteur.beginner.studio_architecture import ArchitectureCandidate  # type: ignore

        candidate = json.loads(json.dumps(b24))
        candidate["emotion_targets"][0]["provenance"] = "author_declared"
        ArchitectureCandidate.model_validate(candidate, context={"new_host_agent_response": True})
        authority_probe = {"author_declared_accepted_from_agent_response": True}
    except Exception as error:  # noqa: BLE001 - the probe records the outcome either way
        authority_probe = {"author_declared_accepted_from_agent_response": False, "error": str(error)[:200]}

    packet_components = {key: len(json.dumps(value, ensure_ascii=False)) for key, value in packet.items()}
    continuation["packet_components_chars"] = packet_components
    # Can the packet alone support the craft-mark revision? Count the revision targets it omits.
    packet_item_ids = (
        {i["id"] for i in packet["exported_pressures_and_consequences"]}
        | {i["id"] for i in packet["provisional_assumptions"]}
        | {i["id"] for i in packet["open_questions_and_author_decisions"]}
    )
    continuation["revision_targets_total"] = len(book_affected)
    continuation["revision_targets_missing_from_packet"] = [i for i in book_affected if i not in packet_item_ids]
    report = {
        "spike": "working-book-architecture-design-20261112",
        "production_code": False,
        "book24_source": {"commit": PR555, "function_path": FN_PATH, "candidate_path": B24_PATH},
        "demonstration_a_preservation": preservation,
        "demonstration_b_revision_trace": revision_trace,
        "demonstration_c_continuation": continuation,
        "demonstration_d_counterfactual": counterfactual,
        "authority_probe": authority_probe,
    }
    (OUT / "probe-output.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({k: v for k, v in report.items() if k != "demonstration_a_preservation"}, indent=2, ensure_ascii=False)[:6000])
    print("preservation summary:", json.dumps({k: preservation[k] for k in (
        "sections_present", "items_total", "assumptions", "assumptions_with_reversal", "typed_edges",
        "typed_edge_targets_resolve", "round_trip_equal", "source_chars", "artifact_json_chars")}))
    print("unlabelled:", preservation["unlabelled_items"])
    print("unresolved refs:", preservation["unresolved_refs"])
    print("external refs:", preservation["external_doc_refs"])
    print("per-section verbatim capture ratio:", {k: v["verbatim_capture_ratio"] for k, v in per_section.items()})


if __name__ == "__main__":
    main()
