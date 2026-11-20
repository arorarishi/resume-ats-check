import os
import sys
import unittest

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.parsers.ats_normalizer import normalize_to_ats_json
from app.analyzer.jd_parser import parse_job_description
from app.analyzer.matcher import compare_resume_to_jd
from app.analyzer.suggester import generate_resume_suggestions
from app.database import (
    init_db, create_application, get_all_applications,
    update_application_stage, get_funnel_stats, delete_application
)

SAMPLE_RESUME = """
JANE DOE
Austin, TX | (512) 555-0199 | jane.doe@techmail.com
linkedin.com/in/janedoe-cloud | github.com/janedoe

PROFESSIONAL SUMMARY
Senior Cloud & DevOps Engineer with 7 years of experience designing secure AWS infrastructure, automating CI/CD pipelines, and managing Kubernetes clusters.

TECHNICAL SKILLS
Languages: Python, Go, Bash, SQL
Cloud & DevOps: AWS, Docker, Kubernetes, Terraform, Jenkins, Linux, CI/CD
Databases: PostgreSQL, Redis
Frameworks: FastAPI, Flask

WORK EXPERIENCE
Lead Infrastructure Engineer | Apex Cloud Systems | Austin, TX | 2021 - Present
- Architected Kubernetes microservices on AWS EKS, increasing cluster reliability to 99.99% and reducing cloud spend by $120,000 annually.
- Spearheaded automated CI/CD deployment pipelines using Jenkins and Docker, accelerating release frequency by 4x.
- Mentored a team of 6 engineers on infrastructure-as-code best practices using Terraform.

DevOps Engineer | Nimbus Solutions | Dallas, TX | 2018 - 2021
- Automated database provisioning and backups for PostgreSQL clusters handling 20TB+ of data.
- Built monitoring and alerting dashboards using Prometheus and Grafana, reducing incident response time by 40%.

EDUCATION
Bachelor of Science in Computer Engineering | University of Texas at Austin | 2014 - 2018
"""

SAMPLE_JD = """
Job Title: Senior Kubernetes & Cloud Infrastructure Engineer
Company: CloudNative Global
Location: Austin, TX (Hybrid)

Requirements:
- 5+ years experience in cloud infrastructure with strong AWS and Kubernetes expertise.
- Hands-on proficiency with Terraform, Docker, and CI/CD pipelines.
- Strong scripting skills in Python or Go.
- Experience with PostgreSQL or distributed databases.

Nice-to-Have:
- Experience with Prometheus, Grafana, and observability tools.
- Familiarity with gRPC, microservices, and Linux internals.
"""

class TestATSApplicationTracker(unittest.TestCase):
    def setUp(self):
        init_db()

    def test_resume_parser_and_ats_json(self):
        res = normalize_to_ats_json(SAMPLE_RESUME, "Jane_Doe_Resume.txt")
        ats_json = res["ats_json"]
        hygiene = res["hygiene_report"]

        # Check contact info
        contact = ats_json["contact_information"]
        self.assertEqual(contact["name"], "JANE DOE")
        self.assertEqual(contact["email"], "jane.doe@techmail.com")
        self.assertEqual(contact["phone"], "(512) 555-0199")

        # Check skills
        skills = ats_json["skills"]["all_keywords"]
        self.assertIn("Python", skills)
        self.assertIn("AWS", skills)
        self.assertIn("Kubernetes", skills)

        # Check hygiene score
        self.assertGreaterEqual(hygiene["score"], 80)
        self.assertIn(hygiene["grade"], ["A+", "A"])
        print(f"\n[Test 1] ATS Hygiene Score: {hygiene['score']} ({hygiene['grade']})")

    def test_jd_parser_and_matching(self):
        res = normalize_to_ats_json(SAMPLE_RESUME, "Jane_Doe_Resume.txt")
        jd_data = parse_job_description(SAMPLE_JD)

        self.assertIn("AWS", jd_data["must_have_skills"])
        self.assertIn("Kubernetes", jd_data["must_have_skills"])

        comparison = compare_resume_to_jd(res, jd_data)
        self.assertGreaterEqual(comparison["match_score"], 70.0)
        self.assertTrue(len(comparison["side_by_side_matrix"]) > 0)
        print(f"[Test 2] ATS Match Score vs JD: {comparison['match_score']}% ({comparison['score_tier']})")
        print(f"         Total Skills Evaluated: {len(comparison['side_by_side_matrix'])}")

    def test_resume_suggestions(self):
        res = normalize_to_ats_json(SAMPLE_RESUME, "Jane_Doe_Resume.txt")
        jd_data = parse_job_description(SAMPLE_JD)
        comparison = compare_resume_to_jd(res, jd_data)

        suggestions = generate_resume_suggestions(res, jd_data, comparison)
        self.assertIn("recommended", suggestions["summary"])
        self.assertTrue(len(suggestions["experience"]) > 0)
        print(f"[Test 3] Generated Tailored Summary & {len(suggestions['experience'])} Role Bullet Rewrites")

    def test_application_funnel_database(self):
        # Create
        app = create_application({
            "company": "CloudNative Global",
            "role": "Senior Kubernetes Engineer",
            "stage": "Applied",
            "salary": "$165,000",
            "match_score": 88.5
        })
        app_id = app["id"]
        self.assertEqual(app["company"], "CloudNative Global")
        self.assertEqual(app["stage"], "Applied")

        # Update stage
        updated = update_application_stage(app_id, "Screening")
        self.assertEqual(updated["stage"], "Screening")

        # Stats
        stats = get_funnel_stats()
        self.assertGreaterEqual(stats["total_tracked"], 1)
        self.assertGreaterEqual(stats["stage_counts"]["Screening"], 1)
        print(f"[Test 4] Funnel Database CRUD passed. Total Applications: {stats['total_tracked']}")

        # Cleanup test entry
        delete_application(app_id)

if __name__ == "__main__":
    unittest.main()
