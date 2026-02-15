# Synapse - Project Context & Guidelines

## 1. Architecture Overview
Synapse is a data scraping and processing pipeline built with:
- **LangGraph**: For orchestrating agent workflows (Checker -> Fixer loops).
- **LangChain Hub**: For centralized prompt management (No hardcoded prompts!).
- **LangSmith**: For tracing and monitoring agent runs.
- **OpenRouter (Mistral Small)**: As the primary LLM for performant and cost-effective generation.
- **PostgreSQL**: As the primary data store (jobs, raw_html).

## 2. Key Services
- **`agents/data_quality.py`**: The main quality assurance agent.
  - Using `ChatOpenAI` pointed to OpenRouter.
  - Pulls prompts from LangSmith Hub (`-/synapse-checker`, `-/synapse-fixer`).
  - Implements a robust JSON extraction logic (`extract_json`) to handle LLM verbosity.
- **`services/langsmith_client.py`**: Centralized logic for interacting with LangSmith.
  - Automatically handles the EU endpoint and Hub Handle (`-`).

## 3. Conventions & Rules
### Prompt Management
- **NEVER hardcode prompts** in Python files.
- ALWAYS use `pull_hub_prompt("prompt-name")` from `services.langsmith_client`.
- Prompts must be edited in the LangSmith UI (Playground).
- **Format**: Prompts must request strict JSON output. Use `{{ }}` for escaping JSON brackets in LangChain templates.

### LLM Configuration
- Use `AGENT_MODEL` env var (default: `mistralai/mistral-small-24b-instruct-2501`).
- Use `OPENROUTER_API_KEY` for authentication.
- Set `temperature=0` for deterministic outputs.

### Robustness
- 3B+ models (or smaller) are chatty. Always use regex-based JSON extraction (`extract_json`), never `json.loads(response.content)` directly.
- Agents must allow for a "Direct List" return from the LLM, even if a wrapper object was requested.

## 4. Current Prompts (Reference)
*As of Feb 2026 - Do not rely on this as source of truth, check LangSmith Hub.*

**Checker System Prompt:**
```text
Tu es un expert en qualité de données. Analyse l'échantillon JSON fourni.
Tu dois impérativement répondre au format JSON suivant :
{{
  "is_valid": true ou false,
  "analysis": "Texte court...",
  "issues": ["..."]
}}
Critères : 
- publication_date : format YYYY-MM-DD obligatoire.
```

## 5. Useful Commands
```bash
# Run the Quality Agent (Standalone)
source venv/bin/activate && python3 agents/data_quality.py

# Run Benchmarks
source venv/bin/activate && python3 benchmark_prompts.py
```
