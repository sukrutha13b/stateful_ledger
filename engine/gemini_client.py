"""engine/gemini_client.py — Gemini API wrapper with retry logic.

All Gemini API calls go through ``call_gemini()`` so that retry logic,
error handling, and search-grounding config live in one place.
"""
import time

from google import genai
from google.genai import types

from config import MODEL_NAME, MAX_OUTPUT_TOKENS
from utils.json_parser import safe_parse_json

# Lazy client — re-reads API key so .env / secrets changes take effect
_client = None
_current_key = None


def _get_client():
    """Return a genai.Client, re-creating it if the API key changed."""
    global _client, _current_key
    import os
    from dotenv import load_dotenv
    load_dotenv(override=True)
    key = os.getenv("GEMINI_API_KEY", "")
    if _client is None or key != _current_key:
        _client = genai.Client(api_key=key)
        _current_key = key
    return _client


def call_gemini(
    system_prompt: str,
    user_prompt: str,
    use_search_grounding: bool = False,
    max_retries: int = 3,
) -> dict:
    """Call the Gemini API with structured JSON output.

    Args:
        system_prompt: System instructions.
        user_prompt: User message.
        use_search_grounding: Enable Google Search grounding (for Call #3).
        max_retries: Number of retry attempts with exponential backoff.

    Returns:
        Parsed JSON dict on success.
        ``{"error": str, "raw_text": str}`` on failure.
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
            response = _get_client().models.generate_content(
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
