# Milestone 15 - LLM Fine-Tuning / LoRA-PEFT Ready Workflow

## Objective

Add a LoRA/PEFT fine-tuning-ready workflow for RAGOps Sentinel failure routing without requiring heavy GPU training in CI.

## Added Capabilities

- Failure-router fine-tuning dataset
- Instruction-tuning record formatter
- Dataset validation script
- LoRA/PEFT training-ready script
- CI-safe training-plan generation
- Lightweight failure-route inference module
- Optional fine-tuning requirements file
- Unit tests for dataset, training plan, and router behavior

## Skills Demonstrated

- LoRA / PEFT fine-tuning workflow design
- Hugging Face Transformers training structure
- Instruction-tuning dataset design
- Failure classification dataset construction
- RAG failure routing
- CI-safe fine-tuning validation

## Validation

Run:

python scripts/validate_fine_tuning_dataset.py

Expected: passed true

Run:

python scripts/prepare_fine_tuning_artifacts.py

Expected: LoRA / PEFT training plan with live_training_executed false

Run tests:

python -m pytest

Expected result after M15: 50 passed

## Limitation

This milestone adds a fine-tuning-ready LoRA/PEFT workflow and dataset validation. It does not claim that a trained LoRA adapter has been produced or deployed unless the optional training script is actually run.
