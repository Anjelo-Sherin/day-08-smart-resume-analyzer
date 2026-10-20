from typing import Optional
from pydantic import BaseModel, Field


class SkillItem(BaseModel):
    name: str
    category: str
    matched_alias: Optional[str] = None
    importance: str = "required"  # "required" | "preferred"


class LearningStep(BaseModel):
    skill: str
    category: str
    priority: str  # "High (Core Requirement)" | "Medium (Role Accelerator)"
    course_title: str
    provider: str
    estimated_hours: int
    capstone_project: str
    why_it_matters: str


class BulletAnalysis(BaseModel):
    original: str
    has_metric: bool
    has_strong_verb: bool
    weak_verbs_found: list[str]
    strength_score: int  # 0 to 100
    critique: str


class BulletRewriteItem(BaseModel):
    original_bullet: str = Field(description="The original weak resume bullet point.")
    xyz_impact_rewrite: str = Field(
        description="Rewritten using Google's XYZ formula: Accomplished [X] as measured by [Y], by doing [Z]. Uses [X%] or [N] placeholders for metrics not in original."
    )
    star_technical_rewrite: str = Field(
        description="Rewritten emphasizing Situation/Task, technical Action, and measurable Result."
    )
    ats_aligned_rewrite: str = Field(
        description="Rewritten to naturally incorporate relevant target job description skills without keyword stuffing."
    )
    injected_keywords: list[str] = Field(
        description="Target job skills naturally woven into the rewrite."
    )
    guardrail_note: str = Field(
        description="Explanation of why this rewrite improves impact while preserving factual honesty."
    )


class BulletRewriteBatchSchema(BaseModel):
    rewrites: list[BulletRewriteItem]
    engine_used: str = "gemini-3.8-flash"


class EducationEntry(BaseModel):
    degree: str
    field_of_study: str
    institution: str
    year: Optional[str] = None


class ExperienceSummary(BaseModel):
    estimated_years: float
    seniority_level: str
    roles_detected: list[str]
    quantified_bullet_ratio: float
    total_bullets: int
    quantified_bullets: int


class BiasAuditReport(BaseModel):
    pii_tokens_scrubbed: int
    scrubbed_categories: list[str]
    debiased_matching_active: bool
    jd_inclusivity_score: int
    jd_inclusivity_flags: list[str]
    audit_summary: str


class JobMatchRank(BaseModel):
    job_id: str
    title: str
    company: str
    location: str
    work_mode: str
    domain: str
    seniority: str
    salary_range: str
    overall_fit_score: float
    semantic_similarity: float
    skill_overlap_score: float
    matched_skills: list[str]
    missing_skills: list[str]
    why_it_fits: str
    description: str


class ScoreBreakdown(BaseModel):
    overall_ats_score: float
    grade_label: str
    semantic_similarity_score: float
    keyword_coverage_score: float
    impact_structure_score: float
    semantic_vs_keyword_delta: float
    explanation: str


class AnalyzeRequest(BaseModel):
    resume_text: str = Field(..., min_length=20)
    job_description: str = Field(..., min_length=20)
    candidate_label: Optional[str] = "Anonymous Candidate"
    target_role_title: Optional[str] = "Target Job Description"
    top_n_jobs: int = Field(default=6, ge=1, le=15)
    save_report: bool = True
    gemini_api_key: Optional[str] = None


class AnalyzeResponse(BaseModel):
    report_id: Optional[int] = None
    candidate_label: str
    target_role_title: str
    score_breakdown: ScoreBreakdown
    extracted_skills: list[SkillItem]
    matched_jd_skills: list[SkillItem]
    missing_jd_skills: list[SkillItem]
    bonus_resume_skills: list[SkillItem]
    learning_path: list[LearningStep]
    education: list[EducationEntry]
    experience: ExperienceSummary
    sections_detected: list[str]
    bullet_audits: list[BulletAnalysis]
    rewrites: list[BulletRewriteItem]
    rewrite_engine: str
    top_job_matches: list[JobMatchRank]
    bias_audit: BiasAuditReport


class RewriteRequest(BaseModel):
    bullets: list[str]
    target_jd: str = ""
    missing_skills: list[str] = []
    gemini_api_key: Optional[str] = None
