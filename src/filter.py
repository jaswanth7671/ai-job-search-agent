from typing import List, Tuple, Dict
from .models import Job
from .company_size import get_company_employee_count

FAANG = {"google", "meta", "amazon", "apple", "microsoft", "netflix"}

def filter_jobs(
    jobs: List[Job],
    exclude_faang: bool = True,
    exclude_startups: bool = True,
    startup_employee_threshold: int = 50,
) -> Tuple[List[Job], Dict]:

    kept: List[Job] = []
    decisions = []

    for j in jobs:
        company = (j.company or "").strip()
        company_l = company.lower()

        # 1) FAANG blacklist
        if exclude_faang and company_l in FAANG:
            decisions.append({
                "company": company,
                "title": j.title,
                "keep": False,
                "reason": "FAANG blacklist"
            })
            continue

        # 2) Startup exclusion (<50 employees)
        if exclude_startups:
            emp = None
            why = ""

            try:
                emp = get_company_employee_count(company)
            except Exception as e:
                emp = None
                why = f"employee lookup failed: {str(e)}"

            if emp is not None and emp < startup_employee_threshold:
                decisions.append({
                    "company": company,
                    "title": j.title,
                    "keep": False,
                    "reason": f"startup heuristic: employees={emp} < {startup_employee_threshold}"
                })
                continue

            if emp is not None:
                why = f"employees={emp} >= {startup_employee_threshold} (kept)"
            else:
                if not why:
                    why = "employees unknown (kept)"

            decisions.append({
                "company": company,
                "title": j.title,
                "keep": True,
                "reason": why
            })

            kept.append(j)
            continue

        # If startup filter disabled
        decisions.append({
            "company": company,
            "title": j.title,
            "keep": True,
            "reason": "startup filter disabled"
        })
        kept.append(j)

    return kept, {"filter_decisions": decisions}
