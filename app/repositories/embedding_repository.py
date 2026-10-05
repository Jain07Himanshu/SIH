import json
import numpy as np
from sqlalchemy.orm import Session
from app.repositories.base import BaseRepository
from app.db.models import ComplaintEmbeddingModel

class EmbeddingRepository(BaseRepository):
    def get_embedding(self, complaint_id: str) -> np.ndarray | None:
        row = self.db.query(ComplaintEmbeddingModel).filter(ComplaintEmbeddingModel.complaint_id == complaint_id).first()
        if not row:
            return None
        return np.array(json.loads(row.embedding_json), dtype=np.float32)

    def get_all_embeddings(self) -> dict[str, np.ndarray]:
        rows = self.db.query(ComplaintEmbeddingModel).all()
        return {r.complaint_id: np.array(json.loads(r.embedding_json), dtype=np.float32) for r in rows}
