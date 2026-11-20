import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from starlette.testclient import TestClient

from app.server import app, current_session_data
from app.database import (
    init_db, get_master_resume, save_master_resume, reset_sample_master_resume,
    get_all_ledger_entries, get_ledger_entry_by_id, delete_ledger_entry,
    link_ledger_to_application, create_application, deactivate_all_providers
)
from app.parsers.resume_exporter import generate_resume_docx, generate_plain_text, OUTPUT_DIR
from app.analyzer.tailorer import (
    build_heuristic_tailoring, resolve_tier_name, select_best_master_projects, tailor_resume_async
)
from app.parsers.ats_normalizer import normalize_to_ats_json
from app.analyzer.jd_parser import parse_job_description
from app.analyzer.matcher import compare_resume_to_jd

client = TestClient(app)

def setup_test_db():
    init_db()

def test_resolve_tier_name():
    assert resolve_tier_name("tier1") == "Tier 1: Minor Changes"
    assert resolve_tier_name("minor") == "Tier 1: Minor Changes"
    assert resolve_tier_name("tier2") == "Tier 2: Reframing"
    assert resolve_tier_name("reframing") == "Tier 2: Reframing"
    assert resolve_tier_name("tier3") == "Tier 3: Major Redo"
    assert resolve_tier_name("redo") == "Tier 3: Major Redo"
    assert resolve_tier_name("unknown") == "Tier 2: Reframing"

def test_select_best_master_projects():
    all_projects = [
        {
            "name": "Distributed Vector Search",
            "tech_stack": "Python, C++, FAISS",
            "description": "High performance embeddings and vector search",
            "bullets": ["Sub-8ms latency for similarity search"]
        },
        {
            "name": "Kubernetes Microservices Event Stream",
            "tech_stack": "Go, Kafka, Docker, Kubernetes",
            "description": "High volume telemetry streaming with Kafka",
            "bullets": ["Ingested 120k events/sec"]
        },
        {
            "name": "Frontend React Dashboard",
            "tech_stack": "React, CSS, HTML",
            "description": "UI dashboard for analytics",
            "bullets": ["Responsive design"]
        }
    ]

    jd_text = "We need expertise in Kubernetes, Docker, and Kafka for microservices."
    best = select_best_master_projects(all_projects, jd_text, max_count=2)
    assert len(best) == 2
    assert best[0]["name"] == "Kubernetes Microservices Event Stream"

def test_master_resume_crud():
    reset_sample_master_resume()
    m = get_master_resume()
    assert m is not None
    assert "full_name" in m
    assert len(m["projects"]) >= 3

    # Update master resume
    m["full_name"] = "Dr. Alexander Rivera, Ph.D."
    saved = save_master_resume(m)
    assert saved["full_name"] == "Dr. Alexander Rivera, Ph.D."

    # Verify reload
    reloaded = get_master_resume()
    assert reloaded["full_name"] == "Dr. Alexander Rivera, Ph.D."

    # Reset sample
    reset = reset_sample_master_resume()
    assert reset["full_name"] == "Alexander Rivera"

def test_resume_exporter_docx_and_txt():
    master = get_master_resume()
    docx_path = generate_resume_docx(master, filename_prefix="Test_Exporter")
    assert os.path.exists(docx_path)
    assert docx_path.endswith(".docx")
    assert os.path.getsize(docx_path) > 10000

    txt_path = docx_path[:-5] + ".txt"
    assert os.path.exists(txt_path)
    assert os.path.getsize(txt_path) > 500

    content = open(txt_path, "r", encoding="utf-8").read()
    assert "ALEXANDER RIVERA" in content
    assert "PROFESSIONAL SUMMARY" in content
    assert "KEY PROJECTS" in content

    # Clean up test files
    try:
        os.remove(docx_path)
        os.remove(txt_path)
    except Exception:
        pass

def test_build_heuristic_tailoring_tier1_minor():
    master = get_master_resume()
    jd_data = {"role_title": "Senior NLP Engineer", "company": "ScaleAI", "seniority": "Senior"}
    comparison_data = {"top_missing_keywords": ["BERT", "PyTorch", "Kubernetes"]}
    
    tailored = build_heuristic_tailoring(
        source_data=master,
        jd_data=jd_data,
        comparison_data=comparison_data,
        tier_name="Tier 1: Minor Changes",
        jd_text="NLP Engineer BERT PyTorch Kubernetes"
    )

    assert "BERT" in tailored["summary"] or "BERT" in str(tailored["skills"])
    assert any("Tier 1" in c.get("tier", "") for c in tailored["changes_summary"])

def test_build_heuristic_tailoring_tier2_reframing():
    master = get_master_resume()
    jd_data = {"role_title": "Staff ML Infrastructure Engineer", "company": "DeepScale", "seniority": "Staff"}
    comparison_data = {"top_missing_keywords": ["TensorRT", "vLLM", "CUDA"]}
    
    tailored = build_heuristic_tailoring(
        source_data=master,
        jd_data=jd_data,
        comparison_data=comparison_data,
        tier_name="Tier 2: Reframing",
        jd_text="Staff ML Infrastructure Engineer TensorRT vLLM CUDA"
    )

    assert "Staff ML Infrastructure Engineer" in tailored["summary"]
    assert any("Reframing" in c.get("tier", "") for c in tailored["changes_summary"])

