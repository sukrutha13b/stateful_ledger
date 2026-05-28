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
            font-size: 14px !important;
        }}

        /* ── Hide Streamlit Elements ── */
        header {{visibility: hidden;}}
        #MainMenu {{visibility: hidden;}}
        footer {{visibility: hidden;}}
        .stDeployButton {{visibility: hidden;}}

        /* ── Main App Background & Layout ── */
        .stApp {{
            background-color: #131314;
        }}

        /* ── Sidebar ── */
        section[data-testid="stSidebar"] {{
            background-color: #1E1F20;
            border-right: 1px solid #282A2C;
        }}

        section[data-testid="stSidebar"] .stMarkdown {{
            color: #E2E2E2;
        }}

        /* ── Chat Input — Pill Shape ── */
        .stChatInput textarea {{
            border-radius: 50px !important;
            background-color: #1E1F20 !important;
            border: 1px solid #282A2C !important;
            color: #E2E2E2 !important;
        }}

        .stChatInput textarea::placeholder {{
            color: #C4C7C5 !important;
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
