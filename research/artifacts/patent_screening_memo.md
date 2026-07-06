# Patent-Screening Memo

## Status
**Potentially patent-screenable, but patentability is not claimed.**

## Non-Novel / High Prior-Art Areas
The following are not safe novelty claims:

1. RAG itself.
2. Vector-database RAG.
3. GraphRAG.
4. Multi-agent RAG.
5. RAG evaluation metrics.
6. Generic faithfulness monitoring.
7. Generic corrective retrieval.
8. Generic RAG observability dashboard.

## Candidate Novel Mechanism
A narrower candidate mechanism is:

> A production RAGOps diagnosis graph that combines document-version metadata, stale/conflicting evidence signals, retrieval traces, evaluation metrics, operational telemetry, and repair outcomes to attribute root cause and route targeted evidence-drift repair.

## Claim Candidates for Attorney Review
1. A method for identifying stale-evidence failures in a RAG pipeline using document-version validity metadata and retrieved-context freshness ratios.
2. A method for constructing a diagnosis graph linking query, retrieved chunks, document versions, generated claims, evaluation signals, telemetry spans, failure labels, and repair actions.
3. A method for selecting temporal-filter repair when stale evidence is detected and validating repair success through pre/post stale-evidence metrics.
4. A method for converting RAG evaluation and observability signals into SLO checks for production RAG reliability.

## Required Prior-Art Search Before Any Filing
Search patent databases for:

- evidence drift RAG
- temporal RAG repair
- retrieval augmented generation failure diagnosis
- RAG observability
- RAG root cause analysis
- version-aware RAG
- knowledge graph RAG diagnosis
- corrective retrieval augmented generation
- multi-agent RAG repair

## Current Risk Assessment
Patent risk is high because RAG, GraphRAG, corrective retrieval, and RAG evaluation have extensive academic and product prior art. Only a narrow, implementation-specific mechanism may survive screening.
