import math
from datetime import datetime

class TemporalSimilarityCalculator:
    @staticmethod
    def calculate(ts1: datetime | None, ts2: datetime | None,
                  max_days: float = 90.0, half_life_days: float = 14.0,
                  decay_function: str = "exponential") -> tuple[float | None, float | None]:
        if ts1 is None or ts2 is None:
            return None, None

        diff_seconds = abs((ts1 - ts2).total_seconds())
        diff_days = diff_seconds / 86400.0

        if diff_days > max_days:
            return 0.0, round(diff_days, 1)

        if decay_function == "exponential":
            # sim = 2^(-diff / half_life)
            sim = math.pow(2.0, - (diff_days / half_life_days))
        else: # linear
            sim = max(0.0, 1.0 - (diff_days / max_days))

        return float(round(sim, 4)), float(round(diff_days, 1))
