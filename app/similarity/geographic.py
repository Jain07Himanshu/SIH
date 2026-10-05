import math

class GeographicSimilarityCalculator:
    EARTH_RADIUS_METERS = 6371000.0

    @staticmethod
    def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)

        a = math.sin(delta_phi / 2.0) ** 2 + \
            math.cos(phi1) * math.cos(phi2) * \
            math.sin(delta_lambda / 2.0) ** 2
        c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
        return GeographicSimilarityCalculator.EARTH_RADIUS_METERS * c

    @staticmethod
    def calculate(lat1: float | None, lon1: float | None, lat2: float | None, lon2: float | None,
                  max_distance_meters: float = 5000.0, sigma_meters: float = 800.0,
                  decay_function: str = "gaussian") -> tuple[float | None, float | None]:
        if lat1 is None or lon1 is None or lat2 is None or lon2 is None:
            return None, None

        dist = GeographicSimilarityCalculator.haversine_distance(lat1, lon1, lat2, lon2)
        if dist > max_distance_meters:
            return 0.0, dist

        if decay_function == "gaussian":
            sim = math.exp(- (dist / sigma_meters) ** 2)
        elif decay_function == "exponential":
            sim = math.exp(- dist / sigma_meters)
        else: # linear
            sim = max(0.0, 1.0 - (dist / max_distance_meters))

        return float(round(sim, 4)), float(round(dist, 1))
