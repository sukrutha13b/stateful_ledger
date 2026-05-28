# Stateful Ledger — MVP System Architecture & Design Document

**Version:** 1.0  
**Stack:** Python · Streamlit · Google Gemini API  
**Scope:** MVP with full dual-layer verification engine

---

## Table of Contents

1. [System Flow & Architecture Breakdown](#1-system-flow--architecture-breakdown)
2. [Core Mechanics — The "How"](#2-core-mechanics--the-how)
3. [User Interaction States](#3-user-interaction-states)
4. [Edge Case Handling & Routing](#4-edge-case-handling--routing)
5. [Implementation Blueprint](#5-implementation-blueprint)

---

## 1. System Flow & Architecture Breakdown

### 1.1 End-to-End Data Flow

```
User Input (chat box)
        │
        ▼
┌─────────────────────────────┐
│   Streamlit Session State   │  ◄─── Editable by user at any time
│        (Ledger DB)          │
│  - rules[]                  │
│  - assumptions[]            │
│  - missing_info[]           │
│  - interaction_history[]    │
│  - rubric{}                 │
│  - trust_score              │
└────────────┬────────────────┘
             │  Ledger context injected into prompt
             ▼
┌─────────────────────────────┐
│   Prompt Assembler          │  Constructs structured system+user prompt
│   (prompt_builder.py)       │  with ledger snapshot embedded
└────────────┬────────────────┘
             │
             ▼
┌─────────────────────────────┐
│   Gemini API Call #1        │  Main generation call
│   (gemini_client.py)        │  Output: structured JSON response
│                             │  - raw_text, reasoning_steps[],
│                             │    claims[], missing_coverage[]
└────────────┬────────────────┘
             │
     ┌───────┴───────┐
     ▼               ▼
┌─────────┐    ┌──────────────┐
│ Layer 1 │    │   Layer 2    │
│ Internal│    │  External    │
│ Logic   │    │ Validation   │
│ Engine  │    │ Engine       │
└────┬────┘    └──────┬───────┘
     │                │
     │  Gemini Call #2 (contradiction check)
     │  Gemini Call #3 (claim classification)
     │                │
     └───────┬────────┘
             ▼
┌─────────────────────────────┐
│   Verified Response Object  │
│  - annotated_text           │
│  - contradiction_flags[]    │
│  - claim_annotations[]      │
│  - completeness_gaps[]      │
│  - rubric_coverage{}        │
└────────────┬────────────────┘
             │
             ▼
┌─────────────────────────────┐
│   Streamlit UI Renderer     │  Renders annotated response
│   (ui_renderer.py)          │  + sidebar panels
└─────────────────────────────┘
```

---

### 1.2 Streamlit Layout Structure

```
├──────────────────────┬──────────────────────────────────────────┤      
│   Right SIDEBAR       │            MAIN CHAT AREA                │
│   (st.sidebar)       │                                          │   
│                      │  ┌──────────────────────────────────┐   │
│  [Ledger State]      │  │  Rubric Card (collapsible)       │   │
│  ─────────────────   │  │  Goal Type: [Analytical]         │   │
│  📋 Rules (3)        │  │  Criteria: [...] [Edit]          │   │
│  ・ rule_1 [edit][x] │  └──────────────────────────────────┘   │
│  ・ rule_2 [edit][x] │                                          │
│  + Add Rule          │  ── Chat History ──────────────────────  │
│                      │                                          │
│  🤔 Assumptions (2)  │  [User]: "..."                           │
│  ・ assumption_1     │                                          │
│                      │  [Assistant Response Block]              │
│  ❓ Missing Info (1) │  ┌────────────────────────────────────┐  │
│  ・ missing_1        │  │ Annotated text with inline badges  │  │
│                      │  │ ● [G] grounded claim               │  │
│  📊 Trust Indicator  │  │ ● [C] contested claim [+views]     │  │
│  ████░░░░ 62%        │  │ ● [U] unverified claim [?]         │  │
│  "Moderate — verify  │  └────────────────────────────────────┘  │
│   externally"        │                                          │
│                      │  [Completeness Tracker]                  │
│  [Reasoning Trace]   │  ✅ Pros covered  ❌ Cons missing        │
│  [Export Ledger]     │                                          │
│                      │  [Contradiction Flags] (if any)          │
│                      │                                          │
│                      │  ── Chat Input ─────────────────────── │
│                      │  [____________________________] [Send]   │
└──────────────────────┴─

```

**Streamlit Layout Code Pattern:**
```python
st.set_page_config(layout="wide")
with st.sidebar:
    render_ledger_panel()       # collapsible sections
    render_trust_indicator()
    render_reasoning_trace()

col_main = st.container()
with col_main:
    render_rubric_card()        # collapsible
    render_chat_history()
    render_input_box()
```

---

### 1.3 Ledger Data Schema

Stored entirely in `st.session_state["ledger"]` as a Python dict:

```python
LEDGER_SCHEMA = {
    "session_id": str,            # UUID, generated at session start

    # ── Core tracking
    "goal_type": str,             # "analytical" | "creative" | "technical" | "exploratory"
    "rubric": {
        "criteria": [str],        # List of evaluation dimensions
        "is_edited_by_user": bool,
        "version": int
    },

    "rules": [                    # User-defined constraints
        {
            "id": str,            # UUID
            "text": str,
            "source": str,        # "user" | "inferred"
            "created_at": int,    # turn index
            "active": bool
        }
    ],

    "assumptions": [              # Model's stated assumptions
        {
            "id": str,
            "text": str,
            "turn_index": int,
            "user_confirmed": bool | None   # None = not reviewed
        }
    ],

    "missing_info": [             # What was unavailable at generation time
        {
            "id": str,
            "text": str,
            "turn_index": int
        }
    ],

    "interaction_history": [      # Full turn log
        {
            "turn_index": int,
            "role": str,          # "user" | "assistant"
            "raw_input": str,
            "verified_response": VerifiedResponseObject,  # see below
            "contradiction_flags": [ContradictionFlag],
            "completeness_gaps": [str],
            "user_feedback": {    # Calibration loop
                "accurate": [int],       # paragraph indices
                "inaccurate": [int],
                "uncertain": [int]
            }
        }
    ],

    "trust_score": float,          # 0.0–1.0, session-level running average
    "turn_count": int
}
```

**VerifiedResponseObject:**
```python
{
    "paragraphs": [
        {
            "index": int,
            "text": str,
            "claims": [
                {
                    "claim_id": str,
                    "text": str,
                    "classification": "grounded" | "contested" | "unverified",
                    "tag": "established" | "reasoned" | "inferred",
                    "perspectives": [str],   # Only if contested, 2–3 items
                    "sources": [str],        # Only if grounded
                    "ledger_rules_used": [str]   # IDs of influencing rules
                }
            ],
            "step_type": "inference" | "assumption" | "established_fact" | None
        }
    ]
}
```

**ContradictionFlag:**
```python
{
    "flag_id": str,
    "conflict_text": str,          # The offending part of the new prompt/output
    "conflicting_rule_id": str,    # ID of the ledger rule it violates
    "conflict_message": str,       # e.g. "This conflicts with [rule]. You can..."
    "resolution": None | "update_rule" | "override_once" | "flag_tension",
    "resolved_at": int | None      # turn index
}
```

---

### 1.4 Layer 1 & 2 Processing — Detailed Data Flow

```
LAYER 1: INTERNAL LOGIC ENGINE
─────────────────────────────────────────────────────
Input:  user_input + ledger_snapshot + raw_gemini_response

Step 1.1 — Contradiction Scan
  │  Compare new user_input against all active ledger rules
  │  Gemini Call #2: "Given these rules: {rules}
  │                   Does this prompt/response violate any?
  │                   Return JSON: {violations: [{rule_id, conflict_text}]}"
  ▼
Step 1.2 — Completeness Audit
  │  Compare rubric.criteria[] against response paragraph coverage
  │  For each criterion: does any paragraph address it? → flag gap if not
  ▼
Step 1.3 — Assumption + Missing Info Extraction
  │  Gemini Call embedded in Call #1 via structured output:
  │  "List all assumptions made and any information that was
  │   unavailable to you when generating this response."
  ▼
Step 1.4 — Reasoning Step Tagging
  │  Each paragraph tagged: "inference" | "assumption" | "established_fact"
  │  Done as part of Gemini Call #1 structured output
  ▼
Step 1.5 — Ledger Update
     Append new assumptions, missing_info, interaction turn


LAYER 2: EXTERNAL VALIDATION ENGINE
─────────────────────────────────────────────────────
Input:  claims[] extracted from raw_gemini_response

Step 2.1 — Claim Extraction
  │  Parse structured JSON from Gemini Call #1 to get discrete claims[]
  ▼
Step 2.2 — Claim Classification
  │  Gemini Call #3 with Google Search grounding enabled:
  │  "For each claim below, classify as:
  │    - grounded: confirmed by multiple high-agreement sources
  │    - contested: valid but one position in an active debate
  │    - unverified: no grounding found
  │   For contested claims, provide 2–3 alternative framings.
  │   Return JSON: {claims: [{claim_id, classification, perspectives[], sources[]}]}"
  ▼
Step 2.3 — Annotation Merge
     Merge claim classifications back into VerifiedResponseObject paragraphs
```

---

## 2. Core Mechanics — The "How"

### 2.1 Output Evaluation Logic

**Gemini Call #1 — Main Generation (Structured Output)**

System prompt template:
```
You are a precise reasoning assistant operating within a Stateful Ledger system.

ACTIVE LEDGER STATE:
Rules: {rules_list}
Assumptions established: {assumptions_list}
Goal type: {goal_type}
Rubric criteria: {rubric_criteria}

INSTRUCTIONS:
1. Generate a response to the user's query.
2. For EACH paragraph, tag its reasoning type:
   - "established_fact": grounded in prior session context or verifiable data
   - "reasoned": derived logically from ledger rules and stated assumptions
   - "inferred": generated without explicit grounding
3. List all assumptions you are making in this response.
4. List all information that was NOT available to you.
5. Extract discrete factual claims as a flat list.

Return ONLY valid JSON matching this schema: {json_schema}
```

**Gemini Call #2 — Contradiction Check**
```
Given these active rules: {rules}
And this user prompt: {user_input}
And this assistant response: {response}

Identify any contradictions between the new content and the established rules.
Return JSON: { "violations": [{"rule_id": "...", "conflict_text": "...", "severity": "direct"|"tension"}] }
If no contradictions, return: { "violations": [] }
```

**Gemini Call #3 — Claim Classification (with Search Grounding)**
```
Classify each of these claims. Use Google Search grounding where available.
For each claim, return:
- classification: "grounded" | "contested" | "unverified"
- perspectives: [] (only if contested — 2 to 3 alternative framings, neutral phrasing)
- sources: [] (only if grounded — brief source descriptions)

Claims: {claims_list}

Return ONLY valid JSON: { "classified_claims": [...] }
```

---

### 2.2 How Uncertainty Is Surfaced

**Inline Claim Badges (rendered via st.markdown with HTML):**

| State | Visual | Tooltip |
|---|---|---|
| Grounded | `🟢 G` green badge | "Confirmed by multiple sources" |
| Contested | `🟡 C` amber badge + expand arrow | "Multiple valid positions exist" |
| Unverified | `🔴 U` red badge | "No grounding found — treat as model inference" |

**Claim Expansion (Contested):**
When user clicks `[C]` badge → `st.expander` opens inline:
```
This claim is framed one way here.
2–3 alternative framings exist:
  → Framing A: "..."
  → Framing B: "..."
  → Framing C: "..."
The system does not indicate which is correct.
[Mark as reviewed]
```

**Inference vs. Fact Differentiator Tags (inline, subtle):**

| Tag | Label | Style |
|---|---|---|
| `established` | `[fact]` | Gray, small caps |
| `reasoned` | `[reasoned]` | Blue, small caps |
| `inferred` | `[inferred]` | Amber italic |

Rendered as `st.caption`-style annotation after each paragraph, not interrupting reading flow.

---

### 2.3 Confidence Communication — 3-State Classification UI

```python
def render_claim_badge(claim: dict) -> str:
    if claim["classification"] == "grounded":
        return "🟢"
    elif claim["classification"] == "contested":
        return "🟡"
    else:
        return "🔴"
```

**Trust Indicator (sidebar):**
```
Session Trust: ████░░░░ 62%
─────────────────────────
Based on 8 rated sections.
Moderate reliability for this task type.
Verify contested and unverified claims externally.
```
- Calculated as: `(accurate_count) / (accurate + inaccurate + uncertain) * weight_map`
- Weight map: accurate=1.0, uncertain=0.5, inaccurate=0.0
- Rendered with `st.progress()` + qualitative label (Low / Moderate / High)

---

### 2.4 User Control — Interactive Elements

**Contradiction Flag Resolution Widget:**
```
⚠️  CONTRADICTION DETECTED
─────────────────────────────────────────────
This response conflicts with Rule #2:
  Rule: "Analysis must remain vendor-neutral"
  Conflict: "The response implicitly favours AWS over alternatives"

Choose how to proceed:
  [Update the Rule]   [Override for this response]   [Flag the Tension]
```
Each button calls a handler that writes to `st.session_state["ledger"]`:
- **Update Rule**: opens inline text editor for that rule
- **Override Once**: marks the flag `resolution="override_once"`, proceeds
- **Flag Tension**: marks `resolution="flag_tension"`, both versions coexist visibly

**Ledger Edit Controls (sidebar):**
- Each rule/assumption has `[✏️ Edit]` and `[✕ Remove]` inline buttons
- `[+ Add Rule]` button opens a `st.text_input` → saves to `ledger.rules[]`
- All edits update `st.session_state` immediately and persist for the session

**Calibration Feedback (per response paragraph):**
```
Was this section: [✅ Accurate]  [❌ Inaccurate]  [❓ Uncertain]
```
Rendered as `st.feedback` or three compact `st.button` calls below each paragraph block. Signals write to `interaction_history[turn].user_feedback`.

---

## 3. User Interaction States

### 3.1 State Machine Overview

```
[INITIAL STATE]          [RUBRIC GENERATION]
 Session starts    ──►   First prompt received
                         Gemini infers goal type
                         Rubric card shown (editable)
                         User confirms or edits rubric
                              │
                              ▼
                    [GENERATING STATE]
                    Spinner shown
                    Calls #1, #2, #3 run concurrently*
                    (* #2 and #3 depend on #1 output)
                              │
                              ▼
                    [VERIFICATION REVIEW STATE]
                    Annotated response displayed
                    Contradiction flags shown (if any)
                    Completeness gaps flagged
                    Claim badges rendered inline
                              │
                    User rates paragraphs (optional)
                              │
                              ▼
                    [CALIBRATED STATE]
                    Trust indicator updated
                    Ledger updated with new turn
                    Ready for next input
```

### 3.2 State: Initial / Rubric Generation

**Trigger:** First message sent in a new session.

**Flow:**
1. Prompt Assembler sends the user's first message to Gemini with instruction: *"Infer the goal type (analytical, creative, technical, exploratory) and generate a 3–5 item evaluation rubric. Return JSON: `{goal_type, rubric_criteria[]}`"*
2. Rubric card rendered at top of chat as an editable `st.form`:
   ```
   📋 Session Rubric — [Analytical]
   ─────────────────────────────
   This rubric will be used to evaluate response completeness.
   ✎ Criterion 1: [Accuracy of claims        ]
   ✎ Criterion 2: [Coverage of counter-args  ]
   ✎ Criterion 3: [Source attribution        ]
   [+ Add criterion]       [Confirm & Proceed]
   ```
3. User confirms or edits, then the rubric is locked into `ledger.rubric`.
4. The first substantive response is then generated using the confirmed rubric.

### 3.3 State: Generating

**Trigger:** User submits any message (post-rubric).

**UI:**
- `st.spinner("Generating and verifying response…")`
- Sidebar shows "Verification in progress…" with a progress bar
- Chat input disabled

**Backend pipeline (sequential — each step feeds the next):**
1. `prompt_builder.build()` → structured prompt
2. `gemini_client.generate()` → Call #1 → raw `VerifiedResponseObject`
3. `layer1_engine.check()` → Call #2 → `contradiction_flags[]`
4. `layer2_engine.classify()` → Call #3 → `claim_annotations[]`
5. `ledger.update(turn_data)` → session state written

### 3.4 State: Verification Review

**Trigger:** All three Gemini calls complete.

**UI elements rendered:**
- Annotated response paragraphs with inline claim badges
- Contradiction flags (if any) rendered as warning boxes with resolution buttons
- Completeness tracker (green check / red X per rubric criterion)
- Reasoning Trace (collapsible): lists ledger rules used, gap-bridging inferences, missing info
- Per-paragraph calibration buttons

**Ambiguity Preservation:** If Gemini's Call #1 returns `goal_type_ambiguous: true` or the completeness tracker detects a genuinely open question, the response block is prefaced with:
```
⚠️ Open Question Detected
This query involves a genuinely unsettled issue. The response presents
competing positions without adjudicating between them.
```

### 3.5 State: Calibrated

**Trigger:** User clicks any calibration button (Accurate / Inaccurate / Uncertain).

**Flow:**
1. `ledger.interaction_history[turn].user_feedback` updated
2. `trust_score` recalculated across all rated turns
3. Sidebar trust indicator re-renders immediately via `st.rerun()`
4. No model behaviour changes — this is a user-facing signal only

### 3.6 Ledger Edit Workflow

Any edit to a rule or assumption in the sidebar triggers:
1. `st.session_state["ledger"]["rules"]` updated
2. A non-intrusive `st.toast("Ledger updated.")` confirmation shown
3. On the next user message, the updated ledger is injected into the prompt — no retroactive re-evaluation of past turns

### 3.7 User as Final Judge — Design Guarantees

The following are implemented as hard constraints, not guidelines:

| Guarantee | Implementation |
|---|---|
| System never resolves contradictions | Resolution buttons require explicit user click; no default action |
| Contested claims never adjudicated | Perspectives shown in neutral phrasing; no "correct framing" indicated |
| Calibration loop never modifies model | Trust score is UI-only; never passed to Gemini API |
| Rubric shown before first response | Generation blocked until user confirms or dismisses rubric |
| Missing info always surfaced | Gemini explicitly instructed to list unavailable information in Call #1 |

---

## 4. Edge Case Handling & Routing

### 4.1 Conflicting Outputs — New Prompt vs. Established Rule

**Detection:** Layer 1, Step 1.1 (Contradiction Scan — Call #2)

**Routing Logic:**
```python
if contradiction_flags:
    for flag in contradiction_flags:
        if flag["severity"] == "direct":
            # Block response rendering, show resolution UI first
            render_contradiction_widget(flag)
            st.stop()   # Halt until user resolves
        elif flag["severity"] == "tension":
            # Render response but prepend tension notice
            render_tension_notice(flag)
            render_response()
```

**Flag message format (exact copy displayed to user):**
> *"This conflicts with Rule [N]: '[rule text]'. You can update the rule, override for this response, or keep both and I'll flag the tension."*

**Post-resolution:** If user selects "Update Rule", the rule editor opens inline. The original response is regenerated (Call #1 re-run) using the updated rule set.

---

### 4.2 Incomplete Reasoning — Rubric Gap

**Detection:** Layer 1, Step 1.2 (Completeness Audit)

**Logic:**
```python
for criterion in ledger["rubric"]["criteria"]:
    covered = any(
        criterion_keyword in paragraph["text"].lower()
        for paragraph in response["paragraphs"]
    )
    # Also use Gemini to do semantic match if keyword match fails
    if not covered:
        completeness_gaps.append(criterion)
```

**UI Rendering:**
```
📋 Completeness Check
─────────────────────
✅ Criterion 1 (Accuracy): Addressed
✅ Criterion 2 (Counter-arguments): Addressed
❌ Criterion 3 (Source attribution): Not addressed

Would you like to:  [Request missing coverage]   [Mark as intentionally skipped]
```

- **Request coverage:** Automatically appends a follow-up prompt: *"Please address the following from the rubric that was not covered: [criterion]"*
- **Mark as skipped:** Flags the criterion as `intentionally_skipped: true` in the rubric; removes it from future completeness checks for this turn

---

### 4.3 Overconfident AI on Contested Topics

**Detection:** Layer 2, Step 2.2 (Claim Classification — Call #3)

**Condition:** A claim is classified as `contested` but the generated text presents it definitively (detected by checking if the source paragraph has `step_type: "established_fact"` while the claim is `contested`).

**Routing:**
```python
for claim in claims:
    if (claim["classification"] == "contested"
            and paragraph["step_type"] == "established_fact"):
        claim["overconfidence_flag"] = True
```

**UI Display:**
```
🟡 PERSPECTIVE FLAG
─────────────────────────────────────────────
This claim is presented as settled, but it represents one position
in an active debate. 2–3 alternative framings exist:

  → "..."
  → "..."
  → "..."

The system does not indicate which framing is correct.
[Dismiss]  [Add to Ledger as Contested]
```

The response text itself is **not modified**. The original phrasing is preserved and the flag appears alongside it. The user decides what to do with the information.

---

### 4.4 Additional Edge Cases

| Scenario | Handling |
|---|---|
| Gemini returns malformed JSON | `try/except` with fallback: display raw text, skip annotation, show error banner |
| All claims unverified (grounding unavailable) | Surface a session-level notice: "Google Search grounding returned no results for this query. All claims are unverified." |
| User edits a rule mid-session | Ledger updated; toast shown: "Rule updated. This will apply to all future responses in this session." Past turns not retroactively changed. |
| Ambiguous first prompt (no clear goal type) | Display rubric with `goal_type: "exploratory"` as default; prompt user to confirm before proceeding |
| User dismisses rubric without editing | Rubric stored as-is with `is_edited_by_user: false`; flagged subtly in sidebar |

---

## 5. Implementation Blueprint

### 5.1 Module & File Structure

```
stateful_ledger/
│
├── app.py                   # Streamlit entry point
├── config.py                # API keys, model names, constants
│
├── ledger/
│   ├── __init__.py
│   ├── schema.py            # LEDGER_SCHEMA dataclass definitions
│   ├── manager.py           # init_ledger(), update_ledger(), get_snapshot()
│   └── trust.py             # calculate_trust_score()
│
├── engine/
│   ├── __init__.py
│   ├── prompt_builder.py    # build_main_prompt(), build_contradiction_prompt(),
│   │                        # build_classification_prompt()
│   ├── gemini_client.py     # call_gemini() with retry + JSON parsing
│   ├── layer1.py            # run_layer1(response, ledger) → flags, gaps, tags
│   └── layer2.py            # run_layer2(claims) → classified_claims
│
├── ui/
│   ├── __init__.py
│   ├── sidebar.py           # render_ledger_panel(), render_trust_indicator()
│   ├── chat.py              # render_chat_history(), render_response_block()
│   ├── rubric.py            # render_rubric_card()
│   ├── flags.py             # render_contradiction_widget(), render_tension_notice()
│   ├── completeness.py      # render_completeness_tracker()
│   ├── claims.py            # render_claim_badges(), render_contested_expander()
│   └── calibration.py      # render_calibration_buttons()
│
└── utils/
    ├── json_parser.py       # safe_parse_json() with fallback
    └── id_gen.py            # generate_id()
```

---

### 5.2 Prioritised Implementation Checklist

Work through each phase in order. Each phase is independently testable.

---

#### PHASE 1 — Skeleton & State Foundation
*Goal: Streamlit app runs, ledger initialises, raw Gemini response displayed.*

- [ ] **1.1** `config.py`: Set `GEMINI_API_KEY`, `MODEL_NAME = "gemini-2.0-flash"`, `MAX_TOKENS = 4096`
- [ ] **1.2** `ledger/schema.py`: Define `LEDGER_SCHEMA` as a typed dict or Python dataclass
- [ ] **1.3** `ledger/manager.py`: Implement `init_ledger()` → writes to `st.session_state["ledger"]`; implement `get_snapshot()` → returns serialisable dict for prompt injection
- [ ] **1.4** `gemini_client.py`: Implement `call_gemini(prompt: str, use_search_grounding: bool = False) -> dict` — bare API call, returns parsed JSON or raw text on failure
- [ ] **1.5** `app.py`: Basic Streamlit layout — sidebar + main chat column, `st.chat_input()`, call `init_ledger()` on first run
- [ ] **1.6** Wire up: user input → `call_gemini()` → display raw response text. **Checkpoint: chat works end-to-end.**

---

#### PHASE 2 — Structured Gemini Output (Call #1)

*Goal: Gemini returns structured JSON with paragraphs, claims, assumptions, missing info.*

- [ ] **2.1** `prompt_builder.py`: Implement `build_main_prompt(user_input, ledger_snapshot)` — injects ledger state, requests structured JSON output
- [ ] **2.2** Define the Call #1 JSON output schema (inline in system prompt or as a Pydantic model for validation)
- [ ] **2.3** `utils/json_parser.py`: Implement `safe_parse_json(text)` — strips markdown fences, handles malformed output with graceful fallback
- [ ] **2.4** Test Call #1 output: confirm paragraphs, claims, step_type tags, assumptions, missing_info are all returned correctly
- [ ] **2.5** `ledger/manager.py`: Add `update_ledger(turn_data)` — appends to `interaction_history`, updates `assumptions` and `missing_info` lists
- [ ] **2.6** `ui/chat.py`: Implement `render_response_block(verified_response)` — renders paragraphs with `step_type` tags. **Checkpoint: annotated text renders with [fact]/[reasoned]/[inferred] labels.**

---

#### PHASE 3 — Rubric Generation

*Goal: First-turn rubric card shown, user can confirm or edit before first response.*

- [ ] **3.1** `prompt_builder.py`: Add `build_rubric_prompt(user_input)` — asks Gemini to infer goal type and return `{goal_type, rubric_criteria[]}`
- [ ] **3.2** `ui/rubric.py`: Implement `render_rubric_card(rubric)` — `st.form` with editable criteria fields, confirm button
- [ ] **3.3** `app.py`: Add session flag `ledger["rubric_confirmed"]`; block main generation until True
- [ ] **3.4** Test: first message shows rubric, generation only starts after user confirms. **Checkpoint: rubric flow works.**

---

#### PHASE 4 — Layer 1: Internal Logic Engine

*Goal: Contradiction detection and completeness tracking work.*

- [ ] **4.1** `prompt_builder.py`: Add `build_contradiction_prompt(rules, user_input, response)`
- [ ] **4.2** `engine/layer1.py`: Implement `run_contradiction_check(response, ledger)` → Call #2 → returns `contradiction_flags[]`
- [ ] **4.3** `engine/layer1.py`: Implement `run_completeness_audit(response, rubric)` → returns `completeness_gaps[]`; use keyword match + optional semantic Gemini call for fuzzy matching
- [ ] **4.4** `ui/flags.py`: Implement `render_contradiction_widget(flag)` — warning box with three resolution buttons; button callbacks update `st.session_state`
- [ ] **4.5** `ui/completeness.py`: Implement `render_completeness_tracker(gaps, criteria)` — ✅/❌ per criterion with action buttons
- [ ] **4.6** Test with a deliberate rule violation prompt. **Checkpoint: contradiction flag appears and resolves.**

---

#### PHASE 5 — Layer 2: External Validation Engine

*Goal: Claims classified as Grounded / Contested / Unverified with inline badges.*

- [ ] **5.1** `prompt_builder.py`: Add `build_classification_prompt(claims_list)`
- [ ] **5.2** `engine/layer2.py`: Implement `run_claim_classification(claims)` → Call #3 with `use_search_grounding=True` → returns `classified_claims[]`
- [ ] **5.3** `ui/claims.py`: Implement `render_claim_badges(paragraph, claims)` — inline 🟢🟡🔴 badges; implement `render_contested_expander(claim)` — `st.expander` with alternative perspectives
- [ ] **5.4** Implement overconfidence flag detection: compare `claim.classification` vs `paragraph.step_type`, set `overconfidence_flag` where mismatch
- [ ] **5.5** Test with a contested claim (e.g., a policy or scientific debate). **Checkpoint: contested claim shows perspectives panel.**

---

#### PHASE 6 — Sidebar Ledger Panel

*Goal: Live editable ledger visible in sidebar.*

- [ ] **6.1** `ui/sidebar.py`: Implement `render_ledger_panel()` — three collapsible sections: Rules, Assumptions, Missing Info
- [ ] **6.2** Each rule row: inline `st.text_input` (edit mode), `[✕]` delete button
- [ ] **6.3** `[+ Add Rule]` button: appends blank rule to `ledger["rules"]`, triggers `st.rerun()`
- [ ] **6.4** `ui/sidebar.py`: Implement `render_reasoning_trace(turn)` — collapsible panel showing rules used, inference bridges, missing info for the current turn
- [ ] **6.5** Test: edit a rule, send a follow-up message, confirm updated rule appears in the next prompt. **Checkpoint: ledger edits persist and propagate.**

---

#### PHASE 7 — Calibration Feedback Loop & Trust Indicator

*Goal: User can rate paragraphs; trust score updates in sidebar.*

- [ ] **7.1** `ui/calibration.py`: Implement `render_calibration_buttons(turn_index, para_index)` — three compact buttons; callbacks update `ledger.interaction_history[turn].user_feedback`
- [ ] **7.2** `ledger/trust.py`: Implement `calculate_trust_score(interaction_history)` — weighted average across all rated paragraphs
- [ ] **7.3** `ui/sidebar.py`: Implement `render_trust_indicator(trust_score)` — `st.progress()` bar + qualitative label
- [ ] **7.4** Ensure `st.rerun()` is called after any feedback button click so trust indicator updates immediately
- [ ] **7.5** Verify: trust score is never passed to Gemini. Audit `gemini_client.py` to confirm. **Checkpoint: feedback loop is purely cosmetic/user-facing.**

---

#### PHASE 8 — Polish & Edge Case Hardening

- [ ] **8.1** `app.py`: Add `[Reset Session]` button that clears `st.session_state` and reruns
- [ ] **8.2** `gemini_client.py`: Add retry logic (3 attempts, exponential backoff) for API failures
- [ ] **8.3** Add `[Export Ledger]` button in sidebar: `st.download_button` with `json.dumps(ledger)` as UTF-8 file
- [ ] **8.4** Handle malformed JSON from any Gemini call: fallback to raw text display + `st.warning("Verification unavailable for this turn")`
- [ ] **8.5** Test ambiguous first prompt → verify `goal_type: "exploratory"` default is used
- [ ] **8.6** Test empty Google Search grounding result → verify "all claims unverified" session notice
- [ ] **8.7** Final audit: verify all five "What the system explicitly does not do" constraints from the spec are enforced in code

---

### 5.3 Gemini API Prompt Strategy Summary

| Call | Purpose | Grounding | Output Format | Estimated tokens |
|---|---|---|---|---|
| Call #1 (Rubric) | Infer goal type + rubric | Off | JSON: `{goal_type, rubric_criteria[]}` | ~500 out |
| Call #1 (Main) | Generate structured response | Off | JSON: `{paragraphs[], assumptions[], missing_info[]}` | ~2000 out |
| Call #2 | Contradiction check | Off | JSON: `{violations[]}` | ~300 out |
| Call #3 | Claim classification | **On** | JSON: `{classified_claims[]}` | ~800 out |

**Key prompt engineering rules:**
- All calls use `response_mime_type: "application/json"` where supported by the model version
- System prompt always includes: `"Return ONLY valid JSON. No markdown fences. No preamble."`
- Ledger snapshot in Call #1 is capped at last 10 turns to stay within context window
- Call #3 sends claims as a numbered list with IDs so classifications can be merged back by ID

---

*End of Architecture Document*
