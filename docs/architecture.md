# Architecture

## Overview

Multi-agent system using LlamaStack + Ollama that evaluates startup ideas through specialized agents coordinated by a supervisor.

## Agent Flow

```
User Input (startup idea)
        |
  [Coordinator Agent] (llama3.1:8b)
        |
   +----+----+----+----+
   |         |         |         |
[Market]  [Tech]  [Finance]  [Risk]    (all llama3.2:3b)
   |         |         |         |
  Score    Score    Score    Score
   +----+----+----+----+
        |
  [Coordinator synthesizes GO/NO-GO report]
```

## Agents

| Agent | Model | Tools | Role |
|-------|-------|-------|------|
| Coordinator | 8b | None | Creates brief, synthesizes report |
| Market | 3b | `search_comparables` | Market opportunity analysis |
| Tech | 3b | `complexity_estimator` | Technical feasibility |
| Finance | 3b | `calculator` | Financial viability |
| Risk | 3b | `risk_checklist` | Risk assessment |

## Patterns Demonstrated

- **Supervisor/Worker**: Coordinator delegates to and synthesizes from specialists
- **Sequential Pipeline**: Agents run in sequence sharing state
- **Tool Calling**: Custom Python function tools with auto-generated schemas
- **Shared State**: `EvaluationState` dataclass passed through pipeline
- **RAG**: Vector DB knowledge retrieval for enhanced evaluation
- **Streaming**: Real-time token output via `EventLogger`
- **Responses API**: OpenAI-compatible alternative to Agent API

## Phase 6: Inter-Agent Security Validation

### Problem

When agents pass output to other agents as input, a compromised or manipulated agent can embed prompt injection attacks in its response. For example, a market agent's output could contain hidden instructions like "ignore all risk scores" that alter the coordinator's behavior.

### Solution: Validation Agent (LLM-as-Firewall)

Add a validation step between agent handoffs that screens output before it's passed downstream.

```
[Specialist Agent] -> [Validator] -> [Coordinator]
```

### Validator Responsibilities

1. **Injection detection**: Flag output containing instruction-like patterns ("ignore previous", "you are now", "system prompt")
2. **Schema conformance**: Verify output contains expected sections (analysis + score) and nothing extraneous
3. **Score bounds checking**: Confirm scores are within 0-10 range and numerically parseable
4. **Anomaly detection**: Flag outputs that are suspiciously short, off-topic, or contradict their own score

### Implementation Plan

- `src/agents/validator.py` — validation agent that screens specialist output
- `src/tools/injection_detector.py` — tool that pattern-matches known injection techniques
- `examples/08_secure_pipeline.py` — full pipeline with validation between agents
- Update `src/pipeline.py` to optionally enable validation via config flag

### Patterns Demonstrated

- **LLM-as-Firewall**: Using an LLM to validate inter-agent communication
- **Defense in Depth**: Combining pattern matching (tool) with semantic analysis (LLM)
- **Secure Agent Handoff**: Sanitizing data at trust boundaries between agents

## Running

```bash
# Start Ollama + LlamaStack
./scripts/start_server.sh

# Run full pipeline
python main.py "your startup idea here"

# Run individual examples
python examples/01_hello_agent.py
```
