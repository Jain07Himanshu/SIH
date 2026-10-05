from typing import Any
from app.adapters.base import BaseDatasetAdapter, DatasetMappingConfig
from app.schemas.complaint import ComplaintRecord


class DictDatasetAdapter(BaseDatasetAdapter):
    def load(self, source: Any) -> tuple[list[ComplaintRecord], list[dict[str, Any]]]:
        if not isinstance(source, list):
            raise ValueError("DictDatasetAdapter expects a list of dicts.")
        return self.adapt_batch(source)

    def load_from_dict_list(self, data: list[dict[str, Any]]) -> list[ComplaintRecord]:
        records, _ = self.load(data)
        return records
