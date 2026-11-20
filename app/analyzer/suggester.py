import re
import json
from typing import Dict, Any, List

def generate_resume_suggestions(resume_data: Dict[str, Any], jd_data: Dict[str, Any], comparison_data: Dict[str, Any]) -> Dict[str, Any]:
    ats_json = resume_data.get("ats_json", {})
    contact = ats_json.get("contact_information", {})
    summary = ats_json.get("professional_summary", "")
    experience = ats_json.get("work_experience", [])
    skills_cat = ats_json.get("skills", {}).get("categories", {})

    target_role = jd_data.get("role_title", "Software Engineer")
    target_company = jd_data.get("company", "the target company")
    missing_keywords = comparison_data.get("top_missing_keywords", [])
    seniority = jd_data.get("seniority", "Mid-Senior")

    # 1. SUMMARY SECTION SUGGESTION
    # Candidate strengths
    top_candidate_skills = []
    for s_list in skills_cat.values():
        top_candidate_skills.extend(s_list)
    top_skills_str = ", ".join(top_candidate_skills[:4]) if top_candidate_skills else "Full Stack & Cloud Technologies"

    # Injected missing keywords into summary
    summary_keywords = ", ".join(missing_keywords[:3]) if missing_keywords else "scalable software architectures"

    suggested_summary = (
        f"Results-driven {seniority} {target_role} with proven track record of designing and scaling robust systems using {top_skills_str}. "
        f"Experienced in cross-functional delivery, performance optimization, and integrating modern workflows with {summary_keywords}. "
        f"Eager to leverage deep technical expertise and problem-solving velocity to drive measurable impact for {target_company}."
    )

    summary_suggestions = {
        "current": summary or "[No dedicated professional summary found in resume]",
        "recommended": suggested_summary,
        "rationale": (
            "Recruiters and ATS parsers scan the first 3 lines for exact title alignment and key competencies. "
            f"Explicitly stating '{target_role}' and highlighting {summary_keywords} immediately boosts relevance."
        )
    }

    # 2. BULLET POINT & WORK EXPERIENCE REWRITES
    experience_suggestions = []
    action_verb_alternatives = ["Spearheaded", "Architected", "Engineered", "Orchestrated", "Accelerated", "Streamlined"]

    verb_idx = 0
    keyword_idx = 0

    for exp_idx, exp in enumerate(experience[:3]):
        role_title = exp.get("title", "Role")
        company = exp.get("company", "Company")
        bullets = exp.get("bullets", [])

        rewritten_bullets = []
        for b_idx, bullet in enumerate(bullets[:4]):
            has_metric = bool(re.search(r'\d+%|\$\d+|\b\d+\b', bullet))
            has_strong_verb = bool(re.match(r'^[A-Z][a-z]+ed\b', bullet))

            # Pick a missing keyword to incorporate if available
            injected_kw = missing_keywords[keyword_idx % len(missing_keywords)] if missing_keywords else "modern CI/CD pipelines"
            keyword_idx += 1
            verb = action_verb_alternatives[verb_idx % len(action_verb_alternatives)]
            verb_idx += 1

            # Build Google XYZ rewrite suggestion
            if not has_metric:
                rewritten = f"{verb} development of core modules utilizing {injected_kw}, improving processing throughput by 32% and reducing deployment cycle time."
                critique = "Lacks measurable impact and key JD technical skills. Rewritten using Google XYZ formula (Accomplished [X] measured by [Y] by doing [Z])."
            else:
                # Enhance existing bullet with missing keyword
                rewritten = f"{verb} {bullet.rstrip('.')} by leveraging {injected_kw}, ensuring high reliability and zero downtime."
                critique = f"Good baseline metric; enhanced with high-priority ATS keyword '{injected_kw}'."

            rewritten_bullets.append({
                "original": bullet,
                "suggested": rewritten,
                "critique": critique
            })

        experience_suggestions.append({
            "company": company,
            "title": role_title,
            "bullets": rewritten_bullets
        })

    # 3. SKILLS SECTION SUGGESTIONS
    skills_to_prioritize = jd_data.get("must_have_skills", [])
    skills_suggestions = {
        "priority_skills_to_feature": skills_to_prioritize[:8],
        "missing_keywords_to_add": missing_keywords,
        "recommendation": (
            "Organize your skills section into clear categories (e.g. Languages, Frameworks, Cloud & DevOps, Databases). "
            f"Place '{', '.join(skills_to_prioritize[:5])}' at the front of each respective group because ATS algorithms assign higher weight to skills appearing earlier."
        )
    }

    # 4. SECTION-BY-SECTION GENERAL AUDIT
    general_audit = [
        {
            "section": "Header & Contact Info",
            "status": "Pass" if contact.get("email") and contact.get("phone") else "Attention Required",
            "advice": "Ensure Phone, Professional Email, LinkedIn URL, and City/State are at the very top in simple text format (no tables or text boxes)."
        },
        {
            "section": "Job Title Matching",
            "status": "Recommendation",
            "advice": f"Align your current/latest title or headline to mirror '{target_role}' where truthful (e.g. '{target_role} | Senior Software Engineer')."
        },
        {
            "section": "Certifications & Education",
            "status": "Tip",
            "advice": "If the job description mentions specific certifications (e.g. AWS Solutions Architect, Kubernetes CKA) and you have them or are in-progress, place them in a dedicated 'Certifications' section."
        }
    ]

    return {
        "summary": summary_suggestions,
        "experience": experience_suggestions,
        "skills": skills_suggestions,
        "general_audit": general_audit
    }

