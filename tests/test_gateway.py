"""Tests for Phase 7: Gateway — rate limiter, schemas, state, extract_score."""

import time

import pytest
from pydantic import ValidationError

from src.gateway.rate_limiter import TokenBucket
from src.gateway.schemas import EvaluateRequest, evaluation_response_from_state
from src.state import AgentEvaluation, EvaluationState
from src.agents.base import extract_score


# ── TokenBucket ──────────────────────────────────────────────────────────

class TestTokenBucket:
    def test_initial_capacity(self):
        bucket = TokenBucket(capacity=5, refill_rate=1.0)
        assert bucket.tokens == 5.0

    def test_consume_decrements(self):
        bucket = TokenBucket(capacity=3, refill_rate=0.0)
        assert bucket.consume() is True
        assert bucket.consume() is True
        assert bucket.consume() is True

    def test_exhaustion(self):
        bucket = TokenBucket(capacity=1, refill_rate=0.0)
        assert bucket.consume() is True
        assert bucket.consume() is False

    def test_refill(self):
        bucket = TokenBucket(capacity=2, refill_rate=100.0)
        bucket.consume()
        bucket.consume()
        # With high refill rate, a tiny sleep should restore tokens
        time.sleep(0.05)
        assert bucket.consume() is True

    def test_does_not_exceed_capacity(self):
        bucket = TokenBucket(capacity=2, refill_rate=1000.0)
        time.sleep(0.05)
        bucket.consume()  # triggers refill
        assert bucket.tokens <= 2.0


# ── EvaluateRequest ──────────────────────────────────────────────────────

class TestEvaluateRequest:
    def test_valid_request(self):
        req = EvaluateRequest(idea="An AI platform for indoor farming optimization")
        assert len(req.idea) >= 10

    def test_too_short(self):
        with pytest.raises(ValidationError, match="at least 10"):
            EvaluateRequest(idea="short")

    def test_too_long(self):
        with pytest.raises(ValidationError, match="at most 2000"):
            EvaluateRequest(idea="x" * 2001)

    def test_strips_whitespace(self):
        req = EvaluateRequest(idea="   An AI platform for farming   ")
        assert not req.idea.startswith(" ")


# ── EvaluationResponse from state ────────────────────────────────────────

class TestEvaluationResponse:
    def test_response_fields(self, sample_state):
        resp = evaluation_response_from_state(sample_state)
        assert resp.startup_idea == sample_state.startup_idea
        assert resp.recommendation == "GO"
        assert len(resp.evaluations) == 2

    def test_average_score(self, sample_state):
        resp = evaluation_response_from_state(sample_state)
        assert resp.average_score == pytest.approx(6.5)

    def test_has_uuid_id(self, sample_state):
        resp = evaluation_response_from_state(sample_state)
        assert len(resp.id) == 36  # UUID format


# ── EvaluationState ──────────────────────────────────────────────────────

class TestEvaluationState:
    def test_add_evaluation(self):
        state = EvaluationState(startup_idea="test")
        state.add_evaluation(AgentEvaluation(agent_name="a", score=8.0))
        assert "a" in state.evaluations

    def test_average_score(self):
        state = EvaluationState(startup_idea="test")
        state.add_evaluation(AgentEvaluation(agent_name="a", score=8.0))
        state.add_evaluation(AgentEvaluation(agent_name="b", score=4.0))
        assert state.average_score == pytest.approx(6.0)

    def test_empty_average(self):
        state = EvaluationState(startup_idea="test")
        assert state.average_score == 0.0


# ── extract_score ────────────────────────────────────────────────────────

class TestExtractScore:
    def test_standard_format(self):
        assert extract_score("Score: 7/10") == 7.0

    def test_decimal_score(self):
        assert extract_score("Score: 7.5/10") == 7.5

    def test_no_match_default(self):
        assert extract_score("No numeric score here") == 5.0

    def test_capped_at_10(self):
        assert extract_score("Score: 15/10") == 10.0

    def test_bare_fraction(self):
        assert extract_score("I give it 8/10 overall") == 8.0
