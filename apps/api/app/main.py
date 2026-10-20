"""FastAPI Application for Day 08 — Smart Resume Analyzer and Job Matcher (RoleFit AI)."""

import json
from typing import Optional
from fastapi import Depends, FastAPI, File, Form, HTTPException, Response, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.config import settings
from app.database import Base, engine, get_db
from app.models import SavedReport
from app.schemas import (
    AnalyzeRequest,
    AnalyzeResponse,
    RewriteRequest,
)
from app.services.document_parser import (
    generate_pdf_bytes,
    parse_uploaded_document,
)
from app.services.nlp_extractor import (
    compute_skill_gap_and_learning_path,
    detect_sections,
    extract_bullets_and_audit,
    extract_education,
    extract_experience_summary,
    extract_skills,
    scrub_pii_and_audit_bias,
)
from app.services.rewrite_coach import rewrite_bullets_with_coach
from app.services.sample_data import JOB_POSTINGS_DATASET, SAMPLE_PERSONAS
from app.services.taxonomy import SKILL_TAXONOMY
from app.services.vector_matcher import (
    compute_ats_score_breakdown,
    run_matching_evaluation_harness,
    vector_index,
)

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "Day 08 of 30 Projects in 30 Days: Upload a resume (PDF/DOCX/Text) and a Job Description to compute "
        "an explainable Hybrid ATS Score, Semantic Vector Similarity, Skill Gap Learning Path, Top-N LinkedIn "
        "Job Role Matches, De-Biased Screening Audit, and Guardrailed LLM Bullet-Point Rewrites."
    ),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _run_full_analysis(
    req: AnalyzeRequest, db: Session
) -> AnalyzeResponse:
    # 1. Scrub PII & Run Bias/Fairness Audit before embedding
    debiased_resume, bias_audit = scrub_pii_and_audit_bias(
        req.resume_text, req.job_description
    )

    # 2. Extract Skills from Resume and Target JD via NLP Skill Taxonomy
    resume_skills = extract_skills(req.resume_text, mark_importance_from_jd=False)
    jd_skills = extract_skills(req.job_description, mark_importance_from_jd=True)

    # 3. Compute Matched Skills, Missing Skills (Set Difference), Bonus Skills & Learning Path
    matched_jd, missing_jd, bonus_res, learning_path = (
        compute_skill_gap_and_learning_path(resume_skills, jd_skills)
    )

    # 4. Extract Sections, Education, Bullet Strength Audits & Experience Summary
    sections = detect_sections(req.resume_text)
    education = extract_education(req.resume_text)
    bullet_audits = extract_bullets_and_audit(req.resume_text)
    experience = extract_experience_summary(req.resume_text, bullet_audits)

    # 5. Compute Hybrid ATS Score Breakdown (Semantic Cosine + Taxonomy Coverage + Impact Readiness)
    score_breakdown = compute_ats_score_breakdown(
        debiased_resume_text=debiased_resume,
        jd_text=req.job_description,
        matched_jd_skills=matched_jd,
        missing_jd_skills=missing_jd,
        sections_detected=sections,
        bullet_audits=bullet_audits,
    )

    # 6. Rank Top-N Best-Fit Job Roles from the Vector Index
    top_jobs = vector_index.rank_jobs_for_resume(
        debiased_resume_text=debiased_resume,
        resume_skills=resume_skills,
        top_n=req.top_n_jobs,
    )

    # 7. Select weakest bullets (or top 4 bullets) and generate XYZ / STAR rewrites
    sorted_for_coaching = sorted(bullet_audits, key=lambda b: b.strength_score)
    bullets_to_rewrite = [b.original for b in sorted_for_coaching[:4]]
    if not bullets_to_rewrite:
        bullets_to_rewrite = [
            "Worked on backend APIs and helped with database queries for the application."
        ]

    rewrites, engine_label = rewrite_bullets_with_coach(
        bullets=bullets_to_rewrite,
        target_jd=req.job_description,
        missing_skills=[m.name for m in missing_jd],
        api_key_override=req.gemini_api_key,
    )

    response_obj = AnalyzeResponse(
        report_id=None,
        candidate_label=req.candidate_label or "Anonymous Candidate",
        target_role_title=req.target_role_title or "Target Job Description",
        score_breakdown=score_breakdown,
        extracted_skills=resume_skills,
        matched_jd_skills=matched_jd,
        missing_jd_skills=missing_jd,
        bonus_resume_skills=bonus_res,
        learning_path=learning_path,
        education=education,
        experience=experience,
        sections_detected=sections,
        bullet_audits=bullet_audits,
        rewrites=rewrites,
        rewrite_engine=engine_label,
        top_job_matches=top_jobs,
        bias_audit=bias_audit,
    )

    if req.save_report:
        db_row = SavedReport(
            candidate_label=response_obj.candidate_label,
            target_role_title=response_obj.target_role_title,
            ats_score=score_breakdown.overall_ats_score,
            semantic_score=score_breakdown.semantic_similarity_score,
            keyword_score=score_breakdown.keyword_coverage_score,
            structure_score=score_breakdown.impact_structure_score,
            matched_skills_count=len(matched_jd),
            missing_skills_count=len(missing_jd),
            top_matched_job=top_jobs[0].title if top_jobs else "",
            payload_json=response_obj.model_dump_json(),
        )
        db.add(db_row)
        db.commit()
        db.refresh(db_row)
        response_obj.report_id = db_row.id

    return response_obj


@app.get("/api/health")
def health_check():
    return {
        "status": "ok",
        "service": settings.app_name,
        "version": settings.app_version,
        "jobs_indexed": len(JOB_POSTINGS_DATASET),
        "skills_in_taxonomy": len(SKILL_TAXONOMY),
        "gemini_configured": bool(settings.gemini_api_key),
        "gemini_model": settings.gemini_model,
    }


