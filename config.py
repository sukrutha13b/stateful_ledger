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
