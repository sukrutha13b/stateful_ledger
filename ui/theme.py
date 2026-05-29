import streamlit as st

# ======================================================
# GEMINI DESIGN LANGUAGE - DESIGN TOKENS
# Source: design language.md
# ======================================================

# -- Backgrounds & Surfaces --
BASE_BG = "#131314"              # Main canvas, empty states
SURFACE_LOW = "#1E1F20"          # Sidebar, floating input bar, cards
SURFACE_HIGH = "#282A2C"         # Hover states, tooltips

# -- Typography --
TEXT_PRIMARY = "#E2E2E2"         # User prompts, AI responses
TEXT_SECONDARY = "#C4C7C5"       # Timestamps, placeholders, inactive icons

# -- Brand Accents --
ACCENT_BLUE = "#8AB4F8"          # Primary interactive accent
ACCENT_GREEN = "#1E8E3E"         # User avatar, grounded claims
AMBIENT_INDIGO = "#1a1a2e"       # Ambient glow base
AMBIENT_PURPLE = "#2d1b4e"       # Ambient glow blend

# -- Claim Classification Colors --
CLAIM_GROUNDED = "#1E8E3E"       # (Green) Green
CLAIM_CONTESTED = "#F9AB00"      # (Amber) Amber
CLAIM_UNVERIFIED = "#EA4335"     # (Red) Red

# -- Contradiction / Warning Colors --
WARNING_BG = "#3d2e00"           # Dark amber background for warnings
WARNING_BORDER = "#F9AB00"       # Amber border
ERROR_BG = "#3d1111"             # Dark red background for errors
ERROR_BORDER = "#EA4335"         # Red border
INFO_BG = "#0d2137"              # Dark blue background for info
INFO_BORDER = "#8AB4F8"          # Blue border

# -- Shape --
RADIUS_PILL = "50px"             # Fully rounded: inputs, primary buttons
RADIUS_CARD = "12px"             # Soft rounded: cards, panels
RADIUS_CARD_LG = "16px"          # Larger cards, expanders

