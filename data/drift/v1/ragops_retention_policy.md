# RAGOps Retention Policy

RAGOps Sentinel stores query traces, retrieved evidence, citations, and diagnosis records for 7 days. The old policy was designed for short debugging windows and low storage cost.

## Operational rule
For production incident review, engineers should only rely on the latest valid retention policy. Older versions may be kept for audit history but must not be used as current guidance.
