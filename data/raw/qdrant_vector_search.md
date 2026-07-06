# Qdrant Vector Search

Qdrant is used as the baseline vector database in RAGOps Sentinel. Each document chunk is converted into a vector and stored with payload metadata such as document identifier, version identifier, section title, and freshness flags.

## Metadata filtering

Metadata filters are necessary for temporal retrieval because the system must retrieve the current valid document version when a newer document supersedes an older one.
