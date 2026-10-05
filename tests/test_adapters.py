import io
from app.adapters.csv_adapter import CSVDatasetAdapter
from app.adapters.json_adapter import JSONDatasetAdapter
from app.adapters.dict_adapter import DictDatasetAdapter
from app.adapters.base import DatasetMappingConfig

def test_csv_adapter():
    csv_content = """complaint_ref,grievance_description,civic_category,prio,lat,lng
C-99,Huge water leak outside ward 3,WATER_LEAKAGE,HIGH,28.6,77.2
"""
    config = DatasetMappingConfig(
        complaint_id_field="complaint_ref",
        text_field="grievance_description",
        category_field="civic_category",
        priority_field="prio",
        latitude_field="lat",
        longitude_field="lng"
    )
    adapter = CSVDatasetAdapter(mapping_config=config)
    records = adapter.load_from_stream(io.StringIO(csv_content))
    assert len(records) == 1
    assert records[0].complaint_id == "C-99"
    assert "water leak" in records[0].text
    assert records[0].latitude == 28.6

def test_json_adapter():
    json_data = [
        {"id": "J1", "desc": "Garbage pile in sector 4", "cat": "GARBAGE_OVERFLOW"}
    ]
    config = DatasetMappingConfig(complaint_id_field="id", text_field="desc", category_field="cat")
    adapter = JSONDatasetAdapter(mapping_config=config)
    records = adapter.load_from_dict_list(json_data)
    assert len(records) == 1
    assert records[0].complaint_id == "J1"
