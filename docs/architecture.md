# Architecture

## Overview

Multi-agent system using LlamaStack + Ollama that evaluates startup ideas through specialized agents coordinated by a supervisor. Implements all 9 FINOS multi-agent reference architecture layers with 17 mitigations.

Everything runs locally: Ollama for inference, LlamaStack for agent runtime, no cloud dependencies.

## Agent Flow

```
User Input (startup idea)
        |
  [Gateway] ── rate limiting, input validation, PII sanitization
        |
  [Shield Gate] ── prompt-guard shield on input
        |
  [Coordinator Agent] (llama3.1:8b)
        |
   +----+----+----+----+
   |         |         |         |
[Market]  [Tech]  [Finance]  [Risk]    (all llama3.2:3b)
   |         |         |         |
  Score    Score    Score    Score
   |         |         |         |
 [Shield Gate + Validator] ── per-agent output security
   +----+----+----+----+
        |
  [Coordinator synthesizes GO/NO-GO report]
        |
  [Output Filter] ── secret-leak scanning
        |
  [LLM-as-Judge] ── quality, consistency, bias scoring
        |
  [Encrypted State] ── persist with integrity check
        |
  [Audit Trail] ── FINOS compliance report
```

## Agents

| Agent | Model | Tools | Role |
|-------|-------|-------|------|
| Coordinator | llama3.1:8b | None | Creates brief, synthesizes report |
| Market | llama3.2:3b | `search_comparables` | Market opportunity analysis |
| Tech | llama3.2:3b | `complexity_estimator` | Technical feasibility |
| Finance | llama3.2:3b | `calculator` | Financial viability |
| Risk | llama3.2:3b | `risk_checklist` | Risk assessment |
| Validator | llama3.2:3b | None | Semantic output validation |

## FINOS Architecture Layers

| Layer | Implementation | Key Files |
|-------|---------------|-----------|
| 1. Input | FastAPI gateway with rate limiting and request validation | `src/gateway/` |
| 2. Orchestration | Agent registry (YAML) + policy engine for least-privilege | `src/governance/registry.py`, `policy.py` |
| 3. Agent/Memory | LlamaStack agents + encrypted state persistence (Fernet) | `src/security/state_manager.py`, `crypto.py` |
| 4. Tools/MCP | Three-tier tool governance + MCP registry/gateway + parameter validation | `src/governance/tool_governance.py`, `tool_validator.py`, `src/mcp/` |
| 5. Model/LLM | PII sanitization + shield-based content safety | `src/security/sanitizer.py` |
| 6. Knowledge | RAG with vector DB | `src/rag/` |
| 7. Security | prompt-guard shields between agents, output secret scanning | `src/security/shield_gate.py`, `output_filter.py` |
| 8. Observability | LlamaStack Telemetry API wrapper + threshold alerting | `src/observability/` |
| 9. Output/Eval | LLM-as-Judge scoring + bias detection + audit trail | `src/evaluation/`, `src/governance/audit.py` |

## Security Controls

- **Inter-agent shields**: prompt-guard runs on every specialist output before coordinator sees it
- **Heuristic validation**: Fast score-consistency check (no LLM call)
- **LLM validator**: Semantic checks for score manipulation and reasoning quality
- **PII redaction**: Regex-based (email, phone, SSN, credit card, IP)
- **Secret scanning**: Detects AWS keys, API keys, tokens, private keys in output
- **Agent isolation**: Per-agent encryption keys prevent cross-agent state access
- **Rate limiting**: Token-bucket per IP on the gateway
- **Tool governance**: Approved/conditional/blocked tiers with parameter schema enforcement
- **Policy engine**: Agents can only use their registered tools and models

## File Structure

```
src/
  agents/
    base.py                    # Agent creation helpers
    coordinator.py             # Brief creation + report synthesis
    market_agent.py            # Market analysis specialist
    tech_agent.py              # Technical feasibility specialist
    finance_agent.py           # Financial viability specialist
    risk_agent.py              # Risk assessment specialist
    validator.py               # Semantic output validation
  gateway/
    server.py                  # FastAPI app with endpoints
    schemas.py                 # Pydantic request/response models
    rate_limiter.py            # Token-bucket rate limiter
  governance/
    registry.py                # Agent registry (YAML-backed)
    policy.py                  # Policy evaluation engine
    tool_governance.py         # Three-tier tool classification
    tool_validator.py          # Parameter schema validation
    audit.py                   # Audit trail collector
    compliance_report.py       # FINOS coverage report generator
  mcp/
    registry.py                # MCP server registry (YAML-backed)
    gateway.py                 # MCP gateway (registry check + governance)
    demo_server.py             # Demo MCP server (FastMCP, SSE)
  security/
    shield_gate.py             # LlamaStack safety shield wrapper
    shield_runner.py           # Multi-shield aggregator
    sanitizer.py               # PII detection and redaction
    output_filter.py           # Secret-leak scanning
    state_manager.py           # Encrypted state persistence
    crypto.py                  # Fernet encryption helpers
  observability/
    pipeline_telemetry.py      # LlamaStack Telemetry API wrapper
    alerts.py                  # Threshold-based alerting
  evaluation/
    scoring_setup.py           # Register LLM-as-Judge scoring functions
    evaluator.py               # Score pipeline output
    bias_detector.py           # Statistical bias detection
  rag/
    setup.py                   # Vector DB setup
    knowledge.py               # Knowledge ingestion
  tools/
    calculator.py              # Arithmetic operations
    market_data.py             # Comparable startup search
    complexity.py              # Technical complexity estimation
    risk_checklist.py          # Structured risk checklists
  pipeline.py                  # Standard pipeline
  pipeline_secure.py           # Pipeline with shield gates
  state.py                     # Shared evaluation state
  config.py                    # Environment configuration
  client.py                    # LlamaStack client wrapper
config/
  run.yaml                     # LlamaStack server configuration
  agent-registry.yaml          # Agent permissions
  policies.yaml                # Access control policies
  tool-policies.yaml           # Tool tier classifications
  mcp-registry.yaml            # MCP server catalog
  scoring-functions.yaml       # LLM-as-Judge prompt templates
```

## Running

```bash
# Start Ollama + LlamaStack
./scripts/start_server.sh

# Start the API gateway
./scripts/start_gateway.sh

# Run full pipeline (CLI)
python main.py "your startup idea here"

# Run individual examples
python examples/01_hello_agent.py     # Hello world agent
python examples/04_full_pipeline.py   # Full evaluation pipeline
python examples/09_gateway.py         # Gateway API client
python examples/10_policy_enforcement.py  # Policy engine demo
python examples/11_secure_pipeline.py     # Secure pipeline with shields
python examples/12_sanitization.py        # PII + secret scanning
python examples/13_tool_governance.py     # Tool tier governance
python examples/14_observability.py       # Alerting demo
python examples/15_evaluation.py          # Bias detection
python examples/16_persistent_state.py    # Encrypted state
python examples/17_audit_trail.py         # Audit + compliance report
python examples/18_mcp_tools.py          # MCP registry + gateway + governance
```
