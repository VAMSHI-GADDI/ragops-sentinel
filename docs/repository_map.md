# RAGOps Sentinel Repository Map

## Main Application

| Path | Purpose |
|---|---|
| ragops/ | Core Python package |
| ragops/agents/ | LangGraph/LangChain-style agent workflow |
| ragops/security/ | AI security guardrails |
| ragops/llm_providers/ | Managed cloud LLM provider abstraction |
| ragops/fine_tuning/ | LoRA/PEFT fine-tuning-ready failure router |
| ragops/optimization/ | Inference optimization utilities |

## Scripts

| Path | Purpose |
|---|---|
| scripts/local_ci.py | Runs local validation workflow |
| scripts/validate_kubernetes_manifests.py | Validates Kubernetes manifests |
| scripts/validate_airflow_dag.py | Validates Airflow DAG structure |
| scripts/validate_spark_job.py | Validates Spark preprocessing workflow |
| scripts/validate_security_guardrails.py | Validates AI security guardrails |
| scripts/validate_llm_providers.py | Validates LLM provider abstraction |
| scripts/validate_fine_tuning_dataset.py | Validates fine-tuning dataset |
| scripts/prepare_fine_tuning_artifacts.py | Generates fine-tuning instruction records and training plan |
| scripts/run_inference_benchmark.py | Runs inference cache benchmark |
| scripts/validate_deployment_packaging.py | Validates Helm, Terraform, and optimization packaging |

## Infrastructure

| Path | Purpose |
|---|---|
| Dockerfile | API container build |
| docker-compose.yml | Local service orchestration |
| infra/kubernetes/ | Kubernetes manifests |
| infra/helm/ | Helm chart packaging |
| infra/terraform/ | Terraform AWS templates |
| infra/airflow/ | Airflow DAG packaging |
| infra/databricks/ | Databricks/Spark-style packaging notes |

## Research and Reports

| Path | Purpose |
|---|---|
| research/ | Milestone research notes |
| research/artifacts/ | Generated technical artifacts |
| research/fine_tuning/ | Generated fine-tuning records and training plan |
| experiments/results/ | Validation outputs and experiment results |
| docs/ | Recruiter and architecture documentation |
| release/ | Final release checklist and packaging notes |

## Tests

| Path | Purpose |
|---|---|
| tests/ | Pytest test suite |
| .github/workflows/ci.yml | GitHub Actions CI workflow |

## Best Files for Recruiters to Read First

1. README.md
2. docs/recruiter_project_summary.md
3. docs/architecture.md
4. docs/skills_matrix.md
5. docs/interview_talking_points.md
6. research/milestone_16_helm_terraform_inference_optimization.md
