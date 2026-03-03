from typing import List, Dict, Tuple
from datetime import datetime
from dateutil.parser import parse
from .models import Job

RESUME_SKILLS = {
    "python","pytorch","tensorflow","mlflow","docker","kubernetes","sql","aws","gcp","azure","rag","llm","langchain"
}

def _recency_score(date_posted: str, days_recent: int) -> float:
    if not date_posted:
        return 0.4  # unknown date gets neutral-ish score
    try:
        d = parse(date_posted).date()
        age = (datetime.utcnow().date() - d).days
        if age <= days_recent:
            return 1.0
        # soft decay
        return max(0.0, 1.0 - (age - days_recent) / max(1, days_recent))
    except Exception:
        return 0.4

def score_job(job: Job, location_pref: str, days_recent: int) -> Tuple[float, Dict]:
    skills = set((job.skills or []))
    overlap = len(skills & RESUME_SKILLS)
    denom = max(1, len(skills))
    skill_match = overlap / denom

    loc_pref = (location_pref or "").lower().strip()
    loc = (job.location or "").lower()
    location_score = 1.0 if loc_pref and loc_pref in loc else 0.3

    recency = _recency_score(job.date_posted, days_recent)

    final = 0.55 * skill_match + 0.25 * location_score + 0.20 * recency
    breakdown = {
        "skill_match": round(skill_match, 3),
        "location_score": round(location_score, 3),
        "recency_score": round(recency, 3),
        "final_score": round(final, 3),
        "matched_skills": sorted(list(skills & RESUME_SKILLS)),
    }
    return final, breakdown

def rank_jobs(jobs: List[Job], location_pref: str, days_recent: int) -> List[Dict]:
    rows = []
    for j in jobs:
        score, b = score_job(j, location_pref, days_recent)
        r = j.to_dict()
        r.update(b)
        rows.append(r)

    rows.sort(key=lambda x: x["final_score"], reverse=True)
    return rows
