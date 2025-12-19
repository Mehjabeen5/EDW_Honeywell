from __future__ import annotations
from typing import List, Dict, Any
import json

from .cortex_client import cortex_complete

def generate_subquestions_via_llm(question: str) -> List[Dict[str, Any]]:
    """Use Cortex to propose sub-questions for quarter / region / product."""
    system_prompt = """
You are a senior analytics planner for Honeywell's Enterprise Data Warehouse.
Given a business question about revenue performance, generate 2–4 focused
sub-questions that help explain *why* metrics changed.

Rules:
- Output MUST be **valid JSON** only (no markdown, no backticks, no commentary).
- JSON structure: an array of objects, each with:
  - "id": a short identifier like "sq1", "sq2"
  - "dimension": one of "quarter", "region", "product", or "other"
  - "question": the natural language sub-question
  - "focus": a very short phrase (3–7 words) describing what this sub-question
    is trying to determine (e.g., "identify worst region", "compare Q3 vs Q4").
- Keep questions tight, business-oriented, and grounded in revenue analysis.
- Prefer 3 questions, one per dimension (quarter, region, product), when possible.
"""

    user_prompt = f"""User question:
{question}
"""

    prompt = (
        system_prompt
        + "\n\nNow respond ONLY with a JSON array, no extra text. Example schema:\n"
        + '[\n'
        + '  {"id": "sq1", "dimension": "quarter", '
        + '"question": "<natural language sub-question>", '
        + '"focus": "<short phrase describing what this sub-question is trying to find>"},\n'
        + '  {"id": "sq2", "dimension": "region", '
        + '"question": "<natural language sub-question>", '
        + '"focus": "<short phrase describing what this sub-question is trying to find>"}\n'
        + ']\n\n'
        + "Now produce the actual array for the user question above."
        + "\n\n"
        + user_prompt
    )

    raw = cortex_complete(prompt)

    try:
        data = json.loads(raw)
        if isinstance(data, list):
            cleaned: List[Dict[str, Any]] = []
            for i, item in enumerate(data, start=1):
                if not isinstance(item, dict):
                    continue
                cleaned.append(
                    {
                        "id": item.get("id") or f"sq{i}",
                        "dimension": item.get("dimension", "other"),
                        "question": item.get("question", "").strip(),
                        "focus": item.get("focus", "").strip(),
                    }
                )
            return cleaned
    except Exception:
        pass

    return [
        {
            "id": "sq1",
            "dimension": "quarter",
            "question": "How did total revenue change between the last two quarters?",
            "focus": "compare quarter-over-quarter revenue",
        },
        {
            "id": "sq2",
            "dimension": "region",
            "question": "Which region showed the largest drop in revenue in the last quarter?",
            "focus": "find weakest region",
        },
        {
            "id": "sq3",
            "dimension": "product",
            "question": "Which product line underperformed in the last quarter?",
            "focus": "find weakest product",
        },
    ]


def plan_steps(question: str) -> Dict[str, Any]:
    """High-level planner for reasoning questions using sub-questions from an LLM."""
    subqs = generate_subquestions_via_llm(question)

    steps: List[Dict[str, Any]] = []
    for sq in subqs:
        dim = sq.get("dimension", "other")
        sid = sq.get("id", "sx")

        if dim == "quarter":
            step_type = "quarter_analytics"
        elif dim == "region":
            step_type = "region_analytics"
        elif dim == "product":
            step_type = "product_analytics"
        else:
            step_type = "generic_analytics"

        steps.append(
            {
                "id": sid,
                "dimension": dim,
                "type": step_type,
                "description": sq.get("question", ""),
                "focus": sq.get("focus", ""),
            }
        )

    if not steps:
        steps = [
            {
                "id": "s1",
                "dimension": "quarter",
                "type": "quarter_analytics",
                "description": "Compare total revenue between the last two quarters.",
                "focus": "quarter-over-quarter change",
            },
            {
                "id": "s2",
                "dimension": "region",
                "type": "region_analytics",
                "description": "Identify which region has the weakest revenue trend.",
                "focus": "weakest region",
            },
            {
                "id": "s3",
                "dimension": "product",
                "type": "product_analytics",
                "description": "Identify which product line underperforms.",
                "focus": "weakest product",
            },
        ]

    return {
        "question": question,
        "sub_questions": subqs,
        "steps": steps,
    }
