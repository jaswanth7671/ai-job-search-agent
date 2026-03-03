from datetime import datetime
import pandas as pd

from .logging_utils import new_trace, log_step
from .search import search_jobs
from .filter import filter_jobs
from .rank import rank_jobs
from .tailor import tailor_application

def run_pipeline(
    query: str,
    max_results: int = 30,
    location_pref: str = "Texas",
    days_recent: int = 30,
    exclude_faang: bool = True,
    exclude_startups: bool = True,
    enable_tailoring: bool = True,
    search_location: str = "United States",
):
    run_id = datetime.utcnow().strftime("run_%Y%m%d_%H%M%S")
    trace = new_trace()

    raw = search_jobs(query=query, max_results=max_results, location=search_location)
    log_step(trace, "search", {"query": query, "raw_count": len(raw), "search_location": search_location})

    filtered, meta = filter_jobs(raw, exclude_faang=exclude_faang, exclude_startups=exclude_startups, startup_employee_threshold=50)
    log_step(trace, "filter", {"filtered_count": len(filtered), **meta})

    ranked = rank_jobs(filtered, location_pref=location_pref, days_recent=days_recent)
    top10 = ranked[:10]
    log_step(trace, "rank", {"top10_count": len(top10), "location_pref": location_pref, "days_recent": days_recent})

    apps = []
    if enable_tailoring:
        for job in top10[:3]:
            out = tailor_application(job)
            apps.append({
                "job_title": job["title"],
                "company": job["company"],
                "location": job["location"],
                "url": job["url"],
                "resume_md": out["resume_md"],
                "cover_letter_md": out["cover_letter_md"],
            })
        log_step(trace, "tailor", {"tailored_count": len(apps)})

    return {
        "run_id": run_id,
        "raw_jobs": pd.DataFrame([j.to_dict() for j in raw]),
        "filtered_jobs": pd.DataFrame([j.to_dict() for j in filtered]),
        "ranked_top10": pd.DataFrame(top10),
        "applications": apps,
        "trace": trace,
    }
