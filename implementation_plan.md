# Stateful Ledger — MVP Implementation Plan

> **Source documents:** [Architecture v2](file:///d:/Projects/Graduation%20Project%202/stateful_ledger/Stateful_Ledger_Architecture_v2.md) · [Solution.md](file:///d:/Projects/Graduation%20Project%202/stateful_ledger/Solution.md) · [Architecture Diagram](file:///d:/Projects/Graduation%20Project%202/stateful_ledger/stateful_ledger_architecture.jpg) · [Gemini Design Language](file:///d:/Projects/Graduation%20Project%202/stateful_ledger/design%20language.md)
>
> **Stack:** Python 3.11+ · Streamlit · Google Gemini API (`google-genai`) · pytest
>
> **Design System:** Gemini Design Language (Dark Mode) — Material 3-inspired
>
> **Target directory:** `d:\Projects\Graduation Project 2\stateful_ledger\`

---

## User Review Required

> [!IMPORTANT]
> **API Key**: You will need a valid Google Gemini API key. The plan assumes you'll set it via a `.env` file or `GEMINI_API_KEY` environment variable. Please confirm your preferred method.

> [!IMPORTANT]
> **Google Search Grounding**: Layer 2 (Call #3) requires Google Search grounding enabled on the Gemini API. This is available on `gemini-2.0-flash` and above. Please confirm your API plan supports this feature.

> [!WARNING]
> **Model Selection**: The architecture specifies `gemini-2.0-flash`. If you want a different model (e.g., `gemini-2.5-flash` for better structured output), please indicate.

## Open Questions — ✅ All Resolved

> [!NOTE]
> 1. ✅ **API key storage**: `.env` file with `python-dotenv`. User provides the key.
> 2. ✅ **Model version**: Configurable parameter in `config.py`. Default: `gemini-2.0-flash`. Can be swapped without code changes.
> 3. ✅ **Session persistence**: Ephemeral by default + optional JSON file export/import via sidebar button.

---

## Design System Reference — Gemini Design Language (Dark Mode)

All UI (local dev dashboard + Streamlit) must follow the [Gemini Design Language](file:///d:/Projects/Graduation%20Project%202/stateful_ledger/design%20language.md) exactly. Key tokens:

### Color Palette

| Token | Hex | Usage |
|---|---|---|
| `BASE_BG` | `#131314` | Main canvas, empty states |
| `SURFACE_LOW` | `#1E1F20` | Sidebar, floating input bar, cards |
| `SURFACE_HIGH` | `#282A2C` | Hover states, tooltips, file cards |
| `TEXT_PRIMARY` | `#E2E2E2` | User prompts, AI responses, active elements |
| `TEXT_SECONDARY` | `#C4C7C5` | Timestamps, placeholder text, inactive icons |
| `ACCENT_GREEN` | `#1E8E3E` | User avatar, success/grounded indicators |
| `CLAIM_GROUNDED` | `#1E8E3E` | 🟢 Grounded claim badge |
| `CLAIM_CONTESTED` | `#F9AB00` | 🟡 Contested claim badge (amber) |
| `CLAIM_UNVERIFIED` | `#EA4335` | 🔴 Unverified claim badge |
| `AMBIENT_GLOW` | Radial gradient: deep indigo → purple → `BASE_BG` | Subtle background glow |
| `GEMINI_SPARK` | Gradient: Blue → Red/Orange → Yellow → Green | Brand accent |

### Typography

| Style | Font | Size | Weight | Line Height |
|---|---|---|---|---|
| Display/Greeting | Google Sans | 32px | Medium | 1.3 |
| Body (Chat) | Google Sans / system sans-serif | 16px | Regular | 1.5 |
| UI Labels | Google Sans / system sans-serif | 14px | Medium | 1.4 |
| Captions/Tags | Google Sans / system sans-serif | 12px | Regular | 1.3 |

### Shape & Elevation

| Element | Border Radius | Notes |
|---|---|---|
| Pill shapes (input, buttons) | `50px` | Fully rounded |
| Cards, panels, expanders | `12–16px` | Soft rounded rectangles |
| Elevation | None | Use color step-ups (`BASE_BG` → `SURFACE_LOW` → `SURFACE_HIGH`), not shadows |

### Core Principles

- **Focus-Driven** — Interface melts away to prioritize conversation
- **Fluid & Organic** — Generous rounded corners, soft gradient glows
- **Progressive Disclosure** — Advanced features collapsed by default

---

## Final File Structure

```
stateful_ledger/
│
├── app.py                        # Streamlit entry point
├── config.py                     # API keys, model names, constants
├── requirements.txt              # Dependencies
├── .env                          # API key (gitignored)
├── .gitignore
│
├── .streamlit/
│   └── config.toml               # Streamlit theme config (Gemini dark mode)
│
├── dev_dashboard/                # LOCAL development dashboard (HTML/JS)
│   └── index.html                # Single-file dashboard — no server needed
│
├── ledger/
│   ├── __init__.py
│   ├── schema.py                 # Dataclass definitions for all schema objects
│   ├── manager.py                # init_ledger(), update_ledger(), get_snapshot()
│   └── trust.py                  # calculate_trust_score()
│
├── engine/
│   ├── __init__.py
│   ├── prompt_builder.py         # All prompt construction functions
│   ├── gemini_client.py          # Gemini API wrapper with retry + JSON parsing
│   ├── layer1.py                 # Internal Logic Engine (contradiction + completeness)
│   └── layer2.py                 # External Validation Engine (claim classification)
│
├── ui/
│   ├── __init__.py
│   ├── theme.py                  # Gemini Design Language tokens + CSS injection
│   ├── sidebar.py                # Ledger panel, trust indicator, reasoning trace
│   ├── chat.py                   # Chat history, response blocks
│   ├── rubric.py                 # Rubric card with editable form
│   ├── flags.py                  # Contradiction widgets, tension notices
│   ├── completeness.py           # Completeness tracker UI
│   ├── claims.py                 # Claim badges, contested expanders
│   └── calibration.py            # Per-paragraph feedback buttons
│
├── utils/
│   ├── __init__.py
│   ├── json_parser.py            # Safe JSON parsing with fallback
│   └── id_gen.py                 # UUID generation helper
│
└── tests/
    ├── __init__.py
    ├── conftest.py               # Shared fixtures (mock ledger, mock responses)
    ├── test_schema.py            # Phase 1 — schema validation
    ├── test_manager.py           # Phase 1 — ledger init/update/snapshot
    ├── test_json_parser.py       # Phase 2 — JSON parsing edge cases
    ├── test_gemini_client.py     # Phase 2 — API call mocking
    ├── test_prompt_builder.py    # Phase 3 — prompt construction
    ├── test_rubric.py            # Phase 4 — rubric generation/editing
    ├── test_layer1.py            # Phase 5 — contradiction + completeness
    ├── test_layer2.py            # Phase 6 — claim classification
    ├── test_trust.py             # Phase 7 — trust score calculation
    ├── test_calibration.py       # Phase 7 — calibration feedback logic
    ├── test_edge_cases.py        # Phase 9 — malformed JSON, empty grounding, etc.
    └── test_integration.py       # Phase 9 — full pipeline end-to-end
```

---

## Phase 0 — Local Development Dashboard

*Goal: A local HTML/JS dashboard you can open in the browser to track implementation progress, inspect ledger state, and test the pipeline — no Streamlit hosting needed.*

### [NEW] [index.html](file:///d:/Projects/Graduation%20Project%202/stateful_ledger/dev_dashboard/index.html)

A single-file, self-contained HTML+CSS+JS application that:

1. **Implementation Progress Tracker** — Checkbox list mirroring all 12 phases; tracks % completion with a visual progress bar
2. **Ledger State Inspector** — Paste/load a JSON ledger snapshot and browse rules, assumptions, missing info, trust score in a structured view
3. **Pipeline Simulator** — Paste raw Gemini JSON responses and see how they'd be rendered (claim badges, contradiction flags, completeness checks)
4. **Mock Chat Interface** — Mirrors the final Streamlit layout so you can preview how the UI will look before hosting

**Design — Gemini Design Language (exact tokens):**
- **Background:** `#131314` base canvas, `#1E1F20` sidebar/cards, `#282A2C` hover states
- **Typography:** `#E2E2E2` primary text, `#C4C7C5` secondary text, Google Sans font via CDN
- **Shapes:** Pill inputs (`border-radius: 50px`), rounded cards (`border-radius: 12px`)
- **Elevation:** Zero shadows — hierarchy via color step-ups only
- **Ambient glow:** Soft radial gradient (deep indigo/purple) behind greeting text
- **Claim badges:** `#1E8E3E` grounded, `#F9AB00` contested, `#EA4335` unverified
- **Layout:** Sidebar (280px, `SURFACE_LOW`) + main panel (`BASE_BG`) matching Streamlit target
- No external dependencies — pure HTML/CSS/JS, open `index.html` directly in browser

**Unit Tests:** N/A (static HTML file, tested by opening in browser)

---

## Phase 1 — Project Scaffolding & Dependencies

*Goal: Project initialised, dependencies installed, linting passing.*

### [NEW] [requirements.txt](file:///d:/Projects/Graduation%20Project%202/stateful_ledger/requirements.txt)

```
streamlit>=1.45.0
google-genai>=1.16.0
python-dotenv>=1.1.0
pytest>=8.3.0
pytest-mock>=3.14.0
```

### [NEW] [.env](file:///d:/Projects/Graduation%20Project%202/stateful_ledger/.env)

```
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL=gemini-2.0-flash
```

> [!TIP]
> To switch models later, just change `GEMINI_MODEL` in `.env` — no code changes needed. e.g. `GEMINI_MODEL=gemini-2.5-flash`

### [NEW] [.gitignore](file:///d:/Projects/Graduation%20Project%202/stateful_ledger/.gitignore)

```
.env
__pycache__/
*.pyc
.pytest_cache/
```

### [NEW] [.streamlit/config.toml](file:///d:/Projects/Graduation%20Project%202/stateful_ledger/.streamlit/config.toml)

Streamlit's built-in theme engine mapped to Gemini Design Language tokens:

```toml
[theme]
base = "dark"
primaryColor = "#8AB4F8"              # Gemini blue accent
backgroundColor = "#131314"            # BASE_BG — deepest charcoal
secondaryBackgroundColor = "#1E1F20"   # SURFACE_LOW — sidebar, cards
textColor = "#E2E2E2"                  # TEXT_PRIMARY — off-white
font = "sans serif"                    # Falls back to system sans-serif
```

### [NEW] [ui/theme.py](file:///d:/Projects/Graduation%20Project%202/stateful_ledger/ui/theme.py)

Design tokens as Python constants + CSS injection function for Streamlit:

```python
import streamlit as st

# ══════════════════════════════════════════════════════
# GEMINI DESIGN LANGUAGE — DESIGN TOKENS
# Source: design language.md
# ══════════════════════════════════════════════════════

# ── Backgrounds & Surfaces ──
BASE_BG = "#131314"              # Main canvas, empty states
SURFACE_LOW = "#1E1F20"          # Sidebar, floating input bar, cards
SURFACE_HIGH = "#282A2C"         # Hover states, tooltips

# ── Typography ──
TEXT_PRIMARY = "#E2E2E2"         # User prompts, AI responses
TEXT_SECONDARY = "#C4C7C5"       # Timestamps, placeholders, inactive icons

# ── Brand Accents ──
ACCENT_BLUE = "#8AB4F8"          # Primary interactive accent
ACCENT_GREEN = "#1E8E3E"         # User avatar, grounded claims
AMBIENT_INDIGO = "#1a1a2e"       # Ambient glow base
AMBIENT_PURPLE = "#2d1b4e"       # Ambient glow blend

# ── Claim Classification Colors ──
CLAIM_GROUNDED = "#1E8E3E"       # 🟢 Green
CLAIM_CONTESTED = "#F9AB00"      # 🟡 Amber
CLAIM_UNVERIFIED = "#EA4335"     # 🔴 Red

# ── Contradiction / Warning Colors ──
WARNING_BG = "#3d2e00"           # Dark amber background for warnings
WARNING_BORDER = "#F9AB00"       # Amber border
ERROR_BG = "#3d1111"             # Dark red background for errors
ERROR_BORDER = "#EA4335"         # Red border
INFO_BG = "#0d2137"              # Dark blue background for info
INFO_BORDER = "#8AB4F8"          # Blue border

# ── Shape ──
RADIUS_PILL = "50px"             # Fully rounded: inputs, primary buttons
RADIUS_CARD = "12px"             # Soft rounded: cards, panels
RADIUS_CARD_LG = "16px"          # Larger cards, expanders

# ── Typography Sizes ──
FONT_DISPLAY = "32px"
FONT_BODY = "16px"
FONT_LABEL = "14px"
FONT_CAPTION = "12px"


def inject_gemini_css():
    """
    Inject custom CSS into Streamlit to fully apply the Gemini Design Language.
    Call this once at the top of app.py, right after st.set_page_config().
    """
    st.markdown(f"""
    <style>
        /* ── Import Google Sans ── */
        @import url('https://fonts.googleapis.com/css2?family=Google+Sans:wght@400;500;700&display=swap');

        /* ── Global Font ── */
        html, body, [class*="st-"] {{
            font-family: 'Google Sans', 'Segoe UI', system-ui, -apple-system, sans-serif;
        }}

        /* ── Main App Background ── */
        .stApp {{
            background-color: {BASE_BG};
        }}

        /* ── Sidebar ── */
        section[data-testid="stSidebar"] {{
            background-color: {SURFACE_LOW};
            border-right: 1px solid {SURFACE_HIGH};
        }}

        section[data-testid="stSidebar"] .stMarkdown {{
            color: {TEXT_PRIMARY};
        }}

        /* ── Chat Input — Pill Shape ── */
        .stChatInput textarea {{
            border-radius: {RADIUS_PILL} !important;
            background-color: {SURFACE_LOW} !important;
            border: 1px solid {SURFACE_HIGH} !important;
            color: {TEXT_PRIMARY} !important;
        }}

        .stChatInput textarea::placeholder {{
            color: {TEXT_SECONDARY} !important;
        }}

        /* ── Chat Messages ── */
        .stChatMessage {{
            background-color: {SURFACE_LOW} !important;
            border-radius: {RADIUS_CARD_LG} !important;
            border: none !important;
            padding: 1rem 1.25rem !important;
        }}

        /* ── Buttons — Pill Shape ── */
        .stButton > button {{
            border-radius: {RADIUS_PILL} !important;
            background-color: {SURFACE_HIGH} !important;
            color: {TEXT_PRIMARY} !important;
            border: 1px solid {SURFACE_HIGH} !important;
            font-family: 'Google Sans', sans-serif !important;
            font-weight: 500 !important;
            transition: background-color 0.2s ease, transform 0.1s ease !important;
        }}

        .stButton > button:hover {{
            background-color: {ACCENT_BLUE} !important;
            color: {BASE_BG} !important;
            transform: translateY(-1px) !important;
        }}

        /* ── Expanders — Rounded Card ── */
        .streamlit-expanderHeader {{
            background-color: {SURFACE_LOW} !important;
            border-radius: {RADIUS_CARD} !important;
            color: {TEXT_PRIMARY} !important;
        }}

        .streamlit-expanderContent {{
            background-color: {SURFACE_LOW} !important;
            border-radius: 0 0 {RADIUS_CARD} {RADIUS_CARD} !important;
        }}

        /* ── Forms — Rounded Card ── */
        [data-testid="stForm"] {{
            background-color: {SURFACE_LOW} !important;
            border-radius: {RADIUS_CARD_LG} !important;
            border: 1px solid {SURFACE_HIGH} !important;
            padding: 1.5rem !important;
        }}

        /* ── Text Inputs ── */
        .stTextInput > div > div > input {{
            background-color: {SURFACE_HIGH} !important;
            color: {TEXT_PRIMARY} !important;
            border-radius: {RADIUS_CARD} !important;
            border: 1px solid {SURFACE_HIGH} !important;
        }}

        /* ── Progress Bar ── */
        .stProgress > div > div > div {{
            background: linear-gradient(90deg, {ACCENT_BLUE}, {ACCENT_GREEN}) !important;
            border-radius: {RADIUS_PILL} !important;
        }}

        /* ── Toast / Alert styling ── */
        .stAlert {{
            border-radius: {RADIUS_CARD} !important;
        }}

        /* ── Dividers — subtle ── */
        hr {{
            border-color: {SURFACE_HIGH} !important;
            opacity: 0.5;
        }}

        /* ── Captions / Secondary Text ── */
        .stCaption, small {{
            color: {TEXT_SECONDARY} !important;
        }}

        /* ── Claim Badge Colors (used via st.markdown HTML) ── */
        .badge-grounded {{
            background-color: {CLAIM_GROUNDED};
            color: white;
            padding: 2px 8px;
            border-radius: {RADIUS_PILL};
            font-size: {FONT_CAPTION};
            font-weight: 500;
        }}
        .badge-contested {{
            background-color: {CLAIM_CONTESTED};
            color: {BASE_BG};
            padding: 2px 8px;
            border-radius: {RADIUS_PILL};
            font-size: {FONT_CAPTION};
            font-weight: 500;
        }}
        .badge-unverified {{
            background-color: {CLAIM_UNVERIFIED};
            color: white;
            padding: 2px 8px;
            border-radius: {RADIUS_PILL};
            font-size: {FONT_CAPTION};
            font-weight: 500;
        }}

        /* ── Step Type Tags ── */
        .tag-established {{
            color: {TEXT_SECONDARY};
            font-size: {FONT_CAPTION};
            font-variant: small-caps;
            opacity: 0.8;
        }}
        .tag-reasoned {{
            color: {ACCENT_BLUE};
            font-size: {FONT_CAPTION};
            font-variant: small-caps;
        }}
        .tag-inferred {{
            color: {CLAIM_CONTESTED};
            font-size: {FONT_CAPTION};
            font-style: italic;
        }}

        /* ── Ambient glow behind greeting ── */
        .ambient-glow {{
            background: radial-gradient(
                ellipse at center,
                {AMBIENT_PURPLE}33 0%,
                {AMBIENT_INDIGO}22 40%,
                transparent 70%
            );
            padding: 3rem 2rem;
            text-align: center;
        }}
    </style>
    """, unsafe_allow_html=True)
```

### [NEW] [config.py](file:///d:/Projects/Graduation%20Project%202/stateful_ledger/config.py)

```python
import os
from dotenv import load_dotenv

load_dotenv()  # Reads from .env file in project root

# ── API Configuration (model is a swappable parameter) ──
GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
MODEL_NAME: str = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")  # Change via .env or env var
MAX_OUTPUT_TOKENS: int = 4096
MAX_HISTORY_TURNS_IN_PROMPT: int = 10

GOAL_TYPES: list[str] = ["analytical", "creative", "technical", "exploratory"]

TRUST_WEIGHTS: dict[str, float] = {
    "accurate": 1.0,
    "uncertain": 0.5,
    "inaccurate": 0.0,
}

CLAIM_CLASSIFICATIONS: list[str] = ["grounded", "contested", "unverified"]
STEP_TYPES: list[str] = ["inference", "assumption", "established_fact"]
CLAIM_TAGS: list[str] = ["established", "reasoned", "inferred"]
```

**Unit Tests for Phase 1:** `tests/test_config.py`
- `test_config_constants_defined` — Assert all constants are non-None and correct types
- `test_goal_types_valid` — Assert expected goal types present
- `test_trust_weights_sum` — Assert weight values are within [0, 1]

---

## Phase 2 — Ledger Data Layer (Schema + Manager)

*Goal: Ledger schema defined as Python dataclasses, manager can initialise/update/snapshot the ledger.*

### [NEW] [ledger/schema.py](file:///d:/Projects/Graduation%20Project%202/stateful_ledger/ledger/schema.py)

Defines all data structures as Python `dataclasses` with `dataclasses_json` for serialisation.

```python
from dataclasses import dataclass, field
from typing import Optional
from utils.id_gen import generate_id

@dataclass
class Rule:
    id: str = field(default_factory=generate_id)
    text: str = ""
    source: str = "user"          # "user" | "inferred"
    created_at: int = 0           # turn index
    active: bool = True

@dataclass
class Assumption:
    id: str = field(default_factory=generate_id)
    text: str = ""
    turn_index: int = 0
    user_confirmed: Optional[bool] = None  # None = not reviewed

@dataclass
class MissingInfo:
    id: str = field(default_factory=generate_id)
    text: str = ""
    turn_index: int = 0

@dataclass
class Claim:
    claim_id: str = field(default_factory=generate_id)
    text: str = ""
    classification: str = "unverified"  # "grounded" | "contested" | "unverified"
    tag: str = "inferred"               # "established" | "reasoned" | "inferred"
    perspectives: list[str] = field(default_factory=list)   # Only if contested
    sources: list[str] = field(default_factory=list)        # Only if grounded
    ledger_rules_used: list[str] = field(default_factory=list)
    overconfidence_flag: bool = False

@dataclass
class Paragraph:
    index: int = 0
    text: str = ""
    claims: list[Claim] = field(default_factory=list)
    step_type: Optional[str] = None  # "inference" | "assumption" | "established_fact"

@dataclass
class VerifiedResponse:
    paragraphs: list[Paragraph] = field(default_factory=list)

@dataclass
class ContradictionFlag:
    flag_id: str = field(default_factory=generate_id)
    conflict_text: str = ""
    conflicting_rule_id: str = ""
    conflict_message: str = ""
    severity: str = "tension"       # "direct" | "tension"
    resolution: Optional[str] = None  # None | "update_rule" | "override_once" | "flag_tension"
    resolved_at: Optional[int] = None

@dataclass
class UserFeedback:
    accurate: list[int] = field(default_factory=list)
    inaccurate: list[int] = field(default_factory=list)
    uncertain: list[int] = field(default_factory=list)

@dataclass
class InteractionTurn:
    turn_index: int = 0
    role: str = "user"
    raw_input: str = ""
    verified_response: Optional[VerifiedResponse] = None
    contradiction_flags: list[ContradictionFlag] = field(default_factory=list)
    completeness_gaps: list[str] = field(default_factory=list)
    user_feedback: UserFeedback = field(default_factory=UserFeedback)

@dataclass
class Rubric:
    criteria: list[str] = field(default_factory=list)
    is_edited_by_user: bool = False
    version: int = 1

@dataclass
class Ledger:
    session_id: str = field(default_factory=generate_id)
    goal_type: str = "exploratory"
    rubric: Rubric = field(default_factory=Rubric)
    rubric_confirmed: bool = False
    rules: list[Rule] = field(default_factory=list)
    assumptions: list[Assumption] = field(default_factory=list)
    missing_info: list[MissingInfo] = field(default_factory=list)
    interaction_history: list[InteractionTurn] = field(default_factory=list)
    trust_score: float = 0.0
    turn_count: int = 0
```

---

### [NEW] [utils/id_gen.py](file:///d:/Projects/Graduation%20Project%202/stateful_ledger/utils/id_gen.py)

```python
import uuid

def generate_id() -> str:
    return str(uuid.uuid4())[:8]
```

---

### [NEW] [ledger/manager.py](file:///d:/Projects/Graduation%20Project%202/stateful_ledger/ledger/manager.py)

```python
from ledger.schema import (
    Ledger, Rule, Assumption, MissingInfo,
    InteractionTurn, VerifiedResponse, ContradictionFlag
)
from dataclasses import asdict
from copy import deepcopy

def init_ledger() -> Ledger:
    """Create a fresh Ledger instance for a new session."""
    return Ledger()

def get_snapshot(ledger: Ledger, max_turns: int = 10) -> dict:
    """
    Return a serialisable dict of the ledger for prompt injection.
    Caps interaction_history to the last `max_turns` to fit context window.
    """
    snapshot = asdict(ledger)
    snapshot["interaction_history"] = snapshot["interaction_history"][-max_turns:]
    return snapshot

def update_ledger(
    ledger: Ledger,
    user_input: str,
    verified_response: VerifiedResponse,
    new_assumptions: list[Assumption],
    new_missing_info: list[MissingInfo],
    contradiction_flags: list[ContradictionFlag],
    completeness_gaps: list[str],
) -> Ledger:
    """
    Append a new turn to the ledger after processing is complete.
    Returns the mutated ledger.
    """
    turn = InteractionTurn(
        turn_index=ledger.turn_count,
        role="assistant",
        raw_input=user_input,
        verified_response=verified_response,
        contradiction_flags=contradiction_flags,
        completeness_gaps=completeness_gaps,
    )
    ledger.interaction_history.append(turn)
    ledger.assumptions.extend(new_assumptions)
    ledger.missing_info.extend(new_missing_info)
    ledger.turn_count += 1
    return ledger

def add_rule(ledger: Ledger, text: str, source: str = "user") -> Rule:
    """Add a new rule to the ledger. Returns the created rule."""
    rule = Rule(text=text, source=source, created_at=ledger.turn_count)
    ledger.rules.append(rule)
    return rule

def remove_rule(ledger: Ledger, rule_id: str) -> bool:
    """Remove a rule by ID. Returns True if found and removed."""
    for i, rule in enumerate(ledger.rules):
        if rule.id == rule_id:
            ledger.rules.pop(i)
            return True
    return False

def update_rule(ledger: Ledger, rule_id: str, new_text: str) -> bool:
    """Update a rule's text by ID. Returns True if found and updated."""
    for rule in ledger.rules:
        if rule.id == rule_id:
            rule.text = new_text
            return True
    return False

def get_active_rules(ledger: Ledger) -> list[Rule]:
    """Return only active rules."""
    return [r for r in ledger.rules if r.active]

def export_ledger(ledger: Ledger) -> dict:
    """Export full ledger as a dict for JSON download."""
    return asdict(ledger)
```

**Unit Tests for Phase 2:** `tests/test_schema.py` + `tests/test_manager.py`

**`test_schema.py`:**
- `test_ledger_creation_defaults` — Verify all defaults are sensible
- `test_rule_has_unique_id` — Two Rule() instances have different IDs
- `test_claim_classification_values` — Classification must be one of the three valid values
- `test_verified_response_structure` — VerifiedResponse holds Paragraphs with Claims
- `test_contradiction_flag_defaults` — Resolution starts as None
- `test_ledger_serialisation_roundtrip` — `asdict(Ledger())` produces valid dict, can reconstruct

**`test_manager.py`:**
- `test_init_ledger_returns_fresh_instance` — session_id is set, turn_count is 0
- `test_get_snapshot_caps_history` — With 15 turns, snapshot only has last 10
- `test_get_snapshot_returns_dict` — Result is a plain dict (JSON-serialisable)
- `test_update_ledger_appends_turn` — After update, turn_count increments, interaction_history grows
- `test_update_ledger_appends_assumptions` — New assumptions are merged into ledger.assumptions
- `test_add_rule_assigns_id_and_appends` — Rule gets an ID, appears in ledger.rules
- `test_remove_rule_by_id` — Rule is removed; removing non-existent ID returns False
- `test_update_rule_by_id` — Rule text changes; updating non-existent ID returns False
- `test_get_active_rules_filters_inactive` — Inactive rules are excluded
- `test_export_ledger_is_complete_dict` — All fields present in export

---

## Phase 3 — Utilities & Gemini API Client

*Goal: Safe JSON parsing works, Gemini API calls work with retry logic and mock support.*

### [NEW] [utils/json_parser.py](file:///d:/Projects/Graduation%20Project%202/stateful_ledger/utils/json_parser.py)

```python
import json
import re

def safe_parse_json(text: str) -> dict | None:
    """
    Parse JSON from text that may contain markdown fences, preamble, or be malformed.
    Returns parsed dict on success, None on failure.
    """
    if not text or not isinstance(text, str):
        return None

    # Strip markdown code fences
    cleaned = re.sub(r"^```(?:json)?\s*\n?", "", text.strip(), flags=re.MULTILINE)
    cleaned = re.sub(r"\n?```\s*$", "", cleaned.strip(), flags=re.MULTILINE)

    # Attempt direct parse
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    # Try to extract first JSON object from the text
    match = re.search(r"\{[\s\S]*\}", cleaned)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    # Try to extract JSON array
    match = re.search(r"\[[\s\S]*\]", cleaned)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    return None
```

---

### [NEW] [engine/gemini_client.py](file:///d:/Projects/Graduation%20Project%202/stateful_ledger/engine/gemini_client.py)

```python
import time
from google import genai
from google.genai import types
from config import GEMINI_API_KEY, MODEL_NAME, MAX_OUTPUT_TOKENS
from utils.json_parser import safe_parse_json

# Initialise client once at module level
client = genai.Client(api_key=GEMINI_API_KEY)


def call_gemini(
    system_prompt: str,
    user_prompt: str,
    use_search_grounding: bool = False,
    max_retries: int = 3,
) -> dict:
    """
    Call the Gemini API with structured JSON output.

    Args:
        system_prompt: System instructions
        user_prompt: User message
        use_search_grounding: Enable Google Search grounding (for Call #3)
        max_retries: Number of retry attempts with exponential backoff

    Returns:
        Parsed JSON dict on success.
        {"error": str, "raw_text": str} on failure.
    """
    tools = []
    if use_search_grounding:
        tools = [types.Tool(google_search=types.GoogleSearch())]

    config = types.GenerateContentConfig(
        system_instruction=system_prompt,
        max_output_tokens=MAX_OUTPUT_TOKENS,
        temperature=0.2,      # Low temperature for consistency
        response_mime_type="application/json",
        tools=tools if tools else None,
    )

    last_error = None
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=user_prompt,
                config=config,
            )
            raw_text = response.text
            parsed = safe_parse_json(raw_text)
            if parsed is not None:
                return parsed
            else:
                return {"error": "JSON parse failed", "raw_text": raw_text}
        except Exception as e:
            last_error = str(e)
            if attempt < max_retries - 1:
                wait = 2 ** attempt  # 1s, 2s, 4s
                time.sleep(wait)

    return {"error": f"API call failed after {max_retries} retries: {last_error}", "raw_text": ""}
