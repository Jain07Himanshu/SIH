from abc import ABC, abstractmethod
import numpy as np

class BaseEmbeddingProvider(ABC):
    @abstractmethod
    def encode(self, texts: list[str]) -> np.ndarray:
        pass

    @abstractmethod
    def encode_one(self, text: str) -> np.ndarray:
        pass

    @abstractmethod
    def get_dimension(self) -> int:
        pass

    @abstractmethod
    def get_model_name(self) -> str:
        pass
