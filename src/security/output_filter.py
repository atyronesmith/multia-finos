"""Output filter for detecting leaked secrets in agent output."""

import logging
import re
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

# Patterns that indicate leaked secrets in output
SECRET_PATTERNS = [
    ("aws_key", r"(?:AKIA|ABIA|ACCA|ASIA)[0-9A-Z]{16}"),
    ("aws_secret", r"(?i)aws[_\-]?secret[_\-]?access[_\-]?key[\s:=\"']+[A-Za-z0-9/+=]{40}"),
    ("generic_api_key", r"(?i)(?:api[_\-]?key|apikey)[\s:=\"']+[A-Za-z0-9\-_.]{20,}"),
    ("generic_secret", r"(?i)(?:secret|password|passwd|token)[\s:=\"']+[A-Za-z0-9\-_.!@#$%^&*]{8,}"),
    ("private_key", r"-----BEGIN (?:RSA |EC |DSA )?PRIVATE KEY-----"),
    ("bearer_token", r"(?i)bearer\s+[A-Za-z0-9\-_.~+/]+=*"),
]


@dataclass
class FilterResult:
    passed: bool
    detections: list[dict] = field(default_factory=list)


def scan_output(text: str) -> FilterResult:
    """Scan output text for leaked secrets.

    Returns FilterResult with passed=False if any secrets are detected.
    """
    detections = []

    for name, pattern in SECRET_PATTERNS:
        for match in re.finditer(pattern, text):
            detections.append({
                "type": name,
                "position": match.start(),
                "snippet": text[max(0, match.start() - 10):match.end() + 10],
            })

    if detections:
        logger.warning(
            "Output filter detected %d potential secret(s): %s",
            len(detections),
            [d["type"] for d in detections],
        )

    return FilterResult(
        passed=len(detections) == 0,
        detections=detections,
    )