```

**Unit Tests for Phase 3:** `tests/test_json_parser.py` + `tests/test_gemini_client.py`

**`test_json_parser.py`:**
- `test_parse_clean_json` — `'{"a": 1}'` → `{"a": 1}`
- `test_parse_json_with_markdown_fences` — `` ```json\n{"a":1}\n``` `` → `{"a": 1}`
- `test_parse_json_with_preamble` — `"Here is the JSON:\n{\"a\":1}"` → `{"a": 1}`
- `test_parse_json_array` — `'[1, 2, 3]'` → `[1, 2, 3]`
- `test_parse_malformed_json_returns_none` — `"not json at all"` → `None`
- `test_parse_empty_string_returns_none` — `""` → `None`
- `test_parse_none_input_returns_none` — `None` → `None`
- `test_parse_nested_json` — Complex nested object parses correctly

**`test_gemini_client.py`** (all using `unittest.mock.patch` to mock the API):
- `test_call_gemini_success_returns_parsed_dict` — Mock returns valid JSON text → parsed dict
- `test_call_gemini_retry_on_error` — First call raises exception, second succeeds → retries correctly
- `test_call_gemini_all_retries_fail` — All 3 attempts fail → returns error dict
- `test_call_gemini_json_parse_failure` — API returns non-JSON → returns error with raw_text
- `test_call_gemini_search_grounding_flag` — When `use_search_grounding=True`, the Tool config includes GoogleSearch

---

## Phase 4 — Prompt Builder & Structured Output (Gemini Call #1)

*Goal: Prompts are correctly constructed with ledger context. Call #1 returns structured paragraphs, claims, assumptions, missing_info.*

### [NEW] [engine/prompt_builder.py](file:///d:/Projects/Graduation%20Project%202/stateful_ledger/engine/prompt_builder.py)

```python
import json

