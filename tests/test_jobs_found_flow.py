import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from starlette.testclient import TestClient
from app.server import app
from app.database import get_all_applications, get_jobs_found, get_all_ledger_entries, delete_application, delete_ledger_entry

client = TestClient(app)

def test_jobs_found_complete_flow():
    print("\n--- Running test_jobs_found_complete_flow ---")
    
    sample_jd = """Principal Distributed AI Systems Engineer
Company: Cerebras & Scale Networks
Location: Sunnyvale, CA
Compensation: $210,000 - $260,000

Requirements:
- 7+ years software engineering experience in Python, C++, or Go.
- Deep expertise in PyTorch, distributed inference, and Kubernetes.
- Experience with Docker, Redis, and high-throughput microservices.
"""

    # 1. Test POST /api/jobs/create-resume
    resp = client.post("/api/jobs/create-resume", json={
        "jd_text": sample_jd,
        "company": "Cerebras & Scale Networks",
        "location": "Sunnyvale, CA",
        "salary": "$210,000 - $260,000",
        "job_url": "https://example.com/jobs/123"
    })
    
    assert resp.status_code == 200, f"Error: {resp.text}"
    data = resp.json()
    
    assert data["success"] is True
    # Verify resume name is derived from first line of JD
    expected_resume_name = "Principal Distributed AI Systems Engineer"
    assert data["resume_name"] == expected_resume_name, f"Expected {expected_resume_name}, got {data['resume_name']}"
    assert data["first_line_jd"] == "Principal Distributed AI Systems Engineer"
    
    # Verify Application created in Funnel under 'Wishlist'
    app_record = data["application"]
    assert app_record["stage"] == "Wishlist"
    assert app_record["company"] == "Cerebras & Scale Networks"
    assert app_record["role"] == expected_resume_name
    assert app_record["match_score"] > 0
    app_id = app_record["id"]
    print(f"[PASS] Application created in stage 'Wishlist' with ID: {app_id}, Role: '{app_record['role']}'")
    
    # Verify Comparison was computed
    comp = data["comparison"]
    assert "match_score" in comp
    assert "side_by_side_matrix" in comp
    print(f"[PASS] ATS Comparison calculated: {comp['match_score']}% ({comp.get('score_tier')})")
    
    # Verify Ledger Entry was logged
    ledger = data["ledger_entry"]
    assert ledger["application_id"] == app_id
    assert ledger["resume_name"] == expected_resume_name
    print(f"[PASS] Ledger entry created with ID: {ledger['id']}, resume_name: '{ledger['resume_name']}'")
    
    # 2. Test GET /api/jobs/found
    resp_found = client.get("/api/jobs/found")
    assert resp_found.status_code == 200
    found_data = resp_found.json()
    assert found_data["count"] >= 1
    found_ids = [j["id"] for j in found_data["jobs"]]
    assert app_id in found_ids
    print(f"[PASS] GET /api/jobs/found verified with {found_data['count']} jobs.")
    
    # 3. Test Funnel Stage Advance from 'Wishlist' to 'Resume Screening'
    resp_stage = client.put(f"/api/funnel/{app_id}/stage", json={"stage": "Resume Screening"})
    assert resp_stage.status_code == 200
    updated_app = resp_stage.json()["application"]
    assert updated_app["stage"] == "Resume Screening"
    print(f"[PASS] Application {app_id} successfully transitioned to 'Resume Screening'.")
    
    # 4. Clean up created records
    delete_application(app_id)
    delete_ledger_entry(ledger["id"])
    print("[PASS] Cleanup completed.")

def test_resume_naming_with_prefix():
    print("\n--- Running test_resume_naming_with_prefix ---")
    
    prefixed_jd = """Job Title: Senior NLP Research Scientist
Company: Hugging Face Partner
Requirements:
- Python, PyTorch, Transformers, BERT
"""
    resp = client.post("/api/jobs/create-resume", json={"jd_text": prefixed_jd})
    assert resp.status_code == 200
    data = resp.json()
    assert data["resume_name"] == "Senior NLP Research Scientist"
    print(f"[PASS] Cleaned prefix 'Job Title:' successfully -> '{data['resume_name']}'")
    
    # Clean up
    delete_application(data["application"]["id"])
    delete_ledger_entry(data["ledger_entry"]["id"])

if __name__ == "__main__":
    test_jobs_found_complete_flow()
    test_resume_naming_with_prefix()
    print("\nALL TESTS IN test_jobs_found_flow.py PASSED SUCCESSFULLY!")
