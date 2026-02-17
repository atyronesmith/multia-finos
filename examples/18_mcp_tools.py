"""Phase 16: MCP Layer — registry, governance, gateway, and audit trail.

Demonstrates the MCP layer without requiring a running LlamaStack or MCP server.
Parts 1-4 run offline. Part 5 (gateway registration) gracefully skips if servers
are not available.
"""

from src.governance.audit import AuditTrail
from src.governance.compliance_report import generate_compliance_report
from src.governance.tool_governance import ToolGovernance
from src.mcp.gateway import MCPGateway
from src.mcp.registry import MCPRegistry


def main():
    # ── Part 1: MCP Registry ──────────────────────────────────────────
    print("=" * 60)
    print("Part 1: MCP Registry")
    print("=" * 60)

    registry = MCPRegistry()

    print(f"\nAll servers ({len(registry.list_servers())}):")
    for server in registry.list_servers():
        print(f"  {server.name:<20} status={server.status:<8} tools={server.tools_provided}")

    print(f"\nActive servers ({len(registry.list_active())}):")
    for server in registry.list_active():
        print(f"  {server.name:<20} endpoint={server.endpoint}")

    # ── Part 2: Tool Governance for MCP tools ─────────────────────────
    print(f"\n{'=' * 60}")
    print("Part 2: MCP Tool Governance")
    print("=" * 60)

    governance = ToolGovernance()

    mcp_tools = [
        "mcp::market_sentiment",
        "mcp::funding_lookup",
        "mcp::file_access",
        "mcp::shell_command",
        "mcp::unknown_tool",
    ]

    for tool in mcp_tools:
        decision = governance.check(tool)
        status = "ALLOWED" if decision.allowed else "DENIED"
        print(f"  [{status:>7}] {tool:<30} tier={decision.tier:<12} {decision.reason}")

    # ── Part 3: MCP Gateway access checks ─────────────────────────────
    print(f"\n{'=' * 60}")
    print("Part 3: MCP Gateway Access Checks")
    print("=" * 60)

    gateway = MCPGateway(client=None, registry=registry, governance=governance)

    access_checks = [
        ("market-sentiment", "market_sentiment"),
        ("funding-data", "funding_lookup"),
        ("external-shell", "shell_command"),
        ("unknown-server", "some_tool"),
    ]

    for server_name, tool_name in access_checks:
        decision = gateway.check_access(server_name, tool_name)
        status = "ALLOWED" if decision.allowed else "DENIED"
        reg = "registered" if decision.server_registered else "NOT registered"
        print(f"  [{status:>7}] {server_name}/{tool_name}")
        print(f"           server={reg}  reason={decision.reason}")

    # ── Part 4: Audit Trail with MCP events ───────────────────────────
    print(f"\n{'=' * 60}")
    print("Part 4: Audit Trail with MCP Events")
    print("=" * 60)

    audit = AuditTrail(evaluation_id="mcp-demo-001", startup_idea="AI fintech platform")
    audit.started_at = "2026-02-17T10:00:00Z"

    # Record MCP registration
    audit.record_mcp_registration("market-sentiment", "http://localhost:8888/sse", success=True)
    audit.record_mcp_registration("funding-data", "http://localhost:8888/sse", success=True)

    # Record MCP access decisions
    for server_name, tool_name in access_checks:
        decision = gateway.check_access(server_name, tool_name)
        audit.record_mcp_access(server_name, tool_name, decision.allowed, decision.reason)

    # Record standard governance checks too
    audit.record_tool_governance("mcp::market_sentiment", tier="approved", allowed=True)
    audit.record_tool_governance("mcp::shell_command", tier="blocked", allowed=False)

    data = audit.to_dict()
    print(f"  Entries: {data['summary']['total_entries']}")
    print(f"  Passes:  {data['summary']['passes']}")
    print(f"  Fails:   {data['summary']['failures']}")
    print(f"  Layers:  {', '.join(data['summary']['layers_covered'])}")

    print("\n  Audit entries:")
    for e in audit.entries:
        status = "PASS" if e.outcome == "pass" else ("FAIL" if e.outcome == "fail" else "INFO")
        print(f"    [{status:>4}] {e.category:<16} {e.action:<40} {e.detail}")

    # ── Part 5: FINOS compliance check ────────────────────────────────
    print(f"\n{'=' * 60}")
    print("Part 5: FINOS Compliance — MI-20 MCP Security Governance")
    print("=" * 60)

    report = generate_compliance_report(audit)
    for m in report.mitigations:
        if m.mitigation_id == "MI-20":
            covered = "COVERED" if m.covered else "NOT COVERED"
            print(f"  {m.mitigation_id} {m.name}: {covered} ({m.evidence_count} evidence entries)")
            break

    # ── Part 6: Gateway registration (requires running servers) ───────
    print(f"\n{'=' * 60}")
    print("Part 6: Gateway Server Registration (requires LlamaStack + MCP server)")
    print("=" * 60)

    try:
        from llama_stack_client import LlamaStackClient
        client = LlamaStackClient(base_url="http://localhost:8321")
        # Quick check if server is up
        client.models.list()

        live_gateway = MCPGateway(client=client, registry=registry, governance=governance)
        success = live_gateway.register_server("market-sentiment")
        print(f"  Register market-sentiment: {'OK' if success else 'FAILED'}")

        if success:
            tools = live_gateway.discover_tools("market-sentiment")
            print(f"  Discovered tools: {tools}")
            live_gateway.unregister_server("market-sentiment")
            print("  Unregistered market-sentiment")
    except Exception as e:
        print(f"  Skipped (server not available): {e}")

    # Save audit trail
    audit.save_json()
    print(f"\nSaved audit trail to .audit/{audit.evaluation_id}.json")


if __name__ == "__main__":
    main()
