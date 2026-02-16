"""PII detection and redaction using regex patterns."""

import json
import logging
import re
from dataclasses import dataclass, field
from pathlib import Path

logger = logging.getLogger(__name__)

PATTERNS_FILE = Path(__file__).resolve().parent.parent.parent / "data" / "pii_patterns.json"


@dataclass
class SanitizeResult:
    original: str
    sanitized: str
    redactions: list[dict] = field(default_factory=list)

    @property
    def was_redacted(self) -> bool:
        return len(self.redactions) > 0


def _load_patterns(path: Path = PATTERNS_FILE) -> list[dict]:
    with open(path) as f:
        return json.load(f)["patterns"]


def sanitize(text: str, patterns_path: Path = PATTERNS_FILE) -> SanitizeResult:
    """Scan text for PII and replace matches with redaction markers."""
    patterns = _load_patterns(patterns_path)
    redactions = []
    sanitized = text

    for pattern in patterns:
        regex = re.compile(pattern["regex"])
        for match in regex.finditer(sanitized):
            redactions.append({
                "type": pattern["name"],
                "matched": match.group(),
                "replacement": pattern["replacement"],
            })
        sanitized = regex.sub(pattern["replacement"], sanitized)

    if redactions:
        logger.info("Redacted %d PII instance(s): %s",
                     len(redactions),
                     [r["type"] for r in redactions])

    return SanitizeResult(
        original=text,
        sanitized=sanitized,
        redactions=redactions,
    )
