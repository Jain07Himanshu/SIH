import pytest
from app.schemas.complaint import ComplaintRecord, ComplaintInput
from app.services.pipeline import GrievanceIntelligencePipeline
from app.classification.taxonomy import TaxonomyManager
from app.extraction.synonyms import SynonymManager
from app.embeddings.encoder import EmbeddingEncoder

@pytest.fixture
def taxonomy_manager():
    return TaxonomyManager()

@pytest.fixture
def synonym_manager():
    return SynonymManager()

@pytest.fixture
def embedding_encoder():
    return EmbeddingEncoder()

@pytest.fixture
def pipeline(taxonomy_manager, synonym_manager, embedding_encoder):
    return GrievanceIntelligencePipeline(
        taxonomy_manager=taxonomy_manager,
        synonym_manager=synonym_manager,
        embedding_encoder=embedding_encoder
    )

@pytest.fixture
def sample_complaints():
    return [
        ComplaintRecord(complaint_id="C01", text="Huge pothole near railway station flyover causing major accidents", category="ROAD_POTHOLE", priority="HIGH", latitude=28.6139, longitude=77.2090),
        ComplaintRecord(complaint_id="C02", text="Dangerous deep pothole outside railway station flyover, two wheelers skidding", category="ROAD_POTHOLE", priority="HIGH", latitude=28.6141, longitude=77.2092),
        ComplaintRecord(complaint_id="C03", text="Vehicle damaged due to big pothole near railway station", category="ROAD_POTHOLE", priority="HIGH", latitude=28.6140, longitude=77.2088),
        ComplaintRecord(complaint_id="C04", text="Garbage dump overflowing near sector 15 market, bad smell", category="GARBAGE_OVERFLOW", priority="MEDIUM", latitude=28.6250, longitude=77.2180),
        ComplaintRecord(complaint_id="C05", text="Uncollected trash and waste pile at sector 15 market gate", category="GARBAGE_OVERFLOW", priority="MEDIUM", latitude=28.6252, longitude=77.2182),
        ComplaintRecord(complaint_id="C06", text="Drinking water pipeline burst in block B, road flooded", category="WATER_LEAKAGE", priority="HIGH", latitude=28.6310, longitude=77.2250)
    ]
