"""utils/json_parser.py - Robust JSON extraction from raw LLM output.

Handles markdown code fences, preamble text, and attempts multiple
extraction strategies before returning None.
"""
import json
import re


def safe_parse_json(text: str) -> dict | list | None:
    """Parse JSON from text that may contain markdown fences, preamble, or be malformed.

    Strategies attempted in order:
    1. Strip markdown ```json fences, then parse directly
    2. Regex-extract the first ``{...}`` object
    3. Regex-extract the first ``[...]`` array

    Returns:
        Parsed dict/list on success, ``None`` on failure.
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
