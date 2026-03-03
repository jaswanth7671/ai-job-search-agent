import os
import re
import time
import json
import requests
from typing import Optional, Dict, Any

SERPAPI_ENDPOINT = "https://serpapi.com/search.json"

# In-memory cache to reduce API calls during one run
_MEM_CACHE: Dict[str, Optional[int]] = {}

def _normalize_company_key(company: str) -> str:
    return re.sub(r"\s+", " ", (company or "").strip().lower())

def _extract_employee_count_from_text(text: str) -> Optional[int]:
    """
    Tries to parse an employee count from snippets like:
    - "1,234 employees"
    - "200+ employees"
    - "10-50 employees"  -> returns 50 (upper bound)
    - "51-200 employees" -> returns 200
    """
    if not text:
        return None
    t = text.lower()

    # Range like 10-50 employees
    m = re.search(r"(\d[\d,]*)\s*[-–]\s*(\d[\d,]*)\s+employees", t)
    if m:
        lo = int(m.group(1).replace(",", ""))
        hi = int(m.group(2).replace(",", ""))
        return max(lo, hi)

    # Single number like 1,234 employees or 200+ employees
    m = re.search(r"(\d[\d,]*)\s*\+?\s+employees", t)
    if m:
        return int(m.group(1).replace(",", ""))

    return None

def _serpapi_request(params: Dict[str, Any]) -> Dict[str, Any]:
    api_key = os.getenv("SERPAPI_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("SERPAPI_API_KEY missing. Add it in environment or HF Secrets.")

    params = dict(params)
    params["api_key"] = api_key
    resp = requests.get(SERPAPI_ENDPOINT, params=params, timeout=30)
    resp.raise_for_status()
    return resp.json()

def get_company_employee_count(company: str, sleep_s: float = 0.3) -> Optional[int]:
    """
    Best-effort employee-count lookup using SerpAPI Google Search.
    Returns an integer employee count if found, otherwise None.
    Caches results in memory.
    """
    key = _normalize_company_key(company)
    if not key:
        return None
    if key in _MEM_CACHE:
        return _MEM_CACHE[key]

    # Small delay to be polite / reduce rate limiting
    time.sleep(sleep_s)

    q = f"{company} number of employees"
    data = _serpapi_request({
        "engine": "google",
        "q": q,
        "hl": "en",
        "gl": "us",
    })

    # 1) Knowledge graph (often has employees)
    kg = data.get("knowledge_graph") or {}
    # sometimes "employees": "10,000+"
    for k in ["employees", "employee_count", "staff"]:
        if k in kg and isinstance(kg[k], str):
            n = _extract_employee_count_from_text(kg[k] + " employees")
            if n is not None:
                _MEM_CACHE[key] = n
                return n

    # 2) Answer box / snippet-like structures
    answer_box = data.get("answer_box") or {}
    # sometimes answer_box has "snippet" or "answer"
    for field in ["snippet", "answer", "snippet_highlighted_words"]:
        val = answer_box.get(field)
        if isinstance(val, str):
            n = _extract_employee_count_from_text(val)
            if n is not None:
                _MEM_CACHE[key] = n
                return n
        if isinstance(val, list):
            joined = " ".join([str(x) for x in val])
            n = _extract_employee_count_from_text(joined)
            if n is not None:
                _MEM_CACHE[key] = n
                return n

    # 3) Organic results snippets
    organic = data.get("organic_results") or []
    for r in organic[:5]:
        snippet = r.get("snippet") or ""
        title = r.get("title") or ""
        combined = f"{title}. {snippet}"
        n = _extract_employee_count_from_text(combined)
        if n is not None:
            _MEM_CACHE[key] = n
            return n

    _MEM_CACHE[key] = None
    return None
