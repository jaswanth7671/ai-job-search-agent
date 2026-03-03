from .models import Job

def search_jobs(query, max_results):
    jobs = [
        Job(
            title="AI Engineer",
            company="State Farm",
            location="Texas",
            url="https://example.com/job1",
            skills=["Python","MLflow","LLM"],
            date_posted="2026-02-20"
        ),
        Job(
            title="Machine Learning Engineer",
            company="John Deere",
            location="Iowa",
            url="https://example.com/job2",
            skills=["Python","PyTorch"],
            date_posted="2026-02-10"
        ),
        Job(
            title="AI Engineer",
            company="Google",
            location="California",
            url="https://example.com/job3",
            skills=["TensorFlow"],
            date_posted="2026-02-15"
        )
    ]

    return jobs[:max_results]
