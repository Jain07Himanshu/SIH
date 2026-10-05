import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes_auth import router as auth_router
from app.api.routes_complaints import router as complaints_router
from app.api.routes_authority import router as authority_router
from app.api.routes_analysis import router as analysis_router
from app.api.routes_similarity import router as similarity_router
from app.api.routes_clusters import router as clusters_router
from app.api.routes_issues import router as issues_router
from app.api.routes_categories import router as categories_router
from app.api.routes_analytics import router as analytics_router
from app.api.routes_health import router as health_router
from app.db.session import init_db

app = FastAPI(
    title="Seva Setu — AI Civic Grievance & Duplicate Engine Platform",
    version="2.0.0",
    description="Unified Citizen Grievance Management, AI Similarity Engine, GIS Mapping & Authority Workflow Platform"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database schema on startup
@app.on_event("startup")
def on_startup():
    init_db()

# Include REST API routers
app.include_router(auth_router)
app.include_router(complaints_router)
app.include_router(authority_router)
app.include_router(analysis_router)
app.include_router(similarity_router)
app.include_router(clusters_router)
app.include_router(issues_router)
app.include_router(categories_router)
app.include_router(analytics_router)
app.include_router(health_router)

# Mount static folder
static_dir = os.path.join(os.path.dirname(__file__), "..", "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Clean UI Page Routes
@app.get("/")
def serve_home():
    return FileResponse(os.path.join(static_dir, "Home.html"))

@app.get("/register/citizen")
def serve_citizen_reg():
    return FileResponse(os.path.join(static_dir, "Citizen registertion.html"))

@app.get("/register/authority")
def serve_authority_reg():
    return FileResponse(os.path.join(static_dir, "authority_register.html"))

@app.get("/login")
def serve_login():
    return FileResponse(os.path.join(static_dir, "login.html"))

@app.get("/citizen")
def serve_citizen_lobby():
    return FileResponse(os.path.join(static_dir, "Citizen Lobby.html"))

@app.get("/authority")
def serve_authority_lobby():
    return FileResponse(os.path.join(static_dir, "Autority Lobby.html"))

@app.get("/authority/map")
def serve_authority_map():
    return FileResponse(os.path.join(static_dir, "Autority Map.html"))
