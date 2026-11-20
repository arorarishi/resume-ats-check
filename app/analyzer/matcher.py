import re
import json
from typing import Dict, Any, List, Set

# Related skill clusters for partial matching
SKILL_FAMILIES = {
    "sql": {"sql", "postgresql", "postgres", "mysql", "sqlite", "mariadb", "oracle"},
    "nosql": {"mongodb", "cassandra", "dynamodb", "redis", "elasticsearch"},
    "cloud": {"aws", "azure", "gcp", "google cloud"},
    "containerization": {"docker", "kubernetes", "k8s", "helm"},
    "frontend": {"react", "react.js", "vue", "vue.js", "angular", "next.js", "typescript", "javascript"},
    "python_ml": {"python", "pytorch", "tensorflow", "scikit-learn", "keras", "pandas", "numpy", "bert", "transformers"},
    "ci_cd": {"ci/cd", "jenkins", "gitlab ci", "github actions", "devops"},
    "api": {"rest api", "graphql", "grpc", "microservices"}
}

def find_partial_match(skill_lower: str, resume_skills_set: Set[str]) -> bool:
    for _, family in SKILL_FAMILIES.items():
        if skill_lower in family:
            overlap = family.intersection(resume_skills_set)
            if overlap:
                return True
    return False

def compare_resume_to_jd(resume_data: Dict[str, Any], jd_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Compares ATS parsed resume data against parsed JD.
    Produces Match Score and detailed Side-by-Side Skill Matrix with ready-to-copy bullet suggestions.
    """
    ats_json = resume_data.get("ats_json", {})
    resume_skills_cat = ats_json.get("skills", {}).get("categories", {})
    raw_resume_text = ats_json.get("raw_text", "")

    # Support Master Resume schema if ats_json is not present
    if not resume_skills_cat and "skills" in resume_data:
        sk = resume_data["skills"]
        if isinstance(sk, dict):
            resume_skills_cat = sk
    if not raw_resume_text:
        raw_resume_text = resume_data.get("raw_text", "")
    if not raw_resume_text:
        try:
            from app.database import build_raw_master_text
            raw_resume_text = build_raw_master_text(resume_data)
        except Exception:
            raw_resume_text = ""

    resume_text_lower = raw_resume_text.lower()

    # Build flat set of candidate skills
    candidate_skills = set()
    if isinstance(resume_skills_cat, dict):
        for cat_list in resume_skills_cat.values():
            if isinstance(cat_list, list):
                for s in cat_list:
                    candidate_skills.add(str(s).lower())
    elif isinstance(resume_skills_cat, list):
        for s in resume_skills_cat:
            candidate_skills.add(str(s).lower())

    must_haves = jd_data.get("must_have_skills", [])
    nice_to_haves = jd_data.get("nice_to_have_skills", [])
    all_jd_skills_by_cat = jd_data.get("skills_by_category", {})
    detailed_reqs = jd_data.get("detailed_requirements", [])

    side_by_side_matrix = []
    matched_must = []
    partial_must = []
    missing_must = []

    matched_nice = []
    partial_nice = []
    missing_nice = []

    seen_skills = set()

    def find_context_snippet(skill_str: str) -> str:
        lines = raw_resume_text.split("\n")
        words = [w.lower() for w in re.findall(r'\b[a-zA-Z0-9_-]{3,}\b', skill_str)]
        for line in lines:
            line_l = line.lower()
            if any(w in line_l for w in words[:3]):
                cleaned = line.strip()
                return cleaned[:80] + "..." if len(cleaned) > 80 else cleaned
        return "Mentioned in skills summary"

    def make_google_xyz_bullet(skill_text: str) -> str:
        return f"Engineered scalable solutions incorporating {skill_text.rstrip('.')}, optimizing operational throughput by 35% and accelerating deployment velocity."

    # 1. Process structured skills by category
    for category, skills in all_jd_skills_by_cat.items():
        for skill in skills:
            skill_lower = skill.lower()
            seen_skills.add(skill_lower)
            priority = "Must-Have" if skill in must_haves else "Nice-to-Have"

            is_exact = skill_lower in candidate_skills or re.search(r'(?<![a-zA-Z0-9])' + re.escape(skill_lower) + r'(?![a-zA-Z0-9])', resume_text_lower)

            if is_exact:
                match_status = "Exact Match"
                context = find_context_snippet(skill)
                advice = "Strong keyword match. Ensure bullet points demonstrate impact with this skill."
                bullet = make_google_xyz_bullet(skill)
                if priority == "Must-Have":
                    matched_must.append(skill)
                else:
                    matched_nice.append(skill)
            else:
                is_partial = find_partial_match(skill_lower, candidate_skills)
                if is_partial:
                    match_status = "Partial Match"
                    context = "Related experience found in candidate skill cluster"
                    advice = f"You possess related technologies. Explicitly add '{skill}' to your skills list."
                    bullet = make_google_xyz_bullet(skill)
                    if priority == "Must-Have":
                        partial_must.append(skill)
                    else:
                        partial_nice.append(skill)
                else:
                    match_status = "Missing"
                    context = "Not detected in resume text"
                    advice = f"Critical missing keyword for ATS filtering. Incorporate this skill into your experience."
                    bullet = make_google_xyz_bullet(skill)
                    if priority == "Must-Have":
                        missing_must.append(skill)
                    else:
                        missing_nice.append(skill)

            side_by_side_matrix.append({
                "skill": skill,
                "category": category,
                "priority": priority,
                "status": match_status,
                "resume_context": context,
                "advice": advice,
                "suggested_bullet": bullet
            })

    # 2. Also process detailed requirements / phrases from JD (e.g. "- Knowledge of Classification, Q&A networks using BERT")
    for req in detailed_reqs:
        req_text = req.get("text", "").strip()
        req_priority = req.get("priority", "Must-Have")
        if not req_text or any(s in req_text.lower() for s in seen_skills if len(s) > 15):
            continue

        # Check match against resume text
        req_words = [w.lower() for w in re.findall(r'\b[a-zA-Z0-9_-]{3,}\b', req_text)]
        matches_found = [w for w in req_words if w in resume_text_lower]
        coverage = len(matches_found) / (len(req_words) or 1)

        if coverage >= 0.6:
            status = "Exact Match"
            context = find_context_snippet(req_text)
            advice = "Demonstrated in resume. Emphasize quantifiable metrics and scope."
            if req_priority == "Must-Have":
                matched_must.append(req_text[:30])
            else:
                matched_nice.append(req_text[:30])
        elif coverage >= 0.25:
            status = "Partial Match"
            context = "Some related terms found in resume text"
            advice = "You have related experience. Bridge the gap by adding exact phrasing to projects."
            if req_priority == "Must-Have":
                partial_must.append(req_text[:30])
            else:
                partial_nice.append(req_text[:30])
        else:
            status = "Missing"
            context = "Not detected in resume text"
            advice = "Explicitly demonstrate this qualification in your experience or personal projects."
            if req_priority == "Must-Have":
                missing_must.append(req_text[:30])
            else:
                missing_nice.append(req_text[:30])

        side_by_side_matrix.append({
            "skill": req_text,
            "category": "Requirements & Qualifications",
            "priority": req_priority,
            "status": status,
            "resume_context": context,
            "advice": advice,
            "suggested_bullet": make_google_xyz_bullet(req_text)
        })

    # Sort matrix: Must-Haves first, Missing / Partial on top
    status_order = {"Missing": 0, "Partial Match": 1, "Exact Match": 2}
    priority_order = {"Must-Have": 0, "Nice-to-Have": 1}
    side_by_side_matrix.sort(key=lambda x: (priority_order.get(x["priority"], 9), status_order.get(x["status"], 9), x["skill"]))

    # Match Score Calculation
    total_must = len(matched_must) + len(partial_must) + len(missing_must) or 1
    total_nice = len(matched_nice) + len(partial_nice) + len(missing_nice) or 1

    must_score = (len(matched_must) * 1.0 + len(partial_must) * 0.5) / total_must
    nice_score = (len(matched_nice) * 1.0 + len(partial_nice) * 0.5) / total_nice

    exp_bonus = 0.85
    if jd_data.get("seniority") == "Senior / Lead":
        if any(w in resume_text_lower for w in ["senior", "lead", "architect", "managed", "headed"]):
            exp_bonus = 1.0
        else:
            exp_bonus = 0.65

    raw_score = (must_score * 60.0) + (nice_score * 20.0) + (exp_bonus * 20.0)
    match_score = round(max(15.0, min(99.0, raw_score)), 1)
    top_missing_keywords = missing_must + missing_nice

    candidate_bonus_skills = []
    for cat, skills in resume_skills_cat.items():
        for s in skills:
            if s.lower() not in [x.lower() for x in jd_data.get("must_have_skills", []) + jd_data.get("nice_to_have_skills", [])]:
                candidate_bonus_skills.append(s)

    return {
        "match_score": match_score,
        "score_tier": "Excellent Match" if match_score >= 80 else "Good Match" if match_score >= 65 else "Moderate Match" if match_score >= 50 else "Low Match",
        "summary_counts": {
            "total_jd_skills": len(side_by_side_matrix),
            "exact_matches": len(matched_must) + len(matched_nice),
            "partial_matches": len(partial_must) + len(partial_nice),
            "missing_skills": len(missing_must) + len(missing_nice),
            "must_haves_covered": f"{len(matched_must)}/{total_must}",
            "nice_to_haves_covered": f"{len(matched_nice)}/{total_nice}"
        },
        "side_by_side_matrix": side_by_side_matrix,
        "top_missing_keywords": top_missing_keywords[:12],
        "candidate_bonus_skills": sorted(list(set(candidate_bonus_skills)))[:15],
        "role_matched": jd_data.get("role_title", ""),
        "company_matched": jd_data.get("company", ""),
        "source": "Local Heuristic Engine"
    }

async def compare_resume_to_jd_async(resume_data: Dict[str, Any], jd_data: Dict[str, Any], jd_raw_text: str = "") -> Dict[str, Any]:
    """
    Uses active LLM to evaluate ALL requirements and domain skills from the JD.
    Falls back to enhanced local matcher if no active provider or on timeout/error.
    """
    from app.database import get_active_provider
    from app.analyzer.llm_client import call_active_llm

    active_provider = get_active_provider()
    local_comparison = compare_resume_to_jd(resume_data, jd_data)

    if not active_provider:
        local_comparison["source"] = "Local Heuristic Engine"
        return local_comparison

    ats_json = resume_data.get("ats_json", {})
    raw_resume = ats_json.get("raw_text") or resume_data.get("raw_text", "")
    if not raw_resume:
        try:
            from app.database import build_raw_master_text
            raw_resume = build_raw_master_text(resume_data)
        except Exception:
            raw_resume = ""
    target_role = jd_data.get("role_title", "Target Role")
    target_company = jd_data.get("company", "Target Company")

    prompt = f"""You are an expert ATS recruitment auditor and technical evaluation AI.
Perform an exhaustive, point-by-point requirement analysis between this Job Description and Candidate Resume.

CRITICAL INSTRUCTIONS:
1. Extract EVERY SINGLE requirement, qualification, technology, domain skill, and key responsibility mentioned in the Job Description.
   - Do NOT reduce requirements to single keywords! Capture complete requirement statements (e.g. "Knowledge of Classification, Q&A networks using BERT", "Experience with low-latency inference pipelines", "Designing distributed microservices in Go or Python", etc.).
2. For EACH requirement, cross-reference the candidate's resume:
   - "skill": The exact requirement or skill statement from the JD.
   - "category": Logical category (e.g. "Core AI & NLP", "Cloud & Infrastructure", "Backend Architecture", "Databases", "Methodologies & Tools", "Soft Skills").
   - "priority": "Must-Have" or "Nice-to-Have".
   - "status": "Exact Match" (if clearly demonstrated in resume), "Partial Match" (if related/transferable skills exist), or "Missing" (if not in resume).
   - "resume_context": Quote or summary of resume evidence, or "Not mentioned in resume".
   - "advice": Strategic explanation of why this gap exists and how to address it.
   - "suggested_bullet": A ready-to-use, powerful bullet point following the Google XYZ formula: "Accomplished [X], as measured by [Y], by doing [Z]" specifically demonstrating this requirement!
3. Calculate an overall ATS Match Score (0.0 to 100.0) reflecting the real qualification match.
4. Identify top missing keywords and candidate bonus skills.

Return JSON in this EXACT schema:
{{
  "match_score": 85.0,
  "score_tier": "Excellent Match",
  "summary_counts": {{
    "total_jd_skills": 16,
    "exact_matches": 10,
    "partial_matches": 3,
    "missing_skills": 3,
    "must_haves_covered": "8/10",
    "nice_to_haves_covered": "5/6"
  }},
  "side_by_side_matrix": [
    {{
      "skill": "Knowledge of Classification, Q&A networks using BERT",
      "category": "Core AI & NLP",
      "priority": "Must-Have",
      "status": "Missing",
      "resume_context": "Not mentioned in resume text",
      "advice": "Essential NLP requirement. Explicitly incorporate BERT transformer fine-tuning for intent classification or QA.",
      "suggested_bullet": "Architected deep learning classification and Q&A pipelines fine-tuning BERT transformers with PyTorch, boosting query comprehension accuracy by 28% across 5M customer queries."
    }}
  ],
  "top_missing_keywords": ["BERT Classification", "Q&A Networks"],
  "candidate_bonus_skills": ["Docker", "TypeScript"],
  "role_matched": "{target_role}",
  "company_matched": "{target_company}"
}}

JOB DESCRIPTION:
{jd_raw_text[:3500]}

CANDIDATE RESUME:
{raw_resume[:3500]}

Output ONLY valid JSON. No conversational preamble, no markdown codeblocks."""

    system_prompt = "You are an elite ATS recruitment engine and technical resume analyzer."
    llm_resp = await call_active_llm(prompt, system_prompt)

    if llm_resp:
        try:
            json_match = re.search(r'(\{[\s\S]*\})', llm_resp)
            raw_to_parse = json_match.group(1) if json_match else llm_resp.strip()
            raw_to_parse = re.sub(r'^```(?:json)?\s*', '', raw_to_parse, flags=re.I)
            raw_to_parse = re.sub(r'\s*```$', '', raw_to_parse).strip()
            parsed = json.loads(raw_to_parse)

            if "side_by_side_matrix" in parsed and len(parsed["side_by_side_matrix"]) > 0:
                parsed["source"] = f"AI Provider: {active_provider.get('name')} ({active_provider.get('model_name')})"
                # Ensure all UI expected fields are populated
                if "match_score" not in parsed:
                    parsed["match_score"] = local_comparison["match_score"]
                if "score_tier" not in parsed:
                    parsed["score_tier"] = local_comparison["score_tier"]
                if "summary_counts" not in parsed:
                    parsed["summary_counts"] = local_comparison["summary_counts"]
                if "top_missing_keywords" not in parsed:
                    parsed["top_missing_keywords"] = local_comparison.get("top_missing_keywords", [])
                if "candidate_bonus_skills" not in parsed:
                    parsed["candidate_bonus_skills"] = local_comparison.get("candidate_bonus_skills", [])
                if "role_matched" not in parsed:
                    parsed["role_matched"] = target_role
                if "company_matched" not in parsed:
                    parsed["company_matched"] = target_company
                return parsed
        except Exception as e:
            print(f"[Matcher Parse Error]: {e}")
            pass

    local_comparison["source"] = "Local Heuristic Engine (Offline / Fallback)"
    return local_comparison
