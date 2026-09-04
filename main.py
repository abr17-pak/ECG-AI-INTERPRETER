"""
ECG-AI Interpreter backend.

Privacy note (build plan Phase 14): uploaded images are decoded in memory
for the duration of one request and never written to disk or a database
by this API. If you add a "Save report" feature, that must be an explicit,
separate opt-in action, not a side effect of analysis.
"""
from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.analyze import router as analyze_router

app = FastAPI(
    title="ECG-AI Interpreter",
    description="Research prototype — not a medical diagnostic device.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten before any real deployment
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analyze_router, prefix="/api")


@app.get("/api/health")
def health():
    return {"status": "ok", "disclaimer": "Research prototype — not a medical diagnostic device."}