# ── Call #1 (Rubric): Infer goal type + rubric ──

def build_rubric_prompt(user_input: str) -> tuple[str, str]:
    """
    Build system + user prompt for rubric generation (first turn only).
    Returns (system_prompt, user_prompt).
    """
    system_prompt = """You are a goal classification assistant for the Stateful Ledger system.
Analyze the user's first message and:
1. Infer the goal type: one of "analytical", "creative", "technical", "exploratory"
2. Generate 3-5 evaluation rubric criteria appropriate for this goal type.

Return ONLY valid JSON matching this schema:
{
    "goal_type": "analytical|creative|technical|exploratory",
    "rubric_criteria": ["criterion 1", "criterion 2", ...]
}
No markdown fences. No preamble."""

    user_prompt = f"User's first message:\n\n{user_input}"
    return system_prompt, user_prompt


# ── Call #1 (Main): Structured response generation ──

MAIN_RESPONSE_SCHEMA = """{
    "paragraphs": [
        {
            "index": 0,
            "text": "paragraph text",
            "claims": [
                {
                    "claim_id": "unique_id",
                    "text": "discrete factual claim",
                    "tag": "established|reasoned|inferred"
                }
            ],
            "step_type": "inference|assumption|established_fact"
        }
    ],
    "assumptions": ["assumption 1", "assumption 2"],
    "missing_info": ["info 1", "info 2"]
}"""

