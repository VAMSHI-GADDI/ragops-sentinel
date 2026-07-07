from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from ragops.fine_tuning.train_lora_failure_router import (
    LoRATrainingConfig,
    build_training_plan,
    write_instruction_records,
    write_training_plan,
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Prepare CI-safe LoRA/PEFT failure-router fine-tuning artifacts."
    )
    parser.add_argument("--dataset-path", default="data/fine_tuning/failure_router_train.jsonl")
    parser.add_argument("--output-dir", default="research/fine_tuning")
    parser.add_argument("--base-model", default="distilgpt2")
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    config = LoRATrainingConfig(
        base_model=args.base_model,
        dataset_path=args.dataset_path,
        output_dir="models/failure_router_lora",
    )

    instruction_path = write_instruction_records(
        dataset_path=args.dataset_path,
        output_path=output_dir / "failure_router_instruction_records.jsonl",
    )
    plan_path = write_training_plan(
        config=config,
        output_path=output_dir / "failure_router_lora_training_plan.json",
    )

    result = build_training_plan(config)
    result["instruction_records_path"] = str(instruction_path)
    result["training_plan_path"] = str(plan_path)

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
