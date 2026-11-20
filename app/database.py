import os
import json
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional, Any

DB_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
DB_PATH = os.path.join(DB_DIR, "applications.db")

STAGES = [
    "Wishlist",
    "Resume Screening",
    "Recruiter Screening",
    "Interview",
    "Offer",
    "Rejected",
    "Archived"
]

def get_connection():
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    os.makedirs(DB_DIR, exist_ok=True)
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS applications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company TEXT NOT NULL,
                role TEXT NOT NULL,
                location TEXT DEFAULT '',
                stage TEXT NOT NULL DEFAULT 'Wishlist',
                salary TEXT DEFAULT '',
                job_url TEXT DEFAULT '',
                jd_text TEXT DEFAULT '',
                match_score REAL DEFAULT 0.0,
                resume_filename TEXT DEFAULT '',
                date_applied TEXT DEFAULT '',
                follow_up_date TEXT DEFAULT '',
                notes TEXT DEFAULT '',
                interview_step TEXT DEFAULT '',
                rejected_from_stage TEXT DEFAULT '',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS api_providers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                base_url TEXT NOT NULL,
                api_key TEXT NOT NULL,
                model_name TEXT NOT NULL,
                is_active INTEGER DEFAULT 0,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS master_resumes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                profile_name TEXT NOT NULL DEFAULT 'Master Profile',
                full_name TEXT DEFAULT '',
                email TEXT DEFAULT '',
                phone TEXT DEFAULT '',
                location TEXT DEFAULT '',
                linkedin TEXT DEFAULT '',
                github TEXT DEFAULT '',
                summary TEXT DEFAULT '',
                skills_json TEXT DEFAULT '{}',
                experiences_json TEXT DEFAULT '[]',
                projects_json TEXT DEFAULT '[]',
                education_json TEXT DEFAULT '[]',
                certifications_json TEXT DEFAULT '[]',
                raw_text TEXT DEFAULT '',
                is_active INTEGER DEFAULT 0,
                is_locked INTEGER DEFAULT 0,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS resume_ledger (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                resume_name TEXT DEFAULT '',
                job_title TEXT NOT NULL,
                company TEXT NOT NULL,
                tier TEXT NOT NULL,
                source_type TEXT NOT NULL DEFAULT 'Current Resume',
                source_name TEXT DEFAULT '',
                match_score_before REAL DEFAULT 0.0,
                match_score_after REAL DEFAULT 0.0,
                filename TEXT DEFAULT '',
                file_path TEXT DEFAULT '',
                resume_text TEXT DEFAULT '',
                ats_json TEXT DEFAULT '{}',
                changes_summary TEXT DEFAULT '[]',
                application_id INTEGER DEFAULT NULL,
                created_at TEXT NOT NULL
            )
        """)
        try:
            cursor.execute("ALTER TABLE applications ADD COLUMN interview_step TEXT DEFAULT ''")
        except Exception:
            pass
        try:
            cursor.execute("ALTER TABLE applications ADD COLUMN rejected_from_stage TEXT DEFAULT ''")
        except Exception:
            pass
        try:
            cursor.execute("ALTER TABLE resume_ledger ADD COLUMN resume_name TEXT DEFAULT ''")
        except Exception:
            pass
        try:
            cursor.execute("ALTER TABLE master_resumes ADD COLUMN is_active INTEGER DEFAULT 0")
        except Exception:
            pass
        try:
            cursor.execute("ALTER TABLE master_resumes ADD COLUMN is_locked INTEGER DEFAULT 0")
        except Exception:
            pass

        # Backfill: if profiles exist from before multi-profile support, mark the
        # oldest one active so get_master_resume()/save_master_resume() (which now
        # resolve "the current profile" via is_active) keep working without a reset.
        cursor.execute("SELECT COUNT(*) FROM master_resumes WHERE is_active = 1")
        if cursor.fetchone()[0] == 0:
            cursor.execute("SELECT COUNT(*) FROM master_resumes")
            if cursor.fetchone()[0] > 0:
                cursor.execute("""
                    UPDATE master_resumes SET is_active = 1
                    WHERE id = (SELECT id FROM master_resumes ORDER BY id ASC LIMIT 1)
                """)

        # Migrate legacy stages
        cursor.execute("UPDATE applications SET stage = 'Wishlist' WHERE stage = 'Jobs Found'")
        cursor.execute("UPDATE applications SET stage = 'Resume Screening' WHERE stage = 'Applied'")
        cursor.execute("UPDATE applications SET stage = 'Recruiter Screening' WHERE stage = 'Screening'")
        cursor.execute("UPDATE applications SET stage = 'Interview' WHERE stage = 'Interviewing'")
        conn.commit()
    
    # Ensure sample master resume exists
    ensure_sample_master_resume()

def create_application(data: Dict[str, Any]) -> Dict[str, Any]:
    now = datetime.now().isoformat()
    stage = data.get("stage", "Wishlist")
    if stage not in STAGES:
        stage = "Wishlist"

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO applications (
                company, role, location, stage, salary, job_url, jd_text,
                match_score, resume_filename, date_applied, follow_up_date, notes,
                interview_step, rejected_from_stage,
                created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data.get("company", "").strip() or "Unnamed Company",
            data.get("role", "").strip() or "Target Role",
            data.get("location", "").strip(),
            stage,
            data.get("salary", "").strip(),
            data.get("job_url", "").strip(),
            data.get("jd_text", "").strip(),
            float(data.get("match_score", 0.0) or 0.0),
            data.get("resume_filename", "").strip(),
            data.get("date_applied", "") or (now[:10] if stage not in ["Wishlist"] else ""),
            data.get("follow_up_date", "").strip(),
            data.get("notes", "").strip(),
            data.get("interview_step", "").strip() or ("Round 1: Technical Screen" if stage == "Interview" else ""),
            data.get("rejected_from_stage", "").strip(),
            now,
            now
        ))
        conn.commit()
        app_id = cursor.lastrowid
        return get_application_by_id(app_id)

def get_all_applications(stage_filter: Optional[str] = None) -> List[Dict[str, Any]]:
    with get_connection() as conn:
        cursor = conn.cursor()
        if stage_filter and stage_filter in STAGES:
            cursor.execute("SELECT * FROM applications WHERE stage = ? ORDER BY id DESC", (stage_filter,))
        else:
            cursor.execute("SELECT * FROM applications ORDER BY id DESC")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

def get_wishlist_jobs() -> List[Dict[str, Any]]:
    return get_all_applications(stage_filter="Wishlist")

def get_jobs_found() -> List[Dict[str, Any]]:
    return get_wishlist_jobs()

def get_application_by_id(app_id: int) -> Optional[Dict[str, Any]]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM applications WHERE id = ?", (app_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

def update_application(app_id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    now = datetime.now().isoformat()
    fields = []
    values = []

    allowed_fields = [
        "company", "role", "location", "stage", "salary", "job_url",
        "jd_text", "match_score", "resume_filename", "date_applied",
        "follow_up_date", "notes", "interview_step", "rejected_from_stage"
    ]

    for key in allowed_fields:
        if key in data:
            val = data[key]
            if key == "match_score":
                val = float(val or 0.0)
            fields.append(f"{key} = ?")
            values.append(val)

    if not fields:
        return get_application_by_id(app_id)

    fields.append("updated_at = ?")
    values.append(now)
    values.append(app_id)

    with get_connection() as conn:
        cursor = conn.cursor()
        query = f"UPDATE applications SET {', '.join(fields)} WHERE id = ?"
        cursor.execute(query, tuple(values))
        conn.commit()
        return get_application_by_id(app_id)

def update_application_stage(app_id: int, new_stage: str, rejected_from_stage: str = "", interview_step: str = "") -> Optional[Dict[str, Any]]:
    if new_stage not in STAGES:
        return None
    data = {"stage": new_stage}
    if new_stage in ["Resume Screening", "Recruiter Screening", "Interview", "Offer"]:
        # automatically stamp date applied if not already set
        existing = get_application_by_id(app_id)
        if existing and not existing.get("date_applied"):
            data["date_applied"] = datetime.now().strftime("%Y-%m-%d")
    if rejected_from_stage:
        data["rejected_from_stage"] = rejected_from_stage
    if interview_step:
        data["interview_step"] = interview_step
    elif new_stage == "Interview":
        existing = get_application_by_id(app_id)
        if existing and not existing.get("interview_step"):
            data["interview_step"] = "Round 1: Technical Screen"
    return update_application(app_id, data)

def delete_application(app_id: int) -> bool:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM applications WHERE id = ?", (app_id,))
        conn.commit()
        return cursor.rowcount > 0

def get_funnel_stats() -> Dict[str, Any]:
    apps = get_all_applications()
    counts = {s: 0 for s in STAGES}
    scores_by_stage: Dict[str, List[float]] = {s: [] for s in STAGES}

    for app in apps:
        stage = app.get("stage", "Wishlist")
        if stage in counts:
            counts[stage] += 1
            if app.get("match_score"):
                scores_by_stage[stage].append(float(app["match_score"]))

    total = len(apps)
    screen_plus = sum(counts[s] for s in ["Resume Screening", "Recruiter Screening", "Interview", "Offer", "Rejected", "Archived"])
    recruiter_plus = sum(counts[s] for s in ["Recruiter Screening", "Interview", "Offer"])
    interview_plus = sum(counts[s] for s in ["Interview", "Offer"])
    offers = counts["Offer"]

    conversion_rates = {
        "screen_to_recruiter": round((recruiter_plus / screen_plus * 100), 1) if screen_plus > 0 else 0.0,
        "recruiter_to_interview": round((interview_plus / recruiter_plus * 100), 1) if recruiter_plus > 0 else 0.0,
        "interview_to_offer": round((offers / interview_plus * 100), 1) if interview_plus > 0 else 0.0,
        "overall_offer_rate": round((offers / screen_plus * 100), 1) if screen_plus > 0 else 0.0,
    }

    avg_match_scores = {}
    for stage, scores in scores_by_stage.items():
        avg_match_scores[stage] = round(sum(scores) / len(scores), 1) if scores else 0.0

    return {
        "total_tracked": total,
        "stage_counts": counts,
        "conversion_rates": conversion_rates,
        "avg_match_scores": avg_match_scores,
        "stages": STAGES
    }

# ================= API PROVIDER DATABASE FUNCTIONS =================

def get_all_providers() -> List[Dict[str, Any]]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM api_providers ORDER BY is_active DESC, id DESC")
        rows = cursor.fetchall()
        providers = []
        for r in rows:
            p = dict(r)
            raw_key = p.get("api_key", "")
            if len(raw_key) > 8:
                p["masked_key"] = raw_key[:4] + "..." + raw_key[-4:]
            elif raw_key:
                p["masked_key"] = "****"
            else:
                p["masked_key"] = "(none)"
            providers.append(p)
        return providers

def get_provider_by_id(provider_id: int) -> Optional[Dict[str, Any]]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM api_providers WHERE id = ?", (provider_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

def get_active_provider() -> Optional[Dict[str, Any]]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM api_providers WHERE is_active = 1 LIMIT 1")
        row = cursor.fetchone()
        return dict(row) if row else None

def save_provider(data: Dict[str, Any]) -> Dict[str, Any]:
    now = datetime.now().isoformat()
    name = data.get("name", "Custom Provider").strip() or "Custom Provider"
    base_url = data.get("base_url", "https://api.openai.com/v1").strip().rstrip("/")
    api_key = data.get("api_key", "").strip()
    model_name = data.get("model_name", "gpt-4o-mini").strip() or "gpt-4o-mini"
    is_active = 1 if data.get("is_active") else 0
    provider_id = data.get("id")

    with get_connection() as conn:
        cursor = conn.cursor()

        # If setting this active, deactivate others
        if is_active:
            cursor.execute("UPDATE api_providers SET is_active = 0")

        if provider_id:
            cursor.execute("""
                UPDATE api_providers
                SET name = ?, base_url = ?, api_key = ?, model_name = ?, is_active = ?, updated_at = ?
                WHERE id = ?
            """, (name, base_url, api_key, model_name, is_active, now, provider_id))
            target_id = provider_id
        else:
            # If this is the first provider being added, make it active by default
            cursor.execute("SELECT COUNT(*) FROM api_providers")
            count = cursor.fetchone()[0]
            if count == 0:
                is_active = 1

            cursor.execute("""
                INSERT INTO api_providers (name, base_url, api_key, model_name, is_active, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (name, base_url, api_key, model_name, is_active, now, now))
            target_id = cursor.lastrowid

        conn.commit()
        return get_provider_by_id(target_id)