def build_main_prompt(user_input: str, ledger_snapshot: dict) -> tuple[str, str]:
    """
    Build system + user prompt for main response generation (Call #1).
    Injects ledger context into the system prompt.
    Returns (system_prompt, user_prompt).
    """
    rules_text = json.dumps(
        [r["text"] for r in ledger_snapshot.get("rules", []) if r.get("active", True)],
        indent=2
    )
    assumptions_text = json.dumps(
        [a["text"] for a in ledger_snapshot.get("assumptions", [])],
        indent=2
    )
    goal_type = ledger_snapshot.get("goal_type", "exploratory")
    rubric_criteria = json.dumps(
        ledger_snapshot.get("rubric", {}).get("criteria", []),
        indent=2
    )

    system_prompt = f"""You are a precise reasoning assistant operating within a Stateful Ledger system.

ACTIVE LEDGER STATE:
Rules: {rules_text}
Assumptions established: {assumptions_text}
Goal type: {goal_type}
Rubric criteria: {rubric_criteria}

INSTRUCTIONS:
1. Generate a comprehensive response to the user's query.
2. For EACH paragraph, tag its reasoning type:
   - "established_fact": grounded in prior session context or verifiable data
   - "assumption": a premise taken without explicit grounding
   - "inference": derived logically from context but not directly stated
3. For each paragraph, extract discrete factual claims as a flat list.
   Tag each claim as "established", "reasoned", or "inferred".
4. List ALL assumptions you are making in this response.
5. List ALL information that was NOT available to you.

Return ONLY valid JSON matching this schema:
{MAIN_RESPONSE_SCHEMA}
No markdown fences. No preamble."""

    user_prompt = user_input
    return system_prompt, user_prompt


# ── Call #2: Contradiction Check ──

def build_contradiction_prompt(
    rules: list[dict],
    user_input: str,
    response_text: str,
) -> tuple[str, str]:
    """
    Build system + user prompt for contradiction detection (Call #2).
    Returns (system_prompt, user_prompt).
    """
    rules_json = json.dumps(
        [{"id": r["id"], "text": r["text"]} for r in rules if r.get("active", True)],
        indent=2
    )

    system_prompt = """You are a contradiction detection engine for the Stateful Ledger system.
Compare the user's prompt and the assistant's response against the established rules.
Identify any contradictions between the new content and the established rules.

Return ONLY valid JSON:
{
    "violations": [
        {
            "rule_id": "id of the violated rule",
            "conflict_text": "the specific text that conflicts",
            "severity": "direct|tension"
        }
    ]
}
If no contradictions exist, return: {"violations": []}
No markdown fences. No preamble."""

    user_prompt = f"""Active rules:
{rules_json}

User prompt:
{user_input}

Assistant response:
{response_text}"""

    return system_prompt, user_prompt


# ── Call #3: Claim Classification with Search Grounding ──

def build_classification_prompt(claims: list[dict]) -> tuple[str, str]:
    """
    Build system + user prompt for claim classification (Call #3).
    This call should use Google Search grounding.
    Returns (system_prompt, user_prompt).
    """
    system_prompt = """You are a claim verification engine. Classify each claim using Google Search grounding where available.

For each claim, return:
- classification: "grounded" | "contested" | "unverified"
- perspectives: [] (only if contested — 2 to 3 alternative framings, neutral phrasing)
- sources: [] (only if grounded — brief source descriptions)

Return ONLY valid JSON:
{
    "classified_claims": [
        {
            "claim_id": "id",
            "classification": "grounded|contested|unverified",
            "perspectives": [],
            "sources": []
        }
    ]
}
No markdown fences. No preamble."""

    claims_text = "\n".join(
        f"{i+1}. [ID: {c['claim_id']}] {c['text']}"
        for i, c in enumerate(claims)
    )

    user_prompt = f"Classify these claims:\n\n{claims_text}"
    return system_prompt, user_prompt
```

**Unit Tests for Phase 4:** `tests/test_prompt_builder.py`

- `test_build_rubric_prompt_contains_goal_types` — System prompt mentions all four goal types
- `test_build_rubric_prompt_includes_user_input` — User prompt contains the user's text
- `test_build_main_prompt_injects_rules` — Active rules appear in the system prompt
- `test_build_main_prompt_injects_rubric` — Rubric criteria appear in the system prompt
- `test_build_main_prompt_includes_schema` — JSON schema is present in system prompt
- `test_build_main_prompt_caps_history` — Snapshot with capped turns is used correctly
- `test_build_contradiction_prompt_includes_rules` — Rules JSON is embedded
- `test_build_contradiction_prompt_includes_response` — Response text is in user prompt
- `test_build_classification_prompt_numbers_claims` — Claims are numbered with IDs
- `test_build_classification_prompt_empty_claims` — Empty claims list produces valid prompt

---

## Phase 5 — Rubric Generation System

*Goal: First-turn rubric card shown, user can confirm/edit before first response.*

### [NEW] [ui/rubric.py](file:///d:/Projects/Graduation%20Project%202/stateful_ledger/ui/rubric.py)

```python
import streamlit as st
from ledger.schema import Rubric


def render_rubric_card(rubric: Rubric, goal_type: str):
    """
    Render the rubric as an editable form at the top of the chat.
    Blocks generation until user confirms.
    """
    with st.form("rubric_form", clear_on_submit=False):
        st.subheader(f"📋 Session Rubric — [{goal_type.capitalize()}]")
        st.caption("This rubric will be used to evaluate response completeness.")

        updated_criteria = []
        for i, criterion in enumerate(rubric.criteria):
            val = st.text_input(
                f"Criterion {i+1}",
                value=criterion,
                key=f"rubric_criterion_{i}"
            )
            updated_criteria.append(val)

        # Add new criterion
        new_criterion = st.text_input(
            "Add new criterion (optional)",
            value="",
            key="rubric_new_criterion"
        )

        submitted = st.form_submit_button("✅ Confirm & Proceed")

        if submitted:
            if new_criterion.strip():
                updated_criteria.append(new_criterion.strip())
            rubric.criteria = [c for c in updated_criteria if c.strip()]
            rubric.is_edited_by_user = True
            rubric.version += 1
            st.session_state["ledger"].rubric = rubric
            st.session_state["ledger"].rubric_confirmed = True
            st.toast("Rubric confirmed ✅")
            st.rerun()
