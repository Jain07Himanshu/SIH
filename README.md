# Seva Setu — AI-Powered Citizen Grievance & Duplicate Clustering Platform

[![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.14-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/Framework-FastAPI-009688.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/Tests-38%20Passed%20(100%25)-brightgreen.svg)]()

**Seva Setu** is an end-to-end, production-grade civic intelligence platform designed to eliminate the #1 bottleneck facing municipal bodies worldwide: **unstructured, duplicate complaint floods**.

By using a multi-signal AI engine, Seva Setu automatically canonicalizes Indian/regional slang (*"khadda"*, *"gadha"*, *"paani leakage"*, *"kachra"*), detects semantic duplicates, calculates Haversine GPS proximity buffers, merges related complaints into underlying municipal issues, and provides real-time tracking for citizens alongside an interactive spatial GIS map for authorities.

$$\text{MANY CITIZEN COMPLAINTS} \longrightarrow \text{FEWER UNDERLYING CIVIC ISSUES}$$

---

## 🏛️ System Architecture

```
                    ┌──────────────────────────────────────────────┐
                    │ 50 Citizen Complaints on Metro Pillar 12    │
                    └──────────────────────┬───────────────────────┘
                                           ▼
                 ┌──────────────────────────────────────────────────┐
                 │ CENTRAL DUPLICATE & CLUSTERING INTELLIGENCE      │
                 │ • NLP Tokenization & PII Redaction               │
                 │ • Hinglish Slang Canonicalizer (khadda->pothole) │
                 │ • TF-IDF Sublinear Cosine Similarity             │
                 │ • Haversine Geodesic Distance Matrix (< 250m)    │
                 └─────────────────────────┬────────────────────────┘
                                           ▼
                 ┌──────────────────────────────────────────────────┐
                 │ 1 Canonical Civic Issue Created:                 │
                 │ "Severe Road Pothole near Central Station"       │
                 │ • 1 Consolidated Authority Work Order Dispatch   │
                 │ • 50 Linked Citizen Trackers (Auto-Updated)      │
                 │ • ~32% Reduction in Municipal Workload Noise     │
                 └──────────────────────────────────────────────────┘
```

---

## 🚀 Quickstart Guide (Run on Any PC)

Follow these simple steps to run the complete project locally on **Windows**, **macOS**, or **Linux**.

### Prerequisites
Make sure you have installed:
1. **Python 3.10+** (Python 3.11, 3.12, or 3.14 recommended). Check with:
   ```bash
   python --version
   ```
2. **Git**:
   ```bash
   git --version
   ```

---

### Step 1: Clone the Repository
Open your terminal or command prompt and clone the repository:
```bash
git clone https://github.com/Jain07Himanshu/SIH.git
cd SIH
```

---

### Step 2: Set Up Virtual Environment (Recommended)

#### On Windows (PowerShell or Command Prompt):
```powershell
python -m venv venv
venv\Scripts\activate
```

#### On macOS / Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```

---

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

---

### Step 4: Seed Demo Database (50 Users & 51 Realistic Complaints)
Run the automated seed script to populate realistic citizen accounts, municipal officers, duplicate clusters across Mumbai coordinates, and historic audit timelines:
```bash
python seed_platform_demo.py
```
*(This will generate the SQLite database `similarity_engine.db` with 50+ users and complaints ready for instant demoing).*

---

### Step 5: Start the Server

#### Option A: One-Click Launcher (Windows)
Double-click `run_app.bat` or run:
```cmd
run_app.bat
```

#### Option B: Terminal Command (Windows, macOS, Linux)
```bash
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Server will start at: **`http://127.0.0.1:8000`**

---

## 🌐 Web Application Portals

Once the server is running, open your web browser to access:

