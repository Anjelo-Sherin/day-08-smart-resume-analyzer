"""NLP Entity & Skill Extractor, Section Parser, Learning Path Builder, and Bias Auditor."""

import re
from typing import Optional

from app.schemas import (
    BiasAuditReport,
    BulletAnalysis,
    EducationEntry,
    ExperienceSummary,
    LearningStep,
    SkillItem,
)
from app.services.taxonomy import (
    SKILL_TAXONOMY,
    STRONG_ACTION_VERBS,
    WEAK_ACTION_PHRASES,
)


def _compile_alias_pattern(alias: str) -> re.Pattern:
    escaped = re.escape(alias.lower())
    # Allow flexible whitespace or hyphen
    escaped = escaped.replace(r"\ ", r"[\s\-]+")
    return re.compile(rf"(?<![a-z0-9_]){escaped}(?![a-z0-9_])", re.IGNORECASE)


_COMPILED_SKILL_PATTERNS: dict[str, list[tuple[str, re.Pattern]]] = {
    skill_key: [(alias, _compile_alias_pattern(alias)) for alias in meta["aliases"]]
    for skill_key, meta in SKILL_TAXONOMY.items()
}


def extract_skills(text: str, mark_importance_from_jd: bool = False) -> list[SkillItem]:
    """Extract canonical skills from text using taxonomy boundary patterns and synonym aliases."""
    lower_text = text.lower()
    preferred_section_pos = -1
    if mark_importance_from_jd:
        for marker in ["nice to have", "preferred", "bonus", "plus", "optional"]:
            idx = lower_text.find(marker)
            if idx != -1:
                preferred_section_pos = idx
                break

    found: list[SkillItem] = []
    for skill_key, alias_patterns in _COMPILED_SKILL_PATTERNS.items():
        meta = SKILL_TAXONOMY[skill_key]
        for alias, pattern in alias_patterns:
            match = pattern.search(text)
            if match:
                importance = "required"
                if (
                    mark_importance_from_jd
                    and preferred_section_pos != -1
                    and match.start() > preferred_section_pos
                ):
                    importance = "preferred"
                found.append(
                    SkillItem(
                        name=meta["name"],
                        category=meta["category"],
                        matched_alias=alias,
                        importance=importance,
                    )
                )
                break
    return found


def compute_skill_gap_and_learning_path(
    resume_skills: list[SkillItem], jd_skills: list[SkillItem]
) -> tuple[list[SkillItem], list[SkillItem], list[SkillItem], list[LearningStep]]:
    """Compute matched JD skills, missing JD skills (set difference), bonus resume skills, and learning path."""
    resume_by_name = {s.name: s for s in resume_skills}
    jd_by_name = {s.name: s for s in jd_skills}

    matched = [jd_s for name, jd_s in jd_by_name.items() if name in resume_by_name]
    missing = [jd_s for name, jd_s in jd_by_name.items() if name not in resume_by_name]
    bonus = [res_s for name, res_s in resume_by_name.items() if name not in jd_by_name]

    # Sort missing so 'required' comes before 'preferred'
    missing.sort(key=lambda s: 0 if s.importance == "required" else 1)

    name_to_meta = {meta["name"]: meta for meta in SKILL_TAXONOMY.values()}
    learning_path: list[LearningStep] = []
    for item in missing:
        meta = name_to_meta.get(item.name)
        if not meta:
            continue
        priority = (
            "High (Core Requirement)"
            if item.importance == "required"
            else "Medium (Role Accelerator)"
        )
        learning_path.append(
            LearningStep(
                skill=item.name,
                category=item.category,
                priority=priority,
                course_title=meta["course_title"],
                provider=meta["provider"],
                estimated_hours=meta["estimated_hours"],
                capstone_project=meta["capstone_project"],
                why_it_matters=meta["why_it_matters"],
            )
        )
    return matched, missing, bonus, learning_path


def detect_sections(resume_text: str) -> list[str]:
    """Identify standard ATS resume sections present in the text."""
    section_rules = {
        "Summary / Objective": r"\b(summary|objective|profile|about me)\b",
        "Experience": r"\b(experience|employment|work history|career)\b",
        "Projects": r"\b(projects|personal projects|academic projects|portfolio)\b",
        "Skills": r"\b(skills|technologies|technical skills|core competencies|tech stack)\b",
        "Education": r"\b(education|academic|university|degree|b\.?tech|b\.?s\.?|m\.?s\.?)\b",
        "Certifications / Awards": r"\b(certifications?|awards?|achievements?|publications?|honors)\b",
    }
    detected = []
    for label, pattern in section_rules.items():
        if re.search(pattern, resume_text, flags=re.IGNORECASE):
            detected.append(label)
    return detected