```

### Integration in [app.py](file:///d:/Projects/Graduation%20Project%202/stateful_ledger/app.py)

The rubric flow is wired into `app.py`:
1. On first user message, call `build_rubric_prompt()` → `call_gemini()` → get `goal_type` + `rubric_criteria`
2. Store in `ledger.rubric` and `ledger.goal_type`
3. Set `ledger.rubric_confirmed = False`
4. Render `render_rubric_card()` — form blocks until confirmed
5. On confirm, set `ledger.rubric_confirmed = True`, proceed to generate response

**Unit Tests for Phase 5:** `tests/test_rubric.py`

- `test_rubric_prompt_returns_valid_goal_type` — Mock API returns valid goal_type → stored correctly
- `test_rubric_prompt_returns_criteria` — Mock API returns 3-5 criteria → all stored
- `test_rubric_edit_updates_criteria` — Simulated form submit with edits → criteria updated
- `test_rubric_add_new_criterion` — New criterion added → appears in criteria list
- `test_rubric_confirm_sets_flag` — After confirm, `rubric_confirmed` is True
- `test_generation_blocked_without_rubric` — Attempting generation with `rubric_confirmed=False` raises/blocks

---

## Phase 6 — Layer 1: Internal Logic Engine

*Goal: Contradiction detection (Call #2) and completeness audit work, with UI for contradiction resolution.*

### [NEW] [engine/layer1.py](file:///d:/Projects/Graduation%20Project%202/stateful_ledger/engine/layer1.py)

```python
from dataclasses import asdict
from ledger.schema import (
    Ledger, ContradictionFlag, VerifiedResponse
)
from engine.prompt_builder import build_contradiction_prompt
from engine.gemini_client import call_gemini
from utils.id_gen import generate_id


def run_contradiction_check(
    user_input: str,
    response: VerifiedResponse,
    ledger: Ledger,
) -> list[ContradictionFlag]:
    """
    Call #2: Check if the user's prompt or the response contradicts active ledger rules.
    Returns a list of ContradictionFlags.
    """
    active_rules = [asdict(r) for r in ledger.rules if r.active]
    if not active_rules:
        return []

    # Build full response text from paragraphs
    response_text = "\n\n".join(p.text for p in response.paragraphs)

    system_prompt, user_prompt = build_contradiction_prompt(
        rules=active_rules,
        user_input=user_input,
        response_text=response_text,
    )

    result = call_gemini(system_prompt, user_prompt)

    if "error" in result:
        return []  # Graceful degradation: skip contradiction check on API failure

    flags = []
    for v in result.get("violations", []):
        flag = ContradictionFlag(
            flag_id=generate_id(),
            conflict_text=v.get("conflict_text", ""),
            conflicting_rule_id=v.get("rule_id", ""),
            severity=v.get("severity", "tension"),
            conflict_message=(
                f"This conflicts with Rule '{v.get('rule_id', '?')}'. "
                f"You can update the rule, override for this response, "
                f"or keep both and I'll flag the tension."
            ),
        )
        flags.append(flag)

    return flags


def run_completeness_audit(
    response: VerifiedResponse,
    rubric_criteria: list[str],
) -> list[str]:
    """
    Check which rubric criteria are not addressed in the response.
    Uses keyword matching first, then falls back to semantic matching if needed.
    Returns list of unaddressed criteria.
    """
    gaps = []
    full_text = " ".join(p.text.lower() for p in response.paragraphs)

    for criterion in rubric_criteria:
        # Simple keyword-based check: split criterion into words, check if most appear
        keywords = [w.lower() for w in criterion.split() if len(w) > 3]
        if not keywords:
            continue

        match_count = sum(1 for kw in keywords if kw in full_text)
        coverage_ratio = match_count / len(keywords) if keywords else 0

        if coverage_ratio < 0.5:
            gaps.append(criterion)

    return gaps


def extract_assumptions_and_missing(
    raw_response: dict,
) -> tuple[list[str], list[str]]:
    """
    Extract assumptions and missing_info from the raw Gemini Call #1 response.
    Returns (assumptions_list, missing_info_list).
    """
    assumptions = raw_response.get("assumptions", [])
    missing_info = raw_response.get("missing_info", [])

    # Ensure they're lists of strings
    if not isinstance(assumptions, list):
        assumptions = []
    if not isinstance(missing_info, list):
        missing_info = []

    return (
        [str(a) for a in assumptions],
        [str(m) for m in missing_info],
    )
```

---

### [NEW] [ui/flags.py](file:///d:/Projects/Graduation%20Project%202/stateful_ledger/ui/flags.py)

```python
import streamlit as st
from ledger.schema import ContradictionFlag, Ledger


def render_contradiction_widget(flag: ContradictionFlag, ledger: Ledger, turn_index: int):
    """
    Render a contradiction warning box with three resolution buttons.
    For "direct" severity, this should block further rendering (call st.stop() after).
    """
    # Find the conflicting rule text
    rule_text = ""
    for rule in ledger.rules:
        if rule.id == flag.conflicting_rule_id:
            rule_text = rule.text
            break

    st.warning(f"""
    ⚠️ **CONTRADICTION DETECTED**

    This response conflicts with Rule: *"{rule_text}"*

    Conflict: *"{flag.conflict_text}"*
    """)

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("📝 Update the Rule", key=f"update_rule_{flag.flag_id}"):
            flag.resolution = "update_rule"
            flag.resolved_at = turn_index
            st.session_state[f"editing_rule_{flag.conflicting_rule_id}"] = True
            st.rerun()

    with col2:
        if st.button("⏭️ Override for this response", key=f"override_{flag.flag_id}"):
            flag.resolution = "override_once"
            flag.resolved_at = turn_index
            st.toast("Override applied for this response.")
            st.rerun()

    with col3:
        if st.button("🔀 Flag the Tension", key=f"tension_{flag.flag_id}"):
            flag.resolution = "flag_tension"
            flag.resolved_at = turn_index
            st.toast("Tension flagged — both positions will coexist.")
            st.rerun()


def render_tension_notice(flag: ContradictionFlag):
    """Render a subtle tension notice prepended to the response."""
    st.info(f"""
    🔀 **Tension Notice**: This response has a noted tension with an established rule.
    *"{flag.conflict_text}"*
    This tension has been acknowledged and both positions coexist.
    """)
```

---

### [NEW] [ui/completeness.py](file:///d:/Projects/Graduation%20Project%202/stateful_ledger/ui/completeness.py)

```python
import streamlit as st


def render_completeness_tracker(
    gaps: list[str],
    all_criteria: list[str],
):
    """
    Render a completeness check showing which rubric criteria were addressed.
    """
    with st.expander("📋 Completeness Check", expanded=bool(gaps)):
        for criterion in all_criteria:
            if criterion in gaps:
                st.markdown(f"❌ **{criterion}**: Not addressed")
            else:
                st.markdown(f"✅ **{criterion}**: Addressed")

        if gaps:
            st.divider()
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔄 Request missing coverage", key="request_coverage"):
                    # Append auto-follow-up prompt
                    missing_text = ", ".join(gaps)
                    follow_up = f"Please address the following from the rubric that was not covered: {missing_text}"
                    st.session_state["auto_followup"] = follow_up
                    st.rerun()
            with col2:
                if st.button("⏭️ Mark as intentionally skipped", key="skip_coverage"):
                    st.toast("Marked as intentionally skipped.")
```

**Unit Tests for Phase 6:** `tests/test_layer1.py`

- `test_contradiction_check_no_rules_returns_empty` — Empty rules → no flags
- `test_contradiction_check_with_violation` — Mock API returns a violation → ContradictionFlag created with correct fields
- `test_contradiction_check_api_failure_graceful` — Mock API error → returns empty list (graceful degradation)
- `test_contradiction_flag_message_format` — Flag message contains rule reference and options
- `test_completeness_audit_all_covered` — Response addresses all criteria → empty gaps list
- `test_completeness_audit_missing_criterion` — Response misses one criterion → gap contains it
- `test_completeness_audit_empty_criteria` — Empty criteria list → empty gaps
- `test_completeness_audit_partial_keyword_match` — Low keyword overlap → flagged as gap
- `test_extract_assumptions_valid` — Valid dict → correct assumption strings extracted
- `test_extract_assumptions_malformed` — Missing keys → returns empty lists
- `test_extract_assumptions_non_list` — Non-list values → returns empty lists

---

## Phase 7 — Layer 2: External Validation Engine

*Goal: Claims classified as Grounded/Contested/Unverified via Call #3 with Google Search grounding. Inline badges rendered.*

### [NEW] [engine/layer2.py](file:///d:/Projects/Graduation%20Project%202/stateful_ledger/engine/layer2.py)

```python
from dataclasses import asdict
from ledger.schema import Claim, VerifiedResponse, Paragraph
from engine.prompt_builder import build_classification_prompt
from engine.gemini_client import call_gemini


def run_claim_classification(
    response: VerifiedResponse,
) -> VerifiedResponse:
    """
    Call #3: Classify all claims in the response using Google Search grounding.
    Mutates the response object's claims with classification results.
    Returns the updated VerifiedResponse.
    """
    # Extract all claims from all paragraphs
    all_claims = []
    for para in response.paragraphs:
        for claim in para.claims:
            all_claims.append({"claim_id": claim.claim_id, "text": claim.text})

    if not all_claims:
        return response

    system_prompt, user_prompt = build_classification_prompt(all_claims)
    result = call_gemini(system_prompt, user_prompt, use_search_grounding=True)

    if "error" in result:
        # Mark all claims as unverified on API failure
        for para in response.paragraphs:
            for claim in para.claims:
                claim.classification = "unverified"
        return response

    # Build lookup from classification results
    classified = {
        c["claim_id"]: c
        for c in result.get("classified_claims", [])
    }

    # Merge classifications back into claims
    for para in response.paragraphs:
        for claim in para.claims:
            if claim.claim_id in classified:
                c = classified[claim.claim_id]
                claim.classification = c.get("classification", "unverified")
                claim.perspectives = c.get("perspectives", [])
                claim.sources = c.get("sources", [])

    return response


