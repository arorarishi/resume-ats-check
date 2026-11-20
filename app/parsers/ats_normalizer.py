import re
from typing import Dict, Any, List, Optional

# Standard ATS Section Names Regex
SECTION_PATTERNS = {
    "summary": r"^(?:professional\s+summary|summary|objective|about\s+me|profile|career\s+profile)",
    "skills": r"^(?:technical\s+skills|skills\s*(?:&|and)?\s*technologies|core\s+competencies|skills|technologies|tools\s*&?\s*technologies)",
    "experience": r"^(?:work\s+experience|professional\s+experience|experience|employment\s+history|career\s+history)",
    "education": r"^(?:education|academic\s+background|educational\s+qualifications|academics)",
    "projects": r"^(?:projects|personal\s+projects|key\s+projects|technical\s+projects|academic\s+projects)",
    "certifications": r"^(?:certifications|licenses\s*&?\s*certifications|certificates|courses\s*&?\s*certifications)"
}

# Compound skills headers (e.g. "Core Competencies & Technical Skills", "Skills & Tools",
# "Key Skills", "Technical Proficiencies", "Areas of Expertise") don't match the exact
# phrases in SECTION_PATTERNS["skills"]. These fall back to a word-level check: a short
# line made up only of these words, with at least one "anchor" word, is a skills header.
SKILLS_HEADER_ANCHOR_WORDS = {
    "skill", "skills", "skillset", "competency", "competencies", "competence",
    "proficiency", "proficiencies", "expertise", "technology", "technologies",
    "tool", "tools", "stack",
}
SKILLS_HEADER_FILLER_WORDS = {"core", "key", "technical", "areas", "the", "of", "and"}


def _is_skills_header(lower_line: str) -> bool:
    tokens = [t for t in re.split(r"[\s/,:&-]+", lower_line) if t]
    if not tokens:
        return False
    known = SKILLS_HEADER_ANCHOR_WORDS | SKILLS_HEADER_FILLER_WORDS
    if not all(t in known for t in tokens):
        return False
    return any(t in SKILLS_HEADER_ANCHOR_WORDS for t in tokens)


ACTION_VERBS = {
    "accelerated", "accomplished", "achieved", "acquired", "adapted", "administered", "advanced",
    "analyzed", "architected", "automated", "built", "boosted", "calculated", "centralized",
    "championed", "collaborated", "constructed", "converted", "created", "customized", "debugged",
    "delivered", "deployed", "designed", "developed", "devised", "diagnosed", "directed",
    "discovered", "doubled", "drove", "engineered", "enhanced", "established", "evaluated",
    "executed", "expanded", "expedited", "fabricated", "facilitated", "forecasted", "formulated",
    "founded", "generated", "guided", "halted", "handled", "headed", "identified", "implemented",
    "improved", "increased", "initiated", "innovated", "inspected", "installed", "instituted",
    "instructed", "integrated", "introduced", "invented", "investigated", "launched", "lead",
    "led", "leveraged", "managed", "maximized", "mentored", "migrated", "minimized", "modernized",
    "monitored", "motivated", "negotiated", "optimized", "orchestrated", "organized", "overhauled",
    "oversaw", "partnered", "performed", "pioneered", "planned", "prepared", "produced",
    "programmed", "promoted", "proposed", "published", "rearchitected", "rebuilt", "reconciled",
    "redesigned", "reduced", "refactored", "refined", "reformed", "remodeled", "reorganized",
    "replaced", "researched", "resolved", "restructured", "revamped", "scaled", "scheduled",
    "secured", "selected", "separated", "simplified", "solved", "spearheaded", "standardized",
    "streamlined", "strengthened", "structured", "supervised", "surpassed", "synthesized",
    "systematized", "targeted", "trained", "transformed", "transitioned", "translated", "tripled",
    "uncovered", "unified", "upgraded", "utilized", "validated", "yielded"
}

