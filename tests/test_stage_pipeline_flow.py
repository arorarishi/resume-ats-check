import os
import sys
import unittest
from starlette.testclient import TestClient

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import (
    init_db,
    get_connection,
    create_application,
    update_application_stage,
    get_application_by_id,
    delete_application,
    get_funnel_stats,
    STAGES
)
from app.server import app

client = TestClient(app)

class TestStagePipelineFlow(unittest.TestCase):
    def setUp(self):
        init_db()

    def test_stages_list(self):
        expected = [
            "Wishlist",
            "Resume Screening",
            "Recruiter Screening",
            "Interview",
            "Offer",
            "Rejected",
            "Archived"
        ]
        self.assertEqual(STAGES, expected)

    def test_create_resume_initial_wishlist_stage(self):
        sample_jd = """Staff Platform Systems Architect
Google Cloud / Sunnyvale, CA
Responsibilities:
- Architect distributed Kubernetes control planes with high availability.
- Design low latency gRPC microservices and optimize throughput.
"""
        response = client.post("/api/jobs/create-resume", json={"jd_text": sample_jd})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertEqual(data["resume_name"], "Staff Platform Systems Architect")
        self.assertEqual(data["application"]["stage"], "Wishlist")
        self.assertEqual(data["ledger_entry"]["resume_name"], "Staff Platform Systems Architect")

        app_id = data["application"]["id"]
        delete_application(app_id)

    def test_pass_stage_progression(self):
        created = create_application({
            "company": "TestCorp",
            "role": "Lead Systems Engineer",
            "stage": "Wishlist"
        })
        app_id = created["id"]
        self.assertEqual(created["stage"], "Wishlist")

        # Pass to Resume Screening
        resp = client.put(f"/api/funnel/{app_id}/stage", json={"stage": "Resume Screening"})
        self.assertEqual(resp.status_code, 200)
        app_data = resp.json()["application"]
        self.assertEqual(app_data["stage"], "Resume Screening")
        self.assertTrue(bool(app_data["date_applied"]))

        # Pass to Recruiter Screening
        resp = client.put(f"/api/funnel/{app_id}/stage", json={"stage": "Recruiter Screening"})
        self.assertEqual(resp.status_code, 200)
        app_data = resp.json()["application"]
        self.assertEqual(app_data["stage"], "Recruiter Screening")

        # Pass to Interview
        resp = client.put(f"/api/funnel/{app_id}/stage", json={"stage": "Interview"})
        self.assertEqual(resp.status_code, 200)
        app_data = resp.json()["application"]
        self.assertEqual(app_data["stage"], "Interview")
        self.assertEqual(app_data["interview_step"], "Round 1: Technical Screen")

        delete_application(app_id)

    def test_multi_step_interview_and_offer(self):
        created = create_application({
            "company": "AI Dynamics",
            "role": "Senior ML Infrastructure Engineer",
            "stage": "Interview",
            "interview_step": "Round 1: Coding Screen"
        })
        app_id = created["id"]
        self.assertEqual(created["interview_step"], "Round 1: Coding Screen")

        # Advance to Round 2
        resp = client.put(f"/api/funnel/{app_id}/stage", json={
            "stage": "Interview",
            "interview_step": "Round 2: System Design & Architecture"
        })
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["application"]["interview_step"], "Round 2: System Design & Architecture")

        # Update / Rename interview step endpoint
        resp2 = client.put(f"/api/funnel/{app_id}/interview-step", json={
            "interview_step": "Round 3: Hiring Manager & Culture"
        })
        self.assertEqual(resp2.status_code, 200)
        self.assertEqual(resp2.json()["application"]["interview_step"], "Round 3: Hiring Manager & Culture")

        # Pass to Offer
        resp_offer = client.put(f"/api/funnel/{app_id}/stage", json={"stage": "Offer"})
        self.assertEqual(resp_offer.status_code, 200)
        self.assertEqual(resp_offer.json()["application"]["stage"], "Offer")

        delete_application(app_id)

    def test_rejection_tracking_at_steps(self):
        # 1. Reject at Recruiter Screening
        app1 = create_application({
            "company": "BetaScale",
            "role": "Distributed Systems Dev",
            "stage": "Recruiter Screening"
        })
        resp = client.put(f"/api/funnel/{app1['id']}/stage", json={
            "stage": "Rejected",
            "rejected_from_stage": "Recruiter Screening"
        })
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["application"]["stage"], "Rejected")
        self.assertEqual(resp.json()["application"]["rejected_from_stage"], "Recruiter Screening")

        # 2. Reject at Interview Round 2
        app2 = create_application({
            "company": "OmegaData",
            "role": "Cloud Architect",
            "stage": "Interview",
            "interview_step": "Round 2: System Design"
        })
        resp2 = client.put(f"/api/funnel/{app2['id']}/stage", json={
            "stage": "Rejected",
            "rejected_from_stage": "Interview (Round 2: System Design)"
        })
        self.assertEqual(resp2.status_code, 200)
        self.assertEqual(resp2.json()["application"]["stage"], "Rejected")
        self.assertEqual(resp2.json()["application"]["rejected_from_stage"], "Interview (Round 2: System Design)")

        # 3. Restore to pipeline
        resp_restore = client.put(f"/api/funnel/{app2['id']}/stage", json={
            "stage": "Interview",
            "interview_step": "Round 2: System Design"
        })
        self.assertEqual(resp_restore.status_code, 200)
        self.assertEqual(resp_restore.json()["application"]["stage"], "Interview")

        delete_application(app1["id"])
        delete_application(app2["id"])

    def test_funnel_stats_structure(self):
        stats = get_funnel_stats()
        self.assertIn("Wishlist", stats["stage_counts"])
        self.assertIn("Resume Screening", stats["stage_counts"])
        self.assertIn("Recruiter Screening", stats["stage_counts"])
        self.assertIn("Interview", stats["stage_counts"])
        self.assertIn("Offer", stats["stage_counts"])
        self.assertIn("Rejected", stats["stage_counts"])
        self.assertIn("recruiter_to_interview", stats["conversion_rates"])
        self.assertIn("overall_offer_rate", stats["conversion_rates"])

if __name__ == "__main__":
    unittest.main()
