import os
from typing import Any
import yaml
from pydantic import BaseModel, Field

class AppLoggingConfig(BaseModel):
    level: str = "INFO"
    format: str = "json"

class EmbeddingSettings(BaseModel):
    provider: str = "auto"
    model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
    dimension: int = 384
    normalize_embeddings: bool = True
    batch_size: int = 64

class SimilarityWeightsConfig(BaseModel):
    semantic: float = 0.45
    lexical: float = 0.15
    keyword: float = 0.15
    category: float = 0.10
    geographic: float = 0.10
    temporal: float = 0.05

class GeographicSettings(BaseModel):
    max_distance_meters: float = 5000.0
    sigma_meters: float = 800.0
    decay_function: str = "gaussian"

class TemporalSettings(BaseModel):
    max_days: float = 90.0
    half_life_days: float = 14.0
    decay_function: str = "exponential"

class SimilaritySettings(BaseModel):
    weights: SimilarityWeightsConfig = Field(default_factory=SimilarityWeightsConfig)
    geographic: GeographicSettings = Field(default_factory=GeographicSettings)
    temporal: TemporalSettings = Field(default_factory=TemporalSettings)

class ThresholdsConfig(BaseModel):
    duplicate: float = 0.80
    possible_match: float = 0.55
    needs_review_margin: float = 0.04

class ClusteringSettings(BaseModel):
    algorithm: str = "hdbscan"
    min_cluster_size: int = 2
    min_samples: int = 1
    cluster_selection_epsilon: float = 0.58

class DatabaseSettings(BaseModel):
    url: str = "sqlite:///./similarity_engine.db"
    echo: bool = False

class ApiSettings(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = False

class AppConfig(BaseModel):
    app_name: str = "Grievance Intelligence Engine"
    version: str = "1.0.0"
    environment: str = "development"
    logging: AppLoggingConfig = Field(default_factory=AppLoggingConfig)
    embedding: EmbeddingSettings = Field(default_factory=EmbeddingSettings)
    similarity: SimilaritySettings = Field(default_factory=SimilaritySettings)
    thresholds: ThresholdsConfig = Field(default_factory=ThresholdsConfig)
    clustering: ClusteringSettings = Field(default_factory=ClusteringSettings)
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    api: ApiSettings = Field(default_factory=ApiSettings)

_config_instance: AppConfig | None = None

def load_config(config_path: str = "configs/default_config.yaml") -> AppConfig:
    global _config_instance
    data: dict[str, Any] = {}
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}

    db_env = os.environ.get("DATABASE_URL")
    if db_env:
        if "database" not in data:
            data["database"] = {}
        data["database"]["url"] = db_env

    _config_instance = AppConfig(**data)
    return _config_instance

def get_config() -> AppConfig:
    global _config_instance
    if _config_instance is None:
        _config_instance = load_config()
    return _config_instance
