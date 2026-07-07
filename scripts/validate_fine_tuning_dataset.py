from __future__ import annotations

import json
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from ragops.fine_tuning.failure_router_dataset import validate_failure_router_dataset


DATASET_PATH = Path("data/fine_tuning/failure_router_train.jsonl")


def validate_fine_tuning_dataset() -> dict[str, object]:
    if not DATASET_PATH.exists():
        return {
            "milestone": "M15_LORA_PEFT_FINE_TUNING_READY_WORKFLOW",
            "dataset_path": str(DATASET_PATH),
            "passed": False,
            "errors": ["Fine-tuning dataset file is missing."],
        }

    return validate_failure_router_dataset(DATASET_PATH)


def main() -> None:
    result = validate_fine_tuning_dataset()
    print(json.dumps(result, indent=2))

    if not result["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
