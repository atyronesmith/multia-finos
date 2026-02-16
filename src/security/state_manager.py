"""Encrypted state persistence with per-agent isolation."""

import json
import logging
from dataclasses import asdict
from pathlib import Path

from src.security.crypto import decrypt, encrypt, get_or_create_key, compute_hmac, verify_hmac
from src.state import AgentEvaluation, EvaluationState

logger = logging.getLogger(__name__)

STATE_DIR = Path(__file__).resolve().parent.parent.parent / ".state"


def _ensure_state_dir():
    STATE_DIR.mkdir(exist_ok=True)


def _state_to_dict(state: EvaluationState) -> dict:
    """Convert EvaluationState to a JSON-serializable dict."""
    return {
        "startup_idea": state.startup_idea,
        "brief": state.brief,
        "evaluations": {
            name: asdict(ev) for name, ev in state.evaluations.items()
        },
        "final_report": state.final_report,
        "recommendation": state.recommendation,
    }


def _dict_to_state(data: dict) -> EvaluationState:
    """Reconstruct EvaluationState from a dict."""
    state = EvaluationState(startup_idea=data["startup_idea"])
    state.brief = data.get("brief", "")
    state.final_report = data.get("final_report", "")
    state.recommendation = data.get("recommendation", "")
    for name, ev_data in data.get("evaluations", {}).items():
        state.add_evaluation(AgentEvaluation(**ev_data))
    return state


def save_state(state: EvaluationState, evaluation_id: str, agent_name: str = "pipeline"):
    """Encrypt and persist an evaluation state.

    Each agent gets its own encryption key, enforcing session isolation.
    """
    _ensure_state_dir()

    key = get_or_create_key(agent_name)
    plaintext = json.dumps(_state_to_dict(state)).encode()

    ciphertext = encrypt(plaintext, key)
    checksum = compute_hmac(ciphertext, key)

    # Write encrypted state
    state_path = STATE_DIR / f"{evaluation_id}.enc"
    state_path.write_bytes(ciphertext)

    # Write integrity checksum
    checksum_path = STATE_DIR / f"{evaluation_id}.hmac"
    checksum_path.write_text(checksum)

    logger.info("Saved encrypted state: %s (agent: %s)", evaluation_id, agent_name)


def load_state(evaluation_id: str, agent_name: str = "pipeline") -> EvaluationState:
    """Load and decrypt a persisted evaluation state.

    Verifies HMAC integrity before decryption. Raises ValueError
    if the state has been tampered with or the wrong key is used.
    """
    state_path = STATE_DIR / f"{evaluation_id}.enc"
    checksum_path = STATE_DIR / f"{evaluation_id}.hmac"

    if not state_path.exists():
        raise FileNotFoundError(f"No saved state for evaluation: {evaluation_id}")

    key = get_or_create_key(agent_name)
    ciphertext = state_path.read_bytes()

    # Verify integrity
    if checksum_path.exists():
        expected = checksum_path.read_text().strip()
        if not verify_hmac(ciphertext, key, expected):
            raise ValueError(f"Integrity check failed for {evaluation_id} — possible tampering")

    plaintext = decrypt(ciphertext, key)
    data = json.loads(plaintext.decode())

    logger.info("Loaded encrypted state: %s (agent: %s)", evaluation_id, agent_name)
    return _dict_to_state(data)


def list_saved_evaluations() -> list[str]:
    """List all saved evaluation IDs."""
    if not STATE_DIR.exists():
        return []
    return [p.stem for p in STATE_DIR.glob("*.enc")]
