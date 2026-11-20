import re
import time
import json
import logging
from typing import Dict, Any, Optional
import httpx
from app.database import get_active_provider

logger = logging.getLogger("llm_client")

async def test_provider_connection(base_url: str, api_key: str, model_name: str) -> Dict[str, Any]:
    """
    Tests an OpenAI-compatible endpoint with a minimal test message.
    """
    clean_base = base_url.strip().rstrip("/")
    # Handle base URLs with or without /v1
    if not clean_base.endswith("/chat/completions"):
        url = f"{clean_base}/chat/completions"
    else:
        url = clean_base

    headers = {
        "Content-Type": "application/json"
    }
    if api_key and api_key.strip():
        headers["Authorization"] = f"Bearer {api_key.strip()}"

    payload = {
        "model": model_name.strip(),
        "messages": [
            {"role": "system", "content": "You are a test agent."},
            {"role": "user", "content": "Ping test. Respond with 'PONG' only."}
        ],
        "max_tokens": 10,
        "temperature": 0.1
    }

    start_time = time.time()
    try:
        async with httpx.AsyncClient(timeout=12.0) as client:
            resp = await client.post(url, headers=headers, json=payload)
            elapsed_ms = round((time.time() - start_time) * 1000)

            if resp.status_code == 200:
                data = resp.json()
                reply = data.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
                return {
                    "success": True,
                    "status_code": 200,
                    "latency_ms": elapsed_ms,
                    "reply": reply or "PONG",
                    "model": model_name
                }
            else:
                err_detail = resp.text
                try:
                    err_json = resp.json()
                    err_detail = err_json.get("error", {}).get("message", resp.text)
                except Exception:
                    pass
                return {
                    "success": False,
                    "status_code": resp.status_code,
                    "error": f"HTTP {resp.status_code}: {err_detail}"
                }
    except httpx.ConnectError:
        return {
            "success": False,
            "error": f"Failed to connect to '{clean_base}'. Is the server running and accessible?"
        }
    except httpx.TimeoutException:
        return {
            "success": False,
            "error": f"Connection timed out after 12 seconds to '{clean_base}'."
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Error: {str(e)}"
        }

async def call_active_llm(prompt: str, system_prompt: str = "") -> Optional[str]:
    """
    Calls the active LLM provider if configured. Returns None if no active provider or on error.
    """
    provider = get_active_provider()
    if not provider:
        return None

    base_url = provider.get("base_url", "").strip().rstrip("/")
    api_key = provider.get("api_key", "").strip()
    model_name = provider.get("model_name", "").strip()

    if not base_url or not model_name:
        return None

    url = f"{base_url}/chat/completions" if not base_url.endswith("/chat/completions") else base_url
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    payload = {
        "model": model_name,
        "messages": messages,
        "temperature": 0.2,
        "max_tokens": 3000
    }

    try:
        timeout = httpx.Timeout(120.0, connect=12.0, read=120.0)
        async with httpx.AsyncClient(timeout=timeout) as client:
            resp = await client.post(url, headers=headers, json=payload)
            if resp.status_code == 200:
                data = resp.json()
                return data.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
            else:
                print(f"[LLM Error] Status {resp.status_code}: {resp.text}")
                return None
    except Exception as e:
        print(f"[LLM Error] Exception: {type(e).__name__}: {e}")
        return None

async def clean_and_extract_master_resume_with_llm(resume_text: str) -> Optional[Dict[str, Any]]:
    """
    Uses the active LLM provider to cleanly extract and fill all sections of the Master Resume
    without character truncation, cutting off metrics, or losing text.
    """
    system_prompt = """You are an expert executive resume architect and ATS data normalizer.
Your job is to read raw resume text and extract all information cleanly into a structured, exhaustive Master Resume schema.

CRITICAL EXTRACTION RULES:
1. ZERO TRUNCATION: Never cut off bullet points, numbers, or achievements. Preserve metrics like '10x', '45%', '$2M+', '99.98%' completely.
2. CAREER PROJECTS:
   - For every project, extract:
     * 'name': Descriptive project name.
     * 'organisation': The company or organization where the project was conducted (e.g. Apex AI Technologies, or Independent / Personal).
     * 'organisation_duration': The candidate's tenure at that organisation (e.g. '2022 - Present'). (Duration belongs to Organisation only).
     * 'tech_stack': Technologies, libraries, frameworks used.
     * 'description': Architectural scope or problem solved.
     * 'metrics': Primary measurable result (e.g. 'Reduced latency by 45%').
     * 'bullets': Detailed implementation bullets.
   - If the resume lacks a dedicated 'Projects' section, extract 2-4 notable system architectures / initiatives from Work Experience.
3. SKILLS TAXONOMY: Group skills logically into categories: 'Languages', 'Frameworks & AI', 'Cloud & DevOps', 'Databases', 'Architecture & Tools'.
4. OUTPUT FORMAT: Respond ONLY with valid, raw JSON matching the schema below. Do NOT include any markdown code fences, commentary, or extra text.

JSON Schema:
{
  "profile_name": "string",
  "full_name": "string",
  "email": "string",
  "phone": "string",
  "location": "string",
  "linkedin": "string",
  "github": "string",
  "summary": "string",
  "skills": {
    "Languages": ["string"],
    "Frameworks & AI": ["string"],
    "Cloud & DevOps": ["string"],
    "Databases": ["string"]
  },
  "experiences": [
    {
      "company": "string",
      "title": "string",
      "location": "string",
      "start_date": "string",
      "end_date": "string",
      "dates": "string",
      "bullets": ["string"]
    }
  ],
  "projects": [
    {
      "id": "proj-1",
      "name": "string",
      "organisation": "string",
      "organisation_duration": "string",
      "tech_stack": "string",
      "description": "string",
      "metrics": "string",
      "bullets": ["string"]
    }
  ],
  "education": [
    {
      "degree": "string",
      "institution": "string",
      "year": "string",
      "details": "string"
    }
  ],
  "certifications": ["string"]
}"""

    user_prompt = f"""Here is the raw resume text to parse and normalize into the Master Resume schema:

---
{resume_text.strip()}
---

Extract cleanly and return ONLY the complete JSON object."""

    response = await call_active_llm(user_prompt, system_prompt=system_prompt)
    if not response:
        return None

    # Parse JSON cleanly
    cleaned = response.strip()
    if "```" in cleaned:
        m = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", cleaned)
        if m:
            cleaned = m.group(1).strip()
        else:
            cleaned = re.sub(r'^```(?:json)?\s*', '', cleaned)
            cleaned = re.sub(r'\s*```$', '', cleaned)

    if "{" in cleaned and "}" in cleaned:
        start = cleaned.find("{")
        end = cleaned.rfind("}") + 1
        cleaned = cleaned[start:end]

    try:
        data = json.loads(cleaned)
        # Ensure project IDs exist
        if "projects" in data and isinstance(data["projects"], list):
            for idx, p in enumerate(data["projects"]):
                if not p.get("id"):
                    p["id"] = f"proj-{idx + 1}"
        return data
    except Exception as e:
        print(f"[LLM Clean JSON Parse Error]: {e}\nRaw output preview: {cleaned[:300]}")
        return None

