from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Iterable
from pydantic import BaseModel, Field
from app.schemas.complaint import ComplaintRecord


class DatasetMappingConfig(BaseModel):
    complaint_id_field: str = "complaint_id"
    text_field: str = "text"
    category_field: str | None = "category"
    department_field: str | None = "department"
    priority_field: str | None = "priority"
    latitude_field: str | None = "latitude"
    longitude_field: str | None = "longitude"
    timestamp_field: str | None = "timestamp"
    source_field: str | None = "source"
    metadata_fields: list[str] | None = None


class BaseDatasetAdapter(ABC):
    def __init__(self, mapping_config: DatasetMappingConfig | dict[str, Any] | None = None):
        if isinstance(mapping_config, dict):
            self.mapping = DatasetMappingConfig(**mapping_config)
        elif isinstance(mapping_config, DatasetMappingConfig):
            self.mapping = mapping_config
        else:
            self.mapping = DatasetMappingConfig()

    def adapt_record(self, raw: dict[str, Any]) -> ComplaintRecord:
        complaint_id = raw.get(self.mapping.complaint_id_field)
        if not complaint_id:
            raise ValueError(f"Missing required ID field '{self.mapping.complaint_id_field}'")

        text = raw.get(self.mapping.text_field)
        if not text or not str(text).strip():
            raise ValueError(f"Missing or empty required text field '{self.mapping.text_field}'")

        category = raw.get(self.mapping.category_field) if self.mapping.category_field else None
        department = raw.get(self.mapping.department_field) if self.mapping.department_field else None
        priority = raw.get(self.mapping.priority_field) if self.mapping.priority_field else None

        lat = None
        if self.mapping.latitude_field and raw.get(self.mapping.latitude_field) is not None:
            try:
                lat = float(raw[self.mapping.latitude_field])
                if not (-90.0 <= lat <= 90.0):
                    raise ValueError()
            except Exception:
                raise ValueError(f"Invalid latitude '{raw.get(self.mapping.latitude_field)}'")

        lng = None
        if self.mapping.longitude_field and raw.get(self.mapping.longitude_field) is not None:
            try:
                lng = float(raw[self.mapping.longitude_field])
                if not (-180.0 <= lng <= 180.0):
                    raise ValueError()
            except Exception:
                raise ValueError(f"Invalid longitude '{raw.get(self.mapping.longitude_field)}'")

        ts = None
        if self.mapping.timestamp_field and raw.get(self.mapping.timestamp_field) is not None:
            val = raw[self.mapping.timestamp_field]
            if isinstance(val, datetime):
                ts = val
            elif isinstance(val, str) and val.strip():
                try:
                    ts = datetime.fromisoformat(val.replace("Z", "+00:00"))
                except Exception:
                    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y"):
                        try:
                            ts = datetime.strptime(val, fmt)
                            break
                        except ValueError:
                            pass

        source_val = raw.get(self.mapping.source_field) if self.mapping.source_field else None
        source = str(source_val) if source_val is not None else None

        metadata: dict[str, Any] = {}
        if self.mapping.metadata_fields:
            for k in self.mapping.metadata_fields:
                if k in raw:
                    metadata[k] = raw[k]
        else:
            mapped_keys = {
                self.mapping.complaint_id_field, self.mapping.text_field,
                self.mapping.category_field, self.mapping.department_field,
                self.mapping.priority_field, self.mapping.latitude_field,
                self.mapping.longitude_field, self.mapping.timestamp_field,
                self.mapping.source_field
            }
            metadata = {k: v for k, v in raw.items() if k not in mapped_keys and v is not None}

        return ComplaintRecord(
            complaint_id=str(complaint_id).strip(),
            text=str(text).strip(),
            category=str(category).strip() if category else None,
            department=str(department).strip() if department else None,
            priority=str(priority).strip().upper() if priority else None,
            latitude=lat,
            longitude=lng,
            timestamp=ts,
            source=source,
            metadata=metadata
        )

    def adapt_batch(self, raw_records: Iterable[dict[str, Any]]) -> tuple[list[ComplaintRecord], list[dict[str, Any]]]:
        valid_records: list[ComplaintRecord] = []
        errors: list[dict[str, Any]] = []

        for idx, item in enumerate(raw_records):
            try:
                record = self.adapt_record(item)
                valid_records.append(record)
            except Exception as e:
                errors.append({"index": idx, "raw": item, "error": str(e)})

        return valid_records, errors

    @abstractmethod
    def load(self, source: Any) -> tuple[list[ComplaintRecord], list[dict[str, Any]]]:
        pass