| Portal | URL | Description |
|---|---|---|
| **Home Landing Page** | [http://localhost:8000](http://localhost:8000) | Landing page with role selection & phone visual shortcuts |
| **Citizen Complaint Filing** | [http://localhost:8000/citizen?mode=submit](http://localhost:8000/citizen?mode=submit) | File a new civic issue with AI category detection |
| **Real-Time 4-Stage Tracker** | [http://localhost:8000/citizen?mode=track](http://localhost:8000/citizen?mode=track) | Live audit stepper (`Submitted` → `Assigned` → `In Progress` → `Resolved`) |
| **Authority Analytics Console** | [http://localhost:8000/authority](http://localhost:8000/authority) | Department workloads, category breakdowns & noise reduction KPIs |
| **Authority Spatial GIS Map** | [http://localhost:8000/authority/map](http://localhost:8000/authority/map) | Interactive Leaflet.js map with circle pins & slide-out dispatch drawer |
| **Interactive API Documentation**| [http://localhost:8000/docs](http://localhost:8000/docs) | Complete Swagger UI with live testing for all REST endpoints |

---

## 🔑 Demo Logins & Test Data

The seed script creates pre-configured accounts and complaints for immediate testing:

### 1. Municipal Authority Login
- **URL**: [http://localhost:8000/login?role=authority](http://localhost:8000/login?role=authority)
- **Email**: `authority@gov.in`
- **Password**: `password123`
*(Also available: `sanitation@gov.in`, `water@gov.in`, `electricity@gov.in` with password `password123`)*

### 2. Citizen Login
- **URL**: [http://localhost:8000/login?role=citizen](http://localhost:8000/login?role=citizen)
- **Email**: `citizen@example.com` or `anita.roy@gmail.com`
- **Password**: `password123`

### 3. Sample Complaint IDs for Tracking Stepper
Enter any of these IDs in the **[Tracking Portal](http://localhost:8000/citizen?mode=track)** to inspect live progress:
- `SS-100001` (Road Pothole — In Progress)
- `SS-100015` (Water Leakage — Assigned)
- `SS-100025` (Garbage Overflow — Resolved)

---

## 🧪 Running Automated Tests

The repository includes a comprehensive test suite (38 test cases) covering the AI similarity engine, text cleaner, slang normalizer, authority analytics, GIS map endpoints, and end-to-end user workflows:

```bash
python -m pytest -v
```

**Expected output:**
```text
====================== 38 passed in 1.80s =======================
```

---

## 🛠️ Technology Stack

- **Backend Framework**: [FastAPI](https://fastapi.tiangolo.com/) (Python 3.10+) with Uvicorn ASGI
- **Database & ORM**: SQLite3 (with Write-Ahead Logging `WAL`) + [SQLAlchemy 2.0](https://www.sqlalchemy.org/)
- **AI & NLP Intelligence**:
  - Semantic Cosine Similarity (Scikit-Learn TF-IDF vectorizer with sublinear scaling)
  - Spherical Geodesic Haversine spatial buffer (< 250m radius)
  - Slang & Regional Keyword Canonicalization (`configs/synonyms.yaml`)
  - Deterministic PII Masking (`[PHONE]`, `[EMAIL]`, Unicode NFKD normalization)
- **Frontend & Mapping**:
  - Tailwind CSS + Vanilla JS (Zero external build toolchains needed)
  - [Leaflet.js 1.9.4](https://leafletjs.com/) with OpenStreetMap tiles for real-time GIS mapping
  - FontAwesome 6 + Sora / Inter typography
- **Authentication**: Stateless JSON Web Tokens (PyJWT) + Bcrypt password hashing

---

## 📂 Project Structure

```text
SIH/
├── app/
│   ├── api/                   # REST API routes (complaints, authority, auth, analytics)
│   ├── auth/                  # JWT security and dependency injection
│   ├── clustering/            # Issue clustering and duplicate grouping engines
│   ├── db/                    # SQLAlchemy models and session management
│   ├── extraction/            # Keywords, civic entities, and slang canonicalizer
│   ├── issue/                 # Issue builder, centroid calculator, and resolver
│   ├── preprocessing/         # Normalizer, PII cleaner, and language detection
│   ├── services/              # Business logic (complaints, analytics, authority)
│   ├── similarity/            # Semantic, spatial, and temporal similarity scorers
│   └── main.py                # FastAPI application entrypoint
├── configs/
│   ├── synonyms.yaml          # Indian civic slang & synonym mappings
│   └── taxonomy.yaml          # Civic categories & department hierarchy
├── static/                    # Frontend UI HTML/CSS/JS screens
│   ├── Home.html              # Landing page
│   ├── Citizen Lobby.html     # Complaint filing & live 4-stage tracking stepper
│   ├── Autority Lobby.html    # Authority console & KPI analytics
│   ├── Autority Map.html      # Interactive Leaflet GIS spatial map
│   └── login.html             # Role-based authentication
├── tests/                     # 38 automated test cases (100% pass)
├── requirements.txt           # Project Python dependencies
├── seed_platform_demo.py      # Demo dataset seeder (50 users + 51 complaints)
├── run_app.bat                # 1-click Windows launcher
└── README.md                  # Documentation & Quickstart
```

---

## ❓ Troubleshooting & FAQs

### 1. `Address already in use` (Port 8000 busy)
If port 8000 is occupied by another process, run on another port (e.g. 8080):
```bash
python -m uvicorn app.main:app --host 127.0.0.1 --port 8080 --reload
```

### 2. Missing C++ Build Tools or PyJWT / Bcrypt issues
Ensure your `pip` is up to date:
```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Reset or Reseed Database
To wipe and recreate the database with clean demo data:
```bash
python seed_platform_demo.py
```

---

## 📄 License
This project is open-source and licensed under the [MIT License](LICENSE).
