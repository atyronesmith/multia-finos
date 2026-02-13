"""Pydantic models for the gateway API."""

import uuid
from datetime import datetime, timezone

from pydantic import BaseModel, field_validator

from src.state import EvaluationState


class EvaluateRequest(BaseModel):
    idea: str

    @field_validator("idea")
    @classmethod
    def validate_idea(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 10:
            raise ValueError("Idea must be at least 10 characters")
        if len(v) > 2000:
            raise ValueError("Idea must be at most 2000 characters")
        return v


class AgentEvaluationResponse(BaseModel):
    agent_name: str
    score: float
    analysis: str


class EvaluationResponse(BaseModel):
    id: str
    startup_idea: str
    brief: str
    evaluations: list[AgentEvaluationResponse]
    average_score: float
    recommendation: str
    final_report: str
    created_at: datetime


class EvaluationSummary(BaseModel):
    id: str
    startup_idea: str
    average_score: float
    recommendation: str
    created_at: datetime


def evaluation_response_from_state(state: EvaluationState) -> EvaluationResponse:
    return EvaluationResponse(
        id=str(uuid.uuid4()),
        startup_idea=state.startup_idea,
        brief=state.brief,
        evaluations=[
            AgentEvaluationResponse(
                agent_name=e.agent_name,
                score=e.score,
                analysis=e.analysis,
            )
            for e in state.evaluations.values()
        ],
        average_score=state.average_score,
        recommendation=state.recommendation,
        final_report=state.final_report,
        created_at=datetime.now(timezone.utc),
    )
