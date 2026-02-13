"""Phase 8: Demonstrate agent registry and policy enforcement.

Shows that agents can only use their designated tools and models.
"""

from src.governance.registry import AgentRegistry
from src.governance.policy import PolicyEngine


def main():
    registry = AgentRegistry()
    policy = PolicyEngine(registry)

    print("Registered agents:")
    for agent in registry.list_agents():
        print(f"  {agent.name:>12} | role={agent.role} | tools={agent.allowed_tools}")
    print()

    # Allowed: finance agent using calculator
    result = policy.check_tool("finance", "calculator")
    print(f"finance -> calculator:        allowed={result.allowed}")

    # Denied: market agent trying to use calculator
    result = policy.check_tool("market", "calculator")
    print(f"market  -> calculator:        allowed={result.allowed}  reason={result.reason}")

    # Denied: coordinator trying to use any tool
    result = policy.check_tool("coordinator", "search_comparables")
    print(f"coordinator -> search_comparables: allowed={result.allowed}  reason={result.reason}")

    # Allowed: coordinator using its model
    result = policy.check_model("coordinator", "ollama/llama3.1:8b")
    print(f"coordinator -> llama3.1:8b:   allowed={result.allowed}")

    # Denied: specialist trying coordinator model
    result = policy.check_model("market", "ollama/llama3.1:8b")
    print(f"market  -> llama3.1:8b:       allowed={result.allowed}  reason={result.reason}")

    # Denied: unregistered agent
    result = policy.check_tool("unknown_agent", "calculator")
    print(f"unknown -> calculator:        allowed={result.allowed}  reason={result.reason}")


if __name__ == "__main__":
    main()
