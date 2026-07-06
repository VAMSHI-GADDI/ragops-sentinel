# RAGOps Sentinel Design

RAGOps Sentinel is designed to detect failures in production retrieval-augmented generation systems. It focuses on evidence drift, stale document retrieval, missing evidence, wrong document version retrieval, low-confidence retrieval, and unsupported answer generation.

## Failure diagnosis

The first baseline uses transparent rules. Later versions will use a Sentinel Diagnosis Graph and a trained failure attribution model.

## Repair

Repair actions include temporal filtering, reranking, query rewriting, graph traversal, re-indexing, abstention, and human review.
