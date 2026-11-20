import re
import json
from typing import Dict, Any, List

RUBRIC_CATEGORIES = [
    {"key": "clarity_structure", "name": "Clarity & Structure",
     "description": "How clean, readable, and well-organized your resume is"},
    {"key": "role_level_positioning", "name": "Role & Level Positioning",
     "description": "Does your resume clearly communicate your role and seniority"},
    {"key": "impact_achievements", "name": "Impact & Achievements",
     "description": "How strongly your resume communicates business and technical impact"},
    {"key": "skills_relevance", "name": "Skills & Relevance",
     "description": "Depth and clarity of skillset for your target role"},
    {"key": "career_trajectory", "name": "Career Trajectory",
     "description": "Does your resume tell a coherent career story"},
    {"key": "language_professionalism", "name": "Language & Professionalism",
     "description": "Writing quality, grammar and professional tone"},
    {"key": "ats_formatting_hygiene", "name": "ATS & Formatting Hygiene",
     "description": "Is your resume ATS compliant and structurally simple"},
]

SENIORITY_WORDS = {
    "senior", "lead", "principal", "staff", "architect", "manager", "director",
    "head", "vp", "vice president", "chief", "founder", "co-founder"
}

ACTION_VERB_START = re.compile(
    r"^(accelerated|accomplished|achieved|acquired|adapted|administered|advanced|analyzed|"
    r"architected|automated|built|boosted|calculated|centralized|championed|collaborated|"
    r"constructed|converted|created|customized|debugged|delivered|deployed|designed|"
    r"developed|devised|diagnosed|directed|discovered|doubled|drove|engineered|enhanced|"
    r"established|evaluated|executed|expanded|expedited|fabricated|facilitated|forecasted|"
    r"formulated|founded|generated|guided|handled|headed|identified|implemented|improved|"
    r"increased|initiated|innovated|inspected|installed|instituted|instructed|integrated|"
    r"introduced|invented|investigated|launched|led|leveraged|managed|maximized|mentored|"
    r"migrated|minimized|modernized|monitored|motivated|negotiated|optimized|orchestrated|"
    r"organized|overhauled|oversaw|partnered|performed|pioneered|planned|prepared|produced|"
    r"programmed|promoted|proposed|published|rebuilt|reconciled|redesigned|reduced|refactored|"
    r"refined|reformed|remodeled|reorganized|replaced|researched|resolved|restructured|"
    r"revamped|scaled|scheduled|secured|selected|simplified|solved|spearheaded|standardized|"
    r"streamlined|strengthened|structured|supervised|surpassed|synthesized|systematized|"
    r"targeted|trained|transformed|transitioned|translated|tripled|uncovered|unified|"
    r"upgraded|utilized|validated|yielded)\b",
    re.I,
)

METRIC_REGEX = re.compile(
    r'(?:\d+%\s*|\$\s*[\d,]+|\b\d+(?:\.\d+)?(?:k|m|b|\+)?\b|\b(?:reduced|increased|improved|saved|boosted)\b)',
    re.I,
)


def _clamp10(x: float) -> int:
    return max(1, min(10, round(x)))


def _all_bullets(experience: List[Dict[str, Any]]) -> List[str]:
    bullets = []
    for exp in experience:
        bullets.extend(exp.get("bullets", []) or [])
    return bullets


def _score_clarity_structure(ats_json: Dict[str, Any], hygiene: Dict[str, Any]) -> Dict[str, Any]:
    strengths, improvements = [], []
    score = 10.0

    present = []
    for key, label in [("professional_summary", "Summary"), ("work_experience", "Experience"),
                        ("education", "Education")]:
        if ats_json.get(key):
            present.append(label)
    if ats_json.get("skills", {}).get("categories"):
        present.append("Skills")

    if len(present) >= 3:
        strengths.append(f"Standard sections present ({', '.join(present)}) in a scannable order.")
    else:
        score -= 2.5
        improvements.append("Several standard sections (Summary, Skills, Experience, Education) are missing or not clearly headed.")

    bullets = _all_bullets(ats_json.get("work_experience", []))
    if bullets:
        long_bullets = [b for b in bullets if len(b) > 180]
        long_ratio = len(long_bullets) / len(bullets)
        if long_ratio > 0.25:
            score -= 2.0
            improvements.append(f"{len(long_bullets)} of {len(bullets)} bullets are dense/long (>180 chars); break these up to improve scannability.")
        else:
            strengths.append("Most bullets are a scannable length with consistent formatting.")

    if not improvements:
        improvements.append("Keep formatting consistent across every section (same bullet style, spacing, date format).")

    return {"score": _clamp10(score), "strengths": strengths or ["Resume reads cleanly overall."], "improvements": improvements}


