import json
from typing import Any
from app.adapters.base import BaseDatasetAdapter, DatasetMappingConfig
from app.schemas.complaint import ComplaintRecord


class JSONDatasetAdapter(BaseDatasetAdapter):
    def load(self, source: Any) -> tuple[list[ComplaintRecord], list[dict[str, Any]]]:
        if isinstance(source, str):
            raw_list = json.loads(source)
        elif isinstance(source, list):
            raw_list = source
        else:
            raise ValueError(f"Unsupported JSON source type: {type(source)}")

        if not isinstance(raw_list, list):
            raw_list = [raw_list]

        return self.adapt_batch(raw_list)

    def load_from_dict_list(self, data: list[dict[str, Any]]) -> list[ComplaintRecord]:
        records, _ = self.load(data)
        return records

    def load_ndjson(self, ndjson_text: str) -> list[ComplaintRecord]:
        lines = [line.strip() for line in ndjson_text.strip().splitlines() if line.strip()]
        raw_list = [json.loads(line) for line in lines]
        records, _ = self.adapt_batch(raw_list)
        return records
