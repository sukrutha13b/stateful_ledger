import json
import re
from schemas.grounding_schemas import ClaimClassification

def parse_grounding_metadata(grounding_result_dict: dict) -> list[ClaimClassification]:
    """Parse Gemini grounding response text back into Structured Claim objects."""
    text_content = grounding_result_dict.get("text_content", "[]")
    
    # Attempt to extract JSON array
    match = re.search(r'\[.*\]', text_content, re.DOTALL)
    if match:
        json_str = match.group(0)
    else:
        json_str = text_content
        
    try:
        parsed_claims = json.loads(json_str)
        results = []
        for c in parsed_claims:
            results.append(ClaimClassification(**c))
        return results
    except Exception as e:
        print(f"Failed to parse grounding results: {e}")
        return []
