import numpy as np
from app.core.config import get_config
from app.embeddings.base import BaseEmbeddingProvider
from app.embeddings.fallback_provider import FallbackEmbeddingProvider

class EmbeddingEncoder:
    def __init__(self, provider: BaseEmbeddingProvider | None = None):
        if provider is not None:
            self.provider = provider
        else:
            config = get_config()
            provider_type = config.embedding.provider
            if provider_type == "sentence_transformers":
                from app.embeddings.sentence_transformer_provider import SentenceTransformerProvider
                self.provider = SentenceTransformerProvider(
                    model_name=config.embedding.model_name,
                    normalize_embeddings=config.embedding.normalize_embeddings
                )
            elif provider_type == "auto":
                try:
                    from app.embeddings.sentence_transformer_provider import SentenceTransformerProvider
                    self.provider = SentenceTransformerProvider(
                        model_name=config.embedding.model_name,
                        normalize_embeddings=config.embedding.normalize_embeddings
                    )
                except Exception:
                    self.provider = FallbackEmbeddingProvider(dimension=config.embedding.dimension)
            else:
                self.provider = FallbackEmbeddingProvider(dimension=config.embedding.dimension)

        self.cache: dict[str, np.ndarray] = {}
        self.cache_limit = 10000

    def encode_one(self, text: str) -> np.ndarray:
        if text in self.cache:
            return self.cache[text]
        vec = self.provider.encode_one(text)
        if len(self.cache) < self.cache_limit:
            self.cache[text] = vec
        return vec

    def encode(self, texts: list[str]) -> np.ndarray:
        uncached_indices = [i for i, t in enumerate(texts) if t not in self.cache]
        if uncached_indices:
            uncached_texts = [texts[i] for i in uncached_indices]
            computed_vectors = self.provider.encode(uncached_texts)
            for idx, vec in zip(uncached_indices, computed_vectors):
                t = texts[idx]
                if len(self.cache) < self.cache_limit:
                    self.cache[t] = vec

        result = [self.cache.get(t, self.provider.encode_one(t)) for t in texts]
        return np.vstack(result) if result else np.empty((0, self.provider.get_dimension()), dtype=np.float32)

    def get_dimension(self) -> int:
        return self.provider.get_dimension()

    def get_model_name(self) -> str:
        return self.provider.get_model_name()