KNOWN_SKILL_CATEGORIES = {
    "Languages": [
        "python", "javascript", "typescript", "java", "c++", "c#", "c", "go", "golang", "rust",
        "ruby", "php", "swift", "kotlin", "scala", "r", "sql", "bash", "shell", "powershell",
        "html", "html5", "css", "css3", "sass", "graphql"
    ],
    "Frameworks & Libraries": [
        "react", "react.js", "react native", "next.js", "vue", "vue.js", "angular", "node.js",
        "express", "django", "flask", "fastapi", "spring", "spring boot", "asp.net", ".net",
        "pytorch", "tensorflow", "keras", "scikit-learn", "pandas", "numpy", "opencv", "hugging face",
        "transformers", "langchain", "llamaindex", "tailwind", "bootstrap"
    ],
    "Cloud & DevOps": [
        "aws", "azure", "gcp", "google cloud", "docker", "kubernetes", "k8s", "terraform",
        "ansible", "jenkins", "gitlab ci", "github actions", "ci/cd", "linux", "unix", "nginx",
        "helm", "prometheus", "grafana", "serverless", "lambda"
    ],
    "Databases": [
        "postgresql", "postgres", "mysql", "sqlite", "mongodb", "redis", "elasticsearch",
        "cassandra", "dynamodb", "oracle", "mariadb", "snowflake", "bigquery", "neo4j", "pinecone",
        "chromadb", "qdrant", "weaviate"
    ],
    "Tools & Platforms": [
        "git", "github", "gitlab", "jira", "confluence", "postman", "figma", "tableau",
        "power bi", "vs code", "pycharm", "jupyter", "datadog", "new relic"
    ],
    "Methodologies & Practices": [
        "agile", "scrum", "kanban", "devops", "ci/cd", "microservices", "rest api", "soap",
        "grpc", "tdd", "system design", "distributed systems", "data structures", "algorithms"
    ],
    "Soft Skills": [
        "leadership", "team collaboration", "communication", "problem solving", "critical thinking",
        "project management", "cross-functional collaboration", "mentoring", "stakeholder management",
        "time management", "adaptability", "analytical skills"
    ]
}