def set_active_provider(provider_id: int) -> Optional[Dict[str, Any]]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE api_providers SET is_active = 0")
        cursor.execute("UPDATE api_providers SET is_active = 1, updated_at = ? WHERE id = ?", (
            datetime.now().isoformat(), provider_id
        ))
        conn.commit()
        return get_provider_by_id(provider_id)

def deactivate_all_providers() -> bool:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE api_providers SET is_active = 0")
        conn.commit()
        return True

def delete_provider(provider_id: int) -> bool:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM api_providers WHERE id = ?", (provider_id,))
        conn.commit()
        return cursor.rowcount > 0

# ================= MASTER RESUME REPOSITORY FUNCTIONS =================

SAMPLE_MASTER_DATA = {
    "profile_name": "Master Tech & ML Profile",
    "full_name": "Alexander Rivera",
    "email": "alex.rivera@email.com",
    "phone": "(555) 382-9012",
    "location": "San Francisco, CA",
    "linkedin": "linkedin.com/in/alex-rivera-ml",
    "github": "github.com/alexrivera-dev",
    "summary": "Senior Full-Stack & Machine Learning Engineer with 7+ years of experience architecting high-throughput microservices, scalable distributed backends, and deploying real-time LLM/NLP pipelines into enterprise production. Proven expertise across Python, PyTorch, Go, Docker, Kubernetes, and AWS.",
    "skills": {
        "Languages": ["Python", "TypeScript", "Go", "C++", "SQL", "Bash", "HTML5", "CSS3"],
        "Frameworks & AI": ["PyTorch", "Hugging Face", "Transformers", "LangChain", "FastAPI", "Django", "React", "Next.js", "Scikit-Learn", "Pandas", "NumPy"],
        "Cloud & DevOps": ["AWS (EC2, S3, Lambda)", "Docker", "Kubernetes", "Terraform", "CI/CD", "GitHub Actions", "Linux"],
        "Databases & Storage": ["PostgreSQL", "Pinecone", "Redis", "MongoDB", "Elasticsearch"],
        "Architecture": ["Microservices", "Distributed Systems", "REST & gRPC", "RAG Pipelines", "TDD", "System Design"]
    },
    "experiences": [
        {
            "company": "Apex AI Technologies",
            "title": "Senior Machine Learning & Systems Engineer",
            "location": "San Francisco, CA",
            "start_date": "2022",
            "end_date": "Present",
            "bullets": [
                "Architected and deployed a multi-tenant retrieval-augmented generation (RAG) platform using FastAPI, PyTorch, and PostgreSQL, reducing search latency by 45%.",
                "Scaled background inference workers using Docker, Redis queues, and Kubernetes, handling 15M+ daily requests with 99.98% uptime.",
                "Integrated continuous integration and automated testing via GitHub Actions, accelerating release deployment velocity by 40%.",
                "Mentored 4 junior engineers across ML ops best practices, code reviews, and distributed systems design."
            ]
        },
        {
            "company": "Horizon Cloud Systems",
            "title": "Full Stack & Cloud Software Engineer",
            "location": "San Jose, CA",
            "start_date": "2019",
            "end_date": "2022",
            "bullets": [
                "Developed scalable web services and responsive interfaces using React, TypeScript, and Python backend services, boosting active user engagement by 28%.",
                "Optimized database indexing and partitioning on large-scale PostgreSQL tables containing 50M+ records, slashing median query execution times by 60%.",
                "Built and maintained automated cloud ingestion pipelines with AWS Lambda, S3, and Docker containers."
            ]
        }
    ],
    "projects": [
        {
            "id": "proj-1",
            "name": "Distributed Vector Search Engine",
            "organisation": "Apex AI Technologies",
            "organisation_duration": "2022 - Present",
            "tech_stack": "Python, C++, FAISS, SIMD, gRPC",
            "description": "High-performance vector similarity search engine capable of sub-8ms k-NN queries across 10M+ dense embeddings.",
            "metrics": "Sub-8ms latency, 99.4% recall, 4x memory compression using product quantization",
            "bullets": [
                "Engineered a distributed vector similarity indexing engine in C++ with Python bindings, achieving sub-8ms nearest-neighbor retrieval across 10M+ 768-dim embeddings.",
                "Implemented product quantization and SIMD optimizations, slashing indexing memory footprint by 4x while maintaining 99.4% recall accuracy."
            ]
        },
        {
            "id": "proj-2",
            "name": "Multi-Tenant Enterprise RAG Knowledge Hub",
            "organisation": "Apex AI Technologies",
            "organisation_duration": "2022 - Present",
            "tech_stack": "LangChain, PyTorch, FastAPI, Pinecone, Redis, Docker",
            "description": "Enterprise-grade RAG Q&A platform with hybrid sparse-dense retrieval, BERT re-ranking, and tenant isolation.",
            "metrics": "45% reduction in search latency, 92% answer precision across 200k docs",
            "bullets": [
                "Designed and productionized a multi-tenant RAG architecture integrating hybrid BM25 + dense Pinecone vector retrieval with cross-encoder BERT re-ranking.",
                "Built token-streaming inference endpoints in FastAPI with Redis cache layering, serving 500+ concurrent enterprise users with sub-second response times."
            ]
        },
        {
            "id": "proj-3",
            "name": "Real-Time Distributed LLM Inference Gateway",
            "organisation": "Apex AI Technologies",
            "organisation_duration": "2022 - Present",
            "tech_stack": "vLLM, TensorRT-LLM, Ray, Kubernetes, AWS EKS",
            "description": "Scalable inference routing gateway supporting dynamic batching, speculative decoding, and autoscaling across GPU clusters.",
            "metrics": "3.5x throughput improvement, 15M+ daily tokens served",
            "bullets": [
                "Deployed auto-scaling vLLM inference worker clusters on AWS EKS using Kubernetes HPA and custom Prometheus GPU metrics.",
                "Configured continuous batching and PagedAttention, increasing token throughput by 3.5x and cutting p99 GPU idle time."
            ]
        },
        {
            "id": "proj-4",
            "name": "Automated ATS Resume Analyzer & Optimizer",
            "organisation": "Personal / Open Source",
            "organisation_duration": "2023 - Present",
            "tech_stack": "Python, FastAPI, SQLite, docx, spaCy, Llama-3",
            "description": "Desktop ATS resume parser, requirement matcher, and automated 3-tier tailoring engine with DOCX export.",
            "metrics": "Evaluates 20+ requirement categories, instant 1-click DOCX generation",
            "bullets": [
                "Created an end-to-end ATS parser extracting complex nested candidate profiles from PDF/DOCX and normalizing into structured JSON.",
                "Engineered dynamic JD requirement alignment algorithms providing Google XYZ bullet transformations and before/after match score tracking."
            ]
        },
        {
            "id": "proj-5",
            "name": "Cloud-Native Microservices Event Streaming Hub",
            "organisation": "Horizon Cloud Systems",
            "organisation_duration": "2019 - 2022",
            "tech_stack": "Go, Kafka, Docker, AWS S3, PostgreSQL",
            "description": "Distributed event streaming pipeline ingesting high-volume telemetry and audit logs with SOC2 compliance.",
            "metrics": "120,000 events/sec throughput with 99.99% message delivery guarantee",
            "bullets": [
                "Developed distributed event consumer microservices in Go using Apache Kafka and PostgreSQL, sustaining 120k events/sec peak ingest.",
                "Implemented dead-letter queues and automated idempotent replay mechanisms, guaranteeing zero message loss during cluster failovers."
            ]
        }
    ],
    "education": [
        {
            "degree": "Bachelor of Science in Computer Science",
            "institution": "University of California, Berkeley",
            "year": "2015 - 2019",
            "details": "GPA: 3.8 / 4.0 | Dean's Honors List"
        }
    ],
    "certifications": [
        "AWS Certified Solutions Architect - Associate",
        "CKA (Certified Kubernetes Administrator)"
    ]
}

