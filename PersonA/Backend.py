import re, uuid, os, requests
from fastapi import FastAPI, APIRouter

# allow package-style imports from repo root
import sys, os as _os
sys.path.append(_os.path.dirname(_os.path.abspath(__file__)))
sys.path.append(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))

from shared.schemas import (
    RouteRequest, RouteResponse, DecomposeResponse, SubQuestion,
    SynthesisRequest
)

# Import B & C routers
from PersonB.FetchNormalize import router as data_router
from PersonC.Synthesis import router as synth_router

app = FastAPI(
    title="EDW Reasoning Assistant - Alpha",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# ---------- A: routing & decomposition ----------
route_router = APIRouter(prefix="/route", tags=["routing"])
REASONING_PAT = re.compile(r"\b(why|cause|reason|decline|drop|drivers?)\b", re.I)

@route_router.post("", response_model=RouteResponse)
def route(req: RouteRequest) -> RouteResponse:
    q = (req.question or "").strip()
    return RouteResponse(type="reasoning" if REASONING_PAT.search(q) else "basic")

@route_router.post("/decompose", response_model=DecomposeResponse)
def decompose(req: RouteRequest) -> DecomposeResponse:
    sid = lambda: uuid.uuid4().hex[:6]
    return DecomposeResponse(sub_questions=[
        SubQuestion(id=f"q_time_{sid()}",    dimension="time",
                    nlq="Analyze revenue QoQ across last two quarters."),
        SubQuestion(id=f"q_region_{sid()}",  dimension="region",
                    nlq="Compare revenue by region across the last quarter."),
        SubQuestion(id=f"q_product_{sid()}", dimension="product",
                    nlq="Compare revenue by product line for the last quarter."),
        SubQuestion(id=f"q_orders_{sid()}",  dimension="orders",
                    nlq="Analyze order volume and average order value QoQ."),
    ])

app.include_router(route_router)   # A
app.include_router(data_router)    # B
app.include_router(synth_router)   # C

@app.get("/")
def root():
    return {"ok": True, "service": "edw-alpha"}

# ---------- Optional: one-call orchestrator ----------
ask_router = APIRouter(prefix="/ask", tags=["orchestrator"])
BASE = os.getenv("SELF_BASE", "http://localhost:8000")

@ask_router.post("")
def ask(req: RouteRequest):
    rtype = requests.post(f"{BASE}/route", json=req.dict()).json()["type"]
    if rtype != "reasoning":
        return {"answer": "Basic path not implemented in alpha."}
    subqs = requests.post(f"{BASE}/route/decompose", json=req.dict()).json()["sub_questions"]
    results = requests.post(f"{BASE}/data/fetch", json={"sub_questions": subqs}).json()["results"]
    evidence = requests.post(f"{BASE}/data/normalize", json={"results": results}).json()["evidence"]
    out = requests.post(f"{BASE}/synth/stub",
                        json=SynthesisRequest(question=req.question, evidence=evidence).dict()).json()
    return {"evidence": evidence, "synthesis": out}

app.include_router(ask_router)

