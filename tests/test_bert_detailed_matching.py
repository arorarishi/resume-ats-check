import os
import sys
import unittest
import asyncio

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.parsers.ats_normalizer import normalize_to_ats_json
from app.analyzer.jd_parser import parse_job_description
from app.analyzer.matcher import compare_resume_to_jd, compare_resume_to_jd_async
from app.database import init_db

SAMPLE_RESUME = """
RACHEL ZANE
San Francisco, CA | rachel@example.com
PROFESSIONAL SUMMARY
Senior Backend Engineer with 6 years experience in Python, FastAPI, Docker, and PostgreSQL.
TECHNICAL SKILLS
Languages: Python, SQL
Cloud: Docker, AWS
Databases: PostgreSQL
WORK EXPERIENCE
Senior Backend Engineer | Apex Inc | 2021 - Present
- Scaled distributed microservices in Python handling 10M daily requests.
"""

SAMPLE_JD = """
Job Title: Senior NLP & Machine Learning Engineer
Company: CognitiveAI Labs
Requirements:
- 5+ years experience in Python and Docker.
- Knowledge of Classification, Q&A networks using BERT.
- Experience with low-latency inference pipelines and multi-tenant RAG architectures.
- Experience with PostgreSQL.
"""

class TestDetailedRequirementMatching(unittest.TestCase):
    def setUp(self):
        init_db()

    def test_bert_and_detailed_requirements_extracted(self):
        res = normalize_to_ats_json(SAMPLE_RESUME, "resume.txt")
        jd_data = parse_job_description(SAMPLE_JD)

        # Verify detailed requirement captured in JD parsing
        req_texts = [r["text"] for r in jd_data["detailed_requirements"]]
        bert_found = any("BERT" in t or "Classification" in t for t in req_texts)
        self.assertTrue(bert_found, "BERT requirement should be captured in detailed_requirements")
        print("\n[JD Parser Test] Captured detailed requirement statements:")
        for r in jd_data["detailed_requirements"]:
            print(f"  • [{r['priority']}] {r['text']}")

        # Compare using matcher
        comp = compare_resume_to_jd(res, jd_data)
        matrix = comp["side_by_side_matrix"]

        # Verify BERT point is present in side-by-side matrix
        bert_matrix_row = next((row for row in matrix if "BERT" in row["skill"] or "Classification" in row["skill"]), None)
        self.assertIsNotNone(bert_matrix_row, "BERT requirement must appear in side_by_side_matrix")
        self.assertEqual(bert_matrix_row["status"], "Missing")
        self.assertTrue(len(bert_matrix_row["suggested_bullet"]) > 20)
        print("\n[Side-by-Side Matrix Test] Verified BERT requirement row:")
        print(f"  • Skill: {bert_matrix_row['skill']}")
        print(f"  • Status: {bert_matrix_row['status']}")
        print(f"  • Suggested XYZ Bullet: {bert_matrix_row['suggested_bullet']}")

    def test_async_matcher_with_active_provider_or_fallback(self):
        res = normalize_to_ats_json(SAMPLE_RESUME, "resume.txt")
        jd_data = parse_job_description(SAMPLE_JD)

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        comp = loop.run_until_complete(
            compare_resume_to_jd_async(res, jd_data, SAMPLE_JD)
        )
        loop.close()

        self.assertTrue(len(comp["side_by_side_matrix"]) > 0)
        self.assertIn("source", comp)
        print(f"\n[Async Matcher Test] Matrix items: {len(comp['side_by_side_matrix'])}, Source: {comp['source']}")

if __name__ == "__main__":
    unittest.main()
