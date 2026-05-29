import re

def extract_factual_claims(text: str) -> list[str]:
    """
    Extract factual claims (sentences) from text using simple regex splitting.
    MVP: Splits by period, question mark, or exclamation mark followed by whitespace.
    """
    # Simple sentence splitting
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    
    # Filter out very short strings or obvious non-claims if needed
    claims = [s.strip() for s in sentences if len(s.strip()) > 10]
    
    return claims