@app.get("/api/samples")
def list_samples():
    """Return sample candidate personas, target JDs, and indexed job postings."""
    return {
        "personas": SAMPLE_PERSONAS,
        "jobs_count": len(JOB_POSTINGS_DATASET),
        "skills_count": len(SKILL_TAXONOMY),
    }


@app.get("/api/samples/{persona_id}/pdf")
def download_sample_persona_pdf(persona_id: str):
    """Generate and download a real PDF resume for any sample persona to test PDF upload."""
    persona = next((p for p in SAMPLE_PERSONAS if p["id"] == persona_id), None)
    if not persona:
        raise HTTPException(status_code=404, detail=f"Persona '{persona_id}' not found.")
    pdf_bytes = generate_pdf_bytes(persona["label"], persona["resume_text"])
    filename = f"{persona_id}-resume.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@app.get("/api/jobs")
def list_indexed_jobs(domain: Optional[str] = None):
    """Return all pre-indexed LinkedIn-style job postings in the vector store."""
    jobs = JOB_POSTINGS_DATASET
    if domain:
        jobs = [j for j in jobs if domain.lower() in j["domain"].lower()]
    return {"jobs": jobs, "total": len(jobs)}


@app.post("/api/upload-resume")
async def upload_and_parse_resume(
    file: UploadFile = File(...),
    job_description: Optional[str] = Form(default=None),
    candidate_label: Optional[str] = Form(default=None),
    target_role_title: Optional[str] = Form(default=None),
    gemini_api_key: Optional[str] = Form(default=None),
    db: Session = Depends(get_db),
):
    """Extract text from uploaded PDF/DOCX/TXT resume and optionally run full ATS analysis."""
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    try:
        extracted_text = parse_uploaded_document(file.filename or "resume.pdf", content)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    if not extracted_text or len(extracted_text.strip()) < 20:
        raise HTTPException(
            status_code=422,
            detail="Extracted text is too short (< 20 characters). Please upload a text-readable PDF, DOCX, or TXT resume.",
        )

    skills_preview = extract_skills(extracted_text)
    sections_preview = detect_sections(extracted_text)

    analysis_result = None
    if job_description and len(job_description.strip()) >= 20:
        req = AnalyzeRequest(
            resume_text=extracted_text,
            job_description=job_description,
            candidate_label=candidate_label or (file.filename or "Uploaded Resume"),
            target_role_title=target_role_title or "Target Job Description",
            gemini_api_key=gemini_api_key,
        )
        analysis_result = _run_full_analysis(req, db)

    return {
        "filename": file.filename,
        "byte_size": len(content),
        "character_count": len(extracted_text),
        "extracted_text": extracted_text,
        "skills_detected_count": len(skills_preview),
        "sections_detected": sections_preview,
        "analysis": analysis_result,
    }


@app.post("/api/analyze", response_model=AnalyzeResponse)
def analyze_resume_and_jd(
    req: AnalyzeRequest,
    db: Session = Depends(get_db),
):
    """Run full 6-stage NLP + Vector ATS Resume Analysis, Gap Learning Path, Job Ranking, and Bullet Coaching."""
    return _run_full_analysis(req, db)


@app.post("/api/rewrite-bullets")
def rewrite_custom_bullets(req: RewriteRequest):
    """Rewrite specific resume bullet points using Gemini 3.8 Flash or Guardrailed XYZ/STAR Coach."""
    rewrites, engine_label = rewrite_bullets_with_coach(
        bullets=req.bullets,
        target_jd=req.target_jd,
        missing_skills=req.missing_skills,
        api_key_override=req.gemini_api_key,
    )
    return {
        "rewrites": rewrites,
        "engine_used": engine_label,
        "count": len(rewrites),
    }


@app.get("/api/evaluate")
def evaluate_matching_quality():
    """Run the Retrieval & Matching Evaluation Harness (NDCG@5, MRR, Recall@3: Hybrid Semantic vs Keyword Counter)."""
    return run_matching_evaluation_harness()


@app.get("/api/reports")
def list_saved_reports(limit: int = 15, db: Session = Depends(get_db)):
    """List saved resume analysis reports from SQLite."""
    rows = (
        db.query(SavedReport)
        .order_by(SavedReport.created_at.desc())
        .limit(limit)
        .all()
    )
    return {
        "reports": [
            {
                "id": r.id,
                "candidate_label": r.candidate_label,
                "target_role_title": r.target_role_title,
                "ats_score": r.ats_score,
                "semantic_score": r.semantic_score,
                "keyword_score": r.keyword_score,
                "structure_score": r.structure_score,
                "matched_skills_count": r.matched_skills_count,
                "missing_skills_count": r.missing_skills_count,
                "top_matched_job": r.top_matched_job,
                "created_at": r.created_at.isoformat() if r.created_at else None,
            }
            for r in rows
        ]
    }


@app.get("/api/reports/{report_id}")
def get_saved_report(report_id: int, db: Session = Depends(get_db)):
    """Retrieve a full saved analysis report by ID."""
    row = db.query(SavedReport).filter(SavedReport.id == report_id).first()
    if not row:
        raise HTTPException(status_code=404, detail=f"Report {report_id} not found.")
    payload = json.loads(row.payload_json)
    payload["report_id"] = row.id
    return payload


@app.delete("/api/reports/{report_id}")
def delete_saved_report(report_id: int, db: Session = Depends(get_db)):
    """Delete a saved analysis report."""
    row = db.query(SavedReport).filter(SavedReport.id == report_id).first()
    if not row:
        raise HTTPException(status_code=404, detail=f"Report {report_id} not found.")
    db.delete(row)
    db.commit()
    return {"deleted": True, "report_id": report_id}
