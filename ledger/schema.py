"""ledger/schema.py — Dataclass definitions for the Stateful Ledger.

Every data structure in the system is a plain Python dataclass.
Serialisation is handled via `dataclasses.asdict()` — no external
serialisation library required.
"""
from dataclasses import dataclass, field
from typing import Optional

from utils.id_gen import generate_id


# ══════════════════════════════════════════════════════
# ATOMIC UNITS
# ══════════════════════════════════════════════════════

@dataclass
class Rule:
    """A user-defined or inferred constraint the model must respect."""
    id: str = field(default_factory=generate_id)
    text: str = ""
    source: str = "user"          # "user" | "inferred"
    created_at: int = 0           # turn index when created
    active: bool = True


@dataclass
class Assumption:
    """An assumption made during a conversation turn, pending user review."""
    id: str = field(default_factory=generate_id)
    text: str = ""
    turn_index: int = 0
    user_confirmed: Optional[bool] = None  # None = not yet reviewed


@dataclass
class MissingInfo:
    """A gap in information flagged during completeness analysis."""
    id: str = field(default_factory=generate_id)
    text: str = ""
    turn_index: int = 0


# ══════════════════════════════════════════════════════
# CLAIM & RESPONSE STRUCTURES
# ══════════════════════════════════════════════════════

@dataclass
class Claim:
    """A single claim extracted from a model response paragraph."""
    claim_id: str = field(default_factory=generate_id)
    text: str = ""
    classification: str = "unverified"  # "grounded" | "contested" | "unverified"
    tag: str = "inferred"               # "established" | "reasoned" | "inferred"
    perspectives: list[str] = field(default_factory=list)   # Only if contested
    sources: list[str] = field(default_factory=list)        # Only if grounded
    ledger_rules_used: list[str] = field(default_factory=list)
    overconfidence_flag: bool = False


@dataclass
class Paragraph:
    """A paragraph in a verified response, containing zero or more claims."""
    index: int = 0
    text: str = ""
    claims: list[Claim] = field(default_factory=list)
    step_type: Optional[str] = None  # "inference" | "assumption" | "established_fact"


@dataclass
class VerifiedResponse:
    """The full structured response after Layer-1 / Layer-2 processing."""
    paragraphs: list[Paragraph] = field(default_factory=list)


# ══════════════════════════════════════════════════════
# CONTRADICTION & FEEDBACK
# ══════════════════════════════════════════════════════

@dataclass
class ContradictionFlag:
    """A flag raised when a model response contradicts a ledger rule."""
    flag_id: str = field(default_factory=generate_id)
    conflict_text: str = ""
    conflicting_rule_id: str = ""
    conflict_message: str = ""
    severity: str = "tension"       # "direct" | "tension"
    resolution: Optional[str] = None  # None | "update_rule" | "override_once" | "flag_tension"
    resolved_at: Optional[int] = None


@dataclass
class UserFeedback:
    """Per-turn feedback: lists of claim indices the user rated."""
    accurate: list[int] = field(default_factory=list)
    inaccurate: list[int] = field(default_factory=list)
    uncertain: list[int] = field(default_factory=list)


# ══════════════════════════════════════════════════════
# INTERACTION TURN
# ══════════════════════════════════════════════════════

@dataclass
class InteractionTurn:
    """One round of user input → model response → validation."""
    turn_index: int = 0
    role: str = "user"
    raw_input: str = ""
    verified_response: Optional[VerifiedResponse] = None
    contradiction_flags: list[ContradictionFlag] = field(default_factory=list)
    completeness_gaps: list[str] = field(default_factory=list)
    user_feedback: UserFeedback = field(default_factory=UserFeedback)


# ══════════════════════════════════════════════════════
# RUBRIC & TOP-LEVEL LEDGER
# ══════════════════════════════════════════════════════

@dataclass
class Rubric:
    """Evaluation criteria auto-generated from the goal, editable by user."""
    criteria: list[str] = field(default_factory=list)
    is_edited_by_user: bool = False
    version: int = 1


@dataclass
class Ledger:
    """The root state object — one per session."""
    session_id: str = field(default_factory=generate_id)
    goal_type: str = "exploratory"
    rubric: Rubric = field(default_factory=Rubric)
    rubric_confirmed: bool = False
    rules: list[Rule] = field(default_factory=list)
    assumptions: list[Assumption] = field(default_factory=list)
    missing_info: list[MissingInfo] = field(default_factory=list)
    interaction_history: list[InteractionTurn] = field(default_factory=list)
    trust_score: float = 0.0
    turn_count: int = 0
