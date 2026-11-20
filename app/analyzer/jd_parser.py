import re
from typing import Dict, Any, List, Set
from app.parsers.ats_normalizer import KNOWN_SKILL_CATEGORIES

# Keywords signaling must-have vs nice-to-have sections
MUST_HAVE_HEADERS = [
    "requirements", "qualifications", "what you need", "what you'll need",
    "must have", "minimum qualifications", "basic qualifications", "essential"
]

NICE_TO_HAVE_HEADERS = [
    "preferred", "nice to have", "bonus", "plus", "desired", "what gives you an edge",
    "preferred qualifications", "good to have"
]

def parse_job_description(jd_text: str) -> Dict[str, Any]:
    lines = jd_text.split("\n")
    cleaned_lines = [l.strip() for l in lines if l.strip()]
    jd_lower = jd_text.lower()

    # 1. Heuristic for Job Title & Company
    role_title = ""
    company = ""
    for idx, line in enumerate(cleaned_lines[:8]):
        # Check for "Position:", "Job Title:", "Role:"
        title_match = re.search(r'(?:role|position|job\s*title)\s*[:\-]\s*(.+)', line, re.I)
        if title_match:
            role_title = title_match.group(1).strip()
            break
        # Or look for common title words
        if any(w in line.lower() for w in ["engineer", "developer", "architect", "scientist", "manager", "lead", "analyst", "specialist"]):
            if len(line.split()) <= 6:
                role_title = line
                break

    for line in cleaned_lines[:8]:
        comp_match = re.search(r'(?:company|at|organization)\s*[:\-]\s*(.+)', line, re.I)
        if comp_match:
            company = comp_match.group(1).strip()
            break

    # 2. Experience Level Detection
    exp_matches = re.findall(r'(\d{1,2}\s*(?:\+|-\s*\d{1,2})?\s*(?:years?|yrs?)(?:\s+of)?\s+experience)', jd_text, re.I)
    experience_req = exp_matches[0] if exp_matches else ""
    seniority = "Mid-Level"
    if any(w in jd_lower for w in ["senior", "sr.", "lead", "principal", "staff"]):
        seniority = "Senior / Lead"
    elif any(w in jd_lower for w in ["junior", "jr.", "entry level", "associate", "intern"]):
        seniority = "Entry Level / Junior"
    elif any(w in jd_lower for w in ["director", "head of", "vp", "chief"]):
        seniority = "Executive / Director"

    # 3. Education Requirements
    education_req = []
    if re.search(r'\b(?:bachelor|b\.?s\.?|b\.?e\.?|b\.?tech)\b', jd_lower):
        education_req.append("Bachelor's Degree")
    if re.search(r'\b(?:master|m\.?s\.?|m\.?tech|mba)\b', jd_lower):
        education_req.append("Master's Degree")
    if re.search(r'\b(?:phd|doctorate)\b', jd_lower):
        education_req.append("PhD")

    # 4. Extract Skills & Classify Must-Have vs Nice-to-Have
    must_have_skills: Set[str] = set()
    nice_to_have_skills: Set[str] = set()
    all_jd_skills: Dict[str, List[str]] = {}

    current_priority = "Must-Have"
    for line in cleaned_lines:
        lower_line = line.lower()
        if any(h in lower_line for h in NICE_TO_HAVE_HEADERS):
            current_priority = "Nice-to-Have"
        elif any(h in lower_line for h in MUST_HAVE_HEADERS):
            current_priority = "Must-Have"

        # Search for skills in this line
        line_pad = f" {lower_line} "
        for category, skill_list in KNOWN_SKILL_CATEGORIES.items():
            for skill in skill_list:
                pattern = r'(?<![a-zA-Z0-9])' + re.escape(skill) + r'(?![a-zA-Z0-9])'
                if re.search(pattern, line_pad):
                    formatted_skill = skill.title() if len(skill) > 3 and not skill.isupper() else skill.upper()
                    if skill in ["react", "react.js", "next.js", "node.js", "vue.js"]:
                        formatted_skill = skill

                    if category not in all_jd_skills:
                        all_jd_skills[category] = []
                    if formatted_skill not in all_jd_skills[category]:
                        all_jd_skills[category].append(formatted_skill)

                    if current_priority == "Must-Have":
                        must_have_skills.add(formatted_skill)
                    else:
                        nice_to_have_skills.add(formatted_skill)

    # Any skill in both defaults to Must-Have
    nice_to_have_skills = nice_to_have_skills - must_have_skills

    # Detailed requirement bullet items (captures full phrases like BERT, Q&A networks, etc.)
    detailed_requirements = []
    curr_req_priority = "Must-Have"
    for line in cleaned_lines:
        lower_line = line.lower()
        if any(h in lower_line for h in NICE_TO_HAVE_HEADERS):
            curr_req_priority = "Nice-to-Have"
        elif any(h in lower_line for h in MUST_HAVE_HEADERS):
            curr_req_priority = "Must-Have"

        is_item = line.startswith(("-", "*", "•", "–", "—", "·")) or (len(line) > 2 and line[0].isdigit() and line[1:3] in [". ", ") "])
        if is_item:
            cleaned_item = re.sub(r'^[-*•–—·\d\.\)\s]+', '', line).strip()
            if len(cleaned_item) > 10 and not any(h in cleaned_item.lower() for h in MUST_HAVE_HEADERS + NICE_TO_HAVE_HEADERS):
                detailed_requirements.append({
                    "text": cleaned_item,
                    "priority": curr_req_priority
                })

    # Key Responsibilities sample lines
    responsibilities = [
        re.sub(r'^[-*•–—\s]+', '', l)
        for l in cleaned_lines
        if (l.startswith(("-", "*", "•")) and len(l) > 30)
    ][:10]

    return {
        "role_title": role_title or "Software Professional",
        "company": company or "Hiring Organization",
        "experience_required": experience_req or "Not explicitly specified",
        "seniority": seniority,
        "education_required": education_req or ["Relevant Bachelor's or equivalent experience"],
        "skills_by_category": all_jd_skills,
        "must_have_skills": sorted(list(must_have_skills)),
        "nice_to_have_skills": sorted(list(nice_to_have_skills)),
        "detailed_requirements": detailed_requirements,
        "total_skills_detected": sum(len(v) for v in all_jd_skills.values()),
        "key_responsibilities": responsibilities
    }
