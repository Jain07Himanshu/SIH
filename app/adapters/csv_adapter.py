import csv
import io
import os
from typing import Any
from app.adapters.base import BaseDatasetAdapter, DatasetMappingConfig
from app.schemas.complaint import ComplaintRecord


class CSVDatasetAdapter(BaseDatasetAdapter):
    def load(self, source: Any) -> tuple[list[ComplaintRecord], list[dict[str, Any]]]:
        if isinstance(source, str) and os.path.exists(source):
            with open(source, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                records = list(reader)
        elif isinstance(source, io.StringIO):
            reader = csv.DictReader(source)
            records = list(reader)
        elif isinstance(source, str):
            stream = io.StringIO(source)
            reader = csv.DictReader(stream)
            records = list(reader)
        else:
            try:
                import pandas as pd
                if isinstance(source, pd.DataFrame):
                    records = source.to_dict(orient="records")
                else:
                    raise ValueError(f"Unsupported CSV source type: {type(source)}")
            except ImportError:
                raise ValueError(f"Unsupported CSV source type: {type(source)}")

        return self.adapt_batch(records)

    def load_from_stream(self, stream: io.StringIO) -> list[ComplaintRecord]:
        records, _ = self.load(stream)
        return records
