# RAGOps Sentinel Proposal

## Working Title

RAGOps Sentinel: Evidence-Drift-Aware Failure Diagnosis and Cost-Aware Repair for Production Agentic RAG Systems

## Current Claim Boundary

This project does not claim novelty for RAG, Agentic RAG, GraphRAG, vector databases, RAG evaluation, or generic observability dashboards.

The research novelty candidate is narrower: evidence-drift-aware production RAG failure diagnosis using temporal document metadata, retrieval traces, evaluator signals, operational telemetry, and cost-aware repair actions.

## Milestone 2 Update

A deterministic evaluation layer was added so future retrieval and repair improvements can be measured instead of described qualitatively.

## Milestone 3 Extension: Evidence Drift Fixture

The project now includes a controlled evidence-drift benchmark where two versions of the same policy document disagree on the operationally correct answer. This fixture supports the central research question: whether temporal/version-aware retrieval can reduce stale-evidence usage and enable component-level failure attribution.

The fixture is intentionally simple. It is not a final benchmark, but it gives the first reproducible path to test stale-document retrieval, wrong-version retrieval, and temporal repair.
