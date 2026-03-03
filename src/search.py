import os
import requests
from typing import List
from dateutil.parser import parse

from .models import Job

SERPAPI_ENDPOINT = "https://serpapi.com/search.json"

def _safe_parse_date(s: str):
    if not s:
        return None
    try:
        return parse(s).date().isoformat()
    except Exception:
        return None

def search_jobs(query: str, max_results: int = 30, location: str = "United States") -> List[Job]:
    """
    Uses SerpAPI Google Jobs engine.
    Returns a list of Job objects.
    """
    api_key = os.getenv("SERPAPI_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("SERPAPI_API_KEY missing. Add it in your environment or Hugging Face Secrets.")

    params = {
        "engine": "google_jobs",
        "q": query,
        "location": location,
        "hl": "en",
        "api_key": api_key,
    }

    resp = requests.get(SERPAPI_ENDPOINT, params=params, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    results = data.get("jobs_results", [])[:max_results]
    jobs: List[Job] = []

    for r in results:
        title = r.get("title") or ""
        company = r.get("company_name") or ""
        loc = r.get("location") or ""
        url = r.get("related_links", [{}])[0].get("link") or r.get("apply_options", [{}])[0].get("link") or ""

        # posted_at can be like "3 days ago" sometimes; SerpAPI may include "detected_extensions"
        detected = r.get("detected_extensions", {}) or {}
        posted_at = detected.get("posted_at") or ""
        date_posted = _safe_parse_date(posted_at)  # best-effort; may be None

        # Skills are not always explicit; we’ll extract from description via simple keyword scan later
        description = r.get("description", "") or ""
        salary = detected.get("salary") or ""

        jobs.append(
            Job(
                title=title,
                company=company,
                location=loc,
                url=url,
                date_posted=date_posted,
                skills=_extract_skills_from_text(description),
                salary=salary,
            )
        )

    return jobs

def _extract_skills_from_text(text: str):
    """Simple keyword-based extraction. Improve later if needed."""
    if not text:
        return []
    t = text.lower()
    skill_bank = [
        "python","pytorch","tensorflow","sklearn","scikit-learn","mlflow","docker","kubernetes",
        "llm","langchain","rag","aws","gcp","azure","spark","sql","nlp","cv","computer vision"
    ]
    found = []
    for s in skill_bank:
        if s in t:
            found.append(s)
    # normalize
    found = sorted(set(found))
    return found
