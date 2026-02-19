"""Tests for Phase 10, 14: Sanitizer, output filter, crypto, state manager."""

import json

import pytest

from src.security.sanitizer import sanitize
from src.security.output_filter import scan_output
from src.security.crypto import generate_key, encrypt, decrypt, compute_hmac, verify_hmac
from src.security.state_manager import save_state, load_state, _state_to_dict, _dict_to_state
from src.state import AgentEvaluation, EvaluationState


# ── Sanitizer ────────────────────────────────────────────────────────────

class TestSanitizer:
    def test_email_redacted(self):
        result = sanitize("Contact john@acme.com for details")
        assert result.was_redacted
        assert "[EMAIL REDACTED]" in result.sanitized
        assert "john@acme.com" not in result.sanitized

    def test_phone_redacted(self):
        result = sanitize("Call 555-123-4567 now")
        assert result.was_redacted
        assert "[PHONE REDACTED]" in result.sanitized

    def test_ssn_redacted(self):
        result = sanitize("SSN is 123-45-6789")
        assert result.was_redacted
        assert "[SSN REDACTED]" in result.sanitized

    def test_credit_card_redacted(self):
        result = sanitize("Card: 4111 1111 1111 1111")
        assert result.was_redacted
        assert "[CARD REDACTED]" in result.sanitized

    def test_clean_text_unchanged(self):
        text = "A startup idea for indoor farming using AI."
        result = sanitize(text)
        assert not result.was_redacted
        assert result.sanitized == text

    def test_multiple_pii(self):
        text = "Email john@acme.com or call 555-123-4567"
        result = sanitize(text)
        assert len(result.redactions) >= 2


# ── Output Filter ────────────────────────────────────────────────────────

class TestOutputFilter:
    def test_clean_text_passes(self):
        result = scan_output("The market is growing at 15% CAGR.")
        assert result.passed is True
        assert result.detections == []

    def test_aws_key_detected(self):
        result = scan_output("Found key: AKIAIOSFODNN7EXAMPLE")
        assert result.passed is False
        assert any(d["type"] == "aws_key" for d in result.detections)

    def test_private_key_detected(self):
        result = scan_output("-----BEGIN RSA PRIVATE KEY-----\ndata\n-----END RSA PRIVATE KEY-----")
        assert result.passed is False
        assert any(d["type"] == "private_key" for d in result.detections)

    def test_bearer_token_detected(self):
        result = scan_output("Authorization: Bearer eyJhbGciOiJIUzI1NiJ9.test.sig")
        assert result.passed is False
        assert any(d["type"] == "bearer_token" for d in result.detections)


# ── Crypto ───────────────────────────────────────────────────────────────

class TestCrypto:
    def test_encrypt_decrypt_roundtrip(self):
        key = generate_key()
        plaintext = b"sensitive evaluation data"
        ciphertext = encrypt(plaintext, key)
        assert decrypt(ciphertext, key) == plaintext

    def test_wrong_key_raises(self):
        key1 = generate_key()
        key2 = generate_key()
        ciphertext = encrypt(b"data", key1)
        with pytest.raises(Exception):
            decrypt(ciphertext, key2)

    def test_hmac_roundtrip(self):
        key = generate_key()
        data = b"evaluation state bytes"
        mac = compute_hmac(data, key)
        assert verify_hmac(data, key, mac) is True

    def test_tampered_data_fails_hmac(self):
        key = generate_key()
        data = b"original data"
        mac = compute_hmac(data, key)
        assert verify_hmac(b"tampered data", key, mac) is False


# ── State Manager ────────────────────────────────────────────────────────

class TestStateManager:
    def test_save_load_roundtrip(self, tmp_path, monkeypatch, sample_state):
        # Monkeypatch directories so tests never write to project dirs
        monkeypatch.setattr("src.security.state_manager.STATE_DIR", tmp_path / ".state")
        monkeypatch.setattr("src.security.crypto.KEYS_DIR", tmp_path / ".keys")

        save_state(sample_state, "eval-001", agent_name="test-agent")
        loaded = load_state("eval-001", agent_name="test-agent")

        assert loaded.startup_idea == sample_state.startup_idea
        assert loaded.recommendation == sample_state.recommendation
        assert len(loaded.evaluations) == len(sample_state.evaluations)
        assert loaded.average_score == pytest.approx(sample_state.average_score)

    def test_state_dict_roundtrip(self, sample_state):
        d = _state_to_dict(sample_state)
        restored = _dict_to_state(d)
        assert restored.startup_idea == sample_state.startup_idea
        assert len(restored.evaluations) == 2

    def test_missing_state_raises(self, tmp_path, monkeypatch):
        monkeypatch.setattr("src.security.state_manager.STATE_DIR", tmp_path / ".state")
        monkeypatch.setattr("src.security.crypto.KEYS_DIR", tmp_path / ".keys")
        with pytest.raises(FileNotFoundError):
            load_state("nonexistent")