def _score_role_level_positioning(ats_json: Dict[str, Any]) -> Dict[str, Any]:
    strengths, improvements = [], []
    score = 6.0
    summary = (ats_json.get("professional_summary") or "").lower()
    latest_title = ""
    experience = ats_json.get("work_experience", [])
    if experience:
        latest_title = (experience[0].get("title") or "").lower()

    has_years = bool(re.search(r'\b\d{1,2}\+?\s*years?\b', summary))
    has_seniority_word = any(w in summary or w in latest_title for w in SENIORITY_WORDS)

    if has_years:
        score += 1.5
        strengths.append("Summary states years of experience, giving recruiters an immediate seniority signal.")
    else:
        improvements.append("Summary doesn't state total years of experience; add this near the top.")

    if has_seniority_word:
        score += 1.5
        strengths.append("Seniority/role-level language (e.g. Senior, Lead, Manager, Architect) is clearly present.")
    else:
        score -= 1.0
        improvements.append("Summary/title lacks a crisp seniority signal (e.g. 'Senior', 'Lead', 'Principal').")

    if len(experience) >= 2:
        titles = [e.get("title", "") for e in experience if e.get("title")]
        if len(set(t.lower() for t in titles)) > 1:
            strengths.append("Title progression across roles is visible, suggesting career growth.")

    return {"score": _clamp10(score), "strengths": strengths or ["Role is identifiable from the resume."], "improvements": improvements or ["Make the target role/level even more explicit in the headline."]}


def _score_impact_achievements(ats_json: Dict[str, Any], hygiene: Dict[str, Any]) -> Dict[str, Any]:
    strengths, improvements = [], []
    bullets = _all_bullets(ats_json.get("work_experience", []))
    total = len(bullets) or 1
    quantified = sum(1 for b in bullets if METRIC_REGEX.search(b))
    ratio = quantified / total
    score = 3.0 + ratio * 7.0

    if quantified > 0:
        strengths.append(f"{quantified} of {len(bullets)} bullets cite a measurable result (%, $, time, or scale).")
    if ratio < 0.4:
        unquantified = len(bullets) - quantified
        improvements.append(f"{unquantified} of {len(bullets)} bullets are duty statements with no outcome attached — add a measurable result to each.")
    else:
        strengths.append("Majority of bullets communicate outcomes, not just duties.")

    if not strengths:
        strengths.append("Experience section is present.")
    if not improvements:
        improvements.append("Keep pushing for a number in every bullet (%, $, time saved, users, scale).")

    return {"score": _clamp10(score), "strengths": strengths, "improvements": improvements}


def _score_skills_relevance(ats_json: Dict[str, Any]) -> Dict[str, Any]:
    strengths, improvements = [], []
    skills_cat = ats_json.get("skills", {}).get("categories", {}) or {}
    all_skills = ats_json.get("skills", {}).get("all_keywords", []) or []
    bullets_text = " ".join(_all_bullets(ats_json.get("work_experience", []))).lower()
    summary_text = (ats_json.get("professional_summary") or "").lower()
    searchable = bullets_text + " " + summary_text

    score = 5.0
    if len(skills_cat) >= 3:
        score += 1.5
        strengths.append(f"Skills are organized into {len(skills_cat)} logical categories.")
    elif skills_cat:
        improvements.append("Skills section exists but isn't broken into categories (e.g. Languages, Cloud, Databases).")
    else:
        score -= 2.0
        improvements.append("No categorized Skills section detected.")

    if all_skills:
        evidenced = [s for s in all_skills if s.lower() in searchable]
        evidenced_ratio = len(evidenced) / len(all_skills)
        if evidenced_ratio >= 0.4:
            score += 1.5
            strengths.append(f"{len(evidenced)} of {len(all_skills)} listed skills are also demonstrated in experience bullets.")
        else:
            unevidenced = [s for s in all_skills if s not in evidenced][:5]
            improvements.append(f"Some skills aren't evidenced anywhere in your bullets (e.g. {', '.join(unevidenced)}) — mention them in context or remove them.")

    return {"score": _clamp10(score), "strengths": strengths or ["Skills section present."], "improvements": improvements or ["Keep skills current with your target role."]}


