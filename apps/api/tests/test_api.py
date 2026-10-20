import io
import zipfile
from fastapi.testclient import TestClient

from app.main import app
from app.services.document_parser import generate_pdf_bytes, parse_uploaded_document
from app.services.sample_data import SAMPLE_PERSONAS

client = TestClient(app)


def _build_minimal_docx_bytes(paragraphs: list[str]) -> bytes:
    buf = io.BytesIO()
    body_xml = "".join(
        f"<w:p><w:r><w:t>{p}</w:t></w:r></w:p>" for p in paragraphs
    )
    doc_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        f"<w:body>{body_xml}</w:body></w:document>"
    )
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("word/document.xml", doc_xml)
    return buf.getvalue()


def test_health_and_samples():
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ok"
    assert data["jobs_indexed"] >= 10
    assert data["skills_in_taxonomy"] >= 20

    samples_res = client.get("/api/samples")
    assert samples_res.status_code == 200
    assert len(samples_res.json()["personas"]) >= 3


def test_pdf_roundtrip_generation_and_upload():
    persona = SAMPLE_PERSONAS[0]
    pdf_res = client.get(f"/api/samples/{persona['id']}/pdf")
    assert pdf_res.status_code == 200
    assert pdf_res.content.startswith(b"%PDF-1.4")

    upload_res = client.post(
        "/api/upload-resume",
        files={"file": ("sample_resume.pdf", pdf_res.content, "application/pdf")},
        data={
            "job_description": persona["job_description"],
            "candidate_label": "PDF Upload Test Candidate",
            "target_role_title": persona["target_role_title"],
        },
    )
    assert upload_res.status_code == 200
    payload = upload_res.json()
    assert "Sentence-Transformers" in payload["extracted_text"] or "FastAPI" in payload["extracted_text"]
    assert payload["skills_detected_count"] >= 8
    assert payload["analysis"] is not None
    assert payload["analysis"]["score_breakdown"]["overall_ats_score"] >= 65.0


def test_docx_upload_extraction():
    docx_bytes = _build_minimal_docx_bytes(
        [
            "Alex Rivera — Full Stack Engineer",
            "SUMMARY: Built scalable Python, FastAPI, React, TypeScript, and PostgreSQL web applications.",
            "EXPERIENCE:",
            "- Engineered REST APIs with FastAPI and Docker, reducing p95 latency by 38%.",
            "- Worked on frontend components in Next.js and Tailwind CSS.",
        ]
    )
    extracted = parse_uploaded_document("resume.docx", docx_bytes)
    assert "FastAPI" in extracted
    assert "PostgreSQL" in extracted


def test_full_analyze_pipeline_and_persistence():
    persona = SAMPLE_PERSONAS[0]
    res = client.post(
        "/api/analyze",
        json={
            "resume_text": persona["resume_text"],
            "job_description": persona["job_description"],
            "candidate_label": persona["label"],
            "target_role_title": persona["target_role_title"],
            "top_n_jobs": 5,
            "save_report": True,
        },
    )
    assert res.status_code == 200
    data = res.json()
    assert data["report_id"] is not None
    assert data["score_breakdown"]["overall_ats_score"] > 70.0
    assert len(data["matched_jd_skills"]) >= 8
    assert len(data["missing_jd_skills"]) >= 1
    assert len(data["learning_path"]) == len(data["missing_jd_skills"])
    assert len(data["top_job_matches"]) == 5
    assert data["bias_audit"]["debiased_matching_active"] is True
    assert data["bias_audit"]["pii_tokens_scrubbed"] >= 2
    assert len(data["rewrites"]) >= 1
    assert "[" in data["rewrites"][0]["xyz_impact_rewrite"]  # Placeholder guardrail check

    # Verify saved report retrieval
    rep_id = data["report_id"]
    get_res = client.get(f"/api/reports/{rep_id}")
    assert get_res.status_code == 200
    assert get_res.json()["candidate_label"] == persona["label"]


def test_rewrite_bullets_endpoint():
    res = client.post(
        "/api/rewrite-bullets",
        json={
            "bullets": [
                "Worked on training deep learning models in PyTorch for text classification.",
                "Helped with building React and TypeScript dashboard pages.",
            ],
            "target_jd": "Looking for a Python, PyTorch, FastAPI, and React engineer.",
            "missing_skills": ["FastAPI", "Docker"],
        },
    )
    assert res.status_code == 200
    body = res.json()
    assert body["count"] == 2
    assert len(body["rewrites"][0]["xyz_impact_rewrite"]) > 30


def test_evaluation_harness_metrics():
    res = client.get("/api/evaluate")
    assert res.status_code == 200
    ev = res.json()
    metrics = ev["summary_metrics"]
    assert metrics["hybrid_mean_ndcg_at_5"] >= metrics["keyword_mean_ndcg_at_5"]
    assert metrics["hybrid_mean_ndcg_at_5"] >= 0.75
