from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, Float, Integer, String, Text

from app.database import Base


class SavedReport(Base):
    __tablename__ = "saved_reports"

    id = Column(Integer, primary_key=True, index=True)
    candidate_label = Column(String(200), nullable=False, default="Anonymous Candidate")
    target_role_title = Column(String(200), nullable=False, default="Target Role")
    ats_score = Column(Float, nullable=False)
    semantic_score = Column(Float, nullable=False)
    keyword_score = Column(Float, nullable=False)
    structure_score = Column(Float, nullable=False)
    matched_skills_count = Column(Integer, nullable=False, default=0)
    missing_skills_count = Column(Integer, nullable=False, default=0)
    top_matched_job = Column(String(200), nullable=False, default="")
    payload_json = Column(Text, nullable=False)
    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