def _score_career_trajectory(ats_json: Dict[str, Any]) -> Dict[str, Any]:
    strengths, improvements = [], []
    experience = ats_json.get("work_experience", [])
    score = 6.0

    if len(experience) >= 2:
        score += 1.0
        strengths.append(f"Career shows {len(experience)} roles, giving a visible progression to evaluate.")
    elif len(experience) == 1:
        improvements.append("Only one role is listed — add earlier experience if relevant to show trajectory.")
    else:
        score -= 3.0
        improvements.append("No work experience entries were detected.")

    companies = [e.get("company", "") for e in experience if e.get("company")]
    if len(set(c.lower() for c in companies)) == len(companies) and companies:
        strengths.append("Domain/company focus is consistent and easy to follow.")

    undated = [e for e in experience if not e.get("dates")]
    if undated:
        score -= 1.0
        improvements.append(f"{len(undated)} role(s) are missing clear dates — add a start/end date (or 'Present') to each.")

    return {"score": _clamp10(score), "strengths": strengths or ["Career history is present."], "improvements": improvements or ["Explain any employment gaps briefly if they exist."]}


def _score_language_professionalism(ats_json: Dict[str, Any]) -> Dict[str, Any]:
    strengths, improvements = [], []
    bullets = _all_bullets(ats_json.get("work_experience", []))
    score = 7.0

    active_count = sum(1 for b in bullets if ACTION_VERB_START.match(b.strip()))
    total = len(bullets) or 1
    active_ratio = active_count / total
    if active_ratio >= 0.7:
        strengths.append(f"Consistent active voice — {active_count} of {len(bullets)} bullets open with a strong action verb.")
    else:
        score -= 1.5
        improvements.append("Several bullets don't open with a strong action verb; standardize on active voice throughout.")

    # Cheap duplicate-word / typo-ish signal: a word immediately repeated.
    dup_word_hits = 0
    for b in bullets:
        if re.search(r'\b(\w+)\s+\1\b', b, re.I):
            dup_word_hits += 1
    if dup_word_hits:
        score -= 1.5
        improvements.append(f"Found {dup_word_hits} bullet(s) with an immediately repeated word — proofread for typos.")
    else:
        strengths.append("No obvious repeated-word typos detected in experience bullets.")

    if not improvements:
        improvements.append("Have a second person proofread for tone consistency and subtle grammar issues.")

    return {"score": _clamp10(score), "strengths": strengths, "improvements": improvements}


def _score_ats_formatting_hygiene(hygiene: Dict[str, Any]) -> Dict[str, Any]:
    score = _clamp10((hygiene.get("score", 70) or 70) / 10.0)
    strengths = list(hygiene.get("strengths", []))[:4] or ["No major ATS formatting red flags detected."]
    improvements = list(hygiene.get("warnings", []))[:4] or list(hygiene.get("suggestions", []))[:4]
    if not improvements:
        improvements = ["Keep using a single-column layout with no tables, text boxes, or images."]
    return {"score": score, "strengths": strengths, "improvements": improvements}


