from pydantic import BaseModel
from typing import Literal, Optional

class SentenceTag(BaseModel):
    sentence_index: int
    text: str
    tag: Literal["Reasoned", "Inferred"]
    reasoning: str

class RuleCheck(BaseModel):
    rule_id: str
    rule_text: str
    status: Literal["Satisfied", "Violated", "Not_Applicable"]
    evidence: str

class RubricScore(BaseModel):
    dimension_id: str
    dimension_name: str
    coverage_score: int
    gap_description: str

class NewContradiction(BaseModel):
    description: str
    conflicting_elements: list[str]
    severity: Literal["Low", "Medium", "High"]

class NewMissingInfo(BaseModel):
    description: str
    severity: Literal["Low", "Medium", "High"]

class NewAssumption(BaseModel):
    text: str
    confidence: Literal["explicit", "inferred"]

class AuditResult(BaseModel):
    sentence_tags: list[SentenceTag]
    rule_checks: list[RuleCheck]
    rubric_scores: list[RubricScore]
    new_contradictions: list[NewContradiction]
    new_missing_info: list[NewMissingInfo]
    new_assumptions: list[NewAssumption]
    overall_audit_confidence: int
    audit_summary: str

class RubricDimensionDef(BaseModel):
    name: str
    description: str

class RubricBootstrapSchema(BaseModel):
    evaluation_dimensions: list[RubricDimensionDef]
    initial_boundary_rules: list[str]
    implicit_assumptions: list[str]
