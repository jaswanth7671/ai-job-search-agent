FAANG = ["Google","Amazon","Meta","Apple","Netflix","Microsoft"]

def filter_jobs(jobs):

    filtered = []

    for job in jobs:
        if job.company in FAANG:
            continue
        filtered.append(job)

    return filtered
