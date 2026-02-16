"""Phase 11: Demonstrate tool governance and parameter validation.

Shows three-tier tool classification and schema-based parameter validation.
"""

from src.governance.tool_governance import ToolGovernance
from src.governance.tool_validator import ToolValidator


def main():
    governance = ToolGovernance()
    validator = ToolValidator()

    # Show all tiers
    print("Tool Governance Tiers")
    print("=" * 60)
    for tier, tools in governance.list_tools().items():
        print(f"  {tier:>12}: {tools}")

    # Tier checks
    print(f"\n{'=' * 60}")
    print("Tier Checks")
    print("=" * 60)

    checks = [
        ("calculator", "approved tool"),
        ("web_search", "conditional tool"),
        ("shell_exec", "blocked tool"),
        ("unknown_tool", "unregistered tool"),
    ]
    for tool, desc in checks:
        result = governance.check(tool)
        print(f"  {tool:>20} ({desc}): tier={result.tier} allowed={result.allowed}")

    # Parameter validation
    print(f"\n{'=' * 60}")
    print("Parameter Validation")
    print("=" * 60)

    # Valid call
    result = validator.validate("calculator", {"operation": "add", "x": 10, "y": 20})
    print(f"  calculator(add, 10, 20):   valid={result.valid}")

    # Invalid operation
    result = validator.validate("calculator", {"operation": "modulo", "x": 10, "y": 3})
    print(f"  calculator(modulo, 10, 3): valid={result.valid} errors={result.errors}")

    # Missing required param
    result = validator.validate("calculator", {"operation": "add", "x": 10})
    print(f"  calculator(add, 10, ?):    valid={result.valid} errors={result.errors}")

    # Invalid type
    result = validator.validate("calculator", {"operation": "add", "x": "abc", "y": 10})
    print(f"  calculator(add, 'abc', 10):valid={result.valid} errors={result.errors}")

    # Valid risk_checklist
    result = validator.validate("risk_checklist", {"category": "market"})
    print(f"  risk_checklist(market):    valid={result.valid}")

    # Invalid category
    result = validator.validate("risk_checklist", {"category": "weather"})
    print(f"  risk_checklist(weather):   valid={result.valid} errors={result.errors}")


if __name__ == "__main__":
    main()
