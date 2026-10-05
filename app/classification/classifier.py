import numpy as np
from app.classification.taxonomy import TaxonomyManager
from app.schemas.category import CategoryPrediction
from app.extraction.synonyms import SynonymManager

class CategoryClassifier:
    def __init__(self, taxonomy_manager: TaxonomyManager | None = None, synonym_manager: SynonymManager | None = None):
        self.taxonomy = taxonomy_manager or TaxonomyManager()
        self.synonyms = synonym_manager or SynonymManager()
        self.prototype_embeddings: np.ndarray | None = None
        self.prototype_category_ids: list[str] = []

    def fit_prototypes(self, embedding_encoder) -> None:
        if not self.taxonomy.category_prototypes:
            return
        proto_texts = [p[1] for p in self.taxonomy.category_prototypes]
        self.prototype_category_ids = [p[0] for p in self.taxonomy.category_prototypes]
        self.prototype_embeddings = embedding_encoder.encode(proto_texts)

    def classify(self, text: str, complaint_embedding: np.ndarray | None = None, embedding_encoder = None) -> CategoryPrediction:
        if not self.taxonomy.categories:
            return CategoryPrediction(
                category_id="OTHER_GENERAL",
                category_name="Other Civic Grievances",
                confidence=0.50,
                department_id="GENERAL_DEPT",
                department_name="General Public Grievance Cell",
                explanation="Default unclassified assignment."
            )

        best_cat_id = "OTHER_GENERAL"
        best_conf = 0.40
        matched_proto = ""

        if self.prototype_embeddings is None and embedding_encoder is not None:
            self.fit_prototypes(embedding_encoder)

        if self.prototype_embeddings is not None:
            if complaint_embedding is None and embedding_encoder is not None:
                complaint_embedding = embedding_encoder.encode_one(text)
            if complaint_embedding is not None:
                sims = np.dot(self.prototype_embeddings, complaint_embedding)
                best_idx = int(np.argmax(sims))
                semantic_score = float(sims[best_idx])
                if semantic_score > best_conf:
                    best_cat_id = self.prototype_category_ids[best_idx]
                    best_conf = semantic_score
                    matched_proto = self.taxonomy.category_prototypes[best_idx][1]

        norm_text = text.lower()
        for cat_id, cat in self.taxonomy.categories.items():
            kw_matches = 0
            for kw in cat.keywords:
                if kw in norm_text or self.synonyms.canonicalize(kw) in norm_text:
                    kw_matches += 1
            if kw_matches > 0:
                kw_score = min(0.95, 0.55 + 0.15 * kw_matches)
                if kw_score > best_conf:
                    best_cat_id = cat_id
                    best_conf = kw_score
                    matched_proto = f"Matched keywords: {kw_matches}"

        cat_record = self.taxonomy.get_category(best_cat_id)
        cat_name = cat_record.name if cat_record else "Other Civic Grievances"
        dept_id = cat_record.department_id if cat_record else "GENERAL_DEPT"
        dept_record = self.taxonomy.get_department(dept_id)
        dept_name = dept_record.name if dept_record else "General Public Grievance Cell"

        return CategoryPrediction(
            category_id=best_cat_id,
            category_name=cat_name,
            confidence=round(float(best_conf), 2),
            department_id=dept_id,
            department_name=dept_name,
            explanation=f"Classified into {cat_name} with confidence {best_conf:.2f}. ({matched_proto})"
        )
