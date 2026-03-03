def rank_jobs(jobs):

    ranked = []

    for job in jobs:
        score = 0

        if job.skills:
            if "Python" in job.skills:
                score += 2

            if "MLflow" in job.skills:
                score += 1

        ranked.append((score, job))

    ranked.sort(reverse=True, key=lambda x: x[0])

    return [job for score, job in ranked]
