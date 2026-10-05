# System Architecture Guide

The Grievance Intelligence Engine is structured as a modular, high-throughput pipeline operating across 7 decoupled layers.

```
                           Raw Complaint Ingestion
                                     │
                                     ▼
                ┌──────────────────────────────────────────┐
                │ 1. DATASET ADAPTER & VALIDATION LAYER    │
                │  • CSV / JSON / Stream / Dict Adapters   │
                │  • Configurable Field Mapping & Casts    │
                └────────────────────┬─────────────────────┘
                                     │
                                     ▼
                ┌──────────────────────────────────────────┐
                │ 2. PREPROCESSING & NLP NORMALIZATION     │
                │  • Unicode & Whitespace Normalizer       │
                │  • PII Masking (Phone, Email, Identity)  │
                │  • Multi-representation Builder          │
                └────────────────────┬─────────────────────┘
                                     │
                                     ▼
                ┌──────────────────────────────────────────┐
                │ 3. EXTRACTION & CLASSIFICATION           │
                │  • Location & Impact Phrase Extractor    │
                │  • Civic Domain Synonym Canonicalizer    │
                │  • Zero-Shot / Prototype Classifier      │
                └────────────────────┬─────────────────────┘
                                     │
                                     ▼
                ┌──────────────────────────────────────────┐
                │ 4. EMBEDDINGS & VECTOR STORE             │
                │  • SentenceTransformer / Fallback Hash   │
                │  • LRU In-Memory Cache                   │
                │  • k-NN Cosine Similarity Index          │
                └────────────────────┬─────────────────────┘
                                     │
                                     ▼
                ┌──────────────────────────────────────────┐
                │ 5. MULTI-SIGNAL SIMILARITY ENGINE        │
                │  • 6 Similarity Signals Weighted Fusion  │
                │  • Dynamic Missing Field Renormalization │
                │  • 3-Tier Match Decision & Evidence      │
                └────────────────────┬─────────────────────┘
                                     │
                                     ▼
                ┌──────────────────────────────────────────┐
                │ 6. CLUSTERING & CANONICAL ISSUE BUILDER  │
                │  • HDBSCAN / DBSCAN Distance Clustering  │
                │  • Canonical Title Generator             │
                │  • Representative Complaint Selection    │
                │  • GIS Centroid & Radius Calculation     │
                └────────────────────┬─────────────────────┘
                                     │
                                     ▼
                ┌──────────────────────────────────────────┐
                │ 7. PERSISTENCE & REST API SERVING        │
                │  • SQLAlchemy SQLite / PostgreSQL Models │
                │  • FastAPI High-Speed Endpoints          │
                │  • Authority Analytics & GIS Hotspots    │
                └──────────────────────────────────────────┘
```
