from .search import search_jobs
from .filter import filter_jobs
from .rank import rank_jobs
from .tailor import tailor_resume


def run_pipeline(query, max_results=10):

    jobs = search_jobs(query, max_results)

    filtered = filter_jobs(jobs)

    ranked = rank_jobs(filtered)

    results = []

    for job in ranked[:3]:

        resume = tailor_resume(job)

        results.append({
            "job": job.to_dict(),
            "tailored_resume": resume
        })

    return results
