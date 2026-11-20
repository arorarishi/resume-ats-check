import os
import sys
import unittest
import unittest.mock
from starlette.testclient import TestClient

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.server import app, current_session_data
from app.database import (
    init_db, get_master_resume, save_master_resume, reset_sample_master_resume,
    sync_master_resume_from_ats
)
from app.parsers.ats_normalizer import normalize_to_ats_json, derive_master_resume_from_ats_json

client = TestClient(app)

SAMPLE_CANDIDATE_RESUME = """SARAH CONNOR
Austin, TX | (512) 555-0199 | sconnor@cyberdyne-ai.io | linkedin.com/in/sarah-connor | github.com/sarahconnor

PROFESSIONAL SUMMARY
Senior Machine Learning Ops Engineer with 5+ years of experience deploying scalable LLM pipelines, Kubernetes clusters, and real-time Kafka streaming architectures.

TECHNICAL SKILLS
Languages: Python, Go, SQL, Bash
Frameworks & AI: PyTorch, Transformers, LangChain, FastAPI, Docker, Kubernetes
Cloud: AWS, GCP, Terraform

WORK EXPERIENCE
Senior MLOps Engineer | Cyberdyne Systems | Austin, TX | 2022 - Present
- Architected enterprise LLM serving platform using FastAPI and vLLM, reducing latency by 40% for 5M daily queries.
- Built automated continuous deployment pipelines on AWS EKS with Prometheus monitoring.

Machine Learning Engineer | Apex Dynamics | Dallas, TX | 2020 - 2022
- Engineered real-time feature store using Redis and PostgreSQL, accelerating model training velocity by 30%.

TECHNICAL PROJECTS
Autonomous Model Evaluation Suite [Python, PyTorch, Ray]
- Built an automated benchmarking harness evaluating 20+ open-weights LLMs on reasoning tasks.
- Achieved sub-50ms inference latency across distributed GPU instances.

Streaming Log Anomaly Detection (Go, Kafka, Docker)
- Productionized distributed event ingestion pipeline processing 50,000 logs/sec with 99.9% uptime.

EDUCATION
Bachelor of Science in Computer Science | University of Texas at Austin | 2016 - 2020

CERTIFICATIONS
- AWS Certified Machine Learning - Specialty
"""