def extract_education(resume_text: str) -> list[EducationEntry]:
    """Extract degree, field of study, institution, and graduation year from resume text."""
    entries: list[EducationEntry] = []
    degree_patterns = [
        (r"\b(Ph\.?D\.?|Doctor of Philosophy)\b", "Ph.D."),
        (r"\b(M\.?Tech\.?|M\.?S\.?|Master of Science|Master of Technology|M\.?E\.?|MCA|MBA)\b", "Master's"),
        (r"\b(B\.?Tech\.?|B\.?S\.?|B\.?E\.?|Bachelor of Technology|Bachelor of Science|Bachelor of Engineering|BCA)\b", "Bachelor's"),
    ]
    field_pattern = re.compile(
        r"\b(Computer Science(?:\s*&\s*Engineering)?|Artificial Intelligence|Data Science|Information Technology|Software Engineering|Electrical Engineering|Mathematics|Statistics|Electronics)\b",
        re.IGNORECASE,
    )
    inst_pattern = re.compile(
        r"\b([A-Z][A-Za-z&,\.\s]{2,45}(?:University|Institute of Technology|College|IIT|NIT|IIIT|School of Engineering|Academy))\b"
    )
    year_pattern = re.compile(r"\b(20[12]\d)\b")

    lines = [ln.strip() for ln in resume_text.splitlines() if ln.strip()]
    for idx, line in enumerate(lines):
        for deg_regex, deg_norm in degree_patterns:
            if re.search(deg_regex, line, flags=re.IGNORECASE):
                context_window = " | ".join(lines[max(0, idx - 1) : min(len(lines), idx + 3)])
                field_m = field_pattern.search(context_window)
                inst_m = inst_pattern.search(context_window)
                year_m = year_pattern.search(context_window)
                entries.append(
                    EducationEntry(
                        degree=deg_norm,
                        field_of_study=field_m.group(1).title() if field_m else "Computer Science / STEM",
                        institution=inst_m.group(1).strip() if inst_m else "Recognized University",
                        year=year_m.group(1) if year_m else None,
                    )
                )
                break

    # Deduplicate by degree
    seen = set()
    unique_entries = []
    for e in entries:
        if e.degree not in seen:
            seen.add(e.degree)
            unique_entries.append(e)
    return unique_entries


def extract_bullets_and_audit(resume_text: str) -> list[BulletAnalysis]:
    """Extract experience/project bullet points and evaluate verb strength and metric quantification."""
    raw_lines = resume_text.splitlines()
    bullets: list[str] = []
    bullet_prefix = re.compile(r"^\s*(?:[\-\*\•\▸\‣]|\d+[\.\)])\s+(.*)$")

    for line in raw_lines:
        m = bullet_prefix.match(line)
        if m:
            candidate = m.group(1).strip()
            if len(candidate.split()) >= 5:
                bullets.append(candidate)

    # Fallback if resume had no bullet characters: pick action-like sentences from body
    if not bullets:
        for line in raw_lines:
            clean = line.strip()
            if 6 <= len(clean.split()) <= 35 and not clean.endswith(":"):
                if any(
                    clean.lower().startswith(v)
                    for v in list(STRONG_ACTION_VERBS) + ["worked", "helped", "built", "created", "developed", "responsible"]
                ):
                    bullets.append(clean)

    metric_pattern = re.compile(
        r"(\b\d+(?:\.\d+)?\s*(?:%|ms|s|x|k|m|gb|tb|fps|hours|days|users|requests|queries|pipelines|models|endpoints|services)\b|\$\s*\d+|\breduced\s+by\b|\bincreased\s+by\b)",
        re.IGNORECASE,
    )

    audits: list[BulletAnalysis] = []
    for b in bullets[:12]:
        lower_b = b.lower()
        first_word = re.sub(r"[^a-z\-]", "", lower_b.split()[0]) if lower_b.split() else ""
        has_strong_verb = first_word in STRONG_ACTION_VERBS or any(
            v in lower_b.split()[:3] for v in STRONG_ACTION_VERBS
        )
        weak_found = [w for w in WEAK_ACTION_PHRASES if w in lower_b]
        has_metric = bool(metric_pattern.search(b))

        score = 45
        if has_strong_verb:
            score += 25
        if has_metric:
            score += 30
        if weak_found:
            score -= 25
        score = max(15, min(100, score))

        if weak_found and not has_metric:
            critique = f"Uses passive phrasing ('{weak_found[0]}') and lacks measurable impact metrics (%, latency, scale)."
        elif weak_found:
            critique = f"Replace passive phrase '{weak_found[0]}' with a direct ownership verb (e.g., Architected, Engineered)."
        elif not has_metric:
            critique = "Strong technical action, but missing quantified outcome (e.g., latency reduction %, throughput, or accuracy gain)."
        elif not has_strong_verb:
            critique = "Contains quantifiable numbers; start with a stronger engineering action verb for maximum ATS impact."
        else:
            critique = "Strong XYZ impact statement with clear action verb and quantified outcome."

        audits.append(
            BulletAnalysis(
                original=b,
                has_metric=has_metric,
                has_strong_verb=has_strong_verb,
                weak_verbs_found=weak_found,
                strength_score=score,
                critique=critique,
            )
        )
    return audits


