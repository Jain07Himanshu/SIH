class CategorySimilarityCalculator:
    @staticmethod
    def calculate(cat_a: str | None, cat_b: str | None) -> float:
        if not cat_a or not cat_b:
            return 0.50 # Neutral score when category is missing
        cat_a_norm = cat_a.strip().upper()
        cat_b_norm = cat_b.strip().upper()

        if cat_a_norm == cat_b_norm:
            return 1.0
        # Partial match on prefix / domain (e.g. ROAD_POTHOLE vs ROAD_SURFACE)
        prefix_a = cat_a_norm.split("_")[0]
        prefix_b = cat_b_norm.split("_")[0]
        if prefix_a == prefix_b:
            return 0.65
        return 0.0