def detect_overconfidence(response: VerifiedResponse) -> VerifiedResponse:
    """
    Detect overconfidence: a claim classified as "contested" but its paragraph
    is tagged "established_fact" — this is a mismatch.
    Sets the overconfidence_flag on such claims.
    """
    for para in response.paragraphs:
        for claim in para.claims:
            if (
                claim.classification == "contested"
                and para.step_type == "established_fact"
            ):
                claim.overconfidence_flag = True
    return response
```

---

### [NEW] [ui/claims.py](file:///d:/Projects/Graduation%20Project%202/stateful_ledger/ui/claims.py)

```python
import streamlit as st
from ledger.schema import Claim, Paragraph


BADGE_MAP = {
    "grounded": ("🟢", "Confirmed by multiple sources"),
    "contested": ("🟡", "Multiple valid positions exist"),
    "unverified": ("🔴", "No grounding found — treat as model inference"),
}

TAG_STYLES = {
    "established": ("[fact]", "gray"),
    "reasoned": ("[reasoned]", "blue"),
    "inferred": ("[inferred]", "orange"),
}


def render_claim_badge(claim: Claim) -> str:
    """Return the emoji badge for a claim's classification."""
    badge, _ = BADGE_MAP.get(claim.classification, ("🔴", "Unknown"))
    return badge


def render_paragraph_with_claims(paragraph: Paragraph, turn_index: int):
    """
    Render a paragraph with inline claim badges and step_type tag.
    """
    # Paragraph text
    st.markdown(paragraph.text)

    # Step type tag
    if paragraph.step_type:
        tag_text, tag_color = TAG_STYLES.get(
            paragraph.step_type, ("[unknown]", "gray")
        )
        st.caption(f":{tag_color}[{tag_text}]")

    # Claim badges
    if paragraph.claims:
        badge_line = " ".join(
            f"{render_claim_badge(c)} `{c.text[:50]}...`"
            if len(c.text) > 50 else f"{render_claim_badge(c)} `{c.text}`"
            for c in paragraph.claims
        )
        st.markdown(badge_line, unsafe_allow_html=True)

        # Expand contested claims
        for claim in paragraph.claims:
            if claim.classification == "contested" and claim.perspectives:
                render_contested_expander(claim, turn_index)

            if claim.overconfidence_flag:
                render_overconfidence_flag(claim)


def render_contested_expander(claim: Claim, turn_index: int):
    """
    Render an expander for a contested claim showing alternative perspectives.
    """
    with st.expander(f"🟡 Perspectives on: \"{claim.text[:60]}...\""):
        st.markdown("""
        This claim is framed one way here.
        2–3 alternative framings exist:
        """)
        for i, perspective in enumerate(claim.perspectives, 1):
            st.markdown(f"→ **Framing {i}:** {perspective}")

        st.caption("The system does not indicate which framing is correct.")
        st.button(
            "Mark as reviewed",
            key=f"reviewed_{claim.claim_id}_{turn_index}"
        )


def render_overconfidence_flag(claim: Claim):
    """
    Render a perspective flag for an overconfident claim.
    """
    st.warning(f"""
    🟡 **PERSPECTIVE FLAG**

    This claim is presented as settled, but it represents one position
    in an active debate. Alternative framings:

    {"".join(f'→ {p}' + chr(10) for p in claim.perspectives)}

    The system does not indicate which framing is correct.
    """)
```

**Unit Tests for Phase 7:** `tests/test_layer2.py`

- `test_claim_classification_empty_claims` — No claims → response unchanged
- `test_claim_classification_all_grounded` — Mock returns all grounded → classifications set correctly
- `test_claim_classification_mixed` — Mock returns mix of grounded/contested/unverified → each set correctly
- `test_claim_classification_api_failure` — Mock error → all claims marked unverified
- `test_claim_classification_merges_perspectives` — Contested claim gets perspectives array
- `test_claim_classification_merges_sources` — Grounded claim gets sources array
- `test_claim_classification_unknown_id_ignored` — API returns ID not in response → ignored gracefully
- `test_detect_overconfidence_flagged` — Contested claim in established_fact paragraph → flag set
- `test_detect_overconfidence_not_flagged` — Contested claim in inference paragraph → flag NOT set
- `test_detect_overconfidence_grounded_not_flagged` — Grounded claim → never flagged regardless of step_type

---

## Phase 8 — Sidebar: Ledger Panel, Trust Indicator, Reasoning Trace

*Goal: Live editable ledger visible in sidebar with edit/delete controls, trust indicator, and reasoning trace.*

### [NEW] [ui/sidebar.py](file:///d:/Projects/Graduation%20Project%202/stateful_ledger/ui/sidebar.py)

```python
import json
import streamlit as st
from ledger.schema import Ledger, InteractionTurn
from ledger.manager import add_rule, remove_rule, update_rule


def render_ledger_panel(ledger: Ledger):
    """Render the full sidebar ledger panel with edit controls."""

    # ── Rules Section ──
    st.subheader(f"📋 Rules ({len([r for r in ledger.rules if r.active])})")
    for rule in ledger.rules:
        if not rule.active:
            continue

        edit_key = f"editing_rule_{rule.id}"
        col1, col2, col3 = st.columns([6, 1, 1])

        with col1:
            if st.session_state.get(edit_key, False):
                new_text = st.text_input(
                    "Edit rule",
                    value=rule.text,
                    key=f"rule_text_{rule.id}",
                    label_visibility="collapsed",
                )
                if st.button("Save", key=f"save_rule_{rule.id}"):
                    update_rule(ledger, rule.id, new_text)
                    st.session_state[edit_key] = False
                    st.toast("Rule updated.")
                    st.rerun()
            else:
                st.markdown(f"・ {rule.text}")

        with col2:
            if st.button("✏️", key=f"edit_btn_{rule.id}"):
                st.session_state[edit_key] = True
                st.rerun()

        with col3:
            if st.button("✕", key=f"del_btn_{rule.id}"):
                remove_rule(ledger, rule.id)
                st.toast("Rule removed.")
                st.rerun()

    # Add Rule button
    if st.button("+ Add Rule", key="add_rule_btn"):
        st.session_state["adding_rule"] = True
        st.rerun()

    if st.session_state.get("adding_rule", False):
        new_rule_text = st.text_input("New rule:", key="new_rule_text")
        if st.button("Save New Rule", key="save_new_rule"):
            if new_rule_text.strip():
                add_rule(ledger, new_rule_text.strip())
                st.session_state["adding_rule"] = False
                st.toast("Rule added.")
                st.rerun()

    st.divider()

    # ── Assumptions Section ──
    st.subheader(f"🤔 Assumptions ({len(ledger.assumptions)})")
    for assumption in ledger.assumptions:
        status = ""
        if assumption.user_confirmed is True:
            status = "✅"
        elif assumption.user_confirmed is False:
            status = "❌"
        else:
            status = "❓"
        st.markdown(f"・ {status} {assumption.text}")

    st.divider()

    # ── Missing Info Section ──
    st.subheader(f"❓ Missing Info ({len(ledger.missing_info)})")
    for info in ledger.missing_info:
        st.markdown(f"・ {info.text}")


def render_trust_indicator(trust_score: float):
    """Render the trust score progress bar with qualitative label."""
    st.divider()
    st.subheader("📊 Trust Indicator")

    # Qualitative label
    if trust_score >= 0.75:
        label = "High reliability"
        colour = "🟢"
    elif trust_score >= 0.4:
        label = "Moderate — verify contested claims externally"
        colour = "🟡"
    else:
        label = "Low — verify all claims externally"
        colour = "🔴"

    st.progress(trust_score, text=f"{colour} {trust_score:.0%} — {label}")

    # Stats
    total_rated = sum(
        len(t.user_feedback.accurate) + len(t.user_feedback.inaccurate) + len(t.user_feedback.uncertain)
        for t in st.session_state["ledger"].interaction_history
    )
    st.caption(f"Based on {total_rated} rated sections.")


def render_reasoning_trace(turn: InteractionTurn, ledger: Ledger):
    """Render the reasoning trace panel for the current turn."""
    with st.expander("🔍 Reasoning Trace"):
        # Rules used
        if turn.verified_response:
            rules_used = set()
            for para in turn.verified_response.paragraphs:
                for claim in para.claims:
                    rules_used.update(claim.ledger_rules_used)

            if rules_used:
                st.markdown("**Ledger rules that influenced this response:**")
                for rule_id in rules_used:
                    rule_text = next(
                        (r.text for r in ledger.rules if r.id == rule_id), rule_id
                    )
                    st.markdown(f"・ {rule_text}")

        # Completeness gaps
        if turn.completeness_gaps:
            st.markdown("**Coverage gaps:**")
            for gap in turn.completeness_gaps:
                st.markdown(f"・ ❌ {gap}")

        # Missing info for this turn
        turn_missing = [
            m for m in ledger.missing_info
            if m.turn_index == turn.turn_index
        ]
        if turn_missing:
            st.markdown("**Information unavailable at generation time:**")
            for m in turn_missing:
                st.markdown(f"・ {m.text}")


def render_export_button(ledger: Ledger):
    """Render the Export Ledger download button."""
    from ledger.manager import export_ledger
    ledger_json = json.dumps(export_ledger(ledger), indent=2, default=str)
    st.download_button(
        label="📥 Export Ledger",
        data=ledger_json,
        file_name="ledger_export.json",
        mime="application/json",
    )
```

**Unit Tests for Phase 8:** (Sidebar tests are primarily visual/integration, but we test the logic functions)

- `test_render_trust_indicator_labels` — Score 0.8 → "High", 0.5 → "Moderate", 0.2 → "Low"
- `test_reasoning_trace_extracts_rules_used` — Verified response with rules_used → displayed
- `test_export_ledger_is_valid_json` — Export produces parseable JSON with all expected keys

---

## Phase 9 — Calibration Feedback Loop & Trust Score

*Goal: User can rate paragraphs, trust score updates in real-time in sidebar.*

### [NEW] [ledger/trust.py](file:///d:/Projects/Graduation%20Project%202/stateful_ledger/ledger/trust.py)

```python
from config import TRUST_WEIGHTS
from ledger.schema import Ledger


