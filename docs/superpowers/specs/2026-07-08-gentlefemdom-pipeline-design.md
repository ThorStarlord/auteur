# Gentle Femdom Genre Pipeline Design Specification

**Date:** 2026-07-08  
**Status:** Design Approved  
**Author:** Claude  
**Related:** [Netorare Pipeline Design](2026-07-07-netorare-pipeline-design.md), [Mystery Pipeline Design](2026-07-08-mystery-pipeline-design.md)

## Executive Summary

The Gentle Femdom genre pipeline extends auteur's 9-layer framework to support intimate power-exchange narratives with three distinct emotional cores: **Sensual Dominance** (playful control), **Tender Surrender** (willing vulnerability), and **Romantic Authority** (affectionate leadership). All three cores use the same infrastructure as netorare and mystery, with only genre-specific templates, validation rules, and identity generation requiring new implementation.

**Expected deliverables:** Three core template classes, genre-specific validation rules, identity generator routing, ~1,500 LOC, 40-50 tests.

---

## Part 1: Genre Architecture & Emotional Cores

### Core 1: Sensual Dominance

**Primary Emotional Arc:** Attraction → Intrigue → Playful Power Exchange → Deepening Connection → Intimate Understanding

**Narrative Intent:** The dominant partner leads with charm and intention. The submissive enjoys the structure and attention. Neither is coerced; both are active participants in a dance of power that creates intimacy rather than harm.

**Layer 4 Structural Forces:**

| Force | Definition | Example |
|-------|-----------|---------|
| **Want** | What the dominant partner seeks | Establish trust through leadership, create a safe space for vulnerability |
| **Resistance** | What makes control dynamic | Partner's boundaries, need to earn trust, resistance to vulnerability |
| **Conflict** | The core tension | Control vs. consent; power vs. care |
| **Stakes** | What's at risk | Emotional intimacy, trust, relationship depth |
| **Change** | How the relationship transforms | From tentative to confident, stranger to intimate partner |

**Emotional Tone:** Playful, confident, caring. The dominant is assertive but attentive. The submissive is eager but retains agency.

**Validation Constraints:**
- Dominance is always consensual and enthusiastic (never forced)
- Boundaries are explicitly respected, never violated
- Submissive partner's desires shape the experience equally
- Playfulness and humor present (not grim or punitive)
- Aftercare and emotional connection central to narrative
- Power exchange serves intimacy, not degradation

**Example Ending:**
- Dominant and submissive deepened in trust and connection
- Vulnerability shared, boundaries respected
- Relationship stronger through honest power exchange
- Both partners fulfilled and celebrated

---

### Core 2: Tender Surrender

**Primary Emotional Arc:** Resistance → Curiosity → Gradual Opening → Safe Falling → Blissful Release

**Narrative Intent:** The submissive character discovers pleasure in releasing control to a trusted partner. This is a journey inward—exploration of desire, vulnerability, and the freedom that comes from surrendering to someone worthy.

**Layer 4 Structural Forces:**

| Force | Definition | Example |
|-------|-----------|---------|
| **Want** | What the submissive seeks | Release from decision-making, experience pleasure through surrender |
| **Resistance** | What creates internal conflict | Fear of vulnerability, doubt about worthiness, past trauma |
| **Conflict** | The core tension | Self-protection vs. desire to trust; control vs. letting go |
| **Stakes** | What's at risk | Emotional walls, identity, sense of safety |
| **Change** | How understanding transforms | From isolated to connected, defended to open, doubting to trusting |

**Emotional Tone:** Vulnerable, hopeful, gradually relaxing. The submissive's internal journey is central; the dominant provides safety for that journey.

**Validation Constraints:**
- Surrender is always voluntary (no coercion or manipulation)
- Vulnerability is honored, not mocked
- The dominant partner proves trustworthiness through action
- Release is portrayed as empowering, not diminishing
- Emotional growth alongside physical exploration
- Safety and communication essential (not assumed)

**Example Ending:**
- Submissive character transformed through safe surrender
- Old fears released, new capacity for trust born
- Dominant partner recognized as worthy of that trust
- Relationship deepened through mutual vulnerability

---

### Core 3: Romantic Authority

**Primary Emotional Arc:** Partnership → Admiration → Willing Deference → Cherished Leadership → Interdependence

**Narrative Intent:** One partner is the clear leader—competent, decisive, caring. The other partner delights in following that leadership because it frees them to be vulnerable, appreciated, and loved exactly as they are. This is romantic, not humiliating.

**Layer 4 Structural Forces:**

| Force | Definition | Example |
|-------|-----------|---------|
| **Want** | What the leader seeks | Provide for and protect their beloved, make decisions that serve them both |
| **Resistance** | What creates tension | Partner's independence, need to prove worthiness, decisions that affect both |
| **Conflict** | The core tension | Leadership vs. partnership; direction vs. choice |
| **Stakes** | What's at risk | Relationship balance, both partners' fulfillment, mutual respect |
| **Change** | How love deepens | From uncertain to confident in roles, separate to interdependent |

