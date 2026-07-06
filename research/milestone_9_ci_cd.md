# Milestone 9 — CI/CD and Software Engineering Automation

## Objective

Add CI/CD and software engineering automation to RAGOps Sentinel.

## Added Capabilities

- GitHub Actions workflow
- Automated pytest execution
- Kubernetes manifest validation in CI
- Research artifact generation in CI
- Docker image build validation
- Local CI runner script
- Makefile for repeatable developer commands

## Skills Demonstrated

- GitHub Actions
- CI/CD
- Automated testing
- Docker build validation
- Reproducible ML system checks
- Software engineering hygiene

## Validation

Run locally:

python scripts/local_ci.py

Expected result:

M9 local CI checks passed.

Run tests:

python -m pytest

Expected result after M9:

17 passed

## Limitation

This milestone validates build/test automation. It does not add cloud deployment, Airflow, Spark, LangGraph, fine-tuning, Terraform, or Helm yet.
