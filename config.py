import os
from dotenv import load_dotenv

load_dotenv()  # Reads from .env file in project root


def _get_secret(key: str, default: str = "") -> str:
    """Read from st.secrets first, then fall back to environment variables."""
    try:
        import streamlit as st
        if key in st.secrets:
            return st.secrets[key]
    except Exception:
        pass
    return os.getenv(key, default)


# ── API Configuration (model is a swappable parameter) ──
GEMINI_API_KEY: str = _get_secret("GEMINI_API_KEY", "")
MODEL_NAME: str = _get_secret("GEMINI_MODEL", "gemini-2.5-flash-lite")  # Change via .env or st.secrets
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
