# Stateful Ledger — MVP Architecture & System Design Document

**Version:** 0.1 — MVP  
**Stack:** Python · Streamlit · Google Gemini API (Flash/Pro)  
**Author:** Architecture Design Spec  
**Status:** Pre-Build Reference

---

## Table of Contents

1. [System Flow & Architecture Breakdown](#1-system-flow--architecture-breakdown)
   - 1.1 High-Level Pipeline Overview
   - 1.2 Multi-Pass Data Flow (Per Turn)
   - 1.3 Streamlit Layout Structure
   - 1.4 Ledger JSON Data Schema
2. [Core Mechanics — The "How"](#2-core-mechanics--the-how)
   - 2.1 Output Evaluation Logic (Layer 1 Internal Audit)
   - 2.2 Uncertainty & Confidence Communication
   - 2.3 User Control Mechanisms
3. [User Interaction States](#3-user-interaction-states)
4. [Edge Case Handling & Routing](#4-edge-case-handling--routing)
5. [Implementation Blueprint](#5-implementation-blueprint)

---

---

# 1. System Flow & Architecture Breakdown

## 1.1 High-Level Pipeline Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         STATEFUL LEDGER — DATA PIPELINE                 │
│                                                                         │
│  USER INPUT                                                             │
│      │                                                                  │
│      ▼                                                                  │
│  ┌────────────────────────────────────────────────┐                    │
│  │ STAGE 0 (Turn 1 Only):  RUBRIC BOOTSTRAP       │ ◄── Gemini Call #0 │
│  │  Auto-generate evaluation rubric + seed rules  │     (Background)   │
│  └───────────────────┬────────────────────────────┘                    │
│                      │                                                  │
│      ▼                                                                  │
│  ┌────────────────────────────────────────────────┐                    │
│  │ STAGE 1: CONTEXT ASSEMBLY (Ledger Hydration)   │                    │
│  │  Inject: rules, assumptions, rubric, history   │                    │
│  └───────────────────┬────────────────────────────┘                    │
│                      │                                                  │
│      ▼                                                                  │
│  ┌────────────────────────────────────────────────┐                    │
│  │ STAGE 2: GENERATION PASS 1                     │ ◄── Gemini Call #1 │
│  │  Produce raw AI response (text)                │                    │
│  └───────────────────┬────────────────────────────┘                    │
│                      │                                                  │
│      ▼                                                                  │
│  ┌────────────────────────────────────────────────┐                    │
│  │ STAGE 3: INTERNAL AUDIT PASS 2 (COMPULSORY)    │ ◄── Gemini Call #2 │
│  │  Structured output: tags, rules, rubric check  │   (response_schema)│
│  └───────────────────┬────────────────────────────┘                    │
│                      │                                                  │
│      ▼                                                                  │
│  ┌────────────────────────────────────────────────┐                    │
│  │ STAGE 4: LEDGER STATE UPDATE                   │                    │
│  │  Merge audit results into persistent Ledger    │                    │
│  └───────────────────┬────────────────────────────┘                    │
│                      │                                                  │
│      ▼                                                                  │
│  ┌────────────────────────────────────────────────┐                    │
│  │ STAGE 5: STREAMLIT UI RENDER                   │                    │
│  │  Chat panel + Ledger sidebar + tagged response │                    │
│  └───────────────────┬────────────────────────────┘                    │
│                      │                                                  │
│      ▼  (User-triggered, asynchronous)                                 │
│  ┌────────────────────────────────────────────────┐                    │
│  │ STAGE 6: EXTERNAL VALIDATION (OPTIONAL)        │ ◄── Gemini Call #3 │
│  │  Google Search Grounding → claim classification│   (tools=search)   │
│  └────────────────────────────────────────────────┘                    │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 1.2 Multi-Pass Data Flow (Per Turn)

### Stage 0 — Rubric Bootstrap *(Turn 1 Only, runs before Stage 1)*

**Trigger:** Fires immediately upon first user message submission, before any response is generated.

**Input:** Raw first user prompt only.

**Process:**
```
Gemini Call #0
  model : gemini-1.5-flash (low cost, fast)
  mode  : structured output (response_schema = RubricBootstrapSchema)
  prompt: "Given this user query, identify: (a) 3–6 evaluation dimensions 
           a thorough answer should cover, (b) 3–5 initial boundary rules 
           that should hold across ALL responses in this session, 
           (c) implicit assumptions the user appears to be making."
```

**Output written to:** `st.session_state.ledger["rubric"]` and `st.session_state.ledger["rules"]`

**Visibility:** Hidden from user during execution. A subtle spinner renders: *"Calibrating evaluation lens…"*

---

### Stage 1 — Context Assembly (Ledger Hydration)

**Input:** Current user prompt + full `st.session_state.ledger`

**Process:** A deterministic Python function `assemble_context()` builds a structured string injected as the system prompt for Pass 1. No AI call. Pure string construction.

```
assemble_context() output structure:
  ┌── [SYSTEM CONTEXT BLOCK] ─────────────────────┐
  │  ACTIVE RULES (rule_id, rule_text, status)     │
  │  ACTIVE ASSUMPTIONS (assumption_id, text)      │
  │  KNOWN MISSING INFO (item_id, description)     │
  │  EVALUATION RUBRIC (dimension_name, weight)    │
  │  CONTRADICTION LOG (unresolved items only)     │
  │  TURN HISTORY (last N turns, N = configurable) │
  └────────────────────────────────────────────────┘
```

**Rule:** If `contradiction_log` contains any item with `resolution_status = "pending"`, append a special directive: *"There is an unresolved contradiction from Turn {N}. Do not resolve it autonomously. Surface it explicitly in your response."*

---

### Stage 2 — Generation Pass 1

**Input:** Assembled context (system prompt) + user message (user turn)

**Process:**
```
Gemini Call #1
  model  : gemini-1.5-pro (or flash based on config)
  mode   : standard text generation
  system : assembled context from Stage 1
  config : temperature = 0.4 (reproducibility priority)
  output : raw_response_text (plain string)
```

**No structured output here.** The raw text is the AI's attempt at a natural-language answer. It is stored immediately as `turn["raw_response"]` in the ledger but is NOT shown to the user yet.

---

### Stage 3 — Compulsory Internal Audit Pass 2

**Input:** `raw_response_text` + active `rubric` + active `rules` + active `assumptions`

**Process:**
```
Gemini Call #2
  model           : gemini-1.5-flash
  mode            : structured output (response_schema = AuditResultSchema)
  temperature     : 0.0  ← deterministic, critical for consistency
  system_prompt   : "You are a strict logic auditor. You do NOT generate 
                     new content. You only evaluate the provided text 
                     against the provided rules and rubric."
  user_prompt     : [constructed audit prompt — see Section 2.1 for 
                     full prompt template]
  response_schema : AuditResultSchema (Pydantic model)
```

**Output:** A fully structured `AuditResult` object. Written to `turn["audit_result"]` and merged into the ledger's running state.

**Non-negotiable:** This call always executes. There is no code path that skips it.

---

### Stage 4 — Ledger State Update

Pure Python logic. No AI calls. The `update_ledger()` function:

1. Appends new `sentence_tags` to the current turn record.
2. Evaluates each `rule_check` result:
   - If `status = "Violated"` → creates a new entry in `contradiction_log` with `resolution_status = "pending"`.
   - If `status = "Satisfied"` → updates the rule's `last_evaluated_at` timestamp.
3. Updates `rubric.dimensions[*].last_coverage_score` for each dimension.
4. Appends new `missing_info` items found during audit to `missing_info_registry` (deduplication by semantic similarity via string matching on `description` field for MVP).
5. Recalculates `trust_score` using the formula defined in Section 2.2.

---

### Stage 5 — Streamlit UI Render

**Trigger:** `st.rerun()` called after `update_ledger()` completes.

**What renders:**
- **Chat panel (left column):** Appends the new AI message bubble with inline sentence tags rendered as styled `st.markdown()` HTML spans.
- **Ledger sidebar (right column):** Fully re-renders all ledger state widgets (rules, rubric progress bars, contradiction flags, trust indicator).
- **[G] Verify Facts button:** Rendered beneath the latest AI message bubble if and only if `len(turn["audit_result"]["sentence_tags"]) > 0`.

---

### Stage 6 — External Validation (Layer 2, Optional)

**Trigger:** User clicks `[G] Verify Facts` button associated with a specific turn.

**Input:** `raw_response_text` of the targeted turn.

**Pre-processing:** Python function `extract_factual_claims(text)` splits the response into discrete factual claims (sentences or clauses that assert a fact, number, event, or attribution). Returns a list of claim strings. This can use a lightweight Gemini call or spaCy sentence splitting for MVP.

**Process:**
```
Gemini Call #3
  model    : gemini-1.5-pro  ← grounding requires Pro tier
  tools    : [{"google_search": {}}]
  prompt   : "For each of the following claims, determine whether it is 
              (a) Grounded — directly supported by search results, 
              (b) Contested — multiple credible conflicting perspectives exist, or 
              (c) Unverified — no search result confirms or denies it.
              Return a structured JSON list.
              Claims: {claims_list}"
  response : parsed for both text content and grounding_metadata chunks
```

**Output stored in:** `turn["grounding_result"]`

**Note:** The `grounding_metadata.grounding_chunks` from the Gemini response provides source URLs and relevance scores. These are mapped back to individual claims and stored alongside the classification.

---

## 1.3 Streamlit Layout Structure

### Global Page Config

```python
st.set_page_config(
    page_title="Stateful Ledger",
    layout="wide",
    initial_sidebar_state="collapsed"  # Native sidebar hidden; layout via columns
)
```

### Column Layout

```python
col_chat, col_ledger = st.columns([65, 35], gap="large")
```

> The native Streamlit `st.sidebar` is NOT used. The right-hand "Ledger Panel" is `col_ledger`. This allows fine-grained control over its height, scroll behavior, and CSS.

### Column: `col_chat` (Left — 65%)

```
┌──────────────────────────────────────────────────────┐
│  STATEFUL LEDGER                      [Trust: 72/100] │  ← App header row
├──────────────────────────────────────────────────────┤
│                                                      │
│  ┌───────────────────────────────────────────────┐  │
│  │  [USER]  What is the impact of X on Y?        │  │  ← st.chat_message("user")
│  └───────────────────────────────────────────────┘  │
│                                                      │
│  ┌───────────────────────────────────────────────┐  │
│  │  [AI]  Response text with inline tags...      │  │  ← st.chat_message("assistant")
│  │                                               │  │    rendered via st.markdown()
│  │  ⚠️ Contradiction flagged — see Ledger       │  │  ← inline contradiction banner
│  │                                               │  │
│  │  [ 🔍 Verify Facts ]  [ ✓ Looks Good ]       │  │  ← action buttons per-message
│  └───────────────────────────────────────────────┘  │
│                                                      │
│  ┌───────────────────────────────────────────────┐  │
│  │  st.chat_input("Ask or clarify...")           │  │  ← pinned at bottom
│  └───────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────┘
```

### Column: `col_ledger` (Right — 35%)

```
┌─────────────────────────────────────┐
│  📒 LEDGER PANEL                   │  ← header
├─────────────────────────────────────┤
│  TRUST INDICATOR                    │
│  [████████░░] 72/100               │  ← st.progress()
│  Updated: Turn 4                    │
├─────────────────────────────────────┤
│  ▼ EVALUATION RUBRIC               │  ← st.expander(), open by default
│  ├── Factual Accuracy       [88%]  │  ← st.progress() per dimension
│  ├── Logical Coherence      [95%]  │
│  ├── Completeness           [60%]  │  ← low = yellow indicator
│  └── Assumption Transparency[75%]  │
├─────────────────────────────────────┤
│  ▼ ACTIVE RULES (4)                │  ← st.expander()
│  ├── ✅ rule_001: [text...]        │
│  ├── ✅ rule_002: [text...]        │
│  ├── ⚠️ rule_003: VIOLATED        │  ← highlighted red
│  │      [Override] [Accept Risk]   │  ← action buttons
│  └── ✅ rule_004: [text...]        │
├─────────────────────────────────────┤
│  ▼ ASSUMPTIONS (3)                 │  ← st.expander()
│  ├── assump_001: [text...]         │
│  └── assump_002: [text...] [✗]     │  ← user can invalidate
├─────────────────────────────────────┤
│  ▼ MISSING INFO (2)                │  ← st.expander()
│  ├── 🔴 HIGH: [description]       │
│  └── 🟡 MED:  [description]       │
├─────────────────────────────────────┤
│  ▼ CONTRADICTION LOG (1 pending)   │  ← st.expander(), opens auto on flag
│  └── contra_001 [Turn 3]          │
│       Description: [text...]       │
│       [Accept Rule Violation]      │
│       [Override Rule]              │
│       [Flag for Review]            │
└─────────────────────────────────────┘
```

### CSS Overrides (injected via `st.markdown("<style>...</style>", unsafe_allow_html=True)`)

```css
/* Make col_ledger sticky/scrollable */
[data-testid="column"]:nth-child(2) {
    position: sticky;
    top: 0;
    max-height: 100vh;
    overflow-y: auto;
    border-left: 1px solid #e0e0e0;
    padding-left: 1rem;
}

/* Sentence tag styling */
.tag-reasoned {
    background-color: #e8f5e9;
    border-bottom: 2px solid #4caf50;
    padding: 1px 2px;
    border-radius: 2px;
}
.tag-inferred {
    background-color: #fff8e1;
    border-bottom: 2px dashed #ff9800;
    padding: 1px 2px;
    border-radius: 2px;
}
.tag-grounded    { background: #e3f2fd; border-bottom: 2px solid #2196f3; }
.tag-contested   { background: #fce4ec; border-bottom: 2px solid #e91e63; }
.tag-unverified  { background: #f3e5f5; border-bottom: 2px dotted #9c27b0; }
```

---

## 1.4 Ledger JSON Data Schema

This is the canonical data structure stored in `st.session_state.ledger`. It is a Python dict serializable to JSON. Every field is defined with its type and purpose.

```json
{
  "ledger_id": "string (uuid4)",
  "session_created_at": "ISO 8601 timestamp",
  "total_turns": "integer",
  "trust_score": "integer (0–100, starts at 50)",

  "rubric": {
    "auto_generated": "boolean",
    "generated_at_turn": "integer (always 1)",
    "dimensions": [
      {
        "id": "string (e.g. 'dim_001')",
        "name": "string (e.g. 'Logical Coherence')",
        "description": "string",
        "weight": "float (0.0–1.0, all weights sum to 1.0)",
        "last_coverage_score": "integer (0–100, null until first audit)",
        "coverage_history": "list[integer] (one per turn)"
      }
    ]
  },

  "rules": [
    {
      "rule_id": "string (e.g. 'rule_001')",
      "type": "enum: auto | user_defined | user_override",
      "text": "string",
      "source_turn": "integer",
      "status": "enum: active | suspended | overridden",
      "override_reason": "string | null",
      "override_at_turn": "integer | null",
      "last_evaluated_at": "ISO 8601 timestamp | null",
      "violation_count": "integer (increments on each violation)"
    }
  ],

  "assumptions": [
    {
      "assumption_id": "string (e.g. 'assump_001')",
      "text": "string",
      "source_turn": "integer",
      "confidence": "enum: explicit | inferred",
      "status": "enum: active | invalidated | user_confirmed",
      "invalidated_at_turn": "integer | null",
      "invalidation_reason": "string | null"
    }
  ],

  "missing_info_registry": [
    {
      "item_id": "string (e.g. 'missing_001')",
      "description": "string",
      "identified_at_turn": "integer",
      "severity": "enum: Low | Medium | High",
      "resolved": "boolean",
      "resolved_at_turn": "integer | null",
      "resolution_note": "string | null"
    }
  ],

  "contradiction_log": [
    {
      "contradiction_id": "string (e.g. 'contra_001')",
      "description": "string",
      "conflicting_elements": "list[string] (e.g. [rule_id, turn reference])",
      "identified_at_turn": "integer",
      "severity": "enum: Low | Medium | High",
      "resolution_status": "enum: pending | user_accepted | user_overridden | flagged",
      "resolution_action": "string | null",
      "resolved_at_turn": "integer | null"
    }
  ],

  "turn_history": [
    {
      "turn_id": "string (e.g. 'turn_001')",
      "turn_number": "integer",
      "timestamp": "ISO 8601 timestamp",
      "user_prompt": "string",
      "raw_response": "string",
      "audit_result": {
        "sentence_tags": [
          {
            "sentence_index": "integer",
            "text": "string",
            "tag": "enum: Reasoned | Inferred",
            "reasoning": "string (why this tag was assigned)"
          }
        ],
        "rule_checks": [
          {
            "rule_id": "string",
            "rule_text": "string",
            "status": "enum: Satisfied | Violated | Not_Applicable",
            "evidence": "string (quote or explanation from raw_response)"
          }
        ],
        "rubric_scores": [
          {
            "dimension_id": "string",
            "dimension_name": "string",
            "coverage_score": "integer (0–100)",
            "gap_description": "string | null"
          }
        ],
        "new_contradictions": "list[string] (contradiction_ids created this turn)",
        "new_missing_info": "list[string] (item_ids created this turn)",
        "new_assumptions": "list[string] (assumption_ids created this turn)",
        "overall_audit_confidence": "integer (0–100)",
        "audit_summary": "string (1–2 sentence plain-language summary)"
      },
      "grounding_result": {
        "status": "enum: not_run | completed | failed",
        "claims": [
          {
            "claim_index": "integer",
            "claim_text": "string",
            "classification": "enum: Grounded | Contested | Unverified",
            "evidence_snippets": "list[string] (paraphrased search result support)",
            "source_urls": "list[string]",
            "contested_perspectives": "list[string] | null (populated if Contested)"
          }
        ],
        "grounding_metadata_raw": "object (raw Gemini grounding_metadata for debugging)"
      }
    }
  ]
}
```

---

---

# 2. Core Mechanics — The "How"

## 2.1 Output Evaluation Logic (Layer 1 — Internal Audit)

### Pydantic Schemas for Structured Output

Define these in `schemas/audit_schemas.py`:

```python
from pydantic import BaseModel
from typing import Literal, Optional

class SentenceTag(BaseModel):
    sentence_index: int
    text: str
    tag: Literal["Reasoned", "Inferred"]
    reasoning: str
    # Reasoned = deduced from stated premises or prior context
    # Inferred  = extrapolated beyond what evidence supports

class RuleCheck(BaseModel):
    rule_id: str
    rule_text: str
    status: Literal["Satisfied", "Violated", "Not_Applicable"]
    evidence: str

class RubricScore(BaseModel):
    dimension_id: str
    dimension_name: str
    coverage_score: int        # 0–100
    gap_description: Optional[str]

class NewContradiction(BaseModel):
    description: str
    conflicting_elements: list[str]
    severity: Literal["Low", "Medium", "High"]

class NewMissingInfo(BaseModel):
    description: str
    severity: Literal["Low", "Medium", "High"]

class NewAssumption(BaseModel):
    text: str
    confidence: Literal["explicit", "inferred"]

class AuditResult(BaseModel):
    sentence_tags: list[SentenceTag]
    rule_checks: list[RuleCheck]
    rubric_scores: list[RubricScore]
    new_contradictions: list[NewContradiction]
    new_missing_info: list[NewMissingInfo]
    new_assumptions: list[NewAssumption]
    overall_audit_confidence: int  # 0–100
    audit_summary: str
```

---

### Audit Prompt Template (Pass 2)

Used in `gemini_client.run_audit()`. Constructed dynamically per turn.

```
SYSTEM:
You are a strict internal logic auditor. Your ONLY job is to evaluate the 
[RESPONSE TEXT] below against the [ACTIVE RULES], [ACTIVE ASSUMPTIONS], and 
[EVALUATION RUBRIC] provided. You do NOT generate new information. 
You do NOT resolve contradictions. You surface them precisely.

USER:
=== RESPONSE TO AUDIT ===
{raw_response_text}

=== ACTIVE RULES ===
{json.dumps(active_rules, indent=2)}

=== ACTIVE ASSUMPTIONS ===
{json.dumps(active_assumptions, indent=2)}

=== EVALUATION RUBRIC ===
{json.dumps(rubric_dimensions, indent=2)}

=== INSTRUCTIONS ===
1. SENTENCE TAGGING: Split the response into individual sentences. 
   Tag each as:
   - "Reasoned": The sentence follows logically from stated premises, 
     prior conversation context, or the user's explicit question.
   - "Inferred": The sentence introduces a claim, extrapolation, or 
     conclusion that goes beyond what the evidence directly supports.

2. RULE CHECKS: For each active rule, determine if the response 
   Satisfied, Violated, or is Not_Applicable. Provide specific evidence 
   (quote or description) from the response.

3. RUBRIC SCORES: For each rubric dimension, assign a coverage score 
   0–100 and describe the gap if score < 80.

4. NEW CONTRADICTIONS: Identify any logical conflicts between the 
   response and active rules or assumptions. Be specific. Do NOT suggest 
   how to resolve them.

5. NEW MISSING INFO: Identify information that would be needed for a 
   more complete answer, that was not provided.

6. NEW ASSUMPTIONS: Identify any NEW implicit assumptions the response 
   introduces.

7. OVERALL CONFIDENCE: Assign 0–100 based on internal logical 
   consistency only (NOT factual correctness).

Return ONLY the structured JSON. No preamble.
```

---

### Step-by-Step Audit Execution Logic

```
FUNCTION run_internal_audit(raw_response, ledger):

  STEP 1 — Prepare inputs:
    active_rules       ← [r for r in ledger["rules"] if r["status"] == "active"]
    active_assumptions ← [a for a in ledger["assumptions"] if a["status"] == "active"]
    rubric_dimensions  ← ledger["rubric"]["dimensions"]

  STEP 2 — Build audit prompt:
    prompt ← fill audit_prompt_template(raw_response, active_rules,
                                         active_assumptions, rubric_dimensions)

  STEP 3 — Call Gemini with structured output:
    audit_result ← gemini_client.generate_structured(
        prompt         = prompt,
        response_schema= AuditResult,
        temperature    = 0.0
    )

  STEP 4 — Validate schema:
    IF audit_result is None OR fails Pydantic validation:
      SET audit_result to a safe "audit_failed" sentinel object
      LOG error to st.session_state.system_errors
      CONTINUE (do not block UI render)

  STEP 5 — Write to turn record:
    turn["audit_result"] ← audit_result.dict()

  STEP 6 — Propagate to ledger:
    FOR each rule_check in audit_result.rule_checks:
      IF status == "Violated":
        CREATE contradiction_log entry (status = "pending")
        INCREMENT rule["violation_count"]

    FOR each new_missing_info:
      APPEND to ledger["missing_info_registry"] (dedup by description)

    FOR each new_assumption:
      APPEND to ledger["assumptions"] (type = "inferred")

    FOR each rubric_score:
      UPDATE ledger["rubric"]["dimensions"][id]["last_coverage_score"]
      APPEND to coverage_history

  STEP 7 — Recalculate trust score:
    trust_score ← compute_trust_score(ledger)
    ledger["trust_score"] ← trust_score

  RETURN audit_result, updated_ledger
```

---

## 2.2 Uncertainty & Confidence Communication

### Sentence Tag Rendering

Tags are rendered inline in the chat message as HTML spans within `st.markdown(..., unsafe_allow_html=True)`.

**Rendering function in `ui/renderers.py`:**

```python
def render_tagged_response(sentence_tags: list[dict]) -> str:
    """Convert sentence_tags list to an HTML string with inline tag spans."""
    html_parts = []
    for tag_obj in sentence_tags:
        text     = tag_obj["text"]
        tag      = tag_obj["tag"]          # "Reasoned" or "Inferred"
        reasoning = tag_obj["reasoning"]    # used as tooltip title

        css_class = "tag-reasoned" if tag == "Reasoned" else "tag-inferred"
        icon      = "✓" if tag == "Reasoned" else "~"
        tooltip   = reasoning.replace('"', '&quot;')

        span = (
            f'<span class="{css_class}" '
            f'title="{tooltip}" '
            f'data-tag="{tag}">'
            f'{text}'
            f'<sup style="font-size:0.65em; margin-left:2px;">{icon}</sup>'
            f'</span> '
        )
        html_parts.append(span)

    return "".join(html_parts)
```

**Visual key rendered below every AI response:**

```
LEGEND:  ✓ Reasoned (green underline)   ~ Inferred (orange dashed underline)
```

### Layer 2 Claim Classification Rendering

After Layer 2 completes, the response is re-rendered with grounding tags replacing or augmenting sentence tags:

| Classification | CSS Class      | Icon | Border Style       | Tooltip Content                            |
|----------------|---------------|------|--------------------|---------------------------------------------|
| Grounded       | `tag-grounded` | 🔵   | solid blue         | Source URL(s), paraphrased evidence         |
| Contested      | `tag-contested`| 🔴   | solid pink         | Multiple perspectives listed (bullet list)  |
| Unverified     | `tag-unverified`| ⚪  | dotted purple      | "No search evidence found for this claim"  |

**Contested claims expand inline:** Clicking a `🔴 Contested` span opens an `st.expander` directly below the message showing 2–3 competing perspectives retrieved via grounding.

### Trust Indicator Computation

```python
def compute_trust_score(ledger: dict) -> int:
    """
    Trust score reflects INTERNAL logical consistency only.
    Range: 0–100. Starts at 50.
    Does NOT reflect factual correctness (that's Layer 2's job).
    """
    if ledger["total_turns"] == 0:
        return 50

    # Component 1: Rule violation rate (weight: 40%)
    total_rules     = len([r for r in ledger["rules"] if r["status"] != "overridden"])
    total_violations = sum(r["violation_count"] for r in ledger["rules"])
    violation_rate  = total_violations / max(total_rules * ledger["total_turns"], 1)
    rule_score      = int((1 - min(violation_rate, 1.0)) * 100)

    # Component 2: Average rubric coverage (weight: 35%)
    scores = [d["last_coverage_score"] for d in ledger["rubric"]["dimensions"]
              if d["last_coverage_score"] is not None]
    rubric_score = int(sum(scores) / len(scores)) if scores else 50

    # Component 3: Unresolved contradictions (weight: 25%)
    pending = len([c for c in ledger["contradiction_log"]
                   if c["resolution_status"] == "pending"])
    contradiction_penalty = min(pending * 10, 50)
    contradiction_score   = 100 - contradiction_penalty

    trust = int(
        0.40 * rule_score +
        0.35 * rubric_score +
        0.25 * contradiction_score
    )
    return max(0, min(100, trust))
```

**Trust score is displayed as:**
- `[████████░░] 82/100` — `st.progress(score/100)` + label
- Color thresholds: 0–40 = red, 41–70 = amber, 71–100 = green (CSS applied to progress bar)
- Label beneath: *"Internal consistency only — not factual accuracy"*

---

## 2.3 User Control Mechanisms

### Rule Override Flow

When `audit_result.rule_checks` contains a `Violated` rule:

**Step 1 — Automatic:** A contradiction entry is created in `contradiction_log` with `resolution_status = "pending"`.

**Step 2 — UI notification:** The violated rule in the Ledger panel gets a red `⚠️ VIOLATED` badge. A non-dismissible banner appears in the chat panel below the AI message:

```
┌─────────────────────────────────────────────────────┐
│ ⚠️ INTERNAL TENSION DETECTED                        │
│ This response may conflict with Rule:               │
│ "{rule_text}"                                       │
│                                                     │
│ The system has NOT resolved this automatically.     │
│ Please choose:                                      │
│                                                     │
│  [Accept This Response Anyway]                      │
│  [Override the Rule (with reason)]                  │
│  [Flag for Later Review]                            │
└─────────────────────────────────────────────────────┘
```

**Step 3 — Button callbacks:**

- **Accept This Response Anyway:** Sets `contradiction.resolution_status = "user_accepted"`. The rule remains active and violation_count increments. A note is appended: *"User accepted violation at Turn N."*

- **Override the Rule:** Opens `st.text_input("Why are you overriding this rule?")`. On submit, sets `rule.status = "overridden"`, stores reason in `rule.override_reason`, and sets `contradiction.resolution_status = "user_overridden"`.

- **Flag for Later Review:** Sets `contradiction.resolution_status = "flagged"`. Contradiction persists in log with an amber indicator. Does not affect rule status.

### Missing Info Acknowledgment

Each item in `missing_info_registry` with `resolved = False` renders in the Ledger panel with:
```
🔴 HIGH: "The response does not address X."    [Mark Resolved]
```
`[Mark Resolved]` button sets `resolved = True` and records `resolved_at_turn`.

### Assumption Invalidation

Each active assumption renders with a small `[✗]` button:
```
assump_002: "User is asking about scenario Y"  [✗]
```
Clicking `[✗]` opens a confirmation: *"Invalidate this assumption? This will be noted in future audits."* On confirm: `assumption.status = "invalidated"`.

---

---

# 3. User Interaction States

## 3.1 State Machine Overview

```
                         ┌─────────────────────┐
                         │   ZERO STATE         │
                         │   (No turns yet)     │
                         └──────────┬──────────┘
                                    │ User sends first message
                                    ▼
                         ┌─────────────────────┐
                         │   BOOTSTRAPPING      │  ← Stage 0 running
                         │   (Rubric + Rules    │     spinner visible
                         │    being generated)  │
                         └──────────┬──────────┘
                                    │ Rubric + rules written to ledger
                                    ▼
                    ┌───────────────────────────────┐
                    │   GENERATION & AUDIT STATE     │  ← Stages 2–4 running
                    │   (Pass 1 + Pass 2 in flight)  │     "Thinking..." spinner
                    └───────────────┬───────────────┘
                                    │ Audit complete, UI renders
                                    ▼
               ┌─────────────────────────────────────────┐
               │         VERIFICATION REVIEW STATE        │
               │  (Layer 1 active, response displayed     │
               │   with sentence tags, ledger updated)    │
               └──────────┬────────────────┬─────────────┘
                          │                │
               No contradictions       Contradiction
               detected               detected
                          │                │
                          ▼                ▼
               ┌──────────────┐  ┌─────────────────────┐
               │  CLEAN STATE │  │  CONTRADICTION STATE  │
               │  (green ✓)   │  │  (⚠️ banner + ledger  │
               └──────┬───────┘  │   options active)    │
                      │          └──────────┬────────────┘
                      │                     │ User resolves
                      │                     ▼
                      │          ┌──────────────────────┐
                      │          │   CALIBRATED STATE    │
                      │          │   (trust score        │
                      │          │    recalculated)      │
                      │          └──────────┬────────────┘
                      │                     │
                      └──────────┬──────────┘
                                 │ User clicks [G] Verify Facts
                                 ▼
                    ┌─────────────────────────────┐
                    │  EXTERNAL VALIDATION STATE   │  ← Stage 6 running
                    │  (Layer 2 in flight)         │     search spinner
                    └──────────────┬──────────────┘
                                   │ Grounding complete
                                   ▼
                    ┌─────────────────────────────┐
                    │  GROUNDED REVIEW STATE       │
                    │  (Claims reclassified,       │
                    │   contested spans expanded)  │
                    └─────────────────────────────┘
```

---

## 3.2 State: Initial Zero-Click Generation

**Session state variables on first load:**
```python
st.session_state.ledger         = init_empty_ledger()   # schema above
st.session_state.messages       = []
st.session_state.audit_results  = {}
st.session_state.grounding_data = {}
st.session_state.app_state      = "zero"
st.session_state.system_errors  = []
```

**What the user sees:**
- Empty chat area with a centered prompt: *"Start a conversation. The Ledger will build itself."*
- Ledger panel on the right shows placeholder text: *"No ledger state yet."*
- No buttons, no spinners.

---

## 3.3 State: Verification Review State (Layer 1 Active)

**Triggered:** After every turn's `update_ledger()` completes.

**What the user sees:**
- AI message rendered with inline Reasoned/Inferred tags.
- Ledger panel fully populated: rubric progress bars updated, rules status refreshed, trust score updated.
- If no contradictions: subtle green `✓ Internally consistent` badge on the AI message.
- If contradictions exist: amber/red banner (see Section 2.3).
- Completeness tracker: rubric dimensions with scores below 70 shown with amber color and gap description tooltip.
- `[G] Verify Facts]` button visible beneath AI message.
- `[✓ Looks Good]` button visible — clicking this triggers a +5 trust score bonus and logs `user_positive_feedback` on the turn.

---

## 3.4 State: External Validation State (Layer 2 Active)

**Triggered:** User clicks `[G] Verify Facts]` on a specific turn.

**What the user sees:**
- A spinner replaces the `[G] Verify Facts]` button: *"Searching for grounding evidence…"*
- Ledger panel adds a new section: **"GROUNDING IN PROGRESS"** with a pulsing indicator.

**After completion:**
- AI message is re-rendered with grounding tags overlaid (Grounded/Contested/Unverified).
- The original Reasoned/Inferred tags are preserved in the ledger data but visually suppressed (toggle available: *"Show internal tags"*).
- `st.expander` sections for each Contested claim appear beneath the message.
- A grounding summary row appears in the Ledger panel:
  ```
  GROUNDING (Turn 2):  ✅ 4 Grounded  🔴 2 Contested  ⚪ 1 Unverified
  ```

---

## 3.5 State: Calibrated State (Trust Indicator Updated via User Feedback)

**Triggered by any of:**
- User resolves a contradiction (override or acceptance)
- User invalidates an assumption
- User clicks `[✓ Looks Good]`
- User clicks `[Mark Resolved]` on missing info

**What the user sees:**
- Trust score bar animates to its new value.
- A one-line change note appears beneath it: *"↑ Score updated: contradiction resolved at Turn 4"*
- Ledger panel items update their status badges in real-time.
- No page reload needed — all changes happen via `st.session_state` mutation + `st.rerun()`.

---

## 3.6 Guaranteeing the User Remains the Final Judge

The following design rules are enforced at the code level, not just the prompt level:

| Guarantee                                      | Implementation Mechanism                                                           |
|-----------------------------------------------|-----------------------------------------------------------------------------------|
| System NEVER resolves contradictions           | No code path mutates `contradiction.resolution_status` without a user callback    |
| System NEVER hides ambiguity                   | Inferred tags always render; opacity is never set to 0 in CSS                    |
| System NEVER claims absolute truth             | Trust score label is always followed by disclaimer text (hardcoded string)        |
| User can override any auto-generated rule       | Every rule has an `[Override]` button — always rendered, never conditionally hidden|
| User can invalidate any assumption              | Every assumption has a `[✗]` button — always rendered                             |
| User action is required before moving past a   | `pending` contradictions block the trust score from reaching >80 unless resolved   |
| high-severity contradiction                    | (soft gate — user can still continue chatting, but trust plateaus visually)       |
| Layer 2 is always optional                     | `[G] Verify Facts]` is a button the user must click; it is never triggered auto   |
| Contested claims show BOTH sides               | `contested_perspectives` always renders as a list; no single-perspective display  |

---

---

# 4. Edge Case Handling & Routing

## 4.1 Conflicting Outputs

**Scenario:** The user's new prompt (Turn N) implies or asserts something that directly contradicts an active rule established in Turn 1–N-1.

### Detection Flow

```
DURING STAGE 3 (Pass 2 Audit):
  rule_check.status == "Violated"
    → NewContradiction created
    → contradiction.conflicting_elements includes [rule_id, "user_prompt_turn_N"]
    → contradiction.severity assessed by audit model (Low/Medium/High)
    → contradiction_log entry created with resolution_status = "pending"

DURING STAGE 4 (Ledger Update):
  IF contradiction.severity == "High":
    SET st.session_state.block_trust_ceiling = True
    (trust score will not exceed 60 until resolved)
```

### User-Facing Routing

```
IF severity == "High":
  → Non-dismissible red banner in chat
  → Ledger contradiction section auto-expands
  → All three options shown: [Accept] [Override] [Flag]
  → Trust score capped at 60

IF severity == "Medium":
  → Amber collapsible banner in chat
  → Ledger contradiction section gains amber badge
  → All three options shown
  → Trust score reduced by 10

IF severity == "Low":
  → Subtle inline note beneath AI message
  → Contradiction logged silently in Ledger (not auto-expanded)
  → Trust score reduced by 3
```

### System Guarantees for This Edge Case

- The AI response IS shown to the user regardless of contradiction severity.
- The system does NOT withhold or regenerate the response.
- The contradiction is SURFACED, not solved.

---

## 4.2 Incomplete Reasoning

**Scenario:** The AI response fails to address one or more dimensions of the auto-generated evaluation rubric (coverage_score < threshold).

### Detection Flow

```
DURING STAGE 3 (Pass 2 Audit):
  rubric_score.coverage_score < 50 for dimension X
    → rubric_score.gap_description populated
    → NewMissingInfo created: "Rubric dimension '{X}' not addressed: {gap_description}"
    → NewMissingInfo.severity = "High" if coverage_score < 30, else "Medium"

DURING STAGE 4 (Ledger Update):
  missing_info_registry entry appended
  Rubric dimension in ledger.rubric.dimensions updated with new score
```

### User-Facing Routing

```
IF any dimension coverage < 50:
  → Rubric section in Ledger panel highlights that dimension in amber/red
  → Gap description shown as tooltip on hover
  → Missing Info section in Ledger panel gains a new entry

IF coverage < 30 (severe gap):
  → An inline note appended to the AI message:
    "ℹ️ Note: This response does not address [dimension name]. 
     See Ledger → Missing Info for details."
  → Trust score reduced by 5 per severely under-addressed dimension
```

### Follow-up Prompt Surfacing

When the user is about to type their next message, if there are `Medium`+ severity missing info items in the registry, a soft suggestion appears in the chat input area:

```
💡 Tip: The ledger flagged a gap in [dimension]. You could ask: 
   "Can you address [gap_description]?"
```
This is a `st.info()` block, not a button — the user must choose to act on it.

---

## 4.3 Overconfident AI Responses

**Scenario:** Pass 1 generates a definitive-sounding answer (high internal confidence score from Pass 2) that Layer 2 later classifies as `Contested` for multiple key claims.

### Detection Flow

**At Pass 2 time** (before Layer 2 runs):
```
IF audit_result.overall_audit_confidence >= 80:
  AND proportion of "Reasoned" tags >= 0.8 (very few Inferred tags):
    SET turn["internal_confidence_flag"] = "High"
    → Note logged: "Response appears highly confident internally."
```

**When Layer 2 is triggered and completes:**
```
contested_claims = [c for c in grounding_result.claims 
                    if c.classification == "Contested"]

contested_ratio = len(contested_claims) / max(len(grounding_result.claims), 1)

IF turn["internal_confidence_flag"] == "High" AND contested_ratio >= 0.3:
  → CREATE a special "Overconfidence Divergence" contradiction entry:
      description: "This response scored {confidence}/100 on internal logic 
                    but {pct}% of claims are externally contested."
      severity: "High"
      resolution_status: "pending"
```

### User-Facing Routing

```
BEFORE Layer 2:
  → No special indicator. Pass 2 tags render normally.
  → Trust score reflects internal consistency only.

AFTER Layer 2 reveals overconfidence divergence:
  → A high-severity contradiction banner is injected into the chat:
    ┌───────────────────────────────────────────────────────────────────┐
    │ 🔴 OVERCONFIDENCE DIVERGENCE DETECTED                             │
    │ This response was internally consistent (score: 85/100) but       │
    │ external search found 3 of 5 claims to be contested or debated.   │
    │ The AI appeared certain where the evidence is genuinely divided.  │
    │                                                                   │
    │ The system has NOT changed the response. You decide what to trust.│
    │ [Acknowledge & Continue]  [Flag This Turn]                        │
    └───────────────────────────────────────────────────────────────────┘
  → Trust score recalculated with grounding penalty applied.
  → The turn's Reasoned sentence tags are visually demoted:
    a note replaces their tooltip: 
    "Internally Reasoned, but Externally Contested — see grounding."
```

### System Guarantees for This Edge Case

- The contested claims are shown with ALL perspectives, not just the majority view.
- The system does NOT re-rank perspectives by plausibility.
- The system does NOT advise the user which perspective to believe.

---

---

# 5. Implementation Blueprint

## 5.1 Project Directory Structure

```
stateful_ledger/
│
├── app.py                        ← Streamlit entrypoint
│
├── config.py                     ← API keys, model names, thresholds
│
├── schemas/
│   ├── __init__.py
│   ├── audit_schemas.py          ← Pydantic models: AuditResult, SentenceTag, etc.
│   ├── grounding_schemas.py      ← GroundingResult, ClaimClassification
│   └── ledger_schemas.py         ← LedgerSchema (for validation, not runtime dict)
│
├── core/
│   ├── __init__.py
│   ├── ledger.py                 ← init_empty_ledger(), update_ledger(), 
│   │                                compute_trust_score()
│   ├── context_assembly.py       ← assemble_context() → system prompt string
│   └── contradiction_router.py   ← Route contradiction severity, flag overconfidence
│
├── gemini/
│   ├── __init__.py
│   ├── client.py                 ← GeminiClient class: generate(), generate_structured(),
│   │                                run_grounding()
│   ├── prompts.py                ← All prompt templates as Python string constants
│   └── grounding_parser.py       ← Parse Gemini grounding_metadata into ClaimList
│
├── ui/
│   ├── __init__.py
│   ├── chat_panel.py             ← render_chat_panel(col_chat)
│   ├── ledger_panel.py           ← render_ledger_panel(col_ledger)
│   ├── renderers.py              ← render_tagged_response(), render_claim_tags()
│   ├── contradiction_ui.py       ← render_contradiction_banner(), handle callbacks
│   └── styles.py                 ← CSS string injected via st.markdown()
│
└── utils/
    ├── __init__.py
    ├── claim_extractor.py        ← extract_factual_claims(text) → list[str]
    └── deduplication.py          ← deduplicate_missing_info()
```

---

## 5.2 Gemini API Strategy

### Configuring Structured Output (Pass 2)

```python
# gemini/client.py
import google.generativeai as genai
from pydantic import BaseModel

def generate_structured(self, prompt: str, response_schema: type[BaseModel], 
                        temperature: float = 0.0) -> BaseModel | None:
    model = genai.GenerativeModel(
        model_name   = self.audit_model,   # "gemini-1.5-flash"
        system_instruction = AUDIT_SYSTEM_PROMPT,
        generation_config  = genai.GenerationConfig(
            temperature      = temperature,
            response_mime_type = "application/json",
            response_schema    = response_schema,
        )
    )
    try:
        response = model.generate_content(prompt)
        return response_schema.model_validate_json(response.text)
    except Exception as e:
        self._log_error("structured_output_failed", str(e))
        return None
```

### Configuring Google Search Grounding (Layer 2)

```python
# gemini/client.py
def run_grounding(self, claims_prompt: str) -> dict:
    model = genai.GenerativeModel(
        model_name = self.grounding_model,   # "gemini-1.5-pro"
        tools      = [{"google_search": {}}]
    )
    response = model.generate_content(claims_prompt)

    # Extract text content
    text_content = "".join(
        part.text for part in response.candidates[0].content.parts
        if hasattr(part, "text")
    )

    # Extract grounding metadata
    grounding_meta = None
    if hasattr(response.candidates[0], "grounding_metadata"):
        grounding_meta = response.candidates[0].grounding_metadata

    return {
        "text_content"       : text_content,
        "grounding_metadata" : grounding_meta
    }
```

### Model Assignments

| Call   | Purpose                  | Model                | Temperature | Mode             |
|--------|--------------------------|----------------------|-------------|------------------|
| #0     | Rubric Bootstrap         | gemini-1.5-flash     | 0.3         | Structured output|
| #1     | Generation Pass 1        | gemini-1.5-pro       | 0.4         | Standard text    |
| #2     | Internal Audit Pass 2    | gemini-1.5-flash     | 0.0         | Structured output|
| #3     | External Validation      | gemini-1.5-pro       | 0.2         | Grounding tools  |

---

## 5.3 Prioritized Build Checklist

Build in this exact order. Each item is a completable, testable unit.

### Phase 0 — Project Foundation

- [ ] **0.1** Create project directory structure as defined in 5.1.
- [ ] **0.2** Set up `config.py`: load `GEMINI_API_KEY` from `.env`, define `AUDIT_MODEL`, `GENERATION_MODEL`, `GROUNDING_MODEL` constants.
- [ ] **0.3** Install dependencies: `google-generativeai`, `streamlit`, `pydantic`, `python-dotenv`.
- [ ] **0.4** Verify Gemini API connection with a trivial `generate_content` test call in a scratch script.

### Phase 1 — Ledger Core (No UI, No AI)

- [ ] **1.1** Write `core/ledger.py`: implement `init_empty_ledger()` returning the full JSON schema as a Python dict with all fields initialized to empty/null values.
- [ ] **1.2** Write `compute_trust_score(ledger: dict) -> int` using the formula in Section 2.2.
- [ ] **1.3** Write `update_ledger(ledger, audit_result, turn_number)` — pure Python, no AI calls, no Streamlit. Unit-test this function independently.
- [ ] **1.4** Write `core/context_assembly.py`: `assemble_context(ledger, user_prompt) -> str`. Test that it produces the correct prompt structure with injected rules and rubric.

### Phase 2 — Gemini Client Layer

- [ ] **2.1** Write `gemini/prompts.py`: define `RUBRIC_BOOTSTRAP_PROMPT`, `AUDIT_SYSTEM_PROMPT`, `AUDIT_USER_PROMPT_TEMPLATE`, `GROUNDING_PROMPT_TEMPLATE` as string constants. No logic — just strings.
- [ ] **2.2** Write `schemas/audit_schemas.py`: implement all Pydantic models (SentenceTag, RuleCheck, RubricScore, AuditResult, etc.) as defined in Section 2.1.
- [ ] **2.3** Write `gemini/client.py` — `GeminiClient` class with `generate()`, `generate_structured()`, `run_rubric_bootstrap()`, `run_grounding()` methods.
- [ ] **2.4** Test `generate_structured()` end-to-end with a hardcoded sample text against `AuditResult` schema. Confirm Pydantic validation succeeds.
- [ ] **2.5** Write `gemini/grounding_parser.py`: `parse_grounding_metadata(raw_metadata) -> list[ClaimClassification]`. Test with a mock grounding response object.

### Phase 3 — Core Pipeline (No UI)

- [ ] **3.1** Write `app.py` orchestration function `process_turn(user_prompt: str)` calling Stages 0–4 in sequence. No Streamlit calls inside this function — pure data pipeline.
- [ ] **3.2** Add Stage 0 gate: `if ledger["total_turns"] == 0: run_rubric_bootstrap()`. Verify it populates ledger rubric and rules correctly.
- [ ] **3.3** Add Stage 2 + 3 call sequence. Verify `raw_response` and `audit_result` are both written to the turn record.
- [ ] **3.4** Test contradiction detection: craft a prompt that violates a seeded rule. Confirm contradiction appears in `contradiction_log` with `status = "pending"`.
- [ ] **3.5** Write `utils/claim_extractor.py`: a simple sentence-splitter using Python's `re` module (period/question mark boundaries) to extract factual claims. No AI needed for MVP.

### Phase 4 — Streamlit UI (Shell)

- [ ] **4.1** Write `app.py` entrypoint with `st.set_page_config(layout="wide")` and column definition `col_chat, col_ledger = st.columns([65, 35])`. Confirm layout renders.
- [ ] **4.2** Write `ui/styles.py`: inject all CSS overrides (tag classes, sticky column, progress bar colors) via `st.markdown()`.
- [ ] **4.3** Write `ui/chat_panel.py`: render static chat history from `st.session_state.messages` using `st.chat_message()`. No tags yet.
- [ ] **4.4** Write `ui/ledger_panel.py`: render all ledger sections as `st.expander()` blocks showing ledger data. Use placeholder/static data first.
- [ ] **4.5** Wire `st.chat_input()` to call `process_turn()` on submit, then `st.rerun()`.

### Phase 5 — Inline Tag Rendering

- [ ] **5.1** Write `ui/renderers.py`: `render_tagged_response(sentence_tags) -> str`. Outputs HTML string with colored spans.
- [ ] **5.2** Replace plain `st.markdown(raw_response)` in `chat_panel.py` with `st.markdown(render_tagged_response(turn["audit_result"]["sentence_tags"]), unsafe_allow_html=True)`.
- [ ] **5.3** Render the visual legend (Reasoned/Inferred key) below every AI message.
- [ ] **5.4** Test visual output with a 5-sentence response. Verify green/orange tag styling is correct.

### Phase 6 — Contradiction UI & User Controls

- [ ] **6.1** Write `ui/contradiction_ui.py`: `render_contradiction_banner(contradiction: dict)` using the banner layout in Section 2.3.
- [ ] **6.2** Implement the three button callbacks: `handle_accept()`, `handle_override()`, `handle_flag()`. Each mutates `st.session_state.ledger` and calls `st.rerun()`.
- [ ] **6.3** Implement assumption `[✗]` invalidation buttons in `ledger_panel.py`.
- [ ] **6.4** Implement `[Mark Resolved]` for missing info items.
- [ ] **6.5** Implement `[Override]` rule button with `st.text_input()` for reason.
- [ ] **6.6** Test full contradiction lifecycle: create → detect → banner appears → user overrides → ledger updates → banner disappears → trust score recalculates.

### Phase 7 — Layer 2 External Validation

- [ ] **7.1** Add `[G] Verify Facts]` button below each AI message in `chat_panel.py`. Button is keyed to `turn_id`.
- [ ] **7.2** Wire button click to call `process_grounding(turn_id)` which runs Stage 6 pipeline.
- [ ] **7.3** Write `ui/renderers.py`: `render_grounded_response(claims: list[ClaimClassification]) -> str`. Outputs HTML with grounding-colored spans.
- [ ] **7.4** Implement Contested claim expansion using `st.expander()` beneath the message.
- [ ] **7.5** Add grounding summary row to Ledger panel: `✅ N Grounded 🔴 N Contested ⚪ N Unverified`.
- [ ] **7.6** Implement overconfidence divergence detection (Section 4.3) in `core/contradiction_router.py`. Test with a mocked high-confidence turn + high contested ratio.

### Phase 8 — Edge Case Hardening

- [ ] **8.1** Implement rubric gap detection: if `coverage_score < 30`, inject the inline gap note beneath the AI message in `chat_panel.py`.
- [ ] **8.2** Implement the "Tip: You could ask…" suggestion using `st.info()` above `st.chat_input()` when missing info severity >= Medium.
- [ ] **8.3** Add audit failure sentinel: if `generate_structured()` returns `None`, render a graceful warning badge: *"⚠️ Audit unavailable this turn"* without blocking the response.
- [ ] **8.4** Add trust score ceiling for unresolved High-severity contradictions (cap at 60).
- [ ] **8.5** Add missing info deduplication in `utils/deduplication.py` to prevent the same gap from being logged on every turn.

### Phase 9 — Polish & Config

- [ ] **9.1** Add `config.py` constants for all thresholds: `RUBRIC_GAP_THRESHOLD = 50`, `HIGH_SEVERITY_GAP = 30`, `TRUST_CEILING_UNRESOLVED = 60`, `OVERCONFIDENCE_THRESHOLD = 80`, `CONTESTED_RATIO_THRESHOLD = 0.3`.
- [ ] **9.2** Add a `[Reset Session]` button in the Ledger panel header that clears all `st.session_state` and reinitializes.
- [ ] **9.3** Add an `[Export Ledger]` button that downloads the full `st.session_state.ledger` as a JSON file using `st.download_button()`.
- [ ] **9.4** Write a hardcoded disclaimer string rendered below the Trust Score: *"This score reflects internal logical consistency only, not factual accuracy."* — this string must never be conditionally hidden.
- [ ] **9.5** Final CSS pass: verify sticky Ledger column behavior, tag tooltip hover states, and contradiction banner color thresholds render correctly across Chrome/Firefox.

---

## 5.4 Key Constraints Summary (Non-Negotiable Code Rules)

| Rule                                                        | Enforcement Point                          |
|-------------------------------------------------------------|---------------------------------------------|
| Pass 2 Audit always runs; no skip path exists               | `process_turn()` has no conditional bypass  |
| Contradiction status never mutated without user callback    | Only `handle_accept/override/flag()` writes |
| Layer 2 only triggers on explicit button click              | No auto-trigger in any pipeline stage       |
| Trust score label always includes consistency-only caveat   | Hardcoded string in `ledger_panel.py`       |
| Contested claims always show all perspectives               | `contested_perspectives` list always rendered|
| Sentence tags always visible (never hidden by default)      | No CSS `display:none` on `.tag-*` classes   |
| AI response is always shown, even with High contradictions  | `render_chat_panel()` renders before banner |

---

*End of Stateful Ledger MVP Architecture Document v0.1*
