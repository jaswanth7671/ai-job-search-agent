import os
from typing import Dict
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

BASE_RESUME = """Jaswanth Produturu — AI Engineer (3–5 years)
Skills: Python, TensorFlow, PyTorch, MLflow, Docker, Kubernetes, SQL, AWS/GCP
Experience:
- Built ML pipelines for training and deployment; improved reliability and monitoring
- Worked on model evaluation, feature engineering, and data preprocessing
Projects:
- LLM/RAG prototypes; prompt engineering; basic MLOps workflows
"""

def tailor_application(job: Dict) -> Dict:
    prompt = f"""
You are an assistant generating job-specific application documents.

JOB:
Title: {job.get("title")}
Company: {job.get("company")}
Location: {job.get("location")}
Skills mentioned: {job.get("skills")}
Matched skills: {job.get("matched_skills")}
URL: {job.get("url")}

BASE RESUME:
{BASE_RESUME}

TASK:
1) Create a tailored RESUME in Markdown (1 page equivalent).
   - Only adjust: Summary, Skills ordering, and 3 experience bullets.
   - Do NOT invent employers, degrees, or certifications.

2) Create a tailored COVER LETTER in Markdown (250–350 words).
   - Mention company + role.
   - Highlight 2–3 relevant skills/projects.
   - Keep tone professional.

Return strictly this format:

## RESUME
...

## COVER_LETTER
...
"""

    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )
    text = resp.choices[0].message.content

    # Split
    resume_md = ""
    cover_md = ""
    if "## COVER_LETTER" in text:
        parts = text.split("## COVER_LETTER", 1)
        resume_md = parts[0].replace("## RESUME", "").strip()
        cover_md = parts[1].strip()
    else:
        resume_md = text.strip()

    return {"resume_md": resume_md, "cover_letter_md": cover_md, "prompt": prompt}
