import hashlib
import numpy as np
from app.embeddings.base import BaseEmbeddingProvider
from app.preprocessing.tokenizer import TextTokenizer
from app.extraction.synonyms import SynonymManager

class FallbackEmbeddingProvider(BaseEmbeddingProvider):
    """
    High-performance deterministic dense embedding provider using word hashing & synonym canonicalization.
    Ensures zero external download dependencies in air-gapped or test environments.
    """
    def __init__(self, dimension: int = 384, synonym_manager: SynonymManager | None = None):
        self.dimension = dimension
        self.tokenizer = TextTokenizer()
        self.synonyms = synonym_manager or SynonymManager()
        self.model_name = "deterministic-civic-hash-384"

    def _hash_token(self, token: str) -> int:
        h = int(hashlib.md5(token.encode('utf-8')).hexdigest(), 16)
        return h % self.dimension

    def encode_one(self, text: str) -> np.ndarray:
        vec = np.zeros(self.dimension, dtype=np.float32)
        if not text or not text.strip():
            return vec

        # Tokenize with stopwords removed for content focus
        tokens = self.tokenizer.tokenize(text.lower(), lowercase=True, remove_stopwords=True)
        canon_tokens = [self.synonyms.canonicalize(t) for t in tokens]

        # 1-grams (weight 2.0)
        for t in canon_tokens:
            idx = self._hash_token(t)
            vec[idx] += 2.0

        # 2-grams (weight 1.0)
        bigrams = self.tokenizer.extract_ngrams(canon_tokens, min_n=2, max_n=2)
        for bg in bigrams:
            idx = self._hash_token(bg)
            vec[idx] += 1.0

        norm = np.linalg.norm(vec)
        if norm > 1e-9:
            vec = vec / norm
        return vec

    def encode(self, texts: list[str]) -> np.ndarray:
        if not texts:
            return np.empty((0, self.dimension), dtype=np.float32)
        vectors = [self.encode_one(t) for t in texts]
        return np.vstack(vectors)

    def get_dimension(self) -> int:
        return self.dimension

    def get_model_name(self) -> str:
        return self.model_name