def extract_contact_info(text: str) -> Dict[str, str]:
    first_lines = text.split("\n")[:10]
    first_chunk = "\n".join(first_lines)

    # Email
    email_match = re.search(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', text)
    email = email_match.group(0) if email_match else ""

    # Phone
    phone_match = re.search(r'(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', text)
    phone = phone_match.group(0).strip() if phone_match else ""

    # LinkedIn
    li_match = re.search(r'(?:https?:\/\/)?(?:www\.)?linkedin\.com\/(?:in\/[a-zA-Z0-9_-]+|[a-zA-Z0-9_-]+)', text, re.I)
    linkedin = li_match.group(0) if li_match else ""

    # GitHub
    gh_match = re.search(r'(?:https?:\/\/)?(?:www\.)?github\.com\/[a-zA-Z0-9_-]+', text, re.I)
    github = gh_match.group(0) if gh_match else ""

    # Portfolio / Website
    web_match = re.search(r'(?:https?:\/\/)?(?:www\.)?[a-zA-Z0-9-]+\.(?:dev|io|me|com|org)(?:\/[^\s]*)?', text, re.I)
    website = ""
    if web_match:
        cand = web_match.group(0)
        if "linkedin" not in cand and "github" not in cand:
            website = cand

    # Candidate Name (heuristic: typically the first non-empty header line)
    name = ""
    for line in first_lines:
        line_clean = line.strip()
        if not line_clean:
            continue
        # Skip if contains email, phone, or URLs
        if "@" in line_clean or "linkedin" in line_clean.lower() or "github" in line_clean.lower() or "http" in line_clean.lower():
            continue
        if len(line_clean.split()) <= 4 and re.match(r'^[A-Za-z\s\.\,\'-]+$', line_clean):
            name = line_clean
            break

    # Location (City, State / Country) — only match whole header segments that look
    # exactly like "City, ST"/"City, Country" rather than any comma inside a longer
    # sentence (e.g. a skills or summary line mentioning "Gen AI, Machine Learning").
    location = ""
    location_pattern = re.compile(r'^[A-Z][a-zA-Z.\s]+,\s*(?:[A-Z]{2}|[A-Z][a-zA-Z]+)$')
    for line in first_lines:
        for segment in re.split(r'\s*[|•]\s*', line.strip()):
            segment = segment.strip().rstrip(".")
            if not segment or "@" in segment or "http" in segment.lower():
                continue
            if len(segment) <= 40 and location_pattern.match(segment):
                location = segment
                break
        if location:
            break

    return {
        "name": name or "Candidate Name",
        "email": email,
        "phone": phone,
        "location": location,
        "linkedin": linkedin,
        "github": github,
        "website": website
    }

def segment_sections(text: str) -> Dict[str, str]:
    lines = text.split("\n")
    current_sec = "header"
    sections: Dict[str, List[str]] = {
        "header": [],
        "summary": [],
        "skills": [],
        "experience": [],
        "education": [],
        "projects": [],
        "certifications": [],
        "other": []
    }

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue

        # Check if line looks like a section header
        found_sec = None
        lower_line = stripped.lower().rstrip(":-_#")
        if len(stripped.split()) <= 5:
            for sec_name, pattern in SECTION_PATTERNS.items():
                if re.match(pattern + r"$", lower_line, re.IGNORECASE):
                    found_sec = sec_name
                    break
            if not found_sec and _is_skills_header(lower_line):
                found_sec = "skills"

        if found_sec:
            current_sec = found_sec
        else:
            sections[current_sec].append(stripped)

    return {k: "\n".join(v).strip() for k, v in sections.items()}

def parse_work_experience(exp_text: str) -> List[Dict[str, Any]]:
    if not exp_text:
        return []

    entries = []
    lines = exp_text.split("\n")
    current_entry = None

    date_regex = r'(?:(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{4}|\d{4})\s*(?:-|–|to)\s*(?:(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{4}|\d{4}|Present|Current)'

    def split_title_company(segment: str, default_to_company: bool = False):
        # Split a header segment into (title, company) without cutting on internal commas,
        # and without silently dropping text past the second "-"-delimited part.
        segment = segment.strip()
        if "|" in segment:
            parts = [p.strip() for p in segment.split("|", 1)]
        elif re.search(r'\s+at\s+', segment, re.I):
            parts = [p.strip() for p in re.split(r'\s+at\s+', segment, maxsplit=1, flags=re.I)]
        elif re.search(r'\s+[–-]\s+', segment):
            parts = [p.strip() for p in re.split(r'\s+[–-]\s+', segment, maxsplit=1)]
        elif "," in segment:
            parts = [p.strip() for p in segment.split(",", 1)]
        else:
            # No delimiter: a lone segment next to a date is almost always the
            # company (e.g. "Acme Corp (Jan 2020 - Dec 2022)"); a lone segment
            # matched purely by a title keyword (no date on the line) is the title.
            return ("", segment) if default_to_company else (segment, "")
        title = parts[0]
        company = parts[1] if len(parts) > 1 else ""
        return title, company

    for line in lines:
        line_clean = line.strip()
        if not line_clean:
            continue

        # Check if this line looks like a title/company with dates
        has_date = re.search(date_regex, line_clean, re.I)
        is_bullet = line_clean.startswith(("-", "*", "•", "–", "—", "·")) or (line_clean[0].isdigit() and line_clean[1:3] in [". ", ") "])

        if has_date or (not is_bullet and len(line_clean) < 95 and any(kw in line_clean.lower() for kw in ["engineer", "developer", "lead", "manager", "architect", "analyst", "consultant", "scientist", "specialist", "intern"])):
            if current_entry:
                entries.append(current_entry)

            date_str = has_date.group(0) if has_date else ""

            if has_date:
                # Pull the date range (and its wrapping parenthesis, if any) out of the
                # line before splitting title/company, so the date's own "-" never gets
                # mistaken for the title/company separator. Text trailing the date
                # (e.g. "Acme Corp (2021 - 2025) - Data Architect") is the designation.
                before = line_clean[:has_date.start()]
                after = line_clean[has_date.end():]
                before = re.sub(r'\(\s*$', '', before).strip()
                after = re.sub(r'^\s*\)', '', after).strip()
                after = re.sub(r'^[\s\-–—,|]+', '', after).strip()

                title, company = split_title_company(before, default_to_company=True)
                if after:
                    title = after
            else:
                title, company = split_title_company(line_clean, default_to_company=False)

            current_entry = {
                "title": title,
                "company": company,
                "dates": date_str,
                "location": "",
                "bullets": []
            }
        else:
            # Strip bullet symbol or enumerated prefix without cutting leading digits from text like '10x'
            cleaned_bullet = re.sub(r'^(?:[-*•–—·]\s*|\d+[\.\)]\s*)', '', line_clean).strip()
            if cleaned_bullet:
                if current_entry:
                    current_entry["bullets"].append(cleaned_bullet)
                else:
                    current_entry = {
                        "title": "Experience",
                        "company": "",
                        "dates": "",
                        "location": "",
                        "bullets": [cleaned_bullet]
                    }

    if current_entry:
        entries.append(current_entry)

    return entries

def extract_categorized_skills(text: str) -> Dict[str, List[str]]:
    text_lower = f" {text.lower()} "
    categorized: Dict[str, List[str]] = {}
    all_found = set()

    for category, skill_list in KNOWN_SKILL_CATEGORIES.items():
        matched = []
        for skill in skill_list:
            pattern = r'(?<![a-zA-Z0-9])' + re.escape(skill) + r'(?![a-zA-Z0-9])'
            if re.search(pattern, text_lower):
                formatted_skill = skill.title() if len(skill) > 3 and not skill.isupper() else skill.upper()
                if skill in ["react", "react.js", "next.js", "node.js", "vue.js"]:
                    formatted_skill = skill
                matched.append(formatted_skill)
                all_found.add(skill)
        if matched:
            categorized[category] = sorted(list(set(matched)))

    return categorized

def evaluate_ats_hygiene(raw_text: str, sections: Dict[str, str], contact: Dict[str, str], experience_entries: List[Dict[str, Any]]) -> Dict[str, Any]:
    score = 100
    warnings = []
    strengths = []
    suggestions = []

    # 1. Check Essential Sections (-10 per missing critical section)
    if not sections.get("skills"):
        score -= 15
        warnings.append("Missing dedicated 'Skills' section heading. ATS parsers rely on this to index competencies.")
    else:
        strengths.append("Dedicated Skills section present.")

    if not sections.get("experience"):
        score -= 20
        warnings.append("Missing standard 'Work Experience' heading.")
    else:
        strengths.append("Standard Work Experience section identified.")

    if not sections.get("education"):
        score -= 10
        warnings.append("Missing standard 'Education' section heading.")

    # 2. Check Contact Details
    if not contact.get("email"):
        score -= 15
        warnings.append("Email address not found or formatted unclearly.")
    else:
        strengths.append("Valid email detected.")

    if not contact.get("phone"):
        score -= 10
        warnings.append("Phone number missing or in an unrecognized format.")
    else:
        strengths.append("Phone number found.")

    if not contact.get("linkedin"):
        suggestions.append("Adding a LinkedIn profile URL improves recruiter reach and ATS indexation.")

    # 3. Action Verbs & Metrics in Experience Bullets
    all_bullets = []
    for exp in experience_entries:
        all_bullets.extend(exp.get("bullets", []))

    if not all_bullets:
        # fallback to raw text bullet search
        all_bullets = [b for b in raw_text.split("\n") if len(b) > 20 and b.strip().startswith(("-", "*", "•"))]

    action_verb_count = 0
    quantified_count = 0

    metric_regex = r'(?:\d+%\s*|\$\s*[\d,]+|\b\d+(?:\.\d+)?(?:k|m|b|\+)?\b|\b(?:reduced|increased|improved|saved|boosted)\b)'

    for b in all_bullets:
        words = re.findall(r'\b[a-zA-Z]+\b', b.lower())
        if words and words[0] in ACTION_VERBS:
            action_verb_count += 1
        elif any(w in ACTION_VERBS for w in words[:3]):
            action_verb_count += 1

        if re.search(metric_regex, b, re.IGNORECASE):
            quantified_count += 1

    total_bullets = len(all_bullets) or 1
    action_verb_ratio = action_verb_count / total_bullets
    quantified_ratio = quantified_count / total_bullets

    if action_verb_ratio < 0.5:
        score -= 10
        warnings.append(f"Only {int(action_verb_ratio * 100)}% of bullet points start with strong action verbs. Aim for >80%.")
    else:
        strengths.append(f"High action-verb usage ({int(action_verb_ratio * 100)}% of experience bullets).")

    if quantified_ratio < 0.35:
        score -= 10
        warnings.append(f"Only {int(quantified_ratio * 100)}% of bullets include measurable metrics (%, $, numbers). Google XYZ / STAR format strongly recommended.")
        suggestions.append("Add measurable outcomes to your bullets (e.g. 'Improved latency by 35%', 'Scaled service to 100K active users').")
    else:
        strengths.append(f"Strong quantification in work experience ({int(quantified_ratio * 100)}% with metrics).")

    # 4. Length & Density Checks
    words = raw_text.split()
    total_words = len(words)
    if total_words < 200:
        score -= 15
        warnings.append("Resume is very brief (< 200 words). It may get discarded for insufficient depth.")
    elif total_words > 1200:
        suggestions.append("Resume exceeds 1200 words (~3 pages). Consider tightening to 1-2 pages for faster human and ATS scanning.")

    score = max(20, min(100, score))

    return {
        "score": score,
        "grade": "A+" if score >= 90 else "A" if score >= 80 else "B" if score >= 70 else "C" if score >= 55 else "Needs Attention",
        "warnings": warnings,
        "strengths": strengths,
        "suggestions": suggestions,
        "metrics": {
            "total_words": total_words,
            "total_bullets": len(all_bullets),
            "action_verb_percentage": round(action_verb_ratio * 100, 1),
            "quantified_percentage": round(quantified_ratio * 100, 1)
        }
    }

_MOJIBAKE_MARKERS = ("â€", "Ã¢", "Ã©", "Ã¨", "Ã¯", "Â ")

def repair_mojibake(text: str) -> str:
    """
    Repairs text that was UTF-8 encoded but mistakenly decoded as CP1252/Latin-1
    upstream (a common artifact of copy-pasting resume content between apps),
    e.g. an en dash "–" turning into the 3-character sequence "â€“". Round-trips
    the text through the inverse transform and only keeps the result if it is
    actually valid UTF-8, so clean text is never touched.
    """
    if not text or not any(marker in text for marker in _MOJIBAKE_MARKERS):
        return text
    try:
        return text.encode("cp1252").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return text

def normalize_to_ats_json(raw_text: str, filename: str = "Uploaded_Resume") -> Dict[str, Any]:
    raw_text = repair_mojibake(raw_text)
    contact = extract_contact_info(raw_text)
    sections = segment_sections(raw_text)
    experience = parse_work_experience(sections.get("experience", ""))
    skills_categorized = extract_categorized_skills(raw_text)
    hygiene = evaluate_ats_hygiene(raw_text, sections, contact, experience)

    # Flatten skills for quick lookup
    all_skills_flat = []
    for cat_skills in skills_categorized.values():
        all_skills_flat.extend(cat_skills)

    # Format ATS JSON Schema
    ats_json = {
        "metadata": {
            "version": "1.0",
            "schema": "ATS_Standard_Resume_v1",
            "source_file": filename,
            "ats_compatibility_score": hygiene["score"],
            "ats_grade": hygiene["grade"]
        },
        "contact_information": contact,
        "professional_summary": sections.get("summary", ""),
        "skills": {
            "categories": skills_categorized,
            "all_keywords": sorted(list(set(all_skills_flat)))
        },
        "work_experience": experience,
        "education": [
            {"raw_text": line.strip()}
            for line in sections.get("education", "").split("\n")
            if line.strip()
        ],
        "projects": [
            {"raw_text": line.strip()}
            for line in sections.get("projects", "").split("\n")
            if line.strip()
        ],
        "certifications": [
            {"raw_text": line.strip()}
            for line in sections.get("certifications", "").split("\n")
            if line.strip()
        ],
        "raw_text": raw_text
    }

    return {
        "ats_json": ats_json,
        "hygiene_report": hygiene
    }

def parse_projects_from_text(projects_text: str, raw_text: str = "") -> List[Dict[str, Any]]:
    """
    Parses project entries from dedicated projects section or extracts projects from raw text.
    Returns structured list of project dicts with id, name, tech_stack, description, metrics, bullets.
    """
    source = projects_text.strip() if projects_text.strip() else ""
    if not source and raw_text:
        proj_match = re.search(r'(?:projects|technical projects|key projects)\s*\n([\s\S]*?)(?=\n[A-Z\s]{4,}\n|\Z)', raw_text, re.I)
        if proj_match:
            source = proj_match.group(1).strip()

    if not source:
        return []

    lines = source.split("\n")
    projects = []
    current_proj = None
    metric_regex = r'(?:\d+%\s*|\$\s*[\d,]+|\b\d+(?:\.\d+)?(?:k|m|b|\+)?\b|\b(?:sub-\d+ms|latency|throughput|accuracy|recall|precision)\b)'

    for line in lines:
        line_clean = line.strip()
        if not line_clean:
            continue

        is_bullet = line_clean.startswith(("-", "*", "•", "–", "—", "·")) or (line_clean[0].isdigit() and len(line_clean) > 2 and line_clean[1:3] in [". ", ") "])

        if not is_bullet and (len(line_clean) < 95 or ":" in line_clean or "(" in line_clean or "[" in line_clean):
            if current_proj:
                projects.append(current_proj)

            tech_stack = ""
            name = line_clean
            bracket_match = re.search(r'[\[\(]([^\]\)]+)[\]\)]', line_clean)
            if bracket_match:
                tech_stack = bracket_match.group(1)
                name = re.sub(r'[\[\(][^\]\)]+[\]\)]', '', line_clean).strip(" -:|")
            elif ":" in line_clean:
                parts = line_clean.split(":", 1)
                name = parts[0].strip()
                if any(kw in parts[1].lower() for kw in ["python", "java", "react", "aws", "docker", "c++", "sql", "pytorch", "fastapi"]):
                    tech_stack = parts[1].strip()

            current_proj = {
                "id": f"proj-{len(projects) + 1}",
                "name": name.strip(" -:|") or "Technical Project",
                "organisation": "",
                "organisation_duration": "",
                "tech_stack": tech_stack,
                "description": "",
                "metrics": "",
                "bullets": []
            }
        else:
            cleaned = re.sub(r'^(?:[-*•–—·]\s*|\d+[\.\)]\s*)', '', line_clean).strip()
            if cleaned:
                if current_proj:
                    current_proj["bullets"].append(cleaned)
                    if not current_proj["metrics"] and re.search(metric_regex, cleaned, re.I):
                        current_proj["metrics"] = cleaned
                else:
                    current_proj = {
                        "id": f"proj-{len(projects) + 1}",
                        "name": "Project Highlight",
                        "organisation": "",
                        "organisation_duration": "",
                        "tech_stack": "",
                        "description": "",
                        "metrics": "",
                        "bullets": [cleaned]
                    }

    if current_proj:
        projects.append(current_proj)

    return projects

def derive_master_resume_from_ats_json(ats_json_data: Dict[str, Any]) -> Dict[str, Any]:
    contact = ats_json_data.get("contact_information", {})
    name = contact.get("name", "Candidate").strip() or "Candidate"
    summary = ats_json_data.get("professional_summary", "").strip()
    skills = ats_json_data.get("skills", {}).get("categories", {})
    work_exps = ats_json_data.get("work_experience", [])
    raw_text = ats_json_data.get("raw_text", "")

    # Parse projects
    projects_raw = ats_json_data.get("projects", [])
    projects_text = "\n".join([p.get("raw_text", str(p)) for p in projects_raw])
    parsed_projects = parse_projects_from_text(projects_text, raw_text)

    # If no projects section, extract notable project achievements from experience bullets
    if not parsed_projects and work_exps:
        for idx, exp in enumerate(work_exps):
            comp_name = exp.get("company") or "Enterprise"
            comp_dur = exp.get("dates") or f"{exp.get('start_date', '')} - {exp.get('end_date', '')}".strip(" -")
            title_name = exp.get("title") or "System"
            for b in exp.get("bullets", []):
                if re.search(r'\d+%|\$\d+|\b\d+\b', b) or any(v in b.lower() for v in ["architected", "built", "engineered", "deployed", "scaled"]):
                    parsed_projects.append({
                        "id": f"proj-{len(parsed_projects) + 1}",
                        "name": f"{title_name} Architecture Initiative",
                        "organisation": comp_name,
                        "organisation_duration": comp_dur,
                        "tech_stack": comp_name,
                        "description": f"Key technical delivery at {comp_name}.",
                        "metrics": b,
                        "bullets": [b]
                    })
                    if len(parsed_projects) >= 3:
                        break
            if len(parsed_projects) >= 3:
                break

    # Link organisation and duration to any projects lacking organisation
    for p in parsed_projects:
        if not p.get("organisation") and work_exps:
            # Check if project matches any company name in work_exps
            matched_exp = next((e for e in work_exps if e.get("company") and (e["company"].lower() in p["name"].lower() or e["company"].lower() in p.get("tech_stack", "").lower())), None)
            if matched_exp:
                p["organisation"] = matched_exp.get("company") or "Independent / Personal Project"
                p["organisation_duration"] = matched_exp.get("dates") or f"{matched_exp.get('start_date', '')} - {matched_exp.get('end_date', '')}".strip(" -")
            else:
                p["organisation"] = work_exps[0].get("company") or "Independent / Personal Project"
                p["organisation_duration"] = work_exps[0].get("dates") or f"{work_exps[0].get('start_date', '')} - {work_exps[0].get('end_date', '')}".strip(" -")
        elif not p.get("organisation"):
            p["organisation"] = "Independent / Open Source"
            p["organisation_duration"] = ""

    # Parse education cleanly without chopping degree text
    education_entries = []
    for edu in ats_json_data.get("education", []):
        edu_text = edu.get("raw_text", "") if isinstance(edu, dict) else str(edu)
        if edu_text:
            if "|" in edu_text:
                parts = [p.strip() for p in edu_text.split("|")]
            elif " – " in edu_text or " - " in edu_text:
                parts = [p.strip() for p in re.split(r'\s+[–-]\s+', edu_text)]
            else:
                parts = [p.strip() for p in edu_text.split(",")]
            degree = parts[0]
            inst = parts[1] if len(parts) > 1 else ""
            year_match = re.search(r'\b(19\d\d|20\d\d)(?:\s*[-–]\s*(?:19\d\d|20\d\d|Present))?\b', edu_text)
            year = year_match.group(0) if year_match else ""
            education_entries.append({
                "degree": degree,
                "institution": inst,
                "year": year,
                "details": edu_text
            })

    # Parse certifications
    certifications = []
    for c in ats_json_data.get("certifications", []):
        c_text = c.get("raw_text", "") if isinstance(c, dict) else str(c)
        if c_text:
            certifications.append(c_text.lstrip("-•* "))

    return {
        # No "profile_name" here deliberately -- it's a user-owned display label
        # (set via Rename or on profile creation), never derived from a parsed
        # resume, so re-syncing/merging a resume can never silently rename a
        # profile out from under the user. save_master_resume() falls back to
        # "{full_name}'s Master Profile" only when creating a brand-new profile.
        "full_name": name,
        "email": contact.get("email", ""),
        "phone": contact.get("phone", ""),
        "location": contact.get("location", ""),
        "linkedin": contact.get("linkedin", ""),
        "github": contact.get("github", ""),
        "summary": summary,
        "skills": skills,
        "experiences": work_exps,
        "projects": parsed_projects,
        "education": education_entries,
        "certifications": certifications
    }

