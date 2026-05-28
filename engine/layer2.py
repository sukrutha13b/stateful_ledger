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
