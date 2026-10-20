# RoleFit AI — REST API Documentation

The FastAPI backend runs on port `8008` by default and exposes interactive Swagger UI documentation at:
**`http://localhost:8008/docs`**

---

## Summary of Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/health` | Health check, indexed jobs count, taxonomy stats, Gemini config status. |
| `GET` | `/api/samples` | Lists 1-click sample personas, pre-indexed job counts, and taxonomy size. |
| `GET` | `/api/samples/{persona_id}/pdf` | Generates and downloads a real, printable PDF resume for testing file uploads. |
| `GET` | `/api/jobs` | Retrieves all 12 pre-indexed LinkedIn-style job postings. |
| `POST` | `/api/upload-resume` | Multipart upload for `.pdf`, `.docx`, or `.txt` with optional live analysis. |
| `POST` | `/api/analyze` | Full 6-stage ATS analysis, skill gap learning path, and bullet rewrites. |
| `POST` | `/api/rewrite-bullets` | On-demand bullet rewriting using Gemini 3.8 Flash or Guardrailed Coach. |
| `GET` | `/api/evaluate` | Runs the retrieval benchmark (Hybrid Semantic vs. Keyword Counter). |
| `GET` | `/api/reports` | Lists saved analysis reports persisted in SQLite. |
| `GET` | `/api/reports/{id}` | Retrieves full JSON payload of a previously saved analysis report. |
| `DELETE` | `/api/reports/{id}` | Deletes a saved report. |

---

## Endpoint Details & Examples

### 1. `POST /api/analyze`

**Request Body:**
```json
{
  "resume_text": "Aarav Sharma\nEmail: aarav@example.com\nSUMMARY: Python, PyTorch, FastAPI, React...",
  "job_description": "Looking for an Applied AI Engineer with Python, PyTorch, FastAPI, and Docker.",
  "candidate_label": "Aarav Sharma",
  "target_role_title": "Applied AI Engineer",
  "top_n_jobs": 5,
  "save_report": true
}
```

**Response (excerpt):**
```json
{
  "report_id": 1,
  "candidate_label": "Aarav Sharma",
  "target_role_title": "Applied AI Engineer",
  "score_breakdown": {
    "overall_ats_score": 89.2,
    "grade_label": "Strong Match (Top 10% ATS Ready)",
    "semantic_similarity_score": 94.6,
    "keyword_coverage_score": 94.3,
    "impact_structure_score": 70.1,
    "semantic_vs_keyword_delta": 46.6,
    "explanation": "Hybrid ATS Score is 89.2/100..."
  },
  "extracted_skills": [
    { "name": "Python", "category": "Languages", "importance": "required" },
    { "name": "PyTorch", "category": "AI & Machine Learning", "importance": "required" }
  ],
  "matched_jd_skills": [ ... ],
  "missing_jd_skills": [
    { "name": "Docker & Containers", "category": "Cloud & DevOps", "importance": "preferred" }
  ],
  "learning_path": [
    {
      "skill": "Docker & Containers",
      "category": "Cloud & DevOps",
      "priority": "Medium (Role Accelerator)",
      "course_title": "Multi-Stage Dockerfiles & Reproducible Microservices",
      "provider": "Docker Curriculum / Linux Foundation",
      "estimated_hours": 10,
      "capstone_project": "Containerize a full-stack AI app with multi-stage builds and healthchecks.",
      "why_it_matters": "Guarantees reproducible builds from local laptop to cloud production."
    }
  ],
  "rewrites": [
    {
      "original_bullet": "Worked on backend APIs and helped with database queries.",
      "xyz_impact_rewrite": "Architected and scaled backend APIs using Python, FastAPI, reducing p95 API latency by [X%] and supporting [N,000+] daily requests with zero downtime.",
      "star_technical_rewrite": "Spearheaded backend engineering for backend APIs (Python, FastAPI), implementing async request validation to cut response times from [X ms] to [Y ms].",
      "guardrail_note": "Guardrail Active: Inserted bracketed placeholders ([X%]) so you can fill in your true metrics."
    }
  ]
}
```

---

### 2. `POST /api/upload-resume`

Accepts `multipart/form-data` with:
- `file`: Resume file (`.pdf`, `.docx`, `.txt`, `.md`)
- `job_description` (optional): If provided, executes full analysis immediately.
- `candidate_label` (optional)
- `gemini_api_key` (optional)

---

### 3. `GET /api/evaluate`

Executes the automated retrieval benchmark across gold-standard resume-job pairs:

**Response:**
```json
{
  "benchmark_size": 5,
  "jobs_indexed": 12,
  "summary_metrics": {
    "hybrid_mean_ndcg_at_5": 0.91,
    "keyword_mean_ndcg_at_5": 0.863,
    "ndcg_lift": "+4.7%",
    "hybrid_mean_mrr": 1.0,
    "keyword_mean_mrr": 1.0,
    "hybrid_mean_recall_at_3": 0.8,
    "keyword_mean_recall_at_3": 0.733
  }
}
```
