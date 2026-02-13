"""FastAPI gateway wrapping the multi-agent evaluation pipeline."""

import asyncio
import logging

from fastapi import Depends, FastAPI, Request
from fastapi.responses import JSONResponse

from src.client import get_client
from src.gateway.rate_limiter import RateLimiter
from src.gateway.schemas import (
    EvaluateRequest,
    EvaluationResponse,
    EvaluationSummary,
    evaluation_response_from_state,
)
from src.pipeline import run_pipeline

logger = logging.getLogger(__name__)

app = FastAPI(title="MultiA Gateway", version="0.1.0")

rate_limiter = RateLimiter()

_evaluations: dict[str, EvaluationResponse] = {}


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.exception("Pipeline error")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal evaluation error"},
    )


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/evaluate", response_model=EvaluationResponse)
async def evaluate(
    request: EvaluateRequest, _rate=Depends(rate_limiter)
):
    client = get_client()
    state = await asyncio.to_thread(run_pipeline, client, request.idea)
    response = evaluation_response_from_state(state)
    _evaluations[response.id] = response
    return response


@app.get("/evaluations", response_model=list[EvaluationSummary])
async def list_evaluations():
    return [
        EvaluationSummary(
            id=e.id,
            startup_idea=e.startup_idea,
            average_score=e.average_score,
            recommendation=e.recommendation,
            created_at=e.created_at,
        )
        for e in _evaluations.values()
    ]


@app.get("/evaluations/{evaluation_id}", response_model=EvaluationResponse)
async def get_evaluation(evaluation_id: str):
    if evaluation_id not in _evaluations:
        return JSONResponse(status_code=404, content={"detail": "Not found"})
    return _evaluations[evaluation_id]
