"""LLM bridge for the generative path — refines archetypal structural forces
and threads against the author's actual premise, characters, and intent.

The template-based generator produces generic archetypal patterns. This module
takes those archetypes and uses an LLM to sharpen them into story-specific
forces, threads, and proposals that reference the actual characters, setting,
and thematic concerns of the blueprint.
"""
from __future__ import annotations

import yaml

from auteur.blueprint import StoryBlueprint, ThreadType
from auteur.llm import LLMClient, LLMRequest
from auteur.structure.generator import (
    GenerationProposal,
    GeneratedThread,
    StructuralForcesSynthesis,
    generate_main_thread,
    generate_subordinate_threads,
    synthesize_structural_forces,
)

_REFINEMENT_SYSTEM_PROMPT = """\
You are a story structure refiner inside the Auteur narrative engineering pipeline.
Your job is to take archetypal structural forces (want, resistance, conflict, stakes,
change) and thread templates and sharpen them against the author's actual premise,
characters, and world.

# Rules
1. Preserve the structural shape — do not change the number of threads or the
   function of the main thread.
2. Replace generic language ("the protagonist", "the threat", "someone") with
   specific character names, setting details, and story-specific stakes drawn
   from the author_intent, characters list, and theme.
3. Keep each thread's want, function, and carriers intact — only rewrite the
   rationale and the structural forces text.
4. The output must be valid YAML matching the schema below.
5. Do not add new threads or remove existing ones.
6. If the author_intent or characters provide no premise detail to sharpen
   against, leave the archetypal text as-is rather than inventing detail.

# Output schema (YAML)
Return exactly one YAML document:

structural_forces:
  want: str
  resistance: str
  conflict: str
  stakes: str
  change: str
main_thread:
  name: str
  thread_type: "main_plot"
  want: str
  function: str
  carriers: list[str]
  confidence: float
  rationale: str
subordinate_threads:
  - name: str
    thread_type: str
    want: str
    function: str
    carriers: list[str]
    confidence: float
    rationale: str
constraints_honored: list[str]

Do not wrap the YAML in markdown fences. Do not include commentary.
"""


def build_refinement_prompt(
    blueprint: StoryBlueprint,
    archetypal_forces: StructuralForcesSynthesis | None = None,
) -> str:
    """Build the user message for the LLM refinement call."""
    if archetypal_forces is None:
        archetypal_forces = synthesize_structural_forces(blueprint)
        if archetypal_forces is None:
            archetypal_forces = StructuralForcesSynthesis(
                want="To change their circumstance",
                resistance="Internal and external forces oppose change",
                conflict="Change requires destroying the old self",
                stakes="Everything the protagonist knows",
                change="Transformation or death",
                rationale="Ultimate fallback — no target experience available.",
            )

    char_lines = []
    for c in blueprint.characters:
        char_lines.append(f"  - {c.name} ({c.role.value})")

    characters_block = "\n".join(char_lines) if char_lines else "  (none)"

    return f"""\
## Story Identity
Title: {blueprint.identity.title}
Genre: {blueprint.identity.genre.value if blueprint.identity.genre else 'unspecified'}
Mode: {blueprint.identity.mode.value if blueprint.identity.mode else 'unspecified'}
Target experience: {blueprint.identity.target_experience.primary if blueprint.identity.target_experience else 'unspecified'}
Length class: {blueprint.identity.length_class.value if blueprint.identity.length_class else 'unspecified'}

## Author Intent
{blueprint.identity.author_intent or '(not provided)'}

## Theme
Central question: {blueprint.theme.central_question}
Thesis: {blueprint.theme.thesis}

## Characters
{characters_block}

## Archetypal Structural Forces (refine these)
want: {archetypal_forces.want}
resistance: {archetypal_forces.resistance}
conflict: {archetypal_forces.conflict}
stakes: {archetypal_forces.stakes}
change: {archetypal_forces.change}

Refine the above structural forces and generate a complete story engine
(one main thread + subordinate threads) that is specific to this story.
Use actual character names, setting details, and premise-specific stakes.
Output valid YAML matching the schema from the system prompt."""


def parse_refinement_response(text: str) -> dict:
    """Parse the LLM response text into a dict matching GenerationProposal shape.

    Strips markdown fences if present, then parses YAML.
    """
    cleaned = text.strip()
    if cleaned.startswith("```"):
        lines = cleaned.splitlines()
        fence_char = lines[0][3:].strip() or "yaml"
        if lines[0].startswith("```"):
            cleaned = "\n".join(lines[1:])
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3].strip()
        elif lines[-1].strip() == "```":
            cleaned = lines[-1].strip()

    data = yaml.safe_load(cleaned)
    if not isinstance(data, dict):
        raise ValueError(f"Expected YAML dict, got {type(data).__name__}")
    return data