def test_build_heuristic_tailoring_tier3_major_redo():
    master = get_master_resume()
    jd_data = {"role_title": "Lead Distributed Systems Architect", "company": "CloudTitan", "seniority": "Lead"}
    comparison_data = {"top_missing_keywords": ["Ray", "Kubernetes", "gRPC"]}
    
    tailored = build_heuristic_tailoring(
        source_data=master,
        jd_data=jd_data,
        comparison_data=comparison_data,
        tier_name="Tier 3: Major Redo",
        jd_text="Lead Distributed Systems Architect Ray Kubernetes gRPC"
    )

    assert "CloudTitan" in tailored["summary"]
    assert any("Major Redo" in c.get("tier", "") for c in tailored["changes_summary"])
    assert len(tailored["projects"]) <= 3

def test_api_master_resume_endpoints():
    # GET master resume
    resp = client.get("/api/master-resume")
    assert resp.status_code == 200
    data = resp.json()
    assert "master_resume" in data
    assert data["master_resume"]["full_name"] == "Alexander Rivera"

    # POST master resume
    mr = data["master_resume"]
    mr["location"] = "Seattle, WA"
    save_resp = client.post("/api/master-resume", json=mr)
    assert save_resp.status_code == 200
    assert save_resp.json()["master_resume"]["location"] == "Seattle, WA"

    # Reset
    reset_resp = client.post("/api/master-resume/reset-sample")
    assert reset_resp.status_code == 200
    assert reset_resp.json()["master_resume"]["location"] == "San Francisco, CA"

def test_api_tailor_and_ledger_flow():
    # Create sample app in funnel
    app_res = create_application({
        "company": "Anthropic AI",
        "role": "Principal Systems Engineer",
        "stage": "Applied"
    })
    app_id = app_res["id"]

    sample_resume = normalize_to_ats_json("""ALEXANDER RIVERA
San Francisco, CA | (555) 382-9012 | alex@example.com
PROFESSIONAL SUMMARY
Senior Engineer with Python and Docker experience.
TECHNICAL SKILLS
Languages: Python, SQL
WORK EXPERIENCE
Senior Engineer | Apex AI | 2022 - Present
- Built web services with Python and Redis.
""")
    sample_jd_text = """Job Title: Principal Systems Engineer
Company: Anthropic AI
Must-Have:
- Deep expertise in PyTorch, Distributed Training, Kubernetes, and vLLM.
- 6+ years experience in high-performance computing."""

    jd_parsed = parse_job_description(sample_jd_text)
    comp = compare_resume_to_jd(sample_resume, jd_parsed)

    current_session_data["resume"] = sample_resume
    current_session_data["jd"] = jd_parsed
    current_session_data["jd_text"] = sample_jd_text
    current_session_data["comparison"] = comp

    # Test Tailor Endpoint (from Master Resume)
    tailor_payload = {
        "tier": "tier2",
        "source_type": "master",
        "custom_instructions": "Highlight RAG and inference scaling",
        "resume_data": sample_resume,
        "jd_data": jd_parsed,
        "jd_text": sample_jd_text,
        "comparison": comp
    }
    
    resp = client.post("/api/resume/tailor", json=tailor_payload)
    assert resp.status_code == 200
    result = resp.json()
    assert "ledger_entry" in result
    assert result["tier"] == "Tier 2: Reframing"
    assert result["source_type"] == "Master Resume"
    assert result["score_after"] >= result["score_before"]
    assert "docx_download_url" in result
    assert "txt_download_url" in result

    ledger_id = result["ledger_entry"]["id"]
    assert ledger_id > 0

    # Test Download DOCX
    docx_resp = client.get(f"/api/resume/download/{ledger_id}/docx")
    assert docx_resp.status_code == 200
    assert len(docx_resp.content) > 5000

    # Test Download TXT
    txt_resp = client.get(f"/api/resume/download/{ledger_id}/txt")
    assert txt_resp.status_code == 200
    assert len(txt_resp.content) > 500

    # Test Ledger List
    ledger_list_resp = client.get("/api/resume/ledger")
    assert ledger_list_resp.status_code == 200
    entries = ledger_list_resp.json()["entries"]
    assert len(entries) >= 1
    assert any(e["id"] == ledger_id for e in entries)

    # Test Link to Funnel
    link_resp = client.post(f"/api/resume/ledger/{ledger_id}/link-funnel", json={"application_id": app_id})
    assert link_resp.status_code == 200
    assert link_resp.json()["entry"]["application_id"] == app_id

    # Test Delete Ledger Entry
    del_resp = client.delete(f"/api/resume/ledger/{ledger_id}")
    assert del_resp.status_code == 200
    assert del_resp.json()["success"] is True

    # Verify deleted
    get_del = client.get(f"/api/resume/ledger/{ledger_id}")
    assert get_del.status_code == 404

if __name__ == "__main__":
    setup_test_db()
    print("Running test_resolve_tier_name...")
    test_resolve_tier_name()
    print("Running test_select_best_master_projects...")
    test_select_best_master_projects()
    print("Running test_master_resume_crud...")
    test_master_resume_crud()
    print("Running test_resume_exporter_docx_and_txt...")
    test_resume_exporter_docx_and_txt()
    print("Running test_build_heuristic_tailoring_tier1_minor...")
    test_build_heuristic_tailoring_tier1_minor()
    print("Running test_build_heuristic_tailoring_tier2_reframing...")
    test_build_heuristic_tailoring_tier2_reframing()
    print("Running test_build_heuristic_tailoring_tier3_major_redo...")
    test_build_heuristic_tailoring_tier3_major_redo()
    print("Running test_api_master_resume_endpoints...")
    test_api_master_resume_endpoints()
    print("Running test_api_tailor_and_ledger_flow...")
    test_api_tailor_and_ledger_flow()
    print("ALL TESTS IN test_tailor_and_ledger.py PASSED SUCCESSFULLY!")
