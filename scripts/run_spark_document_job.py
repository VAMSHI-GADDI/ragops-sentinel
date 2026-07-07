from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from ragops.spark.document_version_job import run_document_version_job


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run RAGOps Sentinel document-version preprocessing."
    )
    parser.add_argument(
        "--input-dir",
        action="append",
        dest="input_dirs",
        default=None,
        help="Input directory. Can be supplied multiple times.",
    )
    parser.add_argument("--output-dir", default="data/processed")
    parser.add_argument(
        "--engine",
        choices=["local", "spark", "auto"],
        default="local",
    )
    args = parser.parse_args()

    input_dirs = args.input_dirs or ["data/raw", "data/drift"]

    result = run_document_version_job(
        input_dirs=input_dirs,
        output_dir=args.output_dir,
        engine=args.engine,
    )

    print(json.dumps(result, indent=2))

    if not result["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
