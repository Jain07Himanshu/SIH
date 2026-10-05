from typing import Optional, Any
from app.integrations.duplicate_engine.client import DuplicateEngineClient

class DuplicateEngineService:
    def __init__(self):
        self.client = DuplicateEngineClient()

    def process_complaint(self,
                          complaint_id: str,
                          text: str,
                          category: Optional[str] = None,
                          priority: Optional[str] = None,
                          latitude: Optional[float] = None,
                          longitude: Optional[float] = None,
                          locality: Optional[str] = None,
                          ward: Optional[str] = None,
                          timestamp: Optional[Any] = None) -> dict[str, Any]:
        return self.client.analyze_complaint(
            complaint_id=complaint_id,
            text=text,
            category=category,
            priority=priority,
            latitude=latitude,
            longitude=longitude,
            timestamp=str(timestamp) if timestamp else None
        )

    def process_new_complaint(self, **kwargs) -> dict[str, Any]:
        return self.process_complaint(**kwargs)

