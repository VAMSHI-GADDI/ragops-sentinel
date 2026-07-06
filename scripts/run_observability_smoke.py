from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from ragops.observability.snapshot import build_observability_snapshot


def main() -> None:
    parser = argparse.ArgumentParser(description="Build Milestone-6 observability snapshot from repair benchmark output.")
    parser.add_argument("--repair-result", default="experiments/results/m5_repair_benchmark.json")
    parser.add_argument("--output", default="experiments/results/m6_observability_snapshot.json")
    args = parser.parse_args()

    snapshot = build_observability_snapshot(Path(args.repair_result), Path(args.output))
    print(json.dumps(snapshot, indent=2))
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
