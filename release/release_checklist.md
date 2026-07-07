# RAGOps Sentinel Release Checklist

## Release Goal

Prepare RAGOps Sentinel as a recruiter-ready, interview-ready, and GitHub-reviewable AI/ML systems project.

## Validation Checklist

- [ ] `python -m pytest` passes
- [ ] `python scripts/local_ci.py` passes
- [ ] GitHub Actions is green
- [ ] Docker build validation passes in GitHub Actions
- [ ] README milestone table is current
- [ ] Recruiter summary exists
- [ ] Architecture document exists
- [ ] Skills matrix exists
- [ ] Interview talking points exist
- [ ] Repository map exists
- [ ] No generated drift is accidentally committed
- [ ] No secrets or API keys are committed
- [ ] Claims are honest and do not overstate production deployment

## Current Validated Status

| Area | Status |
|---|---|
| Unit tests | 58 passed after M16 |
| GitHub Actions | Green after M16 |
| CI/CD | Complete |
| Agentic workflow | Complete |
| Airflow orchestration | Complete |
| PySpark preprocessing | Complete |
| AI security guardrails | Complete |
| LLM provider abstraction | Complete |
| LoRA/PEFT fine-tuning-ready workflow | Complete |
| Helm/Terraform deployment packaging | Complete |
| Inference optimization | Complete |
| Recruiter documentation | In progress |

## Honest Claims Allowed

You can say:

- Production-style RAG reliability platform
- CI-validated AI/ML systems project
- Agentic RAG diagnosis and repair workflow
- AI security guardrails
- Helm/Terraform deployment templates
- LoRA/PEFT fine-tuning-ready workflow
- Inference optimization with response caching and async execution

Do not say unless separately executed:

- Live production deployment
- Fully deployed AWS infrastructure
- Fully deployed Kubernetes cluster
- Trained and deployed LoRA adapter
- Enterprise security compliance certification
