import numpy as np

class SemanticSimilarityCalculator:
    @staticmethod
    def calculate(vec_a: np.ndarray, vec_b: np.ndarray) -> float:
        if vec_a is None or vec_b is None:
            return 0.0
        norm_a = np.linalg.norm(vec_a)
        norm_b = np.linalg.norm(vec_b)
        if norm_a < 1e-9 or norm_b < 1e-9:
            return 0.0
        dot = float(np.dot(vec_a, vec_b))
        sim = dot / (norm_a * norm_b)
        return float(np.clip(sim, 0.0, 1.0))