def calculate_trust_score(ledger: Ledger) -> float:
    """
    Calculate the session-level trust score as a weighted average
    across all user-rated paragraphs.

    Formula: (accurate * 1.0 + uncertain * 0.5 + inaccurate * 0.0) / total_rated

    Returns 0.0 if no paragraphs have been rated.
    This score is NEVER passed to the Gemini API — it's purely user-facing.
    """
    total_weighted = 0.0
    total_count = 0

    for turn in ledger.interaction_history:
        fb = turn.user_feedback
        accurate_count = len(fb.accurate)
        uncertain_count = len(fb.uncertain)
        inaccurate_count = len(fb.inaccurate)

        total_weighted += (
            accurate_count * TRUST_WEIGHTS["accurate"]
            + uncertain_count * TRUST_WEIGHTS["uncertain"]
            + inaccurate_count * TRUST_WEIGHTS["inaccurate"]
        )
        total_count += accurate_count + uncertain_count + inaccurate_count

    if total_count == 0:
        return 0.0

    return total_weighted / total_count
```

---

### [NEW] [ui/calibration.py](file:///d:/Projects/Graduation%20Project%202/stateful_ledger/ui/calibration.py)

```python
import streamlit as st
from ledger.schema import Ledger
from ledger.trust import calculate_trust_score


def render_calibration_buttons(
    turn_index: int,
    para_index: int,
    ledger: Ledger,
):
    """
    Render three compact feedback buttons below each paragraph.
    Updates ledger.interaction_history[turn].user_feedback on click.
    """
    col1, col2, col3 = st.columns(3)

    already_rated = _is_already_rated(ledger, turn_index, para_index)

    if already_rated:
        st.caption("✓ Rated")
        return

    with col1:
        if st.button("✅ Accurate", key=f"accurate_{turn_index}_{para_index}"):
            _record_feedback(ledger, turn_index, para_index, "accurate")

    with col2:
        if st.button("❌ Inaccurate", key=f"inaccurate_{turn_index}_{para_index}"):
            _record_feedback(ledger, turn_index, para_index, "inaccurate")

    with col3:
        if st.button("❓ Uncertain", key=f"uncertain_{turn_index}_{para_index}"):
            _record_feedback(ledger, turn_index, para_index, "uncertain")


def _is_already_rated(ledger: Ledger, turn_index: int, para_index: int) -> bool:
    """Check if a paragraph has already been rated."""
    if turn_index >= len(ledger.interaction_history):
        return False
    fb = ledger.interaction_history[turn_index].user_feedback
    return para_index in fb.accurate or para_index in fb.inaccurate or para_index in fb.uncertain


def _record_feedback(
    ledger: Ledger,
    turn_index: int,
    para_index: int,
    feedback_type: str,
):
    """Record user feedback and recalculate trust score."""
    if turn_index >= len(ledger.interaction_history):
        return

    fb = ledger.interaction_history[turn_index].user_feedback
    getattr(fb, feedback_type).append(para_index)

    # Recalculate trust score
    ledger.trust_score = calculate_trust_score(ledger)

    st.toast(f"Marked as {feedback_type}")
    st.rerun()
```

**Unit Tests for Phase 9:** `tests/test_trust.py` + `tests/test_calibration.py`

**`test_trust.py`:**
- `test_trust_score_no_ratings` — Empty feedback → 0.0
- `test_trust_score_all_accurate` — 5 accurate ratings → 1.0
- `test_trust_score_all_inaccurate` — 5 inaccurate ratings → 0.0
- `test_trust_score_all_uncertain` — 5 uncertain ratings → 0.5
- `test_trust_score_mixed` — 3 accurate + 2 inaccurate + 1 uncertain → correct weighted avg
- `test_trust_score_across_multiple_turns` — Feedback across 3 turns → correctly aggregated
- `test_trust_score_never_exceeds_1` — Any combination → 0.0 ≤ score ≤ 1.0

**`test_calibration.py`:**
- `test_record_feedback_accurate` — Accurate click → para_index added to accurate list
- `test_record_feedback_inaccurate` — Inaccurate click → para_index added to inaccurate list
- `test_is_already_rated_true` — Paragraph in feedback list → returns True
- `test_is_already_rated_false` — Paragraph not in any list → returns False
- `test_record_feedback_recalculates_trust` — After recording → trust_score updated

---

## Phase 10 — Main App Assembly & Chat Loop

*Goal: Full Streamlit app assembled, chat loop functional, all phases integrated.*

### [NEW] [app.py](file:///d:/Projects/Graduation%20Project%202/stateful_ledger/app.py)

```python
import streamlit as st
from dataclasses import asdict
from ledger.schema import (
    Ledger, Assumption, MissingInfo, VerifiedResponse, Paragraph, Claim
)
from ledger.manager import init_ledger, get_snapshot, update_ledger
from ledger.trust import calculate_trust_score
from engine.gemini_client import call_gemini
from engine.prompt_builder import build_rubric_prompt, build_main_prompt
from engine.layer1 import (
    run_contradiction_check, run_completeness_audit,
    extract_assumptions_and_missing
)
from engine.layer2 import run_claim_classification, detect_overconfidence
from ui.sidebar import (
    render_ledger_panel, render_trust_indicator,
    render_reasoning_trace, render_export_button
)
from ui.rubric import render_rubric_card
from ui.chat import render_chat_history, render_response_block
from ui.flags import render_contradiction_widget, render_tension_notice
from ui.completeness import render_completeness_tracker
from ui.calibration import render_calibration_buttons
from utils.id_gen import generate_id


# ── Page Config ──
st.set_page_config(
    page_title="Stateful Ledger",
    page_icon="📒",
    layout="wide",
)


# ── Session State Init ──
if "ledger" not in st.session_state:
    st.session_state["ledger"] = init_ledger()
if "messages" not in st.session_state:
    st.session_state["messages"] = []
if "pending_rubric" not in st.session_state:
    st.session_state["pending_rubric"] = None


# ── Sidebar ──
with st.sidebar:
    ledger: Ledger = st.session_state["ledger"]
    render_ledger_panel(ledger)
    render_trust_indicator(ledger.trust_score)
    render_export_button(ledger)

    st.divider()
    if st.button("🔄 Reset Session", key="reset_session"):
        st.session_state.clear()
        st.rerun()


# ── Main Area ──
st.title("📒 Stateful Ledger")
st.caption("Dual-layer verification engine for AI-generated responses")

ledger = st.session_state["ledger"]

# Render rubric card if pending
if st.session_state.get("pending_rubric") and not ledger.rubric_confirmed:
    render_rubric_card(ledger.rubric, ledger.goal_type)
    st.stop()  # Block until rubric is confirmed

# Render chat history
render_chat_history(st.session_state["messages"], ledger)

# ── Chat Input ──
user_input = st.chat_input("Ask anything...")

# Handle auto-followup from completeness tracker
if st.session_state.get("auto_followup"):
    user_input = st.session_state.pop("auto_followup")

if user_input:
    # Add user message to history
    st.session_state["messages"].append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.markdown(user_input)

    # ── RUBRIC GENERATION (first turn only) ──
    if not ledger.rubric_confirmed and ledger.turn_count == 0:
        with st.spinner("Analyzing your goal..."):
            sys_prompt, usr_prompt = build_rubric_prompt(user_input)
            rubric_result = call_gemini(sys_prompt, usr_prompt)

            if "error" not in rubric_result:
                ledger.goal_type = rubric_result.get("goal_type", "exploratory")
                ledger.rubric.criteria = rubric_result.get("rubric_criteria", [])
                st.session_state["pending_rubric"] = True
                st.rerun()
            else:
                # Fallback: use exploratory with default rubric
                ledger.goal_type = "exploratory"
                ledger.rubric.criteria = ["Accuracy", "Completeness", "Clarity"]
                st.session_state["pending_rubric"] = True
                st.rerun()

    # ── MAIN GENERATION PIPELINE ──
    with st.chat_message("assistant"):
        with st.spinner("Generating and verifying response..."):
            # Step 1: Build prompt with ledger context
            snapshot = get_snapshot(ledger)
            sys_prompt, usr_prompt = build_main_prompt(user_input, snapshot)

            # Step 2: Call #1 — Main generation
            raw_response = call_gemini(sys_prompt, usr_prompt)

            if "error" in raw_response:
                st.error(f"Generation failed: {raw_response.get('error', 'Unknown error')}")
                raw_text = raw_response.get("raw_text", "")
                if raw_text:
                    st.markdown(raw_text)
                    st.warning("⚠️ Verification unavailable for this turn.")
            else:
                # Parse into VerifiedResponse
                verified_response = _parse_verified_response(raw_response)

                # Extract assumptions and missing info
                assumption_texts, missing_texts = extract_assumptions_and_missing(raw_response)
                new_assumptions = [
                    Assumption(text=a, turn_index=ledger.turn_count)
                    for a in assumption_texts
                ]
                new_missing = [
                    MissingInfo(text=m, turn_index=ledger.turn_count)
                    for m in missing_texts
                ]

                # Step 3: Call #2 — Contradiction check
                contradiction_flags = run_contradiction_check(
                    user_input, verified_response, ledger
                )

                # Step 4: Call #3 — Claim classification
                verified_response = run_claim_classification(verified_response)
                verified_response = detect_overconfidence(verified_response)

                # Step 5: Completeness audit
                completeness_gaps = run_completeness_audit(
                    verified_response, ledger.rubric.criteria
                )

                # Step 6: Update ledger
                update_ledger(
                    ledger, user_input, verified_response,
                    new_assumptions, new_missing,
                    contradiction_flags, completeness_gaps
                )

                # ── RENDER ──

                # Handle contradictions
                direct_flags = [f for f in contradiction_flags if f.severity == "direct"]
                tension_flags = [f for f in contradiction_flags if f.severity == "tension"]

                for flag in direct_flags:
                    if flag.resolution is None:
                        render_contradiction_widget(flag, ledger, ledger.turn_count - 1)
                        st.stop()

                for flag in tension_flags:
                    render_tension_notice(flag)

                # Render response
                render_response_block(verified_response, ledger.turn_count - 1, ledger)

                # Render completeness tracker
                render_completeness_tracker(completeness_gaps, ledger.rubric.criteria)

                # Add to messages for chat history
                response_text = "\n\n".join(p.text for p in verified_response.paragraphs)
                st.session_state["messages"].append({
                    "role": "assistant",
                    "content": response_text,
                    "turn_index": ledger.turn_count - 1,
                })