def llm_refine_story_engine(
    blueprint: StoryBlueprint,
    llm: LLMClient,
    archetypal_forces: StructuralForcesSynthesis | None = None,
) -> GenerationProposal:
    """Refine the story engine for a blueprint using an LLM.

    Takes the template-based structural forces and threads, sends them to
    the LLM along with the full premise context, and returns a refined
    GenerationProposal with story-specific forces and threads.

    Falls back to template-based generation if the LLM call fails or the
    response cannot be parsed.
    """
    from auteur.structure.generator import generate_story_engine as _template_generate

    template_result = _template_generate(blueprint)
    if not isinstance(template_result, GenerationProposal):
        try:
            sf = synthesize_structural_forces(blueprint) or archetypal_forces
            if sf is None:
                sf = StructuralForcesSynthesis(
                    want="To change their circumstance",
                    resistance="Internal and external forces oppose change",
                    conflict="Change requires destroying the old self",
                    stakes="Everything the protagonist knows",
                    change="Transformation or death",
                    rationale="Ultimate fallback.",
                )
            main = generate_main_thread(blueprint, sf)
            subs = generate_subordinate_threads(blueprint, sf, main)
            template_result = GenerationProposal(
                structural_forces=sf,
                main_thread=main,
                subordinate_threads=subs,
            )
        except Exception:
            template_result = GenerationProposal(
                structural_forces=StructuralForcesSynthesis(
                    want="To change their circumstance",
                    resistance="Internal and external forces oppose change",
                    conflict="Change requires destroying the old self",
                    stakes="Everything the protagonist knows",
                    change="Transformation or death",
                    rationale="Ultimate fallback.",
                ),
                main_thread=GeneratedThread(
                    name="main_plot",
                    thread_type=ThreadType.MAIN_PLOT,
                    want="To change their circumstance",
                    confidence=0.5,
                    rationale="Fallback — template generation failed.",
                ),
            )

    forces = archetypal_forces or template_result.structural_forces

    user_message = build_refinement_prompt(blueprint, forces)

    try:
        resp = llm.complete(LLMRequest(
            system=_REFINEMENT_SYSTEM_PROMPT,
            user=user_message,
            temperature=0.3,
            max_tokens=4000,
        ))
        data = parse_refinement_response(resp.text)
    except Exception:
        return template_result

    try:
        raw_sf = data.get("structural_forces", {})
        refined_forces = StructuralForcesSynthesis(
            want=raw_sf.get("want", forces.want),
            resistance=raw_sf.get("resistance", forces.resistance),
            conflict=raw_sf.get("conflict", forces.conflict),
            stakes=raw_sf.get("stakes", forces.stakes),
            change=raw_sf.get("change", forces.change),
            rationale="Refined by LLM against premise: " + (
                blueprint.identity.author_intent or blueprint.identity.title
            ),
        )

        raw_main = data.get("main_thread", {})
        refined_main = GeneratedThread(
            name=raw_main.get("name", template_result.main_thread.name),
            thread_type=raw_main.get("thread_type", template_result.main_thread.thread_type),
            want=raw_main.get("want", template_result.main_thread.want),
            function=raw_main.get("function", template_result.main_thread.function),
            carriers=raw_main.get("carriers", template_result.main_thread.carriers),
            confidence=float(raw_main.get("confidence", template_result.main_thread.confidence)),
            rationale=raw_main.get("rationale", template_result.main_thread.rationale),
        )

        raw_subs = data.get("subordinate_threads", [])
        refined_subs = []
        for i, raw in enumerate(raw_subs):
            template_sub = template_result.subordinate_threads[i] if i < len(template_result.subordinate_threads) else None
            refined_subs.append(GeneratedThread(
                name=raw.get("name", template_sub.name if template_sub else f"thread_{i}"),
                thread_type=raw.get("thread_type", template_sub.thread_type if template_sub else ThreadType.CHARACTER_ARC),
                want=raw.get("want", template_sub.want if template_sub else ""),
                function=raw.get("function", template_sub.function if template_sub else None),
                carriers=raw.get("carriers", template_sub.carriers if template_sub else []),
                confidence=float(raw.get("confidence", template_sub.confidence if template_sub else 0.6)),
                rationale=raw.get("rationale", template_sub.rationale if template_sub else ""),
            ))

        raw_honored = data.get("constraints_honored", template_result.constraints_honored)

        return GenerationProposal(
            structural_forces=refined_forces,
            main_thread=refined_main,
            subordinate_threads=refined_subs,
            generation_method="llm-refined",
            constraints_honored=raw_honored if isinstance(raw_honored, list) else template_result.constraints_honored,
            potential_issues=template_result.potential_issues.copy(),
        )
    except Exception:
        return template_result
