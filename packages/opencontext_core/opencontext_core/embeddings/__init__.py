"""Async embedding generation and vector storage.

This package provides infrastructure for generating embeddings asynchronously
with a guaranteed <150ms synchronous write path during indexing.

Architecture:
- EmbeddingWorker: Async background worker that processes embedding queues
- VectorStore: Storage interface for embeddings (vectors + metadata)
- LocalVectorStore: File-based vector storage for development
- EmbeddingGenerator: Provider-specific embedding generation (OpenAI, Cohere, local)
"""

from __future__ import annotations