# -- Typography Sizes --
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
        /* -- Import Google Sans & Material Symbols -- */
        @import url('https://fonts.googleapis.com/css2?family=Google+Sans:wght@400;500;700&display=swap');
        @import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200&display=swap');

        /* -- Global Font (protects icon fonts by inheriting naturally) -- */
        html, body, [data-testid="stAppViewContainer"], [data-testid="stSidebar"] {{
            font-family: 'Google Sans', 'Segoe UI', system-ui, -apple-system, sans-serif;
            font-size: 14px !important;
        }}

        /* -- Protect Material Symbols icons -- */
        .material-symbols-rounded {{
            font-family: 'Material Symbols Rounded' !important;
            font-size: 24px !important;
            -webkit-font-feature-settings: 'liga' !important;
            font-feature-settings: 'liga' !important;
            -webkit-font-smoothing: antialiased;
            overflow: hidden !important;
            width: 24px !important;
            height: 24px !important;
            display: inline-block !important;
        }}

        /* -- Hide Streamlit Branding (keep sidebar toggle visible) -- */
        #MainMenu {{visibility: hidden;}}
        footer {{visibility: hidden;}}
        .stDeployButton {{visibility: hidden;}}
        header[data-testid="stHeader"] {{
            background-color: #131314 !important;
        }}

        /* -- Main App Background & Layout -- */
        .stApp {{
            background-color: #131314;
        }}

        /* -- Sidebar - always visible, collapsible -- */
        section[data-testid="stSidebar"] {{
            background-color: #1E1F20 !important;
            border-right: 1px solid #282A2C !important;
            min-width: 260px !important;
        }}

        /* Ensure the sidebar collapse toggle button is always visible */
        [data-testid="collapsedControl"] {{
            display: flex !important;
            visibility: visible !important;
            opacity: 1 !important;
            color: #E2E2E2 !important;
        }}

        /* Sidebar toggle arrow button */
        button[kind="header"] {{
            display: flex !important;
            visibility: visible !important;
        }}

        section[data-testid="stSidebar"] .stMarkdown {{
            color: #E2E2E2;
        }}

        /* -- Chat Input - Centered Pill Shape -- */
        /* Outer wrapper: center the entire chat input bar */
        [data-testid="stChatInput"] {{
            max-width: 720px !important;
            margin: 0 auto !important;
            width: 100% !important;
        }}

        /* The inner container holding the textarea + button */
        [data-testid="stChatInput"] > div {{
            border-radius: 28px !important;
            background-color: #1E1F20 !important;
            border: 1px solid #3C4043 !important;
            overflow: hidden !important;
            padding: 0 !important;
        }}

        /* The textarea itself */
        .stChatInput textarea {{
            border-radius: 28px !important;
            background-color: #1E1F20 !important;
            border: none !important;
            color: #E2E2E2 !important;
            padding: 14px 56px 14px 20px !important;
            min-height: 52px !important;
            line-height: 1.5 !important;
            overflow-y: auto !important;
            resize: none !important;
            box-shadow: none !important;
            outline: none !important;
        }}

        .stChatInput textarea::placeholder {{
            color: #9AA0A6 !important;
            opacity: 1 !important;
        }}

        /* Focus glow */
        [data-testid="stChatInput"] > div:focus-within {{
            border-color: #8AB4F8 !important;
            box-shadow: 0 0 0 2px rgba(138, 180, 248, 0.15) !important;
        }}

        /* -- Chat Messages -- */
        .stChatMessage {{
            background-color: {SURFACE_LOW} !important;
            border-radius: {RADIUS_CARD_LG} !important;
            border: none !important;
            padding: 1rem 1.25rem !important;
        }}

        /* -- Hide chat avatars (colored blocks) -- */
        [data-testid="chatAvatarIcon-user"],
        [data-testid="chatAvatarIcon-assistant"],
        [data-testid="stChatMessageAvatar"],
        [data-testid="stChatMessageAvatarContainer"],
        .stChatMessageAvatar,
        .stChatMessage > div:first-child {{
            display: none !important;
        }}

        /* -- Buttons - Pill Shape -- */
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

        /* -- Expanders - Rounded Card -- */
        .streamlit-expanderHeader {{
            background-color: {SURFACE_LOW} !important;
            border-radius: {RADIUS_CARD} !important;
            color: {TEXT_PRIMARY} !important;
        }}

        .streamlit-expanderContent {{
            background-color: {SURFACE_LOW} !important;
            border-radius: 0 0 {RADIUS_CARD} {RADIUS_CARD} !important;
        }}

        /* -- Forms - Rounded Card -- */
        [data-testid="stForm"] {{
            background-color: {SURFACE_LOW} !important;
            border-radius: {RADIUS_CARD_LG} !important;
            border: 1px solid {SURFACE_HIGH} !important;
            padding: 1.5rem !important;
        }}

        /* -- Text Inputs -- */
        .stTextInput > div > div > input {{
            background-color: {SURFACE_HIGH} !important;
            color: {TEXT_PRIMARY} !important;
            border-radius: {RADIUS_CARD} !important;
            border: 1px solid {SURFACE_HIGH} !important;
        }}

        /* -- Progress Bar -- */
        .stProgress > div > div > div {{
            background: linear-gradient(90deg, {ACCENT_BLUE}, {ACCENT_GREEN}) !important;
            border-radius: {RADIUS_PILL} !important;
        }}

        /* -- Toast / Alert styling -- */
        .stAlert {{
            border-radius: {RADIUS_CARD} !important;
        }}

        /* -- Dividers - subtle -- */
        hr {{
            border-color: {SURFACE_HIGH} !important;
            opacity: 0.5;
        }}

        /* -- Captions / Secondary Text -- */
        .stCaption, small {{
            color: {TEXT_SECONDARY} !important;
        }}

        /* -- Claim Badge Colors (used via st.markdown HTML) -- */
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

        /* -- Step Type Tags -- */
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

        /* -- Ambient glow behind greeting -- */
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
