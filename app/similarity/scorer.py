import numpy as np
from app.core.config import get_config
from app.schemas.complaint import ComplaintRecord, KeywordItem
from app.schemas.similarity import (
    SimilarityComponents,
    MatchEvidence,
    MatchExplanation,
    SimilarityMatchResult
)
from app.similarity.semantic import SemanticSimilarityCalculator
from app.similarity.lexical import LexicalSimilarityCalculator
from app.similarity.geographic import GeographicSimilarityCalculator
from app.similarity.temporal import TemporalSimilarityCalculator
from app.similarity.category import CategorySimilarityCalculator
from app.extraction.synonyms import SynonymManager

class CompositeSimilarityScorer:
    def __init__(self, synonym_manager: SynonymManager | None = None):
        self.config = get_config()
        self.synonyms = synonym_manager or SynonymManager()
        self.semantic_calc = SemanticSimilarityCalculator()
        self.lexical_calc = LexicalSimilarityCalculator(synonym_manager=self.synonyms)
        self.geo_calc = GeographicSimilarityCalculator()
        self.temp_calc = TemporalSimilarityCalculator()
        self.cat_calc = CategorySimilarityCalculator()

    def compare_keywords(self, kw_a: list[KeywordItem | str], kw_b: list[KeywordItem | str]) -> tuple[float, list[str]]:
        terms_a = set([self.synonyms.canonicalize(k.term.lower() if isinstance(k, KeywordItem) else str(k).lower()) for k in kw_a])
        terms_b = set([self.synonyms.canonicalize(k.term.lower() if isinstance(k, KeywordItem) else str(k).lower()) for k in kw_b])

        if not terms_a or not terms_b:
            return 0.0, []

        shared = list(terms_a.intersection(terms_b))
        jaccard = len(shared) / max(1, len(terms_a.union(terms_b)))
        return float(round(jaccard, 4)), shared

    def score_pair(self,
                   complaint_a: ComplaintRecord,
                   complaint_b: ComplaintRecord,
                   emb_a: np.ndarray | None = None,
                   emb_b: np.ndarray | None = None,
                   kw_a: list[KeywordItem] | None = None,
                   kw_b: list[KeywordItem] | None = None) -> SimilarityMatchResult:
        
        cfg = self.config.similarity
        weights = cfg.weights

        # 1. Semantic
        sem_score = self.semantic_calc.calculate(emb_a, emb_b) if emb_a is not None and emb_b is not None else 0.0

        # 2. Lexical
        lex_score = self.lexical_calc.calculate(complaint_a.text, complaint_b.text)

        # 3. Keyword
        kw_score, shared_keywords = self.compare_keywords(kw_a or [], kw_b or [])

        # 4. Category
        cat_score = self.cat_calc.calculate(complaint_a.category, complaint_b.category)

        # 5. Geographic
        geo_score, dist_meters = self.geo_calc.calculate(
            complaint_a.latitude, complaint_a.longitude,
            complaint_b.latitude, complaint_b.longitude,
            max_distance_meters=cfg.geographic.max_distance_meters,
            sigma_meters=cfg.geographic.sigma_meters,
            decay_function=cfg.geographic.decay_function
        )

        # 6. Temporal
        temp_score, diff_days = self.temp_calc.calculate(
            complaint_a.timestamp, complaint_b.timestamp,
            max_days=cfg.temporal.max_days,
            half_life_days=cfg.temporal.half_life_days,
            decay_function=cfg.temporal.decay_function
        )

        # Weight re-normalization when geo or temp data is missing
        active_weights: dict[str, float] = {
            "semantic": weights.semantic,
            "lexical": weights.lexical,
            "keyword": weights.keyword,
            "category": weights.category,
        }
        score_values: dict[str, float] = {
            "semantic": sem_score,
            "lexical": lex_score,
            "keyword": kw_score,
            "category": cat_score,
        }

        if geo_score is not None:
            active_weights["geographic"] = weights.geographic
            score_values["geographic"] = geo_score
        else:
            geo_score = 1.0

        if temp_score is not None:
            active_weights["temporal"] = weights.temporal
            score_values["temporal"] = temp_score
        else:
            temp_score = 1.0

        total_active_weight = sum(active_weights.values())
        final_score = sum(score_values[k] * (active_weights[k] / total_active_weight) for k in active_weights)
        final_score = float(round(np.clip(final_score, 0.0, 1.0), 4))

        # Decision thresholds
        th = self.config.thresholds
        if final_score >= th.duplicate:
            match_type = "DUPLICATE"
        elif final_score >= th.possible_match:
            match_type = "POSSIBLY_SIMILAR"
        else:
            match_type = "NEW_ISSUE"

        needs_review = abs(final_score - th.duplicate) <= th.needs_review_margin or \
                       abs(final_score - th.possible_match) <= th.needs_review_margin

        if sem_score >= 0.80:
            sem_desc = "Highly similar meaning and description"
        elif sem_score >= 0.60:
            sem_desc = "Moderately similar grievance topic"
        else:
            sem_desc = "Distinct grievance wording"

        same_cat = (complaint_a.category is not None and complaint_a.category == complaint_b.category)
        loc_match = (dist_meters is not None and dist_meters <= 500.0)

        summary_points = [f"Semantic match: {sem_desc}"]
        if shared_keywords:
            summary_points.append(f"Shared keywords: {', '.join(shared_keywords[:4])}")
        if same_cat:
            summary_points.append("Identical grievance category")
        if loc_match:
            summary_points.append(f"Nearby location ({int(dist_meters)}m)")

        evidence = MatchEvidence(
            match_type=match_type,
            confidence=final_score,
            explanation=MatchExplanation(
                semantic_match=sem_desc,
                shared_keywords=shared_keywords,
                same_category=same_cat,
                distance_meters=dist_meters,
                location_match=loc_match,
                temporal_gap_days=diff_days,
                summary="; ".join(summary_points)
            ),
            needs_review=needs_review
        )

        components = SimilarityComponents(
            semantic_similarity=sem_score,
            lexical_similarity=lex_score,
            keyword_similarity=kw_score,
            category_similarity=cat_score,
            geographic_similarity=geo_score,
            temporal_similarity=temp_score
        )

        return SimilarityMatchResult(
            complaint_id=complaint_a.complaint_id,
            matched_complaint_id=complaint_b.complaint_id,
            similarity_score=final_score,
            match_type=match_type,
            components=components,
            evidence=evidence
        )
