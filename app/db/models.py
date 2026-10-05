from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, JSON, Boolean, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class UserModel(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(100), unique=True, index=True, nullable=False)
    name = Column(String(200), nullable=False)
    email = Column(String(200), unique=True, index=True, nullable=False)
    password_hash = Column(String(300), nullable=False)
    role = Column(String(50), nullable=False)  # "CITIZEN" | "AUTHORITY"
    designation = Column(String(200), nullable=True)
    department = Column(String(200), nullable=True)
    employee_id = Column(String(100), nullable=True)
    phone = Column(String(50), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ComplaintModel(Base):
    __tablename__ = "complaints"

    id = Column(Integer, primary_key=True, index=True)
    complaint_id = Column(String(100), unique=True, index=True, nullable=False)
    citizen_id = Column(String(100), index=True, nullable=True) # links to user_id or email
    text = Column(Text, nullable=False)
    clean_text = Column(Text, nullable=True)
    category_id = Column(String(100), index=True, nullable=True)
    department_id = Column(String(100), index=True, nullable=True)
    locality = Column(String(300), nullable=True)
    ward = Column(String(100), nullable=True)
    landmark = Column(String(300), nullable=True)
    priority = Column(String(20), default="MEDIUM")  # "LOW", "MEDIUM", "HIGH", "URGENT"
    status = Column(String(50), default="SUBMITTED", index=True)  # "SUBMITTED", "ASSIGNED", "IN_PROGRESS", "RESOLVED", "REJECTED"
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    image_url = Column(String(500), nullable=True)
    is_anonymous = Column(Boolean, default=False)
    contact_name = Column(String(200), nullable=True)
    contact_phone = Column(String(50), nullable=True)
    source = Column(String(100), default="WEB")
    raw_metadata = Column(JSON, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ComplaintStatusHistoryModel(Base):
    __tablename__ = "complaint_status_history"

    id = Column(Integer, primary_key=True, index=True)
    complaint_id = Column(String(100), ForeignKey("complaints.complaint_id"), index=True, nullable=False)
    old_status = Column(String(50), nullable=False)
    new_status = Column(String(50), nullable=False)
    changed_by = Column(String(200), nullable=True)
    comment = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

class ComplaintEmbeddingModel(Base):
    __tablename__ = "complaint_embeddings"

    id = Column(Integer, primary_key=True, index=True)
    complaint_id = Column(String(100), ForeignKey("complaints.complaint_id"), unique=True, index=True, nullable=False)
    embedding_json = Column(Text, nullable=False)
    dimension = Column(Integer, default=384)
    model_name = Column(String(200), default="deterministic-civic-hash-384")
    created_at = Column(DateTime, default=datetime.utcnow)

class ComplaintKeywordModel(Base):
    __tablename__ = "complaint_keywords"

    id = Column(Integer, primary_key=True, index=True)
    complaint_id = Column(String(100), ForeignKey("complaints.complaint_id"), index=True, nullable=False)
    term = Column(String(200), index=True, nullable=False)
    score = Column(Float, default=1.0)
    term_type = Column(String(50), default="issue")

class IssueModel(Base):
    __tablename__ = "issues"

    id = Column(Integer, primary_key=True, index=True)
    issue_id = Column(String(100), unique=True, index=True, nullable=False)
    title = Column(String(500), nullable=False)
    category_id = Column(String(100), index=True, nullable=True)
    department_id = Column(String(100), index=True, nullable=True)
    representative_complaint_id = Column(String(100), nullable=False)
    complaint_count = Column(Integer, default=1)
    duplicate_count = Column(Integer, default=0)
    similarity_score = Column(Float, default=1.0)
    dominant_priority = Column(String(20), default="MEDIUM")
    status = Column(String(50), default="OPEN", index=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    radius_meters = Column(Float, default=0.0)
    keywords_json = Column(JSON, nullable=True)
    needs_review = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class IssueMemberModel(Base):
    __tablename__ = "issue_members"

    id = Column(Integer, primary_key=True, index=True)
    issue_id = Column(String(100), ForeignKey("issues.issue_id"), index=True, nullable=False)
    complaint_id = Column(String(100), ForeignKey("complaints.complaint_id"), index=True, nullable=False)
    similarity_score = Column(Float, default=1.0)
    is_representative = Column(Boolean, default=False)
    joined_at = Column(DateTime, default=datetime.utcnow)

class DuplicateMatchModel(Base):
    __tablename__ = "duplicate_matches"

    id = Column(Integer, primary_key=True, index=True)
    complaint_id = Column(String(100), ForeignKey("complaints.complaint_id"), index=True, nullable=False)
    matched_complaint_id = Column(String(100), index=True, nullable=True)
    matched_issue_id = Column(String(100), index=True, nullable=True)
    semantic_score = Column(Float, default=0.0)
    final_similarity_score = Column(Float, default=0.0)
    match_type = Column(String(50), nullable=False)  # "DUPLICATE", "POSSIBLY_SIMILAR", "NEW_ISSUE"
    confidence = Column(Float, default=0.0)
    explanation_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class SimilarityMatchModel(Base):
    __tablename__ = "similarity_matches"

    id = Column(Integer, primary_key=True, index=True)
    complaint_id_a = Column(String(100), index=True, nullable=False)
    complaint_id_b = Column(String(100), index=True, nullable=False)
    similarity_score = Column(Float, nullable=False)
    match_type = Column(String(50), nullable=False)
    evidence_json = Column(JSON, nullable=True)
    matched_at = Column(DateTime, default=datetime.utcnow)

class ProcessingJobModel(Base):
    __tablename__ = "processing_jobs"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(String(100), unique=True, index=True, nullable=False)
    total_records = Column(Integer, default=0)
    successful_records = Column(Integer, default=0)
    failed_records = Column(Integer, default=0)
    duration_seconds = Column(Float, default=0.0)
    status = Column(String(50), default="COMPLETED")
    errors_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
