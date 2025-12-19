import json

def classify_question(q: str) -> str:
    """
    LLM-based router using Snowflake Cortex.
    Returns: "simple" or "reasoning".
    """

    if not q or not q.strip():
        return "simple"

    # Prompt forces a JSON object with a single "route" field
    prompt = f"""
You are a routing classifier for an analytics question-answering system.

Classify the user question into exactly one of the following categories:

1. "simple" – The question requests a direct fact, number, table lookup,
   or simple comparison. Examples:
   - "What was revenue last quarter?"
   - "Which product made the most money?"
   - "Show revenue by region."

2. "reasoning" – The question requires multi-step reasoning, causal analysis,
   explanations, comparisons across dimensions, or root-cause analysis.
   Examples:
   - "Why was revenue down last quarter?"
   - "What caused the decline in Europe?"
   - "Explain the main drivers behind Q4 performance."

User question:
\"\"\"{q}\"\"\"

Respond ONLY with valid JSON:
{{
  "route": "simple" or "reasoning"
}}
"""

    # Escape quotes for SQL safe string literal
    safe_prompt = prompt.replace("'", "''")

    query = f"""
        SELECT SNOWFLAKE.CORTEX.COMPLETE(
            'snowflake-arctic',
            '{safe_prompt}'
        )
    """

    raw = session.sql(query).collect()[0][0]

    # Parse JSON safely
    try:
        parsed = json.loads(raw)
        route = parsed.get("route", "simple").lower().strip()
        if route in ("simple", "reasoning"):
            return route
    except Exception:
        pass

    # Fallback if model gives unexpected output
    return "simple"
