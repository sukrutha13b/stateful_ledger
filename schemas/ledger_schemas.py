# schemas/ledger_schemas.py
# Reference structure (used purely for type checking/validation, not as active session_state dataclasses)
from typing import TypedDict, Optional, List, Literal

class LedgerRubricDimension(TypedDict):
    id: str
    name: str
    description: str
    weight: float
    last_coverage_score: Optional[int]
    coverage_history: List[int]

class LedgerRubric(TypedDict):
    auto_generated: bool
    generated_at_turn: int
    dimensions: List[LedgerRubricDimension]

class LedgerRule(TypedDict):
    rule_id: str
    type: Literal["auto", "user_defined", "user_override"]
    text: str
    source_turn: int
    status: Literal["active", "suspended", "overridden"]
    override_reason: Optional[str]
    override_at_turn: Optional[int]
    last_evaluated_at: Optional[str]
    violation_count: int

class LedgerAssumption(TypedDict):
    assumption_id: str
    text: str
    source_turn: int
    confidence: Literal["explicit", "inferred"]
    status: Literal["active", "invalidated", "user_confirmed"]
    invalidated_at_turn: Optional[int]
    invalidation_reason: Optional[str]

class LedgerMissingInfo(TypedDict):
    item_id: str
    description: str
    identified_at_turn: int
    severity: Literal["Low", "Medium", "High"]
    resolved: bool
    resolved_at_turn: Optional[int]
    resolution_note: Optional[str]

class LedgerContradiction(TypedDict):
    contradiction_id: str
    description: str
    conflicting_elements: List[str]
    identified_at_turn: int
    severity: Literal["Low", "Medium", "High"]
    resolution_status: Literal["pending", "user_accepted", "user_overridden", "flagged"]
    resolution_action: Optional[str]
    resolved_at_turn: Optional[int]

class LedgerTurn(TypedDict):
    turn_id: str
    turn_number: int
    timestamp: str
    user_prompt: str
    raw_response: str
    audit_result: dict
    grounding_result: dict
    internal_confidence_flag: Optional[str]

class LedgerSchema(TypedDict):
    ledger_id: str
    session_created_at: str
    total_turns: int
    rubric: LedgerRubric
    rules: List[LedgerRule]
    assumptions: List[LedgerAssumption]
    missing_info_registry: List[LedgerMissingInfo]
    contradiction_log: List[LedgerContradiction]
    turn_history: List[LedgerTurn]
