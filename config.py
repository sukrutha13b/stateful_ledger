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


# -- API Configuration --
GEMINI_API_KEY: str = _get_secret("GEMINI_API_KEY", "")

# -- Model Configuration --
AUDIT_MODEL: str = _get_secret("AUDIT_MODEL", "gemini-2.5-flash")
GENERATION_MODEL: str = _get_secret("GENERATION_MODEL", "gemini-2.5-flash")
GROUNDING_MODEL: str = _get_secret("GROUNDING_MODEL", "gemini-2.5-flash")

# -- Thresholds --
RUBRIC_GAP_THRESHOLD: int = int(_get_secret("RUBRIC_GAP_THRESHOLD", "50"))
HIGH_SEVERITY_GAP: int = int(_get_secret("HIGH_SEVERITY_GAP", "30"))
OVERCONFIDENCE_THRESHOLD: int = int(_get_secret("OVERCONFIDENCE_THRESHOLD", "80"))
CONTESTED_RATIO_THRESHOLD: float = float(_get_secret("CONTESTED_RATIO_THRESHOLD", "0.3"))
