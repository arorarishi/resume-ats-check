import os
import re
import json
from typing import Optional, Dict, Any
from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Body
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware

from app.database import (
    init_db, get_all_applications, get_application_by_id,
    create_application, update_application, update_application_stage,
    delete_application, get_funnel_stats, get_jobs_found,
    get_all_providers, get_provider_by_id, get_active_provider,
    save_provider, set_active_provider, delete_provider, deactivate_all_providers,
    get_master_resume, save_master_resume, reset_sample_master_resume, sync_master_resume_from_ats,
    merge_master_resume_data, is_sample_master_profile,
    get_all_master_resume_profiles, create_master_resume_profile,
    set_active_master_resume_profile, delete_master_resume_profile,
    activate_sample_profile,
    build_raw_master_text, add_ledger_entry,
    get_all_ledger_entries, get_ledger_entry_by_id, delete_ledger_entry, link_ledger_to_application
)
from app.parsers.pdf_parser import extract_text_from_pdf
from app.parsers.docx_parser import extract_text_from_docx
from app.parsers.ats_normalizer import normalize_to_ats_json
from app.analyzer.jd_parser import parse_job_description
from app.analyzer.matcher import compare_resume_to_jd, compare_resume_to_jd_async
from app.analyzer.suggester import generate_resume_suggestions_async
from app.analyzer.rubric_auditor import audit_resume_rubric_async
from app.analyzer.llm_client import test_provider_connection, clean_and_extract_master_resume_with_llm
from app.analyzer.tailorer import tailor_resume_async

# Initialize DB on startup
init_db()

