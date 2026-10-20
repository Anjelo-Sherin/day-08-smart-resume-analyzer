"""Semantic Embeddings, FAISS-Style Dense Vector Index, Hybrid ATS Scorer, and Evaluation Harness."""

import math
import re
from typing import Any
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.schemas import (
    BulletAnalysis,
    JobMatchRank,
    ScoreBreakdown,
    SkillItem,
)
from app.services.nlp_extractor import extract_skills
from app.services.sample_data import EVALUATION_BENCHMARK_CASES, JOB_POSTINGS_DATASET
from app.services.taxonomy import SEMANTIC_CONCEPT_CLUSTERS, SKILL_TAXONOMY


def _expand_semantic_concepts(text: str) -> str:
    """Enrich text with canonical taxonomy names and latent concept cluster tags for semantic vector alignment."""
    lower = text.lower()
    extra_tokens: list[str] = []

    # 1. Expand taxonomy aliases to canonical skill names + categories
    skills = extract_skills(text)
    for s in skills:
        extra_tokens.append(s.name.lower())
        extra_tokens.append(s.category.lower().replace("&", " "))

    # 2. Expand semantic concept clusters when any cluster trigger appears
    for cluster_tag, phrases in SEMANTIC_CONCEPT_CLUSTERS.items():
        hits = sum(1 for p in phrases if p in lower)
        if hits >= 1:
            extra_tokens.extend([cluster_tag] * min(4, hits + 1))

    return f"{text}\n" + " ".join(extra_tokens)


