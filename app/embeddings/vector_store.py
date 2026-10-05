from abc import ABC, abstractmethod
from typing import Any
import numpy as np

class BaseVectorStore(ABC):
    @abstractmethod
    def add(self, complaint_id: str, vector: np.ndarray, metadata: dict[str, Any] | None = None) -> None:
        pass

    @abstractmethod
    def add_batch(self, items: list[tuple[str, np.ndarray, dict[str, Any]]]) -> None:
        pass

    @abstractmethod
    def search(self, query_vector: np.ndarray, top_k: int = 25, filter_dict: dict[str, Any] | None = None) -> list[tuple[str, float, dict[str, Any]]]:
        pass

    @abstractmethod
    def get(self, complaint_id: str) -> tuple[np.ndarray, dict[str, Any]] | None:
        pass

    @abstractmethod
    def delete(self, complaint_id: str) -> bool:
        pass

    @abstractmethod
    def count(self) -> int:
        pass

class InMemoryVectorStore(BaseVectorStore):
    def __init__(self):
        self.ids: list[str] = []
        self.id_to_idx: dict[str, int] = {}
        self.vectors: np.ndarray | None = None
        self.metadatas: list[dict[str, Any]] = []

    def add(self, complaint_id: str, vector: np.ndarray, metadata: dict[str, Any] | None = None) -> None:
        self.add_batch([(complaint_id, vector, metadata or {})])

    def add_batch(self, items: list[tuple[str, np.ndarray, dict[str, Any]]]) -> None:
        if not items:
            return
        new_ids = [it[0] for it in items]
        new_vecs = np.vstack([it[1] for it in items])
        new_meta = [it[2] for it in items]

        for cid in new_ids:
            if cid in self.id_to_idx:
                self.delete(cid)

        start_idx = len(self.ids)
        self.ids.extend(new_ids)
        self.metadatas.extend(new_meta)
        for i, cid in enumerate(new_ids):
            self.id_to_idx[cid] = start_idx + i

        if self.vectors is None:
            self.vectors = new_vecs
        else:
            self.vectors = np.vstack([self.vectors, new_vecs])

    def search(self, query_vector: np.ndarray, top_k: int = 25, filter_dict: dict[str, Any] | None = None) -> list[tuple[str, float, dict[str, Any]]]:
        if self.vectors is None or len(self.ids) == 0:
            return []

        scores = np.dot(self.vectors, query_vector)
        ranked_indices = np.argsort(scores)[::-1]

        results: list[tuple[str, float, dict[str, Any]]] = []
        for idx in ranked_indices:
            cid = self.ids[idx]
            meta = self.metadatas[idx]

            if filter_dict:
                match = True
                for k, v in filter_dict.items():
                    if meta.get(k) != v:
                        match = False
                        break
                if not match:
                    continue

            score = float(scores[idx])
            results.append((cid, score, meta))
            if len(results) >= top_k:
                break

        return results

    def get(self, complaint_id: str) -> tuple[np.ndarray, dict[str, Any]] | None:
        if complaint_id not in self.id_to_idx or self.vectors is None:
            return None
        idx = self.id_to_idx[complaint_id]
        return self.vectors[idx], self.metadatas[idx]

    def delete(self, complaint_id: str) -> bool:
        if complaint_id not in self.id_to_idx or self.vectors is None:
            return False
        idx = self.id_to_idx[complaint_id]
        self.ids.pop(idx)
        self.metadatas.pop(idx)
        self.vectors = np.delete(self.vectors, idx, axis=0)
        self.id_to_idx = {cid: i for i, cid in enumerate(self.ids)}
        return True

    def count(self) -> int:
        return len(self.ids)
