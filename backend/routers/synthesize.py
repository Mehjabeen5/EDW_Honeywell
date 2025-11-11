from fastapi import APIRouter
from typing import List
import os, json
from pydantic import ValidationError
from backend.schemas import SynthesisRequest, SynthesisOut, Driver

router = APIRouter(prefix="/synth", tags=["synthesis"])

# ---------- Work-without-API stub ----------
@router.post("/stub", response_model=SynthesisOut)
def synth_stub(req: SynthesisRequest) -> SynthesisOut:
    drivers: List[Driver] = []
    for ev in req.evidence[:2]:
        label = ev.highlights[0] if ev.highlights else f"{ev.dimension} signal"
        drivers.append(Driver(factor=label, evidence_ids=[ev.id]))
    return SynthesisOut(
        answer="Revenue decline is primarily driven by regional and product headwinds.",
        drivers=drivers,
        confidence="medium",
        limitations=["Mock evidence; limited dimensions"],
        next_steps=["Validate with live Snowflake", "Add pricing/promotions dimension"]
    )

# ---------- Real (OpenAI) with automatic fallback ----------
from openai import OpenAI
MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
OPENAI_KEY = os.getenv("OPENAI_API_KEY", "")

def _build_prompt(req: SynthesisRequest) -> str:
    lines = [f"Question: {req.question}", "Evidence:"]
    for ev in req.evidence:
        lines.append(f"- [{ev.id}] {ev.dimension} period={ev.period} kpis={ev.kpis} highlights={ev.highlights}")
    lines.append(
        "Task: Only claim what the evidence supports. Output strict JSON with fields: "
        "answer, drivers (list of {factor,evidence_ids}), confidence (high|medium|low), "
        "limitations (list), next_steps (list)."
    )
    return "\n".join(lines)

@router.post("", response_model=SynthesisOut)
def synthesize(req: SynthesisRequest) -> SynthesisOut:
    if not OPENAI_KEY:
        return synth_stub(req)

    client = OpenAI(api_key=OPENAI_KEY)
    prompt = _build_prompt(req)

    completion = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        response_format={"type": "json_object"}
    )
    raw = completion.choices[0].message.content

    try:
        data = json.loads(raw)
        return SynthesisOut(**data)
    except (json.JSONDecodeError, ValidationError):
        # Minimal repair
        drivers = []
        for ev in req.evidence[:2]:
            label = ev.highlights[0] if ev.highlights else f"{ev.dimension} signal"
            drivers.append({"factor": label, "evidence_ids": [ev.id]})
        repaired = {
            "answer": "Automated repair: evidence suggests regional/product-driven decline.",
            "drivers": drivers,
            "confidence": "low",
            "limitations": ["Parse error; repaired"],
            "next_steps": ["Retry with stricter schema", "Provide more evidence"],
        }
        return SynthesisOut(**repaired)

