import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from starlette.testclient import TestClient
from app.server import app

client = TestClient(app)

def test_endpoints():
    # 1. Health check
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"
    print("[API Test] Healthcheck passed.")

    # 2. UI Root HTML
    r_root = client.get("/")
    assert r_root.status_code == 200
    assert "Resume ATS Check" in r_root.text
    print("[API Test] UI HTML serving passed.")

    # 3. Resume Parse Endpoint
    resume_text = """
    SARAH CONNOR
    Los Angeles, CA | (310) 555-0144 | sarah@defense.net
    PROFESSIONAL SUMMARY
    Systems Architect with 8 years in distributed systems, Python, and cloud defense.
    TECHNICAL SKILLS
    Languages: Python, C++, Go, Bash
    Cloud: AWS, Docker, Kubernetes
    Databases: PostgreSQL, Redis
    WORK EXPERIENCE
    Senior Architect | Cyberdyne Systems | 2020 - Present
    - Designed secure cloud architectures saving $500,000 and improving uptime to 99.99%.
    """
    r_parse = client.post("/api/resume/parse", data={"raw_text": resume_text})
    assert r_parse.status_code == 200
    res_data = r_parse.json()
    assert "ats_json" in res_data
    assert "hygiene_report" in res_data
    assert res_data["ats_json"]["contact_information"]["name"] == "SARAH CONNOR"
    print("[API Test] /api/resume/parse passed.")

    # 4. JD Compare Endpoint
    jd_text = """
    Job Title: Senior Cloud Architect
    Company: Resistance Tech
    Requirements:
    - 5+ years experience in Python, AWS, Docker, and Kubernetes.
    - PostgreSQL expertise.
    """
    r_comp = client.post("/api/resume/compare", json={
        "jd_text": jd_text,
        "resume_data": res_data
    })
    assert r_comp.status_code == 200
    comp_data = r_comp.json()
    assert "comparison" in comp_data
    assert comp_data["comparison"]["match_score"] > 60
    print(f"[API Test] /api/resume/compare passed. Score: {comp_data['comparison']['match_score']}%")

    # 5. Suggestions Endpoint
    r_sugg = client.post("/api/resume/suggest", json={
        "resume_data": res_data,
        "jd_data": comp_data["jd_parsed"],
        "comparison": comp_data["comparison"]
    })
    assert r_sugg.status_code == 200
    sugg_data = r_sugg.json()
    assert "recommended" in sugg_data["summary"]
    print("[API Test] /api/resume/suggest passed.")

    # 6. Funnel CRUD Endpoints
    # Create
    r_funnel_create = client.post("/api/funnel", json={
        "company": "Resistance Tech",
        "role": "Senior Cloud Architect",
        "stage": "Resume Screening",
        "match_score": comp_data["comparison"]["match_score"],
        "salary": "$180,000"
    })
    assert r_funnel_create.status_code == 200
    created_app = r_funnel_create.json()["application"]
    app_id = created_app["id"]
    print(f"[API Test] Funnel POST passed. Created App ID: {app_id}")

    # Stage update
    r_stage = client.put(f"/api/funnel/{app_id}/stage", json={"stage": "Interview"})
    assert r_stage.status_code == 200
    assert r_stage.json()["application"]["stage"] == "Interview"
    print("[API Test] Funnel Stage PUT passed.")

    # Funnel list
    r_list = client.get("/api/funnel")
    assert r_list.status_code == 200
    assert r_list.json()["stats"]["total_tracked"] >= 1
    print("[API Test] Funnel GET passed.")

    # Funnel delete
    r_del = client.delete(f"/api/funnel/{app_id}")
    assert r_del.status_code == 200
    print("[API Test] Funnel DELETE passed.")

    print("\nALL API ENDPOINTS VALIDATED SUCCESSFULLY!")

if __name__ == "__main__":
    test_endpoints()
