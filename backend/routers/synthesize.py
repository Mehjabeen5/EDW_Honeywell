from fastapi import APIRouter
from typing import List
import os, json
from pydantic import ValidationError
from groq import Groq
from backend.schemas import SynthesisRequest, SynthesisOut, Driver

router = APIRouter(prefix="/synth", tags=["synthesis"])

# --- Groq client (reads from Colab secret) ---
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def _build_prompt(req: SynthesisRequest) -> str:
    lines = [f"Question: {req.question}", "Evidence:"]
    for ev in req.evidence:
        lines.append(f"- [{ev.id}] {ev.dimension} period={ev.period} kpis={ev.kpis} highlights={ev.highlights}")
    lines.append(
        "Task: Summarize causes and patterns using only what evidence supports. "
        "Return a strict JSON object with fields: "
        "answer, drivers (list of {factor,evidence_ids}), confidence, limitations, next_steps."
    )
    return "\n".join(lines)

@router.post("", response_model=SynthesisOut)
def synthesize(req: SynthesisRequest) -> SynthesisOut:
    prompt = _build_prompt(req)
    try:
        response = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            response_format={"type": "json_object"},
        )
        raw = response.choices[0].message.content
        data = json.loads(raw)
        return SynthesisOut(**data)
    except (json.JSONDecodeError, ValidationError, Exception) as e:
        print("⚠️ Parse or API error:", e)
        # fallback stub
        drivers = []
        for ev in req.evidence[:2]:
            label = ev.highlights[0] if ev.highlights else f"{ev.dimension} trend"
            drivers.append(Driver(factor=label, evidence_ids=[ev.id]))
        return SynthesisOut(
            answer="Groq fallback: evidence suggests a regional/product-driven decline.",
            drivers=drivers,
            confidence="low",
            limitations=["Auto fallback used due to parse error."],
            next_steps=["Add more evidence", "Retry with stricter schema"]
        )
