import numpy as np
from app.similarity.semantic import SemanticSimilarityCalculator
from app.similarity.lexical import LexicalSimilarityCalculator
from app.similarity.category import CategorySimilarityCalculator
from app.similarity.temporal import TemporalSimilarityCalculator
from datetime import datetime, timedelta

def test_semantic_similarity():
    v1 = np.array([1.0, 0.0, 0.0])
    v2 = np.array([1.0, 0.0, 0.0])
    v3 = np.array([0.0, 1.0, 0.0])
    assert SemanticSimilarityCalculator.calculate(v1, v2) == 1.0
    assert SemanticSimilarityCalculator.calculate(v1, v3) == 0.0

def test_lexical_similarity():
    calc = LexicalSimilarityCalculator()
    sim = calc.calculate("dangerous deep pothole", "dangerous deep road pothole")
    assert sim > 0.60

def test_category_similarity():
    assert CategorySimilarityCalculator.calculate("ROAD_POTHOLE", "ROAD_POTHOLE") == 1.0
    assert CategorySimilarityCalculator.calculate("ROAD_POTHOLE", "ROAD_STREETLIGHT") == 0.65
    assert CategorySimilarityCalculator.calculate("ROAD_POTHOLE", "GARBAGE_OVERFLOW") == 0.0

def test_temporal_similarity():
    t1 = datetime.utcnow()
    t2 = t1 - timedelta(days=2)
    t3 = t1 - timedelta(days=120)
    sim_close, _ = TemporalSimilarityCalculator.calculate(t1, t2)
    sim_far, _ = TemporalSimilarityCalculator.calculate(t1, t3)
    assert sim_close > 0.85
    assert sim_far == 0.0
