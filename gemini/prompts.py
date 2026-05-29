RUBRIC_BOOTSTRAP_PROMPT = """Given this user query, identify:
(a) 3-6 evaluation dimensions a thorough answer should cover,
(b) 3-5 initial boundary rules that should hold across ALL responses in this session,
(c) implicit assumptions the user appears to be making."""

AUDIT_SYSTEM_PROMPT = """You are a strict internal logic auditor. Your ONLY job is to evaluate the 
response text below against the active rules, active assumptions, and 
evaluation rubric provided. You do NOT generate new information. 
You do NOT resolve contradictions. You surface them precisely."""

AUDIT_USER_PROMPT_TEMPLATE = """=== RESPONSE TO AUDIT ===
{raw_response_text}

=== ACTIVE RULES ===
{active_rules}

=== ACTIVE ASSUMPTIONS ===
{active_assumptions}

=== EVALUATION RUBRIC ===
{rubric_dimensions}

=== INSTRUCTIONS ===
1. SENTENCE TAGGING: Split the response into individual sentences. 
   Tag each as:
   - "Reasoned": The sentence follows logically from stated premises, 
     prior conversation context, or the user's explicit question.
   - "Inferred": The sentence introduces a claim, extrapolation, or 
     conclusion that goes beyond what the evidence directly supports.

2. RULE CHECKS: For each active rule, determine if the response 
   Satisfied, Violated, or is Not_Applicable. Provide specific evidence 
   (quote or description) from the response.

3. RUBRIC SCORES: For each rubric dimension, assign a coverage score 
   0-100 and describe the gap if score < 80.

4. NEW CONTRADICTIONS: Identify any logical conflicts between the 
   response and active rules or assumptions. Be specific. Do NOT suggest 
   how to resolve them.

5. NEW MISSING INFO: Identify information that would be needed for a 
   more complete answer, that was not provided.

6. NEW ASSUMPTIONS: Identify any NEW implicit assumptions the response 
   introduces.

7. OVERALL CONFIDENCE: Assign 0-100 based on internal logical 
   consistency only (NOT factual correctness).

Return ONLY the structured JSON. No preamble."""

GROUNDING_PROMPT_TEMPLATE = """For each of the following claims, determine whether it is 
(a) Grounded - directly supported by search results, 
(b) Contested - multiple credible conflicting perspectives exist, or 
(c) Unverified - no search result confirms or denies it.
Return a structured JSON list.
Claims: {claims_list}"""