def build_raw_master_text(data: Dict[str, Any]) -> str:
    lines = []
    lines.append(data.get("full_name", "").upper())
    contact_parts = [
        data.get("location", ""),
        data.get("phone", ""),
        data.get("email", ""),
        data.get("linkedin", ""),
        data.get("github", "")
    ]
    lines.append(" | ".join([p for p in contact_parts if p]))
    lines.append("")

    if data.get("summary"):
        lines.append("PROFESSIONAL SUMMARY")
        lines.append(data["summary"])
        lines.append("")

    skills = data.get("skills", {})
    if skills:
        lines.append("CORE COMPETENCIES & TECHNICAL SKILLS")
        for cat, s_list in skills.items():
            lines.append(f"{cat}: {', '.join(s_list)}")
        lines.append("")

    exps = data.get("experiences", [])
    if exps:
        lines.append("PROFESSIONAL EXPERIENCE")
        for exp in exps:
            header = f"{exp.get('title', '')} | {exp.get('company', '')} | {exp.get('location', '')} | {exp.get('start_date', '')} - {exp.get('end_date', '')}"
            lines.append(header)
            for b in exp.get("bullets", []):
                lines.append(f"- {b}")
            lines.append("")

    projs = data.get("projects", [])
    if projs:
        lines.append("KEY PROJECTS & ARCHITECTURES")
        for proj in projs:
            header_parts = [proj.get("name", "")]
            org = proj.get("organisation", "").strip()
            org_dur = proj.get("organisation_duration", "").strip()
            if org and org_dur:
                header_parts.append(f"{org} ({org_dur})")
            elif org:
                header_parts.append(org)
            if proj.get("tech_stack"):
                header_parts.append(f"[{proj.get('tech_stack')}]")
            lines.append(" | ".join(header_parts))
            if proj.get("description"):
                lines.append(f"Description: {proj.get('description')}")
            for b in proj.get("bullets", []):
                lines.append(f"- {b}")
            lines.append("")

    edus = data.get("education", [])
    if edus:
        lines.append("EDUCATION")
        for edu in edus:
            lines.append(f"{edu.get('degree', '')} | {edu.get('institution', '')} | {edu.get('year', '')}")
            if edu.get("details"):
                lines.append(edu.get("details"))
        lines.append("")

    certs = data.get("certifications", [])
    if certs:
        lines.append("CERTIFICATIONS")
        for c in certs:
            lines.append(f"- {c}")

    return "\n".join(lines).strip()