def _parse_verified_response(raw: dict) -> VerifiedResponse:
    """Parse the raw Gemini response dict into a VerifiedResponse dataclass."""
    paragraphs = []
    for p_data in raw.get("paragraphs", []):
        claims = [
            Claim(
                claim_id=c.get("claim_id", generate_id()),
                text=c.get("text", ""),
                tag=c.get("tag", "inferred"),
            )
            for c in p_data.get("claims", [])
        ]
        para = Paragraph(
            index=p_data.get("index", 0),
            text=p_data.get("text", ""),
            claims=claims,
            step_type=p_data.get("step_type"),
        )
        paragraphs.append(para)
    return VerifiedResponse(paragraphs=paragraphs)
```

---

### [NEW] [ui/chat.py](file:///d:/Projects/Graduation%20Project%202/stateful_ledger/ui/chat.py)

```python
import streamlit as st
from ledger.schema import VerifiedResponse, Ledger
from ui.claims import render_paragraph_with_claims
from ui.calibration import render_calibration_buttons


def render_chat_history(messages: list[dict], ledger: Ledger):
    """Render all previous messages in the chat history."""
    for msg in messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

            # For assistant messages, render calibration buttons
            if msg["role"] == "assistant" and "turn_index" in msg:
                turn_idx = msg["turn_index"]
                if turn_idx < len(ledger.interaction_history):
                    turn = ledger.interaction_history[turn_idx]
                    if turn.verified_response:
                        for para in turn.verified_response.paragraphs:
                            render_calibration_buttons(turn_idx, para.index, ledger)


def render_response_block(
    response: VerifiedResponse,
    turn_index: int,
    ledger: Ledger,
):
    """
    Render a full verified response block with:
    - Annotated paragraphs with claim badges
    - Step type tags
    - Per-paragraph calibration buttons
    """
    for para in response.paragraphs:
        render_paragraph_with_claims(para, turn_index)
        render_calibration_buttons(turn_index, para.index, ledger)
        st.divider()
```

**Unit Tests for Phase 10:** `tests/test_integration.py`

- `test_full_pipeline_mock` — Mock all 3 Gemini calls → verify end-to-end: ledger updated, response rendered, trust score at 0
- `test_parse_verified_response_valid` — Valid raw dict → VerifiedResponse with correct paragraphs and claims
- `test_parse_verified_response_empty` — Empty dict → VerifiedResponse with no paragraphs
- `test_parse_verified_response_missing_claims` — Paragraphs without claims → empty claims list
- `test_rubric_flow_blocks_generation` — First message triggers rubric → generation blocked until confirmed
- `test_contradiction_blocks_on_direct` — Direct contradiction → rendering halted
- `test_tension_shows_notice` — Tension flag → notice rendered but response not blocked
- `test_auto_followup_from_completeness` — Completeness "Request coverage" → auto-followup processed

---

## Phase 11 — Polish & Edge Case Hardening

*Goal: All edge cases handled, retry logic hardened, final audit of design constraints.*

### Changes across multiple files:

#### [MODIFY] [engine/gemini_client.py](file:///d:/Projects/Graduation%20Project%202/stateful_ledger/engine/gemini_client.py)
- Already has retry logic (3 attempts, exponential backoff) — verify it works with real API errors
- Add request timeout handling

#### [MODIFY] [app.py](file:///d:/Projects/Graduation%20Project%202/stateful_ledger/app.py)
- Add `[Reset Session]` button ✓ (already in Phase 10)
- Handle malformed JSON from any Gemini call → fallback to raw text + `st.warning()`
- Handle ambiguous first prompt → default to `exploratory`
- Handle empty Google Search grounding → session notice

#### Edge cases to verify:
| Scenario | Expected Behaviour |
|---|---|
| Gemini returns malformed JSON | Fallback: display raw text, skip annotation, show `st.warning` |
| All claims unverified (grounding unavailable) | Session notice: "Google Search grounding returned no results" |
| User edits a rule mid-session | Toast shown, rule applies to future responses only |
| Ambiguous first prompt | `goal_type: "exploratory"` default |
| User dismisses rubric without editing | Rubric stored as-is with `is_edited_by_user: false` |

**Unit Tests for Phase 11:** `tests/test_edge_cases.py`

- `test_malformed_json_fallback` — Feed malformed JSON → raw text displayed, no crash
- `test_all_claims_unverified_notice` — All claims return unverified → session-level notice rendered
- `test_rule_edit_mid_session` — Edit rule → next prompt includes updated rule
- `test_ambiguous_prompt_default_exploratory` — Unclear goal → defaults to exploratory
- `test_rubric_dismissed_stored_as_is` — Rubric confirmed without edits → `is_edited_by_user: false`
- `test_trust_score_never_sent_to_api` — Audit: trust_score does not appear in any prompt builder output
- `test_system_never_resolves_contradictions` — Contradiction flags always have `resolution: None` initially
- `test_contested_claims_never_adjudicated` — Perspectives are neutral, no "correct" framing indicated

---

## Shared Test Fixtures — `tests/conftest.py`

```python
import pytest
from ledger.schema import *
from ledger.manager import init_ledger

@pytest.fixture
def empty_ledger():
    return init_ledger()

@pytest.fixture
def ledger_with_rules():
    ledger = init_ledger()
    ledger.rules = [
        Rule(id="r1", text="Analysis must remain vendor-neutral", active=True),
        Rule(id="r2", text="Always cite sources", active=True),
        Rule(id="r3", text="Old inactive rule", active=False),
    ]
    return ledger

@pytest.fixture
def mock_verified_response():
    return VerifiedResponse(paragraphs=[
        Paragraph(
            index=0,
            text="Python is a popular programming language.",
            claims=[
                Claim(claim_id="c1", text="Python is popular", tag="established"),
                Claim(claim_id="c2", text="Python is a programming language", tag="established"),
            ],
            step_type="established_fact",
        ),
        Paragraph(
            index=1,
            text="It is the best language for beginners.",
            claims=[
                Claim(claim_id="c3", text="Python is best for beginners", tag="inferred"),
            ],
            step_type="inference",
        ),
    ])

@pytest.fixture
def mock_raw_gemini_response():
    return {
        "paragraphs": [
            {
                "index": 0,
                "text": "Python is widely used.",
                "claims": [
                    {"claim_id": "c1", "text": "Python is widely used", "tag": "established"}
                ],
                "step_type": "established_fact"
            }
        ],
        "assumptions": ["User is referring to Python 3"],
        "missing_info": ["Specific Python version not specified"]
    }
```

---

## Verification Plan

### Automated Tests

```bash
# Run all tests
cd d:\Projects\Graduation Project 2\stateful_ledger
python -m pytest tests/ -v --tb=short

# Run tests for a specific phase
python -m pytest tests/test_schema.py tests/test_manager.py -v     # Phase 2
python -m pytest tests/test_json_parser.py tests/test_gemini_client.py -v  # Phase 3
python -m pytest tests/test_prompt_builder.py -v                    # Phase 4
python -m pytest tests/test_layer1.py -v                            # Phase 6
python -m pytest tests/test_layer2.py -v                            # Phase 7
python -m pytest tests/test_trust.py tests/test_calibration.py -v   # Phase 9
python -m pytest tests/test_integration.py tests/test_edge_cases.py -v  # Phase 10-11
```

### Local UI Verification

```bash
# Open the dev dashboard to track progress
start dev_dashboard/index.html

# Run the Streamlit app locally
streamlit run app.py
```

### Manual Verification (Per Phase)

| Phase | Checkpoint |
|---|---|
| 0 | Dev dashboard opens in browser, all features functional |
| 1 | `pip install -r requirements.txt` succeeds, `python -c "import config"` works |
| 2 | `pytest tests/test_schema.py tests/test_manager.py` all pass |
| 3 | `pytest tests/test_json_parser.py tests/test_gemini_client.py` all pass |
| 4 | `pytest tests/test_prompt_builder.py` passes; manual: prompts look correct |
| 5 | First message shows rubric card; generation blocked until confirmed |
| 6 | Deliberate rule violation → contradiction flag appears and resolves |
| 7 | Contested claim (e.g., policy debate) → perspectives panel shown |
| 8 | Sidebar shows rules with edit/delete; trust indicator renders |
| 9 | Rate paragraphs → trust score updates immediately |
| 10 | Full chat loop works end-to-end |
| 11 | All edge cases handled; no crashes on malformed input |

### Design Constraint Audit (Phase 11)

Verify all 5 "what the system explicitly does not do" constraints from the architecture:

| # | Constraint | Verification |
|---|---|---|
| 1 | Never presents output as "verified" or "correct" | Inspect UI labels — only "grounded where verifiable, uncertain elsewhere" |
| 2 | Never resolves contested claims | Perspectives shown neutrally; no "correct framing" anywhere |
| 3 | Never builds trust through polish | Trust comes from transparency panel, not output quality |
| 4 | Never removes real ambiguity | Open questions preserved; ambiguity protocol triggers |
| 5 | Never closes evaluation loop | All flags/scores are input to user judgment, never auto-acted-on |