async def generate_resume_suggestions_async(resume_data: Dict[str, Any], jd_data: Dict[str, Any], comparison_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generates suggestions with active LLM if configured; otherwise uses local heuristics.
    """
    local_result = generate_resume_suggestions(resume_data, jd_data, comparison_data)

    from app.analyzer.llm_client import call_active_llm
    from app.database import get_active_provider

    active_provider = get_active_provider()
    if not active_provider:
        local_result["source"] = "Local Heuristic Engine"
        return local_result

    target_role = jd_data.get("role_title", "")
    target_company = jd_data.get("company", "")
    missing_kws = comparison_data.get("top_missing_keywords", [])
    raw_resume = resume_data.get("ats_json", {}).get("raw_text", "")

    prompt = f"""You are an elite ATS Resume Optimization specialist.
Analyze this resume for the position of '{target_role}' at '{target_company}'.
Key missing ATS keywords: {', '.join(missing_kws[:6])}

Original Resume snippet:
{raw_resume[:1500]}

Provide your output in valid JSON matching this structure:
{{
  "tailored_summary": "A punchy 3-sentence professional summary directly aligned to {target_role} including missing keywords.",
  "summary_rationale": "Brief rationale for why this summary improves ATS ranking.",
  "rewritten_bullets": [
    {{
      "original": "original bullet",
      "rewritten": "Google XYZ rewritten bullet (Accomplished [X] measured by [Y] by doing [Z])",
      "critique": "Why this change is stronger"
    }}
  ]
}}
Only return the JSON. No preamble or markdown codeblocks."""

    system_prompt = "You are an expert ATS resume writer and recruiter."
    llm_resp = await call_active_llm(prompt, system_prompt)

    if llm_resp:
        try:
            # Clean possible markdown ticks
            clean_json = re.sub(r'^```(?:json)?\s*', '', llm_resp.strip(), flags=re.I)
            clean_json = re.sub(r'\s*```$', '', clean_json).strip()
            parsed = json.loads(clean_json)

            if "tailored_summary" in parsed:
                local_result["summary"]["recommended"] = parsed["tailored_summary"]
            if "summary_rationale" in parsed:
                local_result["summary"]["rationale"] = parsed["summary_rationale"]

            if "rewritten_bullets" in parsed and isinstance(parsed["rewritten_bullets"], list) and len(parsed["rewritten_bullets"]) > 0:
                # Merge into experience bullets
                llm_bullets = parsed["rewritten_bullets"]
                if local_result["experience"] and len(local_result["experience"]) > 0:
                    for i, lb in enumerate(llm_bullets[:4]):
                        if i < len(local_result["experience"][0]["bullets"]):
                            local_result["experience"][0]["bullets"][i]["suggested"] = lb.get("rewritten", local_result["experience"][0]["bullets"][i]["suggested"])
                            local_result["experience"][0]["bullets"][i]["critique"] = f"AI Generated: {lb.get('critique', '')}"

            local_result["source"] = f"LLM ({active_provider.get('name')}: {active_provider.get('model_name')})"
            return local_result
        except Exception:
            pass

    local_result["source"] = "Local Heuristic Engine (Offline / Fallback)"
    return local_result

