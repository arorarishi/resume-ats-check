# ATS Resume Tracker & Career Suite - Desktop Application

A modern, fast, and local-first desktop application designed to optimize your job application workflow, maximize ATS (Applicant Tracking System) keyword alignment, automate resume tailoring, and track recruitment progress.

> 📖 **Architectural Blueprint & AI Guide**: Looking for detailed database schemas, state machines, REST API specs, or instructions for AI assistants like Claude? See [ARCHITECTURE.md](ARCHITECTURE.md).
> 
> 🌐 **Interactive API Documentation**: Access Swagger UI at [http://127.0.0.1:8765/docs](http://127.0.0.1:8765/docs) or ReDoc at [http://127.0.0.1:8765/redoc](http://127.0.0.1:8765/redoc).

### Core Features (8 Integrated Modules):
1. **Master Career Resume Repository (Tab 1)**: Unified, comprehensive career profile preserving all career achievements without arbitrary page length limits or truncation. Supports AI extraction and merging.
2. **Resume Reader & ATS JSON Generator (Tab 2)**: Normalizes PDF, DOCX, and TXT resumes into standard ATS JSON with instant ATS hygiene audits (action verb density, metrics, formatting safety).
3. **Compare JD / Create New Resume (Tab 3)**: Paste any job description to automatically extract Line 1 as the resume name, initialize an entry in the recruitment pipeline (`Stage 1: Wishlist`), and compute an overall ATS Match Score (%).
4. **Side-by-Side Skill Matrix (Tab 4)**: Interactive dual-column table comparing required JD skills vs resume evidence with status indicators (✅ Exact Match, ⚠️ Partial Match, ❌ Missing) and actionable recommendations.
5. **AI Resume Tailor (Tab 5)**: 3-tier tailoring engine (Tier 1: Keyword injection, Tier 2: Action verb reframing, Tier 3: Full Google XYZ STAR accomplishment overhaul) powered by your choice of OpenAI-compatible API or offline heuristic engine.
6. **Resume Version Ledger & DOCX Exporter (Tab 6)**: Version-controlled audit trail of all tailored resumes with one-click Microsoft Word `.docx` download and before/after match score tracking.
7. **Section Suggestion Engine (Tab 7)**: Tailored professional summary rewrites and Google XYZ / STAR bullet point enhancements with one-click copy.
8. **Application Funnel Kanban Board (Tab 8)**: 6-stage recruitment tracker (`Wishlist` ➔ `Resume Screening` ➔ `Recruiter Screening` ➔ `Interview` [multi-round] ➔ `Offer`, plus `Rejected` with rejection stage tracking and notes, restore, and delete).

---

## 🚀 How to Run the Desktop App

### Method 1: One-Click Desktop Launcher (Windows)
Simply double-click the included batch file:
```
run.bat
```
This automatically activates the `.venv` virtual environment and launches the desktop app window.

### Method 2: Command Line Launcher
```bash
git clone https://github.com/arorarishi/resume-ats-check.git
cd resume-ats-check
python -m venv .venv
# Windows: .\.venv\Scripts\activate    macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python main.py
```
The app will launch in a clean, standalone desktop window (using native Edge / Chrome app mode, or your default browser).

---

## 📁 Project Structure

```
resume-ats-check/
├── .venv/                         # Dedicated Python virtual environment
├── requirements.txt               # Dependencies (FastAPI, Uvicorn, PyPDF, python-docx, etc.)
├── run.bat                        # Double-clickable Windows desktop launcher
├── main.py                        # Desktop window launcher & server entrypoint
├── README.md                      # Quickstart guide & user documentation
├── ARCHITECTURE.md                # Authoritative system blueprint & Claude AI guide
├── app/
│   ├── __init__.py
│   ├── server.py                  # FastAPI REST API, routing & static asset delivery
│   ├── database.py                # SQLite ORM, stage migrations & funnel metrics
│   ├── parsers/
│   │   ├── __init__.py
│   │   ├── pdf_parser.py          # PDF text & structure extraction (pypdf)
│   │   ├── docx_parser.py         # DOCX document & table parsing (python-docx)
│   │   ├── ats_normalizer.py      # ATS JSON schema builder & hygiene scoring
│   │   └── resume_exporter.py     # DOCX & TXT tailored resume file generator
│   ├── analyzer/
│   │   ├── __init__.py
│   │   ├── jd_parser.py           # Job description parser & requirement extractor
│   │   ├── matcher.py             # ATS scoring engine & side-by-side skill matrix
│   │   ├── suggester.py           # Tailored summary & Google XYZ bullet rewriter
│   │   ├── tailorer.py            # 3-tier resume tailoring engine (Keyword, Verbs, XYZ)
│   │   └── llm_client.py          # Multi-provider LLM client with local heuristic fallback
│   └── static/                    # Desktop frontend interface
│       ├── index.html             # Single-page dashboard containing 8 tabs & modals
│       ├── css/
│       │   └── style.css          # Dark-mode styling, 6-column Kanban layout & modals
│       └── js/
│           └── app.js             # Client state, live derivations, dropzone & Kanban
├── data/
│   └── applications.db            # Local SQLite database (apps, master resumes, ledger, keys)
└── tests/
    ├── test_stage_pipeline_flow.py# Full pipeline stage transitions (Wishlist -> Offer/Reject)
    ├── test_jobs_found_flow.py    # Line 1 JD derivation, Wishlist stage & ledger logging
    ├── test_master_derivation.py  # Master resume derivation, sync & merging
    ├── test_tailor_and_ledger.py  # 3-tier tailoring engine & DOCX export
    ├── test_server_endpoints.py   # REST API integration tests
    ├── test_pipeline.py           # End-to-end parser + matcher integration tests
    ├── test_pdf.py                # Unit test for PDF parser
    └── test_docx.py               # Unit test for DOCX parser
```


---

## 💡 Key Features Walkthrough

### 1. Master Career Profile Repository (Tab 1)
- **Exhaustive Career Vault**: Store all your professional experiences, projects, skills, education, and credentials without truncation or page length constraints.
- **Smart Derivation & Sync**: Click **"Sync from Current Resume"** to merge incoming resumes, or **"Fill Missing Sections (AI)"** to intelligently structure unstructured career history.

### 2. Resume Reader & ATS JSON Generator (Tab 2)
- **Multi-Format Extraction**: Drop any `.pdf`, `.docx`, or `.txt` resume, or paste raw text.
- **ATS Hygiene Score (0-100)**: Evaluates action verb density, measurable impact/numbers, section heading safety, and contact information presence.
- **ATS Standard JSON**: Inspect, copy, or download the clean normalized JSON profile.

### 3. Compare JD / Create New Resume (Tab 3)
- **First-Line Resume Naming**: Automatically extracts the first line of the pasted job description as the designated resume name.
- **Automatic Funnel Placement**: Automatically creates an application record in `Stage 1: Wishlist`.
- **Instant ATS Scoring**: Computes ATS Match Score (%), Match Tier (Strong / Good / Fair / Low Match), keyword coverage, and identifies missing keywords.

### 4. Side-by-Side Skills Matrix (Tab 4)
- **Interactive Dual-Column View**: Directly correlates required skills against verifiable evidence in your resume.
- **Filterable Status Badges**: Filter by **All**, **Matched (✅)**, **Partial (⚠️)**, or **Missing (❌)**.
- **Actionable Advice**: Contextual guidance on addressing missing keywords naturally.

### 5. AI Resume Tailor (Tab 5)
- **3-Tier Tailoring Pipeline**:
  - **Tier 1 (Keyword Harmonization)**: Lightweight injection of critical missing skills and keyword variations into summary and skills sections.
  - **Tier 2 (Action Verb & Reframing)**: Rewrites weak bullets using domain-specific action verbs and emphasizes relevant past achievements.
  - **Tier 3 (Google XYZ / STAR Overhaul)**: Comprehensive restructuring of achievements into high-impact Google XYZ bullets (*Accomplished [X], as measured by [Y], by doing [Z]*).
- **Inference Options**: Connect your OpenAI, Groq, Anthropic-compatible, or local Ollama API key, or use the built-in offline heuristic engine.

### 6. Resume Version Ledger & DOCX Exporter (Tab 6)
- **Version Audit Trail**: Every tailored resume is version-tracked with before-and-after ATS scores and change summaries.
- **One-Click Word Export**: Download clean, professional, ATS-formatted Microsoft Word (`.docx`) files ready for submission.

### 7. Section Suggestion Engine (Tab 7)
- **Tailored Summary**: Generates ATS-optimized professional summaries targeting the specific role and company.
- **Google XYZ Bullet Point Optimizer**: Converts weak resume bullets into high-impact accomplishments with one-click copy buttons.

### 8. Application Funnel Kanban Board (Tab 8)
- **6-Stage Recruitment Pipeline**:
  1. `Wishlist`: Potential opportunities identified or derived from JD.
  2. `Resume Screening`: Application submitted; waiting for initial ATS/recruiter review (auto-sets `date_applied`).
  3. `Recruiter Screening`: Initial HR/recruiter phone screen.
  4. `Interview`: Active interview loop with multi-round step tracking (e.g. `Round 1: Tech Screen`, `Round 2: System Design`, `Round 3: Hiring Manager`).
  5. `Offer`: Terminal success stage celebrating job offers.
  6. `Rejected`: Terminal rejection stage tracking exact stage where rejected (`rejected_from_stage`) and notes.
- **Card Controls**:
  - `✓ Pass ➔`: Advance application to the next pipeline stage.
  - `Manage Rounds`: In Interview stage, progress to next round or choose quick round presets.
  - `✕ Reject`: Open rejection audit modal to record rejection stage and feedback.
  - `↺ Restore`: Move rejected application back to its previous stage.
  - `🗑 Delete`: Permanently remove application.

---

## 🔍 How to Verify the APIs

The server runs on `http://127.0.0.1:8765`. You can verify and interact with the REST APIs using any of the following methods:

### 1. Interactive Swagger UI (Recommended)
Open your browser and navigate to:
👉 **[http://127.0.0.1:8765/docs](http://127.0.0.1:8765/docs)**
- Provides full interactive testing ("Try it out" button) for every endpoint.
- Inspect request schemas, parameters, and live responses.

### 2. ReDoc Reference UI
Navigate to:
👉 **[http://127.0.0.1:8765/redoc](http://127.0.0.1:8765/redoc)**
- Clean, readable API reference documentation with full model schemas.

### 3. OpenAPI JSON Specification
Access the raw OpenAPI 3.1 schema:
👉 **[http://127.0.0.1:8765/openapi.json](http://127.0.0.1:8765/openapi.json)**

### 4. Quick cURL & PowerShell Examples

#### Server Health Check:
```powershell
Invoke-RestMethod -Uri http://127.0.0.1:8765/health
```

#### Fetch All Applications & Funnel Stats:
```powershell
Invoke-RestMethod -Uri http://127.0.0.1:8765/api/funnel
```

#### Create Resume from JD & Add to Wishlist:
```powershell
$body = @{
    jd_text = "Staff Machine Learning Engineer`nAnthropic / San Francisco`nRequirements: PyTorch, Distributed Systems, Python"
} | ConvertTo-Json

Invoke-RestMethod -Uri http://127.0.0.1:8765/api/jobs/create-resume -Method Post -Body $body -ContentType "application/json"
```

#### Advance Stage / Pass to Next Step:
```powershell
$body = @{
    stage = "Resume Screening"
} | ConvertTo-Json

Invoke-RestMethod -Uri http://127.0.0.1:8765/api/funnel/1/stage -Method Put -Body $body -ContentType "application/json"
```

#### Update Interview Step:
```powershell
$body = @{
    interview_step = "Round 2: System Design"
} | ConvertTo-Json

Invoke-RestMethod -Uri http://127.0.0.1:8765/api/funnel/1/interview-step -Method Put -Body $body -ContentType "application/json"
```

---

## 🤖 Guiding Claude & AI Assistants to Fix or Extend the Code

When asking Claude or another AI assistant to modify, debug, or extend this application, share the following prompt instructions:

### Recommended Prompt for Claude:
```
I am working on the ATS Resume Tracker & Career Suite located in this repository.
Before making any changes, please read ARCHITECTURE.md completely. It contains the authoritative database schema, REST API routes, pipeline state machine, and design rules.

Rules to follow:
1. Environment: Use the existing virtual environment: .\.venv\Scripts\python.exe. Do not attempt to reinstall or create a new virtual environment.
2. Recruitment Stages: The 6 pipeline stages are strictly:
   ["Wishlist", "Resume Screening", "Recruiter Screening", "Interview", "Offer", "Rejected"].
   - "Jobs Found" has been merged into "Wishlist" (Stage 1) and must NOT be reintroduced.
   - Rejections at any stage record rejected_from_stage and move to "Rejected".
   - Cards in the Interview stage support multi-round tracking via interview_step.
   - Every card supports Pass, Reject, and Delete.
3. Database Migrations: Any SQLite schema changes in app/database.py must include backward-compatible ALTER TABLE statements inside init_db() wrapped in try/except blocks.
4. Testing: Before reporting completion, run the relevant automated test scripts:
   .\.venv\Scripts\python.exe tests/test_stage_pipeline_flow.py
   .\.venv\Scripts\python.exe tests/test_jobs_found_flow.py
   .\.venv\Scripts\python.exe tests/test_server_endpoints.py
   .\.venv\Scripts\python.exe tests/test_tailor_and_ledger.py
   .\.venv\Scripts\python.exe tests/test_master_derivation.py
```

### Key Architectural Guidelines for Developers & AI:
- **Backend API (`app/server.py`)**: All API endpoints return standardized JSON. In-memory session state stores the currently active parsed resume and job description.
- **Database Layer (`app/database.py`)**: SQLite with tables `applications`, `master_resumes`, `resume_ledger`, and `api_providers`.
- **Frontend SPA (`app/static/`)**: Vanilla JavaScript SPA with zero build steps or bundlers. UI state is kept in `app.js`. Tab switching is driven by `.nav-tab` buttons matching `#tab-[name]`.
- **ATS Intelligence (`app/analyzer/`)**: Rules-based keyword extraction, n-gram matching, and hygiene scoring, supplemented by LLMs for generative rewrites.
