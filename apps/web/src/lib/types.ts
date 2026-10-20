export interface SkillItem {
  name: string;
  category: string;
  matched_alias?: string | null;
  importance: "required" | "preferred" | string;
}

export interface LearningStep {
  skill: string;
  category: string;
  priority: string;
  course_title: string;
  provider: string;
  estimated_hours: number;
  capstone_project: string;
  why_it_matters: string;
}

export interface BulletAnalysis {
  original: string;
  has_metric: boolean;
  has_strong_verb: boolean;
  weak_verbs_found: string[];
  strength_score: number;
  critique: string;
}

export interface BulletRewriteItem {
  original_bullet: string;
  xyz_impact_rewrite: string;
  star_technical_rewrite: string;
  ats_aligned_rewrite: string;
  injected_keywords: string[];
  guardrail_note: string;
}

export interface EducationEntry {
  degree: string;
  field_of_study: string;
  institution: string;
  year?: string | null;
}

export interface ExperienceSummary {
  estimated_years: number;
  seniority_level: string;
  roles_detected: string[];
  quantified_bullet_ratio: number;
  total_bullets: number;
  quantified_bullets: number;
}

export interface BiasAuditReport {
  pii_tokens_scrubbed: number;
  scrubbed_categories: string[];
  debiased_matching_active: boolean;
  jd_inclusivity_score: number;
  jd_inclusivity_flags: string[];
  audit_summary: string;
}

export interface JobMatchRank {
  job_id: string;
  title: string;
  company: string;
  location: string;
  work_mode: string;
  domain: string;
  seniority: string;
  salary_range: string;
  overall_fit_score: number;
  semantic_similarity: number;
  skill_overlap_score: number;
  matched_skills: string[];
  missing_skills: string[];
  why_it_fits: string;
  description: string;
}

export interface ScoreBreakdown {
  overall_ats_score: number;
  grade_label: string;
  semantic_similarity_score: number;
  keyword_coverage_score: number;
  impact_structure_score: number;
  semantic_vs_keyword_delta: number;
  explanation: string;
}

export interface AnalyzeResponse {
  report_id?: number | null;
  candidate_label: string;
  target_role_title: string;
  score_breakdown: ScoreBreakdown;
  extracted_skills: SkillItem[];
  matched_jd_skills: SkillItem[];
  missing_jd_skills: SkillItem[];
  bonus_resume_skills: SkillItem[];
  learning_path: LearningStep[];
  education: EducationEntry[];
  experience: ExperienceSummary;
  sections_detected: string[];
  bullet_audits: BulletAnalysis[];
  rewrites: BulletRewriteItem[];
  rewrite_engine: string;
  top_job_matches: JobMatchRank[];
  bias_audit: BiasAuditReport;
}

export interface SamplePersona {
  id: string;
  label: string;
  role_focus: string;
  target_role_title: string;
  resume_text: string;
  job_description: string;
}

export interface SavedReportSummary {
  id: number;
  candidate_label: string;
  target_role_title: string;
  ats_score: number;
  semantic_score: number;
  keyword_score: number;
  structure_score: number;
  matched_skills_count: number;
  missing_skills_count: number;
  top_matched_job: string;
  created_at: string;
}

export interface EvaluationResponse {
  benchmark_size: number;
  jobs_indexed: number;
  skills_in_taxonomy: number;
  summary_metrics: {
    hybrid_mean_ndcg_at_5: number;
    keyword_mean_ndcg_at_5: number;
    ndcg_lift: string;
    hybrid_mean_mrr: number;
    keyword_mean_mrr: number;
    hybrid_mean_recall_at_3: number;
    keyword_mean_recall_at_3: number;
  };
  cases: Array<{
    case_id: string;
    title: string;
    expected_top_jobs: string[];
    hybrid_top3: string[];
    keyword_top3: string[];
    hybrid_ndcg_at_5: number;
    keyword_ndcg_at_5: number;
    hybrid_recall_at_3: number;
    keyword_recall_at_3: number;
  }>;
}