def ensure_sample_master_resume():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM master_resumes")
        count = cursor.fetchone()[0]
        if count == 0:
            now = datetime.now().isoformat()
            raw_txt = build_raw_master_text(SAMPLE_MASTER_DATA)
            cursor.execute("""
                INSERT INTO master_resumes (
                    profile_name, full_name, email, phone, location, linkedin, github,
                    summary, skills_json, experiences_json, projects_json, education_json,
                    certifications_json, raw_text, is_active, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?, ?)
            """, (
                SAMPLE_MASTER_DATA["profile_name"],
                SAMPLE_MASTER_DATA["full_name"],
                SAMPLE_MASTER_DATA["email"],
                SAMPLE_MASTER_DATA["phone"],
                SAMPLE_MASTER_DATA["location"],
                SAMPLE_MASTER_DATA["linkedin"],
                SAMPLE_MASTER_DATA["github"],
                SAMPLE_MASTER_DATA["summary"],
                json.dumps(SAMPLE_MASTER_DATA["skills"]),
                json.dumps(SAMPLE_MASTER_DATA["experiences"]),
                json.dumps(SAMPLE_MASTER_DATA["projects"]),
                json.dumps(SAMPLE_MASTER_DATA["education"]),
                json.dumps(SAMPLE_MASTER_DATA["certifications"]),
                raw_txt,
                now,
                now
            ))
            conn.commit()

