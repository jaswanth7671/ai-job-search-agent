from typing import List, Tuple, Dict
from .models import Job

FAANG = {"google", "meta", "amazon", "apple", "microsoft", "netflix"}

def filter_jobs(jobs: List[Job], exclude_faang: bool = True, exclude_startups: bool = True) -> Tuple[List[Job], Dict]:
    kept = []
    decisions = []

    for j in jobs:
        company_l = (j.company or "").lower().strip()

        if exclude_faang and company_l in FAANG:
            decisions.append({"company": j.company, "keep": False, "reason": "FAANG blacklist"})
            continue

        # Startup heuristic (MVP): we don't have company-size API yet
        # For the assignment, it’s okay to implement a heuristic + logging.
        if exclude_startups:
            # Very simple heuristic: if company name contains "Inc." doesn't mean startup,
            # so we DON'T auto-reject. We log as unknown.
            decisions.append({"company": j.company, "keep": True, "reason": "startup size unknown (kept); improve with company-size lookup"})
            kept.append(j)
            continue

        decisions.append({"company": j.company, "keep": True, "reason": "passed"})
        kept.append(j)

    return kept, {"filter_decisions": decisions}
