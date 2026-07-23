import os
import re
import numpy as np
from typing import List, Union
from app.core.config import get_settings


class EmbeddingGenerator:
    """
    Generates embeddings for texts. Supports:
    1. OpenAI embeddings (if API key is present)
    2. Local TF-IDF bag-of-words embeddings (pure Python/NumPy fallback for keyless environments)
    """

    def __init__(self):
        settings = get_settings()
        self.openai_key = os.getenv("OPENAI_API_KEY") or getattr(settings, "openai_api_key", None)
        self.client = None
        self._vocab = None

        if self.openai_key:
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=self.openai_key)
            except Exception:
                pass

    def get_dim(self) -> int:
        if self.client:
            return 1536  # text-embedding-3-small
        return 1000  # Local TF-IDF fallback vector dimension

    def _clean_text(self, text: str) -> str:
        text = text.lower()
        # Preserve ₹ symbol, numbers, letters, and whitespace for rupee amount matching
        text = re.sub(r"[^a-z0-9\s₹]", " ", text)
        return text

    def build_vocab(self, documents: List[str]):
        """
        Builds a vocabulary from a list of documents for the TF-IDF fallback.
        """
        words = []
        for doc in documents:
            cleaned = self._clean_text(doc)
            words.extend(cleaned.split())

        from collections import Counter
        counts = Counter(words)
        most_common = counts.most_common(self.get_dim())
        self._vocab = {word: idx for idx, (word, _) in enumerate(most_common)}

    def encode(self, texts: Union[str, List[str]]) -> List[List[float]]:
        if isinstance(texts, str):
            texts = [texts]

        # Use OpenAI if key is present
        if self.client:
            try:
                response = self.client.embeddings.create(
                    input=texts,
                    model="text-embedding-3-small"
                )
                return [data.embedding for data in response.data]
            except Exception:
                pass

        # Fallback TF-IDF implementation
        if not self._vocab:
            default_words = [
                "startup", "business", "mvp", "funding", "market", "product", "growth",
                "founder", "manufacturing", "ai", "healthcare", "iot", "lakh", "under",
                "10", "investment", "robotics", "food", "processing", "ev", "electric"
            ]
            self._vocab = {word: idx for idx, word in enumerate(default_words)}

        dim = self.get_dim()
        vectors = []

        for text in texts:
            vector = np.zeros(dim)
            cleaned = self._clean_text(text)
            words = cleaned.split()
            if not words:
                vectors.append(vector.tolist())
                continue

            for word in words:
                if word in self._vocab:
                    idx = self._vocab[word]
                    if idx < dim:
                        vector[idx] += 1.0

            # Normalize vector (L2 norm)
            norm = np.linalg.norm(vector)
            if norm > 0:
                vector = vector / norm

            vectors.append(vector.tolist())

        return vectors