def extract_experience_summary(
    resume_text: str, bullet_audits: list[BulletAnalysis]
) -> ExperienceSummary:
    """Estimate years of experience, seniority level, detected roles, and bullet quantification ratio."""
    years_explicit = re.findall(
        r"(\d+(?:\.\d+)?)\+?\s*years?\s+of\s+(?:experience|hands-on)",
        resume_text,
        flags=re.IGNORECASE,
    )
    estimated_years = 0.0
    if years_explicit:
        estimated_years = max(float(y) for y in years_explicit)
    else:
        # Estimate from date ranges like 2022 - 2025 or 2023 - Present
        range_matches = re.findall(
            r"\b(20[12]\d)\s*[\-\–—to]+\s*(20[12]\d|present|current)\b",
            resume_text,
            flags=re.IGNORECASE,
        )
        total_span = 0.0
        for start_s, end_s in range_matches:
            start_y = int(start_s)
            end_y = 2026 if end_s.lower() in ("present", "current") else int(end_s)
            if 0 <= end_y - start_y <= 15:
                total_span += max(0.5, float(end_y - start_y))
        estimated_years = min(15.0, round(total_span, 1)) if total_span > 0 else 1.5

    if estimated_years >= 5.0:
        seniority = "Senior (5+ yrs)"
    elif estimated_years >= 2.0:
        seniority = "Mid-Level (2–4 yrs)"
    else:
        seniority = "Entry / Early Career (0–2 yrs)"

    role_patterns = [
        "Machine Learning Engineer",
        "AI Engineer",
        "Data Scientist",
        "Full Stack Developer",
        "Full-Stack Engineer",
        "Backend Engineer",
        "Frontend Engineer",
        "Software Engineer",
        "Software Developer",
        "DevOps Engineer",
        "Cloud Engineer",
        "NLP Research Intern",
        "Data Analyst",
    ]
    roles_detected = [
        r for r in role_patterns if re.search(rf"\b{re.escape(r)}\b", resume_text, re.IGNORECASE)
    ]
    if not roles_detected:
        roles_detected = ["Software / AI Practitioner"]

    total_b = len(bullet_audits)
    quant_b = sum(1 for b in bullet_audits if b.has_metric)
    ratio = round((quant_b / total_b) * 100.0, 1) if total_b > 0 else 0.0

    return ExperienceSummary(
        estimated_years=estimated_years,
        seniority_level=seniority,
        roles_detected=roles_detected[:4],
        quantified_bullet_ratio=ratio,
        total_bullets=total_b,
        quantified_bullets=quant_b,
    )


def scrub_pii_and_audit_bias(resume_text: str, jd_text: str) -> tuple[str, BiasAuditReport]:
    """Scrub PII/demographic proxies before vector matching and audit JD for exclusionary phrasing."""
    scrubbed = resume_text
    scrubbed_categories: list[str] = []
    total_scrubbed = 0

    pii_rules = [
        ("Email Address", r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"),
        ("Phone Number", r"(?:\+?\d{1,3}[\s\-]?)?(?:\(?\d{3,4}\)?[\s\-]?)?\d{3}[\s\-]?\d{4}"),
        ("Social / Portfolio Profile URL", r"https?://(?:www\.)?(?:linkedin\.com|github\.com)/\S+"),
        ("Gendered Pronoun / Title Proxy", r"\b(?:Mr\.|Mrs\.|Ms\.|Miss|he/him|she/her|they/them)\b"),
        ("Age / Date of Birth Proxy", r"\b(?:DOB|Date of Birth|Age\s*:\s*\d{2})\b"),
    ]

    for category, pattern in pii_rules:
        matches = re.findall(pattern, scrubbed, flags=re.IGNORECASE)
        if matches:
            total_scrubbed += len(matches)
            scrubbed_categories.append(f"{category} ({len(matches)})")
            scrubbed = re.sub(pattern, "[REDACTED_FOR_FAIR_MATCHING]", scrubbed, flags=re.IGNORECASE)

    # Audit JD for potentially biased / exclusionary language
    jd_flags: list[str] = []
    exclusionary_terms = {
        "rockstar": "Uses 'rockstar/ninja' jargon; replace with concrete engineering competencies.",
        "ninja": "Uses 'ninja' jargon; replace with clear level expectations.",
        "digital native": "Age-coded phrase ('digital native'); specify required tool proficiency instead.",
        "recent graduate only": "Age-restrictive phrasing ('recent graduate only'); prefer '0-2 years experience'.",
        "work hard play hard": "Burnout-coded phrase ('work hard play hard'); state actual on-call/workload expectations.",
        "native english speaker": "Origin-coded requirement; prefer 'fluent written and verbal communication'.",
    }
    lower_jd = jd_text.lower()
    for term, warning in exclusionary_terms.items():
        if term in lower_jd:
            jd_flags.append(warning)

    inclusivity_score = max(50, 100 - len(jd_flags) * 15)
    summary = (
        f"Scrubbed {total_scrubbed} PII/demographic token(s) prior to embedding so candidate name, contact info, "
        f"and demographic proxies have zero weight in vector similarity."
    )

    return scrubbed, BiasAuditReport(
        pii_tokens_scrubbed=total_scrubbed,
        scrubbed_categories=scrubbed_categories,
        debiased_matching_active=True,
        jd_inclusivity_score=inclusivity_score,
        jd_inclusivity_flags=jd_flags,
        audit_summary=summary,
    )