def get_master_resume(profile_id: Optional[int] = None) -> Optional[Dict[str, Any]]:
    """
    Returns a single Master Resume profile. With no profile_id, returns whichever
    profile is currently flagged is_active=1 (the profile Tab 1 / tailoring / JD
    comparison operate on by default) -- mirrors the api_providers active-flag
    pattern so multiple profiles can coexist with one "selected" at a time.
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        if profile_id is not None:
            cursor.execute("SELECT * FROM master_resumes WHERE id = ?", (profile_id,))
            row = cursor.fetchone()
            if not row:
                return None
        else:
            cursor.execute("SELECT * FROM master_resumes WHERE is_active = 1 LIMIT 1")
            row = cursor.fetchone()
            if not row:
                cursor.execute("SELECT * FROM master_resumes ORDER BY id ASC LIMIT 1")
                row = cursor.fetchone()
            if not row:
                ensure_sample_master_resume()
                cursor.execute("SELECT * FROM master_resumes WHERE is_active = 1 LIMIT 1")
                row = cursor.fetchone()
            if not row:
                return None

        d = dict(row)
        try:
            d["skills"] = json.loads(d.get("skills_json", "{}"))
        except Exception:
            d["skills"] = {}
        try:
            d["experiences"] = json.loads(d.get("experiences_json", "[]"))
        except Exception:
            d["experiences"] = []
        try:
            d["projects"] = json.loads(d.get("projects_json", "[]"))
        except Exception:
            d["projects"] = []
        try:
            d["education"] = json.loads(d.get("education_json", "[]"))
        except Exception:
            d["education"] = []
        try:
            d["certifications"] = json.loads(d.get("certifications_json", "[]"))
        except Exception:
            d["certifications"] = []

        return d

def save_master_resume(data: Dict[str, Any], profile_id: Optional[int] = None) -> Dict[str, Any]:
    now = datetime.now().isoformat()
    raw_txt = build_raw_master_text(data)

    # Only overwrite profile_name when the caller explicitly provided a non-empty
    # one (Rename, or the create/duplicate flows). Resume sync/derive payloads
    # never include this key, so uploading or merging a resume can no longer
    # silently rename a profile out from under the user -- see save below.
    incoming_profile_name = (data.get("profile_name") or "").strip()
    full_name = data.get("full_name", "").strip()
    email = data.get("email", "").strip()
    phone = data.get("phone", "").strip()
    location = data.get("location", "").strip()
    linkedin = data.get("linkedin", "").strip()
    github = data.get("github", "").strip()
    summary = data.get("summary", "").strip()

    skills_json = json.dumps(data.get("skills", {}))
    experiences_json = json.dumps(data.get("experiences", []))
    projects_json = json.dumps(data.get("projects", []))
    education_json = json.dumps(data.get("education", []))
    certifications_json = json.dumps(data.get("certifications", []))

    with get_connection() as conn:
        cursor = conn.cursor()
        if profile_id is not None:
            cursor.execute("SELECT id, is_locked FROM master_resumes WHERE id = ?", (profile_id,))
            existing = cursor.fetchone()
            if not existing:
                raise ValueError(f"Master Profile {profile_id} not found.")
        else:
            cursor.execute("SELECT id, is_locked FROM master_resumes WHERE is_active = 1 LIMIT 1")
            existing = cursor.fetchone()
            if not existing:
                cursor.execute("SELECT id, is_locked FROM master_resumes ORDER BY id ASC LIMIT 1")
                existing = cursor.fetchone()

        if existing and existing[1]:
            raise ValueError("The Sample Profile is read-only. Duplicate it first to make an editable copy.")

        if existing:
            m_id = existing[0]
            if incoming_profile_name:
                profile_name = incoming_profile_name
            else:
                cursor.execute("SELECT profile_name FROM master_resumes WHERE id = ?", (m_id,))
                profile_name = cursor.fetchone()[0]
            cursor.execute("""
                UPDATE master_resumes SET
                    profile_name = ?, full_name = ?, email = ?, phone = ?, location = ?,
                    linkedin = ?, github = ?, summary = ?, skills_json = ?, experiences_json = ?,
                    projects_json = ?, education_json = ?, certifications_json = ?, raw_text = ?,
                    updated_at = ?
                WHERE id = ?
            """, (
                profile_name, full_name, email, phone, location, linkedin, github,
                summary, skills_json, experiences_json, projects_json, education_json,
                certifications_json, raw_txt, now, m_id
            ))
        else:
            profile_name = incoming_profile_name or (f"{full_name}'s Master Profile" if full_name else "Master Profile")
            cursor.execute("""
                INSERT INTO master_resumes (
                    profile_name, full_name, email, phone, location, linkedin, github,
                    summary, skills_json, experiences_json, projects_json, education_json,
                    certifications_json, raw_text, is_active, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?, ?)
            """, (
                profile_name, full_name, email, phone, location, linkedin, github,
                summary, skills_json, experiences_json, projects_json, education_json,
                certifications_json, raw_txt, now, now
            ))
            m_id = cursor.lastrowid

        conn.commit()
        return get_master_resume(m_id)

def reset_sample_master_resume(profile_id: Optional[int] = None) -> Dict[str, Any]:
    """
    Resets a single profile (the active one by default) back to the rich sample
    data. Only ever touches that one row -- it must NOT wipe other saved profiles.
    """
    target = get_master_resume(profile_id)
    if not target:
        if profile_id is not None:
            raise ValueError(f"Master Profile {profile_id} not found.")
        ensure_sample_master_resume()
        return get_master_resume()
    return save_master_resume(SAMPLE_MASTER_DATA, profile_id=target["id"])

def is_sample_master_profile(current: Optional[Dict[str, Any]]) -> bool:
    return bool(current) and (
        current.get("full_name") == "Alexander Rivera" or
        "alexander" in str(current.get("email", "")).lower() or
        "alex.rivera" in str(current.get("email", "")).lower()
    )

def merge_master_resume_data(current: Dict[str, Any], derived: Dict[str, Any]) -> Dict[str, Any]:
    """
    Merges a freshly derived/extracted Master Resume payload into the existing one
    additively: identity fields are only overwritten when the derived value is
    non-empty, and skills/experiences/projects/education/certifications are unioned
    with de-duplication rather than replaced, so re-running an extraction (e.g. via
    "Clean & Fill with LLM") never erases previously captured detail for other
    companies/projects.
    """
    merged = dict(current)
    if derived.get("full_name") and derived["full_name"] != "Candidate":
        merged["full_name"] = derived["full_name"]
        # profile_name is intentionally left untouched -- it's the user's own
        # label for this profile (e.g. "Delivery Manager"), not derived content.
    if derived.get("email"):
        merged["email"] = derived["email"]
    if derived.get("phone"):
        merged["phone"] = derived["phone"]
    if derived.get("location"):
        merged["location"] = derived["location"]
    if derived.get("linkedin"):
        merged["linkedin"] = derived["linkedin"]
    if derived.get("github"):
        merged["github"] = derived["github"]
    if derived.get("summary"):
        merged["summary"] = derived["summary"]

    # Merge skills categories
    cur_skills = dict(merged.get("skills", {}))
    for cat, s_list in derived.get("skills", {}).items():
        if cat in cur_skills:
            combined_skills = list(cur_skills[cat])
            existing_lower = [x.lower() for x in combined_skills]
            for s in s_list:
                if s.lower() not in existing_lower:
                    combined_skills.append(s)
                    existing_lower.append(s.lower())
            cur_skills[cat] = combined_skills
        else:
            cur_skills[cat] = list(s_list)
    merged["skills"] = cur_skills

    # Merge work experiences
    cur_exps = list(merged.get("experiences", []))
    existing_exp_keys = {(e.get("company", "").strip().lower(), e.get("title", "").strip().lower()) for e in cur_exps}
    for exp in derived.get("experiences", []):
        exp_key = (exp.get("company", "").strip().lower(), exp.get("title", "").strip().lower())
        if exp_key not in existing_exp_keys:
            cur_exps.append(exp)
            existing_exp_keys.add(exp_key)
    merged["experiences"] = cur_exps

    # Merge projects
    cur_projs = list(merged.get("projects", []))
    existing_proj_names = {p.get("name", "").strip().lower() for p in cur_projs}
    for proj in derived.get("projects", []):
        p_name = proj.get("name", "").strip()
        if p_name and p_name.lower() not in existing_proj_names:
            new_p = dict(proj)
            new_p["id"] = f"proj-{len(cur_projs) + 1}"
            cur_projs.append(new_p)
            existing_proj_names.add(p_name.lower())
    merged["projects"] = cur_projs

    # Merge education
    cur_edus = list(merged.get("education", []))
    existing_edu_keys = {(e.get("degree", "").strip().lower(), e.get("institution", "").strip().lower()) for e in cur_edus}
    for edu in derived.get("education", []):
        edu_key = (edu.get("degree", "").strip().lower(), edu.get("institution", "").strip().lower())
        if edu_key not in existing_edu_keys:
            cur_edus.append(edu)
            existing_edu_keys.add(edu_key)
    merged["education"] = cur_edus

    # Merge certifications
    cur_certs = list(merged.get("certifications", []))
    existing_certs_lower = [c.lower() for c in cur_certs]
    for c in derived.get("certifications", []):
        if c.lower() not in existing_certs_lower:
            cur_certs.append(c)
            existing_certs_lower.append(c.lower())
    merged["certifications"] = cur_certs

    return merged

def sync_master_resume_from_ats(ats_json_data: Dict[str, Any], merge: bool = False) -> Dict[str, Any]:
    from app.parsers.ats_normalizer import derive_master_resume_from_ats_json
    derived = derive_master_resume_from_ats_json(ats_json_data)

    current = get_master_resume()
    if merge and current and not is_sample_master_profile(current):
        return save_master_resume(merge_master_resume_data(current, derived))
    else:
        # Direct derivation / overwrite
        return save_master_resume(derived)

# ================= MASTER RESUME PROFILE MANAGEMENT (MULTI-PROFILE) =================

def get_all_master_resume_profiles() -> List[Dict[str, Any]]:
    """Lightweight list of every saved Master Resume profile, active one first."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM master_resumes ORDER BY is_active DESC, updated_at DESC")
        rows = cursor.fetchall()

    profiles = []
    for row in rows:
        d = dict(row)
        try:
            exp_count = len(json.loads(d.get("experiences_json", "[]")))
        except Exception:
            exp_count = 0
        try:
            proj_count = len(json.loads(d.get("projects_json", "[]")))
        except Exception:
            proj_count = 0
        profiles.append({
            "id": d["id"],
            "profile_name": d["profile_name"],
            "full_name": d["full_name"],
            "email": d["email"],
            "is_active": bool(d["is_active"]),
            "is_locked": bool(d.get("is_locked", 0)),
            "experience_count": exp_count,
            "project_count": proj_count,
            "updated_at": d["updated_at"],
        })
    return profiles

