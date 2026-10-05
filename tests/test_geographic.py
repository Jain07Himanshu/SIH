from app.similarity.geographic import GeographicSimilarityCalculator

def test_haversine_distance():
    # Delhi Connaught Place to India Gate ~ 2.1 km
    lat1, lon1 = 28.6315, 77.2167
    lat2, lon2 = 28.6129, 77.2295
    dist = GeographicSimilarityCalculator.haversine_distance(lat1, lon1, lat2, lon2)
    assert 2000.0 < dist < 2500.0

def test_geographic_decay_functions():
    lat1, lon1 = 28.6139, 77.2090
    lat2, lon2 = 28.6140, 77.2091 # Very close ~15m
    sim_gauss, d = GeographicSimilarityCalculator.calculate(lat1, lon1, lat2, lon2, decay_function="gaussian")
    assert sim_gauss > 0.98
    assert d < 25.0

    # Far location (10 km away)
    lat3, lon3 = 28.7000, 77.3000
    sim_far, _ = GeographicSimilarityCalculator.calculate(lat1, lon1, lat3, lon3, max_distance_meters=5000.0)
    assert sim_far == 0.0

def test_missing_coordinates():
    sim, dist = GeographicSimilarityCalculator.calculate(None, None, 28.6139, 77.2090)
    assert sim is None
    assert dist is None
