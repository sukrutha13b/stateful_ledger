from pydantic import BaseModel
from typing import Literal, Optional

class ClaimClassification(BaseModel):
    claim_index: int
    claim_text: str
    classification: Literal["Grounded", "Contested", "Unverified"]
    evidence_snippets: list[str]
    source_urls: list[str]
    contested_perspectives: list[str]

class GroundingResult(BaseModel):
    status: Literal["not_run", "completed", "failed"]
    claims: list[ClaimClassification]