class TestMasterResumeDerivation(unittest.TestCase):

    def setUp(self):
        init_db()

    def test_derive_master_resume_from_ats(self):
        ats_res = normalize_to_ats_json(SAMPLE_CANDIDATE_RESUME, filename="Sarah_Connor_Resume.txt")
        derived = derive_master_resume_from_ats_json(ats_res["ats_json"])

        self.assertEqual(derived["full_name"], "SARAH CONNOR")
        self.assertEqual(derived["email"], "sconnor@cyberdyne-ai.io")
        self.assertEqual(derived["phone"], "(512) 555-0199")
        self.assertIn("Austin", derived["location"])

        # Projects check
        self.assertGreaterEqual(len(derived["projects"]), 2)
        project_names = [p["name"] for p in derived["projects"]]
        self.assertTrue(any("Autonomous Model Evaluation" in name for name in project_names))
        self.assertTrue(any("Streaming Log Anomaly" in name for name in project_names))

        # Check tech stack extraction
        for p in derived["projects"]:
            if "Autonomous Model Evaluation" in p["name"]:
                self.assertIn("Python", p["tech_stack"])

    def test_sync_master_resume_overwrite_sample(self):
        # Reset to Alexander Rivera first
        reset_sample_master_resume()
        cur = get_master_resume()
        self.assertEqual(cur["full_name"], "Alexander Rivera")

        # Parse Sarah's resume
        ats_res = normalize_to_ats_json(SAMPLE_CANDIDATE_RESUME, filename="Sarah_Connor_Resume.txt")
        updated = sync_master_resume_from_ats(ats_res["ats_json"], merge=False)

        # Master resume should now be Sarah Connor
        self.assertEqual(updated["full_name"], "SARAH CONNOR")
        self.assertEqual(updated["email"], "sconnor@cyberdyne-ai.io")
        self.assertGreaterEqual(len(updated["projects"]), 2)

    def test_sync_master_resume_merge(self):
        # Start with Sarah Connor as current master
        ats_res = normalize_to_ats_json(SAMPLE_CANDIDATE_RESUME, filename="Sarah_Connor_Resume.txt")
        sync_master_resume_from_ats(ats_res["ats_json"], merge=False)

        # Now suppose candidate uploads a project portfolio resume with a brand new project
        second_resume_text = """SARAH CONNOR
Austin, TX | sconnor@cyberdyne-ai.io

PROJECTS
Quantum Circuit Simulator [C++, Python, Qiskit]
- Implemented high performance quantum circuit simulation library with 8x acceleration over baseline.
"""
        ats_res2 = normalize_to_ats_json(second_resume_text, filename="Quantum_Portfolio.txt")
        merged = sync_master_resume_from_ats(ats_res2["ats_json"], merge=True)

        # Should still be Sarah Connor
        self.assertEqual(merged["full_name"], "SARAH CONNOR")
        project_names = [p["name"] for p in merged["projects"]]

        # Should have previous projects AND new project
        self.assertTrue(any("Autonomous Model Evaluation" in name for name in project_names))
        self.assertTrue(any("Quantum Circuit Simulator" in name for name in project_names))

    def test_server_parse_endpoint_auto_syncs_master(self):
        # Send parse request
        response = client.post("/api/resume/parse", data={"raw_text": SAMPLE_CANDIDATE_RESUME})
        self.assertEqual(response.status_code, 200)
        data = response.json()

        # Check response metadata. Note: master_profile_name is NOT expected to
        # contain the parsed candidate's name -- profile_name is a user-owned
        # label that resume sync must never silently rename (see save_master_resume).
        self.assertTrue(data.get("master_synced"))
        self.assertTrue(data.get("master_profile_name"))
        self.assertGreaterEqual(data.get("master_projects_count", 0), 2)

        # Verify DB directly
        m = get_master_resume()
        self.assertEqual(m["full_name"], "SARAH CONNOR")

    def test_server_sync_current_endpoint(self):
        # Parse resume first to populate current_session_data
        client.post("/api/resume/parse", data={"raw_text": SAMPLE_CANDIDATE_RESUME})

        # Call on-demand sync endpoint
        response = client.post("/api/master-resume/sync-current", json={"merge": False})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data.get("success"))
        self.assertEqual(data["master_resume"]["full_name"], "SARAH CONNOR")

    def test_organisation_and_duration_in_projects(self):
        ats_res = normalize_to_ats_json(SAMPLE_CANDIDATE_RESUME)
        derived = derive_master_resume_from_ats_json(ats_res["ats_json"])
        projects = derived.get("projects", [])
        self.assertGreaterEqual(len(projects), 1)
        for p in projects:
            self.assertIn("organisation", p)
            self.assertIn("organisation_duration", p)

    def test_no_character_cutoff_on_metrics(self):
        text_with_leading_digits = """JOHN DOE
San Francisco, CA | jdoe@example.com

EXPERIENCE
Software Engineer | Acme Corp | 2021 - Present
- 10x throughput boost across distributed clusters.
- 5M daily queries handled with sub-10ms response time.
- 99.99% uptime maintained over 24 consecutive months.
"""
        ats_res = normalize_to_ats_json(text_with_leading_digits)
        exps = ats_res["ats_json"].get("work_experience", [])
        self.assertGreaterEqual(len(exps), 1)
        bullets = exps[0].get("bullets", [])
        self.assertTrue(any(b.startswith("10x") for b in bullets), f"Leading 10x was cut off! Bullets: {bullets}")
        self.assertTrue(any(b.startswith("5M") for b in bullets), f"Leading 5M was cut off! Bullets: {bullets}")
        self.assertTrue(any(b.startswith("99.99%") for b in bullets), f"Leading 99.99% was cut off! Bullets: {bullets}")

    @unittest.mock.patch("app.server.clean_and_extract_master_resume_with_llm")
    def test_clean_with_llm_endpoint(self, mock_llm_clean):
        mock_llm_clean.return_value = {
            "profile_name": "SARAH CONNOR's Master Profile",
            "full_name": "SARAH CONNOR",
            "email": "sconnor@cyberdyne-ai.io",
            "phone": "(512) 555-0199",
            "location": "Austin, TX",
            "linkedin": "linkedin.com/in/sarah-connor",
            "github": "github.com/sarahconnor",
            "summary": "Senior Machine Learning Ops Engineer with 5+ years of experience deploying scalable LLM pipelines.",
            "skills": {"Languages": ["Python", "Go"]},
            "experiences": [],
            "projects": [
                {
                    "id": "proj-1",
                    "name": "Autonomous Model Evaluation Suite",
                    "organisation": "Cyberdyne Systems",
                    "organisation_duration": "2022 - Present",
                    "tech_stack": "Python, PyTorch, Ray",
                    "description": "Benchmarking harness",
                    "metrics": "sub-50ms latency",
                    "bullets": ["Achieved sub-50ms inference latency across distributed GPU instances."]
                }
            ],
            "education": [],
            "certifications": []
        }
        client.post("/api/resume/parse", data={"raw_text": SAMPLE_CANDIDATE_RESUME})
        response = client.post("/api/master-resume/clean-with-llm", json={})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data.get("success"))
        self.assertIn("master_resume", data)
        self.assertEqual(data["master_resume"]["full_name"], "SARAH CONNOR")

if __name__ == "__main__":
    unittest.main()