app = FastAPI(title="Resume ATS Check", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
os.makedirs(STATIC_DIR, exist_ok=True)

# In-memory session cache for current active resume & JD
current_session_data = {
    "resume": None,
    "jd": None,
    "jd_text": "",
    "comparison": None
}

@app.get("/api/health")
async def health():
    return {"status": "ok", "app": "ATS Resume Suite Desktop"}

# ================= JOBS FOUND & RESUME CREATION FROM JD =================

@app.post("/api/jobs/create-resume")
async def create_resume_from_jd_endpoint(payload: Dict[str, Any] = Body(...)):
    """
    Creates a new resume from a pasted Job Description:
    1. Extracts the first line of the JD as the Resume Name.
    2. Automatically creates an application record in the Funnel with stage 'Jobs Found'.
    3. Runs the ATS comparison against the candidate's Master Profile.
    4. Creates an initial entry in the Resume Ledger.
    """
    try:
        jd_text = payload.get("jd_text", "").strip()
        if not jd_text:
            raise HTTPException(status_code=400, detail="Please provide Job Description text.")

        # 1. Derive Resume Name from the first non-empty line of the JD
        lines = [l.strip() for l in jd_text.splitlines() if l.strip()]
        first_line = lines[0] if lines else "New Resume"
        # Clean common prefixes like 'Job Title:', 'Role:', 'Position:' if present
        cleaned_first_line = re.sub(r'^(?:job\s*title|position|role)\s*[:\-]\s*', '', first_line, flags=re.I).strip()
        resume_name = cleaned_first_line or first_line

        # 2. Parse JD to detect company, role, skills, requirements
        jd_data = parse_job_description(jd_text)
        detected_company = payload.get("company", "").strip() or jd_data.get("company") or "Target Company"
        job_url = payload.get("job_url", "").strip()
        location = payload.get("location", "").strip()
        salary = payload.get("salary", "").strip()

        # 3. Retrieve or build active resume data from session or Master Resume
        resume_data = current_session_data.get("resume")
        if not resume_data or not resume_data.get("ats_json"):
            cur_master = get_master_resume()
            if cur_master:
                raw_txt = cur_master.get("raw_text") or build_raw_master_text(cur_master)
                resume_data = normalize_to_ats_json(raw_txt)
                current_session_data["resume"] = resume_data
                current_session_data["raw_resume_text"] = raw_txt

        if not resume_data:
            cur_master = reset_sample_master_resume()
            raw_txt = cur_master.get("raw_text") or build_raw_master_text(cur_master)
            resume_data = normalize_to_ats_json(raw_txt)
            current_session_data["resume"] = resume_data
            current_session_data["raw_resume_text"] = raw_txt

        # 4. Run comparison against resume
        current_session_data["jd"] = jd_data
        current_session_data["jd_text"] = jd_text
        comparison = await compare_resume_to_jd_async(resume_data, jd_data, jd_text)
        current_session_data["comparison"] = comparison

        match_score = float(comparison.get("match_score", 0.0))

        # 5. Automatically create Job in Funnel under stage "Wishlist"
        app_data = {
            "company": detected_company,
            "role": resume_name,
            "location": location,
            "stage": "Wishlist",
            "salary": salary,
            "job_url": job_url,
            "jd_text": jd_text,
            "match_score": match_score,
            "resume_filename": f"{resume_name}.docx",
            "notes": f"Created via Wishlist. First line of JD: {first_line}"
        }
        created_app = create_application(app_data)
        app_id = created_app["id"]

        # 6. Add initial entry to Resume Ledger
        ledger_data = {
            "resume_name": resume_name,
            "job_title": resume_name,
            "company": detected_company,
            "tier": "Initial Base Match",
            "source_type": "Master Resume",
            "source_name": "Master_Career_Profile",
            "match_score_before": match_score,
            "match_score_after": match_score,
            "filename": f"{resume_name.replace(' ', '_')}_Base.docx",
            "file_path": "",
            "resume_text": resume_data.get("ats_json", {}).get("raw_text", ""),
            "ats_json": resume_data.get("ats_json", {}),
            "changes_summary": [{
                "section": "Initial Setup",
                "type": "JD Matched",
                "detail": f"Resume initialized and matched for {detected_company} ({resume_name})."
            }],
            "application_id": app_id
        }
        ledger_entry = add_ledger_entry(ledger_data)

        stats = get_funnel_stats()

        return {
            "success": True,
            "resume_name": resume_name,
            "first_line_jd": first_line,
            "application": created_app,
            "ledger_entry": ledger_entry,
            "comparison": comparison,
            "jd_parsed": jd_data,
            "funnel_stats": stats,
            "message": f"Resume '{resume_name}' created, added to Wishlist funnel, and compared!"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create resume from JD: {str(e)}")

@app.get("/api/jobs/found")
async def list_jobs_found():
    jobs = get_jobs_found()
    return {"jobs": jobs, "count": len(jobs)}

@app.post("/api/resume/parse")
async def parse_resume(
    file: Optional[UploadFile] = File(None),
    raw_text: Optional[str] = Form(None)
):
    try:
        text = ""
        filename = "Pasted_Resume.txt"

        if file:
            filename = file.filename or "resume"
            contents = await file.read()
            ext = os.path.splitext(filename)[1].lower()

            if ext == ".pdf":
                pdf_res = extract_text_from_pdf(contents)
                text = pdf_res["text"]
            elif ext in [".docx", ".doc"]:
                docx_res = extract_text_from_docx(contents)
                text = docx_res["text"]
            else:
                text = contents.decode("utf-8", errors="ignore")
        elif raw_text:
            text = raw_text.strip()
        else:
            raise HTTPException(status_code=400, detail="Please provide a resume file (PDF/DOCX) or paste raw text.")

        if not text:
            raise HTTPException(status_code=400, detail="Failed to extract any text from the provided resume.")

        result = normalize_to_ats_json(text, filename=filename)
        current_session_data["resume"] = result

        # Automatically derive and populate Master Resume from uploaded resume
        try:
            updated_master = sync_master_resume_from_ats(result["ats_json"], merge=False)
            result["master_synced"] = True
            result["master_profile_name"] = updated_master.get("profile_name")
            result["master_projects_count"] = len(updated_master.get("projects", []))
        except Exception as e:
            result["master_synced"] = False
            result["master_sync_error"] = str(e)

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error parsing resume: {str(e)}")

@app.get("/api/resume/active")
async def get_active_resume():
    active = current_session_data.get("resume")
    if not active:
        cur_master = get_master_resume()
        if cur_master:
            raw_txt = cur_master.get("raw_text") or build_raw_master_text(cur_master)
            active = normalize_to_ats_json(raw_txt)
            current_session_data["resume"] = active
            current_session_data["raw_resume_text"] = raw_txt
    if active:
        return active
    return {"ats_json": {}, "hygiene_report": {}, "raw_text": ""}

@app.get("/api/master-resume/ats-view")
async def get_master_resume_ats_view():
    """
    Read-only ATS Hygiene/JSON view of the Master Resume. Always recomputed fresh
    from the current Master Resume (no session caching, no write-back), so Tab 2
    stays in sync after edits without needing a separate resume upload.
    """
    cur_master = get_master_resume()
    if not cur_master:
        return {"ats_json": {}, "hygiene_report": {}, "raw_text": ""}
    raw_txt = cur_master.get("raw_text") or build_raw_master_text(cur_master)
    return normalize_to_ats_json(raw_txt, filename="Master Resume")

@app.post("/api/resume/compare")
async def compare_jd(payload: Dict[str, Any] = Body(...)):
    try:
        jd_text = payload.get("jd_text", "").strip()
        if not jd_text:
            raise HTTPException(status_code=400, detail="Please paste a job description.")

        resume_data = payload.get("resume_data") or current_session_data.get("resume")
        if not resume_data or not resume_data.get("ats_json"):
            cur_master = get_master_resume()
            if cur_master:
                raw_txt = cur_master.get("raw_text") or build_raw_master_text(cur_master)
                norm_res = normalize_to_ats_json(raw_txt)
                resume_data = norm_res
                current_session_data["resume"] = resume_data
                current_session_data["raw_resume_text"] = raw_txt

        if not resume_data:
            raise HTTPException(status_code=400, detail="No resume or Master Profile found. Please import a resume or populate your Master Resume in Tab 1.")

        jd_data = parse_job_description(jd_text)
        current_session_data["jd"] = jd_data
        current_session_data["jd_text"] = jd_text

        comparison = await compare_resume_to_jd_async(resume_data, jd_data, jd_text)
        current_session_data["comparison"] = comparison

        return {
            "jd_parsed": jd_data,
            "comparison": comparison
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error comparing resume to JD: {str(e)}")

@app.post("/api/resume/suggest")
async def suggest_changes(payload: Dict[str, Any] = Body(...)):
    try:
        resume_data = payload.get("resume_data") or current_session_data.get("resume")
        if not resume_data or not resume_data.get("ats_json"):
            cur_master = get_master_resume()
            if cur_master:
                raw_txt = cur_master.get("raw_text") or build_raw_master_text(cur_master)
                norm_res = normalize_to_ats_json(raw_txt)
                resume_data = norm_res
                current_session_data["resume"] = resume_data
                current_session_data["raw_resume_text"] = raw_txt

        jd_data = payload.get("jd_data") or current_session_data.get("jd")
        comparison = payload.get("comparison") or current_session_data.get("comparison")

        if not resume_data or not jd_data or not comparison:
            raise HTTPException(status_code=400, detail="Missing required resume, JD, or comparison data.")

        suggestions = await generate_resume_suggestions_async(resume_data, jd_data, comparison)
        return suggestions
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating suggestions: {str(e)}")

@app.post("/api/resume/audit-rubric")
async def audit_resume_rubric_endpoint(payload: Dict[str, Any] = Body(...)):
    """
    7-category resume quality score (Clarity & Structure, Role & Level Positioning,
    Impact & Achievements, Skills & Relevance, Career Trajectory, Language &
    Professionalism, ATS & Formatting Hygiene) - independent of any specific JD.
    """
    try:
        resume_data = payload.get("resume_data") or current_session_data.get("resume")
        if not resume_data or not resume_data.get("ats_json"):
            cur_master = get_master_resume()
            if cur_master:
                raw_txt = cur_master.get("raw_text") or build_raw_master_text(cur_master)
                resume_data = normalize_to_ats_json(raw_txt)
                current_session_data["resume"] = resume_data
                current_session_data["raw_resume_text"] = raw_txt

        if not resume_data or not resume_data.get("ats_json"):
            raise HTTPException(status_code=400, detail="No resume or Master Profile found. Please import a resume or populate your Master Resume in Tab 1.")

        result = await audit_resume_rubric_async(resume_data)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating rubric audit: {str(e)}")

# ================= AI RESUME TAILORING & FIX ENDPOINTS =================

@app.post("/api/resume/tailor")
async def tailor_resume_endpoint(payload: Dict[str, Any] = Body(...)):
    try:
        tier = payload.get("tier", "tier2")
        source_type = payload.get("source_type", "current")
        custom_instructions = payload.get("custom_instructions", "").strip()
        excluded_keywords = payload.get("excluded_keywords") or []

        resume_data = payload.get("resume_data") or current_session_data.get("resume")
        jd_data = payload.get("jd_data") or current_session_data.get("jd")
        comparison = payload.get("comparison") or current_session_data.get("comparison")
        jd_text = payload.get("jd_text", "").strip() or current_session_data.get("jd_text", "")

        if not jd_data or not jd_text:
            raise HTTPException(status_code=400, detail="Please paste and compare a job description first.")

        if source_type != "master" and not resume_data:
            raise HTTPException(status_code=400, detail="No active resume data found. Please parse a resume or select Master Resume as source.")

        if not comparison:
            comparison = await compare_resume_to_jd_async(resume_data or {}, jd_data, jd_text)

        if excluded_keywords:
            excluded_lower = {kw.strip().lower() for kw in excluded_keywords if kw and kw.strip()}
            comparison = dict(comparison)
            comparison["top_missing_keywords"] = [
                kw for kw in comparison.get("top_missing_keywords", [])
                if kw.strip().lower() not in excluded_lower
            ]

        result = await tailor_resume_async(
            source_type=source_type,
            tier=tier,
            current_resume_data=resume_data,
            jd_data=jd_data,
            comparison_data=comparison,
            jd_text=jd_text,
            custom_instructions=custom_instructions
        )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Tailoring failed: {str(e)}")

@app.get("/api/resume/download/{ledger_id}/docx")
async def download_resume_docx(ledger_id: int):
    entry = get_ledger_entry_by_id(ledger_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Ledger entry not found")
    
    file_path = entry.get("file_path", "")
    if not file_path or not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="DOCX file not found on server disk")
    
    return FileResponse(
        file_path,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        filename=entry.get("filename", f"Resume_{ledger_id}.docx")
    )

@app.get("/api/resume/download/{ledger_id}/txt")
async def download_resume_txt(ledger_id: int):
    entry = get_ledger_entry_by_id(ledger_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Ledger entry not found")
    
    file_path = entry.get("file_path", "")
    txt_path = file_path[:-5] + ".txt" if file_path.endswith(".docx") else file_path + ".txt"
    
    if not os.path.exists(txt_path):
        resume_text = entry.get("resume_text", "")
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(resume_text)
            
    return FileResponse(
        txt_path,
        media_type="text/plain",
        filename=entry.get("filename", f"Resume_{ledger_id}.docx").replace(".docx", ".txt")
    )

# ================= MASTER RESUME ENDPOINTS =================

@app.get("/api/master-resume/profiles")
async def list_master_resume_profiles_endpoint():
    return {"profiles": get_all_master_resume_profiles()}

@app.post("/api/master-resume/profiles")
async def create_master_resume_profile_endpoint(payload: Dict[str, Any] = Body(...)):
    try:
        profile_name = payload.get("profile_name", "").strip()
        if not profile_name:
            raise HTTPException(status_code=400, detail="profile_name is required.")
        clone_from_id = payload.get("clone_from_id")

        created = create_master_resume_profile(profile_name, clone_from_id=clone_from_id)
        raw_txt = created.get("raw_text") or build_raw_master_text(created)
        current_session_data["resume"] = normalize_to_ats_json(raw_txt)
        current_session_data["raw_resume_text"] = raw_txt

        return {"success": True, "master_resume": created, "profiles": get_all_master_resume_profiles()}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create master profile: {str(e)}")

@app.post("/api/master-resume/profiles/{profile_id}/activate")
async def activate_master_resume_profile_endpoint(profile_id: int):
    activated = set_active_master_resume_profile(profile_id)
    if not activated:
        raise HTTPException(status_code=404, detail="Master Profile not found")

    raw_txt = activated.get("raw_text") or build_raw_master_text(activated)
    current_session_data["resume"] = normalize_to_ats_json(raw_txt)
    current_session_data["raw_resume_text"] = raw_txt

    return {"success": True, "master_resume": activated, "profiles": get_all_master_resume_profiles()}

@app.delete("/api/master-resume/profiles/{profile_id}")
async def delete_master_resume_profile_endpoint(profile_id: int):
    try:
        result = delete_master_resume_profile(profile_id)
        if result.get("new_active_id"):
            new_active = get_master_resume(result["new_active_id"])
            if new_active:
                raw_txt = new_active.get("raw_text") or build_raw_master_text(new_active)
                current_session_data["resume"] = normalize_to_ats_json(raw_txt)
                current_session_data["raw_resume_text"] = raw_txt
        return {"success": True, **result, "profiles": get_all_master_resume_profiles()}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/master-resume/sample-profile/activate")
async def activate_sample_profile_endpoint():
    """
    Switches to the permanent, read-only Sample Profile (creating it once if it
    doesn't exist yet) -- the safe replacement for the old "reset to sample"
    behavior, which used to overwrite whatever profile was currently active.
    """
    activated = activate_sample_profile()
    raw_txt = activated.get("raw_text") or build_raw_master_text(activated)
    current_session_data["resume"] = normalize_to_ats_json(raw_txt)
    current_session_data["raw_resume_text"] = raw_txt
    return {"success": True, "master_resume": activated, "profiles": get_all_master_resume_profiles()}

@app.get("/api/master-resume")
async def get_master_resume_endpoint():
    m = get_master_resume()
    if not m:
        raise HTTPException(status_code=404, detail="Master resume not found")
    return {"master_resume": m}

@app.post("/api/master-resume")
async def save_master_resume_endpoint(payload: Dict[str, Any] = Body(...)):
    try:
        saved = save_master_resume(payload)
        raw_txt = saved.get("raw_text") or build_raw_master_text(saved)
        current_session_data["resume"] = normalize_to_ats_json(raw_txt)
        current_session_data["raw_resume_text"] = raw_txt
        return {"success": True, "master_resume": saved}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save master resume: {str(e)}")

@app.post("/api/master-resume/reset-sample")
async def reset_master_resume_endpoint():
    try:
        reset = reset_sample_master_resume()
        raw_txt = reset.get("raw_text") or build_raw_master_text(reset)
        current_session_data["resume"] = normalize_to_ats_json(raw_txt)
        current_session_data["raw_resume_text"] = raw_txt
        return {"success": True, "master_resume": reset}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to reset master resume: {str(e)}")

@app.post("/api/master-resume/sync-current")
async def sync_current_resume_endpoint(payload: Dict[str, Any] = Body(default={})):
    try:
        merge = payload.get("merge", False)
        active_resume = current_session_data.get("resume")
        if not active_resume or not active_resume.get("ats_json"):
            raise HTTPException(status_code=400, detail="No active resume found in session. Please upload or parse a resume first.")

        updated = sync_master_resume_from_ats(active_resume["ats_json"], merge=merge)
        action_word = "merged" if merge else "derived and updated"
        return {
            "success": True,
            "master_resume": updated,
            "message": f"Master Resume successfully {action_word} from active resume ({updated.get('full_name')})."
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to sync master resume: {str(e)}")

@app.post("/api/master-resume/clean-with-llm")
async def clean_master_resume_with_llm_endpoint(payload: Dict[str, Any] = Body(default={})):
    try:
        raw_text = payload.get("raw_text", "").strip()
        if not raw_text and "master_data" in payload and isinstance(payload["master_data"], dict):
            raw_text = build_raw_master_text(payload["master_data"])

        if not raw_text:
            active_resume = current_session_data.get("resume")
            if active_resume and active_resume.get("ats_json", {}).get("raw_text"):
                raw_text = active_resume["ats_json"]["raw_text"]
            elif active_resume and active_resume.get("raw_text"):
                raw_text = active_resume["raw_text"]
            else:
                cur_master = get_master_resume()
                if cur_master:
                    raw_text = cur_master.get("raw_text") or build_raw_master_text(cur_master)

        if not raw_text:
            raise HTTPException(status_code=400, detail="No resume or Master Profile text available to clean. Please import a resume or click 'Load Rich Sample Master'.")

        current_master = get_master_resume()
        can_merge = bool(current_master) and not is_sample_master_profile(current_master)

        llm_data = await clean_and_extract_master_resume_with_llm(raw_text)
        if llm_data and isinstance(llm_data, dict) and llm_data.get("full_name"):
            to_save = merge_master_resume_data(current_master, llm_data) if can_merge else llm_data
            updated = save_master_resume(to_save)
            action_word = "merged into" if can_merge else "extracted and filled for"
            return {
                "success": True,
                "master_resume": updated,
                "source": "LLM Inference Engine",
                "message": f"Master Resume cleanly {action_word} {updated.get('full_name')} without character cut-offs."
            }
        else:
            # Fallback to enhanced heuristic normalization
            norm = normalize_to_ats_json(raw_text)
            updated = sync_master_resume_from_ats(norm["ats_json"], merge=can_merge)
            return {
                "success": True,
                "master_resume": updated,
                "source": "Enhanced Heuristic Engine",
                "message": "AI Provider offline or response invalid. Cleaned with enhanced local engine (zero character truncation)."
            }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error cleaning Master Resume with LLM: {str(e)}")

# ================= RESUME LEDGER ENDPOINTS =================

@app.get("/api/resume/ledger")
async def list_resume_ledger():
    entries = get_all_ledger_entries()
    return {"entries": entries}

@app.get("/api/resume/ledger/{ledger_id}")
async def get_single_ledger_entry(ledger_id: int):
    entry = get_ledger_entry_by_id(ledger_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Ledger entry not found")
    return {"entry": entry}

@app.delete("/api/resume/ledger/{ledger_id}")
async def remove_ledger_entry(ledger_id: int):
    deleted = delete_ledger_entry(ledger_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Ledger entry not found")
    return {"success": True}

@app.post("/api/resume/ledger/{ledger_id}/link-funnel")
async def link_ledger_entry(ledger_id: int, payload: Dict[str, Any] = Body(...)):
    app_id = payload.get("application_id")
    if not app_id:
        raise HTTPException(status_code=400, detail="Missing 'application_id' in body")
    updated = link_ledger_to_application(ledger_id, int(app_id))
    if not updated:
        raise HTTPException(status_code=404, detail="Ledger entry not found")
    return {"success": True, "entry": updated}

# FUNNEL ENDPOINTS
@app.get("/api/funnel")
async def list_funnel(stage: Optional[str] = None):
    apps = get_all_applications(stage_filter=stage)
    stats = get_funnel_stats()
    return {
        "applications": apps,
        "stats": stats
    }

@app.post("/api/funnel")
async def add_application(payload: Dict[str, Any] = Body(...)):
    try:
        new_app = create_application(payload)
        stats = get_funnel_stats()
        return {"application": new_app, "stats": stats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create application: {str(e)}")

@app.put("/api/funnel/{app_id}")
async def update_app(app_id: int, payload: Dict[str, Any] = Body(...)):
    try:
        updated = update_application(app_id, payload)
        if not updated:
            raise HTTPException(status_code=404, detail="Application not found")
        stats = get_funnel_stats()
        return {"application": updated, "stats": stats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update application: {str(e)}")

@app.put("/api/funnel/{app_id}/stage")
async def change_stage(app_id: int, payload: Dict[str, Any] = Body(...)):
    new_stage = payload.get("stage")
    rejected_from_stage = payload.get("rejected_from_stage", "")
    interview_step = payload.get("interview_step", "")
    if not new_stage:
        raise HTTPException(status_code=400, detail="Missing 'stage' in request body")
    updated = update_application_stage(
        app_id,
        new_stage,
        rejected_from_stage=rejected_from_stage,
        interview_step=interview_step
    )
    if not updated:
        raise HTTPException(status_code=400, detail="Invalid stage or application not found")
    stats = get_funnel_stats()
    return {"application": updated, "stats": stats}

@app.put("/api/funnel/{app_id}/interview-step")
async def update_interview_step_endpoint(app_id: int, payload: Dict[str, Any] = Body(...)):
    step = payload.get("interview_step", "").strip()
    if not step:
        raise HTTPException(status_code=400, detail="Missing 'interview_step' in request body")
    updated = update_application(app_id, {"interview_step": step})
    if not updated:
        raise HTTPException(status_code=404, detail="Application not found")
    stats = get_funnel_stats()
    return {"application": updated, "stats": stats}

@app.delete("/api/funnel/{app_id}")
async def remove_application(app_id: int):
    deleted = delete_application(app_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Application not found")
    stats = get_funnel_stats()
    return {"success": True, "stats": stats}

# ================= AI PROVIDER SETTINGS ENDPOINTS =================

@app.get("/api/settings/providers")
async def list_providers():
    providers = get_all_providers()
    active = get_active_provider()
    return {
        "providers": providers,
        "active_provider_id": active["id"] if active else None
    }

@app.get("/api/settings/providers/{provider_id}")
async def get_single_provider(provider_id: int):
    p = get_provider_by_id(provider_id)
    if not p:
        raise HTTPException(status_code=404, detail="Provider not found")
    return {"provider": p}

@app.get("/api/settings/active-provider")
async def active_provider_info():
    active = get_active_provider()
    if active:
        return {
            "is_active": True,
            "name": active.get("name"),
            "model_name": active.get("model_name"),
            "base_url": active.get("base_url")
        }
    return {
        "is_active": False,
        "name": "Local Offline Heuristics",
        "model_name": "Built-in Rule Engine"
    }

@app.post("/api/settings/providers")
async def save_or_update_provider(payload: Dict[str, Any] = Body(...)):
    try:
        saved = save_provider(payload)
        return {"success": True, "provider": saved}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save provider: {str(e)}")

@app.put("/api/settings/providers/{provider_id}/active")
async def activate_provider(provider_id: int):
    updated = set_active_provider(provider_id)
    if not updated:
        raise HTTPException(status_code=404, detail="Provider not found")
    return {"success": True, "active_provider": updated}

@app.post("/api/settings/deactivate-all")
async def deactivate_providers():
    deactivate_all_providers()
    return {"success": True, "message": "Using local offline heuristic engine."}

@app.delete("/api/settings/providers/{provider_id}")
async def remove_provider(provider_id: int):
    deleted = delete_provider(provider_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Provider not found")
    return {"success": True}

@app.post("/api/settings/test-connection")
async def test_connection(payload: Dict[str, Any] = Body(...)):
    base_url = payload.get("base_url", "").strip()
    api_key = payload.get("api_key", "").strip()
    model_name = payload.get("model_name", "").strip()

    if not base_url or not model_name:
        raise HTTPException(status_code=400, detail="Base URL and Model Name are required.")

    result = await test_provider_connection(base_url, api_key, model_name)
    return result

# Mount static files
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

NO_CACHE_HEADERS = {"Cache-Control": "no-store, no-cache, must-revalidate"}

@app.get("/")
async def root():
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_path):
        with open(index_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read(), headers=NO_CACHE_HEADERS)
    return HTMLResponse("<h1>ATS Resume Suite Desktop Server Running</h1><p>UI loading...</p>", headers=NO_CACHE_HEADERS)