def create_master_resume_profile(profile_name: str, clone_from_id: Optional[int] = None) -> Dict[str, Any]:
    """
    Creates a new Master Resume profile and makes it the active one. If
    clone_from_id is given, the new profile starts as a copy of that profile's
    content (useful for "Data Science focus" vs "Backend focus" variants of the
    same candidate) -- otherwise it starts blank.
    """
    profile_name = (profile_name or "").strip() or "New Master Profile"
    now = datetime.now().isoformat()
    source = get_master_resume(clone_from_id) if clone_from_id is not None else None
    data = dict(source) if source else {}

    full_name = data.get("full_name", "")
    email = data.get("email", "")
    phone = data.get("phone", "")
    location = data.get("location", "")
    linkedin = data.get("linkedin", "")
    github = data.get("github", "")
    summary = data.get("summary", "")
    skills_json = json.dumps(data.get("skills", {}))
    experiences_json = json.dumps(data.get("experiences", []))
    projects_json = json.dumps(data.get("projects", []))
    education_json = json.dumps(data.get("education", []))
    certifications_json = json.dumps(data.get("certifications", []))
    raw_txt = build_raw_master_text(data) if source else ""

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE master_resumes SET is_active = 0")
        cursor.execute("""
            INSERT INTO master_resumes (
                profile_name, full_name, email, phone, location, linkedin, github,
                summary, skills_json, experiences_json, projects_json, education_json,
                certifications_json, raw_text, is_active, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?, ?)
        """, (
            profile_name, full_name, email, phone, location, linkedin, github,
            summary, skills_json, experiences_json, projects_json, education_json,
            certifications_json, raw_txt, now, now
        ))
        new_id = cursor.lastrowid
        conn.commit()

    return get_master_resume(new_id)

