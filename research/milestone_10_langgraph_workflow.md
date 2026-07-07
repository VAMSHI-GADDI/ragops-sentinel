# Milestone 10 — LangGraph / LangChain Agent Workflow

## Objective

Add a LangGraph-based orchestration layer for the RAGOps Sentinel query, diagnosis, and repair flow.

## Added Capabilities

- LangGraph StateGraph workflow
- LangChain tool definitions for retrieval, diagnosis, and repair planning
- Agentic RAG path: retrieve → generate → diagnose → repair/finalize
- Conditional temporal repair routing
- Human-review routing placeholder for high-confidence unresolved failures
- Runnable agent workflow script
- Unit tests for agent repair behavior and LangChain tool invocation

## Skills Demonstrated

- LangGraph
- LangChain
- Agentic RAG
- Tool-calling workflow design
- Conditional graph routing
- RAG diagnosis and repair orchestration

## Validation

Run:

python -m pytest

Expected result after M10:

19 passed

Run the agent workflow after Qdrant/docs are initialized:

python scripts/run_agent_workflow.py --query "What changed in the Qdrant retrieval policy?" --top-k 5

## Limitation

This milestone adds deterministic LangGraph orchestration. It does not yet add cloud LLM providers, Airflow, Spark, fine-tuning, Terraform, Helm, or production LangSmith deployment.
