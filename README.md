# Central AI Intelligence Engine for Citizen Grievance Platforms

An AI-powered **Duplicate Detection, Multi-Signal Similarity Scoring, Keyword & Entity Extraction, Category Classification, and Canonical Civic Issue Clustering Engine** designed as the central intelligence backend for municipal and citizen grievance platforms.

---

## 🏛️ Core Mission
Citizen grievance portals receive **thousands of noisy, unstructured complaints**. Many report the exact same real-world incident (e.g. 50 citizens reporting a single pothole or broken water pipeline). 

This engine converts:
$$\text{MANY CITIZEN COMPLAINTS} \longrightarrow \text{FEWER UNDERLYING CANONICAL CIVIC ISSUES}$$

```
                ┌──────────────────────────────────────────────┐
                │ 50 Citizen Complaints on Metro Pillar 12    │
                └──────────────────────┬───────────────────────┘
                                       ▼
             ┌──────────────────────────────────────────────────┐
             │ CENTRAL DUPLICATE & CLUSTERING INTELLIGENCE      │
             └─────────────────────────┬────────────────────────┘
                                       ▼
             ┌──────────────────────────────────────────────────┐
             │ 1 Canonical Civic Issue:                         │
             │ "Deep Dangerous Pothole near Central Station"    │
             │ • 1 Consolidated Authority Work Order            │
             │ • 50 Citizen Ticket Subscribers                  │
             │ • High Priority | GIS Radius: 15m                │
             └──────────────────────────────────────────────────┘
```

---

## 🚀 Key Features

1. **Deterministic & Semantic Preprocessing**:
   - Multi-representation preservation (`original_text`, `clean_text`, `semantic_text`, `keyword_text`).
   - PII masking (`[PHONE]`, `[EMAIL]`, `[AADHAAR]`, `[VEHICLE]`), Unicode normalization, boilerplate cleanup.
   - Multilingual support (English, Hindi, mixed transliterated Hinglish).

2. **Multi-Signal Keyword & Entity Extraction**:
   - Extraction of civic entities, location prepositions (`near metro station`), impact expressions (`causing bike skidding`), and temporal markers (`since 3 days`).
   - Civic domain synonym canonicalization dictionary.

3. **6-Signal Composite Similarity Scorer**:
   - **Semantic Similarity** (Dense embedding cosine similarity)
   - **Lexical Similarity** (Token Jaccard & character n-gram overlap)
   - **Keyword / Entity Overlap** (Location & impact overlap)
   - **Category Match** (Exact match & hierarchy domain alignment)
   - **Geographic Proximity** (Haversine distance with Gaussian / Exponential decay)
   - **Temporal Proximity** (Exponential recency decay)
   - *Dynamic re-normalization* when geo or temporal coordinates are absent.

4. **3-Tier Decision & Transparent Explainability**:
   - `DUPLICATE` (Score $\ge 0.82$)
   - `POSSIBLY_SIMILAR` ($0.62 \le \text{Score} < 0.82$)
   - `NEW_ISSUE` (Score $< 0.62$)
   - Human-readable `MatchEvidence` explaining *why* records matched.
   - Borderline review flagging for human triage.

5. **HDBSCAN / DBSCAN Canonical Issue Clustering**:
   - Pairwise distance matrix computation.
   - Unforced noise handling (`is_noise=True` keeps distinct single complaints separate).
   - Evidence-based issue title generator, representative complaint selection, GIS centroid & radius calculation.

6. **Issue Lifecycle Management**:
   - Real-time incremental complaint attachment.
   - `merge_issues` and `split_issue` operations with audit logging.

7. **Authority Analytics & GIS Hotspots**:
   - Executive overview metrics, duplicate reduction rate %, department breakdown, trend timeseries, and spatial hotspot cluster detection.

8. **Dataset-Agnostic Adapter Layer**:
   - Pluggable CSV, JSON, NDJSON, and Python dictionary adapters with configurable field mappings.

---

## 📦 Quickstart & Installation

### 1. Local Environment Setup
```bash
git clone <repo-url>
cd similarity_engine
pip install -r requirements.txt
```

### 2. Run Database Migrations
```bash
python scripts/init_db.py
```

### 3. Run FastAPI Application
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
Interactive OpenAPI documentation will be live at `http://localhost:8000/docs`.

### 4. Run Docker Compose (with PostgreSQL + pgvector)
```bash
docker-compose up -d --build
```

---

## 🧪 Running Tests & Benchmark Evaluation

### Run Full Pytest Suite:
```bash
python -m pytest tests/ -v
```

### Run Threshold Grid Search:
```bash
python scripts/tune_thresholds.py
```

### Run Benchmark Evaluation:
```bash
python scripts/evaluate.py
```

### Run Live End-to-End Demo:
```bash
python scripts/demo_batch_pipeline.py
```

---

## 📡 REST API Overview

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/analyze` | Real-time single complaint ingestion & issue assignment |
| `POST` | `/api/v1/analyze/batch` | Batch complaint ingestion & HDBSCAN issue clustering |
| `POST` | `/api/v1/similarity/compare` | Compare two complaints across 6 similarity signals |
| `GET` | `/api/v1/issues` | List canonical issues with department & priority filters |
| `GET` | `/api/v1/issues/{id}` | Retrieve canonical issue details & member complaints |
| `POST` | `/api/v1/issues/merge` | Merge two existing issues |
| `POST` | `/api/v1/issues/split` | Split complaints out into a new canonical issue |
| `GET` | `/api/v1/analytics/overview` | High-level platform statistics & duplicate reduction % |
| `GET` | `/api/v1/analytics/hotspots` | Spatial GIS clusters & hotspot severity |
| `GET` | `/api/v1/categories` | Complete civic domain taxonomy & prototypes |
| `GET` | `/health` | Health check & model status |

---

## 📐 Architecture & Documentation
For deep technical documentation:
- [Architecture Guide](docs/architecture.md)
- [Algorithm & Math](docs/algorithm.md)
- [API Reference](docs/api.md)
- [Data Contract](docs/data_contract.md)
- [Evaluation & Benchmark](docs/evaluation.md)
