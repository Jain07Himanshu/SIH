import json
import numpy as np
from sqlalchemy.orm import Session
from app.repositories.base import BaseRepository
from app.db.models import ComplaintModel, ComplaintEmbeddingModel, ComplaintKeywordModel
from app.schemas.complaint import ComplaintRecord, NormalizedComplaint

class ComplaintRepository(BaseRepository):
    def create(self, record: ComplaintRecord, clean_text: str | None = None) -> ComplaintModel:
        model = ComplaintModel(
            complaint_id=record.complaint_id,
            text=record.text,
            clean_text=clean_text or record.text,
            category_id=record.category,
            department_id=record.department,
            priority=record.priority,
            latitude=record.latitude,
            longitude=record.longitude,
            timestamp=record.timestamp,
            source=record.source,
            raw_metadata=record.metadata
        )
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return model

    def get_by_id(self, complaint_id: str) -> ComplaintModel | None:
        return self.db.query(ComplaintModel).filter(ComplaintModel.complaint_id == complaint_id).first()

    def get_all(self, limit: int = 1000, offset: int = 0) -> list[ComplaintModel]:
        return self.db.query(ComplaintModel).offset(offset).limit(limit).all()

    def save_embedding(self, complaint_id: str, vector: np.ndarray, model_name: str) -> ComplaintEmbeddingModel:
        emb_json = json.dumps(vector.tolist())
        emb_model = ComplaintEmbeddingModel(
            complaint_id=complaint_id,
            embedding_json=emb_json,
            dimension=len(vector),
            model_name=model_name
        )
        self.db.add(emb_model)
        self.db.commit()
        return emb_model

    def save_keywords(self, complaint_id: str, keywords) -> None:
        for kw in keywords:
            term = kw.term if hasattr(kw, "term") else str(kw)
            score = kw.score if hasattr(kw, "score") else 1.0
            ttype = kw.type if hasattr(kw, "type") else "issue"
            kw_model = ComplaintKeywordModel(
                complaint_id=complaint_id,
                term=term,
                score=score,
                term_type=ttype
            )
            self.db.add(kw_model)
        self.db.commit()