class SemanticJobVectorIndex:
    """Dense L2-normalized semantic + n-gram vector index over the Job Postings corpus."""

    def __init__(self) -> None:
        self.jobs = JOB_POSTINGS_DATASET
        self.job_skills: dict[str, list[SkillItem]] = {}
        corpus_expanded: list[str] = []

        for job in self.jobs:
            full_doc = f"{job['title']} {job['domain']} {job['description']}"
            self.job_skills[job["job_id"]] = extract_skills(full_doc, mark_importance_from_jd=True)
            corpus_expanded.append(_expand_semantic_concepts(full_doc))

        self.vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            stop_words="english",
            sublinear_tf=True,
            max_features=4096,
        )
        sparse_matrix = self.vectorizer.fit_transform(corpus_expanded)
        self.job_vectors = sparse_matrix.toarray().astype(np.float32)
        norms = np.linalg.norm(self.job_vectors, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        self.job_vectors = self.job_vectors / norms

    def embed_text(self, text: str) -> np.ndarray:
        expanded = _expand_semantic_concepts(text)
        vec = self.vectorizer.transform([expanded]).toarray().astype(np.float32)[0]
        norm = float(np.linalg.norm(vec))
        if norm > 0:
            vec = vec / norm
        return vec

    def compute_pair_semantic_similarity(self, resume_text: str, jd_text: str) -> float:
        """Compute calibrated semantic cosine similarity (0-100) between de-biased resume and target JD."""
        v_res = self.embed_text(resume_text)
        v_jd = self.embed_text(jd_text)
        raw_cos = float(np.dot(v_res, v_jd))

        # Calibrate raw TF-IDF/concept cosine (typically 0.15 - 0.78 for matching documents) onto 0-100 scale
        calibrated = min(99.0, max(12.0, (math.sqrt(max(0.0, raw_cos)) * 108.0)))
        return round(calibrated, 1)

    def rank_jobs_for_resume(
        self,
        debiased_resume_text: str,
        resume_skills: list[SkillItem],
        top_n: int = 6,
    ) -> list[JobMatchRank]:
        """Search vector index for Top-N best-fit roles combining vector cosine similarity and skill coverage."""
        v_res = self.embed_text(debiased_resume_text)
        cos_scores = np.dot(self.job_vectors, v_res)
        res_skill_names = {s.name for s in resume_skills}

        ranked: list[JobMatchRank] = []
        for idx, job in enumerate(self.jobs):
            raw_cos = float(max(0.0, cos_scores[idx]))
            sem_score = min(98.0, round(math.sqrt(raw_cos) * 108.0, 1))

            j_skills = self.job_skills[job["job_id"]]
            j_names = [s.name for s in j_skills]
            matched = [name for name in j_names if name in res_skill_names]
            missing = [name for name in j_names if name not in res_skill_names]

            overlap_score = (
                round((len(matched) / len(j_names)) * 100.0, 1) if j_names else sem_score
            )
            overall = round(0.48 * sem_score + 0.52 * overlap_score, 1)

            if matched:
                why = (
                    f"Matches {len(matched)}/{len(j_names)} core role skills ({', '.join(matched[:4])}) "
                    f"with {sem_score}% semantic alignment in {job['domain']}."
                )
            else:
                why = f"Adjacent domain alignment ({sem_score}% semantic similarity); build core skills to unlock."

            ranked.append(
                JobMatchRank(
                    job_id=job["job_id"],
                    title=job["title"],
                    company=job["company"],
                    location=job["location"],
                    work_mode=job["work_mode"],
                    domain=job["domain"],
                    seniority=job["seniority"],
                    salary_range=job["salary_range"],
                    overall_fit_score=overall,
                    semantic_similarity=sem_score,
                    skill_overlap_score=overlap_score,
                    matched_skills=matched,
                    missing_skills=missing,
                    why_it_fits=why,
                    description=job["description"],
                )
            )

        ranked.sort(key=lambda r: r.overall_fit_score, reverse=True)
        return ranked[:top_n]


# Singleton vector index initialized on module load
vector_index = SemanticJobVectorIndex()


def compute_ats_score_breakdown(
    debiased_resume_text: str,
    jd_text: str,
    matched_jd_skills: list[SkillItem],
    missing_jd_skills: list[SkillItem],
    sections_detected: list[str],
    bullet_audits: list[BulletAnalysis],
) -> ScoreBreakdown:
    """Compute explainable hybrid ATS score combining Semantic Similarity, Keyword Coverage, and Impact Readiness."""
    semantic_score = vector_index.compute_pair_semantic_similarity(
        debiased_resume_text, jd_text
    )

    # Weighted keyword coverage: required skills weight 1.0, preferred skills weight 0.5
    total_weight = 0.0
    matched_weight = 0.0
    for s in matched_jd_skills:
        w = 1.0 if s.importance == "required" else 0.5
        total_weight += w
        matched_weight += w
    for s in missing_jd_skills:
        w = 1.0 if s.importance == "required" else 0.5
        total_weight += w

    if total_weight > 0:
        keyword_score = round((matched_weight / total_weight) * 100.0, 1)
    else:
        keyword_score = semantic_score

    # Impact & ATS Structure score: section completeness + bullet strength + metric ratio
    section_ratio = min(1.0, len(sections_detected) / 4.0)
    if bullet_audits:
        avg_bullet_strength = sum(b.strength_score for b in bullet_audits) / len(bullet_audits)
    else:
        avg_bullet_strength = 60.0
    structure_score = round(0.45 * (section_ratio * 100.0) + 0.55 * avg_bullet_strength, 1)

    overall = round(
        0.40 * semantic_score + 0.40 * keyword_score + 0.20 * structure_score,
        1,
    )

    if overall >= 82:
        grade = "Strong Match (Top 10% ATS Ready)"
    elif overall >= 68:
        grade = "Competitive Match (Tailor Missing Gaps)"
    elif overall >= 52:
        grade = "Partial Match (Upskilling Recommended)"
    else:
        grade = "Low Alignment (Pivot / Bridge Core Skills)"

    # Compare against naive exact keyword counter (without synonym expansion or concept vectors)
    jd_words = {
        w
        for w in re.findall(r"\b[a-z]{4,}\b", jd_text.lower())
        if w not in {"with", "that", "this", "from", "have", "will", "your", "team", "work", "role", "experience"}
    }
    res_words = set(re.findall(r"\b[a-z]{4,}\b", debiased_resume_text.lower()))
    naive_overlap = (
        round((len(jd_words & res_words) / len(jd_words)) * 100.0, 1) if jd_words else 50.0
    )
    delta = round(overall - naive_overlap, 1)

    explanation = (
        f"Hybrid ATS Score is {overall}/100 ({grade}): blends {semantic_score}% dense semantic similarity, "
        f"{keyword_score}% taxonomy skill coverage ({len(matched_jd_skills)}/{len(matched_jd_skills) + len(missing_jd_skills)} skills), "
        f"and {structure_score}% bullet impact & structure readiness."
    )

    return ScoreBreakdown(
        overall_ats_score=overall,
        grade_label=grade,
        semantic_similarity_score=semantic_score,
        keyword_coverage_score=keyword_score,
        impact_structure_score=structure_score,
        semantic_vs_keyword_delta=delta,
        explanation=explanation,
    )


def _dcg_at_k(relevances: list[float], k: int) -> float:
    return sum(
        rel / math.log2(idx + 2) for idx, rel in enumerate(relevances[:k])
    )


def _ndcg_at_k(predicted_ids: list[str], gold_ids: list[str], k: int = 5) -> float:
    rel_map = {jid: float(len(gold_ids) - i) for i, jid in enumerate(gold_ids)}
    actual_rels = [rel_map.get(jid, 0.0) for jid in predicted_ids[:k]]
    ideal_rels = sorted(rel_map.values(), reverse=True)[:k]
    idcg = _dcg_at_k(ideal_rels, k)
    if idcg == 0:
        return 0.0
    return _dcg_at_k(actual_rels, k) / idcg


def run_matching_evaluation_harness() -> dict[str, Any]:
    """Evaluate Hybrid Semantic + Taxonomy Search vs. Naive Keyword Counter across gold benchmark cases."""
    case_results = []
    hybrid_ndcgs: list[float] = []
    keyword_ndcgs: list[float] = []
    hybrid_mrrs: list[float] = []
    keyword_mrrs: list[float] = []
    hybrid_recalls: list[float] = []
    keyword_recalls: list[float] = []

    for case in EVALUATION_BENCHMARK_CASES:
        snippet = case["resume_snippet"]
        gold = case["expected_relevant_jobs"]
        res_skills = extract_skills(snippet)

        # 1. Hybrid Semantic + Taxonomy Ranking
        hybrid_ranks = vector_index.rank_jobs_for_resume(snippet, res_skills, top_n=5)
        hybrid_ids = [r.job_id for r in hybrid_ranks]

        # 2. Naive Exact Keyword Overlap Ranking (no taxonomy aliases, no concept clusters)
        res_tokens = set(re.findall(r"\b[a-z0-9]{3,}\b", snippet.lower()))
        naive_scored = []
        for job in JOB_POSTINGS_DATASET:
            job_tokens = set(re.findall(r"\b[a-z0-9]{3,}\b", job["description"].lower()))
            overlap = len(res_tokens & job_tokens) / max(1, len(job_tokens))
            naive_scored.append((overlap, job["job_id"]))
        naive_scored.sort(reverse=True)
        keyword_ids = [jid for _, jid in naive_scored[:5]]

        h_ndcg = round(_ndcg_at_k(hybrid_ids, gold, k=5), 3)
        k_ndcg = round(_ndcg_at_k(keyword_ids, gold, k=5), 3)

        h_mrr = next((round(1.0 / (i + 1), 3) for i, jid in enumerate(hybrid_ids) if jid in gold), 0.0)
        k_mrr = next((round(1.0 / (i + 1), 3) for i, jid in enumerate(keyword_ids) if jid in gold), 0.0)

        h_rec = round(len(set(hybrid_ids[:3]) & set(gold)) / len(gold), 3)
        k_rec = round(len(set(keyword_ids[:3]) & set(gold)) / len(gold), 3)

        hybrid_ndcgs.append(h_ndcg)
        keyword_ndcgs.append(k_ndcg)
        hybrid_mrrs.append(h_mrr)
        keyword_mrrs.append(k_mrr)
        hybrid_recalls.append(h_rec)
        keyword_recalls.append(k_rec)

        case_results.append(
            {
                "case_id": case["case_id"],
                "title": case["title"],
                "expected_top_jobs": gold,
                "hybrid_top3": hybrid_ids[:3],
                "keyword_top3": keyword_ids[:3],
                "hybrid_ndcg_at_5": h_ndcg,
                "keyword_ndcg_at_5": k_ndcg,
                "hybrid_recall_at_3": h_rec,
                "keyword_recall_at_3": k_rec,
            }
        )

    return {
        "benchmark_size": len(EVALUATION_BENCHMARK_CASES),
        "jobs_indexed": len(JOB_POSTINGS_DATASET),
        "skills_in_taxonomy": len(SKILL_TAXONOMY),
        "summary_metrics": {
            "hybrid_mean_ndcg_at_5": round(float(np.mean(hybrid_ndcgs)), 3),
            "keyword_mean_ndcg_at_5": round(float(np.mean(keyword_ndcgs)), 3),
            "ndcg_lift": f"+{round((float(np.mean(hybrid_ndcgs)) - float(np.mean(keyword_ndcgs))) * 100, 1)}%",
            "hybrid_mean_mrr": round(float(np.mean(hybrid_mrrs)), 3),
            "keyword_mean_mrr": round(float(np.mean(keyword_mrrs)), 3),
            "hybrid_mean_recall_at_3": round(float(np.mean(hybrid_recalls)), 3),
            "keyword_mean_recall_at_3": round(float(np.mean(keyword_recalls)), 3),
        },
        "cases": case_results,
    }
