"""Pre-execution parameter validation for tools."""

import logging
from dataclasses import dataclass, field
from pathlib import Path

import yaml

logger = logging.getLogger(__name__)

CONFIG_FILE = Path(__file__).resolve().parent.parent.parent / "config" / "tool-policies.yaml"


@dataclass
class ValidationResult:
    valid: bool
    errors: list[str] = field(default_factory=list)


class ToolValidator:
    """Validates tool parameters against declared schemas."""

    def __init__(self, config_path: Path = CONFIG_FILE):
        self._schemas: dict[str, dict] = {}
        self._load(config_path)

    def _load(self, config_path: Path):
        with open(config_path) as f:
            data = yaml.safe_load(f)
        self._schemas = data.get("schemas", {})

    def validate(self, tool_name: str, params: dict) -> ValidationResult:
        """Validate parameters for a tool call."""
        schema = self._schemas.get(tool_name)
        if schema is None:
            return ValidationResult(valid=True)  # No schema = no constraints

        errors = []

        # Check required params
        for req in schema.get("required", []):
            if req not in params:
                errors.append(f"Missing required parameter: '{req}'")

        # Check param types and allowed values
        param_schemas = schema.get("params", {})
        for name, value in params.items():
            if name not in param_schemas:
                continue
            pschema = param_schemas[name]

            # Type check
            expected_type = pschema.get("type")
            if expected_type == "number" and not isinstance(value, (int, float)):
                try:
                    float(value)
                except (ValueError, TypeError):
                    errors.append(f"Parameter '{name}' must be a number, got '{value}'")

            if expected_type == "string" and not isinstance(value, str):
                errors.append(f"Parameter '{name}' must be a string, got {type(value).__name__}")

            # Allowed values check
            allowed = pschema.get("allowed")
            if allowed is not None and str(value) not in [str(a) for a in allowed]:
                errors.append(
                    f"Parameter '{name}' value '{value}' not in allowed values: {allowed}"
                )

        if errors:
            logger.warning("VALIDATION FAILED for %s: %s", tool_name, errors)

        return ValidationResult(valid=len(errors) == 0, errors=errors)
