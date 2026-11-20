import os
import sys
import unittest
import asyncio

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from starlette.testclient import TestClient
from app.server import app
from app.database import (
    init_db, save_provider, get_all_providers, get_active_provider,
    set_active_provider, delete_provider, deactivate_all_providers
)
from app.analyzer.llm_client import test_provider_connection
from app.analyzer.suggester import generate_resume_suggestions_async
from app.parsers.ats_normalizer import normalize_to_ats_json
from app.analyzer.jd_parser import parse_job_description
from app.analyzer.matcher import compare_resume_to_jd

class TestProviderSettings(unittest.TestCase):
    def setUp(self):
        init_db()

    def test_provider_database_crud(self):
        # 1. Save new provider
        p1 = save_provider({
            "name": "Groq Fast",
            "base_url": "https://api.groq.com/openai/v1",
            "api_key": "gsk_1234567890abcdef12345678",
            "model_name": "llama-3.3-70b-versatile",
            "is_active": 1
        })
        self.assertIsNotNone(p1)
        self.assertEqual(p1["name"], "Groq Fast")
        self.assertEqual(p1["is_active"], 1)

        # 2. Check masked key in get_all_providers
        all_p = get_all_providers()
        saved = next(p for p in all_p if p["id"] == p1["id"])
        self.assertTrue(saved["masked_key"].startswith("gsk_"))
        self.assertTrue(saved["masked_key"].endswith("5678"))
        self.assertIn("...", saved["masked_key"])

        # 3. Save second provider
        p2 = save_provider({
            "name": "Local Ollama",
            "base_url": "http://localhost:11434/v1",
            "api_key": "",
            "model_name": "llama3",
            "is_active": 1
        })
        # Active should have switched to p2
        active = get_active_provider()
        self.assertEqual(active["id"], p2["id"])

        # Switch back to p1
        set_active_provider(p1["id"])
        active_now = get_active_provider()
        self.assertEqual(active_now["id"], p1["id"])

        # Cleanup
        delete_provider(p1["id"])
        delete_provider(p2["id"])
        print("\n[Settings Test] SQLite Provider CRUD & Key Masking validated.")

    def test_api_settings_endpoints(self):
        client = TestClient(app)

        # 1. Save provider via API
        resp = client.post("/api/settings/providers", json={
            "name": "OpenAI Test",
            "base_url": "https://api.openai.com/v1",
            "api_key": "sk-proj-testkey123456789",
            "model_name": "gpt-4o-mini",
            "is_active": True
        })
        self.assertEqual(resp.status_code, 200)
        p_id = resp.json()["provider"]["id"]

        # 2. Check active provider info
        r_act = client.get("/api/settings/active-provider")
        self.assertEqual(r_act.status_code, 200)
        self.assertTrue(r_act.json()["is_active"])
        self.assertEqual(r_act.json()["name"], "OpenAI Test")

        # 3. Test list providers
        r_list = client.get("/api/settings/providers")
        self.assertEqual(r_list.status_code, 200)
        self.assertTrue(len(r_list.json()["providers"]) >= 1)

        # 4. Deactivate all (local mode)
        r_deact = client.post("/api/settings/deactivate-all")
        self.assertEqual(r_deact.status_code, 200)
        r_act2 = client.get("/api/settings/active-provider")
        self.assertFalse(r_act2.json()["is_active"])

        # 5. Delete provider
        r_del = client.delete(f"/api/settings/providers/{p_id}")
        self.assertEqual(r_del.status_code, 200)
        print("[Settings Test] REST API endpoints for provider settings validated.")

    def test_suggester_fallback_and_execution(self):
        # Test that generate_resume_suggestions_async functions seamlessly
        sample_res = """
        JOHN SMITH
        Developer with 5 years experience in Python and AWS.
        Skills: Python, Docker, AWS
        Experience:
        Engineer | Tech Corp | 2020 - Present
        - Built API backend using Python.
        """
        sample_jd = """
        Title: Senior Backend Engineer
        Company: Nexa Systems
        Requirements: Python, Docker, AWS, Kubernetes
        """
        res_data = normalize_to_ats_json(sample_res, "test.txt")
        jd_data = parse_job_description(sample_jd)
        comp = compare_resume_to_jd(res_data, jd_data)

        # Run async suggester
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            generate_resume_suggestions_async(res_data, jd_data, comp)
        )
        loop.close()

        self.assertIn("summary", result)
        self.assertIn("experience", result)
        self.assertTrue("source" in result)
        print(f"[Settings Test] Suggester execution source: {result['source']}")

if __name__ == "__main__":
    unittest.main()
