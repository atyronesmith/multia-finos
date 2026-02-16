"""Encryption/decryption helpers using Fernet (symmetric, authenticated)."""

import hashlib
import hmac
import logging
from pathlib import Path

from cryptography.fernet import Fernet, InvalidToken

logger = logging.getLogger(__name__)

KEYS_DIR = Path(__file__).resolve().parent.parent.parent / ".keys"


def _ensure_keys_dir():
    KEYS_DIR.mkdir(exist_ok=True)


def generate_key() -> bytes:
    """Generate a new Fernet key."""
    return Fernet.generate_key()


def get_or_create_key(name: str) -> bytes:
    """Get an existing key by name, or create one if it doesn't exist.

    Keys are stored in the .keys/ directory (which should be gitignored).
    """
    _ensure_keys_dir()
    key_path = KEYS_DIR / f"{name}.key"

    if key_path.exists():
        return key_path.read_bytes().strip()

    key = generate_key()
    key_path.write_bytes(key)
    logger.info("Created new key: %s", name)
    return key


def encrypt(data: bytes, key: bytes) -> bytes:
    """Encrypt data using Fernet (AES-128-CBC with HMAC-SHA256)."""
    f = Fernet(key)
    return f.encrypt(data)


def decrypt(token: bytes, key: bytes) -> bytes:
    """Decrypt a Fernet token. Raises InvalidToken if tampered."""
    f = Fernet(key)
    try:
        return f.decrypt(token)
    except InvalidToken:
        logger.error("Decryption failed — data may have been tampered with")
        raise


def compute_hmac(data: bytes, key: bytes) -> str:
    """Compute HMAC-SHA256 for integrity verification."""
    return hmac.new(key, data, hashlib.sha256).hexdigest()


def verify_hmac(data: bytes, key: bytes, expected: str) -> bool:
    """Verify HMAC-SHA256 checksum."""
    actual = compute_hmac(data, key)
    return hmac.compare_digest(actual, expected)