def audit_resume_rubric_heuristic(resume_data: Dict[str, Any]) -> Dict[str, Any]:
    ats_json = resume_data.get("ats_json", {}) or {}
    hygiene = resume_data.get("hygiene_report", {}) or {}

    scorers = {
        "clarity_structure": _score_clarity_structure(ats_json, hygiene),
        "role_level_positioning": _score_role_level_positioning(ats_json),
        "impact_achievements": _score_impact_achievements(ats_json, hygiene),
        "skills_relevance": _score_skills_relevance(ats_json),
        "career_trajectory": _score_career_trajectory(ats_json),
        "language_professionalism": _score_language_professionalism(ats_json),
        "ats_formatting_hygiene": _score_ats_formatting_hygiene(hygiene),
    }

    categories = []
    for cat in RUBRIC_CATEGORIES:
        result = scorers[cat["key"]]
        categories.append({
            "key": cat["key"],
            "name": cat["name"],
            "description": cat["description"],
            "score": result["score"],
            "strengths": result["strengths"],
            "improvements": result["improvements"],
        })

    overall = round(sum(c["score"] for c in categories) / len(categories), 1)

    return {
        "overall_score": overall,
        "categories": categories,
        "source": "Local Heuristic Engine",
    }


async def audit_resume_rubric_async(resume_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Produces the 7-category rubric score. Uses the local heuristic engine as a
    baseline, and overrides with a richer LLM pass when a provider is configured
    (same fallback pattern as generate_resume_suggestions_async).
    """
    local_result = audit_resume_rubric_heuristic(resume_data)

    from app.analyzer.llm_client import call_active_llm
    from app.database import get_active_provider

    active_provider = get_active_provider()
    if not active_provider:
        return local_result

    raw_resume = resume_data.get("ats_json", {}).get("raw_text", "")
    category_list = "\n".join(f"- {c['key']}: {c['name']} — {c['description']}" for c in RUBRIC_CATEGORIES)

    prompt = f"""You are an expert resume reviewer and ATS specialist. Score this resume against exactly these 7 categories:
{category_list}

Resume text:
{raw_resume[:4000]}

Return ONLY valid JSON matching this exact structure (score is an integer 1-10 for each category):
{{
  "categories": {{
    "clarity_structure": {{"score": 7, "strengths": ["...", "..."], "improvements": ["...", "..."]}},
    "role_level_positioning": {{"score": 7, "strengths": ["...", "..."], "improvements": ["...", "..."]}},
    "impact_achievements": {{"score": 7, "strengths": ["...", "..."], "improvements": ["...", "..."]}},
    "skills_relevance": {{"score": 7, "strengths": ["...", "..."], "improvements": ["...", "..."]}},
    "career_trajectory": {{"score": 7, "strengths": ["...", "..."], "improvements": ["...", "..."]}},
    "language_professionalism": {{"score": 7, "strengths": ["...", "..."], "improvements": ["...", "..."]}},
    "ats_formatting_hygiene": {{"score": 7, "strengths": ["...", "..."], "improvements": ["...", "..."]}}
  }}
}}
Give 2-3 specific, concrete strengths and improvements per category, referencing actual content from the resume. No preamble, no markdown codeblocks."""

    system_prompt = "You are an expert resume reviewer. You always respond with strict JSON only."
    llm_resp = await call_active_llm(prompt, system_prompt)

    if llm_resp:
        try:
            clean_json = re.sub(r'^```(?:json)?\s*', '', llm_resp.strip(), flags=re.I)
            clean_json = re.sub(r'\s*```$', '', clean_json).strip()
            parsed = json.loads(clean_json)
            llm_categories = parsed.get("categories", {})

            if llm_categories:
                merged = []
                for cat in RUBRIC_CATEGORIES:
                    llm_cat = llm_categories.get(cat["key"])
                    if llm_cat and "score" in llm_cat:
                        merged.append({
                            "key": cat["key"],
                            "name": cat["name"],
                            "description": cat["description"],
                            "score": _clamp10(llm_cat.get("score", 5)),
                            "strengths": llm_cat.get("strengths") or ["No specific strengths returned."],
                            "improvements": llm_cat.get("improvements") or ["No specific improvements returned."],
                        })
                    else:
                        # Fall back to the heuristic result for this one category.
                        merged.append(next(c for c in local_result["categories"] if c["key"] == cat["key"]))

                overall = round(sum(c["score"] for c in merged) / len(merged), 1)
                return {
                    "overall_score": overall,
                    "categories": merged,
                    "source": f"LLM ({active_provider.get('name')}: {active_provider.get('model_name')})",
                }
        except Exception:
            pass

    local_result["source"] = "Local Heuristic Engine (Offline / Fallback)"
    return local_result
