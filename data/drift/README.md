# Evidence Drift Fixture

This folder contains two versions of the same document with the same file name.

- `v1/ragops_retention_policy.md`: old policy, trace retention is 7 days.
- `v2/ragops_retention_policy.md`: current policy, trace retention is 90 days.

The file stem is intentionally identical so the ingestion layer treats both files as versions of the same document.