**Emotional Tone:** Romantic, respectful, confident. The leader is strong but tender. The follower is proud to be chosen and cared for.

**Validation Constraints:**
- Authority is rooted in genuine care, not ego or control
- Submissive partner is genuinely cherished (not diminished by role)
- Leadership serves the relationship, not just the leader
- Respect flows both directions (different forms)
- The submissive partner's input shapes decisions (not overruled)
- Interdependence, not dependence

**Example Ending:**
- Leader confident, partner secure
- Roles clear and mutually fulfilling
- Love expressed through trust and care
- Relationship stronger because of role clarity

---

## Part 2: Implementation Tasks

### Task 1: Gentle Femdom Core Templates

**Files:**
- Create: `src/auteur/gentlefemdom/__init__.py`
- Create: `src/auteur/gentlefemdom/core_templates.py`
- Create: `tests/gentlefemdom/__init__.py`
- Create: `tests/gentlefemdom/test_core_templates.py`

**Interfaces:**
- Produces:
  - `SensualDominanceTemplate()` with `.phases`, `.core_id="sensual_dominance"`, `.primary_emotion="playful_control"`
  - `TenderSurrenderTemplate()` with `.phases`, `.core_id="tender_surrender"`, `.primary_emotion="safe_vulnerability"`
  - `RomanticAuthorityTemplate()` with `.phases`, `.core_id="romantic_authority"`, `.primary_emotion="cherished_leadership"`
  - `get_template(core_id: str)` factory function
  - Each template: `get_options(phase)`, `get_constraints(phase)`, `validate_choices(choices)`

**Test count:** ~15 tests (similar to mystery)

---

### Task 2: Gentle Femdom Validation Rules

**Files:**
- Create: `src/auteur/gentlefemdom/validation.py`
- Create: `tests/gentlefemdom/test_validation.py`

**Validation Rules:**

**Sensual Dominance (3-4 rules):**
- consent_enthusiastic: Dominance is always consensual and enthusiastic
- boundaries_explicit: Boundaries clearly stated and respected
- playfulness_present: Tone is playful, not grim
- care_central: Dominant's care for submissive evident

**Tender Surrender (3-4 rules):**
- surrender_voluntary: Surrender is never coerced
- vulnerability_honored: Submissive's vulnerability is valued
- trust_earned: Dominant proves trustworthiness through action
- growth_emotional: Emotional growth alongside physical

**Romantic Authority (3-4 rules):**
- authority_rooted_in_care: Leadership serves both, not just leader
- partner_cherished: Submissive partner genuinely valued
- respect_bidirectional: Respect flows both ways
- interdependence_balanced: Neither fully dependent

**Test count:** ~20 tests (similar to mystery)

---

### Task 3: Identity Generator Extension & CLI

**Files:**
- Modify: `src/auteur/netorare/identity_generator.py` (add gentlefemdom routing)
- Create: `src/auteur/cli_gentlefemdom.py` (CLI entry point)
- Create: `tests/gentlefemdom/test_identity_generator.py`

**Tests:** ~12 covering identity generation, YAML serialization, CLI workflow

---

## Part 3: Reuse Architecture

All existing infrastructure reuses netorare/mystery:
- Session State Management (Tasks 4-7 from netorare)
- Browser HTTP Server (unchanged)
- Browser UI (unchanged)
- CLI dispatcher (will add gentlefemdom subcommand)

---

## Part 4: Design Decisions & Rationale

### Q1: Why "gentle" femdom specifically?
**A:** To emphasize consent, care, and playfulness over power for its own sake. This distinguishes it from darker BDSM narratives and positions it as a romance/intimacy genre with power-exchange elements.

### Q2: Why three cores?
**A:** Each represents a different perspective on power exchange:
- Sensual Dominance: The leader's point of view
- Tender Surrender: The submissive's journey
- Romantic Authority: The partnership's foundation

### Q3: Validation emphasizes consent and care heavily?
**A:** Yes. These are non-negotiable. Gentle femdom without genuine consent or care becomes something else (abuse, manipulation). The validation rules enforce the genre's emotional integrity.

---

## Part 5: Success Criteria

- ✅ Three emotional cores with 9-phase templates each
- ✅ Genre-specific validation rules for all three cores
- ✅ Identity generation routing to Genre.GENTLEFEMDOM
- ✅ 40-50 tests, all passing
- ✅ CLI integrated (`auteur gentlefemdom init --core sensual_dominance`)
- ✅ Documentation updated
- ✅ Zero regressions on netorare/mystery

---

## Part 6: Next Steps

1. Implementation via subagent-driven-development (similar to mystery)
2. End-to-end verification
3. Code review
4. CLI integration
5. Documentation updates
6. Production ready

