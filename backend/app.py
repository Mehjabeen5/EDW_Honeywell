from fastapi import FastAPI
from backend.routers.route_decompose import router as route_router
from backend.routers.fetch_normalize import router as data_router
from backend.routers.synthesize import router as synth_router

app = FastAPI(title="EDW Reasoning Assistant - Alpha")

# A: Routing & Decomposition
app.include_router(route_router)
# B: Data Adapter & Normalization
app.include_router(data_router)
# C: LLM Synthesis & Guardrails
app.include_router(synth_router)

@app.get("/")
def root():
    return {"ok": True, "service": "edw-alpha"}

