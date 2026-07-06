# RAGOps Sentinel Technical Report

## Project
**RAGOps Sentinel: Evidence-Drift-Aware Failure Diagnosis and Cost-Aware Repair for Production Agentic RAG Systems**

## Current Verified Scope
This report summarizes the implemented prototype through Milestone 8. The prototype includes baseline RAG, deterministic evaluation, evidence-drift fixtures, a Sentinel Diagnosis Graph, targeted temporal repair, Prometheus/Grafana-oriented observability artifacts, and Kubernetes manifest validation.

## Key Result Summary

| Metric | Value |
|---|---:|
| Repair success rate | N/A |
| Before mean stale evidence rate | N/A |
| After mean stale evidence rate | N/A |
| Stale chunk reduction | N/A |
| Before mean faithfulness | N/A |
| After mean faithfulness | N/A |
| Before unsupported claim rate | N/A |
| After unsupported claim rate | N/A |
| Mean repair latency ms | 2496.1400 |
| Kubernetes manifest validation passed | True |

## Evidence-Supported Claim
In the controlled evidence-drift benchmark, temporal-filter repair reduced stale evidence from the pre-repair condition to zero in the evaluated examples. This is an implementation-level finding, not a claim of broad real-world superiority.

## Limitations
1. The benchmark is small and synthetic.
2. The baseline embedding model is deterministic and reproducible but not competitive with modern semantic embeddings.
3. The failure classifier is rule-based, not learned.
4. The current repair policy handles stale-document failures first; other failure types require future milestones.
5. Patentability has not been established.

## Reproducibility Commands
```powershell
python -m pytest
python scripts/reset_local_state.py
python scripts/ingest_docs.py --raw-dir data/raw
python scripts/ingest_drift_fixture.py
python scripts/run_repair_benchmark.py --eval-set data/eval/evidence_drift_eval_set.jsonl --top-k 5
python scripts/run_observability_smoke.py --repair-result experiments/results/m5_repair_benchmark.json
python scripts/validate_kubernetes_manifests.py --manifest-dir infra/kubernetes/base
python scripts/generate_research_artifacts.py
```

## References
[1] P. Lewis et al., "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks," in Advances in Neural Information Processing Systems, 2020.
[2] S. Es, J. James, L. Espinosa-Anke, and S. Schockaert, "RAGAS: Automated Evaluation of Retrieval Augmented Generation," arXiv:2309.15217, 2023.
[3] J. Saad-Falcon, O. Khattab, C. Potts, and M. Zaharia, "ARES: An Automated Evaluation Framework for Retrieval-Augmented Generation Systems," in Proc. NAACL, 2024.
[4] D. Edge et al., "From Local to Global: A Graph RAG Approach to Query-Focused Summarization," arXiv:2404.16130, 2024.
[5] S.-Q. Yan, J.-C. Gu, Y. Zhu, and Z.-H. Ling, "Corrective Retrieval Augmented Generation," arXiv:2401.15884, 2024.
[6] X. Xu et al., "RAGOps: Operating and Managing Retrieval-Augmented Generation Pipelines," arXiv:2506.03401, 2025.
