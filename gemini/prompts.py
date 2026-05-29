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
   BE CRITICAL: Generalizations, subjective assessments, broad claims 
   without citations, and extrapolations MUST be tagged as "Inferred". 
   Only tag sentences as "Reasoned" if they are directly and logically 
   derived from the user's query or established facts. Typically at 
   least 30-50% of sentences in any response should be "Inferred".

2. RULE CHECKS: For each active rule, determine if the response 
   Satisfied, Violated, or is Not_Applicable. Provide specific evidence 
   (quote or description) from the response.

3. RUBRIC SCORES: For each rubric dimension, assign a coverage score 
   0-100 and describe the gap.
   BE STRICT AND REALISTIC:
   - 90-100: The response comprehensively and thoroughly covers this 
     dimension with specific details, examples, and nuance.
   - 60-89: The response addresses this dimension but is missing 
     depth, specifics, or important sub-topics.
   - 30-59: The response only superficially touches on this dimension.
   - 0-29: The response barely or does not address this dimension.
   A single-turn response should RARELY score above 80 on most 
   dimensions. Be honest about what is actually covered vs. what 
   could be covered. Always describe the gap.

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
