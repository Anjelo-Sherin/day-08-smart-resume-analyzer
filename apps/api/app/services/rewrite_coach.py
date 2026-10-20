"""LLM Bullet-Point Rewrite Coach (Gemini 3.8 Flash Interactions API + Guardrailed XYZ/STAR Engine)."""

import json
import re
from typing import Optional
import httpx

from app.config import settings
from app.schemas import BulletRewriteBatchSchema, BulletRewriteItem
from app.services.nlp_extractor import extract_skills
from app.services.taxonomy import WEAK_ACTION_PHRASES


def _strip_weak_prefix(bullet: str) -> str:
    cleaned = bullet.strip().rstrip(".")
    lower = cleaned.lower()
    for phrase in sorted(WEAK_ACTION_PHRASES, key=len, reverse=True):
        if lower.startswith(phrase):
            rest = cleaned[len(phrase) :].strip(" ,:-")
            return rest
    # Also strip generic leading verbs like "Built", "Created", "Developed" so we can re-frame cleanly
    m = re.match(
        r"^(?:worked|helped|assisted|responsible|built|created|developed|made|wrote)\s+(?:on|with|in|for)?\s*(.*)$",
        cleaned,
        flags=re.IGNORECASE,
    )
    if m and len(m.group(1).split()) >= 3:
        return m.group(1).strip()
    return cleaned


def _deterministic_guardrail_rewrite(
    bullet: str,
    jd_skills: list[str],
    missing_skills: list[str],
) -> BulletRewriteItem:
    """Deterministic XYZ / STAR impact rewrite with factual guardrails ([X%] placeholders)."""
    core_clause = _strip_weak_prefix(bullet)
    if core_clause:
        core_lower = core_clause[0].lower() + core_clause[1:]
    else:
        core_lower = bullet.strip().rstrip(".")

    bullet_skills = [s.name for s in extract_skills(bullet)]
    injected = list(dict.fromkeys(bullet_skills + jd_skills[:2] + missing_skills[:1]))[:3]
    tech_tag = ", ".join(injected) if injected else "production Python & modular APIs"

    # Choose context-appropriate verb & metric placeholder
    lower_b = bullet.lower()
    if any(k in lower_b for k in ["api", "backend", "fastapi", "endpoint", "server", "query", "sql"]):
        xyz = (
            f"Architected and scaled {core_lower} using {tech_tag}, reducing p95 API latency by [X%] "
            f"and supporting [N,000+] daily requests with zero downtime."
        )
        star = (
            f"Spearheaded backend engineering for {core_lower} ({tech_tag}), implementing async request validation "
            f"and query indexing to cut response times from [X ms] to [Y ms]."
        )
    elif any(k in lower_b for k in ["model", "ml", "ai", "nlp", "rag", "gemini", "pytorch", "xgboost", "pdf", "spacy"]):
        xyz = (
            f"Engineered {core_lower} powered by {tech_tag}, improving evaluation accuracy/F1 by [X%] "
            f"across [N,000+] benchmark records while enforcing strict output guardrails."
        )
        star = (
            f"Designed and benchmarked {core_lower} utilizing {tech_tag}, automating end-to-end inference "
            f"and reducing manual triage effort by [X hours/week]."
        )
    elif any(k in lower_b for k in ["ui", "frontend", "react", "next.js", "dashboard", "tailwind", "chart"]):
        xyz = (
            f"Delivered an interactive, WCAG-accessible workflow for {core_lower} in {tech_tag}, "
            f"accelerating user task completion by [X%] and boosting Lighthouse performance to [95+]."
        )
        star = (
            f"Refactored {core_lower} into modular {tech_tag} components with optimistic state updates, "
            f"cutting client bundle overhead by [X%] across desktop and mobile viewports."
        )
    else:
        xyz = (
            f"Engineered and automated {core_lower} leveraging {tech_tag}, increasing operational throughput "
            f"by [X%] and eliminating [N hours/week] of manual processing."
        )
        star = (
            f"Owned end-to-end delivery of {core_lower} with {tech_tag}, establishing automated testing "
            f"and observability that improved reliability to [99.X%]."
        )

    ats_aligned = (
        f"Implemented production-grade {core_lower} integrating {tech_tag}, aligning system architecture "
        f"with SLA targets and delivering a measurable [X%] improvement in pipeline efficiency."
    )

    return BulletRewriteItem(
        original_bullet=bullet,
        xyz_impact_rewrite=xyz,
        star_technical_rewrite=star,
        ats_aligned_rewrite=ats_aligned,
        injected_keywords=injected,
        guardrail_note=(
            "Guardrail Active: Replaced passive phrasing with active ownership verbs and inserted bracketed "
            "placeholders ([X%], [N]) so you can fill in your true metrics without fabricating experience."
        ),
    )


