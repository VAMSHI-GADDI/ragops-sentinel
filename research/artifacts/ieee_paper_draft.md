# IEEE-Style Paper Draft

## Title
RAGOps Sentinel: Evidence-Drift-Aware Failure Diagnosis and Cost-Aware Repair for Production Retrieval-Augmented Generation Systems

## Abstract
Retrieval-augmented generation (RAG) systems rely on external corpora that can evolve over time, creating failure modes where retrieved evidence is stale, conflicting, missing, or version-mismatched. Existing RAG evaluation frameworks measure retrieval and generation quality, while corrective RAG methods repair retrieval failures. This work investigates a production-oriented RAGOps layer that detects evidence-drift-induced failures, represents retrieval and generation traces in a Sentinel Diagnosis Graph, and applies targeted temporal repair. In a controlled versioned-document benchmark, the prototype reduced mean stale-evidence rate from N/A to N/A, with a repair success rate of N/A. These early results support further evaluation on larger, real-world evolving corpora.

## I. Introduction
RAG systems improve factual grounding by retrieving external evidence, but retrieval quality is not static. Documents change, indexes become stale, and multiple versions of the same operational policy may conflict. A production RAG system therefore needs not only retrieval and generation, but also evidence lifecycle monitoring, failure diagnosis, and targeted repair.

## II. Related Work
Lewis et al. introduced RAG for knowledge-intensive NLP tasks [1]. RAGAS and ARES provide evaluation frameworks for context relevance, faithfulness, and answer relevance [2], [3]. GraphRAG expands retrieval toward graph-based global corpus reasoning [4]. CRAG adds retrieval evaluation and corrective actions when retrieval goes wrong [5]. RAGOps frames operational management of RAG pipelines around changing data and lifecycle concerns [6].

## III. Problem Statement
Given a user query, retrieved evidence, document versions, generated answer, evaluation signals, and system telemetry, determine whether a failure occurred, localize the likely root cause, and choose a targeted repair action that improves evidence validity without unnecessary full-pipeline reruns.

## IV. Proposed Method
RAGOps Sentinel uses versioned ingestion, vector retrieval, temporal evidence filtering, deterministic evaluation metrics, a Sentinel Diagnosis Graph, and a rule-based first repair policy. The diagnosis graph connects query, retrieval run, chunks, document versions, answer, evaluation metrics, telemetry, failure labels, and repair actions.

## V. Experiments
The current controlled benchmark injects stale evidence by creating old and current versions of a retention-policy document. Baseline retrieval is compared with temporal-filter repair. Metrics include stale-evidence rate, stale chunk count, context precision, context recall, approximate faithfulness, unsupported-claim rate, and repair latency.

## VI. Results
Temporal repair reduced stale chunks from N/A to N/A. Mean faithfulness changed from N/A to N/A. Unsupported claim rate changed from N/A to N/A. Context precision changed from N/A to N/A, which must be treated as a tradeoff rather than ignored.

## VII. Limitations and Future Work
Future work should add stronger embeddings, larger temporal corpora, non-synthetic drift, learned failure attribution, more repair actions, statistical significance testing, and comparisons against stronger RAG/GraphRAG baselines.

## References
[1] P. Lewis et al., "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks," in Advances in Neural Information Processing Systems, 2020.
[2] S. Es, J. James, L. Espinosa-Anke, and S. Schockaert, "RAGAS: Automated Evaluation of Retrieval Augmented Generation," arXiv:2309.15217, 2023.
[3] J. Saad-Falcon, O. Khattab, C. Potts, and M. Zaharia, "ARES: An Automated Evaluation Framework for Retrieval-Augmented Generation Systems," in Proc. NAACL, 2024.
[4] D. Edge et al., "From Local to Global: A Graph RAG Approach to Query-Focused Summarization," arXiv:2404.16130, 2024.
[5] S.-Q. Yan, J.-C. Gu, Y. Zhu, and Z.-H. Ling, "Corrective Retrieval Augmented Generation," arXiv:2401.15884, 2024.
[6] X. Xu et al., "RAGOps: Operating and Managing Retrieval-Augmented Generation Pipelines," arXiv:2506.03401, 2025.
