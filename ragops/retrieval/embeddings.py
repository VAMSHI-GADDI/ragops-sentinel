from __future__ import annotations
import numpy as np
from sklearn.feature_extraction.text import HashingVectorizer
from sklearn.preprocessing import normalize

from ragops.config import get_settings


class HashingEmbeddingModel:
    """Deterministic baseline embedding model.

    This is not a state-of-the-art semantic model. It is used for Milestone 1 so the
    pipeline is fully reproducible and can run without API keys or GPUs.
    """

    def __init__(self, n_features: int | None = None):
        settings = get_settings()
        self.n_features = n_features or settings.embedding_dim
        self.vectorizer = HashingVectorizer(
            n_features=self.n_features,
            alternate_sign=False,
            norm=None,
            analyzer="word",
            ngram_range=(1, 2),
            stop_words="english",
        )

    def embed(self, texts: list[str]) -> list[list[float]]:
        mat = self.vectorizer.transform(texts)
        mat = normalize(mat, norm="l2", axis=1)
        arr = mat.astype(np.float32).toarray()
        return arr.tolist()

    def embed_one(self, text: str) -> list[float]:
        return self.embed([text])[0]