def rewrite_bullets_with_coach(
    bullets: list[str],
    target_jd: str = "",
    missing_skills: Optional[list[str]] = None,
    api_key_override: Optional[str] = None,
) -> tuple[list[BulletRewriteItem], str]:
    """Rewrite weak resume bullets into XYZ/STAR impact statements using Gemini 3.8 Flash or Guardrailed Fallback."""
    clean_bullets = [b.strip() for b in bullets if b and b.strip()][:6]
    if not clean_bullets:
        return [], "guardrail-xyz-coach"

    jd_skill_names = [s.name for s in extract_skills(target_jd)] if target_jd else []
    missing_list = missing_skills or []
    active_key = (api_key_override or settings.gemini_api_key or "").strip()

    if active_key:
        prompt = f"""You are an expert Staff Technical Recruiter and Resume Coach.
Rewrite each of the following resume bullet points into three high-impact variants:
1. xyz_impact_rewrite: Google's XYZ formula ("Accomplished [X] as measured by [Y], by doing [Z]").
2. star_technical_rewrite: Action + Technical Architecture + Measurable Result.
3. ats_aligned_rewrite: Naturally weaves in relevant skills from the target Job Description.

STRICT GUARDRAILS:
- NEVER invent fake employers, degrees, or fabricated numerical claims.
- Where the original bullet lacks a number, insert explicit bracketed placeholders like [X%], [N ms], or [N+ users] so the candidate knows to fill in their real figure.
- Target Job Description Skills: {', '.join(jd_skill_names[:10]) or 'Software & AI Engineering'}
- Candidate Missing/Target Skills to highlight only if contextually plausible: {', '.join(missing_list[:5])}

Bullets to rewrite:
{json.dumps(clean_bullets, indent=2)}
"""
        # 1. Try official google-genai SDK (>=2.30.1) with client.interactions.create
        try:
            from google import genai  # type: ignore

            client = genai.Client(api_key=active_key)
            interaction = client.interactions.create(
                model=settings.gemini_model,
                input=prompt,
                response_format={
                    "type": "text",
                    "mime_type": "application/json",
                    "schema": BulletRewriteBatchSchema.model_json_schema(),
                },
            )
            if interaction and interaction.output_text:
                parsed = BulletRewriteBatchSchema.model_validate_json(
                    interaction.output_text
                )
                return parsed.rewrites, f"{settings.gemini_model} (google-genai SDK)"
        except Exception:
            pass

        # 2. Try Gemini Interactions REST API v1beta2 directly via httpx
        try:
            with httpx.Client(timeout=12.0) as http_client:
                resp = http_client.post(
                    "https://generativelanguage.googleapis.com/v1beta2/interactions",
                    headers={
                        "Content-Type": "application/json",
                        "x-goog-api-key": active_key,
                    },
                    json={
                        "model": settings.gemini_model,
                        "input": prompt,
                        "response_format": {
                            "type": "text",
                            "mime_type": "application/json",
                            "schema": BulletRewriteBatchSchema.model_json_schema(),
                        },
                    },
                )
                if resp.status_code == 200:
                    data = resp.json()
                    output_text = data.get("output_text")
                    if not output_text:
                        for step in reversed(data.get("steps", [])):
                            if step.get("type") == "model_output":
                                for part in step.get("content", []):
                                    if part.get("type") == "text":
                                        output_text = part.get("text")
                                        break
                            if output_text:
                                break
                    if output_text:
                        parsed = BulletRewriteBatchSchema.model_validate_json(output_text)
                        return parsed.rewrites, f"{settings.gemini_model} (Interactions API)"
        except Exception:
            pass

    # 3. Deterministic Guardrailed XYZ/STAR Coach Engine (zero-key local mode)
    rewrites = [
        _deterministic_guardrail_rewrite(b, jd_skill_names, missing_list)
        for b in clean_bullets
    ]
    return rewrites, "Guardrailed XYZ/STAR Coach (Local Deterministic Mode — set GEMINI_API_KEY for live Gemini 3.8 Flash)"