def set_active_master_resume_profile(profile_id: int) -> Optional[Dict[str, Any]]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM master_resumes WHERE id = ?", (profile_id,))
        if not cursor.fetchone():
            return None
        cursor.execute("UPDATE master_resumes SET is_active = 0")
        cursor.execute("UPDATE master_resumes SET is_active = 1 WHERE id = ?", (profile_id,))
        conn.commit()
    return get_master_resume(profile_id)

def delete_master_resume_profile(profile_id: int) -> Dict[str, Any]:
    """
    Deletes a profile. Always keeps at least one profile around. If the deleted
    profile was active, the most recently updated remaining profile becomes active.
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM master_resumes")
        if cursor.fetchone()[0] <= 1:
            raise ValueError("Cannot delete the only remaining Master Profile.")

        cursor.execute("SELECT is_active, is_locked FROM master_resumes WHERE id = ?", (profile_id,))
        row = cursor.fetchone()
        if not row:
            raise ValueError(f"Master Profile {profile_id} not found.")
        if row[1]:
            raise ValueError("The built-in Sample Profile can't be deleted.")
        was_active = bool(row[0])

        cursor.execute("DELETE FROM master_resumes WHERE id = ?", (profile_id,))

        new_active_id = None
        if was_active:
            # Prefer a real (unlocked) profile over the read-only Sample Profile.
            cursor.execute("SELECT id FROM master_resumes WHERE is_locked = 0 ORDER BY updated_at DESC LIMIT 1")
            nxt = cursor.fetchone()
            if not nxt:
                cursor.execute("SELECT id FROM master_resumes ORDER BY updated_at DESC LIMIT 1")
                nxt = cursor.fetchone()
            if nxt:
                new_active_id = nxt[0]
                cursor.execute("UPDATE master_resumes SET is_active = 1 WHERE id = ?", (new_active_id,))

        conn.commit()
    return {"deleted_id": profile_id, "new_active_id": new_active_id}

SAMPLE_PROFILE_NAME = "Sample Profile (Read-Only Reference)"

def get_or_create_locked_sample_profile() -> Dict[str, Any]:
    """
    Returns the single, permanent Sample Profile, creating it once if it doesn't
    exist yet. Flagged is_locked=1 so it can never be deleted, renamed, or edited
    in place -- "Load Sample Master" activates this fixed profile instead of
    overwriting whichever profile the user currently has active with demo data.
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM master_resumes WHERE is_locked = 1 LIMIT 1")
        row = cursor.fetchone()
    if row:
        return get_master_resume(row[0])

    now = datetime.now().isoformat()
    raw_txt = build_raw_master_text(SAMPLE_MASTER_DATA)
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO master_resumes (
                profile_name, full_name, email, phone, location, linkedin, github,
                summary, skills_json, experiences_json, projects_json, education_json,
                certifications_json, raw_text, is_active, is_locked, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, 1, ?, ?)
        """, (
            SAMPLE_PROFILE_NAME,
            SAMPLE_MASTER_DATA["full_name"],
            SAMPLE_MASTER_DATA["email"],
            SAMPLE_MASTER_DATA["phone"],
            SAMPLE_MASTER_DATA["location"],
            SAMPLE_MASTER_DATA["linkedin"],
            SAMPLE_MASTER_DATA["github"],
            SAMPLE_MASTER_DATA["summary"],
            json.dumps(SAMPLE_MASTER_DATA["skills"]),
            json.dumps(SAMPLE_MASTER_DATA["experiences"]),
            json.dumps(SAMPLE_MASTER_DATA["projects"]),
            json.dumps(SAMPLE_MASTER_DATA["education"]),
            json.dumps(SAMPLE_MASTER_DATA["certifications"]),
            raw_txt, now, now
        ))
        new_id = cursor.lastrowid
        conn.commit()
    return get_master_resume(new_id)

def activate_sample_profile() -> Dict[str, Any]:
    sample = get_or_create_locked_sample_profile()
    return set_active_master_resume_profile(sample["id"])

# ================= RESUME LEDGER & TRACE FUNCTIONS =================

def add_ledger_entry(data: Dict[str, Any]) -> Dict[str, Any]:
    now = datetime.now().isoformat()
    changes_json = json.dumps(data.get("changes_summary", []))
    ats_json = json.dumps(data.get("ats_json", {}))
    resume_name = data.get("resume_name", "").strip() or data.get("job_title", "").strip() or "Target Role"

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO resume_ledger (
                resume_name, job_title, company, tier, source_type, source_name,
                match_score_before, match_score_after, filename, file_path,
                resume_text, ats_json, changes_summary, application_id, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            resume_name,
            data.get("job_title", "").strip() or "Target Role",
            data.get("company", "").strip() or "Target Company",
            data.get("tier", "Tier 2: Reframing"),
            data.get("source_type", "Current Resume"),
            data.get("source_name", "Resume.docx"),
            float(data.get("match_score_before", 0.0) or 0.0),
            float(data.get("match_score_after", 0.0) or 0.0),
            data.get("filename", "").strip(),
            data.get("file_path", "").strip(),
            data.get("resume_text", "").strip(),
            ats_json,
            changes_json,
            data.get("application_id"),
            now
        ))
        conn.commit()
        ledger_id = cursor.lastrowid
        return get_ledger_entry_by_id(ledger_id)

def get_all_ledger_entries() -> List[Dict[str, Any]]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM resume_ledger ORDER BY id DESC")
        rows = cursor.fetchall()
        entries = []
        for r in rows:
            entry = dict(r)
            try:
                entry["changes_summary"] = json.loads(entry.get("changes_summary", "[]"))
            except Exception:
                entry["changes_summary"] = []
            entries.append(entry)
        return entries

def get_ledger_entry_by_id(ledger_id: int) -> Optional[Dict[str, Any]]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM resume_ledger WHERE id = ?", (ledger_id,))
        row = cursor.fetchone()
        if not row:
            return None
        entry = dict(row)
        try:
            entry["changes_summary"] = json.loads(entry.get("changes_summary", "[]"))
        except Exception:
            entry["changes_summary"] = []
        try:
            entry["ats_json"] = json.loads(entry.get("ats_json", "{}"))
        except Exception:
            entry["ats_json"] = {}
        return entry

def delete_ledger_entry(ledger_id: int) -> bool:
    entry = get_ledger_entry_by_id(ledger_id)
    if not entry:
        return False

    # Remove physical file if present
    file_path = entry.get("file_path", "")
    if file_path and os.path.exists(file_path):
        try:
            os.remove(file_path)
        except Exception:
            pass

    # Also check txt file if docx
    if file_path and file_path.endswith(".docx"):
        txt_path = file_path[:-5] + ".txt"
        if os.path.exists(txt_path):
            try:
                os.remove(txt_path)
            except Exception:
                pass

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM resume_ledger WHERE id = ?", (ledger_id,))
        conn.commit()
        return cursor.rowcount > 0

def link_ledger_to_application(ledger_id: int, app_id: int) -> Optional[Dict[str, Any]]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE resume_ledger SET application_id = ? WHERE id = ?", (app_id, ledger_id))
        conn.commit()
        return get_ledger_entry_by_id(ledger_id)


